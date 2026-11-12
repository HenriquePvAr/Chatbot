# MIRA — Clara Camarão: aplicação controlada das correções

**Etapa 6 — 11/11/2026.** Aplicadas exatamente as seis propostas da [auditoria da etapa 5](AUDITORIA_RESPOSTAS_ETAPA5.md), após autorização humana expressa. As redações foram extraídas do próprio relatório, sem reescrita adicional.

Foram modificados somente `perguntas_respostas.json` e `matriz_perguntas.json`. A comparação com os backups encontrou **dez mudanças de valores**: seis campos `resposta`, dois campos `uso` de CCS012, um `status_verificacao` e um `tipo_tratamento`. Os demais campos e a formatação preexistente foram preservados. A personagem **não está pronta para uso** e não foi publicada versão estável.

## Backup anterior e hashes

Antes de qualquer modificação dos dois arquivos, foram criadas cópias byte a byte em [antes_etapa6_2026-11-11/](antes_etapa6_2026-11-11/) e conferidos seus hashes. O [inventário anterior](PRESERVACAO_ANTES_ETAPA6.json) registra SHA-256 de todos os arquivos então presentes em `MIRA_BASE_CONHECIMENTO/` e `distribuicoes/`, incluindo os suportes históricos, os documentos de Clara, Esperança Garcia, backups, manifestos e distribuição.

| Arquivo | SHA-256 anterior e do backup | SHA-256 depois |
|---|---|---|
| [perguntas_respostas.json](../perguntas_respostas.json) | `d657185e27377c3519cd5120a32256026b5aa6a339256ad48f64143be9a15cd6` | `cf2a4f161f3686eaa49d562c48d8d977aa58c6bb6ac53c80ede96cbf08719e73` |
| [matriz_perguntas.json](../matriz_perguntas.json) | `53b451a853274ddf86cbb4fea07c9a38a7cfe4ba61f611cf9907b30666f4649f` | `a407ae147a840a8139a34d075a4357e4417d60ec35310cdaff84a4a977d680bd` |

Os hashes dos backups permanecem iguais aos anteriores, e as cópias foram produzidas antes da aplicação. O inventário e os backups são novos artefatos de rastreabilidade; nenhum backup anterior foi sobrescrito.

## Mudanças efetivamente aplicadas

| ID | Campo alterado | Aplicação |
|---|---|---|
| CCQ002 | `conteudo.resposta` | Substituição integral pela redação completa da proposta correspondente, conferida por igualdade exata. |
| CCQ005 | `conteudo.resposta` | Substituição integral pela redação completa da proposta correspondente, conferida por igualdade exata. |
| CCQ011 | `conteudo.resposta` | Substituição integral pela redação completa da proposta correspondente, conferida por igualdade exata. |
| CCQ012 | `conteudo.resposta` | Substituição integral pela redação completa da proposta correspondente, conferida por igualdade exata. |
| CCQ014 | `conteudo.resposta` | Substituição integral pela redação completa da proposta correspondente, conferida por igualdade exata. |
| CCQ016 | `conteudo.resposta` | Substituição integral pela redação completa da proposta correspondente, conferida por igualdade exata. |
| CCQ011 | `conteudo.fontes_utilizadas[CCS012].uso` | Descrição específica da menção a Tejucupapo na apresentação anterior à fala de Rita. |
| CCQ012 | `conteudo.fontes_utilizadas[CCS012].uso` | Descrição específica da menção a Guararapes na apresentação anterior à fala de Rita. |
| CCQ016 | `conteudo.status_verificacao` | `interpretacao_academica` → `misto`. |
| CCQ016 | `matriz_perguntas.json: tipo_tratamento` | `interpretacao_academica` → `misto`. |

Nenhum título, URL, ID, localizador ou outro campo das referências foi modificado. As referências planejadas na matriz também permaneceram intactas. O validador e os testes não foram editados: a coerência foi obtida pela mudança coordenada do status e do tratamento de CCQ016, sem desativar ou enfraquecer verificações.

