"""Modular patch JSON loader — Karst style.

Load/save node-graph patches as JSON and build a ModularGraph from a
declarative description.

JSON format:
{
  "nodes": [
    {"type": "osc", "name": "osc1", "params": {"freq": 440, "waveform": "sine"}},
    {"type": "gain", "name": "g1", "params": {"gain": 0.5}},
    {"type": "out", "name": "out1", "params": {}}
  ],
  "edges": [
    {"src": "osc1", "out": "out", "dst": "g1", "in": "in"},
    {"src": "g1", "out": "out", "dst": "out1", "in": "in"}
  ]
}
"""

import json
from typing import Dict, List, Any, Optional

__all__ = ["PatchLoader", "PatchBuilder"]

_NODE_TYPES = {
    "osc": ("OscNode", ["freq", "waveform"]),
    "gain": ("GainNode", ["gain"]),
    "filter": ("FilterNode", ["cutoff"]),
    "delay": ("DelayNode", ["delay_seconds", "feedback"]),
    "mix": ("MixNode", ["gains"]),
    "env": ("EnvNode", ["attack", "decay", "sustain", "release"]),
    "noise": ("NoiseNode", ["seed"]),
    "out": ("OutNode", []),
}


class PatchLoader:
    """JSON patch file I/O."""

    @staticmethod
    def load(path: str) -> Dict[str, Any]:
        """Read a patch JSON file."""
        with open(path, "r") as f:
            return json.load(f)

    @staticmethod
    def save(patch: Dict[str, Any], path: str):
        """Write a patch JSON file (indented, sorted keys)."""
        with open(path, "w") as f:
            json.dump(patch, f, indent=2, sort_keys=True)


class PatchBuilder:
    """Build a ModularGraph from a JSON patch description."""

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate

    def _make_node(self, node_spec: Dict[str, Any]):
        """Instantiate a modular node from a spec dict."""
        from sound.modular import (OscNode, GainNode, FilterNode, DelayNode,
                                   MixNode, EnvNode, NoiseNode, OutNode)

        ntype = node_spec.get("type", "").lower()
        params = dict(node_spec.get("params", {}))
        params.setdefault("sample_rate", self.sample_rate)

        if ntype == "osc":
            return OscNode(**params)
        if ntype == "gain":
            return GainNode(**params)
        if ntype == "filter":
            return FilterNode(**params)
        if ntype == "delay":
            return DelayNode(**params)
        if ntype == "mix":
            return MixNode(**params)
        if ntype == "env":
            return EnvNode(**params)
        if ntype == "noise":
            return NoiseNode(**params)
        if ntype == "out":
            return OutNode(**params)
        raise ValueError(f"Unknown node type: {ntype}")

    def build(self, patch: Dict[str, Any]) -> Any:
        """Construct a ModularGraph from the patch description.

        Returns:
            sound.modular.ModularGraph instance (renders via .render(duration)).
        """
        from sound.modular import ModularGraph

        graph = ModularGraph(sample_rate=self.sample_rate)
        by_name: Dict[str, Any] = {}

        for spec in patch.get("nodes", []):
            name = spec.get("name")
            node = self._make_node(spec)
            node.name = name or node.name
            graph.add(node)
            if name:
                by_name[name] = node

        for edge in patch.get("edges", []):
            src = by_name.get(edge.get("src"))
            dst = by_name.get(edge.get("dst"))
            if src is None or dst is None:
                raise ValueError(f"Edge references unknown node: {edge}")
            graph.connect(src, edge.get("out", "out"),
                          dst, edge.get("in", "in"))

        return graph
