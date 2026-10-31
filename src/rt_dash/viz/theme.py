"""Paleta GHC e template Plotly. Nenhum gráfico deve ter cor escrita fora deste módulo."""

from __future__ import annotations

import plotly.graph_objects as go
import plotly.io as pio

# Moldura (identidade GHC, medida nos slides de agosto/2026)
GHC_VERDE = "#004231"
GHC_PETROLEO = "#006E77"
GHC_AGUA = "#7ABBB1"
FUNDO = "#F4F6F6"
CARTAO = "#FFFFFF"
TEXTO = "#2B2B2B"
TEXTO_SECUNDARIO = "#6B7280"
GRADE = "#E5E7EB"

# Dados: cores com significado fixo
CORES_FLUXO = {
    "Eletivo": "#2F6EBA",
    "Prioridade": "#E08A00",
    "Urgência": "#C62828",
    "Braquiterapia": "#7B5EA7",
    "Retomografado": "#8A9BA3",
    "Sem tipo": "#BFC5CA",
}
CORES_TURNO = {"Dia": "#2F6EBA", "Noite": GHC_VERDE}
CORES_ETAPA = {
    "Recepção": "#9DB8C9",
    "Simulação": "#5E9CB0",
    "Planejamento": GHC_PETROLEO,
    "Pré-Tratamento": "#3E7D5A",
    "Controle de Qualidade": "#7A6A9B",
}
NO_PRAZO = "#2E8B57"
ATRASADO = "#C62828"
DESTAQUE = GHC_PETROLEO
NEUTRO = "#9CA3AF"
ESCALA_SEQUENCIAL = [[0, "#FFFFFF"], [1, GHC_PETROLEO]]
ESCALA_DIVERGENTE = [[0, NO_PRAZO], [0.5, "#FFFFFF"], [1, ATRASADO]]

# Cores adicionais das paletas Adobe para visualizações multidimensionais
CORES_ADOBE_PALETTE1 = ["#004231", "#423200", "#3C0042", "#32977E", "#C2AA61"]
CORES_ADOBE_PALETTE2 = ["#004231", "#421C00", "#420400", "#61C2AA", "#C28961"]
CORES_ADOBE_PALETTE3 = ["#004231", "#177S5E", "#43A88F", "#84DBC5", "#CCFFF2"]
CORES_ADOBE_PALETTE4 = ["#004231", "#00EBB0", "#00C291", "#009973", "#007054"]

# Paleta sequencial ampliada (para gradientes em heatmaps)
CORES_SEQUENCIAL = [
    "#FFFFFF",
    "#F0F8F7",
    "#E1F1F0",
    "#D2EBE9",
    "#C3E5E2",
    "#B4DFDB",
    "#84DBC5",
    "#61C2AA",
    "#32977E",
    "#177S5E",
    "#00C291",
    "#009973",
    "#004231",
]

FONTE = "Inter, 'Segoe UI', Roboto, Arial, sans-serif"

MESES_PT = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]


def rotulo_mes(ts) -> str:
    return f"{MESES_PT[ts.month - 1]}/{str(ts.year)[2:]}"


def registrar_template() -> None:
    pio.templates["ghc"] = go.layout.Template(
        layout=go.Layout(
            font=dict(family=FONTE, size=13, color=TEXTO),
            title=dict(font=dict(size=15, color=TEXTO), x=0, xanchor="left"),
            paper_bgcolor=CARTAO,
            plot_bgcolor=CARTAO,
            colorway=[CORES_FLUXO["Eletivo"], CORES_FLUXO["Prioridade"], GHC_VERDE, NEUTRO],
            margin=dict(l=48, r=16, t=40, b=40),
            xaxis=dict(showgrid=False, linecolor=GRADE, ticks="outside", tickcolor=GRADE),
            yaxis=dict(gridcolor=GRADE, zeroline=False, linecolor=GRADE),
            legend=dict(orientation="h", y=1.02, yanchor="bottom", x=0, title_text=""),
            hoverlabel=dict(font=dict(family=FONTE, size=12), bgcolor=CARTAO),
            separators=",.",
        )
    )
    pio.templates.default = "plotly_white+ghc"
