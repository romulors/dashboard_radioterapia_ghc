"""Gráficos novos da proposta de melhoria (Visual Vocabulary / Tableau Chart Catalog), em Plotly.

Regras de acessibilidade comuns: valor escrito no gráfico sempre que couber, símbolo ou texto além da
cor, títulos de eixo com unidade. Cores só de `viz/theme.py`.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from rt_dash.metrics.fluxo import DIAS_SEMANA
from rt_dash.viz import theme as t
from rt_dash.viz.figures import vazio


def _br(valor: float, casas: int = 0) -> str:
    return f"{valor:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _layout(fig: go.Figure, altura: int, **kw) -> go.Figure:
    fig.update_layout(height=altura, margin=kw.pop("margin", dict(l=8, r=16, t=24, b=40)), **kw)
    return fig


# ---------------------------------------------------------------- KPIs
def bullet(
    valor: float | None,
    meta: tuple[float, float] | float | None,
    titulo: str,
    maximo: float,
    percentual: bool = True,
    polaridade: str = "faixa",
    altura: int = 110,
) -> go.Figure:
    """Bullet graph: barra do valor, faixa da meta em cinza e traço no limite da meta."""
    if valor is None or valor != valor:
        return vazio("Sem dado no mês")
    fator = 100 if percentual else 1
    lo, hi = (meta if isinstance(meta, tuple | list) else (meta, meta)) if meta is not None else (None, None)
    passos = []
    if lo is not None:
        if polaridade == "maior":
            passos = [dict(range=[lo * fator, maximo * fator], color="#D9DDE1")]
        elif polaridade == "menor":
            passos = [dict(range=[0, hi * fator], color="#D9DDE1")]
        else:
            passos = [dict(range=[lo * fator, hi * fator], color="#D9DDE1")]
    gauge = dict(
        shape="bullet",
        axis=dict(range=[0, maximo * fator], ticksuffix="%" if percentual else "", tickfont=dict(size=11)),
        bar=dict(color=t.GHC_VERDE, thickness=0.45),
        steps=passos,
        bgcolor="#F1F3F4",
        borderwidth=1,
        bordercolor=t.TEXTO_SECUNDARIO,
    )
    if lo is not None:
        limite = lo if polaridade != "menor" else hi
        gauge["threshold"] = dict(line=dict(color=t.TEXTO, width=3), thickness=0.9, value=limite * fator)
    fig = go.Figure(
        go.Indicator(
            mode="number+gauge",
            value=valor * fator,
            number=dict(
                suffix="%" if percentual else "", valueformat=".0f" if percentual else ".1f", font=dict(size=22)
            ),
            domain=dict(x=[0.22, 1], y=[0.15, 0.85]),
            title=dict(text=titulo, font=dict(size=12)),
            gauge=gauge,
        )
    )
    return _layout(fig, altura, margin=dict(l=8, r=24, t=8, b=20))


def sparkline(df: pd.DataFrame, altura: int = 60) -> go.Figure:
    """Minigráfico: linha da série mensal com o último ponto destacado e rotulado."""
    if df.empty:
        return vazio("")
    total = df.groupby("mes")["valor"].sum().sort_index()
    fig = go.Figure(
        go.Scatter(
            x=[t.rotulo_mes(m) for m in total.index],
            y=total.to_numpy(),
            mode="lines",
            line=dict(color=t.GHC_PETROLEO, width=2),
            hovertemplate="%{x}: %{y:,.0f}<extra></extra>",
            name="Série mensal",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[t.rotulo_mes(total.index[-1])],
            y=[total.iloc[-1]],
            mode="markers",
            marker=dict(size=8, color=t.GHC_VERDE, symbol="circle"),
            hoverinfo="skip",
            name="Último mês",
        )
    )
    fig.update_xaxes(visible=False, type="category")
    fig.update_yaxes(visible=False)
    return _layout(fig, altura, margin=dict(l=4, r=4, t=4, b=4), showlegend=False)


def win_loss(dentro: pd.DataFrame, altura: int = 150) -> go.Figure:
    """Win/Loss: uma linha por indicador e um traço por mês, para cima (dentro da meta) ou para baixo (fora)."""
    if dentro.empty:
        return vazio("Nenhum indicador com meta definida")
    fig = go.Figure()
    for indicador, g in dentro.groupby("indicador", sort=False):
        g = g.sort_values("mes")
        ok = g["dentro"].astype(bool)
        fig.add_trace(
            go.Scatter(
                x=[t.rotulo_mes(m) for m in g["mes"]],
                y=[indicador] * len(g),
                mode="markers+text",
                marker=dict(
                    symbol=["triangle-up" if v else "triangle-down" for v in ok],
                    size=16,
                    color=[t.NO_PRAZO if v else t.ATRASADO for v in ok],
                ),
                text=["✓" if v else "✕" for v in ok],
                textposition="middle right",
                textfont=dict(size=11, color=t.TEXTO),
                name=indicador,
                hovertemplate="%{y} · %{x}: %{text}<extra></extra>",
            )
        )
    fig.update_xaxes(type="category", showgrid=False)
    fig.update_yaxes(automargin=True)
    return _layout(fig, altura, showlegend=False)


# ---------------------------------------------------------------- Resultado
def calendario(dias: pd.DataFrame, altura: int = 300) -> go.Figure:
    """Calendário de sessões por dia: semanas nas colunas, dias da semana nas linhas, valor em cada célula."""
    if dias.empty:
        return vazio()
    p = dias.pivot_table(index="dia_semana", columns="semana", values="sessoes", aggfunc="sum")
    p = p.reindex([d for d in DIAS_SEMANA if d in p.index])
    rotulos = [s.strftime("%d/%m") for s in p.columns]
    fig = go.Figure(
        go.Heatmap(
            z=p.values,
            x=rotulos,
            y=list(p.index),
            colorscale=t.ESCALA_SEQUENCIAL,
            text=np.where(np.isnan(p.values), "", p.values.astype(object)),
            texttemplate="%{text}",
            textfont=dict(size=9),
            xgap=2,
            ygap=2,
            colorbar=dict(title="Sessões", thickness=10),
            hovertemplate="Semana de %{x} · %{y}: %{z} sessões<extra></extra>",
        )
    )
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(title_text="Semana (início)", tickangle=-45, nticks=18)
    return _layout(fig, altura, margin=dict(l=8, r=8, t=16, b=56))


def indice(df: pd.DataFrame, altura: int = 300) -> go.Figure:
    """Index chart: cada série com o primeiro mês = 100, rótulo direto no fim da linha."""
    if df.empty:
        return vazio()
    fig = go.Figure()
    for i, (serie, g) in enumerate(df.groupby("serie", sort=False)):
        g = g.sort_values("mes")
        cor = t.CORES_TURNO.get(serie) or t.CORES_FLUXO.get(serie) or t.PALETA_CATEGORICA[i]
        x = [t.rotulo_mes(m) for m in g["mes"]]
        fig.add_trace(
            go.Scatter(
                x=x,
                y=g["indice"],
                name=serie,
                mode="lines+markers",
                line=dict(color=cor, width=2.5, dash=t.TRACOS_LINHA[i % len(t.TRACOS_LINHA)]),
                marker=dict(symbol=t.SIMBOLOS[i % len(t.SIMBOLOS)], size=7, color=cor),
                hovertemplate=f"{serie} · %{{x}}: índice %{{y:.0f}}<extra></extra>",
            )
        )
        fig.add_annotation(
            x=x[-1],
            y=g["indice"].iloc[-1],
            text=f"<b>{serie}</b> {_br(g['indice'].iloc[-1])}",
            showarrow=False,
            xanchor="left",
            xshift=8,
            font=dict(size=12, color=cor),
        )
    fig.add_hline(y=100, line=dict(color=t.TEXTO_SECUNDARIO, width=1, dash="dot"))
    fig.update_xaxes(type="category")
    fig.update_yaxes(title_text="Índice (1º mês = 100)")
    return _layout(fig, altura, margin=dict(l=8, r=90, t=16, b=40), showlegend=False)


# ---------------------------------------------------------------- Tendência
def wip(df: pd.DataFrame, altura: int = 300) -> go.Figure:
    """Step chart dos ciclos abertos em planejamento por dia."""
    if df.empty:
        return vazio()
    fig = go.Figure(
        go.Scatter(
            x=df["data"],
            y=df["abertos"],
            mode="lines",
            line=dict(color=t.GHC_PETROLEO, width=2, shape="hv"),
            name="Ciclos abertos",
            hovertemplate="%{x|%d/%m/%Y}: %{y} ciclos abertos<extra></extra>",
        )
    )
    media = df["abertos"].mean()
    fig.add_hline(
        y=media,
        line=dict(color=t.TEXTO_SECUNDARIO, width=1, dash="dot"),
        annotation_text=f"Média {_br(media)}",
        annotation_position="top left",
        annotation_font=dict(size=11, color=t.TEXTO_SECUNDARIO),
    )
    ultimo = df.iloc[-1]
    fig.add_annotation(
        x=ultimo["data"],
        y=ultimo["abertos"],
        text=f"<b>{int(ultimo['abertos'])}</b> em {ultimo['data']:%d/%m}",
        showarrow=True,
        arrowhead=0,
        ax=-40,
        ay=-24,
        font=dict(size=12, color=t.GHC_VERDE),
    )
    fig.update_yaxes(title_text="Ciclos abertos", rangemode="tozero")
    return _layout(fig, altura, showlegend=False)


def entradas_saidas(df: pd.DataFrame, altura: int = 300) -> go.Figure:
    """Entradas × saídas por semana: linhas com traço e símbolo distintos e o saldo em barras."""
    if df.empty:
        return vazio()
    fig = go.Figure()
    p = df.pivot_table(index="semana", columns="serie", values="valor", aggfunc="sum", fill_value=0).sort_index()
    saldo = p.iloc[:, 0] - p.iloc[:, 1] if p.shape[1] == 2 else None
    if saldo is not None:
        fig.add_trace(
            go.Bar(
                x=p.index,
                y=saldo,
                name="Saldo (entradas − saídas)",
                marker_color=t.NEUTRO,
                opacity=0.6,
                hovertemplate="Semana de %{x|%d/%m}: saldo %{y:+}<extra></extra>",
            )
        )
    for i, serie in enumerate(p.columns):
        cor = [t.GHC_PETROLEO, t.CORES_FLUXO["Urgência"]][i % 2]
        fig.add_trace(
            go.Scatter(
                x=p.index,
                y=p[serie],
                name=serie,
                mode="lines+markers",
                line=dict(color=cor, width=2, dash=t.TRACOS_LINHA[i]),
                marker=dict(symbol=t.SIMBOLOS[i], size=6, color=cor),
                hovertemplate=f"{serie} · semana de %{{x|%d/%m}}: %{{y}}<extra></extra>",
            )
        )
    fig.update_yaxes(title_text="Ciclos por semana", zeroline=True, zerolinecolor=t.TEXTO_SECUNDARIO)
    return _layout(fig, altura)


def idade_abertos(df: pd.DataFrame, referencia_p90: float | None, altura: int = 300) -> go.Figure:
    """Dot strip: cada ciclo aberto é um ponto (idade em dias), por tipo de fluxo, com a linha do P90 histórico."""
    if df.empty:
        return vazio("Nenhum ciclo aberto na data de referência")
    fig = go.Figure()
    ordem = [f for f in t.CORES_FLUXO if f in set(df["tipo_fluxo"])]
    for i, fluxo in enumerate(ordem):
        g = df[df["tipo_fluxo"] == fluxo]
        fig.add_trace(
            go.Scatter(
                x=g["idade_dias"],
                y=[fluxo] * len(g),
                mode="markers",
                marker=dict(
                    color=t.CORES_FLUXO.get(fluxo, t.NEUTRO),
                    symbol=t.SIMBOLOS[i % len(t.SIMBOLOS)],
                    size=9,
                    line=dict(width=1, color=t.TEXTO),
                ),
                name=f"{fluxo} ({len(g)})",
                customdata=g[["ciclo_id"]].to_numpy(),
                hovertemplate="%{customdata[0]} · aberto há %{x:.0f} dias<extra>" + fluxo + "</extra>",
            )
        )
    if referencia_p90:
        fig.add_vline(
            x=referencia_p90,
            line=dict(color=t.ATRASADO, width=2, dash="dash"),
            annotation_text=f"P90 histórico até aprovação: {_br(referencia_p90)} dias",
            annotation_position="top right",
            annotation_font=dict(size=11, color=t.ATRASADO),
        )
    fig.update_xaxes(title_text="Dias desde a importação da TC", rangemode="tozero")
    fig.update_yaxes(automargin=True)
    return _layout(fig, altura, showlegend=False)


# ---------------------------------------------------------------- Eficácia / Eficiência
def waffle(comp: pd.DataFrame, altura: int = 300) -> go.Figure:
    """Waffle 10×10: cada quadrado = 1% dos planejamentos; legenda com o percentual escrito."""
    if comp.empty:
        return vazio()
    quadros = np.round(comp["pct"].to_numpy() * 100).astype(int)
    quadros[np.argmax(quadros)] += 100 - quadros.sum()
    fig = go.Figure()
    pos = 0
    for i, (fluxo, n_q, pct, n) in enumerate(zip(comp["tipo_fluxo"], quadros, comp["pct"], comp["n"], strict=True)):
        idx = np.arange(pos, pos + n_q)
        pos += n_q
        fig.add_trace(
            go.Scatter(
                x=idx % 10,
                y=idx // 10,
                mode="markers",
                marker=dict(
                    symbol="square",
                    size=18,
                    color=t.CORES_FLUXO.get(fluxo, t.PALETA_CATEGORICA[i]),
                    line=dict(width=1, color="#FFFFFF"),
                ),
                name=f"{fluxo}: {_br(pct * 100)}% ({n})",
                hovertemplate=f"{fluxo}: {_br(pct * 100)}% · {n} ciclos<extra></extra>",
            )
        )
    fig.update_xaxes(visible=False, range=[-0.6, 9.6])
    fig.update_yaxes(visible=False, range=[9.6, -0.6], scaleanchor="x")
    return _layout(
        fig,
        altura,
        margin=dict(l=8, r=8, t=8, b=8),
        legend=dict(orientation="v", x=1.02, y=1, yanchor="top", font=dict(size=12)),
    )


def barbell(df: pd.DataFrame, altura: int = 360) -> go.Figure:
    """Barbell: espera mediana de dia e de noite por sítio, ligadas por uma linha."""
    if df.empty:
        return vazio("Poucos sítios com sessões nos dois turnos")
    fig = go.Figure()
    for _, r in df.iterrows():
        fig.add_trace(
            go.Scatter(
                x=[r["Dia"], r["Noite"]],
                y=[r["sitio"]] * 2,
                mode="lines",
                line=dict(color=t.NEUTRO, width=3),
                hoverinfo="skip",
                showlegend=False,
            )
        )
    for turno, simbolo in (("Dia", "circle"), ("Noite", "diamond")):
        fig.add_trace(
            go.Scatter(
                x=df[turno],
                y=df["sitio"],
                mode="markers+text",
                name=turno,
                marker=dict(symbol=simbolo, size=12, color=t.CORES_TURNO[turno], line=dict(width=1, color=t.TEXTO)),
                text=df[turno].round(0).astype(int).astype(str),
                textposition="middle left" if turno == "Dia" else "middle right",
                textfont=dict(size=10, color=t.TEXTO),
                hovertemplate=f"%{{y}} · {turno}: %{{x:.0f}} min<extra></extra>",
            )
        )
    fig.update_xaxes(title_text="Espera mediana check-in → início (min)")
    fig.update_yaxes(automargin=True)
    return _layout(fig, altura, margin=dict(l=8, r=24, t=32, b=40))


def ridgeline(ciclos: pd.DataFrame, coluna: str = "lead_time_dias", altura: int = 380) -> go.Figure:
    """Ridgeline: distribuição mensal da duração do ciclo, um 'cume' por mês, com a mediana marcada."""
    c = ciclos.dropna(subset=[coluna, "mes"])
    c = c[c[coluna] >= 0]
    if c.empty:
        return vazio()
    teto = c[coluna].quantile(0.95)
    fig = go.Figure()
    for mes, g in sorted(c.groupby("mes"), key=lambda x: x[0], reverse=True):
        rot = t.rotulo_mes(mes)
        fig.add_trace(
            go.Violin(
                x=g[coluna].clip(upper=teto),
                name=rot,
                side="positive",
                orientation="h",
                width=1.8,
                line=dict(color=t.GHC_PETROLEO, width=1),
                fillcolor="rgba(3,140,140,0.25)",
                points=False,
                meanline=dict(visible=False),
                box=dict(visible=False),
                spanmode="hard",
                hoverinfo="skip",
            )
        )
        med = g[coluna].median()
        fig.add_trace(
            go.Scatter(
                x=[med],
                y=[rot],
                mode="markers+text",
                marker=dict(symbol="line-ns", size=14, line=dict(width=2.5, color=t.GHC_VERDE)),
                text=[f"{_br(med, 1)} d"],
                textposition="top center",
                textfont=dict(size=10, color=t.GHC_VERDE),
                hovertemplate=f"{rot}: mediana {_br(med, 1)} dias (n = {len(g)})<extra></extra>",
                showlegend=False,
            )
        )
    fig.update_xaxes(title_text=f"Duração do ciclo (dias, cortado no P95 = {_br(teto, 0)})", rangemode="tozero")
    fig.update_yaxes(type="category")
    return _layout(fig, altura, showlegend=False, violingap=0, violinmode="overlay")


# ---------------------------------------------------------------- Processos
def fluxo_valor(df: pd.DataFrame, altura: int = 300) -> go.Figure:
    """Fluxo de valor: espera (cinza, hachurada) e execução (cor) medianas por etapa, na ordem do fluxo."""
    if df.empty:
        return vazio()
    d = df.iloc[::-1]
    gargalo = df.loc[(df["espera_h"] + df["execucao_h"]).idxmax(), "etapa"]
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            y=d["etapa"],
            x=d["execucao_h"],
            orientation="h",
            name="Execução",
            marker=dict(color=t.GHC_PETROLEO),
            text=[f"{_br(v, 1)} h" for v in d["execucao_h"]],
            textposition="inside",
            insidetextanchor="middle",
            hovertemplate="%{y} · execução mediana: %{x:.1f} h<extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            y=d["etapa"],
            x=d["espera_h"],
            orientation="h",
            name="Espera",
            marker=dict(color="#D9DDE1", pattern=dict(shape="/", fgcolor=t.TEXTO_SECUNDARIO)),
            text=[
                f"{_br(v, 1)} h" + ("  ◀ gargalo" if e == gargalo else "")
                for v, e in zip(d["espera_h"], d["etapa"], strict=True)
            ],
            textposition="outside",
            hovertemplate="%{y} · espera mediana: %{x:.1f} h<extra></extra>",
        )
    )
    fig.update_layout(barmode="stack")
    fig.update_xaxes(
        title_text="Horas por ciclo (mediana)", range=[0, float((df["espera_h"] + df["execucao_h"]).max()) * 1.45]
    )
    fig.update_yaxes(automargin=True)
    return _layout(fig, altura, margin=dict(l=8, r=16, t=32, b=40))


def controle(df: pd.DataFrame, altura: int = 340) -> go.Figure:
    """Carta de controle (I): duração de cada ciclo na ordem de importação, média e limites de controle."""
    if df.empty:
        return vazio()
    fig = go.Figure()
    dentro, fora = df[~df["fora"]], df[df["fora"]]
    fig.add_trace(
        go.Scatter(
            x=df["importacao"],
            y=df["valor"],
            mode="lines",
            line=dict(color=t.NEUTRO, width=1),
            hoverinfo="skip",
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=dentro["importacao"],
            y=dentro["valor"],
            mode="markers",
            name="Dentro dos limites",
            marker=dict(symbol="circle", size=6, color=t.GHC_PETROLEO),
            customdata=dentro[["ciclo_id", "tipo_fluxo"]].to_numpy(),
            hovertemplate="%{customdata[0]} (%{customdata[1]}) · %{y:.1f} dias<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=fora["importacao"],
            y=fora["valor"],
            mode="markers",
            name="Fora dos limites (causa especial)",
            marker=dict(symbol="x", size=10, color=t.ATRASADO, line=dict(width=1, color=t.ATRASADO)),
            customdata=fora[["ciclo_id", "tipo_fluxo"]].to_numpy(),
            hovertemplate="%{customdata[0]} (%{customdata[1]}) · %{y:.1f} dias<extra></extra>",
        )
    )
    r = df.iloc[0]
    for valor, nome, traco in ((r["media"], "Média", "solid"), (r["lsc"], "LSC", "dash"), (r["lic"], "LIC", "dash")):
        fig.add_hline(
            y=valor,
            line=dict(color=t.TEXTO, width=1, dash=traco),
            annotation_text=f"{nome} {_br(valor, 1)} d",
            annotation_position="right",
            annotation_font=dict(size=11, color=t.TEXTO),
        )
    fig.update_yaxes(title_text="Duração do ciclo (dias)", rangemode="tozero")
    return _layout(fig, altura, margin=dict(l=8, r=80, t=32, b=40))


def pareto(df: pd.DataFrame, altura: int | None = None) -> go.Figure:
    """Pareto deitado: espera total por atividade, da maior para a menor; as que somam até 80% em destaque."""
    if df.empty:
        return vazio()
    dd = df.assign(vital=df["pct_acumulado"].shift(1, fill_value=0) < 0.8)
    fig = go.Figure()
    for vital, nome, cor in ((True, "Somam até 80% da espera", t.GHC_PETROLEO), (False, "Demais", t.NEUTRO)):
        g = dd[dd["vital"] == vital]
        fig.add_trace(
            go.Bar(
                y=g["atividade"],
                x=g["horas"],
                orientation="h",
                name=nome,
                marker_color=cor,
                text=[
                    f"{_br(h)} h · {_br(p * 100)}% acum." for h, p in zip(g["horas"], g["pct_acumulado"], strict=True)
                ],
                textposition="outside",
                textfont=dict(size=10),
                hovertemplate="%{y}: %{x:,.0f} h de espera<extra></extra>",
            )
        )
    fig.update_yaxes(categoryorder="array", categoryarray=list(dd["atividade"][::-1]), automargin=True)
    fig.update_xaxes(title_text="Horas de espera somadas", range=[0, float(df["horas"].max()) * 1.5])
    return _layout(fig, altura or 26 * len(df) + 100, margin=dict(l=8, r=16, t=32, b=40))


def lollipop(df: pd.DataFrame, altura: int | None = None) -> go.Figure:
    """Lollipop ordenado: % de ciclos com atraso por sítio, com o valor escrito e n de ciclos."""
    if df.empty:
        return vazio()
    altura = altura or 24 * len(df) + 80
    fig = go.Figure()
    for _, r in df.iterrows():
        fig.add_trace(
            go.Scatter(
                x=[0, r["pct"]],
                y=[r["sitio"]] * 2,
                mode="lines",
                line=dict(color=t.NEUTRO, width=2),
                hoverinfo="skip",
                showlegend=False,
            )
        )
    fig.add_trace(
        go.Scatter(
            x=df["pct"],
            y=df["sitio"],
            mode="markers+text",
            marker=dict(size=11, color=t.ATRASADO, symbol="circle"),
            text=[f"{_br(p * 100)}% (n={n})" for p, n in zip(df["pct"], df["n"], strict=True)],
            textposition="middle right",
            textfont=dict(size=11, color=t.TEXTO),
            showlegend=False,
            hovertemplate="%{y}: %{x:.0%} dos ciclos com atraso<extra></extra>",
        )
    )
    fig.update_xaxes(tickformat=".0%", range=[0, 1.25], title_text="Ciclos com alguma tarefa atrasada")
    fig.update_yaxes(automargin=True)
    return _layout(fig, altura, margin=dict(l=8, r=16, t=16, b=40))


def dot_strip(ciclos: pd.DataFrame, coluna: str = "lead_time_dias", altura: int = 320) -> go.Figure:
    """Dot strip com jitter: cada ciclo é um ponto, por tipo de fluxo, com a mediana escrita."""
    c = ciclos.dropna(subset=[coluna])
    if c.empty:
        return vazio()
    teto = c[coluna].quantile(0.98)
    rng = np.random.default_rng(42)
    fig = go.Figure()
    ordem = [f for f in t.CORES_FLUXO if f in set(c["tipo_fluxo"])]
    rotulos: list[str] = []
    for i, fluxo in enumerate(ordem):
        g = c[c["tipo_fluxo"] == fluxo]
        y = i + rng.uniform(-0.28, 0.28, len(g))
        fig.add_trace(
            go.Scatter(
                x=g[coluna].clip(upper=teto),
                y=y,
                mode="markers",
                name=fluxo,
                marker=dict(
                    size=5,
                    opacity=0.55,
                    color=t.CORES_FLUXO.get(fluxo, t.NEUTRO),
                    symbol=t.SIMBOLOS[i % len(t.SIMBOLOS)],
                ),
                customdata=g[["ciclo_id"]].to_numpy(),
                hovertemplate="%{customdata[0]}: %{x:.1f} dias<extra>" + fluxo + "</extra>",
            )
        )
        med = g[coluna].median()
        rotulos.append(f"{fluxo} · mediana {_br(med, 1)} d")
        fig.add_shape(type="line", x0=med, x1=med, y0=i - 0.4, y1=i + 0.4, line=dict(color=t.TEXTO, width=3))
    fig.update_yaxes(
        tickvals=list(range(len(ordem))), ticktext=rotulos, range=[-0.6, len(ordem) - 0.4], automargin=True
    )
    fig.update_xaxes(title_text=f"Duração do ciclo (dias, cortado no P98 = {_br(teto)})", rangemode="tozero")
    return _layout(fig, altura, showlegend=False)
