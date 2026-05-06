#!/usr/bin/env python3
"""
sync_skill_root.py — Generate Gemini-adapted SKILL.md files from skills/ppt-master/SKILL.md

Both targets are auto-generated and have identical content:
  root SKILL.md                       — Gemini user install entry (gemini skills install)
  .gemini/skills/ppt-master/SKILL.md  — Gemini workspace skill (for contributors cloning the repo)

Architecture (following eduForge multi-platform pattern):
  Claude plugin   → skills/ppt-master/SKILL.md           (canonical, ${SKILL_DIR}/scripts/...)
  Gemini install  → SKILL.md (root)                      (auto-generated, full workflow)
  Gemini workspace→ .gemini/skills/ppt-master/SKILL.md   (same content as root)

Path adaptation applied to body:
  ${SKILL_DIR}/  →  ${SKILL_DIR}/skills/ppt-master/
  Rationale: gemini skills install clones full repo to ~/.gemini/skills/ppt-master/ (= SKILL_DIR),
  so scripts live at ${SKILL_DIR}/skills/ppt-master/scripts/ not ${SKILL_DIR}/scripts/.

Usage:
    python scripts/sync_skill_root.py           # check: verify both Gemini files are up-to-date
    python scripts/sync_skill_root.py --apply   # generate/update both from canonical
    python scripts/sync_skill_root.py --reverse # NOT supported (Gemini files are derived)
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANONICAL = ROOT / "skills" / "ppt-master" / "SKILL.md"
ROOT_SKILL = ROOT / "SKILL.md"
GEMINI_SKILL = ROOT / ".gemini" / "skills" / "ppt-master" / "SKILL.md"

TARGETS = [ROOT_SKILL, GEMINI_SKILL]

_GEMINI_YAML = """\
---
name: ppt-master
description: >
  AI-driven multi-format SVG content generation system. Converts source documents
  (PDF/DOCX/URL/Markdown) into high-quality SVG pages and exports to PPTX through
  multi-role collaboration. Use when user asks to "create PPT", "make presentation",
  "生成PPT", "做PPT", "制作演示文稿", or mentions "ppt-master".
license: MIT
compatibility: >
  Python 3.8+ and Git required.
  Install: gemini skills install https://github.com/mosjin/ppt-master.git --consent --scope user
  Then: pip install -r "$(gemini skills path mosjin/ppt-master)/requirements.txt"
metadata:
  author: mosjin
  version: "2.6.0"
  upstream: hugohe3/ppt-master
  integration: Gemini CLI (root SKILL.md + .gemini/skills/ppt-master/SKILL.md)
  note: AUTO-GENERATED — edit skills/ppt-master/SKILL.md, run sync_skill_root.py --apply
allowed-tools: Bash Read Write Edit
---

"""


def _normalize(text: str) -> str:
    return text.replace("\r\n", "\n")


def _strip_yaml_frontmatter(text: str) -> str:
    """Strip leading YAML frontmatter (--- ... ---) tolerating both LF and CRLF."""
    text = _normalize(text)
    if not text.startswith("---"):
        return text
    m = re.search(r"\n---\n", text[3:])
    if not m:
        return text
    return text[3 + m.end():]


def _expected_gemini_text(canonical_text: str) -> str:
    body = _strip_yaml_frontmatter(canonical_text)
    # Anchored replacement: only replace ${SKILL_DIR}/ not already followed by skills/ppt-master/
    adapted = re.sub(
        r"\$\{SKILL_DIR\}/(?!skills/ppt-master/)",
        "${SKILL_DIR}/skills/ppt-master/",
        body,
    )
    return _GEMINI_YAML + adapted


def _atomic_write(path: Path, text: str) -> None:
    """Write text to path atomically via a sibling .tmp file (LF, UTF-8)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    try:
        tmp.write_text(text, encoding="utf-8", newline="\n")
        tmp.replace(path)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise


def _read_normalized(path: Path) -> str | None:
    if not path.exists():
        return None
    return _normalize(path.read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser(
        description="Sync Gemini SKILL.md files from skills/ppt-master/SKILL.md (canonical)"
    )
    parser.add_argument("--apply", action="store_true", help="Generate/update Gemini SKILL.md files from canonical")
    parser.add_argument(
        "--reverse",
        action="store_true",
        help="Not supported — Gemini SKILL.md files are derived from canonical",
    )
    args = parser.parse_args()

    if args.reverse:
        print("[ERROR] --reverse not supported: Gemini SKILL.md files are auto-generated.")
        print("  Edit skills/ppt-master/SKILL.md directly, then run --apply.")
        sys.exit(1)

    canonical_text = CANONICAL.read_text(encoding="utf-8")
    expected = _expected_gemini_text(canonical_text)

    any_issue = False
    for target in TARGETS:
        label = str(target.relative_to(ROOT))
        current = _read_normalized(target)

        if current == expected:
            print(f"[OK] {label} is up-to-date")
            continue

        any_issue = True
        if current is None:
            print(f"[WARN] {label} does not exist yet")
        else:
            print(f"[WARN] {label} is out of sync with canonical")

        if args.apply:
            _atomic_write(target, expected)
            print(f"[OK] {label} updated")
        else:
            print(f"  Run with --apply to fix")

    if any_issue and not args.apply:
        sys.exit(1)


if __name__ == "__main__":
    main()
