# Assistente WhatsApp - Cultura Afro-Indígena 2026.2

Assistente escolar do projeto **Falas de Maria: Lutas e Conquistas**. Responde em português sobre histórias, culturas, línguas, patrimônios e povos afro-brasileiros e indígenas. Usa materiais em `documents/`, busca local com Ollama e pesquisa na web quando necessário. O modelo nao foi treinado do zero: a base pode ser ampliada com documentos revisados e fontes públicas.

O bot atende conversas individuais. Grupos, canais, status e listas de transmissao sao ignorados. Também responde perguntas institucionais basicas sobre ESBAM/UNIESBAM usando os dados documentados em `documents/informacoes_institucionais_esbam.md`.

## Preparar no Windows

O script detecta os componentes existentes e instala o que faltar: Python 3.12 de 64 bits, Ollama, dependências Python e modelos configurados. Cria ou reutiliza `.venv`, preserva configuracoes locais, baixa apenas os modelos ausentes e reindexa os documentos quando eles mudarem.

Abra o PowerShell nesta pasta e execute:

```powershell
powershell -ExecutionPolicy Bypass -File .\preparar_ambiente.ps1
```

E necessário acesso a internet e espaco em disco para os modelos locais (vários gigabytes). A política da máquina pode exigir autorização administrativa para instalar programas. O script testa se a biblioteca Neonize carrega; se o Controle de Aplicativos bloquear a DLL (`WinError 4551`), a liberacao deve ser solicitada ao administrador de TI.

Inicie o bot:

```powershell
.\.venv\Scripts\python.exe .\bot_agentes.py
```

Para reiniciar automaticamente ao salvar arquivos Python ou `.env.extensao`:

```powershell
.\.venv\Scripts\python.exe .\rodar_com_reload.py
```

Na primeira conexão, siga o QR ou o pedido de pareamento do Neonize em **Aparelhos conectados** do WhatsApp. A sessão fica salva localmente em `sessao_whatsapp.db`. Execute somente uma instancia do bot por sessão.

## Configuração

O arquivo `.env.extensao` e criado a partir de `.env.extensao.example` quando ainda nao existe. Edite-o localmente para mudar os modelos, o endereco do Ollama ou os limites da fila. Nao compartilhe o arquivo local.

```dotenv
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b
EMBEDDING_MODEL=nomic-embed-text
WHATSAPP_QUEUE_WORKERS=2
WHATSAPP_USER_BURST=3
WHATSAPP_USER_PAUSE_SECONDS=5
WHATSAPP_MAX_PENDING_PER_USER=30
WHATSAPP_MAX_PENDING_TOTAL=2000
WHATSAPP_MESSAGE_BURST_WINDOW_SECONDS=3.5
WHATSAPP_OFF_TOPIC_NOTICE_SECONDS=180
WHATSAPP_MAX_MESSAGE_AGE_SECONDS=120
WHATSAPP_STICKER_INTERVAL=5
WHATSAPP_IMAGE_INTERVAL=5
```

A fila espera ate 3,5 segundos de silencio para juntar mensagens consecutivas da mesma conversa em uma unica consulta. Risadas e reacoes curtas sao descartadas quando vieram junto de uma pergunta; avisos como "bugou" ou "lascou" tambem nao interrompem a pergunta agrupada. Se forem enviados sozinhos, recebem uma resposta breve e acolhedora. Mensagens antigas e duplicadas podem ser ignoradas. O intervalo de avisos fora do tema reduz repeticoes.

## Como conversar

Escreva normalmente, sem comandos. Exemplos:

- Quem foi Tereza de Benguela e por que ela e lembrada?
- Qual e a funcao do berimbau na capoeira?
- Como línguas africanas influenciaram o português brasileiro?
- Quais línguas indígenas sao faladas no Brasil?
- O que e a ESBAM? Qual o telefone ou o Instagram?

Pode juntar perguntas na mesma mensagem, separando-as com `?`, ponto e virgula ou nova linha. O bot tenta responder todas em uma so mensagem, na mesma ordem. Mensagens curtas seguintes, como "e por que?", podem ser entendidas pelo contexto recente da conversa.

Comandos disponíveis:

- `/menu` ou `/ajuda`: exemplos e orientações.
- `/web pergunta`: solicitar uma pesquisa na internet.
- `/fontes`: buscar referências online ligadas a última resposta. Também pode perguntar "quais sao as fontes?".
- `/sobre`: informações sobre o assistente.
- `/plano`: detalhes tecnicos da última pesquisa, para depuracao.

Respostas factuais terminam com links das fontes web consultadas. Quando a resposta comeca nos materiais locais e ainda nao houve busca web, o bot procura referencias publicas antes de responder; se nao encontrar uma fonte confiavel, informa isso sem inventar links. As referencias ficam no fim da mensagem.

## Conhecimento e materiais

Os guias `direitos_e_lutas_povos_indigenas.md` e `direitos_lutas_populacao_negra_quilombola.md` ampliam a base com direitos, território, saúde, educação, legislação, desigualdades e desafios atuais. São sínteses educativas; temas jurídicos e situações em andamento devem ser conferidos em fontes oficiais atualizadas e contextualizados para cada povo ou comunidade.

Os arquivos Markdown e PDFs pesquisaveis ficam em `documents/`. Revise a origem, a permissão de uso e a ausencia de dados pessoais antes de adicionar material. Para reindexar manualmente:

```powershell
.\.venv\Scripts\python.exe .\indexar_pdfs.py
```

O indice e criado em `dados_rag/indice.json` e pode ser reconstruido; nao precisa ser versionado. PDFs digitalizados sem texto selecionavel precisam de OCR. Alterações no indice sao lidas nas proximas consultas, sem reiniciar o bot. O modelo nao aprende automaticamente com as conversas.

Os guias locais sao sinteticos e nao representam todas as comunidades. Para dados atuais, cursos, mensalidades, vestibular ou servicos da ESBAM, encaminhe a pessoa ao site oficial: https://esbam.edu.br/.

### Prévia de personagens MIRA

**MIRA: Vozes que atravessam gerações** é o nome do projeto; as duas personagens são **Esperança Garcia** (base v1.2.1) e **Clara Camarão** (base textual v1.0.0). No WhatsApp, envie `/mira` para ver as orientações ou use:

- `/mira esperanca`: selecionar Esperança Garcia.
- `/mira clara`: selecionar Clara Camarão.
- `/mira sair`: voltar ao assistente geral.

Envie o comando sozinho, sem acrescentar o nome da personagem. Para pesquisa na internet, use `/web <pergunta>` com a barra inicial, por exemplo: `/web preservacao das linguas indigenas`.

A personagem selecionada fica salva localmente por conversa. As perguntas podem ser livres, não precisam repetir as perguntas de exemplo. No modo MIRA, o bot responde com a base e as fontes registradas para a personagem selecionada; não faz busca web fora dessa base e reconhece quando não encontra evidência suficiente. Fora do modo MIRA, continua valendo o fluxo geral do assistente.

As duas personagens são representações educativas virtuais, não simulações de memórias pessoais. As prévias ficam ativadas por padrão; defina `MIRA_PREVIEW_ENABLED=0` para desativar ambas ou `MIRA_CLARA_PREVIEW_ENABLED=0` para desativar somente Clara. A entrega de Clara ainda a marca como não aprovada para conversa pública, e seus 14 cenários precisam de avaliação. A ativação padrão habilita o uso local do modo MIRA, mas não constitui liberação pública. A selecao MIRA fica em `logs/mira_modos.json` (ignorado pelo Git), permanece ativa apos reiniciar e pode ser desativada com `/mira sair`.

Os testes locais conferem integridade das bases, recuperação de evidências, referências permitidas, limites de lacunas e encaminhamento de conversas. Eles não substituem revisão das respostas do modelo; a integração deve continuar em prévia até essa revisão.

Para repetir a validação:

```powershell
.\.venv\Scripts\python.exe -m unittest -v test_mira_personagens.py
```

## Imagens e figurinhas

Pedidos como "Pode me mandar uma imagem da capoeira?" ou "Me manda uma figurinha de capoeira" testam o envio de mídia. Imagens podem acompanhar respostas sobre alguns temas visuais, e figurinhas podem ser enviadas automaticamente conforme `WHATSAPP_STICKER_INTERVAL`. Além do pedido explícito, a cada `WHATSAPP_IMAGE_INTERVAL` respostas dentro do tema o bot pode enviar sozinho uma imagem do assunto que estava sendo conversado, descoberto pela base local usada naquela resposta (sem depender de uma lista fixa de termos); isso só acontece quando a resposta é informativa e não for junto com uma figurinha na mesma mensagem. O envio depende da rede, da disponibilidade do arquivo e do WhatsApp. O terminal e `logs/interacoes_whatsapp.jsonl` registram o resultado.

## Privacidade, dados locais e Git

A sessão do WhatsApp, `.env.extensao`, logs, bancos de dados e indice local nao devem ser publicados. Os logs podem conter mensagens, respostas, evidências e resultados da web. O arquivo `.gitignore` bloqueia esses itens, ambientes Python, PDFs e pastas de documentos locais/privados. `.env.extensao.example` e permitido e deve conter somente valores ficticios ou padroes sem segredo.

Antes de preparar um commit, revise o estado e os arquivos staged. O guia [Segurança_E_GIT.md](./SEGURANCA_E_GIT.md) explica as verificacoes, os caminhos protegidos e o que fazer se algum segredo ja tiver sido rastreado. `.gitignore` nao remove arquivos ja rastreados; se um segredo ja foi enviado a um repositorio remoto, revogue-o e invalide a sessão exposta.

Consulte [Política_Conteúdo_E_FONTES.md](./POLITICA_CONTEUDO_E_FONTES.md) para critérios de segurança, fontes e resposta escolar.

## Estrutura principal

- `bot_agentes.py`: conexão WhatsApp, comandos, fila, histórico e envio de mídia.
- `agentes_autonomos.py`, `busca_web.py`: busca local/web e respostas.
- `mira_personagens.py`: seleção de perfil e respostas fundamentadas nas bases MIRA.
- `rag_local.py`, `indexar_pdfs.py`: indexação e recuperacao de documentos.
- `fila_whatsapp.py`, `escopo_assunto.py`: agrupamento de mensagens e filtros.
- `midia_whatsapp.py`: busca e preparacao de imagens e figurinhas.
- `documents/`: materiais revisados para a base do bot.
- `documents/mira/`: bases e auditorias recebidas do projeto MIRA.
- `dados_rag/`: indice gerado localmente.
- `logs/`: diagnosticos locais, ignorados pelo Git.