## Comparação antes/depois

Os textos seguintes reproduzem integralmente os seis campos alterados. O [registro de verificação](RESULTADO_VERIFICACAO_ETAPA6.json) contém os dez caminhos estruturais exatos, valores anteriores e posteriores, hashes e saídas completas dos testes.


### CCQ002

**Antes — campo `resposta`:**

> Essas grafias aparecem em publicações diferentes: o verbete Impressões Rebeldes usa Clara Felipe Camarão; a notícia da Câmara de Natal de 2017 usa Clara Felipa Camarão; e a justificativa parlamentar publicada em 2012 usa Clara Filipa Camarão.

> A comparação confirma a diferença entre os textos, mas a pesquisa não estabeleceu por que ela ocorreu. Sem um registro de batismo conferido, não é seguro escolher uma das formas como o nome batismal verdadeiro.

**Depois — campo `resposta`:**

> A pesquisa não estabeleceu por que essas grafias são diferentes. O que foi possível conferir é que elas aparecem em publicações distintas: o verbete Impressões Rebeldes usa Clara Felipe Camarão; a notícia da Câmara de Natal de 2017 usa Clara Felipa Camarão; e a justificativa parlamentar publicada em 2012 usa Clara Filipa Camarão.

> Comparar os textos permite reconhecer essa variação, mas não descobrir sua causa. Como nenhum registro de batismo foi conferido nesta pesquisa, não é seguro afirmar qual dessas formas corresponderia ao nome registrado no batismo.

### CCQ005

**Antes — campo `resposta`:**

> Falta um registro de nascimento conferido, e as formulações consultadas não permitem construir uma cronologia segura. O verbete Impressões Rebeldes sugere um período, enquanto a justificativa parlamentar publicada em 2012 apresenta uma tensão interna.

> Essa justificativa situa o nascimento na metade do século XVII, mas também atribui a Clara uma atuação em Porto Calvo em 1637. A pesquisa registra o problema, sem tentar consertar o texto por adivinhação. Também não calcula a idade de Clara a partir de um episódio cuja participação individual continua sem comprovação suficiente.

**Depois — campo `resposta`:**

> Não há um registro de nascimento conferido que permita fixar uma data ou calcular a idade de Clara. As publicações consultadas também não oferecem uma sequência segura de datas: o verbete Impressões Rebeldes sugere um período de nascimento, e a justificativa parlamentar publicada em 2012 contém informações que não combinam entre si.

> Essa justificativa situa o nascimento na metade do século XVII, aproximadamente em torno de 1650, mas também atribui a Clara uma atuação em Porto Calvo em 1637, antes desse período. A pesquisa registra a inconsistência sem escolher uma correção por suposição. Também não calcula sua idade com base em um episódio cuja participação individual ainda não foi suficientemente comprovada.

### CCQ011

**Antes — campo `resposta`:**

> A principal limitação é a falta de uma passagem de época conferida nesta pesquisa que identifique Clara individualmente em Tejucupapo. O verbete Impressões Rebeldes associa seu nome à tradição sobre a batalha, e a apresentação da homenagem no Senado de 2023 também menciona essa participação.

> Esses textos mostram que a associação faz parte de narrativas posteriores. Eles não equivalem a um testemunho do conflito colonial. Reconhecer a memória da participação de mulheres em Tejucupapo não permite concluir, sem outra evidência, que Clara esteve pessoalmente entre elas.

**Depois — campo `resposta`:**

> A principal limitação é a falta de um texto da época, conferido nesta pesquisa, que identifique Clara individualmente em Tejucupapo. O verbete Impressões Rebeldes associa seu nome à tradição sobre a batalha. A apresentação da homenagem no Senado, em 2023, antes da fala de Rita Potyguara, também atribui essa participação a Clara.

> Esses registros mostram que a associação aparece em narrativas posteriores; não são testemunhos do conflito colonial. Reconhecer a memória da participação de mulheres em Tejucupapo não permite concluir, sem outra evidência, que Clara esteve pessoalmente entre elas.

