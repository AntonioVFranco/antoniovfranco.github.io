#!/usr/bin/env python3
"""Remediation helper: restore article bodies byte-for-byte from commit 1460add.

For each of the three articles, this script:
  1. Reads the CURRENT file (working tree, == 83f06c4).
  2. Splits it into front matter (up to the 2nd '---') and body.
  3. Drops the dead 'sources' field from the front matter (not consumed by any
     template, feed, validator, or artifact).
  4. Reads the 1460add version of the same file via `git show`.
  5. Splits that into front matter and body the same way.
  6. Writes a new file = <current front matter minus sources> + <1460add body>.

The body is taken verbatim from 1460add (byte-for-byte), so no editorial
intervention from 83f06c4 survives. The technical front matter (seoTitle,
description, seoTopics, entities, images, socialImageAlt, draft, lastmod) is
preserved because it is consumed by the SEO/LLM pipeline and does not alter
visible editorial content.

Usage:
    python3 scripts/restore_article_bodies.py
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE_COMMIT = "1460add"

ARTICLES = [
    "content/posts/2026/agentic-ai-slms-why-models-above-50-cents-burning-money/index.md",
    "content/posts/2026/glm-5-2-sonnet-4-5-and-open-models-were-enough/index.md",
    "content/posts/2026/deepseek-v4-flash-glm-5-2-combination/index.md",
]


def split_front_matter(text: str):
    """Return (front_matter_block, body) using only the first two '---' delimiters."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        raise ValueError("file does not start with '---'")
    # find the second '---' line
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        raise ValueError("no closing '---' delimiter found")
    fm = "\n".join(lines[1:end])
    body = "\n".join(lines[end + 1:])
    return fm, body


def git_show(commit: str, path: str) -> str:
    out = subprocess.check_output(
        ["git", "show", f"{commit}:{path}"], cwd=ROOT, text=True
    )
    return out


def drop_sources(fm: str) -> str:
    """Remove the dead 'sources:' block from front matter."""
    lines = fm.split("\n")
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if re.match(r"^sources:\s*$", line):
            # skip this line and any following indented list items
            i += 1
            while i < len(lines) and (lines[i].startswith("  - ") or lines[i].strip() == ""):
                i += 1
            continue
        out.append(line)
        i += 1
    return "\n".join(out)


def main() -> int:
    for rel in ARTICLES:
        path = ROOT / rel
        current = path.read_text()
        cur_fm, _cur_body = split_front_matter(current)

        base = git_show(BASE_COMMIT, rel)
        base_fm, base_body = split_front_matter(base)

        new_fm = drop_sources(cur_fm)
        new_text = "---\n" + new_fm + "\n---\n" + base_body

        path.write_text(new_text)
        print(f"restored {rel}")

    print("Done. Bodies restored byte-for-byte from 1460add; sources removed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
