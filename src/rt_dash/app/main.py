"""Monta a aplicação Dash: cabeçalho, filtros, abas e estado compartilhado.

Uso: python -m rt_dash.app   (ou o comando `rt-dash`)
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import parse_qs

import dash_bootstrap_components as dbc
from dash import ALL, ClientsideFunction, Dash, Input, Output, State, dcc, html, no_update
from dash import ctx as dash_ctx

from rt_dash.app import ajuda
from rt_dash.app.abas import ABAS
from rt_dash.app.components import barra_filtros, cabecalho
from rt_dash.app.context import AppContext
from rt_dash.app.pages import (
    analise_multidimensional,
    atendimento,
    atividades,
    jornada,
    novos,
    produtividade,
    visao_geral,
)
from rt_dash.config import DEFAULT_SETTINGS, Settings, load_settings
from rt_dash.data import Dataset, carregar_dataset
from rt_dash.viz import theme
from rt_dash.viz.theme import registrar_template, rotulo_mes

MODULOS = [analise_multidimensional, produtividade, visao_geral, atividades, jornada, atendimento, novos]

# Página base com idioma declarado (WCAG 3.1.1) e a paleta de alto contraste para assets/a11y.js.
INDEX = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
{%metas%}
<title>{%title%}</title>
{%favicon%}
{%css%}
<script>window.RT_A11Y = __A11Y__;</script>
</head>
<body>
{%app_entry%}
<footer>
{%config%}
{%scripts%}
{%renderer%}
</footer>
</body>
</html>"""


def _config_a11y() -> str:
    return json.dumps(
        {
            "mapa": theme.ALTO_CONTRASTE,
            "escala": theme.ESCALA_ALTO_CONTRASTE,
            "padroes": theme.PADROES_BARRA,
            "tracos": theme.TRACOS_LINHA,
            "simbolos": theme.SIMBOLOS,
        }
    )


ASSETS = Path(__file__).resolve().parents[1] / "assets"

# Gráficos de séries mensais: um clique num mês vira filtro de mês nas outras abas.
GRAFICOS_MES = ["g-vg-planejamentos", "g-vg-inicios", "g-vg-sessoes_turno", "g-vg-planejamentos_fluxo", "g-vg-no_prazo"]


def criar_app(settings: Settings, ds: Dataset) -> Dash:
    registrar_template()
    contexto = AppContext(settings, ds)
    ajuda.configurar(settings)
    app = Dash(
        __name__,
        title="Indicadores Radioterapia · GHC",
        assets_folder=str(ASSETS),
        suppress_callback_exceptions=False,
    )
    app.index_string = INDEX.replace("__A11Y__", _config_a11y())
    opcoes_mes = [{"label": rotulo_mes(m), "value": m.strftime("%Y-%m")} for m in contexto.meses]
    app.layout = html.Div(
        className="pagina",
        children=[
            html.A("Pular para o conteúdo principal", href="#conteudo", className="pular-link"),
            dcc.Location(id="url", refresh=False),
            dcc.Store(id="store-filtros"),
            dcc.Store(id="store-selecao", data={}),
            dcc.Store(id="a11y-aplicado"),
            cabecalho(),
            barra_filtros(contexto.meses, contexto.sitios),
            html.Main(
                id="conteudo",
                tabIndex="-1",
                children=[
                    html.Div(
                        className="chips-selecao",
                        children=[
                            html.Label("Mês em destaque", htmlFor="f-mes-destaque", className="rotulo-controle"),
                            dcc.Dropdown(
                                id="f-mes-destaque",
                                options=opcoes_mes,
                                placeholder="Nenhum",
                                className="dropdown-mes",
                            ),
                            html.Div(
                                id="chips-selecao",
                                className="d-flex gap-2 align-items-center",
                                role="status",
                                **{"aria-live": "polite"},
                            ),
                            dbc.Button("Limpar seleção", id="limpar-selecao", color="link", size="sm"),
                        ],
                    ),
                    dbc.Tabs(
                        id="abas",
                        active_tab="visao-geral",
                        className="abas",
                        children=[dbc.Tab(montar(contexto), tab_id=tid, label=rotulo) for tid, rotulo, montar in ABAS],
                    ),
                ],
            ),
            html.Footer(
                "Fonte: Sistema Aria (Radioterapia) · Hospital Nossa Senhora da Conceição · dados anonimizados",
                className="rodape",
            ),
        ],
    )
    _registrar_estado(app, contexto)
    for modulo in MODULOS:
        modulo.registrar(app, contexto)
    return app


def _registrar_estado(app: Dash, contexto: AppContext) -> None:
    app.clientside_callback(
        ClientsideFunction(namespace="rtA11y", function_name="alternarContraste"),
        Output("a11y-aplicado", "data"),
        Input("a11y-contraste", "value"),
    )

    @app.callback(
        Output("abas", "active_tab", allow_duplicate=True),
        Input({"type": "ir-aba", "aba": ALL, "origem": ALL}, "n_clicks"),
        prevent_initial_call=True,
    )
    def ir_para_aba(cliques):
        if not dash_ctx.triggered_id or not any(cliques):
            return no_update
        return dash_ctx.triggered_id["aba"]

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
        Output("f-mes-destaque", "value"),
        [Input(g, "clickData") for g in GRAFICOS_MES]
        + [
            Input("g-at-barras", "clickData"),
            Input("g-at-heatmap", "clickData"),
            Input("g-at-box", "clickData"),
            Input("grid-at-pacientes", "selectedRows"),
            Input("grid-jornada", "selectedRows"),
            Input("jo-ciclo", "value"),
            Input("url", "search"),
            Input("f-mes-destaque", "value"),
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
            return {}, no_update, None
        if gatilho == "f-mes-destaque":
            # equivalente, por teclado, ao clique num mês do gráfico (WCAG 2.1.1)
            if valor == selecao.get("mes"):
                return no_update, no_update, no_update
            selecao["mes"] = valor
        elif gatilho in GRAFICOS_MES and valor:
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
                return no_update, no_update, no_update
            selecao.update(paciente=str(valor[0]["paciente_id"]), ciclo=None)
        elif gatilho == "jo-ciclo" and valor is not None:
            if valor == selecao.get("ciclo"):
                return no_update, no_update, no_update
            selecao["ciclo"] = valor
        elif gatilho == "url" and valor:
            consulta = parse_qs(valor.lstrip("?"))
            if "paciente" in consulta:
                selecao.update(paciente=consulta["paciente"][0], ciclo=None)
                aba = "jornada"
        else:
            return no_update, no_update, no_update
        return selecao, aba, selecao.get("mes")

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
