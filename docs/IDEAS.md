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

## 测试

- [ ] 添加 YAML 有效性测试：`yaml.safe_load(_GEMINI_YAML)` 验证 `_GEMINI_YAML` 常量本身是合法 YAML
- [ ] 添加 `Path(__file__).resolve()` 路径处理的测试（symlink 场景）

---
