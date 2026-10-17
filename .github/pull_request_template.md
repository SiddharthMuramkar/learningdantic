## What and why

<!-- One or two sentences: what changed, and why. Link the issue if there is one (Fixes #12). -->

## Checklist

- [ ] `uv run ruff check . && uv run ruff format --check .`
- [ ] `uv run python scripts/check_notebooks.py`
- [ ] Keyless notebooks still run with no key (the list in `.github/workflows/ci.yml`)
- [ ] No ✅ Checkpoint was weakened or removed
- [ ] Outputs stripped: `uv run pre-commit run --files <changed files>`
- [ ] Ran `/code-review` and `/security-review` and fixed real findings (skip for Markdown-only changes)
- [ ] Changed a live notebook? I ran it with my own key: `uv run pytest notebooks/NN_name.ipynb`
- [ ] No API keys, tokens or `.env` contents anywhere in the diff
