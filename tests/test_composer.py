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


# ── Plan 02 Task 1: from_json, swap_node, scaffold ────────────────────────


class TestFromJson:
    """Test WorkflowGraph.from_json classmethod."""

    def test_from_json_parses_nodes_and_links(self):
        from src.composer.graph import WorkflowGraph

        data = {
            "nodes": [
                {
                    "id": 1,
                    "type": "KSampler",
                    "pos": [100, 200],
                    "size": [315, 170],
                    "flags": {},
                    "order": 0,
                    "mode": 0,
                    "inputs": [{"name": "model", "type": "MODEL", "link": None}],
                    "outputs": [{"name": "LATENT", "type": "LATENT", "links": [1]}],
                    "properties": {"Node name for S&R": "KSampler"},
                    "widgets_values": [42, 20, 8.0, "euler", "normal"],
                },
                {
                    "id": 2,
                    "type": "VAEDecode",
                    "pos": [300, 200],
                    "size": [315, 170],
                    "flags": {},
                    "order": 1,
                    "mode": 0,
                    "inputs": [{"name": "samples", "type": "LATENT", "link": 1}],
                    "outputs": [{"name": "IMAGE", "type": "IMAGE", "links": []}],
                    "properties": {"Node name for S&R": "VAEDecode"},
                    "widgets_values": [],
                },
            ],
            "links": [[1, 1, 0, 2, 0, "LATENT"]],
            "groups": [],
            "config": {},
            "extra": {},
            "version": 0.4,
        }
        g = WorkflowGraph.from_json(data)
        assert 1 in g._nodes
        assert 2 in g._nodes
        assert len(g._links) == 1
        assert g._nodes[1].type == "KSampler"
        assert g._nodes[2].type == "VAEDecode"

    def test_from_json_deep_copy(self):
        from src.composer.graph import WorkflowGraph

        data = {
            "nodes": [
                {
                    "id": 1,
                    "type": "KSampler",
                    "pos": [100, 200],
                    "inputs": [],
                    "outputs": [{"name": "LATENT", "type": "LATENT", "links": []}],
                    "properties": {},
                    "widgets_values": [42],
                },
            ],
            "links": [],
        }
        g = WorkflowGraph.from_json(data)
        # Modify graph -- original dict should be unaffected
        g._nodes[1].pos = [999, 999]
        assert data["nodes"][0]["pos"] == [100, 200]

    def test_from_json_preserves_subgraphs(self, sample_workflow_with_subgraphs):
        from src.composer.graph import WorkflowGraph

        g = WorkflowGraph.from_json(sample_workflow_with_subgraphs)
        assert len(g._definitions["subgraphs"]) == 1
        assert g._definitions["subgraphs"][0]["id"] == "ef10a538-17cf-46fb-930c-5460c4cf7f0e"

    def test_from_json_sets_next_ids_correctly(self):
        from src.composer.graph import WorkflowGraph

        data = {
            "nodes": [
                {"id": 5, "type": "A", "pos": [0, 0], "inputs": [], "outputs": [], "properties": {}, "widgets_values": []},
                {"id": 10, "type": "B", "pos": [0, 0], "inputs": [], "outputs": [], "properties": {}, "widgets_values": []},
            ],
            "links": [[3, 5, 0, 10, 0, "IMAGE"], [7, 10, 0, 5, 0, "IMAGE"]],
        }
        g = WorkflowGraph.from_json(data)
        assert g._next_node_id == 11  # max(5,10) + 1
        assert g._next_link_id == 8  # max(3,7) + 1


