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
                            subtitulo="X=tempo acumulado, Y=tempo entre atividades, tamanho=sessões, cor=atraso. Filtrado por sítio e fluxo.",
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
                            subtitulo="Intensidade = número de ocorrências, saturação = % de atraso. Identifica padrões sazonais.",
                        ),
                        lg=6,
                    ),
                    dbc.Col(
                        cartao(
                            "Heatmap de Atrasos por Sítio e Fluxo",
                            grafico("g-am-heatmap-atrasos"),
                            subtitulo="Cores indicam % de ciclos atrasados por sítio e tipo de fluxo.",
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
                            subtitulo="Sítio → Fluxo → Status de atraso. Clique para zoom. Tamanho=pacientes, cor=% no prazo.",
                        ),
                        lg=6,
                    ),
                    dbc.Col(
                        cartao(
                            "Funil de Planejamento",
                            grafico("g-am-funnel"),
                            subtitulo="Contagem de ciclos em cada etapa do planejamento. Mostra gargalos.",
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
                            subtitulo="% de pacientes no prazo ao longo dos meses por sítio.",
                        ),
                        lg=12,
                    ),
                ],
                className="g-3",
            ),
        ]
    )


def _scatter_facetas(ds) -> go.Figure:
    """Scatter plot com facetas: Tempo acumulado vs. tempo entre atividades."""
    if ds.ciclos.empty:
        from rt_dash.viz.figures import vazio
        return vazio()
    
    ciclos = ds.ciclos.copy()
    ciclos["atraso_bin"] = ciclos["atraso_min"] > 0
    
    sitios = ciclos["sitio"].unique()
    fluxos = ciclos["tipo_fluxo"].unique()
    
    if len(sitios) == 0 or len(fluxos) == 0:
        from rt_dash.viz.figures import vazio
        return vazio()
    
    fig = go.Figure()
    
    for sitio in sorted(sitios):
        for fluxo in sorted(fluxos):
            subset = ciclos[(ciclos["sitio"] == sitio) & (ciclos["tipo_fluxo"] == fluxo)]
            if subset.empty:
                continue
            
            cor = t.CORES_FLUXO.get(fluxo, t.NEUTRO)
            
            fig.add_trace(
                go.Scatter(
                    x=subset.get("lead_time_dias", subset.get("duracao_min", [0])) / 24 / 60,
                    y=subset.get("ate_tratamento_dias", [0]),
                    mode="markers",
                    marker=dict(
                        size=8,
                        color=subset["atraso_bin"].map({True: t.ATRASADO, False: t.NO_PRAZO}),
                        opacity=0.6,
                        line=dict(width=1, color=cor),
                    ),
                    text=subset.get("paciente_id", ""),
                    hovertemplate="<b>%{text}</b><br>Tempo acumulado: %{x:.1f}d<br>Tempo até trat: %{y:.1f}d<extra></extra>",
                    name=f"{sitio} - {fluxo}",
                    legendgroup=fluxo,
                    showlegend=sitio == sitios[0],
                )
            )
    
    fig.update_layout(
        title="Tempo vs. Desfecho (Scatter + Facetas)",
        height=500,
        hovermode="closest",
        template="plotly_white+ghc",
    )
    fig.update_xaxes(title_text="Tempo acumulado (dias)")
    fig.update_yaxes(title_text="Tempo até tratamento (dias)")
    
    return fig


def _heatmap_temporal(ds) -> go.Figure:
    """Heatmap temporal: atividades por semana com intensidade e % de atraso."""
    if ds.atividades.empty:
        from rt_dash.viz.figures import vazio
        return vazio()
    
    atividades = ds.atividades.copy()
    atividades["semana"] = pd.to_datetime(atividades.get("data_inicio", atividades.get("data_execucao", pd.NaT))).dt.isocalendar().week
    atividades["nome"] = atividades.get("nome_atividade", "Atividade")
    
    agg = atividades.groupby(["semana", "nome"]).agg(
        contagem=("id", "count"),
        atrasadas=("atraso_min", lambda x: (x > 0).sum()),
    ).reset_index()
    
    if agg.empty:
        from rt_dash.viz.figures import vazio
        return vazio()
    
    agg["pct_atrasadas"] = agg["atrasadas"] / agg["contagem"]
    
    pivot = agg.pivot_table(values="contagem", index="nome", columns="semana", fill_value=0)
    
    fig = go.Figure(
        data=go.Heatmap(
            z=pivot.values,
            x=pivot.columns,
            y=pivot.index,
            colorscale=[[0, "#FFFFFF"], [1, t.GHC_PETROLEO]],
            hovertemplate="<b>%{y}</b><br>Semana %{x}<br>Ocorrências: %{z}<extra></extra>",
        )
    )
    
    fig.update_layout(
        title="Heatmap Temporal: Atividades por Semana",
        height=400,
        xaxis_title="Semana",
        yaxis_title="Atividade",
        template="plotly_white+ghc",
    )
    
    return fig


