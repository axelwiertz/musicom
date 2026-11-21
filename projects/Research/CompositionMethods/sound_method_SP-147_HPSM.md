# SP-147 — Handpan/Steelpan Spherical-Shell Modal Synthesis (HPSM)

**Layer:** absolute (sound production — LAYER_ARCHITECTURE.md)
**Category:** Synthesis Engines / Physical Modeling — tuned spherical-shell idiophone
**ID:** SP-147 (resolved dynamically: table + file scan max was SP-146)
**Date:** 2026-11-21 (scheduled cron research agent)
**Candidate code path:** `sound/synthesis/handpan_shell.py`, dispatched from `workflows.musicom_workflow.py::produce(method="SP-147", ...)`
**Prototype:** `_web147_hpsm/hpsm_prototype.py` — **10/10 checks pass**; outputs `_web147_hpsm/hpsm_results.json`, `_web147_hpsm/hpsm_out.wav` (1,221,614 B, 13.85 s).

---

## 1. One-liner

Renders the pitched spherical-shell idiophone family — Trinidad steelpan (concave oil-drum bowl) and handpan/Hang (twin gas-nitrided steel domes) — as a modal sum of **deliberately tuned integer partials** per note area (handpan 1:2:3:4 single-note chord, steelpan harmonic series), with curvature-difference mode confinement, velocity→brightness, a Helmholtz port drone that pitch-bends when covered, and optional duo-note detune shimmer.

## 2. Why this method, why now

The database's percussion coverage: SP-003 flat plates/bars (untuned natural partials), SP-136 tabla membrane + syahi (membranophone), SP-145 cast bell (campanological *inharmonic* partials, clapper-struck, no air port), SP-087/098/089 TR-808 transistor circuits, SP-120 particle shakers. **No method covers the steel shell idiophone whose note areas are deliberately tuned to integer partial ratios and whose cavity+port adds a Helmholtz bass.** Grep audit before entry: `handpan` = 0, `steelpan` = 0, `spherical shell` = 0, `rotoid` = 0 in `methods_db.md`; `helmholtz` = 13 (all SP-120 coke-can shaker context, unrelated). Novel.

The physics is documented: Wikipedia (Handpan, Hang (instrument), Steelpan — fetched 2026-11-21) and arXiv:2212.14465 "Localization in musical steelpans" (2022), which establishes the **curvature-difference mode confinement** principle — each note area vibrates independently, making the pan "operate as a two-dimensional xylophone".

## 3. Instrument model

| property | handpan / Hang | steelpan |
|---|---|---|
| body | two deep-drawn gas-nitrided half-shells, glued at rim, convex lens | 200-L oil-drum, concave bowl ("sunk" playing surface) |
| note areas | centre Ding + 7–8 tone fields (elliptical dimples) | 3–30+ hammered note areas (larger = lower) |
| partial tuning | 1:2:3:4 (fundamental, octave, tritave, double octave) | 1:2:3:…:N integer harmonic series |
| excitation | hands/fingers (soft) | rubber-tipped sticks ("ping") |
| air port | Gu hole in bottom shell → Helmholtz bass, coverable | none (open bowl) |
| other | friction idiophone, singing-bowl ring | — |

## 4. Extended mathematics

### 4.1 Note-area sizing (clamped circular plate law)

Fundamental of a clamped circular plate (thickness $h$, radius $a$):

$$f_{01} = \frac{10.2158}{2\pi a^2}\,h\,\sqrt{\frac{E}{12\rho(1-\nu^2)}}$$

Steel: $E=200$ GPa, $\rho=7800$ kg/m³, $\nu=0.3$ → radical ≈ 1532 m/s →

$$f_{01} \approx 2493\,\frac{h}{a^2}\ \text{Hz}$$

Scaling: $f \propto h/a^2$ — doubling the note-area radius quarters the pitch (verified ×4.0 exactly). Real handpans sit below the flat-plate value (the dimple is a dished spherical cap with lower effective stiffness); the law is for ordering/register, not absolute pitch — tune f0 from MIDI in production.

### 4.2 Modal sum

$$y(t) = \sum_{k=1}^{K} A_k\, e^{-t/\tau_k} \sin(2\pi f_k t + \phi_k), \qquad f_k = r_k f_0,\quad \tau_k = \frac{T_{60,k}}{\ln 1000}$$

$r_k$: handpan {1,2,3,4}; steelpan {1,2,…,N}. Verified: FFT peak ratios 1:2:3:4 exact (max rel. err 0.0); T60 2.505 s vs 2.5 s spec (0.2 %).

### 4.3 Velocity → brightness

$$A_k(v) = v\,\alpha_k\, v^{\gamma_k-1}, \qquad \gamma_k \propto r_k$$

Verified: partial-amplitude centroid 1.441 → 1.692 → 1.956 for $v$ = 0.2/0.5/1.0. Hard slap rings the octave+tritave; soft touch is pure fundamental — the instrument's expressive core.

