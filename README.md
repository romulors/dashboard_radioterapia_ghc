# Dashboard do Fluxo de Radioterapia (GHC / SUS)

Dashboard interativo em Python (Plotly Dash) sobre o fluxo de planejamento e tratamento do serviço de
Radioterapia do Grupo Hospitalar Conceição. O foco é acompanhar **cada paciente, ciclo a ciclo**, com o
**tempo entre atividades** como informação principal, além dos indicadores mensais das apresentações
de junho e agosto de 2026.

## Instalação

Requer Python 3.10 ou superior.

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows (no Linux/macOS: source .venv/bin/activate)
pip install -e ".[dev]"
```

## Uso

As planilhas `Tarefas RT Anonimizado - 2026.xlsx` e `Consultas AL Anonimizado - 2026.xlsx` ficam na raiz
do projeto (caminhos em `config/settings.yaml`).

```bash
python -m rt_dash.etl     # opcional: lê as planilhas e gera o cache em data/processed/*.parquet
python -m rt_dash.app     # sobe o dashboard em http://127.0.0.1:8050  (ou: rt-dash)
```

Na primeira execução o app monta o cache sozinho; ele é refeito quando as planilhas mudam.

## Abas

| Aba | Para quê |
| --- | --- |
| **Visão Geral** | Resumo executivo: KPIs do planejamento, os indicadores do formato da apresentação de agosto e pacientes por sítio; botão "Modo apresentação". |
| **KPIs** | Indicadores-chave do mês (planejamento/tratamento e acelerador linear) e as demais séries mensais do registro. |
| **Eficácia vs Eficiência** | Eficácia: ocupação vs meta, inícios, planejamentos e pacientes por sítio. Eficiência: esperas, duração das sessões e sessões por tratamento. |
| **Resultado vs Tendência** | Resultado: sessões dia × noite e funil de planejamento. Tendência: evolução de ciclos por sítio, heatmap temporal e dispersão tempo × desfecho. |
| **Processos** | Atividades do fluxo por etapa (espera, execução, atraso), heatmap de atrasos por sítio × fluxo e composição sítio → fluxo → status. |
| **Jornada do Paciente** | Lista de pacientes, ciclos de planejamento, Gantt com esperas destacadas, cascata de tempos e comparação com a referência. Exporta CSV. |
| **Sobre** | Autoria, fonte dos dados, tecnologia, referências, definições e metas, qualidade dos dados e acessibilidade. |

Os filtros do topo (período, tipo de fluxo, sítio, ambulatorial × internado) valem para todas as abas, e cliques nos gráficos
filtram as demais visões.

## Testes e qualidade

```bash
pytest -q
ruff check .
```

## Estrutura

```
config/settings.yaml   caminhos, horário do acelerador, corte dia/noite, metas e prazos
src/rt_dash/
  io/        leitura das exportações do Aria (acha cabeçalho, remove rodapé)
  domain/    catálogo de atividades, segmentação em ciclos e tempos, sessões de tratamento
  metrics/   indicadores mensais (registro @indicador), estatísticas por atividade e por paciente
  viz/       paleta GHC, template Plotly e funções de figura
  app/       layout, componentes e uma página por aba
  assets/    CSS (Bootstrap local + estilo GHC)
tests/       pytest com dados sintéticos
docs/        plano do dashboard, fluxo e perguntas de negócio
```

## Limitações conhecidas

- Ainda sem dados de faltas no acelerador, agenda do tomógrafo e CID; a tomografia usa
  `Importar TC e Fusao` como aproximação.
- Ciclos que só têm a recepção (sem importação ainda) aparecem como "Sem tipo".
