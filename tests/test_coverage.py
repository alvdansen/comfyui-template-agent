"""Tests for gap analysis and coverage reporting (TMPL-04, TMPL-05)."""

from unittest.mock import patch

import pytest

from src.registry.models import NodePack
from src.templates.coverage import (
    coverage_report,
    format_coverage_report,
    format_gap_analysis,
    gap_analysis,
    score_gap_opportunity,
    suggest_template_idea,
)
from src.templates.models import TemplateCategory


# --- Test fixtures ---


def _make_pack(
    id: str,
    name: str,
    downloads: int = 1000,
    stars: int = 50,
    description: str = "",
) -> NodePack:
    return NodePack(
        id=id,
        name=name,
        description=description,
        downloads=downloads,
        github_stars=stars,
    )


@pytest.fixture
def mock_node_packs() -> list[NodePack]:
    """5 packs: 2 covered by templates, 3 not (gaps)."""
    return [
        _make_pack("comfyui-flux-pack", "Flux Pack", 50000, 200, "Flux image generation"),
        _make_pack("comfyui-controlnet-aux", "ControlNet Aux", 30000, 150, "ControlNet utilities"),
        _make_pack("comfyui-video-helper", "Video Helper", 20000, 80, "Video animation tools"),
        _make_pack("comfyui-audio-gen", "Audio Gen", 5000, 20, "Audio speech generation with tts"),
        _make_pack("comfyui-misc-utils", "Misc Utils", 1000, 5, "Miscellaneous utilities"),
    ]


@pytest.fixture
def mock_template_categories() -> list[TemplateCategory]:
    """2 categories with templates referencing flux-pack and controlnet-aux."""
    return [
        TemplateCategory(
            moduleName="image_gen",
            category="image",
            title="Image Generation",
            type="category",
            templates=[
                {
                    "name": "flux-basic",
                    "title": "Flux Basic",
                    "mediaType": "image",
                    "tags": ["flux"],
                    "models": [],
                    "requiresCustomNodes": ["comfyui-flux-pack"],
                    "date": "2026-01-15",
                    "usage": 5000,
                },
                {
                    "name": "sdxl-upscale",
                    "title": "SDXL Upscale",
                    "mediaType": "image",
                    "tags": ["upscale"],
                    "models": [],
                    "requiresCustomNodes": ["comfyui-controlnet-aux"],
                    "date": "2026-02-10",
                    "usage": 3000,
                },
            ],
        ),
        TemplateCategory(
            moduleName="video_gen",
            category="video",
            title="Video Generation",
            type="category",
            templates=[
                {
                    "name": "wan-t2v",
                    "title": "Wan T2V",
                    "mediaType": "video",
                    "tags": ["wan", "video"],
                    "models": [],
                    "requiresCustomNodes": ["comfyui-flux-pack"],
                    "date": "2025-12-05",
                    "usage": 8000,
                },
            ],
        ),
    ]


# --- Gap Scoring Tests (TMPL-04) ---


def test_score_gap_opportunity_no_template():
    """Pack with 0 templates should get a positive score."""
    pack = _make_pack("test", "Test", downloads=10000, stars=100)
    score = score_gap_opportunity(pack, template_count=0)
    assert score > 0


def test_score_gap_opportunity_has_template():
    """Pack with templates should score 0."""
    pack = _make_pack("test", "Test", downloads=10000, stars=100)
    score = score_gap_opportunity(pack, template_count=1)
    assert score == 0.0


def test_score_gap_opportunity_higher_downloads_higher_score():
    """More popular pack should score higher than less popular one."""
    popular = _make_pack("pop", "Popular", downloads=100000, stars=500)
    niche = _make_pack("niche", "Niche", downloads=100, stars=5)
    score_pop = score_gap_opportunity(popular, 0)
    score_niche = score_gap_opportunity(niche, 0)
    assert score_pop > score_niche


# --- Template Suggestion Tests ---


def test_suggest_template_idea_video():
    """Video-classified pack gets video suggestion."""
    pack = _make_pack("vid-tool", "Video Tool", description="Video animation helper")
    suggestion = suggest_template_idea(pack)
    assert "video" in suggestion.lower() or "img2vid" in suggestion.lower()


def test_suggest_template_idea_utility():
    """Unclassified pack gets utility suggestion."""
    pack = _make_pack("misc-thing", "Misc Thing", description="General purpose tool")
    suggestion = suggest_template_idea(pack)
    assert "utility" in suggestion.lower() or "pipeline" in suggestion.lower()


# --- Gap Analysis Integration Tests ---


@patch("src.templates.coverage.fetch_template_index")
@patch("src.templates.coverage.fetch_all_nodes")
def test_gap_analysis_returns_sorted_gaps(
    mock_fetch_nodes, mock_fetch_templates, mock_node_packs, mock_template_categories
):
    """Gaps should be sorted by score descending."""
    mock_fetch_nodes.return_value = mock_node_packs
    mock_fetch_templates.return_value = mock_template_categories

    result = gap_analysis()
    scores = [g["score"] for g in result["gaps"]]
    assert scores == sorted(scores, reverse=True)
    assert all(s > 0 for s in scores)


@patch("src.templates.coverage.fetch_template_index")
@patch("src.templates.coverage.fetch_all_nodes")
def test_gap_analysis_by_category(
    mock_fetch_nodes, mock_fetch_templates, mock_node_packs, mock_template_categories
):
    """by_category=True should group results by category."""
    mock_fetch_nodes.return_value = mock_node_packs
    mock_fetch_templates.return_value = mock_template_categories

    result = gap_analysis(by_category=True)
    assert "by_category" in result
    assert isinstance(result["by_category"], dict)
    # At least one category should have gaps
    assert len(result["by_category"]) > 0


