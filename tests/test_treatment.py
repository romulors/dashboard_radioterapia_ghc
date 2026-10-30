from datetime import time

import pytest

from rt_dash.config import Acelerador, FaixaEspecial
from rt_dash.domain.cycles import construir_jornada, resumir_ciclos
from rt_dash.domain.treatment import cursos_de_tratamento, ligar_ciclos_ao_tratamento, preparar_sessoes


@pytest.fixture
def sessoes(consultas):
    return preparar_sessoes(consultas, time(19, 0))


def test_turno_dia_ate_1845_noite_a_partir_das_19(sessoes):
    turno = sessoes.set_index("linha")["turno"]
    assert turno[2] == "Dia"  # 18:45
    assert turno[3] == "Noite"  # 19:00


def test_classificacao_internado_e_sitio(sessoes):
    s = sessoes.set_index("linha")
    assert s.loc[5, "internado"]
    assert s.loc[5, "sitio"] == s.loc[6, "sitio"] == "Ginecológico"  # grafias unificadas
    assert s.loc[7, "tipo_agendamento"] == "Controle de Qualidade"
    assert not s.loc[7, "eh_tratamento"]
    assert s.loc[1, "tipo_agendamento"] == "Início"


def test_duracao_invalida_e_espera_checkin(sessoes):
    s = sessoes.set_index("linha")
    assert not s.loc[6, "duracao_valida"]  # 500 min
    assert s.loc[1, "espera_checkin_min"] == pytest.approx(25)


def test_cursos(sessoes):
    a = cursos_de_tratamento(sessoes).query("paciente_id == 'A'").iloc[0]
    assert a["curso"] == 1 and a["n_sessoes"] == 4 and a["teve_alta"]


def test_ligacao_ciclo_inicio_do_tratamento(tarefas, sessoes):
    ciclos = ligar_ciclos_ao_tratamento(resumir_ciclos(construir_jornada(tarefas)), sessoes)
    a1 = ciclos.set_index("ciclo_id").loc["A-1"]
    assert a1["inicio_tratamento"].strftime("%d/%m") == "14/01"
    assert a1["ate_tratamento_dias"] == pytest.approx(7, abs=0.1)


def test_capacidade_do_acelerador():
    acel = Acelerador(
        abertura=time(7, 0),
        fechamento=time(22, 30),
        vaga_minutos=15,
        faixas_especiais=(FaixaEspecial(time(10), time(11), 20), FaixaEspecial(time(15), time(16), 20)),
    )
    assert acel.minutos_por_dia == 930
    assert acel.vagas_por_dia == 54 + 6
