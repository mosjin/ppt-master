"""把 SVG 中 widgets/<basename>.html 改写为实际文件名 widgets/<frame_id>_<basename>.html。

EduForge 约定：widget 文件名带帧号前缀（如 1-2-1-f04_discretize_demo.html），
但 SVG 作者常写 widgets/discretize_demo.html。本脚本扫描 widgets/ 目录建映射并修复。

Usage:
    python fix_widget_links.py <svg_dir> <widgets_dir>
"""
import re
import sys
from pathlib import Path

LINK_RE = re.compile(r'(<a\s+href=")widgets/([^"/]+\.html)(")', re.IGNORECASE)


def build_basename_map(widgets_dir: Path) -> dict[str, str]:
    """Map basename (no frame prefix) → real filename. E.g. 'foo.html' → '1-2-1-f04_foo.html'."""
    real_files = {p.name: p.name for p in widgets_dir.glob('*.html')}
    # Also map "stripped" name (without leading frame id) → real name
    for real in list(real_files.values()):
        m = re.match(r'^(\d+(?:-\d+)*(?:-f\d+)?_)(.+\.html)$', real)
        if m:
            basename = m.group(2)
            real_files.setdefault(basename, real)
    return real_files


def fix(svg_path: Path, name_map: dict[str, str]) -> int:
    text = svg_path.read_text(encoding='utf-8')
    changes = 0

    def _sub(m: re.Match) -> str:
        nonlocal changes
        bn = m.group(2)
        real = name_map.get(bn)
        if real and real != bn:
            changes += 1
            return f'{m.group(1)}widgets/{real}{m.group(3)}'
        return m.group(0)

    new_text = LINK_RE.sub(_sub, text)
    if changes:
        svg_path.write_text(new_text, encoding='utf-8')
    return changes


def main() -> None:
    if len(sys.argv) != 3:
        print('Usage: python fix_widget_links.py <svg_dir> <widgets_dir>')
        sys.exit(1)

    svg_dir = Path(sys.argv[1])
    widgets_dir = Path(sys.argv[2])
    if not svg_dir.is_dir() or not widgets_dir.is_dir():
        print('Both args must be directories')
        sys.exit(1)

    name_map = build_basename_map(widgets_dir)
    print(f'widgets directory has {len([k for k in name_map if "_" not in k])} real files, '
          f'{len(name_map)} total mappings')

    total = 0
    for svg in sorted(svg_dir.glob('*.svg')):
        n = fix(svg, name_map)
        if n:
            print(f'  {svg.name}: {n} link(s) rewritten')
            total += n
    print(f'\nTotal links rewritten: {total}')


if __name__ == '__main__':
    main()
