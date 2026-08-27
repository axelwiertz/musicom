# Waveset Distortion Synthesis (WDS) (Method SP-054)

### **Source**
Waveset / wave-cycle distortion originates in the electroacoustic work of **Trevor Wishart**, formalized in his book ***Audible Design: A Plain and Easy Introduction to Practical Sound Composition*** (Orpheus the Pantomime, York, 1994; ISBN 978-0-9510313-3-2), Chapter 9 "Wave-set distortion", where he developed a family of transformations that take the waveform's own zero-crossing contour as the unit of musical structure — rather than the sample or the FFT frame. The technique was implemented and further documented by **Richard Dobson** in "An Introduction to the CDP DISTORT Functions" (Composers Desktop Project, 1996), which codified the operation set (REPEAT, OMIT, INTERPOLATE, AVERAGE, HARMONIC, DIVIDE, MULTIPLY, REVERSE, SHUFFLE, ENVEL, FRACTAL) and the notion of the "pseudo-wavecycle". These remain available in the open-source **CDP8** (Composers Desktop Project, github.com/ComposersDesktop/CDP8) under the DISTORT / DISTMORE / DIST / EXTEND modules. In the Musicom catalog, WDS fills the *waveform-driven, zero-crossing-aligned* granular gap: SP-016 granular synthesis uses fixed-duration grains, SP-037 PSOLA uses pitch-synchronous windows, and SP-050 spectral delay filters operate in the STFT domain — WDS is the only method whose grain boundaries are defined *by the signal's own zero-crossings*, making it inherently adaptive and non-linear.

### **Description**
Waveset distortion is a non-linear, time-domain granular method. The signal is partitioned into **wavesets** (a.k.a. pseudo-wavecycles): each waveset is the chunk of samples running from one zero-crossing, through a second, to a third — i.e. one complete positive-plus-negative excursion, three crossings total. These segment boundaries are *data-defined*, not imposed: a pure sine yields one waveset per period, while a complex or noisy signal yields a variable-length, variable-shape chain of wavesets. Once segmented, the waveset sequence is transformed as if it were a sequence of "grains" whose size adapts to the signal's own oscillation rate. Because the operations act on whole pseudo-cycles, they decouple three things that sample-level DSP conflates: (1) **number of cycles** (pitch/density), (2) **cycle shape** (timbre), and (3) **cycle order** (gesture). Repeating/omitting/resampling cycles changes pitch and time; averaging cycles changes timbre; shuffling/reversing cycles changes gesture — all without resynthesis artifacts like FFT phase-scatter. The result ranges from subtle timbral distortion and time-stretch to radical granular re-composition. **Complexity**: $O(N)$ segmentation (one pass for zero-crossings), then $O(N)$ per transform (each is an index permutation or a per-waveset resample).

### **Technical Mechanics**

**1. Zero-crossing segmentation.** For a discrete signal $x[n]$, a zero-crossing occurs between $n-1$ and $n$ when $\operatorname{sgn}(x[n-1])\ne\operatorname{sgn}(x[n])$ (samples exactly at zero belong to the crossing). Collect the crossing indices into a strictly increasing list $Z=[z_0, z_1, \dots, z_M]$. The CDP hierarchy is:

- **wave** (unipolar lobe): $x[z_i : z_{i+1}]$ — between two adjacent crossings.
- **waveset / pseudo-wavecycle** (full cycle): $w_j = x[z_{2j} : z_{2j+2}]$, length $\ell_j = z_{2j+2}-z_{2j}$, containing exactly two lobes and three crossings.
- **wave-group**: $G_k = [w_j,\dots,w_{j+N-1}]$ — $N$ consecutive wavesets treated as one unit (the "group-size" parameter).

For a pure sinusoid at frequency $f_0$ sampled at $f_s$, every waveset has $\ell_j \approx f_s/f_0$ and the segmentation recovers the true period; for inharmonic/noisy material $\ell_j$ varies wildly, and the waveset count per second is *at least* $f_0$ but usually much higher.

**2. Frequency multiply / divide (pitch).** Because a waveset is (approximately) one cycle, duplicating or discarding whole wavesets changes the *cycle rate*:

- **Repeat each waveset $r$ times** (time expansion / subharmonic): $\hat{x} = \bigoplus_{j} w_j^{\oplus r}$. Each cycle now occupies $r$ times its original duration, so the local fundamental divides by $r$: $f_{out} \approx f_{in}/r$. CDP DISTREP (timestretch) is $r$ chosen to fill a target duration; $r=2$ yields octave-down subharmonics.
- **Omit every $k$-th waveset** (time contraction): delete the set $\{w_{km}\}$; the file shortens by the total length of the deleted wavesets while surviving cycles play at their original rate. Pure time-contraction of the pitch-bearing material.
- **Resample each waveset to $1/m$ its duration** (frequency multiply): $w'_j[k] = w_j\!\left[\operatorname{round}\!\left(\tfrac{k\,\ell_j}{m}\right)\right]$, $k=0..\ell_j/m$. Each cycle plays $m\times$ faster, so $f_{out} \approx m\,f_{in}$; CDP DISTMORE DOUBLE is $m=2$. This is the waveset analogue of transposition *without* FFT phase-vocoder smearing, at the cost of waveset-boundary discontinuity.

**3. Timbre transforms.**

- **Averaging (DISTORT AVERAGE):** time-normalize $N$ consecutive wavesets to a common length (linear resample), then replace the group by the ensemble mean $\bar{w}[k]=\tfrac1N\sum_j w_j[k]$. This suppresses cycle-to-cycle variation — noise, vibrato, and transient jitter average out, leaving the "mean cycle shape": a smoother, more pitched, more static timbre.
- **Harmonic superposition (DISTORT HARMONIC):** add scaled, time-compressed copies of each waveset onto itself: $y[n]=\sum_h a_h\, w_j\!\left[\operatorname{round}\!\left(\tfrac{h\,(n-z_{2j})}{\ell_j}\right)\right]$ for $n\in[z_{2j},z_{2j+2})$. Reinforces/creates harmonics directly in the time domain.
- **Envelope (DISTORT ENVEL):** multiply each group by an imposed amplitude envelope $e[k]$: $w_j[k]\leftarrow e[k]\cdot w_j[k]$, reshaping attack/decay per group.
- **Fractal (DISTORT FRACTAL):** superimpose down-scaled copies of each waveset onto itself at multiple scales (self-similar detail inside each cycle).

**4. Gesture transforms.**

- **Reversal:** $\tilde w_j[k]=w_j[\ell_j-1-k]$ (reverse each cycle or each group).
- **Shuffling:** apply a permutation $\pi$ to the waveset (or group) order: $\hat{x}=\bigoplus_j w_{\pi(j)}$. Deterministic (sort by length, by peak amplitude, by average zero-crossing rate) or random.
- **Interpolation (DISTORT INTERPOLATE):** repeat wavesets to stretch time, but crossfade adjacent copies $\hat x[n]=(1-\alpha)\,x[n-d_j]+\alpha\,x[n-d_{j+1}]$ across the overlap so repeated cycles blend smoothly instead of clicking.

**Complexity**: segmentation $O(N)$; every transform is a re-indexing, a concatenation, or a per-waveset resample, all $O(N)$; averaging/harmonic $O(N)$ with per-group resampling. Memory $O(N)$ (the waveset index list is the only auxiliary structure).

### **Implementation Requirements (Python / NumPy)**

```python
import numpy as np

def waveset_indices(x, min_len=4):
    """Zero-crossing positions: strictly increasing crossing indices."""
    s = np.sign(x)
    crossing = np.flatnonzero(s[1:] != s[:-1]) + 1
    if len(crossing) < 2:
        return np.array([0, len(x)])
    return crossing

def segment_wavesets(x, crossing):
    """Split x into full cycles (wavesets): crossing[2j] -> crossing[2j+2]."""
    c = crossing
    if len(c) % 2 == 0:
        c = c[:-1]  # need an odd count to pair full cycles cleanly
    return [x[c[i]:c[i + 2]] for i in range(0, len(c) - 2, 2)]

def repeat_wavesets(x, r):
    """Repeat each waveset r times -> time expansion, f_out ~ f_in / r."""
    ws = segment_wavesets(x, waveset_indices(x))
    return np.concatenate([np.tile(w, r) for w in ws])

def omit_wavesets(x, k):
    """Delete every k-th waveset -> time contraction."""
    ws = segment_wavesets(x, waveset_indices(x))
    keep = [w for i, w in enumerate(ws) if (i + 1) % k != 0]
    return np.concatenate(keep) if keep else x

def resample_waveset(w, m):
    """Play each cycle m times faster -> pitch x m."""
    L = int(np.ceil(len(w) / m))
    idx = np.clip(np.round(np.arange(L) * m).astype(int), 0, len(w) - 1)
    return w[idx]

def multiply_wavesets(x, m):
    ws = segment_wavesets(x, waveset_indices(x))
    return np.concatenate([resample_waveset(w, m) for w in ws])

def average_wavesets(x, N):
    """Replace each group of N cycles by their mean cycle shape."""
    ws = segment_wavesets(x, waveset_indices(x))
    out = []
    for i in range(0, len(ws) - N + 1, N):
        group = ws[i:i + N]
        L = max(len(w) for w in group)
        norm = [np.interp(np.linspace(0, 1, L), np.linspace(0, 1, len(w)), w)
                for w in group]
        out.append(np.mean(norm, axis=0))
    return np.concatenate(out)

def harmonic_wavesets(x, amps=(1.0, 0.5, 0.25)):
    """Superimpose time-compressed harmonics of each cycle onto itself."""
    ws = segment_wavesets(x, waveset_indices(x))
    out = []
    for w in ws:
        L = len(w)
        acc = np.zeros(L)
        for h, a in enumerate(amps, start=1):
            idx = np.clip(np.round(np.arange(L) * h).astype(int), 0, L - 1)
            acc += a * w[idx]
        out.append(acc)
    return np.concatenate(out)

def reverse_wavesets(x):
    ws = segment_wavesets(x, waveset_indices(x))
    return np.concatenate([w[::-1] for w in ws])

def shuffle_wavesets(x, rng=None):
    """Randomly reorder wavesets (granular scramble)."""
    rng = rng or np.random.default_rng()
    ws = segment_wavesets(x, waveset_indices(x))
    rng.shuffle(ws)
    return np.concatenate(ws) if ws else x
```