### 4.4 Helmholtz port

$$f_H = \frac{c}{2\pi}\sqrt{\frac{A}{V\,L_{\text{eff}}}}, \qquad L_{\text{eff}} = L + 1.7a \ \text{(flanged)}\quad\text{or}\quad L + 1.22a \ \text{(unflanged)}$$

Handpan numbers (V = 20 L, a = 5 cm, L = 1.2 mm): **116.5 Hz flanged** (≈A2), 137.2 Hz unflanged. Covering the port (hand/leg) reduces effective $A$:

$$\frac{f_H'}{f_H} = \sqrt{\frac{A'}{A}}$$

Verified: $A' = A/2$ → ×0.70711 exactly. Demo: 40 % cover → 116.5 → 90.3 Hz, a **−4.4-semitone talking-drum bend**, phase-continuous. Blocking the Gu is how handpan players drop the drone to a sympathetic D2-class note.

### 4.5 Duo-note beating

Two duplicate notes δ cents apart:

$$\Delta f = f_0\left(2^{\delta/1200}-1\right) \approx \frac{f_0\,\delta}{1731}$$

Verified: δ = 8 ¢ @ 196 Hz → predicted 0.9078 Hz, measured 0.9028 Hz (FFT bin 0.0347 Hz). Keep δ ≤ 10 ¢: at 200 Hz that is ≤ 1.2 Hz — slow shimmer, not wobble.

### 4.6 Attack and ring

- Steelpan "ping": <30 ms velocity-scaled burst of high shell modes / band-limited noise + fast-decay high partials.
- Handpan: hand-struck — soft noise puff + high partials; fundamental rings 2.5–4 s.
- Friction/singing-bowl: near-undamped high partial or slow-sweep rim excitation.

### 4.7 Cost

$O(K)$ per sample per note, $K \le 12$; NumPy-vectorised across voices; dozens of notes real-time at 48 kHz. No training, no corpus, deterministic per seed, sample-count exact (zero-drift safe).

## 5. Python / NumPy implementation sketch

```python
"""sound/synthesis/handpan_shell.py (SP-147) — prototype-faithful skeleton."""
import numpy as np
from scipy.signal import fftconvolve   # only for verification helpers

FS = 44100
C = 343.0
LN1000 = np.log(1000.0)

def midi_to_hz(m):
    return 440.0 * 2.0 ** ((m - 69) / 12.0)

def helmholtz(A, V, L, a, flanged=True):
    """Port resonance. A=pi a^2; L_eff = L + 1.7a (flanged) | L + 1.22a."""
    L_eff = L + (1.7 if flanged else 1.22) * a
    return (C / (2 * np.pi)) * np.sqrt(A / (V * L_eff)), L_eff

class HandpanShell:
    """One row = one instrument. Note areas = partial banks, port = Helmholtz drone."""

    # D-Kurd layout: Ding D4 + tone circle; MIDI -> note-area label
    LAYOUT_D_KURD = {62: "ding", 57: "A3", 58: "Bb3", 60: "C4", 64: "E4", 65: "F4", 67: "G4", 69: "A4"}

    def __init__(self, family="handpan", partials=(1, 2, 3, 4),
                 t60=(3.2, 1.6, 1.1, 0.8), duo_cents=4.0, port=None, seed=0):
        self.family = family
        self.ratios = np.asarray(partials, float)
        self.t60 = np.asarray(t60, float)
        self.duo_cents = duo_cents
        self.port = port or dict(V=0.02, a=0.05, L=0.0012)
        self.rng = np.random.default_rng(seed)
        self.seed = seed

    def _partial_phases(self, note_seed):
        return np.random.default_rng(self.seed * 101 + note_seed).uniform(0, 2 * np.pi, len(self.ratios))

    def note(self, midi, velocity=0.7, dur=6.0, muted=False, note_seed=0):
        """Render one struck note area as a modal sum (exact sample count)."""
        n = int(round(dur * FS))
        t = np.arange(n) / FS
        f0 = midi_to_hz(midi)
        gamma = 1.0 + 0.4 * (self.ratios - 1.0)          # higher partials steeper in v
        amps = velocity ** gamma                          # A_k(v) = v^gamma_k
        tau = (self.t60 * (0.4 if muted else 1.0)) / LN1000
        phi = self._partial_phases(note_seed)
        y = np.zeros(n)
        for k, (r, A, tt) in enumerate(zip(self.ratios, amps, tau)):
            y += A * np.exp(-t / tt) * np.sin(2 * np.pi * r * f0 * t + phi[k])
        if self.duo_cents and midi in (62,):              # duo shimmer on the ding
            f1 = f0 * 2 ** (self.duo_cents / 1200)
            for k, (r, A, tt) in enumerate(zip(self.ratios, amps * 0.5, tau)):
                y += A * np.exp(-t / tt) * np.sin(2 * np.pi * r * f1 * t + phi[k] + 1.3)
        return y

    def port_drone(self, dur, cover=0.0, bend_at=None, seed=0):
        """Helmholtz drone; cover in [0,1) shrinks A -> pitch bend (phase-continuous)."""
        n = int(round(dur * FS)); t = np.arange(n) / FS
        p = self.port
        f_open = helmholtz(np.pi * p["a"] ** 2, p["V"], p["L"], p["a"])[0]
        f_cur = f_open * np.sqrt(1.0 - cover)             # effective area shrink
        tau = 6.0 / LN1000
        rng = np.random.default_rng(seed)
        y = 0.18 * np.exp(-t / tau) * np.sin(2 * np.pi * f_cur * t + rng.uniform(0, 2 * np.pi))
        return y
```

