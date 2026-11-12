# Correções pós-auditoria — MIRA / Esperança Garcia v1.2.0

Data: 10/11/2026. Escopo: aplicação das oito propostas expressamente autorizadas, preservação dos demais registros e reavaliação histórica e pedagógica. A versão da base continua 1.2.0; este documento identifica a revisão pós-auditoria. Não foi criado backend, API, interface ou integração com aplicativos.

## Backup e preservação

Antes de modificar qualquer arquivo, foi criado o backup completo `../backups/2026-11-10_v1.2.0_antes_correcoes_pos_auditoria/`, com **57 arquivos preexistentes**, incluindo `AUDITORIA_V1.2.0.md`, o README, a base e os backups anteriores. O manifesto SHA-256 registra o caminho relativo e o hash de cada arquivo copiado; não inclui a si próprio. O destino não existia e nenhum backup foi sobrescrito.

Os 57 hashes foram conferidos logo após a cópia. A verificação completa dos backups, incluindo suas cópias aninhadas, examinou **sete manifestos e 153 entradas**, sem divergências. Essas entradas incluem cópias repetidas de versões anteriores; não representam 153 documentos históricos independentes.

Somente EGQA013, EGQA018, EGQA037, EGQA038, EGQA039, EGQA041, EGQA051 e EGQA055 foram modificadas na coleção principal. As outras **52 respostas** preservam integralmente IDs, perguntas, objetivos, categorias, fatos, lacunas, tipos, falas, estados, referências, notas e rodapés. Além da comparação de todos os campos, os testes comparam o texto bruto de cada um desses 52 objetos JSON com o backup. A matriz dos 52 registros também permanece igual.

`fatos_historicos.json`, `fontes.json`, `personalidade.md` e `AUDITORIA_V1.2.0.md` permanecem idênticos ao backup, byte a byte. Os dez fatos e as cinco fontes não foram alterados ou ampliados. As dez lacunas anteriores também permanecem iguais: apenas EGL011 foi acrescentada. A auditoria original continua sendo o registro da avaliação anterior, sem reescrita retroativa.

## Alterações aplicadas e oito resultados

| ID | Alteração efetiva | Fatos, fontes e lacunas após a correção | Estado documental | Resultado da reavaliação |
|---|---|---|---|---|
| EGQA013 | Aplicada a redação autorizada que restringe a limitação da rotina a esta base. Incluída nota específica sobre a rotina e ajustado o tipo para resposta mista. | EG002 → F001; EGL006. | `parcialmente_sustentado` | APROVADA |
| EGQA018 | Aplicada a abertura direta sobre ausência de confirmação de deslocamento conjunto. Substituído o vínculo amplo de EGL007 por EGL011; nota específica sobre o percurso. | EG002 e EG006 → F001; EGL011. | `parcialmente_sustentado` | APROVADA |
| EGQA037 | Aplicada a distinção entre a pessoa responsável no caso específico e uma explicação geral sobre atribuições religiosas. Nenhuma regra religiosa foi acrescentada. | Sem fatos ou fontes utilizados; EGL009. | `sem_sustentacao_documental` | APROVADA como resposta de limitação |
| EGQA038 | Aplicada a distinção entre descrição histórica e lembrança pessoal. Mantida a ausência de descrição ritual não documentada. | Sem fatos ou fontes utilizados; EGL005 e EGL009. | `sem_sustentacao_documental` | APROVADA como resposta de limitação |
| EGQA039 | Mantidos integralmente fala, estado e rodapé. Acrescentado somente EGL005 à lista de lacunas e à matriz. | EG004, EG005 e EG006 → F001; EGL009 e EGL005. | `parcialmente_sustentado` | APROVADA |
| EGQA041 | Aplicada a redação autorizada que relaciona o título à carta, seguida do reconhecimento posterior e da distinção de habilitação. Acrescentados os fatos existentes EG003 e EG006 e a referência F001, mantendo EG007 e F002. | EG003 e EG006 → F001; EG007 → F002. | `sustentado` | APROVADA no alcance institucional explicado abaixo |
| EGQA051 | Aplicada a resposta breve pela perspectiva da representação educativa, sem comentário técnico sobre integração. | Sem fatos, lacunas ou fontes utilizados. | `nao_aplicavel` | APROVADA como orientação da representação |
| EGQA055 | Aplicada a alternativa conservadora autorizada. Retiradas as referências nominais aos jesuítas e à discussão de uma hipótese de alfabetização. Nenhuma fonte foi adicionada. | Sem fatos ou fontes utilizados; EGL004. | `sem_sustentacao_documental` | APROVADA como resposta de limitação |

