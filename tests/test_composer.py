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


# ── Task 2: WorkflowGraph Builder ──────────────────────────────────────────


def _build_cache(*fixtures):
    """Helper: build a NodeSpecCache from raw MCP fixture dicts."""
    from src.composer.node_specs import NodeSpecCache

    cache = NodeSpecCache()
    for name, raw in fixtures:
        cache.from_mcp_response(name, raw)
    return cache


class TestAddNode:
    """Test WorkflowGraph.add_node behavior."""

    def test_add_node_structural_fields(self, sample_ksampler_spec):
        from src.composer.graph import WorkflowGraph

        cache = _build_cache(("KSampler", sample_ksampler_spec))
        g = WorkflowGraph(specs=cache)
        nid = g.add_node("KSampler", pos=[100.0, 200.0])
        assert nid == 1
        node = g._nodes[nid]
        assert node.id == 1
        assert node.type == "KSampler"
        assert node.pos == [100.0, 200.0]
        assert node.size == [315, 170]
        assert node.flags == {}
        assert node.order == 0
        assert node.mode == 0
        assert node.properties == {"Node name for S&R": "KSampler"}

    def test_add_node_auto_populates_widgets_values(self, sample_ksampler_spec):
        from src.composer.graph import WorkflowGraph

        cache = _build_cache(("KSampler", sample_ksampler_spec))
        g = WorkflowGraph(specs=cache)
        nid = g.add_node("KSampler")
        node = g._nodes[nid]
        # KSampler widgets in order: seed(INT), steps(INT), cfg(FLOAT),
        # sampler_name(COMBO), scheduler(COMBO)
        # Connection inputs (model, positive, negative, latent_image) are skipped
        assert len(node.widgets_values) == 5
        assert node.widgets_values[0] == 0  # seed default
        assert node.widgets_values[1] == 20  # steps default
        assert node.widgets_values[2] == 8.0  # cfg default
        assert node.widgets_values[3] == "euler"  # sampler_name first option
        assert node.widgets_values[4] == "normal"  # scheduler first option

    def test_add_node_populates_connection_inputs(self, sample_ksampler_spec):
        from src.composer.graph import WorkflowGraph

        cache = _build_cache(("KSampler", sample_ksampler_spec))
        g = WorkflowGraph(specs=cache)
        nid = g.add_node("KSampler")
        node = g._nodes[nid]
        # KSampler has 4 connection inputs: model, positive, negative, latent_image
        input_names = [inp["name"] for inp in node.inputs]
        assert "model" in input_names
        assert "positive" in input_names
        assert "negative" in input_names
        assert "latent_image" in input_names

    def test_add_node_populates_outputs(self, sample_ksampler_spec):
        from src.composer.graph import WorkflowGraph

        cache = _build_cache(("KSampler", sample_ksampler_spec))
        g = WorkflowGraph(specs=cache)
        nid = g.add_node("KSampler")
        node = g._nodes[nid]
        assert len(node.outputs) == 1
        assert node.outputs[0]["name"] == "LATENT"
        assert node.outputs[0]["type"] == "LATENT"

    def test_add_node_without_spec(self):
        from src.composer.graph import WorkflowGraph

        g = WorkflowGraph()
        nid = g.add_node("UnknownNode", pos=[50.0, 50.0])
        assert nid == 1
        node = g._nodes[nid]
        assert node.type == "UnknownNode"
        assert node.widgets_values == []


