#!/usr/bin/env bash
set -eEuo pipefail

# ICP Skills Installer
# Installs AI coding assistant skills for ICP/Motoko development

REPO_URL="https://github.com/dfinity/icp-dev-skills"
SKILLS_DIR="skills"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1" >&2; }

usage() {
    cat <<EOF
ICP Development Skills Installer

Usage: $0 [OPTIONS] [AGENT]

Agents:
  cursor      Install to .cursor/skills/ (default)
  claude      Install as CLAUDE.md (Claude Code / Anthropic)
  codex       Install as AGENTS.md (OpenAI Codex CLI)
  copilot     Install to .github/copilot-instructions.md (GitHub Copilot)
  windsurf    Install as .windsurfrules (Windsurf/Codeium)
  all         Install for all supported agents

Options:
  -g, --global    Install globally (~/.cursor/skills/) instead of project-local
  -l, --list      List available skills
  -h, --help      Show this help

Examples:
  $0                    # Install for Cursor in current project
  $0 --global           # Install globally for all Cursor projects
  $0 claude             # Install for Claude Code
  $0 all                # Install for all agents

EOF
}

list_skills() {
    echo "Available ICP Development Skills:"
    echo ""
    for skill_dir in "$SKILLS_DIR"/*/; do
        if [[ -f "${skill_dir}SKILL.md" ]]; then
            skill_name=$(basename "$skill_dir")
            # Extract description from SKILL.md frontmatter
            desc=$(grep -A1 "^description:" "${skill_dir}SKILL.md" 2>/dev/null | head -1 | sed 's/^description: *//' | cut -c1-80)
            echo "  - $skill_name"
            [[ -n "$desc" ]] && echo "    $desc"
        fi
    done
}

install_cursor() {
    local target_dir="$1"
    
    info "Installing skills to $target_dir"
    mkdir -p "$target_dir"
    
    for skill_dir in "$SKILLS_DIR"/*/; do
        if [[ -d "$skill_dir" ]]; then
            skill_name=$(basename "$skill_dir")
            info "  Installing $skill_name..."
            cp -r "$skill_dir" "$target_dir/"
        fi
    done
    
    success "Cursor skills installed to $target_dir"
}

# Generate combined markdown content from all skills
generate_combined_content() {
    local title="$1"
    
    echo "# $title"
    echo ""
    echo "These instructions help you write code for the Internet Computer Protocol (ICP)."
    echo ""
    
    for skill_dir in "$SKILLS_DIR"/*/; do
        if [[ -d "$skill_dir" ]]; then
            skill_name=$(basename "$skill_dir")
            echo "---"
            echo ""
            echo "# $skill_name"
            echo ""
            
            # Concatenate all markdown files in the skill
            for md_file in "$skill_dir"*.md; do
                if [[ -f "$md_file" ]]; then
                    # Skip frontmatter for SKILL.md
                    if [[ "$(basename "$md_file")" == "SKILL.md" ]]; then
                        sed '1,/^---$/d; 1,/^---$/d' "$md_file"
                    else
                        cat "$md_file"
                    fi
                    echo ""
                fi
            done
        fi
    done
}

install_copilot() {
    local target_dir="$1/.github"
    local target_file="$target_dir/copilot-instructions.md"
    
    info "Installing to $target_file"
    mkdir -p "$target_dir"
    
    generate_combined_content "ICP Development Instructions" > "$target_file"
    
    success "GitHub Copilot instructions installed to $target_file"
}

install_claude() {
    local target_file="$1/CLAUDE.md"
    
    info "Installing to $target_file"
    
    generate_combined_content "ICP Development Guide" > "$target_file"
    
    success "Claude Code instructions installed to $target_file"
}

install_codex() {
    local target_file="$1/AGENTS.md"
    
    # Check if AGENTS.md already exists and has content
    if [[ -f "$target_file" ]]; then
        info "AGENTS.md exists, appending ICP skills..."
        {
            echo ""
            echo "---"
            echo ""
            generate_combined_content "ICP Development Skills"
        } >> "$target_file"
    else
        info "Installing to $target_file"
        generate_combined_content "ICP Development Skills" > "$target_file"
    fi
    
    success "Codex/OpenAI instructions installed to $target_file"
}

install_windsurf() {
    local target_file="$1/.windsurfrules"
    
    info "Installing to $target_file"
    
    generate_combined_content "ICP Development Rules" > "$target_file"
    
    success "Windsurf rules installed to $target_file"
}

# Parse arguments
GLOBAL=false
AGENT="cursor"

while [[ $# -gt 0 ]]; do
    case $1 in
        -g|--global)
            GLOBAL=true
            shift
            ;;
        -l|--list)
            list_skills
            exit 0
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        cursor|claude|codex|copilot|windsurf|all)
            AGENT="$1"
            shift
            ;;
        *)
            error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Capture user's current directory before changing
USER_CWD="$(pwd)"

# Determine script location (for when run from clone)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check skills directory exists
if [[ ! -d "$SKILLS_DIR" ]]; then
    error "Skills directory not found. Run this script from the repository root."
    exit 1
fi

# Determine target directory
if $GLOBAL; then
    CURSOR_TARGET="$HOME/.cursor/skills"
    PROJECT_TARGET="$HOME"
else
    # Install to the directory where user ran the script from
    CURSOR_TARGET="$USER_CWD/.cursor/skills"
    PROJECT_TARGET="$USER_CWD"
fi

# Install based on agent
case $AGENT in
    cursor)
        install_cursor "$CURSOR_TARGET"
        ;;
    claude)
        install_claude "$PROJECT_TARGET"
        ;;
    codex)
        install_codex "$PROJECT_TARGET"
        ;;
    copilot)
        install_copilot "$PROJECT_TARGET"
        ;;
    windsurf)
        install_windsurf "$PROJECT_TARGET"
        ;;
    all)
        install_cursor "$CURSOR_TARGET"
        install_claude "$PROJECT_TARGET"
        install_copilot "$PROJECT_TARGET"
        install_windsurf "$PROJECT_TARGET"
        # Skip codex for 'all' since it modifies AGENTS.md which may conflict
        info "Skipping codex (AGENTS.md) - run './install.sh codex' separately if needed"
        ;;
esac

echo ""
success "Installation complete!"
echo ""
echo "Skills are now available. Start coding with ICP/Motoko!"
