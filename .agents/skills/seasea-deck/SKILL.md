---
name: seasea-deck
version: 1.0.0
description: "Reverse-engineer a deck Markdown into Accenture/Deloitte boardroom-grade GPT Image 2 中文 prompts (16:9), append them as 附录 A, then batch-render PNGs into a sibling output directory next to the source doc. Trigger when the user says 'generate deck images', 'render brandbook visuals', '为 XX 文档批量生成 PPT 图', '逆向生成 GPT Image 2 prompts', 'seasea-deck', 'turn this brandbook into 16:9 images'."
metadata:
  requires:
    bins: ["python3"]
    env: ["OPENAI_API_KEY"]
  defaults:
    model: "gpt-image-2"
    size: "1792x1024"
    quality: "high"
---

# seasea-deck (v1)

Reverse a strategic Markdown deck (brandbook, pitch, internal memo) into a **GPT Image 2 中文 Prompt appendix**, then **batch-render 16:9 PNGs** at boardroom-grade visual quality (Accenture / Deloitte tone). Output PNGs land in a sibling directory named `<source-stem>-image2-output/` next to the source doc.

**CRITICAL — Before generating any prompt, MUST read [`references/visual-standard.md`](references/visual-standard.md) and [`references/prompt-template.md`](references/prompt-template.md). These two files are the contract; do not rely on memory.**

---

## When to use

Trigger on any of:
- "为 `<doc>.md` 批量生成 PPT 图 / 视觉手册图 / 16:9 PNG"
- "Reverse this brandbook into GPT Image 2 prompts"
- "为这份文档逆向生成附录 A 的中文 prompts"
- Direct invocation: user mentions `seasea-deck`

Skip when:
- The user wants HTML / video / animation output (use `hyperframes` instead).
- The user only wants Lark Slides XML (use `lark-slides`).
- The deck has fewer than 2 logical pages (just write a single prompt by hand).

---

## Inputs

| Input | Required | Notes |
|---|---|---|
| `<source>.md` | yes | The source Markdown deck. Each top-level chapter / numbered page becomes one image. |
| Page list override | no | If the user wants to skip pages or remap titles, ask for the explicit list. |
| Visual variant | no | Default is the locked Musein.ai visual standard. Other variants require an explicit new preamble — do not improvise. |
| `OPENAI_API_KEY` | yes (Phase 3) | Must be exported in shell. `~/.zshrc` is loaded; GUI envs are not. |

---

## Outputs

```
<source-dir>/
├── <source>.md                          ← appended with 附录 A
└── <source-stem>-image2-output/
    ├── page-01.png                      ← 1792×1024 (or --size override)
    ├── page-01.prompt.txt               ← exact prompt sent
    ├── ...
    ├── page-NN.png
    ├── page-NN.prompt.txt
    └── index.md                         ← table of contents with hashes
```

---

## Three-phase workflow

### Phase 1 — Reverse-engineer the deck structure

1. Read the source Markdown end-to-end.
2. Identify the **logical pages**. Default heuristics, in priority order:
   - Numbered chapters (e.g., `## 1. ...`, `## 2. ...`).
   - `##` headings that map to deck sections.
   - User-provided explicit page list.
3. For each page extract: **title (中文)**, **core narrative**, **3–5 must-show data points or visual elements**, **explicit negatives** (what NOT to draw).
4. Confirm the count and titles with the user before writing prompts (cheap to confirm, expensive to regenerate).

### Phase 2 — Generate 附录 A (append to source doc)

1. Open [`references/visual-standard.md`](references/visual-standard.md) and **copy the locked preamble verbatim** into every prompt body.
2. Open [`references/prompt-template.md`](references/prompt-template.md) and follow the exact heading shape:

   ```markdown
   ### 第 NN 页 Prompt — <中文标题>

   ```text
   <locked preamble>

   幻灯片主题："<中文标题>"。<对本页叙事的一段定性描述>。

   核心呈现内容：<具体视觉指令>。

   可选项与禁忌：<必保留 / 必避免>。
   ```
   ```

3. **Append** the appendix as a top-level `## 附录 A. <N> 页视觉品牌手册的 GPT Image 2 中文 Prompts` section at the end of the source doc. Do NOT replace existing appendices; insert a horizontal rule before it.
4. Use `search_replace` to perform the append in a single edit. Never overwrite the entire file.
5. Verify by running the script in dry-run mode (Phase 3, step 0) — it must report `len(prompts) == <expected page count>`.

