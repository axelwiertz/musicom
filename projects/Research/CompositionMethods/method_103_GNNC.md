# Method 103: Graph Neural Network Composition (GNNC)

## Paradigm
**AI-Driven**

## Layer
**concrete** — generates concrete pitch, rhythm, harmony, structure, and texture events that fill UnitMatrix cells. The GNN operates on a heterogeneous graph (note, chord, bar, section nodes) via message-passing, and the refined node embeddings are decoded into per-cell MusicEvent attributes.

## One-line Description
Models composition as a heterogeneous graph (note, chord, bar, section nodes; temporal/harmonic/metric/voice edges). GNN message-passing refines node embeddings, decoded into pitch/duration/velocity/voice assignments. Relational inductive bias explicitly encodes voice-leading, harmony, and meter.

## Summary Table Row
|| **103** | concrete | Graph Neural Network Composition (GNNC) | **AI-Driven** | Pitch, Rhythm, Harmony, Structure, Texture | Variable (Graph-learned) | Grid-Locked / Continuous | Macro / Graph Neighborhood | $\mathcal{O}(V \cdot T \cdot d^2)$ | Models composition as a heterogeneous graph (note, chord, bar nodes; temporal/harmonic/metric/voice edges). GNN message-passing refines node embeddings, decoded into pitch/duration/velocity/voice assignments. Relational inductive bias explicitly encodes voice-leading, harmony, and meter. |

---

## Mathematical Formulation

### Core Algorithm

Graph Neural Network Composition (GNNC) represents the entire composition as a heterogeneous directed multigraph $\mathcal{G} = (\mathcal{V}, \mathcal{E}, \mathcal{R}, \mathcal{T})$ where:

- $\mathcal{V} = \mathcal{V}_N \cup \mathcal{V}_C \cup \mathcal{V}_B \cup \mathcal{V}_S$: node set partitioned into **note nodes** $n_i$ (pitch, onset, duration, velocity, voice-id), **chord nodes** $c_j$ (root, quality, inversion), **bar nodes** $b_k$ (meter, downbeat, harmony summarization), and **section nodes** $s_l$ (form label, key, register range).
- $\mathcal{E}$: edge set with relation types $\mathcal{R} = \{\texttt{TEMPORAL}, \texttt{HARMONIC}, \texttt{METRIC}, \texttt{SIMULTANEITY}, \texttt{VOICE}, \texttt{ATTENTIONAL}\}$.
- $\mathcal{T}$: node type mapping $\mathcal{V} \to \{\text{note}, \text{chord}, \text{bar}, \text{section}\}$.

### Message Passing (Relational GCN / Gated Graph Network)

For $T$ rounds, each node $v$ updates its hidden state $h_v^{(t)}$ by aggregating messages from its neighbors, weighted by relation type:

$$h_v^{(t+1)} = \text{GRU}\!\left(h_v^{(t)},\; \sum_{r \in \mathcal{R}} \sum_{u \in \mathcal{N}_r(v)} \frac{1}{|\mathcal{N}_r(v)|} \, W_r \, h_u^{(t)}\right)$$

where:
- $W_r \in \mathbb{R}^{d \times d}$ is a learned weight matrix per relation type.
- $\mathcal{N}_r(v)$ is the set of neighbors of $v$ through edges of type $r$.
- Normalization by $1/|\mathcal{N}_r(v)|$ prevents degree-biased embeddings.

For **GAT** (Graph Attention Network) variant:

$$h_v^{(t+1)} = \sigma\!\left(\sum_{r \in \mathcal{R}} \sum_{u \in \mathcal{N}_r(v)} \alpha_{vu}^{(r)} \, W_r \, h_u^{(t)}\right)$$

$$\alpha_{vu}^{(r)} = \frac{\exp\!\big(\text{LeakyReLU}(a_r^T [W_r h_v^{(t)} \| W_r h_u^{(t)}])\big)}{\sum_{w \in \mathcal{N}_r(v)} \exp\!\big(\text{LeakyReLU}(a_r^T [W_r h_v^{(t)} \| W_r h_w^{(t)}])\big)}$$

where $\alpha_{vu}^{(r)}$ is a learned attention weight, $\|$ denotes concatenation, and $a_r$ is the attention vector for relation $r$.

### Decoding

After $T$ rounds, each node's final embedding $h_v^{(T)}$ is decoded into musical attributes:

