"""
Tests for scripts/sync_skill_root.py

Covers:
  - _strip_yaml_frontmatter: LF, CRLF, no-frontmatter, incomplete
  - _expected_gemini_text: YAML frontmatter, path adaptation, no-bare, no-doubled, allowed-tools
  - CLI check-only: up-to-date (exit 0), missing (exit 1), out-of-sync (exit 1)
  - CLI --apply: creates missing, fixes out-of-sync, idempotent, reverse rejected
  - Both targets (root SKILL.md + .gemini/skills/ppt-master/SKILL.md) checked
"""
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "sync_skill_root.py"
CANONICAL = REPO / "skills" / "ppt-master" / "SKILL.md"
ROOT_SKILL = REPO / "SKILL.md"
GEMINI_SKILL = REPO / ".gemini" / "skills" / "ppt-master" / "SKILL.md"
TARGETS = [ROOT_SKILL, GEMINI_SKILL]

sys.path.insert(0, str(REPO / "scripts"))
from sync_skill_root import (  # noqa: E402
    _expected_gemini_text,
    _strip_yaml_frontmatter,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        cwd=str(REPO),
    )


def _backup(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _restore(path: Path, content: str) -> None:
    if content:
        path.write_text(content, encoding="utf-8")
    elif path.exists():
        path.unlink()


# ---------------------------------------------------------------------------
# Pure function tests
# ---------------------------------------------------------------------------


class TestStripYamlFrontmatter:
    def test_strips_lf(self):
        assert _strip_yaml_frontmatter("---\nname: foo\n---\nbody") == "body"

    def test_strips_crlf(self):
        text = "---\r\nname: foo\r\n---\r\nbody\r\n"
        result = _strip_yaml_frontmatter(text)
        assert result == "body\n"  # normalized after strip

    def test_no_frontmatter_unchanged(self):
        text = "# Hello\nworld"
        assert _strip_yaml_frontmatter(text) == text

    def test_incomplete_frontmatter_unchanged(self):
        text = "---\nname: foo\nbody without closing fence"
        assert _strip_yaml_frontmatter(text) == text

    def test_real_canonical_strips_cleanly(self):
        """Canonical SKILL.md (may be CRLF on Windows) must strip without error."""
        text = CANONICAL.read_text(encoding="utf-8")
        result = _strip_yaml_frontmatter(text)
        assert not result.lstrip().startswith("---"), "Frontmatter not stripped"
        assert "PPT Master Skill" in result


class TestExpectedGeminiText:
    def test_starts_with_valid_yaml(self):
        result = _expected_gemini_text(CANONICAL.read_text(encoding="utf-8"))
        assert result.startswith("---\nname: ppt-master\n")

    def test_path_adaptation_applied(self):
        canonical = "---\nname: x\n---\npath ${SKILL_DIR}/scripts/foo.py end"
        result = _expected_gemini_text(canonical)
        assert "${SKILL_DIR}/skills/ppt-master/scripts/foo.py" in result
        assert "${SKILL_DIR}/scripts/foo.py" not in result

    def test_no_bare_skill_dir_in_real_canonical(self):
        """No ${SKILL_DIR}/ without skills/ppt-master/ prefix in generated output."""
        import re
        result = _expected_gemini_text(CANONICAL.read_text(encoding="utf-8"))
        bare = re.findall(r"\$\{SKILL_DIR\}/(?!skills/ppt-master/)", result)
        assert bare == [], f"Bare SKILL_DIR refs remain: {bare}"

    def test_no_doubled_prefix(self):
        """Replacement must not double-apply if canonical somehow has the adapted path."""
        canonical = "---\nname: x\n---\n${SKILL_DIR}/skills/ppt-master/scripts/foo.py"
        result = _expected_gemini_text(canonical)
        assert "skills/ppt-master/skills/ppt-master/" not in result

    def test_no_double_frontmatter_block(self):
        """Generated file must contain exactly one YAML frontmatter block."""
        result = _expected_gemini_text(CANONICAL.read_text(encoding="utf-8"))
        # After stripping the generated YAML block, body must not start with ---
        parts = result.split("---\n", 2)
        assert len(parts) >= 3, "Could not find closing --- of frontmatter"
        body = parts[2]
        assert not body.lstrip().startswith("---"), (
            "Generated file has a second frontmatter block — CRLF strip bug?"
        )

    def test_allowed_tools_present(self):
        result = _expected_gemini_text(CANONICAL.read_text(encoding="utf-8"))
        assert "allowed-tools: Bash Read Write Edit" in result

    def test_auto_generated_note_present(self):
        result = _expected_gemini_text(CANONICAL.read_text(encoding="utf-8"))
        assert "AUTO-GENERATED" in result

    def test_full_workflow_content_preserved(self):
        """Workflow steps must survive in the generated file."""
        result = _expected_gemini_text(CANONICAL.read_text(encoding="utf-8"))
        assert "Step 1" in result and "Step 7" in result
        assert "Strategist" in result
        assert "Executor" in result


# ---------------------------------------------------------------------------
# CLI integration tests — check-only
# ---------------------------------------------------------------------------


class TestCheckOnly:
    def test_up_to_date_exits_0(self):
        """Both targets current → check exits 0."""
        result = _run()
        assert result.returncode == 0, result.stdout + result.stderr
        assert result.stdout.count("[OK]") == 2

    def test_missing_target_exits_nonzero(self):
        """One target absent → check exits 1."""
        bak = _backup(GEMINI_SKILL)
        GEMINI_SKILL.unlink()
        try:
            result = _run()
            assert result.returncode != 0
            assert "does not exist" in result.stdout
        finally:
            _restore(GEMINI_SKILL, bak)

    def test_out_of_sync_exits_nonzero(self):
        """Tampered target → check exits 1."""
        bak = _backup(ROOT_SKILL)
        ROOT_SKILL.write_text(bak + "\n# tampered\n", encoding="utf-8")
        try:
            result = _run()
            assert result.returncode != 0
            assert "out of sync" in result.stdout
        finally:
            _restore(ROOT_SKILL, bak)


# ---------------------------------------------------------------------------
# CLI integration tests — --apply
# ---------------------------------------------------------------------------


class TestApply:
    def test_apply_creates_missing(self):
        """--apply must create absent target with correct content."""
        bak = _backup(GEMINI_SKILL)
        GEMINI_SKILL.unlink()
        try:
            result = _run("--apply")
            assert result.returncode == 0, result.stderr
            assert GEMINI_SKILL.exists()
            content = GEMINI_SKILL.read_text(encoding="utf-8")
            assert content.startswith("---\nname: ppt-master\n")
            assert "Step 7" in content
        finally:
            _restore(GEMINI_SKILL, bak)

    def test_apply_fixes_out_of_sync(self):
        """--apply must restore a tampered target."""
        bak = _backup(ROOT_SKILL)
        ROOT_SKILL.write_text(bak + "\n# tampered\n", encoding="utf-8")
        try:
            result = _run("--apply")
            assert result.returncode == 0, result.stderr
            restored = ROOT_SKILL.read_text(encoding="utf-8").replace("\r\n", "\n")
            expected = bak.replace("\r\n", "\n")
            assert restored == expected
        finally:
            _restore(ROOT_SKILL, bak)

    def test_apply_idempotent(self):
        """--apply on current targets must exit 0 and not change files."""
        bak_root = _backup(ROOT_SKILL)
        bak_gemini = _backup(GEMINI_SKILL)
        result = _run("--apply")
        assert result.returncode == 0
        assert ROOT_SKILL.read_text(encoding="utf-8") == bak_root
        assert GEMINI_SKILL.read_text(encoding="utf-8") == bak_gemini

    def test_both_targets_updated(self):
        """--apply must update both root and .gemini skill files."""
        bak_root = _backup(ROOT_SKILL)
        bak_gemini = _backup(GEMINI_SKILL)
        ROOT_SKILL.write_text(bak_root + "\n# tamper\n", encoding="utf-8")
        GEMINI_SKILL.write_text(bak_gemini + "\n# tamper\n", encoding="utf-8")
        try:
            result = _run("--apply")
            assert result.returncode == 0
            assert result.stdout.count("[OK]") == 2
        finally:
            _restore(ROOT_SKILL, bak_root)
            _restore(GEMINI_SKILL, bak_gemini)

    def test_reverse_flag_exits_nonzero(self):
        """--reverse must exit non-zero with a clear error."""
        result = _run("--reverse")
        assert result.returncode != 0
        assert "not supported" in result.stdout.lower()
