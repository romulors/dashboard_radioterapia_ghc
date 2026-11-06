"""Gráficos multidimensionais mantidos após a revisão: dispersão tempo × aprovação (Processos) e funil (Resultado).

Heatmaps, sunburst e área empilhada foram trocados por gráficos de posição e comprimento (ver `viz/novos.py`).
"""

from __future__ import annotations

import traceback

import pandas as pd
import plotly.graph_objects as go
from dash import Dash, Input, Output

from rt_dash.app.context import AppContext
from rt_dash.metrics.fluxo import ciclos_com_sitio
from rt_dash.viz import theme as t
from rt_dash.viz.figures import vazio


def _ciclos(ds) -> pd.DataFrame:
    """Ciclos com o sítio do paciente (o mais frequente nos cursos de tratamento)."""
    c = ciclos_com_sitio(ds.ciclos, ds.cursos)
    c["status"] = c["atrasado"].map({True: "Atrasado", False: "No prazo"})
    return c


def _layout(fig: go.Figure, altura: int) -> go.Figure:
    fig.update_layout(height=altura, margin=dict(l=50, r=20, t=20, b=50), hovermode="closest")
    return fig


def _scatter_facetas(ds) -> go.Figure:
    c = _ciclos(ds).dropna(subset=["lead_time_dias", "ate_aprovacao_dias"])
    if c.empty:
        return vazio()
    fig = go.Figure()
    for fluxo, g in c.groupby("tipo_fluxo"):
        fig.add_trace(
            go.Scatter(
                x=g["lead_time_dias"],
                y=g["ate_aprovacao_dias"],
                mode="markers",
                name=fluxo,
                marker=dict(
                    size=(g["n_atividades"].clip(upper=60) / 3 + 5),
                    color=t.CORES_FLUXO.get(fluxo, t.NEUTRO),
                    opacity=0.7,
                    # atraso por símbolo (◆) além da cor do contorno: WCAG 1.4.1
                    symbol=["diamond" if a else "circle" for a in g["atrasado"]],
                    line=dict(width=1, color=[t.ATRASADO if a else t.TEXTO for a in g["atrasado"]]),
                ),
                customdata=g[["paciente_id", "sitio", "n_atividades", "status"]].to_numpy(),
                hovertemplate=(
                    "<b>%{customdata[0]}</b> · %{customdata[1]}<br>Ciclo: %{x:.1f} d<br>"
                    "Até aprovação: %{y:.1f} d<br>Atividades: %{customdata[2]}<br>%{customdata[3]}"
                    "<extra>" + fluxo + "</extra>"
                ),
            )
        )
    fig.update_xaxes(title_text="Duração do ciclo (dias)")
    fig.update_yaxes(title_text="Até aprovação (dias)")
    return _layout(fig, 460)


def _funnel(ds) -> go.Figure:
    c = _ciclos(ds)
    if c.empty:
        return vazio()
    etapas = [
        ("Ciclos iniciados", len(c)),
        ("Com importação de TC", int(c["tem_importacao"].sum())),
        ("Plano aprovado", int(c["aprovacao"].notna().sum())),
        ("Tratamento iniciado", int(c["inicio_tratamento"].notna().sum())),
    ]
    fig = go.Figure(
        go.Funnel(
            y=[e[0] for e in etapas],
            x=[e[1] for e in etapas],
            textinfo="value+percent initial",
            marker=dict(color=t.PALETA_GRADIENTE[::-1][:4]),
        )
    )
    return _layout(fig, 360)


def _seguro(fn, ds) -> go.Figure:
    try:
        return fn(ds)
    except Exception as exc:
        traceback.print_exc()
        return vazio(f"Erro ao montar o gráfico: {exc}")


def registrar(app: Dash, ctx: AppContext) -> None:
    @app.callback(
        Output("g-am-scatter-facetas", "figure"),
        Output("g-am-funnel", "figure"),
        Input("store-filtros", "data"),
    )
    def atualizar_graficos(estado):
        ds = ctx.dados(estado)
        return tuple(_seguro(f, ds) for f in (_scatter_facetas, _funnel))
