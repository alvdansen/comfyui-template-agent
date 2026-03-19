"""Tests for src.registry.highlights — discovery modes, scoring, caching, formatting."""

import math
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest

from src.registry.highlights import (
    _days_since,
    _score_rising,
    _score_trending,
    fetch_all_nodes,
    format_results,
    get_highlights,
)
from src.registry.models import NodePack


def _make_node(**overrides) -> dict:
    """Build a node dict with sensible defaults."""
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


def _make_node_pack(**overrides) -> NodePack:
    return NodePack(**_make_node(**overrides))


def _recent_iso(days_ago: int) -> str:
    dt = datetime.now(timezone.utc) - timedelta(days=days_ago)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


# --- _days_since ---

def test_days_since_valid_date():
    iso = _recent_iso(10)
    assert _days_since(iso) == 10


def test_days_since_invalid_date():
    assert _days_since("not-a-date") == 365


def test_days_since_minimum_one():
    # Today should return 1 (clamped)
    iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    assert _days_since(iso) >= 1


# --- _score_trending ---

def test_score_trending_higher_for_newer_popular():
    old = _make_node_pack(created_at=_recent_iso(300), downloads=5000)
    new = _make_node_pack(created_at=_recent_iso(30), downloads=5000)
    assert _score_trending(new) > _score_trending(old)


def test_score_trending_higher_for_more_stars():
    low_stars = _make_node_pack(github_stars=10, created_at=_recent_iso(60), downloads=1000)
    high_stars = _make_node_pack(github_stars=1000, created_at=_recent_iso(60), downloads=1000)
    assert _score_trending(high_stars) > _score_trending(low_stars)


def test_score_trending_positive():
    node = _make_node_pack(downloads=100, github_stars=5, created_at=_recent_iso(30))
    assert _score_trending(node) > 0


# --- _score_rising ---

def test_score_rising_zero_for_old_nodes():
    old = _make_node_pack(created_at=_recent_iso(100), downloads=5000)
    assert _score_rising(old) == 0


def test_score_rising_positive_for_new_nodes():
    new = _make_node_pack(created_at=_recent_iso(30), downloads=500)
    assert _score_rising(new) > 0


def test_score_rising_higher_for_newer():
    newer = _make_node_pack(created_at=_recent_iso(10), downloads=500)
    older = _make_node_pack(created_at=_recent_iso(80), downloads=500)
    assert _score_rising(newer) > _score_rising(older)


# --- fetch_all_nodes ---

@patch("src.registry.highlights._cache")
@patch("src.registry.highlights.get_client")
@patch("src.registry.highlights.fetch_json")
def test_fetch_all_nodes_returns_node_packs(mock_fetch, mock_client, mock_cache):
    mock_cache.get.return_value = None
    mock_client.return_value = MagicMock()
    mock_fetch.return_value = {
        "nodes": [_make_node(), _make_node(id="node-2", name="Node 2")]
    }
    result = fetch_all_nodes(pages=1)
    assert len(result) == 2
    assert all(isinstance(n, NodePack) for n in result)


@patch("src.registry.highlights._cache")
@patch("src.registry.highlights.get_client")
@patch("src.registry.highlights.fetch_json")
def test_fetch_all_nodes_filters_inactive(mock_fetch, mock_client, mock_cache):
    mock_cache.get.return_value = None
    mock_client.return_value = MagicMock()
    mock_fetch.return_value = {
        "nodes": [
            _make_node(status="NodeStatusActive"),
            _make_node(id="banned", status="NodeStatusBanned"),
        ]
    }
    result = fetch_all_nodes(pages=1)
    assert len(result) == 1
    assert result[0].id == "test-node"


@patch("src.registry.highlights._cache")
@patch("src.registry.highlights.get_client")
def test_fetch_all_nodes_caches(mock_client, mock_cache):
    mock_cache.get.return_value = [_make_node()]
    result = fetch_all_nodes()
    assert len(result) == 1
    mock_client.assert_not_called()


# --- get_highlights ---

@patch("src.registry.highlights.fetch_all_nodes")
def test_get_highlights_trending(mock_fetch):
    nodes = [
        _make_node_pack(id="hot", downloads=10000, github_stars=500, created_at=_recent_iso(10)),
        _make_node_pack(id="cold", downloads=100, github_stars=2, created_at=_recent_iso(300)),
    ]
    mock_fetch.return_value = nodes
    result = get_highlights(mode="trending", limit=2)
    assert result[0].id == "hot"


