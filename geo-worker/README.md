# Redirecionamento geográfico da V9_2

Este Worker roda na borda do domínio `antoniovfranco.com` e utiliza somente `request.cf.country` e, em países multilíngues, `Accept-Language` e `request.cf.regionCode`. Não consulta serviços externos, não lê o IP bruto, não armazena país nem cria registros de visita. A única persistência é o cookie `hw-language` quando a pessoa escolhe um idioma no seletor ou usa um link legado `?lang=`.

## Comportamento

- Em `/`, `/blog/`, `/about/`, `/contact/`, `/research/`, `/open-source/`, `/privacy/` e nos nove artigos da prévia, redireciona a visita sem idioma para a rota correspondente à localidade.
- País desconhecido ou sem idioma disponível vai para inglês (`/en/`). País multilíngue usa o idioma compatível mais bem classificado no navegador; Quebec usa francês. Sem correspondência, usa inglês.
- URLs com idioma explícito, como `/fr/`, `/blog/fr/` e `/articles/titre/fr/`, são preservadas. A escolha manual no seletor grava preferência de idioma por um ano para futuros acessos a rotas sem idioma.
- `?lang=` legado tem prioridade e é removido da nova URL. Outros parâmetros da URL são preservados.
- Outros caminhos, inclusive assets, APIs e artigos reais do Hugo fora dos nove artigos localizados da V9, continuam a ser servidos normalmente. Não redirecionar um artigo nativo a uma tradução que ainda não existe.
- O redirecionamento é temporário (HTTP 302) e não pode ser compartilhado por cache (`private, no-store`).

## Integração

1. Revisar os arquivos em `overlay/` e manter a alteração de `static/hw/js/site.js` que persiste a escolha manual em cookie. A prévia portátil já possui a mesma alteração em `hw/js/site.js`.
2. Gerar o Hugo real e confirmar que todas as rotas localizadas da V9 existem no resultado da publicação. O Worker não gera páginas; depende das pastas em `overlay/static`.
3. Executar `node --test index.test.mjs` dentro desta pasta. Revisar o mapa de países para o público desejado.
4. Com `antoniovfranco.com` ativo como zona Cloudflare e seu registro DNS **proxied**, criar este Worker e associar a rota `antoniovfranco.com/*`. O `wrangler.toml` contém essa rota. A origem continua sendo o site existente. Se `www.antoniovfranco.com` responder sem redirecionar ao domínio principal, configurar também sua rota de modo equivalente.
5. Verificar em produção `/`, `/blog/`, `/articles/agents/` e as versões explícitas `/en/`, `/pt/`, `/blog/fr/`, `/articles/<slug>/ja/`. Testar troca manual e retorno à raiz; conferir também arquivos CSS, imagens, formulários e posts nativos. O painel de preview de Workers não fornece `request.cf`, portanto teste de geolocalização com requisições reais na borda ou com os testes locais.

Não implantar o Worker antes de conferir o DNS e a publicação das rotas localizadas: uma rota para uma página ainda ausente resultaria em 404. A configuração do Worker é uma peça separada do overlay Hugo, pois GitHub Pages serve arquivos estáticos e não executa código de backend. Não são necessárias chaves ou segredos para este redirecionamento.
