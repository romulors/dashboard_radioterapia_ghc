"""Leitura da configuração (config/settings.yaml) e regras de negócio derivadas dela."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import time
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SETTINGS = PROJECT_ROOT / "config" / "settings.yaml"


def _parse_time(value: str) -> time:
    hours, minutes = value.split(":")
    return time(int(hours), int(minutes))


def _minutes(t: time) -> int:
    return t.hour * 60 + t.minute


@dataclass(frozen=True)
class FaixaEspecial:
    inicio: time
    fim: time
    vaga_minutos: int


@dataclass(frozen=True)
class Acelerador:
    abertura: time
    fechamento: time
    vaga_minutos: int
    faixas_especiais: tuple[FaixaEspecial, ...] = ()

    @property
    def minutos_por_dia(self) -> int:
        return _minutes(self.fechamento) - _minutes(self.abertura)

    @property
    def vagas_por_dia(self) -> int:
        """Vagas diárias: faixas especiais com vaga própria, resto com a vaga padrão."""
        especiais = sum((_minutes(f.fim) - _minutes(f.inicio)) // f.vaga_minutos for f in self.faixas_especiais)
        minutos_especiais = sum(_minutes(f.fim) - _minutes(f.inicio) for f in self.faixas_especiais)
        regulares = (self.minutos_por_dia - minutos_especiais) // self.vaga_minutos
        return regulares + especiais


@dataclass(frozen=True)
class Settings:
    raiz: Path
    arquivo_tarefas: Path
    arquivo_consultas: Path
    pasta_processados: Path
    inicio_noite: time
    acelerador: Acelerador
    meta_ocupacao_acelerador: tuple[float, float]
    meta_ocupacao_tomografo: tuple[float, float]
    prazo_planejamento_dias_uteis: dict[str, int] = field(default_factory=dict)
    meta_pct_no_prazo: tuple[float, float] | None = None
    meta_lead_time_dias: float | None = None
    meta_pacientes_novos: float | None = None  # por mês; meta = acima deste valor
    host: str = "127.0.0.1"
    port: int = 8050
    debug: bool = False


def load_settings(path: Path | str = DEFAULT_SETTINGS, raiz: Path | None = None) -> Settings:
    path = Path(path)
    raiz = raiz or path.resolve().parents[1]
    cfg = yaml.safe_load(path.read_text(encoding="utf-8"))
    dados, acel, metas, app = cfg["dados"], cfg["acelerador"], cfg["metas"], cfg.get("app", {})
    return Settings(
        raiz=raiz,
        arquivo_tarefas=raiz / dados["tarefas"],
        arquivo_consultas=raiz / dados["consultas"],
        pasta_processados=raiz / dados["processados"],
        inicio_noite=_parse_time(cfg["turno"]["inicio_noite"]),
        acelerador=Acelerador(
            abertura=_parse_time(acel["abertura"]),
            fechamento=_parse_time(acel["fechamento"]),
            vaga_minutos=int(acel["vaga_minutos"]),
            faixas_especiais=tuple(
                FaixaEspecial(_parse_time(f["inicio"]), _parse_time(f["fim"]), int(f["vaga_minutos"]))
                for f in acel.get("faixas_especiais", [])
            ),
        ),
        meta_ocupacao_acelerador=tuple(metas["ocupacao_acelerador"]),
        meta_ocupacao_tomografo=tuple(metas["ocupacao_tomografo"]),
        prazo_planejamento_dias_uteis=dict(metas.get("prazo_planejamento_dias_uteis", {})),
        meta_pct_no_prazo=tuple(metas["pct_no_prazo"]) if metas.get("pct_no_prazo") else None,
        meta_lead_time_dias=float(metas["lead_time_mediana_dias"]) if metas.get("lead_time_mediana_dias") else None,
        meta_pacientes_novos=float(metas["pacientes_novos_mes"]) if metas.get("pacientes_novos_mes") else None,
        host=app.get("host", "127.0.0.1"),
        port=int(app.get("port", 8050)),
        debug=bool(app.get("debug", False)),
    )
