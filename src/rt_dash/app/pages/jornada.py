"""Aba Jornada do Paciente: lista de pacientes e, para o paciente escolhido, cada ciclo de
planejamento com as atividades, a espera entre elas e a comparação com o tipo de fluxo."""

from __future__ import annotations

import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, State, dcc, html

from rt_dash.app.components import cartao, fmt_num, fmt_pct, grafico, kpi, seletor_unidade
from rt_dash.app.context import AppContext
from rt_dash.metrics.patient import faixa_referencia, tabela_pacientes
from rt_dash.viz import figures as fig

KPIS = [
    ("jo-k-fluxo", "Tipo de fluxo"),
    ("jo-k-lead", "Duração do ciclo"),
    ("jo-k-espera", "Espera somada"),
    ("jo-k-prazo", "Atividades no prazo"),
    ("jo-k-trat", "Até o início do tratamento"),
]

COLUNAS_PACIENTES = [
    {"field": "paciente_id", "headerName": "Paciente", "width": 115, "pinned": "left"},
    {"field": "n_ciclos", "headerName": "Ciclos", "width": 85, "type": "rightAligned"},
    {"field": "tipos_fluxo", "headerName": "Fluxo", "width": 150},
    {"field": "ultimo_inicio", "headerName": "Último ciclo", "width": 120},
    {"field": "lead_time_dias", "headerName": "Ciclo (dias)", "width": 115, "type": "rightAligned"},
    {"field": "espera_total_h", "headerName": "Espera (h)", "width": 110, "type": "rightAligned"},
    {"field": "pct_no_prazo", "headerName": "% no prazo", "width": 110, "type": "rightAligned"},
    {"field": "ate_tratamento_dias", "headerName": "Até tratar (dias)", "width": 135, "type": "rightAligned"},
    {"field": "sitio", "headerName": "Sítio", "width": 150},
]

COLUNAS_ATIVIDADES = [
    {"field": "ordem", "headerName": "#", "width": 60},
    {"field": "atividade", "headerName": "Atividade", "width": 260},
    {"field": "etapa", "headerName": "Etapa", "width": 140},
    {"field": "inicio", "headerName": "Início", "width": 125},
    {"field": "termino", "headerName": "Término", "width": 125},
    {"field": "espera_h", "headerName": "Espera (h)", "width": 105, "type": "rightAligned"},
    {"field": "duracao_min", "headerName": "Execução (min)", "width": 125, "type": "rightAligned"},
    {
        "field": "atraso_h",
        "headerName": "Atraso (h)",
        "width": 105,
        "type": "rightAligned",
        "cellClassRules": {"celula-atraso": "params.value > 0"},
    },
    {"field": "usuario", "headerName": "Usuário", "width": 110},
]


def layout(ctx: AppContext) -> html.Div:
    return dbc.Row(
        [
            dbc.Col(
                cartao(
                    "Pacientes",
                    dbc.Input(
                        id="jo-busca", placeholder="Buscar por ID, fluxo ou sítio…", type="search", className="mb-2"
                    ),
                    dag.AgGrid(
                        id="grid-jornada",
                        columnDefs=COLUNAS_PACIENTES,
                        rowData=[],
                        defaultColDef={"sortable": True, "filter": True, "resizable": True},
                        dashGridOptions={
                            "rowSelection": {"mode": "singleRow", "checkboxes": False, "enableClickSelection": True},
                            "pagination": True,
                            "paginationPageSize": 20,
                        },
                        getRowId="params.data.paciente_id",
                        style={"height": "760px"},
                        className="ag-theme-alpine",
                    ),
                    subtitulo="Clique num paciente para ver a jornada",
                ),
                xl=4,
            ),
            dbc.Col(
                [
                    html.Div(
                        className="cabecalho-paciente",
                        children=[
                            html.H2(id="jo-titulo", children="Selecione um paciente"),
                            dbc.RadioItems(
                                id="jo-ciclo",
                                options=[],
                                value=None,
                                inline=True,
                                inputClassName="btn-check",
                                labelClassName="chip",
                                labelCheckedClassName="chip-ativo",
                            ),
                            html.Div(
                                [html.Span("Unidade", className="rotulo-controle"), seletor_unidade("jo-unidade", "d")],
                                className="ms-auto d-flex align-items-center gap-2",
                            ),
                        ],
                    ),
                    html.Div([kpi(i, t) for i, t in KPIS], className="linha-kpis"),
                    cartao(
                        "Linha do tempo do ciclo",
                        grafico("g-jo-gantt"),
                        subtitulo="Cinza = espera desde a atividade anterior · vermelho = espera acima do P90 "
                        "da atividade · barra colorida = execução (cor da etapa) · traço = término "
                        "(verde no prazo, vermelho atrasado)",
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                cartao(
                                    "Quanto cada atividade somou ao ciclo",
                                    grafico("g-jo-cascata"),
                                    subtitulo="Espera + execução, em ordem",
                                ),
                                lg=6,
                            ),
                            dbc.Col(
                                cartao(
                                    "Paciente × mediana do mesmo tipo de fluxo",
                                    grafico("g-jo-comparacao"),
                                    subtitulo="Dias acumulados desde a importação da TC",
                                ),
                                lg=6,
                            ),
                        ],
                        className="g-3 mt-1",
                    ),
                    cartao(
                        "Atividades do ciclo",
                        dag.AgGrid(
                            id="grid-jo-atividades",
                            columnDefs=COLUNAS_ATIVIDADES,
                            rowData=[],
                            defaultColDef={"sortable": True, "resizable": True},
                            style={"height": "420px"},
                            className="ag-theme-alpine",
                            csvExportParams={"fileName": "jornada_paciente.csv"},
                        ),
                        dbc.Button("Exportar CSV", id="jo-exportar", color="light", size="sm", className="mt-2"),
                        classe="mt-3",
                    ),
                    dcc.Store(id="jo-dummy"),
                ],
                xl=8,
            ),
        ],
        className="g-3",
    )


