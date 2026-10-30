"""Indicadores: funções puras que recebem o Dataset (já filtrado) e devolvem DataFrames."""

from rt_dash.metrics import activity, monthly, patient  # noqa: F401  (registra indicadores)
from rt_dash.metrics.registry import REGISTRO, Indicador, indicador

__all__ = ["REGISTRO", "Indicador", "indicador"]
