# seasea-deck

Reverse any strategic Markdown deck into **Accenture/Deloitte boardroom-grade GPT Image 2 中文 prompts**, then batch-render 16:9 PNGs — standard-library Python only, no dependencies.

## What it does

1. **Reverse-engineer** a Markdown deck into page-by-page GPT Image 2 prompts
2. **Append** `附录 A. N 页视觉品牌手册的 GPT Image 2 中文 Prompts` to the source doc
3. **Batch render** all pages to `1792×1024` PNGs via OpenAI Images API (`gpt-image-2`)
4. Output lands in `<source-stem>-image2-output/` alongside the source doc

## Quick start

```bash
git clone https://github.com/aaronwz0/seasea-cc.git
cd seasea-cc

# Set API key
export OPENAI_API_KEY=sk-proj-...

# Dry run (no spend)
python3 .agents/skills/seasea-deck/scripts/generate_deck_images.py \
  --source /path/to/your-deck.md --dry-run

# Full batch
python3 .agents/skills/seasea-deck/scripts/generate_deck_images.py \
  --source /path/to/your-deck.md
```

## Key options

| Flag | Default | Description |
|---|---|---|
| `--size` | `1792x1024` | Landscape size. Use `1920x1080` for true 16:9 |
| `--model` | `gpt-image-2` | OpenAI image model name |
| `--quality` | `high` | `standard` or `high` |
| `--limit N` | all | Render only the first N pages |
| `--overwrite` | off | Re-render even if PNG already exists |
| `--dry-run` | off | Parse prompts only, no API calls |

## File layout

```
seasea-cc/
├── README.md
├── .agents/skills/seasea-deck/
│   ├── SKILL.md                           ← Qoder agent instruction file
│   ├── scripts/
│   │   └── generate_deck_images.py        ← batch renderer (standard library only)
│   └── references/
│       ├── visual-standard.md              ← locked Accenture/Deloitte preamble
│       └── prompt-template.md             ← heading regex, anti-patterns
```

## For Qoder agents

Place the `.agents/skills/seasea-deck/` folder in your workspace root. The agent reads `SKILL.md` automatically.

## License

MIT — free to use and modify within the Seasea OS ecosystem.
