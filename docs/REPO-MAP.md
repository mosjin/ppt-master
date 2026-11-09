# REPO-MAP — ppt-master 的位置与依赖（简版）

全景总图在 **Easel** 的 `docs/REPO-MAP.md`：https://github.com/mosjin/Easel/blob/main/docs/REPO-MAP.md

## 本仓是谁

**ppt-master** — https://github.com/mosjin/ppt-master

AI 生成原生可编辑 PPTX 的工具 fork（真实 PowerPoint 形状、非图片）。

- 上游：**hugohe3/ppt-master** — https://github.com/hugohe3/ppt-master
- 同步机制：cron 每周三、周日约 09:00 查上游新版 tag → 备份 → cherry-pick → 审计本地定制 .py 文件 → 仅干净时推送（`sync-upstream-v*` 分支线）；推送 PAT 只存本地 `~/.ppt-master-push-pat`（0600），不进 git config、**不入库**。
- 本地克隆：VM `~/workspace/repos/mosjin-ppt-master`。

## 关系

- 与 mosjin 其他工作仓**无代码依赖**：只向上游 hugohe3/ppt-master 同步，独立使用。

## 全景一句话

ppt-master 是独立的 PPTX 生成工具 fork：与仓群无代码往来，唯一的纪律是每周两次跟上游对表、保住本地定制。