### Phase 3 — Batch render PNGs

```bash
# 0. Dry run — confirm the appendix parses (no API spend)
python3 .agents/skills/seasea-deck/scripts/generate_deck_images.py \
    --source <path/to/source>.md --dry-run

# 1. Smoke test on page 1 only
python3 .agents/skills/seasea-deck/scripts/generate_deck_images.py \
    --source <path/to/source>.md --limit 1

# 2. Full batch (page 1 will be skipped because it already exists)
python3 .agents/skills/seasea-deck/scripts/generate_deck_images.py \
    --source <path/to/source>.md
```

Common flags:
- `--overwrite` — regenerate images even if `page-NN.png` already exists.
- `--size 1920x1080` — try true 16:9 if your `gpt-image-2` access supports it; otherwise default `1792x1024` (1.7500 ratio, ~1.6% off true 16:9).
- `--model <name>` — override default `gpt-image-2`.
- `--limit N` — generate first N only (useful for incremental iteration).

The script:
- Validates 16:9 landscape ratio and warns if the requested size deviates.
- Retries each page up to `--retries` times with exponential backoff.
- Writes one `.prompt.txt` sidecar per image for traceability.
- Generates an `index.md` summary at the end.

---

## Post-render verification

After generation, MUST verify:

1. **Aspect ratio of every PNG:**
   ```bash
   python3 -c "
   import struct, pathlib
   for p in sorted(pathlib.Path('<output-dir>').glob('page-*.png')):
       with open(p,'rb') as f: f.read(16); w,h = struct.unpack('>II', f.read(8))
       print(f'{p.name}: {w}x{h}, ratio={w/h:.4f}')
   "
   ```
2. **Prompt-image traceability:** every PNG has a `.prompt.txt` sibling whose SHA-256[:16] matches the `index.md` table.
3. **Visual standard adherence (manual scan, 30 sec/page):**
   - Top-left has a clean blank square (~5% of width). No logo, no frame.
   - Bottom-right shows the literal text `Privileged&Confidential` in light gray.
   - No Musein logo anywhere.
   - Background is Canvas White (warm off-white), text is Studio Black, gradient is rationed.
4. **(Optional) Pixel-exact 16:9:** if the deployment requires perfect 16:9 (1920×1080 or 1792×1008), crop in post or rerun with the larger size if your model supports it.

---

## Common pitfalls

| Symptom | Fix |
|---|---|
| `OPENAI_API_KEY is not set` | `source ~/.zshrc` first; GUI/IDE shells don't inherit it. |
| `No GPT Image prompt blocks found` | Heading shape is wrong. Check the `### 第 NN 页 Prompt — 标题` pattern; page must be 2-digit zero-padded; em-dash, en-dash, or hyphen are all accepted; the body MUST be inside a ` ```text ` fence with a blank line before it. |
| Image renders without the top-left safe zone | The preamble was paraphrased. Restore it verbatim from `references/visual-standard.md`. |
| Logo accidentally appears | A page-specific paragraph mentioned a logo, brand mark, or wordmark. Remove all such references; the locked preamble already says `不要绘制 Musein 的 Logo`. |
| Image is 1792×1024 but you need true 16:9 | Crop top+bottom by 8px each (→ 1792×1008) for clean 16:9, or rerun with `--size 1920x1080 --overwrite`. |
| Each image takes ~3 minutes | Expected for `--quality high` at 1792×1024. Run unattended; check progress with `ls <output-dir>/page-*.png`. |

---

## Reference example

The Musein Chinese brandbook is the canonical reference deck:

- **Source:** [`brand/guidelines/musein-brandbook-v1-zh.md`](../../../brand/guidelines/musein-brandbook-v1-zh.md) (附录 A spans 9 pages: 北极星 / 市场问题 / 品类转型 / 产品架构 / AI TVC / 短剧与 IP 系列 / 复利护城河 / 受众与话语 / 视觉识别与治理).
- **Output:** [`brand/guidelines/musein-brandbook-v1-zh-image2-output/`](../../../brand/guidelines/musein-brandbook-v1-zh-image2-output/) (target path; the historical run wrote to `musein-image2-output-zh/` before the skill was generalized).

When in doubt about prompt shape or visual standard, **diff your draft against the Musein appendix**, not against memory.
