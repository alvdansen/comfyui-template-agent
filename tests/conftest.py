"""Shared test fixtures for ComfyUI Template Agent tests."""

import pytest


@pytest.fixture
def sample_node_pack_data() -> dict:
    """Dict matching registry API /nodes response shape for a single node pack."""
    return {
        "id": "comfyui-impact-pack",
        "name": "Impact Pack",
        "author": "Dr.Lt.Data",
        "description": "A collection of useful nodes for ComfyUI",
        "downloads": 250000,
        "github_stars": 1500,
        "rating": 4.8,
        "created_at": "2024-01-15T00:00:00Z",
        "repository": "https://github.com/ltdrdata/ComfyUI-Impact-Pack",
        "tags": [],
        "status": "NodeStatusActive",
        "icon": "https://example.com/icon.png",
    }


@pytest.fixture
def sample_comfy_node_data() -> dict:
    """Dict matching /comfy-nodes response shape for a single comfy node."""
    return {
        "comfy_node_name": "KSampler",
        "category": "sampling",
        "input_types": '{"required": {"model": ["MODEL"], "seed": ["INT"], "image": ["IMAGE"]}}',
        "return_types": '["IMAGE"]',
        "return_names": "",
        "deprecated": False,
        "experimental": False,
    }


@pytest.fixture
def sample_search_result(sample_node_pack_data: dict) -> dict:
    """Dict matching full /nodes paginated response."""
    return {
        "nodes": [sample_node_pack_data],
        "total": 1,
        "page": 1,
        "limit": 50,
        "totalPages": 1,
    }


@pytest.fixture
def sample_workflow_json() -> dict:
    """Dict in ComfyUI workflow format (has nodes list and links list)."""
    return {
        "nodes": [
            {"id": 1, "type": "KSampler", "pos": [100, 200]},
            {"id": 2, "type": "VAEDecode", "pos": [300, 200]},
        ],
        "links": [
            [1, 1, 0, 2, 0, "LATENT"],
        ],
    }


@pytest.fixture
def sample_api_json() -> dict:
    """Dict in ComfyUI API format (flat keys with class_type values)."""
    return {
        "3": {
            "class_type": "KSampler",
            "inputs": {"seed": 42, "steps": 20},
        },
        "4": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["3", 0]},
        },
    }


@pytest.fixture
def tmp_cache_dir(tmp_path):
    """Isolated temporary cache directory."""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    return cache_dir
