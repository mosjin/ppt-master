#!/usr/bin/env python3
"""Apply IntelliJ Classic Dark color scheme to SVG code blocks.

Replaces Catppuccin Mocha colors used in code blocks with IntelliJ Classic Dark.
Also adds xml:space="preserve" to fix leading-space indentation rendering.

Usage:
    python fix_code_colors.py <svg_dir>
    python fix_code_colors.py <svg_dir> --dry-run
"""

import re
import sys
from pathlib import Path

# Catppuccin Mocha → IntelliJ Classic Dark
# Only the code-block colors (leave slide background/card colors alone)
COLOR_MAP = [
    # Background of code block — must come first (substring safety)
    ('#1E1E2E', '#2B2B2B'),
    # Keyword: blue → orange-brown
    ('#89B4FA', '#CC7832'),
    # String: light green → muted green
    ('#A6E3A1', '#6A8759'),
    # Number: orange → steel blue
    ('#FAB387', '#6897BB'),
    # Default code text: light lavender → steel-grey
    ('#CDD6F4', '#A9B7C6'),
    # Comment: same grey, just unify to IntelliJ shade
    ('#6B7280', '#808080'),
]


def _apply_colors(text: str) -> str:
    for old, new in COLOR_MAP:
        text = text.replace(old, new)
    return text


def _add_xml_space_preserve(text: str) -> str:
    """Add xml:space="preserve" to <text> elements whose content starts with spaces.

    SVG xml:space="default" collapses leading/trailing whitespace.
    Preserve mode prevents that, fixing indentation rendering.
    """
    def _fix_text_elem(m: re.Match) -> str:
        tag_attrs = m.group(1)
        content = m.group(2)
        close = m.group(3)
        if not content.startswith(' '):
            return m.group(0)
        if 'xml:space' in tag_attrs:
            return m.group(0)
        return f'<text{tag_attrs} xml:space="preserve">{content}{close}'

    return re.sub(
        r'<text([^>]*)>([ ][^<]+)(</text>)',
        _fix_text_elem,
        text,
    )


def fix_svg(svg_path: Path, dry_run: bool = False) -> bool:
    """Apply IntelliJ Classic colors to one SVG. Returns True if changed."""
    original = svg_path.read_text(encoding='utf-8')

    # Only touch files that contain code blocks
    if '#1E1E2E' not in original and '#89B4FA' not in original:
        return False

    result = _apply_colors(original)
    result = _add_xml_space_preserve(result)

    if result == original:
        return False

    if not dry_run:
        svg_path.write_text(result, encoding='utf-8')
    return True


def main() -> None:
    args = sys.argv[1:]
    dry_run = '--dry-run' in args
    dirs = [a for a in args if not a.startswith('--')]

    if not dirs:
        print('Usage: python fix_code_colors.py <svg_dir> [--dry-run]')
        sys.exit(1)

    svg_dir = Path(dirs[0])
    if not svg_dir.is_dir():
        print(f'Error: {svg_dir} is not a directory')
        sys.exit(1)

    changed = 0
    skipped = 0
    for f in sorted(svg_dir.glob('*.svg')):
        if fix_svg(f, dry_run=dry_run):
            print(f'  {"[dry-run] " if dry_run else ""}Fixed: {f.name}')
            changed += 1
        else:
            skipped += 1

    mode = 'dry-run' if dry_run else 'applied'
    print(f'\n{mode}: {changed} fixed, {skipped} skipped (no code block)')


if __name__ == '__main__':
    main()
