---
name: upgrade
description: |
  Upgrade ppt-master to the latest commit on `main`. Runs `git pull` in the
  plugin install dir, re-installs `requirements.txt`, verifies that
  parse_hex_color resolves CSS named colors (regression guard for the
  eduForge #19 black-PPT bug), and reminds the user to reload the plugin.
  Trigger: /ppt-master:upgrade
user-invocable: true
---

# ppt-master Upgrade

Pull the latest ppt-master release, refresh Python deps, and prove the
regression guard holds.

Mirrors the [`/context-mode:ctx-upgrade`](https://github.com/mksglu/context-mode) pattern: one slash command per skill, deterministic shell sequence, idempotent.

## Instructions

1. **Find the plugin install path.** Priority order — pick the first existing path:
   - `$PPT_MASTER_HOME` (environment override)
   - `~/.claude/plugins/ppt-master/` (Claude Code default)
   - `D:/works/ppt-master/` (local dev fallback on Windows / `~/works/ppt-master/` on POSIX)

   If none exists, point the user at the [Install section of the README](https://github.com/mosjin/ppt-master#3-set-up) and stop.

2. **Capture the current version** (so the diff is meaningful):
   ```bash
   OLD=$(grep -oP '"version":\s*"\K[^"]+' <PLUGIN_PATH>/.claude-plugin/marketplace.json)
   OLD_SHA=$(git -C <PLUGIN_PATH> rev-parse --short HEAD)
   ```

3. **Fetch + fast-forward `main`:**
   ```bash
   git -C <PLUGIN_PATH> fetch origin main
   git -C <PLUGIN_PATH> pull --ff-only origin main
   ```
   If `pull` fails (local edits, diverged branch) → abort and report; never force. Tell the user to commit/stash their local changes and re-run `/ppt-master:upgrade`.

4. **Capture the new version** and cross-check three sources stay in sync:
   ```bash
   NEW=$(grep -oP '"version":\s*"\K[^"]+' <PLUGIN_PATH>/.claude-plugin/marketplace.json)
   NEW_SHA=$(git -C <PLUGIN_PATH> rev-parse --short HEAD)
   ```
   Both of these should report `NEW`:
   - `<PLUGIN_PATH>/skills/ppt-master/SKILL.md` → frontmatter `version:`
   - `<PLUGIN_PATH>/.claude-plugin/marketplace.json` → `plugins[0].version`

5. **Refresh Python dependencies** (ppt-master ships scripts that need `requirements.txt`):
   ```bash
   pip install -r <PLUGIN_PATH>/requirements.txt
   ```
   If `pip install` fails, surface the error and stop — do not advance to step 6 with a broken interpreter.

6. **Run the regression-guard smoke test** — eduForge #19 root cause was
   `parse_hex_color()` returning `None` for CSS named colors. Verify the
   fix is in place:
   ```bash
   python -c "import sys; sys.path.insert(0, '<PLUGIN_PATH>/skills/ppt-master/scripts'); from svg_to_pptx.drawingml_utils import parse_hex_color; v = parse_hex_color('white'); assert v == 'FFFFFF', f'#19 regressed: parse_hex_color(\"white\") -> {v!r}, expected FFFFFF'; print('OK: parse_hex_color(white) =', v)"
   ```
   If this assertion fails, **stop and warn the user** — the upgrade brought back the black-PPT bug. They should pin to an earlier known-good version or file an issue.

7. **Display a markdown checklist:**
   ```
   ## ppt-master upgrade
   - [x] Plugin path: <PLUGIN_PATH>
   - [x] Pulled <OLD_SHA>..<NEW_SHA> on `main`
   - [x] Version <OLD> → <NEW>
   - [x] pip install -r requirements.txt: OK
   - [x] #19 regression guard: parse_hex_color('white') = FFFFFF
   ```
   Use `[x]` for success, `[ ]` for failure. Quote actual values.

8. **Tell the user to reload the plugin** so the new SKILL.md / scripts register:
   ```
   /reload-plugin ppt-master
   ```
   Or restart Claude Code if `/reload-plugin` is unavailable in their build.

## Idempotency

When `git pull` reports `Already up to date.`:
- `OLD == NEW` → checklist shows `Version <NEW> (unchanged)`
- Skip the reload reminder; the user is already on the latest.
- Still run the regression-guard smoke test — a stale install is a real failure mode.

## Fallback (no git available)

If `git` is missing from PATH (zip-install path), fall back to:
```bash
python3 -c "import sys; sys.path.insert(0, '<PLUGIN_PATH>/skills/ppt-master/scripts'); from svg_to_pptx.drawingml_utils import parse_hex_color; print(parse_hex_color('white'))"
```
…and tell the user to either install Git or re-download the zip from
https://github.com/mosjin/ppt-master/releases/latest.
