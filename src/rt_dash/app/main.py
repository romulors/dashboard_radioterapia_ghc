"""Monta a aplicação Dash: cabeçalho, filtros, abas e estado compartilhado.

Uso: python -m rt_dash.app   (ou o comando `rt-dash`)
"""

from __future__ import annotations

import argparse
from pathlib import Path
from urllib.parse import parse_qs

import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, State, dcc, html, no_update
from dash import ctx as dash_ctx

from rt_dash.app.components import barra_filtros, cabecalho
from rt_dash.app.context import AppContext
from rt_dash.app.pages import atendimento, atividades, jornada, produtividade, visao_geral
from rt_dash.config import DEFAULT_SETTINGS, Settings, load_settings
from rt_dash.data import Dataset, carregar_dataset
from rt_dash.viz.theme import registrar_template, rotulo_mes

PAGINAS = [
    ("produtividade", "Produtividade", produtividade),
    ("visao-geral", "Visão Geral", visao_geral),
    ("atividades", "Atividades", atividades),
    ("jornada", "Jornada do Paciente", jornada),
    ("atendimento", "Atendimento no AL", atendimento),
]

ASSETS = Path(__file__).resolve().parents[1] / "assets"

# Gráficos de séries mensais: um clique num mês vira filtro de mês nas outras abas.
GRAFICOS_MES = ["g-vg-planejamentos", "g-vg-inicios", "g-vg-sessoes_turno", "g-vg-planejamentos_fluxo", "g-vg-no_prazo"]


def criar_app(settings: Settings, ds: Dataset) -> Dash:
    registrar_template()
    contexto = AppContext(settings, ds)
    app = Dash(
        __name__,
        title="Indicadores Radioterapia · GHC",
        assets_folder=str(ASSETS),
        suppress_callback_exceptions=False,
    )
    app.layout = html.Div(
        className="pagina",
        children=[
            dcc.Location(id="url", refresh=False),
            dcc.Store(id="store-filtros"),
            dcc.Store(id="store-selecao", data={}),
            cabecalho(),
            barra_filtros(contexto.meses, contexto.sitios),
            html.Div(
                className="chips-selecao",
                children=[
                    html.Div(id="chips-selecao", className="d-flex gap-2 align-items-center"),
                    dbc.Button("Limpar seleção", id="limpar-selecao", color="link", size="sm"),
                ],
            ),
            dbc.Tabs(
                id="abas",
                active_tab="produtividade",
                className="abas",
                children=[
                    dbc.Tab(pagina.layout(contexto), tab_id=tid, label=rotulo) for tid, rotulo, pagina in PAGINAS
                ],
            ),
            html.Footer(
                "Fonte: Sistema Aria (Radioterapia) · Hospital Nossa Senhora da Conceição · dados anonimizados",
                className="rodape",
            ),
        ],
    )
    _registrar_estado(app, contexto)
    for _, _, pagina in PAGINAS:
        pagina.registrar(app, contexto)
    return app


