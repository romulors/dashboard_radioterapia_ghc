"""Sinal de vida (keep-alive) entre o navegador e o servidor, com encerramento automático.

Cada aba aberta do dashboard envia um POST para ``/_keepalive/sinal`` a cada ``intervalo`` segundos
(o timer roda num Web Worker, que o navegador não congela quando a aba fica em segundo plano).
Ao fechar a aba, ela avisa com ``navigator.sendBeacon`` em ``/_keepalive/tchau``.

Um vigia (thread daemon) encerra o processo quando:
- nenhuma aba deu sinal há mais de ``timeout`` segundos (navegador fechado, travado ou suspenso); ou
- a última aba avisou que fechou e nenhuma outra apareceu em ``tolerancia_fechar`` segundos
  (o prazo curto deixa recarregar a página, F5, sem derrubar o servidor).

Nada aqui depende das abas do dashboard: ``instalar_keepalive(app)`` só acrescenta duas rotas Flask,
um script no HTML da página e o vigia.
"""

from __future__ import annotations

import logging
import os
import threading
import time
from collections.abc import Callable

from dash import Dash
from flask import Response, request

log = logging.getLogger(__name__)

ROTA = "/_keepalive"


class MonitorKeepAlive:
    """Estado puro do keep-alive: quais abas estão vivas e se o servidor deve encerrar.

    ``relogio`` é injetável para os testes; em produção é ``time.monotonic``.
    """

    def __init__(
        self,
        timeout: float = 120.0,
        tolerancia_fechar: float = 15.0,
        carencia_inicial: float = 180.0,
        relogio: Callable[[], float] = time.monotonic,
    ) -> None:
        self.timeout = timeout
        self.tolerancia_fechar = tolerancia_fechar
        self.carencia_inicial = carencia_inicial
        self._relogio = relogio
        self._trava = threading.Lock()
        self._abas: dict[str, float] = {}
        self._inicio = relogio()
        self._ultimo_sinal: float | None = None
        self._ultimo_tchau: float | None = None

    def sinal(self, aba: str) -> None:
        with self._trava:
            agora = self._relogio()
            self._abas[aba] = agora
            self._ultimo_sinal = agora

    def tchau(self, aba: str) -> None:
        with self._trava:
            self._abas.pop(aba, None)
            self._ultimo_tchau = self._relogio()

    def abas_vivas(self) -> int:
        with self._trava:
            self._expirar(self._relogio())
            return len(self._abas)

    def motivo_encerrar(self) -> str | None:
        """Devolve o motivo para encerrar, ou ``None`` se o servidor deve continuar."""
        with self._trava:
            agora = self._relogio()
            self._expirar(agora)
            if self._abas:
                return None
            if self._ultimo_sinal is None:
                # Ainda nenhuma aba conectou: espera o navegador abrir a página.
                if agora - self._inicio > self.carencia_inicial:
                    return f"nenhum navegador conectou em {self.carencia_inicial:.0f} s"
                return None
            if self._ultimo_tchau is not None and self._ultimo_tchau >= self._ultimo_sinal:
                if agora - self._ultimo_tchau > self.tolerancia_fechar:
                    return "a última aba do dashboard foi fechada"
                return None
            if agora - self._ultimo_sinal > self.timeout:
                return f"sem sinal do navegador há mais de {self.timeout:.0f} s"
            return None

    def _expirar(self, agora: float) -> None:
        for aba, visto in list(self._abas.items()):
            if agora - visto > self.timeout:
                del self._abas[aba]


def _script_cliente(intervalo: float, prefixo: str) -> str:
    ms = int(intervalo * 1000)
    return f"""
(function () {{
  var base = location.origin + "{prefixo}{ROTA.lstrip('/')}";
  var aba = (crypto.randomUUID ? crypto.randomUUID() : String(Math.random()).slice(2));
  var corpo = JSON.stringify({{aba: aba}});
  function enviar() {{
    fetch(base + "/sinal", {{method: "POST", body: corpo, keepalive: true,
      headers: {{"Content-Type": "application/json"}}}}).catch(function () {{}});
  }}
  enviar();
  try {{
    // Timer num Web Worker: abas em segundo plano não têm o setInterval estrangulado.
    var codigo = "setInterval(function(){{postMessage(0)}}, {ms});";
    var worker = new Worker(URL.createObjectURL(new Blob([codigo], {{type: "text/javascript"}})));
    worker.onmessage = enviar;
  }} catch (e) {{
    setInterval(enviar, {ms});
  }}
  document.addEventListener("visibilitychange", function () {{
    if (document.visibilityState === "visible") enviar();
  }});
  window.addEventListener("pagehide", function () {{
    navigator.sendBeacon(base + "/tchau", new Blob([corpo], {{type: "application/json"}}));
  }});
}})();
"""


def _encerrar(motivo: str) -> None:
    log.warning("Encerrando o dashboard: %s.", motivo)
    logging.shutdown()
    os._exit(0)


def instalar_keepalive(
    app: Dash,
    intervalo: float = 30.0,
    timeout: float = 120.0,
    tolerancia_fechar: float = 15.0,
    carencia_inicial: float = 180.0,
    encerrar: Callable[[str], None] = _encerrar,
    iniciar_vigia: bool = True,
) -> MonitorKeepAlive:
    """Liga o keep-alive na ``app`` e devolve o monitor (útil para testes).

    ``timeout`` deve ser bem maior que ``intervalo`` (sugestão: 3 a 4 vezes), porque navegadores
    atrasam requisições de abas em segundo plano e de computadores que acabaram de acordar.
    """
    if timeout <= intervalo:
        raise ValueError("timeout deve ser maior que o intervalo do sinal")
    monitor = MonitorKeepAlive(timeout, tolerancia_fechar, carencia_inicial)
    servidor = app.server
    prefixo = app.config.requests_pathname_prefix or "/"
    script = _script_cliente(intervalo, prefixo)

    def _aba() -> str:
        dados = request.get_json(force=True, silent=True) or {}
        return str(dados.get("aba") or request.remote_addr or "?")[:64]

    @servidor.route(f"{ROTA}/sinal", methods=["POST"])
    def keepalive_sinal():
        monitor.sinal(_aba())
        return Response(status=204)

    @servidor.route(f"{ROTA}/tchau", methods=["POST"])
    def keepalive_tchau():
        monitor.tchau(_aba())
        return Response(status=204)

    @servidor.route(f"{ROTA}/cliente.js")
    def keepalive_cliente():
        return Response(script, mimetype="text/javascript", headers={"Cache-Control": "no-store"})

    @servidor.route(f"{ROTA}/status")
    def keepalive_status():
        return {"abas": monitor.abas_vivas()}

    tag = f'<script src="{prefixo}{ROTA.lstrip("/")}/cliente.js"></script>'
    app.index_string = app.index_string.replace("</body>", f"{tag}\n</body>", 1)

    if iniciar_vigia:
        passo = max(1.0, min(5.0, tolerancia_fechar / 3))

        def vigiar() -> None:
            while True:
                time.sleep(passo)
                motivo = monitor.motivo_encerrar()
                if motivo:
                    encerrar(motivo)
                    return

        threading.Thread(target=vigiar, name="keepalive-vigia", daemon=True).start()
    log.info("Keep-alive ativo: sinal a cada %.0f s, encerra após %.0f s sem sinal.", intervalo, timeout)
    return monitor
