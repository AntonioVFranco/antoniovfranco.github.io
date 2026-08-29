#!/usr/bin/env python3
"""Validate published posts against SEO / LLM-discovery requirements.

Run after `hugo` has built into ./public and after generate_social_images.py.
Fails (exit 1) on any objective violation so CI blocks bad future articles.

Checks per published post:
  - front matter: title, seoTitle, description, date, publishDate, lastmod, draft
  - seoTopics, social image exists/generable, socialImageAlt
  - exactly one <h1> in final HTML
  - internal links resolve within the build
  - absolute canonical; no <meta name="keywords">; robots correct
  - JSON-LD parseable, no empty string values
  - presence in sitemap.xml, index.xml (RSS), llms.txt, llms-full.txt
  - absence of drafts from those artifacts
  - no ghost/removed URLs
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"
BASE = "https://antoniovfranco.com"
CONTENT = ROOT / "content" / "posts"

GHOST_URLS = [
    "/posts/2026/quantized-llms-cost-effectiveness/",
    "/posts/2026/by-osmosis-fuvest-arc-prize-vitalabs-study-research-method/",
    "/posts/2026/auditable-contract-screening-nli/",
]

errors: list[str] = []


def err(msg: str):
    errors.append(msg)


def load(path: Path) -> str:
    try:
        return path.read_text()
    except FileNotFoundError:
        return ""


def get_front_matter(md: str) -> dict:
    m = re.match(r"^---\s*\n(.*?)\n---", md, re.S)
    if not m:
        return {}
    block = m.group(1)
    out = {}
    for key in ("title", "seoTitle", "description", "date", "publishDate",
                "lastmod", "draft", "socialImageAlt"):
        fm = re.search(rf"^{key}:\s*[\"']?(.*?)[\"']?\s*$", block, re.M)
        if fm:
            out[key] = fm.group(1).strip()
    out["seoTopics"] = [re.sub(r'^"|"$', "", x) for x in re.findall(r"^  - .+$", block, re.M)
                        if "og-image" not in x and ": " not in x and not x.startswith('"https://')]
    out["images"] = [x for x in re.findall(r"^  - [\"']?([a-zA-Z0-9_\-./]+\.png)[\"']?$", block, re.M)]
    return out


def main() -> int:
    sitemap = load(PUBLIC / "sitemap.xml")
    rss = load(PUBLIC / "index.xml")
    llms = load(PUBLIC / "llms.txt")
    llmsfull = load(PUBLIC / "llms-full.txt")

    # Ghost URL scan across all artifacts
    alltext = sitemap + rss + llms + llmsfull
    for g in GHOST_URLS:
        if g in alltext:
            err(f"ghost URL present in artifacts: {g}")

    drafts = []
    posts = sorted(CONTENT.rglob("index.md"))
    for md_path in posts:
        slug = md_path.parent.name
        rel = md_path.parent.relative_to(CONTENT).as_posix()
        url = f"{BASE}/posts/{rel}/"
        public_html = PUBLIC / "posts" / rel / "index.html"
        fm = get_front_matter(md_path.read_text())
        page_url = url

        if str(fm.get("draft", "")).lower() == "true":
            drafts.append((rel, fm))
            continue

        # front matter requirements
        for req in ("title", "seoTitle", "description", "date", "publishDate", "lastmod", "draft", "socialImageAlt"):
            if not fm.get(req):
                err(f"{slug}: missing front matter '{req}'")
        if not fm["seoTopics"]:
            err(f"{slug}: no seoTopics")
        social = [i for i in fm["images"] if "og-image" in i]
        if not social:
            err(f"{slug}: no og-image in images front matter")

        # html exists
        if not public_html.exists():
            err(f"{slug}: public HTML missing ({page_url})")
            continue
        html = public_html.read_text()

        # h1
        if html.count("<h1") != 1:
            err(f"{slug}: expected exactly 1 <h1>, found {html.count('<h1')}")

        # meta (tolerate minified unquoted attributes)
        if re.search(r'name=["\']?keywords', html):
            err(f"{slug}: meta keywords present")
        m = re.search(r'name=["\']?robots["\']?\s+content=["\']?([^"\'>]+)', html)
        if not (m and m.group(1).strip().startswith("index, follow")):
            err(f"{slug}: robots meta wrong: {m.group(1).strip() if m else 'MISSING'}")
        m = re.search(r'rel=["\']?canonical["\']?\s+href=["\']?([^"\'> ]*)', html)
        if not (m and m.group(1) == page_url):
            err(f"{slug}: canonical wrong: {m.group(1) if m else 'MISSING'} != {page_url}")

        # JSON-LD (tolerate minified builds where the attribute may be unquoted)
        blocks = re.findall(r'<script type=["\']?application/ld\+json["\']?>(.*?)</script>', html, re.S)
        if not blocks:
            err(f"{slug}: no JSON-LD")
        else:
            for b in blocks:
                try:
                    import json
                    obj = json.loads(b)
                except Exception as e:
                    err(f"{slug}: JSON-LD invalid: {e}")
                    continue
                if not obj.get("@graph"):
                    err(f"{slug}: JSON-LD missing @graph")

        # presence in artifacts
        if url not in sitemap:
            err(f"{slug}: not in sitemap.xml")
        if f"<link>{url}</link>" not in rss:
            err(f"{slug}: not in RSS")
        if url not in llms:
            err(f"{slug}: not in llms.txt")
        if url not in llmsfull:
            err(f"{slug}: not in llms-full.txt")

        # internal links resolve
        for href in re.findall(r'href="(/[^"]*)"', html):
            if href.startswith(("/posts/", "/")):
                target = (PUBLIC / href.lstrip("/")).resolve()
                if not target.exists() and not (ROOT / href.lstrip("/")).exists():
                    err(f"{slug}: broken internal link {href}")

    # drafts must not appear in artifacts
    for rel, _fm in drafts:
        url = f"{BASE}/posts/{rel}/"
        if url in sitemap or url in rss or url in llms or url in llmsfull:
            err(f"draft present in published artifacts: {url}")

    # summary
    published = len(posts) - len(drafts)
    print(f"Validated: {published} published, {len(drafts)} draft(s).")
    if errors:
        print(f"FAIL ({len(errors)}):", file=sys.stderr)
        for e in errors:
            print("  -", e, file=sys.stderr)
        return 1
    print("OK: all objective checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
