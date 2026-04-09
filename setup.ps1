# ComfyUI Template Agent - Setup (Windows PowerShell)
# Requires: Developer Mode enabled or Admin shell (for symlinks)

$ErrorActionPreference = "Stop"

Write-Host "ComfyUI Template Agent - Setup" -ForegroundColor Cyan
Write-Host "=============================="

# Check Python 3.12+
try {
    $pythonVersion = (python --version 2>&1) -replace "Python ", ""
    $parts = $pythonVersion.Split(".")
    $major = [int]$parts[0]
    $minor = [int]$parts[1]
    if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 12)) {
        Write-Host "ERROR: Python $pythonVersion found, need 3.12+." -ForegroundColor Red
        exit 1
    }
    Write-Host "OK Python $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python not found. Install Python 3.12+" -ForegroundColor Red
    exit 1
}

# Install dependencies (editable mode makes python -m src.* work from anywhere)
Write-Host ""
Write-Host "Installing dependencies..."
pip install -e ".[dev]"

# Create skill symlinks in ~/.claude/skills/
$skillsDir = Join-Path $env:USERPROFILE ".claude\skills"
$repoSkills = Join-Path $PSScriptRoot ".claude\skills"

if (-not (Test-Path $skillsDir)) {
    New-Item -ItemType Directory -Path $skillsDir -Force | Out-Null
}

Write-Host ""
Write-Host "Linking skills..."
$skills = @("comfy-discover", "comfy-template-audit", "comfy-validate", "comfy-compose", "comfy-document", "comfy-flow")

foreach ($skill in $skills) {
    $target = Join-Path $skillsDir $skill
    $source = Join-Path $repoSkills $skill

    if (Test-Path $target) {
        $item = Get-Item $target -Force
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
            Write-Host "SKIP $skill (symlink exists)" -ForegroundColor Yellow
        } else {
            Write-Host "WARN $skill directory exists at $target — skipping (remove manually to re-link)" -ForegroundColor Yellow
        }
    } else {
        try {
            New-Item -ItemType SymbolicLink -Path $target -Target $source | Out-Null
            Write-Host "OK   $skill -> $source" -ForegroundColor Green
        } catch {
            Write-Host "FAIL $skill — enable Developer Mode or run as Admin for symlinks" -ForegroundColor Red
        }
    }
}

# Prerequisites reminder
Write-Host ""
Write-Host "Prerequisites:" -ForegroundColor Cyan
Write-Host "  - ComfyUI MCP server (comfyui-cloud or comfyui-mcp) for compose/flow skills"
Write-Host "  - Notion MCP server for document skill (optional)"
Write-Host "  - GITHUB_TOKEN env var for higher API rate limits (optional)"
Write-Host ""

# Run tests
Write-Host "Running tests..."
python -m pytest tests/ -q
Write-Host ""
Write-Host "Setup complete! Use /comfy-flow in Claude Code to start." -ForegroundColor Green