class TestSwapNode:
    """Test WorkflowGraph.swap_node method."""

    def test_swap_node_updates_type_and_snr(self):
        from src.composer.graph import WorkflowGraph

        data = {
            "nodes": [
                {
                    "id": 1,
                    "type": "KSampler",
                    "pos": [100, 200],
                    "inputs": [],
                    "outputs": [{"name": "LATENT", "type": "LATENT", "links": []}],
                    "properties": {"Node name for S&R": "KSampler"},
                    "widgets_values": [42],
                },
            ],
            "links": [],
        }
        g = WorkflowGraph.from_json(data)
        g.swap_node(1, "KSamplerAdvanced")
        assert g._nodes[1].type == "KSamplerAdvanced"
        assert g._nodes[1].properties["Node name for S&R"] == "KSamplerAdvanced"

    def test_swap_node_preserves_compatible_connections(self):
        from src.composer.graph import WorkflowGraph
        from src.composer.models import NodeSpec, OutputSpec

        data = {
            "nodes": [
                {
                    "id": 1,
                    "type": "NodeA",
                    "pos": [0, 0],
                    "inputs": [],
                    "outputs": [{"name": "LATENT", "type": "LATENT", "links": [1]}],
                    "properties": {},
                    "widgets_values": [],
                },
                {
                    "id": 2,
                    "type": "NodeB",
                    "pos": [200, 0],
                    "inputs": [{"name": "samples", "type": "LATENT", "link": 1}],
                    "outputs": [],
                    "properties": {},
                    "widgets_values": [],
                },
            ],
            "links": [[1, 1, 0, 2, 0, "LATENT"]],
        }
        g = WorkflowGraph.from_json(data)
        # Swap NodeA to NewNodeA which still outputs LATENT
        new_spec = NodeSpec(
            name="NewNodeA",
            outputs=[OutputSpec(name="LATENT", type="LATENT")],
        )
        g.swap_node(1, "NewNodeA", spec=new_spec)
        # Connection should be preserved
        assert len(g._links) == 1

    def test_swap_node_removes_incompatible_connections(self):
        from src.composer.graph import WorkflowGraph
        from src.composer.models import NodeSpec, OutputSpec

        data = {
            "nodes": [
                {
                    "id": 1,
                    "type": "NodeA",
                    "pos": [0, 0],
                    "inputs": [],
                    "outputs": [{"name": "LATENT", "type": "LATENT", "links": [1]}],
                    "properties": {},
                    "widgets_values": [],
                },
                {
                    "id": 2,
                    "type": "NodeB",
                    "pos": [200, 0],
                    "inputs": [{"name": "samples", "type": "LATENT", "link": 1}],
                    "outputs": [],
                    "properties": {},
                    "widgets_values": [],
                },
            ],
            "links": [[1, 1, 0, 2, 0, "LATENT"]],
        }
        g = WorkflowGraph.from_json(data)
        # Swap NodeA to something that outputs IMAGE instead of LATENT
        new_spec = NodeSpec(
            name="NewNodeA",
            outputs=[OutputSpec(name="IMAGE", type="IMAGE")],
        )
        g.swap_node(1, "NewNodeA", spec=new_spec)
        # Incompatible connection should be removed
        assert len(g._links) == 0
        assert g._nodes[2].inputs[0]["link"] is None


class TestScaffoldFromTemplate:
    """Test scaffold_from_template function."""

    def test_scaffold_from_template_returns_graph(self, monkeypatch):
        from src.composer import scaffold
        from src.composer.graph import WorkflowGraph

        mock_wf = {
            "nodes": [
                {"id": 1, "type": "KSampler", "pos": [100, 200], "inputs": [], "outputs": [], "properties": {}, "widgets_values": []},
            ],
            "links": [],
        }
        monkeypatch.setattr(scaffold, "fetch_workflow_json", lambda name, **kw: mock_wf)
        g = scaffold.scaffold_from_template("flux-schnell-basic")
        assert isinstance(g, WorkflowGraph)
        assert 1 in g._nodes

    def test_scaffold_from_template_raises_on_not_found(self, monkeypatch):
        from src.composer import scaffold

        monkeypatch.setattr(scaffold, "fetch_workflow_json", lambda name, **kw: None)
        with pytest.raises(ValueError, match="not found"):
            scaffold.scaffold_from_template("nonexistent-template")


class TestScaffoldFromFile:
    """Test scaffold_from_file function."""

    def test_scaffold_from_file_loads_workflow(self, tmp_path):
        import json

        from src.composer.graph import WorkflowGraph
        from src.composer.scaffold import scaffold_from_file

        wf = {
            "nodes": [
                {"id": 1, "type": "KSampler", "pos": [0, 0], "inputs": [], "outputs": [], "properties": {}, "widgets_values": []},
            ],
            "links": [],
        }
        fp = tmp_path / "test.json"
        fp.write_text(json.dumps(wf))
        g = scaffold_from_file(str(fp))
        assert isinstance(g, WorkflowGraph)
        assert 1 in g._nodes

    def test_scaffold_from_file_rejects_api_format(self, tmp_path):
        import json

        from src.composer.scaffold import scaffold_from_file

        api_data = {
            "3": {"class_type": "KSampler", "inputs": {"seed": 42}},
        }
        fp = tmp_path / "api.json"
        fp.write_text(json.dumps(api_data))
        with pytest.raises(ValueError, match="not workflow format"):
            scaffold_from_file(str(fp))


# ── Plan 02 Task 2: Auto-layout ───────────────────────────────────────────


