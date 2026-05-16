"""Coordinate helpers, color parsing, and font utilities for DrawingML conversion."""

from __future__ import annotations

import re
from xml.etree import ElementTree as ET

from .drawingml_context import ConvertContext

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SVG_NS = 'http://www.w3.org/2000/svg'
XLINK_NS = 'http://www.w3.org/1999/xlink'

EMU_PER_PX = 9525  # 1 SVG px = 9525 EMU (96 DPI)
FONT_PX_TO_HUNDREDTHS_PT = 75  # 1px = 0.75pt -> 75 hundredths-of-a-point
ANGLE_UNIT = 60000  # DrawingML angle: 60000ths of a degree

# SVG attributes inheritable from parent <g>
INHERITABLE_ATTRS = [
    'fill', 'stroke', 'stroke-width', 'stroke-dasharray', 'stroke-linecap',
    'stroke-linejoin', 'opacity', 'fill-opacity', 'stroke-opacity',
    'font-family', 'font-size', 'font-weight', 'font-style',
    'text-anchor', 'letter-spacing', 'text-decoration',
]

# Known East Asian fonts
EA_FONTS = {
    'PingFang SC', 'PingFang TC', 'PingFang HK',
    'Microsoft YaHei', 'Microsoft JhengHei',
    'SimSun', 'SimHei', 'FangSong', 'KaiTi', 'STKaiti',
    'STHeiti', 'STSong', 'STFangsong', 'STXihei', 'STZhongsong',
    'Hiragino Sans', 'Hiragino Sans GB', 'Hiragino Mincho ProN',
    'Noto Sans SC', 'Noto Sans TC', 'Noto Serif SC', 'Noto Serif TC',
    'Source Han Sans SC', 'Source Han Sans TC',
    'Source Han Serif SC', 'Source Han Serif TC',
    'WenQuanYi Micro Hei', 'WenQuanYi Zen Hei',
    'YouYuan', 'LiSu', 'HuaWenKaiTi',
    'Songti SC', 'Songti TC',
}
SYSTEM_FONTS = {'system-ui', '-apple-system', 'BlinkMacSystemFont'}

# macOS/Linux-only fonts -> Windows equivalents
FONT_FALLBACK_WIN = {
    'PingFang SC': 'Microsoft YaHei',
    'PingFang TC': 'Microsoft JhengHei',
    'PingFang HK': 'Microsoft JhengHei',
    'Hiragino Sans': 'Microsoft YaHei',
    'Hiragino Sans GB': 'Microsoft YaHei',
    'Hiragino Mincho ProN': 'SimSun',
    'STHeiti': 'SimHei',
    'STSong': 'SimSun',
    'STKaiti': 'KaiTi',
    'STFangsong': 'FangSong',
    'STXihei': 'Microsoft YaHei',
    'STZhongsong': 'SimSun',
    'Songti SC': 'SimSun',
    'Songti TC': 'SimSun',
    'Noto Sans SC': 'Microsoft YaHei',
    'Noto Sans TC': 'Microsoft JhengHei',
    'Noto Serif SC': 'SimSun',
    'Noto Serif TC': 'SimSun',
    'Source Han Sans SC': 'Microsoft YaHei',
    'Source Han Sans TC': 'Microsoft JhengHei',
    'Source Han Serif SC': 'SimSun',
    'Source Han Serif TC': 'SimSun',
    'WenQuanYi Micro Hei': 'Microsoft YaHei',
    'WenQuanYi Zen Hei': 'Microsoft YaHei',
    # Latin fonts (macOS / Linux / Web -> Windows)
    'SF Pro': 'Segoe UI',
    'SF Pro Display': 'Segoe UI',
    'SF Pro Text': 'Segoe UI',
    'SF Mono': 'Consolas',
    'Menlo': 'Consolas',
    'Monaco': 'Consolas',
    'Helvetica Neue': 'Arial',
    'Helvetica': 'Arial',
    'Roboto': 'Segoe UI',
    'Ubuntu': 'Segoe UI',
    'Liberation Sans': 'Arial',
    'Liberation Serif': 'Times New Roman',
    'Liberation Mono': 'Consolas',
    'DejaVu Sans': 'Segoe UI',
    'DejaVu Serif': 'Times New Roman',
    'DejaVu Sans Mono': 'Consolas',
}

GENERIC_FONT_MAP = {
    'monospace': 'Consolas',
    'sans-serif': 'Segoe UI',
    'serif': 'Times New Roman',
}