**Tooling**: NumPy alone suffices; `np.flatnonzero` for crossings, `np.tile`/`np.concatenate` for repetition, `np.interp` for resampling/averaging. For real-time use, stream the zero-crossing detector and keep a small ring buffer. The musicom engine supplies the symbolic UnitMatrix + zero-drift MIDI upstream; WDS consumes a *rendered audio buffer* (from FluidSynth or any SP-001..SP-042 engine) as its input and emits a transformed buffer per voice.

### **Worked Example (Sub-Octave + Brighten Chain)**
1. Render a bass line voice to mono buffer `b` (FluidSynth or SP-029 subtractive).
2. `b_sub = repeat_wavesets(b, 2)` → one octave down, doubled duration (sub-bass weight).
3. `b_bright = harmonic_wavesets(b_sub, amps=(1.0, 0.6, 0.3))` → add 2nd/3rd harmonics for presence.
4. Crossfade the two buffers over a section boundary (parameter interpolation of $r$ and $a_h$).

### **Musical Elements Framework**

- **PITCH**: The zero-crossing structure *is* the pitch carrier. Repeat = subharmonic division ($f/2$ = octave down, $f/3$ = fifth+octave down); resample each waveset = harmonic multiplication ($2f$ = octave up); omit/insert groups = macro pitch gestures. Crucially, the pitch effect is *signal-contour-dependent*: a pure tone transposes cleanly, a complex tone transposes its *formant/spectral-average* differently than its perceived fundamental, and noise barely changes pitch at all — Wishart exploits this for timbre-selective "pitch colouring".
- **RHYTHM**: Each waveset is a grain with its own duration $\ell_j$; the sequence $\{\ell_j\}$ is a data-defined rhythm stream. Group-size $N$ + envelope impose a metrical grid (group = beat/bar); repeating/omitting whole groups produces meter; the ratio of waveset-rate to group-rate is the groove.
- **HARMONY**: Harmonic superposition (DISTORT HARMONIC) builds harmonic spectra directly; averaging shifts the spectral centroid toward the mean-cycle spectrum; multiply/divide retune the partial structure of inharmonic material. Waveset operations are the time-domain counterpart of harmonic transposition but act on *whole cycles* rather than partials.
- **STRUCTURE**: Macro-form = time-varying choice of function + parameters. Section A = subharmonic repeat (dark, dense, slow); Section B = harmonic brighten (resample ×2, add harmonics); Section C = shuffle/reverse (gestural scramble); a "recap" repeats A's exact function to return. Group-size trajectories (e.g. $N$ growing then collapsing) give large-scale shape.
- **TEXTURE**: Waveset density (cycles/sec), group size, and shuffle/repeat rates produce the full granular continuum: $N=1$, high repetition = gritty lo-fi; large $N$ + averaging = smooth, spectral-static pad; shuffle = pointillistic cloud. The grain is adaptive — dense in fast/spiky passages, sparse in slow ones — giving a "self-timed" texture no fixed-grain method (SP-016) achieves.

### **UnitMatrix Integration (Voices and Sections)**

