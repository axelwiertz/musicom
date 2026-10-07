# Method 108 — Hyperdimensional Computing Composition (HDCC)

**Acronym**: HDCC
**Paradigm**: AI-Driven
**Layer**: concrete
**Next free ID**: 109

## Summary Table Row

| **108** | concrete | Hyperdimensional Computing Composition (HDCC) | **AI-Driven** | Pitch, Rhythm, Harmony, Structure, Texture | Moderate (Prototype-similarity-guided) | Grid-Locked / Continuous | Macro / Hypervector Trajectory | $\mathcal{O}(D \cdot N)$ | Encodes every musical element as a quasi-orthogonal high-dimensional random vector ($D \geq 10{,}000$) and composes via explicit algebraic operations (binding $\otimes$, bundling $+$, permutation $\rho$) over hypervectors. Binding creates role–filler structures (pitch $\otimes$ chord), bundling superpositions multi-voice polyphony, permutation encodes sequence order. Composition = encode section hypervectors → decode via similarity search item memory → fill UnitMatrix cells. No training — the HD algebra is the generative process. Brain-inspired, non-connectionist AI-Driven counterpart to 002 Markov / 054 ATS / 046 VAE-LSI. |

## Extended Description

Hyperdimensional Computing Composition (HDCC) leverages the Vector Symbolic Architecture (VSA) framework — a family of computational models that use high-dimensional distributed representations and rely on the algebraic properties of random high-dimensional vector spaces. In HDCC, every musical symbol (pitch class, duration class, chord type, voice role, section label, metric position) is represented as a hypervector: a vector in $\{\pm1\}^D$ or $\{0,1\}^D$ with $D$ typically $\geq 10{,}000$.

### Core VSA Operations

1. **Bundling** (superposition): $\mathbf{z} = \mathrm{sgn}(\mathbf{x} + \mathbf{y})$ for bipolar HVs. The bundled result is similar to both $\mathbf{x}$ and $\mathbf{y}$: $\cos(\mathbf{z}, \mathbf{x}) > 0.5$, $\cos(\mathbf{z}, \mathbf{y}) > 0.5$.
2. **Binding** (structured association): $\mathbf{z} = \mathbf{x} \otimes \mathbf{y}$. For binary HVs, $\otimes$ is elementwise XOR; for real-valued HVs (HRR), it's circular convolution. Binding is invertible: $\mathbf{x} = \mathbf{z} \oslash \mathbf{y}$ (XOR is self-inverse).
3. **Permutation** (sequence order): $\mathbf{z} = \rho^k(\mathbf{x})$, a fixed cyclic shift by $k$ positions. Repeated permutation encodes position in a sequence.

These three operations form an algebraic system isomorphic to a high-dimensional vector space with near-deterministic recovery. The probability that two random hypervectors have cosine similarity $> 0$ is negligible for $D \geq 10{,}000$ (quasi-orthogonality).

### Musical Encoding

**Pitch classes** $p_0 \ldots p_{11}$: i.i.d. random $\{\pm1\}^D$ vectors. A chord = bundled pitch classes:
$$\mathbf{H}_{\mathrm{Cmaj}} = p_0 + p_4 + p_7$$

**Duration classes** $d_{1/4}, d_{1/8}, d_{1/16}, d_{1/32}$: random HVs. **Velocity levels** $v_{pp}, v_p, v_f, v_{ff}$: random HVs.

**Voice roles** $r_{\text{lead}}, r_{\text{bass}}, r_{\text{chord}}, r_{\text{perc}}$: random HVs. Quasi-orthogonality ensures voices are separable.

**Metric positions** $m_0 \ldots m_{15}$ (16th positions in a bar): random HVs. Bar number $b$ is a permutation of the metric position HVs: $m_{i}^{(b)} = \rho^b(m_i)$.

**Section labels** $L_{\text{intro}}, L_{\text{verse}}, L_{\text{chorus}}, L_{\text{bridge}}, L_{\text{outro}}$: random HVs.

### Composition Algorithm

