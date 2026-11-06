"""Componentes visuais reutilizáveis (cabeçalho, filtros, cartões)."""

from __future__ import annotations

import inspect

import dash_bootstrap_components as dbc
from dash import dcc, html

from rt_dash.app.ajuda import calculo, meta_e_tolerancia
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


def _rotulo_filtro(texto: str) -> html.Span:
    return html.Span(texto, className="filtro-rotulo")


def _menu_checklist(id_: str, nome: str, opcoes: list[str]) -> dbc.DropdownMenu:
    """Menu suspenso com caixas de seleção (o rótulo do botão mostra o que está marcado)."""
    return dbc.DropdownMenu(
        id=f"{id_}-menu",
        label=[html.Span(f"{nome}: ", className="visually-hidden"), "Todos"],
        children=[
            dbc.Checklist(
                id=id_,
                options=[{"label": o, "value": o} for o in opcoes],
                value=[],
                className="menu-checklist",
                inputClassName="form-check-input",
            )
        ],
        color="light",
        className="menu-filtro",
        toggleClassName="menu-filtro-botao",
    )


def barra_filtros(meses, sitios) -> html.Div:
    """Barra compacta (alternativa A): uma linha de controles da mesma altura e, abaixo, a faixa com os filtros
    ativos (cada um removível) e a seleção atual."""
    from rt_dash.viz.theme import rotulo_mes

    opcoes_mes = [{"label": rotulo_mes(m), "value": i} for i, m in enumerate(meses)]
    opcoes_destaque = [{"label": rotulo_mes(m), "value": m.strftime("%Y-%m")} for m in meses]
    separador = html.Span(className="filtro-sep", **{"aria-hidden": "true"})
    barra = html.Div(
        className="barra-filtros barra-compacta",
        role="search",
        **{"aria-label": "Filtros do painel"},
        children=[
            html.Div(
                className="filtro-grupo",
                children=[
                    html.Label("Período", htmlFor="f-periodo-ini", className="filtro-rotulo"),
                    dcc.Dropdown(
                        id="f-periodo-ini",
                        options=opcoes_mes,
                        value=0,
                        clearable=False,
                        searchable=False,
                        className="dd-filtro dd-mes",
                    ),
                    html.Label("até", htmlFor="f-periodo-fim", className="filtro-ate"),
                    dcc.Dropdown(
                        id="f-periodo-fim",
                        options=opcoes_mes,
                        value=len(meses) - 1,
                        clearable=False,
                        searchable=False,
                        className="dd-filtro dd-mes",
                    ),
                ],
            ),
            separador,
            html.Div(
                className="filtro-grupo",
                children=[_rotulo_filtro("Fluxo"), _menu_checklist("f-fluxo", "Fluxo", TIPOS_FLUXO)],
            ),
            html.Div(
                className="filtro-grupo",
                children=[_rotulo_filtro("Sítio"), _menu_checklist("f-sitio", "Sítio", sitios)],
            ),
            separador,
            html.Div(
                className="filtro-grupo",
                role="radiogroup",
                **{"aria-label": "Atendimento"},
                children=[
                    _rotulo_filtro("Atendimento"),
                    dbc.RadioItems(
                        id="f-internado",
                        options=[
                            {"label": "Todos", "value": ""},
                            {"label": "Ambulatorial", "value": "ambulatorial"},
                            {"label": "Internado", "value": "internado"},
                        ],
                        value="",
                        inline=True,
                        className="segmentado",
                        inputClassName="btn-check",
                        labelClassName="segmento",
                        labelCheckedClassName="segmento-ativo",
                    ),
                ],
            ),
            html.Div(
                className="filtro-grupo ms-auto",
                children=[
                    html.Label("Mês em destaque", htmlFor="f-mes-destaque", className="filtro-rotulo"),
                    dcc.Dropdown(
                        id="f-mes-destaque",
                        options=opcoes_destaque,
                        placeholder="Nenhum",
                        searchable=False,
                        className="dd-filtro dd-mes",
                    ),
                ],
            ),
        ],
    )
    faixa = html.Div(
        className="faixa-ativos",
        children=[
            html.Span("Filtros ativos:", className="faixa-rotulo"),
            html.Div(id="filtros-ativos", className="faixa-tags", role="status", **{"aria-live": "polite"}),
            html.Div(id="chips-selecao", className="faixa-tags", role="status", **{"aria-live": "polite"}),
            html.Button("Limpar seleção", id="limpar-selecao", type="button", className="link-limpar"),
            html.Button("Limpar tudo", id="f-limpar", type="button", className="link-limpar ms-auto"),
        ],
    )
    return html.Div([barra, faixa], className="filtros-fixos")


def _controles_do_grafico(conteudo) -> tuple[html.Div | None, html.Div | None]:
    """Retira os controles (info e ações) do primeiro gráfico do cartão para colocá-los no cabeçalho."""
    for item in conteudo:
        filhos = getattr(item, "children", None)
        if (
            "grafico-a11y" in (getattr(item, "className", "") or "")
            and isinstance(filhos, list)
            and len(filhos) > 1
            and getattr(filhos[0], "className", "") == "grafico-cab-info"
        ):
            info, acoes = filhos[0], filhos[1]
            del filhos[:2]
            return info, acoes
    return None, None


