#!/usr/bin/env python3
"""
sync_skill_root.py — Keep root SKILL.md in sync with skills/ppt-master/SKILL.md

Gemini CLI installs skills from the repo root (SKILL.md).
Claude plugin uses skills/ppt-master/SKILL.md.
This script ensures both are identical.

Usage:
    python scripts/sync_skill_root.py           # check only
    python scripts/sync_skill_root.py --apply   # copy canonical → root
    python scripts/sync_skill_root.py --reverse # copy root → canonical
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
CANONICAL = ROOT / "skills" / "ppt-master" / "SKILL.md"
ROOT_SKILL = ROOT / "SKILL.md"


def main():
    parser = argparse.ArgumentParser(description="Sync SKILL.md between root and skills/ppt-master/")
    parser.add_argument("--apply", action="store_true", help="Copy canonical → root")
    parser.add_argument("--reverse", action="store_true", help="Copy root → canonical")
    args = parser.parse_args()

    if args.apply and args.reverse:
        print("❌ Cannot use --apply and --reverse together")
        sys.exit(1)

    canonical_text = CANONICAL.read_text(encoding="utf-8")
    root_text = ROOT_SKILL.read_text(encoding="utf-8") if ROOT_SKILL.exists() else None

    if root_text is None:
        print("⚠️  Root SKILL.md does not exist yet")
        if args.apply:
            ROOT_SKILL.write_text(canonical_text, encoding="utf-8")
            print(f"✅ Created {ROOT_SKILL} from canonical")
        else:
            print("   Run with --apply to create it")
            sys.exit(1)
        return

    if canonical_text == root_text:
        print("✅ Both SKILL.md files are identical — no sync needed")
        return

    print("⚠️  SKILL.md files differ:")
    print(f"   Canonical: {CANONICAL} ({len(canonical_text)} chars)")
    print(f"   Root:      {ROOT_SKILL} ({len(root_text)} chars)")

    if args.apply:
        ROOT_SKILL.write_text(canonical_text, encoding="utf-8")
        print(f"✅ Synced canonical → root SKILL.md")
    elif args.reverse:
        CANONICAL.write_text(root_text, encoding="utf-8")
        print(f"✅ Synced root → canonical SKILL.md")
    else:
        print("   Run with --apply to copy canonical → root, or --reverse to copy root → canonical")
        sys.exit(1)


if __name__ == "__main__":
    main()
