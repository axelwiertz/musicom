# Registration Report — Method 109: Spiking Neural Network Composition (SNN-C)

**Date**: 2026-10-08
**Agent**: cron music-research job
**Next free ID**: 110

## Method Overview

| Field | Value |
|---|---|
| **ID** | 109 |
| **Name** | Spiking Neural Network Composition (SNN-C) |
| **Paradigm** | Nature-Led |
| **LAYER** | concrete |
| **Description** | Generates musical compositions using a multi-region spiking neural network of Izhikevich neurons with STDP learning. Hippocampal memory stores motif sequences via spike-timing-dependent plasticity; prefrontal cortex encodes mode/scale/style knowledge; thalamic theta-gamma oscillators drive metric hierarchy; insula system controls tension/release trajectory. Spike trains decoded to pitch (population-rate), duration (ISI), velocity (peak firing). Biologically-plausible Nature-Led counterpart to 059 ESN-RC / 037 FHN; non-backpropagation foil to 054 ATS / 046 VAE-LSI. |

## Summary Table Row

```
|| **109** | concrete | Spiking Neural Network Composition (SNN-C) | **Nature-Led** | Pitch, Rhythm, Harmony, Structure, Texture | Strict (Mode/Synaptic-guided) | Grid-Locked / Continuous | Meso / Spike-Train | $\mathcal{O}(N \cdot T)$ simulation | Generates musical compositions using a multi-region spiking neural network of Izhikevich neurons with STDP learning. Hippocampal memory stores motif sequences via spike-timing-dependent plasticity; prefrontal cortex encodes mode/scale/style knowledge; thalamic theta-gamma oscillators drive metric hierarchy; insula system controls tension/release trajectory. Spike trains decoded to pitch (population-rate), duration (ISI), velocity (peak firing). Biologically-plausible Nature-Led counterpart to 059 ESN-RC / 037 FHN; non-backpropagation foil to 054 ATS / 046 VAE-LSI. |
```

## Classification Details

### Paradigm: Nature-Led

The entire architecture is biologically inspired: Izhikevich spiking neurons model cortical dynamics, STDP models Hebbian synaptic learning, brain oscillation rhythms (theta/gamma) drive temporal structure, and multi-region circuits (hippocampus, prefrontal cortex, thalamus, insula) collaborate as in the human brain. No backpropagation training — STDP is local, unsupervised, and spike-timing dependent. No explicit musical rewrite rules — musical knowledge emerges from the learned synaptic connectivity matrices.

### Layer: concrete

Generates events (spike-train-decoded pitch/duration/velocity) that fill UnitMatrix cells. The multi-region spiking neural network produces discrete spike trains; a readout layer decodes population firing rates or exact spike times into per-voice MusicEvents. Feeds generators/ via `generators/snn_composer.py`.

### Relationship to Existing Methods

| Method | Relationship |
|---|---|
| 037 FHN | FHN is a continuous ODE model of a *single-cell* membrane potential (2-variable system) used to trigger rhythmic impulses. SNN-C is a full *network* of Izhikevich spiking neurons with multi-brain-region architecture, STDP learning, and spike-train-to-pitch decoding. |
| 059 ESN-RC | ESN is a rate-coded reservoir with linear readout. SNN uses discrete spike events, temporal coding, and biologically-plausible STDP learning. |
| 071 HAM-C | Hopfield networks are attractor networks with binary threshold neurons. SNN uses Izhikevich spiking neurons with temporal dynamics and STDP. |
| 082 RBNCC | RBN is a discrete-time Boolean network. SNN uses continuous-time spiking dynamics. |
| 054 ATS / 046 VAE | Both are backpropagation-trained continuous activation networks. SNN uses local STDP learning — no backpropagation. |

## Musical Elements Framework

| Element | SNN-C Mechanism |
|---|---|
| **PITCH** | Population-rate decoding over 12 pitch-class columns (tonotopic A1 sheet). Winning column via softmax of firing rates. Intervals emerge from tonotopic distance. |
| **RHYTHM** | Thalamic theta-gamma phase coupling. PLV controls metric rigidity. Gamma cycles per theta cycle = subdivision. |
| **HARMONY** | Co-activated pitch columns during same gamma cycle = chord. STDP-learned excitatory/inhibitory connections encode interval preferences (consonant/dissonant). |
| **STRUCTURE** | "Form theta" oscillator (0.1–0.5 Hz) governs section transitions. Prefrontal section-token firing patterns gate per-section parameters. |
| **TEXTURE** | Inter-population spike correlation controls voice independence. Low correlation = independent voices; high = homophonic. |

## UnitMatrix Integration

- **Voices**: Each UnitMatrix voice = one spiking neural population (25 Izhikevich RS neurons) with its own tonotopic range, STDP matrix, and decoder.
- **Sections**: Each section = theta oscillation period with distinct prefrontal section-token pattern.
- **Cells**: Decoded (pitch, onset_tick, duration, velocity) from spike trains per voice per section window.

