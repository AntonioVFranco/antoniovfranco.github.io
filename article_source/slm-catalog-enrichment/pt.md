# Fine-tuning de SLMs: por que marketplaces estão revendo o custo de enriquecer seus catálogos

Um marketplace pode processar milhões de produtos para responder a uma pergunta aparentemente simples: o que cada produto oferece?

Imagine uma cafeteira cuja descrição informa uma pressão de 15 bar. Para permitir que o cliente compare esse produto com outros, o marketplace precisa identificar a informação e preencher o campo correspondente no catálogo. Parece pouco trabalho. Agora multiplique essa operação por milhões de anúncios, com novos produtos e alterações todos os dias.

É nesse ponto que usar um LLM generalista para cada extração começa a pesar no orçamento.

Em 2026, três pesquisas conduzidas por equipes da Amazon mostraram um caminho diferente. Modelos menores, adaptados para trabalhar com atributos de produtos, alcançaram reduções expressivas no custo de inferência. Os estudos também revelaram onde a qualidade cai e como evitar que essa economia se transforme em mais trabalho de revisão.

A pergunta para quem administra um catálogo não deveria ser qual modelo escreve melhor. Deveria ser quanto custa obter um atributo correto, pronto para ser utilizado.

## Por que enriquecer um catálogo custa tanto?

Quem já trabalhou com dados de produtos conhece o problema. Fornecedores descrevem mercadorias de maneiras diferentes, mesmo quando pertencem à mesma categoria. Parte das informações está no título, outra na descrição, e nem sempre os termos usados são consistentes.

Isso afeta diretamente a experiência de compra. Sem atributos preenchidos corretamente, filtros deixam de encontrar produtos, comparações perdem utilidade e o cliente tem mais dificuldade para decidir.

Modelos de linguagem ajudam a transformar descrições em campos que um sistema consegue consultar. O problema aparece quando a empresa adota o mesmo modelo generalista para praticamente todas as tarefas, inclusive aquelas que se repetem com pouca variação.

Considere uma operação que precisa extrair o atributo de pressão de milhares de cafeteiras. O trabalho exige reconhecer o valor e sua unidade, respeitar o formato do catálogo e não inventar informações ausentes. Não exige que o modelo domine uma conversa aberta sobre qualquer assunto.

Mesmo quando a inferência individual parece barata, ela se repete sempre que o catálogo cresce ou precisa ser atualizado. Um gasto pequeno por produto pode se tornar relevante quando a operação alcança dezenas de milhões de registros.

Por isso, o volume muda a decisão. Quanto maior a frequência de processamento, mais sentido faz investigar um modelo especializado.

## O que significa treinar um SLM para trabalhar com produtos?

SLM é a sigla para *small language model*, ou modelo de linguagem pequeno. A ideia é utilizar um modelo com menos parâmetros e adaptá-lo para uma tarefa definida, como extrair atributos de descrições de produtos.

Com fine-tuning, o modelo recebe exemplos de entradas e saídas esperadas. Assim, aprende como aquela operação deve ser realizada, quais campos preencher e quando deixar um valor em branco.

Uma técnica usada nesse processo é LoRA, que permite treinar uma quantidade menor de parâmetros em vez de atualizar todos os pesos do modelo. Isso pode reduzir a memória necessária durante o treinamento. Não significa, por si só, que a inferência ficará 98% mais barata. O custo final depende também do modelo escolhido e da maneira como ele é executado.

Existe outra possibilidade: usar um modelo maior para produzir exemplos de treinamento e transferir parte dessa capacidade para o menor. Esse processo é conhecido como destilação. Depois de treinado, o modelo pequeno executa uma tarefa que antes dependia do modelo maior.

A diferença prática é que a empresa concentra o trabalho de adaptação antes da operação em escala. Em vez de pagar continuamente por um modelo com capacidades que pouco utiliza, passa a executar um modelo preparado para o processo.

Essa estratégia só faz sentido quando o comportamento aprendido é útil por tempo suficiente para compensar o treinamento e a manutenção. Os resultados publicados em 2026 ajudam a dimensionar essa possibilidade.

## Um estudo encontrou redução de 98% no custo de inferência

