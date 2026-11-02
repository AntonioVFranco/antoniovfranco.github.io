#!/usr/bin/env python3
"""Pre-render existing translations and build truthful, localized SEO metadata.

No new visible copy, CSS, components, images, research claims or lead behavior.
Usage: python3 scripts/optimize-seo.py
Requires Node.js and scripts/requirements-seo.txt. Deployment serves static/.
"""
from pathlib import Path
from urllib.parse import urlsplit, unquote, quote
from datetime import datetime
from email.utils import format_datetime
import copy
import json
import posixpath
import re
import subprocess
import xml.etree.ElementTree as ET
from lxml import html, etree

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / 'static'
BASE = 'https://antoniovfranco.com'
DATA = json.loads(subprocess.check_output(['node', str(ROOT / 'scripts/seo-data.cjs')]))
C = DATA['HW_CONTENT']
LANGS = list(DATA['HW_SLUGS']['agentic-finetuning'])
LANG_TAG = {'pt': 'pt-BR', 'zh': 'zh-CN'}
OG_LOCALE = dict(zip(LANGS, ['en_US', 'pt_BR', 'es_ES', 'zh_CN', 'ar_SA', 'ru_RU', 'it_IT', 'fr_FR', 'de_DE', 'ja_JP', 'ko_KR']))
POSTS = {p['id']: p for p in C['posts']}
SECTIONS = ['blog', 'about', 'contact', 'research', 'open-source', 'privacy']
SHORT_TITLES = {
 'slm-catalog-enrichment': dict(zip(LANGS, [
  'SLM Fine-Tuning for Marketplace Catalog Costs', 'Fine-tuning de SLMs e custos de catálogos',
  'Fine-tuning de SLM y costes de catálogos', 'SLM 微调与电商商品目录成本',
  'الضبط الدقيق لنماذج SLM وتكلفة كتالوجات المنتجات', 'Дообучение SLM и стоимость товарных каталогов',
  'Fine-tuning degli SLM e costi dei cataloghi', 'Fine-tuning des SLM et coûts des catalogues',
  'SLM-Fine-Tuning und Kosten der Kataloganreicherung', 'SLM のファインチューニングと商品カタログのコスト',
  'SLM 파인튜닝과 상품 카탈로그 비용'])),
 'n8n-langgraph': dict(zip(LANGS, [
  'n8n 3.0 vs LangGraph for AI Agents', 'n8n 3.0 vs LangGraph para agentes de IA',
  'n8n 3.0 vs LangGraph para agentes de IA', 'n8n 3.0 与 LangGraph：AI 智能体工程',
  'n8n 3.0 أم LangGraph لوكلاء الذكاء الاصطناعي', 'n8n 3.0 и LangGraph для ИИ-агентов',
  'n8n 3.0 e LangGraph per gli agenti IA', 'n8n 3.0 ou LangGraph pour les agents IA',
  'n8n 3.0 vs. LangGraph für KI-Agenten', 'AI エージェント開発：n8n 3.0 と LangGraph',
  'AI 에이전트 개발: n8n 3.0과 LangGraph'])),
 'agentic-finetuning': dict(zip(LANGS, [
  'Agentic Fine-Tuning: Smaller Models and AI Costs', 'Fine-tuning agêntico: modelos menores e custos de IA',
  'Fine-tuning agéntico: modelos pequeños y costes de IA', '智能体微调：小模型与 AI 成本',
  'الضبط الدقيق الوكيلي: نماذج أصغر وتكاليف الذكاء الاصطناعي',
  'Агентное дообучение: малые модели и стоимость ИИ',
  'Fine-tuning agentico: piccoli modelli e costi IA', 'Fine-tuning agentique : petits modèles et coûts IA',
  'Agentisches Fine-Tuning: kleine Modelle und KI-Kosten', 'エージェント型ファインチューニング：小型モデルと AI コスト',
  '에이전트 파인튜닝: 소형 모델과 AI 비용']))}
