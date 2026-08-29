#!/usr/bin/env python3
"""Submit URLs to IndexNow (Bing and participants) after a successful deploy.

Usage:
    python3 scripts/submit_indexnow.py

Reads the canonical URLs for the homepage, all published posts, and the sitemap
from a Hugo build (public/sitemap.xml or a URL list argument). A transient
IndexNow outage must NOT fail the deploy, so any submit failure only logs a
warning and exits 0.
"""
import os
import sys
import json
import ssl
import re
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEY = os.environ.get("INDEXNOW_KEY", "4aee93251a59ff29f22f84706d8b7e49")
BASE_URL = "https://antoniovfranco.com"
HOST = "antoniovfranco.com"
ENDPOINT = "https://api.indexnow.org/indexnow"


def collect_urls() -> list:
    """Homepage + every published post URL + the sitemap URL.

    Prefers the built public/ tree (present in the build job). Falls back to
    published content front matter when public/ is absent (e.g. a fresh
    checkout in the notify step).
    """
    urls = [f"{BASE_URL}/", f"{BASE_URL}/sitemap.xml"]
    public = ROOT / "public"
    if public.exists():
        for idx in public.rglob("index.html"):
            p = str(idx.relative_to(public))
            if p == "index.html":
                continue
            if p.endswith("/index.html"):
                urls.append(f"{BASE_URL}/{p[:-len('index.html')]}")
    else:
        # Fallback: published posts from content front matter.
        posts = ROOT / "content" / "posts"
        if posts.exists():
            for md in posts.rglob("index.md"):
                text = md.read_text(errors="replace")
                if re.search(r"^draft:\s*true\s*$", text, re.M):
                    continue
                year = md.parent.parent.name
                slug = md.parent.name
                urls.append(f"{BASE_URL}/posts/{year}/{slug}/")
    # keep only homepage / sitemap / post paths
    posts = [u for u in urls if "/posts/" in u or u in (f"{BASE_URL}/", f"{BASE_URL}/sitemap.xml")]
    return sorted(set(posts))


def submit(urls: list) -> bool:
    payload = json.dumps({"host": HOST, "key": KEY, "keyLocation": f"{BASE_URL}/{KEY}.txt", "urlList": urls}).encode()
    ctx = ssl.create_default_context()
    req = urllib.request.Request(
        ENDPOINT, data=payload, headers={"Content-Type": "application/json; charset=utf-8"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
            code = resp.getcode()
            print(f"IndexNow accepted ({code}) for {len(urls)} URL(s).")
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        print(f"IndexNow HTTP {e.code}: {body}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"IndexNow submit failed (transient, not failing deploy): {e}", file=sys.stderr)
        return False


def main() -> int:
    urls = collect_urls()
    print("Submitting to IndexNow:")
    for u in urls:
        print("  ", u)
    # Never fail the deploy on IndexNow outage.
    submit(urls)
    return 0


if __name__ == "__main__":
    sys.exit(main())