def cartao(titulo: str, *conteudo, subtitulo: str | None = None, classe: str = "") -> dbc.Card:
    """Cartão com cabeçalho na ordem: ⓘ · título e subtítulo · 2/4 · alternar · expandir."""
    texto = [html.H3(titulo, className="cartao-titulo")]
    if subtitulo:
        texto.append(html.Div(subtitulo, className="cartao-sub"))
    info, acoes = _controles_do_grafico(conteudo)
    if info is None:
        return dbc.Card(dbc.CardBody([*texto, *conteudo]), className=f"cartao {classe}")
    cab = html.Div([info, html.Div(texto, className="cartao-cab-texto"), acoes], className="cartao-cab")
    return dbc.Card(dbc.CardBody([cab, *conteudo]), className=f"cartao {classe}")


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


# Gráficos cuja forma não admite outra renderização dos mesmos dados (mostram 1/1).
SEM_ALTERNATIVAS = {"g-nv-waffle", "g-sc-winloss", "g-jo-gantt", "g-jo-cascata", "g-sc-ocupacao", "g-sc-prazo"}


def _icone(nome: str) -> html.Span:
    """Ícone do Material Symbols (Google, Apache 2.0), servido de assets/icones como máscara CSS."""
    return html.Span(className=f"icone icone-{nome}", **{"aria-hidden": "true"})


def _dica(alvo: str, conteudo, posicao: str = "bottom", classe: str = "") -> dbc.Tooltip:
    return dbc.Tooltip(
        conteudo, target=alvo, placement=posicao, trigger="hover focus", className=f"ajuda-tooltip {classe}".strip()
    )


def _conteudo_info(id_: str) -> list:
    partes = []
    texto = calculo(id_)
    if texto:
        partes.append(html.P([html.Strong("Como é calculado: "), texto]))
    meta = meta_e_tolerancia(id_)
    if meta:
        alvo, tolerancia = meta
        partes.append(html.P([html.Strong("Meta: "), alvo]))
        if tolerancia:
            partes.append(html.P([html.Strong("Tolerância: "), tolerancia]))
    return partes or [html.P("Sem descrição de cálculo para este gráfico.")]


def grafico(id_: str, altura: int | None = None, descricao: str = "", alternativas: bool = True) -> html.Figure:
    """Gráfico acessível (WCAG 1.1.1 e 1.3.1): o resumo em texto e a tabela de dados são gerados dos próprios
    dados a cada atualização por `assets/a11y.js`; `descricao` é o texto inicial, antes do primeiro desenho.

    Controles (ordem pedida): ícone de informação (cálculo, meta e tolerância) à esquerda do título e, à direita,
    o índice da visualização (ex.: 2/4), o botão que alterna a visualização e o de expandir. Dentro de `cartao`,
    eles vão para o cabeçalho do cartão; fora dele, ficam no topo da própria figura.
    """
    estilo = {"height": f"{altura}px"} if altura else None
    alternativas = alternativas and id_ not in SEM_ALTERNATIVAS
    info = html.Div(
        [
            html.Button(
                _icone("info"),
                id=f"{id_}-info",
                type="button",
                className="grafico-btn grafico-info",
                **{"aria-label": "Como é calculado, meta e tolerância", "aria-describedby": f"{id_}-info-texto"},
            ),
            dbc.Tooltip(
                _conteudo_info(id_),
                id=f"{id_}-info-texto",
                target=f"{id_}-info",
                placement="bottom-start",
                trigger="hover focus",
                className="ajuda-tooltip tooltip-info",
            ),
        ],
        className="grafico-cab-info",
    )
    acoes = html.Div(
        [
            html.Span(
                "1/1",
                id=f"{id_}-variante",
                className="grafico-variante",
                title="Visualização 1 de 1",
                **{"aria-live": "polite", "aria-label": "Visualização 1 de 1"},
            ),
            html.Button(
                _icone("alternar"),
                id=f"{id_}-alternar",
                type="button",
                className="grafico-btn grafico-alternar",
                disabled=not alternativas,
                **{"data-grafico": id_, "aria-label": "Alternar visualização: mesmos dados em outro tipo de gráfico"},
            ),
            _dica(
                f"{id_}-alternar",
                [html.Strong("Alternar visualização: "), "mostra os mesmos dados em outro tipo de gráfico."],
            ),
            html.Button(
                _icone("expandir"),
                id=f"{id_}-expandir",
                type="button",
                className="grafico-btn grafico-expandir",
                **{
                    "data-grafico": id_,
                    "aria-label": "Expandir gráfico para a largura total da tela",
                    "aria-expanded": "false",
                },
            ),
            _dica(
                f"{id_}-expandir",
                [
                    html.Span(
                        [html.Strong("Expandir: "), "mostra só este gráfico, na largura total da tela."],
                        className="dica-expandir",
                    ),
                    html.Span(
                        [html.Strong("Recolher: "), "volta ao painel (ou tecle Esc)."], className="dica-recolher"
                    ),
                ],
                posicao="bottom-end",
                classe="tooltip-expandir",
            ),
        ],
        className="grafico-cab-acoes",
    )
    return html.Figure(
        className="grafico-a11y",
        **{"data-alternativas": "1" if alternativas else "0"},
        children=[
            info,
            acoes,
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
