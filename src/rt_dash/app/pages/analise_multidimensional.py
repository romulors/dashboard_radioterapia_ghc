"""Aba Análise Multidimensional: novos gráficos interativos para exploração de dados em múltiplas dimensões.

Incluindo: Scatter + Facetas, Heatmap Temporal, Sunburst, Funnel, e Gráficos de Área.
"""

from __future__ import annotations

import traceback

import pandas as pd
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, html

from rt_dash.app.components import cartao, grafico
from rt_dash.app.context import AppContext
from rt_dash.viz import theme as t
from rt_dash.viz.figures import vazio


def layout(ctx: AppContext) -> html.Div:
    return html.Div(
        [
            html.Div(
                className="linha-controles",
                children=[
                    html.Span(
                        "Visualizações multidimensionais interativas para análise exploratória de dados.",
                        className="nota",
                    ),
                ],
            ),
            dbc.Row(
                [
                    dbc.Col(
                        cartao(
                            "Tempo vs. Desfecho (Scatter + Facetas)",
                            grafico("g-am-scatter-facetas"),
                            subtitulo="X=duração do ciclo, Y=até aprovação. Tamanho=atividades, cor=fluxo, contorno vermelho=com atraso.",
                        ),
                        lg=12,
                    ),
                ],
                className="g-3",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        cartao(
                            "Heatmap Temporal: Atividades por Semana",
                            grafico("g-am-heatmap-temporal"),
                            subtitulo="Intensidade = número de ciclos. Identifica padrões sazonais.",
                        ),
                        lg=6,
                    ),
                    dbc.Col(
                        cartao(
                            "Heatmap de Atrasos por Sítio e Fluxo",
                            grafico("g-am-heatmap-atrasos"),
                            subtitulo="% de ciclos com atraso (verde=no prazo, vermelho=atrasado).",
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
                            "Composição Hierárquica de Pacientes",
                            grafico("g-am-sunburst"),
                            subtitulo="Sítio → Fluxo → Status. Clique para ampliar.",
                        ),
                        lg=6,
                    ),
                    dbc.Col(
                        cartao(
                            "Funil de Planejamento",
                            grafico("g-am-funnel"),
                            subtitulo="Contagem de ciclos em cada etapa de planejamento.",
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
                            "Evolução de Indicadores por Sítio (Área)",
                            grafico("g-am-area-indicadores"),
                            subtitulo="% de pacientes no prazo ao longo do tempo.",
                        ),
                        lg=12,
                    ),
                ],
                className="g-3",
            ),
        ]
    )


PALETA = t.CORES_ADOBE_PALETTE1[:1] + t.CORES_ADOBE_PALETTE4[1:] + t.CORES_ADOBE_PALETTE1[3:] + t.CORES_ADOBE_PALETTE2[3:]


def _ciclos(ds) -> pd.DataFrame:
    """Ciclos com o sítio do paciente (o mais frequente nos cursos de tratamento)."""
    c = ds.ciclos.copy()
    sitio = (
        ds.cursos.dropna(subset=["sitio"]).groupby("paciente_id")["sitio"].agg(lambda s: s.mode().iat[0])
        if not ds.cursos.empty
        else pd.Series(dtype=object)
    )
    c["sitio"] = c["paciente_id"].map(sitio).fillna("Sem sítio")
    c["tipo_fluxo"] = c["tipo_fluxo"].fillna("Sem tipo")
    c["atrasado"] = c["n_atrasadas"] > 0
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
                    opacity=0.65,
                    line=dict(width=1, color=[t.ATRASADO if a else t.NO_PRAZO for a in g["atrasado"]]),
                ),
                customdata=g[["paciente_id", "sitio", "n_atividades"]].to_numpy(),
                hovertemplate=(
                    "<b>%{customdata[0]}</b> · %{customdata[1]}<br>Ciclo: %{x:.1f} d<br>"
                    "Até aprovação: %{y:.1f} d<br>Atividades: %{customdata[2]}<extra>" + fluxo + "</extra>"
                ),
            )
        )
    fig.update_xaxes(title_text="Duração do ciclo (dias)")
    fig.update_yaxes(title_text="Até aprovação (dias)")
    return _layout(fig, 460)


