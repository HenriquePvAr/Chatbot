# MIRA — Esperança Garcia: release estável 1.2.1

Data: 10/11/2026. Tipo de revisão: identificação, documentação, integridade e empacotamento. A edição de conteúdo é a 1.2.0 após auditoria, oito correções autorizadas e reavaliação. A estabilidade se refere ao estado distribuído e ao escopo validado, não à eliminação das lacunas históricas.

## Conteúdo preservado

As 60 respostas, seus IDs e metadados, os dez fatos históricos, as cinco fontes, as onze lacunas e a personalidade permanecem sem alteração, byte a byte nos respectivos arquivos. A matriz, os quatro exemplos canônicos, as regras de integridade, o contrato e o script de validação também foram preservados. A auditoria e os relatórios anteriores não foram reescritos.

A identificação da distribuição está em `VERSAO.json` e no README. Permanecem os identificadores de origem da matriz (`1.2.0`) e do contrato (`1.1.0`, compatível com o conteúdo `1.2.0`), inclusive o nome `matriz_perguntas_v1.2.0.json`. A distribuição 1.2.1 utiliza esse mesmo conteúdo e essas mesmas regras. Não houve renomeação de arquivos referenciados pela personalidade ou pelo validador.

## Estrutura do ZIP

O pacote possui uma pasta raiz `MIRA_Esperanca_Garcia_v1.2.1/`:

```text
MIRA_Esperanca_Garcia_v1.2.1/
  README.md
  VERSAO.json
  RELEASE_NOTES_v1.2.1.md
  MANIFESTO_SHA256_v1.2.1.json
  esperanca_garcia/
    perfil.json
    fatos_historicos.json
    fontes.json
    lacunas_e_hipoteses.json
    personalidade.md
    regras_de_seguranca.md
    contrato_resposta.json
    matriz_perguntas_v1.2.0.json
    perguntas_respostas.json
    perguntas_respostas_expandidas.json
    testes_validacao.json
    documentos/carta_1770_REFERENCIA.md
  documentacao/
    historico/
      REVISAO_2026-11-06.md
      ALTERACOES_2026-11-10.md
      ALTERACOES_v1.2.0.md
      AUDITORIA_V1.2.0.md
      CORRECOES_POS_AUDITORIA_V1.2.0.md
    validacao/
      RESULTADO_VALIDACAO_v1.2.1.txt
```

O manifesto mapeia cada caminho de origem para seu caminho dentro dessa pasta raiz. A reorganização é somente do pacote: os relatórios continuam intactos nos caminhos originais do workspace. Seus links relativos e referências a backups descrevem a estrutura de trabalho da época e devem ser interpretados como registros históricos, não como arquivos ausentes necessários à integração.

Foram excluídos backups históricos, manifestos desses backups, caches, temporários e artefatos de distribuição anteriores. O validador Python original continua no workspace e é identificado pelo manifesto, mas não é incluído no ZIP: a suíte completa depende dos backups e de seus caminhos históricos. Nenhum código de backend, API, interface, integração ou serviço executável foi criado ou distribuído. `testes_validacao.json` contém rubricas declarativas, não um serviço ou um teste de conversa em execução.

## Organização da coleção

| Categoria | Registros |
|---|---:|
| Carta de 1770 e seus pedidos | 10 |
| Família, deslocamento e trabalho | 10 |
| Violência e reivindicações documentadas | 10 |
| Religiosidade na carta | 10 |
| Reconhecimento e preservação da memória | 10 |
| Fontes, lacunas e representação educativa | 10 |
| **Total** | **60** |

Os IDs são EGQA001–EGQA060. Os quatro exemplos canônicos são um subconjunto dos 60 e não devem ser contados como perguntas adicionais. EGQA013, EGQA018, EGQA037, EGQA038, EGQA039, EGQA041, EGQA051 e EGQA055 mantêm as correções aprovadas e foram novamente conferidos contra a matriz. Os exemplos EGQA041 e EGQA051 também permanecem sincronizados com o arquivo canônico.

Distribuição documental preservada: 30 respostas sustentadas, 13 parcialmente sustentadas, 14 de limitação documental e três de orientação educativa sem afirmação histórica positiva. O reconhecimento de limites é parte do conteúdo aprovado, não uma lacuna a preencher automaticamente.

## Validação desta release

A suíte completa existente foi executada novamente no workspace original, sem alteração de código:

```powershell
python MIRA_BASE_CONHECIMENTO/esperanca_garcia/validar_consistencia.py
```

Resultado: **14 testes aprovados, zero falhas e zero erros**, incluindo 30 subcasos negativos, quatro divergências simuladas da matriz e as verificações pós-auditoria. O registro da execução acompanha o pacote. Os testes confirmam estrutura, IDs, distribuição, duplicações normalizadas, vínculos documentais, apresentação dos rodapés, sincronização dos exemplos e preservação das 52 respostas não corrigidas e dos documentos protegidos nas etapas anteriores.

