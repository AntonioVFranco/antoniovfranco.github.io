import test from 'node:test';
import assert from 'node:assert/strict';
import worker, { redirectForRequest, languageForCountry } from './index.mjs';
import { articleSlugs } from './article-slugs.mjs';

function request(path, { country, region, cookie, accept, method = 'GET', cf = true } = {}) {
  const headers = new Headers();
  if (cookie) headers.set('Cookie', cookie);
  if (accept) headers.set('Accept-Language', accept);
  const value = new Request(`https://antoniovfranco.com${path}`, { method, headers });
  if (cf) Object.defineProperty(value, 'cf', { value: { country, regionCode: region } });
  return value;
}
function target(path, options) {
  return redirectForRequest(request(path, options))?.headers.get('Location');
}

test('country routing and English fallback', () => {
  assert.equal(target('/', { country: 'BR' }), 'https://antoniovfranco.com/pt/');
  assert.equal(target('/blog/', { country: 'JP' }), 'https://antoniovfranco.com/blog/ja/');
  assert.equal(target('/contact/index.html', { country: 'SA' }), 'https://antoniovfranco.com/contact/ar/');
  assert.equal(target('/research/', { country: 'FR' }), 'https://antoniovfranco.com/research/fr/');
  assert.equal(target('/', { country: 'NL' }), 'https://antoniovfranco.com/en/');
  assert.equal(target('/', { cf: false }), 'https://antoniovfranco.com/en/');
  assert.equal(target('/', { country: 'XX' }), 'https://antoniovfranco.com/en/');
  assert.equal(languageForCountry('CH', 'fr-CH,fr;q=0.9,de;q=0.8'), 'fr');
  assert.equal(languageForCountry('CA', 'en-CA,en;q=0.7', 'QC'), 'fr');
  assert.equal(languageForCountry('BE', 'nl-BE,nl;q=0.9'), 'en');
});

test('localized paths are authoritative and do not loop', () => {
  for (const locale of ['en', 'pt', 'es', 'zh', 'ar', 'ru', 'it', 'fr', 'de', 'ja', 'ko']) {
    assert.equal(target(`/${locale}/`, { country: 'BR' }), undefined);
    assert.equal(target(`/blog/${locale}/index.html`, { country: 'JP' }), undefined);
    assert.equal(target(`/articles/${articleSlugs.agents[locale]}/${locale}/`, { country: 'FR' }), undefined);
  }
});

test('legacy article slugs map to the localized article for every language', () => {
  const countries = { en: 'US', pt: 'BR', es: 'ES', zh: 'CN', ar: 'SA', ru: 'RU', it: 'IT', fr: 'FR', de: 'DE', ja: 'JP', ko: 'KR' };
  for (const [id, slugs] of Object.entries(articleSlugs)) {
    for (const [locale, country] of Object.entries(countries)) {
      assert.equal(target(`/articles/${id}/`, { country }), `https://antoniovfranco.com/articles/${encodeURI(slugs[locale])}/${locale}/`);
    }
  }
});

test('a manual choice overrides geolocation and old query links', () => {
  assert.equal(target('/', { country: 'BR', cookie: 'hw-language=ja' }), 'https://antoniovfranco.com/ja/');
  assert.equal(target('/blog/?lang=fr&search=agents', { country: 'BR', cookie: 'hw-language=ja' }),
    'https://antoniovfranco.com/blog/fr/?search=agents');
  const response = redirectForRequest(request('/?lang=de', { country: 'BR' }));
  assert.match(response.headers.get('Set-Cookie'), /^hw-language=de;/);
  assert.equal(response.headers.get('Cache-Control'), 'private, no-store');
  assert.equal(target('/en/?lang=pt', { country: 'BR' }), undefined);
});

test('assets, unknown content and non-navigation requests pass through', async () => {
  assert.equal(target('/hw/assets/site.css', { country: 'BR' }), undefined);
  assert.equal(target('/posts/existing-article/', { country: 'BR' }), undefined);
  assert.equal(target('/articles/unknown/', { country: 'BR' }), undefined);
  assert.equal(target('/contact/', { country: 'BR', method: 'POST' }), undefined);
  const oldFetch = globalThis.fetch;
  try {
    globalThis.fetch = async () => new Response('origin');
    assert.equal(await (await worker.fetch(request('/hw/assets/site.css', { country: 'BR' }))).text(), 'origin');
  } finally { globalThis.fetch = oldFetch; }
});