## Files Created/Modified

| File | Action | Lines |
|---|---|---|
| `methods_db.md` | Modified — summary row + detailed section appended | Before: 23964 → After: 24035 (+71 lines) |
| `method_109_SNN-C.md` | Created — standalone write-up | 1 file (21,405 bytes) |
| `report_109.md` | Created — this report | 1 file |

## Line Count

- `methods_db.md` before: 23964 lines
- `methods_db.md` after: 24035 lines
- Delta: +71 lines

## Standalone File Path

`/opt/data/projects/Research/CompositionMethods/method_109_SNN-C.md`

## Report File Path

`/opt/data/projects/Research/CompositionMethods/report_109.md`

## Candidate Code Path

```
generators/snn_composer.py
```

Module containing: `IzhikevichNeuron`, `STDPSynapse`, `PopulationRateDecoder`, and `SNNComposer` classes. The `SNNComposer.compose(section_plan, bars_per_section)` returns per-voice note event dicts for UnitMatrix filling.

## Complete Method Section (appended text)

```
### 109. Spiking Neural Network Composition (SNN-C)

### Source
Liang, Q. & Zeng, Y. (2021). "Stylistic Composition of Melodies Based on a Brain-Inspired Spiking Neural Network." *Frontiers in Systems Neuroscience* 15, 639484. — Liang, Q., Zeng, Y. & Tang, M. (2025). "Mode-conditioned music learning and composition: a spiking neural network inspired by neuroscience and psychology." *arXiv:2411.14773*. — Zeng, Y. et al. (2023). "BrainCog: A spiking neural network based, brain-inspired cognitive intelligence engine." *Patterns* 4, 100789. — Izhikevich, E. M. (2003). "Simple model of spiking neurons." *IEEE Transactions on Neural Networks* 14(6), 1569–1572. — Bi, G. & Poo, M.-M. (1998). "Synaptic modifications in cultured hippocampal neurons: dependence on spike timing, synaptic strength, and postsynaptic cell type." *Journal of Neuroscience* 18(24), 10464–10472.

### Layer
**concrete** — generates sequences of spike-train-decoded pitch/duration/velocity events that fill UnitMatrix cells. The multi-region spiking neural network produces discrete spike trains; a readout layer decodes population firing rates or exact spike times into per-voice MusicEvents. Feeds generators/ via `generators/snn_composer.py`.

### Paradigm
**Nature-Led** — the entire architecture is biologically inspired: Izhikevich spiking neurons model cortical dynamics, STDP (spike-timing-dependent plasticity) models Hebbian synaptic learning, brain oscillation rhythms (theta/gamma) drive temporal structure, and multi-region circuits (hippocampus, prefrontal cortex, thalamus, insula) collaborate as they do in the human brain. No backpropagation training—STDP is local, unsupervised, and spike-timing dependent. No explicit musical rewrite rules—musical knowledge emerges from the learned synaptic connectivity matrices.

### Description
**Spiking Neural Network Composition (SNN-C)** is a brain-inspired computational model that generates musical compositions using a multi-region spiking neural network of Izhikevich neurons with STDP learning. Unlike rate-coded neural networks (RNNs, transformers, ESNs), SNNs communicate via discrete spike events (action potentials) in continuous time, where the *exact timing* of each spike carries information—offering a fundamentally different computational substrate for music generation that is closer to biological neural computation.

[Full description text in methods_db.md and method_109_SNN-C.md]

### Musical Elements Framework
[Full text in methods_db.md]

### UnitMatrix Integration (Voices & Sections)
[Full text in methods_db.md]

### Pitfalls
[8 pitfalls documented in methods_db.md]
```

## Quirks/Pitfalls Encountered

1. **Table pipe normalization**: The methods_db.md summary table has inconsistent pipe prefixes (`||`, `|||`, `||||`). The patch tool's fuzzy matching caused a previous row (105 PURC) to lose its method ID prefix on the first patch attempt. Fixed with a second targeted patch.

2. **Concatenation without header**: The `cat` append of `_temp_method_109.md` to `methods_db.md` produced no blank line between the HDCC section's end and the new content's `### Source` header, resulting in a concatenated line. Fixed with a patch to insert the `### 109.` header and a blank line.

3. **LaTeX backslash escaping**: The `patch` tool handles `$` and `\` characters. Double-escaped backslashes `\\` in the file (from prior tool operations) were preserved correctly by the patch tool.

4. **170+ character lines**: The summary table rows are extremely long (single-line cells). The patch tool handled them correctly using fuzzy context matching.

## Verification

```bash
wc -l /opt/data/projects/Research/CompositionMethods/methods_db.md
# Expected: 24035 lines (was 23964, +71)

grep "109.*SNN-C" /opt/data/projects/Research/CompositionMethods/methods_db.md
# Expected: summary row + section header
```