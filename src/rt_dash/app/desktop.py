"""Abre o dashboard como um aplicativo de área de trabalho: sem janela de console e com fim automático.

Uso (Windows, sem console):  .venv\\Scripts\\pythonw.exe -m rt_dash.app.desktop
Ou com dois cliques em "Abrir Dashboard.vbs", na raiz do projeto.

- Carrega os dados, sobe o servidor e abre o navegador quando ele estiver pronto.
- Liga o keep-alive (``keepalive.py``): o servidor se encerra sozinho quando nenhuma aba do
  dashboard dá sinal de vida, ou pouco depois de a última aba ser fechada.
- Se o dashboard já estiver rodando, apenas abre outra aba no navegador.
- Sem console (pythonw), as mensagens vão para %LOCALAPPDATA%\\rt-dash\\dashboard.log e erros
  de inicialização aparecem numa caixa de mensagem.
"""

from __future__ import annotations

import argparse
import logging
import os
import socket
import sys
import tempfile
import threading
import time
import traceback
import urllib.request
import webbrowser
from pathlib import Path

from rt_dash.app.keepalive import ROTA, instalar_keepalive
from rt_dash.config import DEFAULT_SETTINGS, load_settings

TITULO = "Dashboard Radioterapia"
ARQUIVO_LOG = Path(os.environ.get("LOCALAPPDATA") or tempfile.gettempdir()) / "rt-dash" / "dashboard.log"
log = logging.getLogger("rt_dash.desktop")


def _sem_console() -> bool:
    return sys.stdout is None or sys.stderr is None or Path(sys.executable).stem.lower() == "pythonw"


def _preparar_log() -> None:
    if _sem_console():
        ARQUIVO_LOG.parent.mkdir(parents=True, exist_ok=True)
        arquivo = open(ARQUIVO_LOG, "w", encoding="utf-8", buffering=1)  # noqa: SIM115 (vive até o fim)
        sys.stdout = sys.stderr = arquivo
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
        force=True,
    )


def _avisar(mensagem: str) -> None:
    """Mostra um aviso ao usuário mesmo sem console (caixa de mensagem no Windows)."""
    log.error(mensagem)
    if sys.platform == "win32" and _sem_console():
        import ctypes

        ctypes.windll.user32.MessageBoxW(None, mensagem, TITULO, 0x10)
    else:
        print(mensagem, file=sys.stderr)


def _url_navegador(host: str, porta: int) -> str:
    host = "127.0.0.1" if host in ("0.0.0.0", "") else host
    return f"http://{host}:{porta}/"


def _ja_rodando(url: str) -> bool:
    try:
        with urllib.request.urlopen(f"{url}{ROTA.lstrip('/')}/status", timeout=2) as resposta:
            return resposta.status == 200
    except OSError:
        return False


def _porta_ocupada(host: str, porta: int) -> bool:
    with socket.socket() as s:
        s.settimeout(1)
        return s.connect_ex(("127.0.0.1" if host in ("0.0.0.0", "") else host, porta)) == 0


def _abrir_quando_pronto(url: str, host: str, porta: int, limite: float = 60.0) -> None:
    def esperar() -> None:
        fim = time.monotonic() + limite
        while time.monotonic() < fim:
            if _porta_ocupada(host, porta):
                webbrowser.open(url)
                return
            time.sleep(0.3)
        log.error("O servidor não respondeu em %.0f s; navegador não foi aberto.", limite)

    threading.Thread(target=esperar, name="abrir-navegador", daemon=True).start()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Dashboard de Radioterapia sem console, com encerramento automático")
    parser.add_argument("--config", default=str(DEFAULT_SETTINGS))
    parser.add_argument("--recriar", action="store_true", help="refaz o ETL a partir das planilhas")
    parser.add_argument("--intervalo", type=float, default=30.0, help="segundos entre sinais do navegador (30)")
    parser.add_argument("--timeout", type=float, default=120.0, help="segundos sem sinal até encerrar (120)")
    parser.add_argument("--sem-navegador", action="store_true", help="não abre o navegador automaticamente")
    parser.add_argument("--sem-keepalive", action="store_true", help="não encerra sozinho")
    args = parser.parse_args(argv)

    _preparar_log()
    try:
        settings = load_settings(args.config)
        url = _url_navegador(settings.host, settings.port)
        if _ja_rodando(url):
            log.info("Dashboard já está rodando em %s; abrindo outra aba.", url)
            if not args.sem_navegador:
                webbrowser.open(url)
            return
        if _porta_ocupada(settings.host, settings.port):
            _avisar(f"A porta {settings.port} já está em uso por outro programa.\n"
                    "Feche-o ou mude 'app.port' em config/settings.yaml.")
            sys.exit(1)

        # Importa aqui para o aviso de "já rodando" sair rápido, sem carregar pandas/plotly.
        from rt_dash.app.main import criar_app
        from rt_dash.data import carregar_dataset

        app = criar_app(settings, carregar_dataset(settings, recriar=args.recriar))
        if not args.sem_keepalive:
            instalar_keepalive(app, intervalo=args.intervalo, timeout=args.timeout)
        if not args.sem_navegador:
            _abrir_quando_pronto(url, settings.host, settings.port)
        log.info("Servindo em %s (log: %s)", url, ARQUIVO_LOG if _sem_console() else "console")
        app.run(host=settings.host, port=settings.port, debug=False)
    except SystemExit:
        raise
    except Exception:
        log.error("Falha ao iniciar:\n%s", traceback.format_exc())
        _avisar(f"Não foi possível iniciar o dashboard.\nDetalhes em:\n{ARQUIVO_LOG}")
        sys.exit(1)


if __name__ == "__main__":
    main()