$$p_v = \text{softmax}(\text{MLP}_p(h_v^{(T)})) \quad \text{(pitch logits over MIDI range)}$$
$$d_v = \text{softmax}(\text{MLP}_d(h_v^{(T)})) \quad \text{(duration class distribution)}$$
$$v_v = \text{tanh}(\text{MLP}_v(h_v^{(T)})) \times 127 \quad \text{(velocity, scaled 0--127)}$$
$$w_v = \text{softmax}(\text{MLP}_w(h_v^{(T)})) \quad \text{(voice assignment)}$$
$$o_v = \sigma(\text{MLP}_o(h_v^{(T)})) \times \text{section\_len} \quad \text{(onset offset within section)}$$

### Training Objective

$$\mathcal{L} = \mathcal{L}_{\text{pitch}}(\hat{p},p) + \mathcal{L}_{\text{dur}}(\hat{d},d) + \mathcal{L}_{\text{vel}}(v,v_{\text{target}}) + \mathcal{L}_{\text{voice}}(\hat{w},w) + \lambda_{\text{KL}} \text{KL}(q(z|x)\|p(z))$$

For VAE variants (Cosenza et al. 2023), a latent variable $z \sim \mathcal{N}(0,I)$ is sampled and concatenated to each node's initial embedding, enabling structured latent-space interpolation and unconditional generation.

### Complexity

| Phase | Complexity |
|---|---|
| Graph construction | $\mathcal{O}(|\mathcal{V}| + |\mathcal{E}|)$ |
| Message passing (per round) | $\mathcal{O}(|\mathcal{E}| \cdot d^2 + |\mathcal{V}| \cdot d^2)$ |
| Decoding | $\mathcal{O}(|\mathcal{V}_N| \cdot d)$ |
| UnitMatrix assembly | $\mathcal{O}(|\mathcal{V}_N| \log |\mathcal{V}_N|)$ |
| **Total per step** | $\mathcal{O}(V \cdot T \cdot d^2)$ where $V = |\mathcal{V}_N|$ |

---

## Key Distinctions From Existing AI-Driven Methods

| vs. | Difference |
|---|---|
| **054 ATS** (Autoregressive Transformer) | GNNC is **bidirectional** — every node sees past + future context simultaneously through graph edges. ATS is left-to-right only. GNNC explicitly models relational structure (voice-leading, harmony) as graph edges; ATS learns it implicitly from token order. |
| **047 DSMG** (Diffusion) | GNNC operates on a discrete symbolic graph, not continuous piano-roll denoising. GNNC's inductive bias comes from edge types, not from the score-predicting diffusion process. |
| **046 VAE-LSI** (Latent Space Interpolation) | GNNC (VAE variant) learns a per-graph latent, not per-bar/segment. The graph structure is generated, not a fixed series of latent vectors. |
| **057 MT-GAC** (GAN) | GNNC is density-based (VAE/flow), not adversarial. Graph structure is explicit rather than implicit in the generator architecture. |
| **072 NFC** (Normalizing Flow) | GNNC does not require invertibility; the graph permits arbitrary many-to-many relationships. |
| **060 S4SC** (State Space) | S4 is a sequential model with linear-time recurrence; GNNC is a graph-structured model with $T$-hop propagation. S4 cannot naturally model simultaneous note relationships. |

---

## Musical Elements Framework

### PITCH
Driven by the pitch decoder acting on node embeddings that aggregate harmonic (chord-tone membership via HARMONIC edges), temporal (melodic contour via TEMPORAL edges), and voice (voice-leading via VOICE edges) information simultaneously. The relational inductive bias means each note node "knows" its chord context, melodic neighbors, and voice peers. The HARMONIC edge from note to chord propagates the chord-scale constraint (e.g., Cmaj chord node sends root=60, third=64, fifth=67 embeddings to all its note nodes). TEMPORAL edges enforce stepwise motion (interval preference via learned $W_r$), while SIMULTANEITY edges prevent parallel unisons and regulate voice-crossing (negative weight on parallel fifths).

### RHYTHM
Emerges from the duration decoder combined with the graph's temporal adjacency structure. TEMPORAL edges carry implicit inter-onset-interval (IOI) information through the difference in their onset attributes. The GRU state update propagates rhythmic cell and groove patterns across the graph via recurrent connections. Bar nodes encode metric hierarchy (strong/weak beat via embedded downbeat position), which the message-passing spreads to individual note nodes, anchoring durational choices to metric positions. Syncopation arises when a note's decoded duration disagrees with its metric-level expectation, creating a learned positive-tension gradient that propagates via METRIC edges.

