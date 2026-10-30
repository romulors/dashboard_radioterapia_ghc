"""Leitura dos relatórios do Aria exportados em Excel.

Os relatórios têm um bloco de título antes do cabeçalho e linhas de totais no fim
(Máx, Média, DEV STD). O cabeçalho é a linha cuja célula vale "#".
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from rt_dash.io.schemas import (
    CONSULTAS_COLUNAS,
    CONSULTAS_DATAS,
    TAREFAS_COLUNAS,
    TAREFAS_DATAS,
    SchemaError,
    normalizar,
)


def ler_relatorio_aria(caminho: Path | str, aba: int | str = 1) -> pd.DataFrame:
    """Lê a aba de dados de um relatório do Aria, com o cabeçalho real e colunas sem espaços."""
    bruto = pd.read_excel(caminho, sheet_name=aba, header=None)
    linhas_cabecalho = bruto.index[bruto.apply(lambda r: r.astype(str).str.strip().eq("#").any(), axis=1)]
    if len(linhas_cabecalho) == 0:
        raise SchemaError(f"{caminho}: cabeçalho com a coluna '#' não encontrado")
    i = linhas_cabecalho[0]
    cabecalho = bruto.iloc[i].map(lambda v: str(v).strip() if pd.notna(v) else None)
    dados = bruto.iloc[i + 1 :].copy()
    dados.columns = cabecalho
    dados = dados.loc[:, [c is not None for c in dados.columns]]
    return dados.reset_index(drop=True)


def carregar_tarefas(caminho: Path | str) -> pd.DataFrame:
    return normalizar(ler_relatorio_aria(caminho), TAREFAS_COLUNAS, TAREFAS_DATAS, "Tarefas RT")


def carregar_consultas(caminho: Path | str) -> pd.DataFrame:
    df = normalizar(ler_relatorio_aria(caminho), CONSULTAS_COLUNAS, CONSULTAS_DATAS, "Consultas AL")
    df["duracao_min"] = pd.to_numeric(df["duracao_min"], errors="coerce")
    return df
