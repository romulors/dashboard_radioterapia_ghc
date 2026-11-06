"""Composição das abas: reorganiza os cartões de cada módulo de métricas por tipo de indicador.

Visão Geral · KPIs · Eficácia vs Eficiência · Resultado vs Tendência · Processos · Jornada do Paciente.
Cada gráfico/KPI aparece em uma única aba; os callbacks continuam nos módulos de `pages`.
"""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import dcc, html

from rt_dash.app.components import cartao, grafico, kpi
from rt_dash.app.context import AppContext
from rt_dash.app.pages import atendimento, atividades, jornada, produtividade, visao_geral
from rt_dash.metrics import REGISTRO
from rt_dash.viz.theme import rotulo_mes


def _secao(titulo: str, nota: str, *filhos) -> html.Div:
    return html.Div(
        [html.H2(titulo, className="secao-titulo"), html.Div(nota, className="secao-nota"), *filhos],
        className="secao",
    )


def _colunas(*colunas, lg: int = 6) -> dbc.Row:
    return dbc.Row([dbc.Col(c, lg=lg) for c in colunas], className="g-3 mt-1")


def _pilha(*cartoes) -> list:
    return [c if i == 0 else html.Div(c, className="mt-3") for i, c in enumerate(cartoes)]


def _cartao_registro(id_: str) -> dbc.Col:
    ind = REGISTRO[id_]
    sub = f"{ind.unidade} · origem {ind.origem}" + (f" · {ind.nota}" if ind.nota else "")
    return dbc.Col(cartao(ind.titulo, grafico(f"g-vg-{id_}"), subtitulo=sub), lg=6, xxl=4)


def visao_geral_aba(ctx: AppContext) -> html.Div:
    destaque = [i for i in visao_geral.APRESENTACAO if i in REGISTRO]
    cartoes = [_cartao_registro(i) for i in destaque]
    cartoes.append(
        dbc.Col(
            cartao("Pacientes tratados por sítio", grafico("g-vg-sitios"), subtitulo="pacientes distintos no período"),
            lg=6,
            xxl=4,
        )
    )
    modal = dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Indicadores Radioterapia · formato de apresentação")),
            dbc.ModalBody(
                [
                    html.Div(
                        [html.H2(REGISTRO[i].titulo, className="slide-titulo"), grafico(f"g-ap-{i}")], className="slide"
                    )
                    for i in visao_geral.APRESENTACAO
                ]
                + [
                    html.Div(
                        [html.H2("Pacientes tratados por sítio", className="slide-titulo"), grafico("g-ap-sitios")],
                        className="slide",
                    )
                ]
            ),
        ],
        id="vg-modal",
        fullscreen=True,
        is_open=False,
    )
    return html.Div(
        [
            html.Div(
                className="linha-controles",
                children=[
                    html.Span(
                        "Clique num mês de qualquer gráfico para filtrar as outras abas por ele.", className="nota"
                    ),
                    dbc.Button("Modo apresentação", id="vg-apresentar", className="botao-ghc ms-auto"),
                ],
            ),
            html.Div([kpi(i, t) for i, t in visao_geral.KPIS], className="linha-kpis"),
            dbc.Row(cartoes, className="g-3"),
            modal,
        ]
    )


def kpis_aba(ctx: AppContext) -> html.Div:
    opcoes = [{"label": rotulo_mes(m), "value": m.strftime("%Y-%m")} for m in ctx.meses]
    complementares = [i for i in REGISTRO if i not in visao_geral.APRESENTACAO]
    return html.Div(
        [
            html.Div(
                className="linha-controles",
                children=[
                    html.Span("Mês de referência", className="rotulo-controle"),
                    dcc.Dropdown(
                        id="prod-mes",
                        options=opcoes,
                        value=opcoes[-1]["value"],
                        clearable=False,
                        className="dropdown-mes",
                    ),
                    html.Span("Valores do mês, comparados à média dos 6 meses anteriores.", className="nota"),
                ],
            ),
            _secao(
                "Planejamento e tratamento",
                "Indicadores-chave do mês de referência.",
                html.Div([kpi(i, t) for i, t in produtividade.KPIS], className="linha-kpis"),
            ),
            _secao(
                "Acelerador linear",
                "Indicadores-chave do atendimento no período filtrado.",
                html.Div([kpi(i, t) for i, t in atendimento.KPIS], className="linha-kpis"),
            ),
            _secao(
                "Demais indicadores mensais",
                "Série mensal de cada indicador do registro que não está na Visão Geral.",
                dbc.Row([_cartao_registro(i) for i in complementares], className="g-3"),
            ),
        ]
    )


