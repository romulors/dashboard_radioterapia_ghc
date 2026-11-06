# TODO — versões futuras

Pendências do dashboard de Radioterapia (GHC), reunidas em 06/11/2026 a partir do `README.md`,
do `CLAUDE.md`, de `docs/plano-dashboard.md` e das conversas do projeto. Nada aqui está em andamento.

## 1. Assistente de IA local (chatbot de ajuda)

Objetivo: ajudar quem é novo na radioterapia ou está perdido no painel a entender os dados e a navegação,
sem enviar nada para fora do computador.

- **Ferramenta:** Ollama no Windows com modelo pequeno quantizado, bom em português
  (Qwen 2.5/3 de 3–4B ou Gemma 3 4B). Cerca de 4–6 GB de RAM e 2–3 GB de disco; só CPU gera
  ~5–15 palavras/s. Com GPU de 6–8 GB, modelos de 7–8B respondem melhor.
- **Privacidade:** tudo local (`localhost`). O modelo recebe só agregados e textos de ajuda,
  nunca linhas de pacientes.
- [ ] **Nível 1 — guia do painel (~2 dias, fazer primeiro).** Responder com base nos textos do "?"
  (`app/ajuda.py`), na aba Sobre, nas definições (ciclo, espera, atraso, tipo de fluxo) e nas metas.
  O corpus é pequeno, então não precisa de banco vetorial. Indicar a aba onde está a resposta.
  - [ ] Painel lateral (offcanvas) no Dash com histórico em `dcc.Store`; chamada ao Ollama em
    callback em segundo plano para não travar a tela.
  - [ ] Instrução de sistema: responder só com o contexto fornecido e dizer "não sei" quando faltar.
  - [ ] Aviso amigável quando o Ollama não estiver rodando; `Lançar Dashboard.bat` inicia o Ollama.
  - [ ] Modelo e endereço do Ollama em `config/settings.yaml`.
  - [ ] Testes com um conjunto fixo de perguntas e respostas esperadas.
- **Configuração-alvo (06/11):** modelos < 9B, pesos Q4_K_M, KV cache Q4 (ou K em q8_0 e V em q4_0
  no llama.cpp), contexto de 32k, raciocínio ("thinking") desligado e respostas em JSON validado por schema.
  - Escolha do Romulo (06/11): **LiquidAI LFM3-1.7B**, arquivo `LFM3-1.7B-QAD-Q4_0.gguf` (1,28 GB; português
    suportado; feito para tool calling e saída estruturada). Temperatura 0.1, top_k 50, repetition_penalty 1.1.
    Comparar com Qwen3.5-4B nas mesmas perguntas. Conferir a licença LFM Open License v1.0.
  - Rodar com `llama-server` (b11960 ou mais novo): `-c 32768 -fa on -ctk q8_0 -ctv q8_0 --json-schema ...`,
    ou importar o GGUF no Ollama via Modelfile. O "thinking" vem ligado: desligar e testar se obedece.
  - Ollama: `OLLAMA_FLASH_ATTENTION=1`, `OLLAMA_KV_CACHE_TYPE=q4_0`, `OLLAMA_CONTEXT_LENGTH=32768`;
    parâmetro `format` com o JSON Schema da resposta e `think: false`.
  - Prompt de sistema fixo no início para reaproveitar o cache; enviar só os trechos de ajuda relevantes.
- [ ] **Nível 2 — perguntas sobre os dados (+2–3 dias).** O modelo escolhe um indicador já registrado
  com `@indicator` e os filtros (ex.: "atraso médio de Urgência em agosto"); o Python calcula.
- [ ] **Nível 3 — perguntas por áudio (+2–3 dias).** Modelo avaliado: **LiquidAI LFM3-Omni-2B**
  (`Q4_K_M`, 1,1 GB, mais o `mmproj-LFM3-Omni-2B-Q8_0.gguf`). Ele aceita áudio de 16 kHz, faz ASR em
  português, tem tool calling e não usa thinking (`--reasoning off`, temperatura 0). Contexto de 32k.
  - Opção A (mais simples): usar só o Omni para áudio e texto. Opção B: o Omni transcreve e o LFM3-1.7B responde.
  - [ ] Botão de microfone no painel do chat: MediaRecorder em `assets/`, convertido para WAV 16 kHz mono no
    navegador e enviado ao callback. O microfone só funciona em `localhost`/`127.0.0.1` ou com HTTPS.
  - [ ] Não usar a Web Speech API do Chrome: ela envia o áudio para servidores do Google.
  - [ ] Não gravar o áudio em disco; mostrar a transcrição antes de responder, para o usuário corrigir.
  - [ ] Confirmar se o `llama-server` aceita `input_audio` na API; senão, usar `/v1/realtime` ou o `llama cli`.
  - [ ] Opcional: resposta falada (TTS em português) como recurso de acessibilidade.
- **Não fazer:** deixar o modelo gerar e executar código pandas livre (erros frequentes em modelos
  pequenos e risco de segurança).
- Alternativa sem IA, de esforço quase zero: aba ou seção "Como usar" com perguntas frequentes.

## 2. Dados que faltam

- [ ] Faltas (absenteísmo) no acelerador linear: sem fonte.
- [ ] CID por paciente: sem fonte.
- [ ] Exportação com as atividades de tomografia por sítio (ex.: "Tomografia Pelve") para estimar a
  ocupação do tomógrafo; hoje o proxy é `Importar TC e Fusao`.
- [ ] Ciclos que só têm a recepção (sem importação) aparecem como "Sem tipo": definir tratamento.

## 3. Metas a definir com a gestão

- [ ] `metas.pct_no_prazo` e `metas.lead_time_mediana_dias` estão `null` em `config/settings.yaml`
  (o painel mostra "Sem meta definida").
- [ ] Tolerâncias de cada meta no scorecard de KPIs.

## 4. Interface e acessibilidade

- [ ] Escolher a barra de filtros entre as 3 alternativas (A compacta, B lateral, C linha do tempo;
  capturas `filtros-alt-*.png`).
- [ ] Cores abaixo de 3:1 contra o branco (WCAG 1.4.11): Sem tipo 1,74, Retomografado 2,14,
  Prioridade 2,28, Dia `#04BABA` 2,40, Neutro 2,54. Eletivo e No prazo quase iguais (1,06:1).
- [ ] Decidir se o modo alto contraste deve ser o padrão na apresentação (banca).
