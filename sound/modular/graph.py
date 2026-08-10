"""Modular node-graph DSP engine — SynthEdit-style visual patching.

Nodes = osc/filter/env/delay/etc, edges = audio/CV connections.
Execution = topological sort over the node graph.

Reference: surveillance report Aug 2026, SynthEdit (modular builder concept).

Usage:
    from sound.modular.graph import ModularGraph, OscNode, GainNode, OutNode

    g = ModularGraph(sample_rate=44100)
    osc = g.add(OscNode(freq=440.0))
    gain = g.add(GainNode(gain=0.5))
    out = g.add(OutNode())
    g.connect(osc, 'out', gain, 'in')
    g.connect(gain, 'out', out, 'in')
    audio = g.render(duration=1.0)
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Deque
from collections import deque

__all__ = [
    "ModularGraph", "Node", "OscNode", "GainNode", "OutNode",
    "FilterNode", "DelayNode", "MixNode", "EnvNode", "NoiseNode",
]


class Node:
    """Base node in the modular graph."""

    def __init__(self, name: str = "", sample_rate: int = 44100):
        self.name = name
        self.sr = sample_rate
        self.inputs: Dict[str, Any] = {}
        self.outputs: Dict[str, np.ndarray] = {}
        self._in_edges: List[Tuple[str, str]] = []   # (out_port, in_port) from sources
        self._out_edges: List[Tuple[str, str]] = []  # (out_port, in_port) to sinks

    def process(self, n_samples: int):
        """Process this node for n_samples.  Subclasses override."""
        raise NotImplementedError

    def get(self, port: str) -> np.ndarray:
        """Get output port value."""
        return self.outputs.get(port, np.zeros(1))


class OscNode(Node):
    """Oscillator node (sine/saw/square via phase accumulator)."""

    WAVEFORMS = ["sine", "saw", "square", "triangle"]

    def __init__(self, freq: float = 440.0, waveform: str = "sine",
                 sample_rate: int = 44100, name: str = ""):
        super().__init__(name, sample_rate)
        self.freq = freq
        self.waveform = waveform
        self._phase = 0.0

    def process(self, n_samples: int):
        t = np.arange(n_samples) / self.sr
        phase = (self.freq * t + self._phase) % 1.0
        self._phase = phase[-1]
        if self.waveform == "sine":
            sig = np.sin(2 * np.pi * phase)
        elif self.waveform == "saw":
            sig = 2.0 * phase - 1.0
        elif self.waveform == "square":
            sig = np.sign(2.0 * phase - 1.0)
        elif self.waveform == "triangle":
            sig = 2.0 * np.abs(2.0 * phase - 1.0) - 1.0
        else:
            sig = np.sin(2 * np.pi * phase)
        self.outputs["out"] = sig.astype(np.float32)


class GainNode(Node):
    """Gain/attenuation node."""

    def __init__(self, gain: float = 0.5, name: str = "",
                 sample_rate: int = 44100):
        super().__init__(name, sample_rate)
        self.gain = gain

    def process(self, n_samples: int):
        inp = self.inputs.get("in", np.zeros(n_samples))
        self.outputs["out"] = (inp * self.gain).astype(np.float32)


class FilterNode(Node):
    """Simple one-pole low-pass filter node."""

    def __init__(self, cutoff: float = 1000.0, sample_rate: int = 44100,
                 name: str = ""):
        super().__init__(name, sample_rate)
        self.cutoff = cutoff
        self._state = 0.0

    def process(self, n_samples: int):
        inp = self.inputs.get("in", np.zeros(n_samples))
        alpha = 1.0 - np.exp(-2 * np.pi * self.cutoff / self.sr)
        out = np.zeros(n_samples)
        state = self._state
        for i in range(n_samples):
            state = state + alpha * (inp[i] - state)
            out[i] = state
        self._state = state
        self.outputs["out"] = out.astype(np.float32)


class DelayNode(Node):
    """Tape-style delay node with feedback."""

    def __init__(self, delay_seconds: float = 0.25, feedback: float = 0.3,
                 sample_rate: int = 44100, name: str = ""):
        super().__init__(name, sample_rate)
        self.delay_samples = max(1, int(delay_seconds * sample_rate))
        self.feedback = feedback
        self._buffer = np.zeros(self.delay_samples + 1)

    def process(self, n_samples: int):
        inp = self.inputs.get("in", np.zeros(n_samples))
        buf = self._buffer
        d = self.delay_samples
        out = np.zeros(n_samples)
        for i in range(n_samples):
            delayed = buf[i % (d + 1)]
            out[i] = inp[i] + delayed * self.feedback
            buf[i % (d + 1)] = out[i]
        self.outputs["out"] = out.astype(np.float32)


class MixNode(Node):
    """Mix multiple inputs."""

    def __init__(self, gains: Optional[List[float]] = None, name: str = "",
                 sample_rate: int = 44100):
        super().__init__(name, sample_rate)
        self.gains = gains or [1.0, 1.0]

    def process(self, n_samples: int):
        n_in = len(self.gains)
        out = np.zeros(n_samples)
        for i in range(n_in):
            inp = self.inputs.get(f"in{i}", np.zeros(n_samples))
            g = self.gains[i] if i < len(self.gains) else 1.0
            out += inp * g
        self.outputs["out"] = out.astype(np.float32)


class EnvNode(Node):
    """ADSR envelope node (generates a control signal)."""

    def __init__(self, attack: float = 0.01, decay: float = 0.1,
                 sustain: float = 0.7, release: float = 0.2,
                 sample_rate: int = 44100, name: str = ""):
        super().__init__(name, sample_rate)
        self.attack = attack
        self.decay = decay
        self.sustain = sustain
        self.release = release

    def process(self, n_samples: int):
        a = int(self.attack * self.sr)
        d = int(self.decay * self.sr)
        r = int(self.release * self.sr)
        n = n_samples
        env = np.zeros(n)
        if a > 0:
            env[:a] = np.linspace(0, 1, a)
        if d > 0:
            end = min(a + d, n)
            env[a:end] = np.linspace(1, self.sustain, max(1, end - a))
        env[a + d:] = self.sustain
        if r > 0:
            env[-r:] *= np.linspace(1, 0, r)
        self.outputs["out"] = env.astype(np.float32)


class NoiseNode(Node):
    """White noise source."""

    def __init__(self, seed: Optional[int] = None, name: str = "",
                 sample_rate: int = 44100):
        super().__init__(name, sample_rate)
        self._rng = np.random.default_rng(seed)

    def process(self, n_samples: int):
        self.outputs["out"] = self._rng.uniform(-1, 1, n_samples).astype(np.float32)


class OutNode(Node):
    """Output node — collects final audio."""

    def __init__(self, name: str = "", sample_rate: int = 44100):
        super().__init__(name, sample_rate)
        self.audio: Optional[np.ndarray] = None

    def process(self, n_samples: int):
        inp = self.inputs.get("in", np.zeros(n_samples))
        self.audio = inp.copy()
        self.outputs["out"] = inp


class ModularGraph:
    """Node-graph DSP engine with topological-sort execution.

    Parameters
    ----------
    sample_rate : int
        Audio sample rate.
    """

    def __init__(self, sample_rate: int = 44100):
        self.sr = sample_rate
        self.nodes: List[Node] = []
        self.edges: List[Tuple[Node, str, Node, str]] = []

    def add(self, node: Node) -> Node:
        """Add a node to the graph (node.sr set at construction)."""
        self.nodes.append(node)
        return node

    def connect(self, src: Node, out_port: str,
                dst: Node, in_port: str):
        """Connect src.out_port -> dst.in_port."""
        self.edges.append((src, out_port, dst, in_port))
        src._out_edges.append((out_port, in_port))
        dst._in_edges.append((out_port, in_port))

    def _topo_sort(self) -> List[Node]:
        """Return nodes in dependency order (sources first). Kahn's algorithm."""
        by_id = {id(n): n for n in self.nodes}
        indeg: Dict[int, int] = {id(n): 0 for n in self.nodes}
        adj: Dict[int, List[int]] = {id(n): [] for n in self.nodes}
        for src, _op, dst, _ip in self.edges:
            adj[id(src)].append(id(dst))
            indeg[id(dst)] += 1
        q: Deque[int] = deque([id(n) for n in self.nodes if indeg[id(n)] == 0])
        order: List[Node] = []
        while q:
            nid = q.popleft()
            order.append(by_id[nid])
            for dst_id in adj[nid]:
                indeg[dst_id] -= 1
                if indeg[dst_id] == 0:
                    q.append(dst_id)
        # cycles: append unprocessed in original order
        processed = {id(n) for n in order}
        order += [n for n in self.nodes if id(n) not in processed]
        return order

    def render(self, duration: float) -> np.ndarray:
        """Render the graph to mono audio.

        Returns
        -------
        np.ndarray
            1D audio normalized to [-1, 1].
        """
        n = int(duration * self.sr)
        order = self._topo_sort()

        # Execute in topo order; a source's outputs become available after
        # it processes, then we push them to downstream inputs.
        for node in order:
            node.process(n)
            # push outputs to downstream inputs
            for out_port, in_port in node._out_edges:
                for (s, op, d, ip) in self.edges:
                    if s is node and op == out_port and ip == in_port:
                        if out_port in node.outputs:
                            d.inputs[in_port] = node.outputs[out_port]

        # gather output
        outs = [nd for nd in self.nodes if isinstance(nd, OutNode)]
        if outs and outs[-1].audio is not None:
            audio = outs[-1].audio
        else:
            audio = self.nodes[-1].get("out")
        audio = np.asarray(audio, dtype=float)
        peak = np.max(np.abs(audio)) if len(audio) else 1.0
        if peak > 0:
            audio = audio / peak
        return audio.astype(np.float32)
