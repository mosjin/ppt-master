# PPT Master Domain Registry (v0.5+)

> **Purpose**: when source markdown matches a registered domain's trigger regex, Strategist auto-loads the corresponding design system reference and uses its pre-approved eight-confirmation defaults (skip BLOCKING).

## Registered domains

| Domain | Trigger regex (matched against source markdown lines 1-5) | Reference file |
|--------|------------------------------------------------------------|----------------|
| EduForge CSP-S/J 教案 | `EduForge\|五幕认知循环\|RLSI[ΣI]\|知识树全景图\|prefix_sum\|binary_(answer\|search)\|union_find\|segment_tree\|scanline\|monotonic_stack` | `eduforge_csp_design_system.md` |

> Add new domains by appending rows. Each row: `| 中文 domain 名 | \`<regex>\` | \`<ref_file>\` |`

## How auto-load works (Step 4.0)

```
sources/*.md (first 5 lines)
        │
        ▼
  scan against each registered regex
        │
   ┌────┴────┐
   ▼         ▼
matched   no match
   │         │
   │         └──► standard Step 4 BLOCKING eight confirmations
   ▼
load referenced design system
   │
   ▼
use §XI predefined values for eight confirmations
   │
   ▼
skip BLOCKING (no user re-prompt)
   │
   ▼
proceed to Step 5/6 with auto-locked design
```

## Adding a new domain

1. Create your design system reference at `references/<domain>_design_system.md` following the structure of `eduforge_csp_design_system.md` (§I-§XII).
2. Pick trigger regex from your reference's §XII (load triggers section).
3. Add a row to the table above.
4. Test: place a source markdown matching the regex into a project's `sources/`, run `/ppt-master`, verify Step 4.0 prints `🎯 Domain matched: <name>`.

## Coverage testing

Use `tools/test_ppt_trigger_coverage.py` (in eduforge consumer project) to assert each domain's trigger regex matches its expected fixtures.

## Versioning

When a domain's reference file changes incompatibly (e.g., color palette swap), bump its filename: `eduforge_csp_design_system_v2.md`. Update this registry's row to point at the new file. Keep the old file for legacy projects.
