# IDEAS — ppt-master (mosjin fork)

待实现的改进和想法。

---

## Gemini CLI 集成

- [ ] 添加 `.gitattributes`（`*.md text eol=lf`、`*.py text eol=lf`）— 防止 Windows autocrlf 导致的 CRLF 问题从根源上复发，code-review 已建议
- [ ] 端到端功能验证：在 Gemini CLI 中实际触发 `/ppt-master`，用一个真实 PDF 走完完整 pipeline，确认路径解析无误
- [ ] CI: 在 GitHub Actions 中加 `python scripts/sync_skill_root.py`（check-only）的 lint step，防止 canonical 更新后忘记同步

## upstream sync (#2)

- [ ] 建立定期 upstream sync 流程（issue #2）：每次 upstream 有新 release 时 merge，保持 fork 同步
- [ ] 考虑用 GitHub Actions 定时检查 upstream 新 tag 并自动开 PR

## SVG 质量自校正循环 (issue #133) ✅ 已实现

**已完成 (2026-05-07)**：
- ✅ `SKILL.md` Step 6 Quality Check Gate 新增 max-3 重试表 + `⛔ STOP` 升级协议
- ✅ `scripts/svg_quality_checker.py` 新增三项检测（checks 9–11）：
  - `_check_placeholder_phrases` — 检测占位支架 SVG（issue #125）
  - `_check_wcag_contrast` — WCAG AA 4.5:1 对比度（issue #133）
  - `_check_font_size_tiny` — font-size < 10px（issue #133）
- ✅ `eduForge_skill` Phase 5 新增 Gate-Outcome Contract（ppt-master 重试耗尽后的 BLOCKING 处理）

**待优化**：
- [ ] lxml 版 AABB 碰撞检测（axis-aligned bounding box 文字重叠）— 需要元素树遍历，regex 不可行
- [ ] cairosvg 渲染后截图 + VLM 视觉打分（依赖本地模型，暂缓）
- [ ] `check_directory` 输出格式改为机器可读 JSON（`--json` flag），方便 CI 消费

## 测试

- [ ] 添加 YAML 有效性测试：`yaml.safe_load(_GEMINI_YAML)` 验证 `_GEMINI_YAML` 常量本身是合法 YAML
- [ ] 添加 `Path(__file__).resolve()` 路径处理的测试（symlink 场景）

---
