# Sound Production Method SP-144 — PADsynth Spectrum-to-Wavetable Synthesis (PADS)

> Layer: **absolute** (sound production — LAYER_ARCHITECTURE.md). Candidate code path: `sound/synthesis/padsynth.py` (NumPy table builder + minimal loop player).
> Sources fetched live 2026-11-18: Nasca's "PADsynth algorithm" page (via web.archive.org — the live sourceforge.io path 404s), ZynAddSubFX repo (tag 2.4.4 `PADnote.cpp`, master `OscilGen.cpp`), Wikipedia "ZynAddSubFX", `ryukau/padsynth_kde`, `nyanpasu64/padsynth` — cached in `/opt/data/_web144_pads/`.

### Source

- **Nasca Octavian Paul, "PADsynth algorithm" (2007).** https://zynaddsubfx.sourceforge.io/doc/PADsynth/PADsynth.htm (fetched live 2026-11-18 via web.archive.org/web/2024id_/…; the live path now 404s). The canonical description: basic + extended pseudocode, Gaussian harmonic-profile function, input/output spec, random-phase step, tips (random start, stereo N/2 offset, per-pitch wavetables, base_frequency resampling), public-domain C/C++ implementations. Released **public domain**.
- **ZynAddSubFX (GPL)** — original implementation ("PADsynth module"). Tag 2.4.4 `src/Synth/PADnote.cpp` (PADnote table player); master `src/Synth/OscilGen.cpp` (spectrum-mode construction, `Prand` phase randomness, `ADvsPAD` flag). Default table size 262144 @ 44100 Hz.
- **Wikipedia "ZynAddSubFX"** (fetched 2026-11-18): "an original algorithm used to generate wavetables in the PADSynth engine" — attribution corroborated.
- **Independent implementations** (fetched 2026-11-18): `ryukau/padsynth_kde` (Python/NumPy; KDE-profiled variant — cites the canonical page), `nyanpasu64/padsynth` (Rust resynthesis variant; `Harmonic(stdev)` mode, seedable, `random_amplitudes`, chord mode), `mmontag/padsynth-js` (JavaScript).
- **Novelty check (2026-11-18, before entry):** `padsynth`=0, `PADsynth`=0, `Nasca`=0, `base_frequency`=0; `harmonic profile`=2 (TWEMS organ prose only), `bandwidth.*cents`=3 (SP-050 prose only), `detuned.*band`=4 (SP-141 playback prose only), `spectrum.*IFFT`=2 (SP-055 Hilbert / SP-056 Walsh — unrelated). Wavetable family present: SP-041 (playback), SP-039 (frame IFFT additive), SP-116 (closed-form additive), SP-022 (terrain), SP-018 (scanned). **No table-construction-from-detune-bands method → SP-144 novel.**

### Layer

**absolute** (sound production — LAYER_ARCHITECTURE.md). **Synthesis Engines** — wavetable-construction algorithm. Consumes a symbolic harmonic spec (amplitudes $A[h]$, bandwidth $bw$, optional $relF$ ratios) → emits a static, perfectly looped wavetable; any table-scanning player renders it at pitch. No composition decisions, no events, no timing authority. Stage order: **PADS table build → table player (source) → per-row filter (SP-007/SP-029) → spatialize (SP-021/SP-053/SP-119) → space/tail (SP-009/SP-032/SP-140) → bus dynamics (SP-008/SP-107) → loudness (SP-126) → dither (SP-122)**.

### Description

