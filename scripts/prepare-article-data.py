#!/usr/bin/env python3
"""Load the shared data components on every localized article at publication."""
import argparse
from pathlib import Path
import posixpath

from lxml import html


ASSETS = (('link', 'href', 'article-data.css'), ('script', 'src', 'article-data.js'))


def prepare_page(page, root):
    document = html.document_fromstring(page.read_bytes())
    head = document.find('head')
    if head is None:
        raise ValueError(f'{page}: article has no document head')
    added = False
    for tag, attribute, name in ASSETS:
        target = root / 'assets' / name
        if not target.is_file():
            raise FileNotFoundError(target)
        url = posixpath.relpath(target, page.parent)
        if head.xpath(f'./{tag}[@{attribute}=$path]', path=url):
            continue
        node = html.Element(tag, {attribute: url})
        if tag == 'link':
            node.set('rel', 'stylesheet')
        else:
            node.set('defer', '')
        head.append(node)
        added = True
    if added:
        page.write_bytes(html.tostring(document, encoding='UTF-8', doctype='<!doctype html>'))
    return added


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('static'))
    root = parser.parse_args().root
    articles = sorted((root / 'articles').glob('*/*/index.html'))
    changed = sum(prepare_page(page, root) for page in articles)
    print(f'Article data components available on {len(articles)} pages ({changed} newly prepared).')


if __name__ == '__main__':
    main()