@patch("src.templates.coverage.fetch_template_index")
@patch("src.templates.coverage.fetch_all_nodes")
def test_gap_analysis_limit(
    mock_fetch_nodes, mock_fetch_templates, mock_node_packs, mock_template_categories
):
    """Limit parameter caps the number of results."""
    mock_fetch_nodes.return_value = mock_node_packs
    mock_fetch_templates.return_value = mock_template_categories

    result = gap_analysis(limit=1)
    assert len(result["gaps"]) <= 1


@patch("src.templates.coverage.fetch_template_index")
@patch("src.templates.coverage.fetch_all_nodes")
def test_gap_analysis_excludes_covered_packs(
    mock_fetch_nodes, mock_fetch_templates, mock_node_packs, mock_template_categories
):
    """Packs that appear in templates should NOT be in gaps."""
    mock_fetch_nodes.return_value = mock_node_packs
    mock_fetch_templates.return_value = mock_template_categories

    result = gap_analysis()
    gap_ids = {g["id"] for g in result["gaps"]}
    # flux-pack and controlnet-aux are in templates
    assert "comfyui-flux-pack" not in gap_ids
    assert "comfyui-controlnet-aux" not in gap_ids
    # video-helper, audio-gen, misc-utils are gaps
    assert "comfyui-video-helper" in gap_ids
    assert "comfyui-audio-gen" in gap_ids
    assert "comfyui-misc-utils" in gap_ids


# --- Coverage Report Tests (TMPL-05) ---


@patch("src.templates.coverage.fetch_all_nodes")
@patch("src.templates.coverage.fetch_template_index")
def test_coverage_report_total_templates(
    mock_fetch_templates, mock_fetch_nodes, mock_template_categories, mock_node_packs
):
    """Total template count should match fixture data."""
    mock_fetch_templates.return_value = mock_template_categories
    mock_fetch_nodes.return_value = mock_node_packs

    result = coverage_report()
    assert result["total_templates"] == 3  # 2 image + 1 video


@patch("src.templates.coverage.fetch_all_nodes")
@patch("src.templates.coverage.fetch_template_index")
def test_coverage_report_by_category(
    mock_fetch_templates, mock_fetch_nodes, mock_template_categories, mock_node_packs
):
    """Category counts should match mediaType distribution."""
    mock_fetch_templates.return_value = mock_template_categories
    mock_fetch_nodes.return_value = mock_node_packs

    result = coverage_report()
    assert result["templates_by_category"]["image"] == 2
    assert result["templates_by_category"]["video"] == 1


@patch("src.templates.coverage.fetch_all_nodes")
@patch("src.templates.coverage.fetch_template_index")
def test_coverage_report_thin_spots(
    mock_fetch_templates, mock_fetch_nodes, mock_template_categories, mock_node_packs
):
    """Categories below average should be flagged as thin spots."""
    mock_fetch_templates.return_value = mock_template_categories
    mock_fetch_nodes.return_value = mock_node_packs

    result = coverage_report()
    # Average is 1.5 (3 templates / 2 categories). Video has 1 < 1.5 = thin
    thin_cats = [s["category"] for s in result["thin_spots"]]
    assert "video" in thin_cats


@patch("src.templates.coverage.fetch_all_nodes")
@patch("src.templates.coverage.fetch_template_index")
def test_coverage_report_growth_trends(
    mock_fetch_templates, mock_fetch_nodes, mock_template_categories, mock_node_packs
):
    """Growth trends should group templates by month."""
    mock_fetch_templates.return_value = mock_template_categories
    mock_fetch_nodes.return_value = mock_node_packs

    result = coverage_report()
    growth = result["growth_by_month"]
    assert isinstance(growth, dict)
    # We have dates: 2026-01, 2026-02, 2025-12
    assert "2026-01" in growth
    assert "2026-02" in growth
    assert "2025-12" in growth


# --- Format Tests ---


@patch("src.templates.coverage.fetch_all_nodes")
@patch("src.templates.coverage.fetch_template_index")
def test_format_coverage_report_contains_metrics(
    mock_fetch_templates, mock_fetch_nodes, mock_template_categories, mock_node_packs
):
    """Formatted output should include all four metric sections."""
    mock_fetch_templates.return_value = mock_template_categories
    mock_fetch_nodes.return_value = mock_node_packs

    result = coverage_report()
    formatted = format_coverage_report(result)
    assert "Template Library:" in formatted
    assert "pack coverage" in formatted
    assert "Templates by Category:" in formatted
    assert "Thin Spots" in formatted
    assert "Growth Trends" in formatted


@patch("src.templates.coverage.fetch_template_index")
@patch("src.templates.coverage.fetch_all_nodes")
def test_format_gap_analysis_contains_suggestions(
    mock_fetch_nodes, mock_fetch_templates, mock_node_packs, mock_template_categories
):
    """Formatted gap analysis should include suggestion text."""
    mock_fetch_nodes.return_value = mock_node_packs
    mock_fetch_templates.return_value = mock_template_categories

    result = gap_analysis()
    formatted = format_gap_analysis(result)
    assert "Gap Analysis:" in formatted
    assert "Suggestion:" in formatted
    assert "Score:" in formatted