- **Rows (Voices)**: Each voice $v$ is rendered to a mono buffer (FluidSynth or its synthesis engine), then passed through its own WDS instance with a per-voice parameter set. Voice 1 (lead) = mild resample vibrato ($m(t)$ slow LFO); Voice 2 (bass) = repeat ×2 for sub-octave weight; Voice 3 (pad) = averaging $N{=}8$ for smooth sustained texture; Voice 4 (percussion) = omit/shuffle for broken-beat granular hits. Per-voice independent segmentation keeps each row's pitch/harmony identity intact.
- **Columns (Sections)**: Each section $s$ prescribes a function recipe (which transform + parameter automation), so the columns become a *timbral macro-form*: A = repeat/omit (sparse→dense), B = harmonic/resample (bright climax), C = average/reverse (cool static). Section joins are either hard function switches or parameter crossfades (interpolating $m$, $N$, $r$).
- **Cells** $U_{v,s}$:
  - `{PITCH}`: per-cell resample factor $m$ (or repeat factor $r$) — transposes that cell's rendered audio by cycle-rate scaling.
  - `{RHYTHM}`: per-cell group-size $N$ and repeat/omit pattern — sets the grain rhythm within the cell.
  - `{HARMONY}`: per-cell harmonic-superposition weights $\{a_h\}$ — spectral brightening of the chord at that cell.
  - `{TEXTURE}`: per-cell waveset density target (via omission rate / shuffle) — controls the granular cloud thickness.
- **Mapping Flow**:
  1. Compose + fill the UnitMatrix; validate zero-drift; export MIDI via the musicom engine (symbolic layer).
  2. Render each voice mono through its assigned synthesis engine (SP-001..SP-042).
  3. Apply the per-cell/section WDS function recipe to each voice buffer (segment → transform → concatenate).
  4. Sum voices; post-process (SP-007 EQ, SP-008 DRC); export audio or spatialize (SP-021/SP-034/SP-043).

### **Pitfalls**

1. **DC offset / no zero-crossings** → a DC-shifted or all-positive buffer has no (or one) crossing → waveset undefined. Fix: high-pass / DC-remove the buffer first (subtract mean or first-order HPF at ~20 Hz).
2. **Spurious micro-wavesets in silence** → low-level noise near zero crosses thousands of times, producing 1–2 sample wavesets that make transforms unpredictable. Fix: amplitude gate + minimum waveset length (e.g. $<4$ samples merge into the neighbour), and LPF before segmentation.
3. **Boundary clicks** → reversal/repeat/resample create discontinuities at waveset seams (mild transient distortion is inherent and often desired — Dobson's "glitch" note). Fix: crossfade adjacent wavesets (INTERPOLATE) or apply a gentle LPF post-transform when clean output is wanted.
4. **Phase-relationship dependence** → two signals identical except partial phases yield different waveset segmentations, hence different outputs for the same transform. This is a property, not a bug, but it means results are *not reproducible across phase variants* — pin the source buffer; do not expect identical output from a re-rendered input.
5. **High-frequency content = tiny wavesets** → a bright signal has few-sample cycles that resample/average into aliased garbage. Fix: strong LPF (CDP FILTER LOHI) before processing; use the highest sample rate available.
6. **Naive per-sample Python too slow** → looping over samples in Python for segmentation is $O(N)$ but slow in wall-clock. Fix: vectorize with `np.flatnonzero` for crossings and `np.tile`/`np.concatenate` for transforms; JIT hot loops with Numba if streaming.
7. **Sparse/staccato source → sparse waveset stream** → a gappy input yields a gappy waveset chain with silent stretches, reproducing the "staccato" failure mode of sparse methods (011/032). Fix: per the Method Hybridization rule, layer a continuous fill (026 DPSM pad, sustained string) under the waveset-transformed sparse layer.

### **Comparison With Related Methods**

| Method | Grain definition | Grain size | Pitch control | Domain | Artifacts |
|---|---|---|---|---|---|
| Granular (SP-016) | Fixed window | User-set | Resample/grain rate | Time | Grain-smeared |
| PSOLA (SP-037) | Pitch-synchronous window | f0 period | Window shift | Time | Phase at seams |
| Phase Vocoder (SP-026) | STFT frame | FFT size | Bin shift | Frequency | Phase-scatter/smear |
| **Waveset (SP-054)** | **Zero-crossing (adaptive)** | **Signal-defined** | **Cycle repeat/omit/resample** | **Time (non-linear)** | **Boundary transients (often desired)** |

### **References**

- Wishart, T. (1994). *Audible Design: A Plain and Easy Introduction to Practical Sound Composition.* Orpheus the Pantomime, York. Chapter 9, "Wave-set distortion."
- Wishart, T. (1996). *On Sonic Art.* 2nd ed., Harwood Academic Publishers. (Wave-cycle / waveset transformation context.)
- Dobson, R. (1996). "An Introduction to the CDP DISTORT Functions." Composers Desktop Project. cdp-org.uk.
- Composers Desktop Project (2023). *CDP8 Reference — DISTORT / DISTMORE / DIST / EXTEND modules.* github.com/ComposersDesktop/CDP8. ("Wavesets: technical description of a pseudo-wavecycle," cdistort.htm.)
