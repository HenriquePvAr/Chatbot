# MIRA — Clara Camarão: BASE TEXTUAL 1.0.0

Base textual revisada, com 25 respostas fixas e 15 lacunas históricas preservadas.
Comportamento de modelo de IA ainda não validado. Integração não realizada.
**Personagem não liberada para uso público. Entrega à equipe técnica aguardando aprovação humana.**

Leia o [guia de integração](documentacao/GUIA_INTEGRACAO_BASE_TEXTUAL_v1.0.0.md), os [metadados de distribuição](VERSAO.json) e o [índice de auditoria](documentacao/INDICE_AUDITORIA.md).
Estabilidade refere-se à coleção textual, não a chatbot, geração livre ou completude biográfica.

## Arquivos

Os oito arquivos de dados e regras conservam os bytes aprovados do acervo. A coleção separa metadados da pergunta e `conteudo`, com os campos `resposta`, `fontes_utilizadas` e `status_verificacao`. Use os IDs existentes, as ressalvas integrais e até três fontes relevantes separadas da fala.

Os avisos de fases anteriores nos arquivos preservados continuam históricos; `VERSAO.json` descreve a presente distribuição textual 1.0.0. Isso não autoriza mudar regras de evidência nem ativar um chatbot. A pesquisa original permanece 0.1.0-pesquisa no acervo, fora deste pacote.

O [catálogo de cenários](testes/cenarios_comportamento_etapa7.json) serve à futura avaliação com modelo; nenhum dos 14 cenários tem comportamento de IA aprovado. As amostras negativas são dados de teste, separados da coleção educativa.

## Integridade

Confira o SHA-256 externo do ZIP e, depois de extrair em uma pasta vazia, execute:

```powershell
python -B verificar_integridade_pacote.py
```

O [manifesto](MANIFESTO_SHA256.json) cobre cada arquivo entregue, inclusive o verificador, exceto o próprio manifesto para evitar autorreferência. O checksum externo do ZIP cobre o manifesto também. O verificador não comprova comportamento de modelo, verdade histórica integral ou disponibilidade atual de URLs.

Os validadores completos e os suportes históricos permanecem no acervo de trabalho. O índice documenta referências internas de auditoria que não estão neste pacote mínimo. Não foram incluídos backups, temporários, caches, PDFs de pesquisa ou arquivos de Esperança Garcia.

Não há backend, frontend, API ou WhatsApp. Aguardar aprovação humana para entregar o pacote à equipe de integração.
