# Catálogo de gráficos por tipo de informação

**Dashboard de Radioterapia GHC · 06/11/2026**

Este documento reúne, sem repetição, todos os gráficos que aparecem nos quatro painéis do Tableau Public indicados pelo Romulo. Cada gráfico está classificado pelo tipo de informação que comunica. Para cada um há o uso recomendado, a interatividade possível, a viabilidade em Plotly/Dash e o quanto ele serve aos dados de radioterapia. No fim está a estratégia de implementação.

## 1. Fontes e como foram lidas

| Código | Painel | Autor | Itens lidos |
|---|---|---|---|
| **F** | [The Tableau Chart Catalog](https://public.tableau.com/app/profile/kevin.flerlage/viz/TheTableauChartCatalog/TableauChartExamples) | Kevin Flerlage | 100 gráficos (74 autores) |
| **C** | [Tableau Viz Cookbook](https://public.tableau.com/app/profile/josh.weyburne/viz/CookBook/VizCookbook) | Josh Weyburne | 52 cartões e 111 nomes no filtro "por nome" (inclui sinônimos) |
| **T** | [Tutorials of visualizations](https://public.tableau.com/app/profile/lilla.rasztik/viz/Tutorialsofvisualizations/Tutorial) | Lilla Rasztik | 35 tutoriais |
| **G** | [Chart Suggestions Guide](https://public.tableau.com/app/profile/adedamola8122/viz/ChartSelectionGuide2/Dashboard) | Adedamola Ladipo (baseado em A. Abela, 2009) | 20 gráficos em 4 propósitos |

Os painéis foram abertos no navegador do computador do Romulo, porque o container bloqueia o Tableau Public. Os nomes foram lidos das capturas de tela e, no Cookbook, também da lista do filtro. Para o uso de cada gráfico, usei a taxonomia do [Visual Vocabulary do Financial Times](https://github.com/ft-interactive/visual-vocabulary) (desvio, correlação, ranking, distribuição, tempo, magnitude, parte-todo, espacial e fluxo), o próprio guia G (comparação, relação, distribuição e composição) e a documentação do Plotly.

**O que não consegui verificar:**
- **Atualização de 06/11:** abri todos os exemplos, inclusive os raros (101 do Flerlage, 52 do Cookbook e 53 links de tutoriais da Rasztik). O link e a descrição de cada um estão no Apêndice A. Os sete modelos que antes estavam como "não verificado" foram conferidos e corrigidos (seção 3.14), e entrou um modelo novo, V13 Icicle de desvio.
- No Cookbook, o filtro "por nome" lista sinônimos que não têm cartão próprio. A maioria é sinônimo conhecido do [Data Viz Catalogue](https://datavizcatalogue.com), mas quatro ficaram sem associação certa: **Belt Chart**, **Dna**, **Linear Embeddings** e **Timetable**. Associei cada um ao modelo mais provável e deixei isso indicado.
- O filtro "por tipo" do Cookbook tem as categorias (Comparisons, Data over time, Distribution, Flow, Hierarchy, Location, Part-to-a-whole, Relationships etc.), mas não extraí qual cartão pertence a cada uma. A classificação abaixo é minha.

## 2. Regras usadas na classificação

1. **Sem repetição.** Sinônimos e o mesmo gráfico em painéis diferentes viram um único modelo, com todas as fontes listadas. Exemplo: "Barbell" (F, C) e "Dumbbell" (T) são o mesmo modelo.
2. **Estilo conta como modelo separado.** Como o Romulo pediu, quando uma estilização visual muda o gráfico (contorno, cantos arredondados, curvas, versão radial, gradiente), ela vira um modelo próprio. Exemplo: Barras, Barras com contorno, Barras arredondadas e Barras "desenhadas à mão" são quatro modelos.
3. **Um tipo principal por modelo.** Cada modelo fica no tipo de informação em que ele é mais forte. Os usos secundários aparecem na coluna "Uso recomendado".

### Legendas das colunas

**Interatividade** (o que o gráfico permite em Plotly/Dash):

| Sigla | Significado |
|---|---|
| H | Dica ao passar o mouse (hover) |
| Z | Zoom e arrastar |
| L | Clicar na legenda para mostrar ou ocultar séries |
| S | Selecionar pontos com caixa ou laço (`selectedData`) |
| C | Clique como filtro cruzado para outros gráficos (`clickData` em callback) |
| D | Drill-down nativo (clicar para entrar no nível de baixo) |
| A | Animação ou controle deslizante por período (`animation_frame`) |
| R | Seletor de intervalo de datas (range slider) |
| M | Mover elementos (nós do Sankey, eixos e filtros do Parcoords) |

**Plotly/Dash:** **N** = nativo (um trace ou uma função do `plotly.express`); **Mo** = montagem (combinar traces, `shapes` e cálculos simples); **Df** = difícil (não existe trace; exige geometria calculada à mão, biblioteca externa ou componente JavaScript).

**Uso na RT:** ★★★ alta, ★★ média, ★ baixa, — não se aplica aos dados atuais.

## 3. Catálogo (131 modelos)

### 3.1 Indicador e progresso (KPI)
Mostra um único número em relação a uma meta. É o primeiro nível de leitura do gestor.

| # | Modelo (sinônimos) | Fontes | Uso recomendado | Interat. | Plotly | Uso na RT |
|---|---|---|---|---|---|---|
| K1 | Bullet graph | F, C | Valor atual contra meta e faixas de tolerância, em pouco espaço | H | N (`go.Indicator` com `gauge.shape="bullet"`) | ★★★ Ocupação do acelerador contra a faixa de 80–85%; inícios do mês contra a meta de 60 |
| K2 | Gauge (velocímetro) | F | Um único KPI com zonas de alerta; ocupa muito espaço | H | N (`go.Indicator` gauge) | ★ Prefira o bullet; só para tela de apresentação |
| K3 | Donut de progresso radial | F | Percentual concluído com o número no centro | H | Mo (`go.Pie` com `hole` e duas fatias) | ★★ % de tarefas no prazo |
| K4 | Barra de progresso | F | Percentual de uma meta, linear e fácil de ler | H | Mo (`go.Bar` sobre barra de fundo) | ★★★ Vagas ocupadas no dia (de 60) |

### 3.2 Comparação de magnitude entre categorias
Responde "quanto" e "qual é maior". As barras são a escolha padrão porque o olho compara comprimentos com precisão.

| # | Modelo (sinônimos) | Fontes | Uso recomendado | Interat. | Plotly | Uso na RT |
|---|---|---|---|---|---|---|
| M1 | Barras horizontais (Bar chart, Bar graph) | F, C, G | Muitas categorias ou rótulos longos | H, C, Z | N | ★★★ Volume por atividade, por sítio |
| M2 | Colunas verticais (Column chart/graph) | C, G | Poucas categorias ou períodos | H, C, Z | N | ★★★ Inícios de tratamento por mês |
| M3 | Barras com contorno (Bar outline) | F | Destacar uma barra (o mês atual) e esvaziar as demais | H, C | Mo (`marker.line` e preenchimento transparente) | ★★ Mês corrente ainda incompleto |
| M4 | Barras arredondadas (Rounded bar) | T | Visual mais leve em painéis de apresentação | H, C | N (`barcornerradius`, Plotly ≥ 5.19) | ★ Só estética |
| M5 | Barras "desenhadas à mão" / hachuradas (Hand-drawn bar) | T | Textura no lugar da cor | H, C | Mo (`marker.pattern.shape`) | ★★ Diferenciar Eletivo/Prioridade/Urgência sem depender só da cor (acessibilidade) |
| M6 | Barras agrupadas (Side-by-side, Clustered, Grouped, Multi-set bar) | C | Comparar 2–4 séries por categoria | H, L, C | N (`barmode="group"`) | ★★★ Sessões dia × noite por mês |
| M7 | Barra dentro de barra (Bar in bar) | F, T | Realizado contra capacidade ou contra período anterior | H, L | Mo (`barmode="overlay"` com larguras diferentes) | ★★★ Sessões realizadas dentro das vagas disponíveis |
| M8 | Colunas de largura variável | G | Duas variáveis por item: largura e altura | H | Mo (`go.Bar` com `width` por barra) | ★★ Sítio: largura = nº de pacientes, altura = mediana de dias |
| M9 | Pirulito (Lollipop) | F, C, T | Muitas categorias com menos tinta que a barra | H, C | Mo (`go.Scatter` com marcadores e linhas) | ★★★ Mediana de dias por atividade (15+ atividades) |
| M10 | Gráfico de pontos de Cleveland (Cleveland dot plot) | F | Comparar valores de duas ou mais séries no mesmo eixo | H, L, C | N (`go.Scatter`, modo marcadores) | ★★★ Mediana por sítio, um ponto por fluxo |
| M11 | Bolhas agrupadas (Packed bubbles) | F, C | Visão geral de tamanho; leitura imprecisa | H | Df (calcular posições com `circlify`) | ★ |
| M12 | Barras radiais (Radial bar) | F, C | Barras em arcos concêntricos; estética | H | Mo (`go.Barpolar`) | ★ |
| M13 | Barras radiais arredondadas (Rounded radial bar) | T | Variante estética da anterior | H | Df | — |
| M14 | Colunas radiais (Radial column, Circular column graph) | C, G | Dados cíclicos (horas do dia, dias da semana) | H, L | N (`go.Barpolar`) | ★★ Sessões por hora do dia (07h–22h30) |
| M15 | Gráfico de unidades (Unit chart) | F | Cada ícone é uma unidade; bom para contagens pequenas | H | Mo (`go.Scatter` com símbolos em grade) | ★★ Pacientes iniciados na semana |
| M16 | Pictograma composto (Compound pictogram) | F | Várias grades de ícones comparadas lado a lado | H | Mo | ★ |
| M17 | Forma preenchida (Filled shaped chart) | F | Percentual mostrado como nível de preenchimento de um ícone | — | Df (imagem e `shapes`) | ★ |
| M18 | Radar (Spider, Web, Star plot, Star graph, Polar chart) | F, C, T | Perfil de poucos itens em 4–8 métricas | H, L | N (`go.Scatterpolar`, `fill="toself"`) | ★ Perfil por sítio; barras agrupadas leem melhor |
| M19 | Polígono radial com abas (Radial tab polygon) | T | Anel de "abas" de mesma largura, uma por categoria, com a cor codificando o valor; é uma tabela de destaque em forma de anel, usada como moldura decorativa | H | Mo (`go.Barpolar` com raios fixos e cor pelo valor) | — |
| M20 | Gráfico de pétalas (Petal chart) | F | Várias métricas por item como pétalas | H | Df | — |
| M21 | Pétalas sem polígonos | F | Variante da anterior com círculos | H | Df | — |
| M22 | Formas personalizadas (Shapes) | T | Técnica, não um gráfico: imagens próprias usadas como marca (por exemplo pétalas com centro comum, cujo tamanho é o valor, em vez de polígonos) | H | Mo (`layout.images` ou símbolos) | ★ |

### 3.3 Ranking
Mostra posição, não só valor.

| # | Modelo (sinônimos) | Fontes | Uso recomendado | Interat. | Plotly | Uso na RT |
|---|---|---|---|---|---|---|
| R1 | Bump chart | F, C | Mudança de posição ao longo do tempo | H, L, C | N (linhas e marcadores com eixo y invertido) | ★★ Ranking de sítios por volume a cada mês |
| R2 | Bump curvo (Bump curvy, Curvy bump) | F, T | Igual ao anterior, com linhas suaves | H, L | N (`line.shape="spline"`) | ★★ |
| R3 | Bump curvo radial | F | Variante circular | H | Df | — |
| R4 | Gráfico de inclinação (Slope graph) | F, C | Antes e depois de dois momentos | H, C | N | ★★★ Mediana por atividade no 1º contra o 2º quadrimestre |
| R5 | Inclinação estilo Sankey | F | Faixas largas entre os dois momentos | H | Mo | ★ |
| R6 | Inclinação curva (Slope curvy) | F | Linhas em S | H | Mo | ★ |
| R7 | Pareto | F, C | Quais poucos itens somam 80% do total | H, C | Mo (barras e linha acumulada no eixo secundário) | ★★★ Atividades que concentram 80% do tempo de espera |

### 3.4 Desvio, diferença e intervalo
Mostra a distância entre dois valores, ou entre um valor e uma referência.

| # | Modelo (sinônimos) | Fontes | Uso recomendado | Interat. | Plotly | Uso na RT |
|---|---|---|---|---|---|---|
| V1 | Haltere (Barbell, Dumbbell; "Dna" provável) | F, C, T | Distância entre dois valores por categoria | H, C | Mo | ★★★ Dia × noite por sítio; prazo previsto × realizado |
| V2 | Faixa / barra flutuante (Span chart, Range bar/column, Floating bar, High-low graph, Difference graph) | C | Mínimo e máximo, ou P25 e P75, por categoria | H, C | N (`go.Bar` com `base`) | ★★★ Intervalo interquartil de dias por atividade |
| V3 | Barras divergentes (Diverging bar) | T | Desvio positivo ou negativo de uma meta | H, C | N | ★★★ Inícios do mês menos a meta de 60 |
| V4 | Pirâmide / tornado (Population pyramid, Age & Sex pyramid, Tornado chart) | F, C | Dois grupos espelhados no mesmo eixo | H, L | N (`barmode="relative"` com um lado negativo) | ★★ Sessões dia × noite por sítio, espelhadas |
| V5 | Gráfico de setas (Arrow chart) | C | Direção e tamanho da mudança entre dois momentos | H | Mo (`annotations` com seta) | ★★★ Quanto cada atividade melhorou ou piorou de jan para ago |
| V6 | Cometa (Comet chart) | F | Mudança mostrada como linha afinando | H | Mo | ★★ |
| V7 | Girino (Tadpole chart) | F | Valor atual com "cauda" até o anterior | H | Mo | ★★ |
| V8 | Cascata (Waterfall) | F, C, G | Como parcelas somam ou subtraem até um total | H | N (`go.Waterfall`) | ★★★ Composição dos dias do ciclo (já implementado) |
| V9 | Cascata conectada (Waterfall connected) | F | Cascata com linhas ligando os degraus | H | N (`connector`) | ★★★ Mesmo uso, leitura mais fácil |
| V10 | Bandas de Bollinger (Bollinger bands; "Belt chart" provável) | C | Média móvel com faixa de ±2 desvios | H, Z, R | Mo (linhas com `fill="tonexty"`) | ★★★ Tempo até início com faixa esperada |
| V11 | Gráfico de controle (Control chart) | C | Processo com limites superior e inferior | H, Z, R, S | Mo | ★★★ Já implementado; marcar pontos fora do limite |
| V13 | Icicle de desvio (Deviation icicle chart) | T | Barras que "pendem" da linha da meta para baixo ou sobem acima dela, período a período; mostra o quanto faltou ou sobrou em relação à meta | H, C | Mo (`go.Bar` com `base` igual à meta) | ★★★ Inícios de tratamento por mês contra a meta de 60 |
| V12 | Candlestick (Japanese candlestick) | C, T | Abertura, fechamento, máximo e mínimo por período | H, Z, R | N (`go.Candlestick`) | ★ Pode mostrar mín/P25/P75/máx da espera por semana, mas o box plot é mais claro |

### 3.5 Tempo e tendência
Mostra como algo muda. A linha é a escolha padrão para muitos períodos; colunas servem para poucos.

| # | Modelo (sinônimos) | Fontes | Uso recomendado | Interat. | Plotly | Uso na RT |
|---|---|---|---|---|---|---|
| T1 | Linhas (Line chart) | F, C, G | Série contínua, poucas ou muitas séries | H, Z, L, R, S | N | ★★★ Tempo médio por mês (pergunta 6) |
| T2 | Linha curva (Curved line chart) | T | Suaviza a leitura; pode sugerir valores que não existem | H, Z, L | N (`spline`) | ★ |
| T3 | Área (Area graph) | F, C | Volume ao longo do tempo | H, Z, L, R | N | ★★ |
| T4 | Área com gradiente (Gradient area) | T | Estética; dá peso visual à série principal | H, Z | N (`fillgradient`, Plotly ≥ 5.20) | ★ |
| T5 | Degraus (Step chart) | F | Valores que mudam em saltos | H, Z, R | N (`line_shape="hv"`) | ★★★ Ciclos em aberto (WIP) dia a dia |
| T6 | Índice base 100 (Index chart) | F | Crescimento relativo de séries com escalas diferentes | H, Z, L | N | ★★ Crescimento por sítio desde janeiro |
| T7 | Sparklines | F, C | Tendência em miniatura ao lado de um número | H | Mo (figuras pequenas sem eixos) | ★★★ Cartões de KPI com tendência |
| T8 | Tabela com gráficos embutidos | G | Tabela com mini barras ou linhas por linha | H, C | Mo (Dash AG Grid com células de gráfico) | ★★★ Tabela de sítios com tendência |
| T9 | Horizonte (Horizon chart) | F, C | Muitas séries temporais em pouco espaço | H | Df | ★ |
| T10 | Fluxo empilhado (Stream graph, ThemeRiver) | F, C, T | Composição ao longo do tempo com forma orgânica | H, L | Mo (área empilhada com deslocamento calculado) | ★ |
| T11 | Espiral (Spiral plot, Time series spiral) | F, C | Padrões sazonais em séries longas | H | Mo (`go.Scatterpolar`) | ★ Precisaria de vários anos de dados |
| T12 | Linha radial (Radial line) | F | Série cíclica em volta do círculo | H, L | N (`go.Scatterpolar`) | ★ |
| T13 | Série temporal radial (Radial time series) | F, T | Pontos ou barras por dia em volta do círculo | H | Mo | ★ |
| T14 | Área empilhada radial | F | Variante circular da área empilhada | H | Mo | — |
| T15 | Jump plot | F, C | Arcos entre momentos para mostrar saltos | H | Df | ★ |
| T16 | Calendário (Calendar heatmap) | F, C | Valor por dia com padrões de semana | H, C | Mo (`go.Heatmap` semana × dia da semana) | ★★★ Ocupação diária do acelerador; faltas |
| T17 | Combinação / dois eixos (Combination chart, Dual axis) | C | Duas medidas de escalas diferentes | H, Z, L | N (`secondary_y`) | ★★ Sessões (colunas) e ocupação % (linha); usar com cuidado |
| T18 | Coxcomb / rosa de Nightingale (Polar area) | F, C, T | Ciclos (meses, horas) com área por setor | H, L | N (`go.Barpolar`) | ★ Colunas comuns leem melhor |

### 3.6 Distribuição
Mostra como os valores se espalham: centro, variação e extremos. É o tipo mais importante para o requisito-chave do projeto (tempo entre atividades por paciente).

| # | Modelo (sinônimos) | Fontes | Uso recomendado | Interat. | Plotly | Uso na RT |
|---|---|---|---|---|---|---|
| D1 | Histograma em colunas (Column histogram) | F, C, G | Uma variável, poucos dados | H, Z, S | N | ★★★ Espera no check-in (já implementado) |
| D2 | Histograma de linha / densidade (Line histogram) | G | Uma variável com muitos dados; sobrepor grupos | H, Z, L | Mo (`ff.create_distplot` ou KDE) | ★★★ Dias até o início, uma curva por fluxo |
| D3 | Histograma marginal | F | Dispersão com a distribuição de cada eixo nas bordas | H, Z, S | N (`px.scatter(marginal_x=...)`) | ★★ |
| D4 | Box plot (Box and whisker) | F, C | Comparar mediana e variabilidade entre grupos | H, Z, L, C | N | ★★★ Duração por fluxo (pergunta 4, já implementado) |
| D5 | Violino (Violin plot) | T | Forma da distribuição, inclusive dois picos | H, Z, L | N (`go.Violin`) | ★★★ Tempo até início por fluxo |
| D6 | Pontos com dispersão (Jitter plot, Jittering) | F, T | Cada observação visível sem sobreposição | H, Z, S, C | N (`px.strip`) | ★★★ Um ponto por paciente sobre o box plot |
| D7 | Faixa de pontos (Dot strip plot) | F | Valores de cada grupo numa faixa, destacando um | H, S, C | N | ★★★ Mediana de cada sítio com o serviço como referência |
| D8 | Ridgeline (Joy plot) | F, T | Muitas distribuições empilhadas para comparar forma | H | Mo (`go.Violin` com `side="positive"`) | ★★ Espera por mês |
| D9 | Histograma de unidades (Unit histogram) | F | Histograma em que cada ponto é uma pessoa | H, C | Mo | ★★ Cada paciente como ponto; humaniza o dado |
| D10 | Histograma radial empilhado | F | Variante circular | H | Df | — |
| D11 | Distribuição espelhada (Mirrored distribution) | F | Duas distribuições frente a frente | H, L | Mo (dois histogramas, um negativo) | ★★ Horários de sessão dia × noite |
| D12 | Dispersão hexagonal (Scatter hexbin) | F | Densidade quando há pontos demais | H, Z | Mo (`go.Histogram2d` ou contorno) | ★★ Hora de início × duração da sessão |
| D13 | Plum pudding (waffle circular) | F, T | Waffle de 100 ícones ou círculos dispostos em círculo ("o mundo como 100 pessoas"); é composição, variante do P8 | H | Mo (`go.Scatter` com marcadores em posições calculadas) | ★★ 60 vagas do dia como 60 círculos |

### 3.7 Relação e correlação
Mostra se duas ou mais variáveis andam juntas.

| # | Modelo (sinônimos) | Fontes | Uso recomendado | Interat. | Plotly | Uso na RT |
|---|---|---|---|---|---|---|
| L1 | Dispersão (Scatter plot, Scatter chart/graph, Scattergram, X-Y plot, Point graph) | F, C, G | Duas variáveis numéricas | H, Z, S, C | N | ★★★ Dias de planejamento × nº de atividades do ciclo |
| L2 | Bolhas (Scatter with size, Bubble plot) | F, G | Três variáveis | H, Z, S, L | N | ★★ Sítio: volume × mediana × atraso |
| L3 | Dispersão com totais (Scatter with totals) | F | Pontos individuais (cada temporada) e um marcador maior com o total ou média de cada grupo no mesmo plano | H, S, C | Mo (dois traces de dispersão) | ★★ Dias de cada paciente e a mediana do fluxo |
| L4 | Dispersão com faixas de referência | F | Zonas de "bom" e "ruim" no fundo | H, Z, S | N (`add_hrect`/`add_vrect`) | ★★★ Atraso × duração com a faixa da meta |
| L5 | Coordenadas paralelas (Parallel coordinates) | F | Muitas variáveis por item; filtros nos eixos | H, M | N (`go.Parcoords`, com filtro nos eixos) | ★★ Exploratório: dias em cada etapa por ciclo |
| L6 | Ternário (Ternary plot) | F | Itens com três partes que somam 100% | H, Z, S | N (`go.Scatterternary`) | ★ % do tempo do ciclo em pré-planejamento, planejamento e espera |
| L7 | Tabela de destaque / mapa de calor (Highlight table, Heatmap) | F, C | Duas categorias com intensidade de cor | H, C, Z | N (`go.Heatmap` com texto) | ★★★ Atividade × mês (já implementado) |
| L8 | Mapa de calor com quadrados dimensionados | C | Cor e tamanho codificam duas medidas | H, C | Mo (marcadores quadrados com tamanho) | ★★ Atividade × fluxo: tamanho = volume, cor = mediana |
| L9 | Tabela de destaque radial | F | Variante circular | H | Df | — |
| L10 | Tabela cruzada (Crosstab, Pivot table, Text table) | C | Valores exatos para consulta | Ordenar, filtrar, exportar | N (Dash AG Grid ou DataTable) | ★★★ Tabela acessível de todo gráfico |

### 3.8 Composição (parte de um todo)

| # | Modelo (sinônimos) | Fontes | Uso recomendado | Interat. | Plotly | Uso na RT |
|---|---|---|---|---|---|---|
| P1 | Pizza (Pie chart) | F, C | Até 3 partes, uma única vez | H, L, C | N | ★ Eletivo/Prioridade/Urgência, no máximo |
| P2 | Rosca (Donut, Ring chart) | F, C, T, G | Participação simples com total no centro | H, L, C | N (`hole`) | ★★ Pergunta 2 |
| P3 | Barras empilhadas (Stacked bar/column) | F, G | Total e partes ao longo de poucos períodos | H, L, C | N (`barmode="stack"`) | ★★★ Inícios por mês por fluxo |
| P4 | Colunas 100% empilhadas | G | Só a proporção importa | H, L, C | N (`barnorm="percent"`) | ★★★ % dia × noite por mês |
| P5 | Colunas 100% com subcomponentes | G | Partes com subdivisões | H, L | Mo | ★★ Fluxo dividido por sítio |
| P6 | Área empilhada | F, G | Total e partes em muitos períodos | H, L, Z, R | N | ★★ |
| P7 | Área 100% empilhada | G | Proporção em muitos períodos | H, L, Z, R | N (`groupnorm="percent"`) | ★★ |
| P8 | Waffle | F, T | Percentual em grade 10 × 10, fácil para leigos | H | Mo (`go.Heatmap` em grade) | ★★★ 60 vagas do dia: ocupadas, livres, faltas |
| P9 | Marimekko (Mosaic plot) | F, C | Duas dimensões de proporção ao mesmo tempo | H, C | Mo (barras com largura variável) | ★★ Sítio × fluxo |
| P10 | Treemap | F, C, G | Hierarquia com tamanho e cor | H, D, C | N (`go.Treemap`) | ★★ Sítios por volume, cor = mediana |
| P11 | Sunburst (Radial treemap, Multi-level pie) | F, C, T | Hierarquia em anéis | H, D, C | N (`go.Sunburst`) | ★★ Fluxo → sítio |
| P12 | Icicle | F, T | Hierarquia em faixas retangulares; lê melhor que o sunburst | H, D, C | N (`go.Icicle`) | ★★ Fluxo → sítio → atividade |
| P13 | Treemap de Voronoi | T | Hierarquia em células orgânicas | H | Df | — |
| P14 | Gráfico de parlamento | F | Assentos em semicírculo | H | Mo | ★ |
| P15 | Barras radiais empilhadas (Radial stacked bar) | F, C, T | Partes por categoria em volta do círculo | H, L | Mo (`go.Barpolar` empilhado) | ★ |
| P16 | Funil (Funnel) | F, C | Quanto sobra em cada etapa | H, C | N (`go.Funnel`) | ★★★ Ciclos que chegam a cada etapa até o início |

### 3.9 Fluxo
Mostra movimento entre estados ou etapas.

| # | Modelo (sinônimos) | Fontes | Uso recomendado | Interat. | Plotly | Uso na RT |
|---|---|---|---|---|---|---|
| X1 | Sankey horizontal | F, C, T | Volume que passa de uma etapa para outra | H, M, C | N (`go.Sankey`) | ★★★ Fluxo → sítio → turno; caminhos entre atividades |
| X2 | Sankey vertical | F | Mesmo uso, de cima para baixo | H, M | N (`orientation="v"`) | ★★ |
| X3 | Sankey radial / circular (Circular sankey) | F, T | Fluxos com retorno a etapas anteriores | H | Df | ★★ Mostraria retomografias, mas é difícil |
| X4 | Sankey em arco (Arc sankey) | T | Fluxos como arcos de largura variável | H | Df | ★ |
| X5 | Diagrama de cordas (Chord diagram) | C, T | Trocas entre grupos em ambos os sentidos | H | Df | ★ |
| X6 | Cordas em leque (Fan chord) | T | Um ponto ligado a muitos | H | Df | — |
| X7 | Handoff chart | F | O exemplo é uma narrativa em capítulos com rolagem ("scrollytelling"), em que cada gráfico passa a leitura ao seguinte; é uma técnica de layout, não um tipo de gráfico | H | Df (exige páginas ou rolagem com estado) | ★ A aba Apresentação já segue essa ideia |

### 3.10 Rede e hierarquia

| # | Modelo (sinônimos) | Fontes | Uso recomendado | Interat. | Plotly | Uso na RT |
|---|---|---|---|---|---|---|
| N1 | Rede (Network diagram/graph, Node-link diagram) | F, C | Conexões entre muitos itens | H, Z, M, C | Mo (`networkx` + `go.Scatter`) ou `dash-cytoscape` | ★★ Grafo de transições entre atividades (mineração de processos) |
| N2 | Diagrama de arcos (Arc diagram/chart; "Linear embeddings" provável) | F, C | Conexões entre itens em uma linha ordenada | H | Mo (`shapes` com curvas) | ★★ Atividades em ordem, arcos para retornos |
| N3 | Agrupamento de arestas (Edge bundling) | T | Os dois tutoriais ensinam o diagrama de cordas com arestas curvas agrupadas; é a técnica de desenho do X5, mantida como modelo de estilo | H | Df | — |
| N4 | Hive plot | F | Rede em eixos radiais | H | Df | — |
| N5 | Notabilia | F | Trajetórias que partem de um ponto comum e viram para um lado a cada evento (no exemplo, cada repetição de verso numa música); mostra sequências acumuladas | H | Mo (linhas com ângulos acumulados) | ★ Trajetória de tarefas no prazo ou em atraso por paciente |
| N6 | Árvore (Tree diagram, Dendrogram, Organisational chart, Linkage tree) | F, C | Hierarquia ou agrupamento | H, C | Mo (`ff.create_dendrogram`) ou `dash-cytoscape` | ★ |
| N7 | Árvore radial | F | Variante circular | H | Mo | — |

### 3.11 Cronograma e processo

| # | Modelo (sinônimos) | Fontes | Uso recomendado | Interat. | Plotly | Uso na RT |
|---|---|---|---|---|---|---|
| S1 | Gantt (Gantt chart; "Timetable" provável) | F, C | Duração e sobreposição de tarefas | H, Z, C | N (`px.timeline`) | ★★★ Jornada do paciente (já implementado) |
| S2 | Linha do tempo (Timeline) | F | Eventos pontuais em ordem | H, Z | Mo | ★★★ Marcos do ciclo: TC, contorno, planejamento, início |
| S3 | Linha do tempo curva | F | Muitos eventos em espaço curto | H | Df | ★ |
| S4 | Linha do tempo em círculos (Timeline circles, Half circle timeline) | F, T | Duração como semicírculo | H | Mo (`shapes` em arco) | ★ |
| S5 | Vitória-derrota / código de barras (Win loss, Barcode) | F | Sim ou não por dia | H | Mo (`go.Bar` ±1 ou faixa de heatmap) | ★★ Dias em que a ocupação ficou na meta |

### 3.12 Geográfico
Os dados atuais não têm município nem endereço. Os modelos só seriam úteis se o hospital fornecer o município de residência, por exemplo para mostrar deslocamento dos pacientes.

| # | Modelo (sinônimos) | Fontes | Uso recomendado | Interat. | Plotly | Uso na RT |
|---|---|---|---|---|---|---|
| G1 | Coroplético (Choropleth, Filled map) | F, C | Taxa por região | H, Z, C | N (`go.Choropleth`, `go.Choroplethmap`) | — |
| G2 | Mapa de bolhas (Bubble map) | F, C | Volume por local | H, Z, C | N (`go.Scattermap`) | — |
| G3 | Mapa hexagonal / mosaico (Hexmap, Hex tile map, Grid/Tile map) | F, C, T | Regiões com área igual | H, C | Mo | — |
| G4 | Hexágonos por latitude e longitude | F | Densidade de pontos agregada | H, Z | N (`ff.create_hexbin_map`) | — |
| G5 | Mapa com camada de fundo (Mapbox) | F | Estilo do mapa base | H, Z | N (MapLibre no Plotly 6) | — |
| G6 | Mapa de densidade (Density marks) | F | Concentração contínua | H, Z | N (`go.Densitymap`) | — |
| G7 | Cartograma | F, C | Região deformada pelo valor | H | Df | — |
| G8 | Mapa de conexões (MakeLine, Connection, Flow, Path, Link, Ray, Spider map, Hub and spoke, Network map) | F, C | Trajetos entre origem e destino | H, Z | Mo (`go.Scattergeo` com linhas) | — Origem do paciente até o GHC, se houver dado |

### 3.13 Texto e técnicas de layout

| # | Modelo (sinônimos) | Fontes | Uso recomendado | Interat. | Plotly | Uso na RT |
|---|---|---|---|---|---|---|
| W1 | Nuvem de palavras (Word cloud, Tag cloud) | F, C | Frequência de termos; imprecisa | H | Df (biblioteca `wordcloud` gera imagem) | — Não há texto livre nos dados |
| W2 | Pequenos múltiplos (Small multiples, Panel charts, Trellis) | F, C | Repetir o mesmo gráfico por categoria com eixos iguais | H, Z, L | N (`facet_col`, `facet_row`) | ★★★ Uma linha de tendência por sítio ou por fluxo |

**Total:** 132 modelos únicos (131 da primeira versão e o V13 Icicle de desvio). Destes, 59 são nativos no Plotly, 52 exigem montagem e 21 são difíceis. Nos dados de radioterapia, 42 têm uso alto e 37 uso médio.

### 3.14 Correções após abrir os exemplos

| Modelo | Antes | Depois de abrir o exemplo |
|---|---|---|
| D13 Plum pudding | Pontos numa escala | Waffle circular de 100 unidades; pertence a Composição (variante do P8) |
| L3 Dispersão com totais | Não verificado | Pontos individuais e um marcador agregado por grupo |
| N5 Notabilia | Ramificações de discussões | Trajetórias que viram a cada evento; montagem possível |
| X7 Handoff | Passagens entre participantes | Narrativa em capítulos com rolagem; técnica de layout |
| N3 Edge bundling | Rede densa | Desenho do diagrama de cordas (X5) com arestas agrupadas |
| M19 Polígono radial com abas | Variante do radar | Anel de abas iguais com cor pelo valor |
| M22 Formas | Ícones como marcador | Técnica de imagens próprias como marca |
| V13 Icicle de desvio | Não existia | Modelo novo, vindo do tutorial da Rasztik (L. Betzendahl) |

## 4. Estratégia de implementação

### 4.1 Do tipo de informação para o gráfico
Antes de escolher o gráfico, a tela deve dizer qual pergunta responde. A tabela abaixo é a regra de decisão proposta para o dashboard.

| O que se quer mostrar | Primeira escolha | Alternativa | Evitar |
|---|---|---|---|
| Um número contra a meta | K1 Bullet | K4 Barra de progresso | K2 Gauge |
| Comparar categorias | M1/M2 Barras | M9 Pirulito, M10 Pontos | M18 Radar, M11 Bolhas agrupadas |
| Antes e depois | R4 Inclinação | V1 Haltere, V5 Setas | Duas pizzas |
| Desvio da meta | V3 Barras divergentes | V13 Icicle de desvio, L4 Dispersão com faixas | |
| Tendência mensal | T1 Linhas | M2 Colunas (poucos meses) | T2 Linha curva |
| Estabilidade do processo | V11 Controle | V10 Bollinger | |
| Distribuição de tempos | D4 Box + D6 Jitter | D5 Violino, D2 Densidade | Só a média |
| Composição simples | P3/P4 Empilhadas | P2 Rosca (≤ 3 partes) | P1 Pizza com muitas fatias |
| Capacidade do dia | P8 Waffle de 60 vagas | M7 Barra dentro de barra | |
| Hierarquia | P12 Icicle | P10 Treemap | P13 Voronoi |
| Etapas e perdas | P16 Funil | X1 Sankey | X5 Cordas |
| Jornada de um paciente | S1 Gantt | S2 Linha do tempo | |
| Padrão por dia ou hora | T16 Calendário, L7 Mapa de calor | M14 Colunas radiais | T18 Coxcomb |
| Muitas categorias ao mesmo tempo | W2 Pequenos múltiplos | T7 Sparklines | Uma linha com 15 cores |

### 4.2 Perguntas de negócio do projeto e gráfico sugerido

| Pergunta (docs/perguntas-negocio.md) | Gráfico principal | Complemento | Interatividade sugerida |
|---|---|---|---|
| 1. Evolução dos planejamentos concluídos | T1 Linhas por mês | K1 Bullet do mês contra a meta | R e C (clicar no mês filtra as demais telas) |
| 2. Distribuição entre Urgência, Prioridade e Eletivo | P4 Colunas 100% por mês | P2 Rosca do período | L e C |
| 3. Atividades com maior tempo | M9 Pirulito ordenado | R7 Pareto | C (abre a distribuição da atividade) |
| 4. Duração por fluxo | D4 Box com D6 Jitter | D5 Violino | S (selecionar pacientes extremos) |
| 5. Atividades com maior variabilidade | V2 Faixa P25–P75 por atividade | D8 Ridgeline | H com mediana e IQR |
| 6. Evolução do tempo médio por mês | V11 Controle | R4 Inclinação (início × fim) | Z, R |
| 7. % de tarefas no prazo | K1 Bullet | P8 Waffle ou K3 Donut de progresso | H |
| 8. Maiores atrasos contra o vencimento | V3 Barras divergentes | L4 Dispersão com faixa da meta | C, S |
| 9. Espera entre check-in e atendimento | D1 Histograma | L7 Mapa de calor hora × dia | S |
| 10. Duração por tipo de tratamento | M10 Pontos de Cleveland | D4 Box por sítio | C |
| Requisito-chave: tempo entre atividades por paciente | S1 Gantt do ciclo | X1 Sankey ou N1 Rede de transições | C (clicar no paciente abre a jornada) |
| Ocupação do acelerador (meta 80–85%) | T16 Calendário diário | P8 Waffle do dia, V6/M7 | C |
| Dia × noite | M6 Barras agrupadas | V4 Pirâmide por sítio | L |

### 4.3 Fases

**Fase 1, gráficos nativos de alto valor (1 a 2 dias).** O dashboard já usa barras, box plot, mapa de calor, Gantt, cascata, histograma, linhas, bullet e controle. Os próximos são todos nativos: D5 Violino, D6 Jitter sobre o box, R4 Inclinação, P4 Colunas 100%, P16 Funil, X1 Sankey, T5 Degraus para ciclos em aberto e W2 Pequenos múltiplos. Cada um é uma função nova em `viz/figures.py`.

**Fase 2, gráficos por montagem (3 a 4 dias).** M9 Pirulito, M7 Barra dentro de barra, V1 Haltere, V2 Faixa P25–P75, V3 Divergentes, V5 Setas, V10 Bollinger, R7 Pareto, T16 Calendário, P8 Waffle de vagas, D9 Histograma de unidades e T7/T8 Sparklines em tabela. Cada um vira uma função com teste próprio.

**Fase 3, opcionais e exploratórios.** L5 Coordenadas paralelas, N1 Rede de transições com `dash-cytoscape`, L6 Ternário e X3 Sankey circular para mostrar retomografias. Só entram se responderem a uma pergunta que a banca ou a gestão fizer.

**Fora do escopo.** Os 23 modelos difíceis e os geográficos, enquanto não houver dados de localização. Os radiais (M12, M13, R3, T12–T14, D10, L9, P15) também ficam fora, porque comparar ângulos e arcos é menos preciso que comparar comprimentos.

### 4.4 Organização no código
1. **Uma função por modelo.** Em `viz/`, cada modelo recebe um DataFrame "tidy" e parâmetros simples e devolve `go.Figure`. Os nomes seguem os códigos deste catálogo (por exemplo `pirulito()`, `haltere()`, `waffle_vagas()`), o que facilita achar o gráfico a partir do documento.
2. **Registro por tipo de informação.** Um dicionário em `viz/catalogo.py` liga cada tipo (comparação, distribuição etc.) às funções disponíveis, no mesmo padrão do `metrics/registry.py`. A aba Sobre pode listar esse registro como ficha técnica.
3. **Interatividade padrão.** Todo gráfico tem dica em português com unidade (`hovertemplate`), e o clique publica a categoria em um `dcc.Store` que as outras abas leem para o filtro cruzado. Seleção por laço fica só nos gráficos de pontos.
4. **Acessibilidade.** Hachura (`marker.pattern`) como segunda codificação para os três fluxos; tema único em `viz/theme.py`; o texto alternativo e a tabela de dados que o `a11y.js` já gera para cada figura.
5. **Testes.** Para cada função, um teste verifica tipo e quantidade de traces e que um DataFrame vazio devolve a figura `vazio()`.

### 4.5 Distribuição dos gráficos no dashboard (implementada em 06/11)

Regra adotada: a visualização 1, mostrada por padrão, é a de maior interatividade (dica com unidade, zoom, clique na legenda, seleção por laço e linhas-guia que seguem o cursor). As demais ficam no botão ⇄ de cada cartão, para leitura ou apresentação. Todo gráfico tem pelo menos três visualizações. As conversões automáticas são feitas no navegador (`assets/a11y.js`); onde elas não servem, a figura já sai do servidor com as alternativas prontas (`viz/alternativas.py`).

| Aba | Gráfico (id) | Padrão | Alternativas no ⇄ | Interat. do padrão |
|---|---|---|---|---|
| Visão Geral | Pacientes novos (`g-vg-res-novos`) | T1 Linhas | M2 Colunas, T3 Área, M10 Pontos, T5 Degraus | H, Z, R, C |
| Visão Geral | Planejamentos por fluxo (`g-vg-res-fluxo`) | P3 Barras empilhadas | T1 Linhas, M6 Barras, T3 Área, M10 Pontos, T5 Degraus | H, Z, L, C |
| Visão Geral | Sessões dia × noite (`g-vg-res-turno`) | P3 Barras empilhadas | T1, M6, T3, M10, T5 | H, Z, L, C |
| Visão Geral | Tratados por sítio (`g-vg-res-sitio`) | M1 Barras | M9 Pirulito, M10 Pontos, M2 Colunas | H, Z, C |
| KPIs | Ocupação do acelerador (`g-sc-ocupacao`) | K1 Bullet como barra com dica | K1 Bullet (indicador), K2 Velocímetro | H |
| KPIs | Tarefas no prazo (`g-sc-prazo`) | K1 Bullet como barra com dica | K1 Bullet (indicador), K2 Velocímetro | H |
| KPIs | Meses na meta (`g-sc-winloss`) | L7 Grade sim/não (mapa de calor) | S5 Vitória-derrota, P3 Barras empilhadas | H, Z |
| KPIs | 11 indicadores mensais (`g-vg-*`) | T1 Linhas ou P3/P4 Empilhadas | T1, M2/M6, T3 Área, M10 Pontos, T5 Degraus | H, Z, L, R, C |
| KPIs | Sparklines da tabela (`sc-tabela`) | T7 Sparklines | Sem ⇄: são miniaturas estáticas dentro da tabela; o gráfico completo de cada indicador está logo abaixo | — |
| Eficácia vs Eficiência | Ocupação, inícios, tempos (`g-al-ocupacao`, `g-prod-inicios`, `g-al-duracao`, `g-al-sessoes-trat`, `g-al-espera-hora`) | T1 Linhas | M2 Colunas, T3 Área, M10 Pontos, T5 Degraus | H, Z, R, C |
| Eficácia vs Eficiência | Planejamentos por fluxo (`g-prod-fluxo`) | M6 Barras agrupadas | T1, P3, T3, M10, T5 | H, Z, L, C |
| Eficácia vs Eficiência | Composição por fluxo (`g-nv-waffle`) | P4 Barra 100% | P8 Waffle, P2 Rosca | H, L |
| Eficácia vs Eficiência | Por sítio (`g-prod-sitio`, `g-al-duracao-sitio`) | M1 Barras | M9 Pirulito, M10 Pontos, M2 Colunas | H, Z, C |
| Eficácia vs Eficiência | Espera por sítio (`g-nv-ridgeline`) | D5 Violino (D8 Ridgeline) | D4 Caixa, D4+D6 Caixa com pontos, D7 Pontos | H, Z, L |
| Eficácia vs Eficiência | Espera até o atendimento (`g-al-espera`) | D1 Histograma | D4 Caixa, D5 Violino, D2 Acumulada | H, Z, S |
| Eficácia vs Eficiência | Dia × noite por sítio (`g-nv-barbell`) | V1 Haltere | M6 Barras agrupadas, M2 Colunas | H, Z, C |
| Resultado vs Tendência | Sessões por turno (`g-prod-turno`) | P3 Barras empilhadas | T1, M6, T3, M10, T5 | H, Z, L, C |
| Resultado vs Tendência | Índice base 100 (`g-nv-indice`) | T6 Índice | M2, T3, M10, T5 | H, Z, L, R |
| Resultado vs Tendência | Calendário (`g-nv-calendario`) | T16 Calendário | L2 Bolhas, T1 Linhas | H, Z, C |
| Resultado vs Tendência | Funil do ciclo (`g-am-funnel`) | P16 Funil com % do início e da etapa anterior | M1 Barras com conversão, V8 Cascata de perdas | H, C |
| Resultado vs Tendência | Ciclos em aberto (`g-nv-wip`) | T1 Linhas | M2, T3, M10, T5 | H, Z, R |
| Resultado vs Tendência | Entradas e saídas (`g-nv-entradas`) | M2 Colunas com linha | T1, T3, M10, T5 | H, Z, L |
| Resultado vs Tendência | Idade dos ciclos (`g-nv-idade`) | D6 Pontos com dispersão | D4 Caixa, D5 Violino, D4+D6 | H, Z, S, C |
| Processos | Fluxo de valor (`g-nv-fluxo-valor`) | P3 Barras empilhadas | M6 Barras agrupadas, M10 Pontos, M2 Colunas | H, Z, L |
| Processos | Controle (`g-nv-controle`) | V11 Controle | D7 Pontos, T5 Degraus | H, Z, R, S |
| Processos | Pareto (`g-nv-pareto`) | R7 Pareto | M9 Pirulito, M10 Pontos, M2 Colunas | H, Z, C |
| Processos | Faixa de pontos (`g-nv-dotstrip`) | D7 Faixa de pontos | D4 Caixa, D5 Violino, D4+D6 | H, Z, S |
| Processos | Atividades (`g-at-barras`) | M1 Barras com ponto | M9, M10, M2 | H, Z, C |
| Processos | Duração por atividade (`g-at-box`) | D4 Caixa | D5 Violino, D4+D6, D7 Pontos | H, Z, S |
| Processos | Tendência da atividade (`g-at-tendencia`) | T1 Linhas | M2, T3, M10, T5 | H, Z, L, R |
| Processos | Atividade × mês (`g-at-heatmap`) | L7 Mapa de calor | L2 Bolhas, T1 Linhas | H, Z |
| Processos | Pirulito (`g-nv-lollipop`) | M10/M9 Pontos e hastes | M1 Barras, M9 Pirulito, M2 Colunas | H, Z, C |
| Processos | Dispersão por faceta (`g-am-scatter-facetas`) | L1 Dispersão em W2 Pequenos múltiplos | D12 Densidade, contornos | H, Z, S, C |
| Jornada do Paciente | Linha do ciclo (`g-jo-gantt`) | S1 Gantt | S2 Marcos do ciclo, P3 Espera e execução (horas) | H, Z, C |
| Jornada do Paciente | Composição dos dias (`g-jo-cascata`) | V9 Cascata conectada | T5 Degraus do acumulado, M1 Barras por atividade | H, Z |
| Jornada do Paciente | Paciente × fluxo (`g-jo-comparacao`) | L4 Pontos com faixa P25–P75 | V3 Desvio da mediana, V2 Pontos e faixa | H, Z, L |

Nota: a aba Apresentação (`g-ap-*`) reaproveita as mesmas figuras da Visão Geral e herda as mesmas alternativas.

## 5. Referências
- Kevin Flerlage, *The Tableau Chart Catalog*, Tableau Public.
- Josh Weyburne, *Tableau Viz Cookbook*, Tableau Public.
- Lilla Rasztik, *Tutorials of visualizations*, Tableau Public.
- Adedamola Ladipo, *Chart Suggestions Guide*, Tableau Public, a partir de Andrew Abela, *Chart Suggestions — A Thought-Starter* (2009).
- Financial Times, [Visual Vocabulary](https://github.com/ft-interactive/visual-vocabulary).
- [Data Viz Catalogue](https://datavizcatalogue.com), para os sinônimos do Cookbook.
- [Documentação do Plotly para Python](https://plotly.com/python/) e [Dash](https://dash.plotly.com/).

## Apêndice A. Exemplos abertos (link e descrição)

Um exemplo por linha, na ordem de cada painel. A descrição é a do autor, encurtada quando longa; ela mostra o caso de uso real que inspirou o gráfico. O guia G (Ladipo) não tem exemplos externos, só os 20 desenhos esquemáticos.

### A.1 Flerlage, The Tableau Chart Catalog

| Gráfico | Autor | Exemplo | Descrição |
|---|---|---|---|
| Arc Diagram | James Smith | [Lewis Hamilton F1 Career](https://public.tableau.com/app/profile/sports.chord/viz/HamiltonF1/HamiltonVertical) | Hamilton F1 |
| Area Chart | Bo McCready | [Film Genre Popularity - 1910-2018](https://public.tableau.com/app/profile/bo.mccready8742/viz/FilmGenrePopularity-1910-2018/GenreRelativePopularityfixedrange) |  |
| Area Chart (Stacked) | Kevin Flerlage | [IronViz - The Day the Music Died](https://public.tableau.com/app/profile/kevin.flerlage/viz/IronViz-TheDaytheMusicDied/TheDaytheMusicDied) | IronViz - The Day the Music Died #IronViz |
| Bar Chart | Bridget Cogley | [Metric Analysis Alt](https://public.tableau.com/app/profile/bridget/viz/MetricAnalysisAlt/MetricsAlt) | Response to https://www.tableau.com/about/blog/2015/12/heres-our-key-metrics-dashboard-revamped-47658 |
| Bar Chart (Stacked) | Lorna Eden | [FRIENDS THROUGH THE TRANSCRIPTS #IRONVIZ](https://public.tableau.com/app/profile/lorna.eden/viz/FRIENDSTHROUGHTHETRANSCRIPTSIRONVIZ/Page23) |  |
| Bar in Bar Chart | Pablo Gomez | [Can Tableau Public help you get your next job?](https://public.tableau.com/app/profile/pablolgomez/viz/CanTableauPublichelpyougetyournextjob/Dashboard1) | Can Tableau Public help you get your next job? ... viz used as part of my presentation at #TinyTableauTalks |
| Bar (Outline) | Eva Murray | [Fatal Bear Attacks](https://public.tableau.com/app/profile/eva.murray/viz/FatalBearAttacks/Bearattacks) |  |
| Barbell Chart | Mark Bradbourne | [Most Important Characteristics #MakeoverMonday](https://public.tableau.com/app/profile/mark.bradbourne/viz/MostImportantCharacteristics/MostImportantCharacteristics) | Most Important Characteristics |
| Box  & Whisker Plot | Joshua Smith | [Pasture and Crop: The Ways We Farm Our Land](https://public.tableau.com/app/profile/datajackalope/viz/IronViz_15561510177280/Dashboard12) | #IronViz, #Agriculture, #IronViz2019 |
| Bullet Graph | Daniel Benevento | [tutorial](https://public.tableau.com/shared/QSJWHRKRW?:display_count=yes&:origin=viz_share_link) |  |
| Bump Chart | Rodrigo Calloni | [The State of USA Population 2016-2056 / MakeoverMonday](https://public.tableau.com/app/profile/calloni/viz/TheStateofUSAPopulation2016-2056MakeoverMonday/TheStateofUSAPopulation2016-2056) |  |
| Bump Chart (Curvy) | Rody Zakovich | [The Untangling of Color Popularity among New Cars in North America](https://public.tableau.com/app/profile/rody.zakovich/viz/TheUntanglingofColorPopularityamongNewCarsinNorthAmerica/TheUntanglingofColorPopularityforNewCars) |  |
| Bump Chart (Curvy Radial) | Alexander Varlamov | [Formula 1 2018 World Championship. Results](https://public.tableau.com/app/profile/alexandervar/viz/Formula12018WorldChampionship_Results/Formula12018) | #SportsVizSunday |
| Calendar View | Rody Zakovich | [Trump's 2017 Presidential Golf Outings](https://public.tableau.com/app/profile/rody.zakovich/viz/Trumps2017PresidentialGolfOutings/Trumps2017PresidentialGolfOutings) |  |
| Cleveland Dot Plot | Anna Foard | [Remembering Aretha](https://public.tableau.com/app/profile/statsninja/viz/RememberingAretha/Dashboard1) | A tribute: My aunt taught me how to feel the music. She also showed me how to be strong. I lost her suddenly a few weeks before we lost Aretha. |
| Comet Chart | Steve Wexler | [Comet_DataRevelations_2019.1](https://public.tableau.com/app/profile/swexler/viz/Comet_DataRevelations_2019_1/CometChartGradient) |  |
| Compound Pictogram | Luke Stanke | [Workout Wednesday - Week 15: Total Products By Sub-Category](https://public.tableau.com/app/profile/stanke/viz/WorkoutWednesday-Week15TotalProductsBySub-Category/Jedi) |  |
| Coxcomb Chart | Harpreet Ghuman | [Diversity in Tech #Vizforsocialgood](https://public.tableau.com/app/profile/harpreetghuman/viz/DataDiversity/DiversityinTech) | A visual representation of the racial and gender distribution in the top 100 tech firms. |
| Donut Chart | Pradeep Kumar | [U.S. Farms and Farmers Under Threat](https://public.tableau.com/app/profile/pradeepkumar.g/viz/U_S_FarmsandFarmersUnderThreat/IronViz2019) | U.S. Farms and Farmers Under Threat / #IronViz2019 / #Agriculture / #Top5 / #pradeepgk |
| Donut (Radial Progress Bar) | Joshua Preston | [Sleep Time in the U.S. 2003-2017](https://public.tableau.com/app/profile/joshpreston/viz/sleepytime/Dashboard1) | Sleep Time in the U.S. 2003-2017 #MakeoverMonday |
| Dot Strip Plot | Lindsay Betzendahl | [Medicaid & CHIP Scorecard (dot strip plots)](https://public.tableau.com/app/profile/lindsay.betzendahl/viz/MedicaidCHIPScorecarddotstripplots/Measuresdotstrip) |  |
| Filled Shaped Chart | Kevin Flerlage | [The African Water Crisis](https://public.tableau.com/app/profile/kevin.flerlage/viz/TheAfricanWaterCrisis_1/WaterDashboard) | Water scarcity continues to be one of the world's largest problems. Without access to clean water, residents are at constant risk of disease. |
| Funnel Chart | Adam Crahen | [Marketing Funnel](https://public.tableau.com/views/MarketingFunnel_0/Marketing?:embed=y&:display_count=yes&:showviz=no#1) |  |
| Gantt Chart | Robert Rouse | [Genesis Timeline](https://public.tableau.com/app/profile/robertrouse/viz/GenesisGenealogy/GenesisTimelinefromAdamtoAbraham) | How do we understand the timeline of Genesis? Laying out genealogies on a timeline offers the answer. #bible |
| Gauge | Adam McCann | [KPI Options](https://public.tableau.com/app/profile/adam.e.mccann/viz/KPIOptions/AllDaKPIs) |  |
| Handoff Chart | Ludovic Tavernier | [the amazing letter e](https://public.tableau.com/app/profile/ludovic.tavernier/viz/theamazinglettere/theamazinglettere) |  |
| Highlight Table / Heat Map | Andy Kriebel | [Most Common Birthdays](https://public.tableau.com/app/profile/andy.kriebel/viz/MostCommonBirthdays/MostCommonBirthdays) |  |
| Highlight Table (Radial) | Ellen Blackburn | [International Human Rights Instruments #VOTD](https://public.tableau.com/app/profile/ellen4268/viz/InternationalHumanRightsInstruments/Dashboard-Public) | Create your own radial heatmap with the help of this blog from Alex Jones: http://www.weblogaboutdata.com/kick-ass-radial-heatmap-in-alteryx/ |
| Histogram | Dinushki DeLivera | [The awesome women employed by City of Cincinnati](https://public.tableau.com/app/profile/dinushki.de.livera/viz/TheawsomewomenemployedbytheCityofCincinnati/WomenoftheCity) | The awsome women employed by the City of Cincinnati |
| Histogram (Marginal) | Jacob Osulfka | [2017 MLB Pitcher Heatmaps](https://public.tableau.com/app/profile/datavizard/viz/2017MLBPitcherHeatmaps/MLB) |  |
| Hive Plot | Chris DeMartini | [Hive Plot 2.0](https://public.tableau.com/app/profile/vizde7382/viz/HivePlot2_0/ZenHivePlot) |  |
| Horizon Chart | Joe Mako | [Unemployment Horizion Chart - Gallery](https://public.tableau.com/app/profile/joe.mako/viz/UnemploymentHorizionChart-Gallery_4/HorizonChart) |  |
| Icicle Chart | Adam McCann | [Icicle Chart](https://public.tableau.com/app/profile/adam.e.mccann/viz/IcicleChart/IcicleChart) |  |
| Index Chart | Jeff Shaffer | [The Billion Views Club](https://public.tableau.com/app/profile/jeffrey.shaffer/viz/TheBillionViewsClub/ABillionViews) | The Billion Views Club #VOTD |
| Jitter Plot | Andy Cotgreave | [Goal Quarter Finals](https://public.tableau.com/app/profile/acotgreave.tableausoftware.com/viz/GoalQuarterFinals/Goooaaaaalinteractive) |  |
| Joy / Ridgeline Plot | David Velleca | [US Recorded Music Revenue by Format - 1973 to 2018](https://public.tableau.com/app/profile/david.c.velleca/viz/USRecordedMusicRevenuebyFormat-1973to2018/USRecordedMusicRevenuebyFormat-1973to2018) | US Recorded Music Revenue by Format - 1973 to 2018 Viz of the Day & Week on March 13, 2019 #ThrowbackDataThursday |
| Jump Plot | Chris DeMartini | [Jump Plot Examples](https://public.tableau.com/app/profile/vizde7382/viz/JumpPlotExamples/DaysBetweenHRDash) |  |
| Line Chart | Jeff Plattner | [#MakeoverMonday 2019-22](https://public.tableau.com/app/profile/jeff.plattner4532/viz/MakeoverMonday2019-22/Dashboard1) |  |
| Lollipop Chart | Sarah Bartlett | [The Secret of Success](https://public.tableau.com/app/profile/sarah.bartlett/viz/TheSecretofSuccess_0/TheSecretofSuccess) | The Secret of Success #makeovermonday 2017 Week 13 |
| Map (Choropleth) | Samo Drole | [Global Measles Cases](https://public.tableau.com/app/profile/samodrole/viz/WHOGlobalMeaslesCasesProjectHealthViz2019March/Measles) | WHO Global Measles Cases for #ProjectHealthViz/March 2019 |
| Map (with Bubbles) | Anya A'Hearn | [Those SF Giants Freaks that Shop at SuperStore](https://public.tableau.com/app/profile/anya./viz/ThoseSFGiantsFreaksthatShopatSuperStore/ThoseSFGiantsFreaksthatShopatSuperStore) |  |
| Map (Hexmap) | Matt Chambers | [Body Camera Laws](https://public.tableau.com/app/profile/matt.chambers/viz/BodyCameraLaws/BodyCameraLaws) |  |
| Map (Lat Long Hex Bins) | Matt Chambers | [Tornado Density - Alternate Hexbins](https://public.tableau.com/app/profile/matt.chambers/viz/TornadoDensity-AlternateHexbins/TornadoDensity-Alternatehexbins) |  |
| Map (Mapbox) | Allan Walker | [CinciHeroin](https://public.tableau.com/app/profile/allan.walker/viz/CinciHeroin/CincinattiHeroinIncidents) |  |
| Map (with Density Marks) | Sarah Bartlett | [Rat Sightings in NYC](https://public.tableau.com/app/profile/sarah.bartlett/viz/RatSightingsinNYC_15598096824670/RatSightingsinNYC) | Rat Sightings in NYC #MakeoverMonday 2018 Week 27 |
| Map (Cartogram) | Rob Radburn | [A World Map of Carbon Emissions](https://public.tableau.com/app/profile/robradburn/viz/CO2_124/CO2) | CO2 |
| Map (with MakeLine) | Anna Dzikowska | [#IronViz Europe 2019](https://public.tableau.com/app/profile/anna.h.dzikowska/viz/AnnaDzikowska/Dashboard1) | Created in 20 min live on Stge AnnaDzikowska #IronViz Europe 2019 Dashboard Eurovision Dataset |
| Marimekko Chart | Jonathan Drummey | [Marimekko/mosaic plot](https://public.tableau.com/app/profile/jonathan.drummey/viz/marimekko-mosaicplot/MarimekkowGT) | Workbook for the Tableau blog posts on Marimekko charts. |
| Mirrored Distribution | Sam Parsons | [viz](https://public.tableau.com/app/profile/sparsonsdataviz/viz/SOWINGSEEDSINAMERICAIronViz2019Feeder1/SOWINGSEEDS) |  |
| Network Diagram | Seffana Mohamed - Ajaz | [Marvel Cinematic Universe Network](https://public.tableau.com/app/profile/seffana.mohamed.ajaz/viz/MarvelCinematicUniverseNetwork/CharacterNetwork) | Originally released on 9th May 2019. Marvel Cinematic Universe Network #MCU #Marvel #VOTD Network chart built using Ben Moss' Plot Network macro in #alteryx. bit.ly/2mawXhM |
| Notabilia Chart | Chris Love | [Yeah Yeah Yeah  Lyrical Repetition in Popular Music Loops](https://public.tableau.com/app/profile/chrisluv/viz/YeahYeahYeahLyricalRepetitioninPopularMusicLoops/LyricalRepetition) | Yeah Yeah Yeah Lyrical Repetition in Popular Music Loops |
| Packed Bubbles | Zach Bowders: | [Genre](https://public.tableau.com/app/profile/zach.bowders/viz/Genre_15560692279410/Genre) |  |
| Panel Charts / Small Multiples | Andy Kriebel | [NHL Attendance](https://public.tableau.com/app/profile/andy.kriebel/viz/NHLAttendance_3/MM1) | #MakeoverMonday: Team by Team NHL Attendance |
| Parallel Coordinates | Joe Mako | [Parallel Coordinates Example](https://public.tableau.com/app/profile/joe.mako/viz/ParallelCoordinatesExample/ParallelCoordinatesExample) | Two examples, a simple and complex |
| Pareto Chart | Sean Miller | [What % of States Accounted for 80% of Sales](https://public.tableau.com/app/profile/kcmillersean/viz/ParetoforKevin/Dashboard1) | Pareto for Kevin |
| Parliament Chart | Alexander Varlamov | [Women in the House of Representatives](https://public.tableau.com/app/profile/alexandervar/viz/WomenintheHouseofRepresentatives_2/HouseofRepresentatives) | #makeovermonday |
| Petal Chart | Neil Richards | [Diversity in Technology](https://public.tableau.com/app/profile/neil.richards/viz/deartech/Dashboard2) | Visualising data from @deartechpeople for #VizForSocialGood - examining diversity profile of leadership roles in 100 top tech companies |
| Petal Chart (No Polygons) | Sarah Burnett | [Cost of a night out](https://public.tableau.com/app/profile/sarah.burnett/viz/Costofanightout_0/Costofnightout) | Night Out Makeover Monday 2018 week 48 Polygons |
| Pie Chart | Eva Murray | [Mortgage Spending USA](https://public.tableau.com/app/profile/eva.murray/viz/MortgageSpendingUSA/Mortgage) | Mortgage Spending USA #MakeoverMonday |
| Population Pyramid | Sean Miller | [Poppin' Pyramids](https://public.tableau.com/app/profile/kcmillersean/viz/Book4_15556982970350/PoppinPyramids) | How to make your population pyramids POP! in Tableau #VizOfTheDay |
| Progress Bar | Ryan Sleeper | [BLOCKBUSTER](https://public.tableau.com/app/profile/osmguy/viz/BLOCKBUSTER/BLOCKBUSTER) | BLOCKBUSTER: Analyzing the 10 Highest Grossing Actors of All Time |
| Radar Chart | Ellen Blackburn | [Which Sport is the Toughest?](https://public.tableau.com/app/profile/ellen4268/viz/WhichSportistheToughest/sheet1) |  |
| Radial Bar Chart | Kasia Gasiewska-Holc | [US Baby Names (#VOTD)](https://public.tableau.com/app/profile/kasia.gasiewska.holc/viz/USBabyNamesVOTD/BabyNames) | US Baby Names (VOTD) |
| Radial Bar Chart (Stacked) | Jennifer Dawes | [Elton John - Music That Travels The World  / #IronViz 2019](https://public.tableau.com/app/profile/jennifer.dawes/viz/EltonJohn-MusicThatTravelstheWorld/EltonJohn) | Elton John - Music That Travels the World |
| Radial Stacked Histogram | Ken Flerlage | [Wind Roses Single City](https://public.tableau.com/app/profile/ken.flerlage/viz/WindRosesSingleCity/WindRose) |  |
| Radial Line Chart | Kevin Flerlage | [STREAKING: 2018 MLB Wins, Losses, & Streaks](https://public.tableau.com/app/profile/kevin.flerlage/viz/STREAKING2018MLBWinsLossesStreaks/ALWest) |  |
| Radial Stacked Area Chart | Ken Flerlage | [US Births by Day](https://public.tableau.com/app/profile/ken.flerlage/viz/USBirthsbyDay/Births) |  |
| Radial Time Series Chart | Lindsay Betzendahl | [Influenza Season - #MakeoverMonday](https://public.tableau.com/app/profile/lindsay.betzendahl/viz/InfluenzaSeason-MakeoverMonday/Influenza) |  |
| Sankey Diagram (Horizontal) | Jeff Shaffer | [Myers Briggs Frequency](https://public.tableau.com/app/profile/jeffrey.shaffer/viz/MyersBriggsFrequency/MyersBriggsFrequency) |  |
| Sankey Diagram (Vertical) | Ivett Kovacs | [Job Application Process](https://public.tableau.com/app/profile/yvette/viz/JobApplicationProcess_15520359515640/JobApplicationFlow) | Originally Published on: https://tabsoft.co/2EUMXeO |
| Sankey Diagram (Radial) | Luke Stanke | [Sankey Chord Diagram](https://public.tableau.com/app/profile/stanke/viz/SankeyChordDiagram/SankeyChordDiagram) |  |
| Scatter Plot | Lindsey Poulter | [Makeover Monday: Hours Americans Need to Work to Pay Their Mortgage](https://public.tableau.com/app/profile/lindsey.poulter8872/viz/MakeoverMondayHoursAmericansNeedtoWorktoPayTheirMortgage/MMMortgages) |  |
| Scatter Plot (With Size) | Adam McCann | [SNL](https://public.tableau.com/app/profile/adam.e.mccann/viz/SNL_15584125948520/SNLHosts) |  |
| Scatter Plot (With Totals) | Mike Cisneros | [Winning at Every Cost](https://public.tableau.com/app/profile/mikevizneros/viz/WinningatEveryCost/WinningatEveryCost) | A #MakeoverMonday showing the costs of a win in the NBA per franchise since 1990-91, overall and for individual seasons. |
| Scatter Plot (with Ref Bands) | Steve Fenn | [All-Time MLS Players](https://public.tableau.com/app/profile/fennsk/viz/All-TimeMLSPlayers/ScoringShotsvsGoals) |  |
| Scatter Plot (Hexbin) | Ken Flerlage | [Hexbin Scatterplot](https://public.tableau.com/app/profile/ken.flerlage/viz/HexbinScatterplot/HexScatterplot) |  |
| Slope Graph | Ben Jones | [Slopegraphs](https://public.tableau.com/app/profile/ben.jones/viz/Slopegraphs/Slopegraphs) |  |
| Slope Graph (Sankey Style) | Jeff Shaffer | [State of America Rankings](https://public.tableau.com/app/profile/jeffrey.shaffer/viz/StateofAmericaRankings/TableauVersion) | State of America Rankings - this was the first viz done in Tableau using the Sigmoid function to create the curvy lines. #sankey #slopegraph |
| Slope Graph (Curvy) | Hesham Eissa | [How do the 50 states rank?](https://public.tableau.com/app/profile/hesham3827/viz/HOWDOTHE50STATESRANKMakeoverMonday2019W15/Dashboard3) | HOW DO THE 50 STATES RANK? — #MakeoverMonday 2019W15 |
| Sparklines | Spencer Baucke | [NFL Combine](https://public.tableau.com/app/profile/spencer.baucke/viz/NFLCombine_1/NFLCombine) | NFL Combine / #SportsVizSunday |
| Step Chart | Chantilly Jaggernauth | [NHL Game Attendance](https://public.tableau.com/app/profile/chantilly.jaggernauth/viz/NHLGameAttendance_0/NHLGameAttendance) |  |
| Stream Graph | Alex Jones | [MAKEOVER MONDAY - PAYING THE PRESIDENT 🐸](https://public.tableau.com/app/profile/jusdespommes/viz/StreamGraph_0/MAKEOVERMONDAY-TRUMPSINTERESTS) | NOTE TO SELF - UPDATE WHEN TRANSPARENT SHEETS BECOME A THING |
| Spiral Chart | Soha Elghany | [Journalist Death](https://public.tableau.com/app/profile/soha.elghany/viz/Journalistdyringacrosstheworld/journalistdeath) | Journalist dying across the world |
| Sunburst Diagram | Simon Beaumont | [Data For A Cause - Global Fishing Watch](https://public.tableau.com/app/profile/simon.beaumont/viz/DataForACause-GlobalFishingWatch-AnAnalysisOfIllegalFishing/DataForACause-GlobalFishingWatch-AnAnalysisOfIllegalFishing) | Data For A Cause - Global Fishing Watch - An Analysis Of Which Countries Fish In Other Countries' Waters. |
| Tadpole Chart | Mark Edwards | [Gender Diversity In Tech (Makeover Monday)](https://public.tableau.com/app/profile/mtedw/viz/GenderDiversityInTechMakeoverMonday/Dashboard1) |  |
| Ternary Plot | Adam McCann | [GOT Ternary](https://public.tableau.com/app/profile/adam.e.mccann/viz/GOTTernary/GOTTernary) |  |
| Timeline | Kimly Scott | [#IronQuest Jan 2019 / The Legacy of Genocide](https://public.tableau.com/app/profile/kimly.scott/viz/IronQuestJan2019TheLegacyofGenocide/TheLegacyofGenocide) |  |
| Timeline (Curvy) | Adam Green | [British Prime Ministers 1905-2019](https://public.tableau.com/app/profile/adam.green4310/viz/BritishPrimeMinisters1905-2019/BritishPrimeMinisters1905-2019) | British Prime Ministers 1905-2019 #VOTD |
| Timeline (Circles) | Josh Tapley | [Josh Tapley Resume](https://public.tableau.com/app/profile/josh.tapley/viz/JoshTapleyResume/ResumeOverview) |  |
| Tree Diagram | Jeff Shaffer | [Node Link Tree Diagram Example 2.0](https://public.tableau.com/app/profile/jeffrey.shaffer/viz/NodeLinkTreeDiagramExample2_0/Node-LinkTreeDiagram) |  |
| Tree Diagram (Radial) | Chris DeMartini | [The Tableau JS API Library](https://public.tableau.com/app/profile/vizde7382/viz/TheTableauJSAPILibrary/APITrees) |  |
| Treemap | Chris Love | [Top 100 Songs of All Time Lyrics](https://public.tableau.com/app/profile/chrisluv/viz/Top100SongsofAllTimeLyrics/Top100Lyrics) |  |
| Unit Chart | David Pires | [IronViz Food](https://public.tableau.com/app/profile/david.pires/viz/IronVizI/Scale) | The food we waste. |
| Unit Histogram | Ann Jackson | [The Changing Landscape of Agriculture in America / #IronViz](https://public.tableau.com/app/profile/ann.jackson/viz/TheChangingLandscapeofAgricultureinAmericaIronViz/TheChangingLandscapeofAgricultureinAmericaIronViz) | The Changing Landscape of Agriculture in America / #IronViz entry for first round feeder of 2019 |
| Waffle Chart | Pooja Gandhi | [#DuoDare 8 - Rain in Seattle (1948-2017)](https://public.tableau.com/app/profile/poojagandhi/viz/DuoDare8-RaininSeattle1948-2017/DuoDare8-RaininSeattle1948-2017) |  |
| Waffle (Plum Pudding Chart) | Kizely Benedict | [The World As 100 People #MakeoverMonday](https://public.tableau.com/app/profile/kizley.benedict/viz/TheWorldAs100PeopleMakeoverMonday/100people) |  |
| Waterfall Chart | Steve Wexler | [CH24_BBOD_ChurnTurnover](https://public.tableau.com/app/profile/swexler/viz/CH24_BBOD_ChurnTurnover/SubscriberChurnAnalysis) | From The Big Book of Dashboards Chapter 24 Showing Churn or Turnover |
| Waterfall Chart (Connected) | Klaus Shulte | [Change in Seasonal Gross Value Added in the UK Bicycle Industry](https://public.tableau.com/app/profile/klaus.schulte/viz/ChangeinSeasonalGrossValueAddedintheUKBicycleIndustry/Dashboard1) |  |
| Win Loss / Barcode Chart | Craig Wortman | [2015 MLB Regular Season via BarCode Charts](https://public.tableau.com/app/profile/craig.wortman/viz/MLB_BarCode_2015_Published/MLBBarCode-LongFormat) | Inspired by Peter Gilks awesome “BallCode” chart from 2014. Loved the idea of making “BarCode” style charts to represent W/L for the 2015 MLB season. |
| Word Cloud | Ken Flerlage | [The Words of  "I Have a Dream"](https://public.tableau.com/app/profile/ken.flerlage/viz/TheWordsofIHaveaDream_0/MLK) | The Words of "I Have a Dream" |

### A.2 Weyburne, Tableau Viz Cookbook

| Gráfico | Autor | Exemplo | Descrição |
|---|---|---|---|
| Word Cloud |  | [Word Cloud](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/WordCloud) | Description A tag cloud (word cloud, or weighted list in visual design) is a visual representation of text data, typically used to depict keyword metadata (tags) on websites,… |
| Waterfall Chart |  | [Waterfall Chart](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/WaterfallChart) | Description A waterfall chart is a form of data visualization that helps in understanding the cumulative effect of sequentially introduced positive or negative values. The… |
| Treemap |  | [Treemap](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/Treemap) | Description Use treemaps to display data in nested rectangles. You use dimensions to define the structure of the treemap, and measures to define the size or color of the… |
| Tree Diagram |  | [Tree Diagram](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/TreeDiagram) | Original view created by Jeffrey Shaffer Description A Tree Diagram is a way of visually representing hierarchy in a tree-like structure. Typically the structure of a Tree… |
| Stream Graph |  | [Stream Graph](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/StreamGraph) | Original view created by Andy Kriebel Description This type of visualisation is a variation of a Stacked Area Graph, which instead of plotting values against a fixed, straight… |
| Spiral Plot |  | [Spiral Plot](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/SpiralPlot) | Original view created by Neil Richards Description This type of visualisation plots time-based data along an Archimedean spiral. The graph begins from the center of the spiral… |
| Sparklines |  | [Sparklines](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/Sparklines) | Description A sparkline is a very small line chart, typically drawn without axes or coordinates. It presents the general shape of the variation (typically over time) in some… |
| Span Chart |  | [Span Chart](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/SpanChart) | Description A span chart used to display dataset ranges between a minimum value and a maximum value. It's ideal for comparing ranges, typically categorised ranges. Span charts… |
| Small Multiples |  | [Small Multiples](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/SmallMultiples) | Description A small multiple (sometimes called trellis chart, lattice chart, grid chart, or panel chart) is a series of similar graphs or charts using the same scale and axes,… |
| Slopegraphs |  | [Slopegraphs](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/Slopegraphs) | Description A slopegraph is a lot like a line graph, in that it plots change between points. However a slopegraph plots the change between only two points, without any kind of… |
| Side-By-Side Bar Chart |  | [Side-By-Side Bar Chart](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/SideBySideBarChart) | Description This variation of a Bar Chart is used when two or more data sets are plotted side-by-side and grouped together under categories, all on the same axis. Like a Bar… |
| Scatter Plot |  | [Scatter Plot](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/ScatterPlot) | Description A scatter plot (also called a scatter graph, scatter chart, scattergram, or scatter diagram) is a type of plot or mathematical diagram using Cartesian coordinates… |
| Sankey Diagram |  | [Sankey Diagram](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/SankeyDiagram) | Original view created by Olivier Catherin Description Sankey diagrams are a specific type of flow diagram, in which the width of the arrows is shown proportionally to the flow… |
| Radial Tree Map |  | [Radial Tree Map](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/RadialTreeMap) | Original view created by Bora Beran Description This type of visualisation shows hierarchy through a series of rings, that are sliced for each category node. Each ring… |
| Radial Column Chart |  | [Radial Column Chart](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/RadialColumnChart) | Original view created by Ryan Rowland Description This type of graph uses a grid of concentric circles to plot bars on. Each circle on the graph represents a value on a scale,… |
| Radial Bar Chart |  | [Radial Bar Chart](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/RadialBarChart) | Original view created by Bora Beran Description A Radial/Circular Bar Chart is simply a Bar Chart plotted on a polar coordinate system, rather than on a cartesian one. While… |
| Radar Chart |  | [Radar Chart](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/RadarChart) | Original view created by Jonathan Trajkovic Description A radar chart is a graphical method of displaying multivariate data in the form of a two-dimensional chart of three or… |
| Pie Chart |  | [Pie Chart](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/PieChart) | Description Use pie charts to show proportions. |
| Pareto Chart |  | [Pareto Chart](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/ParetoChart) | Original view created by Andy Kriebel Description A Pareto chart, named after Vilfredo Pareto, is a type of chart that contains both bars and a line graph, where individual… |
| Panel Charts |  | [Panel Charts](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/PanelCharts) | Description A panel chart is a set of similar charts neatly aligned in panels to help us understand some data which has multiple variables in it. www.chandoo.org |
| Packed Bubble Chart |  | [Packed Bubble Chart](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/PackedBubbleChart) | Description Use packed bubble charts to display data in a cluster of circles. Dimensions define the individual bubbles, and measures define the size and color of the individual… |
| Network Diagram |  | [Network Diagram](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/NetworkDiagram) | Original view created by Robert Mundigl Description This type of visualisation shows how things are interconnected through the use of nodes / vertices and link lines to… |
| Marimekko Chart |  | [Marimekko Chart](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/MarimekkoChart) | Description A Mekko chart (sometimes also called marimekko chart) is a two-dimensional stacked chart. In addition to the varying segment heights of a regular stacked chart, a… |
| Lollipop Chart |  | [Lollipop Chart](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/LollipopChart) | Description A lollipop chart is a combination of a line chart and dot plot that allows you to add more detailed information into the chart. |
| Line Chart |  | [Line Chart](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/LineChart) | Original view created by Christian Chabot Description Line charts connect individual data points in a view. They provide a simple way to visualize a sequence of values and are… |
| Jump Plot |  | [Jump Plot](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/JumpPlot) | Original view created by Chris DeMartini and Tom VanBuskirk Description The Jump Plot allows for scalable graphing of sequence event data with multiple variations to… |
| Horizon Chart |  | [Horizon Chart](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/HorizonChart) | Original view created by Yvan Fornes Description Horizon charts are a Horizon charts are a powerful tool for comparing data over time among many items within a category. This… |
| Histogram |  | [Histogram](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/Histogram) | Description A histogram is a chart that displays the shape of a distribution. A histogram looks like a bar chart but groups values for a continuous measure into ranges, or bins. |
| Hex Tile Map |  | [Hex Tile Map](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/HexTileMap) | Original view created by Matt Chambers Description A Hex tile map is a map that uses hexagons to represent geographic areas to prevent bias towards areas with a larger… |
| Heatmap |  | [Heatmap](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/Heatmap) | Description A heat map (or heatmap) is a graphical representation of data where the individual values contained in a matrix are represented as colors. Fractal maps and tree… |
| Gantt Chart |  | [Gantt Chart](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/GanttChart) | Description A chart in which a series of horizontal lines shows the amount of work done or production completed in certain periods of time in relation to the amount planned for… |
| Funnel Chart |  | [Funnel Chart](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/FunnelChart) | Original view created by Alexander Mou Description Funnel charts are a type of chart, often used to represent stages in a sales process and show the amount of potential revenue… |
| Donut Chart |  | [Donut Chart](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/DonutChart) | Description Just like pie charts, a donut chart is type of graph in which a circle is divided into sectors that each represent a proportion of the whole. The difference is that… |
| Crosstab |  | [Crosstab](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/Crosstab) | Description Crosstab, or Cross Tabulation, is a process or function that combines and/or summarizes data from one or more sources into a concise format for analysis or… |
| Coxcomb |  | [Coxcomb](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/Coxcomb) | Original view created by Bora Beran Description A Coxcomb chart, sometimes referred to as a polar area chart or a rose chart, is sort of a combination of a bar chart and a pie… |
| Control Charts |  | [Control Charts](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/ControlCharts) | Description The control chart is a graph used to study how a process changes over time. Data are plotted in time order. A control chart always has a central line for the… |
| Connection Map |  | [Connection Map](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/ConnectionMap) | Description Connection Maps are drawn by connecting points placed on a map by straight or curved lines. While Connection Maps are great for showing connections and… |
| Combination Charts |  | [Combination Charts](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/CombinationCharts) | Description Combination charts are views that use multiple mark types in the same sheet. For example, you may show sum of profit as bars with a line across the bars showing sum… |
| Choropleth Map |  | [Choropleth Map](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/ChoroplethMap) | Description A choropleth map is a thematic map in which areas are shaded or patterned in proportion to the measurement of the statistical variable being displayed on the map,… |
| Chord Diagram |  | [Chord Diagram](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/ChordDiagram) | Original view created by Noah Salvaterra Description A chord diagram is a graphical method of displaying the inter-relationships between data in a matrix. The data is arranged… |
| Cartograms |  | [Cartograms](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/Cartograms) | Original view created by Robert Mundigl Description A cartogram is a map in which some thematic mapping variable – such as travel time, population, or Gross National Product –… |
| Candlestick Chart |  | [Candlestick Chart](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/CandlestickChart) | Description A candlestick chart (also called Japanese candlestick chart) is a style of financial chart used to describe price movements of a security, derivative, or currency.… |
| Calendar |  | [Calendar](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/Calendar) | Description A calendar chart is a visualization used to show activity over the course of a long span of time, such as months or years. They're best used when you want to… |
| Bump Charts |  | [Bump Charts](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/BumpCharts) | Original view created by Matt Chambers Description A Bump Chart is used to compare two Dimensions against each other using one of the Measure value. They are very useful for… |
| Bullet Graph |  | [Bullet Graph](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/BulletGraph) | Description A bullet graph is a variation of a bar graph developed by Stephen Few. Seemingly inspired by the traditional thermometer charts and progress bars found in many… |
| Bubble Map |  | [Bubble Map](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/BubbleMap) | Description With this data map, circles are displayed over a designated geographical region with the area of the circle being proportional to its value in the dataset. Bubble… |
| Box and Whisker Plot |  | [Box and Whisker Plot](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/BoxandWhiskerPlot) | Original view created by Steve Wexler Description In descriptive statistics, a boxplot or box plot is a convenient way of graphically depicting groups of numerical data through… |
| Bollinger Bands |  | [Bollinger Bands](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/BollingerBands) | Description Bollinger Bands is a tool invented by John Bollinger in the 1980s as well as a term trademarked by him in 2011. Having evolved from the concept of trading bands,… |
| Bar Chart |  | [Bar Chart](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/BarChart) | Description A bar chart or bar graph is a chart or graph that presents grouped data with rectangle/rectangular bars with lengths proportional to the values that they represent.… |
| Arrow Chart |  | [Arrow Chart](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/ArrowChart) | Original view created by Joe Mako Description Arrow charts can be used as an alternative to multiple pie charts. |
| Area Graph |  | [Area Graph](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/AreaGraph) | Description An area chart or area graph displays graphically quantitative data. It is based on the line chart. The area between axis and line are commonly emphasized with… |
| Arc Chart |  | [Arc Chart](https://public.tableau.com/profile/josh.weyburne#!/vizhome/CookBook/ArcChart) | Original view created by Asher Campbell Description An Arc Chart is a style of graph drawing, in which the vertices of a graph are placed along a line in the Euclidean plane,… |

### A.3 Rasztik, Tutorials of visualizations

| Gráfico | Autor | Exemplo | Descrição |
|---|---|---|---|
| Waffle chart | Recnac | [tutorial](https://www.pluralsight.com/guides/tableau-playbook-waffle-chart) |  |
| Voronoi treemap | Tristan Guillevin | [tutorial](https://www.ladataviz.com/tools/advviz/voronoi) |  |
| Violin Plot | Liam Holland (The Data School) | [tutorial](https://www.thedataschool.co.uk/liam-holland/understanding-and-making-violin-plot-in-tableau) |  |
| Sunburst chart | Lindsay Betzendahl | [tutorial](https://vizzendata.com/2022/01/07/part-2-the-build-an-annual-sunburst-chart-template/) |  |
| Sunburst chart | Eric Balash | [tutorial](https://www.youtube.com/watch?v=YBnMWHwMOdo) |  |
| Sunburst chart | Data Embassy | [tutorial](https://www.youtube.com/watch?v=goIAKkk-eFE) |  |
| Stream graph | Toan Hoang | [tutorial](https://tableau.toanhoang.com/sigmoid-area-charts-in-tableau/) |  |
| Shapes | Kevin Flerlage | [tutorial](https://www.flerlagetwins.com/2018/10/no-polygons_86.html) |  |
| Shapes | CJ Mayes | [tutorial](https://cj-mayes.com/2021/06/26/game-shape-match/) |  |
| Sankey | Brandon Fitz-Gerald (The Information Lab) | [tutorial](https://www.youtube.com/watch?v=PkCfSn8NnJk) |  |
| Rounded bar | Shipra Saxena | [tutorial](https://www.analyticsvidhya.com/blog/2021/02/create-rounded-bar-chart-tableau/) |  |
| Rounded bar | Ryan Sleeper | [tutorial](https://playfairdata.com/dashboard-gauge-2-how-to-make-rounded-bars-and-scales-in-tableau/) |  |
| Ridgeline plot | Ken Flerlage | [tutorial](https://www.flerlagetwins.com/2018/05/joy-plot.html) |  |
| Ridgeline plot | Ben Wells (The Information Lab) | [tutorial](https://www.youtube.com/watch?v=QNTxKSLqKcY) |  |
| Radial time series | Rahul Singh | [tutorial](https://vizzingdata.com/visualizing-radial-time-series-data-to-uncover-patterns-in-tableau/) |  |
| Radial time series | Lindsay Betzendahl | [tutorial](https://vizzendata.com/2018/07/20/the-cycle-of-influenza-creating-a-radial-time-series-chart/) |  |
| Radial tab polygon | Lindsay Betzendahl | [tutorial](https://vizzendata.com/2019/12/04/radial-tab-polygon-chart/) |  |
| Radial stacked bar | Data Embassy | [tutorial](https://www.youtube.com/watch?v=0v6PMf2tHM4) |  |
| Radial bar | Art of Visualization | [tutorial](https://www.youtube.com/watch?v=d6-aptKLvgg) |  |
| Radar chart | Ellen Blackburn (The Data School) | [tutorial](https://www.thedataschool.co.uk/ellen-blackburn/a-simple-way-to-make-a-radar-chart) |  |
| Radar chart | Brant W | [tutorial](https://towardsdatascience.com/an-easy-way-to-draw-spider-charts-on-tableau-part-i-6fc75bcaa45a) |  |
| Plum pudding chart | Kizley Benedict | [tutorial](https://vizzendata.com/2019/05/15/guest-post-how-to-create-a-plum-pudding-chart-circular-waffle-chart/) |  |
| Lollipop chart | Rigor Data Solutions | [tutorial](https://www.rigordatasolutions.com/post/2018/09/08/tableau-charts-lollipop-chart) |  |
| Jittering | Anthony B. Smoak | [tutorial](https://www.youtube.com/watch?v=6Xhlt4GT9rw) |  |
| Icicle chart | Lindsay Betzendahl | [tutorial](https://vizzendata.com/2019/12/27/creating-a-deviation-icicle-chart/) |  |
| Half circle timeline | Toan Hoang | [tutorial](https://tableau.toanhoang.com/creating-half-circle-timelines-variation-in-tableau/) |  |
| Grid map | Matt Chambers | [tutorial](https://www.sirvizalot.com/2015/11/hex-tile-maps-in-tableau.html) |  |
| Grid map | Brittany Fong | [tutorial](https://www.tableau.com/about/blog/2015/11/how-make-tiled-maps-tableau-45742) |  |
| Gradient area chart | Ken Flerlage | [tutorial](https://www.flerlagetwins.com/2022/09/gradient.html?m=1) |  |
| Fan chord | CJ Mayes | [tutorial](https://cj-mayes.com/2022/10/11/fan-chord-chart-tutorial/) |  |
| Edge bundling | Marc Reid | [tutorial](https://datavis.blog/2020/07/02/creating-chord-diagram-in-tableau/) |  |
| Edge bundling | Luke Stanke | [tutorial](https://www.phdata.io/blog/tableau-tutorial-chord-diagram/) |  |
| Dumbbell | Recnac | [tutorial](https://www.pluralsight.com/guides/tableau-playbook-dumbbell-chart) |  |
| Dumbbell | Donna Coles | [tutorial](https://donnacoles.home.blog/2022/08/12/can-you-build-a-dumbbell-chart/) |  |
| Donut chart | Techi Anshi | [tutorial](https://www.youtube.com/watch?v=HMtChgswsyU) |  |
| Donut chart | Data Embassy | [tutorial](https://www.youtube.com/watch?v=ZfpUzp8mBSw) |  |
| Diverging bar | Sandeep Pothula (S-Square Systems) | [tutorial](https://www.s-squaresystems.com/steps-to-create-butterfly-chart-in-tableau/) |  |
| Diverging bar | Ryan Sleeper | [tutorial](https://playfairdata.com/how-to-make-a-diverging-bar-chart-in-tableau) |  |
| Diverging bar | Andy Kriebel | [tutorial](https://www.youtube.com/watch?v=ynhRqI3_iwU) |  |
| Curvy bump | Kevin Flerlage | [tutorial](https://www.flerlagetwins.com/2019/03/curvy-bump-chart-slope-chart-template_27.html) |  |
| Curved line chart | Rajeev Pandey | [tutorial](https://vizartpandey.com/how-to-make-a-curved-line-chart-in-tableau-4f8051d3639f) |  |
| Coxcomb | Toan Hoang | [tutorial](https://tableau.toanhoang.com/creating-a-polar-chart-in-tableau/) |  |
| Coxcomb | Toan Hoang | [tutorial](https://tableau.toanhoang.com/creating-a-coxcomb-chart-in-tableau/) |  |
| Coxcomb | Ruth Amarteifio (The Information Lab) | [tutorial](https://www.youtube.com/watch?v=iFQMefl1vII) |  |
| Coxcomb | Ken Flerlage | [tutorial](https://www.flerlagetwins.com/2021/12/coxcomb.html) |  |
| Circular sankey | Gurpreet Singh (Data Viz Canvas) | [tutorial](https://www.youtube.com/watch?v=K0Bf3THr88s) |  |
| Circular sankey | CJ Mayes | [tutorial](https://datavis.blog/2020/11/28/circular-sankey-template/) |  |
| Chord diagram | Noah Salvaterra | [tutorial](https://www.datablick.com/blog/2015/08/27/diy-chord-diagrams-in-tableau-by-noah-salvaterra) |  |
| Candlestick chart | Jenny Martin (The Information Lab) | [tutorial](https://www.youtube.com/watch?v=7hEMwOKmYxY) |  |
| Candlestick chart | Andrew Watson | [tutorial](https://tarsolutions.co.uk/blog/tableau-candlestick-chart/) |  |
| Bar in bar | Shipra Saxena | [tutorial](https://www.analyticsvidhya.com/blog/2021/02/create-rounded-bar-chart-tableau/) |  |
| Arc sankey | Ken Flerlage | [tutorial](https://www.flerlagetwins.com/2019/10/arc-sankey.html) |  |
| “Hand-drawn” bar | Brian Moore | [tutorial](https://domoorewithdata.com/2022/06/29/totally-useless-charts-how-to-build-them-hand-drawn-bar-charts/) |  |
