# MIRA — Base de conhecimento / Esperança Garcia

**Versão da distribuição:** 1.2.1 estável (conteúdo da 1.2.0 pós-auditoria, preservado)  
**Data:** 2026-11-10  
**Escopo:** apenas conteúdo e personalidade, **sem backend, sem API, sem código de chatbot**.

## Distribuição estável 1.2.1

Esta revisão somente identifica e documenta a distribuição final. Não altera as 60 respostas, os dez fatos, as cinco fontes, as lacunas ou as regras de personalidade. `VERSAO.json` identifica a release; a matriz mantém sua versão de origem 1.2.0 e o contrato declarativo mantém sua versão própria 1.1.0 e compatibilidade declarada com o conteúdo 1.2.0. Esses identificadores não foram reescritos retroativamente.

Leia `RELEASE_NOTES_v1.2.1.md` para estrutura, limites documentais, validações e utilização. `MANIFESTO_SHA256_v1.2.1.json` registra o estado final dos arquivos ativos, com caminhos de origem e correspondência no pacote. Seu próprio hash é excluído para evitar autorreferência; sua cópia dentro do ZIP é conferida separadamente na verificação do pacote.

O ZIP fica em `../distribuicoes/MIRA_Esperanca_Garcia_v1.2.1.zip`, acompanhado de hash SHA-256 e certificado de verificação. No ZIP, os cinco relatórios históricos ficam em `documentacao/historico/` e o resultado dos testes em `documentacao/validacao/`. Na pasta de trabalho, os relatórios continuam nos caminhos originais citados abaixo. Backups, arquivos temporários e o script dependente desses backups não fazem parte do ZIP. O comando da suíte completa continua válido somente no workspace original com os backups preservados.

## Estrutura
- `perfil.json`: metadados da personagem
- `fatos_historicos.json`: afirmações rastreáveis e IDs de fontes
- `fontes.json`: bibliografia e links
- `lacunas_e_hipoteses.json`: informações não estabelecidas
- `personalidade.md`: instruções de conversa imersiva
- `regras_de_seguranca.md`: limites éticos e históricos
- `perguntas_respostas.json`: quatro exemplos originais revisados, como subconjunto da coleção principal
- `perguntas_respostas_expandidas.json`: coleção principal com 60 perguntas educativas; não são provas históricas
- `matriz_perguntas_v1.2.0.json`: seis categorias, objetivos e vínculos documentais planejados para os 60 registros
- `contrato_resposta.json`: contrato declarativo 1.1.0, compatível com a base 1.2.0
- `validar_consistencia.py`: testes offline de estrutura, vínculos, apresentação e preservação
- `testes_validacao.json`: casos para futura avaliação
- `documentos/carta_1770_REFERENCIA.md`: link para transcrição publicada

## Para integrar depois
1. Ler `personalidade.md` como instruções de comportamento.
2. Indexar os fatos e, após verificar direitos e edição, a transcrição da carta.
3. Vincular cada resposta factual aos IDs das fontes.
4. Aplicar os testes de validação; submeter a revisão humana.
5. Não tratar exemplos de diálogo como documentos históricos.

## Observações
- Ano de nascimento 1751 é reportado pela OAB, mas esta base não contém registro de nascimento.
- O título de primeira advogada é reconhecimento institucional histórico e simbólico, não prova de habilitação profissional no século XVIII.
- O nome do governador é apoiado em fonte institucional secundária; a carta publicada utiliza tratamento de autoridade, sem nomear o destinatário no trecho transcrito.
- Os fatos e fontes devem ser revisados antes de publicação.

## Referências clicáveis (1.1.0)
A fala e o rodapé são descritos em `esperanca_garcia/personalidade.md`; o contrato declarativo está em `esperanca_garcia/contrato_resposta.json`. Os exemplos incluem a fala separada e a apresentação completa. Nenhuma API, backend ou interface foi criada.

Execute na raiz do projeto:

```powershell
python MIRA_BASE_CONHECIMENTO/esperanca_garcia/validar_consistencia.py
```

O validador é offline: verifica estrutura e vínculos, não acessibilidade atual das páginas nem verdade histórica. Os cenários de `testes_validacao.json` precisam de avaliação humana ou de um futuro sistema de conversa. Consulte `esperanca_garcia/ALTERACOES_2026-11-10.md` para auditoria da versão 1.1.0.