# When the latin font is serif and no EA font is specified,
# prefer SimSun (serif CJK) over Microsoft YaHei (sans-serif CJK).
_SERIF_LATIN = {
    'Times New Roman', 'Georgia', 'Garamond', 'Palatino', 'Palatino Linotype',
    'Book Antiqua', 'Cambria', 'SimSun', 'Liberation Serif', 'DejaVu Serif',
}

# SVG stroke-dasharray -> DrawingML prstDash
DASH_PRESETS = {
    '4,4': 'dash',  '4 4': 'dash',
    '6,3': 'dash',  '6 3': 'dash',
    '2,2': 'sysDot', '2 2': 'sysDot',
    '8,4': 'lgDash', '8 4': 'lgDash',
    '8,4,2,4': 'lgDashDot', '8 4 2 4': 'lgDashDot',
}


# ---------------------------------------------------------------------------
# Coordinate helpers
# ---------------------------------------------------------------------------

def px_to_emu(px: float) -> int:
    """Convert SVG pixels to EMU."""
    return round(px * EMU_PER_PX)


def _f(val: str | None, default: float = 0.0) -> float:
    """Parse a float attribute value, returning default if missing."""
    if val is None:
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def _extract_inheritable_styles(elem: ET.Element) -> dict[str, str]:
    """Extract all SVG-inheritable presentation attributes from an element."""
    styles: dict[str, str] = {}
    for attr in INHERITABLE_ATTRS:
        val = elem.get(attr)
        if val is not None:
            styles[attr] = val
    return styles


def _get_attr(elem: ET.Element, attr: str, ctx: ConvertContext) -> str | None:
    """Get effective attribute: element's own value first, then inherited."""
    val = elem.get(attr)
    if val is not None:
        return val
    return ctx.inherited_styles.get(attr)


def ctx_x(val: float, ctx: ConvertContext) -> float:
    """Apply context scale + translate to an X coordinate."""
    return val * ctx.scale_x + ctx.translate_x


def ctx_y(val: float, ctx: ConvertContext) -> float:
    """Apply context scale + translate to a Y coordinate."""
    return val * ctx.scale_y + ctx.translate_y


def ctx_w(val: float, ctx: ConvertContext) -> float:
    """Apply context scale to a width value."""
    return val * ctx.scale_x


def ctx_h(val: float, ctx: ConvertContext) -> float:
    """Apply context scale to a height value."""
    return val * ctx.scale_y


# ---------------------------------------------------------------------------
# Color / style parsing
# ---------------------------------------------------------------------------

