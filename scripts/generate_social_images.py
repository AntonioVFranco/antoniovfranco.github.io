#!/usr/bin/env python3
"""Generate 1200x630 typographic social images for posts.

Deterministic: reads each post's index.md front matter and writes an
og-image.png into the page bundle (content/posts/<year>/<slug>/og-image.png).

Run before `hugo`:
    python3 scripts/generate_social_images.py

Dependencies: Pillow (`pip install pillow`). Uses system fonts via fc-match
with a DejaVu fallback. The generated image is NOT shown in the article body
or listing — it is referenced only in Open Graph / Twitter / JSON-LD.
"""
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content" / "posts"
WIDTH, HEIGHT = 1200, 630
BG = (255, 255, 255)          # white, matches light theme
FG = (17, 17, 17)             # near-black
ACCENT = (42, 122, 234)       # default site link blue
SITE = "ANTONIO V. FRANCO"


def find_font(wanted: str) -> str:
    """Resolve a font file by family name via fc-match, falling back to DejaVu."""
    try:
        out = subprocess.check_output(
            ["fc-match", "-f", "%{file}", wanted], timeout=5
        ).decode().strip()
        if out and Path(out).exists():
            return out
    except Exception:
        pass
    for cand in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        if Path(cand).exists():
            return cand
    return wanted


def load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def wrap_text(text: str, font, draw: ImageDraw.ImageDraw, max_width: int) -> list:
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=font) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def read_front_matter(md: str):
    fm_match = re.match(r"^---\s*\n(.*?)\n---", md, re.S)
    title = ""
    if fm_match:
        t = re.search(r"^title:\s*[\"']?(.*?)[\"']?\s*$", fm_match.group(1), re.M)
        if t:
            title = t.group(1).rstrip()
    return title


def generate(post_dir: Path) -> bool:
    md = post_dir / "index.md"
    if not md.exists():
        return False
    title = read_front_matter(md.read_text()) or post_dir.name.replace("-", " ").title()

    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)

    bold_path = find_font("DejaVu Sans:style=Bold")
    font_site = load_font(bold_path, 34)
    font_title = load_font(bold_path, 72)
    font_small = load_font(bold_path, 54)

    draw.text((70, 48), SITE, font=font_site, fill=ACCENT)

    # Try large font; fall back to small if it overflows vertically.
    lines = wrap_text(title, font_title, draw, WIDTH - 140)
    active_font = font_title
    line_h = font_title.size + 14
    if len(lines) * line_h > HEIGHT - 140 - 60:
        lines = wrap_text(title, font_small, draw, WIDTH - 140)
        active_font = font_small
        line_h = font_small.size + 12

    total_h = len(lines) * line_h
    y = (HEIGHT - total_h) // 2
    for ln in lines:
        draw.text((70, y), ln, font=active_font, fill=FG)
        y += line_h

    out = post_dir / "og-image.png"
    img.save(out, "PNG")
    return True


def main() -> int:
    count = 0
    if not CONTENT.exists():
        print(f"Content dir not found: {CONTENT}")
        return 1
    for post_dir in sorted(CONTENT.rglob("index.md")):
        d = post_dir.parent
        if generate(d):
            out = d / "og-image.png"
            print(f"generated {out.relative_to(ROOT)}")
            count += 1
    print(f"Done. {count} social image(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
