# Alterações — 10/11/2026

Versão da base: 1.1.0. Escopo: conteúdo, contrato de apresentação e validação offline.

## Preservação
Antes de qualquer alteração, os 11 arquivos originais foram copiados byte a byte para `../backups/2026-11-10_antes_referencias/`. O manifesto SHA-256 permite conferir a integridade dessa cópia. Os testes verificam os hashes.

## Conferência documental
As cinco URLs originais foram abertas em pesquisa web em 10/11/2026. Títulos, instituição e anos conferem com as páginas publicadas. Não se alegou inspeção do manuscrito original. A consulta pode utilizar a cópia indexada pelo serviço de pesquisa; não representa monitoramento de disponibilidade nem certificação de autenticidade. Não foram adicionadas URLs.

- F001: transcrição publicada; sustenta EG001–EG006. A data aparece no cabeçalho editorial da transcrição.
- F002: notícia de 25/11/2022; sustenta EG007. O caráter histórico e simbólico distingue o reconhecimento institucional da habilitação profissional.
- F003: biografia de 03/08/2022; primeiro e último parágrafos sustentam EG008 e EG009. A página também menciona um decreto de 1869 em discussão da carta de 1770: esse trecho anacrônico não foi incorporado à base.
- F004: notícia de 23/10/2024 sobre lançamento de obras. Não contém a informação sobre a localização da carta em 1979. Foi preservada como bibliografia verificada, sem fato associado.
- F005: notícia de 26/11/2022; a identificação do governador é atribuída a uma declaração de Carlos Augusto Pires Brandão, mantendo EG010 como registro secundário.

As URLs e títulos completos estão em `fontes.json`. `verificada` significa página e conteúdo consultados no escopo anotado, não endosso irrestrito de toda a publicação. Revalidar após mudança de URL ou conteúdo e antes de ampliar o escopo dos fatos.

## Modificações
- `fontes.json`: status, data, método, escopo, ressalvas e fatos sustentados; instituição abreviada para apresentação. Metadados bibliográficos originais preservados, sem inventar autoria individual.
- `fatos_historicos.json`: EG009 passou de F004 para F003; demais afirmações e IDs preservados. Adicionados localizadores, natureza documental e estado de sustentação.
- `personalidade.md`: rodapé obrigatório, máximo de três referências, seleção por sustentação direta, reconhecimento de lacunas e separação da fala em primeira pessoa.
- `perguntas_respostas.json`: fala separada, fontes e status; exemplos históricos com rodapé. Exemplo sobre tecnologia reescrito sem alegar uma integração existente ou introduzir cronologia sem fonte. Exemplo de reconhecimento ajustado ao escopo de EG007.
- `contrato_resposta.json`: campos e estados declarativos para futura integração, sem implementação de serviço.
- `testes_validacao.json`: cenários de múltiplas fontes, sustentação parcial, lacunas, saudação e rejeição de fontes inadequadas.
- `validar_consistencia.py`: validação offline e testes negativos; verifica fatos sem fontes, URLs ausentes ou malformadas, IDs inexistentes/duplicados, fontes não verificadas, cobertura declarada, exemplos e backup.
- `README.md`: versão, execução e restauração.

## Limites
Os testes estruturais não demonstram que um modelo seguirá as instruções, nem verificam automaticamente se uma frase é historicamente sustentada. Os vínculos documentais foram revisados nesta alteração; novas afirmações e respostas exigem revisão semântica. Rodapés sem fontes contêm uma nota explícita de limitação, nunca uma referência genérica.