Em julho de 2026, Lakshman Kolasani e Fatemeh Taheri Dezaki publicaram o estudo [*Progressive Fine-Tuning for Cost-Effective Structured Attribute Generation in E-commerce*](https://aclanthology.org/2026.acl-industry.40/), na trilha industrial da ACL.

Os pesquisadores adaptaram o Amazon Nova 2 Lite com LoRA para gerar atributos durante o cadastro de produtos. A comparação principal foi feita com o Claude Sonnet 4.5, que apresentava os melhores resultados para a tarefa entre os modelos avaliados pela equipe naquele momento.

O modelo adaptado apresentou uma estimativa de **98% menos custo de inferência**, calculada a partir dos preços públicos dos modelos na época dos experimentos. A latência p90 também caiu aproximadamente **70%**. Isso significa que o tempo abaixo do qual 90% das respostas eram concluídas ficou menor.

O estudo foi além dos testes internos. Em um experimento com usuários reais, a taxa de aceitação das sugestões do modelo pequeno foi de **86,4%**, contra **88,3%** para o Claude Sonnet 4.5.

Aqui existe um detalhe que não pode ser ignorado. O modelo menor também apresentou uma taxa de preenchimento de atributos aceitos de **59,1%**, contra **63,0%** para o modelo maior. As diferenças foram estatisticamente significativas, segundo os autores.

Portanto, a economia não veio acompanhada de desempenho idêntico em produção. A decisão empresarial é avaliar se a diferença de qualidade justifica a redução de custo e como tratar os campos que o modelo não consegue preencher.

O trabalho traz ainda uma ideia importante para o treinamento: selecionar novos exemplos a partir das informações que o modelo deixou de extrair, mas que já estavam presentes no catálogo. Em vez de aumentar indiscriminadamente o conjunto de treinamento, a equipe concentrou a segunda rodada nos casos em que havia maior diferença entre o catálogo e as previsões.

Com duas rodadas de mil exemplos cada, o modelo passou de 66,03% para 74,20% de preenchimento válido na avaliação offline. Isso mostrou ganho no conjunto de teste utilizado, embora o desempenho em produção tenha ficado abaixo do modelo maior.

Para um marketplace, a lição é simples: **os erros que aparecem no próprio catálogo podem ajudar a escolher os próximos dados de treinamento**. Mas é necessário conferir se o conteúdo existente está correto antes de tratá-lo como referência.

## Outro estudo processou 30 milhões de produtos por cerca de US$ 5 mil

Publicado em outubro de 2026, o trabalho [*Scaling E-Commerce Attribute Extraction with Parallel Decoding*](https://aclanthology.org/2026.akbc-1.13/), de Nikhita Vedula e colaboradores, investigou o problema por outro ângulo.

A equipe partiu de uma pergunta que muitas operações ignoram: quais atributos realmente ajudam o comprador a distinguir produtos de uma categoria?

Primeiro, um modelo maior identifica os atributos relevantes. Depois, um Qwen3-4B adaptado extrai os valores das descrições. O sistema utiliza uma técnica chamada *Hyper-Parallel Decoding* (HPD), que permite gerar valores de vários atributos em paralelo, em vez de produzir tudo em sequência.

O resultado foi uma acurácia de extração próxima de **85%**, semelhante à do modelo maior utilizado como referência. A pesquisa também incluiu uma avaliação humana de 500 produtos, que encontrou aproximadamente a mesma taxa de acerto.

A diferença econômica aparece no processamento de 30 milhões de produtos:

| Configuração avaliada | Custo de inferência estimado | Tempo estimado |
| --- | ---: | ---: |
| LLM de referência por API em lotes | US$ 63 mil | Mais de 300 horas, sem contar espera em filas |
| Qwen3-4B com geração convencional | US$ 46 mil | 333 horas |
| Qwen3-4B com HPD | US$ 5 mil | 36 horas |

Os valores são os reportados pelos autores para a configuração do estudo, não uma cotação atual de serviços de nuvem. A equipe também estimou cerca de US$ 350 para uma etapa de fine-tuning com oito GPUs A100, sem que esse valor represente todos os custos de dados e desenvolvimento.

A economia de **92%** frente ao LLM de referência chama atenção, mas há uma distinção essencial: ela não foi produzida somente pelo fine-tuning. A execução com HPD foi determinante. O mesmo Qwen3-4B, gerando os atributos da maneira convencional, custava muito mais no experimento.

Essa comparação mostra por que escolher um modelo menor é apenas parte da solução. O formato da saída e o método de inferência podem alterar bastante o custo de processar o catálogo.

O estudo foi realizado com textos de produtos em inglês. A aplicação direta a catálogos em português exige avaliação própria, especialmente quando fornecedores usam descrições incompletas ou convenções diferentes de unidades.

## E quando o modelo pequeno errar?

Esse é o ponto em que muitas propostas de economia deixam de ser convincentes.

Um atributo incorreto pode prejudicar filtros e comparações. Se a operação precisa revisar manualmente uma quantidade excessiva de registros, a economia com inferência perde valor.

Em outubro de 2026, outro artigo da trilha industrial do EMNLP, [*When to Defer: Scope-Aware Cascades for Structured Attribute Generation in E-commerce Product Catalogs*](https://aclanthology.org/2026.emnlp-industry.187/), investigou como escolher quais respostas de um SLM devem ser aceitas.

A solução foi considerar não só a confiança do modelo, mas também a tarefa que estava sendo executada. Um modelo pode acertar com frequência um atributo e falhar bastante em outro. Um único limite de confiança, aplicado a tudo, não capta bem essa diferença.

Com um mecanismo de seleção que considera o tipo de produto e o atributo, os pesquisadores conseguiram aceitar **11,4 pontos percentuais a mais de previsões** do que com um limite geral de confiança, mantendo a mesma precisão observada de **90,3%** naquele ponto de avaliação.

Isso não significa que o SLM tenha ficado 11,4% mais preciso. O ganho foi conseguir aproveitar mais respostas sem reduzir a precisão medida.

A implicação para a operação é importante. O modelo pequeno pode atender a maior parte do volume, enquanto os casos de maior risco são encaminhados para revisão ou para outro modelo. E nem todo erro exige um LLM maior: às vezes, a melhor decisão é deixar o campo sem resposta até que exista informação suficiente.

Não é necessário gastar com o modelo mais caro em todos os produtos. É necessário saber **quando a resposta mais barata pode ser utilizada**.

## Como descobrir se o fine-tuning vale a pena no seu marketplace?

Comece identificando uma categoria que recebe muitos produtos e gera trabalho recorrente de preenchimento ou correção. O objetivo é medir uma tarefa definida antes de expandir a solução para o catálogo inteiro.

Separe produtos para treinamento, validação e teste. Preserve no teste produtos que o modelo não viu durante a adaptação e inclua descrições que representem o tráfego atual. Caso contrário, o resultado pode parecer melhor do que será na operação.

Compare o sistema existente com um SLM sem adaptação e com o mesmo SLM após fine-tuning. Se houver interesse em HPD ou em outra técnica de inferência, faça uma comparação separada. Assim será possível distinguir o ganho causado pelo treinamento daquele causado pela execução.

Depois, avalie o resultado por atributo, não apenas por produto. Uma média de acerto pode esconder falhas concentradas justamente nos campos de maior importância comercial. Meça também quantos registros exigem revisão e quantos deixam de ser preenchidos.

A métrica econômica deve incluir o custo para entregar um atributo correto e aprovado, não apenas o preço de gerar uma resposta:

**Custo por atributo aprovado = (inferência + revisão + correção + infraestrutura + treinamento amortizado) ÷ quantidade de atributos aprovados corretamente.**

Todos os custos precisam considerar o mesmo período. O treinamento deve ser distribuído pelo volume que se espera processar antes de uma nova adaptação.

Esse cálculo evita um erro comum: considerar que um modelo custou menos porque sua GPU foi mais barata, sem contabilizar o trabalho necessário para corrigir as saídas.

Para uma operação com atualizações frequentes e volume elevado, um SLM adaptado tende a ser uma alternativa especialmente interessante. O investimento inicial pode ser diluído entre muitas extrações. Já um catálogo de baixo volume talvez não gere economia suficiente para justificar uma infraestrutura dedicada.

O critério de avanço é objetivo. Se o SLM entrega os atributos exigidos, mantém a taxa de erros dentro do limite da operação e reduz o custo por atributo aprovado, existe fundamento para ampliar seu uso.

## O próximo ganho de eficiência pode estar no seu catálogo, não em um LLM maior

Os estudos de 2026 mostram que enriquecer produtos com modelos pequenos deixou de ser apenas uma possibilidade de laboratório. Há resultados de implantação, comparações de custo e métodos para decidir quais respostas podem ser aproveitadas.

Os números são expressivos: **98% de redução estimada no custo de inferência em um estudo e 92% em outro**. Eles foram obtidos em condições diferentes e não devem ser tratados como uma promessa de economia para qualquer marketplace.

A conclusão que realmente interessa é outra. Quando o trabalho consiste em extrair atributos de milhões de produtos, faz sentido começar pela especialização de um modelo menor, medir sua qualidade e otimizar a maneira como ele executa a tarefa. Manter um LLM generalista em todas as etapas pode significar pagar continuamente por capacidade que a operação não utiliza.

Se a sua empresa precisa avaliar essa decisão com seus próprios dados, volume e requisitos de qualidade, a Huyawo Solutions trabalha com seleção e adaptação de modelos para problemas empresariais. O contato é feito por escrito.

### Estudos e documentação consultados

1. [Kolasani e Dezaki, *Progressive Fine-Tuning for Cost-Effective Structured Attribute Generation in E-commerce*, ACL Industry Track, julho de 2026](https://aclanthology.org/2026.acl-industry.40/).
2. [Vedula e colaboradores, *Scaling E-Commerce Attribute Extraction with Parallel Decoding*, AKBC, outubro de 2026](https://aclanthology.org/2026.akbc-1.13/).
3. [Mansoori e colaboradores, *When to Defer: Scope-Aware Cascades for Structured Attribute Generation in E-commerce Product Catalogs*, EMNLP Industry Track, outubro de 2026](https://aclanthology.org/2026.emnlp-industry.187/).
4. [Hugging Face, documentação de LoRA no PEFT](https://huggingface.co/docs/peft/v0.21.0/conceptual_guides/lora).
