"""Agendamentos no acelerador linear: tipo de agendamento, sítio, turno e espera."""

from __future__ import annotations

import unicodedata
from datetime import time

import pandas as pd

PREFIXO_INTERNADO = "Internado - "
TIPOS_TRATAMENTO = ("Sessão", "Início", "Alta")
# Agendamentos de tratamento que não informam o sítio.
SEM_SITIO = frozenset({"Encaixe"})
# Durações acima disso são tratadas como erro de registro (ex.: feixe não encerrado no sistema).
DURACAO_MAXIMA_SESSAO_MIN = 60


def classificar_agendamento(atividade: str) -> str:
    if atividade == "Início do Tratamento":
        return "Início"
    if atividade == "Alta do Tratamento":
        return "Alta"
    if "CQ" in atividade:
        return "Controle de Qualidade"
    if atividade.startswith("Reserva de Horário") or atividade in (
        "Irradiação Hemocomponentes",
        "Simulação Especial",
    ):
        return "Outro"
    return "Sessão"


def _sem_acento(texto: str) -> str:
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower().strip()


def unificar_grafias(nomes: pd.Series) -> pd.Series:
    """'Ginecologico' e 'Ginecológico' viram a grafia mais frequente (de preferência acentuada)."""
    validos = nomes.dropna()
    if validos.empty:
        return nomes
    contagem = (
        pd.DataFrame({"chave": validos.map(_sem_acento), "nome": validos}).value_counts().rename("n").reset_index()
    )
    contagem["acentuado"] = contagem["nome"].str.lower().str.strip() != contagem["chave"]
    contagem = contagem.sort_values(["acentuado", "n"], ascending=False)
    canonico = contagem.drop_duplicates("chave").set_index("chave")["nome"]
    return nomes.map(lambda n: canonico.get(_sem_acento(n), n) if isinstance(n, str) else n)


def preparar_sessoes(consultas: pd.DataFrame, inicio_noite: time) -> pd.DataFrame:
    s = consultas.copy()
    atividade = s["atividade"].astype("string")
    s["internado"] = atividade.str.startswith(PREFIXO_INTERNADO).fillna(False).astype(bool)
    s["atividade_limpa"] = atividade.str.removeprefix(PREFIXO_INTERNADO)
    s["tipo_agendamento"] = s["atividade_limpa"].map(classificar_agendamento)
    s["atividade_limpa"] = unificar_grafias(s["atividade_limpa"])
    s["sitio"] = s["atividade_limpa"].where((s["tipo_agendamento"] == "Sessão") & ~s["atividade_limpa"].isin(SEM_SITIO))
    s["eh_tratamento"] = s["tipo_agendamento"].isin(TIPOS_TRATAMENTO)
    referencia = s["agendado"].fillna(s["inicio"])
    minutos = referencia.dt.hour * 60 + referencia.dt.minute
    corte = inicio_noite.hour * 60 + inicio_noite.minute
    s["turno"] = (minutos >= corte).map({True: "Noite", False: "Dia"})
    s["duracao_valida"] = s["duracao_min"].between(0, DURACAO_MAXIMA_SESSAO_MIN)
    s["espera_checkin_min"] = (s["inicio"] - s["checkin"]) / pd.Timedelta(minutes=1)
    s["data"] = referencia.dt.normalize()
    s["mes"] = referencia.dt.to_period("M").dt.to_timestamp()
    s["hora"] = referencia.dt.hour
    return s.sort_values(["paciente_id", "agendado"]).reset_index(drop=True)


def cursos_de_tratamento(sessoes: pd.DataFrame) -> pd.DataFrame:
    """Um curso por 'Início do Tratamento'; sessões anteriores ficam no curso 0 (iniciado antes)."""
    t = sessoes[sessoes["eh_tratamento"]].sort_values(["paciente_id", "agendado"]).copy()
    t["curso"] = (t["tipo_agendamento"] == "Início").groupby(t["paciente_id"]).cumsum()
    cursos = t.groupby(["paciente_id", "curso"]).agg(
        inicio_tratamento=("agendado", "min"),
        ultima_sessao=("agendado", "max"),
        n_sessoes=("agendado", "size"),
        teve_alta=("tipo_agendamento", lambda s: bool((s == "Alta").any())),
        sitio=("sitio", lambda s: s.mode().iat[0] if s.notna().any() else pd.NA),
        internado=("internado", "any"),
    )
    cursos = cursos.reset_index()
    cursos["dias_tratamento"] = (cursos["ultima_sessao"] - cursos["inicio_tratamento"]) / pd.Timedelta(days=1)
    return cursos


def ligar_ciclos_ao_tratamento(ciclos: pd.DataFrame, sessoes: pd.DataFrame) -> pd.DataFrame:
    """Acrescenta a cada ciclo o primeiro 'Início do Tratamento' após o início do ciclo."""
    inicios = (
        sessoes.loc[sessoes["tipo_agendamento"] == "Início", ["paciente_id", "agendado"]]
        .dropna()
        .rename(columns={"agendado": "inicio_tratamento"})
        .sort_values("inicio_tratamento")
    )
    base = ciclos.sort_values("inicio")
    ligado = pd.merge_asof(
        base,
        inicios,
        left_on="inicio",
        right_on="inicio_tratamento",
        by="paciente_id",
        direction="forward",
        tolerance=pd.Timedelta(days=120),
    )
    dias = pd.Timedelta(days=1)
    ligado["ate_tratamento_dias"] = (ligado["inicio_tratamento"] - ligado["inicio"]) / dias
    ligado["aprovacao_ate_tratamento_dias"] = (ligado["inicio_tratamento"] - ligado["aprovacao"]) / dias
    return ligado.sort_values(["paciente_id", "ciclo"]).reset_index(drop=True)
