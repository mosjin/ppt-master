"""Extract clickable <a href> regions from SVG for PPTX hyperlink overlay."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path


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