def _registrar_estado(app: Dash, contexto: AppContext) -> None:
    @app.callback(
        Output("store-filtros", "data"),
        Input("f-periodo", "value"),
        Input("f-fluxo", "value"),
        Input("f-sitio", "value"),
        Input("f-internado", "value"),
    )
    def filtros(periodo, fluxos, sitios, internado):
        return {"periodo": periodo, "fluxos": fluxos or [], "sitios": sitios or [], "internado": internado or ""}

    @app.callback(
        Output("f-periodo", "value"),
        Output("f-fluxo", "value"),
        Output("f-sitio", "value"),
        Output("f-internado", "value"),
        Input("f-limpar", "n_clicks"),
        prevent_initial_call=True,
    )
    def limpar_filtros(_):
        return [0, len(contexto.meses) - 1], [], [], ""

    @app.callback(
        Output("store-selecao", "data"),
        Output("abas", "active_tab"),
        [Input(g, "clickData") for g in GRAFICOS_MES]
        + [
            Input("g-at-barras", "clickData"),
            Input("g-at-heatmap", "clickData"),
            Input("g-at-box", "clickData"),
            Input("grid-at-pacientes", "selectedRows"),
            Input("grid-jornada", "selectedRows"),
            Input("jo-ciclo", "value"),
            Input("url", "search"),
            Input("limpar-selecao", "n_clicks"),
            Input("f-limpar", "n_clicks"),
        ],
        State("store-selecao", "data"),
        prevent_initial_call=True,
    )
    def selecionar(*args):
        selecao = dict(args[-1] or {})
        gatilho = dash_ctx.triggered_id
        valor = dash_ctx.triggered[0]["value"] if dash_ctx.triggered else None
        aba = no_update
        if gatilho in ("limpar-selecao", "f-limpar"):
            return {}, no_update
        if gatilho in GRAFICOS_MES and valor:
            mes = valor["points"][0].get("customdata")
            selecao["mes"] = None if selecao.get("mes") == mes else mes
        elif gatilho == "g-at-barras" and valor:
            selecao["atividade"] = valor["points"][0]["customdata"][0]
        elif gatilho == "g-at-heatmap" and valor:
            selecao["atividade"] = valor["points"][0]["y"]
        elif gatilho == "g-at-box" and valor:
            paciente, ciclo = valor["points"][0]["customdata"][:2]
            selecao.update(paciente=str(paciente), ciclo=int(ciclo))
            aba = "jornada"
        elif gatilho == "grid-at-pacientes" and valor:
            selecao.update(paciente=str(valor[0]["paciente_id"]), ciclo=int(valor[0]["ciclo"]))
            aba = "jornada"
        elif gatilho == "grid-jornada" and valor:
            if str(valor[0]["paciente_id"]) == selecao.get("paciente"):
                return no_update, no_update
            selecao.update(paciente=str(valor[0]["paciente_id"]), ciclo=None)
        elif gatilho == "jo-ciclo" and valor is not None:
            if valor == selecao.get("ciclo"):
                return no_update, no_update
            selecao["ciclo"] = valor
        elif gatilho == "url" and valor:
            consulta = parse_qs(valor.lstrip("?"))
            if "paciente" in consulta:
                selecao.update(paciente=consulta["paciente"][0], ciclo=None)
                aba = "jornada"
        else:
            return no_update, no_update
        return selecao, aba

    @app.callback(
        Output("chips-selecao", "children"),
        Output("limpar-selecao", "style"),
        Input("store-selecao", "data"),
    )
    def chips(selecao):
        selecao = selecao or {}
        itens = []
        if selecao.get("mes"):
            import pandas as pd

            itens.append(f"Mês: {rotulo_mes(pd.Timestamp(selecao['mes']))}")
        if selecao.get("atividade"):
            itens.append(f"Atividade: {selecao['atividade']}")
        if selecao.get("paciente"):
            itens.append(
                f"Paciente: {selecao['paciente']}" + (f" · ciclo {selecao['ciclo']}" if selecao.get("ciclo") else "")
            )
        if not itens:
            dica = "Dica: clique num mês, numa atividade ou num paciente para filtrar as outras abas."
            return [html.Span(dica, className="nota")], {"display": "none"}
        conteudo = [html.Span("Seleção:", className="rotulo-controle")] + [
            html.Span(i, className="chip chip-ativo") for i in itens
        ]
        return conteudo, {}


def main() -> None:
    parser = argparse.ArgumentParser(description="Dashboard de Radioterapia (GHC)")
    parser.add_argument("--config", default=str(DEFAULT_SETTINGS))
    parser.add_argument("--recriar", action="store_true", help="refaz o ETL a partir das planilhas")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    settings = load_settings(args.config)
    app = criar_app(settings, carregar_dataset(settings, recriar=args.recriar))
    app.run(host=settings.host, port=settings.port, debug=args.debug or settings.debug)


if __name__ == "__main__":
    main()
