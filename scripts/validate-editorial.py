#!/usr/bin/env python3
"""Validate the static release and optionally compare article content to the previous site."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

from lxml import html

DOMAIN = 'https://antoniovfranco.com'
LANGUAGES = {'en', 'pt', 'es', 'zh', 'ar', 'ru', 'it', 'fr', 'de', 'ja', 'ko'}


def parse(path):
    return html.fromstring(path.read_bytes())


def text(node):
    return ' '.join(node.text_content().split())


def article_payload(node):
    return text(node), node.xpath('.//a/@href'), node.xpath('.//section/@id'), len(node.xpath('.//table'))


def local_target(directory, value):
    url = urlsplit(value)
    if url.scheme and (url.scheme != 'https' or url.netloc != 'antoniovfranco.com'):
        return None
    if not url.path:
        return None
    path = unquote(url.path)
    destination = args.root / path.lstrip('/') if path.startswith('/') else directory / path
    return destination / 'index.html' if destination.is_dir() else destination


def require(condition, label, message):
    if not condition:
        errors.append(f'{label}: {message}')


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--root', type=Path, default=Path('static'))
parser.add_argument('--baseline', type=Path)
parser.add_argument('--preview', action='store_true')
args = parser.parse_args()
errors = []
articles = Counter()
canonical_pages = {}
expected_mode = 'preview' if args.preview else 'production'

for path in sorted(args.root.rglob('index.html')):
    rel = path.relative_to(args.root)
    doc = parse(path)
    for node in doc.xpath('//*[@href or @src or @srcset or @imagesrcset]'):
        values = [node.get(name) for name in ('href', 'src') if node.get(name)]
        for attr in ('srcset', 'imagesrcset'):
            if node.get(attr):
                values.extend(item.strip().split()[0] for item in node.get(attr).split(','))
        for value in values:
            dest = local_target(path.parent, value)
            if dest is not None:
                require(dest.is_file(), rel, f'missing {value}')
    canonical = doc.xpath('string(//link[@rel="canonical"]/@href)')
    if not canonical:
        continue
    lang = doc.get('lang').split('-')[0]
    choices = set(doc.xpath('//a[@data-lang-choice]/@data-lang-choice'))
    require(choices == LANGUAGES, rel, 'incomplete language selector')
    require(doc.get('dir') == ('rtl' if lang == 'ar' else 'ltr'), rel, 'invalid direction')
    require(doc.get('data-theme') == 'dark', rel, 'invalid default theme')
    require(doc.xpath('string(//body/@data-analytics)') == expected_mode, rel, 'invalid analytics mode')
    require(len(doc.xpath('//h1')) == 1, rel, 'missing or multiple h1 elements')
    require(bool(doc.xpath('string(//meta[@name="description"]/@content)')), rel, 'description missing')
    require(doc.xpath('string(//meta[@property="og:url"]/@content)') == canonical, rel, 'social metadata URL mismatch')
    alt = {n.get('hreflang'): n.get('href') for n in doc.xpath('//link[@hreflang]')}
    require(set(alt) == LANGUAGES | {'x-default'} and alt.get('x-default') == alt.get('en'), rel, 'invalid hreflang')
    if not doc.xpath('//body[@data-language-entry]'):
        canonical_pages[canonical] = alt
    if rel.parts[0] != 'articles':
        continue
    articles[lang] += 1
    article = doc.xpath('//article[@class="prose"]')[0]
    scripts = doc.xpath('//head/script/@src')
    styles = doc.xpath('//head/link[@rel="stylesheet"]/@href')
    require(any(Path(asset).name == 'article-data.js' for asset in scripts), rel, 'shared article data script missing')
    require(any(Path(asset).name == 'article-data.css' for asset in styles), rel, 'shared article data styles missing')
    require(not article.xpath('.//table[@style] | .//table//*[@style]'), rel, 'legacy inline table styling')

    anchors = doc.xpath('//aside[@class="toc"]//a/@href')
    require(anchors == ['#' + section for section in article.xpath('.//section[@id][h2]/@id')], rel, 'table of contents mismatch')
    graph = json.loads(doc.xpath('string(//script[@id="hw-seo-graph"])'))['@graph']
    item = next(entry for entry in graph if entry['@type'] == 'BlogPosting')
    require(item['headline'] == text(doc.xpath('//h1')[0]), rel, 'article metadata headline mismatch')
    require(re.sub(r'\s+', ' ', item['articleBody']).strip() == text(article), rel, 'article metadata text mismatch')
    if args.baseline:
        original = parse(args.baseline / rel).xpath('//article')[0]
        for node in original.xpath('.//*[contains(concat(" ", normalize-space(@class), " "), " hw-article-lead-card ")]'):
            node.drop_tree()
        require(article_payload(article) == article_payload(original), rel, 'published article content changed')

ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9', 'x': 'http://www.w3.org/1999/xhtml'}
sitemap = {}
for row in ET.parse(args.root / 'sitemap.xml').findall('s:url', ns):
    url = row.findtext('s:loc', namespaces=ns)
    sitemap[url] = {n.get('hreflang'): n.get('href') for n in row.findall('x:link', ns)}
require(sitemap == canonical_pages, 'sitemap', 'HTML and sitemap canonical URLs or alternates differ')
for url, links in canonical_pages.items():
    require(all(canonical_pages.get(alt) == links for alt in links.values()), url, 'nonreciprocal language alternates')
for lang in LANGUAGES:
    items = ET.parse(args.root / 'blog' / lang / 'index.xml').findall('channel/item')
    require(len(items) == articles[lang], lang, 'article count differs from RSS feed')
    require(all(item.findtext('link') in canonical_pages for item in items), lang, 'invalid RSS link')
require(set(articles) == LANGUAGES and len(set(articles.values())) == 1, 'articles', 'incomplete language coverage')
require(bool(re.search(r"measurementId:\s*'G-[A-Z0-9]+'", (args.root / 'assets' / 'analytics-config.js').read_text())), 'analytics', 'GA4 measurement ID missing')
if not args.preview:
    require((args.root / '.nojekyll').is_file(), 'Pages', 'missing .nojekyll')
    require((args.root / 'CNAME').read_text().strip() == urlsplit(DOMAIN).netloc, 'Pages', 'unexpected custom domain')

if errors:
    raise SystemExit('\n'.join(errors))
print(f'{len(canonical_pages)} canonical pages, {sum(articles.values())} article versions and {len(articles)} languages verified.')
