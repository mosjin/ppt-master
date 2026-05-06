# CHANGELOG — ppt-master (mosjin fork)

## [dev] — 2026-05-06

### 🚀 Feature: Gemini CLI workspace skill + sync_skill_root 全面重构

**Commit**: `9528f661`

**新增文件：**
- `.gemini/skills/ppt-master/SKILL.md` — Gemini workspace skill（Gemini CLI 官方格式，含 YAML frontmatter + 完整 workflow）
- `tests/test_sync_skill_root.py` — 21 个单元测试（21/21 通过）

**修改文件：**
- `SKILL.md` (root) — 恢复完整 workflow 内容；加 Gemini YAML frontmatter（之前 v1 实现错误地改为 stub）
- `scripts/sync_skill_root.py` — 全面重写：

### 🐛 Fix: CRITICAL CRLF bug in _strip_yaml_frontmatter

Windows `core.autocrlf=true` 导致 `str.find("\n---\n")` 失败，生成文件含双 frontmatter 块。改用 `re.search(r"\n---\n")` + 行尾归一化。

### 🐛 Fix: 路径替换锚定

`str.replace` → `re.sub` + negative lookahead，防止 `${SKILL_DIR}/skills/ppt-master/` 被双重替换。

### 🐛 Fix: 原子写不一致

missing 分支直接 `write_text`（非原子），update 分支用 tmp+replace（原子）。统一为 `_atomic_write()`。

### 🐛 Fix: 行尾比较不稳定

读写均通过 `_normalize()` 归一化后比较，消除 CRLF/LF 差异导致的永久 out-of-sync。

**架构**：
```
sync_skill_root.py --apply 生成两个目标（内容相同）：
  root SKILL.md                      ← gemini skills install 用户安装入口
  .gemini/skills/ppt-master/SKILL.md ← workspace skill（clone repo 后自动发现）
```

**验证**：
- `gemini skills install git@github.com:mosjin/ppt-master.git --consent --scope user` ✅
- `gemini skills list` 显示正确 description ✅
- `~/.gemini/skills/ppt-master/` 含完整 repo，脚本路径解析正确 ✅
- workspace skill conflict 警告为预期行为（workspace > user 优先级）✅

---

## 历史

### v2.6.0-fork — 2026-05-06 (before this session)

- `feat(#3)`: 根目录 SKILL.md Gemini CLI skill 安装兼容（初版，后发现 CRLF bug 已在本次修复）
- `merge(upstream v2.6.0)`: sync 30+ upstream commits

---
