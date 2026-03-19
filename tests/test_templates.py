"""Tests for template fetch, search, and detail (TMPL-01, TMPL-02)."""

from unittest.mock import MagicMock, patch

import pytest

from src.templates.fetch import (
    extract_node_types,
    fetch_template_index,
    flatten_templates,
    get_template_detail,
)
from src.templates.models import Template, TemplateCategory
from src.templates.search import search_templates


# --- Fetch Tests ---


@patch("src.templates.fetch._cache")
@patch("src.templates.fetch.get_github_client")
def test_fetch_template_index_caches(mock_get_client, mock_cache, sample_index_data):
    """Cache hit should skip HTTP call."""
    mock_cache.get.return_value = sample_index_data
    result = fetch_template_index()
    assert len(result) == 2
    assert isinstance(result[0], TemplateCategory)
    mock_get_client.assert_not_called()


@patch("src.templates.fetch._cache")
@patch("src.templates.fetch.get_github_client")
def test_fetch_template_index_parses_nested_structure(
    mock_get_client, mock_cache, sample_index_data
):
    """Fetched data should parse into nested TemplateCategory objects."""
    mock_cache.get.return_value = None

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = sample_index_data

    mock_client = MagicMock()
    mock_client.get.return_value = mock_response
    mock_get_client.return_value = mock_client

    result = fetch_template_index()
    assert len(result) == 2
    assert result[0].category == "image"
    assert len(result[0].templates) == 2
    assert result[1].category == "video"
    assert len(result[1].templates) == 2
    mock_cache.set.assert_called_once()


def test_extract_node_types_standard_workflow(sample_template_workflow_json):
    """Standard workflow extracts class_types from top-level nodes."""
    types = extract_node_types(sample_template_workflow_json)
    assert types == {"KSampler", "CLIPTextEncode", "SaveImage"}


def test_extract_node_types_subgraph_workflow(sample_workflow_with_subgraphs):
    """Subgraph workflow extracts from definitions, filters UUIDs."""
    types = extract_node_types(sample_workflow_with_subgraphs)
    assert "KSampler" in types
    assert "VAEDecode" in types
    assert "SaveImage" in types
    # UUIDs should be filtered out
    assert "ef10a538-17cf-46fb-930c-5460c4cf7f0e" not in types
    assert "aaaa1111-bbbb-cccc-dddd-eeee2222ffff" not in types


def test_extract_node_types_empty():
    """Empty workflow returns empty set."""
    assert extract_node_types({}) == set()
    assert extract_node_types({"nodes": []}) == set()


@patch("src.templates.fetch.fetch_workflow_json")
@patch("src.templates.fetch.fetch_template_index")
def test_get_template_detail_returns_merged_data(
    mock_index, mock_workflow, sample_index_data, sample_template_workflow_json
):
    """Detail should contain both metadata and extracted node types."""
    mock_index.return_value = [TemplateCategory(**c) for c in sample_index_data]
    mock_workflow.return_value = sample_template_workflow_json

    detail = get_template_detail("flux-schnell-basic")
    assert detail is not None
    assert detail["name"] == "flux-schnell-basic"
    assert detail["title"] == "Flux Schnell Basic"
    assert detail["tags"] == ["flux", "image", "fast"]
    assert detail["models"] == ["flux-schnell"]
    assert detail["category"] == "image"
    assert "KSampler" in detail["node_types"]
    assert detail["node_count"] == 3


@patch("src.templates.fetch.fetch_template_index")
def test_get_template_detail_not_found(mock_index, sample_index_data):
    """Unknown template name returns None."""
    mock_index.return_value = [TemplateCategory(**c) for c in sample_index_data]
    assert get_template_detail("nonexistent-template") is None


@patch("src.templates.fetch.fetch_workflow_json")
@patch("src.templates.fetch.fetch_template_index")
def test_get_template_detail_no_workflow(
    mock_index, mock_workflow, sample_index_data
):
    """Template exists but workflow fetch fails -- returns detail with empty node_types."""
    mock_index.return_value = [TemplateCategory(**c) for c in sample_index_data]
    mock_workflow.return_value = None

    detail = get_template_detail("flux-schnell-basic")
    assert detail is not None
    assert detail["name"] == "flux-schnell-basic"
    assert detail["node_types"] == []
    assert detail["node_count"] == 0


# --- Flatten Tests ---


def test_flatten_templates(sample_index_data):
    """Flatten produces correct count across categories."""
    categories = [TemplateCategory(**c) for c in sample_index_data]
    flat = flatten_templates(categories)
    assert len(flat) == 4
    assert all(isinstance(t, Template) for t in flat)


# --- Search Tests ---


@patch("src.templates.search.fetch_template_index")
def test_search_by_title(mock_index, sample_index_data):
    """Query matching title scores highest."""
    mock_index.return_value = [TemplateCategory(**c) for c in sample_index_data]
    results = search_templates("Flux")
    assert len(results) >= 1
    assert results[0].name == "flux-schnell-basic"


@patch("src.templates.search.fetch_template_index")
def test_search_by_tag(mock_index, sample_index_data):
    """Query matching tag returns results."""
    mock_index.return_value = [TemplateCategory(**c) for c in sample_index_data]
    results = search_templates("controlnet")
    assert any(t.name == "sdxl-upscale" for t in results)


@patch("src.templates.search.fetch_template_index")
def test_search_by_model(mock_index, sample_index_data):
    """Query with model filter narrows results."""
    mock_index.return_value = [TemplateCategory(**c) for c in sample_index_data]
    results = search_templates("video", model="wan")
    assert len(results) >= 1
    assert results[0].name == "wan-t2v-basic"


@patch("src.templates.search.fetch_template_index")
def test_search_by_media_type(mock_index, sample_index_data):
    """media_type filter restricts to matching type."""
    mock_index.return_value = [TemplateCategory(**c) for c in sample_index_data]
    results = search_templates("image", media_type="video")
    # "image" appears in tags/description of image templates but they are filtered out
    assert all(t.mediaType == "video" for t in results)


@patch("src.templates.search.fetch_template_index")
def test_search_no_results(mock_index, sample_index_data):
    """Non-matching query returns empty list."""
    mock_index.return_value = [TemplateCategory(**c) for c in sample_index_data]
    results = search_templates("xyznonexistent")
    assert results == []
