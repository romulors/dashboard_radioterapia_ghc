"""Dados sintéticos pequenos, no formato já normalizado pelos loaders."""

from __future__ import annotations

import pandas as pd
import pytest

from rt_dash.config import load_settings


def _t(linha, paciente, atividade, categoria, inicio, termino, vencimento=None, status="Concluído"):
    return {
        "linha": linha,
        "paciente_id": paciente,
        "atividade": atividade,
        "categoria": categoria,
        "status": status,
        "usuario": "ad\\1",
        "vencimento": pd.Timestamp(vencimento) if vencimento else pd.NaT,
        "inicio": pd.Timestamp(inicio) if inicio else pd.NaT,
        "termino": pd.Timestamp(termino) if termino else pd.NaT,
    }


@pytest.fixture
def tarefas() -> pd.DataFrame:
    rec, pla, pre = "2 - Recepção", "4 - Planejamento", "5 - Pre Tratamento"
    linhas = [
        # Paciente A: recepção + ciclo eletivo + replanejamento (nova TC)
        _t(1, "A", "Selecionar Fluxo Tratamento", rec, "2026-01-05 09:00", "2026-01-05 09:00", "2026-01-05 12:00"),
        _t(2, "A", "Importar TC e Fusao", pla, "2026-01-07 10:00", "2026-01-07 10:10", "2026-01-07 12:00"),
        _t(3, "A", "Contorno de OAR Eletivo", pla, "2026-01-07 11:00", "2026-01-07 13:00", "2026-01-08 12:00"),
        # em paralelo com o OAR: começa antes do término do OAR
        _t(4, "A", "Contorno do PTV Eletivo", pla, "2026-01-07 12:00", "2026-01-08 09:00", "2026-01-08 08:00"),
        _t(5, "A", "Aprovação Eletivo", pla, "2026-01-09 09:00", "2026-01-09 09:30", "2026-01-12 12:00"),
        _t(6, "A", "Preparar a ficha - Eletivo", pre, "2026-01-09 10:00", "2026-01-09 10:20", "2026-01-12 12:00"),
        _t(7, "A", "Importar TC e Fusao", pla, None, None, "2026-01-20 12:00", status="Cancelado"),
        _t(8, "A", "Importar TC e Fusao", pla, "2026-02-02 08:00", "2026-02-02 08:05", "2026-02-02 12:00"),
        _t(9, "A", "Contorno do PTV Retomografado", pla, "2026-02-02 09:00", "2026-02-02 10:00", "2026-02-02 12:00"),
        _t(10, "A", "Aprovação Replanejamento", pla, "2026-02-03 09:00", "2026-02-03 09:10", "2026-02-03 08:00"),
        # Paciente B: urgência
        _t(11, "B", "Importar TC e Fusao", pla, "2026-01-10 08:00", "2026-01-10 08:10", "2026-01-10 12:00"),
        _t(12, "B", "Planejamento Urgência", pla, "2026-01-10 09:00", "2026-01-10 11:00", "2026-01-10 18:00"),
        _t(13, "B", "Aprovação Urgência", pla, "2026-01-10 12:00", "2026-01-10 12:05", "2026-01-10 18:00"),
        # Revisão de imagens não entra na jornada
        _t(
            14,
            "B",
            "Revisar Imagens do Tratamento",
            "V  - Atividades especiais de revisão",
            "2026-01-20 08:00",
            "2026-01-20 08:00",
            "2026-01-19 08:00",
        ),
    ]
    return pd.DataFrame(linhas)


def _c(linha, paciente, atividade, agendado, checkin, inicio, duracao):
    return {
        "linha": linha,
        "paciente_id": paciente,
        "atividade": atividade,
        "agendado": pd.Timestamp(agendado),
        "checkin": pd.Timestamp(checkin),
        "inicio": pd.Timestamp(inicio),
        "termino": pd.Timestamp(inicio) + pd.Timedelta(minutes=duracao),
        "duracao_min": duracao,
    }


@pytest.fixture
def consultas() -> pd.DataFrame:
    return pd.DataFrame(
        [
            _c(1, "A", "Início do Tratamento", "2026-01-14 10:00", "2026-01-14 09:40", "2026-01-14 10:05", 18),
            _c(2, "A", "Mama", "2026-01-15 18:45", "2026-01-15 18:30", "2026-01-15 18:50", 12),
            _c(3, "A", "Mama", "2026-01-16 19:00", "2026-01-16 18:40", "2026-01-16 19:10", 13),
            _c(4, "A", "Alta do Tratamento", "2026-01-17 19:15", "2026-01-17 19:00", "2026-01-17 19:20", 14),
            _c(5, "B", "Internado - Ginecologico", "2026-01-12 08:00", "2026-01-12 07:50", "2026-01-12 08:10", 15),
            _c(6, "B", "Ginecológico", "2026-01-13 08:00", "2026-01-13 07:50", "2026-01-13 08:10", 500),
            _c(7, "B", "Executar CQ do Plano", "2026-01-11 07:00", "2026-01-11 06:50", "2026-01-11 07:00", 30),
        ]
    )


@pytest.fixture
def settings():
    return load_settings()