SHORT_TITLES['openclaw-saas-costs'] = {'en': 'OpenClaw and Open Source: SaaS Replacement Costs', 'pt': 'OpenClaw e open source: quanto custa substituir SaaS?', 'es': 'OpenClaw y código abierto: costes de sustituir SaaS', 'zh': 'OpenClaw 与开源软件：替代 SaaS 的成本', 'ar': 'OpenClaw والبرمجيات المفتوحة: تكلفة استبدال SaaS', 'ru': 'OpenClaw и открытый код: стоимость замены SaaS', 'it': 'OpenClaw e open source: costi per sostituire SaaS', 'fr': 'OpenClaw et open source : coût du remplacement SaaS', 'de': 'OpenClaw und Open Source: Kosten für den SaaS-Ersatz', 'ja': 'OpenClaw とオープンソース：SaaS の置き換え費用', 'ko': 'OpenClaw와 오픈 소스: SaaS 대체 비용'}
HOME_TITLES = dict(zip(LANGS, [
 'AI Engineering & Efficient Models', 'Engenharia de IA e modelos eficientes',
 'Ingeniería de IA y modelos eficientes', 'AI 工程与高效模型', 'هندسة الذكاء الاصطناعي والنماذج الكفؤة',
 'Инженерия ИИ и эффективные модели', 'Ingegneria IA e modelli efficienti',
 'Ingénierie IA et modèles efficaces', 'KI-Engineering und effiziente Modelle',
 'AI エンジニアリングと効率的なモデル', 'AI 엔지니어링과 효율적인 모델']))
TOPICS = {'slm-catalog-enrichment': ['Small language models', 'Fine-tuning', 'Product attribute extraction', 'Model economics'],
 'n8n-langgraph': ['AI agents', 'n8n', 'LangGraph', 'Durable execution'],
 'agentic-finetuning': ['Agentic fine-tuning', 'Small language models', 'LoRA', 'Reinforcement learning']}

TOPICS['openclaw-saas-costs'] = ['OpenClaw', 'Open-source software', 'SaaS costs', 'AI agents', 'Model economics']

def cls(name):
    return 'contains(concat(" ",normalize-space(@class)," ")," ' + name + ' ")'

def text(e):
    return re.sub(r'\s+', ' ', e.text_content()).strip()

def set_text(e, value):
    for child in list(e):
        e.remove(child)
    e.text = value

def set_html(e, value):
    for child in list(e):
        e.remove(child)
    e.text = None
    for part in html.fragments_fromstring(value):
        if isinstance(part, str):
            if len(e):
                e[-1].tail = (e[-1].tail or '') + part
            else:
                e.text = (e.text or '') + part
        else:
            e.append(part)

def by_id(doc, name):
    nodes = doc.xpath('//*[@id=$id]', id=name)
    return nodes[0] if nodes else None

def route(section, lang):
    return '/' + (section + '/' if section else '') + lang + '/'

def absolute(path):
    return BASE + quote(path, safe='/#')

def article_route(pid, lang):
    return '/articles/' + DATA['HW_SLUGS'][pid][lang] + '/' + lang + '/'

def localize(path, lang):
    u = urlsplit(path)
    parts = unquote(u.path).strip('/').split('/')
    if parts and parts[0] == 'articles' and len(parts) > 1:
        for pid, slugs in DATA['HW_SLUGS'].items():
            if parts[1] == pid or parts[1] in slugs.values():
                target = article_route(pid, lang)
                break
        else:
            return path
    else:
        target = route(parts[0] if parts and parts[0] in SECTIONS else '', lang)
    return target + ('?' + u.query if u.query else '') + ('#' + u.fragment if u.fragment else '')

