import pandas as pd
import pytest

from rt_dash.io.loaders import carregar_tarefas, ler_relatorio_aria
from rt_dash.io.schemas import SchemaError


def _planilha(tmp_path, cabecalho, linhas):
    """Imita a exportação do Aria: aba 'Document map', título, cabeçalho e rodapé de totais."""
    caminho = tmp_path / "relatorio.xlsx"
    titulo = [[None, None, "Relatório"], [None] * 3, [None] * 3]
    largura = len(cabecalho) + 1
    corpo = [[None, *cabecalho], *[[None, *linha] for linha in linhas], [None, None, "Máx:", 99]]
    titulo = [(r + [None] * largura)[:largura] for r in titulo]
    corpo = [(r + [None] * largura)[:largura] for r in corpo]
    with pd.ExcelWriter(caminho) as w:
        pd.DataFrame([["Document map"]]).to_excel(w, sheet_name="Document map", header=False, index=False)
        pd.DataFrame(titulo + corpo).to_excel(w, sheet_name="dados", header=False, index=False)
    return caminho


CAB = [
    "#",
    "Id do Paciente ",
    "Nome da Atividade",
    "Categoria da Atividade",
    "Status",
    "Ultima edição por",
    "Hora Vencimento",
    "Hora de Inicio",
    "Hora de Termino",
]


def test_le_cabecalho_e_descarta_rodape(tmp_path):
    caminho = _planilha(
        tmp_path,
        CAB,
        [
            [
                1,
                44162936,
                "Importar TC e Fusao",
                "4 - Planejamento",
                "Concluído",
                "ad\\1",
                "2026-03-04 12:00",
                "2026-03-04 09:43",
                "2026-03-04 09:44",
            ]
        ],
    )
    bruto = ler_relatorio_aria(caminho)
    assert "Id do Paciente" in bruto.columns  # espaços removidos
    t = carregar_tarefas(caminho)
    assert len(t) == 1
    assert t.loc[0, "paciente_id"] == "44162936"
    assert t.loc[0, "inicio"] == pd.Timestamp("2026-03-04 09:43")


def test_erro_claro_quando_falta_coluna(tmp_path):
    caminho = _planilha(tmp_path, CAB[:-1], [[1, 1, "x", "4 - Planejamento", "Concluído", "u", None, None]])
    with pytest.raises(SchemaError, match="Hora de Termino"):
        carregar_tarefas(caminho)