PADSynth builds one large, perfectly looped wavetable from a user-defined harmonic spectrum via a **single inverse FFT** — no oscillators, no filters, no overlap-add. Each harmonic is a *band* of closely spaced frequencies, not one sine: the composer gives per-harmonic amplitude $A[h]$ and a bandwidth in cents (growing with harmonic number — natural ensembles detune proportionally to frequency), and every bin inside each band gets a **uniform random phase**. The random phases are never heard as noise (all bins sit inside the harmonic's band) but they make the looped table carry continuous internal beating — each period differs microscopically from the next, exactly like $N$ detuned voices — so the sound evolves on its own with **zero LFOs and zero playback modulation**. Because the phase pattern repeats with the loop, the evolution is perfectly periodic (loop period $= N/f_s$). Result: the classic ZynAddSubFX pad/choir/ensemble voice — huge, organic, slow-moving, perfectly loopable. The extended algorithm adds $relF(h)$ (inharmonic overtone ratios → bells/metallic) and $bwscale$ (bandwidth growth law); the *base_frequency* trick resamples the amplitude array per pitch so the spectral envelope stays tied to **absolute frequency** across the keyboard.

### Technical Mechanics

**1. Inputs.** $N$ = wavetable length (power of two, "like 262144"); $f_s$ = sample rate; $f$ = fundamental of the table; $bw$ = bandwidth of the first harmonic in cents (> 0); `number_harmonics` < $f_s/f$; $A[1..\text{number\_harmonics}]$ = amplitudes.

**2. Spectrum assembly.** For each harmonic $nh$:

$$bw_{Hz}(nh) = (2^{bw/1200} - 1)\, f\, nh, \qquad bwi = \frac{bw_{Hz}}{2 f_s}, \qquad fi = \frac{f\, nh}{f_s}$$

$$x = \frac{k/N - fi}{bwi}, \qquad \mathrm{profile}(x) = \frac{e^{-x^2}}{bwi}, \qquad \mathrm{freq\_amp}[k] \mathrel{+}= \mathrm{profile}(x)\cdot A[nh]$$

The $1/bwi$ factor keeps each harmonic's energy bandwidth-invariant: $\int \mathrm{profile} = \sqrt{\pi}$ for any $bwi$. Bandwidth in Hz grows linearly with harmonic number → wide bands merge into a noise band near Nyquist (normal, not to be avoided).

**3. Phases + one IFFT.**

$$\varphi_k \sim \mathcal{U}(0, 2\pi), \qquad X[k] = \mathrm{freq\_amp}[k]\, e^{j\varphi_k}, \qquad \mathrm{smp} = \mathrm{IFFT}(X), \qquad \mathrm{normalize}(\mathrm{smp})$$

No windowing, no overlap-add; periodic spectrum → perfectly looped time signal by construction.

**4. Extended algorithm.** $relF(nh)$ = relative overtone frequency ($=nh$ → harmonic; inharmonic → bells); $bwscale$ = bandwidth growth law:

$$bw_{Hz} = (2^{bw/1200}-1)\, f\, relF(nh)^{bwscale}, \qquad fi = f\, relF(nh)/f_s$$

$relF(nh){=}nh$, $bwscale{=}1$ ⇒ basic algorithm exactly.

**5. Playback.** Phase accumulator at $f_0$: $\varphi \mathrel{+}= f_0/f_s$ per sample; linear/cubic interpolation. Doc tips: random start per note-on; stereo = same table offset $N/2$ L/R; per-pitch wavetable bank (nearest table — anti-aliasing); base_frequency resampling of $A[]$ by $f_{base}/f_0$ (spectrum constant in Hz, not harmonic number).

**6. Complexity.** Build: $O(N \cdot H)$ + one $O(N \log N)$ IFFT, offline. Playback: $O(1)$ per sample. Memory: 1 MB float32 per 262144-sample table. Pure NumPy; deterministic per seed; no training, no external data.

### Python implementation sketch

```python
# sound/synthesis/padsynth.py — SP-144 PADSynth table builder + loop player (sketch)
import numpy as np


def padsynth_table(N, fs, f, bw_cents, amps, relF=None, bwscale=1.0, seed=0):
    """Build a perfectly looped wavetable from a harmonic spectrum (Nasca 2007).

    amps   : array of per-harmonic amplitudes A[1..H]  (e.g. 1/sqrt(h))
    relF   : overtone ratios; None = harmonic series relF(h)=h
    bw_cents: bandwidth of the FIRST harmonic in cents (>0)
    Returns float32 wavetable of length N, peak-normalized to 1.0.
    """
    rng = np.random.default_rng(seed)
    H = len(amps)
    relF = np.arange(1, H + 1) if relF is None else np.asarray(relF, dtype=float)
    bins = np.arange(N // 2) / N                    # normalized bin freqs (cyc/samp)
    spec = np.zeros(N // 2)
    for h in range(1, H + 1):
        fh = f * relF[h - 1]                        # harmonic freq (Hz)
        bw_hz = (2.0 ** (bw_cents / 1200.0) - 1.0) * f * relF[h - 1] ** bwscale
        bwi = bw_hz / (2.0 * fs)                    # Gaussian width (normalized)
        fi = fh / fs                                # harmonic center (normalized)
        x = (bins - fi) / bwi
        spec += np.exp(-x * x) / bwi * amps[h - 1]  # energy invariant vs bandwidth
    phase = rng.uniform(0.0, 2.0 * np.pi, N // 2)
    phase[0] = 0.0                                  # no DC
    X = spec * np.exp(1j * phase)
    X = np.concatenate([X, [0j], np.conj(X[1:][::-1])])  # + Nyquist bin + mirror -> N bins
    smp = np.fft.ifft(X).real
    return (smp / np.max(np.abs(smp))).astype(np.float32)


def play_table(table, fs, f0, n_samples, start=None, interp="linear"):
    """Phase-accumulator loop player. start=None -> random table position."""
    N = len(table)
    if start is None:
        start = np.random.default_rng().uniform(0.0, 1.0)
    idx = start * N
    inc = f0 / fs * N
    out = np.empty(n_samples)
    if interp == "linear":
        for n in range(n_samples):
            i = int(idx) % N
            frac = idx - int(idx)
            out[n] = table[i] * (1 - frac) + table[(i + 1) % N] * frac
            idx += inc
    return out

# --- UnitMatrix dispatch (workflows/musicom_workflow.py produce "SP-144") ---
# produce(midi_path, method="SP-144", params={
#   "rows": {"pad":   {"N": 262144, "bw_cents": 40, "amps": "1/sqrt(h)", "seed": 7},
#            "choir": {"N": 262144, "bw_cents": 80, "amps": "1/h^1.2",  "seed": 11}},
#   "player": {"interp": "linear", "random_start": True},
#   "columns": {"A": {"bw_cents": 25}, "B": {"bw_cents": 70}}})
# row pipeline: padsynth_table (offline, once) -> play_table per MusicEvent -> per-row DSP
```

### Musical Elements Framework

- **PITCH** — the table's fundamental $f$ IS the pitch anchor; transposition = reading the table at another rate (phase accumulator), shifting the whole spectrum *including* the detune bands (relative detune preserved → ensemble character survives transposition). base_frequency resampling keeps the absolute envelope fixed in Hz across the keyboard.
- **RHYTHM** — none intrinsic: static periodic loop; internal beating period $N/f_s$ (262144/44100 ≈ 5.94 s) is the longest timbral "rhythmic" event. Onsets/decay delegated to the player envelope or downstream dynamics (SP-008/SP-107). Loop-seam safety automatic (perfect loop, sample-exact — the zero-drift audio analogue).
- **HARMONY** — $A[]$ is a one-note spectral chord; choir = broad bands over odd+even partials, bell = inharmonic $relF$ ratios; multiple fundamentals' partials can be summed into ONE table (chord mode — single-note chord timbre, spectral analogue of SP-097's subharmonic stacks).
- **STRUCTURE** — table = timbre object, not form object; structure enters via per-section table selection (column change = timbre change) and the evolution timescale $N/f_s$; per-octave banks act as a registral macro-form.
- **TEXTURE** — the defining output: $bw$ (cents) is the single texture knob — $bw{\to}0$ pure sine-like "single voice", ~10–50 cents classic detuned-ensemble pad, large $bw$ choir/noise-band shimmer. Random phases give "many-voices" motion with no chorus effect; the loop repeats it exactly.

