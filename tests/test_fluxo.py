import pandas as pd

from rt_dash.data import construir_dataset
from rt_dash.metrics import fluxo as fx
from rt_dash.metrics.registry import REGISTRO, ficha_tecnica


def test_status_meta_por_polaridade():
    assert fx.status_meta(0.82, (0.80, 0.85), "faixa")[0] == "ok"
    assert fx.status_meta(0.78, (0.80, 0.85), "faixa")[0] == "atencao"
    assert fx.status_meta(0.50, (0.80, 0.85), "faixa")[0] == "fora"
    assert fx.status_meta(9, 10, "menor")[0] == "ok"
    assert fx.status_meta(15, 10, "menor")[0] == "fora"
    assert fx.status_meta(10, 10, "menor")[0] == "ok"
    assert fx.status_meta(9.5, 10, "abaixo")[0] == "ok"
    assert fx.status_meta(10, 10, "abaixo")[0] == "atencao"
    assert fx.status_meta(12, 10, "abaixo")[0] == "fora"
    assert fx.status_meta(0.95, (0.9, 1.0), "maior")[0] == "ok"
    assert fx.status_meta(61, 60, "acima")[0] == "ok"
    assert fx.status_meta(60, 60, "acima")[0] == "atencao"
    assert fx.status_meta(40, 60, "acima")[0] == "fora"
    assert fx.status_meta(0.5, None, "maior") == ("sem_meta", "Sem meta definida")
    assert fx.status_meta(None, (0.8, 0.85), "faixa")[0] == "sem_meta"


def test_carta_controle_limites():
    ciclos = pd.DataFrame(
        {
            "ciclo_id": list("abcde"),
            "importacao": pd.date_range("2026-01-01", periods=5),
            "tipo_fluxo": ["Eletivo"] * 5,
            "lead_time_dias": [5.0, 6.0, 5.0, 6.0, 40.0],
        }
    )
    c = fx.carta_controle(ciclos)
    assert c["media"].iat[0] == 12.4
    assert c["lic"].iat[0] == 0.0
    assert c["fora"].tolist() == [False, False, False, False, True]


def test_wip_e_entradas_saidas(tarefas, consultas, settings):
    ds = construir_dataset(tarefas, consultas, settings)
    wip = fx.wip_diario(ds.ciclos)
    assert wip["abertos"].min() >= 0 and wip["abertos"].max() >= 1
    es = fx.entradas_saidas_semana(ds.ciclos)
    total = es.groupby("serie")["valor"].sum()
    assert total["Entradas (TC importada)"] == ds.ciclos["tem_importacao"].sum()


def test_fluxo_valor_pareto_e_composicao(tarefas, consultas, settings):
    ds = construir_dataset(tarefas, consultas, settings)
    fv = fx.fluxo_valor_por_etapa(ds.jornada)
    assert set(fv["etapa"]) <= {"Recepção", "Simulação", "Planejamento", "Pré-Tratamento", "Controle de Qualidade"}
    assert (fv[["espera_h", "execucao_h"]] >= 0).all().all()
    p = fx.pareto_espera(ds.jornada)
    assert p["pct_acumulado"].is_monotonic_increasing
    comp = fx.composicao_fluxo(ds.ciclos)
    assert abs(comp["pct"].sum() - 1) < 1e-9


def test_indice_base_100():
    df = pd.DataFrame(
        {
            "mes": pd.to_datetime(["2026-01-01", "2026-02-01"] * 2),
            "serie": ["Dia", "Dia", "Noite", "Noite"],
            "valor": [10, 15, 4, 2],
        }
    )
    idx = fx.indice_base_100(df).set_index(["serie", "mes"])["indice"]
    assert idx[("Dia", pd.Timestamp("2026-02-01"))] == 150
    assert idx[("Noite", pd.Timestamp("2026-02-01"))] == 50


def test_ficha_tecnica_completa():
    ficha = ficha_tecnica()
    assert len(ficha) == len(REGISTRO)
    assert ficha["Como se calcula"].str.len().gt(0).all()
    assert all(i.polaridade in {"maior", "menor", "faixa", "neutra"} for i in REGISTRO.values())