class TestConnect:
    """Test WorkflowGraph.connect behavior."""

    def test_connect_matching_types(
        self, sample_ksampler_spec, sample_vaedecode_spec
    ):
        from src.composer.graph import WorkflowGraph

        cache = _build_cache(
            ("KSampler", sample_ksampler_spec),
            ("VAEDecode", sample_vaedecode_spec),
        )
        g = WorkflowGraph(specs=cache)
        ks_id = g.add_node("KSampler")
        vae_id = g.add_node("VAEDecode")
        # KSampler output[0] = LATENT, VAEDecode input "samples" = LATENT
        link_id = g.connect(ks_id, 0, vae_id, "samples")
        assert link_id == 1

    def test_connect_type_mismatch_raises(
        self, sample_loadimage_spec, sample_ksampler_spec
    ):
        from src.composer.graph import WorkflowGraph

        cache = _build_cache(
            ("LoadImage", sample_loadimage_spec),
            ("KSampler", sample_ksampler_spec),
        )
        g = WorkflowGraph(specs=cache)
        img_id = g.add_node("LoadImage")
        ks_id = g.add_node("KSampler")
        # LoadImage output[0] = IMAGE, KSampler input "latent_image" = LATENT
        with pytest.raises(TypeError, match="Cannot connect IMAGE to LATENT"):
            g.connect(img_id, 0, ks_id, "latent_image")

    def test_connect_wildcard_succeeds(self, sample_ksampler_spec):
        from src.composer.graph import WorkflowGraph
        from src.composer.models import GraphNode

        cache = _build_cache(("KSampler", sample_ksampler_spec))
        g = WorkflowGraph(specs=cache)
        # Add a node with wildcard output manually
        wild_node = GraphNode(
            id=99,
            type="Reroute",
            pos=[0, 0],
            outputs=[{"name": "output", "type": "*", "links": []}],
        )
        g._nodes[99] = wild_node
        g._next_node_id = 100
        ks_id = g.add_node("KSampler")
        # Wildcard output should connect to any input
        link_id = g.connect(99, 0, ks_id, "model")
        assert link_id >= 1

    def test_connect_creates_correct_link_format(
        self, sample_ksampler_spec, sample_vaedecode_spec
    ):
        from src.composer.graph import WorkflowGraph

        cache = _build_cache(
            ("KSampler", sample_ksampler_spec),
            ("VAEDecode", sample_vaedecode_spec),
        )
        g = WorkflowGraph(specs=cache)
        ks_id = g.add_node("KSampler")
        vae_id = g.add_node("VAEDecode")
        link_id = g.connect(ks_id, 0, vae_id, 0)
        link = g._links[0]
        assert link.link_id == link_id
        assert link.origin_node_id == ks_id
        assert link.origin_slot == 0
        assert link.target_node_id == vae_id
        assert link.target_slot == 0
        assert link.type == "LATENT"

    def test_connect_updates_node_io(
        self, sample_ksampler_spec, sample_vaedecode_spec
    ):
        from src.composer.graph import WorkflowGraph

        cache = _build_cache(
            ("KSampler", sample_ksampler_spec),
            ("VAEDecode", sample_vaedecode_spec),
        )
        g = WorkflowGraph(specs=cache)
        ks_id = g.add_node("KSampler")
        vae_id = g.add_node("VAEDecode")
        link_id = g.connect(ks_id, 0, vae_id, 0)
        # Source output should reference the link
        assert link_id in g._nodes[ks_id].outputs[0]["links"]
        # Target input should reference the link
        assert g._nodes[vae_id].inputs[0]["link"] == link_id


class TestSetWidget:
    """Test WorkflowGraph.set_widget behavior."""

    def test_set_widget_updates_value(self, sample_ksampler_spec):
        from src.composer.graph import WorkflowGraph

        cache = _build_cache(("KSampler", sample_ksampler_spec))
        g = WorkflowGraph(specs=cache)
        nid = g.add_node("KSampler")
        g.set_widget(nid, "steps", 50)
        assert g._nodes[nid].widgets_values[1] == 50

    def test_set_widget_validates_combo(self, sample_ksampler_spec):
        from src.composer.graph import WorkflowGraph

        cache = _build_cache(("KSampler", sample_ksampler_spec))
        g = WorkflowGraph(specs=cache)
        nid = g.add_node("KSampler")
        with pytest.raises(ValueError, match="not a valid option"):
            g.set_widget(nid, "sampler_name", "nonexistent_sampler")

    def test_set_widget_valid_combo_succeeds(self, sample_ksampler_spec):
        from src.composer.graph import WorkflowGraph

        cache = _build_cache(("KSampler", sample_ksampler_spec))
        g = WorkflowGraph(specs=cache)
        nid = g.add_node("KSampler")
        g.set_widget(nid, "sampler_name", "euler_a")
        assert g._nodes[nid].widgets_values[3] == "euler_a"