### HARMONY
Encoded explicitly through chord nodes and HARMONIC edges linking note nodes to their parent chord node. The chord node itself is a conditioned embedding specifying root (12-class), quality (major/minor/dim/aug/sus4/7th/etc.), and inversion. During generation, chord nodes are either sampled from a prior (unconditional) or fixed from a progression (conditional). The HARMONIC edge ensures every note reflects its chord function (root, third, fifth, seventh). SIMULTANEITY edges across notes assigned to the same chord enforce vertical consonance constraints (anti-parallel-fifths, voice-spacing). The chord-to-chord transition is modeled as a HARMONIC edge from chord $c_t$ to $c_{t+1}$, encoding the learned progression grammar.

### STRUCTURE
Hierarchical multi-graph: the full-graph $\mathcal{G}$ has four node levels:
- **Section nodes** $s_l$: highest level, embedding encodes form label (verse/chorus/bridge), key, tempo, and register range.
- **Bar nodes** $b_k$: connected to parent section via METRIC edges. Encode meter, downbeat, and harmony summary.
- **Chord nodes** $c_j$: connected to parent bar via METRIC edges.
- **Note nodes** $n_i$: connected to parent chord via HARMONIC and parent bar via METRIC edges.

Message-passing propagates downward: section context → bars → chords → notes, ensuring every note is consistent with its structural position. Section-to-section edges encode transition probabilities (e.g., verse→chorus is highly probable, chorus→bridge less so).

### TEXTURE
Controlled by voice assignment (decoder $w_v$) and the density of nodes in the graph. The VOICE edge type ensures all notes assigned to a voice form a connected subgraph, maintaining voice independence. Texture density emerges from the decoding temperature $\tau$:

$$\text{density} = \sum_{v \in \mathcal{V}_N} \mathbb{I}\{\text{MLP}_{\text{keep}}(h_v) > \tau\}$$

where $\text{MLP}_{\text{keep}}$ is a binary classifier that decides whether to include a candidate node. At high $\tau$, fewer nodes survive → sparse texture; at low $\tau$, more nodes survive → dense texture. Per-section $\tau$ schedules control macro-texture arc.

---

## UnitMatrix Integration (Voices & Sections)

### UnitMatrix Model
The composer creates a UnitMatrix: rows = voices (independent instrumental lines), columns = sections (formal segments A, B, chorus, bridge, etc.), cells = MusicUnit (ordered sequence of MusicEvents).

### Voices (Rows)
Each voice corresponds to a connected subgraph of $\mathcal{G}$, bound by VOICE-type edges. The voice decoder $w_v$ assigns each note node to a voice ID via softmax over $K$ voices. During decoding, a diversity loss $\mathcal{L}_{\text{div}} = -\sum_{b \in \mathcal{B}} \sum_{i \neq j} d(w_i^{(b)}, w_j^{(b)})$ prevents mode collapse (all notes assigned to voice 1). Voice edges connect all nodes of the same voice in temporal order, so voice-leading smoothness propagates through message passing.

The number of voices $K$ is either fixed (user sets voice count) or learned as the rank of the voice-embedding matrix.

### Sections (Columns)
Section nodes $s_l$ are created one per formal segment. Each bar node connects to exactly one section node. Section transition edges encode the form grammar — A→B with learned probability, B→A with repetition penalty, etc. During conditioned generation, section embeddings are fixed from a form template (AABA, verse-chorus). During unconditional generation, section embeddings are sampled from a learned prior (Gaussian mixture model over section types).

### Cells = MusicUnit
Each cell (voice $v_i$, section $s_j$) is the set of note nodes satisfying:
- $w_v(\text{node}) = v_i$ (voice assignment)
- $\text{METRIC}(\text{node}) \in [\text{start}_j, \text{end}_j]$ (section time bounds)

The onset offset decoder $o_v$ gives the time within the section, so nodes are sorted by onset within each cell. The full cell content is packed into a `MusicUnit` (list of `MusicEvent` objects) and placed in the UnitMatrix. 

**Zero-drift invariant**: Every node has an explicit metric anchor (bar node + section node), and the decoded onset $o_v$ is relative to the section start. Therefore, the terminal landmark of each cell's note sequence is always $\leq$ the section length; padding aligns the last event's end tick to the section boundary if needed.

