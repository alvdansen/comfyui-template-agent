"""Tests for the composition engine: models, node spec cache, and graph builder."""

import pytest


# ── Task 1: Models and Node Spec Cache ──────────────────────────────────────


class TestInputSpecClassification:
    """Test widget vs connection type classification."""

    def test_int_with_constraints_is_widget(self):
        from src.composer.models import is_widget_input

        raw = ["INT", {"default": 0, "min": 0, "max": 100}]
        assert is_widget_input(raw) is True

    def test_float_is_widget(self):
        from src.composer.models import is_widget_input

        raw = ["FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0}]
        assert is_widget_input(raw) is True

    def test_string_is_widget(self):
        from src.composer.models import is_widget_input

        raw = ["STRING", {"default": ""}]
        assert is_widget_input(raw) is True

    def test_boolean_is_widget(self):
        from src.composer.models import is_widget_input

        raw = ["BOOLEAN", {"default": False}]
        assert is_widget_input(raw) is True

    def test_combo_list_is_widget(self):
        from src.composer.models import is_widget_input

        raw = [["euler", "euler_a", "heun"]]
        assert is_widget_input(raw) is True

    def test_image_is_not_widget(self):
        from src.composer.models import is_widget_input

        raw = ["IMAGE"]
        assert is_widget_input(raw) is False

    def test_latent_is_not_widget(self):
        from src.composer.models import is_widget_input

        raw = ["LATENT"]
        assert is_widget_input(raw) is False

    def test_model_is_not_widget(self):
        from src.composer.models import is_widget_input

        raw = ["MODEL"]
        assert is_widget_input(raw) is False

    def test_conditioning_is_not_widget(self):
        from src.composer.models import is_widget_input

        raw = ["CONDITIONING"]
        assert is_widget_input(raw) is False

    def test_vae_is_not_widget(self):
        from src.composer.models import is_widget_input

        raw = ["VAE"]
        assert is_widget_input(raw) is False

    def test_mask_is_not_widget(self):
        from src.composer.models import is_widget_input

        raw = ["MASK"]
        assert is_widget_input(raw) is False


class TestNodeSpecParsing:
    """Test parse_node_spec converts MCP response to NodeSpec model."""

    def test_parse_ksampler_spec(self, sample_ksampler_spec):
        from src.composer.models import parse_node_spec

        spec = parse_node_spec("KSampler", sample_ksampler_spec)
        assert spec.name == "KSampler"
        assert spec.display_name == "KSampler"
        assert spec.category == "sampling"
        # Required connection inputs
        assert "model" in spec.inputs_required
        assert spec.inputs_required["model"].is_widget is False
        assert "positive" in spec.inputs_required
        assert spec.inputs_required["positive"].is_widget is False
        # Required widget inputs
        assert "seed" in spec.inputs_required
        assert spec.inputs_required["seed"].is_widget is True
        assert spec.inputs_required["seed"].default == 0
        assert "sampler_name" in spec.inputs_required
        assert spec.inputs_required["sampler_name"].is_widget is True
        assert spec.inputs_required["sampler_name"].combo_options == [
            "euler",
            "euler_a",
            "heun",
            "dpm_2",
        ]
        # Outputs
        assert len(spec.outputs) == 1
        assert spec.outputs[0].type == "LATENT"

    def test_parse_vaedecode_spec(self, sample_vaedecode_spec):
        from src.composer.models import parse_node_spec

        spec = parse_node_spec("VAEDecode", sample_vaedecode_spec)
        assert spec.name == "VAEDecode"
        assert "samples" in spec.inputs_required
        assert spec.inputs_required["samples"].is_widget is False
        assert spec.inputs_required["samples"].type == "LATENT"
        assert len(spec.outputs) == 1
        assert spec.outputs[0].type == "IMAGE"

    def test_parse_loadimage_spec(self, sample_loadimage_spec):
        from src.composer.models import parse_node_spec

        spec = parse_node_spec("LoadImage", sample_loadimage_spec)
        assert spec.name == "LoadImage"
        assert len(spec.outputs) == 2
        assert spec.outputs[0].type == "IMAGE"
        assert spec.outputs[1].type == "MASK"


class TestInputSpec:
    """Test InputSpec model fields."""

    def test_input_spec_with_constraints(self):
        from src.composer.models import InputSpec

        spec = InputSpec(
            name="seed",
            type="INT",
            default=0,
            min=0,
            max=100,
            is_widget=True,
        )
        assert spec.name == "seed"
        assert spec.type == "INT"
        assert spec.default == 0
        assert spec.min == 0
        assert spec.max == 100
        assert spec.is_widget is True

    def test_input_spec_connection_type(self):
        from src.composer.models import InputSpec

        spec = InputSpec(name="model", type="MODEL", is_widget=False)
        assert spec.is_widget is False


class TestGraphNodeModel:
    """Test GraphNode model has all required structural fields."""

    def test_graph_node_required_fields(self):
        from src.composer.models import GraphNode

        node = GraphNode(id=1, type="KSampler", pos=[100.0, 200.0])
        assert node.id == 1
        assert node.type == "KSampler"
        assert node.pos == [100.0, 200.0]
        assert node.size == [315, 170]
        assert node.flags == {}
        assert node.order == 0
        assert node.mode == 0
        assert node.properties == {}
        assert node.widgets_values == []
        assert node.inputs == []
        assert node.outputs == []


class TestGraphLinkModel:
    """Test GraphLink model stores link data correctly."""

    def test_graph_link_fields(self):
        from src.composer.models import GraphLink

        link = GraphLink(
            link_id=1,
            origin_node_id=1,
            origin_slot=0,
            target_node_id=2,
            target_slot=0,
            type="LATENT",
        )
        assert link.link_id == 1
        assert link.origin_node_id == 1
        assert link.origin_slot == 0
        assert link.target_node_id == 2
        assert link.target_slot == 0
        assert link.type == "LATENT"

    def test_graph_link_to_array(self):
        from src.composer.models import GraphLink

        link = GraphLink(
            link_id=5,
            origin_node_id=3,
            origin_slot=0,
            target_node_id=7,
            target_slot=1,
            type="IMAGE",
        )
        arr = link.to_array()
        assert arr == [5, 3, 0, 7, 1, "IMAGE"]


class TestNodeSpecCache:
    """Test NodeSpecCache caching behavior."""

    def test_cache_put_and_get(self, sample_ksampler_spec):
        from src.composer.models import parse_node_spec
        from src.composer.node_specs import NodeSpecCache

        cache = NodeSpecCache()
        spec = parse_node_spec("KSampler", sample_ksampler_spec)
        cache.put("KSampler", spec)
        assert cache.get("KSampler") is spec

    def test_cache_returns_none_for_missing(self):
        from src.composer.node_specs import NodeSpecCache

        cache = NodeSpecCache()
        assert cache.get("NonExistent") is None

    def test_cache_has(self, sample_ksampler_spec):
        from src.composer.models import parse_node_spec
        from src.composer.node_specs import NodeSpecCache

        cache = NodeSpecCache()
        assert cache.has("KSampler") is False
        spec = parse_node_spec("KSampler", sample_ksampler_spec)
        cache.put("KSampler", spec)
        assert cache.has("KSampler") is True

    def test_cache_from_mcp_response(self, sample_ksampler_spec):
        from src.composer.node_specs import NodeSpecCache

        cache = NodeSpecCache()
        spec = cache.from_mcp_response("KSampler", sample_ksampler_spec)
        assert spec.name == "KSampler"
        # Second call returns cached
        assert cache.get("KSampler") is spec

    def test_cache_second_call_no_refetch(self, sample_ksampler_spec):
        from src.composer.node_specs import NodeSpecCache

        cache = NodeSpecCache()
        spec1 = cache.from_mcp_response("KSampler", sample_ksampler_spec)
        spec2 = cache.get("KSampler")
        assert spec1 is spec2  # Same object, no re-parse