def prerender(doc, lang, relative):
    """Mirror existing initial site.js/v5-ui.js rendering; never invent copy."""
    body = doc.find('body')
    trans = C['translations'][lang]
    for e in doc.xpath('//*[@data-t]'):
        if trans.get(e.get('data-t')):
            set_text(e, trans[e.get('data-t')])
    for e in doc.xpath('//*[@data-t-html]'):
        if trans.get(e.get('data-t-html')):
            set_html(e, trans[e.get('data-t-html')])
    for e in doc.xpath('//*[@data-placeholder]'):
        if trans.get(e.get('data-placeholder')):
            e.set('placeholder', trans[e.get('data-placeholder')])
    current = by_id(doc, 'current-lang')
    if current is not None:
        set_text(current, {'zh': 'CN'}.get(lang, lang.upper()))
    author = DATA.get('HW_AUTHOR', {}).get(lang)
    if author:
        expressions = [f'//*[{cls("hw-author-caption")}]', f'//*[{cls("hw-author-role")}]',
                       f'//*[{cls("hw-author-follow")}]/span', f'//*[{cls("hw-author-bio")}]']
        for expression, value in zip(expressions, author):
            for e in doc.xpath(expression):
                set_text(e, value)
    promo = by_id(doc, 'promo-text')
    if promo is not None and trans.get('promo1'):
        set_text(promo, trans['promo1'])
    service = by_id(doc, 'service-title')
    if service is not None:
        row = C['serviceCopy'][lang][0]
        set_text(service, row[1])
        set_text(by_id(doc, 'service-desc'), row[2])
        host = by_id(doc, 'service-list')
        set_text(host, '')
        for value in row[3]:
            etree.SubElement(host, 'li').text = value
    landing = body.get('data-landing')
    if landing and landing in C['landing'][lang] and by_id(doc, 'landing-title') is not None:
        row = C['landing'][lang][landing]
        set_text(by_id(doc, 'landing-title'), row[1])
        set_text(by_id(doc, 'landing-description'), row[2])
        host = by_id(doc, 'landing-blocks')
        set_text(host, '')
        for title, desc in row[3]:
            d = etree.SubElement(host, 'div', {'class': 'hw-landing-tile'})
            h = etree.SubElement(d, 'a' if '@' in title else 'h2')
            if '@' in title:
                h.set('href', route('contact', lang))
            h.text = title
            etree.SubElement(d, 'p').text = desc
    privacy = doc.xpath(f'//*[{cls("hw-privacy")}]')
    if privacy:
        d = DATA['HW_PRIVACY'].get(lang) or DATA['HW_PRIVACY'].get('en')
        if d:
            host = privacy[0]
            set_text(host, '')
            etree.SubElement(host, 'div', {'class': 'hw-eyebrow'}).text = d['kicker']
            etree.SubElement(host, 'h1').text = d['title']
            for heading, paragraph in d['sections']:
                etree.SubElement(host, 'h2').text = heading
                etree.SubElement(host, 'p').text = paragraph
    found = by_id(doc, 'hw-found-intro')
    if found is not None:
        row = DATA['HW_V5']['panels'][lang][0]
        set_text(found, row[1])
        host = by_id(doc, 'hw-found-items')
        set_text(host, '')
        for value in row[2]:
            p = etree.SubElement(host, 'p')
            etree.SubElement(p, 'i', {'aria-hidden': 'true'})
            etree.SubElement(p, 'span').text = value
    # These links are localized by the existing runtime; expose the same hrefs
    # to crawlers before JavaScript. Relative asset paths remain untouched.
    for a in doc.xpath('//a[starts-with(@href,"/")]'):
        if not a.get('href').startswith('/hw/'):
            a.set('href', localize(a.get('href'), lang))
    for a in doc.xpath(f'//*[{cls("hw-article-breadcrumb")}]/a'):
        a.set('href', route('blog', lang))

def meta(head, key, value, prop=False):
    name = 'property' if prop else 'name'
    for old in head.xpath('./meta[@' + name + '=$key]', key=key):
        head.remove(old)
    etree.SubElement(head, 'meta', {name: key, 'content': value})

def link(head, rel, href, **attrs):
    etree.SubElement(head, 'link', {'rel': rel, 'href': href, **attrs})

def clean_article(article):
    clone = copy.deepcopy(article)
    for node in clone.xpath('.//form | .//script | .//style | .//*[' + cls('hw-inline-cta') + ']'):
        node.getparent().remove(node)
    return clone

def citations(article):
    values = {}
    for a in article.xpath('.//a[starts-with(@href,"https://")]'):
        url = a.get('href')
        if urlsplit(url).hostname not in {'antoniovfranco.com', 'solutions.huyawo.com'}:
            values.setdefault(url, {'@type': 'CreativeWork', 'url': url, 'name': text(a) or url})
    return list(values.values())

def image_info(doc, pid):
    if pid:
        src = POSTS[pid]['cover']
    else:
        src = '/hw/assets/hero.webp'
    # The dimensions below are read from the existing image, not inferred.
    raw = (STATIC / src.lstrip('/')).read_bytes()
    if raw[:8] == b'\x89PNG\r\n\x1a\n':
        import struct
        w, h = struct.unpack('>II', raw[16:24])
    else:
        w = h = None
    result = {'@type': 'ImageObject', 'url': BASE + src, 'contentUrl': BASE + src}
    if w:
        result.update(width=w, height=h)
    return result

