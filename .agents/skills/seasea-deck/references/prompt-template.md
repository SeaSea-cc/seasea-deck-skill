# seasea-deck — Appendix A Heading & Prompt Template

The batch generator (`scripts/generate_deck_images.py`) parses prompts via this **exact** regex:

```text
^###\s+第\s*(?P<page>\d{2})\s*页\s*Prompt\s*[—\-–]\s*(?P<title>.+?)

```text
(?P<prompt>.*?)
```
```

So every appended prompt block MUST follow this shape — page number is **two zero-padded digits**, separator is em-dash `—` (en-dash `–` and hyphen `-` also accepted), and the prompt body MUST be inside a ` ```text ` fenced block with a blank line between heading and fence.

## Appendix A skeleton (append to source doc)

```markdown
---

## 附录 A. <N> 页视觉品牌手册的 GPT Image 2 中文 Prompts

> 用于在 GPT Image 2 上批量生成本手册的视觉版本（16:9，1920×1080）。每条 Prompt 自带视觉标准前置段，可直接复制使用。生成脚本：`.agents/skills/seasea-deck/scripts/generate_deck_images.py`。

### 第 01 页 Prompt — <第 1 页中文标题>

```text
<LOCKED_PREAMBLE — see references/visual-standard.md>

幻灯片主题："<第 1 页中文标题>"。<对该页核心叙事的一段框架性描述>。

核心呈现内容：<针对该页的具体视觉指令：图表、callout、流程示意、关键数字、对比、版式分区。使用 Canvas White / Studio Black / Director Blue → Electric Indigo 强调色描述细节>。

可选项与禁忌：<列出本页要刻意避免的视觉、必须保留的关键词、文本要素>。
```

### 第 02 页 Prompt — <第 2 页中文标题>

```text
... (same shape)
```

... (one block per source page)
```

## Per-page prompt body — recommended structure

Each prompt body inside the fence has 3-5 paragraphs:

1. **Locked preamble** — copy verbatim from `references/visual-standard.md`.
2. **Subject sentence** — `幻灯片主题："<title>"。` plus one paragraph of narrative framing.
3. **Visual content directive** — what to draw: charts, diagrams, callouts, key numbers, layout regions, anchored quotations, comparison panels, etc. Reference the palette and gradient sparingly.
4. **(Optional) Negative & must-keep list** — what to avoid (consumer-app palette, stock-photo people, decorative gradients) and what must appear (specific phrases, KPI numbers).

## Title sizing helper

If the primary subject must dominate a sub-headline, append after the title clause:

```text
该主题字号要比副标题的字号大2.5倍。
```

## Anti-patterns (will be rejected by reviewers)

- Bullet-point dumps masquerading as prompt — must be flowing executive prose.
- Pixel coordinates / strict layout grids — let the model interpret editorial composition.
- Brand logo references — explicitly forbidden by the visual standard.
- English mixed with Chinese narrative — keep the body Chinese; tokens like `Director Blue` / `Electric Indigo` / `Privileged&Confidential` stay verbatim.
