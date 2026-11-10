# Bot WhatsApp — Cultura Afro-Indígena 2026.2

Assistente do projeto **Falas de Maria: Lutas e Conquistas**. Responde dúvidas sobre culturas e histórias afro-brasileiras e indígenas usando os materiais em `documents/`, o Ollama local e pesquisa na web quando necessário. Atende somente conversas individuais; grupos, canais, status e listas de transmissão são ignorados.

## Preparar no Windows

Instale o [Python 3.10 ou superior](https://www.python.org/downloads/windows/) e o [Ollama para Windows](https://ollama.com/download/windows). Abra o Ollama e aguarde a API local ficar disponível. Depois, no PowerShell, dentro desta pasta, execute:

```powershell
powershell -ExecutionPolicy Bypass -File .\preparar_ambiente.ps1
```

O script cria `.venv`, instala as dependências, cria `.env.extensao` a partir do exemplo, baixa os modelos configurados e indexa os documentos. Na primeira execução, os modelos podem baixar alguns gigabytes.

Para iniciar o bot:

```powershell
.\.venv\Scripts\python.exe .\bot_agentes.py
```

Na primeira execução, siga o QR/pedido de pareamento exibido pelo Neonize usando **Aparelhos conectados** no WhatsApp. Mantenha o Ollama aberto e execute apenas uma instância do bot por vez. A sessão do WhatsApp fica em `sessao_whatsapp.db` e não deve ser compartilhada entre computadores.

## Configuração

Edite `.env.extensao` para escolher modelos, endereço do Ollama ou limites da fila. O arquivo não deve ser compartilhado; o exemplo sem dados privados está em `.env.extensao.example`.

```dotenv
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b
EMBEDDING_MODEL=nomic-embed-text
WHATSAPP_QUEUE_WORKERS=2
WHATSAPP_USER_BURST=3
WHATSAPP_USER_PAUSE_SECONDS=5
WHATSAPP_MAX_PENDING_PER_USER=30
WHATSAPP_MAX_PENDING_TOTAL=2000
```

A fila preserva a ordem de cada conversa, atende no máximo três mensagens seguidas por pessoa e espera cinco segundos antes das próximas. Assuntos fora do tema e tentativas comuns de prompt injection são bloqueados antes da chamada ao modelo.

## Materiais e comandos

Os três arquivos Markdown em `documents/` são a base inicial. Para acrescentar conteúdo, coloque um PDF com texto selecionável ou um Markdown nessa pasta e rode novamente:

```powershell
.\.venv\Scripts\python.exe .\indexar_pdfs.py
```

O índice é recriado localmente em `dados_rag/indice.json`; ele não precisa ser copiado para outro PC. PDFs e a sessão do WhatsApp também ficam locais.

Comandos disponíveis no chat: `/menu`, `/ajuda`, `/sobre`, `/documentos`, `/plano`, `/limpar`. Para solicitar pesquisa na web, envie `/web` seguido da pergunta. O bot também pode pesquisar automaticamente.

## Estrutura

- `bot_agentes.py`: conexão WhatsApp, fila e comandos.
- `agentes_autonomos.py`, `busca_web.py`: pesquisa local/web e geração de respostas.
- `rag_local.py`, `indexar_pdfs.py`: base documental e índice local.
- `fila_whatsapp.py`, `escopo_assunto.py`: limites da fila e filtro de assunto/injeção.
- `documents/`: materiais de conhecimento incluídos no projeto.
- `dados_rag/`: índice gerado no computador onde o bot roda.