def eficacia_eficiencia_aba(ctx: AppContext) -> html.Div:
    vagas = ctx.settings.acelerador.vagas_por_dia
    eficacia = _secao(
        "Eficácia",
        "Os objetivos foram atingidos? Foco no resultado final.",
        *_pilha(
            cartao(
                "Taxa de ocupação do acelerador linear",
                grafico("g-al-ocupacao"),
                subtitulo=f"Sessões ÷ ({vagas} vagas/dia × dias com atendimento) · meta 80–85%",
            ),
            cartao(
                "Pacientes (sítios) que iniciaram tratamento",
                grafico("g-prod-inicios"),
                subtitulo="Pacientes distintos com 'Início do Tratamento' no mês",
            ),
            cartao(
                "Planejamentos Eletivos, Prioridades e Urgências",
                grafico("g-prod-fluxo"),
                subtitulo="Ciclos de planejamento por mês da aprovação",
            ),
            cartao("Pacientes tratados por sítio", grafico("g-prod-sitio")),
        ),
    )
    eficiencia = _secao(
        "Eficiência",
        "Quanto tempo e recurso foi gasto para chegar ao resultado?",
        *_pilha(
            cartao(
                "Espera entre check-in e início do atendimento",
                grafico("g-al-espera"),
                subtitulo="P9 · atendimentos com espera entre −60 e 240 min",
            ),
            cartao("Espera por hora agendada", grafico("g-al-espera-hora"), subtitulo="Mediana e faixa P25–P75"),
            cartao(
                "Duração da sessão por sítio", grafico("g-al-duracao-sitio"), subtitulo="P10 · 12 sítios com mais sessões"
            ),
            cartao("Tempo médio de duração das sessões", grafico("g-al-duracao")),
            cartao("Número médio de sessões por tratamento", grafico("g-al-sessoes-trat")),
        ),
    )
    return html.Div([_colunas(eficacia, eficiencia)])


def resultado_tendencia_aba(ctx: AppContext) -> html.Div:
    resultado = _secao(
        "Resultado",
        "O que já aconteceu: confirma o desempenho do período.",
        *_pilha(
            cartao(
                "Sessões de radioterapia – dia e noite",
                grafico("g-prod-turno"),
                subtitulo="Dia: até 18h45 · Noite: a partir das 19h",
            ),
            cartao("Sessões – dia e noite (acelerador)", grafico("g-al-turno"), subtitulo="Dia: até 18h45 · Noite: a partir das 19h"),
            cartao(
                "Funil de Planejamento",
                grafico("g-am-funnel"),
                subtitulo="Ciclos em cada etapa: iniciado, TC importada, aprovado, tratamento iniciado.",
            ),
        ),
    )
    tendencia = _secao(
        "Tendência",
        "Sinais antecipados: para onde o desempenho caminha.",
        *_pilha(
            cartao(
                "Evolução de ciclos por sítio (Área)",
                grafico("g-am-area-indicadores"),
                subtitulo="Ciclos de planejamento por mês e sítio.",
            ),
            cartao(
                "Heatmap Temporal: Ciclos por Mês e Fluxo",
                grafico("g-am-heatmap-temporal"),
                subtitulo="Intensidade = número de ciclos. Identifica padrões sazonais.",
            ),
            cartao(
                "Tempo vs. Desfecho (Scatter)",
                grafico("g-am-scatter-facetas"),
                subtitulo="X=duração do ciclo, Y=até aprovação. Tamanho=atividades, cor=fluxo, contorno vermelho=com atraso.",
            ),
        ),
    )
    return html.Div([_colunas(resultado, tendencia)])


def processos_aba(ctx: AppContext) -> html.Div:
    return html.Div(
        [
            atividades.layout(ctx),
            _colunas(
                cartao(
                    "Heatmap de Atrasos por Sítio e Fluxo",
                    grafico("g-am-heatmap-atrasos"),
                    subtitulo="% de ciclos com atraso (verde=no prazo, vermelho=atrasado).",
                ),
                cartao(
                    "Composição Hierárquica de Pacientes",
                    grafico("g-am-sunburst"),
                    subtitulo="Sítio → Fluxo → Status. Clique para ampliar.",
                ),
            ),
        ]
    )


ABAS = [
    ("visao-geral", "Visão Geral", visao_geral_aba),
    ("kpis", "KPIs", kpis_aba),
    ("eficacia-eficiencia", "Eficácia vs Eficiência", eficacia_eficiencia_aba),
    ("resultado-tendencia", "Resultado vs Tendência", resultado_tendencia_aba),
    ("processos", "Processos", processos_aba),
    ("jornada", "Jornada do Paciente", lambda ctx: jornada.layout(ctx)),
]
