# Contributing to seasea-deck-skill

Thank you for your interest in contributing!

## How to contribute

### Reporting issues

Open an issue for:
- Bugs or unexpected behavior
- Missing features or prompt quality issues
- Documentation improvements

### Submitting changes

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/my-improvement`
3. Make your changes
4. Run a dry-run to verify prompts still parse: `python3 scripts/generate_deck_images.py --source <any-test-deck>.md --dry-run`
5. Commit with clear messages: `git commit -m "fix: prevent logo rendering when preamble is paraphrased"`
6. Push and open a Pull Request

### Style guide for prompts

- Every prompt starts with the **locked preamble verbatim** from `references/visual-standard.md` — never paraphrase it
- Use flowing executive prose, not bullet lists
- All tokens like `Director Blue`, `Electric Indigo`, `Privileged&Confidential` stay in English
- Include a `可选项与禁忌` section listing specific numbers and what to avoid

### Code style

- Standard library Python only (no external dependencies)
- Type hints for all public functions
- 2-digit zero-padded page numbers in all headings

## License

By contributing, you agree your contributions will be licensed under the MIT License.
