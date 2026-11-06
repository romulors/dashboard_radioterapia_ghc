"""Aba Produtividade (gestores): visão rápida de 4 indicadores."""

from __future__ import annotations

import pandas as pd
from dash import Dash, Input, Output

from rt_dash.app.components import fmt_num
from rt_dash.app.context import AppContext
from rt_dash.metrics.monthly import (
    pacientes_que_iniciaram,
    planejamentos_por_fluxo,
    sessoes_por_turno,
)
from rt_dash.viz import figures as fig
from rt_dash.viz.theme import rotulo_mes

KPIS = [
    ("prod-k-inicios", "Pacientes que iniciaram"),
    ("prod-k-sessoes", "Sessões"),
    ("prod-k-noite", "Sessões à noite"),
    ("prod-k-planej", "Planejamentos"),
]


def _comparar(serie: pd.DataFrame, mes: pd.Timestamp) -> tuple[float | None, str]:
    total = serie.groupby("mes")["valor"].sum().sort_index()
    atual = total.get(mes)
    anteriores = total[total.index < mes].tail(6)
    if atual is None or anteriores.empty:
        return atual, ""
    media = anteriores.mean()
    delta = (atual - media) / media if media else 0
    seta = "▲" if delta > 0.005 else "▼" if delta < -0.005 else "■"
    return atual, f"{seta} {fmt_num(abs(delta) * 100, 0, '%')} vs média 6 meses ({fmt_num(media, 0)})"


def registrar(app: Dash, ctx: AppContext) -> None:
    @app.callback(
        [Output(f"{i}-valor", "children") for i, _ in KPIS]
        + [Output(f"{i}-nota", "children") for i, _ in KPIS]
        + [
            Output("g-prod-inicios", "figure"),
            Output("g-prod-turno", "figure"),
            Output("g-prod-fluxo", "figure"),
            Output("g-prod-sitio", "figure"),
        ],
        Input("store-filtros", "data"),
        Input("prod-mes", "value"),
    )
    def atualizar(estado, mes_ref):
        ds = ctx.dados(estado)
        mes = pd.Timestamp(mes_ref)
        inicios = pacientes_que_iniciaram(ds, ctx.settings)
        turno = sessoes_por_turno(ds, ctx.settings)
        fluxo = planejamentos_por_fluxo(ds, ctx.settings)

        valores, notas = [], []
        for serie in (inicios, turno, turno[turno["serie"] == "Noite"], fluxo):
            v, n = _comparar(serie, mes)
            valores.append(fmt_num(v))
            notas.append(n)

        # Sítios: pacientes distintos tratados no mês de referência
        ds_mes = ctx.dados(estado, {"mes": mes_ref}, usar_mes=True)
        s = ds_mes.sessoes[ds_mes.sessoes["sitio"].notna()]
        por_sitio = (
            s.groupby("sitio")["paciente_id"].nunique().rename("pacientes").sort_values(ascending=False).reset_index()
        )
        f_sitio = fig.barras_sitio(por_sitio, top=15, altura=380)
        f_sitio.update_layout(
            title=dict(
                text=f"{rotulo_mes(mes)} · {fmt_num(s['paciente_id'].nunique())} pacientes",
                font=dict(size=13),
                y=0.98,
                yanchor="top",
            ),
            margin=dict(t=40),
        )
        return (
            *valores,
            *notas,
            fig.serie_mensal(inicios, meta_minima=ctx.settings.meta_pacientes_novos, mes_selecionado=mes_ref),
            fig.serie_mensal(turno, tipo="barras_empilhadas", mes_selecionado=mes_ref),
            fig.serie_mensal(fluxo, tipo="barras_agrupadas", mes_selecionado=mes_ref),
            f_sitio,
        )

    @app.callback(
        Output("prod-mes", "value"),
        Input("g-prod-inicios", "clickData"),
        Input("g-prod-turno", "clickData"),
        Input("g-prod-fluxo", "clickData"),
        prevent_initial_call=True,
    )
    def escolher_mes(*cliques):
        from dash import ctx as dash_ctx

        clique = dash_ctx.triggered[0]["value"] if dash_ctx.triggered else None
        if not clique:
            from dash import no_update

            return no_update
        return clique["points"][0]["customdata"]
