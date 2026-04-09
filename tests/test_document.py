"""Tests for the documentation generation module (DOCS-01 through DOCS-04)."""

import json
import tempfile
from unittest import mock

import pytest

from src.document.metadata import generate_index_entry, extract_io_spec, format_index_entry
from src.document.notion import generate_notion_markdown, thumbnail_reminder
from src.document.models import IndexEntry, IOSpec, IOItem

# -- Inline fixtures --

WORKFLOW_BASIC = {
    "nodes": [
        {"id": 1, "type": "CheckpointLoaderSimple", "widgets_values": ["sd_xl_base_1.0.safetensors"]},
        {"id": 2, "type": "KSampler", "widgets_values": [42, 20, 8.0, "euler", "normal", 1.0]},
        {"id": 3, "type": "VAEDecode"},
        {"id": 4, "type": "SaveImage", "widgets_values": ["ComfyUI"]},
        {"id": 5, "type": "LoadImage", "widgets_values": ["example.png"]},
        {"id": 6, "type": "CLIPTextEncode"},
    ],
    "links": [],
}

WORKFLOW_WITH_CUSTOM = {
    "nodes": [
        {"id": 1, "type": "KSampler"},
        {"id": 2, "type": "SomeCustomNode"},
        {"id": 3, "type": "AnotherCustomNode"},
        {"id": 4, "type": "SaveImage"},
    ],
    "links": [],
}

WORKFLOW_VIDEO = {
    "nodes": [
        {"id": 1, "type": "CheckpointLoaderSimple", "widgets_values": ["wan-2.1-t2v.safetensors"]},
        {"id": 2, "type": "KSampler"},
        {"id": 3, "type": "VHS_VideoCombine", "widgets_values": ["output", 24, 0, "video/h264-mp4"]},
    ],
    "links": [],
}

WORKFLOW_WITH_SUBGRAPH_IO = {
    "nodes": [
        {"id": 1, "type": "ef10a538-17cf-46fb-930c-5460c4cf7f0e"},
    ],
    "links": [],
    "definitions": {
        "subgraphs": [{
            "id": "ef10a538-17cf-46fb-930c-5460c4cf7f0e",
            "nodes": [
                {"id": 10, "type": "LoadImage"},
                {"id": 11, "type": "SaveImage"},
            ],
        }]
    },
}

API_FORMAT = {"3": {"class_type": "KSampler", "inputs": {}}}


# -- IO extraction tests --


def test_extract_io_basic():
    """extract_io_spec finds LoadImage and SaveImage in basic workflow."""
    io = extract_io_spec(WORKFLOW_BASIC)
    assert isinstance(io, IOSpec)
    assert len(io.inputs) == 1
    assert io.inputs[0].nodeType == "LoadImage"
    assert io.inputs[0].nodeId == 5
    assert io.inputs[0].mediaType == "image"
    assert len(io.outputs) == 1
    assert io.outputs[0].nodeType == "SaveImage"
    assert io.outputs[0].nodeId == 4
    assert io.outputs[0].mediaType == "image"


def test_extract_io_video():
    """extract_io_spec finds VHS_VideoCombine as video output."""
    io = extract_io_spec(WORKFLOW_VIDEO)
    assert len(io.outputs) == 1
    assert io.outputs[0].nodeType == "VHS_VideoCombine"
    assert io.outputs[0].mediaType == "video"


def test_extract_io_subgraph():
    """extract_io_spec finds LoadImage and SaveImage inside subgraphs."""
    io = extract_io_spec(WORKFLOW_WITH_SUBGRAPH_IO)
    assert len(io.inputs) == 1
    assert io.inputs[0].nodeType == "LoadImage"
    assert len(io.outputs) == 1
    assert io.outputs[0].nodeType == "SaveImage"


# -- Model detection tests --


def test_detect_models():
    """generate_index_entry extracts model paths from loader nodes."""
    entry = generate_index_entry(WORKFLOW_BASIC, "test")
    assert "sd_xl_base_1.0.safetensors" in entry.models


# -- Media type detection tests --


def test_detect_media_type_image():
    """Workflow with SaveImage produces mediaType 'image'."""
    entry = generate_index_entry(WORKFLOW_BASIC, "test")
    assert entry.mediaType == "image"


def test_detect_media_type_video():
    """Workflow with VHS_VideoCombine produces mediaType 'video'."""
    entry = generate_index_entry(WORKFLOW_VIDEO, "test")
    assert entry.mediaType == "video"


# -- Custom node detection tests --


def test_detect_custom_nodes():
    """Custom nodes detected, core nodes excluded."""
    entry = generate_index_entry(WORKFLOW_WITH_CUSTOM, "test")
    assert "SomeCustomNode" in entry.requiresCustomNodes
    assert "AnotherCustomNode" in entry.requiresCustomNodes
    assert "KSampler" not in entry.requiresCustomNodes
    assert "SaveImage" not in entry.requiresCustomNodes


# -- Full generation tests --


def test_generate_index_entry_full():
    """generate_index_entry with all params populates all fields."""
    entry = generate_index_entry(
        WORKFLOW_BASIC,
        name="my-template",
        title="My Template",
        description="A test template",
        tags=["test", "sdxl"],
        username="testuser",
        vram=8,
        size=12,
    )
    assert entry.name == "my-template"
    assert entry.title == "My Template"
    assert entry.description == "A test template"
    assert entry.tags == ["test", "sdxl"]
    assert entry.username == "testuser"
    assert entry.vram == 8
    assert entry.size == 12
    assert entry.date  # Should be today's date
    assert len(entry.io.inputs) > 0
    assert len(entry.io.outputs) > 0


def test_generate_index_entry_format_gate():
    """generate_index_entry raises ValueError for API-format JSON."""
    with pytest.raises(ValueError, match="Expected workflow format"):
        generate_index_entry(API_FORMAT, "test")


# -- Format tests --


def test_format_index_entry():
    """format_index_entry returns valid JSON string with template name."""
    entry = generate_index_entry(WORKFLOW_BASIC, "my-test-template")
    output = format_index_entry(entry)
    parsed = json.loads(output)
    assert parsed["name"] == "my-test-template"


# -- Notion markdown tests --


def test_notion_markdown():
    """generate_notion_markdown includes all required sections."""
    entry = generate_index_entry(WORKFLOW_BASIC, "test-tmpl", title="Test Template")
    md = generate_notion_markdown(entry, workflow_link="https://example.com")
    assert "Template Submission:" in md
    assert "Test Template" in md
    assert "sd_xl_base_1.0.safetensors" in md
    assert "https://example.com" in md
    assert "Inputs" in md
    assert "Outputs" in md


def test_thumbnail_reminder():
    """thumbnail_reminder contains key requirements."""
    text = thumbnail_reminder()
    assert "1:1" in text
    assert "3-5" in text
    assert "screenshot" in text.lower()
    assert "top-left" in text


# -- CLI tests --


def test_cli_both_output():
    """CLI with --output both shows index JSON and Notion markdown."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(WORKFLOW_BASIC, f)
        f.flush()
        tmpfile = f.name

    with mock.patch("sys.argv", ["prog", "--file", tmpfile, "--name", "test-tmpl"]):
        with mock.patch("builtins.print") as mock_print:
            from src.document.generate import main
            main()
            printed = " ".join(str(call[0][0]) for call in mock_print.call_args_list)
            # Should contain JSON-like index entry content
            assert "test-tmpl" in printed
            # Should contain Notion markdown
            assert "Template Submission" in printed