1. **Item memory construction**: Generate random $\{\pm1\}^D$ for each atomic symbol ($\sim$50–200 symbols). Store in $\mathcal{M}$.

2. **Per-section composition**: For each section $s$:
   a. Define chord progression: sequence of $(r_i, T_i, \text{bar}_b, m_i)$
   b. Encode each chord: $\mathbf{chord}_{i} = p_{r_i} \otimes c_{T_i}$
   c. Bundle chords into progression: $\mathbf{Prog}_s = \sum_i \rho^{b\cdot 16 + i}(\mathbf{chord}_i) \otimes m_i$
   d. For each voice $v$: encode rhythm pattern as set of metric positions where notes fire
   e. For each onset position $i$: $\mathbf{note}_i = p_{\text{pitch}} + d_{\text{dur}} + v_{\text{vel}}$
   f. Bundle voice content: $\mathbf{V}_{v,s} = \sum_i \rho^{i}(\mathbf{note}_i) \otimes r_v$
   g. Assemble section: $\mathbf{S}_s = (\sum_v \mathbf{V}_{v,s} + \mathbf{Prog}_s) \otimes L_s$

3. **Macro-form assembly**: $\mathbf{Form} = \sum_s \rho^{s \cdot T}(\mathbf{S}_s)$ where $T$ is section length in metric positions.

4. **Decoding**: For each section $s$, bar $b$, 16th-position $m_i$, voice $v$:
   a. $\mathbf{h} = \mathbf{Form} \oslash L_s$ (extract section)
   b. $\mathbf{h}_v = \mathbf{h} \oslash r_v$ (extract voice)
   c. $\mathbf{h}_{v,i} = \rho^{-(b\cdot 16 + i)}(\mathbf{h}_v) \oslash m_i$ (extract position)
   d. $p^* = \arg\max_p \cos(p, \mathbf{h}_{v,i})$
   e. If $\cos(p^*, \mathbf{h}_{v,i}) > \theta_{\text{onset}}$: emit note-on event
   f. Decode duration: $d^* = \arg\max_d \cos(d, \mathbf{h}_{v,i})$
   g. Decode velocity: $v^* = \arg\max_v \cos(v, \mathbf{h}_{v,i})$

5. **UnitMatrix filling**: Convert decoded events to $MusicUnit$ cells per voice and section.

### Mathematical Foundations

The quasi-orthogonality of random hypervectors: For $\mathbf{x}, \mathbf{y} \in \{\pm1\}^D$ i.i.d., the dot product $\mathbf{x} \cdot \mathbf{y}$ has mean 0 and variance $D$. By the Central Limit Theorem, $\frac{\mathbf{x} \cdot \mathbf{y}}{\sqrt{D}} \sim \mathcal{N}(0, 1)$. Thus $P(|\cos\theta| > \epsilon) \to 0$ as $D \to \infty$.

Binding (XOR) preserves this property: $\mathbf{x} \otimes \mathbf{y}$ is also i.i.d. $\{\pm1\}^D$ when $\mathbf{x}$ and $\mathbf{y}$ are independent. Bundling $k$ independent hypervectors yields a vector with mean $1/k$ per-component similarity to each member, enabling clean separation by nearest-neighbor search.

Recovery probability: For a bundle of $k$ items, the probability of correct nearest-neighbor decoding is:
$$P_{\text{correct}} = \Phi\left(\frac{\sqrt{D}(1 - \epsilon)}{\sqrt{k-1}}\right)$$
where $\Phi$ is the standard normal CDF and $\epsilon$ is the query similarity threshold. For $D=10{,}000$, $k=8$ voices, $P_{\text{correct}} > 0.99$.

## Python Implementation Sketch

