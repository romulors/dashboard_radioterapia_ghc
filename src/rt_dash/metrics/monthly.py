"""Indicadores mensais das apresentações de junho e agosto/2026."""

from __future__ import annotations

import pandas as pd

from rt_dash.config import Settings
from rt_dash.data import Dataset
from rt_dash.domain.activities import TIPOS_FLUXO
from rt_dash.metrics.registry import indicador


def _contar(df: pd.DataFrame, por: list[str], nome: str = "valor") -> pd.DataFrame:
    return df.groupby(por, observed=True).size().rename(nome).reset_index()


@indicador("inicios", "Atividades de início em radioterapia", "inícios", origem="J, A")
def inicios_por_mes(ds: Dataset, _: Settings) -> pd.DataFrame:
    s = ds.sessoes
    return _contar(s[s["tipo_agendamento"] == "Início"], ["mes"])


@indicador(
    "pacientes_iniciaram",
    "Pacientes (sítios) que iniciaram tratamento",
    "pacientes",
    origem="J",
)
def pacientes_que_iniciaram(ds: Dataset, _: Settings) -> pd.DataFrame:
    s = ds.sessoes[ds.sessoes["tipo_agendamento"] == "Início"]
    return s.groupby("mes")["paciente_id"].nunique().rename("valor").reset_index()


@indicador(
    "sessoes_turno",
    "Número de sessões de radioterapia – dia e noite",
    "sessões",
    origem="J, A",
    grafico="barras_empilhadas",
)
def sessoes_por_turno(ds: Dataset, _: Settings) -> pd.DataFrame:
    s = ds.sessoes[ds.sessoes["eh_tratamento"]]
    return _contar(s, ["mes", "turno"]).rename(columns={"turno": "serie"})


@indicador(
    "ocupacao_acelerador",
    "Taxa de ocupação do acelerador linear",
    "%",
    origem="J",
    formato=".0%",
    nota="Sessões ÷ (vagas por dia × dias com atendimento no mês)",
)
def ocupacao_acelerador(ds: Dataset, settings: Settings) -> pd.DataFrame:
    s = ds.sessoes[ds.sessoes["eh_tratamento"]]
    por_mes = s.groupby("mes").agg(sessoes=("agendado", "size"), dias=("data", "nunique"))
    capacidade = por_mes["dias"] * settings.acelerador.vagas_por_dia
    return (por_mes["sessoes"] / capacidade).rename("valor").reset_index()


@indicador(
    "tomografias",
    "Ocupação do tomógrafo – exames e pacientes únicos",
    "exames",
    origem="J",
    nota="Estimado por 'Importar TC e Fusao' até haver exportação das tomografias",
)
def tomografias_por_mes(ds: Dataset, _: Settings) -> pd.DataFrame:
    t = ds.tarefas
    tc = t[(t["atividade"] == "Importar TC e Fusao") & (t["status"] == "Concluído")]
    exames = _contar(tc, ["mes"]).assign(serie="Exames")
    pacientes = tc.groupby("mes")["paciente_id"].nunique().rename("valor").reset_index()
    return pd.concat([exames, pacientes.assign(serie="Pacientes únicos")], ignore_index=True)


@indicador("planejamentos", "Número de planejamentos", "planejamentos", origem="J, A, P1")
def planejamentos_por_mes(ds: Dataset, _: Settings) -> pd.DataFrame:
    c = ds.ciclos[ds.ciclos["tem_importacao"]]
    return _contar(c, ["mes"])


@indicador(
    "planejamentos_fluxo",
    "Planejamentos Eletivos, Prioridades e Urgências",
    "planejamentos",
    origem="J, A, P2",
    grafico="barras_agrupadas",
)
def planejamentos_por_fluxo(ds: Dataset, _: Settings) -> pd.DataFrame:
    c = ds.ciclos[ds.ciclos["tem_importacao"] & ds.ciclos["tipo_fluxo"].isin(TIPOS_FLUXO[:3])]
    return _contar(c, ["mes", "tipo_fluxo"]).rename(columns={"tipo_fluxo": "serie"})


@indicador(
    "planejamentos_fluxo_pct",
    "Percentual de planejamentos por tipo de fluxo",
    "%",
    origem="J, A, P2",
    grafico="barras_100",
    formato=".0%",
)
def percentual_por_fluxo(ds: Dataset, settings: Settings) -> pd.DataFrame:
    n = planejamentos_por_fluxo(ds, settings)
    n["valor"] = n["valor"] / n.groupby("mes")["valor"].transform("sum")
    return n


@indicador(
    "duracao_sessao",
    "Tempo médio de duração das sessões",
    "min",
    origem="J",
    formato=".1f",
    nota="Exclui durações acima de 60 min (erros de registro)",
)
def duracao_media_sessao(ds: Dataset, _: Settings) -> pd.DataFrame:
    s = ds.sessoes[ds.sessoes["eh_tratamento"] & ds.sessoes["duracao_valida"]]
    return s.groupby("mes")["duracao_min"].mean().rename("valor").reset_index()


@indicador(
    "sessoes_por_tratamento",
    "Número médio de sessões por tratamento",
    "sessões",
    origem="J",
    formato=".1f",
    nota="Cursos iniciados no mês e com alta registrada",
)
def sessoes_por_tratamento(ds: Dataset, _: Settings) -> pd.DataFrame:
    c = ds.cursos[(ds.cursos["curso"] > 0) & ds.cursos["teve_alta"]]
    mes = c["inicio_tratamento"].dt.to_period("M").dt.to_timestamp()
    return c.groupby(mes)["n_sessoes"].mean().rename("valor").rename_axis("mes").reset_index()


@indicador("no_prazo", "Tarefas de planejamento concluídas no prazo", "%", origem="P7", formato=".0%")
def pct_no_prazo(ds: Dataset, _: Settings) -> pd.DataFrame:
    j = ds.jornada[ds.jornada["no_prazo"].notna()]
    return j.groupby("mes")["no_prazo"].mean().rename("valor").reset_index()


def pacientes_por_sitio(ds: Dataset) -> pd.DataFrame:
    """Pacientes distintos tratados por sítio no período (indicador 10)."""
    s = ds.sessoes[ds.sessoes["sitio"].notna()]
    return s.groupby("sitio")["paciente_id"].nunique().rename("pacientes").sort_values(ascending=False).reset_index()


def media_ultimos_meses(serie: pd.DataFrame, n: int = 6) -> float | None:
    if serie.empty:
        return None
    total = serie.groupby("mes")["valor"].sum().sort_index()
    return float(total.tail(n).mean())
