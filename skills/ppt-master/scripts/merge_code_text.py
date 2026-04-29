"""把 SVG 中同行连续 monospace <text> 合并为单 <text> + 多 <tspan>。

根因：SVG 生成器把语法高亮的 token 拆成多个 <text>，每个有独立 x。SVG 按
char_w≈7.0px 算 x，但 PowerPoint Consolas 实际 ~7.7px，textbox 边界微重叠。

修复：合并连续 monospace text 为单 textbox + colored runs。PowerPoint 按
run 顺序渲染，自动避免重叠。

Usage:
    python merge_code_text.py <svg_dir>
"""
import re
import sys
from pathlib import Path

# 匹配单行 <text x=".." y=".." font-family=".." font-size=".." fill=".." [xml:space=".."]>content</text>
TEXT_RE = re.compile(
    r'(?P<indent>[ \t]*)<text\s+'
    r'(?P<attrs>[^>]*)>'
    r'(?P<content>[^<]*)'
    r'</text>',
    re.IGNORECASE,
)

ATTR_RE = re.compile(r'([\w:-]+)="([^"]*)"')


def parse_attrs(attr_str: str) -> dict[str, str]:
    return dict(ATTR_RE.findall(attr_str))


def is_monospace(family: str) -> bool:
    f = family.lower()
    return any(k in f for k in ('consolas', 'courier', 'monospace'))


def merge_runs(svg_path: Path) -> int:
    """Merge contiguous monospace <text> on same y into one <text> with <tspan>s."""
    text = svg_path.read_text(encoding='utf-8')
    matches = list(TEXT_RE.finditer(text))
    if not matches:
        return 0

    # Group consecutive monospace text on same (y, font_size, font_family).
    groups: list[list[int]] = []
    current: list[int] = []
    last_key = None
    last_end = 0
    for i, m in enumerate(matches):
        attrs = parse_attrs(m.group('attrs'))
        family = attrs.get('font-family', '')
        if not is_monospace(family):
            if len(current) > 1:
                groups.append(current)
            current = []
            last_key = None
            last_end = m.end()
            continue
        y = attrs.get('y', '')
        size = attrs.get('font-size', '')
        key = (y, size, family)
        # only group if no other tag in between
        between = text[last_end:m.start()]
        if last_key == key and not re.search(r'<(?!/?text\b)', between):
            current.append(i)
        else:
            if len(current) > 1:
                groups.append(current)
            current = [i]
        last_key = key
        last_end = m.end()
    if len(current) > 1:
        groups.append(current)

    if not groups:
        return 0

    # Rewrite from the end so earlier offsets stay valid
    pieces = list(text)
    changes = 0
    for grp in reversed(groups):
        first_m = matches[grp[0]]
        first_attrs = parse_attrs(first_m.group('attrs'))
        first_fill = first_attrs.get('fill', '#000000')
        # Keep first text's x as anchor, drop fill (move to per-tspan)
        keep = {k: v for k, v in first_attrs.items() if k != 'fill'}
        # Force xml:space="preserve" so leading/trailing spaces survive
        keep['xml:space'] = 'preserve'
        attr_str = ' '.join(f'{k}="{v}"' for k, v in keep.items())

        tspans = []
        for idx in grp:
            m = matches[idx]
            attrs = parse_attrs(m.group('attrs'))
            fill = attrs.get('fill', first_fill)
            # tspan owns only the fill (other attrs inherit from <text>)
            content = m.group('content')
            tspans.append(f'<tspan fill="{fill}">{content}</tspan>')

        new_text = f'<text {attr_str}>{"".join(tspans)}</text>'
        # Replace from end of last match back to start of first
        start = matches[grp[0]].start()
        end = matches[grp[-1]].end()
        pieces[start:end] = list(new_text)
        changes += len(grp) - 1

    new = ''.join(pieces)
    if new != text:
        svg_path.write_text(new, encoding='utf-8')
    return changes


def main() -> None:
    if len(sys.argv) != 2:
        print('Usage: python merge_code_text.py <svg_dir>')
        sys.exit(1)

    svg_dir = Path(sys.argv[1])
    total_files = 0
    total_merges = 0
    for svg in sorted(svg_dir.glob('*.svg')):
        n = merge_runs(svg)
        if n:
            total_files += 1
            total_merges += n
            print(f'  {svg.name}: merged {n} text(s) into runs')
    print(f'\nTotal: {total_merges} merges across {total_files} files')


if __name__ == '__main__':
    main()
