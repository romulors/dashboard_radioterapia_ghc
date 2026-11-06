"""Visualizações alternativas montadas no servidor para o botão ⇄ de cada gráfico.

A maioria dos gráficos ganha alternativas automáticas no navegador (`assets/a11y.js`, `classificar`), que
convertem as séries desenhadas em outro tipo (linhas ↔ barras, caixa ↔ violino etc.). Quando a conversão
automática não serve (indicadores, Gantt, cascata, funil, waffle), a figura leva as alternativas prontas em
`layout.meta`, e o navegador as acrescenta à lista do ⇄.

Regra do catálogo de gráficos (docs/catalogo-graficos.md): a visualização 1, mostrada por padrão, é a de
maior interatividade (dica, zoom, clique, legenda); as demais são opções para leitura ou apresentação.
"""

from __future__ import annotations

import plotly.graph_objects as go


def _serializar(fig: go.Figure) -> dict:
    layout = fig.layout.to_plotly_json()
    layout.pop("template", None)  # o navegador reaproveita o template da figura original
    layout.pop("meta", None)
    return {"data": [tr.to_plotly_json() for tr in fig.data], "layout": layout}


def com_alternativas(
    fig: go.Figure,
    nome: str,
    alternativas: list[tuple[str, go.Figure | None]],
    automaticas: bool = False,
) -> go.Figure:
    """Anexa alternativas prontas à figura.

    `nome` é o nome da visualização 1 (a própria figura). `automaticas=False` desliga as conversões automáticas
    do navegador, para que o ⇄ mostre só as opções definidas aqui.
    """
    extras = [{"nome": n, **_serializar(f)} for n, f in alternativas if f is not None and len(f.data)]
    meta = dict(fig.layout.meta) if isinstance(fig.layout.meta, dict) else {}
    meta.update(rt_nome=nome, rt_alternativas=extras, rt_auto=automaticas)
    fig.update_layout(meta=meta)
    return fig


def nomes(fig: go.Figure) -> list[str]:
    """Nomes das visualizações anexadas (a 1ª é a própria figura). Usado nos testes."""
    meta = fig.layout.meta if isinstance(fig.layout.meta, dict) else {}
    return [meta.get("rt_nome", "Original")] + [a["nome"] for a in meta.get("rt_alternativas", [])]