class TestAutoLayout:
    """Test auto_layout algorithm."""

    def test_auto_layout_distinct_positions(self):
        from src.composer.graph import WorkflowGraph
        from src.composer.layout import auto_layout

        data = {
            "nodes": [
                {"id": 1, "type": "A", "pos": [0, 0], "inputs": [], "outputs": [{"name": "OUT", "type": "IMAGE", "links": [1]}], "properties": {}, "widgets_values": []},
                {"id": 2, "type": "B", "pos": [0, 0], "inputs": [{"name": "IN", "type": "IMAGE", "link": 1}], "outputs": [{"name": "OUT", "type": "IMAGE", "links": [2]}], "properties": {}, "widgets_values": []},
                {"id": 3, "type": "C", "pos": [0, 0], "inputs": [{"name": "IN", "type": "IMAGE", "link": 2}], "outputs": [], "properties": {}, "widgets_values": []},
            ],
            "links": [[1, 1, 0, 2, 0, "IMAGE"], [2, 2, 0, 3, 0, "IMAGE"]],
        }
        g = WorkflowGraph.from_json(data)
        auto_layout(g)
        positions = [tuple(n.pos) for n in g.get_nodes()]
        assert len(set(positions)) == len(positions), "All positions should be distinct"

    def test_auto_layout_source_left_of_target(self):
        from src.composer.graph import WorkflowGraph
        from src.composer.layout import auto_layout

        data = {
            "nodes": [
                {"id": 1, "type": "Source", "pos": [500, 500], "inputs": [], "outputs": [{"name": "OUT", "type": "IMAGE", "links": [1]}], "properties": {}, "widgets_values": []},
                {"id": 2, "type": "Target", "pos": [0, 0], "inputs": [{"name": "IN", "type": "IMAGE", "link": 1}], "outputs": [], "properties": {}, "widgets_values": []},
            ],
            "links": [[1, 1, 0, 2, 0, "IMAGE"]],
        }
        g = WorkflowGraph.from_json(data)
        auto_layout(g)
        src_x = g.get_node(1).pos[0]
        tgt_x = g.get_node(2).pos[0]
        assert src_x < tgt_x, "Source node should be left of target node"

    def test_auto_layout_single_node(self):
        from src.composer.graph import WorkflowGraph
        from src.composer.layout import auto_layout

        data = {
            "nodes": [
                {"id": 1, "type": "Solo", "pos": [0, 0], "inputs": [], "outputs": [], "properties": {}, "widgets_values": []},
            ],
            "links": [],
        }
        g = WorkflowGraph.from_json(data)
        auto_layout(g)
        # Should not raise; position should be assigned
        assert g.get_node(1).pos[0] == 100  # start_x default
        assert g.get_node(1).pos[1] == 200  # start_y default

    def test_auto_layout_disconnected_nodes(self):
        from src.composer.graph import WorkflowGraph
        from src.composer.layout import auto_layout

        data = {
            "nodes": [
                {"id": 1, "type": "A", "pos": [0, 100], "inputs": [], "outputs": [], "properties": {}, "widgets_values": []},
                {"id": 2, "type": "B", "pos": [0, 200], "inputs": [], "outputs": [], "properties": {}, "widgets_values": []},
                {"id": 3, "type": "C", "pos": [0, 300], "inputs": [], "outputs": [], "properties": {}, "widgets_values": []},
            ],
            "links": [],
        }
        g = WorkflowGraph.from_json(data)
        auto_layout(g)
        # All should be in layer 0 (same x) with vertical spacing
        xs = [g.get_node(nid).pos[0] for nid in [1, 2, 3]]
        ys = [g.get_node(nid).pos[1] for nid in [1, 2, 3]]
        assert all(x == 100 for x in xs), "All disconnected nodes in layer 0"
        assert len(set(ys)) == 3, "All should have distinct y positions"


# ── Plan 03 Task 1: CLI, save_workflow, integration ───────────────────────


class TestSaveWorkflow:
    """Test save_workflow writes valid JSON and returns report."""

    def test_save_workflow_writes_json_file(
        self, tmp_path, sample_ksampler_spec, sample_vaedecode_spec
    ):
        from src.composer.compose import save_workflow
        from src.composer.graph import WorkflowGraph

        cache = _build_cache(
            ("KSampler", sample_ksampler_spec),
            ("VAEDecode", sample_vaedecode_spec),
        )
        g = WorkflowGraph(specs=cache)
        g.add_node("KSampler")
        g.add_node("VAEDecode")

        out = tmp_path / "out.json"
        result = save_workflow(g, str(out), validate=False)
        assert out.exists()

        import json

        data = json.loads(out.read_text())
        assert isinstance(data["nodes"], list)
        assert data["version"] == 0.4
        assert result["path"] == str(out)
        assert result["node_count"] == 2

    def test_save_workflow_output_is_workflow_format(
        self, tmp_path, sample_ksampler_spec, sample_vaedecode_spec
    ):
        from src.composer.compose import save_workflow
        from src.composer.graph import WorkflowGraph
        from src.shared.format_detector import detect_format

        import json

        cache = _build_cache(
            ("KSampler", sample_ksampler_spec),
            ("VAEDecode", sample_vaedecode_spec),
        )
        g = WorkflowGraph(specs=cache)
        g.add_node("KSampler")
        g.add_node("VAEDecode")

        out = tmp_path / "out.json"
        save_workflow(g, str(out), validate=False)
        data = json.loads(out.read_text())
        assert detect_format(data) == "workflow"

    def test_save_workflow_with_validation(
        self, tmp_path, sample_ksampler_spec, sample_vaedecode_spec
    ):
        from src.composer.compose import save_workflow
        from src.composer.graph import WorkflowGraph

        cache = _build_cache(
            ("KSampler", sample_ksampler_spec),
            ("VAEDecode", sample_vaedecode_spec),
        )
        g = WorkflowGraph(specs=cache)
        g.add_node("KSampler")
        g.add_node("VAEDecode")

        out = tmp_path / "out.json"
        result = save_workflow(g, str(out), validate=True)
        assert result["validation"] is not None
        assert "passed" in result["validation"]
        assert "score" in result["validation"]

    def test_save_workflow_without_validation(
        self, tmp_path, sample_ksampler_spec
    ):
        from src.composer.compose import save_workflow
        from src.composer.graph import WorkflowGraph

        cache = _build_cache(("KSampler", sample_ksampler_spec))
        g = WorkflowGraph(specs=cache)
        g.add_node("KSampler")

        out = tmp_path / "out.json"
        result = save_workflow(g, str(out), validate=False)
        assert result["validation"] is None


