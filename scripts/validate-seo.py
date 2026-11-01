#!/usr/bin/env python3
"""Validate crawlability, translated metadata, source parity and sitemap closure.

Usage: python3 scripts/validate-seo.py [--baseline /path/to/original/static]
This checks real documents and cross-file contracts, not a browser or rankings.
"""
from pathlib import Path
from urllib.parse import urlsplit, unquote
from collections import Counter
import argparse
import copy
import hashlib
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from lxml import html

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / 'static'
BASE = 'https://antoniovfranco.com'
DATA = json.loads(subprocess.check_output(['node',str(ROOT/'scripts/seo-data.cjs')]))
LANGS = {'en','pt','es','zh','ar','ru','it','fr','de','ja','ko'}
parser = argparse.ArgumentParser()
parser.add_argument('--baseline', type=Path)
args = parser.parse_args()
errors, checks, articles, localized = [], 0, [], []

def check(condition, message):
    global checks
    checks += 1
    if not condition:
        errors.append(message)

def target(url):
    p = unquote(urlsplit(url).path).lstrip('/')
    q = STATIC / p
    return q/'index.html' if not q.suffix or p.endswith('/') else q

def norm(node):
    return re.sub(r'\s+',' ',node.text_content()).strip()

docs = {}
for p in STATIC.rglob('index.html'):
    doc = html.fromstring(p.read_bytes())
    rel = p.relative_to(STATIC).as_posix()
    docs[rel] = doc
    title = doc.xpath('//title/text()')
    canonical = doc.xpath('//link[@rel="canonical"]/@href')
    check(len(title)==1 and bool(title[0]), rel+': title')
    check(len(canonical)==1 and canonical[0].startswith(BASE+'/'), rel+': canonical')
    if not canonical:
        continue
    url = canonical[0]
    check(target(url).is_file(),rel+': canonical destination missing')
    description = doc.xpath('//meta[@name="description"]/@content')
    check(len(description)==1 and bool(description[0]),rel+': description')
    check(len(doc.xpath('//h1'))==1,rel+': exactly one H1')
    check(len(doc.xpath('//meta[@name="robots" and contains(@content,"max-snippet:-1")]'))==1,rel+': snippet availability')
    alternates = {e.get('hreflang'):e.get('href') for e in doc.xpath('//link[@hreflang]')}
    check(set(alternates)==LANGS|{'x-default'},rel+': complete hreflang cluster')
    check(len(doc.xpath('//link[@hreflang]'))==12,rel+': duplicate hreflang')
    for l,dest in alternates.items():
        check(target(dest).is_file(),rel+': alternate missing '+dest)
    check(alternates.get('x-default')==alternates.get('en'),rel+': stable default')
    graph_nodes = doc.xpath('//script[@type="application/ld+json"]/text()')
    check(len(graph_nodes)==1,rel+': one schema graph')
    try:
        schema = json.loads(graph_nodes[0])
        graph = schema['@graph']
    except (ValueError,IndexError,KeyError):
        check(False,rel+': invalid JSON-LD')
        continue
    ids = [n.get('@id') for n in graph]
    check(len(ids)==len(set(ids)),rel+': unique schema entity IDs')
    web = next((n for n in graph if n.get('@id')==url+'#webpage'),{})
    check(web.get('name')==norm(doc.xpath('//h1')[0]),rel+': schema visible headline parity')
    check(web.get('description')==description[0],rel+': schema description parity')
    for key in ['og:title','og:description','og:url','og:image','og:locale']:
        check(len(doc.xpath('//meta[@property=$key]',key=key))==1,rel+': '+key)
    check(doc.xpath('//meta[@property="og:url"]/@content')==[url],rel+': social canonical parity')
    feed = doc.xpath('//link[@type="application/rss+xml"]/@href')
    check(len(feed)==1,rel+': feed discovery')
    if feed:
        check((p.parent/feed[0]).resolve().is_file(),rel+': feed target')
    lang = doc.get('lang').split('-')[0]
    check(lang in LANGS,rel+': document language')
    check(doc.get('dir')==('rtl' if lang=='ar' else 'ltr'),rel+': direction')
    if p.parent.name in LANGS:
        localized.append((url,lang,rel,description[0],title[0]))
        check(alternates.get(lang)==url,rel+': hreflang self')
        for e in doc.xpath('//*[@data-t or @data-t-html]'):
            check(bool(norm(e)),rel+': empty translated element')
            translations = DATA['HW_CONTENT']['translations'][lang]
            key = e.get('data-t') or e.get('data-t-html')
            expected = translations.get(key)
            if expected:
                if e.get('data-t-html'):
                    expected = html.fromstring('<div>'+expected+'</div>').text_content()
                check(e.text_content()==expected,rel+': translation requires JavaScript: '+key)
        for e in doc.xpath('//*[@data-placeholder]'):
            expected = DATA['HW_CONTENT']['translations'][lang].get(e.get('data-placeholder'))
            if expected:
                check(e.get('placeholder')==expected,rel+': placeholder requires JavaScript')
    pid = doc.find('body').get('data-article')
    if pid:
        articles.append((pid,lang))
        article = doc.xpath('//article')[0]
        check(len(article.xpath('.//form'))==2,rel+': original two lead forms')
        postings = [n for n in graph if n.get('@type')=='BlogPosting']
        check(len(postings)==1,rel+': BlogPosting')
        posting = postings[0]
        check(posting.get('headline')==norm(doc.xpath('//h1')[0]),rel+': article headline parity')
        clone = copy.deepcopy(article)
        for n in clone.xpath('.//form | .//script | .//style | .//*[contains(concat(" ",normalize-space(@class)," ")," hw-inline-cta ")]'):
            n.getparent().remove(n)
        check(posting.get('articleBody')==norm(clone),rel+': full article body parity')
        original_citations = set(clone.xpath('.//a[starts-with(@href,"https://")]/@href'))
        check(set(c['url'] for c in posting['citation'])==original_citations,rel+': citation parity')
        check(len(posting.get('citation',[]))>=3,rel+': primary references')
        check(len(posting.get('workTranslation',[]))==10,rel+': translations graph')
        for node in posting.get('hasPart',[]):
            anchor = unquote(urlsplit(node['@id']).fragment)
            matches = article.xpath('.//*[@id=$anchor]',anchor=anchor)
            check(len(matches)==1 and node['text']==norm(matches[0]),rel+': section text parity '+anchor)
        check(len(posting.get('hasPart',[]))==len(article.xpath('./section[@id]')),rel+': all article sections')
        actual_date = doc.xpath('//meta[@property="article:published_time"]/@content')
        check(posting.get('datePublished')==(actual_date[0] if actual_date else None),rel+': no fabricated publication date')
        if args.baseline:
            old = html.fromstring((args.baseline/rel).read_bytes()).xpath('//article')[0]
            check(old.text_content()==article.text_content(),rel+': article text changed')
            check(html.tostring(old,method='c14n')==html.tostring(article,method='c14n'),rel+': article DOM changed')
    # Resolve local asset and navigation targets without requiring JavaScript.
    for e in doc.xpath('//*[@href or @src]'):
        attr = 'src' if e.get('src') else 'href'
        value = e.get(attr)
        if not value or value.startswith(('#','mailto:','tel:','data:','javascript:')):
            continue
        u = urlsplit(value)
        if u.netloc and u.netloc!='antoniovfranco.com':
            continue
        if u.netloc or value.startswith('/'):
            q = target(value)
        else:
            q = p.parent/unquote(u.path)
            if q.is_dir():
                q = q/'index.html'
        check(q.is_file(),rel+': broken local '+attr+' '+value)

