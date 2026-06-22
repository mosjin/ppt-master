"""
test_issue11_single_panel_layout.py — Regression guard for ppt-master#11.

Single content-panel slides (one full-width content panel, e.g. the EduForge
CSP `#EDE4D1` panel at x=120 y=180 w=1040 h=320) exhibited a systematic triple
layout defect:

  1. an empty colored header strip at the panel top carrying no title text;
  2. the first content line clipped against the panel / header top edge;
  3. content occupying only the upper ~30-60% of the panel, leaving a large
     empty band at the bottom (fixed-height panel that did not fit/fill).

Reproduction frames lived in consumer repo `new_csp_s_teach` (graph-theory
lessons): dijkstra P04, mst_kruskal P32.  This test pins the detection added to
`svg_quality_checker.SVGQualityChecker` so a future refactor cannot silently
drop the guard.

The guard is WARNING severity (heuristic layout signal) and must only fire on
single dominant-panel frames — card-grid / multi-panel / code-panel frames must
stay clean (no false positives; tree_centroid card-grid was 0/12 in the issue).

Linked issue: ppt-master#11
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "skills" / "ppt-master" / "scripts"))

from svg_quality_checker import SVGQualityChecker  # noqa: E402

MARKER = "single content-panel"
_HEAD = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720">'
_BG = '<rect width="1280" height="720" fill="#F5EFE3"/>'
_TAIL = "</svg>"


def _write(tmp_path: Path, name: str, body: str) -> str:
    p = tmp_path / name
    p.write_text(_HEAD + _BG + body + _TAIL, encoding="utf-8")
    return str(p)


def _warnings(svg_path: str) -> list[str]:
    res = SVGQualityChecker(template_mode=True).check_file(svg_path)
    return res["warnings"]


def _texts(ys: list[int]) -> str:
    return "".join(
        f'<text x="160" y="{y}" font-family="Noto Sans SC" font-size="14">line {i}</text>'
        for i, y in enumerate(ys)
    )


# --- defect #3: content underfills a fixed-height single panel ---------------
def test_underfilled_single_panel_flags(tmp_path: Path) -> None:
    # Panel 180..500 (h=320); content hugs top (first y=226) and stops at y=382,
    # leaving ~118px (37%) empty at the bottom — mirrors dijkstra P04.
    panel = '<rect x="120" y="180" width="1040" height="320" rx="10" fill="#EDE4D1"/>'
    body = panel + _texts([226, 266, 306, 346, 382])
    warns = _warnings(_write(tmp_path, "underfill.svg", body))
    assert any(MARKER in w for w in warns), warns


# --- defect #1: empty colored header strip (no title text) -------------------
def test_empty_colored_header_strip_flags(tmp_path: Path) -> None:
    panel = '<rect x="120" y="180" width="1040" height="320" rx="10" fill="#EDE4D1"/>'
    strip = '<rect x="120" y="180" width="1040" height="44" fill="#3C6589"/>'
    # First text well below the strip; nothing overlaps the strip band.
    body = panel + strip + _texts([260, 300, 340, 380, 420, 460])
    warns = _warnings(_write(tmp_path, "empty_header.svg", body))
    assert any(MARKER in w for w in warns), warns


# --- defect #2: first content line clipped at panel top ----------------------
def test_first_line_clipped_flags(tmp_path: Path) -> None:
    panel = '<rect x="120" y="180" width="1040" height="320" rx="10" fill="#EDE4D1"/>'
    # First line y=188 is only 8px below the panel top -> clipped.
    body = panel + _texts([188, 230, 280, 330, 380, 430, 480])
    warns = _warnings(_write(tmp_path, "clip.svg", body))
    assert any(MARKER in w for w in warns), warns


# --- no false positive: content fills the panel ------------------------------
def test_filled_single_panel_passes(tmp_path: Path) -> None:
    panel = '<rect x="120" y="180" width="1040" height="320" rx="10" fill="#EDE4D1"/>'
    # Content spans 215..455 — small top gap, small bottom gap, no header strip.
    body = panel + _texts([215, 255, 295, 335, 375, 415, 455])
    warns = _warnings(_write(tmp_path, "filled.svg", body))
    assert not any(MARKER in w for w in warns), warns


# --- no false positive: card-grid (multi-panel) frame ------------------------
def test_card_grid_not_flagged(tmp_path: Path) -> None:
    cards = "".join(
        f'<rect x="{x}" y="{y}" width="540" height="220" rx="10" fill="#FFFFFF" stroke="#3C6589"/>'
        f'<text x="{x + 20}" y="{y + 40}" font-size="22">card</text>'
        for x, y in [(80, 170), (660, 170), (80, 420), (660, 420)]
    )
    warns = _warnings(_write(tmp_path, "cardgrid.svg", cards))
    assert not any(MARKER in w for w in warns), warns


# --- no false positive: colored header strip that DOES carry title text ------
def test_colored_header_with_title_text_passes(tmp_path: Path) -> None:
    # A legitimate accent header: strip + title text overlapping it. The
    # `overlaps` discriminator must keep this from firing the empty-header check.
    panel = '<rect x="120" y="180" width="1040" height="320" rx="10" fill="#EDE4D1"/>'
    strip = '<rect x="120" y="180" width="1040" height="44" fill="#3C6589"/>'
    title = '<text x="160" y="210" font-size="26">Section Title</text>'  # inside strip band
    body = panel + strip + title + _texts([260, 300, 340, 380, 420, 460])
    warns = _warnings(_write(tmp_path, "legit_header.svg", body))
    assert not any(MARKER in w for w in warns), warns


# --- no false positive: two-column dominant panels (count guard) -------------
def test_two_column_panels_not_flagged(tmp_path: Path) -> None:
    # Both panels qualify as dominant (w>=820, h>=200, top in band) -> count != 1
    # -> the single-panel firewall must early-return, no warning.
    left = '<rect x="60" y="180" width="850" height="460" rx="10" fill="#EDE4D1"/>'
    right = '<rect x="940" y="180" width="850" height="460" rx="10" fill="#EDE4D1"/>'
    body = left + right + _texts([220, 260, 300])
    warns = _warnings(_write(tmp_path, "two_col.svg", body))
    assert not any(MARKER in w for w in warns), warns


# --- no false positive: full-width banner (short, not a content panel) -------
def test_short_banner_not_flagged(tmp_path: Path) -> None:
    banner = '<rect x="80" y="555" width="1120" height="105" rx="10" fill="#3C6589"/>'
    body = banner + '<text x="640" y="600" font-size="26">key takeaway</text>'
    warns = _warnings(_write(tmp_path, "banner.svg", body))
    assert not any(MARKER in w for w in warns), warns


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
