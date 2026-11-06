"""Composição das abas: cada aba responde a uma pergunta de negócio e cada gráfico mora numa aba só.

Visão Geral (contexto e negócio, sem gráficos) · KPIs (scorecard frente à meta) · Eficácia vs Eficiência ·
Resultado vs Tendência · Processos · Jornada do Paciente · Sobre (autoria, regras, dados e acessibilidade).
Os callbacks ficam nos módulos de `pages`.
"""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import dcc, html

from rt_dash.app.components import cartao, grafico, kpi, kpi_meta
from rt_dash.app.context import AppContext
from rt_dash.app.pages import atendimento, atividades, jornada, produtividade, visao_geral
from rt_dash.domain.activities import ETAPAS_FLUXO
from rt_dash.metrics import REGISTRO
from rt_dash.viz.theme import rotulo_mes

# Pergunta de negócio e público de cada aba (mostrados na Visão Geral e no topo de cada aba).
PERGUNTAS = {
    "visao-geral": ("Para que serve este painel e como está o serviço?", "Todos"),
    "kpis": ("Estamos dentro da meta neste mês?", "Gestores"),
    "eficacia-eficiencia": ("Atingimos o objetivo, e a que custo de tempo e capacidade?", "Gestores e coordenação"),
    "resultado-tendencia": ("O que já entregamos e o que vem aí?", "Gestores e planejamento"),
    "processos": ("Onde o fluxo trava?", "Equipe técnica e melhoria contínua"),
    "jornada": ("O que aconteceu com este paciente, passo a passo?", "Equipe assistencial"),
    "sobre": ("Quem fez este painel, com quais dados, regras e recursos de acessibilidade?", "Todos"),
}

PERGUNTAS_NEGOCIO = [
    ("Como evoluiu a quantidade de planejamentos concluídos em 2026?", "kpis"),
    ("Como se distribuem os planejamentos entre Urgência, Prioridade e Eletivo?", "eficacia-eficiencia"),
    ("Quais atividades do planejamento levam mais tempo?", "processos"),
    ("Como a duração das atividades varia entre os tipos de fluxo?", "processos"),
    ("Quais atividades têm maior variabilidade de tempo?", "processos"),
    ("Como evoluiu o tempo de execução das atividades mês a mês?", "processos"),
    ("Qual percentual das tarefas é concluído no prazo?", "kpis"),
    ("Quais atividades têm os maiores atrasos?", "processos"),
    ("Quanto o paciente espera entre o check-in e o início do atendimento?", "eficacia-eficiencia"),
    ("Qual a duração média dos atendimentos por tipo de tratamento?", "eficacia-eficiencia"),
]


def _secao(titulo: str, nota: str, *filhos) -> html.Section:
    return html.Section(
        [html.H2(titulo, className="secao-titulo"), html.P(nota, className="secao-nota"), *filhos],
        className="secao",
    )


def _colunas(*colunas, lg: int = 6) -> dbc.Row:
    return dbc.Row([dbc.Col(c, lg=lg) for c in colunas], className="g-3 mt-1")


def _pilha(*cartoes) -> list:
    return [c if i == 0 else html.Div(c, className="mt-3") for i, c in enumerate(cartoes)]


def _pergunta(aba: str) -> html.P:
    pergunta, publico = PERGUNTAS[aba]
    return html.P(
        [html.Strong("Pergunta desta aba: "), pergunta, html.Span(f" · Para: {publico}", className="nota")],
        className="pergunta-aba",
    )


def _cartao_registro(id_: str) -> dbc.Col:
    ind = REGISTRO[id_]
    sub = ind.descricao or ind.nota
    sub = f"{sub} · {ind.unidade}" if sub else ind.unidade
    return dbc.Col(cartao(ind.titulo, grafico(f"g-vg-{id_}"), subtitulo=sub), lg=6, xxl=4)


def _ir(aba: str, rotulo: str, origem: str) -> html.Button:
    return html.Button(rotulo, id={"type": "ir-aba", "aba": aba, "origem": origem}, className="link-aba", n_clicks=0)


