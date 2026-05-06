#!/usr/bin/env python3
"""
sync_skill_root.py — Generate root SKILL.md (Gemini) from skills/ppt-master/SKILL.md (Claude)

Context:
  Claude plugin uses skills/ppt-master/SKILL.md, where SKILL_DIR = ~/.claude/skills/ppt-master/
    → all script paths are ${SKILL_DIR}/scripts/...

  Gemini CLI installs the full repo to ~/.gemini/skills/ppt-master/, where SKILL_DIR = repo root
    → scripts actually live at ${SKILL_DIR}/skills/ppt-master/scripts/...

The root SKILL.md is NOT a simple copy — it needs path adaptation:
  ${SKILL_DIR}/  →  ${SKILL_DIR}/skills/ppt-master/

Usage:
    python scripts/sync_skill_root.py           # check: verify root is up-to-date
    python scripts/sync_skill_root.py --apply   # generate/update root SKILL.md from canonical
    python scripts/sync_skill_root.py --reverse # NOT supported (root is derived, not source)
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
CANONICAL = ROOT / "skills" / "ppt-master" / "SKILL.md"
ROOT_SKILL = ROOT / "SKILL.md"

# Banner inserted at top of root SKILL.md so it's clear it's auto-generated
_BANNER = """\
<!-- AUTO-GENERATED for Gemini CLI installation — do NOT edit directly.
     Edit skills/ppt-master/SKILL.md and run: python scripts/sync_skill_root.py --apply
     Path adaptation: ${SKILL_DIR}/ → ${SKILL_DIR}/skills/ppt-master/ -->
"""


def _adapt_for_gemini(text: str) -> str:
    """Replace ${SKILL_DIR}/ with ${SKILL_DIR}/skills/ppt-master/ for Gemini install layout."""
    adapted = text.replace("${SKILL_DIR}/", "${SKILL_DIR}/skills/ppt-master/")
    return _BANNER + adapted


def _expected_root_text(canonical_text: str) -> str:
    return _adapt_for_gemini(canonical_text)


def main():
    parser = argparse.ArgumentParser(
        description="Sync root SKILL.md (Gemini) from skills/ppt-master/SKILL.md (Claude)"
    )
    parser.add_argument("--apply", action="store_true", help="Generate/update root SKILL.md from canonical")
    parser.add_argument(
        "--reverse",
        action="store_true",
        help="Not supported — root is derived from canonical, not the other way",
    )
    args = parser.parse_args()

    if args.reverse:
        print("❌ --reverse is not supported: root SKILL.md is auto-generated from the canonical.")
        print("   Edit skills/ppt-master/SKILL.md directly, then run --apply.")
        sys.exit(1)

    canonical_text = CANONICAL.read_text(encoding="utf-8")
    expected = _expected_root_text(canonical_text)
    root_text = ROOT_SKILL.read_text(encoding="utf-8") if ROOT_SKILL.exists() else None

    if root_text is None:
        print("⚠️  Root SKILL.md does not exist yet")
        if args.apply:
            ROOT_SKILL.write_text(expected, encoding="utf-8")
            print(f"✅ Created {ROOT_SKILL} (Gemini path-adapted)")
        else:
            print("   Run with --apply to create it")
            sys.exit(1)
        return

    if root_text == expected:
        print("✅ Root SKILL.md is up-to-date (Gemini path-adapted)")
        return

    print("⚠️  Root SKILL.md is out of sync with canonical:")
    print(f"   Canonical: {CANONICAL} ({len(canonical_text)} chars)")
    print(f"   Root:      {ROOT_SKILL} ({len(root_text)} chars, expected {len(expected)})")

    if args.apply:
        tmp = ROOT_SKILL.with_suffix(".md.tmp")
        tmp.write_text(expected, encoding="utf-8")
        tmp.replace(ROOT_SKILL)
        print("✅ Root SKILL.md updated (Gemini path-adapted)")
    else:
        print("   Run with --apply to update")
        sys.exit(1)


if __name__ == "__main__":
    main()
