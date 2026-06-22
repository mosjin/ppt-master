# CHANGELOG — ppt-master (mosjin fork)

## [2.9.0] — 2026-06-22

### 🚀 Release: v2.9.0（客户发布版）

统一全部版本串到 `2.9.0`（fork 自己版本线，上版 2.8.0）：
- `SKILL.md`（root）、`skills/ppt-master/SKILL.md`（canonical）、`.gemini/skills/ppt-master/SKILL.md`
- `scripts/sync_skill_root.py` 内嵌 frontmatter 模板常量（root/.gemini 版本真源，原硬编码 2.6.0）
- `README.md` / `README_CN.md` badge（v2.11.0 → v2.9.0，链接改指 mosjin/ppt-master releases）
- `.claude-plugin/marketplace.json` version + description

打包内容：
- upstream hugohe3 v2.11 内容同步（pptx_intake / 演示模式 / visual-styles / LaTeX / brand 预设）
- #11 单面板版面守卫（`svg_quality_checker._check_single_panel_layout`）

发布：commit `ff7ab1f8`，tag `v2.9.0`（origin），author/committer = mosjin。

## [sync] — 2026-06-22

### 🔄 Sync: 合并 upstream v2.8–v2.11（131 commits）

**Merge commit**: `9b190904`

**关键新功能（来自 upstream hugohe3/ppt-master）：**
- `extract_svg_assets.py` — SVG 资源提取工具
- `pptx_intake.py` — 多 PPTX 导入 + 素材发散确认
- `image_search.py` — 并发 `--batch` 模式
- `references/modes/` — 新增 5 种演示模式（briefing/narrative/pyramid/showcase/instructional）
- `references/visual-styles/` — 新增 15 种视觉风格目录
- `references/executor-*.md` 迁移至 `modes/`
- `svg_to_pptx`: `<a>` 标签透明组渲染、文本语言逐 run 检测、text_height 收紧（1.5x→1.2x）
- `source_to_md`: 各 converter 统一输出 `image_manifest.json`

**本地 commit 全部保留**（windows-docs 修复 + svg hyperlink features）

---

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