### UnitMatrix Integration

**Voices = rows = one table per row (or per row-register).** Row $v$ params: `{N, fs, f_base, bw_cents, A[], relF[], bwscale, seed, table_bank, player {interp, random_start}}`. Timbre identity = harmonic spec + bandwidth; seed fixes the phase pattern → same spec + seed = byte-identical table/audio (deterministic, provenance-friendly).

**Sections = columns = table/parameter switches.** Column $j$: `{bw_cents_override, A[]_override, seed_j, table_bank_j}` — a column change is a timbre change. Seam safety: held notes render click-free (phase accumulator continues through the perfect loop); table *swaps* land on the section grid — choose $N$ so $N/f_s$ divides the section's sample count (or resample).

**Cells = MusicUnit.** Cell $(v,j)$: `MusicEvent` (pitch, start/end ticks) drives the player — pitch → table rate $f_0/f_{base}$, duration → sample count; `random_start` per note-on (doc tip) so repeated cells don't sound identical. Cell-level edits = local spectral surgery (per-cell $bw$/$A[]$ overrides). Dispatch: `produce(midi_path, method="SP-144", ...)`; table build offline once per row; fixed-rate PCM output — resample before sample-count-sensitive stages (SP-050 GCD grids) or re-quantize to the tick grid.

### Pitfalls