def registrar(app: Dash, ctx: AppContext) -> None:
    @app.callback(
        Output("grid-jornada", "rowData"),
        Input("store-filtros", "data"),
        Input("store-selecao", "data"),
    )
    def lista(estado, selecao):
        ds = ctx.dados(estado, selecao, usar_mes=True)
        tab = tabela_pacientes(ds.ciclos, ds.cursos)
        tab["ultimo_inicio"] = tab["ultimo_inicio"].dt.strftime("%Y-%m-%d")
        for col, casas in (("lead_time_dias", 1), ("espera_total_h", 1), ("ate_tratamento_dias", 1)):
            tab[col] = tab[col].round(casas)
        tab["pct_no_prazo"] = (tab["pct_no_prazo"] * 100).round(0)
        return tab.to_dict("records")

    app.clientside_callback(
        "function(texto, opcoes){ return Object.assign({}, opcoes, {quickFilterText: texto || ''}); }",
        Output("grid-jornada", "dashGridOptions", allow_duplicate=True),
        Input("jo-busca", "value"),
        State("grid-jornada", "dashGridOptions"),
        prevent_initial_call=True,
    )

    app.clientside_callback(
        "function(n){ return !!n; }",
        Output("grid-jo-atividades", "exportDataAsCsv"),
        Input("jo-exportar", "n_clicks"),
        prevent_initial_call=True,
    )

    @app.callback(
        Output("jo-ciclo", "options"),
        Output("jo-ciclo", "value"),
        Output("jo-titulo", "children"),
        Input("store-selecao", "data"),
    )
    def ciclos_do_paciente(selecao):
        selecao = selecao or {}
        paciente = selecao.get("paciente")
        if not paciente:
            return [], None, "Selecione um paciente"
        c = ctx.ds.ciclos[ctx.ds.ciclos["paciente_id"] == paciente].sort_values("ciclo")
        opcoes = [
            {"label": f"Ciclo {r.ciclo} · {r.tipo_fluxo} · {r.inicio:%d/%m}", "value": int(r.ciclo)}
            for r in c.itertuples()
        ]
        valor = (
            selecao.get("ciclo")
            if selecao.get("ciclo") in set(c["ciclo"])
            else (int(c["ciclo"].iat[-1]) if len(c) else None)
        )
        return opcoes, valor, f"Paciente {paciente}"

    @app.callback(
        [Output(f"{i}-valor", "children") for i, _ in KPIS]
        + [Output(f"{i}-nota", "children") for i, _ in KPIS]
        + [
            Output("g-jo-gantt", "figure"),
            Output("g-jo-cascata", "figure"),
            Output("g-jo-comparacao", "figure"),
            Output("grid-jo-atividades", "rowData"),
        ],
        Input("jo-ciclo", "value"),
        Input("jo-unidade", "value"),
        State("store-selecao", "data"),
    )
    def jornada(ciclo, unidade, selecao):
        paciente = (selecao or {}).get("paciente")
        vazio = fig.vazio("Selecione um paciente na lista")
        if not paciente or ciclo is None:
            return (*["–"] * len(KPIS), *[""] * len(KPIS), vazio, vazio, vazio, [])
        cid = f"{paciente}-{ciclo}"
        j = ctx.ds.jornada[ctx.ds.jornada["ciclo_id"] == cid].sort_values("ordem")
        resumo = ctx.ds.ciclos[ctx.ds.ciclos["ciclo_id"] == cid].iloc[0]
        nome_un = fig.UNIDADES[unidade][0]
        valores = [
            resumo["tipo_fluxo"],
            f"{fmt_num(resumo['lead_time_dias'], 1)} dias",
            f"{fmt_num(fig.converter(resumo['espera_total_min'], unidade), 1)} {nome_un}",
            fmt_pct(resumo["pct_no_prazo"]),
            f"{fmt_num(resumo['ate_tratamento_dias'], 1)} dias"
            if resumo["ate_tratamento_dias"] == resumo["ate_tratamento_dias"]
            else "–",
        ]
        referencia = ctx.ds.ciclos[ctx.ds.ciclos["tipo_fluxo"] == resumo["tipo_fluxo"]]["lead_time_dias"].median()
        notas = [
            f"{fmt_num(resumo['n_atividades'])} atividades",
            f"mediana do fluxo: {fmt_num(referencia, 1)} dias",
            "soma das esperas positivas",
            f"{fmt_num(resumo['n_atrasadas'])} atrasadas",
            f"início em {resumo['inicio_tratamento']:%d/%m/%Y}"
            if resumo["inicio_tratamento"] == resumo["inicio_tratamento"]
            else "sem início registrado",
        ]
        faixa = faixa_referencia(ctx.ds.jornada, resumo["tipo_fluxo"])
        grade = j.assign(
            inicio=j["inicio"].dt.strftime("%d/%m %H:%M"),
            termino=j["termino"].dt.strftime("%d/%m %H:%M"),
            espera_h=(j["espera_min"] / 60).round(1),
            duracao_min=j["duracao_min"].round(0),
            atraso_h=(j["atraso_min"] / 60).round(1),
        )[[c["field"] for c in COLUNAS_ATIVIDADES]]
        return (
            *valores,
            *notas,
            fig.gantt_ciclo(j, ctx.limiar_espera),
            fig.cascata_ciclo(j, unidade),
            fig.comparacao_referencia(j, faixa),
            grade.to_dict("records"),
        )
