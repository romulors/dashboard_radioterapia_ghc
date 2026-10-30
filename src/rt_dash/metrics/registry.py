"""Registro de indicadores mensais.

Cada indicador é uma função `(Dataset, Settings) -> DataFrame` com as colunas
`mes`, `valor` e, opcionalmente, `serie`. Para criar um indicador novo basta decorar
a função com @indicador(...): as telas leem o registro e não precisam mudar.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import pandas as pd

from rt_dash.config import Settings
from rt_dash.data import Dataset

FuncaoIndicador = Callable[[Dataset, Settings], pd.DataFrame]


@dataclass(frozen=True)
class Indicador:
    id: str
    titulo: str
    unidade: str
    funcao: FuncaoIndicador
    origem: str = ""  # J = apresentação junho, A = agosto, P = perguntas de negócio
    formato: str = ",.0f"
    grafico: str = "linha"  # linha | barras_empilhadas | barras_agrupadas | barras_100
    meta: tuple[float, float] | None = None
    nota: str = ""

    def calcular(self, ds: Dataset, settings: Settings) -> pd.DataFrame:
        return self.funcao(ds, settings)


REGISTRO: dict[str, Indicador] = {}


def indicador(id: str, titulo: str, unidade: str, **kwargs) -> Callable[[FuncaoIndicador], FuncaoIndicador]:
    def registrar(funcao: FuncaoIndicador) -> FuncaoIndicador:
        if id in REGISTRO:
            raise ValueError(f"Indicador '{id}' registrado duas vezes")
        REGISTRO[id] = Indicador(id=id, titulo=titulo, unidade=unidade, funcao=funcao, **kwargs)
        return funcao

    return registrar