class TestRemoveNode:
    """Test WorkflowGraph.remove_node behavior."""

    def test_remove_node_and_links(
        self, sample_ksampler_spec, sample_vaedecode_spec
    ):
        from src.composer.graph import WorkflowGraph

        cache = _build_cache(
            ("KSampler", sample_ksampler_spec),
            ("VAEDecode", sample_vaedecode_spec),
        )
        g = WorkflowGraph(specs=cache)
        ks_id = g.add_node("KSampler")
        vae_id = g.add_node("VAEDecode")
        g.connect(ks_id, 0, vae_id, 0)
        assert len(g._links) == 1
        g.remove_node(ks_id)
        assert ks_id not in g._nodes
        assert len(g._links) == 0
        # VAEDecode input should be cleared
        assert g._nodes[vae_id].inputs[0]["link"] is None


class TestSerialize:
    """Test WorkflowGraph.serialize behavior."""

    def test_serialize_workflow_format(
        self, sample_ksampler_spec, sample_vaedecode_spec
    ):
        from src.composer.graph import WorkflowGraph

        cache = _build_cache(
            ("KSampler", sample_ksampler_spec),
            ("VAEDecode", sample_vaedecode_spec),
        )
        g = WorkflowGraph(specs=cache)
        ks_id = g.add_node("KSampler")
        vae_id = g.add_node("VAEDecode")
        g.connect(ks_id, 0, vae_id, 0)
        result = g.serialize()
        assert result["version"] == 0.4
        assert isinstance(result["nodes"], list)
        assert isinstance(result["links"], list)
        assert result["last_node_id"] == max(ks_id, vae_id)
        assert result["last_link_id"] == 1

    def test_serialize_passes_format_detection(
        self, sample_ksampler_spec, sample_vaedecode_spec
    ):
        from src.shared.format_detector import detect_format
        from src.composer.graph import WorkflowGraph

        cache = _build_cache(
            ("KSampler", sample_ksampler_spec),
            ("VAEDecode", sample_vaedecode_spec),
        )
        g = WorkflowGraph(specs=cache)
        g.add_node("KSampler")
        g.add_node("VAEDecode")
        result = g.serialize()
        assert detect_format(result) == "workflow"

    def test_serialize_node_has_snr_property(self, sample_ksampler_spec):
        from src.composer.graph import WorkflowGraph

        cache = _build_cache(("KSampler", sample_ksampler_spec))
        g = WorkflowGraph(specs=cache)
        g.add_node("KSampler")
        result = g.serialize()
        node_data = result["nodes"][0]
        assert node_data["properties"]["Node name for S&R"] == "KSampler"

    def test_serialize_link_array_format(
        self, sample_ksampler_spec, sample_vaedecode_spec
    ):
        from src.composer.graph import WorkflowGraph

        cache = _build_cache(
            ("KSampler", sample_ksampler_spec),
            ("VAEDecode", sample_vaedecode_spec),
        )
        g = WorkflowGraph(specs=cache)
        ks_id = g.add_node("KSampler")
        vae_id = g.add_node("VAEDecode")
        g.connect(ks_id, 0, vae_id, 0)
        result = g.serialize()
        link_arr = result["links"][0]
        assert isinstance(link_arr, list)
        assert len(link_arr) == 6
        assert link_arr[5] == "LATENT"

    def test_serialize_empty_graph(self):
        from src.composer.graph import WorkflowGraph

        g = WorkflowGraph()
        result = g.serialize()
        assert result["version"] == 0.4
        assert result["nodes"] == []
        assert result["links"] == []
        assert result["last_node_id"] == 0
        assert result["last_link_id"] == 0


class TestCheckTypeCompatibility:
    """Test the type compatibility checker."""

    def test_exact_match(self):
        from src.composer.graph import check_type_compatibility

        assert check_type_compatibility("LATENT", "LATENT") is True

    def test_mismatch(self):
        from src.composer.graph import check_type_compatibility

        assert check_type_compatibility("IMAGE", "LATENT") is False

    def test_wildcard_output(self):
        from src.composer.graph import check_type_compatibility

        assert check_type_compatibility("*", "LATENT") is True

    def test_wildcard_input(self):
        from src.composer.graph import check_type_compatibility

        assert check_type_compatibility("IMAGE", "*") is True