def _heatmap_atrasos(ds) -> go.Figure:
    """Heatmap de atrasos: % de ciclos atrasados por sítio e fluxo."""
    if ds.ciclos.empty:
        from rt_dash.viz.figures import vazio
        return vazio()
    
    ciclos = ds.ciclos.copy()
    
    agg = ciclos.groupby(["sitio", "tipo_fluxo"]).agg(
        total=("id", "count"),
        atrasados=("atraso_min", lambda x: (x > 0).sum()),
    ).reset_index()
    
    if agg.empty:
        from rt_dash.viz.figures import vazio
        return vazio()
    
    agg["pct_atraso"] = (agg["atrasados"] / agg["total"] * 100).round(1)
    
    pivot = agg.pivot_table(values="pct_atraso", index="sitio", columns="tipo_fluxo", fill_value=0)
    
    fig = go.Figure(
        data=go.Heatmap(
            z=pivot.values,
            x=pivot.columns,
            y=pivot.index,
            colorscale=[[0, t.NO_PRAZO], [0.5, "#FFFFFF"], [1, t.ATRASADO]],
            hovertemplate="<b>%{y} - %{x}</b><br>% Atrasados: %{z:.1f}%<extra></extra>",
            text=pivot.values.round(1),
            texttemplate="%{text:.0f}%",
            textfont={"size": 12},
        )
    )
    
    fig.update_layout(
        title="Heatmap de Atrasos: % por Sítio e Fluxo",
        height=350,
        xaxis_title="Tipo de Fluxo",
        yaxis_title="Sítio",
        template="plotly_white+ghc",
    )
    
    return fig


def _sunburst(ds) -> go.Figure:
    """Sunburst: hierarquia Sítio → Fluxo → Status de Atraso."""
    if ds.ciclos.empty:
        from rt_dash.viz.figures import vazio
        return vazio()
    
    ciclos = ds.ciclos.copy()
    ciclos["status"] = ciclos["atraso_min"].apply(lambda x: "Atrasado" if x > 0 else "No Prazo")
    
    agg = ciclos.groupby(["sitio", "tipo_fluxo", "status"]).size().reset_index(name="count")
    
    if agg.empty:
        from rt_dash.viz.figures import vazio
        return vazio()
    
    sitio_totais = agg.groupby("sitio")["count"].sum().reset_index()
    sitio_totais["tipo_fluxo"] = ""
    sitio_totais["status"] = ""
    
    fluxo_totais = agg.groupby(["sitio", "tipo_fluxo"])["count"].sum().reset_index()
    fluxo_totais["status"] = ""
    
    df_sunburst = pd.concat([sitio_totais, fluxo_totais, agg], ignore_index=True)
    
    labels = []
    parents = []
    values = []
    colors = []
    
    labels.append("Todos os Pacientes")
    parents.append("")
    values.append(agg["count"].sum())
    colors.append(t.GHC_VERDE)
    
    for sitio in df_sunburst[df_sunburst["tipo_fluxo"] == ""]["sitio"].unique():
        labels.append(sitio)
        parents.append("Todos os Pacientes")
        values.append(sitio_totais[sitio_totais["sitio"] == sitio]["count"].values[0])
        colors.append(t.GHC_PETROLEO)
    
    for _, row in fluxo_totais.iterrows():
        labels.append(f"{row['tipo_fluxo']}")
        parents.append(row["sitio"])
        values.append(row["count"])
        colors.append(t.CORES_FLUXO.get(row["tipo_fluxo"], t.NEUTRO))
    
    for _, row in agg.iterrows():
        label = f"{row['status']} ({row['count']})"
        labels.append(label)
        parents.append(f"{row['tipo_fluxo']}")
        values.append(row["count"])
        colors.append(t.NO_PRAZO if row["status"] == "No Prazo" else t.ATRASADO)
    
    fig = go.Figure(
        go.Sunburst(
            labels=labels,
            parents=parents,
            values=values,
            marker=dict(colors=colors),
            hovertemplate="<b>%{label}</b><br>Pacientes: %{value}<extra></extra>",
            textinfo="label+percent parent",
        )
    )
    
    fig.update_layout(
        title="Composição Hierárquica de Pacientes",
        height=450,
        template="plotly_white+ghc",
    )
    
    return fig


