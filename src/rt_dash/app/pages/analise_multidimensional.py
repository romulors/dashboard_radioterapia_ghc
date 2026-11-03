"""Aba Análise Multidimensional: novos gráficos interativos para exploração de dados em múltiplas dimensões.

Incluindo: Scatter + Facetas, Heatmap Temporal, Sunburst, Funnel, e Gráficos de Área.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, html

from rt_dash.app.components import cartao, grafico
from rt_dash.app.context import AppContext
from rt_dash.viz import theme as t


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
                            subtitulo="X=tempo acumulado, Y=tempo até aprovação. Tamanho=atividades, cor=% no prazo.",
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


def _scatter_facetas(ds) -> go.Figure:
    """Scatter plot: Lead time vs. tempo até aprovação, colorido por % no prazo."""
    if ds.ciclos.empty:
        return go.Figure().add_annotation(text="Sem dados")
    
    ciclos = ds.ciclos.copy()
    
    fig = go.Figure()
    for fluxo in sorted(ciclos["tipo_fluxo"].unique()):
        subset = ciclos[ciclos["tipo_fluxo"] == fluxo]
        cor = t.CORES_FLUXO.get(fluxo, t.NEUTRO)
        
        fig.add_trace(
            go.Scatter(
                x=subset["lead_time_dias"],
                y=subset["ate_aprovacao_dias"],
                mode="markers",
                marker=dict(
                    size=subset["n_atividades"],
                    color=subset["pct_no_prazo"].fillna(0),
                    colorscale="RdYlGn",
                    cmin=0,
                    cmax=1,
                    showscale=(fluxo == sorted(ciclos["tipo_fluxo"].unique())[0]),
                    colorbar=dict(title="% No Prazo"),
                    line=dict(width=1, color=cor),
                ),
                text=subset["paciente_id"],
                hovertemplate="<b>%{text}</b><br>Lead time: %{x:.1f}d<br>Até Aprovação: %{y:.1f}d<extra></extra>",
                name=fluxo,
            )
        )
    
    fig.update_layout(height=500, hovermode="closest", template="plotly_white")
    fig.update_xaxes(title_text="Lead Time (dias)")
    fig.update_yaxes(title_text="Até Aprovação (dias)")
    return fig


def _heatmap_temporal(ds) -> go.Figure:
    """Heatmap: Ciclos por mês."""
    if ds.ciclos.empty:
        return go.Figure().add_annotation(text="Sem dados")
    
    ciclos = ds.ciclos.copy()
    ciclos["mes_str"] = ciclos["mes"].dt.strftime("%b/%y")
    contagem = ciclos.groupby(["mes_str", "tipo_fluxo"]).size().unstack(fill_value=0)
    
    fig = go.Figure(
        data=go.Heatmap(
            x=contagem.columns,
            y=contagem.index,
            z=contagem.values,
            colorscale="Viridis",
        )
    )
    fig.update_layout(height=400, title="Ciclos por Mês e Fluxo")
    return fig


def _heatmap_atrasos(ds) -> go.Figure:
    """Heatmap: % de ciclos atrasados por sítio e fluxo."""
    if ds.ciclos.empty:
        return go.Figure().add_annotation(text="Sem dados")
    
    ciclos = ds.ciclos.copy()
    ciclos["atrasado"] = ciclos["n_atrasadas"] > 0
    atrasos = ciclos.groupby(["sitio", "tipo_fluxo"])["atrasado"].apply(lambda x: (x.sum() / len(x) * 100) if len(x) > 0 else 0)
    pivot = atrasos.unstack(fill_value=0)
    
    fig = go.Figure(
        data=go.Heatmap(
            x=pivot.columns,
            y=pivot.index,
            z=pivot.values,
            colorscale="RdYlGn_r",
            cmin=0,
            cmax=100,
        )
    )
    fig.update_layout(height=400, title="% Ciclos Atrasados")
    return fig


def _sunburst(ds) -> go.Figure:
    """Sunburst: Sítio → Fluxo → Status."""
    if ds.ciclos.empty:
        return go.Figure().add_annotation(text="Sem dados")
    
    ciclos = ds.ciclos.copy()
    ciclos["status"] = ciclos["pct_no_prazo"].fillna(0).apply(lambda x: "No Prazo" if x >= 0.5 else "Atrasado")
    
    contagem = ciclos.groupby(["sitio", "tipo_fluxo", "status"]).size().reset_index(name="count")
    
    fig = go.Figure(
        go.Sunburst(
            labels=["Total"] + contagem["sitio"].unique().tolist() + contagem["tipo_fluxo"].unique().tolist() + contagem["status"].unique().tolist(),
            parents=[""] + ["Total"] * len(contagem["sitio"].unique()) + contagem["sitio"].tolist() + contagem["sitio"].tolist(),
            values=[contagem["count"].sum()] + [contagem[contagem["sitio"] == s]["count"].sum() for s in contagem["sitio"].unique()] + contagem["count"].tolist(),
        )
    )
    fig.update_layout(height=500)
    return fig


def _funnel(ds) -> go.Figure:
    """Funnel: Estágios de planejamento."""
    if ds.ciclos.empty:
        return go.Figure().add_annotation(text="Sem dados")
    
    ciclos = ds.ciclos.copy()
    total = len(ciclos)
    com_importacao = (ciclos["tem_importacao"]).sum()
    com_aprovacao = (ciclos["aprovacao"].notna()).sum()
    
    fig = go.Figure(
        go.Funnel(
            x=[total, com_importacao, com_aprovacao],
            y=["Todos os Ciclos", "Com Importação", "Com Aprovação"],
        )
    )
    fig.update_layout(height=400)
    return fig


def _area_indicadores(ds) -> go.Figure:
    """Área: Evolução de % no prazo por sítio."""
    if ds.ciclos.empty:
        return go.Figure().add_annotation(text="Sem dados")
    
    ciclos = ds.ciclos.copy()
    evolucao = ciclos.groupby(["mes", "sitio"])["pct_no_prazo"].mean().unstack(fill_value=0) * 100
    
    fig = go.Figure()
    for sitio in evolucao.columns:
        fig.add_trace(
            go.Scatter(
                x=evolucao.index,
                y=evolucao[sitio],
                name=sitio,
                mode="lines",
                stackgroup="one",
                fillcolor=t.CORES_FLUXO.get(sitio, t.NEUTRO),
            )
        )
    
    fig.update_layout(height=400, hovermode="x unified", title="% Ciclos No Prazo")
    fig.update_yaxes(title_text="% No Prazo")
    return fig


def registrar(app: Dash, ctx: AppContext) -> None:
    """Registra callbacks para atualizar todos os gráficos."""
    
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
        
        return (
            _scatter_facetas(ds),
            _heatmap_temporal(ds),
            _heatmap_atrasos(ds),
            _sunburst(ds),
            _funnel(ds),
            _area_indicadores(ds),
        )
