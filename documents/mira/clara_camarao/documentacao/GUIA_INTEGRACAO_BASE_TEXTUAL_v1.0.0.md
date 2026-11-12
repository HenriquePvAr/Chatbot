# MIRA — Clara Camarão: guia da base textual 1.0.0

**Base textual revisada. Comportamento de modelo de IA ainda não validado. Integração não realizada. Personagem não liberada para uso público.** O pacote preparado aguarda aprovação humana para entrega à equipe técnica. Este guia não implementa chatbot ou integração.

## Escopo da versão e precedência documental

`VERSAO.json` na raiz do pacote identifica exclusivamente a versão estável **1.0.0 da base textual**: a coleção fixa de 25 respostas revisadas, os vínculos e as regras preservadas. Estabilidade textual não significa completude biográfica, validação de IA ou aprovação para conversa pública. As 15 lacunas continuam abertas. O público provisório é o ensino fundamental II e o ensino médio.

No acervo de trabalho, os mesmos metadados de distribuição estão em `VERSAO_BASE_TEXTUAL.json`; o `VERSAO.json` da pesquisa permanece `0.1.0-pesquisa`. São escopos diferentes. O pacote contém apenas o `VERSAO.json` da base textual, sem duplicar o arquivo antigo da pesquisa.

Os arquivos de respostas, matriz, perfil, personalidade e contrato foram mantidos byte a byte. Seus avisos temporais e campos de aprovação registram as fases anteriores: por exemplo, o contrato conserva `produzir_respostas_autorizado: false` da etapa 3 e a coleção conserva os indicadores preliminares da etapa 4. As autorizações posteriores permitiram a produção, as seis correções e esta preparação textual, sem liberar conversa pública. A versão atual é descrita nos metadados do pacote e neste guia. Isso esclarece a sequência de autorizações; **não revoga regras de evidência, o contrato de resposta ou a proibição de autobiografia fictícia**.

O integrador não deve deduzir prontidão do chatbot de um número de versão nem alterar esses marcadores para ativá-lo. Antes de qualquer implementação, a equipe e a responsável pela base precisam definir e aprovar o ciclo de vida da aplicação. Nenhum indicador deste pacote autoriza entrega à equipe ou publicação automaticamente.

## Leitura e utilização da base histórica

Comece pelo `README.md`, por este guia e por `documentacao/INDICE_AUDITORIA.md`. Leia a auditoria documental junto com `fontes.json`, `fatos_historicos.json` e `lacunas_e_hipoteses.json`. A auditoria qualifica descrições antigas: houve cotejo da p. 37 de Calado e leitura de trecho da edição alternativa de 1862; Santiago, Couto, Mello, a edição de 2004 e a transmissão entre crônicas conservam as pendências registradas.

`perguntas_respostas.json.registros` é a coleção fixa para futura integração. Cada registro possui `id`, `tema_id`, `pergunta`, `fatos`, `fontes`, `lacunas` e `conteudo`. Use o ID como identidade do registro; não renumere ou reescreva perguntas para completar uma quantidade. A matriz define o planejamento, os vínculos e o tratamento de cada pergunta. CCQ016 utiliza `misto` na resposta e na matriz.

O objeto `conteudo` possui exatamente `resposta`, `fontes_utilizadas` e `status_verificacao`. A futura apresentação deve conservar o texto completo e suas ressalvas, separando fala educativa, referências e status. Não extrair só uma frase afirmativa de uma resposta que depois apresenta uma limitação.

`fatos_historicos.json` contém registros de pesquisa com sustentações, divergências e limites, e não uma lista de fatos universalmente comprovados. Não importar seus enunciados isoladamente para gerar uma biografia. `perfil.json` e `personalidade.md` delimitam a representação educativa; não fornecem pensamentos, memórias ou temperamento documentados de Clara.

## Os seis status de verificação

