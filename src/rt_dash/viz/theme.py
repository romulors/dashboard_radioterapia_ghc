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

# Paletas de referência (Adobe Color, pasta Material Referência)
PALETA_ACESSIVEIS = ["#038C8C", "#038C3E", "#8C5A03", "#8C3603", "#143737"]
PALETA_GRADIENTE = ["#05E3E3", "#04BABA", "#038C8C", "#026969", "#014040"]
PALETA_COMPLEMENTARES = ["#004231", "#21826A", "#61C2AA", "#974B32", "#421000"]
PALETA_CONTRASTE = ["#004231", "#32977E", "#423F00", "#421000", "#180042"]
# Séries sem cor fixa (sítios, etapas do funil): tons alternados para separar categorias vizinhas
PALETA_CATEGORICA = ["#038C8C", "#8C5A03", "#21826A", "#8C3603", "#143737", "#61C2AA", "#974B32", "#32977E", "#180042", "#423F00"]

# Dados: cores com significado fixo
CORES_FLUXO = {
    "Eletivo": "#038C8C",
    "Prioridade": "#C2AA61",
    "Urgência": "#8C3603",
    "Braquiterapia": "#180042",
    "Retomografado": "#61C2AA",
    "Sem tipo": "#BFC5CA",
}
CORES_TURNO = {"Dia": "#04BABA", "Noite": "#014040"}
CORES_ETAPA = {
    "Recepção": "#04BABA",
    "Simulação": "#038C8C",
    "Planejamento": "#026969",
    "Pré-Tratamento": "#038C3E",
    "Controle de Qualidade": "#8C5A03",
}
NO_PRAZO = "#038C3E"
ATRASADO = "#8C3603"
DESTAQUE = GHC_PETROLEO
NEUTRO = "#9CA3AF"
ESCALA_SEQUENCIAL = [[0, "#FFFFFF"], [0.25, "#04BABA"], [0.5, "#038C8C"], [0.75, "#026969"], [1, "#014040"]]
ESCALA_DIVERGENTE = [[0, NO_PRAZO], [0.5, "#FFFFFF"], [1, ATRASADO]]

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
            colorway=PALETA_CATEGORICA,
            margin=dict(l=48, r=16, t=40, b=40),
            xaxis=dict(showgrid=False, linecolor=GRADE, ticks="outside", tickcolor=GRADE),
            yaxis=dict(gridcolor=GRADE, zeroline=False, linecolor=GRADE),
            legend=dict(orientation="h", y=1.02, yanchor="bottom", x=0, title_text=""),
            hoverlabel=dict(font=dict(family=FONTE, size=12), bgcolor=CARTAO),
            separators=",.",
        )
    )
    pio.templates.default = "plotly_white+ghc"