def _heatmap_temporal(ds) -> go.Figure:
    c = _ciclos(ds).dropna(subset=["mes"])
    if c.empty:
        return vazio()
    tab = c.groupby(["tipo_fluxo", "mes"]).size().unstack(fill_value=0).sort_index(axis=1)
    fig = go.Figure(
        go.Heatmap(
            z=tab.values,
            x=[t.rotulo_mes(m) for m in tab.columns],
            y=list(tab.index),
            colorscale=t.ESCALA_SEQUENCIAL,
            colorbar=dict(title="Ciclos"),
            hovertemplate="%{y} · %{x}<br>%{z} ciclos<extra></extra>",
        )
    )
    return _layout(fig, 360)


def _heatmap_atrasos(ds) -> go.Figure:
    c = _ciclos(ds)
    if c.empty:
        return vazio()
    tab = (c.groupby(["sitio", "tipo_fluxo"])["atrasado"].mean() * 100).unstack()
    fig = go.Figure(
        go.Heatmap(
            z=tab.values,
            x=list(tab.columns),
            y=list(tab.index),
            zmin=0,
            zmax=100,
            colorscale=[[0, t.NO_PRAZO], [0.5, "#FFFFFF"], [1, t.ATRASADO]],
            colorbar=dict(title="% atrasados"),
            hovertemplate="%{y} · %{x}<br>%{z:.0f}% dos ciclos com atraso<extra></extra>",
        )
    )
    return _layout(fig, 360)


def _sunburst(ds) -> go.Figure:
    c = _ciclos(ds)
    if c.empty:
        return vazio()
    n = c.groupby(["sitio", "tipo_fluxo", "status"]).size().reset_index(name="n")
    ids, labels, parents, values = [], [], [], []
    for s, gs in n.groupby("sitio"):
        ids.append(s); labels.append(s); parents.append(""); values.append(int(gs["n"].sum()))
        for f, gf in gs.groupby("tipo_fluxo"):
            ids.append(f"{s}|{f}"); labels.append(f); parents.append(s); values.append(int(gf["n"].sum()))
            for _, r in gf.iterrows():
                ids.append(f"{s}|{f}|{r['status']}")
                labels.append(r["status"]); parents.append(f"{s}|{f}"); values.append(int(r["n"]))
    fig = go.Figure(go.Sunburst(ids=ids, labels=labels, parents=parents, values=values, branchvalues="total"))
    fig.update_traces(
        marker=dict(colors=[t.ATRASADO if l == "Atrasado" else t.NO_PRAZO if l == "No prazo" else PALETA[hash(i.split("|")[0]) % len(PALETA)] for i, l in zip(ids, labels)])
    )
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
            marker=dict(color=PALETA[: len(etapas)]),
        )
    )
    return _layout(fig, 360)


def _area_indicadores(ds) -> go.Figure:
    c = _ciclos(ds).dropna(subset=["mes"])
    if c.empty:
        return vazio()
    top = c["sitio"].value_counts().head(6).index
    ev = c[c["sitio"].isin(top)].groupby(["mes", "sitio"]).size().unstack(fill_value=0).sort_index()
    fig = go.Figure()
    for i, s in enumerate(ev.columns):
        fig.add_trace(
            go.Scatter(
                x=[t.rotulo_mes(m) for m in ev.index],
                y=ev[s],
                name=s,
                mode="lines",
                stackgroup="um",
                line=dict(width=1, color=PALETA[i % len(PALETA)]),
            )
        )
    fig.update_yaxes(title_text="Ciclos de planejamento")
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
        Output("g-am-heatmap-temporal", "figure"),
        Output("g-am-heatmap-atrasos", "figure"),
        Output("g-am-sunburst", "figure"),
        Output("g-am-funnel", "figure"),
        Output("g-am-area-indicadores", "figure"),
        Input("store-filtros", "data"),
    )
    def atualizar_graficos(estado):
        ds = ctx.dados(estado)
        return tuple(
            _seguro(f, ds)
            for f in (_scatter_facetas, _heatmap_temporal, _heatmap_atrasos, _sunburst, _funnel, _area_indicadores)
        )