# CSS Color Module Level 3 named colors → 6-digit hex.
# Maintained inline (not imported from webcolors) so this module stays
# stdlib-only. See https://www.w3.org/TR/css-color-3/#svg-color
_CSS_NAMED_COLORS: dict[str, str] = {
    'aliceblue': 'F0F8FF', 'antiquewhite': 'FAEBD7', 'aqua': '00FFFF',
    'aquamarine': '7FFFD4', 'azure': 'F0FFFF', 'beige': 'F5F5DC',
    'bisque': 'FFE4C4', 'black': '000000', 'blanchedalmond': 'FFEBCD',
    'blue': '0000FF', 'blueviolet': '8A2BE2', 'brown': 'A52A2A',
    'burlywood': 'DEB887', 'cadetblue': '5F9EA0', 'chartreuse': '7FFF00',
    'chocolate': 'D2691E', 'coral': 'FF7F50', 'cornflowerblue': '6495ED',
    'cornsilk': 'FFF8DC', 'crimson': 'DC143C', 'cyan': '00FFFF',
    'darkblue': '00008B', 'darkcyan': '008B8B', 'darkgoldenrod': 'B8860B',
    'darkgray': 'A9A9A9', 'darkgreen': '006400', 'darkgrey': 'A9A9A9',
    'darkkhaki': 'BDB76B', 'darkmagenta': '8B008B', 'darkolivegreen': '556B2F',
    'darkorange': 'FF8C00', 'darkorchid': '9932CC', 'darkred': '8B0000',
    'darksalmon': 'E9967A', 'darkseagreen': '8FBC8F', 'darkslateblue': '483D8B',
    'darkslategray': '2F4F4F', 'darkslategrey': '2F4F4F', 'darkturquoise': '00CED1',
    'darkviolet': '9400D3', 'deeppink': 'FF1493', 'deepskyblue': '00BFFF',
    'dimgray': '696969', 'dimgrey': '696969', 'dodgerblue': '1E90FF',
    'firebrick': 'B22222', 'floralwhite': 'FFFAF0', 'forestgreen': '228B22',
    'fuchsia': 'FF00FF', 'gainsboro': 'DCDCDC', 'ghostwhite': 'F8F8FF',
    'gold': 'FFD700', 'goldenrod': 'DAA520', 'gray': '808080',
    'green': '008000', 'greenyellow': 'ADFF2F', 'grey': '808080',
    'honeydew': 'F0FFF0', 'hotpink': 'FF69B4', 'indianred': 'CD5C5C',
    'indigo': '4B0082', 'ivory': 'FFFFF0', 'khaki': 'F0E68C',
    'lavender': 'E6E6FA', 'lavenderblush': 'FFF0F5', 'lawngreen': '7CFC00',
    'lemonchiffon': 'FFFACD', 'lightblue': 'ADD8E6', 'lightcoral': 'F08080',
    'lightcyan': 'E0FFFF', 'lightgoldenrodyellow': 'FAFAD2', 'lightgray': 'D3D3D3',
    'lightgreen': '90EE90', 'lightgrey': 'D3D3D3', 'lightpink': 'FFB6C1',
    'lightsalmon': 'FFA07A', 'lightseagreen': '20B2AA', 'lightskyblue': '87CEFA',
    'lightslategray': '778899', 'lightslategrey': '778899', 'lightsteelblue': 'B0C4DE',
    'lightyellow': 'FFFFE0', 'lime': '00FF00', 'limegreen': '32CD32',
    'linen': 'FAF0E6', 'magenta': 'FF00FF', 'maroon': '800000',
    'mediumaquamarine': '66CDAA', 'mediumblue': '0000CD', 'mediumorchid': 'BA55D3',
    'mediumpurple': '9370DB', 'mediumseagreen': '3CB371', 'mediumslateblue': '7B68EE',
    'mediumspringgreen': '00FA9A', 'mediumturquoise': '48D1CC', 'mediumvioletred': 'C71585',
    'midnightblue': '191970', 'mintcream': 'F5FFFA', 'mistyrose': 'FFE4E1',
    'moccasin': 'FFE4B5', 'navajowhite': 'FFDEAD', 'navy': '000080',
    'oldlace': 'FDF5E6', 'olive': '808000', 'olivedrab': '6B8E23',
    'orange': 'FFA500', 'orangered': 'FF4500', 'orchid': 'DA70D6',
    'palegoldenrod': 'EEE8AA', 'palegreen': '98FB98', 'paleturquoise': 'AFEEEE',
    'palevioletred': 'DB7093', 'papayawhip': 'FFEFD5', 'peachpuff': 'FFDAB9',
    'peru': 'CD853F', 'pink': 'FFC0CB', 'plum': 'DDA0DD',
    'powderblue': 'B0E0E6', 'purple': '800080', 'rebeccapurple': '663399',
    'red': 'FF0000', 'rosybrown': 'BC8F8F', 'royalblue': '4169E1',
    'saddlebrown': '8B4513', 'salmon': 'FA8072', 'sandybrown': 'F4A460',
    'seagreen': '2E8B57', 'seashell': 'FFF5EE', 'sienna': 'A0522D',
    'silver': 'C0C0C0', 'skyblue': '87CEEB', 'slateblue': '6A5ACD',
    'slategray': '708090', 'slategrey': '708090', 'snow': 'FFFAFA',
    'springgreen': '00FF7F', 'steelblue': '4682B4', 'tan': 'D2B48C',
    'teal': '008080', 'thistle': 'D8BFD8', 'tomato': 'FF6347',
    'transparent': '000000',  # treat transparent as black (alpha lost in DML hex)
    'turquoise': '40E0D0', 'violet': 'EE82EE', 'wheat': 'F5DEB3',
    'white': 'FFFFFF', 'whitesmoke': 'F5F5F5', 'yellow': 'FFFF00',
    'yellowgreen': '9ACD32',
}


def parse_hex_color(color_str: str) -> str | None:
    """Parse SVG color value to a 6-digit uppercase hex string.

    Accepts:
    - `#RRGGBB` (canonical 6-digit hex)
    - `#RGB` (3-digit shorthand, expanded to 6 digits)
    - CSS3 named colors (`white`, `black`, `red`, ..., `rebeccapurple`)
    - `rgb(R, G, B)` with integer components 0-255 (functional notation)

    Returns the 6-digit uppercase hex without leading `#`, or `None` if the
    input cannot be parsed.

    NOTE: The named-color path was added to fix eduForge #19: `fill="white"`
    used to return `None` from this function, which forced callers to fall
    back to `'000000'` (black). On dark-themed slides every white text run
    rendered as black-on-black — entire pages appeared blank.
    """
    if not color_str:
        return None
    color_str = color_str.strip()
    if not color_str:
        return None

    # Functional notation: rgb(R, G, B) / rgb(R G B)
    if color_str.lower().startswith('rgb('):
        inner = color_str[4:].rstrip(')').replace(',', ' ').split()
        if len(inner) == 3:
            try:
                r, g, b = (max(0, min(255, int(float(v)))) for v in inner)
                return f'{r:02X}{g:02X}{b:02X}'
            except (ValueError, TypeError):
                return None
        return None

    # Hex notation: #RGB or #RRGGBB
    if color_str.startswith('#'):
        hex_part = color_str[1:]
        if len(hex_part) == 3:
            hex_part = ''.join(c * 2 for c in hex_part)
        if len(hex_part) == 6 and all(c in '0123456789abcdefABCDEF' for c in hex_part):
            return hex_part.upper()
        return None

    # CSS3 named color (case-insensitive)
    named = _CSS_NAMED_COLORS.get(color_str.lower())
    if named is not None:
        return named

    return None


