"""Tests for template cross-reference module (TMPL-03)."""

from unittest.mock import patch

import pytest

from src.templates.cross_ref import (
    build_pack_index,
    cross_reference,
    format_cross_reference,
)
from src.templates.models import TemplateCategory, TemplateSummary


def test_build_pack_index(sample_index_data):
    """Pack index maps pack IDs to template summaries."""
    categories = [TemplateCategory(**c) for c in sample_index_data]
    index = build_pack_index(categories)

    assert "comfyui-flux-pack" in index
    # flux-schnell-basic and wan-t2v-basic both require comfyui-flux-pack
    assert len(index["comfyui-flux-pack"]) == 2
    assert all(isinstance(s, TemplateSummary) for s in index["comfyui-flux-pack"])

    assert "comfyui-controlnet-aux" in index
    assert len(index["comfyui-controlnet-aux"]) == 1


def test_build_pack_index_empty_custom_nodes(sample_index_data):
    """Templates with no requiresCustomNodes don't appear in pack index."""
    categories = [TemplateCategory(**c) for c in sample_index_data]
    index = build_pack_index(categories)

    # hunyuan-i2v.app has empty requiresCustomNodes
    all_names = [s.name for summaries in index.values() for s in summaries]
    assert "hunyuan-i2v.app" not in all_names


@patch("src.templates.cross_ref.fetch_template_index")
def test_cross_reference_pack_level(mock_index, sample_index_data):
    """Pack query returns count + top examples."""
    mock_index.return_value = [TemplateCategory(**c) for c in sample_index_data]
    result = cross_reference("comfyui-flux-pack", level="pack")

    assert result["query"] == "comfyui-flux-pack"
    assert result["level"] == "pack"
    assert result["total_count"] == 2
    assert len(result["exact_matches"]) == 2
    assert len(result["top_examples"]) == 2
    assert result["fuzzy_matches"] == []


@patch("src.templates.cross_ref.fetch_template_index")
def test_cross_reference_fuzzy_match(mock_index, sample_index_data):
    """Partial name matches related packs via fuzzy matching."""
    mock_index.return_value = [TemplateCategory(**c) for c in sample_index_data]
    result = cross_reference("flux", level="pack")

    # "flux" should fuzzy-match "comfyui-flux-pack"
    assert result["exact_matches"] == []
    assert len(result["fuzzy_matches"]) >= 1
    assert result["total_count"] >= 1


@patch("src.templates.cross_ref.fetch_template_index")
def test_format_cross_reference(mock_index, sample_index_data):
    """Formatted output contains count and example names."""
    mock_index.return_value = [TemplateCategory(**c) for c in sample_index_data]
    result = cross_reference("comfyui-flux-pack", level="pack")
    formatted = format_cross_reference(result)

    assert "2 template(s)" in formatted
    assert "comfyui-flux-pack" in formatted


@patch("src.templates.cross_ref.fetch_template_index")
def test_cross_reference_no_match(mock_index, sample_index_data):
    """Unknown query returns 0 count."""
    mock_index.return_value = [TemplateCategory(**c) for c in sample_index_data]
    result = cross_reference("totally-unknown-pack-xyz", level="pack")

    assert result["total_count"] == 0
    assert result["exact_matches"] == []
    assert result["fuzzy_matches"] == []
