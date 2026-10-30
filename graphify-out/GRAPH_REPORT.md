# Graph Report - proj  (2026-10-30)

## Corpus Check
- Corpus is ~3,414 words - fits in a single context window. You may not need a graph.

## Summary
- 61 nodes · 93 edges · 5 communities
- Extraction: 69% EXTRACTED · 31% INFERRED · 0% AMBIGUOUS · INFERRED: 29 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Guia, arquitetura e configuração
- Tempos e prazos por atividade
- Fluxo do processo (Aria)
- Paciente, ciclos e dados
- Layouts e interatividade

## God Nodes (most connected - your core abstractions)
1. `Fluxo de Radioterapia (swimlanes, 2024-12-06)` - 14 edges
2. `CLAUDE.md – guia do projeto` - 11 edges
3. `Dashboard Fluxo de Radioterapia GHC` - 9 edges
4. `Ciclo de planejamento` - 7 edges
5. `Arquitetura em camadas io→domain→metrics→viz→app` - 7 edges
6. `Atividade do fluxo` - 6 edges
7. `Layout recomendado: híbrido A + C + D (+E)` - 6 edges
8. `Planilha Consultas AL (Aria)` - 5 edges
9. `Planilha Tarefas RT (Aria)` - 4 edges
10. `Duração da atividade` - 4 edges

## Surprising Connections (you probably didn't know these)
- `CLAUDE.md – guia do projeto` --references--> `Ciclo de planejamento`  [INFERRED]
  CLAUDE.md → docs/plano-dashboard.md
- `Simulação: Importar TC + Fusão` --conceptually_related_to--> `Ciclo de planejamento`  [INFERRED]
  docs/fluxo-radioterapia.png → docs/plano-dashboard.md
- `Fluxo de Radioterapia (swimlanes, 2024-12-06)` --conceptually_related_to--> `Atividade do fluxo`  [INFERRED]
  docs/fluxo-radioterapia.png → docs/plano-dashboard.md
- `Fluxo de Radioterapia (swimlanes, 2024-12-06)` --conceptually_related_to--> `Layout C · Fluxo como navegação`  [INFERRED]
  docs/fluxo-radioterapia.png → docs/plano-dashboard.md
- `CLAUDE.md – guia do projeto` --references--> `Layout recomendado: híbrido A + C + D (+E)`  [INFERRED]
  CLAUDE.md → docs/plano-dashboard.md

## Hyperedges (group relationships)
- **Jornada do paciente** — docs_plano_dashboard_paciente, docs_plano_dashboard_ciclo, docs_plano_dashboard_atividade, docs_plano_dashboard_espera, docs_plano_dashboard_gantt, docs_plano_dashboard_inicio_tratamento [EXTRACTED 1.00]
- **Layouts alternativos** — docs_plano_dashboard_layout_a, docs_plano_dashboard_layout_b, docs_plano_dashboard_layout_c, docs_plano_dashboard_layout_d, docs_plano_dashboard_layout_e [EXTRACTED 1.00]
- **Perguntas de negócio** — docs_perguntas_negocio_p1, docs_perguntas_negocio_p2, docs_perguntas_negocio_p3, docs_perguntas_negocio_p4, docs_perguntas_negocio_p5, docs_perguntas_negocio_p6, docs_perguntas_negocio_p7, docs_perguntas_negocio_p8, docs_perguntas_negocio_p9, docs_perguntas_negocio_p10 [EXTRACTED 1.00]

## Communities (5 total, 0 thin omitted)

### Community 0 - "Guia, arquitetura e configuração"
Cohesion: 0.24
Nodes (6): CLAUDE.md – guia do projeto, Configuração em YAML (metas, capacidade, corte), Dashboard Fluxo de Radioterapia GHC, Indicadores agosto/2026 (formato resumido), Indicadores junho/2026 (16), Testes pytest com dados sintéticos

### Community 1 - "Tempos e prazos por atividade"
Cohesion: 0.15
Nodes (11): P2 · Distribuição Urgência/Prioridade/Eletivo, P3 · Atividades com maior tempo de execução, P4 · Duração por tipo de fluxo, P6 · Evolução do tempo médio por mês, P7 · % tarefas no prazo, P8 · Atividades com maiores atrasos, Atividade do fluxo, Atraso vs vencimento (+3 more)

### Community 2 - "Fluxo do processo (Aria)"
Cohesion: 0.29
Nodes (13): Recepção: Programar e Agendar Simulação, Simulação: Realizar Tomografia, Simulação: Importar TC + Fusão, Planejamento: Contorno do PTV, Planejamento: Criar Diagnóstico, Planejamento: Prescrição, Planejamento: Planejamento, Planejamento: Aprovação (+5 more)

### Community 3 - "Paciente, ciclos e dados"
Cohesion: 0.20
Nodes (8): P1 · Evolução dos planejamentos concluídos, P10 · Duração do atendimento por tipo, P9 · Espera check-in → início, Planejamento → início do tratamento, Paciente, Contratos de dados com pandera, Planilha Consultas AL (Aria), Planilha Tarefas RT (Aria)

### Community 4 - "Layouts e interatividade"
Cohesion: 0.24
Nodes (9): Wireframes dos 4 layouts, P5 · Atividades com maior variabilidade, Boxplot por atividade e fluxo, Gantt da jornada do paciente, Layout A · Abas temáticas, Layout B · Painel único drill-down, Layout C · Fluxo como navegação, Layout D · Paciente no centro (+1 more)

## Knowledge Gaps
- **13 isolated node(s):** `Paciente`, `Layout E · Modo apresentação`, `Testes pytest com dados sintéticos`, `P1 · Evolução dos planejamentos concluídos`, `P2 · Distribuição Urgência/Prioridade/Eletivo` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 16 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Atividade do fluxo` connect `Tempos e prazos por atividade` to `Fluxo do processo (Aria)`, `Paciente, ciclos e dados`?**
  _High betweenness centrality (0.363) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `Fluxo de Radioterapia (swimlanes, 2024-12-06)` (e.g. with `Atividade do fluxo` and `Layout C · Fluxo como navegação`) actually correct?**
  _`Fluxo de Radioterapia (swimlanes, 2024-12-06)` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Paciente`, `Layout E · Modo apresentação`, `Testes pytest com dados sintéticos` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Why does `Ciclo de planejamento` connect `Paciente, ciclos e dados` to `Guia, arquitetura e configuração`, `Tempos e prazos por atividade`, `Fluxo do processo (Aria)`?**
  _High betweenness centrality (0.327) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `CLAUDE.md – guia do projeto` (e.g. with `Arquitetura em camadas io→domain→metrics→viz→app` and `Ciclo de planejamento`) actually correct?**
  _`CLAUDE.md – guia do projeto` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Why does `Fluxo de Radioterapia (swimlanes, 2024-12-06)` connect `Fluxo do processo (Aria)` to `Tempos e prazos por atividade`, `Layouts e interatividade`?**
  _High betweenness centrality (0.318) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `Ciclo de planejamento` (e.g. with `CLAUDE.md – guia do projeto` and `Simulação: Importar TC + Fusão`) actually correct?**
  _`Ciclo de planejamento` has 3 INFERRED edges - model-reasoned connections that need verification._