Production notes: (a) render per (row, section) once, slice to cells — never per note event, or tails clip; (b) assert `len(buf) == n` before mixing (zero drift); (c) seed per note (`seed*101+row` convention) for golden-hash reproducibility; (d) stage order: HPSM source → SP-007 EQ → SP-021/053/119 spatialize → SP-009/032/140 reverb → SP-008/107 dynamics → SP-126 loudness → SP-122 dither.

## 6. Verification results (prototype, 2026-11-21)

| # | check | spec | measured | pass |
|---|---|---|---|---|
| 1 | MIDI→Hz (69/81/57/60) | 440/880/220/261.6256 | exact (≤1e-9 rel) | ✔ |
| 2 | partial ratios 1:2:3:4 @196 Hz | peaks 196/392/588/784 | exact, max rel err 0.0 | ✔ |
| 3 | modal T60 | 2.5 s | 2.505 s (0.2 %) | ✔ |
| 4 | Helmholtz + cover | 116.5 Hz; ×√0.5 on 50 % cover | 116.52; ×0.70711 | ✔ |
| 5 | duo beating 8 ¢ @196 Hz | 0.9078 Hz | 0.9028 Hz (bin 0.0347) | ✔ |
| 6 | velocity→brightness centroid | rising | 1.441→1.692→1.956 | ✔ |
| 7 | sizing law f∝1/a² | ×4.0 per 2× radius | ×4.0 exact | ✔ |
| 8 | zero drift | exact count | 221,734 = 221,734 | ✔ |
| 9 | determinism | byte-identical | SHA256 equal | ✔ |
| 10 | demo WAV | >40 kB | 1,221,614 B, 13.85 s | ✔ |

## 7. References

- Wikipedia: "Handpan" (extract + wikitext, MediaWiki API, fetched 2026-11-21).
- Wikipedia: "Hang (instrument)" (wikitext, fetched 2026-11-21) — tuned harmonically (fundamental, octave, fifth above octave); Gu Helmholtz resonator; sympathetic D2; friction/singing-bowl; gas nitriding.
- Wikipedia: "Steelpan" (wikitext, fetched 2026-11-21) — 200-L drum origin; harmonic overtone tuning (Marshall, Gervais); strobe tuner practice; circle-of-fifths layout (Williams); note area size ↔ pitch.
- M. Nouh & co-authors, "Localization in musical steelpans," arXiv:2212.14465 (2022) — curvature-difference mode confinement; "two-dimensional xylophone".
- D. R. et al., "ConvNets for Counting: Object Detection of Transient Phenomena in Steelpan Drums," arXiv:2102.00632 (2021) — elliptical antinode regions (ESPI).
- T. et al., "espiownage: Tracking Transients in Steelpan Drum Strikes…," arXiv:2110.12261 (2021).
- Prototype: `_web147_hpsm/hpsm_prototype.py` (this run, 10/10 checks), `_web147_hpsm/hpsm_results.json`, `_web147_hpsm/hpsm_out.wav`.

## 8. Pitfalls (condensed)

1. Untuned partials > ~5 ¢ → "broken metal pan", not handpan; verify ratios per render.
2. Single global decay → "ping with a tail"; partials must decay independently (higher faster).
3. Helmholtz without end correction ($L+1.7a$ / $L+1.22a$) → drone off by a musical interval; keep it off tone-circle fundamentals.
4. Port-cover bends are smooth √A glides — phase-continuous or clicks (cf. SP-132/SP-133).
5. Duo δ > 10–15 ¢ → wobble; shimmer needs Δf ≤ f0/173.
6. No attack transient → bell, not pan; <30 ms velocity-scaled ping for steelpan.
7. Zero drift binds: exact sample count per section + tail, assert before mixing.
8. Determinism: seed phases + attack noise; golden-hash safe.
9. Not SP-003/042 (generic untuned modal), SP-145 (inharmonic bell partials), SP-136 (membrane), SP-087/098/089 (circuits), SP-120 (shakers).
10. Sizing law is a law, not a tuner: production f0 comes from MIDI; $f\propto h/a^2$ orders note areas/registers.
