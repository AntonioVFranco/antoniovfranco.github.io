import { articleSlugs } from './article-slugs.mjs';

const supported = new Set(['en', 'pt', 'es', 'zh', 'ar', 'ru', 'it', 'fr', 'de', 'ja', 'ko']);
const sections = new Set(['blog', 'about', 'contact', 'research', 'open-source', 'privacy']);
const countryGroups = {
  pt: 'BR PT AO MZ CV GW ST TL',
  es: 'ES MX AR CL CO PE VE EC BO PY UY CR PA GT HN NI SV DO CU GQ PR',
  zh: 'CN TW HK MO',
  ar: 'SA AE QA KW BH OM YE IQ JO LB SY PS EG LY TN DZ MA SD MR DJ SO KM',
  ru: 'RU BY KZ KG',
  it: 'IT SM VA',
  fr: 'FR MC SN CI ML BF NE BJ TG GA GN CD CG CF TD MG HT',
  de: 'DE AT LI',
  ja: 'JP',
  ko: 'KR KP',
};
const countryLocale = new Map(Object.entries(countryGroups).flatMap(([language, countries]) =>
  countries.split(' ').map(country => [country, language])));
const multilingual = {
  CA: ['en', 'fr'], CH: ['de', 'fr', 'it'], BE: ['fr', 'de'],
  LU: ['fr', 'de'], SG: ['en', 'zh'], CM: ['fr', 'en'],
};
const slugToId = new Map(Object.entries(articleSlugs).flatMap(([id, values]) =>
  [id, ...Object.values(values)].map(slug => [slug, id])));

function preferredLanguage(header, available) {
  const choices = (header || '').split(',').map(part => {
    const [tag, ...params] = part.trim().split(';');
    const q = params.find(value => value.trim().startsWith('q='));
    return { language: tag.toLowerCase().split('-')[0], quality: q ? Number(q.trim().slice(2)) : 1 };
  }).filter(item => Number.isFinite(item.quality) && item.quality > 0)
    .sort((a, b) => b.quality - a.quality);
  const first = choices.find(item => available.includes(item.language));
  return first?.language || null;
}

export function languageForCountry(country, acceptLanguage = '', region = '') {
  const code = String(country || '').toUpperCase();
  if (code === 'CA' && String(region).toUpperCase() === 'QC') return 'fr';
  if (code in multilingual) return preferredLanguage(acceptLanguage, multilingual[code]) || 'en';
  return countryLocale.get(code) || 'en';
}

function cookiePreference(request) {
  const value = request.headers.get('Cookie')?.match(/(?:^|;\s*)hw-language=([a-z]{2})(?:;|$)/)?.[1];
  return supported.has(value) ? value : null;
}

function destination(pathname, language) {
  let path;
  try { path = decodeURIComponent(pathname); } catch { return null; }
  const parts = path.split('/').filter(Boolean);
  if (parts.at(-1) === 'index.html') parts.pop();
  // An explicitly localized URL is authoritative, including deep article URLs.
  if (supported.has(parts.at(-1))) return null;
  if (parts.length === 0) return `/${language}/`;
  if (parts.length === 1 && sections.has(parts[0])) return `/${parts[0]}/${language}/`;
  if (parts.length === 2 && parts[0] === 'articles') {
    const id = slugToId.get(parts[1]);
    if (id) return `/articles/${articleSlugs[id][language]}/${language}/`;
  }
  // Other routes, API endpoints and assets are left to the existing origin.
  return null;
}

export function redirectForRequest(request) {
  if (request.method !== 'GET' && request.method !== 'HEAD') return null;
  const url = new URL(request.url);
  const languageInUrl = url.searchParams.get('lang');
  const explicitQuery = supported.has(languageInUrl) ? languageInUrl : null;
  const language = explicitQuery || cookiePreference(request) ||
    languageForCountry(request.cf?.country, request.headers.get('Accept-Language'), request.cf?.regionCode);
  const path = destination(url.pathname, language);
  if (!path) return null;
  url.pathname = path;
  url.searchParams.delete('lang');
  const headers = new Headers({ Location: url.href, 'Cache-Control': 'private, no-store', Vary: 'Cookie, Accept-Language' });
  if (explicitQuery) headers.set('Set-Cookie', `hw-language=${explicitQuery}; Max-Age=31536000; Path=/; SameSite=Lax; Secure`);
  return new Response(null, { status: 302, headers });
}

export default {
  async fetch(request) {
    return redirectForRequest(request) || fetch(request);
  },
};