# ---------------------------------------------------------------- Visão Geral
def _fluxo_processo() -> html.Ol:
    etapas = [*ETAPAS_FLUXO, "Tratamento no acelerador linear"]
    detalhes = {
        "Recepção": "cadastro e escolha do fluxo",
        "Simulação": "tomografia de planejamento (TC) e importação",
        "Planejamento": "contornos, cálculo e aprovação do plano",
        "Pré-Tratamento": "ficha, prescrição e agendamento",
        "Controle de Qualidade": "verificação física do plano",
        "Tratamento no acelerador linear": "sessões diárias até a alta",
    }
    return html.Ol(
        [
            html.Li(
                [html.Strong(e), html.Span(detalhes.get(e, ""), className="etapa-detalhe")], className="fluxo-passo"
            )
            for e in etapas
        ],
        className="fluxo-processo",
        **{"aria-label": "Etapas do fluxo da radioterapia, em ordem"},
    )


def _perguntas_por_aba(mapa: list[tuple[str, str]]) -> html.Div:
    """Um cartão por aba (mesma borda do Mapa das abas); cada pergunta é uma linha inteira clicável."""
    cartoes = []
    for aba, rotulo in mapa:
        itens = [(i, p) for i, (p, a) in enumerate(PERGUNTAS_NEGOCIO, 1) if a == aba]
        if not itens:
            continue
        n = len(itens)
        cartoes.append(
            html.Section(
                [
                    html.H3(
                        [rotulo, html.Span(f"{PERGUNTAS[aba][0]} · {n} pergunta{'s' if n > 1 else ''}")],
                        className="grupo-perguntas-titulo",
                    ),
                    html.Ul(
                        [
                            html.Li(
                                html.Button(
                                    [
                                        html.Span(str(i), className="pergunta-num", **{"aria-hidden": "true"}),
                                        html.Span(p, className="pergunta-texto"),
                                        html.Span("›", className="pergunta-seta", **{"aria-hidden": "true"}),
                                    ],
                                    id={"type": "ir-aba", "aba": aba, "origem": f"perg-{i}"},
                                    n_clicks=0,
                                    type="button",
                                    className="pergunta-linha",
                                    **{"aria-label": f"Pergunta {i}: {p} Abrir a aba {rotulo}."},
                                )
                            )
                            for i, p in itens
                        ],
                        className="grupo-perguntas-lista",
                    ),
                ],
                className="mapa-aba grupo-perguntas",
                **{"aria-label": f"Perguntas respondidas na aba {rotulo}"},
            )
        )
    return html.Div(cartoes, className="perguntas-por-aba")


def visao_geral_aba(ctx: AppContext) -> html.Div:
    mapa = [
        ("kpis", "KPIs"),
        ("eficacia-eficiencia", "Eficácia vs Eficiência"),
        ("resultado-tendencia", "Resultado vs Tendência"),
        ("processos", "Processos"),
        ("jornada", "Jornada do Paciente"),
        ("sobre", "Sobre"),
    ]
    return html.Div(
        className="visao-geral",
        children=[
            _secao(
                "Mapa das abas",
                "Cada aba responde a uma pergunta e serve a um público.",
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(rotulo, className="cartao-titulo"),
                                html.P(PERGUNTAS[aba][0]),
                                html.P(f"Para: {PERGUNTAS[aba][1]}", className="nota"),
                                _ir(aba, f"Abrir {rotulo} →", f"mapa-{aba}"),
                            ],
                            className="mapa-aba",
                        )
                        for aba, rotulo in mapa
                    ],
                    className="grade-mapa",
                ),
            ),
            html.Section(
                [
                    html.H2("Situação no período filtrado", className="secao-titulo"),
                    html.Div(
                        [
                            kpi_meta("vg-h-inicios", "Pacientes que iniciaram tratamento", ("kpis", "KPIs")),
                            kpi_meta("vg-h-ciclo", "Mediana da duração do ciclo", ("processos", "Processos")),
                            kpi_meta("vg-h-prazo", "Tarefas no prazo", ("kpis", "KPIs")),
                            kpi_meta("vg-h-ocupacao", "Ocupação do acelerador", ("eficacia-eficiencia", "Eficácia")),
                        ],
                        className="linha-kpis linha-manchete",
                    ),
                ],
                className="secao",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        _secao(
                            "Como o paciente percorre o serviço",
                            "Um novo ciclo de planejamento começa a cada “Importar TC e Fusao” concluído "
                            "(ou “Importar Radiografia”, na braquiterapia).",
                            _fluxo_processo(),
                        ),
                        lg=6,
                    ),
                    dbc.Col(
                        _secao(
                            "Perguntas que o painel responde",
                            "Clique numa pergunta para abrir a aba que a responde.",
                            _perguntas_por_aba(mapa),
                        ),
                        lg=6,
                    ),
                ],
                className="g-3",
            ),
        ],
    )


