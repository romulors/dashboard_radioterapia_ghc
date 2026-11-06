"""Alternativas montadas no servidor: todo gráfico sem conversão automática precisa de pelo menos duas."""

import pandas as pd
import plotly.graph_objects as go

from rt_dash.viz import novos as nv
from rt_dash.viz.alternativas import com_alternativas, nomes


def test_com_alternativas_guarda_nomes_e_ignora_vazias():
    fig = com_alternativas(
        go.Figure(go.Bar(x=[1], y=["a"])), "Barras", [("Pontos", go.Figure(go.Scatter(x=[1]))), ("Nada", go.Figure())]
    )
    assert nomes(fig) == ["Barras", "Pontos"]
    assert fig.layout.meta["rt_auto"] is False
    assert "template" not in fig.layout.meta["rt_alternativas"][0]["layout"]


def test_bullet_padrao_interativo_com_duas_alternativas():
    fig = nv.bullet(0.82, (0.80, 0.85), "Ocupação", 1.0)
    assert fig.data[0].type == "bar" and fig.data[0].hovertemplate
    assert nomes(fig) == ["Bullet (barra com dica)", "Bullet (indicador)", "Velocímetro"]


def test_win_loss_tem_grade_e_alternativas():
    meses = pd.to_datetime(["2026-01-01", "2026-02-01"])
    d = pd.DataFrame({"indicador": ["A", "A", "B", "B"], "mes": list(meses) * 2, "dentro": [True, False, True, True]})
    fig = nv.win_loss(d)
    assert fig.data[0].type == "heatmap"
    assert len(nomes(fig)) >= 3


def test_waffle_padrao_barra_com_waffle_e_rosca():
    comp = pd.DataFrame({"tipo_fluxo": ["Eletivo", "Urgência"], "pct": [0.7, 0.3], "n": [70, 30]})
    fig = nv.waffle(comp)
    assert fig.data[0].type == "bar"
    assert nomes(fig) == ["Barra 100%", "Waffle", "Rosca"]
