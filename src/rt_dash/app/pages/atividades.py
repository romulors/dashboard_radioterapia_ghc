"""Aba Atividades: estatísticas por atividade, navegadas pelas etapas do fluxo (P3 a P8)."""

from __future__ import annotations

import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, html

from rt_dash.app.components import cartao, fmt_num, fmt_pct, grafico, kpi, seletor_unidade
from rt_dash.app.context import AppContext
from rt_dash.domain.activities import ETAPAS_FLUXO
from rt_dash.metrics.activity import METRICAS_TEMPO, estatisticas_por_atividade, evolucao_mensal
from rt_dash.viz import figures as fig

KPIS = [
    ("at-k-n", "Atividades concluídas"),
    ("at-k-prazo", "No prazo"),
    ("at-k-maior", "Maior mediana"),
    ("at-k-variavel", "Maior variabilidade (IQR)"),
    ("at-k-atraso", "Maior atraso mediano"),
]


def layout(ctx: AppContext) -> html.Div:
    etapas = [{"label": "Todas", "value": ""}] + [
        {"label": f"{i}. {e}", "value": e} for i, e in enumerate(ETAPAS_FLUXO, 1)
    ]
    return html.Div(
        [
            html.Div(
                className="fluxo-nav",
                children=[
                    html.Span("Etapa do fluxo", className="rotulo-controle"),
                    dbc.RadioItems(
                        id="at-etapa",
                        options=etapas,
                        value="",
                        inline=True,
                        className="fluxo-etapas",
                        inputClassName="btn-check",
                        labelClassName="etapa",
                        labelCheckedClassName="etapa-ativa",
                    ),
                ],
            ),
            html.Div(
                className="linha-controles",
                children=[
                    html.Span("Medida", className="rotulo-controle"),
                    dbc.RadioItems(
                        id="at-metrica",
                        options=[{"label": v, "value": k} for k, v in METRICAS_TEMPO.items()],
                        value="tempo_etapa_min",
                        inline=True,
                        inputClassName="btn-check",
                        labelClassName="chip",
                        labelCheckedClassName="chip-ativo",
                    ),
                    html.Span("Unidade", className="rotulo-controle ms-3"),
                    seletor_unidade("at-unidade"),
                ],
            ),
            html.Div([kpi(i, t) for i, t in KPIS], className="linha-kpis"),
            dbc.Row(
                [
                    dbc.Col(
                        cartao(
                            "Tempo por atividade",
                            grafico("g-at-barras"),
                            subtitulo="Barra = mediana · losango = P90 · clique numa atividade para detalhar",
                        ),
                        lg=6,
                    ),
                    dbc.Col(
                        [
                            cartao(
                                "Distribuição por tipo de fluxo",
                                html.Div(id="at-titulo-sel", className="selecao-atual"),
                                grafico("g-at-box"),
                                subtitulo="Clique num ponto para abrir a jornada do paciente",
                            ),
                            cartao("Evolução mensal da mediana", grafico("g-at-tendencia"), classe="mt-3"),
                        ],
                        lg=6,
                    ),
                ],
                className="g-3",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        cartao(
                            "Mediana por atividade e mês",
                            grafico("g-at-heatmap"),
                            subtitulo="Clique numa célula para selecionar a atividade",
                        ),
                        lg=6,
                    ),
                    dbc.Col(
                        cartao(
                            "Pacientes na atividade selecionada",
                            dag.AgGrid(
                                id="grid-at-pacientes",
                                columnDefs=[
                                    {"field": "paciente_id", "headerName": "Paciente", "width": 120},
                                    {"field": "ciclo", "headerName": "Ciclo", "width": 80},
                                    {"field": "tipo_fluxo", "headerName": "Fluxo", "width": 120},
                                    {"field": "termino", "headerName": "Término", "width": 130},
                                    {
                                        "field": "valor",
                                        "headerName": "Medida",
                                        "width": 110,
                                        "sort": "desc",
                                        "type": "rightAligned",
                                    },
                                    {
                                        "field": "atraso_h",
                                        "headerName": "Atraso (h)",
                                        "width": 110,
                                        "type": "rightAligned",
                                    },
                                ],
                                rowData=[],
                                defaultColDef={"sortable": True, "filter": True, "resizable": True},
                                dashGridOptions={
                                    "rowSelection": {
                                        "mode": "singleRow",
                                        "checkboxes": False,
                                        "enableClickSelection": True,
                                    },
                                    "pagination": True,
                                    "paginationPageSize": 12,
                                },
                                style={"height": "440px"},
                                className="ag-theme-alpine",
                            ),
                            subtitulo="Ordenados pela medida escolhida · clique numa linha para abrir a jornada",
                        ),
                        lg=6,
                    ),
                ],
                className="g-3 mt-1",
            ),
        ]
    )