# ---------------------------------------------------------------- KPIs
def kpis_aba(ctx: AppContext) -> html.Div:
    opcoes = [{"label": rotulo_mes(m), "value": m.strftime("%Y-%m")} for m in ctx.meses]
    ordem = visao_geral.APRESENTACAO + [i for i in REGISTRO if i not in visao_geral.APRESENTACAO]
    modal = dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Indicadores Radioterapia · formato de apresentação")),
            dbc.ModalBody(
                [
                    html.Div(
                        [html.H2(REGISTRO[i].titulo, className="slide-titulo"), grafico(f"g-ap-{i}")], className="slide"
                    )
                    for i in visao_geral.APRESENTACAO
                ]
                + [
                    html.Div(
                        [html.H2("Pacientes tratados por sítio", className="slide-titulo"), grafico("g-ap-sitios")],
                        className="slide",
                    )
                ]
            ),
        ],
        id="vg-modal",
        fullscreen=True,
        is_open=False,
    )
    return html.Div(
        [
            _pergunta("kpis"),
            html.Div(
                className="linha-controles",
                children=[
                    html.Label("Mês de referência", htmlFor="prod-mes", className="rotulo-controle"),
                    dcc.Dropdown(
                        id="prod-mes",
                        options=opcoes,
                        value=opcoes[-1]["value"],
                        clearable=False,
                        className="dropdown-mes",
                    ),
                    html.Span("Valores do mês, comparados à meta e à média dos 6 meses anteriores.", className="nota"),
                    dbc.Button("Modo apresentação", id="vg-apresentar", className="botao-ghc ms-auto"),
                ],
            ),
            _secao(
                "Scorecard do mês",
                "Valor, meta, situação (ícone e palavra) e tendência de cada indicador-chave.",
                html.Div(id="sc-tabela", className="tabela-rolavel"),
                _colunas(
                    cartao(
                        "Ocupação do acelerador frente à meta",
                        grafico("g-sc-ocupacao", altura=120),
                        subtitulo="Barra = mês de referência · faixa cinza = meta · traço = limite inferior",
                    ),
                    cartao(
                        "Tarefas no prazo frente à meta",
                        grafico("g-sc-prazo", altura=120),
                        subtitulo="Barra = mês de referência · traço = meta (se definida)",
                    ),
                ),
                html.Div(
                    cartao(
                        "Meses dentro (▲ ✓) e fora (▼ ✕) da meta",
                        grafico("g-sc-winloss", altura=170),
                        subtitulo="Um símbolo por mês para cada indicador com meta",
                    ),
                    className="mt-3",
                ),
            ),
            _secao(
                "Planejamento e tratamento",
                "Indicadores do mês de referência, com a variação contra a média dos 6 meses anteriores.",
                html.Div([kpi(i, t) for i, t in produtividade.KPIS], className="linha-kpis"),
            ),
            _secao(
                "Planejamento no período filtrado",
                "Volumes e tempos do período escolhido na barra de filtros.",
                html.Div([kpi(i, t) for i, t in visao_geral.KPIS], className="linha-kpis"),
            ),
            _secao(
                "Acelerador linear",
                "Indicadores do atendimento no período filtrado.",
                html.Div([kpi(i, t) for i, t in atendimento.KPIS], className="linha-kpis"),
            ),
            _secao(
                "Séries mensais",
                "Clique num mês (ou escolha em “Mês em destaque”) para filtrar as outras abas.",
                dbc.Row([_cartao_registro(i) for i in ordem], className="g-3"),
            ),
            modal,
        ]
    )


