# Registro de alterações da base 1.2.0

Data: 10/11/2026. Implementação autorizada pelo responsável pelo projeto. Escopo: base de conhecimento, regras de apresentação e validação offline.

## Preservação antes das alterações

Foi criado primeiro o backup completo `../backups/2026-11-10_v1.1.0_antes_v1.2.0/`, com os 26 arquivos existentes na base naquele momento, incluindo o backup anterior e seu manifesto. O arquivo `manifesto_sha256.json` registra caminhos relativos e hashes SHA-256 de cada arquivo copiado, sem incluir a si próprio. O destino não existia e não houve sobrescrita de backup.

As cinco fontes permanecem sem alteração. As dez afirmações históricas, seus IDs, classificações e vínculos com fontes foram preservados; apenas erros editoriais nos localizadores foram corrigidos. Não foram introduzidos novos acontecimentos, documentos ou URLs. Não houve nova pesquisa web nesta expansão: ela utiliza o escopo documental já registrado na 1.1.0.

## Matriz e coleção

A matriz foi gravada antes da coleção expandida. Cada pergunta foi associada a um objetivo educativo, categoria, fatos, lacunas e fontes planejadas. A coleção foi construída a partir desse plano e ambas são verificadas em conjunto.

| Categoria | IDs | Quantidade |
|---|---|---:|
| Carta de 1770 e seus pedidos | EGQA001–EGQA010 | 10 |
| Família, deslocamento e trabalho | EGQA011–EGQA020 | 10 |
| Violência e reivindicações documentadas | EGQA021–EGQA030 | 10 |
| Religiosidade na carta | EGQA031–EGQA040 | 10 |
| Reconhecimento e preservação da memória | EGQA041–EGQA050 | 10 |
| Fontes, lacunas e representação educativa | EGQA051–EGQA060 | 10 |
| **Total** | **EGQA001–EGQA060** | **60** |

Os quatro exemplos anteriores correspondem a EGQA001 (motivo da carta), EGQA011 (retorno à família), EGQA051 (tecnologia atual) e EGQA041 (primeira advogada). As perguntas foram mantidas; as respostas foram revisadas e os registros são idênticos aos correspondentes da coleção principal. Não são quatro itens adicionais.

Distribuição documental: 31 respostas `sustentado`, 12 `parcialmente_sustentado`, 14 `sem_sustentacao_documental` e três `nao_aplicavel`. Quarenta respostas têm uma fonte, três têm duas e 17 não têm fontes. Destas últimas, 14 apresentam rodapé com nota de limitação, sem links; as três de orientação educativa dispensam rodapé. Nenhuma resposta excede três fontes.

## Arquivos criados

- `matriz_perguntas_v1.2.0.json`: planejamento dos 60 registros e seis categorias.
- `perguntas_respostas_expandidas.json`: coleção educativa principal, com fala separada e apresentação completa.
- `ALTERACOES_v1.2.0.md`: este registro, resultados e pendências.
- Backup completo da 1.1.0 e respectivo manifesto SHA-256.

## Arquivos modificados

- `perguntas_respostas.json`: quatro exemplos revisados, com IDs e campos iguais aos da coleção principal.
- `fatos_historicos.json`: correção de caracteres nos localizadores, sem mudar afirmações, fontes ou significado histórico.
- `lacunas_e_hipoteses.json`: IDs EGL001–EGL005 nos temas existentes; EGL006–EGL010 para rotinas, identificação familiar, trajetória documental, práticas religiosas e providências da autoridade. São limites do acervo, não novos fatos históricos. Status absolutos de desconhecimento foram delimitados ao conhecimento desta base.
- `personalidade.md`: correções editoriais, consulta explícita às lacunas, precedência da incerteza, uso da coleção principal e regra de nota em respostas mistas.
- `contrato_resposta.json`: versão própria 1.1.0, compatível com a base 1.2.0; mantém os três campos centrais, define os metadados educativos e a composição do rodapé. Não é uma implementação de serviço nem um JSON Schema formal.
- `testes_validacao.json`: reparos editoriais e quatro cenários adicionais; total de 15 rubricas declarativas.
- `validar_consistencia.py`: validação ampliada e testes negativos, sem rede ou gravação de arquivos.
- `ALTERACOES_2026-11-10.md`: somente correções editoriais, preservando o registro histórico da versão 1.1.0.
- `../README.md`: versão, estrutura, distribuição, testes, limites e restauração.