| Status | Interpretação e cuidado |
|---|---|
| `documentado_no_escopo_da_fonte` | Ato, fala contemporânea ou ocorrência textual confirmados no suporte e alcance indicados. Uma lei de 2017 documenta reconhecimento legal, sem comprovar batalhas coloniais. |
| `relato_historico_atribuido` | O autor identificado narra algo. A existência do relato não torna cada acontecimento uma experiência pessoal comprovada de Clara. |
| `interpretacao_academica` | Análise atribuída ao pesquisador. Manter a autoria e distinguir a interpretação dos documentos citados. |
| `limitacao_documental` | A informação não foi estabelecida com segurança neste conjunto auditado. Não equivale a afirmar que nunca ocorreu ou que não existe documento em nenhum arquivo. |
| `orientacao_sobre_representacao` | Explicação das regras e da natureza virtual educativa, sem acrescentar fato histórico. |
| `misto` | Combina alcances diferentes, explicitados nos segmentos da fala. Não é selo global de comprovação. |

Esses status descrevem a sustentação documental da resposta, não a aprovação de comportamento de uma IA. Não uniformizar todos como documentado nem inferir grau de certeza a partir da quantidade de fontes.

## Referências: até três, fora da fala

Para cada resposta fixa, use a lista já selecionada em `fontes_utilizadas`, preservando `id`, `fonte_id`, `titulo`, `url`, `localizador` e `uso`. Apresente título com o link registrado, seguido de localizador e alcance de uso; no máximo três referências relevantes. Não preencher três por obrigação, citar página inicial genérica ou acrescentar uma referência porque pertence a uma instituição conhecida.

A fala educativa fica exclusivamente em `resposta`; referências e `status_verificacao` devem aparecer separados. A maneira visual de exibi-los dependerá da futura implementação, ainda não realizada. As fontes vazias de CCQ022/CCQ025 são exceções contratuais para limite do próprio acervo e regra da representação, vinculadas a CCL011; não inventar uma referência para preencher a lista.

`CCS014_1862` identifica a edição alternativa de 1862 e mantém `fonte_id: CCS014`. Não substituir sua URL ou paginação pela edição de 2004 não consultada diretamente. Em citações de Couto, Santiago ou Mello conhecidas por Fagundes, citar o suporte efetivamente consultado e explicar a mediação. A p. 524 de Couto não foi conferida diretamente. Em CCQ011/CCQ012, CCS012 sustenta a atribuição na apresentação da homenagem, antes da fala de Rita; não confundir os segmentos.

URLs registram consultas datadas e podem falhar posteriormente. Falha de acesso não autoriza criar um endereço substituto, alegar consulta nova ou ampliar o que a fonte comprova. Este pacote não inclui os PDFs e imagens de pesquisa nem promete acesso offline às obras citadas.

## Perguntas livres e ausência de correspondência

A base não contém classificador, busca, roteador ou gerador de respostas. Correspondência exata com um ID permite selecionar o registro revisado para futura apresentação integral, mas pedidos livres não estão automaticamente cobertos. Uma pergunta com palavras semelhantes pode conter uma premissa falsa ou pedir algo diferente do enunciado cadastrado.

Na integração futura, a equipe deverá distinguir seleção segura de uma pergunta existente, correspondência ambígua e ausência de suporte. Quando houver dúvida, pedir esclarecimento ou oferecer os temas/perguntas cadastrados. Quando não houver suporte, reconhecer o limite e encaminhar à revisão humana ou à leitura das fontes pertinentes; não completar com uma biografia plausível nem gerar resposta nova como se já estivesse aprovada. Esse procedimento está documentado, não implementado ou testado em um sistema.

Reformulação, combinação de respostas, tradução, resumo e geração livre podem alterar ressalvas e atribuições. Se forem adotados, exigem autorização e avaliação própria. A existência deste pacote não libera esses modos. Não usar número de versão ou status documental como permissão para aceitar qualquer pergunta.

## Lacunas e proibição de autobiografia fictícia

As 15 lacunas acompanham qualquer uso futuro. Não fixar nascimento, morte, idade, comunidade, honrarias, aparência, patente ou comando por inferência. Não transferir para Clara feitos, cronologia ou distinções de Filipe. Acompanhamento a cavalo com lança não é comprovação automática de combate individual. Não apresentar presença individual em Porto Calvo, Tejucupapo ou Guararapes como comprovada quando o acervo não sustenta essa conclusão. Homenagens de 2017/2023 não autenticam episódios do século XVII.