# ---------------------------------------------------------------- Eficácia vs Eficiência
def eficacia_eficiencia_aba(ctx: AppContext) -> html.Div:
    vagas = ctx.settings.acelerador.vagas_por_dia
    eficacia = _secao(
        "Eficácia",
        "Os objetivos foram atingidos? Foco no resultado final.",
        *_pilha(
            cartao(
                "Taxa de ocupação do acelerador linear",
                grafico("g-al-ocupacao"),
                subtitulo=f"Sessões ÷ ({vagas} vagas/dia × dias com atendimento) · meta 80–85% (faixa)",
            ),
            cartao(
                "Pacientes (sítios) que iniciaram tratamento",
                grafico("g-prod-inicios"),
                subtitulo="Pacientes distintos com 'Início do Tratamento' no mês",
            ),
            cartao(
                "Planejamentos Eletivos, Prioridades e Urgências",
                grafico("g-prod-fluxo"),
                subtitulo="Ciclos de planejamento por mês da aprovação",
            ),
            cartao(
                "Composição dos planejamentos por tipo de fluxo",
                grafico("g-nv-waffle"),
                subtitulo="Waffle: cada quadrado = 1% dos ciclos com TC importada no período",
            ),
            cartao("Pacientes tratados por sítio", grafico("g-prod-sitio")),
        ),
    )
    eficiencia = _secao(
        "Eficiência",
        "Quanto tempo e recurso foi gasto para chegar ao resultado?",
        *_pilha(
            cartao(
                "Distribuição mensal da duração do ciclo",
                grafico("g-nv-ridgeline"),
                subtitulo="Ridgeline: um perfil por mês; o traço e o número marcam a mediana",
            ),
            cartao(
                "Espera entre check-in e início do atendimento",
                grafico("g-al-espera"),
                subtitulo="P9 · atendimentos com espera entre −60 e 240 min",
            ),
            cartao(
                "Espera de dia e de noite por sítio",
                grafico("g-nv-barbell"),
                subtitulo="Barbell: ● dia, ◆ noite; sítios com pelo menos 20 sessões em cada turno",
            ),
            cartao("Espera por hora agendada", grafico("g-al-espera-hora"), subtitulo="Mediana e faixa P25–P75"),
            cartao(
                "Duração da sessão por sítio",
                grafico("g-al-duracao-sitio"),
                subtitulo="P10 · 12 sítios com mais sessões",
            ),
            cartao("Tempo médio de duração das sessões", grafico("g-al-duracao")),
            cartao("Número médio de sessões por tratamento", grafico("g-al-sessoes-trat")),
        ),
    )
    return html.Div([_pergunta("eficacia-eficiencia"), _colunas(eficacia, eficiencia)])


# ---------------------------------------------------------------- Resultado vs Tendência
def resultado_tendencia_aba(ctx: AppContext) -> html.Div:
    resultado = _secao(
        "Resultado",
        "O que já aconteceu: confirma o desempenho do período (indicadores de resultado).",
        *_pilha(
            cartao(
                "Sessões de radioterapia – dia e noite",
                grafico("g-prod-turno"),
                subtitulo="Dia: até 18h45 · Noite: a partir das 19h",
            ),
            cartao(
                "Crescimento relativo das sessões de dia e de noite",
                grafico("g-nv-indice"),
                subtitulo="Índice: primeiro mês = 100",
            ),
            cartao(
                "Sessões por dia no acelerador",
                grafico("g-nv-calendario"),
                subtitulo="Calendário: semanas nas colunas, dias da semana nas linhas, número de sessões na célula",
            ),
            cartao(
                "Funil de planejamento",
                grafico("g-am-funnel"),
                subtitulo="Ciclos em cada etapa: iniciado, TC importada, aprovado, tratamento iniciado",
            ),
        ),
    )
    tendencia = _secao(
        "Tendência",
        "Sinais antecipados: se a fila cresce, o prazo vai estourar (indicadores de tendência).",
        *_pilha(
            cartao(
                "Ciclos abertos em planejamento",
                grafico("g-nv-wip"),
                subtitulo="Por dia: TC importada e plano ainda não aprovado",
            ),
            cartao(
                "Entradas × saídas por semana",
                grafico("g-nv-entradas"),
                subtitulo="Entradas = TC importada · saídas = plano aprovado · barras = saldo",
            ),
            cartao(
                "Há quanto tempo os ciclos abertos esperam",
                grafico("g-nv-idade"),
                subtitulo="Cada ponto é um ciclo sem aprovação no fim do período; linha = P90 histórico",
            ),
        ),
    )
    return html.Div([_pergunta("resultado-tendencia"), _colunas(resultado, tendencia)])