**CCS012 — campo `uso`:**

- Antes: Entrega e fala contemporânea; sem generalização para todo um povo ou comprovação colonial.
- Depois: Menção a Tejucupapo na apresentação da homenagem, antes da fala de Rita; atribuição de 2023, sem comprovação colonial individual.


### CCQ012

**Antes — campo `resposta`:**

> A presença e a ação militar individual de Clara nas batalhas dos Guararapes não foram estabelecidas com segurança nesta pesquisa. O verbete Impressões Rebeldes apresenta sua participação como hipótese; o Memorial da Assembleia e a apresentação no Senado fazem atribuições posteriores.

> É preciso examinar cada batalha e cada data com evidências próprias. A trajetória de Filipe Camarão não comprova automaticamente a de Clara, e os registros de homenagem não substituem documentos sobre sua atuação individual.

**Depois — campo `resposta`:**

> A presença e a ação militar individual de Clara nas batalhas dos Guararapes não foram estabelecidas com segurança nesta pesquisa. O verbete Impressões Rebeldes apresenta como hipótese sua participação na primeira batalha. O Memorial da Assembleia e a apresentação da homenagem no Senado, antes da fala de Rita Potyguara, também fazem atribuições posteriores de participação.

> Cada batalha e cada data precisam ser examinadas com evidências próprias. A trajetória de Filipe Camarão não comprova automaticamente a de Clara, e os registros de homenagem não substituem documentos sobre sua atuação individual.

**CCS012 — campo `uso`:**

- Antes: Entrega e fala contemporânea; sem generalização para todo um povo ou comprovação colonial.
- Depois: Menção a Guararapes na apresentação da homenagem, antes da fala de Rita; atribuição de 2023, sem comprovação colonial individual.


### CCQ014

**Antes — campo `resposta`:**

> Fagundes interpreta o destaque dado a Clara por Loreto Couto como uma valorização posterior de sua figura. Ele compara essa narrativa elogiosa com as menções mais limitadas das crônicas anteriores.

> Essa é uma análise sobre a construção da memória heroica: como autores de outros tempos dão destaque e significado a uma personagem. Ela não comprova cada feito militar narrado, mas também não demonstra que toda participação de Clara seja falsa.

**Depois — campo `resposta`:**

> Fagundes observa que Loreto Couto dá grande destaque aos feitos militares atribuídos a Clara, enquanto as crônicas anteriores trazem menções mais breves. Para o pesquisador, esse contraste ajuda a analisar como sua figura ganhou importância em uma narrativa posterior.

> Essa é uma interpretação sobre a construção da memória heroica: o modo como autores de outros tempos elogiam uma pessoa e dão significado à sua trajetória. A análise não comprova cada feito militar narrado, mas também não demonstra que toda participação de Clara seja falsa.

### CCQ016

**Antes — campo `resposta`:**

> Porque vários textos podem transmitir uma mesma informação recebida de outro autor. Se um texto usa o relato de outro, a repetição não acrescenta, por si só, uma nova evidência sobre o acontecimento.

> Fagundes reúne passagens e análises de outros autores. O trecho de Calado foi consultado diretamente nesta pesquisa, enquanto algumas outras obras foram conhecidas por meio dessas citações. É preciso distinguir quais textos foram lidos e quais são conhecidos por intermédio de outro autor.

> Para saber se os relatos oferecem evidências independentes, é preciso investigar de onde vieram as informações e como circularam entre os textos. Essa investigação continua pendente para as crônicas examinadas. A semelhança entre elas não permite concluir automaticamente que houve cópia, plágio ou confirmação independente.

**Depois — campo `resposta`:**

> Porque vários textos podem repetir uma informação recebida de um mesmo autor. Para considerar os relatos confirmações independentes, é necessário investigar se eles se apoiam em informações de origens diferentes. A repetição, sozinha, não demonstra isso.