records = []
for path in sorted(STATIC.rglob('index.html')):
    relative = path.relative_to(STATIC)
    doc = html.fromstring(path.read_bytes())
    body = doc.find('body')
    pid = body.get('data-article')
    if pid and pid not in POSTS:
        raise ValueError('Unknown article: ' + pid)
    parts = relative.parts[:-1]
    localized = bool(parts and parts[-1] in LANGS)
    lang = parts[-1] if localized else 'en'
    section = parts[0] if parts and parts[0] in SECTIONS else ''
    doc.set('lang', LANG_TAG.get(lang, lang))
    doc.set('dir', 'rtl' if lang == 'ar' else 'ltr')
    # Root compatibility documents have no site.js. Preserve their approved
    # body rather than changing their UI to the localized template.
    if localized:
        prerender(doc, lang, relative)
    url = absolute(article_route(pid, lang) if pid else route(section, lang))
    alternates = {l: absolute(article_route(pid, l) if pid else route(section, l)) for l in LANGS}
    head = doc.find('head')
    for old in head.xpath('./link[@rel="canonical" or @hreflang] | ./script[@type="application/ld+json"]'):
        head.remove(old)
    headline = text(doc.xpath('//h1')[0])
    description = head.xpath('./meta[@name="description"]/@content')
    description = POSTS[pid]['excerpts'][lang] if pid else (description[0] if description else headline)
    if not pid and section in {'about', 'research', 'open-source'}:
        description = C['landing'][lang][section][2]
    elif not pid and section == 'contact':
        description = C['translations'][lang].get('contactPageLead') or text(doc.xpath('//p[@data-t="contactPageLead"]')[0])
    elif not pid and section == 'blog':
        description = C['translations'][lang].get('blogDesc') or text(doc.xpath('//p[@data-t="blogDesc"]')[0])
    elif not pid and section == 'privacy':
        privacy_copy = DATA['HW_PRIVACY'][lang]
        description = privacy_copy['title'] + '. ' + privacy_copy['sections'][0][1]
    if not description:
        description = text(doc.xpath('//main//p')[0])
    page_title = (SHORT_TITLES[pid][lang] if pid else HOME_TITLES[lang] if not section else headline) + ' | Antonio V. Franco'
    set_text(head.find('title'), page_title)
    meta(head, 'description', description)
    meta(head, 'author', 'Antonio V. Franco')
    meta(head, 'robots', 'index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1')
    link(head, 'canonical', url)
    for old in head.xpath('./link[@rel="author"]'):
        head.remove(old)
    link(head, 'author', BASE + '/about/' + lang + '/')
    for l, alternate in alternates.items():
        link(head, 'alternate', alternate, hreflang=l)
    link(head, 'alternate', alternates['en'], hreflang='x-default')
    feed_path = '/blog/' + lang + '/index.xml'
    # Keep feed discovery relative so it also works in the localhost archive.
    feed_relative = posixpath.relpath(feed_path.lstrip('/'), str(relative.parent))
    for old in head.xpath('./link[@type="application/rss+xml"]'):
        head.remove(old)
    link(head, 'alternate', feed_relative, type='application/rss+xml', title='Antonio V. Franco (' + lang + ')')
    image = image_info(doc, pid)
    meta(head, 'og:type', 'article' if pid else 'website', True)
    for key, value in {'og:title': headline, 'og:description': description, 'og:url': url,
                       'og:site_name': 'Antonio V. Franco', 'og:locale': OG_LOCALE[lang],
                       'og:image': image['url'], 'og:image:secure_url': image['url'],
                       'og:image:type': 'image/png' if pid else 'image/webp', 'og:image:alt': headline}.items():
        meta(head, key, value, True)
    for old in head.xpath('./meta[@property="og:locale:alternate"]'):
        head.remove(old)
    for l in LANGS:
        if l != lang:
            etree.SubElement(head, 'meta', property='og:locale:alternate', content=OG_LOCALE[l])
    if image.get('width'):
        meta(head, 'og:image:width', str(image['width']), True)
        meta(head, 'og:image:height', str(image['height']), True)
    for key, value in {'twitter:card': 'summary_large_image', 'twitter:title': headline,
                       'twitter:description': description, 'twitter:image': image['url'],
                       'twitter:image:alt': headline}.items():
        meta(head, key, value)
    person = {'@type': 'Person', '@id': BASE + '/#person', 'name': 'Antonio V. Franco',
              'url': BASE + '/about/' + lang + '/',
              'sameAs': ['https://github.com/AntonioVFranco', 'https://x.com/AntonioVFranco'],
              'affiliation': {'@id': 'https://huyawo.com/#organization'},
              'worksFor': {'@id': 'https://solutions.huyawo.com/#organization'}}
    huyawo = {'@type': 'Organization', '@id': 'https://huyawo.com/#organization',
              'name': 'Huyawo', 'url': 'https://huyawo.com/',
              'sameAs': ['https://github.com/OnHuyawo'], 'founder': {'@id': person['@id']}}
    solutions = {'@type': 'Organization', '@id': 'https://solutions.huyawo.com/#organization',
                 'name': 'Huyawo Solutions', 'url': 'https://solutions.huyawo.com/',
                 'founder': {'@id': person['@id']}, 'parentOrganization': {'@id': huyawo['@id']}}
    website = {'@type': 'WebSite', '@id': BASE + '/#website', 'url': BASE + '/',
               'name': 'Antonio V. Franco', 'inLanguage': [LANG_TAG.get(l,l) for l in LANGS],
               'publisher': {'@id': person['@id']}}
    webpage = {'@type': 'WebPage', '@id': url + '#webpage', 'url': url, 'name': headline,
               'description': description, 'inLanguage': LANG_TAG.get(lang, lang),
               'isPartOf': {'@id': website['@id']}, 'primaryImageOfPage': image}
    graph = [person, huyawo, solutions, website, webpage]
    if pid:
        article = clean_article(doc.xpath('//article')[0])
        pub = head.xpath('./meta[@property="article:published_time"]/@content')
        sections = []
        for node in article.xpath('./section[@id]'):
            headings = node.xpath('./h2')
            if headings:
                sections.append({'@type': 'WebPageElement', '@id': url + '#' + node.get('id'),
                                 'name': text(headings[0]), 'text': text(node)})
        cats = C['categories']
        category = C['categoryNames'][lang][cats.index(POSTS[pid]['category'])]
        posting = {'@type': 'BlogPosting', '@id': url + '#article', 'url': url,
                   'headline': headline, 'description': description,
                   'inLanguage': LANG_TAG.get(lang, lang), 'isAccessibleForFree': True,
                   'author': {'@id': person['@id']}, 'publisher': {'@id': person['@id']},
                   'image': image, 'mainEntityOfPage': {'@id': webpage['@id']},
                   'articleSection': category, 'articleBody': text(article),
                   'about': [{'@type': 'Thing', 'name': t} for t in TOPICS[pid]],
                   'citation': citations(article), 'hasPart': sections,
                   'workTranslation': [{'@id': other + '#article'} for l, other in alternates.items() if l != lang]}
        intro = article.xpath('./div[' + cls('hw-article-intro') + ']')
        if intro:
            posting['abstract'] = text(intro[0])
        if pub:
            posting['datePublished'] = pub[0]
            posting['dateModified'] = pub[0]  # No invented editorial update.
        webpage['mainEntity'] = {'@id': posting['@id']}
        crumb_nodes = doc.xpath(f'//*[{cls("hw-article-breadcrumb")}]/a')
        crumb_name = text(crumb_nodes[0]) if crumb_nodes else 'Blog'
        breadcrumb = {'@type': 'BreadcrumbList', '@id': url + '#breadcrumb', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': crumb_name, 'item': BASE + route('blog', lang)},
            {'@type': 'ListItem', 'position': 2, 'name': headline, 'item': url}]}
        webpage['breadcrumb'] = {'@id': breadcrumb['@id']}
        graph += [posting, breadcrumb]
    elif section == 'blog':
        listing = {'@type': 'ItemList', '@id': url + '#articles', 'itemListElement': [
            {'@type': 'ListItem', 'position': i+1, 'url': absolute(article_route(p['id'],lang)),
             'name': p['titles'][lang]} for i,p in enumerate(C['posts'])]}
        webpage['@type'] = 'CollectionPage'
        webpage['mainEntity'] = {'@id': listing['@id']}
        graph.append(listing)
    elif section == 'about':
        webpage['@type'] = 'ProfilePage'
        webpage['mainEntity'] = {'@id': person['@id']}
    elif section == 'contact':
        webpage['@type'] = 'ContactPage'
    schema = etree.SubElement(head, 'script', type='application/ld+json', id='hw-seo-graph')
    schema.text = json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False, separators=(',', ':')).replace('<','\\u003c')
    # Loading hints do not modify image bytes, geometry, or stylesheet order.
    for old in head.xpath('./link[@data-seo-preload]'):
        head.remove(old)
    if pid or not section:
        preload_src = urlsplit(image['url']).path.lstrip('/')
        link(head, 'preload', posixpath.relpath(preload_src, str(relative.parent)),
             **{'as': 'image', 'fetchpriority': 'high', 'data-seo-preload': 'true'})
    # Save HTML in UTF-8. lxml preserves script/style text and visible DOM order.
    path.write_text('<!doctype html>\n' + html.tostring(doc, encoding='unicode', method='html'), encoding='utf-8')
    records.append({'path': relative.as_posix(), 'url': url, 'lang': lang, 'article': pid,
                    'localized': localized, 'title': page_title, 'alternates': alternates,
                    'datePublished': pub[0] if pid and pub else None})

