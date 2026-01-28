# ICP Development Skills for AI Coding Assistants

AI-powered development skills for building on the [Internet Computer Protocol (ICP)](https://internetcomputer.org/). Works with Cursor, GitHub Copilot, and other AI coding assistants.

## Quick Install

### One-liner (recommended)

```bash
# Clone and install for Cursor (project-local)
git clone --depth 1 https://github.com/dfinity/icp-dev-skills.git /tmp/icp-skills \
  && /tmp/icp-skills/install.sh \
  && rm -rf /tmp/icp-skills
```

### Manual Install

```bash
git clone https://github.com/dfinity/icp-dev-skills.git
cd icp-dev-skills

# Install for Cursor (project-local)
./install.sh cursor

# Install for Claude Code
./install.sh claude

# Install for OpenAI Codex CLI
./install.sh codex

# Install for GitHub Copilot
./install.sh copilot

# Install for Windsurf
./install.sh windsurf

# Install for all agents at once
./install.sh all

# Install Cursor skills globally (all projects)
./install.sh --global cursor
```

## Available Skills

| Skill | Description | Status |
|-------|-------------|--------|
| `icp-backend-motoko` | Motoko language, actors, async patterns, stable memory, upgrades | Ready |
| `icp-backend-rust` | Rust CDK, stable structures, memory management | Planned |
| `icp-fundamentals` | ICP architecture, subnets, canisters, consensus | Planned |
| `icp-frontend` | Asset canisters, web apps, React integration | Planned |
| `icp-authentication` | Internet Identity, session management | Planned |
| `icp-tokens-icrc` | ICRC token standards, ledger integration | Planned |

See [TODO.md](TODO.md) for the full roadmap.

## What's Included

Each skill provides:

- **Quick reference** - Common patterns and syntax at a glance
- **Best practices** - Style guides and anti-patterns to avoid
- **Real examples** - Working code from production canisters
- **Testing patterns** - Unit and integration testing approaches
- **Advanced topics** - Performance, security, and optimization

### Motoko Skill Structure

```
skills/icp-backend-motoko/
├── SKILL.md      # Core language reference and patterns
├── patterns.md   # Data structures, HTTP, encoding
├── style.md      # Code style and best practices
├── testing.md    # Testing with mops and PocketIC
└── advanced.md   # Generics, persistence, optimization
```

## Supported Agents

| Agent | Command | Install Location |
|-------|---------|------------------|
| **Cursor** | `./install.sh cursor` | `.cursor/skills/` |
| **Claude Code** | `./install.sh claude` | `CLAUDE.md` |
| **Codex CLI** | `./install.sh codex` | `AGENTS.md` |
| **GitHub Copilot** | `./install.sh copilot` | `.github/copilot-instructions.md` |
| **Windsurf** | `./install.sh windsurf` | `.windsurfrules` |
| **All agents** | `./install.sh all` | All of the above |

## Usage

Once installed, your AI assistant will automatically have context about ICP development. Just start coding:

```
"Create a Motoko canister that stores user profiles"
"Add ICRC-1 token transfer support"
"Write tests for this actor's upgrade behavior"
```

## Contributing

We welcome contributions! To add or improve skills:

1. Fork this repository
2. Edit files in `skills/`
3. Test locally with `./install.sh`
4. Submit a PR

### Skill Format

Each skill lives in `skills/<skill-name>/` with at minimum a `SKILL.md` file:

```markdown
---
name: skill-name
description: Brief description for skill discovery
---

# Skill Title

Content here...
```

## Development

This repo includes tooling to fetch and convert ICP documentation:

```bash
# Fetch learn.internetcomputer.org content
uv run fetch_learn.py

# Source documentation is in portal/ and learn-md/
```

## License

Apache 2.0 - See [LICENSE](LICENSE)

---

Built with care by the DFINITY community.
