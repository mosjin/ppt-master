"""
test_xml_space_preserve_contract.py — Regression guard for xml:space="preserve"
on SVG <text> elements in ppt-master's DrawingML converter.

Protects the receiver-side contract that eduForge V_CODE_TEXT_PRESERVE_SPACE
(introduced in eduForge v3.1.5, PR #35) depends on.  Without this test a future
refactor of drawingml_elements.py could silently stop honoring xml:space while
eduForge kept enforcing "preserve must be present" on the caller side.

Linked issues: eduForge_skill#31, ppt-master#9
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "skills" / "ppt-master" / "scripts"))

from svg_to_pptx.drawingml_context import ConvertContext  # noqa: E402
from svg_to_pptx.drawingml_elements import convert_text  # noqa: E402

# Namespace used by xml:space — must be set as a Clark-notation attribute.
XML_SPACE_NS = "{http://www.w3.org/XML/1998/namespace}space"

# Pattern matching every <a:t ...>...</a:t> run (no nested tags allowed by spec).
_AT_PATTERN = re.compile(r"<a:t[^>]*>[^<]*</a:t>")


def _make_text_elem(text_content: str, *, preserve: bool = False) -> ET.Element:
    """Build a minimal SVG <text> element with the given text content."""
    elem = ET.Element("text")
    elem.set("x", "10")
    elem.set("y", "20")
    elem.set("font-family", "Consolas, monospace")
    elem.set("font-size", "14")
    if preserve:
        elem.set(XML_SPACE_NS, "preserve")
    elem.text = text_content
    return elem


def _at_runs(xml: str) -> list[str]:
    """Return all <a:t ...>...</a:t> fragments from a DrawingML XML string."""
    return _AT_PATTERN.findall(xml)


# ---------------------------------------------------------------------------
# Test 1: without xml:space="preserve" — whitespace must collapse
# ---------------------------------------------------------------------------


def test_text_without_preserve_collapses_whitespace() -> None:
    """V1: plain <text> with leading spaces and newline → collapsed, no preserve attr."""
    # Arrange
    raw = "    int x = 0;\n  return 0;"
    elem = _make_text_elem(raw, preserve=False)
    ctx = ConvertContext()

    # Act
    result = convert_text(elem, ctx)

    # Assert
    assert result is not None, "convert_text returned None for a valid <text> element"
    runs = _at_runs(result.xml)
    assert runs, f"no <a:t> runs found in output:\n{result.xml}"

    for run in runs:
        assert 'xml:space="preserve"' not in run, (
            f'unexpected xml:space="preserve" on run without preserve input: {run!r}'
        )
        assert "    int" not in run, (
            f"leading 4-space indent survived collapse (should not): {run!r}"
        )


# ---------------------------------------------------------------------------
# Test 2: with xml:space="preserve" — whitespace must be kept verbatim
# ---------------------------------------------------------------------------


def test_text_with_preserve_keeps_whitespace() -> None:
    """V2: <text xml:space="preserve"> → literal 4-space indent survives in output."""
    # Arrange
    raw = "    int x = 0;\n  return 0;"
    elem = _make_text_elem(raw, preserve=True)
    ctx = ConvertContext()

    # Act
    result = convert_text(elem, ctx)

    # Assert
    assert result is not None, "convert_text returned None for a valid <text> element"
    runs = _at_runs(result.xml)
    assert runs, f"no <a:t> runs found in output:\n{result.xml}"

    assert any('xml:space="preserve">    int x = 0;' in run for run in runs), (
        f"expected run with xml:space=\"preserve\" and 4-space indent; got:\n"
        + "\n".join(runs)
    )


# ---------------------------------------------------------------------------
# Test 3: tspan inherits parent xml:space="preserve"
# ---------------------------------------------------------------------------


def test_tspan_inherits_parent_preserve() -> None:
    """<text xml:space="preserve"><tspan> → tspan run keeps leading spaces."""
    # Arrange
    elem = ET.Element("text")
    elem.set("x", "10")
    elem.set("y", "20")
    elem.set("font-family", "Consolas, monospace")
    elem.set("font-size", "14")
    elem.set(XML_SPACE_NS, "preserve")

    tspan = ET.SubElement(elem, "tspan")
    tspan.text = "    inner"

    ctx = ConvertContext()

    # Act
    result = convert_text(elem, ctx)

    # Assert
    assert result is not None, "convert_text returned None for a valid <text> element"
    runs = _at_runs(result.xml)
    assert runs, f"no <a:t> runs found in output:\n{result.xml}"

    assert any("    inner" in run for run in runs), (
        "tspan leading spaces were collapsed even though parent has xml:space=\"preserve\";\n"
        + "\n".join(runs)
    )
