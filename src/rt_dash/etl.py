"""Executa o ETL e grava o cache parquet: python -m rt_dash.etl"""

from __future__ import annotations

import argparse

from rt_dash.config import DEFAULT_SETTINGS, load_settings
from rt_dash.data import carregar_dataset


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(DEFAULT_SETTINGS))
    args = parser.parse_args()
    settings = load_settings(args.config)
    ds = carregar_dataset(settings, recriar=True)
    print(
        f"Tarefas: {len(ds.tarefas):,} | atividades na jornada: {len(ds.jornada):,} | "
        f"ciclos: {len(ds.ciclos):,} | pacientes: {ds.ciclos['paciente_id'].nunique():,} | "
        f"agendamentos no AL: {len(ds.sessoes):,}"
    )
    print(f"Cache gravado em {settings.pasta_processados}")


if __name__ == "__main__":
    main()