class TestCLIMain:
    """Test CLI main function."""

    def test_cli_scaffold_writes_output(self, tmp_path, monkeypatch):
        from src.composer import compose as compose_mod

        mock_wf = {
            "nodes": [
                {
                    "id": 1,
                    "type": "KSampler",
                    "pos": [100, 200],
                    "inputs": [],
                    "outputs": [],
                    "properties": {},
                    "widgets_values": [],
                },
            ],
            "links": [],
        }
        monkeypatch.setattr(
            compose_mod,
            "scaffold_from_template",
            lambda name, **kw: __import__(
                "src.composer.graph", fromlist=["WorkflowGraph"]
            ).WorkflowGraph.from_json(mock_wf),
        )

        out = tmp_path / "cli_out.json"
        monkeypatch.setattr(
            "sys.argv",
            ["compose", "--scaffold", "test-template", "--output", str(out), "--no-validate"],
        )
        compose_mod.main()
        assert out.exists()

    def test_cli_file_writes_output(self, tmp_path, monkeypatch):
        import json

        from src.composer import compose as compose_mod

        wf = {
            "nodes": [
                {
                    "id": 1,
                    "type": "KSampler",
                    "pos": [0, 0],
                    "inputs": [],
                    "outputs": [],
                    "properties": {},
                    "widgets_values": [],
                },
            ],
            "links": [],
        }
        src_file = tmp_path / "input.json"
        src_file.write_text(json.dumps(wf))

        out = tmp_path / "cli_out.json"
        monkeypatch.setattr(
            "sys.argv",
            ["compose", "--file", str(src_file), "--output", str(out), "--no-validate"],
        )
        compose_mod.main()
        assert out.exists()


class TestFullPipeline:
    """Test full pipeline: build graph from scratch, save, validate."""

    def test_full_pipeline_build_save_validate(
        self, tmp_path, sample_ksampler_spec, sample_vaedecode_spec
    ):
        """Build a 3-node graph, connect, save, validate -- all passes."""
        from src.composer.compose import save_workflow
        from src.composer.graph import WorkflowGraph
        from src.composer.models import NodeSpec, InputSpec, OutputSpec
        from src.shared.format_detector import detect_format

        import json

        # Build a SaveImage-like spec manually
        save_spec = NodeSpec(
            name="SaveImage",
            display_name="Save Image",
            category="image",
            inputs_required={
                "images": InputSpec(name="images", type="IMAGE", is_widget=False),
            },
            outputs=[],
        )

        cache = _build_cache(
            ("KSampler", sample_ksampler_spec),
            ("VAEDecode", sample_vaedecode_spec),
        )
        cache.put("SaveImage", save_spec)

        g = WorkflowGraph(specs=cache)
        ks_id = g.add_node("KSampler")
        vae_id = g.add_node("VAEDecode")
        save_id = g.add_node("SaveImage")

        # KSampler -> VAEDecode (LATENT)
        g.connect(ks_id, 0, vae_id, "samples")
        # VAEDecode -> SaveImage (IMAGE)
        g.connect(vae_id, 0, save_id, "images")

        out = tmp_path / "pipeline.json"
        result = save_workflow(g, str(out), validate=True, layout=True)

        # File exists and is valid JSON
        assert out.exists()
        data = json.loads(out.read_text())

        # Output is workflow format
        assert detect_format(data) == "workflow"

        # Counts correct
        assert result["node_count"] == 3
        assert result["link_count"] == 2

        # Validation ran
        assert result["validation"] is not None
        assert "passed" in result["validation"]