> Na pesquisa, também é preciso separar duas questões: se um texto foi consultado diretamente e de onde veio a informação que ele apresenta. O trecho de Calado foi consultado diretamente; outras passagens foram conhecidas por meio das citações reunidas por Fagundes. Ler um texto diretamente não garante que seu relato seja independente de outros.

> O caminho pelo qual essas informações passaram de um texto a outro ainda precisa ser investigado nas crônicas examinadas. Por isso, não se pode concluir automaticamente que houve cópia, plágio ou confirmação independente. Aqui, os exemplos documentais e os limites da pesquisa ajudam a explicar um cuidado do trabalho com fontes.

**Status e planejamento:** antes `interpretacao_academica`; depois `misto`, tanto no status da resposta quanto no tratamento da matriz.


## Conferências de preservação e consistência

| Verificação | Resultado |
|---|---|
| Respostas presentes | 25, com os mesmos IDs, ordem e perguntas. |
| Campos de resposta alterados | Exatamente seis: CCQ002, CCQ005, CCQ011, CCQ012, CCQ014 e CCQ016. |
| Correspondência com as propostas | Igualdade exata entre os seis textos aplicados e os parágrafos das propostas na auditoria. |
| Campos uso alterados | Exatamente dois: CCS012 em CCQ011 e CCQ012, com os textos específicos da auditoria. |
| Status alterado | Somente CCQ016, para misto. |
| Matriz alterada | Somente tipo_tratamento de CCQ016, para misto. |
| Outras 19 respostas | Registros completos iguais aos dos backups: texto, pergunta, metadados, fontes, vínculos e status. |
| Referências | Títulos, URLs, IDs, localizadores e demais referências preservados; não houve inclusão ou exclusão. |
| Fontes e vínculos | Fontes e vínculos a fatos/lacunas mantidos; validador e testes passaram. |
| Lacunas | As mesmas 15, sem alteração de qualquer valor ou encerramento. |
| Pesquisa histórica | fatos_historicos.json, fontes.json, lacunas_e_hipoteses.json, auditoria documental e suportes históricos intactos. Nenhum fato novo cadastrado. |
| Perfil, personalidade e contrato | Sem alteração. |
| Aprovação e prontidão | Indicadores preservados; não foram ativadas aprovação editorial, prontidão ou publicação estável. |
| Esperança Garcia v1.2.1 | Nenhuma alteração, inclusive backups, manifestos e distribuição. |

Dos **184 arquivos preexistentes inventariados**, somente os dois arquivos autorizados mudaram; os **182 restantes** mantiveram seus SHA-256. A verificação abrange todo o acervo anterior e sua distribuição, e não apenas uma seleção de nomes. Nenhum arquivo anterior foi removido.

**IDs dos 19 registros integralmente preservados:** CCQ001, CCQ003, CCQ004, CCQ006, CCQ007, CCQ008, CCQ009, CCQ010, CCQ013, CCQ015, CCQ017, CCQ018, CCQ019, CCQ020, CCQ021, CCQ022, CCQ023, CCQ024, CCQ025.


As propostas mantêm relatos como atribuídos e as limitações documentais expressas. Em CCQ005, a menção aproximada a 1650 explica a expressão “metade do século XVII” presente no documento; não estabelece uma data de nascimento de Clara. Em CCQ011/CCQ012, as homenagens continuam sem valor de comprovação automática de presença individual nos conflitos. Em CCQ016, consulta direta continua distinta de independência da informação.

## Validador e todos os testes atuais de Clara

Foram executados os dois comandos documentados no README de Clara, com `-B` para evitar escrita de cache. A suíte atual inteira foi executada; cópias históricas de testes em backups e validadores de Esperança Garcia não foram executados nem alterados, pois não integram a suíte atual de Clara.


### `python -B MIRA_BASE_CONHECIMENTO/clara_camarao/validar_consistencia.py`

Código de saída: **0**.

```text
Research: 21 facts, 17 sources, 15 gaps
Planning: 25 candidate questions, 6 themes
Preliminary answers: 25 records; editorial approval pending
PASS: offline structure and links; no historical, live-URL or model-behavior verification
```


