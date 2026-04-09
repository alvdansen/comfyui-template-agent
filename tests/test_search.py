"""Tests for src.registry.search — name search, type search, formatting."""

from unittest.mock import MagicMock, patch

from src.registry.models import NodePack
from src.registry.search import format_search_results, search_by_type, search_nodes


def _make_node(**overrides) -> dict:
    base = {
        "id": "test-node",
        "name": "Test Node",
        "author": "tester",
        "description": "A test node",
        "downloads": 1000,
        "github_stars": 50,
        "rating": 4.0,
        "created_at": "2025-06-01T00:00:00Z",
        "repository": "https://github.com/test/test-node",
        "tags": [],
        "status": "NodeStatusActive",
        "icon": "",
    }
    base.update(overrides)
    return base


def _search_response(*nodes):
    return {
        "nodes": list(nodes),
        "total": len(nodes),
        "page": 1,
        "limit": 50,
        "totalPages": 1,
    }


@patch("src.registry.search._cache")
@patch("src.registry.search.get_client")
@patch("src.registry.search.fetch_json")
def test_search_nodes_basic(mock_fetch, mock_client, mock_cache):
    mock_cache.get.return_value = None
    mock_client.return_value = MagicMock()
    mock_fetch.return_value = _search_response(_make_node(), _make_node(id="n2", name="N2"))
    result = search_nodes("test")
    assert len(result) == 2
    assert all(isinstance(n, NodePack) for n in result)


@patch("src.registry.search._cache")
@patch("src.registry.search.get_client")
def test_search_nodes_caches(mock_client, mock_cache):
    mock_cache.get.return_value = [_make_node()]
    result = search_nodes("test")
    assert len(result) == 1
    mock_client.assert_not_called()


@patch("src.registry.search._cache")
@patch("src.registry.search.get_client")
@patch("src.registry.search.fetch_json")
def test_search_nodes_with_category(mock_fetch, mock_client, mock_cache):
    mock_cache.get.return_value = None
    mock_client.return_value = MagicMock()
    mock_fetch.return_value = _search_response(
        _make_node(id="vid", name="Video Tool", description="video processing"),
        _make_node(id="txt", name="Text Tool", description="text processing"),
    )
    result = search_nodes("tool", category="video")
    assert len(result) == 1
    assert result[0].id == "vid"


@patch("src.registry.search._cache")
@patch("src.registry.search.get_client")
@patch("src.registry.search.fetch_json")
def test_search_nodes_empty_results(mock_fetch, mock_client, mock_cache):
    mock_cache.get.return_value = None
    mock_client.return_value = MagicMock()
    mock_fetch.return_value = _search_response()
    result = search_nodes("nonexistent")
    assert result == []


@patch("src.registry.search._cache")
@patch("src.registry.search.get_client")
@patch("src.registry.search.fetch_json")
def test_search_by_type_finds_matching(mock_fetch, mock_client, mock_cache):
    mock_cache.get.return_value = None
    mock_client.return_value = MagicMock()

    # First call: search_nodes via /nodes
    # Second call: /comfy-nodes for the pack
    mock_fetch.side_effect = [
        _search_response(_make_node(id="pack1")),
        {
            "comfy_nodes": [
                {
                    "comfy_node_name": "MyNode",
                    "category": "image",
                    "input_types": '{"required": {"image": ["IMAGE"]}}',
                    "return_types": '["MASK"]',
                    "return_names": "",
                    "deprecated": False,
                    "experimental": False,
                },
            ],
            "total": 1,
        },
    ]
    result = search_by_type(output_type="MASK")
    assert len(result) == 1
    assert result[0]["matching_nodes"][0].comfy_node_name == "MyNode"


def test_search_by_type_no_query():
    result = search_by_type()
    assert result == []


def test_format_search_results():
    nodes = [NodePack(**_make_node(name="Upscale Pro", author="dev"))]
    output = format_search_results(nodes, "upscale")
    assert "Upscale Pro" in output
    assert "dev" in output
    assert "upscale" in output


def test_format_search_results_empty():
    output = format_search_results([], "nothing")
    assert "No results" in output