check(len(docs)==117,'117 approved HTML documents')
check(len(localized)==110,'110 canonical translated pages')
check(len(articles)==33,'33 article translations')
check(all(v==3 for v in Counter(l for _,l in articles).values()),'three articles per language')
check(set(l for _,l in articles)==LANGS,'all article languages')
for lang in LANGS:
    rows = [r for r in localized if r[1]==lang]
    check(len(set(r[3] for r in rows))==len(rows),'unique descriptions in '+lang)
    check(len(set(r[4] for r in rows))==len(rows),'unique titles in '+lang)
    feed = ET.parse(STATIC/'blog'/lang/'index.xml')
    entries = feed.findall('channel/item')
    check(len(entries)==3,'all articles in '+lang+' feed')
    for item in entries:
        check(target(item.findtext('link')).is_file(),'feed target '+lang)
ns = {'s':'http://www.sitemaps.org/schemas/sitemap/0.9','x':'http://www.w3.org/1999/xhtml'}
sm = ET.parse(STATIC/'sitemap.xml')
urls = sm.findall('s:url',ns)
locs = [n.findtext('s:loc',namespaces=ns) for n in urls]
check(set(locs)=={r[0] for r in localized},'sitemap contains exactly canonical URLs')
check(len(locs)==len(set(locs))==110,'no sitemap duplicates')
for node in urls:
    links = {e.get('hreflang'):e.get('href') for e in node.findall('x:link',ns)}
    check(set(links)==LANGS|{'x-default'},'sitemap language cluster')
    source = docs[target(node.findtext('s:loc',namespaces=ns)).relative_to(STATIC).as_posix()]
    expected = {e.get('hreflang'):e.get('href') for e in source.xpath('//link[@hreflang]')}
    check(links==expected,'HTML/sitemap alternate parity')
for rel,doc in docs.items():
    for a in doc.xpath('//link[@hreflang]'):
        other = docs[target(a.get('href')).relative_to(STATIC).as_posix()]
        actual = {e.get('hreflang'):e.get('href') for e in other.xpath('//link[@hreflang]')}
        check(actual=={e.get('hreflang'):e.get('href') for e in doc.xpath('//link[@hreflang]')},rel+': nonreciprocal hreflang')
robots = (STATIC/'robots.txt').read_text()
check('Sitemap: '+BASE+'/sitemap.xml' in robots,'robots sitemap discovery')
check('Disallow:' not in robots,'no accidental crawler exclusion')
if args.baseline:
    for p in (args.baseline/'hw').rglob('*'):
        if p.is_file() and p.name!='site.js':
            check(p.read_bytes()==(STATIC/p.relative_to(args.baseline)).read_bytes(),'approved asset modified '+str(p))
summary = {'status':'PASS' if not errors else 'FAIL','checks':checks,'html_pages':len(docs),
           'canonical_pages':len(localized),'article_pages':len(articles),'languages':sorted(LANGS),
           'baseline_comparison':bool(args.baseline),'errors':errors}
(ROOT/'reports/validation.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(summary,ensure_ascii=False,indent=2))
raise SystemExit(bool(errors))
