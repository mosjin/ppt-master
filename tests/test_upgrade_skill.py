"""
test_upgrade_skill.py — TDD guard for /ppt-master:upgrade sub-skill (issue #23).

Mirrors /context-mode:ctx-upgrade semantics. Validates SKILL.md
structure, trigger declaration, and canonical upgrade workflow.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_PATH = REPO_ROOT / "skills" / "upgrade" / "SKILL.md"


class TestUpgradeSubSkill(unittest.TestCase):
    """Issue mosjin/eduForge_skill#23: /ppt-master:upgrade must mirror /context-mode:ctx-upgrade semantics."""

    def setUp(self) -> None:
        self.assertTrue(SKILL_PATH.exists(), f"missing: {SKILL_PATH}")
        self.content = SKILL_PATH.read_text(encoding="utf-8")

    def test_has_yaml_frontmatter(self) -> None:
        self.assertTrue(self.content.startswith("---\n"))
        self.assertIn("\n---\n", self.content)

    def test_frontmatter_name_is_upgrade(self) -> None:
        self.assertIsNotNone(
            re.search(r"^name:\s*upgrade\s*$", self.content, re.MULTILINE)
        )

    def test_declares_trigger(self) -> None:
        self.assertIn("/ppt-master:upgrade", self.content)

    def test_user_invocable_flag(self) -> None:
        self.assertIsNotNone(
            re.search(r"^user-invocable:\s*true\s*$", self.content, re.MULTILINE)
        )

    def test_includes_git_pull_step(self) -> None:
        self.assertRegex(self.content, r"git\s+(-C\s+\S+\s+)?pull")

    def test_includes_version_verify_step(self) -> None:
        self.assertRegex(
            self.content,
            r"marketplace\.json|plugin\.json|SKILL\.md.+version|version.+SKILL\.md|parse_hex_color",
        )

    def test_includes_reload_hint(self) -> None:
        self.assertRegex(self.content, r"reload|restart|/reload-plugin")

    def test_includes_pip_install_step(self) -> None:
        # ppt-master has python deps — must remind user
        self.assertRegex(self.content, r"pip\s+install|requirements\.txt")


if __name__ == "__main__":
    unittest.main(verbosity=2)
