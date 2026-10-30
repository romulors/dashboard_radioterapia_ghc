"""Conjunto de dados do dashboard: ETL das planilhas, cache em parquet e filtros."""

from __future__ import annotations

from dataclasses import dataclass, fields
from pathlib import Path

import pandas as pd

from rt_dash.config import Settings
from rt_dash.domain.activities import anotar_tarefas
from rt_dash.domain.cycles import construir_jornada, resumir_ciclos
from rt_dash.domain.treatment import (
    cursos_de_tratamento,
    ligar_ciclos_ao_tratamento,
    preparar_sessoes,
)
from rt_dash.io.loaders import carregar_consultas, carregar_tarefas

# Aumente quando mudar o ETL ou as regras de domínio: invalida o cache parquet.
VERSAO_CACHE = "3"


@dataclass(frozen=True)
class Dataset:
    tarefas: pd.DataFrame  # todas as tarefas do Aria, anotadas
    jornada: pd.DataFrame  # atividades concluídas do fluxo, com ciclo e tempos
    ciclos: pd.DataFrame  # um registro por ciclo de planejamento
    sessoes: pd.DataFrame  # agendamentos no acelerador linear
    cursos: pd.DataFrame  # cursos de tratamento por paciente

    @property
    def meses(self) -> list[pd.Timestamp]:
        todos = pd.concat([self.jornada["mes"], self.sessoes["mes"]]).dropna().unique()
        return sorted(pd.Timestamp(m) for m in todos)


def construir_dataset(tarefas: pd.DataFrame, consultas: pd.DataFrame, settings: Settings) -> Dataset:
    tarefas = anotar_tarefas(tarefas)
    tarefas["mes"] = tarefas["termino"].fillna(tarefas["vencimento"]).dt.to_period("M").dt.to_timestamp()
    jornada = construir_jornada(tarefas)
    sessoes = preparar_sessoes(consultas, settings.inicio_noite)
    ciclos = ligar_ciclos_ao_tratamento(resumir_ciclos(jornada), sessoes)
    return Dataset(
        tarefas=tarefas,
        jornada=jornada,
        ciclos=ciclos,
        sessoes=sessoes,
        cursos=cursos_de_tratamento(sessoes),
    )


def _arquivos_cache(pasta: Path) -> dict[str, Path]:
    return {f.name: pasta / f"{f.name}.parquet" for f in fields(Dataset)}


def carregar_dataset(settings: Settings, recriar: bool = False) -> Dataset:
    """Lê do cache parquet; refaz o ETL se o cache não existir ou for mais antigo que as planilhas."""
    cache = _arquivos_cache(settings.pasta_processados)
    fontes = [settings.arquivo_tarefas, settings.arquivo_consultas]
    mais_novo = max(p.stat().st_mtime for p in fontes)
    arquivo_versao = settings.pasta_processados / "versao.txt"
    valido = (
        arquivo_versao.exists()
        and arquivo_versao.read_text(encoding="utf-8").strip() == VERSAO_CACHE
        and all(p.exists() and p.stat().st_mtime >= mais_novo for p in cache.values())
    )
    if valido and not recriar:
        return Dataset(**{nome: pd.read_parquet(p) for nome, p in cache.items()})

    ds = construir_dataset(
        carregar_tarefas(settings.arquivo_tarefas),
        carregar_consultas(settings.arquivo_consultas),
        settings,
    )
    settings.pasta_processados.mkdir(parents=True, exist_ok=True)
    for nome, p in cache.items():
        getattr(ds, nome).to_parquet(p, index=False)
    arquivo_versao.write_text(VERSAO_CACHE, encoding="utf-8")
    return ds


@dataclass(frozen=True)
class Filtros:
    """Filtros globais da barra superior. Listas vazias = sem filtro."""

    mes_inicio: pd.Timestamp | None = None
    mes_fim: pd.Timestamp | None = None
    tipos_fluxo: tuple[str, ...] = ()
    sitios: tuple[str, ...] = ()
    internado: bool | None = None

    def _periodo(self, mes: pd.Series) -> pd.Series:
        ok = pd.Series(True, index=mes.index)
        if self.mes_inicio is not None:
            ok &= mes >= self.mes_inicio
        if self.mes_fim is not None:
            ok &= mes <= self.mes_fim
        return ok

    def aplicar(self, ds: Dataset) -> Dataset:
        ciclos = ds.ciclos[self._periodo(ds.ciclos["mes"])]
        if self.tipos_fluxo:
            ciclos = ciclos[ciclos["tipo_fluxo"].isin(self.tipos_fluxo)]
        jornada = ds.jornada[ds.jornada["ciclo_id"].isin(ciclos["ciclo_id"])]

        sessoes = ds.sessoes[self._periodo(ds.sessoes["mes"])]
        if self.sitios:
            sessoes = sessoes[sessoes["sitio"].isin(self.sitios)]
        if self.internado is not None:
            sessoes = sessoes[sessoes["internado"] == self.internado]
        cursos = ds.cursos[self._periodo(ds.cursos["inicio_tratamento"].dt.to_period("M").dt.to_timestamp())]
        if self.sitios:
            cursos = cursos[cursos["sitio"].isin(self.sitios)]
        if self.internado is not None:
            cursos = cursos[cursos["internado"] == self.internado]

        tarefas = ds.tarefas[self._periodo(ds.tarefas["mes"])]
        return Dataset(tarefas=tarefas, jornada=jornada, ciclos=ciclos, sessoes=sessoes, cursos=cursos)
