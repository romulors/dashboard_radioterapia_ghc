# CLAUDE.md — Dashboard do Fluxo de Radioterapia (GHC / SUS)

Dashboard em Python (Plotly Dash) sobre o fluxo de atendimento — planejamento e tratamento — do
serviço de Radioterapia do Grupo Hospitalar Conceição (GHC). Trabalho da disciplina de
Visualização de Dados. Idioma do projeto, da interface e dos comentários: **português**.

O plano completo está em `docs/plano-dashboard.md`. O mapa de ideias (Graphify) está em
`graphify-out/` — abra `graphify-out/graph.html` no navegador e leia `graphify-out/GRAPH_REPORT.md`.

## Objetivo central

Acompanhar o **fluxo de planejamento de cada paciente**, segmentado por paciente e por ciclo, com o
**tempo entre atividades** como informação-chave. Além disso, reproduzir os indicadores das
apresentações de junho/2026 e agosto/2026 e responder às perguntas de `PerguntasNegocio.txt`.

## Fontes de dados (exportações do sistema Aria, anonimizadas)

| Arquivo | Aba útil | Cabeçalho | Conteúdo |
| --- | --- | --- | --- |
| `Tarefas RT Anonimizado - 2026.xlsx` | 2ª aba | linha 13 (índice 12) | ~21,2 mil tarefas do fluxo, 683 pacientes |
| `Consultas AL Anonimizado - 2026.xlsx` | 2ª aba | linha 9 (índice 8) | ~8,1 mil agendamentos no acelerador linear, 581 pacientes |

- Chave de ligação: ID do paciente (`Id do Paciente` / `ID do paciente`).
- Rodapé com totais (`Máx:`, `Média:`, `DEV STD:`) deve ser descartado: manter só linhas com `#` numérico.
- Nomes de colunas têm espaços sobrando — sempre aplicar `.str.strip()`.
- Tarefas `Cancelado` não têm início/término; contam só como cancelamento.
- Muitas tarefas têm duração 0 (apenas "marcadas"): para elas o tempo relevante é a espera.
- Os dados (anonimizados) **são versionados** no Git por decisão do autor.

## Modelo de domínio

**Paciente → Ciclo de planejamento → Atividade.**

- Novo ciclo a cada `Importar TC e Fusao` (ou `Importar Radiografia`, braquiterapia) concluído.
- Tipo de fluxo vem do sufixo do nome: Eletivo, Prioridade, Urgência, Braquiterapia, Retomografado.
  Separar em `atividade_generica` + `tipo_fluxo`.
- Etapas (categoria Aria): 2-Recepção, 3-Simulação, 4-Planejamento, 5-Pré-Tratamento,
  8-Controle de Qualidade, G-Gestão, V-Revisão (revisão de imagens fica fora do fluxo de planejamento).
- Por atividade, dentro do ciclo, ordenado por início:
  - `espera` = início − término da atividade anterior (negativa = paralelismo, não zerar)
  - `duracao` = término − início
  - `atraso` = término − vencimento (> 0 = fora do prazo)
  - `acumulado` = tempo desde `Importar TC e Fusao`
- Ciclo → tratamento: primeira consulta `Início do Tratamento` após o fim do ciclo (até 120 dias).
- Tarefas de Recepção e Simulação pertencem ao ciclo da **próxima** importação; demais tarefas anteriores à
  primeira importação do paciente (sobras de ciclos de 2025) são descartadas.
- `espera` usa o maior término anterior (cummax), não só a atividade imediatamente anterior.
- Sessões com duração > 60 min são excluídas da média de duração; grafias com/sem acento do sítio são
  unificadas e `Encaixe` não conta como sítio.

## Arquitetura (camadas, dependência num só sentido)

`io` → `domain` → `metrics` → `viz` → `app`

```
src/rt_dash/
  config.py  carrega config/settings.yaml (dataclass Settings)
  data.py    Dataset (tarefas, jornada, ciclos, sessoes, cursos), cache parquet e Filtros globais
  etl.py     python -m rt_dash.etl
  io/        loaders.py (lê xlsx, acha cabeçalho, remove rodapé), schemas.py (mapa de colunas)
  domain/    activities.py (catálogo), cycles.py (segmentação e tempos), treatment.py (sessões AL)
  metrics/   monthly.py (indicadores mensais), activity.py, patient.py, registry.py (@indicador)
  viz/       theme.py (paleta + template Plotly "ghc"), figures.py (DataFrame → Figure)
  app/       main.py (abas, estado, callbacks globais), components.py, context.py, pages/ (uma por aba)
  assets/    bootstrap.min.css (local, CDN bloqueado) e style.css
config/      settings.yaml (caminhos, acelerador, corte dia/noite, metas, prazos)
tests/       pytest com dados sintéticos
```