---

## Implementation Sketch (Python + PyTorch Geometric)

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.data import HeteroData
from torch_geometric.nn import HGTConv, to_hetero

class GNNC(nn.Module):
    """Graph Neural Network Composition model."""

    def __init__(
        self,
        node_types: list[str] = ["note", "chord", "bar", "section"],
        edge_types: list[tuple] = [
            ("note", "temporal", "note"),
            ("note", "harmonic", "chord"),
            ("note", "metric", "bar"),
            ("note", "voice", "note"),
            ("bar", "metric", "section"),
            ("chord", "metric", "bar"),
        ],
        hidden_dim: int = 128,
        num_layers: int = 6,
        num_heads: int = 4,
        num_voices: int = 4,
        midi_range: int = 88,
    ):
        super().__init__()
        self.node_emb = nn.ModuleDict({
            nt: nn.Linear(in_feats[nt], hidden_dim)
            for nt in node_types
        })
        self.convs = nn.ModuleList([
            HGTConv(hidden_dim, hidden_dim, edge_types, num_heads)
            for _ in range(num_layers)
        ])
        # Per-attribute decoders
        self.pitch_decoder = nn.Linear(hidden_dim, midi_range)
        self.dur_decoder = nn.Linear(hidden_dim, 16)  # 16 duration classes
        self.vel_decoder = nn.Linear(hidden_dim, 1)
        self.voice_decoder = nn.Linear(hidden_dim, num_voices)
        self.onset_decoder = nn.Sequential(
            nn.Linear(hidden_dim, 64), nn.ReLU(), nn.Linear(64, 1)
        )

    def forward(self, data: HeteroData) -> dict:
        x_dict = data.x_dict
        # Initial embeddings
        for nt, x in x_dict.items():
            x_dict[nt] = self.node_emb[nt](x)
        # Message passing
        for conv in self.convs:
            x_dict = conv(x_dict, data.edge_index_dict)
        # Decode note nodes only
        h_note = x_dict["note"]
        return {
            "pitch": self.pitch_decoder(h_note),
            "duration": self.dur_decoder(h_note),
            "velocity": self.vel_decoder(h_note).squeeze(-1),
            "voice": self.voice_decoder(h_note),
            "onset": self.onset_decoder(h_note).squeeze(-1),
        }

    def compose(self, data: HeteroData, temperature: float = 1.0) -> dict:
        """Generate a composition from the graph."""
        logits = self.forward(data)
        # Sample with temperature
        pitch = F.softmax(logits["pitch"] / temperature, dim=-1).multinomial(1)
        dur = F.softmax(logits["duration"] / temperature, dim=-1).multinomial(1)
        vel = torch.clamp(logits["velocity"] + torch.randn_like(logits["velocity"]) * temperature * 10, 0, 127)
        voice = F.softmax(logits["voice"] / temperature, dim=-1).argmax(dim=-1)
        onset = torch.sigmoid(logits["onset"])  # 0-1 within section
        return {"pitch": pitch, "duration": dur, "velocity": vel, "voice": voice, "onset": onset}
```

---

## References

- Cosenza, E., Valenti, A. & Bacciu, D. (2023). "Graph-based Polyphonic Multitrack Music Generation." *IJCAI 2023*, pp. 643–658.
- Lim, W. Q., Liang, J. & Zhang, H. (2024). "Hierarchical Symbolic Pop Music Generation with Graph Neural Networks." *arXiv:2409.08155*.
- Jeong, D. et al. (2019). "Graph Neural Network for Music Score Data and Modeling Expressive Piano Performance." *ICML*, PMLR 97.
- Schlichtkrull, M. et al. (2018). "Modeling Relational Data with Graph Convolutional Networks." *ESWC*, Springer.
- Wu, J. et al. (2020). "PopMNet: Generating Structured Pop Music Melodies Using Neural Networks." *Artificial Intelligence* 286, 103303.
- Zou, Y. et al. (2022). "MELONS: Generating Melody with Long-term Structure Using Transformers and Structure Graph." *ICASSP 2022*, pp. 191–195.
- Veličković, P. et al. (2018). "Graph Attention Networks." *ICLR 2018*.
- Kipf, T. N. & Welling, M. (2017). "Semi-Supervised Classification with Graph Convolutional Networks." *ICLR 2017*.