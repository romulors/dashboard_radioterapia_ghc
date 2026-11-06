"""Visão Geral (resumo do serviço em 4 gráficos), séries mensais do registro e modo apresentação."""

from __future__ import annotations

from dash import Dash, Input, Output, State

from rt_dash.app.components import fmt_num, fmt_pct
from rt_dash.app.context import AppContext
from rt_dash.metrics import REGISTRO
from rt_dash.metrics.monthly import (
    pacientes_por_sitio,
    pacientes_que_iniciaram,
    percentual_por_fluxo,
    sessoes_por_turno,
)
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
    return {
        "ocupacao_acelerador": ctx.settings.meta_ocupacao_acelerador,
        "ocupacao_tomografo": ctx.settings.meta_ocupacao_tomografo,
    }


def _linhas_meta(ctx: AppContext) -> dict[str, tuple[float, str]]:
    """Metas de limite único desenhadas como linha: id do indicador → (valor, rótulo)."""
    st = ctx.settings
    linhas: dict[str, tuple[float, str]] = {}
    if st.meta_pacientes_novos:
        for i in ("inicios", "pacientes_iniciaram"):
            linhas[i] = (st.meta_pacientes_novos, f"Meta: acima de {st.meta_pacientes_novos:g}")
    if st.meta_pct_no_prazo:
        linhas["no_prazo"] = (st.meta_pct_no_prazo[0], f"Meta: acima de {st.meta_pct_no_prazo[0]:.0%}")
    if st.meta_sessoes_mes:
        linhas["sessoes_turno"] = (st.meta_sessoes_mes, f"Meta: total acima de {st.meta_sessoes_mes:g}")
    if st.meta_duracao_sessao_min:
        linhas["duracao_sessao"] = (st.meta_duracao_sessao_min, f"Meta: abaixo de {st.meta_duracao_sessao_min:g} min")
    if st.meta_lead_time_dias:
        linhas["lead_time"] = (st.meta_lead_time_dias, f"Meta: abaixo de {st.meta_lead_time_dias:g} dias")
    return linhas


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
        linhas = _linhas_meta(ctx)
        figuras = [
            fig.serie_mensal(
                REGISTRO[i].calcular(ds, ctx.settings),
                formato=REGISTRO[i].formato,
                tipo=REGISTRO[i].grafico,
                meta=metas.get(i),
                meta_minima=linhas.get(i, (None, None))[0],
                meta_rotulo=linhas.get(i, (None, None))[1],
                mes_selecionado=mes,
                altura=280,
            )
            for i in ids
        ]
        return (*valores, *notas, *figuras)

    @app.callback(
        Output("g-vg-res-novos", "figure"),
        Output("g-vg-res-fluxo", "figure"),
        Output("g-vg-res-turno", "figure"),
        Output("g-vg-res-sitio", "figure"),
        Input("store-filtros", "data"),
        Input("store-selecao", "data"),
    )
    def resumo_servico(estado, selecao):
        """Resumo para a diretoria: os quatro gráficos que substituíram os números de manchete."""
        ds = ctx.dados(estado)
        st = ctx.settings
        mes = (selecao or {}).get("mes")
        return (
            fig.serie_mensal(
                pacientes_que_iniciaram(ds, st), meta_minima=st.meta_pacientes_novos, mes_selecionado=mes, altura=320
            ),
            fig.serie_mensal(
                percentual_por_fluxo(ds, st),
                formato=".0%",
                tipo="barras_100",
                media_meses=None,
                mes_selecionado=mes,
                altura=320,
            ),
            fig.serie_mensal(sessoes_por_turno(ds, st), tipo="barras_empilhadas", mes_selecionado=mes, altura=320),
            fig.barras_sitio(pacientes_por_sitio(ds), top=15, altura=320),
        )

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
                meta_minima=ctx.settings.meta_pacientes_novos if i == "inicios" else None,
                altura=460,
            )
            for i in APRESENTACAO
        ]
        return True, *figuras, fig.barras_sitio(pacientes_por_sitio(ds), top=20, altura=520)