# Regenerate the sitemap from existing, indexable translated pages only.
NS = 'http://www.sitemaps.org/schemas/sitemap/0.9'
XH = 'http://www.w3.org/1999/xhtml'
ET.register_namespace('', NS)
ET.register_namespace('xhtml', XH)
site_map = ET.Element('{' + NS + '}urlset')
for record in records:
    if not record['localized']:
        continue
    item = ET.SubElement(site_map, '{' + NS + '}url')
    ET.SubElement(item, '{' + NS + '}loc').text = record['url']
    # This release changes served HTML, not the article's editorial date.
    ET.SubElement(item, '{' + NS + '}lastmod').text = '2026-11-02'
    for l, alternate in {**record['alternates'], 'x-default': record['alternates']['en']}.items():
        ET.SubElement(item, '{' + XH + '}link', rel='alternate', hreflang=l, href=alternate)
ET.ElementTree(site_map).write(STATIC/'sitemap.xml', encoding='utf-8', xml_declaration=True)
(STATIC/'robots.txt').write_text('User-agent: *\nAllow: /\n\nSitemap: ' + BASE + '/sitemap.xml\n', encoding='utf-8')
(STATIC/'.nojekyll').touch()

# Every language gets a feed containing all published articles. The
# undated first article stays undated; never invent its publication date.
ATOM = 'http://www.w3.org/2005/Atom'
ET.register_namespace('atom', ATOM)
for lang in LANGS:
    feed_url = BASE + '/blog/' + lang + '/index.xml'
    rss = ET.Element('rss', version='2.0')
    channel = ET.SubElement(rss, 'channel')
    for key, val in [('title','Antonio V. Franco'), ('link',BASE+route('blog',lang)),
                     ('description',HOME_TITLES[lang]), ('language',LANG_TAG.get(lang,lang))]:
        ET.SubElement(channel,key).text = val
    ET.SubElement(channel,'{'+ATOM+'}link',href=feed_url,rel='self',type='application/rss+xml')
    for p in C['posts']:
        entry = ET.SubElement(channel, 'item')
        for key,val in [('title',p['titles'][lang]), ('link',absolute(article_route(p['id'],lang))),
                        ('guid',absolute(article_route(p['id'],lang))), ('description',p['excerpts'][lang])]:
            ET.SubElement(entry,key).text = val
        if p.get('date'):
            ET.SubElement(entry,'pubDate').text = format_datetime(datetime.fromisoformat(p['date']+'T09:00:00-03:00'))
    payload = ET.tostring(rss, encoding='utf-8', xml_declaration=True)
    (STATIC/'blog'/lang/'index.xml').write_bytes(payload)
    if lang == 'en':
        for name in ['index.xml','blog/index.xml']:
            alias = ET.fromstring(payload)
            alias.find('channel/{'+ATOM+'}link').set('href',BASE+'/'+name)
            (STATIC/name).write_bytes(ET.tostring(alias,encoding='utf-8',xml_declaration=True))

# Optional discovery index, not a ranking mechanism or a replacement for HTML.
lines = ['# Antonio V. Franco', '', '> AI engineering articles by Antonio V. Franco.',
         '> Public research and engineering within the Huyawo ecosystem.', '', '## Website',
         '- [English homepage]('+BASE+'/en/)', '- [Author]('+BASE+'/about/en/)',
         '- [Huyawo Solutions](https://solutions.huyawo.com/)', '', '## Articles by language']
for lang in LANGS:
    lines += ['', '### '+LANG_TAG.get(lang,lang)]
    lines += ['- ['+p['titles'][lang]+']('+absolute(article_route(p['id'],lang))+'): '+p['excerpts'][lang] for p in C['posts']]
(STATIC/'llms.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
(ROOT/'reports/seo-inventory.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'html_pages':len(records),'canonical_pages':sum(r['localized'] for r in records),
                  'article_pages':sum(bool(r['article']) for r in records),'languages':LANGS,'status':'OK'}))
