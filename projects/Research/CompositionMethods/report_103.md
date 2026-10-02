# Report: Method 103 — Graph Neural Network Composition (GNNC)

## Method Identity
- **Method ID**: 103
- **Name**: Graph Neural Network Composition (GNNC)
- **Paradigm**: AI-Driven
- **Layer**: concrete
- **Acronym**: GNNC

## Summary Table Row (as inserted)
```
|| **103** | concrete | Graph Neural Network Composition (GNNC) | **AI-Driven** | Pitch, Rhythm, Harmony, Structure, Texture | Variable (Graph-learned) | Grid-Locked / Continuous | Macro / Graph Neighborhood | $\mathcal{O}(V \cdot T \cdot d^2)$ | Models composition as a heterogeneous graph (note, chord, bar nodes; temporal/harmonic/metric/voice edges). GNN message-passing refines node embeddings, decoded into pitch/duration/velocity/voice assignments. Relational inductive bias explicitly encodes voice-leading, harmony, and meter. |
```

## One-line Description
Models composition as a heterogeneous graph (note, chord, bar, section nodes; temporal/harmonic/metric/voice edges). GNN message-passing refines node embeddings, decoded into pitch/duration/velocity/voice assignments. Relational inductive bias explicitly encodes voice-leading, harmony, and meter.

## Classification Details

| Property | Value |
|---|---|
| Paradigm | AI-Driven |
| Layer | concrete (fills UnitMatrix cells with decoded graph-to-event results) |
| Tonal Gravity | Variable (Graph-learned — tonal gravity emerges from HARMONIC edge propagation from chord nodes; no hard-coded tonal rules) |
| Metric Binding | Grid-Locked / Continuous (bar-level metric anchors + continuous onset decoder within sections) |
| Memory Depth | Macro / Graph Neighborhood (T-hop neighborhood spans entire piece; hierarchical section→bar→chord→note structure) |
| Time Complexity | $\mathcal{O}(V \cdot T \cdot d^2)$ — V = number of note nodes, T = message-passing rounds, d = hidden dimension |
| Primary Elements | Pitch, Rhythm, Harmony, Structure, Texture (all five) |

## Distinction from Existing AI-Driven Methods

| Method | What makes GNNC different |
|---|---|
| 054 ATS (Autoregressive Transformer) | GNNC is **bidirectional** — every node sees past + future context simultaneously through graph edges. ATS is left-to-right only. GNNC explicitly models relational structure as graph edges; ATS learns it implicitly from token order. |
| 047 DSMG (Diffusion) | GNNC operates on a discrete symbolic graph, not continuous piano-roll denoising. Different inductive bias: edge types vs. score-function gradients. |
| 046 VAE-LSI (Latent Space) | GNNC learns per-graph latents (not per-bar/segment). The graph structure is generated, not a fixed sequence of latent vectors. |
| 057 MT-GAC (GAN) | GNNC is density-based (VAE/flow), not adversarial. Graph structure is explicit in the model, not implicit in the architecture. |
| 072 NFC (Normalizing Flow) | GNNC does not require invertibility; supports arbitrary many-to-many relationships that flows cannot model. |
| 060 S4SC (State Space) | S4 is a sequential model with linear recurrence; GNNC is graph-structured with T-hop propagation. S4 cannot naturally model simultaneous note interactions. |
| 062 RLPOC (RL Policy Optimization) | GNNC has no reward function, no value estimation, no policy gradient — it reconstructs/denoises graphs directly. |
| 100 AIFC (Active Inference) | GNNC has no free-energy minimization; it uses learned message-passing weights rather than Bayesian model evidence. |
| 101 FMC (Flow Matching) | GNNC operates on discrete graph nodes, not continuous ODE trajectories over token embeddings. |
| 095 CTC / 099 SSMC (Abstract) | GNNC is concrete-layer; it generates the actual events, not abstract contour or form prototypes. |