```python
import numpy as np
from typing import Dict, List, Tuple

D = 10000  # hypervector dimensionality

class HDItemMemory:
    """Stores atomic hypervectors for musical symbols."""
    
    def __init__(self, seed: int = 42):
        self.rng = np.random.default_rng(seed)
        self.memory: Dict[str, np.ndarray] = {}
    
    def add_atom(self, name: str) -> np.ndarray:
        hv = self.rng.choice([-1, 1], size=D, dtype=np.int8)
        self.memory[name] = hv
        return hv
    
    def get(self, name: str) -> np.ndarray:
        return self.memory[name]
    
    def decode(self, query: np.ndarray, candidates: List[str]) -> Tuple[str, float]:
        """Nearest-neighbor decode via cosine similarity."""
        best_name, best_sim = None, -1.0
        for name in candidates:
            sim = np.dot(query, self.memory[name]) / D
            if sim > best_sim:
                best_sim = sim
                best_name = name
        return best_name, best_sim


# VSA operations
def bundle(hvs: List[np.ndarray]) -> np.ndarray:
    """Bundle (superpose) hypervectors via sum + sign."""
    return np.sign(np.sum(hvs, axis=0)).astype(np.int8)

def bind(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Bind via elementwise XOR (binary VSA model)."""
    return (x * y).astype(np.int8)

def unbind(z: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Unbind (inverse of XOR binding). For binary, same as bind."""
    return bind(z, y)

def permute(x: np.ndarray, k: int = 1) -> np.ndarray:
    """Permute by cyclic shift."""
    return np.roll(x, k)

# --- Music encoding functions ---

def encode_note(pitch_hv: np.ndarray, dur_hv: np.ndarray, 
                vel_hv: np.ndarray) -> np.ndarray:
    return bundle([pitch_hv, dur_hv, vel_hv])

def encode_chord(root_hv: np.ndarray, chord_type_hv: np.ndarray) -> np.ndarray:
    return bind(root_hv, chord_type_hv)

def encode_section(voice_contents: Dict[str, List[Tuple[int, np.ndarray]]],
                   section_label_hv: np.ndarray,
                   mem: HDItemMemory) -> np.ndarray:
    """Encode a full section from per-voice note sequences.
    
    voice_contents: {voice_name: [(metric_position, note_hv), ...]}
    """
    section_hv = np.zeros(D, dtype=np.int8)
    for voice_name, notes in voice_contents.items():
        r_v = mem.get(voice_name)
        voice_hv = np.zeros(D, dtype=np.int8)
        for pos, note_hv in notes:
            m_i = mem.get(f"m_{pos}")
            voice_hv += permute(bind(note_hv, r_v), pos)
        section_hv += voice_hv
    return bind(np.sign(section_hv).astype(np.int8), section_label_hv)

def decode_section(section_hv: np.ndarray, section_label: str,
                   voice_roles: List[str], num_metric_positions: int,
                   mem: HDItemMemory, theta_onset: float = 0.35) -> Dict[str, List]:
    """Decode a section hypervector back to per-voice note events."""
    L_s = mem.get(section_label)
    section_raw = unbind(section_hv, L_s)
    
    pitch_candidates = [f"p_{i}" for i in range(12)]
    dur_candidates = ["d_1/4", "d_1/8", "d_1/16", "d_1/32"]
    vel_candidates = ["v_pp", "v_p", "v_f", "v_ff"]
    
    result = {}
    for voice in voice_roles:
        r_v = mem.get(voice)
        voice_raw = unbind(section_raw, r_v)
        events = []
        for pos in range(num_metric_positions):
            m_i = mem.get(f"m_{pos}")
            h = unbind(permute(voice_raw, -pos), m_i)
            
            p_name, p_sim = mem.decode(h, pitch_candidates)
            if p_sim < theta_onset:
                continue  # rest at this position
            
            d_name, _ = mem.decode(h, dur_candidates)
            v_name, _ = mem.decode(h, vel_candidates)
            
            events.append({
                'pitch': int(p_name.split('_')[1]),
                'position': pos,
                'duration': d_name,
                'velocity': v_name
            })
        result[voice] = events
    return result


# Example: compose a 4-bar C major verse with lead + chord + bass
if __name__ == "__main__":
    mem = HDItemMemory(seed=42)
    
    # Build vocabulary
    for i in range(12):
        mem.add_atom(f"p_{i}")
    for name in ["d_1/4", "d_1/8", "d_1/16", "d_1/32"]:
        mem.add_atom(name)
    for name in ["v_pp", "v_p", "v_f", "v_ff"]:
        mem.add_atom(name)
    for name in ["lead", "bass", "chord", "perc"]:
        mem.add_atom(name)
    for name in ["L_intro", "L_verse", "L_chorus", "L_bridge", "L_outro"]:
        mem.add_atom(name)
    for i in range(64):  # 4 bars × 16 positions
        mem.add_atom(f"m_{i}")
    for name in ["c_maj", "c_min", "c_dim", "c_aug"]:
        mem.add_atom(name)
    
    # Build a C major chord hypervector
    c_maj = bundle([mem.get("p_0"), mem.get("p_4"), mem.get("p_7")])
    
    # Voice: lead — scalar melody over C major
    scale_c_maj = [0, 2, 4, 5, 7, 9, 11]  # C Ionian
    lead_notes = []
    for pos in range(64):
        degree = scale_c_maj[pos % len(scale_c_maj)]
        lead_notes.append((
            pos,
            encode_note(mem.get(f"p_{degree}"), mem.get("d_1/8"), mem.get("v_f"))
        ))
    
    # Voice: chord — pad every 8 positions
    chord_notes = []
    for pos in range(0, 64, 8):
        chord_notes.append((
            pos,
            bundle([c_maj, mem.get("d_1/4"), mem.get("v_p")])
        ))
    
    # Voice: bass — root movement
    bass_notes = []
    for pos in range(0, 64, 4):
        bass_notes.append((
            pos,
            encode_note(mem.get("p_0"), mem.get("d_1/4"), mem.get("v_f"))
        ))
    
    voice_contents = {
        "lead": lead_notes,
        "chord": chord_notes,
        "bass": bass_notes
    }
    
    # Encode section
    section_hv = encode_section(voice_contents, mem.get("L_verse"), mem)
    
    # Decode and verify
    decoded = decode_section(section_hv, "L_verse", 
                             ["lead", "chord", "bass"], 64, mem)
    for voice, events in decoded.items():
        print(f"{voice}: {len(events)} events")
```