Originais: `backups/2026-11-10_antes_referencias/`, com manifesto SHA-256. Para restaurar, copie os arquivos correspondentes dessa pasta para seus caminhos originais; preserve separadamente os novos arquivos antes de decidir removê-los.

## Coleção educativa 1.2.0

| Categoria | Quantidade |
|---|---:|
| Carta de 1770 e seus pedidos | 10 |
| Família, deslocamento e trabalho | 10 |
| Violência e reivindicações documentadas | 10 |
| Religiosidade na carta | 10 |
| Reconhecimento e preservação da memória | 10 |
| Fontes, lacunas e representação educativa | 10 |
| **Total** | **60** |

Os quatro exemplos originais foram preservados, revisados e identificados como `EGQA001`, `EGQA011`, `EGQA051` e `EGQA041`. Estão incluídos nos 60; não some os dois arquivos como se fossem 64 perguntas. Cada registro tem ID estável, categoria, objetivo educativo, fatos e lacunas, além dos campos do contrato e da apresentação completa.

Os dez fatos e as cinco fontes foram preservados. Após as correções autorizadas da auditoria, as respostas se distribuem em 30 sustentadas, 13 parcialmente sustentadas, 14 de limitação documental e três de orientação educativa sem conteúdo histórico. As lacunas não foram preenchidas com ficção. A categoria de religiosidade limita-se aos trechos e pedidos cadastrados, sem presumir vivência interior ou cerimônias.

`resposta` contém somente a fala; `fontes_utilizadas` contém ID, título e URL exatos do cadastro; `status_verificacao` descreve a sustentação documental. `resposta_modelo` reúne fala e rodapé clicável, com até três fontes. `nota_limitacao` acompanha registros com lacunas, na fala e como nota final do rodapé. Sem fatos e sem lacunas, a orientação educativa dispensa rodapé. A apresentação completa deve corresponder exatamente aos campos separados.

O mesmo comando acima executa **14 testes**, incluindo **30 casos negativos de consistência**, quatro casos negativos de matriz, leitura JSON estrita e três verificações adicionais de preservação e rastreabilidade pós-auditoria. A execução não grava arquivos e não utiliza rede. Há 15 rubricas pedagógicas declarativas em `testes_validacao.json`; elas não equivalem a testes executados contra um modelo de conversa. Não há backend, API, interface ou integração com aplicativos.

Backup completo da 1.1.0: `backups/2026-11-10_v1.1.0_antes_v1.2.0/`, com 26 arquivos e manifesto SHA-256, incluindo o backup anterior. O manifesto não inclui a si próprio. Para restaurar a 1.1.0, copie os caminhos relativos do manifesto para a raiz desta base; os arquivos exclusivos da 1.2.0 devem ser arquivados separadamente antes de eventual remoção. Não misture o conteúdo de versões diferentes.

Auditoria, resultados e pendências: `esperanca_garcia/ALTERACOES_v1.2.0.md`. Os pareceres anteriores permanecem como registros de suas respectivas versões, não como descrição da situação atual.

## Correções pós-auditoria da 1.2.0

O relatório `esperanca_garcia/AUDITORIA_V1.2.0.md` permanece intacto como avaliação do estado anterior. As oito correções autorizadas, os resultados da validação e a reavaliação pelos sete critérios estão em `esperanca_garcia/CORRECOES_POS_AUDITORIA_V1.2.0.md`. As outras 52 respostas foram preservadas integralmente, incluindo metadados e rodapés. A coleção continua com 60 perguntas e dez por categoria.

Foi acrescentada apenas a lacuna EGL011, específica para o percurso do marido, sem alterar EGL007 ou as demais lacunas existentes. O contrato mantém seus campos e regras; a descrição dos IDs foi estendida até EGL011. EGQA039 mantém inclusive sua fala e seu rodapé originais, com correção apenas do vínculo de lacuna. EGQA055 usa a redação conservadora, sem fonte nova. Os dez fatos e as cinco fontes continuam intactos.

Backup completo anterior às correções: `backups/2026-11-10_v1.2.0_antes_correcoes_pos_auditoria/`, com 57 arquivos, incluindo o relatório de auditoria e todos os backups anteriores, acompanhado de manifesto SHA-256. Para restaurar o estado auditado, utilize seus caminhos relativos, arquivando separadamente os arquivos criados após esse backup antes de eventual remoção.