## Source References
- Cosenza, E., Valenti, A. & Bacciu, D. (2023). "Graph-based Polyphonic Multitrack Music Generation." *Proceedings of the 32nd International Joint Conference on Artificial Intelligence (IJCAI)*, pp. 643–658. — **First work to use deep graph networks for multitrack polyphonic symbolic music generation.**
- Lim, W. Q., Liang, J. & Zhang, H. (2024). "Hierarchical Symbolic Pop Music Generation with Graph Neural Networks." *arXiv:2409.08155*. — **Two-stage hierarchical VAE with graph representation: phrase-level + structure-level graphs.**
- Jeong, D. et al. (2019). "Graph Neural Network for Music Score Data and Modeling Expressive Piano Performance." *International Conference on Machine Learning*, PMLR 97.
- Schlichtkrull, M. et al. (2018). "Modeling Relational Data with Graph Convolutional Networks." *ESWC*, Springer.
- Wu, J. et al. (2020). "PopMNet: Generating Structured Pop Music Melodies Using Neural Networks." *Artificial Intelligence* 286, 103303.
- Zou, Y. et al. (2022). "MELONS: Generating Melody with Long-term Structure Using Transformers and Structure Graph." *ICASSP 2022*, pp. 191–195.

## File Paths
- **Standalone method**: `/opt/data/projects/Research/CompositionMethods/method_103_GNNC.md`
- **Report**: `/opt/data/projects/Research/CompositionMethods/report_103.md`
- **Methods DB**: `/opt/data/projects/Research/CompositionMethods/methods_db.md`

## Line Count Metrics
- **Before**: 22546 lines (from first read_file header)
- **After**: 22623 lines (from wc -l)
- **Delta**: +77 lines (method section + summary row + separators)

## Candidate Code Path
`generators/gnnc_generator.py`

This module would implement the GNN composition pipeline:
1. Build the heterogeneous graph (note, chord, bar, section nodes; TEMPORAL, HARMONIC, METRIC, VOICE edges) from either a seed graph or empty template.
2. Run T rounds of relational message-passing (HGTConv / GAT-typed convolution).
3. Decode each note node's embedding → pitch logits, duration class logits, velocity scalar, voice assignment logits, onset offset.
4. Assemble the decoded events into MusicUnits per (voice, section) cell.
5. Validate zero-drift invariant (equal-length tracks) and export to MIDI via UnitMatrixComposer.

Alternatively, the graph-based VAE approach:
`generators/gnnc_vae_generator.py`
1. Encode the full musical graph to a latent vector via GNN encoder + global pooling.
2. Sample latent from learned prior $\mathcal{N}(0, I)$.
3. Decode graph structure (node counts, edge types) and node attributes (pitch, duration, velocity, voice).
4. Assemble and export as above.

## Method Section Text (complete appended text — written to _temp_method_103.md and cat-appended)

The following text was appended to methods_db.md as the new method 103 section:

