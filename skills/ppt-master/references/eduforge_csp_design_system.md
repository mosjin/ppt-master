# EduForge CSP-S/J 教案设计系统 — ppt-master 适配 reference

> **权威来源**: `docs/STYLE_SPEC_v11.md`（单一真相源）— 修改规范先改 STYLE_SPEC_v11.md，再同步本文件。
>
> **背景**：当 ppt-master 被 eduforge skill (https://github.com/mosjin/eduforge_skill) 调用生成 CSP-S/J / NOI 竞赛编程教案 PPT 时，加载本文件作为 Strategist 八项确认的预设默认值。
>
> **来源**：基于 5 月 4 日 P1314 教案 suite（v10 280KB 真内容版）+ 5 月 5 日 prefix_sum_1d 34 帧 SVG 主 agent 手写实证（150KB v1.3.2 audit pass）的设计 DNA。
>
> **触发**：当 markdown 源含 `EduForge v11.0` / `五幕认知循环 RLSIΣ` / `知识树全景图` 等关键词时自动启用。

---

## 0. 三层架构定位

```
Layer 1：教案标准（v3.1→v11.0 累加）— markdown 内容
Layer 2：ppt-master — markdown → SVG → PPT  ← 本 reference 在此层服务
Layer 3：eduforge — skill 化 + 通用化（所有 AI）
```

ppt-master 不应假定教案内容；本 reference 仅约束**渲染样式**，让生成的 SVG 视觉风格统一。

---

## I. Canvas 约束

```
format:    ppt169 (1280×720)
viewBox:   0 0 1280 720
margins:   left/right 56px, top 52px, bottom 48px
content:   1168 × 620 px
```

---

## II. 「阿力的彩色地毯展厅」DNA — 5 条铁律

1. **不用渐变背景** — 暖纸色底 `#F5EFE3` 保持纯净，projector 友好
2. **不临时发明图形** — 只组合六种主角元素：卡片 / 箭头 / 数组格 / 代码面板 / 标注 / 轨迹
3. **代码块永远 IntelliJ Classic Light** — 白底深色字 (`#FFFFFF` bg + `#1A1814` ink + 关键字 `#000080` navy)
4. **口诀框永远朱砂左边框** — `stroke="#C94620" stroke-width="3"` 在左侧
5. **每幻灯片左下角必有帧编号戳** — `[fNN] [幕badge]` (Consolas 13px bold)，与课堂版.md 帧号一一对应

---

## III. 18 色语义调色板

| 角色 | HEX | 用途 |
|------|-----|------|
| paper | `#F5EFE3` | 页面底色（燕麦纸）|
| paper-2 | `#EDE4D1` | 卡片背景、代码面板衬底 |
| ink | `#1A1814` | 主文字（近黑暖色）|
| ink-2 | `#2B2620` | 正文、解说文字 |
| ink-3 | `#5A5147` | 注释、副标题、帧号 |
| rule | `#C9BEA6` | 分割线、卡片边框 |
| highlight | `#F5CD46` | 关键点高亮背景 |
| **rust 朱砂** | `#C94620` | lo/hi 边界指针 · B帧 WRONG · 口诀左边框 · **幕I act 色** |
| rust-deep | `#8A2F15` | 朱砂深色（文字、边框）|
| **teal 青绿** | `#1F7378` | check=true ✅ · 可行 · cnt 数组 |
| teal-deep | `#134E52` | 青绿深色 |
| **mustard 藤黄** | `#D89528` | mid 中间值 · P帧预测高亮 · 答案候选 · **幕R act 色** |
| mustard-deep | `#9C6812` | 藤黄深色 |
| **plum 绛紫** | `#6F3258` | D帧推导 · Proof 数学证明框 · **幕S act 色** |
| **moss 苔绿** | `#667A2E` | 答案 W* · 正确结论 · **幕Σ act 色** |
| **sky 黛蓝** | `#3C6589` | T帧下游预告 · 知识树 · 关联链 · **幕L act 色** |
| code-bg | `#FFFFFF` | 代码块背景 |
| code-keyword | `#000080` | 代码关键字（navy bold）|
| code-comment | `#808080` | 代码注释（gray italic）|
| code-number | `#0000FF` | 代码数字（blue）|
| code-string | `#008000` | 代码字符串（green）|

## IV. 五幕色映射

| 幕 | 名称 | act 色 | HEX |
|----|------|--------|-----|
| R | 知识热身 | mustard 藤黄 | `#D89528` |
| L | 图谱建构 | sky 黛蓝 | `#3C6589` |
| S | 精讲引导 | plum 绛紫 | `#6F3258` |
| I | 独立实战 | rust 朱砂 | `#C94620` |
| Σ | 归纳总结 | moss 苔绿 | `#667A2E` |
| 序幕 | OPEN | ink-3 | `#5A5147` |

---

## V. 字体系统

| 角色 | 字体 | 字重 | 大小 |
|------|------|------|------|
| 封面 Display | Noto Serif SC, Microsoft YaHei, serif | 900 | 52px |
| H1 幕标题 | Noto Serif SC | 700 | 36px |
| H2 帧标题 | Noto Serif SC | 500 | 26px |
| H3 节标题 | Noto Sans SC, Microsoft YaHei, sans-serif | 700 | 22px |
| Body | Noto Sans SC | 500 | 20px |
| 正文 small | Noto Sans SC | 500 | 17px |
| 注释 Annotation | Noto Sans SC | 500 | 15px ← **最小内容字号** |
| 代码 Code | Consolas, Courier New, monospace | 500 | 17px |
| 帧号戳/眉线 | Consolas | 700 | 11–13px (UI chrome 专用) |

### 字体硬约束

- 所有 `<text>` 必须显式 `font-weight`（缺失会让投影屏字体细若发丝）
- 内容文字最低 `font-weight="500"`，标题 `"700"`+
- SVG 属性内**禁嵌套双引号**（破 XML 解析）— 用 bare names: `font-family="Consolas, monospace"`

---

## VI. 标准滑轨组件（每页固定元素）

```svg
<!-- 1. Eyebrow（眉线，y=40） -->
<text x="56" y="40" font-family="Consolas, monospace" font-size="12"
      font-weight="700" fill="#5A5147" letter-spacing="0.2em">
  EDUFORGE v11.0  ·  &lt;KP_NAME&gt;  ·  &lt;PID/SLUG&gt;
</text>
<line x1="56" y1="52" x2="1224" y2="52" stroke="#C9BEA6" stroke-width="1"/>

<!-- 2. 幕徽（右上，y=40） -->
<circle cx="1180" cy="40" r="6" fill="{ACT_COLOR}"/>
<text x="1196" y="44" font-family="Consolas, monospace" font-size="13"
      font-weight="700" fill="{ACT_COLOR}">幕{ACT_NAME}</text>

<!-- 3. 帧标题（y=110） -->
<text x="56" y="110" font-family="Noto Serif SC, Microsoft YaHei, serif"
      font-size="28" font-weight="700" fill="#1A1814">
  {fNN} · {帧类型} · {帧标题}
</text>
<line x1="56" y1="135" x2="1224" y2="135" stroke="{ACT_COLOR}" stroke-width="2"/>

<!-- 4. 内容区（y=170-660） -->
<!-- ... 主体卡片/数组/代码 panel/口诀框 等 ... -->

<!-- 5. 帧号戳 + 底部品牌（y=680-695） -->
<rect x="56" y="680" width="60" height="22" rx="3" fill="{ACT_COLOR}"/>
<text x="86" y="695" text-anchor="middle" font-family="Consolas, monospace"
      font-size="13" font-weight="700" fill="#FFFFFF">{fNN}</text>
<text x="124" y="695" font-family="Consolas, monospace" font-size="11"
      font-weight="500" fill="#5A5147">幕{ACT} {ACT_NAME}</text>
<text x="1224" y="695" text-anchor="end" font-family="Consolas, monospace"
      font-size="11" font-weight="500" fill="#5A5147">
  EduForge v11.0  ·  {KP_NAME}
</text>
```

---

## VII. 视觉元素 catalog（六种主角元素）

### 1. 卡片（rounded panel）

```svg
<rect x="80" y="170" width="540" height="220" rx="10"
      fill="#FFFFFF" stroke="#3C6589" stroke-width="2"/>
<text x="100" y="208" font-family="Noto Sans SC, sans-serif"
      font-size="22" font-weight="700" fill="#3C6589">🪣 已经建立的画面</text>
<!-- body text -->
```

### 2. 数组格子（algorithm visualization）

```svg
<rect x="240" y="312" width="64" height="50" rx="4"
      fill="#FFFFFF" stroke="#3C6589" stroke-width="2"/>
<text x="272" y="345" text-anchor="middle"
      font-family="Consolas, monospace" font-size="22" font-weight="700"
      fill="#3C6589">2</text>
```

### 3. 代码面板（IntelliJ Classic Light）

**铁律（#119 fix）：每行代码用 1 个 `<text>` + N 个 `<tspan>`，禁止每 token 独立 `<text>`。**
多 `<text>` 方案要求 AI 估算 x 坐标（Consolas 19px ≈ 11.4px/字符），累计误差导致关键字与变量名重叠。
`<tspan>` 方案让渲染器自动算间距，零重叠。

```svg
<!-- ✅ 正确：行号独立 <text>；代码行 = 单 <text> + 多 <tspan> -->
<rect x="80" y="155" width="740" height="490" rx="8" fill="#FFFFFF" stroke="#C9BEA6" stroke-width="1.5"/>
<text x="100" y="188" font-family="Consolas, monospace" font-size="13" font-weight="700" fill="#5A5147">solution.cpp</text>
<line x1="100" y1="196" x2="800" y2="196" stroke="#C9BEA6" stroke-width="1"/>

<text x="112" y="224" font-family="Consolas, monospace" font-size="13" font-weight="500" fill="#808080">01</text>
<text x="150" y="224" font-family="Consolas, monospace" font-size="19" font-weight="500" fill="#808080" font-style="italic"><tspan>// 二分答案：check(W) 是否可行</tspan></text>

<text x="112" y="250" font-family="Consolas, monospace" font-size="13" font-weight="500" fill="#808080">02</text>
<text x="150" y="250" font-family="Consolas, monospace" font-size="19" font-weight="500" fill="#1A1814"><tspan fill="#000080" font-weight="700">int</tspan><tspan> lo = </tspan><tspan fill="#0000FF">1</tspan><tspan>, hi = n;</tspan></text>

<text x="112" y="276" font-family="Consolas, monospace" font-size="13" font-weight="500" fill="#808080">03</text>
<text x="150" y="276" font-family="Consolas, monospace" font-size="19" font-weight="500" fill="#1A1814"><tspan fill="#000080" font-weight="700">while</tspan><tspan> (lo &lt;= hi) {</tspan></text>

<text x="112" y="302" font-family="Consolas, monospace" font-size="13" font-weight="500" fill="#808080">04</text>
<text x="150" y="302" font-family="Consolas, monospace" font-size="19" font-weight="500" fill="#1A1814"><tspan>    </tspan><tspan fill="#000080" font-weight="700">int</tspan><tspan> mid = (lo + hi) / </tspan><tspan fill="#0000FF">2</tspan><tspan>;</tspan></text>

<!-- ❌ 错误示范（禁止）：多 <text> 硬编码 x，会导致 token 重叠 -->
<!-- <text x="150" y="302" ...>    </text>                    -->
<!-- <text x="186" y="302" ...>int</text>   ← x 坐标估算误差  -->
<!-- <text x="216" y="302" ...> mid = ...</text> ← 与上行重叠 -->
```

### 4. 口诀框（朱砂左边框 + 渐变背景）

```svg
<rect x="80" y="200" width="1120" height="320" rx="20" fill="#C94620"/>
<text x="640" y="280" text-anchor="middle"
      font-family="Noto Serif SC, serif" font-size="32"
      font-weight="500" fill="#F5EFE3">📜 整课总结口诀（11 字）</text>
<line x1="380" y1="310" x2="900" y2="310" stroke="#F5CD46" stroke-width="3"/>
<text x="640" y="395" text-anchor="middle"
      font-family="Noto Serif SC, serif" font-size="56"
      font-weight="900" fill="#FFFFFF">前缀差出区间</text>
```

### 5. 锚定 / 总结横幅（act 色背景）

```svg
<rect x="80" y="555" width="1120" height="105" rx="10" fill="#3C6589" opacity="0.95"/>
<text x="640" y="600" text-anchor="middle"
      font-family="Noto Serif SC, serif" font-size="26"
      font-weight="700" fill="#F5EFE3">💡 关键设计</text>
```

### 6. 桥梁帧（左右 panel + 中间巨大箭头）

```svg
<rect x="80" y="280" width="540" height="220" rx="10" fill="#EDE4D1" stroke="#5A5147" stroke-width="2"/>
<!-- 左 panel：旧场景 -->

<text x="640" y="395" text-anchor="middle"
      font-family="Consolas, monospace" font-size="60" font-weight="700" fill="#C94620">→</text>

<rect x="660" y="280" width="540" height="220" rx="10" fill="#FFFFFF" stroke="#C94620" stroke-width="3"/>
<!-- 右 panel：新场景 -->
```

---

## VIII. 内容硬约束（v1.3.2 audit 拦截）

❌ **禁出现的占位词**（任一出现 = `V_PPT_CONTENT_NOT_PLACEHOLDER` CRITICAL fail）：
- `详见课堂版`
- `教师按 .md 内容讲解` / `教师按.md内容讲解`
- `EDUFORGE_SCAFFOLD_V132` (marker)

✅ **必须出现的真内容**（从 markdown frame body 提取）：
- 帧标题（不只 `f01`，要含具体内容如 `f01 · 知识树全景图 — 今天的旅程`）
- 该帧 markdown body 的核心内容（叙事段落 / 代码块 / 数学公式 / 口诀）
- 视觉化（数组格子 / 代码 panel / 卡片对比 / 桥梁箭头）

---

## IX. SVG 技术约束（与 shared-standards.md 一致）

- ❌ 禁 `rgba()`（用 `stop-opacity` 或 `fill-opacity`）
- ❌ 禁 `<style>` / `class` / `<foreignObject>` / `<animate*>` / `<script>`
- ❌ 禁 HTML 命名实体 `&nbsp;` 等（用 Unicode 直接写）
- ❌ 禁 XML 注释含 `--`（XML 1.0 §2.5 违规，svg_quality_checker 报 ERROR）
- ❌ 禁混用图标库；所有可视化通过 SVG 直接绘制
- ❌ 禁代码行内多 `<text>` token 拆分 — 每行代码用 1 `<text>` + N `<tspan>`（#119 fix，见 §VII.3）

---

## X. 五幕节奏（page_rhythm 提示）

| 幕 | rhythm | 帧数典型 |
|----|--------|---------|
| 序幕 | breathing | 1-2 帧（知识树 + 叙事） |
| R | dense | 3-4 帧（K帧 + MCQ） |
| L | mixed | 8-12 帧（Q/P/D/B/M/A/I 七联帧 + L5→L1） |
| S | dense | 6-8 帧（PVSPR + Cs + Sv） |
| I | breathing | 3 帧（桥梁 + 变体 + 校对） |
| Σ | mixed | 3-4 帧（题型图谱 + 元认知 + 下游） |

---

## XI. Strategist 八项预设（八项 BLOCKING 直接采用，无需重问）

当 markdown 触发 eduforge mode 时，Strategist 八项确认采用以下默认值：

1. **Canvas format**: `ppt169` (1280×720)
2. **页数范围**: 课堂版 .md 帧数（grep `^### f\d+` 计数）
3. **目标受众**: 小学/初中，初次接触该知识点
4. **风格目标**: 「阿力的彩色地毯展厅」DNA（5 条铁律 §II）
5. **配色**: 18 色语义板 + 5 幕 act 色（§III §IV）
6. **图标**: SVG inline (Lucide 风格简笔)，无 CDN
7. **字体**: §V 字体系统
8. **图片**: 默认无 AI 图（前缀和/二分等概念用 SVG 直接画）

---

## XII. 加载触发条件

ppt-master 在 Step 4 Strategist 阶段，**先看 markdown 第 1-5 行**，若含以下任一关键词则自动加载本 reference：

- `EduForge`
- `五幕认知循环` / `RLSIΣ`
- `七联帧` / `Q→P→D→B→M→A→I`
- `知识树全景图`
- `prefix_sum` / `binary_search` / `binary_answer` / `union_find` / `segment_tree`（或其他 CSP 关键算法 slug）

加载后跳过 Strategist 八项 BLOCKING（已用本文件预设），直接进 Step 5/6。

---

## XIII. 实证 reference

| 教案 | 帧数 | 备注 |
|------|------|------|
| P1314 | 50 帧 | 5 月 4 日 ppt-master 全流程，v10 真内容 |
| prefix_sum_1d | 34 帧 | 5 月 5 日主 agent 手写实证（v1.3.2 audit pass）|
| **P8218** | **50 帧** | **v11.0 权威参考实现**（spec_lock.md canonical source） |

未来 binary_answer (50 帧) + 其它 KP 应用本设计系统。

---

> 本文件是 `docs/STYLE_SPEC_v11.md` 的 ppt-master 适配摘要。如遇冲突，以 STYLE_SPEC_v11.md 为准。