## References

- Kanerva, P. (2009). "Hyperdimensional Computing: An Introduction to Computing in Distributed Representation with High-Dimensional Random Vectors." *Cognitive Computation* 1, 139–159.
- Plate, T. A. (2003). *Holographic Reduced Representation: Distributed Representation for Cognitive Structures*. CSLI Publications.
- Gayler, R. W. (2003). "Vector Symbolic Architectures Answer Jackendoff's Challenges for Cognitive Neuroscience." *Proc. Joint Int. Conf. Cognitive Science*, 133–138.
- Kleyko, D. et al. (2021). "A Survey on Hyperdimensional Computing aka Vector Symbolic Architectures, Part I: Models and Data Transformations." *ACM Computing Surveys* 55(6), 1–40.
- Kleyko, D. et al. (2023). "A Survey on Hyperdimensional Computing aka Vector Symbolic Architectures, Part II: Applications." *ACM Computing Surveys* 55(9), 1–38.
- Frady, E. P. et al. (2022). "Computing on Functions Using Randomized Vector Representations." *arXiv:2109.03429*.
- Rahimi, A. et al. (2016). "A Robust and Energy Efficient Classifier Using Brain-Inspired Hyperdimensional Computing." *Proc. IEEE/ACM ISLPED*, 64–69.
- Komer, B. et al. (2019). "A Neural Representation of Grammar: Vector Symbolic Architectures for Context-Free Grammars." *Neurocomputing*.

## Candidate Code Path

```
generators/hd_composer.py
```

Implementation as a new generator module: `generators/hd_composer.py` containing `HDItemMemory`, `HDEncoder`, `HDDecoder`, and `HDComposer` classes that implement the VSA encoding pipeline and decode to `MusicEvent` objects. The `HDComposer.compose(section_plan, item_memory)` method returns a filled `UnitMatrix`.