"""Texto do ícone de ajuda (?) de cada gráfico: como o indicador é calculado.

Substitui a antiga "Ficha técnica" da Visão Geral. Gráficos das séries mensais (`g-vg-*` e `g-ap-*`) usam a
descrição do próprio indicador no registro; os demais têm o texto aqui.
"""

from __future__ import annotations

from rt_dash.metrics.fluxo import TOLERANCIA_FAIXA, TOLERANCIA_LIMITE
from rt_dash.metrics.registry import REGISTRO

_DURACAO_CICLO = "Duração do ciclo = dias entre o início do ciclo e o término da última tarefa registrada nele."
_ESPERA_AL = "Espera = início do atendimento − check-in, em minutos; só sessões de tratamento entre −60 e 240 min."

CALCULO: dict[str, str] = {
    # Visão Geral: resumo do serviço
    "g-vg-res-novos": "Pacientes distintos com agendamento “Início do Tratamento” no acelerador, por mês. "
    "A linha pontilhada cinza é a média dos últimos 6 meses; a tracejada verde, a meta.",
    "g-vg-res-fluxo": "Ciclos de planejamento de cada tipo de fluxo (Eletivo, Prioridade, Urgência) ÷ total de "
    "ciclos do mês; cada barra soma 100%.",
    "g-vg-res-turno": "Sessões de tratamento por mês, separadas pelo horário agendado: dia até 18h45, noite a partir "
    "das 19h.",
    "g-vg-res-sitio": "Pacientes distintos com sessão de tratamento no período filtrado, por sítio do curso "
    "(15 maiores).",
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


# ---------------------------------------------------------------- metas e tolerâncias
_settings = None

# Gráfico → (campo da meta em Settings, polaridade, formato). A meta vem de config/settings.yaml.
_OCUPACAO = ("meta_ocupacao_acelerador", "faixa", "pct")
_TOMOGRAFO = ("meta_ocupacao_tomografo", "faixa", "pct")
_PRAZO = ("meta_pct_no_prazo", "acima", "pct")
_LEAD = ("meta_lead_time_dias", "abaixo", "dias")
_NOVOS = ("meta_pacientes_novos", "acima", "num")
_SESSOES = ("meta_sessoes_mes", "acima", "num")
_DURACAO = ("meta_duracao_sessao_min", "abaixo", "min")
METAS_GRAFICO = {
    "g-al-ocupacao": _OCUPACAO,
    "g-sc-ocupacao": _OCUPACAO,
    "g-vg-ocupacao_acelerador": _OCUPACAO,
    "g-vg-ocupacao_tomografo": _TOMOGRAFO,
    "g-ap-ocupacao_acelerador": _OCUPACAO,
    "g-sc-prazo": _PRAZO,
    "g-vg-no_prazo": _PRAZO,
    "g-vg-lead_time": _LEAD,
    "g-vg-sessoes_turno": _SESSOES,
    "g-vg-duracao_sessao": _DURACAO,
    "g-vg-pacientes_iniciaram": _NOVOS,
    "g-ap-no_prazo": _PRAZO,
    "g-nv-controle": _LEAD,
    "g-nv-ridgeline": _LEAD,
    "g-nv-dotstrip": _LEAD,
    "g-vg-res-novos": _NOVOS,
    "g-prod-inicios": _NOVOS,
    "g-vg-inicios": _NOVOS,
    "g-ap-inicios": _NOVOS,
}


def configurar(settings) -> None:
    """Guarda as configurações para os textos de meta (chamado ao montar o app)."""
    global _settings
    _settings = settings


def _fmt(v: float, formato: str) -> str:
    n = v * 100 if formato == "pct" else v
    texto = f"{n:.2f}".rstrip("0").rstrip(".").replace(".", ",")
    if formato == "num":
        return f"{v:.0f}" if float(v).is_integer() else texto
    if formato == "min":
        return f"{texto} min"
    return f"{texto}%" if formato == "pct" else f"{texto} dias"


def meta_e_tolerancia(id_: str) -> tuple[str, str] | None:
    """(meta, tolerância) do gráfico em texto; None quando o indicador não tem meta."""
    if id_ == "g-sc-winloss":
        return (
            "a de cada indicador (ocupação do AL, tarefas no prazo, duração do ciclo, pacientes novos, sessões e "
            "duração da sessão), definida em config/settings.yaml e listada na aba Sobre.",
            "",
        )
    if id_ not in METAS_GRAFICO:
        return None
    campo, polaridade, formato = METAS_GRAFICO[id_]
    meta = getattr(_settings, campo, None) if _settings is not None else None
    if meta is None:
        return ("ainda não definida pela gestão (config/settings.yaml).", "")
    lo, hi = meta if isinstance(meta, tuple | list) else (meta, meta)
    if polaridade == "faixa":
        alvo = f"entre {_fmt(lo, formato)} e {_fmt(hi, formato)}"
        tol = (
            f"até {TOLERANCIA_FAIXA:.0%} além da faixa ({_fmt(lo * (1 - TOLERANCIA_FAIXA), formato)} a "
            f"{_fmt(hi * (1 + TOLERANCIA_FAIXA), formato)}) conta como “atenção”; além disso, “fora da meta”."
        )
    elif polaridade == "acima":
        alvo = f"acima de {_fmt(lo, formato)} por mês"
        tol = (
            f"até {TOLERANCIA_LIMITE:.0%} abaixo (de {_fmt(lo * (1 - TOLERANCIA_LIMITE), formato)} "
            f"a {_fmt(lo, formato)}) conta como “atenção”; abaixo disso, “fora da meta”."
        )
    elif polaridade == "maior":
        alvo = f"{_fmt(lo, formato)} ou mais"
        tol = (
            f"até {TOLERANCIA_LIMITE:.0%} abaixo (a partir de {_fmt(lo * (1 - TOLERANCIA_LIMITE), formato)}) conta "
            "como “atenção”; abaixo disso, “fora da meta”."
        )
    elif polaridade == "abaixo":
        alvo = f"abaixo de {_fmt(hi, formato)}" + (" (mediana)" if formato == "dias" else " (média do mês)")
        tol = (
            f"de {_fmt(hi, formato)} até {TOLERANCIA_LIMITE:.0%} acima ({_fmt(hi * (1 + TOLERANCIA_LIMITE), formato)}) "
            "conta como “atenção”; acima disso, “fora da meta”."
        )
    else:
        alvo = f"{_fmt(hi, formato)} ou menos (mediana)"
        tol = (
            f"até {TOLERANCIA_LIMITE:.0%} acima (até {_fmt(hi * (1 + TOLERANCIA_LIMITE), formato)}) conta como "
            "“atenção”; acima disso, “fora da meta”."
        )
    return (alvo + ".", tol)
