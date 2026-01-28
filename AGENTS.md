# Agent Instructions

This repo develops AI coding assistant skills for ICP development.

## Repository Structure

```
skills/                    # The skills (source of truth)
  icp-backend-motoko/      # Motoko development skill
    SKILL.md               # Main skill file (required)
    patterns.md            # Data structures, HTTP, etc.
    style.md               # Code style guide
    testing.md             # Testing patterns
    advanced.md            # Advanced topics
.cursor/skills/            # Symlink to skills/ for local dev
portal/                    # Source docs from ICP portal
learn-md/                  # Converted learning articles
```

## Working on Skills

1. Edit files directly in `skills/<skill-name>/`
2. The `.cursor/skills/` symlink ensures Cursor picks them up automatically
3. Test by asking the AI to use the skill in this project

### Skill File Format

Each skill requires at minimum a `SKILL.md` with frontmatter:

```markdown
---
name: skill-name
description: Brief description for skill discovery (shown in skill picker)
---

# Skill Title

Content...
```

Additional `.md` files in the skill folder are included automatically.

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
| `install.sh` | Install skills to Cursor, Copilot, or other agents |

## Usage

```bash
# Fetch and convert source docs (incremental)
uv run fetch_learn.py

# Force re-fetch and re-convert all
uv run fetch_learn.py --force

# Test install script
./install.sh --list
```

## Source Material

- `.cache/html/` - Raw HTML cache (for debugging)
- `learn-md/` - AI-readable Markdown articles from learn.internetcomputer.org
- `portal/docs/` - Developer documentation from ICP portal
