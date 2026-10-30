"""Contratos das planilhas: colunas esperadas e nomes internos (snake_case)."""

from __future__ import annotations

import pandas as pd

TAREFAS_COLUNAS = {
    "#": "linha",
    "Id do Paciente": "paciente_id",
    "Nome da Atividade": "atividade",
    "Categoria da Atividade": "categoria",
    "Status": "status",
    "Ultima edição por": "usuario",
    "Hora Vencimento": "vencimento",
    "Hora de Inicio": "inicio",
    "Hora de Termino": "termino",
}

CONSULTAS_COLUNAS = {
    "#": "linha",
    "ID do paciente": "paciente_id",
    "Atividade": "atividade",
    "Horário do agendamento (SC)": "agendado",
    "Horário do check in (CK)": "checkin",
    "Hora de início (ST)": "inicio",
    "Hora de término (ET)": "termino",
    "Duração (AD)": "duracao_min",
}

TAREFAS_DATAS = ("vencimento", "inicio", "termino")
CONSULTAS_DATAS = ("agendado", "checkin", "inicio", "termino")


class SchemaError(ValueError):
    """A planilha não tem o formato esperado da exportação do Aria."""


def validar_colunas(df: pd.DataFrame, esperadas: dict[str, str], origem: str) -> None:
    faltando = [c for c in esperadas if c not in df.columns]
    if faltando:
        raise SchemaError(f"{origem}: colunas ausentes {faltando}. Colunas encontradas: {list(df.columns)}")


def normalizar(df: pd.DataFrame, esperadas: dict[str, str], datas: tuple[str, ...], origem: str) -> pd.DataFrame:
    """Valida, renomeia, tipa as colunas e descarta linhas de rodapé (sem número de linha)."""
    validar_colunas(df, esperadas, origem)
    out = df[list(esperadas)].rename(columns=esperadas)
    out["linha"] = pd.to_numeric(out["linha"], errors="coerce")
    out = out[out["linha"].notna() & out["paciente_id"].notna()].copy()
    out["linha"] = out["linha"].astype(int)
    out["paciente_id"] = out["paciente_id"].astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
    for col in datas:
        out[col] = pd.to_datetime(out[col], errors="coerce")
    textos = [c for c in out.columns if c not in (*datas, "paciente_id", "linha")]
    for col in textos:
        if out[col].dtype == object or str(out[col].dtype) in ("str", "string"):
            out[col] = out[col].astype("string").str.strip()
    return out.reset_index(drop=True)
