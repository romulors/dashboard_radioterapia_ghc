import pandas as pd
import pytest

from rt_dash.domain.cycles import construir_jornada, resumir_ciclos


@pytest.fixture
def jornada(tarefas):
    return construir_jornada(tarefas)


def test_so_concluidas_do_fluxo(jornada):
    assert "Revisar Imagens do Tratamento" not in set(jornada["atividade"])
    assert len(jornada) == 12  # 14 tarefas - 1 cancelada - 1 revisão


def test_ciclo_novo_a_cada_importacao_concluida(jornada):
    a = jornada[jornada["paciente_id"] == "A"]
    assert a.groupby("ciclo").size().to_dict() == {1: 6, 2: 3}
    # recepção (antes da 1ª importação) pertence ao ciclo 1
    assert a.loc[a["atividade"] == "Selecionar Fluxo Tratamento", "ciclo"].item() == 1


def test_espera_usa_maior_termino_anterior(jornada):
    a1 = jornada[jornada["ciclo_id"] == "A-1"].set_index("atividade")
    # PTV começa 12:00, OAR termina 13:00 -> paralelo: espera negativa de 60 min
    assert a1.loc["Contorno do PTV Eletivo", "espera_min"] == pytest.approx(-60)
    # Aprovação começa 09/01 09:00; maior término anterior = PTV 08/01 09:00 -> 24 h
    assert a1.loc["Aprovação Eletivo", "espera_min"] == pytest.approx(24 * 60)
    assert a1.loc["Aprovação Eletivo", "tempo_etapa_min"] == pytest.approx(24 * 60 + 30)


def test_atraso_e_prazo(jornada):
    ptv = jornada[jornada["atividade"] == "Contorno do PTV Eletivo"].iloc[0]
    assert ptv["atraso_min"] == pytest.approx(60)
    assert not ptv["no_prazo"]


def test_acumulado_conta_da_importacao(jornada):
    a1 = jornada[jornada["ciclo_id"] == "A-1"].set_index("atividade")
    assert a1.loc["Importar TC e Fusao", "acumulado_min"] == pytest.approx(10)


def test_tipo_de_fluxo_do_ciclo(jornada):
    tipos = jornada.groupby("ciclo_id")["tipo_fluxo"].first().to_dict()
    assert tipos == {"A-1": "Eletivo", "A-2": "Retomografado", "B-1": "Urgência"}


def test_resumo_de_ciclos(jornada):
    c = resumir_ciclos(jornada).set_index("ciclo_id")
    assert list(c.index) == ["A-1", "A-2", "B-1"]
    assert c.loc["A-1", "aprovacao"] == pd.Timestamp("2026-01-09 09:30")
    assert c.loc["B-1", "lead_time_dias"] == pytest.approx((4 * 60 + 5) / 1440)
    assert c.loc["A-2", "n_atrasadas"] == 1


def test_recepcao_vai_para_o_proximo_ciclo_e_resto_antigo_sai(tarefas):
    from tests.conftest import _t

    extra = pd.DataFrame(
        [
            # CQ de um ciclo anterior ao período exportado: fica de fora
            _t(20, "B", "Revisar CQ do Plano", "8 - Controle de Qualidade", "2026-01-02 08:00", "2026-01-02 09:00"),
            # nova recepção depois da última importação: abre um ciclo ainda sem planejamento
            _t(21, "B", "Confirmar Cadastro Paciente", "2 - Recepção", "2026-03-01 08:00", "2026-03-01 08:00"),
        ]
    )
    j = construir_jornada(pd.concat([tarefas, extra], ignore_index=True))
    b = j[j["paciente_id"] == "B"]
    assert "Revisar CQ do Plano" not in set(b["atividade"])
    assert b.loc[b["atividade"] == "Confirmar Cadastro Paciente", "ciclo"].item() == 2
