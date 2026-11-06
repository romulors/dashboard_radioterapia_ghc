"""Indicadores de fluxo e de tendência: fila (WIP), entradas × saídas, fluxo de valor, controle estatístico.

Funções puras: recebem DataFrames do Dataset (já filtrado) e devolvem DataFrames prontos para os gráficos.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from rt_dash.domain.activities import ETAPAS_FLUXO

DIAS_SEMANA = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]


def ciclos_com_sitio(ciclos: pd.DataFrame, cursos: pd.DataFrame) -> pd.DataFrame:
    """Ciclos com o sítio mais frequente do paciente nos cursos de tratamento e a marca de atraso."""
    c = ciclos.copy()
    if cursos.empty:
        sitio = pd.Series(dtype=object)
    else:
        sitio = cursos.dropna(subset=["sitio"]).groupby("paciente_id")["sitio"].agg(lambda s: s.mode().iat[0])
    c["sitio"] = c["paciente_id"].map(sitio).fillna("Sem sítio")
    c["tipo_fluxo"] = c["tipo_fluxo"].astype(object).fillna("Sem tipo")
    c["atrasado"] = c["n_atrasadas"] > 0
    return c


def _fechamento(ciclos: pd.DataFrame) -> pd.Series:
    """Data em que o ciclo sai da fila de planejamento: aprovação ou, sem ela, a última atividade."""
    return ciclos["aprovacao"].fillna(ciclos["fim"])


def wip_diario(ciclos: pd.DataFrame) -> pd.DataFrame:
    """Ciclos abertos em planejamento por dia (TC importada e ainda sem aprovação)."""
    c = ciclos[ciclos["tem_importacao"]].dropna(subset=["importacao"])
    if c.empty:
        return pd.DataFrame(columns=["data", "abertos"])
    entrada = c["importacao"].dt.normalize()
    saida = _fechamento(c).dt.normalize()
    dias = pd.date_range(entrada.min(), saida.max(), freq="D")
    eventos = (
        pd.concat([entrada.value_counts(), -saida.value_counts()]).groupby(level=0).sum().reindex(dias, fill_value=0)
    )
    return pd.DataFrame({"data": dias, "abertos": eventos.cumsum().to_numpy()})


def entradas_saidas_semana(ciclos: pd.DataFrame) -> pd.DataFrame:
    """Ciclos que entraram (TC importada) e saíram (aprovados) por semana; colunas semana, serie, valor."""
    c = ciclos[ciclos["tem_importacao"]]
    semana = lambda s: s.dt.to_period("W-SUN").dt.start_time  # noqa: E731
    ent = c["importacao"].dropna().pipe(semana).value_counts().rename("valor")
    sai = c["aprovacao"].dropna().pipe(semana).value_counts().rename("valor")
    partes = [
        ent.rename_axis("semana").reset_index().assign(serie="Entradas (TC importada)"),
        sai.rename_axis("semana").reset_index().assign(serie="Saídas (plano aprovado)"),
    ]
    return pd.concat(partes, ignore_index=True).sort_values("semana")


def idade_ciclos_abertos(ciclos: pd.DataFrame, referencia: pd.Timestamp | None = None) -> pd.DataFrame:
    """Ciclos sem aprovação na data de referência e há quantos dias estão abertos."""
    c = ciclos[ciclos["tem_importacao"]].dropna(subset=["importacao"])
    if c.empty:
        return c.assign(idade_dias=pd.Series(dtype=float))
    referencia = referencia or c[["importacao", "fim"]].max().max()
    abertos = c[(c["importacao"] <= referencia) & (c["aprovacao"].isna() | (c["aprovacao"] > referencia))]
    return abertos.assign(
        idade_dias=(referencia - abertos["importacao"]).dt.total_seconds() / 86400,
        tipo_fluxo=abertos["tipo_fluxo"].astype(object).fillna("Sem tipo"),
    ).sort_values("idade_dias", ascending=False)


def fluxo_valor_por_etapa(jornada: pd.DataFrame) -> pd.DataFrame:
    """Mediana, entre ciclos, do tempo de espera e de execução somados em cada etapa (horas)."""
    j = jornada.copy()
    # A espera antes de "Importar TC e Fusao" é a espera pela tomografia de simulação: conta na Simulação.
    j["etapa"] = j["etapa"].astype(object).where(j["atividade_generica"] != "Importar TC e Fusao", "Simulação")
    j = j[j["etapa"].isin(ETAPAS_FLUXO)]
    if j.empty:
        return pd.DataFrame(columns=["etapa", "espera_h", "execucao_h", "n_ciclos"])
    por_ciclo = (
        j.assign(espera=j["espera_min"].clip(lower=0), execucao=j["duracao_min"].clip(lower=0))
        .groupby(["etapa", "ciclo_id"], observed=True)[["espera", "execucao"]]
        .sum()
    )
    res = por_ciclo.groupby(level="etapa", observed=True).agg(
        espera_h=("espera", "median"), execucao_h=("execucao", "median"), n_ciclos=("espera", "size")
    )
    res[["espera_h", "execucao_h"]] /= 60
    ordem = [e for e in ETAPAS_FLUXO if e in res.index]
    return res.loc[ordem].reset_index()


def carta_controle(ciclos: pd.DataFrame, coluna: str = "lead_time_dias") -> pd.DataFrame:
    """Carta de valores individuais (I-MR): limites = média ± 2,66 × amplitude móvel média."""
    c = ciclos.dropna(subset=["importacao", coluna]).sort_values("importacao")
    if c.empty:
        return pd.DataFrame(columns=["ciclo_id", "importacao", "valor", "media", "lsc", "lic", "fora"])
    valor = c[coluna].astype(float)
    media = valor.mean()
    amplitude = valor.diff().abs().mean() if len(valor) > 1 else 0.0
    lsc, lic = media + 2.66 * amplitude, max(media - 2.66 * amplitude, 0.0)
    return pd.DataFrame(
        {
            "ciclo_id": c["ciclo_id"].to_numpy(),
            "importacao": c["importacao"].to_numpy(),
            "tipo_fluxo": c["tipo_fluxo"].astype(object).fillna("Sem tipo").to_numpy(),
            "valor": valor.to_numpy(),
            "media": media,
            "lsc": lsc,
            "lic": lic,
            "fora": ((valor > lsc) | (valor < lic)).to_numpy(),
        }
    )


def pareto_espera(jornada: pd.DataFrame, top: int = 15) -> pd.DataFrame:
    """Atividades ordenadas pela espera total (h) e o percentual acumulado."""
    j = jornada.dropna(subset=["espera_min"])
    if j.empty:
        return pd.DataFrame(columns=["atividade", "horas", "pct_acumulado"])
    total = (j["espera_min"].clip(lower=0) / 60).groupby(j["atividade_generica"], observed=True).sum()
    total = total.sort_values(ascending=False).rename(
        index={"Importar TC e Fusao": "Importar TC e Fusao (inclui espera pela TC)"}
    )
    acumulado = total.cumsum() / total.sum() if total.sum() else total * 0
    return (
        pd.DataFrame({"atividade": total.index, "horas": total.to_numpy(), "pct_acumulado": acumulado.to_numpy()})
        .head(top)
        .reset_index(drop=True)
    )


def atraso_por_sitio(ciclos_sitio: pd.DataFrame, minimo: int = 5) -> pd.DataFrame:
    """% de ciclos com alguma tarefa atrasada por sítio (sítios com pelo menos `minimo` ciclos)."""
    g = ciclos_sitio.groupby("sitio").agg(n=("ciclo_id", "size"), pct=("atrasado", "mean"))
    return g[g["n"] >= minimo].sort_values("pct").reset_index()


def sessoes_por_dia(sessoes: pd.DataFrame) -> pd.DataFrame:
    """Sessões de tratamento por dia, com semana e dia da semana para o calendário."""
    s = sessoes[sessoes["eh_tratamento"]].dropna(subset=["data"])
    if s.empty:
        return pd.DataFrame(columns=["data", "sessoes", "semana", "dia_semana"])
    d = s.groupby("data").size().rename("sessoes").reset_index()
    d["semana"] = d["data"].dt.to_period("W-SUN").dt.start_time
    d["dia_semana"] = d["data"].dt.dayofweek.map(lambda i: DIAS_SEMANA[i])
    return d


def indice_base_100(serie: pd.DataFrame) -> pd.DataFrame:
    """Converte uma série mensal (mes, serie, valor) em índice com o primeiro mês de cada série = 100."""
    if serie.empty:
        return serie
    d = serie.sort_values("mes").copy()
    base = d.groupby("serie")["valor"].transform("first")
    d["indice"] = np.where(base > 0, d["valor"] / base * 100, np.nan)
    return d


def espera_por_turno_e_sitio(sessoes: pd.DataFrame, top: int = 10, minimo: int = 20) -> pd.DataFrame:
    """Espera mediana (check-in → início) de dia e de noite nos sítios com mais sessões nos dois turnos."""
    s = sessoes[sessoes["eh_tratamento"] & sessoes["espera_checkin_min"].between(-60, 240)].dropna(subset=["sitio"])
    if s.empty:
        return pd.DataFrame(columns=["sitio", "Dia", "Noite", "n"])
    contagem = s.groupby(["sitio", "turno"]).size().unstack(fill_value=0)
    validos = contagem[(contagem.get("Dia", 0) >= minimo) & (contagem.get("Noite", 0) >= minimo)]
    principais = validos.sum(axis=1).nlargest(top).index
    med = s[s["sitio"].isin(principais)].groupby(["sitio", "turno"])["espera_checkin_min"].median().unstack()
    med["n"] = validos.loc[med.index].sum(axis=1)
    return med.reindex(columns=["Dia", "Noite", "n"]).sort_values("Dia").reset_index()


def composicao_fluxo(ciclos: pd.DataFrame) -> pd.DataFrame:
    """Ciclos com TC importada por tipo de fluxo e o percentual de cada um."""
    c = ciclos[ciclos["tem_importacao"]]
    n = c["tipo_fluxo"].astype(object).fillna("Sem tipo").value_counts()
    return pd.DataFrame({"tipo_fluxo": n.index, "n": n.to_numpy(), "pct": (n / n.sum()).to_numpy()})


# Tolerância (desvio aceito antes de "fora da meta"): dentro dela a situação é "atenção".
TOLERANCIA_LIMITE = 0.10  # metas de limite único: 10% abaixo (quanto maior, melhor) ou acima (quanto menor, melhor)
TOLERANCIA_FAIXA = 0.05  # metas em faixa: 5% abaixo do mínimo ou acima do máximo


def status_meta(valor: float | None, meta: tuple[float, float] | float | None, polaridade: str) -> tuple[str, str]:
    """Status de um valor frente à meta: (código, texto). Código: ok | atencao | fora | sem_meta.

    `meta` pode ser uma faixa (mín, máx) ou um limite único. Polaridade "maior" = quanto maior melhor,
    "menor" = quanto menor melhor, "faixa" = deve ficar dentro da faixa.
    """
    if valor is None or valor != valor:
        return "sem_meta", "Sem dado"
    if meta is None:
        return "sem_meta", "Sem meta definida"
    lo, hi = meta if isinstance(meta, tuple | list) else (meta, meta)
    if polaridade == "menor":
        if valor <= hi:
            return "ok", "Dentro da meta"
        perto = valor <= hi * (1 + TOLERANCIA_LIMITE)
        return ("atencao", "Pouco acima da meta") if perto else ("fora", "Acima da meta")
    if polaridade == "maior":
        if valor >= lo:
            return "ok", "Dentro da meta"
        perto = valor >= lo * (1 - TOLERANCIA_LIMITE)
        return ("atencao", "Pouco abaixo da meta") if perto else ("fora", "Abaixo da meta")
    if lo <= valor <= hi:
        return "ok", "Dentro da meta"
    perto = lo * (1 - TOLERANCIA_FAIXA) <= valor <= hi * (1 + TOLERANCIA_FAIXA)
    texto = "abaixo" if valor < lo else "acima"
    return ("atencao", f"Pouco {texto} da meta") if perto else ("fora", f"{texto.capitalize()} da meta")


def mediana_mensal(ciclos: pd.DataFrame, coluna: str = "lead_time_dias") -> pd.DataFrame:
    """Mediana mensal de uma coluna dos ciclos com TC importada (mes, valor)."""
    c = ciclos[ciclos["tem_importacao"]].dropna(subset=[coluna, "mes"])
    return c.groupby("mes")[coluna].median().rename("valor").reset_index()


def dentro_da_meta_mensal(series: dict[str, tuple[pd.DataFrame, tuple | float, str]]) -> pd.DataFrame:
    """Para cada indicador com meta, se cada mês ficou dentro dela (para o gráfico Win/Loss)."""
    linhas = []
    for nome, (serie, meta, polaridade) in series.items():
        if meta is None or serie.empty:
            continue
        total = serie.groupby("mes")["valor"].sum().sort_index()
        for mes, valor in total.items():
            linhas.append({"indicador": nome, "mes": mes, "dentro": status_meta(valor, meta, polaridade)[0] == "ok"})
    return pd.DataFrame(linhas, columns=["indicador", "mes", "dentro"])
