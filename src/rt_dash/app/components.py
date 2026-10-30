"""Componentes visuais reutilizáveis (cabeçalho, filtros, cartões)."""

from __future__ import annotations

import inspect

import dash_bootstrap_components as dbc
from dash import dcc, html

from rt_dash.domain.activities import TIPOS_FLUXO
from rt_dash.viz import theme as t


def fmt_num(valor, casas: int = 0, sufixo: str = "") -> str:
    """Número no padrão brasileiro: 1.234,5"""
    if valor is None or valor != valor:  # None ou NaN
        return "–"
    texto = f"{valor:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return texto + sufixo


def fmt_pct(valor, casas: int = 0) -> str:
    return "–" if valor is None or valor != valor else fmt_num(valor * 100, casas, "%")


# Dash 4 mostra caixas numéricas ao lado do slider; aqui os índices dos meses não interessam.
_SEM_CAIXA_NUMERICA = (
    {"allow_direct_input": False} if "allow_direct_input" in inspect.signature(dcc.RangeSlider).parameters else {}
)


def cabecalho() -> html.Header:
    return html.Header(
        className="ghc-header",
        children=[
            html.Div(
                className="ghc-marca",
                children=[
                    html.Span("GHC", className="ghc-logo"),
                    html.Span("100% SUS", className="ghc-sus"),
                    html.Span("Grupo Hospitalar Conceição", className="ghc-grupo"),
                ],
            ),
            html.Div(
                className="ghc-titulo",
                children=[
                    html.H1("Indicadores Radioterapia"),
                    html.Span("Fluxo de planejamento e tratamento · Fonte: Sistema Aria", className="ghc-sub"),
                ],
            ),
        ],
    )


def barra_filtros(meses, sitios) -> html.Div:
    from rt_dash.viz.theme import rotulo_mes

    marcas = {i: rotulo_mes(m) for i, m in enumerate(meses)}
    return html.Div(
        className="barra-filtros",
        children=[
            html.Div(
                className="filtro filtro-periodo",
                children=[
                    html.Label("Período"),
                    dcc.RangeSlider(
                        id="f-periodo",
                        min=0,
                        max=len(meses) - 1,
                        step=1,
                        value=[0, len(meses) - 1],
                        marks=marcas,
                        allowCross=False,
                        pushable=0,
                        **_SEM_CAIXA_NUMERICA,
                    ),
                ],
            ),
            html.Div(
                className="filtro",
                children=[
                    html.Label("Tipo de fluxo"),
                    dbc.Checklist(
                        id="f-fluxo",
                        options=[{"label": f, "value": f} for f in TIPOS_FLUXO],
                        value=[],
                        inline=True,
                        className="chips-fluxo",
                        inputClassName="btn-check",
                        labelClassName="chip",
                        labelCheckedClassName="chip-ativo",
                    ),
                ],
            ),
            html.Div(
                className="filtro filtro-sitio",
                children=[
                    html.Label("Sítio"),
                    dcc.Dropdown(id="f-sitio", options=sitios, multi=True, placeholder="Todos"),
                ],
            ),
            html.Div(
                className="filtro",
                children=[
                    html.Label("Atendimento"),
                    dbc.RadioItems(
                        id="f-internado",
                        options=[
                            {"label": "Todos", "value": ""},
                            {"label": "Ambulatorial", "value": "ambulatorial"},
                            {"label": "Internado", "value": "internado"},
                        ],
                        value="",
                        inline=True,
                        inputClassName="btn-check",
                        labelClassName="chip",
                        labelCheckedClassName="chip-ativo",
                    ),
                ],
            ),
            dbc.Button("Limpar", id="f-limpar", color="light", className="botao-limpar"),
        ],
    )


def cartao(titulo: str, *conteudo, subtitulo: str | None = None, classe: str = "") -> dbc.Card:
    cab = [html.H3(titulo, className="cartao-titulo")]
    if subtitulo:
        cab.append(html.Div(subtitulo, className="cartao-sub"))
    return dbc.Card(dbc.CardBody([*cab, *conteudo]), className=f"cartao {classe}")


def kpi(id_: str, titulo: str) -> html.Div:
    """Cartão KPI; valor e nota são preenchidos por callback (id_-valor, id_-nota)."""
    return html.Div(
        className="kpi",
        children=[
            html.Div(titulo, className="kpi-titulo"),
            html.Div("–", id=f"{id_}-valor", className="kpi-valor"),
            html.Div("", id=f"{id_}-nota", className="kpi-nota"),
        ],
    )


def grafico(id_: str, altura: int | None = None) -> dcc.Graph:
    estilo = {"height": f"{altura}px"} if altura else None
    return dcc.Loading(
        dcc.Graph(
            id=id_,
            style=estilo,
            config={
                "displaylogo": False,
                "locale": "pt-BR",
                "modeBarButtonsToRemove": ["lasso2d", "select2d", "autoScale2d"],
                "toImageButtonOptions": {"format": "png", "scale": 2},
            },
        ),
        type="dot",
        color=t.GHC_PETROLEO,
    )


def seletor_unidade(id_: str, valor: str = "h") -> dbc.RadioItems:
    return dbc.RadioItems(
        id=id_,
        options=[{"label": "horas", "value": "h"}, {"label": "dias", "value": "d"}],
        value=valor,
        inline=True,
        inputClassName="btn-check",
        labelClassName="chip",
        labelCheckedClassName="chip-ativo",
    )