@patch("src.registry.highlights.fetch_all_nodes")
def test_get_highlights_new(mock_fetch):
    nodes = [
        _make_node_pack(id="recent", created_at=_recent_iso(5), downloads=10),
        _make_node_pack(id="old", created_at=_recent_iso(200), downloads=5000),
    ]
    mock_fetch.return_value = nodes
    result = get_highlights(mode="new", limit=10)
    assert result[0].id == "recent"


@patch("src.registry.highlights.fetch_all_nodes")
def test_get_highlights_new_fallback(mock_fetch):
    """If no nodes in last 14 days, fallback to most recent."""
    nodes = [
        _make_node_pack(id="older", created_at=_recent_iso(60), downloads=100),
        _make_node_pack(id="oldest", created_at=_recent_iso(200), downloads=50),
    ]
    mock_fetch.return_value = nodes
    result = get_highlights(mode="new", limit=10)
    assert len(result) > 0
    assert result[0].id == "older"


@patch("src.registry.highlights.fetch_all_nodes")
def test_get_highlights_popular(mock_fetch):
    nodes = [
        _make_node_pack(id="pop", downloads=999999),
        _make_node_pack(id="niche", downloads=10),
    ]
    mock_fetch.return_value = nodes
    result = get_highlights(mode="popular", limit=2)
    assert result[0].id == "pop"
    assert result[0].downloads > result[1].downloads


@patch("src.registry.highlights.fetch_all_nodes")
def test_get_highlights_rising(mock_fetch):
    nodes = [
        _make_node_pack(id="rocket", created_at=_recent_iso(15), downloads=3000),
        _make_node_pack(id="stale", created_at=_recent_iso(200), downloads=50000),
    ]
    mock_fetch.return_value = nodes
    result = get_highlights(mode="rising", limit=10)
    assert all(n.id != "stale" for n in result)
    assert any(n.id == "rocket" for n in result)


@patch("src.registry.highlights.fetch_all_nodes")
def test_get_highlights_random_weighted(mock_fetch):
    high_dl = _make_node_pack(id="big", downloads=100000, github_stars=500)
    low_dl = _make_node_pack(id="tiny", downloads=1, github_stars=0)
    mock_fetch.return_value = [high_dl, low_dl]

    # Over many runs, weighted random should favor high-download nodes
    big_count = 0
    for _ in range(100):
        result = get_highlights(mode="random", limit=1)
        if result and result[0].id == "big":
            big_count += 1

    assert big_count > 60  # Should appear much more often than 50%


@patch("src.registry.highlights.fetch_all_nodes")
def test_get_highlights_random_truly(mock_fetch):
    nodes = [_make_node_pack(id=f"n{i}", downloads=i) for i in range(20)]
    mock_fetch.return_value = nodes
    result = get_highlights(mode="random", limit=5, truly_random=True)
    assert len(result) == 5
    # All unique
    assert len(set(n.id for n in result)) == 5


@patch("src.registry.highlights.fetch_all_nodes")
def test_get_highlights_unknown_mode(mock_fetch):
    mock_fetch.return_value = [_make_node_pack()]
    with pytest.raises(ValueError, match="Unknown mode"):
        get_highlights(mode="invalid")


@patch("src.registry.highlights.fetch_all_nodes")
def test_get_highlights_with_category_filter(mock_fetch):
    video_node = _make_node_pack(id="vid", name="Video Upscaler", description="video processing")
    audio_node = _make_node_pack(id="aud", name="Audio Gen", description="audio synthesis")
    mock_fetch.return_value = [video_node, audio_node]
    result = get_highlights(mode="trending", category="video")
    assert all("vid" == n.id for n in result)


@patch("src.registry.highlights.fetch_all_nodes")
def test_get_highlights_empty_nodes(mock_fetch):
    mock_fetch.return_value = []
    result = get_highlights(mode="trending")
    assert result == []


# --- format_results ---

def test_format_results_includes_fields():
    nodes = [_make_node_pack(name="Cool Node", author="dev", downloads=5000)]
    output = format_results(nodes, "trending")
    assert "Cool Node" in output
    assert "dev" in output
    assert "5,000" in output
    assert "Trending" in output


def test_format_results_empty():
    output = format_results([], "trending")
    assert "No trending" in output
