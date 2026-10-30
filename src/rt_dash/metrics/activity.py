"""Estatísticas por atividade do fluxo (perguntas de negócio P3 a P8)."""

from __future__ import annotations

import pandas as pd

METRICAS_TEMPO = {
    "tempo_etapa_min": "Tempo da etapa (espera + execução)",
    "espera_min": "Espera desde a atividade anterior",
    "duracao_min": "Execução (início → término)",
    "atraso_min": "Atraso em relação ao vencimento",
}


def estatisticas_por_atividade(jornada: pd.DataFrame, metrica: str = "tempo_etapa_min") -> pd.DataFrame:
    """Mediana, P25, P75, P90, IQR, coeficiente de variação e % no prazo por atividade."""
    if jornada.empty:
        return pd.DataFrame(
            columns=[
                "atividade_generica",
                "etapa",
                "n",
                "mediana",
                "p25",
                "p75",
                "p90",
                "media",
                "iqr",
                "cv",
                "pct_no_prazo",
                "atraso_mediano_min",
            ]
        )
    g = jornada.groupby("atividade_generica")
    x = g[metrica]
    est = pd.DataFrame(
        {
            "etapa": g["etapa"].agg(lambda s: s.mode().iat[0]),
            "ordem": g["ordem"].median(),
            "n": x.size(),
            "mediana": x.median(),
            "p25": x.quantile(0.25),
            "p75": x.quantile(0.75),
            "p90": x.quantile(0.90),
            "media": x.mean(),
            "desvio": x.std(),
            "pct_no_prazo": g["no_prazo"].mean(),
            "atraso_mediano_min": jornada[jornada["atraso_min"] > 0]
            .groupby("atividade_generica")["atraso_min"]
            .median(),
        }
    )
    est["iqr"] = est["p75"] - est["p25"]
    est["cv"] = est["desvio"] / est["media"].where(est["media"].abs() > 1e-9)
    return est.reset_index().sort_values("ordem")


def evolucao_mensal(jornada: pd.DataFrame, metrica: str = "tempo_etapa_min") -> pd.DataFrame:
    """Mediana da métrica por atividade e mês (heatmap P6)."""
    return jornada.pivot_table(index="atividade_generica", columns="mes", values=metrica, aggfunc="median")


def limiar_p90(jornada: pd.DataFrame, metrica: str = "espera_min") -> pd.Series:
    """P90 da métrica por (atividade genérica, tipo de fluxo); usado para marcar gargalos."""
    return jornada.groupby(["atividade_generica", "tipo_fluxo"])[metrica].quantile(0.9)