# ---------------------------------------------------------------- Processos
def processos_aba(ctx: AppContext) -> html.Div:
    return html.Div(
        [
            _pergunta("processos"),
            _secao(
                "Fluxo de valor e estabilidade",
                "Onde o tempo se acumula e se o processo está sob controle.",
                _colunas(
                    cartao(
                        "Espera e execução por etapa",
                        grafico("g-nv-fluxo-valor"),
                        subtitulo="Mediana por ciclo, em horas · espera hachurada · a espera pela TC conta na "
                        "Simulação",
                    ),
                    cartao(
                        "Carta de controle da duração do ciclo",
                        grafico("g-nv-controle"),
                        subtitulo="Valores individuais · LSC/LIC = média ± 2,66 × amplitude móvel · ✕ = fora dos "
                        "limites",
                    ),
                ),
                _colunas(
                    cartao(
                        "Pareto da espera por atividade",
                        grafico("g-nv-pareto"),
                        subtitulo="Horas de espera somadas por atividade · em destaque as que somam até 80% da espera",
                    ),
                    cartao(
                        "Duração do ciclo por tipo de fluxo",
                        grafico("g-nv-dotstrip"),
                        subtitulo="Cada ponto é um ciclo; o traço marca a mediana",
                    ),
                ),
            ),
            _secao(
                "Atividades",
                "Tempos por atividade e etapa (perguntas 3 a 8).",
                atividades.layout(ctx),
            ),
            _secao(
                "Atrasos e relações",
                "Onde estão os atrasos e como tempo e volume se relacionam.",
                _colunas(
                    cartao(
                        "Ciclos com atraso por sítio",
                        grafico("g-nv-lollipop"),
                        subtitulo="% de ciclos com ao menos uma tarefa atrasada · sítios com 5 ou mais ciclos",
                    ),
                    cartao(
                        "Duração do ciclo × tempo até a aprovação",
                        grafico("g-am-scatter-facetas"),
                        subtitulo="Tamanho = nº de atividades · ◆ = ciclo com atraso, ● = sem atraso",
                    ),
                ),
            ),
        ]
    )


def jornada_aba(ctx: AppContext) -> html.Div:
    return html.Div([_pergunta("jornada"), jornada.layout(ctx)])


# ---------------------------------------------------------------- Sobre
REFERENCIAS = [
    "PMI. PMBOK Guide, 7ª ed. — domínio de desempenho de Medição (indicadores de tendência e de resultado, metas).",
    "W3C. Web Content Accessibility Guidelines (WCAG) 2.2, nível AA.",
    "ETSI. EN 301 549 — requisitos de acessibilidade para produtos e serviços de TIC (cláusulas 9 e 11).",
    "Financial Times / Andy Kriebel. Visual Vocabulary.",
    "Ken Flerlage e Kevin Flerlage. Tableau Chart Catalog.",
    "oHub. Paleta e acessibilidade em dashboards.",
]


