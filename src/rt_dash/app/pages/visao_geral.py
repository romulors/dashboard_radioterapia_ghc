"""Aba Visão Geral: todos os indicadores mensais do registro + modo apresentação (formato agosto)."""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, State, html

from rt_dash.app.components import cartao, fmt_num, fmt_pct, grafico, kpi
from rt_dash.app.context import AppContext
from rt_dash.metrics import REGISTRO
from rt_dash.metrics.monthly import pacientes_por_sitio
from rt_dash.viz import figures as fig

# Indicadores do formato resumido de agosto/2026 (modo apresentação)
APRESENTACAO = ["inicios", "planejamentos_fluxo_pct", "planejamentos_fluxo", "sessoes_turno"]

KPIS = [
    ("vg-k-pacientes", "Pacientes em planejamento"),
    ("vg-k-ciclos", "Ciclos de planejamento"),
    ("vg-k-leadtime", "Mediana do ciclo (dias)"),
    ("vg-k-prazo", "Tarefas no prazo"),
    ("vg-k-ate-trat", "Importar TC → início (dias)"),
    ("vg-k-sessoes", "Sessões no AL"),
]


def _metas(ctx: AppContext) -> dict[str, tuple[float, float]]:
    return {"ocupacao_acelerador": ctx.settings.meta_ocupacao_acelerador}


def layout(ctx: AppContext) -> html.Div:
    cartoes = []
    for ind in REGISTRO.values():
        sub = f"{ind.unidade} · origem {ind.origem}" + (f" · {ind.nota}" if ind.nota else "")
        cartoes.append(dbc.Col(cartao(ind.titulo, grafico(f"g-vg-{ind.id}"), subtitulo=sub), lg=6, xxl=4))
    cartoes.append(
        dbc.Col(
            cartao("Pacientes tratados por sítio", grafico("g-vg-sitios"), subtitulo="pacientes distintos no período"),
            lg=6,
            xxl=4,
        )
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
            html.Div([kpi(i, t) for i, t in KPIS], className="linha-kpis"),
            dbc.Row(cartoes, className="g-3"),
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("Indicadores Radioterapia · formato de apresentação")),
                    dbc.ModalBody(
                        [
                            html.Div(
                                [html.H2(REGISTRO[i].titulo, className="slide-titulo"), grafico(f"g-ap-{i}")],
                                className="slide",
                            )
                            for i in APRESENTACAO
                        ]
                        + [
                            html.Div(
                                [
                                    html.H2("Pacientes tratados por sítio", className="slide-titulo"),
                                    grafico("g-ap-sitios"),
                                ],
                                className="slide",
                            )
                        ]
                    ),
                ],
                id="vg-modal",
                fullscreen=True,
                is_open=False,
            ),
        ]
    )


def registrar(app: Dash, ctx: AppContext) -> None:
    ids = list(REGISTRO)

    @app.callback(
        [Output(f"{i}-valor", "children") for i, _ in KPIS]
        + [Output(f"{i}-nota", "children") for i, _ in KPIS]
        + [Output(f"g-vg-{i}", "figure") for i in ids]
        + [Output("g-vg-sitios", "figure")],
        Input("store-filtros", "data"),
        Input("store-selecao", "data"),
    )
    def atualizar(estado, selecao):
        ds = ctx.dados(estado)
        mes = (selecao or {}).get("mes")
        c = ds.ciclos[ds.ciclos["tem_importacao"]]
        sess = ds.sessoes[ds.sessoes["eh_tratamento"]]
        valores = [
            fmt_num(c["paciente_id"].nunique()),
            fmt_num(len(c)),
            fmt_num(c["lead_time_dias"].median(), 1),
            fmt_pct(ds.jornada["no_prazo"].dropna().mean()),
            fmt_num(c["ate_tratamento_dias"].median(), 1),
            fmt_num(len(sess)),
        ]
        notas = [
            f"{fmt_num((c.groupby('paciente_id').size() > 1).sum())} com mais de um ciclo",
            "com importação de TC/radiografia",
            "importação → última atividade",
            "término ≤ vencimento",
            "mediana por ciclo",
            f"{fmt_pct((sess['turno'] == 'Noite').mean())} à noite",
        ]
        metas = _metas(ctx)
        figuras = [
            fig.serie_mensal(
                REGISTRO[i].calcular(ds, ctx.settings),
                formato=REGISTRO[i].formato,
                tipo=REGISTRO[i].grafico,
                meta=metas.get(i),
                mes_selecionado=mes,
                altura=280,
            )
            for i in ids
        ]
        return (*valores, *notas, *figuras, fig.barras_sitio(pacientes_por_sitio(ds), altura=280))

    @app.callback(
        [Output("vg-modal", "is_open")]
        + [Output(f"g-ap-{i}", "figure") for i in APRESENTACAO]
        + [Output("g-ap-sitios", "figure")],
        Input("vg-apresentar", "n_clicks"),
        State("store-filtros", "data"),
        prevent_initial_call=True,
    )
    def apresentar(_, estado):
        ds = ctx.dados(estado)
        figuras = [
            fig.serie_mensal(
                REGISTRO[i].calcular(ds, ctx.settings),
                formato=REGISTRO[i].formato,
                tipo=REGISTRO[i].grafico,
                altura=460,
            )
            for i in APRESENTACAO
        ]
        return True, *figuras, fig.barras_sitio(pacientes_por_sitio(ds), top=20, altura=520)