Sem alterações em `fontes.json`, `perfil.json`, `regras_de_seguranca.md`, `REVISAO_2026-11-06.md` e `documentos/carta_1770_REFERENCIA.md`. Os backups permanecem intactos.

## Referências e integridade histórica

O rodapé mantém o cabeçalho e os links Markdown solicitados, separados da fala. Títulos e URLs são copiados do cadastro. Nas respostas mistas, a nota explicita que a fonte sustenta apenas a parte documentada. Na fala, a limitação é específica à pergunta. Não se usa referência genérica para confirmar o que não se sabe.

F001 permanece uma transcrição publicada, sem alegação de inspeção do manuscrito. EG001–EG006 são apresentados como data, relatos e pedidos da carta. Os acontecimentos posteriores são explicados pela representação educativa, respeitando o campo de primeira pessoa. F004 continua sem fato associado e não aparece como comprovação nas respostas. A ressalva de F003 sobre o trecho anacrônico continua válida.

## Testes e resultados

Comando executado na raiz do projeto:

```powershell
python MIRA_BASE_CONHECIMENTO/esperanca_garcia/validar_consistencia.py
```

Resultado: **11 testes aprovados, zero falhas e zero erros**. A suíte inclui:

- leitura JSON estrita, com rejeição de chaves duplicadas e constantes não JSON;
- 60 IDs únicos e dez perguntas por categoria;
- duplicação de perguntas e respostas após normalização de caixa, acentos e pontuação;
- fatos, fontes e lacunas existentes; campos obrigatórios e tipos; vínculos documentais nos dois sentidos;
- título e URL iguais ao cadastro, fontes verificadas, máximo de três referências e rejeição de fontes sem fato associado;
- apresentação completa reconstruída a partir da fala, referências e nota, com correspondência exata;
- matriz compatível com a coleção e quatro exemplos originais canônicos;
- preservação dos fatos e fontes em comparação com o backup;
- hashes dos 26 arquivos da cópia 1.1.0 e dos 11 arquivos do backup inicial;
- detecção de padrões conhecidos de corrupção de caracteres;
- 30 alterações inválidas simuladas em memória, todas rejeitadas;
- quatro divergências simuladas na matriz, todas rejeitadas.

Os 30 casos negativos e as quatro divergências são subcasos dentro dos 11 métodos de teste, não 34 métodos adicionais. As 15 rubricas pedagógicas foram verificadas estruturalmente; não houve execução contra um modelo conversacional. A suíte não comprova a verdade histórica nem garante comportamento futuro de uma IA.

## Pendências de revisão histórica e pedagógica

1. Revisar humanamente as 60 respostas quanto a fidelidade, tom, diversidade de objetivos e clareza para o público educativo. O acervo permanece limitado a dez fatos; algumas perguntas retomam a mesma passagem sob objetivos diferentes.
2. Manter como lacunas o desfecho da petição, providências da autoridade, identificação completa da família, rotina, alfabetização, aparência, morte e sentimentos íntimos. Ampliar apenas com documentação específica conferida.
3. Caso seja usado em futuras respostas, o ano de nascimento reportado no perfil precisará de vínculo factual revisado; não foi promovido a um novo fato nesta expansão nem usado para calcular idade.
4. Melhorar a precisão dos localizadores por trecho em futura revisão da transcrição. Os localizadores atuais são suficientes para o mapeamento existente, mas não constituem uma edição crítica.
5. Revalidar acessibilidade e conteúdo das páginas antes de publicação ou ampliação de escopo. As cinco fontes pertencem à mesma instituição e não representam cinco confirmações independentes.
6. Manter os IDs estáveis nas próximas revisões e sincronizar alterações entre matriz, coleção expandida e quatro exemplos canônicos.

Não foi criado backend, API, interface gráfica ou integração com WhatsApp. Não houve publicação externa da base.
