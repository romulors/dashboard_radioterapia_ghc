"""Segmentação Paciente -> Ciclo de planejamento -> Atividade e tempos entre atividades.

Regras (ver CLAUDE.md):
- Só tarefas concluídas das etapas do fluxo (Recepção a Controle de Qualidade).
- Um ciclo novo começa a cada atividade de INICIO_CICLO concluída.
- Recepção e Simulação preparam o ciclo seguinte: pertencem à próxima importação. Uma recepção
  sem importação depois dela abre um ciclo ainda sem planejamento.
- As demais etapas pertencem à última importação anterior. As que vêm antes da primeira
  importação do paciente são de um ciclo iniciado antes do período exportado e ficam de fora.
- espera = início da atividade - maior término anterior no ciclo. Negativa = atividades
  em paralelo (não é zerada).
- tempo_etapa = término - maior término anterior (espera + execução); para a primeira
  atividade do ciclo é a própria duração.
- atraso = término - vencimento (positivo = fora do prazo).
"""

from __future__ import annotations

import pandas as pd

from rt_dash.domain.activities import (
    ETAPAS_FLUXO,
    INICIO_CICLO,
    PREFIXO_APROVACAO,
    TIPOS_FLUXO,
    anotar_tarefas,
)

_MIN = pd.Timedelta(minutes=1)
ETAPAS_PREPARO = ("Recepção", "Simulação")


def _minutos(delta: pd.Series) -> pd.Series:
    return delta / _MIN


def construir_jornada(tarefas: pd.DataFrame) -> pd.DataFrame:
    """Uma linha por atividade concluída, com ciclo e tempos calculados."""
    t = tarefas if "etapa" in tarefas.columns else anotar_tarefas(tarefas)
    feitas = t[
        (t["status"] == "Concluído") & t["inicio"].notna() & t["termino"].notna() & t["etapa"].isin(ETAPAS_FLUXO)
    ].sort_values(["paciente_id", "inicio", "termino", "linha"], kind="stable")
    j = feitas.reset_index(drop=True)

    abre_ciclo = j["atividade"].isin(INICIO_CICLO)
    importacoes_ate_aqui = abre_ciclo.groupby(j["paciente_id"]).cumsum()
    preparo = j["etapa"].isin(ETAPAS_PREPARO) & ~abre_ciclo
    j["ciclo"] = importacoes_ate_aqui.where(~preparo, importacoes_ate_aqui + 1).astype(int)
    j = j[j["ciclo"] > 0].reset_index(drop=True)
    j["ciclo_id"] = j["paciente_id"] + "-" + j["ciclo"].astype(str)
    # ordem cronológica dentro do ciclo (a recepção vem antes da importação)
    j = j.sort_values(["paciente_id", "ciclo", "inicio", "termino", "linha"], kind="stable").reset_index(drop=True)

    grupo = j.groupby("ciclo_id", sort=False)
    termino_anterior = grupo["termino"].transform(lambda s: s.cummax().shift())
    j["espera_min"] = _minutos(j["inicio"] - termino_anterior)
    j["duracao_min"] = _minutos(j["termino"] - j["inicio"])
    j["tempo_etapa_min"] = _minutos(j["termino"] - termino_anterior).fillna(j["duracao_min"])
    j["atraso_min"] = _minutos(j["termino"] - j["vencimento"])
    j["no_prazo"] = (j["atraso_min"] <= 0).where(j["vencimento"].notna())

    inicio_import = j["inicio"].where(j["atividade"].isin(INICIO_CICLO)).groupby(j["ciclo_id"]).transform("min")
    j["ciclo_inicio"] = inicio_import.fillna(grupo["inicio"].transform("min"))
    j["acumulado_min"] = _minutos(j["termino"] - j["ciclo_inicio"])
    j["ordem"] = grupo.cumcount() + 1
    j["tipo_fluxo"] = j["ciclo_id"].map(_tipo_fluxo_por_ciclo(j))
    j["mes"] = j["termino"].dt.to_period("M").dt.to_timestamp()
    return j


def _tipo_fluxo_por_ciclo(jornada: pd.DataFrame) -> pd.Series:
    """Retomografado e Braquiterapia prevalecem; senão, o tipo mais frequente no ciclo."""

    def escolher(tipos: pd.Series) -> str:
        presentes = tipos.dropna()
        if presentes.empty:
            return "Sem tipo"
        for especial in ("Retomografado", "Braquiterapia"):
            if (presentes == especial).any():
                return especial
        contagem = presentes.value_counts()
        maximo = contagem.max()
        for tipo in TIPOS_FLUXO:
            if contagem.get(tipo, 0) == maximo:
                return tipo
        return str(contagem.index[0])

    return jornada.groupby("ciclo_id")["tipo_fluxo_atividade"].agg(escolher)


def resumir_ciclos(jornada: pd.DataFrame) -> pd.DataFrame:
    """Uma linha por ciclo de planejamento."""
    j = jornada
    aprovacao = (
        j[j["atividade"].str.startswith(PREFIXO_APROVACAO, na=False)]
        .groupby("ciclo_id")["termino"]
        .min()
        .rename("aprovacao")
    )
    importou = j[j["atividade"].isin(INICIO_CICLO)].groupby("ciclo_id")["inicio"].min().rename("importacao")
    resumo = j.groupby("ciclo_id").agg(
        paciente_id=("paciente_id", "first"),
        ciclo=("ciclo", "first"),
        tipo_fluxo=("tipo_fluxo", "first"),
        inicio=("ciclo_inicio", "first"),
        primeira_atividade=("inicio", "min"),
        fim=("termino", "max"),
        n_atividades=("atividade", "size"),
        espera_total_min=("espera_min", lambda s: s.clip(lower=0).sum()),
        n_atrasadas=("no_prazo", lambda s: int((s == False).sum())),  # noqa: E712
        n_com_prazo=("no_prazo", lambda s: int(s.notna().sum())),
    )
    resumo = resumo.join(aprovacao).join(importou).reset_index()
    resumo["tem_importacao"] = resumo["importacao"].notna()
    resumo["lead_time_dias"] = (resumo["fim"] - resumo["inicio"]) / pd.Timedelta(days=1)
    resumo["ate_aprovacao_dias"] = (resumo["aprovacao"] - resumo["inicio"]) / pd.Timedelta(days=1)
    resumo["pct_no_prazo"] = 1 - resumo["n_atrasadas"] / resumo["n_com_prazo"].where(resumo["n_com_prazo"] > 0)
    referencia = resumo["aprovacao"].fillna(resumo["fim"])
    resumo["mes"] = referencia.dt.to_period("M").dt.to_timestamp()
    return resumo.sort_values(["paciente_id", "ciclo"]).reset_index(drop=True)
