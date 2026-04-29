"""Extract clickable <a href> regions from SVG for PPTX hyperlink overlay."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

_PATH_NUM_RE = re.compile(r'-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?')
_PATH_CMD_RE = re.compile(r'([MmLlHhVvCcSsQqTtAaZz])([^MmLlHhVvCcSsQqTtAaZz]*)')

# Number of numeric arguments per command (one segment).
# Note: 'M' acts as 'L' for subsequent number pairs.
_PATH_ARG_COUNT = {
    'M': 2, 'L': 2, 'T': 2,
    'H': 1, 'V': 1,
    'C': 6, 'S': 4, 'Q': 4,
    'A': 7,  # rx ry rot large sweep x y
    'Z': 0,
}


def _path_bbox(d: str) -> tuple[float, float, float, float] | None:
    """Compute a bounding box for an SVG path's `d` attribute.

    Tracks the pen position through M/L/H/V/C/S/Q/T/A/Z commands so that
    arc-flag bytes (0/1) are not mistaken for coordinates.
    """
    cur_x = cur_y = 0.0
    start_x = start_y = 0.0
    xs: list[float] = []
    ys: list[float] = []

    for cmd, args_str in _PATH_CMD_RE.findall(d):
        upper = cmd.upper()
        relative = cmd != upper
        nums = [float(m) for m in _PATH_NUM_RE.findall(args_str)]
        argc = _PATH_ARG_COUNT.get(upper, 0)

        if upper == 'Z':
            cur_x, cur_y = start_x, start_y
            continue
        if argc == 0 or not nums:
            continue

        for i in range(0, len(nums), argc):
            chunk = nums[i:i + argc]
            if len(chunk) < argc:
                break
            if upper == 'H':
                nx = chunk[0] + (cur_x if relative else 0)
                ny = cur_y
            elif upper == 'V':
                nx = cur_x
                ny = chunk[0] + (cur_y if relative else 0)
            elif upper == 'A':
                # Endpoint is the last two numbers (x, y); skip flags.
                nx = chunk[5] + (cur_x if relative else 0)
                ny = chunk[6] + (cur_y if relative else 0)
            else:
                # M/L/T → last 2; C → last 2 of 6; S/Q → last 2 of 4
                nx = chunk[-2] + (cur_x if relative else 0)
                ny = chunk[-1] + (cur_y if relative else 0)

            xs.append(nx)
            ys.append(ny)
            cur_x, cur_y = nx, ny
            if upper == 'M' and i == 0:
                start_x, start_y = cur_x, cur_y
                # subsequent M-args behave as L
                upper = 'L'

    if not xs or not ys:
        return None
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    w = x_max - x_min
    h = y_max - y_min
    if w <= 0 or h <= 0:
        return None
    return (x_min, y_min, w, h)


_SVG_NS = 'http://www.w3.org/2000/svg'
_XLINK_NS = 'http://www.w3.org/1999/xlink'

_TAGS = {
    'svg': f'{{{_SVG_NS}}}svg',
    'a': f'{{{_SVG_NS}}}a',
    'rect': f'{{{_SVG_NS}}}rect',
    'circle': f'{{{_SVG_NS}}}circle',
    'ellipse': f'{{{_SVG_NS}}}ellipse',
    'text': f'{{{_SVG_NS}}}text',
    'g': f'{{{_SVG_NS}}}g',
    'path': f'{{{_SVG_NS}}}path',
    'line': f'{{{_SVG_NS}}}line',
    'polyline': f'{{{_SVG_NS}}}polyline',
    'polygon': f'{{{_SVG_NS}}}polygon',
    'image': f'{{{_SVG_NS}}}image',
}


def _float(val: str | None, default: float = 0.0) -> float:
    try:
        return float(val) if val else default
    except (ValueError, TypeError):
        return default


def _elem_bbox(elem: ET.Element) -> tuple[float, float, float, float] | None:
    """Return (x, y, w, h) bounding box for a single SVG element, or None."""
    tag = elem.tag

    if tag == _TAGS['rect'] or tag == _TAGS['image']:
        x = _float(elem.get('x'))
        y = _float(elem.get('y'))
        w = _float(elem.get('width'))
        h = _float(elem.get('height'))
        if w > 0 and h > 0:
            return (x, y, w, h)

    elif tag == _TAGS['circle']:
        cx = _float(elem.get('cx'))
        cy = _float(elem.get('cy'))
        r = _float(elem.get('r'))
        if r > 0:
            return (cx - r, cy - r, 2 * r, 2 * r)

    elif tag == _TAGS['ellipse']:
        cx = _float(elem.get('cx'))
        cy = _float(elem.get('cy'))
        rx = _float(elem.get('rx'))
        ry = _float(elem.get('ry'))
        if rx > 0 and ry > 0:
            return (cx - rx, cy - ry, 2 * rx, 2 * ry)

    elif tag == _TAGS['path']:
        # finalize_svg.py converts rounded rects to <path> — recover bbox
        # by walking M/L/H/V/C/S/Q/T/A commands so arc flag bytes (0/1)
        # don't get mistaken for coordinates.
        d = elem.get('d') or ''
        return _path_bbox(d)

    elif tag == _TAGS['text']:
        x = _float(elem.get('x'))
        y = _float(elem.get('y'))
        fs = _float(elem.get('font-size'), 14.0)
        text = (elem.text or '') + ''.join(c.text or '' for c in elem)
        char_w = fs * 0.6
        w = max(len(text) * char_w, 10.0)
        h = fs * 1.4
        return (x, y - fs, w, h)

    return None


def _union_bbox(
    bboxes: list[tuple[float, float, float, float]],
) -> tuple[float, float, float, float] | None:
    if not bboxes:
        return None
    x1 = min(b[0] for b in bboxes)
    y1 = min(b[1] for b in bboxes)
    x2 = max(b[0] + b[2] for b in bboxes)
    y2 = max(b[1] + b[3] for b in bboxes)
    return (x1, y1, x2 - x1, y2 - y1)


def _subtree_bbox(
    elem: ET.Element,
) -> tuple[float, float, float, float] | None:
    """Recursively compute bounding box for an element and all descendants."""
    bboxes: list[tuple[float, float, float, float]] = []
    bb = _elem_bbox(elem)
    if bb:
        bboxes.append(bb)
    for child in elem:
        cb = _subtree_bbox(child)
        if cb:
            bboxes.append(cb)
    return _union_bbox(bboxes)


def extract_links(
    svg_path: Path,
    slide_width_emu: int,
    slide_height_emu: int,
) -> list[dict]:
    """Extract <a href> regions from an SVG and return PPTX-ready link specs.

    Returns a list of dicts:
        {href: str, x: int, y: int, w: int, h: int}   (all in EMU)
    """
    try:
        tree = ET.parse(svg_path)
    except ET.ParseError:
        return []

    root = tree.getroot()

    # Get SVG canvas dimensions from viewBox or width/height
    vb = root.get('viewBox', '')
    if vb:
        parts = vb.replace(',', ' ').split()
        if len(parts) >= 4:
            svg_w = _float(parts[2])
            svg_h = _float(parts[3])
        else:
            svg_w = _float(root.get('width'), 1280.0)
            svg_h = _float(root.get('height'), 720.0)
    else:
        svg_w = _float(root.get('width'), 1280.0)
        svg_h = _float(root.get('height'), 720.0)

    if svg_w <= 0 or svg_h <= 0:
        return []

    scale_x = slide_width_emu / svg_w
    scale_y = slide_height_emu / svg_h

    links: list[dict] = []

    # Walk entire tree for <a> elements
    for anchor in root.iter(_TAGS['a']):
        href = (
            anchor.get('href')
            or anchor.get(f'{{{_XLINK_NS}}}href')
            or ''
        )
        if not href:
            continue

        # Skip fragment-only and javascript: links
        if href.startswith('#') or href.lower().startswith('javascript:'):
            continue

        bb = _subtree_bbox(anchor)
        if bb is None:
            continue

        x_svg, y_svg, w_svg, h_svg = bb
        # Clamp to SVG canvas
        x_svg = max(0.0, x_svg)
        y_svg = max(0.0, y_svg)
        w_svg = min(w_svg, svg_w - x_svg)
        h_svg = min(h_svg, svg_h - y_svg)

        if w_svg <= 0 or h_svg <= 0:
            continue

        links.append({
            'href': href,
            'x': round(x_svg * scale_x),
            'y': round(y_svg * scale_y),
            'w': round(w_svg * scale_x),
            'h': round(h_svg * scale_y),
        })

    return links
