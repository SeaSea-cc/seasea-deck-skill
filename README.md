# seasea-deck-skill

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/downloads/)
[![Standard Library](https://img.shields.io/badge/standard%20library-only-orange.svg)](#dependencies)

> Reverse any Markdown deck into **Accenture/Deloitte boardroom-grade GPT Image 2 中文 prompts**, then batch-render 16:9 PNGs. No dependencies.

## What it does

```
输入: 一份中文 Markdown 格式的战略文档（品牌手册 / pitch / 内参）
        ↓  Phase 1 — 逆向结构（第 N 页 → 标题 + 核心叙事 + 关键数据）
        ↓  Phase 2 — 生成附录 A（GPT Image 2 Prompts，含锁定视觉标准前导段）
        ↓  Phase 3 — 调用 OpenAI Images API，批量输出 PNG
输出: <源文档名>-image2-output/page-01.png … page-NN.png
```

## Features

- **Zero dependencies** — standard library Python only, no pip install
- **GPT Image 2** via OpenAI Images API (`b64_json` response)
- **16:9 landscape** at `1792×1024` (or `--size 1920x1080` for true 16:9)
- **Accenture/Deloitte boardroom visual standard** — locked preamble, never paraphrased
- **Prompt traceability** — every PNG has a `.prompt.txt` sidecar + SHA-256 hash
- **Idempotent** — skips existing images by default, `--overwrite` to re-render

## Quick start

```bash
# Clone
git clone https://github.com/SeaSea-cc/seasea-deck-skill.git
cd seasea-deck-skill

# Set API key
export OPENAI_API_KEY=sk-proj-...

# Dry run — verify prompts parse (no spend)
python3 .agents/skills/seasea-deck/scripts/generate_deck_images.py \
  --source /path/to/your-deck.md --dry-run

# Smoke test — render page 1 only
python3 .agents/skills/seasea-deck/scripts/generate_deck_images.py \
  --source /path/to/your-deck.md --limit 1

# Full batch
python3 .agents/skills/seasea-deck/scripts/generate_deck_images.py \
  --source /path/to/your-deck.md
```

## CLI options

| Flag | Default | Description |
|---|---|---|
| `--source <file>` | **required** | Source Markdown deck |
| `--size` | `1792x1024` | Landscape size. `1920x1080` for true 16:9 |
| `--model` | `gpt-image-2` | OpenAI image model name |
| `--quality` | `high` | `standard` or `high` |
| `--limit N` | all | Render only the first N pages |
| `--overwrite` | off | Re-render even if PNG exists |
| `--dry-run` | off | Parse prompts only, no API calls |
| `--retries N` | `2` | Retry count per page |
| `--output-dir <dir>` | auto | Custom output directory |

## Output structure

```
/path/to/
├── your-deck.md
└── your-deck-image2-output/
    ├── page-01.png
    ├── page-01.prompt.txt          ← exact prompt sent
    ├── page-02.png
    ├── page-02.prompt.txt
    └── index.md                    ← page / hash / file table
```

## File layout

```
seasea-deck-skill/
├── README.md
├── LICENSE                        ← MIT
├── CHANGELOG.md
├── CONTRIBUTING.md
└── .agents/skills/seasea-deck/
    ├── SKILL.md                   ← Qoder agent instruction file
    ├── scripts/
    │   └── generate_deck_images.py
    └── references/
        ├── visual-standard.md     ← locked preamble (verbatim!)
        └── prompt-template.md     ← heading regex, anti-patterns
```

## Dependencies

**None.** Uses only Python 3.8+ standard library:
`argparse · base64 · hashlib · json · os · pathlib · re · urllib`

## For Qoder agents

Place the `.agents/skills/seasea-deck/` folder in your workspace root.
The agent reads `SKILL.md` automatically.

## License

MIT — see [LICENSE](./LICENSE).
