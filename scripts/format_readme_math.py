"""
Convert README TeX delimiters to GitHub math: \\( \\) -> $...$, \\[ \\] -> $$...$$.
Nested \\( is supported. Skips content inside $$ ... $$ and inside fenced code blocks.

Run from project root:  python scripts/format_readme_math.py
"""

from __future__ import annotations

import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README = os.path.join(ROOT, "README.md")


def replace_inline_math_block(s: str) -> str:
    """Replace all \\(...\\) in s with $...$ (innermost / nested aware)."""
    out: list[str] = []
    i = 0
    while i < len(s):
        if i + 1 < len(s) and s[i] == "\\" and s[i + 1] == "(":
            depth = 1
            j = i + 2
            start = i + 2
            matched = False
            while j < len(s) - 1 and depth > 0:
                if s[j] == "\\" and s[j + 1] == "(":
                    depth += 1
                    j += 2
                    continue
                if s[j] == "\\" and s[j + 1] == ")":
                    depth -= 1
                    if depth == 0:
                        inner = s[start:j]
                        out.append("$")
                        out.append(inner)
                        out.append("$")
                        j += 2
                        i = j
                        matched = True
                        break
                    j += 2
                    continue
                j += 1
            if matched:
                continue
        out.append(s[i])
        i += 1
    return "".join(out)


def process_outside_code(text: str) -> str:
    """Process only outside ``` ... ``` and outside $$ ... $$ (display already converted)."""
    parts = re.split(r"(```[\s\S]*?```)", text)
    out: list[str] = []
    for p in parts:
        if p.startswith("```"):
            out.append(p)
            continue
        # split by $$ to not touch display math
        sub = p.split("$$")
        for k, seg in enumerate(sub):
            if k % 2 == 0:
                sub[k] = replace_inline_math_block(seg)
        out.append("$$".join(sub))
    return "".join(out)


def main() -> None:
    with open(README, encoding="utf-8") as f:
        text = f.read()

    # \\[ ... \\] -> $$ ... $$ (display)
    while True:
        m = re.search(r"\\\[(.*?)\\\]", text, flags=re.DOTALL)
        if not m:
            break
        inner = m.group(1).strip()
        rep = "$$\n" + inner + "\n$$"
        text = text[: m.start()] + rep + text[m.end() :]

    text = process_outside_code(text)

    with open(README, "w", encoding="utf-8") as f:
        f.write(text)
    print("Updated:", README)


if __name__ == "__main__":
    main()
