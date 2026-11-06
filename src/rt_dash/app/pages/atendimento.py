"""Aba Atendimento no Acelerador Linear: ocupação, turnos, espera e duração (P9, P10)."""

from __future__ import annotations

from dash import Dash, Input, Output

from rt_dash.app.components import fmt_num, fmt_pct
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
