"""API URLs, cache paths, TTL config, and environment variables."""

import os
from pathlib import Path

import httpx

BASE_URL = "https://api.comfy.org"
CLIENT_TIMEOUT = httpx.Timeout(15.0, connect=5.0)
USER_AGENT = "ComfyTemplateAgent/1.0"

CACHE_DIR = Path(__file__).parent.parent.parent / "data" / "cache"

CACHE_TTLS = {
    "highlights": 3600,     # 1 hour
    "search": 900,          # 15 minutes
    "spec": 86400,          # 24 hours
    "core_nodes": 604800,   # 7 days
    "templates": 86400,     # 24 hours
}

GITHUB_RAW_BASE = "https://raw.githubusercontent.com/Comfy-Org/workflow_templates/refs/heads/main/templates"

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