def parse_stop_style(style_str: str) -> tuple[str | None, float]:
    """Parse a gradient stop's style attribute.

    Args:
        style_str: Style string like 'stop-color:#XXX;stop-opacity:N'.

    Returns:
        (color, opacity) tuple.
    """
    color = None
    opacity = 1.0
    if not style_str:
        return color, opacity

    for part in style_str.split(';'):
        part = part.strip()
        if part.startswith('stop-color:'):
            color = parse_hex_color(part.split(':', 1)[1].strip())
        elif part.startswith('stop-opacity:'):
            try:
                opacity = float(part.split(':', 1)[1].strip())
            except ValueError:
                pass

    return color, opacity


def resolve_url_id(url_str: str) -> str | None:
    """Extract ID from 'url(#someId)' reference."""
    if not url_str:
        return None
    m = re.match(r'url\(#([^)]+)\)', url_str.strip())
    return m.group(1) if m else None


def get_effective_filter_id(elem: ET.Element, ctx: ConvertContext) -> str | None:
    """Get the effective filter ID for an element, including inherited context."""
    filt = elem.get('filter')
    if filt:
        return resolve_url_id(filt)
    return ctx.filter_id


# ---------------------------------------------------------------------------
# Font parsing
# ---------------------------------------------------------------------------

def parse_font_family(font_family_str: str) -> dict[str, str]:
    """Parse CSS font-family into latin/ea typeface names.

    Prioritizes Windows-available fonts since PPTX is primarily opened on
    Windows. macOS/Linux-only fonts are mapped via FONT_FALLBACK_WIN.
    """
    if not font_family_str:
        return {'latin': 'Segoe UI', 'ea': 'Microsoft YaHei'}

    fonts = [f.strip().strip("'\"") for f in font_family_str.split(',')]
    latin_font = None
    ea_font = None

    for font in fonts:
        if font in SYSTEM_FONTS:
            continue
        if font in GENERIC_FONT_MAP:
            resolved = GENERIC_FONT_MAP[font]
            latin_font = latin_font or resolved
            continue

        win_font = FONT_FALLBACK_WIN.get(font, font)
        if font in EA_FONTS:
            ea_font = ea_font or win_font
        else:
            latin_font = latin_font or win_font

    # PPT renders CJK text via latin typeface when ea doesn't match
    if not latin_font and ea_font:
        latin_font = ea_font

    final_latin = latin_font or 'Segoe UI'

    # EA must always be a CJK-capable font
    if not ea_font:
        ea_font = 'SimSun' if final_latin in _SERIF_LATIN else 'Microsoft YaHei'

    return {'latin': final_latin, 'ea': ea_font}


def is_cjk_char(ch: str) -> bool:
    """Check if a character is CJK (Chinese/Japanese/Korean)."""
    cp = ord(ch)
    return (0x4E00 <= cp <= 0x9FFF or 0x3400 <= cp <= 0x4DBF or
            0x2E80 <= cp <= 0x2EFF or 0x3000 <= cp <= 0x303F or
            0xFF00 <= cp <= 0xFFEF or 0xF900 <= cp <= 0xFAFF or
            0x20000 <= cp <= 0x2A6DF)


def estimate_text_width(text: str, font_size: float, font_weight: str = '400') -> float:
    """Estimate text width in SVG pixels."""
    width = 0.0
    for ch in text:
        if is_cjk_char(ch):
            width += font_size
        elif ch == ' ':
            width += font_size * 0.3
        elif ch in 'mMwWOQ':
            width += font_size * 0.75
        elif ch in 'iIlj1!|':
            width += font_size * 0.3
        else:
            width += font_size * 0.55

    if font_weight in ('bold', '600', '700', '800', '900'):
        width *= 1.05

    return width


def _xml_escape(text: str) -> str:
    """Escape XML special characters."""
    return (text.replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;'))
