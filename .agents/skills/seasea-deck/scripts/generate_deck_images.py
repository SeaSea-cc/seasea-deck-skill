#!/usr/bin/env python3
"""
seasea-deck: batch-generate 16:9 PPT-grade images from a deck Markdown's
"附录 A. ... GPT Image 2 中文 Prompts" appendix via OpenAI Images API.

Workflow:
1. Read the source Markdown file (--source).
2. Parse the "附录 A" prompt blocks. Heading format MUST be:
       ### 第 NN 页 Prompt — 标题

       ```text
       <prompt body>
       ```
3. POST each prompt to /v1/images/generations with size=1792x1024 (16:9).
4. Write page-NN.png + page-NN.prompt.txt + index.md to:
       <source-dir>/<source-stem>-image2-output/

Standard library only — no SDK install required.

Environment:
    OPENAI_API_KEY        required at run time (not for --dry-run)
    SEASEA_DECK_MODEL     overrides --model (default: gpt-image-2)
    SEASEA_DECK_SIZE      overrides --size  (default: 1792x1024)
    SEASEA_DECK_QUALITY   overrides --quality (default: high)
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_MODEL = "gpt-image-2"
# 1792x1024 is the closest standard OpenAI landscape size to 16:9 (1.7500 vs 1.7778).
# If your model accepts true 16:9 (e.g. 1920x1080), pass --size 1920x1080.
DEFAULT_SIZE = "1792x1024"


# Matches: "### 第 NN 页 Prompt — 标题" followed by a ```text ... ``` block.
# Accepts em dash "—", en dash "–" and hyphen "-" as separators.
PROMPT_RE = re.compile(
    r"^###\s+第\s*(?P<page>\d{2})\s*页\s*Prompt\s*[—\-–]\s*(?P<title>.+?)\n\n```text\n(?P<prompt>.*?)\n```",
    re.MULTILINE | re.DOTALL,
)


def extract_prompts(markdown: str) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for match in PROMPT_RE.finditer(markdown):
        prompt = match.group("prompt").strip()
        out.append(
            {
                "page": match.group("page"),
                "title": match.group("title").strip(),
                "prompt": prompt,
                "prompt_hash": hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16],
            }
        )
    return out


def call_images_api(
    *,
    api_key: str,
    model: str,
    prompt: str,
    size: str,
    quality: str,
    timeout: int,
) -> bytes:
    payload = {"model": model, "prompt": prompt, "size": size, "quality": quality, "n": 1}
    request = Request(
        "https://api.openai.com/v1/images/generations",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urlopen(request, timeout=timeout) as response:
        data = json.loads(response.read().decode("utf-8"))
    try:
        image_b64 = data["data"][0]["b64_json"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(
            f"Images API response missing data[0].b64_json: {data}"
        ) from exc
    return base64.b64decode(image_b64)


def write_index(
    output_dir: Path,
    source: Path,
    prompts: Iterable[dict[str, str]],
    model: str,
    size: str,
    quality: str,
) -> None:
    lines = [
        f"# {source.stem} — GPT Image 2 批量输出（16:9）",
        "",
        f"**Source:** `{source.name}`",
        f"**Model:** `{model}`",
        f"**Size:** `{size}` (landscape, 16:9 oriented)",
        f"**Quality:** `{quality}`",
        "",
        "| 页码 | 标题 | Prompt Hash | 图片 |",
        "| --- | --- | --- | --- |",
    ]
    for item in prompts:
        image_name = f"page-{item['page']}.png"
        lines.append(
            f"| {item['page']} | {item['title']} | `{item['prompt_hash']}` | "
            f"[{image_name}](./{image_name}) |"
        )
    lines.append("")
    (output_dir / "index.md").write_text("\n".join(lines), encoding="utf-8")


def assert_landscape_16_9(size: str) -> None:
    match = re.fullmatch(r"(\d+)x(\d+)", size)
    if not match:
        print(f"Warning: --size '{size}' is not WxH formatted; passing through.", file=sys.stderr)
        return
    width, height = int(match.group(1)), int(match.group(2))
    if width <= height:
        print(
            f"Warning: --size {size} is not landscape (width must exceed height for 16:9).",
            file=sys.stderr,
        )
        return
    ratio = width / height
    target = 16 / 9
    if abs(ratio - target) > 0.1:
        print(
            f"Warning: --size {size} ratio {ratio:.3f} differs from 16:9 ({target:.3f}). "
            "Use 1792x1024 or 1920x1080 for true 16:9.",
            file=sys.stderr,
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="seasea-deck: batch-generate 16:9 deck images from a Markdown 附录 A prompts block."
    )
    parser.add_argument(
        "--source",
        type=Path,
        required=True,
        help="Path to the source Markdown deck (must contain '### 第 NN 页 Prompt — ...' blocks).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory for PNGs (default: <source-dir>/<source-stem>-image2-output).",
    )
    parser.add_argument(
        "--model",
        default=os.getenv("SEASEA_DECK_MODEL", DEFAULT_MODEL),
    )
    parser.add_argument(
        "--size",
        default=os.getenv("SEASEA_DECK_SIZE", DEFAULT_SIZE),
        help="Image size; must be a 16:9 (or close) landscape ratio. Default: 1792x1024.",
    )
    parser.add_argument(
        "--quality",
        default=os.getenv("SEASEA_DECK_QUALITY", "high"),
    )
    parser.add_argument("--limit", type=int, default=None, help="Generate only the first N images.")
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--retry-sleep", type=int, default=20)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="Extract prompts, call no APIs.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    assert_landscape_16_9(args.size)

    source = args.source.resolve()
    if not source.exists():
        print(f"Source Markdown not found: {source}", file=sys.stderr)
        return 2

    output_dir = (
        args.output_dir.resolve()
        if args.output_dir
        else source.parent / f"{source.stem}-image2-output"
    )

    prompts = extract_prompts(source.read_text(encoding="utf-8"))
    if not prompts:
        print(
            f"No GPT Image prompt blocks found in {source}.\n"
            "Expected headings: '### 第 NN 页 Prompt — 标题' followed by ```text fenced block.",
            file=sys.stderr,
        )
        return 2

    if args.limit is not None:
        prompts = prompts[: args.limit]

    print(f"Source: {source}")
    print(f"Output: {output_dir}")
    print(f"Found {len(prompts)} prompt(s):")
    for item in prompts:
        print(f"  - 第 {item['page']} 页: {item['title']} ({item['prompt_hash']})")

    if args.dry_run:
        print("Dry run complete. No API calls made.")
        return 0

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY is not set. Export it before generating images.", file=sys.stderr)
        return 2

    output_dir.mkdir(parents=True, exist_ok=True)

    generated: list[dict[str, str]] = []
    for item in prompts:
        image_path = output_dir / f"page-{item['page']}.png"
        if image_path.exists() and not args.overwrite:
            print(f"Skipping existing {image_path}")
            generated.append(item)
            continue

        print(f"Generating 第 {item['page']} 页: {item['title']}")
        last_error = None
        for attempt in range(1, args.retries + 2):
            try:
                image_bytes = call_images_api(
                    api_key=api_key,
                    model=args.model,
                    prompt=item["prompt"],
                    size=args.size,
                    quality=args.quality,
                    timeout=args.timeout,
                )
                image_path.write_bytes(image_bytes)
                (output_dir / f"page-{item['page']}.prompt.txt").write_text(
                    item["prompt"], encoding="utf-8"
                )
                print(f"Wrote {image_path}")
                generated.append(item)
                break
            except HTTPError as exc:
                last_error = f"HTTP {exc.code}: {exc.read().decode('utf-8', errors='replace')}"
            except (URLError, TimeoutError, RuntimeError) as exc:
                last_error = str(exc)

            if attempt <= args.retries:
                print(f"Attempt {attempt} failed: {last_error}")
                print(f"Retrying in {args.retry_sleep}s...")
                time.sleep(args.retry_sleep)
            else:
                print(f"Failed 第 {item['page']} 页: {last_error}", file=sys.stderr)
                return 1

    write_index(output_dir, source, generated, args.model, args.size, args.quality)
    print(f"Wrote {output_dir / 'index.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
