"""Tests for shared infrastructure: HTTP client, cache, format detector, categories, models."""

from unittest.mock import MagicMock, patch

import httpx
import pytest

from src.shared.cache import DiskCache
from src.shared.categories import CATEGORY_KEYWORDS, classify_node
from src.shared.config import BASE_URL, CACHE_TTLS
from src.shared.format_detector import detect_format
from src.shared.http import fetch_json, get_client
from src.registry.models import ComfyNode, ComfyNodeResult, NodePack, SearchResult


# --- HTTP Client Tests ---


def test_get_client_returns_httpx_client():
    client = get_client()
    assert isinstance(client, httpx.Client)
    assert str(client.base_url).rstrip("/") == BASE_URL
    client.close()


def test_fetch_json_returns_parsed_json():
    mock_response = MagicMock()
    mock_response.json.return_value = {"nodes": [], "total": 0}
    mock_response.raise_for_status = MagicMock()

    mock_client = MagicMock()
    mock_client.get.return_value = mock_response

    result = fetch_json(mock_client, "/nodes")
    assert result == {"nodes": [], "total": 0}
    mock_client.get.assert_called_once_with("/nodes", params=None)


def test_fetch_json_raises_on_http_error():
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Server Error",
        request=MagicMock(),
        response=MagicMock(status_code=500),
    )

    mock_client = MagicMock()
    mock_client.get.return_value = mock_response

    with pytest.raises(httpx.HTTPStatusError):
        fetch_json(mock_client, "/nodes")


# --- Cache Tests ---


def test_cache_set_and_get(tmp_cache_dir):
    cache = DiskCache(cache_dir=tmp_cache_dir)
    cache.set("test_key", {"hello": "world"})
    result = cache.get("test_key", ttl=3600)
    assert result == {"hello": "world"}


def test_cache_expired(tmp_cache_dir):
    cache = DiskCache(cache_dir=tmp_cache_dir)
    cache.set("test_key", {"hello": "world"})
    result = cache.get("test_key", ttl=0)
    assert result is None


def test_cache_miss(tmp_cache_dir):
    cache = DiskCache(cache_dir=tmp_cache_dir)
    result = cache.get("nonexistent", ttl=3600)
    assert result is None


def test_cache_clear_specific(tmp_cache_dir):
    cache = DiskCache(cache_dir=tmp_cache_dir)
    cache.set("key_a", {"a": 1})
    cache.set("key_b", {"b": 2})
    cache.clear("key_a")
    assert cache.get("key_a", ttl=3600) is None
    assert cache.get("key_b", ttl=3600) == {"b": 2}


def test_cache_clear_all(tmp_cache_dir):
    cache = DiskCache(cache_dir=tmp_cache_dir)
    cache.set("key_a", {"a": 1})
    cache.set("key_b", {"b": 2})
    cache.clear()
    assert cache.get("key_a", ttl=3600) is None
    assert cache.get("key_b", ttl=3600) is None


# --- Format Detector Tests ---


def test_detect_workflow_format(sample_workflow_json):
    assert detect_format(sample_workflow_json) == "workflow"


def test_detect_api_format(sample_api_json):
    assert detect_format(sample_api_json) == "api"


def test_detect_unknown_format():
    assert detect_format({}) == "unknown"
    assert detect_format({"something": "else"}) == "unknown"


# --- Category Tests ---


def test_classify_video_node():
    result = classify_node("AnimateDiff", "animation tool")
    assert "video" in result


def test_classify_image_node():
    result = classify_node("KSampler", "image denoising")
    assert "image" in result


def test_classify_audio_node():
    result = classify_node("AudioGen", "audio generation")
    assert "audio" in result


def test_classify_3d_node():
    result = classify_node("Mesh3D", "3d mesh processing")
    assert "3d" in result


def test_classify_utility_fallback():
    result = classify_node("SomeUtil", "does stuff")
    assert result == ["utility"]


def test_classify_multi_category():
    result = classify_node("VideoImageProcessor", "video and image frame tool")
    assert "video" in result
    assert "image" in result


def test_category_keywords_has_expected_keys():
    assert set(CATEGORY_KEYWORDS.keys()) == {"video", "image", "audio", "3d"}


# --- Pydantic Model Tests ---


def test_node_pack_from_api_data(sample_node_pack_data):
    pack = NodePack(**sample_node_pack_data)
    assert pack.id == "comfyui-impact-pack"
    assert pack.name == "Impact Pack"
    assert pack.author == "Dr.Lt.Data"
    assert pack.downloads == 250000
    assert pack.github_stars == 1500
    assert pack.rating == 4.8
    assert pack.status == "NodeStatusActive"
    assert pack.tags == []


def test_comfy_node_parsed_input_types(sample_comfy_node_data):
    node = ComfyNode(**sample_comfy_node_data)
    inputs = node.parsed_input_types()
    assert isinstance(inputs, dict)
    assert "required" in inputs
    assert "image" in inputs["required"]


def test_comfy_node_parsed_return_types(sample_comfy_node_data):
    node = ComfyNode(**sample_comfy_node_data)
    returns = node.parsed_return_types()
    assert isinstance(returns, list)
    assert "IMAGE" in returns


def test_comfy_node_empty_input_types():
    node = ComfyNode(comfy_node_name="Test")
    assert node.parsed_input_types() == {}
    assert node.parsed_return_types() == []


def test_search_result_from_api_data(sample_search_result):
    result = SearchResult(**sample_search_result)
    assert len(result.nodes) == 1
    assert result.total == 1
    assert result.page == 1
    assert result.limit == 50
    assert result.totalPages == 1
    assert result.nodes[0].id == "comfyui-impact-pack"


def test_comfy_node_result():
    data = {
        "comfy_nodes": [
            {"comfy_node_name": "KSampler", "category": "sampling"},
        ],
        "total": 1,
    }
    result = ComfyNodeResult(**data)
    assert len(result.comfy_nodes) == 1
    assert result.comfy_nodes[0].comfy_node_name == "KSampler"
    assert result.total == 1