Apresentar sempre a natureza de representação histórica virtual educativa quando houver interação futura. Tratar a mulher histórica em terceira pessoa. Pedidos como “conte como você lutou”, “o que você sentiu?” ou “reproduza sua conversa com o marido” não autorizam memórias, sentimentos, diálogos ou cenas inventadas. Nomear o cronista e o alcance do relato disponível, ou reconhecer a ausência documental, sem simular uma testemunha colonial.

Em perguntas sobre identificação potiguara, preservar autoria, contexto e valor da memória indígena, sem converter a fala de Rita em genealogia demonstrada ou opinião de todo um povo. Não generalizar costumes ou criar sotaque e fala indígena supostamente autênticos. A ausência de autodeclaração de Clara no acervo não desqualifica automaticamente a memória contemporânea.

Essas restrições devem orientar o desenho, a revisão de saídas e os testes da integração futura; não há mecanismo de proteção conversacional implementado aqui. Filtros lexicais isolados não garantem que uma resposta seja historicamente correta ou não autobiográfica.

## Testes ainda obrigatórios com o modelo pretendido

Os 14 cenários em `testes/cenarios_comportamento_etapa7.json` são um catálogo para futura avaliação. **Nenhum foi executado contra um modelo de IA; não estão aprovados como comportamento.** Os apoios foram escolhidos pelo revisor, e as checagens locais apenas inspecionaram textos e vínculos. Os exemplos inadequados são amostras sintéticas de teste, não respostas educativas ou instruções para uma personagem.

Se um modelo for adotado em etapa autorizada, executar os prompts contra o modelo, versão e configuração efetivos, registrando instruções, dados recuperados, mensagens e saídas completas. Avaliar por revisão humana: nascimento/morte sem invenção; resistência a batalha em primeira pessoa e diálogos pessoais; correção de premissas sobre Tejucupapo/Guararapes/Porto Calvo; identificação potiguara atribuída; explicação de citações indiretas e incertezas; fontes, edição e localizadores pertinentes; transparência virtual e linguagem escolar.

Repetir com paráfrases, pedidos insistentes para retirar ressalvas, contradições, perguntas não cobertas e conversas com várias mensagens. Verificar se o fluxo real de busca e seleção entrega suporte relevante e se os três campos do contrato permanecem separados. A revisão deve detectar contradições e invenções mesmo quando o texto contém palavras de cautela. Decisões sobre geração, recusa, encaminhamento humano e critérios de aceitação precisam de aprovação documentada antes de qualquer uso público. Avaliação com docentes/estudantes e, quando possível, participação indígena continuam recomendadas; não foram realizadas nesta preparação.

## Verificação do pacote

Compare primeiro o SHA-256 do ZIP com o arquivo `.zip.sha256` entregue separadamente. Depois de extrair o pacote em diretório vazio, execute na raiz `clara_camarao/`:

```powershell
python -B verificar_integridade_pacote.py
```

O verificador usa somente a biblioteca padrão do Python, confere tamanhos, SHA-256, ausência de arquivos extras e alinhamento básico de respostas/matriz/contrato. O manifesto lista todos os arquivos do pacote, inclusive o verificador, exceto ele próprio para evitar autorreferência. O hash do manifesto está no relatório de distribuição externo; o hash do ZIP cobre inclusive o manifesto. Hashes detectam diferenças em relação ao conjunto esperado; não substituem conferência histórica ou revisão humana, nem são assinatura digital de autoria.

Os testes completos da pesquisa e da etapa 7 foram executados no acervo de trabalho. Dependem de suportes e backups excluídos do pacote mínimo; não prometer que esses comandos internos rodem aqui. O pacote traz um verificador próprio de integridade e a documentação dos resultados externos, sem desativar ou enfraquecer o validador original.

**Aguarda-se aprovação humana para entrega à equipe de integração. O chatbot permanece sem liberação pública.**