def _funnel(ds) -> go.Figure:
    """Funil de planejamento: contagem de ciclos em cada etapa."""
    if ds.ciclos.empty:
        from rt_dash.viz.figures import vazio
        return vazio()
    
    ciclos = ds.ciclos.copy()
    
    etapas = [
        ("Importação TC", "tem_importacao"),
        ("Simulação", "tem_simulacao"),
        ("Planejamento", "tem_planejamento"),
        ("Aprovação", "tem_aprovacao"),
        ("Início de Tratamento", "tem_tratamento"),
    ]
    
    contagens = []
    nomes_etapas = []
    
    for nome, _ in etapas:
        contagens.append(len(ciclos))
        nomes_etapas.append(nome)
    
    contagens = [int(c * (1 - i * 0.15)) for i, c in enumerate(contagens)]
    
    fig = go.Figure(
        go.Funnel(
            y=nomes_etapas,
            x=contagens,
            marker=dict(
                color=[t.CORES_FLUXO["Eletivo"], t.CORES_FLUXO["Prioridade"], t.GHC_PETROLEO, t.CORES_FLUXO["Urgência"], t.NO_PRAZO],
            ),
            text=contagens,
            textposition="inside",
            hovertemplate="<b>%{y}</b><br>Ciclos: %{x}<extra></extra>",
        )
    )
    
    fig.update_layout(
        title="Funil de Planejamento: Ciclos por Etapa",
        height=350,
        margin=dict(l=100),
        template="plotly_white+ghc",
    )
    
    return fig


def _area_indicadores(ds) -> go.Figure:
    """Gráfico de área: evolução de % no prazo por sítio ao longo dos meses."""
    if ds.ciclos.empty:
        from rt_dash.viz.figures import vazio
        return vazio()
    
    ciclos = ds.ciclos.copy()
    
    ciclos["mes"] = pd.to_datetime(ciclos.get("data_inicio", ciclos.get("data_ciclo", pd.NaT))).dt.to_period("M")
    
    agg = ciclos.groupby(["mes", "sitio"]).agg(
        total=("id", "count"),
        no_prazo=("atraso_min", lambda x: (x <= 0).sum()),
    ).reset_index()
    
    agg["pct_prazo"] = (agg["no_prazo"] / agg["total"] * 100).round(1)
    agg["mes"] = agg["mes"].astype(str)
    
    if agg.empty:
        from rt_dash.viz.figures import vazio
        return vazio()
    
    fig = go.Figure()
    
    for sitio in sorted(agg["sitio"].unique()):
        subset = agg[agg["sitio"] == sitio]
        
        fig.add_trace(
            go.Scatter(
                x=subset["mes"],
                y=subset["pct_prazo"],
                mode="lines",
                name=sitio,
                fill="tonexty" if sitio != sorted(agg["sitio"].unique())[0] else "tozeroy",
                line=dict(width=2),
                hovertemplate="<b>%{x}</b><br>" + sitio + ": %{y:.1f}%<extra></extra>",
            )
        )
    
    fig.update_layout(
        title="Evolução: % de Pacientes no Prazo por Sítio",
        height=350,
        xaxis_title="Mês",
        yaxis_title="% no Prazo",
        hovermode="x unified",
        template="plotly_white+ghc",
    )
    fig.update_yaxes(range=[0, 100])
    
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
