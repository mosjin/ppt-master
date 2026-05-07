# TECH_LOG — ppt-master (mosjin fork)

工程经验日志，最新在最上方。

---

## 2026-05-07: SVG Quality Check Gate — max-3 self-correcting loop (Issue #133)

### 1. Problem

Step 6 Quality Check Gate language was vague: "return to Visual Construction, regenerate that page, re-run check" with no retry limit or stop condition. AI agents interpreted this as: retry silently forever, or quietly skip failing pages.

### 2. Root Cause

- No explicit max-attempts bound → unbounded loop risk
- No `⛔ STOP` escalation protocol → AI would never block and ask the user
- Three quality checks missing: placeholder scaffold SVG (issue #125), WCAG AA 4.5:1 contrast (issue #133), font-size < 10 px (issue #133)

### 3. Fix

**SKILL.md Step 6** — Quality Check Gate now has an explicit retry table:

| Attempt | Action |
|---------|--------|
| 1 | Run checker. 0 errors → proceed |
| 2 | Regenerate only failing pages in-context (no sub-agents). Re-run checker |
| 3 | Same as attempt 2. Re-run checker |
| Exhausted | ⛔ STOP. Report failing filenames + full error text. Wait for user authorisation |

**`scripts/svg_quality_checker.py`** — Three new methods added to `SVGQualityChecker`:
- Check 9 `_check_placeholder_phrases` — detects "详见课堂版" scaffold SVG
- Check 10 `_check_wcag_contrast` — WCAG AA 4.5:1; excludes `_CODE_BG_COLORS` to avoid false positives on code blocks
- Check 11 `_check_font_size_tiny` — font-size < 10 px is unreadable on projection

### 4. Lessons

- **Rule**: Every AI-facing quality gate MUST have a numeric max-retry bound and an explicit `⛔ STOP` + escalation path.
- **Why**: Without a stop condition the AI retries silently (burning context) or skips failures silently (shipping bad slides).

- **Rule**: Code-block backgrounds (`#1e1e1e`, `#2d2d2d`, etc.) must be excluded from the WCAG contrast candidate set — they use intentional dark-on-dark syntax highlighting.
- **Why**: Including them as background candidates produces false positives on every slide that has a code panel.

---

## 2026-05-06: Gemini CLI skill 架构重构 + CRLF 致命 bug 修复

### 1. Problem

`sync_skill_root.py --apply` 在 Windows 上生成的根目录 `SKILL.md` 包含**两个 YAML frontmatter 块**，导致 Gemini CLI 解析结果不确定。同时原始实现把根目录 SKILL.md 改成了一个 stub（只有几行），导致 `gemini skills install` 安装后技能完全失效（无 workflow 内容）。

### 2. Root Cause

**CRLF 盲区**：`_strip_yaml_frontmatter` 用 `text.find("\n---\n")` 查找 frontmatter 结束标记，但 Windows 上 `core.autocrlf=true` 使 canonical `SKILL.md` 以 CRLF 存储，结束标记实际是 `\r\n---\r\n`，`find` 返回 -1，函数静默返回原文，导致新 YAML header 被追加到**已含 frontmatter 的原文**前，输出文件有两个 `---` 块。

**Stub 架构误判**：误以为 `.gemini/skills/ppt-master/SKILL.md` 可以替代 root SKILL.md 的功能。实际上 `gemini skills install` 激活时把 SKILL.md **body 整体注入 conversation**——stub 里只有一句 "see other file"，AI 不会自动 follow 这个引用。

**路径替换未锚定**：`str.replace("${SKILL_DIR}/", "${SKILL_DIR}/skills/ppt-master/")` 对已含 `skills/ppt-master/` 的路径会双重替换为 `skills/ppt-master/skills/ppt-master/`。

### 3. Fix / Approach

```python
# CRLF fix: 用 re.search 替代 str.find
def _strip_yaml_frontmatter(text: str) -> str:
    text = text.replace("\r\n", "\n")  # normalize first
    if not text.startswith("---"):
        return text
    m = re.search(r"\n---\n", text[3:])
    if not m:
        return text
    return text[3 + m.end():]

# 锚定替换: negative lookahead 防止双重替换
adapted = re.sub(
    r"\$\{SKILL_DIR\}/(?!skills/ppt-master/)",
    "${SKILL_DIR}/skills/ppt-master/",
    body,
)

# 原子写: 统一用 tmp+replace，读写均 normalize 行尾后比较
def _atomic_write(path: Path, text: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    try:
        tmp.write_text(text, encoding="utf-8", newline="\n")
        tmp.replace(path)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise
```

**架构修正**：`sync_skill_root.py --apply` 同时生成两个目标文件（root SKILL.md + `.gemini/skills/ppt-master/SKILL.md`），两者内容相同，均含完整 workflow。

### 4. Lessons

- **Rule**: 在 Windows 上处理文本文件比较前，始终先 `.replace("\r\n", "\n")` 归一化行尾；`str.find` 对行尾不可靠，用 `re.search` + `\r?\n`。
- **Why**: `core.autocrlf=true` 是 Windows Git 默认值，任何 `\n` 搜索都可能因 CRLF 而失败。

- **Rule**: `gemini skills install` 激活技能时把 SKILL.md body **完整注入 context**，root SKILL.md 必须包含完整 workflow 内容，不能是 stub 或重定向。
- **Why**: Gemini CLI 不会自动 follow "see other file" 类型的引用。

- **Rule**: 字符串路径替换要用 `re.sub` + negative lookahead 做幂等保护。
- **Why**: `str.replace` 无法避免对已经包含目标前缀的路径重复替换。

- **Rule**: Gemini CLI workspace skill（`.gemini/skills/<name>/`）优先级高于 user skill（`~/.gemini/skills/<name>/`）。在 repo 目录内运行时两者都会被发现并产生 conflict 警告，这是正常的预期行为。

---
