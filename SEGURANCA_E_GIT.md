# Seguranca, privacidade e Git

Este projeto mantém no computador dados necessários para a conexão do WhatsApp e para depuração. Eles podem conter credenciais, identificadores ou conteúdo de conversas e não devem ser enviados ao Git.

## Arquivos locais que não devem ser publicados

- `.env.extensao`, `.env` e outros arquivos de configuração locais. O modelo seguro para compartilhar é `.env.extensao.example`, sem tokens ou credenciais.
- `sessao_whatsapp.db` e arquivos de sessão, autenticação, QR ou pareamento. A sessão autenticada permite acessar a conta conectada.
- `logs/`, `*.log` e `*.jsonl`. Os registros podem incluir mensagens, respostas, fontes, trechos de documentos e eventos de envio.
- `.venv/`, caches, bancos SQLite, arquivos temporários e `dados_rag/*.json`. O índice contém trechos e embeddings dos materiais locais e pode ser reconstruído com `preparar_ambiente.ps1` ou `indexar_pdfs.py`.
- PDFs e arquivos colocados em `documents/local/` ou `documents/privado/`. Antes de compartilhar qualquer outro material em `documents/`, confirme que ele pode ser publicado e que não contém dados pessoais ou conteúdo restrito.

As regras correspondentes estão em `.gitignore`. O arquivo de exemplo de configuração é explicitamente permitido; não copie valores secretos para ele.

## Conferência antes de enviar alterações

Na pasta `Chatbot`, execute:

```powershell
git status --short
git status --short --ignored
git ls-files
git diff --check
```

Confirme que não aparecem `.env.extensao`, `sessao_whatsapp.db`, arquivos de `logs/`, bancos, índices locais ou documentos privados. Para verificar uma regra específica do `.gitignore`:

```powershell
git check-ignore -v -- .env.extensao sessao_whatsapp.db logs/interacoes_ia.jsonl dados_rag/indice.json
```

O resultado deve mostrar a regra que ignora cada caminho. `git status --short --ignored` mostra arquivos ignorados, mas `git ls-files` verifica o que já está rastreado. O `.gitignore` só impede a inclusão de arquivos ainda não rastreados; não remove um arquivo que já foi adicionado ao histórico.

Antes de criar um commit, revise também os arquivos staged:

```powershell
git diff --cached --name-only
git diff --cached
```

Não inclua dados reais de conversas, capturas de tela com números, identificadores, QR codes, tokens ou credenciais. Use exemplos fictícios e remova dados pessoais dos logs antes de compartilhar diagnósticos.

## Se um segredo já foi rastreado ou enviado

Apagar o arquivo numa alteração posterior não remove cópias de commits anteriores nem de clones. Revogue ou substitua imediatamente a credencial exposta. Para parar de rastrear um arquivo que deve permanecer no computador, remova-o do índice do Git sem apagar a cópia local:

```powershell
git rm --cached -- .env.extensao
```

Repita apenas para o caminho que foi identificado e revise o histórico do repositório antes de torná-lo público. Uma sessão do WhatsApp exposta deve ser desconectada em **Aparelhos conectados** e pareada novamente.

## O que pode ser compartilhado

Em geral, código-fonte, documentação técnica, `requirements.txt` e `.env.extensao.example` sem segredos podem ser versionados. Materiais em `documents/` devem ser avaliados um por um: o `.gitignore` bloqueia PDFs por padrão, mas arquivos de texto podem conter conteúdo privado ou protegido. Só force a inclusão de um arquivo ignorado depois de confirmar que a publicação é permitida.