```
### 103. Graph Neural Network Composition (GNNC)

### Source
Cosenza, E., Valenti, A. & Bacciu, D. (2023). "Graph-based Polyphonic Multitrack Music Generation." *Proceedings of the 32nd International Joint Conference on Artificial Intelligence (IJCAI)*, pp. 643–658. — Lim, W. Q., Liang, J. & Zhang, H. (2024). "Hierarchical Symbolic Pop Music Generation with Graph Neural Networks." *arXiv:2409.08155*. — Jeong, D. et al. (2019). "Graph Neural Network for Music Score Data and Modeling Expressive Piano Performance." *International Conference on Machine Learning*, PMLR 97.

### Layer
**concrete** — generates concrete pitch, rhythm, harmony, structure, and texture events that fill UnitMatrix cells. The GNN operates on a graph where nodes encode musical events (notes, chords, onsets) and edges encode temporal and tonal relationships; message-passing refines node features, which are decoded into per-cell MusicEvents.

### Description
[Full detailed description in method_103_GNNC.md]

**PITCH**: Driven by the pitch decoder acting on node embeddings that aggregate harmonic (chord-tone membership), temporal (melodic contour), and voice (voice-leading) information. The relational inductive bias means a note "knows" its chord context, voice neighbors, and metric position simultaneously, producing tonally and contrapuntally coherent pitch choices.

**RHYTHM**: Emerges from the duration decoder combined with the graph's temporal adjacency structure. TEMPORAL edges carry inter-onset-interval information, so rhythmic cells and groove patterns propagate across the graph.

**HARMONY**: Encoded explicitly through chord nodes and HARMONIC edges linking note nodes to their parent chord node. The chord node specifies root, quality, and inversion. Message-passing ensures every note reflects its harmonic function.

**STRUCTURE**: Multi-graph hierarchy: section → bar → chord → note. Section-to-section edges encode form transition probabilities. Hierarchical message passing propagates structural decisions down to individual notes.

**TEXTURE**: Controlled by voice assignment decoder and density temperature. VOICE edges maintain independent per-voice subgraphs.

### UnitMatrix Integration
**Voices (Rows)**: Each voice = a connected subgraph bound by VOICE edges. Voice decoder assigns nodes via softmax over K voices. Diversity loss prevents mode collapse (all notes to one voice).

**Sections (Columns)**: Section nodes created one per formal segment. Bar nodes connect to their parent section. Section transition edges encode form grammar (A→B, B→A).

**Cells (MusicUnits)**: Each cell = set of note nodes matching (voice, section). Sorted by onset. Zero-drift invariant: every node has explicit metric anchor → padding aligns to section boundary.

### Pitfalls
1. Graph construction is costly — batched encoding required for full pieces.
2. Edge type explosion with 6+ types — type-agnostic bundling is a practical simplification.
3. Training data needs graph annotations (chord-to-note links, section labels) — synthetic augmentation helps.
4. UnitMatrix cell boundary rounding — nodes crossing section boundaries must be split.
5. Parallel voice collapse — diversity loss or per-voice decoders needed.
6. Long-range dependencies require deep GNNs with oversmoothing mitigation.
7. Inference requires either autoregressive graph expansion or full-graph VAE — both active research areas.
```

## Quirks and Pitfalls Encountered

1. **ID resolution**: Max method ID was 102 (Cross-Entropy Method Composition). Confirmed via both summary table scan and file listing of `method_*.md`. Note: some method files exist for IDs below 042 (method_042_neural_style_transfer.md, method_043_satm.md) and 048–102, but no gaps cause issues.

2. **Summary table row format**: Rows 001–100 start with `| **NNN** |` (single leading pipe), but rows 101+ start with `|| **NNN** |` (double leading pipe). This is a pre-existing formatting inconsistency in the DB. The patch preserved whatever the existing format was for the surrounding rows.

3. **LaTeX escaping**: The summary table uses `$\\mathcal{O}(...)$` with single backslashes. The patch tool does NOT double-escape these — verified by re-reading the patched lines.

4. **Large file**: methods_db.md is ~22,623 lines / ~2.2 MB. Reading requires pagination with offset/limit. Full-file reads are rejected.

5. **Classifying layer**: GNNC is concrete-layer — it generates actual MusicEvents (pitch, duration, velocity) that fill UnitMatrix cells, not abstract subset sequences or sound production artifacts.

6. **Novelty check**: No existing method in the DB uses graph neural networks. The family of AI methods includes transformers (054), VAEs (046), diffusion (047), GANs (057), state-space (060), normalizing flows (072), RL (062), active inference (100), flow matching (101), RBM (074), NMF (085) — but none use relational graph-structured architectures. GNNC fills this gap.

7. **Patch table row insert**: When inserting the new summary row, had to ensure the trailing `|||` separator (after 102's row the table has `|||` empty line) was preserved. The patch was set to match `|||` existing pattern.

## Verification Commands

```
wc -l /opt/data/projects/Research/CompositionMethods/methods_db.md
# After:  22623 lines

grep 'GNNC\|Graph Neural Network\|103' /opt/data/projects/Research/CompositionMethods/methods_db.md
# Confirms new row and method section

grep -c '### Source' /opt/data/projects/Research/CompositionMethods/methods_db.md
# Returns correct count (includes new section)
```

## Next Free ID
After 103 (GNNC), the next free algorithmic method ID is **104**.

## Final Artifacts

| File | Description |
|---|---|
| `methods_db.md` (summary table row) | Row for GNNC added at line 113 |
| `methods_db.md` (near end) | Full GNNC method section appended after the CEMC section |
| `method_103_GNNC.md` | Standalone write-up (16 KB): extended math, implementation sketch, references |
| `report_103.md` | This report — the PRIMARY record |