#!/usr/bin/env python3
"""Boost contrast of non-code grey text in generated SVG slides.

Many EduForge SVGs use IntelliJ comment grey (#808080) for both code
comments AND right-side annotation panels. The grey works on the dark
code-block background but flunks WCAG AA on the white slide background
(contrast ratio ~3.9:1, target ≥4.5:1). This script rewrites #808080 →
#374151 (slate-700, ~10.4:1) on every <text> element whose font-family
is NOT a code font, leaving syntax-highlighted comments untouched.

Idempotent. Safe to re-run after regenerating SVGs.

Usage:
    python fix_text_contrast.py <svg_dir>
"""
import re
import sys
from pathlib import Path

TEXT_RE = re.compile(
    r'(<text\s[^>]*?)fill="#808080"([^>]*>)',
    re.IGNORECASE,
)

CODE_FONT_KEYWORDS = ('consolas', 'courier', 'monospace')


def is_code_text(attrs: str) -> bool:
    m = re.search(r'font-family="([^"]*)"', attrs, re.IGNORECASE)
    if not m:
        return False
    family = m.group(1).lower()
    return any(kw in family for kw in CODE_FONT_KEYWORDS)


def fix(svg_path: Path) -> int:
    text = svg_path.read_text(encoding='utf-8')
    changes = 0

    def _sub(m: re.Match) -> str:
        nonlocal changes
        attrs = m.group(1) + m.group(2)
        if is_code_text(attrs):
            return m.group(0)
        changes += 1
        return f'{m.group(1)}fill="#374151"{m.group(2)}'

    new_text = TEXT_RE.sub(_sub, text)
    if changes:
        svg_path.write_text(new_text, encoding='utf-8')
    return changes


def main() -> None:
    if len(sys.argv) != 2:
        print('Usage: python fix_text_contrast.py <svg_dir>')
        sys.exit(1)

    svg_dir = Path(sys.argv[1])
    if not svg_dir.is_dir():
        print(f'Error: {svg_dir} is not a directory')
        sys.exit(1)

    total = 0
    for svg in sorted(svg_dir.glob('*.svg')):
        n = fix(svg)
        if n:
            print(f'  {svg.name}: {n} text(s) re-colored')
            total += n
    print(f'\nTotal non-code grey text re-colored: {total}')


if __name__ == '__main__':
    main()