def registrar(app: Dash, ctx: AppContext) -> None:
    @app.callback(
        [Output(f"{i}-valor", "children") for i, _ in KPIS]
        + [Output(f"{i}-nota", "children") for i, _ in KPIS]
        + [
            Output("g-at-barras", "figure"),
            Output("g-at-box", "figure"),
            Output("g-at-tendencia", "figure"),
            Output("g-at-heatmap", "figure"),
            Output("grid-at-pacientes", "rowData"),
            Output("at-titulo-sel", "children"),
        ],
        Input("store-filtros", "data"),
        Input("store-selecao", "data"),
        Input("at-etapa", "value"),
        Input("at-metrica", "value"),
        Input("at-unidade", "value"),
    )
    def atualizar(estado, selecao, etapa, metrica, unidade):
        selecao = selecao or {}
        ds_periodo = ctx.dados(estado)
        ds = ctx.dados(estado, selecao, usar_mes=True)
        j = ds.jornada if not etapa else ds.jornada[ds.jornada["etapa"] == etapa]
        est = estatisticas_por_atividade(j, metrica)
        atividade = selecao.get("atividade")
        if atividade not in set(est["atividade_generica"]):
            atividade = (
                est.sort_values("mediana", ascending=False)["atividade_generica"].iat[0] if not est.empty else None
            )
        nome_un = fig.UNIDADES[unidade][0]

        def conv(v):
            return fig.converter(v, unidade)

        if est.empty:
            valores = ["–"] * len(KPIS)
            notas = [""] * len(KPIS)
        else:
            maior = est.loc[est["mediana"].idxmax()]
            variavel = est.loc[est["iqr"].idxmax()]
            atraso = est.dropna(subset=["atraso_mediano_min"])
            atraso = atraso.loc[atraso["atraso_mediano_min"].idxmax()] if not atraso.empty else None
            valores = [
                fmt_num(len(j)),
                fmt_pct(j["no_prazo"].dropna().mean()),
                maior["atividade_generica"],
                variavel["atividade_generica"],
                atraso["atividade_generica"] if atraso is not None else "–",
            ]
            notas = [
                f"{fmt_num(j['ciclo_id'].nunique())} ciclos",
                "término até o vencimento",
                f"{fmt_num(conv(maior['mediana']), 1)} {nome_un}",
                f"IQR {fmt_num(conv(variavel['iqr']), 1)} {nome_un}",
                f"{fmt_num(atraso['atraso_mediano_min'] / 60, 1)} h quando atrasa" if atraso is not None else "",
            ]

        sel = j[j["atividade_generica"] == atividade] if atividade else j.iloc[0:0]
        sel_periodo = ds_periodo.jornada[ds_periodo.jornada["atividade_generica"] == atividade] if atividade else sel
        grade = sel.assign(
            valor=conv(sel[metrica]).round(1),
            atraso_h=(sel["atraso_min"] / 60).round(1),
            termino=sel["termino"].dt.strftime("%d/%m/%Y %H:%M"),
        )[["paciente_id", "ciclo", "tipo_fluxo", "termino", "valor", "atraso_h"]].sort_values("valor", ascending=False)
        ordem = est.sort_values("ordem")["atividade_generica"].tolist()
        jp = ds_periodo.jornada if not etapa else ds_periodo.jornada[ds_periodo.jornada["etapa"] == etapa]
        return (
            *valores,
            *notas,
            fig.barras_atividades(est, unidade, atividade),
            fig.box_por_fluxo(sel, metrica, unidade),
            fig.tendencia_por_fluxo(sel_periodo, metrica, unidade),
            fig.heatmap_atividade_mes(evolucao_mensal(jp, metrica), unidade, ordem),
            grade.to_dict("records"),
            f"Atividade: {atividade} · {METRICAS_TEMPO[metrica].lower()}" if atividade else "",
        )