### `python -B MIRA_BASE_CONHECIMENTO/clara_camarao/testar_validacao.py`

Código de saída: **0**.

```text
test_answer_correspondence_and_traceability (__main__.PlanningTests.test_answer_correspondence_and_traceability) ... ok
test_bad_planning_is_rejected (__main__.PlanningTests.test_bad_planning_is_rejected) ... ok
test_current_bundle (__main__.PlanningTests.test_current_bundle) ... ok
test_known_source_not_authorized_for_question (__main__.PlanningTests.test_known_source_not_authorized_for_question) ... ok
test_response_contract_with_synthetic_tokens (__main__.PlanningTests.test_response_contract_with_synthetic_tokens) ... ok
test_standalone_clara_folder (__main__.PlanningTests.test_standalone_clara_folder) ... ok
test_strict_json (__main__.PlanningTests.test_strict_json) ... ok
test_variable_question_count (__main__.PlanningTests.test_variable_question_count) ... ok

----------------------------------------------------------------------
Ran 8 tests in 0.197s

OK
```


**Resultado: PASS no validador; os oito testes automatizados passaram.** A suíte existente cobre os 59 casos negativos registrados na etapa 4, além da consistência do conjunto atual, correspondência com a matriz, contrato, fontes autorizadas por pergunta, JSON estrito, isolamento e quantidade variável. A análise estrutural adicional comparou recursivamente os dois JSON com seus backups e exigiu que o conjunto de caminhos alterados fosse exatamente o autorizado.

Esses resultados comprovam os controles locais executados, sem certificar verdade histórica completa, comportamento de um modelo ou aprendizagem em sala. Não houve nova pesquisa histórica, revalidação de URLs ou inspeção visual de documentos: títulos e URLs foram mantidos como autorizado, e a conferência documental continua sendo a das auditorias anteriores.

## Arquivos criados e alterados nesta etapa

| Caminho relativo à pasta de Clara | Operação |
|---|---|
| `perguntas_respostas.json` | Alterado nos nove valores autorizados: seis respostas, dois usos e um status. |
| `matriz_perguntas.json` | Alterado somente o tratamento de CCQ016. |
| `documentacao/antes_etapa6_2026-11-11/perguntas_respostas.json` | Backup anterior criado. |
| `documentacao/antes_etapa6_2026-11-11/matriz_perguntas.json` | Backup anterior criado. |
| `documentacao/PRESERVACAO_ANTES_ETAPA6.json` | Inventário anterior e hashes dos backups. |
| `documentacao/RESULTADO_VERIFICACAO_ETAPA6.json` | Comparação exata, hashes e saídas de testes. |
| `documentacao/RELATORIO_CORRECOES_ETAPA6.md` | Este relatório. |

O script auxiliar desta aplicação fica em `tmp/aplicar_etapa6.py`. Não houve mudança de versão, geração de distribuição, desenvolvimento de backend, frontend, API ou integração.

## Pendências e recomendação para a próxima etapa

As seis propostas autorizadas foram aplicadas, mas a aplicação não substitui a revisão final. As 15 lacunas históricas permanecem; fontes indiretas, transmissão das crônicas e edição de 2004 conservam suas limitações. O README e os relatórios anteriores continuam como registros das respectivas etapas, sem reescrita fora do escopo autorizado.

Recomenda-se, após nova autorização, revisar a coleção resultante com atenção à atribuição indígena em CCQ003/CCQ019, à compreensão escolar dos conceitos em CCQ013/CCQ016/CCQ024 e à separação entre relato, hipótese, interpretação e documento contemporâneo. A revisão humana final deverá avaliar as seis correções aplicadas e a coleção completa antes de qualquer decisão posterior de uso. Não houve aplicação em turma nem avaliação de comportamento de uma interface ou modelo.

**Entrega da etapa 6 concluída. A personagem permanece preliminar e sem liberação para uso. Aguarda-se autorização para a revisão final.**
