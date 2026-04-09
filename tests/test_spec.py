"""Tests for src.registry.spec — node pack inspection, caching, formatting."""

from unittest.mock import MagicMock, patch

from src.registry.models import ComfyNode
from src.registry.spec import format_pack_detail, get_pack_nodes


def _comfy_node_data(**overrides) -> dict:
    base = {
        "comfy_node_name": "KSampler",
        "category": "sampling",
        "input_types": '{"required": {"model": ["MODEL"], "seed": ["INT"]}}',
        "return_types": '["IMAGE"]',
        "return_names": "",
        "deprecated": False,
        "experimental": False,
    }
    base.update(overrides)
    return base


@patch("src.registry.spec._cache")
@patch("src.registry.spec.get_client")
@patch("src.registry.spec.fetch_json")
def test_get_pack_nodes_basic(mock_fetch, mock_client, mock_cache):
    mock_cache.get.return_value = None
    mock_client.return_value = MagicMock()
    mock_fetch.return_value = {
        "comfy_nodes": [_comfy_node_data(), _comfy_node_data(comfy_node_name="VAEDecode")],
        "total": 2,
    }
    result = get_pack_nodes("test-pack")
    assert len(result) == 2
    assert all(isinstance(n, ComfyNode) for n in result)


@patch("src.registry.spec._cache")
@patch("src.registry.spec.get_client")
def test_get_pack_nodes_caches(mock_client, mock_cache):
    mock_cache.get.return_value = [_comfy_node_data()]
    result = get_pack_nodes("test-pack")
    assert len(result) == 1
    mock_client.assert_not_called()


@patch("src.registry.spec._cache")
@patch("src.registry.spec.get_client")
@patch("src.registry.spec.fetch_json")
def test_get_pack_nodes_pagination(mock_fetch, mock_client, mock_cache):
    mock_cache.get.return_value = None
    mock_client.return_value = MagicMock()
    # First page returns 2 of 3, second page returns the rest
    mock_fetch.side_effect = [
        {
            "comfy_nodes": [_comfy_node_data(comfy_node_name="A"), _comfy_node_data(comfy_node_name="B")],
            "total": 3,
        },
        {
            "comfy_nodes": [_comfy_node_data(comfy_node_name="C")],
            "total": 3,
        },
    ]
    result = get_pack_nodes("big-pack", limit=2)
    assert len(result) == 3


def test_format_pack_detail_summary():
    nodes = [
        ComfyNode(**_comfy_node_data(comfy_node_name="KSampler", category="sampling")),
        ComfyNode(**_comfy_node_data(comfy_node_name="VAEDecode", category="latent")),
    ]
    output = format_pack_detail("test-pack", nodes, summary=True)
    assert "test-pack" in output
    assert "2 nodes" in output
    assert "KSampler" in output
    assert "VAEDecode" in output


def test_format_pack_detail_full():
    nodes = [
        ComfyNode(**_comfy_node_data(
            comfy_node_name="KSampler",
            input_types='{"required": {"model": ["MODEL"], "seed": ["INT"]}}',
            return_types='["IMAGE"]',
        )),
    ]
    output = format_pack_detail("test-pack", nodes, summary=False)
    assert "KSampler" in output
    assert "MODEL" in output
    assert "IMAGE" in output


def test_format_pack_detail_empty():
    output = format_pack_detail("empty-pack", [], summary=True)
    assert "No nodes found" in output


def test_comfy_node_io_parsing():
    node = ComfyNode(**_comfy_node_data(
        input_types='{"required": {"image": ["IMAGE"], "mask": ["MASK"]}}',
        return_types='["IMAGE", "MASK"]',
    ))
    inputs = node.parsed_input_types()
    assert "required" in inputs
    assert "image" in inputs["required"]
    returns = node.parsed_return_types()
    assert "IMAGE" in returns
    assert "MASK" in returns


def test_comfy_node_empty_io():
    node = ComfyNode(**_comfy_node_data(input_types="", return_types=""))
    assert node.parsed_input_types() == {}
    assert node.parsed_return_types() == []