Regras:
- Callbacks do Dash **não** leem Excel nem calculam tempos; só chamam funções puras de `metrics`.
- Funções de `domain` e `metrics` são puras (DataFrame entra, DataFrame sai) e testadas.
- Indicador novo = função registrada com `@indicador(...)` em `metrics/registry.py`.
- Nenhuma cor escrita à mão em gráficos: usar `viz/theme.py`.
- Constantes de negócio (metas 80–85%, corte dia/noite 19h, 60 vagas/dia) ficam em `config/settings.yaml`.
- Ao mudar colunas derivadas do `Dataset`, incremente `VERSAO_CACHE` em `data.py` (invalida o parquet).

## Abas implementadas

Ordem e conteúdo (composição em `app/abas.py`, tipos de indicador conforme scopi.com.br/blog/tipos-de-indicadores):
**Visão Geral** (resumo + "modo apresentação"), **KPIs** (KPIs do mês, acelerador e demais séries mensais),
**Eficácia vs Eficiência** (objetivo atingido × recursos/tempo gastos), **Resultado vs Tendência** (o que ocorreu ×
sinais de evolução), **Processos** (atividades, atrasos, composição) e **Jornada do Paciente** (lista + Gantt + CSV).
Os callbacks seguem nos módulos de `pages/`; `abas.py` só decide onde cada cartão aparece (cada id uma única vez).
Filtragem cruzada com estado único em `dcc.Store` (`store-filtros`, `store-selecao`).

## Paleta

- Moldura GHC: `#004231` (verde escuro), `#006E77` (petróleo), `#7ABBB1` (verde-água), fundo `#F4F6F6`.
- Referências de cor em `Material Referência/Cores - *.jpeg` (acessíveis, complementares, contraste, gradiente),
  definidas em `viz/theme.py` como `PALETA_ACESSIVEIS`, `PALETA_COMPLEMENTARES`, `PALETA_CONTRASTE`,
  `PALETA_GRADIENTE` (e `PALETA_CATEGORICA` para séries sem cor fixa).
- Tipo de fluxo: Eletivo `#038C8C`, Prioridade `#C2AA61`, Urgência `#8C3603`,
  Braquiterapia `#180042`, Retomografado `#61C2AA`. Dia `#04BABA` (clara) / Noite `#014040` (escura), do gradiente.
- Escala sequencial (heatmaps): branco → `#04BABA` → `#038C8C` → `#026969` → `#014040` (gradiente).
- No prazo `#038C3E` / atrasado `#8C3603`, sempre com ícone ou texto.
- Máx. 5–8 cores categóricas; sem arco-íris; escalas sequenciais de uma matiz.

## Stack e comandos

Python 3.10+, pandas, plotly, dash, dash-bootstrap-components, dash-ag-grid, pyarrow, pyyaml,
pytest, ruff.

```bash
pip install -e ".[dev]"
python -m rt_dash.etl          # opcional: gera data/processed/*.parquet
python -m rt_dash.app          # sobe o dashboard em http://127.0.0.1:8050 (ou: rt-dash)
pytest -q && ruff check .
```

## Convenções

- Código, nomes e textos da interface em português; nomes de variáveis em snake_case sem acento.
- Tempos internos em minutos; exibir em horas ou dias úteis conforme seletor.
- Datas sempre `datetime64`; mês de referência = mês do término da atividade.
- O autor versiona manualmente: **não fazer commits** sem pedido explícito.
- Material de referência (aulas de DataViz, Dash, cores, composição) em `Material Referência/`.

## Perguntas em aberto

- Fonte para faltas (absenteísmo) do acelerador e CID por paciente.
- Exportação com as atividades de tomografia (ex.: "Tomografia Pelve"); as planilhas atuais não as trazem.

## Regras de negócio confirmadas

- Acelerador linear: atende das 07h00 às 22h30, vagas de 15 min; entre 10h–11h e 15h–16h as vagas são
  de 20 min, preferencialmente para inícios de tratamento. Capacidade = 54 + 6 = **60 vagas/dia** (930 min).
- Turno: **dia** = atendimentos até 18h45; **noite** = a partir das 19h00.
- Tomógrafo: não há agenda própria; estimar a ocupação pelas atividades de tomografia por sítio
  (ex.: "Tomografia Pelve"). Enquanto não houver essa exportação, usar `Importar TC e Fusao` como proxy.
