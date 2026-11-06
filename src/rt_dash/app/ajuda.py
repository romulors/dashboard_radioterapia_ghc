"""Texto do ícone de ajuda (?) de cada gráfico: como o indicador é calculado.

Substitui a antiga "Ficha técnica" da Visão Geral. Gráficos das séries mensais (`g-vg-*` e `g-ap-*`) usam a
descrição do próprio indicador no registro; os demais têm o texto aqui.
"""

from __future__ import annotations

from rt_dash.metrics.registry import REGISTRO

_DURACAO_CICLO = "Duração do ciclo = dias entre o início do ciclo e o término da última tarefa registrada nele."
_ESPERA_AL = "Espera = início do atendimento − check-in, em minutos; só sessões de tratamento entre −60 e 240 min."

CALCULO: dict[str, str] = {
    # KPIs / scorecard
    "g-ap-sitios": "Pacientes distintos com sessão de tratamento no mês, agrupados pelo sítio do curso.",
    "g-sc-ocupacao": "Sessões de tratamento ÷ (vagas por dia × dias com atendimento) no mês de referência, "
    "comparado à faixa de meta de 80–85%.",
    "g-sc-prazo": "Tarefas de planejamento com término até o vencimento ÷ tarefas com vencimento, no mês de "
    "referência, comparado à meta (quando definida em settings.yaml).",
    "g-sc-winloss": "Para cada mês e indicador com meta: ▲ quando o valor do mês ficou dentro da meta, ▼ quando "
    "ficou fora.",
    # Eficácia
    "g-al-ocupacao": "Sessões de tratamento ÷ (vagas por dia × dias com atendimento no mês). As vagas por dia vêm "
    "das regras do acelerador (07h–22h30, 15 min; 20 min nas janelas de início).",
    "g-prod-inicios": "Pacientes distintos com agendamento “Início do Tratamento” no acelerador, por mês.",
    "g-prod-fluxo": "Ciclos de planejamento contados no mês da aprovação, separados pelo tipo de fluxo "
    "(Eletivo, Prioridade, Urgência).",
    "g-nv-waffle": "Ciclos com TC importada no período, por tipo de fluxo; cada quadrado equivale a 1% do total.",
    "g-prod-sitio": "Pacientes distintos com sessão de tratamento no mês de referência, por sítio (15 maiores).",
    # Eficiência
    "g-nv-ridgeline": f"Distribuição da duração do ciclo em cada mês (mês da aprovação). {_DURACAO_CICLO} "
    "O traço marca a mediana; valores acima do P95 são cortados.",
    "g-al-espera": f"Histograma da espera de cada sessão. {_ESPERA_AL}",
    "g-nv-barbell": f"Mediana da espera de dia (até 18h45) e de noite (a partir das 19h) por sítio. {_ESPERA_AL} "
    "Só sítios com 20 ou mais sessões em cada turno.",
    "g-al-espera-hora": f"Mediana e faixa P25–P75 da espera, agrupada pela hora agendada. {_ESPERA_AL}",
    "g-al-duracao-sitio": "Duração da sessão (término − início) nos 12 sítios com mais sessões; registros acima "
    "de 60 min são descartados.",
    "g-al-duracao": "Média mensal da duração das sessões de tratamento (término − início), excluindo registros "
    "acima de 60 min.",
    "g-al-sessoes-trat": "Média de sessões por curso de tratamento, pelo mês de início, só cursos com alta registrada.",
    # Resultado
    "g-prod-turno": "Sessões de tratamento por mês, separadas pelo horário agendado: dia até 18h45, noite a partir "
    "das 19h.",
    "g-nv-indice": "Sessões de cada turno no mês ÷ sessões do mesmo turno no primeiro mês do período × 100.",
    "g-nv-calendario": "Número de sessões de tratamento em cada dia; colunas são semanas e linhas, dias da semana.",
    "g-am-funnel": "Ciclos que chegaram a cada etapa: iniciado, TC importada, plano aprovado e tratamento iniciado.",
    # Tendência
    "g-nv-wip": "Por dia, ciclos com TC importada e ainda sem aprovação do plano (sem aprovação, o ciclo fecha "
    "no término da última tarefa).",
    "g-nv-entradas": "Por semana: entradas = TCs importadas, saídas = planos aprovados; a barra é o saldo "
    "(entradas − saídas).",
    "g-nv-idade": "Dias desde a importação da TC até o fim do período, para os ciclos ainda sem aprovação. "
    "A linha é o P90 histórico do tempo até a aprovação.",
    # Processos
    "g-nv-fluxo-valor": "Para cada ciclo, soma das esperas e das execuções das atividades em cada etapa; o gráfico "
    "mostra a mediana entre ciclos, em horas. A espera antes de “Importar TC e Fusao” conta na Simulação.",
    "g-nv-controle": f"Carta de valores individuais (I-MR) da duração do ciclo, na ordem da importação da TC. "
    f"{_DURACAO_CICLO} Limites = média ± 2,66 × média das amplitudes móveis.",
    "g-nv-pareto": "Horas de espera (início da atividade − término da anterior) somadas por atividade, em ordem "
    "decrescente, com o percentual acumulado.",
    "g-nv-dotstrip": f"Cada ponto é um ciclo; o traço marca a mediana por tipo de fluxo. {_DURACAO_CICLO}",
    "g-at-barras": "Por atividade: barra = mediana e losango = P90 da medida escolhida em “Medida” "
    "(tempo da etapa = espera + execução, espera desde a atividade anterior, execução ou atraso frente ao vencimento).",
    "g-at-box": "Distribuição da medida da atividade selecionada por tipo de fluxo; cada ponto é uma ocorrência.",
    "g-at-tendencia": "Mediana mensal da medida da atividade selecionada (ou de todas, sem seleção).",
    "g-at-heatmap": "Mediana da medida por atividade (linhas) e mês (colunas).",
    "g-nv-lollipop": "Ciclos com ao menos uma tarefa concluída depois do vencimento ÷ ciclos do sítio; só sítios "
    "com 5 ou mais ciclos.",
    "g-am-scatter-facetas": "Cada ponto é um ciclo: eixo x = dias até a aprovação, eixo y = duração do ciclo; "
    "tamanho = número de atividades.",
    # Jornada
    "g-jo-gantt": "Cada barra é uma atividade do ciclo, do início ao término; a parte cinza é a espera desde o "
    "término da atividade anterior.",
    "g-jo-cascata": "Espera + execução de cada atividade, somadas em ordem até a duração total do ciclo.",
    "g-jo-comparacao": "Dias acumulados desde a importação da TC: o paciente comparado à mediana dos ciclos do "
    "mesmo tipo de fluxo.",
}


def calculo(id_: str) -> str:
    """Como o indicador do gráfico `id_` é calculado ('' quando não há texto)."""
    if id_ in CALCULO:
        return CALCULO[id_]
    for prefixo in ("g-vg-", "g-ap-"):
        if id_.startswith(prefixo):
            ind = REGISTRO.get(id_.removeprefix(prefixo))
            if ind is not None:
                partes = [ind.descricao or ind.nota or "", ind.nota if ind.descricao and ind.nota else ""]
                texto = ". ".join(p.rstrip(".") for p in partes if p)
                return f"{texto}. Unidade: {ind.unidade}." if ind.unidade else f"{texto}."
    return ""
