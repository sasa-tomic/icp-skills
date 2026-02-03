# ICP Development Skills for AI Coding Assistants

AI-powered coding skills for the [Internet Computer Protocol (ICP)](https://internetcomputer.org/).

## Install

Download the skill file and save it to your agent's context location.

### Per-Project (Recommended)

Version-controlled with your repo, shared with your team:

| Agent | Command |
|-------|---------|
| **Claude Code** | `curl -fsSL https://raw.githubusercontent.com/sasa-tomic/icp-skills/main/dist/icp-backend-motoko.md -o CLAUDE.md` |
| **OpenCode** | `curl -fsSL https://raw.githubusercontent.com/sasa-tomic/icp-skills/main/dist/icp-backend-motoko.md -o AGENTS.md` |
| **Copilot** | `mkdir -p .github && curl -fsSL https://raw.githubusercontent.com/sasa-tomic/icp-skills/main/dist/icp-backend-motoko.md -o .github/copilot-instructions.md` |
| **Cursor** | `mkdir -p .cursor/rules && curl -fsSL https://raw.githubusercontent.com/sasa-tomic/icp-skills/main/dist/icp-backend-motoko.md -o .cursor/rules/icp-backend-motoko.mdc` |
| **Windsurf** | `curl -fsSL https://raw.githubusercontent.com/sasa-tomic/icp-skills/main/dist/icp-backend-motoko.md -o .windsurfrules` |
| **Aider** | `curl -fsSL https://raw.githubusercontent.com/sasa-tomic/icp-skills/main/dist/icp-backend-motoko.md -o CONVENTIONS.md` |

### Per-User (Global)

Install once, applies to all your ICP projects:

| Agent | Command |
|-------|---------|
| **Claude Code** | `mkdir -p ~/.claude && curl -fsSL https://raw.githubusercontent.com/sasa-tomic/icp-skills/main/dist/icp-backend-motoko.md -o ~/.claude/CLAUDE.md` |
| **OpenCode** | `mkdir -p ~/.config/opencode && curl -fsSL https://raw.githubusercontent.com/sasa-tomic/icp-skills/main/dist/icp-backend-motoko.md -o ~/.config/opencode/AGENTS.md` |
| **Cursor** | `mkdir -p ~/.cursor/rules && curl -fsSL https://raw.githubusercontent.com/sasa-tomic/icp-skills/main/dist/icp-backend-motoko.md -o ~/.cursor/rules/icp-backend-motoko.mdc` |
| **Aider** | `curl -fsSL https://raw.githubusercontent.com/sasa-tomic/icp-skills/main/dist/icp-backend-motoko.md -o ~/CONVENTIONS.md` then add `read: ~/CONVENTIONS.md` to `~/.aider.conf.yml` |

Note: Windsurf has a 6k character limit for global rules, so per-project is recommended.

## Available Skills

| Skill | Description | Status |
|-------|-------------|--------|
| `icp-backend-motoko` | Motoko language, actors, async, stable memory, upgrades | **Ready** |
| `icp-backend-rust` | Rust CDK, stable structures, memory management | Planned |
| `icp-fundamentals` | ICP architecture, subnets, canisters, consensus | Planned |
| `icp-frontend` | Asset canisters, web apps, React integration | Planned |
| `icp-authentication` | Internet Identity, session management | Planned |
| `icp-tokens-icrc` | ICRC token standards, ledger integration | Planned |

## What's Included

Each skill provides:

- **Quick reference** - Common patterns at a glance
- **Best practices** - Style guide and anti-patterns
- **Real examples** - Working production code
- **Testing patterns** - Unit and integration testing
- **Table of contents** - Easy navigation in large files

## Usage

Once installed, your AI assistant has ICP context. Just code:

```
"Create a Motoko canister that stores user profiles"
"Add ICRC-1 token transfer support"
"Write tests for this actor's upgrade behavior"
```

## Contributing

1. Fork this repo
2. Edit files in `skills/<skill-name>/`
3. Run `uv run build.py` to regenerate `dist/`
4. Submit a PR

### Skill Format

```
skills/<skill-name>/
├── SKILL.md       # Main content (required)
├── patterns.md    # Additional sections
├── style.md
└── ...
```

## Development

```bash
# Edit source files
vim skills/icp-backend-motoko/patterns.md

# Rebuild distribution
uv run build.py

# Output in dist/
ls dist/
```

## License

Apache 2.0

---

Built for the ICP developer community.