1. **Loop-period math** — loop period = $N/f_s$; notes shorter truncate mid-evolution (fade out); exact loop alignment needs $N/f_s$ dividing the section sample count.
2. **bw cents is relative, Hz is absolute** — basic-algorithm bandwidth scales with harmonic number (constant relative detune); fixed-Hz bands need relF/bwscale bending; at low fundamentals a 40-cent band ≈ 1.3 Hz ≈ one bin at small $N$ — raise $N$.
3. **Keep the 1/bwi normalization** — dropping it makes wide-band harmonics louder (violates the doc's energy-invariance rule).
4. **DC and Nyquist bins** — `freq_amp[0]=0` (no DC thump); keep energy off $k=N/2$ (breaks conjugate symmetry for real IFFT).
5. **Random start is load-bearing** — playing always from index 0 gives identical attacks and can expose a table-head transient.
6. **Aliasing at high octaves** — table is band-limited only to its own Nyquist; transpose up → foldback. Fixes: per-octave table bank, or base_frequency resampling of $A[]$.
7. **Seed determinism** — phase pattern (beating structure) fixed by seed; record in provenance; different seed = different "take".
8. **Neighbour audit** — SP-041 BLW-MI = *playback* of pre-computed tables (PADS is the *construction* algorithm those players consume); SP-039 = per-frame IFFT + overlap-add *resynthesis* (PADS: one IFFT, no OLA, designed spectrum); SP-116 DSFS = closed-form time-domain summation (no IFFT, no detune bands); SP-022 terrain / SP-018 scanned = other table-scanning sources; SP-141 SOSS = detuned saw *stack playback* (PADS bakes the detune into one static table). **SP-144 PADS = spectrum→wavetable construction with per-harmonic Gaussian detune bands + random phases — the missing table-building member of the wavetable family.** Repo: `sound/synthesis/padsynth.py` (new; NumPy-only; no training, no external data).

### References

1. Nasca, O. P. (2007). "PADsynth algorithm." https://zynaddsubfx.sourceforge.io/doc/PADsynth/PADsynth.htm (public domain; archived 2026-11-18).
2. ZynAddSubFX — PADsynth module. https://github.com/zynaddsubfx/zynaddsubfx (GPL; tag 2.4.4 `src/Synth/PADnote.cpp`, master `src/Synth/OscilGen.cpp`).
3. Wikipedia. "ZynAddSubFX" (fetched 2026-11-18) — PADSynth engine attribution.
4. ryukau (2020s). padsynth_kde — https://github.com/ryukau/padsynth_kde (Python/NumPy, KDE-profiled variant).
5. nyanpasu64. padsynth — https://github.com/nyanpasu64/padsynth (Rust resynthesis variant: Harmonic(stdev), seedable, chord mode).
6. mmontag. padsynth-js — https://github.com/mmontag/padsynth-js (JavaScript port).
