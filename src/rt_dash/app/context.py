"""Estado compartilhado entre as páginas: configuração, dados e filtros (com cache)."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import lru_cache

import pandas as pd

from rt_dash.config import Settings
from rt_dash.data import Dataset, Filtros
from rt_dash.metrics.activity import limiar_p90


@dataclass
class AppContext:
    settings: Settings
    ds: Dataset
    _cache: dict = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        self.meses = self.ds.meses
        self.sitios = sorted(self.ds.sessoes["sitio"].dropna().unique())
        self.limiar_espera = limiar_p90(self.ds.jornada, "espera_min")
        self._filtrar = lru_cache(maxsize=64)(self._filtrar_sem_cache)

    def filtros(self, estado: dict | None, selecao: dict | None = None, usar_mes: bool = False) -> Filtros:
        estado = estado or {}
        ini, fim = estado.get("periodo") or [0, len(self.meses) - 1]
        mes_ini, mes_fim = self.meses[ini], self.meses[fim]
        if usar_mes and selecao and selecao.get("mes"):
            mes_ini = mes_fim = pd.Timestamp(selecao["mes"])
        internado = {"internado": True, "ambulatorial": False}.get(estado.get("internado") or "")
        return Filtros(
            mes_inicio=mes_ini,
            mes_fim=mes_fim,
            tipos_fluxo=tuple(estado.get("fluxos") or ()),
            sitios=tuple(estado.get("sitios") or ()),
            internado=internado,
        )

    def dados(self, estado: dict | None, selecao: dict | None = None, usar_mes: bool = False) -> Dataset:
        f = self.filtros(estado, selecao, usar_mes)
        chave = json.dumps(
            [str(f.mes_inicio), str(f.mes_fim), f.tipos_fluxo, f.sitios, f.internado], ensure_ascii=False
        )
        return self._filtrar(chave)

    def _filtrar_sem_cache(self, chave: str) -> Dataset:
        ini, fim, fluxos, sitios, internado = json.loads(chave)
        return Filtros(pd.Timestamp(ini), pd.Timestamp(fim), tuple(fluxos), tuple(sitios), internado).aplicar(self.ds)
