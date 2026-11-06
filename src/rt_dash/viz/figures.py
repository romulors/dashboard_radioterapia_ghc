"""Fábrica de gráficos: cada função recebe DataFrames prontos e devolve uma Figure.

Os gráficos guardam o mês, a atividade ou o paciente em `customdata`, para que os
callbacks de clique façam a filtragem cruzada.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from rt_dash.viz import theme as t
from rt_dash.viz.alternativas import com_alternativas

UNIDADES = {"h": ("horas", 60.0), "d": ("dias", 60.0 * 24)}


def converter(minutos: pd.Series | float, unidade: str) -> pd.Series | float:
    return minutos / UNIDADES[unidade][1]


def vazio(mensagem: str = "Sem dados para os filtros atuais") -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(text=mensagem, showarrow=False, font=dict(color=t.TEXTO_SECUNDARIO, size=13))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    fig.update_layout(height=260, margin=dict(l=8, r=8, t=8, b=8))
    return fig


def _ordenar_meses(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values("mes").copy()
    df["rotulo"] = df["mes"].map(t.rotulo_mes)
    return df


_CORES_EXTRAS = t.PALETA_CATEGORICA


def _cor_serie(serie: str, i: int = 0) -> str:
    return t.CORES_FLUXO.get(serie) or t.CORES_TURNO.get(serie) or _CORES_EXTRAS[i % len(_CORES_EXTRAS)]


def serie_mensal(
    df: pd.DataFrame,
    formato: str = ",.0f",
    tipo: str = "linha",
    meta: tuple[float, float] | None = None,
    meta_minima: float | None = None,
    meta_rotulo: str | None = None,
    media_meses: int | None = 6,
    mes_selecionado: str | None = None,
    altura: int = 300,
) -> go.Figure:
    """Série mensal com uma ou mais séries (coluna `serie`).

    `meta_minima` desenha a linha de uma meta de limite único; `meta_rotulo` troca o texto padrão ("acima de").
    """
    if df.empty:
        return vazio()
    df = _ordenar_meses(df)
    if "serie" not in df.columns:
        df["serie"] = "Total"
    fig = go.Figure()
    ordem_series = [s for s in (*t.CORES_FLUXO, *t.CORES_TURNO) if s in set(df["serie"])]
    ordem_series += [s for s in df["serie"].unique() if s not in ordem_series]
    for i, serie in enumerate(ordem_series):
        d = df[df["serie"] == serie]
        cor = _cor_serie(serie, i) if serie != "Total" else t.GHC_PETROLEO
        texto = d["valor"].map(lambda v, f=formato: format(v, f).replace(",", "X").replace(".", ",").replace("X", "."))
        comum = dict(
            x=d["rotulo"],
            y=d["valor"],
            name=serie,
            customdata=d["mes"].dt.strftime("%Y-%m"),
            text=texto,
            hovertemplate=f"%{{x}}<br>{serie}: %{{y:{formato}}}<extra></extra>",
        )
        if tipo == "linha":
            fig.add_trace(
                go.Scatter(
                    **comum,
                    mode="lines+markers+text",
                    textposition="top center",
                    line=dict(color=cor, width=2.5),
                    marker=dict(size=7, color=cor),
                    textfont=dict(size=11, color=cor),
                    cliponaxis=False,
                )
            )
        else:
            fig.add_trace(
                go.Bar(
                    **comum,
                    marker_color=cor,
                    textposition="inside" if tipo != "barras_agrupadas" else "outside",
                    textfont=dict(size=11),
                    cliponaxis=False,
                )
            )
    if tipo in ("barras_empilhadas", "barras_100"):
        fig.update_layout(barmode="stack")
    elif tipo == "barras_agrupadas":
        fig.update_layout(barmode="group", bargap=0.25)
    if tipo == "barras_100" or "%" in formato:
        fig.update_yaxes(tickformat=".0%")
    if meta:
        fig.add_hrect(
            y0=meta[0],
            y1=meta[1],
            fillcolor=t.GHC_AGUA,
            opacity=0.25,
            line_width=0,
            annotation_text=f"Meta {meta[0]:.0%}–{meta[1]:.0%}",
            annotation_position="top left",
            annotation_font=dict(size=11, color=t.GHC_VERDE),
        )
    if meta_minima is not None:
        fig.add_hline(
            y=meta_minima,
            line=dict(color=t.GHC_VERDE, dash="dash", width=1.5),
            annotation_text=meta_rotulo or f"Meta: acima de {format(meta_minima, formato)}",
            annotation_position="top left" if tipo == "linha" else "top right",
            annotation_font=dict(size=11, color=t.GHC_VERDE),
            annotation_bgcolor=t.CARTAO,  # legível sobre as barras empilhadas
        )
    if media_meses and tipo == "linha" and len(ordem_series) == 1:
        media = df.groupby("mes")["valor"].sum().sort_index().tail(media_meses).mean()
        fig.add_hline(
            y=media,
            line=dict(color=t.NEUTRO, dash="dot", width=1),
            annotation_text=f"Média {media_meses} meses: {format(media, formato)}",
            annotation_position="bottom right",
            annotation_font=dict(size=11, color=t.TEXTO_SECUNDARIO),
        )
    if mes_selecionado:
        rot = t.rotulo_mes(pd.Timestamp(mes_selecionado))
        if rot in set(df["rotulo"]):
            fig.add_vrect(x0=rot, x1=rot, line=dict(color=t.GHC_VERDE, width=12), opacity=0.12)
    fig.update_xaxes(type="category", categoryorder="array", categoryarray=list(dict.fromkeys(df["rotulo"])))
    if tipo == "linha":
        total = df.groupby("mes")["valor"].sum() if len(ordem_series) == 1 else df["valor"]
        folga = (total.max() - total.min()) * 0.15 or abs(total.max()) * 0.1 or 1
        limites = [*(meta or ()), *([meta_minima] if meta_minima is not None else [])]
        baixo = min([total.min(), *limites]) - folga
        alto = max([total.max(), *limites]) + folga
        fig.update_yaxes(range=[baixo, alto])
    elif meta_minima is not None and tipo == "barras_empilhadas":
        topo = df.groupby("mes")["valor"].sum().max()
        fig.update_yaxes(range=[0, max(topo, meta_minima) * 1.12])
    fig.update_layout(height=altura, showlegend=len(ordem_series) > 1, clickmode="event")
    return fig


def barras_sitio(df: pd.DataFrame, top: int = 15, altura: int = 420) -> go.Figure:
    if df.empty:
        return vazio()
    d = df.head(top).iloc[::-1]
    fig = go.Figure(
        go.Bar(
            x=d["pacientes"],
            y=d["sitio"],
            orientation="h",
            marker_color=t.GHC_PETROLEO,
            text=d["pacientes"],
            textposition="outside",
            customdata=d["sitio"],
            hovertemplate="%{y}: %{x} pacientes<extra></extra>",
            cliponaxis=False,
        )
    )
    fig.update_layout(height=altura, margin=dict(l=8, r=32, t=16, b=24))
    fig.update_yaxes(automargin=True)
    fig.update_xaxes(showticklabels=False, showgrid=False)
    return fig


def sitios_por_mes(df: pd.DataFrame, top: int = 8, altura: int = 360) -> go.Figure:
    """Pacientes distintos por sítio e mês, para os `top` sítios mais frequentes (heatmap)."""
    if df.empty:
        return vazio()
    principais = df.groupby("sitio")["pacientes"].sum().nlargest(top).index
    p = df[df["sitio"].isin(principais)].pivot_table(
        index="sitio", columns="mes", values="pacientes", aggfunc="sum", fill_value=0
    )
    p = p.loc[principais[::-1]]
    fig = go.Figure(
        go.Heatmap(
            z=p.values,
            x=[t.rotulo_mes(m) for m in p.columns],
            y=p.index,
            colorscale=t.ESCALA_SEQUENCIAL,
            text=p.values,
            texttemplate="%{text}",
            showscale=False,
            hovertemplate="%{y} · %{x}: %{z} pacientes<extra></extra>",
            xgap=2,
            ygap=2,
        )
    )
    fig.update_layout(height=altura, margin=dict(l=8, r=8, t=16, b=32))
    fig.update_yaxes(automargin=True)
    return fig


def barras_atividades(
    est: pd.DataFrame, unidade: str, selecionada: str | None = None, altura: int | None = None
) -> go.Figure:
    """Mediana por atividade (barra) com o P90 (losango) — P3 e P8."""
    if est.empty:
        return vazio()
    d = est.sort_values("ordem", ascending=False)
    nome, _ = UNIDADES[unidade]
    cores = [
        t.GHC_VERDE if a == selecionada else t.CORES_ETAPA.get(e, t.NEUTRO)
        for a, e in zip(d["atividade_generica"], d["etapa"], strict=False)
    ]
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=converter(d["mediana"], unidade),
            y=d["atividade_generica"],
            orientation="h",
            name="Mediana",
            marker=dict(
                color=cores,
                line=dict(width=[2 if a == selecionada else 0 for a in d["atividade_generica"]], color=t.TEXTO),
            ),
            customdata=d[["atividade_generica", "n"]],
            hovertemplate="%{y}<br>Mediana: %{x:.1f} " + nome + "<br>n = %{customdata[1]}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=converter(d["p90"], unidade),
            y=d["atividade_generica"],
            mode="markers",
            name="P90",
            marker=dict(symbol="diamond", size=9, color=t.TEXTO, line=dict(width=1, color=t.CARTAO)),
            customdata=d[["atividade_generica", "n"]],
            hovertemplate="%{y}<br>P90: %{x:.1f} " + nome + "<extra></extra>",
        )
    )
    fig.update_layout(height=altura or 26 * len(d) + 110, margin=dict(l=8, r=16, t=36, b=36), clickmode="event")
    fig.update_xaxes(title_text=nome, rangemode="tozero", showgrid=True, gridcolor=t.GRADE)
    fig.update_yaxes(dtick=1)
    fig.update_yaxes(automargin=True)
    return fig


def box_por_fluxo(jornada: pd.DataFrame, metrica: str, unidade: str, altura: int = 300) -> go.Figure:
    """Distribuição da métrica por tipo de fluxo — P4 e P5."""
    if jornada.empty:
        return vazio("Selecione uma atividade")
    nome, _ = UNIDADES[unidade]
    fig = go.Figure()
    for tipo in t.CORES_FLUXO:
        d = jornada[jornada["tipo_fluxo"] == tipo]
        if d.empty:
            continue
        fig.add_trace(
            go.Box(
                y=converter(d[metrica], unidade),
                name=tipo,
                marker_color=t.CORES_FLUXO[tipo],
                boxpoints="outliers",
                customdata=d[["paciente_id", "ciclo"]],
                hovertemplate="Paciente %{customdata[0]} · ciclo %{customdata[1]}<br>%{y:.1f} "
                + nome
                + "<extra></extra>",
            )
        )
    fig.update_layout(height=altura, showlegend=False, clickmode="event")
    fig.update_yaxes(title_text=nome)
    return fig


def tendencia_por_fluxo(jornada: pd.DataFrame, metrica: str, unidade: str, altura: int = 260) -> go.Figure:
    """Mediana mensal por tipo de fluxo — P6."""
    if jornada.empty:
        return vazio("Selecione uma atividade")
    nome, _ = UNIDADES[unidade]
    g = jornada.groupby(["mes", "tipo_fluxo"])[metrica].median().reset_index()
    g = _ordenar_meses(g)
    fig = go.Figure()
    for tipo in t.CORES_FLUXO:
        d = g[g["tipo_fluxo"] == tipo]
        if d.empty:
            continue
        fig.add_trace(
            go.Scatter(
                x=d["rotulo"],
                y=converter(d[metrica], unidade),
                name=tipo,
                mode="lines+markers",
                line=dict(color=t.CORES_FLUXO[tipo], width=2),
                hovertemplate="%{x} · " + tipo + ": %{y:.1f} " + nome + "<extra></extra>",
            )
        )
    fig.update_xaxes(type="category", categoryorder="array", categoryarray=list(dict.fromkeys(g["rotulo"])))
    fig.update_yaxes(title_text=f"mediana ({nome})", rangemode="tozero")
    fig.update_layout(height=altura)
    return fig


def heatmap_atividade_mes(pivot: pd.DataFrame, unidade: str, ordem: list[str], altura: int | None = None) -> go.Figure:
    if pivot.empty:
        return vazio()
    nome, _ = UNIDADES[unidade]
    p = pivot.reindex([a for a in ordem if a in pivot.index][::-1])
    z = converter(p, unidade)
    fig = go.Figure(
        go.Heatmap(
            z=z.values,
            x=[t.rotulo_mes(m) for m in p.columns],
            y=p.index,
            colorscale=t.ESCALA_SEQUENCIAL,
            texttemplate="%{z:.1f}",
            textfont=dict(size=10),
            colorbar=dict(title=nome, thickness=10),
            customdata=[[a] * len(p.columns) for a in p.index],
            hovertemplate="%{y} · %{x}<br>mediana: %{z:.1f} " + nome + "<extra></extra>",
            xgap=1,
            ygap=1,
        )
    )
    fig.update_layout(height=altura or 24 * len(p) + 90, margin=dict(l=8, r=8, t=16, b=32))
    fig.update_yaxes(automargin=True, dtick=1)
    return fig


def gantt_ciclo(ciclo: pd.DataFrame, limiar_espera: pd.Series | None = None, altura: int | None = None) -> go.Figure:
    """Linha do tempo das atividades de um ciclo: espera (clara ou vermelha se > P90) e execução."""
    if ciclo.empty:
        return vazio("Selecione um paciente na lista")
    c = ciclo.sort_values("ordem").copy()
    c["rotulo"] = c["ordem"].map("{:02d}".format) + ". " + c["atividade"]
    inicio_espera = c["inicio"] - pd.to_timedelta(c["espera_min"].clip(lower=0), unit="m")
    limiar = None
    if limiar_espera is not None and not limiar_espera.empty:
        limiar = [limiar_espera.get((a, f)) for a, f in zip(c["atividade_generica"], c["tipo_fluxo"], strict=False)]
    gargalo = [
        bool(lim is not None and pd.notna(lim) and esp > lim and esp > 60)
        for esp, lim in zip(c["espera_min"], limiar or [None] * len(c), strict=False)
    ]
    horas = c["espera_min"] / 60
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            y=c["rotulo"],
            x=(c["inicio"] - inicio_espera) / pd.Timedelta(milliseconds=1),
            base=inicio_espera,
            orientation="h",
            name="Espera",
            marker=dict(
                color=[t.ATRASADO if g else "#D7DEE2" for g in gargalo], opacity=[0.75 if g else 1 for g in gargalo]
            ),
            customdata=list(zip(horas.round(1), ["acima do P90" if g else "" for g in gargalo], strict=True)),
            hovertemplate="%{y}<br>Espera: %{customdata[0]} h %{customdata[1]}<extra></extra>",
        )
    )
    duracao_ms = (c["termino"] - c["inicio"]) / pd.Timedelta(milliseconds=1)
    fig.add_trace(
        go.Bar(
            y=c["rotulo"],
            x=duracao_ms.clip(lower=15 * 60 * 1000),
            base=c["inicio"],
            orientation="h",
            name="Execução",
            marker_color=[t.CORES_ETAPA.get(e, t.NEUTRO) for e in c["etapa"]],
            customdata=c[["etapa", "duracao_min", "atraso_min", "usuario"]].assign(
                inicio=c["inicio"].dt.strftime("%d/%m %H:%M"),
                termino=c["termino"].dt.strftime("%d/%m %H:%M"),
                prazo=c["atraso_min"].map(
                    lambda m: "no prazo" if m <= 0 else f"atraso {m / 60:.1f} h" if pd.notna(m) else "sem prazo"
                ),
            )[["etapa", "duracao_min", "inicio", "termino", "prazo", "usuario"]],
            hovertemplate=(
                "%{y}<br>%{customdata[0]}<br>%{customdata[2]} → %{customdata[3]}"
                "<br>Execução: %{customdata[1]:.0f} min · %{customdata[4]}<br>Usuário: %{customdata[5]}<extra></extra>"
            ),
        )
    )
    fig.add_trace(
        go.Scatter(
            y=c["rotulo"],
            x=c["termino"],
            mode="markers",
            name="Término",
            showlegend=False,
            hoverinfo="skip",
            marker=dict(
                symbol="line-ns-open",
                size=10,
                color=[t.ATRASADO if a > 0 else t.NO_PRAZO for a in c["atraso_min"].fillna(0)],
            ),
        )
    )
    fig.update_layout(
        barmode="overlay",
        height=altura or max(300, 26 * len(c) + 80),
        margin=dict(l=8, r=16, t=36, b=32),
        legend=dict(orientation="h", y=1.02, x=0),
    )
    fig.update_yaxes(autorange="reversed", automargin=True)
    fig.update_xaxes(type="date", showgrid=True, gridcolor=t.GRADE, tickformat="%d/%m")
    # Alternativas do catálogo: marcos do ciclo (S2) e espera × execução em horas (P3).
    marcos = go.Figure(
        go.Scatter(
            x=c["termino"],
            y=c["rotulo"],
            mode="markers+lines",
            line=dict(color=t.GRADE, width=1),
            marker=dict(
                size=11,
                color=[t.CORES_ETAPA.get(e, t.NEUTRO) for e in c["etapa"]],
                symbol=["diamond" if a > 0 else "circle" for a in c["atraso_min"].fillna(0)],
                line=dict(width=1, color=t.TEXTO),
            ),
            customdata=c[["etapa"]].assign(t=c["termino"].dt.strftime("%d/%m %H:%M")).to_numpy(),
            hovertemplate="%{y}<br>%{customdata[0]}<br>Término: %{customdata[1]}<extra></extra>",
            name="Término",
        )
    )
    marcos.update_yaxes(autorange="reversed", automargin=True)
    marcos.update_xaxes(type="date", showgrid=True, gridcolor=t.GRADE, tickformat="%d/%m")
    marcos.update_layout(height=fig.layout.height, margin=dict(l=8, r=16, t=36, b=32), showlegend=False)
    horas_exec = ((c["termino"] - c["inicio"]) / pd.Timedelta(hours=1)).clip(lower=0)
    barras = go.Figure(
        [
            go.Bar(
                y=c["rotulo"],
                x=horas.clip(lower=0),
                orientation="h",
                name="Espera (h)",
                marker_color="#D7DEE2",
                hovertemplate="%{y}<br>Espera: %{x:.1f} h<extra></extra>",
            ),
            go.Bar(
                y=c["rotulo"],
                x=horas_exec,
                orientation="h",
                name="Execução (h)",
                marker_color=t.GHC_PETROLEO,
                hovertemplate="%{y}<br>Execução: %{x:.1f} h<extra></extra>",
            ),
        ]
    )
    barras.update_yaxes(autorange="reversed", automargin=True)
    barras.update_xaxes(title_text="horas")
    barras.update_layout(
        barmode="stack",
        height=fig.layout.height,
        margin=dict(l=8, r=16, t=36, b=32),
        legend=dict(orientation="h", y=1.02, x=0),
    )
    return com_alternativas(fig, "Gantt", [("Marcos do ciclo", marcos), ("Espera e execução", barras)])


def cascata_ciclo(ciclo: pd.DataFrame, unidade: str, altura: int = 340) -> go.Figure:
    """Quanto cada atividade acrescentou ao tempo total do ciclo (espera + execução)."""
    if ciclo.empty:
        return vazio("Selecione um paciente na lista")
    nome, _ = UNIDADES[unidade]
    c = ciclo.sort_values("ordem")
    passos = converter(c["tempo_etapa_min"].clip(lower=0), unidade)
    fig = go.Figure(
        go.Waterfall(
            x=c["ordem"].map("{:02d}".format) + ". " + c["atividade_generica"],
            y=passos,
            measure=["relative"] * len(c),
            connector=dict(line=dict(color=t.GRADE)),
            increasing=dict(marker=dict(color=t.GHC_PETROLEO)),
            decreasing=dict(marker=dict(color=t.NO_PRAZO)),
            text=[f"{v:.1f}" if v >= 0.05 else "" for v in passos],
            textposition="outside",
            hovertemplate="%{x}<br>+%{y:.1f} " + nome + "<extra></extra>",
        )
    )
    fig.update_layout(height=altura, showlegend=False, margin=dict(l=48, r=16, t=24, b=120))
    fig.update_yaxes(title_text=f"acumulado ({nome})")
    fig.update_xaxes(tickangle=-40)
    # Alternativas do catálogo: degraus do acumulado (T5) e barras por atividade, ordenadas (M1).
    rotulos = c["ordem"].map("{:02d}".format) + ". " + c["atividade_generica"]
    degraus = go.Figure(
        go.Scatter(
            x=rotulos,
            y=passos.cumsum(),
            mode="lines+markers",
            line=dict(shape="hv", color=t.GHC_PETROLEO, width=2.5),
            hovertemplate="%{x}<br>Acumulado: %{y:.1f} " + nome + "<extra></extra>",
            name="Acumulado",
        )
    )
    degraus.update_layout(height=altura, showlegend=False, margin=dict(l=48, r=16, t=24, b=120))
    degraus.update_yaxes(title_text=f"acumulado ({nome})", rangemode="tozero")
    degraus.update_xaxes(tickangle=-40)
    ordem = passos.sort_values()
    barras = go.Figure(
        go.Bar(
            y=rotulos.loc[ordem.index],
            x=ordem,
            orientation="h",
            marker_color=t.GHC_PETROLEO,
            hovertemplate="%{y}<br>%{x:.1f} " + nome + "<extra></extra>",
        )
    )
    barras.update_layout(height=max(altura, 22 * len(c) + 60), showlegend=False, margin=dict(l=8, r=16, t=24, b=40))
    barras.update_xaxes(title_text=nome)
    barras.update_yaxes(automargin=True)
    return com_alternativas(fig, "Cascata", [("Degraus do acumulado", degraus), ("Barras por atividade", barras)])


def comparacao_referencia(ciclo: pd.DataFrame, faixa: pd.DataFrame, altura: int = 320) -> go.Figure:
    """Tempo acumulado do paciente vs P25–P75 e mediana do mesmo tipo de fluxo."""
    if ciclo.empty:
        return vazio("Selecione um paciente na lista")
    c = ciclo[ciclo["acumulado_min"] >= 0].sort_values("ordem").drop_duplicates("atividade_generica")
    c = c[c["atividade_generica"].isin(faixa.index)] if not faixa.empty else c
    x = c["atividade_generica"]
    fig = go.Figure()
    if not faixa.empty:
        f = faixa.reindex(x)
        fig.add_trace(go.Scatter(x=x, y=f["p75"], mode="lines", line=dict(width=0), showlegend=False, hoverinfo="skip"))
        fig.add_trace(
            go.Scatter(
                x=x,
                y=f["p25"],
                mode="lines",
                line=dict(width=0),
                fill="tonexty",
                fillcolor="rgba(122,187,177,0.35)",
                name="P25–P75 do fluxo",
                hoverinfo="skip",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=x,
                y=f["mediana"],
                mode="lines",
                line=dict(color=t.GHC_AGUA, dash="dash"),
                name="Mediana do fluxo",
                hovertemplate="%{x}<br>Mediana: %{y:.1f} dias<extra></extra>",
            )
        )
    fig.add_trace(
        go.Scatter(
            x=x,
            y=c["acumulado_min"] / 1440,
            mode="lines+markers",
            name="Paciente",
            line=dict(color=t.GHC_VERDE, width=2.5),
            marker=dict(size=7),
            hovertemplate="%{x}<br>Paciente: %{y:.1f} dias<extra></extra>",
        )
    )
    fig.update_layout(height=altura, margin=dict(l=48, r=16, t=36, b=120))
    fig.update_yaxes(title_text="dias desde a importação da TC", rangemode="tozero")
    fig.update_xaxes(tickangle=-40)
    if faixa.empty:
        return com_alternativas(fig, "Paciente × faixa do fluxo", [], automaticas=True)
    # Alternativas do catálogo: desvio da mediana (V3, barras divergentes) e pontos com faixa P25–P75 (V2).
    f = faixa.reindex(x)
    paciente = (c["acumulado_min"] / 1440).to_numpy()
    desvio = paciente - f["mediana"].to_numpy()
    divergente = go.Figure(
        go.Bar(
            x=x,
            y=desvio,
            marker_color=[t.ATRASADO if d > 0 else t.NO_PRAZO for d in desvio],
            marker_pattern_shape=["/" if d > 0 else "" for d in desvio],
            hovertemplate="%{x}<br>%{y:+.1f} dias em relação à mediana do fluxo<extra></extra>",
            name="Desvio",
        )
    )
    divergente.add_hline(y=0, line_color=t.TEXTO, line_width=1)
    divergente.update_layout(height=altura, showlegend=False, margin=dict(l=48, r=16, t=36, b=120))
    divergente.update_yaxes(title_text="dias acima (+) ou abaixo (−) da mediana")
    divergente.update_xaxes(tickangle=-40)
    pontos = go.Figure(
        [
            go.Scatter(
                x=x,
                y=f["mediana"],
                mode="markers",
                name="Mediana do fluxo (P25–P75)",
                marker=dict(color=t.GHC_AGUA, size=9, symbol="line-ew-open", line=dict(width=3)),
                error_y=dict(
                    type="data",
                    symmetric=False,
                    array=(f["p75"] - f["mediana"]).to_numpy(),
                    arrayminus=(f["mediana"] - f["p25"]).to_numpy(),
                    color=t.GHC_AGUA,
                    thickness=6,
                    width=0,
                ),
                hovertemplate="%{x}<br>Mediana: %{y:.1f} dias<extra></extra>",
            ),
            go.Scatter(
                x=x,
                y=paciente,
                mode="markers",
                name="Paciente",
                marker=dict(color=t.GHC_VERDE, size=10),
                hovertemplate="%{x}<br>Paciente: %{y:.1f} dias<extra></extra>",
            ),
        ]
    )
    pontos.update_layout(height=altura, margin=dict(l=48, r=16, t=36, b=120))
    pontos.update_yaxes(title_text="dias desde a importação da TC", rangemode="tozero")
    pontos.update_xaxes(tickangle=-40)
    return com_alternativas(
        fig, "Paciente × faixa do fluxo", [("Desvio da mediana", divergente), ("Pontos e faixa P25–P75", pontos)]
    )


def histograma_espera(sessoes: pd.DataFrame, altura: int = 300) -> go.Figure:
    """Espera entre check-in e início do atendimento — P9."""
    s = sessoes[sessoes["espera_checkin_min"].between(-60, 240)]
    if s.empty:
        return vazio()
    fig = go.Figure(
        go.Histogram(
            x=s["espera_checkin_min"],
            xbins=dict(size=10),
            marker_color=t.GHC_PETROLEO,
            hovertemplate="%{x} min: %{y} atendimentos<extra></extra>",
        )
    )
    med = s["espera_checkin_min"].median()
    fig.add_vline(
        x=med,
        line=dict(color=t.GHC_VERDE, dash="dash"),
        annotation_text=f"Mediana {med:.0f} min",
        annotation_position="top right",
    )
    fig.update_layout(height=altura, bargap=0.05)
    fig.update_xaxes(title_text="minutos entre check-in e início")
    fig.update_yaxes(title_text="atendimentos")
    return fig


def espera_por_hora(sessoes: pd.DataFrame, altura: int = 300) -> go.Figure:
    s = sessoes[sessoes["espera_checkin_min"].between(-60, 240)]
    if s.empty:
        return vazio()
    g = s.groupby("hora")["espera_checkin_min"].agg(
        ["median", lambda x: x.quantile(0.25), lambda x: x.quantile(0.75), "size"]
    )
    g.columns = ["mediana", "p25", "p75", "n"]
    fig = go.Figure(
        go.Scatter(
            x=g.index,
            y=g["mediana"],
            mode="lines+markers",
            line=dict(color=t.GHC_PETROLEO, width=2.5),
            error_y=dict(
                type="data",
                symmetric=False,
                array=g["p75"] - g["mediana"],
                arrayminus=g["mediana"] - g["p25"],
                color=t.GHC_AGUA,
                thickness=1.5,
            ),
            customdata=g["n"],
            hovertemplate="%{x}h: mediana %{y:.0f} min (n=%{customdata})<extra></extra>",
        )
    )
    fig.update_layout(height=altura)
    fig.update_xaxes(title_text="hora agendada", dtick=1)
    fig.update_yaxes(title_text="espera (min), mediana e P25–P75")
    return fig


def duracao_por_sitio(sessoes: pd.DataFrame, top: int = 12, altura: int = 380) -> go.Figure:
    """Duração das sessões por sítio — P10."""
    s = sessoes[sessoes["sitio"].notna() & sessoes["duracao_valida"]]
    if s.empty:
        return vazio()
    principais = s["sitio"].value_counts().head(top).index
    g = (
        s[s["sitio"].isin(principais)]
        .groupby("sitio")["duracao_min"]
        .agg(["mean", lambda x: x.quantile(0.25), lambda x: x.quantile(0.75), "size"])
    )
    g.columns = ["media", "p25", "p75", "n"]
    g = g.sort_values("media")
    fig = go.Figure(
        go.Bar(
            x=g["media"],
            y=g.index,
            orientation="h",
            marker_color=t.GHC_PETROLEO,
            error_x=dict(
                type="data",
                symmetric=False,
                array=(g["p75"] - g["media"]).clip(lower=0),
                arrayminus=(g["media"] - g["p25"]).clip(lower=0),
                color=t.TEXTO_SECUNDARIO,
                thickness=1,
            ),
            customdata=g["n"],
            hovertemplate="%{y}: média %{x:.1f} min (n=%{customdata})<extra></extra>",
        )
    )
    fig.update_layout(height=altura, margin=dict(l=8, r=16, t=16, b=40))
    fig.update_xaxes(title_text="minutos (média, barra = P25–P75)")
    fig.update_yaxes(automargin=True)
    return fig
