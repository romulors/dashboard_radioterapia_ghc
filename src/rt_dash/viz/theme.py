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
PALETA_CATEGORICA = [
    "#038C8C",
    "#8C5A03",
    "#21826A",
    "#8C3603",
    "#143737",
    "#61C2AA",
    "#974B32",
    "#32977E",
    "#180042",
    "#423F00",
]

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

# Modo alto contraste (WCAG 2.2: 1.4.1, 1.4.11). Cores sólidas com pelo menos 4,5:1 contra o branco;
# cada série também ganha hachura (barras), traço (linhas) e símbolo (marcadores), aplicados em assets/a11y.js.
ALTO_CONTRASTE = {
    "#038C8C": "#006B6B",  # Eletivo, Simulação
    "#04BABA": "#1F4E99",  # Dia, Recepção
    "#014040": "#1A1A1A",  # Noite
    "#C2AA61": "#7A5A00",  # Prioridade
    "#8C3603": "#8C3603",  # Urgência, atrasado
    "#180042": "#3B1F8C",  # Braquiterapia
    "#61C2AA": "#4D4D4D",  # Retomografado
    "#BFC5CA": "#6E6E6E",  # Sem tipo
    "#9CA3AF": "#6E6E6E",  # neutro
    "#026969": "#1A1A1A",  # Planejamento
    "#038C3E": "#2E6B1F",  # Pré-Tratamento, no prazo
    "#8C5A03": "#7A5A00",  # Controle de Qualidade
    "#21826A": "#1F6B57",
    "#143737": "#1A1A1A",
    "#974B32": "#8C3603",
    "#32977E": "#1F6B57",
    "#423F00": "#7A5A00",
    "#7ABBB1": "#4D4D4D",
    "#006E77": "#004D4D",
}
ESCALA_ALTO_CONTRASTE = [[0, "#FFFFFF"], [0.25, "#B3D1D1"], [0.5, "#5E9999"], [0.75, "#1F6666"], [1, "#002B2B"]]
PADROES_BARRA = ["", "/", "x", ".", "\\", "+", "-", "|"]
TRACOS_LINHA = ["solid", "dash", "dot", "dashdot", "longdash", "longdashdot"]
SIMBOLOS = ["circle", "square", "diamond", "triangle-up", "x", "star", "triangle-down", "cross"]

# Status frente à meta: ícone + palavra, nunca só cor (WCAG 1.4.1)
STATUS = {
    "ok": ("✓", NO_PRAZO),
    "atencao": ("!", "#7A5A00"),
    "fora": ("✕", ATRASADO),
    "sem_meta": ("–", TEXTO_SECUNDARIO),
}

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
        ),
        # Contorno escuro nas barras: garante 3:1 contra o fundo mesmo nas cores claras (WCAG 1.4.11).
        data=dict(bar=[go.Bar(marker_line_width=0.8, marker_line_color="rgba(43,43,43,0.65)")]),
    )
    pio.templates.default = "plotly_white+ghc"
