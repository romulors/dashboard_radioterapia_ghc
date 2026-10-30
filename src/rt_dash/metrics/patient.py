"""Visão por paciente e por ciclo (jornada)."""

from __future__ import annotations

import pandas as pd


def tabela_pacientes(ciclos: pd.DataFrame, cursos: pd.DataFrame) -> pd.DataFrame:
    """Uma linha por paciente para a lista da aba Jornada."""
    if ciclos.empty:
        return pd.DataFrame(
            columns=[
                "paciente_id",
                "n_ciclos",
                "tipos_fluxo",
                "ultimo_inicio",
                "lead_time_dias",
                "espera_total_h",
                "pct_no_prazo",
                "ate_tratamento_dias",
                "sitio",
            ]
        )
    g = ciclos.sort_values("ciclo").groupby("paciente_id")
    tab = pd.DataFrame(
        {
            "n_ciclos": g.size(),
            "tipos_fluxo": g["tipo_fluxo"].agg(lambda s: " → ".join(dict.fromkeys(s))),
            "ultimo_inicio": g["inicio"].max(),
            "lead_time_dias": g["lead_time_dias"].last(),
            "espera_total_h": g["espera_total_min"].sum() / 60,
            "pct_no_prazo": g["pct_no_prazo"].mean(),
            "ate_tratamento_dias": g["ate_tratamento_dias"].last(),
        }
    )
    sitio = cursos.dropna(subset=["sitio"]).sort_values("inicio_tratamento").groupby("paciente_id")["sitio"].last()
    tab = tab.join(sitio).reset_index()
    return tab.sort_values("ultimo_inicio", ascending=False).reset_index(drop=True)


def faixa_referencia(jornada_ref: pd.DataFrame, tipo_fluxo: str) -> pd.DataFrame:
    """P25, mediana e P75 do tempo acumulado (dias) por atividade, para o tipo de fluxo."""
    ref = jornada_ref[jornada_ref["tipo_fluxo"] == tipo_fluxo]
    q = ref.groupby("atividade_generica")["acumulado_min"].quantile([0.25, 0.5, 0.75]).unstack()
    q.columns = ["p25", "mediana", "p75"]
    return q / (60 * 24)
