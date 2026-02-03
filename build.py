#!/usr/bin/env python3
"""Build single-file skill distributions.

Usage:
    uv run build.py

Outputs:
    dist/<skill-name>.md  - One file per skill
    dist/icp-all.md       - All skills combined (when multiple exist)
"""

import re
from datetime import datetime, timezone
from pathlib import Path

SKILLS_DIR = Path("skills")
DIST_DIR = Path("dist")
REPO_URL = "https://github.com/sasa-tomic/icp-skills"

# File order within a skill (SKILL.md is always first, then these in order)
FILE_ORDER = ["patterns.md", "style.md", "testing.md", "advanced.md"]


def strip_frontmatter(content: str) -> str:
    """Remove YAML frontmatter from markdown content."""
    if content.startswith("---"):
        match = re.match(r"^---\s*\n.*?\n---\s*\n", content, re.DOTALL)
        if match:
            return content[match.end():]
    return content


def is_real_section_heading(title: str) -> bool:
    """Filter out code comments that look like markdown headings."""
    lower = title.lower()

    # Real section headings typically:
    # - Start with a capital letter in the original
    # - Are noun phrases or topic names
    # - Don't contain file paths or code

    # Skip command-like patterns (bash comments)
    skip_starters = (
        "install", "initialize", "init ", "add ", "run ", "update",
        "create", "set ", "get ", "check", "download", "configure",
        "enable", "import", "export", "copy", "move", "delete",
        "remove", "watch", "verbose", "ensure", "deploy", "take ",
        "list ", "restore", "follow", "on ", "step ", "local",
        "build", "start", "stop", "restart", "#", "//", "/*",
        "make ", "then ", "first ", "next ", "now ", "if ",
    )
    if lower.startswith(skip_starters):
        return False

    # Skip file paths (contain / and look like paths)
    if "/" in title:
        return False

    # Skip things that look like code (contain special chars)
    if any(c in title for c in ["()", "=>", "->", "::", "=", "{"]):
        return False

    return True


def extract_toc_headings(content: str) -> list[tuple[int, str]]:
    """Extract h1/h2 headings for table of contents, carefully skipping code blocks."""
    headings = []
    lines = content.split("\n")
    in_code_block = False

    for i, line in enumerate(lines):
        # Check for code fence (``` with optional language)
        if re.match(r"^```", line.strip()):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            continue

        # Only h1 and h2 for TOC
        match = re.match(r"^(#{1,2})\s+(.+)$", line)
        if match:
            level = len(match.group(1))
            title = match.group(2).strip()

            if is_real_section_heading(title):
                headings.append((level, title))

    return headings


def generate_toc(headings: list[tuple[int, str]]) -> str:
    """Generate a table of contents from headings."""
    toc_lines = ["## Contents", ""]
    for level, title in headings:
        # Create anchor link
        anchor = re.sub(r"[^\w\s-]", "", title.lower())
        anchor = re.sub(r"\s+", "-", anchor)
        indent = "  " * (level - 1)
        toc_lines.append(f"{indent}- [{title}](#{anchor})")
    toc_lines.append("")
    return "\n".join(toc_lines)


def get_ordered_files(skill_dir: Path) -> list[Path]:
    """Get skill files in defined order."""
    files = []

    # SKILL.md always first
    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        files.append(skill_md)

    # Then files in defined order
    for filename in FILE_ORDER:
        f = skill_dir / filename
        if f.exists():
            files.append(f)

    # Then any remaining .md files (alphabetically)
    for f in sorted(skill_dir.glob("*.md")):
        if f not in files:
            files.append(f)

    return files


def build_skill(skill_dir: Path) -> tuple[str, str]:
    """Build a single skill into one markdown file.

    Returns (skill_name, content).
    """
    skill_name = skill_dir.name
    output_file = DIST_DIR / f"{skill_name}.md"

    # Collect content from all files
    parts = []
    for md_file in get_ordered_files(skill_dir):
        content = md_file.read_text()
        if md_file.name == "SKILL.md":
            content = strip_frontmatter(content)
        else:
            # Add separator between sections
            parts.append("\n---\n")
        parts.append(content)

    body = "\n".join(parts)

    # Extract headings for TOC
    headings = extract_toc_headings(body)
    toc = generate_toc(headings)

    # Build final content with metadata header
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    header = f"""<!--
  ICP Development Skill: {skill_name}
  Generated: {now}
  Source: {REPO_URL}

  Install (per-project):
    curl -fsSL {REPO_URL}/raw/main/dist/{skill_name}.md -o <FILE>

  Per-project locations:
    Claude Code:   CLAUDE.md
    OpenCode:      AGENTS.md
    Copilot:       .github/copilot-instructions.md
    Cursor:        .cursor/rules/{skill_name}.mdc
    Windsurf:      .windsurfrules
    Aider:         CONVENTIONS.md

  Per-user (global) locations:
    Claude Code:   ~/.claude/CLAUDE.md
    OpenCode:      ~/.config/opencode/AGENTS.md
    Cursor:        ~/.cursor/rules/{skill_name}.mdc
    Aider:         ~/.aider.conf.yml (read: path/to/file)
-->

"""

    combined = header + toc + "\n" + body
    output_file.write_text(combined)

    lines = combined.count("\n") + 1
    size_kb = len(combined.encode()) / 1024
    print(f"  {skill_name}: {lines:,} lines, {size_kb:.0f} KB -> {output_file}")

    return skill_name, combined


def build_combined(skills: dict[str, str]) -> None:
    """Build combined file with all skills (only if multiple skills exist)."""
    if len(skills) <= 1:
        return

    output_file = DIST_DIR / "icp-all.md"

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    header = f"""<!--
  ICP Development Skills (All)
  Generated: {now}
  Source: {REPO_URL}

  Contains: {", ".join(sorted(skills.keys()))}
-->

# ICP Development Skills

All skills for Internet Computer Protocol development.

"""

    # Combine all skills
    parts = [header]
    for name in sorted(skills.keys()):
        parts.append(f"\n---\n\n# Skill: {name}\n\n")
        # Strip the metadata header from individual skill
        content = skills[name]
        if content.startswith("<!--"):
            end = content.find("-->")
            if end != -1:
                content = content[end + 3:].lstrip()
        parts.append(content)

    combined = "".join(parts)
    output_file.write_text(combined)

    lines = combined.count("\n") + 1
    size_kb = len(combined.encode()) / 1024
    print(f"  ALL: {lines:,} lines, {size_kb:.0f} KB -> {output_file}")


def main() -> None:
    print("Building ICP Skills")
    print("=" * 40)

    # Clean dist directory
    if DIST_DIR.exists():
        for f in DIST_DIR.iterdir():
            f.unlink()
    DIST_DIR.mkdir(exist_ok=True)

    # Build each skill
    skills = {}
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
            name, content = build_skill(skill_dir)
            skills[name] = content

    # Build combined file (only if multiple skills)
    build_combined(skills)

    print("=" * 40)
    print(f"Done. {len(skills)} skill(s) built.")


if __name__ == "__main__":
    main()
