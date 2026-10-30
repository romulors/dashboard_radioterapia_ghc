import pytest

from rt_dash.domain.activities import atividade_generica, etapa_da_categoria, tipo_fluxo_da_atividade


@pytest.mark.parametrize(
    ("nome", "generica", "tipo"),
    [
        ("Contorno do PTV Eletivo", "Contorno do PTV", "Eletivo"),
        ("Preparar a ficha - Urgência", "Preparar a ficha", "Urgência"),
        ("Pacientes em Fluxo - Prioridade - 05 Dias Úteis", "Pacientes em Fluxo", "Prioridade"),
        ("Contorno de OAR Retomografado", "Contorno de OAR", "Retomografado"),
        ("Planejamento Nova TC", "Planejamento", "Retomografado"),
        ("Raio X - 1. Braquiterapia", "Raio X", "Braquiterapia"),
        ("Importar TC e Fusao", "Importar TC e Fusao", None),
        ("Aprovação Replanejamento", "Aprovação Replanejamento", None),
    ],
)
def test_nome_generico_e_tipo(nome, generica, tipo):
    assert atividade_generica(nome) == generica
    assert tipo_fluxo_da_atividade(nome) == tipo


def test_etapa_da_categoria():
    assert etapa_da_categoria("4 - Planejamento") == "Planejamento"
    assert etapa_da_categoria("V  - Atividades especiais de revisão") == "Revisão"
    assert etapa_da_categoria(None) is None