Na preparação da distribuição também foram conferidos: presença exata dos 60 IDs, dez itens por categoria, dez fatos, cinco fontes, os oito registros corrigidos contra a matriz, os quatro exemplos canônicos e a invariância dos arquivos de conteúdo desde o início desta etapa. Os hashes dos backups existentes foram novamente verificados no workspace. Essas verificações não transformam testes estruturais em autenticação histórica.

O ZIP é verificado por CRC, ausência de entradas duplicadas ou caminhos inseguros, lista exata de arquivos esperados e SHA-256 de cada entrada contra o manifesto. O manifesto contido no ZIP é comparado byte a byte ao manifesto de origem. Ao final são gerados o SHA-256 externo do ZIP e `VERIFICACAO_PACOTE_v1.2.1.json`, com os resultados e o inventário do pacote.

## Manifesto e integridade

`MANIFESTO_SHA256_v1.2.1.json` descreve o estado final dos arquivos ativos da base: caminho de origem, tamanho, SHA-256, inclusão ou não no ZIP e caminho de destino quando incluído. Os backups e a pasta de distribuição ficam fora desse escopo. O manifesto não inclui a si próprio; esse procedimento evita uma dependência circular de hashes. O ZIP inclui o manifesto e sua integridade é conferida externamente.

Os artefatos finais ficam em `../distribuicoes/`, fora da base:

- `MIRA_Esperanca_Garcia_v1.2.1.zip`;
- `MIRA_Esperanca_Garcia_v1.2.1.zip.sha256`;
- `VERIFICACAO_PACOTE_v1.2.1.json`.

Para comparar o hash do ZIP no PowerShell:

```powershell
Get-FileHash -LiteralPath .\distribuicoes\MIRA_Esperanca_Garcia_v1.2.1.zip -Algorithm SHA256
Get-Content -LiteralPath .\distribuicoes\MIRA_Esperanca_Garcia_v1.2.1.zip.sha256
```

Execute esses comandos na raiz do projeto MIRA. O hash retornado deve corresponder ao valor registrado no arquivo de conferência. Hashes verificam identidade dos bytes; não são assinatura digital, prova de autoria ou confirmação de verdade histórica.

## Orientações para futura utilização

1. Leia `VERSAO.json` para identificar a distribuição e `contrato_resposta.json` para os campos e estados. Leia conjuntamente personalidade e regras de integridade.
2. Utilize `perguntas_respostas_expandidas.json` como coleção principal. Os exemplos são paráfrases educativas, não documentos primários e não devem substituir os fatos e suas evidências.
3. Preserve a separação entre `resposta`, `fontes_utilizadas` e `status_verificacao`. `resposta_modelo` já contém a apresentação completa; não acrescente outro rodapé a esse campo.
4. Quando compuser uma apresentação a partir dos campos separados, mantenha o rodapé no final, com títulos e URLs exatos do cadastro e até três fontes diretamente pertinentes. Não use fonte genérica para sustentar informação ausente.
5. Respeite as notas de limitação e as lacunas. Um estado parcial não autoriza completar o trecho desconhecido; ausência de confirmação nesta base não significa inexistência universal de documento.
6. Preserve a primeira pessoa apenas no escopo permitido. Acontecimentos posteriores são explicados pela representação educativa, sem criar experiências pessoais.
7. Para auditar a evolução, consulte `documentacao/historico/`. Para reproduzir todos os 14 testes, utilize o workspace original com o script e os backups: o ZIP declarativo não é uma cópia desse ambiente de validação.

Não foi especificado ou implantado um mecanismo de recuperação, geração ou integração. Qualquer futuro sistema deverá respeitar o contrato e verificar a correspondência semântica entre afirmação e fonte, além das relações entre IDs.

## Limitações documentais preservadas

A base utiliza uma transcrição publicada e notícias institucionais; a estabilidade da release não afirma acesso ao manuscrito ou pesquisa historiográfica exaustiva. As cinco fontes pertencem à mesma instituição e não equivalem a cinco confirmações independentes. Não houve nova pesquisa histórica nesta etapa de empacotamento.

Permanecem os limites registrados sobre resultado dos pedidos, percursos familiares, identificação completa da família, rotina, alfabetização, aparência, morte, práticas religiosas específicas e sentimentos íntimos. F004 continua sem fato associado. As ressalvas sobre passagens anacrônicas de F003 permanecem em vigor. URLs e conteúdos publicados podem mudar; devem ser reavaliados antes de ampliação de escopo ou uso público que dependa de disponibilidade atual.

A auditoria aprovou o uso educativo no escopo descrito, incluindo respostas que reconhecem ausência documental. A avaliação de adequação a uma faixa etária ou contexto escolar específico e testes com usuários continuam recomendados. Nenhuma dessas limitações foi removida para atribuir o rótulo estável à distribuição.
