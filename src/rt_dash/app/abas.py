"""Composição das abas: cada aba responde a uma pergunta de negócio e cada gráfico mora numa aba só.

Visão Geral (contexto e negócio, sem gráficos) · KPIs (scorecard frente à meta) · Eficácia vs Eficiência ·
Resultado vs Tendência · Processos · Jornada do Paciente. Os callbacks ficam nos módulos de `pages`.
"""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import dcc, html

from rt_dash.app.components import cartao, grafico, kpi, kpi_meta
from rt_dash.app.context import AppContext
from rt_dash.app.pages import atendimento, atividades, jornada, produtividade, visao_geral
from rt_dash.domain.activities import ETAPAS_FLUXO
from rt_dash.metrics import REGISTRO
from rt_dash.metrics.registry import ficha_tecnica
from rt_dash.viz.theme import rotulo_mes

# Pergunta de negócio e público de cada aba (mostrados na Visão Geral e no topo de cada aba).
PERGUNTAS = {
    "visao-geral": ("Para que serve este painel e como está o serviço?", "Todos"),
    "kpis": ("Estamos dentro da meta neste mês?", "Gestores"),
    "eficacia-eficiencia": ("Atingimos o objetivo, e a que custo de tempo e capacidade?", "Gestores e coordenação"),
    "resultado-tendencia": ("O que já entregamos e o que vem aí?", "Gestores e planejamento"),
    "processos": ("Onde o fluxo trava?", "Equipe técnica e melhoria contínua"),
    "jornada": ("O que aconteceu com este paciente, passo a passo?", "Equipe assistencial"),
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


def _tabela_ficha() -> html.Table:
    ficha = ficha_tecnica()
    return html.Table(
        [
            html.Caption("Ficha técnica dos indicadores mensais"),
            html.Thead(html.Tr([html.Th(c, scope="col") for c in ficha.columns])),
            html.Tbody(
                [
                    html.Tr([html.Th(r.iloc[0], scope="row"), *[html.Td(v) for v in r.iloc[1:]]])
                    for _, r in ficha.iterrows()
                ]
            ),
        ],
        className="tabela-ficha",
    )


def visao_geral_aba(ctx: AppContext) -> html.Div:
    st = ctx.settings
    ini, fim = rotulo_mes(ctx.meses[0]), rotulo_mes(ctx.meses[-1])
    mapa = [
        ("kpis", "KPIs"),
        ("eficacia-eficiencia", "Eficácia vs Eficiência"),
        ("resultado-tendencia", "Resultado vs Tendência"),
        ("processos", "Processos"),
        ("jornada", "Jornada do Paciente"),
    ]
    return html.Div(
        className="visao-geral",
        children=[
            html.Section(
                className="vg-proposito",
                children=[
                    html.H2("Para que serve este painel", className="secao-titulo"),
                    html.P(
                        "Acompanha o fluxo do paciente da tomografia de planejamento ao fim do tratamento no Serviço "
                        "de Radioterapia do Grupo Hospitalar Conceição (100% SUS). O objetivo é reduzir o tempo até o "
                        "início do tratamento e usar bem o acelerador linear. A informação central é o tempo entre as "
                        "atividades de cada paciente, em cada ciclo de planejamento."
                    ),
                    html.P(id="vg-frase", className="vg-frase", role="status", **{"aria-live": "polite"}),
                ],
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
                            "Cada pergunta leva à aba onde ela é respondida.",
                            html.Ol(
                                [
                                    html.Li([p, " ", _ir(aba, "→ abrir", f"perg-{i}")])
                                    for i, (p, aba) in enumerate(PERGUNTAS_NEGOCIO, 1)
                                ],
                                className="lista-perguntas",
                            ),
                        ),
                        lg=6,
                    ),
                ],
                className="g-3",
            ),
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
            dbc.Row(
                [
                    dbc.Col(
                        _secao(
                            "Definições e metas",
                            "Regras de negócio usadas nos cálculos (config/settings.yaml).",
                            html.Dl(
                                [
                                    html.Dt("Ciclo de planejamento"),
                                    html.Dd("Da importação da TC até a última atividade antes do próximo ciclo."),
                                    html.Dt("Tipo de fluxo"),
                                    html.Dd(
                                        "Eletivo, Prioridade, Urgência, Braquiterapia e Retomografado (pelo nome da "
                                        "tarefa no Aria). Prazo do planejamento: "
                                        + ", ".join(
                                            f"{k} {v} dia(s) útil(eis)"
                                            for k, v in st.prazo_planejamento_dias_uteis.items()
                                        )
                                        + "."
                                    ),
                                    html.Dt("Turno"),
                                    html.Dd("Dia: atendimentos agendados até 18h45. Noite: a partir das 19h."),
                                    html.Dt("Capacidade do acelerador"),
                                    html.Dd(
                                        f"{st.acelerador.vagas_por_dia} vagas por dia, das "
                                        f"{st.acelerador.abertura:%H:%M} às {st.acelerador.fechamento:%H:%M}."
                                    ),
                                    html.Dt("Metas"),
                                    html.Dd(
                                        f"Ocupação do acelerador {st.meta_ocupacao_acelerador[0]:.0%} a "
                                        f"{st.meta_ocupacao_acelerador[1]:.0%}. Tarefas no prazo e duração do ciclo: "
                                        + (
                                            "definidas em config/settings.yaml."
                                            if st.meta_pct_no_prazo or st.meta_lead_time_dias
                                            else "ainda sem meta definida pela gestão."
                                        )
                                    ),
                                ],
                                className="lista-definicoes",
                            ),
                        ),
                        lg=6,
                    ),
                    dbc.Col(
                        _secao(
                            "Qualidade e limites dos dados",
                            "O que o painel cobre e o que ainda falta.",
                            html.Ul(
                                [
                                    html.Li(f"Período coberto: {ini} a {fim}. Dados anonimizados do Sistema Aria."),
                                    html.Li(
                                        f"{len(ctx.ds.ciclos):,} ciclos de planejamento, {len(ctx.ds.jornada):,} "
                                        f"atividades e {len(ctx.ds.sessoes):,} agendamentos no acelerador.".replace(
                                            ",", "."
                                        )
                                    ),
                                    html.Li("Faltas no acelerador e CID por paciente: sem fonte de dados até agora."),
                                    html.Li(
                                        "Tomografia: sem agenda própria; a ocupação é estimada por “Importar TC e "
                                        "Fusao”."
                                    ),
                                    html.Li("Sessões acima de 60 min são tratadas como erro de registro."),
                                ]
                            ),
                        ),
                        lg=6,
                    ),
                ],
                className="g-3",
            ),
            _secao(
                "Ficha técnica dos indicadores",
                "O que cada indicador mede, como é calculado e como ler.",
                html.Div(_tabela_ficha(), className="tabela-rolavel"),
            ),
            _secao(
                "Acessibilidade",
                "Segue a WCAG 2.2 nível AA (base da EN 301 549).",
                html.Ul(
                    [
                        html.Li(
                            "Navegação por teclado: Tab e Shift+Tab percorrem os controles; nas abas, use as setas."
                        ),
                        html.Li("“Pular para o conteúdo” é o primeiro item ao pressionar Tab."),
                        html.Li(
                            "O interruptor “Alto contraste”, no cabeçalho, troca o gradiente por cores sólidas e "
                            "acrescenta hachuras, traços e símbolos às séries. A escolha fica salva neste navegador."
                        ),
                        html.Li(
                            "Cada gráfico tem um resumo em texto logo abaixo e o botão “Ver dados em tabela” com os "
                            "mesmos valores."
                        ),
                        html.Li("Situações frente à meta usam ícone e palavra (✓ ! ✕), não só cor."),
                    ]
                ),
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


ABAS = [
    ("visao-geral", "Visão Geral", visao_geral_aba),
    ("kpis", "KPIs", kpis_aba),
    ("eficacia-eficiencia", "Eficácia vs Eficiência", eficacia_eficiencia_aba),
    ("resultado-tendencia", "Resultado vs Tendência", resultado_tendencia_aba),
    ("processos", "Processos", processos_aba),
    ("jornada", "Jornada do Paciente", jornada_aba),
]
