"""Componentes visuais reutilizáveis (cabeçalho, filtros, cartões)."""

from __future__ import annotations

import inspect

import dash_bootstrap_components as dbc
from dash import dcc, html

from rt_dash.app.ajuda import calculo
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
                children=html.Img(
                    src="/assets/ghc_logo.png",
                    alt="GHC · 100% SUS · Grupo Hospitalar Conceição",
                    className="ghc-logo-img",
                ),
            ),
            html.Div(
                className="ghc-titulo",
                children=[
                    html.H1("Indicadores Radioterapia"),
                    html.Span("Fluxo de planejamento e tratamento · Fonte: Sistema Aria", className="ghc-sub"),
                ],
            ),
            html.Div(
                className="ghc-acessibilidade",
                children=[
                    dbc.Switch(
                        id="a11y-contraste",
                        label="Alto contraste",
                        value=False,
                        persistence=True,
                        persistence_type="local",
                        className="switch-contraste",
                    ),
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


def grafico(id_: str, altura: int | None = None, descricao: str = "") -> html.Figure:
    """Gráfico acessível (WCAG 1.1.1 e 1.3.1): o resumo em texto e a tabela de dados são gerados dos próprios
    dados a cada atualização por `assets/a11y.js`; `descricao` é o texto inicial, antes do primeiro desenho."""
    estilo = {"height": f"{altura}px"} if altura else None
    texto_calculo = calculo(id_)
    ajuda = (
        [
            html.Button(
                "?",
                id=f"{id_}-ajuda",
                type="button",
                className="ajuda-calculo",
                **{"aria-label": "Como este indicador é calculado", "aria-describedby": f"{id_}-ajuda-texto"},
            ),
            dbc.Tooltip(
                [html.Strong("Como é calculado: "), texto_calculo],
                id=f"{id_}-ajuda-texto",
                target=f"{id_}-ajuda",
                placement="left",
                trigger="hover focus",
                className="ajuda-tooltip",
            ),
        ]
        if texto_calculo
        else []
    )
    return html.Figure(
        className="grafico-a11y",
        children=[
            *ajuda,
            dcc.Loading(
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
            ),
            html.Figcaption(descricao or "Carregando gráfico…", id=f"{id_}-alt", className="grafico-alt"),
            html.Details(
                [
                    html.Summary("Ver dados em tabela"),
                    html.Div(id=f"{id_}-tabela", className="grafico-tabela"),
                ],
                className="grafico-detalhes",
            ),
        ],
    )


def status_badge(codigo: str, texto: str) -> html.Span:
    """Situação frente à meta com ícone + palavra (nunca só cor, WCAG 1.4.1)."""
    icone, _ = t.STATUS.get(codigo, t.STATUS["sem_meta"])
    return html.Span(
        [html.Span(icone, className="status-icone", **{"aria-hidden": "true"}), " ", texto],
        className=f"status status-{codigo}",
    )


def kpi_meta(id_: str, titulo: str, destino: str | None = None) -> html.Div:
    """KPI de manchete: valor, situação frente à meta e link para a aba onde é analisado."""
    filhos = [
        html.H3(titulo, className="kpi-titulo"),
        html.Div("–", id=f"{id_}-valor", className="kpi-valor"),
        html.Div("", id=f"{id_}-status", className="kpi-status"),
        html.Div("", id=f"{id_}-nota", className="kpi-nota"),
    ]
    if destino:
        filhos.append(
            html.Button(
                f"Ver em {destino[1]} →",
                id={"type": "ir-aba", "aba": destino[0], "origem": id_},
                className="link-aba",
                n_clicks=0,
            )
        )
    return html.Div(filhos, className="kpi kpi-meta")


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
