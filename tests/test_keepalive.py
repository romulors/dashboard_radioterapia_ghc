"""Keep-alive: o servidor só encerra quando nenhuma aba dá sinal."""

from __future__ import annotations

from dash import Dash, html

from rt_dash.app.keepalive import MonitorKeepAlive, instalar_keepalive


class Relogio:
    def __init__(self) -> None:
        self.t = 0.0

    def __call__(self) -> float:
        return self.t


def _monitor(relogio: Relogio) -> MonitorKeepAlive:
    return MonitorKeepAlive(timeout=120, tolerancia_fechar=15, carencia_inicial=180, relogio=relogio)


def test_espera_o_navegador_abrir_e_depois_desiste():
    r = Relogio()
    m = _monitor(r)
    r.t = 170
    assert m.motivo_encerrar() is None
    r.t = 181
    assert "nenhum navegador" in m.motivo_encerrar()


def test_sinais_regulares_mantem_o_servidor_vivo():
    r = Relogio()
    m = _monitor(r)
    for t in range(0, 600, 30):
        r.t = t
        m.sinal("a")
        assert m.motivo_encerrar() is None


def test_encerra_apos_timeout_sem_sinal():
    r = Relogio()
    m = _monitor(r)
    m.sinal("a")
    r.t = 119
    assert m.motivo_encerrar() is None
    r.t = 121
    assert "sem sinal" in m.motivo_encerrar()


def test_fechar_a_ultima_aba_encerra_rapido_mas_permite_recarregar():
    r = Relogio()
    m = _monitor(r)
    m.sinal("a")
    r.t = 10
    m.tchau("a")
    r.t = 20
    assert m.motivo_encerrar() is None  # dentro da tolerância (F5)
    r.t = 22
    m.sinal("b")  # página recarregada = nova aba
    r.t = 60
    assert m.motivo_encerrar() is None
    m.tchau("b")
    r.t = 76
    assert "fechada" in m.motivo_encerrar()


def test_fechar_uma_aba_nao_derruba_as_outras():
    r = Relogio()
    m = _monitor(r)
    m.sinal("a")
    m.sinal("b")
    r.t = 5
    m.tchau("a")
    r.t = 100
    assert m.motivo_encerrar() is None
    assert m.abas_vivas() == 1


def test_rotas_flask_e_script_na_pagina():
    app = Dash(__name__)
    app.layout = html.Div("ok")
    motivos: list[str] = []
    monitor = instalar_keepalive(app, encerrar=motivos.append, iniciar_vigia=False)
    cliente = app.server.test_client()

    assert cliente.post("/_keepalive/sinal", json={"aba": "x"}).status_code == 204
    assert cliente.get("/_keepalive/status").get_json() == {"abas": 1}
    assert cliente.post("/_keepalive/tchau", data='{"aba": "x"}').status_code == 204
    assert monitor.abas_vivas() == 0

    js = cliente.get("/_keepalive/cliente.js").get_data(as_text=True)
    assert "sendBeacon" in js and "30000" in js
    assert "/_keepalive/cliente.js" in cliente.get("/").get_data(as_text=True)
