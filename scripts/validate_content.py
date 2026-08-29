#!/usr/bin/env python3
"""Validate published posts against SEO / LLM-discovery requirements.

Run after `hugo` has built into ./public and after generate_social_images.py.
Fails (exit 1) on any objective violation so CI blocks bad future articles.

Checks per published post:
  - front matter (real YAML): title, seoTitle, description, date, publishDate,
    lastmod, draft, seoTopics (as a specific field), socialImageAlt
  - social image exists and is exactly 1200x630
  - exactly one <h1> in final HTML
  - internal links resolve within the build (does NOT require new links)
  - absolute unique canonical; no <meta name="keywords">; robots correct
  - JSON-LD parseable, no empty string values, no empty {} / empty @graph nodes
  - BlogPosting.headline == .Title and BlogPosting.name == .Title
  - date/publishDate/lastmod match the original editorial dates
  - presence in sitemap.xml, index.xml (RSS), llms.txt, llms-full.txt
  - absence of drafts from those artifacts
  - no ghost/removed URLs
  - does NOT impose headings, external sources, internal links, word counts,
    or any editorial formula on the body

Dependencies: PyYAML (`pip install pyyaml`).
"""
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"
BASE = "https://antoniovfranco.com"
CONTENT = ROOT / "content" / "posts"

# Original editorial dates (must not drift with commits / remediation).
ORIGINAL_DATES = {
    "agentic-ai-slms-why-models-above-50-cents-burning-money": {
        "date": "2026-06-13",
        "publishDate": "2026-06-13",
        "lastmod": "2026-06-13",
    },
    "glm-5-2-sonnet-4-5-and-open-models-were-enough": {
        "date": "2026-06-25",
        "publishDate": "2026-06-25",
        "lastmod": "2026-06-25",
    },
    "deepseek-v4-flash-glm-5-2-combination": {
        "date": "2026-07-24",
        "publishDate": "2026-07-24",
        "lastmod": "2026-07-24",
    },
}

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


def split_front_matter(text: str):
    """Return (front_matter_block, body) using only the first two '---' delimiters."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None, text
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return None, text
    fm = "\n".join(lines[1:end])
    body = "\n".join(lines[end + 1:])
    return fm, body


def parse_front_matter(md: str) -> dict:
    fm, _ = split_front_matter(md)
    if fm is None:
        return {}
    try:
        data = yaml.safe_load(fm)
    except Exception as e:
        err(f"front matter YAML parse error: {e}")
        return {}
    if not isinstance(data, dict):
        return {}
    return data


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
        fm = parse_front_matter(md_path.read_text())

        if str(fm.get("draft", "")).lower() == "true":
            drafts.append((rel, fm))
            continue

        # --- front matter requirements ---
        for req in ("title", "seoTitle", "description", "date", "publishDate",
                    "lastmod", "draft", "socialImageAlt"):
            if req not in fm or fm.get(req) in (None, ""):
                err(f"{slug}: missing front matter '{req}'")

        # seoTopics must be a specific list field (not confused with sources/entities/images)
        if not isinstance(fm.get("seoTopics"), list) or not fm["seoTopics"]:
            err(f"{slug}: seoTopics missing or not a non-empty list")
        else:
            for t in fm["seoTopics"]:
                if not isinstance(t, str) or not t.strip():
                    err(f"{slug}: seoTopics contains empty/invalid entry")

        # images must reference the social image
        images = fm.get("images") or []
        if not any("og-image" in str(i) for i in images):
            err(f"{slug}: no og-image in images front matter")

        # --- original editorial dates ---
        if slug in ORIGINAL_DATES:
            for field, expected in ORIGINAL_DATES[slug].items():
                actual = str(fm.get(field, "")).strip()
                if actual != expected:
                    err(f"{slug}: {field} = {actual!r}, expected {expected!r}")

        # --- social image exists and is exactly 1200x630 ---
        social_img = None
        for i in images:
            if "og-image" in str(i):
                social_img = md_path.parent / str(i)
                break
        if social_img is None:
            err(f"{slug}: social image file not found in front matter")
        elif not social_img.exists():
            err(f"{slug}: social image file missing: {social_img.name}")
        else:
            try:
                from PIL import Image
                with Image.open(social_img) as im:
                    w, h = im.size
                if (w, h) != (1200, 630):
                    err(f"{slug}: social image is {w}x{h}, expected 1200x630")
            except Exception as e:
                err(f"{slug}: cannot read social image: {e}")

        # --- html exists ---
        if not public_html.exists():
            err(f"{slug}: public HTML missing ({url})")
            continue
        html = public_html.read_text()

        # --- h1 ---
        if html.count("<h1") != 1:
            err(f"{slug}: expected exactly 1 <h1>, found {html.count('<h1')}")

        # --- meta (tolerate minified unquoted attributes) ---
        if re.search(r'name=["\']?keywords', html):
            err(f"{slug}: meta keywords present")
        m = re.search(r'name=["\']?robots["\']?\s+content=["\']?([^"\'>]+)', html)
        if not (m and m.group(1).strip().startswith("index, follow")):
            err(f"{slug}: robots meta wrong: {m.group(1).strip() if m else 'MISSING'}")
        m = re.search(r'rel=["\']?canonical["\']?\s+href=["\']?([^"\'> ]*)', html)
        if not (m and m.group(1) == url):
            err(f"{slug}: canonical wrong: {m.group(1) if m else 'MISSING'} != {url}")
        # canonical must be unique
        if html.count('rel="canonical"') + html.count("rel=canonical") != 1:
            err(f"{slug}: canonical not unique")

        # --- JSON-LD ---
        blocks = re.findall(r'<script type=["\']?application/ld\+json["\']?>(.*?)</script>', html, re.S)
        if not blocks:
            err(f"{slug}: no JSON-LD")
        else:
            for b in blocks:
                try:
                    obj = json.loads(b)
                except Exception as e:
                    err(f"{slug}: JSON-LD invalid: {e}")
                    continue
                graph = obj.get("@graph")
                if not isinstance(graph, list) or not graph:
                    err(f"{slug}: JSON-LD missing @graph")
                    continue
                for node in graph:
                    if not isinstance(node, dict) or not node:
                        err(f"{slug}: empty node in @graph")
                    elif not node.get("@type"):
                        err(f"{slug}: @graph node missing @type")
                    # no empty required string values
                    for k, v in node.items():
                        if isinstance(v, str) and v.strip() == "":
                            err(f"{slug}: empty string value for '{k}' in @graph")
                # BlogPosting headline/name must equal .Title
                for node in graph:
                    if isinstance(node, dict) and node.get("@type") == "BlogPosting":
                        if node.get("headline") != fm.get("title"):
                            err(f"{slug}: BlogPosting.headline != .Title")
                        if node.get("name") != fm.get("title"):
                            err(f"{slug}: BlogPosting.name != .Title")

        # --- presence in artifacts ---
        if url not in sitemap:
            err(f"{slug}: not in sitemap.xml")
        if f"<link>{url}</link>" not in rss:
            err(f"{slug}: not in RSS")
        if url not in llms:
            err(f"{slug}: not in llms.txt")
        if url not in llmsfull:
            err(f"{slug}: not in llms-full.txt")

        # --- internal links resolve (does NOT require new links) ---
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
