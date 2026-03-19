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


@pytest.fixture
def sample_index_data() -> list:
    """List of TemplateCategory dicts matching index.json nested structure."""
    return [
        {
            "moduleName": "image_gen",
            "category": "image",
            "icon": "image-icon",
            "title": "Image Generation",
            "type": "category",
            "isEssential": True,
            "templates": [
                {
                    "name": "flux-schnell-basic",
                    "title": "Flux Schnell Basic",
                    "description": "Generate images with Flux Schnell model",
                    "mediaType": "image",
                    "mediaSubtype": "",
                    "tags": ["flux", "image", "fast"],
                    "models": ["flux-schnell"],
                    "requiresCustomNodes": ["comfyui-flux-pack"],
                    "date": "2025-06-01",
                    "openSource": True,
                    "size": 12,
                    "vram": 8,
                    "usage": 5000,
                    "searchRank": 1,
                    "username": "comfy",
                    "io": {"inputs": [], "outputs": []},
                    "thumbnail": [],
                },
                {
                    "name": "sdxl-upscale",
                    "title": "SDXL Upscale Pipeline",
                    "description": "Upscale images using SDXL and ControlNet",
                    "mediaType": "image",
                    "tags": ["sdxl", "upscale", "controlnet"],
                    "models": ["sdxl-base-1.0", "controlnet-tile"],
                    "requiresCustomNodes": ["comfyui-controlnet-aux"],
                    "date": "2025-07-15",
                    "usage": 3000,
                    "username": "artist",
                    "io": {"inputs": [], "outputs": []},
                    "thumbnail": [],
                },
            ],
        },
        {
            "moduleName": "video_gen",
            "category": "video",
            "icon": "video-icon",
            "title": "Video Generation",
            "type": "category",
            "isEssential": False,
            "templates": [
                {
                    "name": "wan-t2v-basic",
                    "title": "Wan Text to Video",
                    "description": "Generate videos from text using Wan 2.1",
                    "mediaType": "video",
                    "tags": ["wan", "video", "t2v"],
                    "models": ["wan-2.1-t2v-14b"],
                    "requiresCustomNodes": ["comfyui-flux-pack"],
                    "date": "2026-01-10",
                    "usage": 8000,
                    "username": "comfy",
                    "io": {"inputs": [], "outputs": []},
                    "thumbnail": [],
                },
                {
                    "name": "hunyuan-i2v.app",
                    "title": "HunyuanVideo Image to Video",
                    "description": "Convert images to video with HunyuanVideo",
                    "mediaType": "video",
                    "tags": ["hunyuan", "video", "i2v"],
                    "models": ["hunyuan-video"],
                    "requiresCustomNodes": [],
                    "date": "2026-02-20",
                    "usage": 2000,
                    "username": "researcher",
                    "io": {"inputs": [], "outputs": []},
                    "thumbnail": [],
                },
            ],
        },
    ]


@pytest.fixture
def sample_template_workflow_json() -> dict:
    """Workflow dict with standard top-level nodes (no subgraphs)."""
    return {
        "nodes": [
            {"id": 1, "type": "KSampler", "pos": [100, 200]},
            {"id": 2, "type": "CLIPTextEncode", "pos": [200, 200]},
            {"id": 3, "type": "SaveImage", "pos": [300, 200]},
        ],
        "links": [],
    }


@pytest.fixture
def sample_workflow_with_subgraphs() -> dict:
    """Workflow dict with UUID subgraph references and definitions."""
    return {
        "nodes": [
            {"id": 1, "type": "SaveImage", "pos": [500, 200]},
            {
                "id": 2,
                "type": "ef10a538-17cf-46fb-930c-5460c4cf7f0e",
                "pos": [100, 200],
            },
        ],
        "links": [],
        "definitions": {
            "subgraphs": [
                {
                    "id": "ef10a538-17cf-46fb-930c-5460c4cf7f0e",
                    "nodes": [
                        {"id": 10, "type": "KSampler", "pos": [50, 50]},
                        {"id": 11, "type": "VAEDecode", "pos": [150, 50]},
                        {
                            "id": 12,
                            "type": "aaaa1111-bbbb-cccc-dddd-eeee2222ffff",
                            "pos": [250, 50],
                        },
                    ],
                }
            ]
        },
    }