ACESSIBILIDADE = [
    ("⌨", "Teclado", "Tab e Shift+Tab percorrem os controles; nas abas, use as setas."),
    ("↷", "Pular para o conteúdo", "É o primeiro item ao pressionar Tab."),
    (
        "◐",
        "Alto contraste",
        "O interruptor no cabeçalho troca o gradiente por cores sólidas, hachuras, traços e "
        "símbolos. A escolha fica salva neste navegador.",
    ),
    (
        "▤",
        "Texto e tabela",
        "Cada gráfico tem um resumo em texto e o botão “Ver dados em tabela” com os mesmos valores.",
    ),
    ("✓", "Não só cor", "Situações frente à meta usam ícone e palavra (✓ ! ✕)."),
    (
        "i",
        "Ícone de informação",
        "O ⓘ de cada gráfico explica o cálculo, a meta e a tolerância; abre com o mouse "
        "ou o foco do teclado, e Esc fecha.",
    ),
    (
        "⇄",
        "Outras visualizações",
        "O ⇄ mostra os mesmos dados em outro tipo de gráfico; o índice (ex.: 2/4) diz qual está na tela.",
    ),
]


def _fato(rotulo: str, valor) -> html.Div:
    return html.Div(
        [html.Span(rotulo, className="fato-rotulo"), html.Span(valor, className="fato-valor")], className="fato"
    )


def _cartao_sobre(titulo: str, nota: str, *filhos, classe: str = "") -> html.Section:
    return html.Section(
        [html.H2(titulo, className="secao-titulo"), html.P(nota, className="secao-nota"), *filhos],
        className=f"cartao-sobre {classe}".strip(),
    )


def _situacao(codigo: str, texto: str) -> html.Span:
    icone = {"ok": "✓", "aviso": "!", "falta": "✕", "sem": "–"}[codigo]
    return html.Span(
        [html.Span(icone, className="situacao-icone", **{"aria-hidden": "true"}), " ", texto],
        className=f"situacao situacao-{codigo}",
    )


