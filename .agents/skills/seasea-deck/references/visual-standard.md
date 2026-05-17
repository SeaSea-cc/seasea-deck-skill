# seasea-deck — Visual Standard (Locked Preamble)

> **Do not edit lightly.** This preamble is the contract between the deck content and the GPT Image 2 renderer. Every page prompt MUST start with this exact preamble (substituting only the page-specific subject line described in `prompt-template.md`).

## Locked Preamble (中文)

```text
创建一张 16:9 高管战略幻灯片图像，1920x1080，用于 Musein.ai。采用 Accenture / Deloitte 级别的董事会咨询视觉标准：锐利的信息层级、高端编辑式版式、内容密集但可扫读的商业信息、精致的矢量风格示意图、考究的字体排印，避免任何消费类应用的活泼调性。使用 Canvas White / 米白色背景、Studio Black 黑色文字，仅在关键强调、活跃工作流路径和战略亮点处使用 Director Blue 至 Electric Indigo 的明亮渐变。在图像左上角预留一块等于整图宽度 5% 的空白正方形；该区域与背景完全一致，无边框、无占位符、无图标、无 Logo、无任何框架。不要绘制 Musein 的 Logo。在图像右下角加入精确文本 "Privileged&Confidential"，以浅灰色小号字呈现。
```

## What this guarantees

| Element | Spec |
|---|---|
| Aspect ratio | 16:9 landscape (1920×1080 declared in prompt; rendered at `1792×1024` if the model rejects 1920) |
| Tone | Accenture / Deloitte boardroom-grade, editorial, dense-but-scannable |
| Palette | Canvas White background, Studio Black text, Director Blue → Electric Indigo gradient for emphasis only |
| Logo safe zone | 5% blank square in **top-left**, identical to background, no frame |
| Watermark | "Privileged&Confidential" in **bottom-right**, light-gray small caps |
| Logo policy | Do **not** render the Musein logo |

## Per-page subject line

Every page-specific prompt MUST insert a line of the form:

```
幻灯片主题："<page title in Chinese>"。<one-paragraph framing of the page narrative>.
```

Then the subsequent paragraphs describe the visual content (charts, callouts, diagrams) using the palette and the dense-editorial idiom defined above.

## Title-vs-subtitle sizing convention

When the page has a primary subject and a subtitle/secondary line, the primary subject font should be **2.5×** the subtitle font size. Add the literal phrase `该主题字号要比副标题的字号大2.5倍` after the page title clause when this hierarchy is required.

## Common quality controls (always include)

- `信息密集但可扫读` (dense but scannable)
- `精致的矢量风格示意图` (refined vector-style diagrams)
- `考究的字体排印` (considered typography)
- `避免任何消费类应用的活泼调性` (no consumer-app cheer)
- `仅在关键强调处使用 Director Blue 至 Electric Indigo 的明亮渐变` (gradient is rationed)
