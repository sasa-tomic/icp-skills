# Agent Instructions

## Python Dependency Management

**Always use `uv` for Python dependency management.**

- Run scripts: `uv run <script.py>`
- Add dependencies: `uv add <package>`
- Sync environment: `uv sync`
- Do NOT use pip, pip3, or virtualenv directly

## Scripts

| Script | Purpose |
|--------|---------|
| `fetch_learn.py` | Fetch learn.internetcomputer.org and convert to Markdown |

## Usage

```bash
# Fetch and convert (incremental - skips existing)
uv run fetch_learn.py

# Force re-fetch and re-convert all
uv run fetch_learn.py --force
```

## Output

- `.cache/html/` - Raw HTML cache (for debugging)
- `learn-md/` - AI-readable Markdown articles
