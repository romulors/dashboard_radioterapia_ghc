"""Catálogo das atividades do Aria: etapa do fluxo, tipo de fluxo e nome genérico."""

from __future__ import annotations

import re

import pandas as pd

TIPOS_FLUXO = ("Eletivo", "Prioridade", "Urgência", "Braquiterapia", "Retomografado")

# Etapas na ordem do processo (2024 12 06 - Fluxo Radioterapia.PNG).
ETAPAS_FLUXO = ("Recepção", "Simulação", "Planejamento", "Pré-Tratamento", "Controle de Qualidade")

_ETAPA_POR_CODIGO = {
    "2": "Recepção",
    "3": "Simulação",
    "4": "Planejamento",
    "5": "Pré-Tratamento",
    "8": "Controle de Qualidade",
    "G": "Gestão",
    "V": "Revisão",
}

# Atividades que abrem um novo ciclo de planejamento (nova TC ou nova radiografia).
INICIO_CICLO = frozenset({"Importar TC e Fusao", "Importar Radiografia"})
PREFIXO_APROVACAO = "Aprovação"

_SUFIXO_FLUXO = re.compile(
    r"\s*(?:-\s*)?(?:\d+\.\s*)?(Eletivo|Prioridade|Urgência|Retomografado|Braquiterapia|Nova TC)"
    r"(?:\s*-\s*.*)?$"
)


def etapa_da_categoria(categoria: str | None) -> str | None:
    if categoria is None or pd.isna(categoria):
        return None
    codigo = str(categoria).split("-")[0].strip()
    return _ETAPA_POR_CODIGO.get(codigo)


def tipo_fluxo_da_atividade(nome: str | None) -> str | None:
    """Tipo de fluxo indicado no nome da atividade, se houver."""
    if nome is None or pd.isna(nome):
        return None
    nome = str(nome)
    if "Retomografado" in nome or "Nova TC" in nome:
        return "Retomografado"
    if "Braquiterapia" in nome or nome == "Importar Radiografia":
        return "Braquiterapia"
    for tipo in ("Urgência", "Prioridade", "Eletivo"):
        if tipo in nome:
            return tipo
    return None


def atividade_generica(nome: str | None) -> str | None:
    """Nome da atividade sem o tipo de fluxo: 'Contorno do PTV Eletivo' -> 'Contorno do PTV'."""
    if nome is None or pd.isna(nome):
        return None
    limpo = _SUFIXO_FLUXO.sub("", str(nome)).strip(" -")
    return limpo or str(nome)


def anotar_tarefas(tarefas: pd.DataFrame) -> pd.DataFrame:
    """Acrescenta etapa, tipo de fluxo e atividade genérica a cada tarefa."""
    out = tarefas.copy()
    out["etapa"] = out["categoria"].map(etapa_da_categoria)
    out["tipo_fluxo_atividade"] = out["atividade"].map(tipo_fluxo_da_atividade)
    out["atividade_generica"] = out["atividade"].map(atividade_generica)
    return out
