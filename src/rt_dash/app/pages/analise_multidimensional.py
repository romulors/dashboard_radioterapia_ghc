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
from rt_dash.viz.alternativas import com_alternativas
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
    nomes = [e[0] for e in etapas]
    valores = [e[1] for e in etapas]
    cores = t.PALETA_GRADIENTE[::-1][:4]
    fig = go.Figure(
        go.Funnel(
            y=nomes,
            x=valores,
            textinfo="value+percent initial",
            marker=dict(color=cores),
            hovertemplate=(
                "%{y}: %{x} ciclos<br>%{percentInitial:.0%} do início"
                " · %{percentPrevious:.0%} da etapa anterior<extra></extra>"
            ),
        )
    )
    # Alternativas do catálogo: barras com a conversão escrita (M1) e cascata de perdas entre etapas (V8).
    base = valores[0] or 1
    barras = go.Figure(
        go.Bar(
            y=nomes,
            x=valores,
            orientation="h",
            marker_color=cores,
            text=[f"{v} ({v / base:.0%})".replace(".", ",") for v in valores],
            textposition="outside",
            hovertemplate="%{y}: %{x} ciclos<extra></extra>",
        )
    )
    barras.update_yaxes(autorange="reversed", automargin=True)
    barras.update_xaxes(title_text="ciclos")
    perdas = [valores[0]] + [valores[i] - valores[i - 1] for i in range(1, len(valores))]
    cascata = go.Figure(
        go.Waterfall(
            x=["Ciclos iniciados"] + [f"Perda até {n.lower()}" for n in nomes[1:]] + ["Tratamento iniciado"],
            y=perdas + [0],
            measure=["absolute"] + ["relative"] * (len(perdas) - 1) + ["total"],
            decreasing=dict(marker=dict(color=t.ATRASADO)),
            increasing=dict(marker=dict(color=t.GHC_PETROLEO)),
            totals=dict(marker=dict(color=t.GHC_VERDE)),
            connector=dict(line=dict(color=t.GRADE)),
            hovertemplate="%{x}: %{y} ciclos<extra></extra>",
        )
    )
    cascata.update_xaxes(tickangle=-20)
    cascata.update_yaxes(title_text="ciclos")
    return com_alternativas(
        _layout(fig, 360),
        "Funil",
        [("Barras com conversão", _layout(barras, 360)), ("Cascata de perdas", _layout(cascata, 360))],
    )


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
