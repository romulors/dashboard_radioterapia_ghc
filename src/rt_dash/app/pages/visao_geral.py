"""Visão Geral (manchetes de negócio) e séries mensais do registro + modo apresentação (estes na aba KPIs)."""

from __future__ import annotations

from dash import Dash, Input, Output, State

from rt_dash.app.components import fmt_num, fmt_pct, status_badge
from rt_dash.app.context import AppContext
from rt_dash.metrics import REGISTRO
from rt_dash.metrics.fluxo import status_meta
from rt_dash.metrics.monthly import ocupacao_acelerador, pacientes_por_sitio
from rt_dash.viz import figures as fig

# Indicadores do formato resumido de agosto/2026 (modo apresentação)
APRESENTACAO = ["inicios", "planejamentos_fluxo_pct", "planejamentos_fluxo", "sessoes_turno"]

KPIS = [
    ("vg-k-pacientes", "Pacientes em planejamento"),
    ("vg-k-ciclos", "Ciclos de planejamento"),
    ("vg-k-leadtime", "Mediana do ciclo (dias)"),
    ("vg-k-prazo", "Tarefas no prazo"),
    ("vg-k-ate-trat", "Importar TC → início (dias)"),
    ("vg-k-sessoes", "Sessões no AL"),
]


def _metas(ctx: AppContext) -> dict[str, tuple[float, float]]:
    return {"ocupacao_acelerador": ctx.settings.meta_ocupacao_acelerador}


def registrar(app: Dash, ctx: AppContext) -> None:
    ids = list(REGISTRO)

    @app.callback(
        [Output(f"{i}-valor", "children") for i, _ in KPIS]
        + [Output(f"{i}-nota", "children") for i, _ in KPIS]
        + [Output(f"g-vg-{i}", "figure") for i in ids],
        Input("store-filtros", "data"),
        Input("store-selecao", "data"),
    )
    def atualizar(estado, selecao):
        ds = ctx.dados(estado)
        mes = (selecao or {}).get("mes")
        c = ds.ciclos[ds.ciclos["tem_importacao"]]
        sess = ds.sessoes[ds.sessoes["eh_tratamento"]]
        valores = [
            fmt_num(c["paciente_id"].nunique()),
            fmt_num(len(c)),
            fmt_num(c["lead_time_dias"].median(), 1),
            fmt_pct(ds.jornada["no_prazo"].dropna().mean()),
            fmt_num(c["ate_tratamento_dias"].median(), 1),
            fmt_num(len(sess)),
        ]
        notas = [
            f"{fmt_num((c.groupby('paciente_id').size() > 1).sum())} com mais de um ciclo",
            "com importação de TC/radiografia",
            "importação → última atividade",
            "término ≤ vencimento",
            "mediana por ciclo",
            f"{fmt_pct((sess['turno'] == 'Noite').mean())} à noite",
        ]
        metas = _metas(ctx)
        figuras = [
            fig.serie_mensal(
                REGISTRO[i].calcular(ds, ctx.settings),
                formato=REGISTRO[i].formato,
                tipo=REGISTRO[i].grafico,
                meta=metas.get(i),
                mes_selecionado=mes,
                altura=280,
            )
            for i in ids
        ]
        return (*valores, *notas, *figuras)

    manchetes = ["vg-h-inicios", "vg-h-ciclo", "vg-h-prazo", "vg-h-ocupacao"]

    @app.callback(
        [Output(f"{i}-{campo}", "children") for i in manchetes for campo in ("valor", "status", "nota")],
        Input("store-filtros", "data"),
    )
    def manchete(estado):
        ds = ctx.dados(estado)
        st = ctx.settings
        c = ds.ciclos[ds.ciclos["tem_importacao"]]
        inicios = ds.sessoes[ds.sessoes["tipo_agendamento"] == "Início"]["paciente_id"].nunique()
        ciclo = c["lead_time_dias"].median()
        prazo = ds.jornada["no_prazo"].dropna().mean()
        ocup = ocupacao_acelerador(ds, st)["valor"].mean()
        s_ciclo = status_meta(ciclo, st.meta_lead_time_dias, "menor")
        s_prazo = status_meta(prazo, st.meta_pct_no_prazo, "maior")
        s_ocup = status_meta(ocup, st.meta_ocupacao_acelerador, "faixa")
        meta_txt = f"meta {st.meta_ocupacao_acelerador[0]:.0%}–{st.meta_ocupacao_acelerador[1]:.0%}"
        saida = [
            fmt_num(inicios),
            status_badge("sem_meta", "Volume, sem meta"),
            "pacientes distintos no período",
            fmt_num(ciclo, 1, " dias"),
            status_badge(*s_ciclo),
            f"{fmt_num(len(c))} ciclos com TC importada",
            fmt_pct(prazo),
            status_badge(*s_prazo),
            "término até o vencimento",
            fmt_pct(ocup),
            status_badge(*s_ocup),
            f"média mensal · {meta_txt}",
        ]
        return saida

    @app.callback(
        [Output("vg-modal", "is_open")]
        + [Output(f"g-ap-{i}", "figure") for i in APRESENTACAO]
        + [Output("g-ap-sitios", "figure")],
        Input("vg-apresentar", "n_clicks"),
        State("store-filtros", "data"),
        prevent_initial_call=True,
    )
    def apresentar(_, estado):
        ds = ctx.dados(estado)
        figuras = [
            fig.serie_mensal(
                REGISTRO[i].calcular(ds, ctx.settings),
                formato=REGISTRO[i].formato,
                tipo=REGISTRO[i].grafico,
                altura=460,
            )
            for i in APRESENTACAO
        ]
        return True, *figuras, fig.barras_sitio(pacientes_por_sitio(ds), top=20, altura=520)
