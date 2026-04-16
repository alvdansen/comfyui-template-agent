#!/usr/bin/env bash
set -euo pipefail

echo "ComfyUI Template Agent - Setup"
echo "=============================="

# Check Python 3.12+
python_cmd=""
for cmd in python3.12 python3 python; do
    if command -v "$cmd" &>/dev/null; then
        python_cmd="$cmd"
        break
    fi
done

if [[ -z "$python_cmd" ]]; then
    echo "ERROR: Python not found. Install Python 3.12+"
    exit 1
fi

python_version=$($python_cmd --version 2>/dev/null | sed -E 's/Python ([0-9]+\.[0-9]+).*/\1/' | head -1)
major=$(echo "$python_version" | cut -d. -f1)
minor=$(echo "$python_version" | cut -d. -f2)
if (( major < 3 || (major == 3 && minor < 12) )); then
    echo "ERROR: Python $python_version found, need 3.12+."
    exit 1
fi
echo "OK Python $python_version"

# Create/activate virtual environment
VENV_DIR=".venv"
if [[ ! -d "$VENV_DIR" ]]; then
    echo ""
    echo "Creating virtual environment..."
    $python_cmd -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"
python_cmd="python"

# Install dependencies (editable mode makes python -m src.* work from anywhere)
echo ""
echo "Installing dependencies..."
python -m pip install -e ".[dev]"

# Create skill symlinks in ~/.claude/skills/
SKILLS_DIR="$HOME/.claude/skills"
REPO_SKILLS="$(cd "$(dirname "$0")" && pwd)/.claude/skills"

mkdir -p "$SKILLS_DIR"

echo ""
echo "Linking skills..."
for skill in comfy-discover comfy-template-audit comfy-validate comfy-compose comfy-document comfy-flow comfy-onboard comfy-explain; do
    target="$SKILLS_DIR/$skill"
    source="$REPO_SKILLS/$skill"
    if [[ -L "$target" ]]; then
        echo "SKIP $skill (symlink exists)"
    elif [[ -d "$target" ]]; then
        echo "WARN $skill directory exists at $target — skipping (remove manually to re-link)"
    else
        ln -s "$source" "$target"
        echo "OK   $skill -> $source"
    fi
done

# Prerequisites reminder
echo ""
echo "Prerequisites:"
echo "  - ComfyUI MCP server (comfyui-cloud or comfyui-mcp) for compose/flow skills"
echo "  - Notion MCP server for document skill (optional)"
echo "  - GITHUB_TOKEN env var for higher API rate limits (optional)"
echo ""

# Run tests
echo "Running tests..."
$python_cmd -m pytest tests/ -q
echo ""
echo "Setup complete! Use /comfy-flow in Claude Code to start."
