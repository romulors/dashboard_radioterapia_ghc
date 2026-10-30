"""Aba Atendimento no Acelerador Linear: ocupação, turnos, espera e duração (P9, P10)."""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, html

from rt_dash.app.components import cartao, fmt_num, fmt_pct, grafico, kpi
from rt_dash.app.context import AppContext
from rt_dash.metrics.monthly import (
    duracao_media_sessao,
    ocupacao_acelerador,
    sessoes_por_tratamento,
    sessoes_por_turno,
)
from rt_dash.viz import figures as fig

KPIS = [
    ("al-k-sessoes", "Sessões"),
    ("al-k-ocupacao", "Ocupação média"),
    ("al-k-duracao", "Duração média da sessão"),
    ("al-k-espera", "Espera check-in → início"),
    ("al-k-pacientes", "Pacientes atendidos"),
]


def layout(ctx: AppContext) -> html.Div:
    vagas = ctx.settings.acelerador.vagas_por_dia
    return html.Div(
        [
            html.Div([kpi(i, t) for i, t in KPIS], className="linha-kpis"),
            dbc.Row(
                [
                    dbc.Col(
                        cartao(
                            "Taxa de ocupação do acelerador linear",
                            grafico("g-al-ocupacao"),
                            subtitulo=f"Sessões ÷ ({vagas} vagas/dia × dias com atendimento) · meta 80–85%",
                        ),
                        lg=6,
                    ),
                    dbc.Col(
                        cartao(
                            "Sessões – dia e noite",
                            grafico("g-al-turno"),
                            subtitulo="Dia: até 18h45 · Noite: a partir das 19h",
                        ),
                        lg=6,
                    ),
                ],
                className="g-3",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        cartao(
                            "Espera entre check-in e início do atendimento",
                            grafico("g-al-espera"),
                            subtitulo="P9 · atendimentos com espera entre −60 e 240 min",
                        ),
                        lg=6,
                    ),
                    dbc.Col(
                        cartao(
                            "Espera por hora agendada", grafico("g-al-espera-hora"), subtitulo="Mediana e faixa P25–P75"
                        ),
                        lg=6,
                    ),
                ],
                className="g-3 mt-1",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        cartao(
                            "Duração da sessão por sítio",
                            grafico("g-al-duracao-sitio"),
                            subtitulo="P10 · 12 sítios com mais sessões",
                        ),
                        lg=6,
                    ),
                    dbc.Col(
                        [
                            cartao("Tempo médio de duração das sessões", grafico("g-al-duracao")),
                            cartao(
                                "Número médio de sessões por tratamento", grafico("g-al-sessoes-trat"), classe="mt-3"
                            ),
                        ],
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
            Output("g-al-ocupacao", "figure"),
            Output("g-al-turno", "figure"),
            Output("g-al-espera", "figure"),
            Output("g-al-espera-hora", "figure"),
            Output("g-al-duracao-sitio", "figure"),
            Output("g-al-duracao", "figure"),
            Output("g-al-sessoes-trat", "figure"),
        ],
        Input("store-filtros", "data"),
        Input("store-selecao", "data"),
    )
    def atualizar(estado, selecao):
        ds = ctx.dados(estado)
        ds_sel = ctx.dados(estado, selecao, usar_mes=True)
        mes = (selecao or {}).get("mes")
        s = ds_sel.sessoes[ds_sel.sessoes["eh_tratamento"]]
        ocup = ocupacao_acelerador(ds_sel, ctx.settings)
        valores = [
            fmt_num(len(s)),
            fmt_pct(ocup["valor"].mean()),
            fmt_num(s.loc[s["duracao_valida"], "duracao_min"].mean(), 1, " min"),
            fmt_num(s["espera_checkin_min"].median(), 0, " min"),
            fmt_num(s["paciente_id"].nunique()),
        ]
        notas = [
            f"{fmt_pct((s['turno'] == 'Noite').mean())} à noite",
            "meta 80–85%",
            "exclui registros acima de 60 min",
            "mediana",
            f"{fmt_pct(s['internado'].mean())} das sessões de internados",
        ]
        return (
            *valores,
            *notas,
            fig.serie_mensal(
                ocupacao_acelerador(ds, ctx.settings),
                formato=".0%",
                meta=ctx.settings.meta_ocupacao_acelerador,
                media_meses=None,
                mes_selecionado=mes,
            ),
            fig.serie_mensal(sessoes_por_turno(ds, ctx.settings), tipo="barras_empilhadas", mes_selecionado=mes),
            fig.histograma_espera(s),
            fig.espera_por_hora(s),
            fig.duracao_por_sitio(s),
            fig.serie_mensal(duracao_media_sessao(ds, ctx.settings), formato=".1f", mes_selecionado=mes, altura=240),
            fig.serie_mensal(sessoes_por_tratamento(ds, ctx.settings), formato=".1f", mes_selecionado=mes, altura=240),
        )