As sete falas substituídas correspondem exatamente aos textos propostos na conversa e autorizados. EGQA039 conserva sua fala anterior, conforme a proposta aprovada. Não houve mudança em perguntas, IDs, categorias ou objetivos educativos. A sincronização da matriz se limita aos vínculos necessários; uma entrada cujo planejamento não mudou continua com o mesmo conteúdo.

### Lacuna específica de EGQA018

Foi criada **EGL011 — Percurso e deslocamentos do marido**, com estado `nao_confirmado_nesta_base` e o seguinte limite: esta base não confirma que o marido de Esperança tenha sido levado junto para a casa do capitão nem permite reconstruir todos os seus deslocamentos.

EGL011 é um registro de insuficiência do acervo, não um novo acontecimento histórico. Não afirma que o marido foi levado, permaneceu em um lugar determinado ou realizou um percurso específico. EGL007 continua descrevendo identificação e composição familiar, sem ampliação de significado. Somente EGQA018 utiliza EGL011 nesta revisão.

### Conferência documental de EGQA041

Foram consultadas novamente as duas publicações cadastradas, via pesquisa web em 10/11/2026:

- [F001 — Transcrição publicada da carta](https://www.oab.org.br/noticia/60795/leia-a-carta-de-esperanca-garcia-a-primeira-advogada-do-brasil): o corpo da transcrição sustenta a paráfrase dos relatos e pedidos, correspondente aos fatos existentes EG003 e EG006. Não sustenta o reconhecimento posterior.
- [F002 — Notícia do reconhecimento nacional](https://www.oab.org.br/noticia/60503/esperanca-garcia-e-reconhecida-pelo-conselho-pleno-como-a-primeira-advogada-brasileira): a abertura registra o reconhecimento pelo Conselho Pleno; a declaração institucional sobre a petição e a seção histórica relacionam a homenagem à denúncia e à reivindicação de providências. Isso sustenta a relação explicativa proposta, sem transformar todo o contexto institucional em um novo fato cadastrado.

A primeira frase da resposta combina o nexo institucional indicado por F002 com a paráfrase documental sustentada por F001. A parte seguinte explica o reconhecimento de EG007 pela perspectiva da representação. As fontes têm funções distintas e não são intercambiáveis. A distinção de habilitação delimita o que se pode inferir do reconhecimento, sem afirmar uma inexistência histórica universal de documentos ou atuação jurídica.

Não foram importadas para a resposta classificações de prioridade jurídica absoluta, interpretações normativas ou discussões de alfabetização presentes nas notícias. Não houve acesso ao manuscrito, ao processo integral de reconhecimento ou ao dossiê subjacente. As páginas foram acessadas por serviço de pesquisa, que pode apresentar versão indexada. A aprovação é relativa ao conteúdo institucional publicado e às atribuições expressas, não uma autenticação independente desses documentos subjacentes.

### Solução conservadora de EGQA055

A resposta agora declara apenas a insuficiência desta base para identificar quem ensinou Esperança a escrever. A referência genérica a não apresentar possibilidade como certeza é uma regra de cautela, sem enunciar uma hipótese específica sobre sua alfabetização. F003 não foi acrescentada ao rodapé e nenhuma pessoa ou grupo recebeu atribuição histórica. O registro EGL004 foi preservado em seu conteúdo original, mas a resposta não reproduz sua hipótese nominal. A pendência de rastrear a origem de uma hipótese na fala foi eliminada pela retirada dessa alusão, sem alegar que a questão histórica foi resolvida.

## Campos, apresentação e sincronização

`resposta` contém somente a fala; `fontes_utilizadas` mantém metadados exatos das fontes cadastradas. Os rodapés foram recompostos apenas nos registros corrigidos, com links Markdown clicáveis, notas documentais quando há lacunas e até três referências. EGQA041 utiliza duas; EGQA013, EGQA018 e EGQA039 utilizam uma; EGQA037, EGQA038 e EGQA055 mantêm apenas nota de limitação; EGQA051 continua sem rodapé histórico. O rodapé de EGQA039 permaneceu literalmente igual.

Os quatro exemplos canônicos continuam sendo EGQA001, EGQA011, EGQA051 e EGQA041. Os dois primeiros foram preservados, e os dois últimos foram sincronizados com a coleção principal. Não são registros adicionais. A matriz permanece compatível com os 60 registros e mantém dez perguntas em cada uma das seis categorias.

O contrato continua na versão própria 1.1.0, compatível com a base 1.2.0. Sua única mudança é a descrição dos IDs de lacuna, estendida de EGL010 até EGL011. Campos obrigatórios, estados, limite de referências e regras de apresentação foram preservados.

Distribuição atual: **30 respostas sustentadas, 13 parcialmente sustentadas, 14 de limitação documental e três de orientação educativa**. Há 39 respostas com uma referência, quatro com duas e 17 sem referências. A mudança de distribuição decorre do reconhecimento explícito da lacuna em EGQA013 e da inclusão pertinente de F001 em EGQA041, não da criação de fatos ou fontes.

## Reavaliação individual pelos sete critérios

Critérios iguais aos da auditoria original: **H** — fidelidade histórica; **F** — correspondência entre afirmação e fonte; **P** — primeira pessoa; **I** — ausência de invenção; **C** — clareza e qualidade pedagógica; **R** — rodapé; **L** — lacunas. OK significa adequado no escopo avaliado; NA significa que não há afirmação histórica positiva ou lacuna pertinente naquele critério.

| ID | H | F | P | I | C | R | L | Justificativa da nova avaliação | Classificação |
|---|---|---|---|---|---|---|---|---|---|
| EGQA013 | OK | OK | OK | OK | OK | OK | OK | O relato permanece atribuído à carta; a ausência de detalhes é delimitada ao acervo e ligada a EGL006. F001 sustenta a ocupação, não a rotina desconhecida. A resposta não cria tarefas. | APROVADA |
| EGQA018 | OK | OK | OK | OK | OK | OK | OK | A abertura responde diretamente e não transforma incerteza em negativa histórica. A parte documentada mantém seus fatos e fonte; EGL011 representa a lacuna específica sem alterar EGL007. Não se cria um itinerário. | APROVADA |
| EGQA037 | NA | NA | OK | OK | OK | OK | OK | Distingue indivíduo desconhecido de contexto religioso geral. Não inventa celebrante, padrinhos ou regras religiosas. A ausência de fonte é apropriada para o limite explicitado e não há referência genérica. | APROVADA |
| EGQA038 | NA | NA | OK | OK | OK | OK | OK | Diferencia contextualização e experiência pessoal, sem produzir cena ou ritual. Reconhece a necessidade de fonte específica para uma futura descrição geral, mantendo as lacunas e a nota. | APROVADA |
| EGQA039 | OK | OK | OK | OK | OK | OK | OK | A síntese documental é a mesma anteriormente aceita; o limite sobre sentimentos íntimos passa a ter vínculo explícito com EGL005, além de EGL009. Fala e rodapé não foram alterados. | APROVADA |
| EGQA041 | OK | OK | OK | OK | OK | OK | OK | O nexo entre a petição e o reconhecimento foi confrontado com F002; os detalhes da carta têm apoio em F001. A representação explica o evento posterior sem alegar experiência vivida ou habilitação profissional. | APROVADA |
| EGQA051 | NA | NA | OK | OK | OK | OK | NA | Responde de forma direta pela identidade educativa, sem promessa técnica nem testemunho histórico. O estado editorial e a ausência de rodapé são coerentes. | APROVADA |
| EGQA055 | NA | NA | OK | OK | OK | OK | OK | Não afirma quem alfabetizou Esperança, não menciona hipótese específica e não adiciona fonte como comprovação indevida. A incerteza local está clara e o rodapé de limitação é adequado. | APROVADA |

**Resultado: oito registros aprovados no escopo de suas respostas corrigidas, sem pendência documental ou pedagógica impeditiva identificada nesses oito textos.** Essa conclusão não transforma os estados `sem_sustentacao_documental` em afirmações historicamente comprovadas nem elimina as lacunas. As outras 52 respostas não foram reescritas ou submetidas a nova classificação: permanecem com a aprovação da auditoria original.

## Validação e hashes

Comando executado na raiz do projeto:

```powershell
python MIRA_BASE_CONHECIMENTO/esperanca_garcia/validar_consistencia.py
```

Resultado da suíte completa: **14 testes aprovados, zero falhas e zero erros**. Foram mantidos todos os 11 testes anteriores, inclusive os 30 subcasos negativos e os quatro subcasos de divergência da matriz. Foram acrescentados três testes:

1. Preservação integral das 52 respostas, por campos e texto bruto, e preservação de suas entradas de matriz.
2. Preservação byte a byte de fatos, fontes, personalidade e auditoria, igualdade das dez lacunas anteriores e invariância das regras do contrato.
3. Rastreabilidade específica de EGQA013, EGQA018, EGQA039, EGQA041, EGQA051 e EGQA055, incluindo a solução conservadora sem hipótese nominal ou nova fonte.

A suíte também verifica o manifesto de 57 arquivos do novo backup, além dos manifestos anteriores de 26 e 11 arquivos. Em conferência adicional, todos os sete manifestos presentes na árvore de backups, inclusive cópias aninhadas, foram lidos e suas 153 entradas tiveram hashes conferidos, sem divergência.

A aprovação dos testes não substitui o cotejo documental e a avaliação pedagógica apresentados acima. A validação não usa rede, não grava arquivos e não executa um modelo conversacional.

## Arquivos afetados

- `perguntas_respostas_expandidas.json`: somente os oito registros autorizados.
- `perguntas_respostas.json`: EGQA041 e EGQA051 sincronizados; EGQA001 e EGQA011 preservados.
- `matriz_perguntas_v1.2.0.json`: vínculos atualizados em EGQA013, EGQA018, EGQA039 e EGQA041; demais entradas preservadas.
- `lacunas_e_hipoteses.json`: apenas inclusão de EGL011, sem modificar as dez anteriores.
- `contrato_resposta.json`: apenas atualização do intervalo descritivo de IDs de lacuna.
- `validar_consistencia.py`: três testes adicionais e inclusão do novo manifesto na verificação.
- `../README.md`: contagens atuais, comando de validação e referência ao estado pós-auditoria.
- `CORRECOES_POS_AUDITORIA_V1.2.0.md`: este registro e reavaliação.
- Novo backup completo com manifesto SHA-256.

Os relatórios de versões anteriores foram preservados e devem ser lidos como registros dos estados que avaliaram. Nenhuma alteração foi aplicada aos dez fatos, cinco fontes, personalidade, perfil, regras de integridade, rubricas pedagógicas ou referência documental da carta.

## Limitações remanescentes

Permanecem desconhecidos neste acervo os percursos completos da família, o resultado dos pedidos e demais temas explicitamente registrados nas lacunas. A alfabetização não foi estabelecida: apenas se retirou uma alusão que exigia melhor rastreabilidade. Atribuições religiosas gerais também não foram acrescentadas sem documentação. Essas limitações são reconhecidas nas respostas e não foram ocultadas para obter aprovação.

A conferência institucional não equivale a exame do manuscrito, de um processo original ou a levantamento historiográfico independente. Para ampliar a base, será necessária documentação própria. A avaliação da coleção inteira para uma faixa etária ou contexto escolar específico continua sendo recomendação geral da auditoria, não uma pendência factual resolvida por esta revisão. Não houve nova avaliação de uso com estudantes nem teste contra uma IA em execução.
