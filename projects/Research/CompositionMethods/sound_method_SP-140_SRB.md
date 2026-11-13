# Sound Production Method SP-140 — Schroeder Reverberator (Classic Comb/Allpass Network) (SRB)

### Source

- **Schroeder, M. R. (1962). "Natural Sounding Artificial Reverberation."** *Journal of the Audio Engineering Society* 10(3), 219–223 — the canonical design: a parallel bank of feedback comb filters (the resonance engine) summed into a series chain of allpass filters (the diffuser). JAES articles of this era carry no DOI (no Crossref record; cited from the Dattorro 1997 reference list and the SP-032/SP-071 entries).
- **Schroeder, M. R. (1961). "'Colorless' Artificial Reverberation."** *IRE Transactions on Audio* AU-9(5), 192–197. DOI 10.1109/TAU.1961.1166351 — the allpass filter IS the "colorless" element: unit magnitude at every frequency, pure phase dispersion. (Verified via Crossref.)
- **Schroeder, M. R. (1970). "Digital Simulation of Sound Transmission in Reverberant Spaces."** *JASA* 47(2), 424–431. DOI 10.1121/1.1911541 — digital implementation of the network and the backward-integration (energy-decay) method used here to measure RT60. (Verified via Crossref.)
- **Jot, J.-M. (1992). "An Analysis/Synthesis Approach to Real-Time Artificial Reverberation."** *Proc. ICASSP-92*, vol. 2, 221–224. DOI 10.1109/ICASSP.1992.226080 — frequency-dependent comb loops (one-pole damping in the feedback path); the SRB `damp` control follows this. (Verified via Crossref.)
- **Moorer, J. A. (1979). "About This Reverberation Business."** *Computer Music Journal* 3(2), 16–28 — the canonical parameter set used in SRB: combs 29.7/37.1/41.1/43.7 ms at g = 0.77, allpasses 5.0/1.7 ms at g = 0.7 (the classic "Schroeder/Moorer" preset).
- **Dattorro, J. (1997). "Effect Design, Part 1: Reverberator and Other Filters."** *Journal of the Audio Engineering Society* 45(9), 660–684 — stability and design analysis of comb+allpass networks (also the source of SP-071 DPR's tank).
- **Smith, J. O. (2023). *Physical Audio Signal Processing*.** Stanford CCRMA online book — comb-filter and allpass-filter chapters that the reverberator section builds on. Cached: `_web140/ccrma_Artificial_Reverberation.html`.
- **Wikipedia: "Reverberation"** — RT60/Sabine context and Schroeder's 1965 energy-integration measurement method (used in check 4). Cached: `_web140/wiki_reverb.html`.
- **Novelty check (2026-11-13):** `grep -ci` on `methods_db.md` **before** entry: `comb filter reverb` = 0, `quasi-stereo` = 0, `allpass diffuser` = 0, `comb+allpass` = 2 (both prose inside SP-071 DPR's comparison table), `Schroeder` = 8 (all prose: SP-032 FDN's history/references, SP-071 DPR's references, SP-075 ISRA's Schroeder-frequency prose, SP-129 TCCR's Atal–Schroeder "apparent source translator" — never a method). **No SP method documents the classic comb+allpass reverberator.** Repo antecedents: `sound/effects/reverb.py` already implements the Schroeder/Moorer topology as `AlgorithmicReverb` (8 parallel combs → 4 series allpasses, interleaved L/R comb pairs, COMB_DELAYS 1117–1617 samples, ALLPASS_DELAYS [557, 441, 341, 225], allpass feedback 0.5 — a production variant of the same network); `sound/effects/room_reverb.py` carries the low-level Schroeder `comb()`/`allpass()` primitives for its diffuse tail (lines 41–57). SRB is the DB's first *algorithmic reverb-class* entry for the 1962 topology itself. Adjacent-but-different: **SP-032** FDN (N feedback delay lines + unitary matrix — the generalized successor, O(N)/sample); **SP-071** DPR (plate: figure-eight tank + 7 taps); **SP-058** DWSR (dispersive spring waveguide, allpass chain but a *spring* model); **SP-009** (convolution with measured IRs); **SP-075** ISRA (image-source geometric early field); **SP-013** (a single modulated feedback delay line — slap/flanger class, not a reverb network); **SP-050** SDF (STFT-domain per-bin delays — spectral, not sample-domain).
- **Verified prototype for this document:** `_web140/verify_sp140.py`, log `_web140/verify_sp140_output.txt`, audio `_web140/sp140_demo.wav` (2.20 s stereo, 97 020 frames/ch, 388 124 B) — **13/13 checks pass** (all numbers quoted below are measured).

### Layer

**absolute** (sound production — LAYER_ARCHITECTURE.md). SRB consumes rendered per-voice or bus audio buffers and emits the wet (and mixed) tail — it holds no timing authority, emits no events, and decides nothing about composition: it is a post-processing / DSP effect in the space stage of the render chain. Candidate code path: `sound/effects/reverb.py` (existing `AlgorithmicReverb`, Schroeder/Moorer topology — extend with the canonical 4+2 Moorer preset, quasi-stereo cross-feed option, and freeze/damp section columns), low-level primitives `comb()`/`allpass()` in `sound/effects/room_reverb.py`, dispatched from `workflows/musicom_workflow.py::produce(method="SP-140", ...)`. It is the classic ancestor that SP-032 FDN generalizes and the "small-room comb+allpass tail" that SP-071 DPR's comparison table already attributes to `room_reverb.py`.

### Description

A cathedral's tail without the cathedral: four feedback comb filters (each a delay line feeding back with gain g, producing a geometric echo train whose magnitude spectrum is a comb of resonances spaced $f_s/m$ Hz apart) run in parallel with *incommensurate* delay lengths so their resonance peaks never coincide; their outputs sum and pass through two series allpass filters — unit magnitude at every frequency, pure phase dispersion — that multiply the echo density without adding coloration (the "colorless" property). That is Schroeder's 1962 recipe, the template every later algorithmic reverb (including SP-032 FDN and SP-071 DPR) descends from. Design criteria: ≥ 4 combs with mutually-prime-ish delays, ≥ 2 allpasses, every loop gain < 1. Cost: **O(1) per sample** — six delay lines total, the cheapest dense reverb in the DB (contrast SP-032's O(N) matrix, SP-009's O(L) convolution). Character: smooth, dense, warm "classic studio" tail; the budget workhorse for hall/room spaces, and the exact topology already shipped in `sound/effects/reverb.py`.

SRB is that network, discretized per buffer with sample-count preservation and deterministic reset per note/buffer.

### Technical Mechanics

**1. Feedback comb (the resonance engine).**
$$y[n] = x[n] + g\,y[n-m], \qquad H(z) = \frac{1}{1 - g\,z^{-m}}$$
Impulse response: decaying impulses at every $k\cdot m$ samples with per-echo factor $g$; magnitude peaks at $f_k = k\,f_s/m$ spaced $f_s/m$ Hz apart (the "comb" — metallic alone, colorless in an incommensurate bank). RT60 of one comb follows from $g^k = 10^{-3}$:
$$T_{60} = \frac{3\,m}{f_s\,|\log_{10} g|}$$
Verified: echo spacing exactly $m$ = 1310 samples (29.7 ms), per-echo decay exactly 0.770000 (checks 1–2).

**2. Schroeder allpass (the colorless diffuser).**
$$y[n] = -g\,x[n] + x[n-m] + g\,y[n-m], \qquad H(z) = \frac{z^{-m} - g}{1 - g\,z^{-m}}$$
On the unit circle $|z^{-m} - g| = |1 - g\,z^{-m}|$ for all $\omega$, so $|H(e^{j\omega})| = 1$: **zero spectral coloration, pure phase dispersion**. Single-delay-line implementation: store $v[n] = x[n-m] + g\,y[n-m]$, output $y[n] = v[n] - g\,x[n]$. Verified: max |H| deviation **0.0000 dB** over 20 Hz–20 kHz (check 3).

**3. The network.** wet $= \big(\sum_{i=1}^{4} \text{comb}_i\big)/4 \to$ allpass(5.0 ms) $\to$ allpass(1.7 ms). Canonical Moorer set @ 44.1 kHz: combs 1310/1636/1813/1927 samples (29.7/37.1/41.1/43.7 ms), g = 0.77; allpasses 220/75 samples (5.0/1.7 ms), g = 0.7. Design RT60 (longest comb): $3\cdot 1927/(44100\cdot|\log_{10}0.77|)$ = 1.155 s; measured (Schroeder 1965 backward integration on the 3 s wet IR) **1.065 s (−7.8 %)** (check 4).

**4. Echo-density growth (the anti-flutter criterion).** The comb bank alone yields only ~110 echoes/s ($4 f_s/\bar m$ — audible flutter); each allpass multiplies the density. Measured: **1240 → 18 960 → 16 380 echoes/s** in [0,50)/[100,150)/[150,200) ms windows — 15× growth, late density ≫ Schroeder's ≥ 1000 echoes/s "unresolvable" target (checks 5–6).

**5. Coloration = periodic ripple, not peak-to-valley.** A lone comb's dB spectrum autocorrelates 1.00 at its 33.7 Hz spacing; the 4-comb network's autocorrelation at the same lag is **0.02** — the incommensurate delays destroy the dominant metallic ripple (check 7). (Beware: the network's *raw* P2V is 67.9 dB — deep narrow nulls from comb phase cancellation — but that is not the perceptual metric; see Pitfalls 3.)

**6. HF damping (Jot 1992).** One-pole lowpass inside each comb loop: $l_p = (1-\text{damp})\,\text{out} + \text{damp}\,l_p$, feedback $= g\,l_p$; damp = 0 recovers the colorless classic. Verified: tail spectral centroid **11 052 → 9 282 Hz** at damp = 0.5 (check 12). Convention matches `reverb.py`'s `_comb_feedback` (damping = pole coefficient on history; 0 = classic, 1 = fully dark).

**7. Quasi-stereo (Schroeder 1961).** Two allpass chains fed from the shared comb sum: L = (5.0, 1.7 ms), R = (4.7, 1.3 ms) — the few-ms chain mismatch decorrelates L/R. Verified: corr(L, R) = **0.23**, RMS ratio 1.000 (check 8).

**8. Numerical.** O(1) per sample per channel (6 delay lines); pure-Python prototype ≈ realtime per channel at 44.1 kHz; deterministic per buffer (delay lines reset per note/buffer; same input → bit-identical output, check 9); stability: all loop gains < 1 → bounded (noise peak out/in = 0.71, check 10); time/frequency consistency: steady-state sine gain **0.768 == |H(f_k)| 0.768** at a comb-1 resonance (check 11); sample-count preserving per channel; WAV artifact exact (44 + 4·97 020 B, check 13).

### Musical Elements Framework

- **PITCH**: colorless by design — |H| = 1 means SRB adds no pitch, no formants, no harmonic content (contrast SP-031 cross-synthesis, SP-062 shaping). Comb spacing $f_s/m \approx 33$ Hz is far below pitch perception, so tuned-instrument rows stay in tune; the comb resonances contribute "room warmth" at low densities. Deliberately *not* pitch-synced (unlike SP-050's band templates) — SRB is the neutral space layer.
- **RHYTHM**: the tail IS the rhythmic envelope: measured RT60 1.065 s sets the decay feel (contrast SP-071 plate ~2–3 s, SP-032 arbitrary); pre-delay separates the dry attack from the tail onset; echo density 1240→16 380/s governs legibility — below ~1000/s fast passages smear into flutter, above it the tail is smooth (checks 5–6); damped combs shorten the HF component of the tail, tightening fast patterns; freeze (g→1) is the infinite-hold drone.
- **HARMONY**: linear filter network — zero intermodulation, so dense chords stay clean in the shared tail (contrast nonlinear SP-070/SP-062); sum topology = one space for all voices, chords blend by their decay envelopes; the colorless magnitude means chord balance is preserved (no resonant notes pop out, unlike tuned-comb resonant-body designs).
- **STRUCTURE**: sections = space states: dry/room/hall columns {rt60_scale, damp, mix, pre_delay, freeze}; a crescendo-to-freeze is a g-ramp column; the wet/dry mix is a section parameter. Seam rule (SP-136/SP-138): the tail must be rendered into the buffer margin — never re-time a tail across a section seam (Pitfall 7).
- **TEXTURE**: (a) the classic smooth dense tail (vs FDN's colorless parametric late field, DPR's warm plate density, DWSR's boing), (b) echo-density evolution (the tail's graininess curve), (c) damp 0 vs 0.5 (bright shimmer vs dark warmth, centroid 11.0→9.3 kHz), (d) quasi-stereo width corr 0.23 (wide but not phasey), (e) pre-delay + early-tap options for slap/room flavor, (f) freeze washes as under-layers.

### UnitMatrix Integration

**Voices = rows = send groups.** Row $v$ carries `{mix (wet send level), predelay_ms, damp, g_scale, freeze}`. Example rows: "lead send" (mix 0.35, damp 0.2, predelay 0), "pad send" (mix 0.55, damp 0.45, g_scale 1.2), "drum send" (mix 0.15, predelay 5 ms), "freeze pad" (freeze 1). The shared SRB instance runs once per bus; each row's send gain scales its contribution.

**Sections = columns = space states.** Column $j$ holds `{rt60_scale (scales m or g), damp, mix, predelay_ms, freeze}` — a column change is a space change (dry verse → wet hall chorus). SRB is sample-count preserving per buffer; a release at a seam is the tail ringing into the margin (the SP-136/SP-138 seam rule applies — never re-time a tail).

**Cells = MusicUnit.** Each cell's `MusicEvent`s (pitch, velocity, start_tick, end_tick) render into the row's dry buffer (via the source SP method); cell velocity → send level (per-note wet amount); cell duration → dry note length; the tail continues into the buffer margin (length = dry + ceil(T60·f_s) margin).

**Produce dispatch:** `produce(midi_path, method="SP-140", params={"rows": {"lead": {"mix": 0.35, "damp": 0.2, "predelay_ms": 0.0}, "pad": {"mix": 0.55, "damp": 0.45, "g_scale": 1.2}}, "columns": {"A": {"rt60_scale": 1.0, "damp": 0.3, "mix": 0.35}, "B": {"rt60_scale": 1.4, "damp": 0.5, "mix": 0.5, "freeze": 1}}, "fs": 44100})`. Stage order: per-row source render (SP-001/SP-011/SP-134/SP-139/...) → per-row EQ (SP-007) → spatialize (SP-021/SP-053) → **SRB or SP-009/SP-032/SP-071/SP-075 (space/tail stage)** → bus dynamics (SP-008/SP-107) → loudness (SP-126) → dither (SP-122). Use SRB for the cheap classic hall/room tail (O(1), the budget reverb, already in `sound/effects/reverb.py`); use SP-032 FDN for parametric colorless late fields; use SP-071 for plate character; use SP-009 for measured spaces; use SP-075 image-source early taps + SRB tail for geometrically exact small rooms (the `room_reverb.py` pattern). NOTE (2026-11-13): the `produce()` dispatch map in `workflows/musicom_workflow.py` carries a parallel surveillance namespace whose SP numbering diverges from methods_db (see `hermes_agent/surveillance.md`); the methods_db numbering is authoritative for this entry.

### Pitfalls

1. **The damped-comb convention trap.** `filterstore = out·damp + store·(1−damp)` (a common Freeverb-derived form) FREEZES the feedback at damp = 0 — the classic comb degenerates into a plain delay. Use `lp = (1−damp)·out + damp·lp` so damp = 0 recovers $y[n] = x[n] + g\,y[n-m]$ exactly. (This exact bug was hit and fixed in the prototype; checks 1–2 would have failed otherwise.)
2. **Allpass IR truncation lies.** Measuring |H| from an allpass IR truncated at 4·m samples shows phantom 4.5 dB ripple; the true response is flat to machine precision (0.0000 dB). Render ≥ 200·m samples ($g^{200} \approx 10^{-31}$) before the FFT.
3. **Peak-to-valley is the wrong coloration metric.** The 4-comb sum has deep narrow nulls (raw P2V 67.9 dB) yet zero *periodic* ripple (autocorr 0.02 at every comb spacing). Judge metallic coloration by dB-spectrum autocorrelation at the comb spacings, not P2V.
4. **Resonance gain of the bank ≠ 1/(1−g).** Parallel comb phases cancel: measured sine gain 0.768 at a comb-1 resonance vs 1.837 from the naive single-comb sum formula. Design gains by measuring the network, never from single-comb formulas.
5. **Freeze (g→1) diverges.** Any DC or numerical residue circulates forever and grows to full scale. DC-block input/output, use magnitude-truncation semantics, and crossfade freeze in over ~100 ms (the SP-071 lesson).
6. **Echo density below ~1000/s flutters.** 2 combs or a single allpass leaves the tail "zinging" audibly; 4 incommensurate combs + ≥ 2 allpasses is the Schroeder minimum — verify with the density check (checks 5–6).
7. **Seam discipline.** The tail must be rendered into the buffer margin (dry length = note length; wet continues into the margin). Re-timing a tail across a section seam breaks the zero-drift invariant (SP-136/SP-138 rule).
8. **Neighbour audit.** SP-032 FDN = the generalized successor (N lines, unitary feedback matrix, O(N)); SP-071 DPR = plate tank; SP-058 = dispersive spring; SP-009 = measured IRs; SP-075 = image-source early field; SP-013 = single modulated delay (slap/chorus class); SP-050 = spectral (STFT) delays. SRB = the fixed 4+2 comb+allpass classic, O(1), the ancestor of them all. Repo: `sound/effects/reverb.py` (AlgorithmicReverb, 8+4 production variant) and `sound/effects/room_reverb.py` (`comb()`/`allpass()` primitives, lines 41–57); SP-140 documents the canonical Moorer 4+2 preset and the quasi-stereo/freeze extensions for them.

### Python / NumPy Implementation Sketch

```python
"""SP-140 SRB core (verified prototype: _web140/verify_sp140.py, 13/13 checks)."""
import numpy as np

FS = 44100
# canonical Moorer/Schroeder set (ms -> samples @44.1k)
COMB_MS = [29.7, 37.1, 41.1, 43.7]   # -> 1310, 1636, 1813, 1927 samples
COMB_G = 0.77
AP_MS_L = [5.0, 1.7]                 # left  allpass chain -> 220, 75
AP_MS_R = [4.7, 1.3]                 # right chain (quasi-stereo decorrelation)
AP_G = 0.7

def ms2s(ms):
    return int(round(ms * FS / 1000.0))

class FeedbackComb:
    """y[n] = x[n] + g*lp; lp = (1-damp)*out + damp*lp  (damp=0 -> classic comb)."""
    def __init__(self, m, g=COMB_G, damp=0.0):
        self.m, self.g, self.damp = m, g, damp
        self.dly = np.zeros(m); self.lp = 0.0; self.idx = 0
    def process(self, x):
        m, g, damp = self.m, self.g, self.damp
        dly, lp, idx = self.dly, self.lp, self.idx
        y = np.empty_like(x)
        for i in range(len(x)):
            out = dly[idx]
            lp = (1.0 - damp) * out + damp * lp
            dly[idx] = x[i] + g * lp
            y[i] = out
            idx = (idx + 1) % m
        self.lp, self.idx = lp, idx
        return y

class SchroederAllpass:
    """y[n] = -g x[n] + x[n-m] + g y[n-m]; single delay line stores v[n-m]."""
    def __init__(self, m, g=AP_G):
        self.m, self.g = m, g
        self.dly = np.zeros(m); self.idx = 0
    def process(self, x):
        m, g = self.m, self.g
        dly, idx = self.dly, self.idx
        y = np.empty_like(x)
        for i in range(len(x)):
            v = dly[idx]                  # x[n-m] + g*y[n-m]
            y[i] = v - g * x[i]
            dly[idx] = x[i] + g * y[i]
            idx = (idx + 1) % m
        self.idx = idx
        return y

class SchroederReverb:
    """4 parallel combs -> 2 allpass chains (quasi-stereo). O(1) per sample."""
    def __init__(self, damp=0.0, chain="L"):
        ap = AP_MS_L if chain == "L" else AP_MS_R
        self.combs = [FeedbackComb(ms2s(m), COMB_G, damp) for m in COMB_MS]
        self.aps = [SchroederAllpass(ms2s(d), AP_G) for d in ap]
    def process(self, x):
        wet = sum(c.process(x) for c in self.combs) / 4.0
        for a in self.aps:
            wet = a.process(wet)
        return wet

# stereo render: L/R from the shared comb sum via decorrelated chains
def render_stereo(x, damp=0.0, mix=0.45):
    L = SchroederReverb(damp, "L").process(x)
    R = SchroederReverb(damp, "R").process(x)
    return (1 - mix) * x + mix * L, (1 - mix) * x + mix * R
```

Cost: **O(1) per sample per channel** (6 delay lines total); pure-Python prototype ≈ realtime per channel at 44.1 kHz (vectorize across rows / use Numba for the production path, as `sound/effects/reverb.py` does). Deterministic per buffer; sample-count exact per channel; tail continues into the caller's margin (dry length = note length, margin = ceil(T60·f_s)).

### Verification Summary (prototype `_web140/verify_sp140.py`, 2026-11-13)

**13/13 checks pass.** Measured numbers (log `_web140/verify_sp140_output.txt`):

| # | Check | Measured vs reference |
|---|-------|----------------------|
| 1 | comb echo spacing | exactly m = 1310 samples (29.7 ms) |
| 2 | comb geometric decay | exactly 0.770000 per echo (g = 0.77) |
| 3 | allpass |H| flatness (colorless) | max deviation 0.0000 dB over 20 Hz–20 kHz |
| 4 | network RT60 (backward integration) | 1.065 s vs design 1.155 s (−7.8 %) |
| 5 | echo-density growth | 1240 → 18 960 → 16 380 echoes/s ([0,50) [100,150) [150,200) ms) |
| 6 | late echo density ≥ 500/s | 16 380 echoes/s (Schroeder target ~1000/s) |
| 7 | no dominant periodic comb ripple | dB-spectrum autocorr @33.7 Hz: comb 1.00 → network 0.02 |
| 8 | quasi-stereo decorrelation | corr(L,R) = 0.23, RMS ratio 1.000 |
| 9 | determinism | two renders bit-identical |
| 10 | bounded output (g<1) | noise peak out/in = 0.71 (comb resonance 1/(1−g) = 4.35) |
| 11 | sine gain == \|H(f_k)\| | 0.768 == 0.768 @ 10099 Hz (time/freq consistency) |
| 12 | in-loop damping darkens tail | centroid 11 052 → 9 282 Hz (damp 0 → 0.5) |
| 13 | WAV artifact + frame count | 388 124 B = 44 + 4·97 020 frames (2.20 s) |

Demo audio: `_web140/sp140_demo.wav` — 4 decaying notes (C4/E4/G4/C5, mix 0.45, damp 0.25) through the quasi-stereo network.

### References

- Schroeder, M. R. (1962). "Natural Sounding Artificial Reverberation." *JAES* 10(3), 219–223.
- Schroeder, M. R. (1961). "'Colorless' Artificial Reverberation." *IRE Trans. Audio* AU-9(5), 192–197. DOI 10.1109/TAU.1961.1166351.
- Schroeder, M. R. (1970). "Digital Simulation of Sound Transmission in Reverberant Spaces." *JASA* 47(2), 424–431. DOI 10.1121/1.1911541.
- Jot, J.-M. (1992). "An Analysis/Synthesis Approach to Real-Time Artificial Reverberation." *Proc. ICASSP-92*, 2, 221–224. DOI 10.1109/ICASSP.1992.226080.
- Moorer, J. A. (1979). "About This Reverberation Business." *Computer Music Journal* 3(2), 16–28.
- Dattorro, J. (1997). "Effect Design, Part 1: Reverberator and Other Filters." *JAES* 45(9), 660–684.
- Smith, J. O. (2023). *Physical Audio Signal Processing*, Stanford CCRMA (comb/allpass chapters; cached `_web140/ccrma_Artificial_Reverberation.html`).
- Wikipedia: "Reverberation" (cached `_web140/wiki_reverb.html`).
- Repo: `sound/effects/reverb.py` (AlgorithmicReverb, Schroeder/Moorer 8+4 variant), `sound/effects/room_reverb.py` (`comb()`/`allpass()` primitives, lines 41–57).
