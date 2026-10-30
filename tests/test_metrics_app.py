import pandas as pd

from rt_dash.data import Filtros, construir_dataset
from rt_dash.metrics import REGISTRO
from rt_dash.metrics.activity import estatisticas_por_atividade
from rt_dash.metrics.patient import tabela_pacientes


def test_todos_os_indicadores_registrados_calculam(tarefas, consultas, settings):
    ds = construir_dataset(tarefas, consultas, settings)
    assert {"inicios", "sessoes_turno", "planejamentos_fluxo", "ocupacao_acelerador"} <= set(REGISTRO)
    for ind in REGISTRO.values():
        df = ind.calcular(ds, settings)
        assert {"mes", "valor"} <= set(df.columns), ind.id


def test_sessoes_por_turno_e_ocupacao(tarefas, consultas, settings):
    ds = construir_dataset(tarefas, consultas, settings)
    turno = REGISTRO["sessoes_turno"].calcular(ds, settings).set_index("serie")["valor"]
    assert turno.to_dict() == {"Dia": 4, "Noite": 2}
    ocup = REGISTRO["ocupacao_acelerador"].calcular(ds, settings)["valor"].iat[0]
    assert ocup == 6 / (6 * 60)  # 6 sessões em 6 dias com atendimento, 60 vagas/dia


def test_filtros(tarefas, consultas, settings):
    ds = construir_dataset(tarefas, consultas, settings)
    so_urgencia = Filtros(tipos_fluxo=("Urgência",)).aplicar(ds)
    assert set(so_urgencia.ciclos["ciclo_id"]) == {"B-1"}
    assert set(so_urgencia.jornada["paciente_id"]) == {"B"}
    fevereiro = Filtros(mes_inicio=pd.Timestamp("2026-02-01"), mes_fim=pd.Timestamp("2026-02-01")).aplicar(ds)
    assert set(fevereiro.ciclos["ciclo_id"]) == {"A-2"}


def test_estatisticas_e_tabela_de_pacientes(tarefas, consultas, settings):
    ds = construir_dataset(tarefas, consultas, settings)
    est = estatisticas_por_atividade(ds.jornada).set_index("atividade_generica")
    assert est.loc["Importar TC e Fusao", "n"] == 3
    tab = tabela_pacientes(ds.ciclos, ds.cursos).set_index("paciente_id")
    assert tab.loc["A", "n_ciclos"] == 2
    assert tab.loc["A", "tipos_fluxo"] == "Eletivo → Retomografado"


def test_app_monta(tarefas, consultas, settings):
    from rt_dash.app.main import criar_app

    app = criar_app(settings, construir_dataset(tarefas, consultas, settings))
    assert len(app.callback_map) > 10