def sobre_aba(ctx: AppContext) -> html.Div:
    st = ctx.settings
    ini, fim = rotulo_mes(ctx.meses[0]), rotulo_mes(ctx.meses[-1])
    n = lambda v: f"{v:,}".replace(",", ".")  # noqa: E731

    def pct(v):
        return f"{v * 100:.0f}%"

    prazos = " · ".join(
        f"{k} {v} dia{'s' if v > 1 else ''} út{'eis' if v > 1 else 'il'}"
        for k, v in st.prazo_planejamento_dias_uteis.items()
    )
    definicoes = [
        ("Ciclo de planejamento", "Da importação da TC até a última atividade antes do próximo ciclo."),
        (
            "Tipo de fluxo",
            "Eletivo, Prioridade, Urgência, Braquiterapia e Retomografado (pelo nome da tarefa no Aria).",
        ),
        ("Prazo do planejamento", prazos + "."),
        ("Turno", "Dia: atendimentos agendados até 18h45. Noite: a partir das 19h."),
        (
            "Capacidade do acelerador",
            f"{st.acelerador.vagas_por_dia} vagas por dia, das {st.acelerador.abertura:%H:%M} às "
            f"{st.acelerador.fechamento:%H:%M}.",
        ),
    ]
    lo, hi = st.meta_ocupacao_acelerador
    metas = [
        ("Ocupação do acelerador", ("ok", f"{pct(lo)} a {pct(hi)}")),
        (
            "Tarefas no prazo",
            ("ok", f"{pct(st.meta_pct_no_prazo[0])} ou mais") if st.meta_pct_no_prazo else ("sem", "sem meta definida"),
        ),
        (
            "Duração do ciclo (mediana)",
            ("ok", f"até {st.meta_lead_time_dias:g} dias") if st.meta_lead_time_dias else ("sem", "sem meta definida"),
        ),
    ]
    qualidade = [
        ("ok", f"Período coberto: {ini} a {fim}. Dados anonimizados do Sistema Aria."),
        (
            "ok",
            f"{n(len(ctx.ds.ciclos))} ciclos de planejamento, {n(len(ctx.ds.jornada))} atividades e "
            f"{n(len(ctx.ds.sessoes))} agendamentos no acelerador.",
        ),
        ("falta", "Faltas no acelerador e CID por paciente: sem fonte de dados até agora."),
        ("aviso", "Tomografia sem agenda própria: a ocupação é estimada por “Importar TC e Fusao”."),
        ("aviso", "Sessões acima de 60 min são tratadas como erro de registro."),
    ]
    icone_q = {"ok": ("✓", "dado completo"), "aviso": ("!", "estimativa"), "falta": ("✕", "sem fonte")}
    return html.Div(
        className="sobre",
        children=[
            _pergunta("sobre"),
            html.Section(
                className="sobre-hero",
                children=[
                    html.H2("Sobre o painel", className="secao-titulo"),
                    html.P(
                        "Acompanhar o fluxo de planejamento e tratamento do Serviço de Radioterapia do Grupo "
                        "Hospitalar Conceição (100% SUS), paciente a paciente e ciclo a ciclo, com o tempo entre as "
                        "atividades como informação central.",
                        className="sobre-objetivo",
                    ),
                    html.Div(
                        [
                            _fato("Autoria", "Romulo Rocha Santos · disciplina de Visualização de Dados"),
                            _fato("Fonte", "Sistema Aria · exportações anonimizadas"),
                            _fato("Período", f"{ini} a {fim}"),
                            _fato("Tecnologia", "Python · Plotly Dash · Bootstrap · AG Grid · pandas"),
                            _fato(
                                "Código-fonte",
                                html.A(
                                    "github.com/romulors/dashboard_radioterapia_ghc",
                                    href="https://github.com/romulors/dashboard_radioterapia_ghc",
                                    target="_blank",
                                    rel="noopener",
                                ),
                            ),
                        ],
                        className="sobre-fatos",
                    ),
                ],
            ),
            html.Div(
                className="sobre-grade",
                children=[
                    _cartao_sobre(
                        "Definições",
                        "Regras de negócio usadas nos cálculos (config/settings.yaml).",
                        html.Dl(
                            [x for d, t in definicoes for x in (html.Dt(d), html.Dd(t))],
                            className="sobre-pares",
                        ),
                    ),
                    _cartao_sobre(
                        "Metas",
                        "Valores que o serviço quer atingir.",
                        html.Ul(
                            [html.Li([html.Span(m), _situacao(*sit)], className="sobre-meta") for m, sit in metas],
                            className="sobre-lista",
                        ),
                        html.H2("Qualidade e limites dos dados", className="secao-titulo mt-3"),
                        html.P("O que o painel cobre e o que ainda falta.", className="secao-nota"),
                        html.Ul(
                            [
                                html.Li(
                                    [
                                        html.Span(
                                            icone_q[c][0],
                                            className=f"q-icone q-{c}",
                                            title=icone_q[c][1],
                                            **{"aria-label": icone_q[c][1]},
                                        ),
                                        html.Span(t),
                                    ],
                                    className="sobre-qualidade",
                                )
                                for c, t in qualidade
                            ],
                            className="sobre-lista",
                        ),
                    ),
                    _cartao_sobre(
                        "Acessibilidade",
                        "Segue a WCAG 2.2 nível AA (base da EN 301 549).",
                        html.Ul(
                            [
                                html.Li(
                                    [
                                        html.Span(i, className="a11y-icone", **{"aria-hidden": "true"}),
                                        html.Div([html.Strong(t), html.Span(d)]),
                                    ],
                                    className="sobre-a11y",
                                )
                                for i, t, d in ACESSIBILIDADE
                            ],
                            className="sobre-lista",
                        ),
                    ),
                ],
            ),
            _cartao_sobre(
                "Referências",
                "Base metodológica para os indicadores, os gráficos e a acessibilidade.",
                html.Ol([html.Li(r) for r in REFERENCIAS], className="sobre-refs"),
                classe="mt-3",
            ),
        ],
    )


ABAS = [
    ("visao-geral", "Visão Geral", visao_geral_aba),
    ("kpis", "KPIs", kpis_aba),
    ("eficacia-eficiencia", "Eficácia vs Eficiência", eficacia_eficiencia_aba),
    ("resultado-tendencia", "Resultado vs Tendência", resultado_tendencia_aba),
    ("processos", "Processos", processos_aba),
    ("jornada", "Jornada do Paciente", jornada_aba),
    ("sobre", "Sobre", sobre_aba),
]
