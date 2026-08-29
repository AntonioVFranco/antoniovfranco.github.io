#!/usr/bin/env python3
"""Remediation test: verify article bodies are byte-for-byte identical to 1460add.

For each of the three articles:
  1. Read the current file.
  2. Split front matter from body using only the first two '---' delimiters.
  3. Read the 1460add version via `git show`.
  4. Extract its body the same way.
  5. Compare bytes; fail on ANY difference (added space, changed line break,
     changed quotes, changed alt text, added link, added heading, punctuation).

Also prints the SHA-256 of the original (1460add) and restored body for each
article. The pairs must be identical.

Usage:
    python3 scripts/verify_article_bodies.py
"""
import hashlib
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


def split_body(text: str) -> str:
    """Return the body (everything after the 2nd '---' delimiter)."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        raise ValueError("file does not start with '---'")
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        raise ValueError("no closing '---' delimiter found")
    return "\n".join(lines[end + 1:])


def git_show(commit: str, path: str) -> str:
    return subprocess.check_output(
        ["git", "show", f"{commit}:{path}"], cwd=ROOT, text=True
    )


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main() -> int:
    failed = False
    for rel in ARTICLES:
        path = ROOT / rel
        current = path.read_text()
        restored_body = split_body(current)

        base = git_show(BASE_COMMIT, rel)
        original_body = split_body(base)

        orig_sha = sha256(original_body.encode())
        rest_sha = sha256(restored_body.encode())
        match = restored_body == original_body

        print(f"=== {rel} ===")
        print(f"  original  SHA-256: {orig_sha}")
        print(f"  restored  SHA-256: {rest_sha}")
        print(f"  byte-identical:    {'YES' if match else 'NO'}")

        if not match:
            failed = True
            # show first differing line for diagnosis
            ol = original_body.split("\n")
            rl = restored_body.split("\n")
            for i in range(max(len(ol), len(rl))):
                a = ol[i] if i < len(ol) else "<EOF>"
                b = rl[i] if i < len(rl) else "<EOF>"
                if a != b:
                    print(f"  first diff at line {i+1}:")
                    print(f"    original : {a!r}")
                    print(f"    restored : {b!r}")
                    break

    if failed:
        print("\nFAIL: one or more bodies differ from 1460add.", file=sys.stderr)
        return 1
    print("\nOK: all three bodies are byte-for-byte identical to 1460add.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
