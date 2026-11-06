"""Gráficos novos da proposta de melhoria: tendência (fila), processos (fluxo de valor, controle), scorecard.

Os callbacks só chamam funções puras de `metrics.fluxo` e de `viz.novos`.
"""

from __future__ import annotations

import traceback

import pandas as pd
from dash import Dash, Input, Output, dcc, html

from rt_dash.app.components import fmt_num, fmt_pct, status_badge
from rt_dash.app.context import AppContext
from rt_dash.metrics import fluxo as fx
from rt_dash.metrics.monthly import ocupacao_acelerador, pacientes_que_iniciaram, pct_no_prazo, sessoes_por_turno
from rt_dash.viz import novos as nv
from rt_dash.viz.figures import vazio

GRAFICOS = [
    "g-nv-wip",
    "g-nv-entradas",
    "g-nv-idade",
    "g-nv-fluxo-valor",
    "g-nv-controle",
    "g-nv-pareto",
    "g-nv-lollipop",
    "g-nv-dotstrip",
    "g-nv-calendario",
    "g-nv-indice",
    "g-nv-waffle",
    "g-nv-barbell",
    "g-nv-ridgeline",
]


def _seguro(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except Exception as exc:  # um gráfico com erro não derruba a aba inteira
        traceback.print_exc()
        return vazio(f"Erro ao montar o gráfico: {exc}")


def _valor_no_mes(serie: pd.DataFrame, mes: pd.Timestamp) -> float | None:
    total = serie.groupby("mes")["valor"].sum()
    return float(total[mes]) if mes in total.index else None


def _texto_meta(meta, polaridade: str, pct: bool) -> str:
    if meta is None:
        return "Sem meta definida"
    fmt = (lambda v: fmt_pct(v)) if pct else (lambda v: fmt_num(v, 1))
    lo, hi = meta if isinstance(meta, tuple | list) else (meta, meta)
    if polaridade == "maior":
        return f"≥ {fmt(lo)}"
    if polaridade == "menor":
        return f"≤ {fmt(hi)}"
    return f"{fmt(lo)} a {fmt(hi)}"


def registrar(app: Dash, ctx: AppContext) -> None:
    @app.callback([Output(g, "figure") for g in GRAFICOS], Input("store-filtros", "data"))
    def atualizar(estado):
        ds = ctx.dados(estado)
        c = ds.ciclos[ds.ciclos["tem_importacao"]]
        cs = fx.ciclos_com_sitio(ds.ciclos, ds.cursos)
        p90 = ctx.ds.ciclos["ate_aprovacao_dias"].quantile(0.9)
        return (
            _seguro(lambda: nv.wip(fx.wip_diario(ds.ciclos))),
            _seguro(lambda: nv.entradas_saidas(fx.entradas_saidas_semana(ds.ciclos))),
            _seguro(lambda: nv.idade_abertos(fx.idade_ciclos_abertos(ds.ciclos), p90)),
            _seguro(lambda: nv.fluxo_valor(fx.fluxo_valor_por_etapa(ds.jornada))),
            _seguro(lambda: nv.controle(fx.carta_controle(c))),
            _seguro(lambda: nv.pareto(fx.pareto_espera(ds.jornada))),
            _seguro(lambda: nv.lollipop(fx.atraso_por_sitio(cs))),
            _seguro(lambda: nv.dot_strip(cs[cs["tem_importacao"]])),
            _seguro(lambda: nv.calendario(fx.sessoes_por_dia(ds.sessoes))),
            _seguro(lambda: nv.indice(fx.indice_base_100(sessoes_por_turno(ds, ctx.settings)))),
            _seguro(lambda: nv.waffle(fx.composicao_fluxo(ds.ciclos))),
            _seguro(lambda: nv.barbell(fx.espera_por_turno_e_sitio(ds.sessoes))),
            _seguro(lambda: nv.ridgeline(c)),
        )

    @app.callback(
        Output("sc-tabela", "children"),
        Output("g-sc-ocupacao", "figure"),
        Output("g-sc-prazo", "figure"),
        Output("g-sc-winloss", "figure"),
        Input("store-filtros", "data"),
        Input("prod-mes", "value"),
    )
    def scorecard(estado, mes_ref):
        ds = ctx.dados(estado)
        st = ctx.settings
        mes = pd.Timestamp(mes_ref)
        ocup = ocupacao_acelerador(ds, st)
        prazo = pct_no_prazo(ds, st)
        lead = fx.mediana_mensal(ds.ciclos)
        inicios = pacientes_que_iniciaram(ds, st)
        linhas_def = [
            ("Ocupação do acelerador linear", ocup, st.meta_ocupacao_acelerador, "faixa", True),
            ("Tarefas de planejamento no prazo", prazo, st.meta_pct_no_prazo, "maior", True),
            ("Mediana da duração do ciclo (dias)", lead, st.meta_lead_time_dias, "menor", False),
            ("Pacientes que iniciaram tratamento", inicios, None, "neutra", False),
        ]
        corpo = []
        for nome, serie, meta, pol, pct in linhas_def:
            valor = _valor_no_mes(serie, mes)
            codigo, texto = fx.status_meta(valor, meta, pol) if pol != "neutra" else ("sem_meta", "Volume, sem meta")
            valor_txt = fmt_pct(valor) if pct else fmt_num(valor, 1 if "dias" in nome else 0)
            spark = dcc.Graph(
                figure=nv.sparkline(serie),
                config={"staticPlot": True, "displayModeBar": False},
                className="sparkline",
                style={"height": "48px", "width": "160px"},
            )
            corpo.append(
                html.Tr(
                    [
                        html.Th(nome, scope="row"),
                        html.Td(valor_txt, className="sc-valor"),
                        html.Td(_texto_meta(meta, pol, pct)),
                        html.Td(status_badge(codigo, texto)),
                        html.Td(html.Div(spark, role="img", **{"aria-label": f"Tendência mensal de {nome}"})),
                    ]
                )
            )
        tabela = html.Table(
            [
                html.Caption("Indicadores do mês de referência frente à meta"),
                html.Thead(
                    html.Tr(
                        [
                            html.Th(c, scope="col")
                            for c in ("Indicador", "Valor no mês", "Meta", "Situação", "Tendência")
                        ]
                    )
                ),
                html.Tbody(corpo),
            ],
            className="tabela-scorecard",
        )
        wl = fx.dentro_da_meta_mensal(
            {
                "Ocupação AL": (ocup, st.meta_ocupacao_acelerador, "faixa"),
                "No prazo": (prazo, st.meta_pct_no_prazo, "maior"),
                "Mediana do ciclo": (lead, st.meta_lead_time_dias, "menor"),
            }
        )
        return (
            tabela,
            _seguro(nv.bullet, _valor_no_mes(ocup, mes), st.meta_ocupacao_acelerador, "Ocupação do AL", 1.0),
            _seguro(
                nv.bullet, _valor_no_mes(prazo, mes), st.meta_pct_no_prazo, "Tarefas no prazo", 1.0, polaridade="maior"
            ),
            _seguro(nv.win_loss, wl),
        )
