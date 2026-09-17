# SP-087 — TR-808 Analog Snare Drum Synthesis (TASS)

**Layer:** absolute (sound production — Synthesis Engines)
**Category:** Synthesis Engines | **Target Output:** Circuit-Faithful Analog Snare / Drum-Voice Timbre
**Candidate code path:** `sound/synthesis/drum_synth_808.py`
**Status:** documented 2026-09-17 (cron sound-production research job)

One-line: renders the Roland TR-808 snare from its transistor-circuit topology —
two high-Q bridged-T shell resonators an octave apart (typical 476/238 Hz, June
1981 service-manual values) summed with differentiator-shaped ("violet") white
noise under 60–75 ms RC envelopes. Audio out, from symbolic percussion events.

## 1. Why this method (gap analysis)

No 808-specific analog drum-voice method exists in this database. The 606
engine's snare (`sound/synthesis/drum_synth_606.py`) is a *generic*
tonal-body-plus-bandpassed-noise recipe with no bridged-T equations and no
Tone/Snappy semantics. SP-051 WDF is the general circuit-modeling framework
(netlist → scattering tree) without a drum-voice instantiation. SP-011/033/048
are string waveguides, not drum resonators; SP-040 FDTD is plate/membrane
oriented; SP-074 struck the piano string, not the drum shell. TASS fills the
**analog drum-voice** gap and is the first method whose specification is a
named historical circuit with published component values and design equations.

TASS renders one snare hit as the sum of three deterministic parts:

1. **Shell** — two exponentially decaying sine partials at $f_H \approx 2 f_L$
   (service-manual typical: 476/238 Hz). Each is the impulse response of a
   high-Q bridged-T resonator: near-sinusoidal, ~60 ms to −20 dB (the manual's
   "decay time" convention — amplitude to 1/10, not 1/1000), zero attack.
2. **Snap** — a short highpassed white-noise burst (~1 kHz highpass at mid
   Tone, ~75 ms decay) for the attack transient and wire-like sizzle; its level
   relative to the shell is the **Snappy** knob.
3. **Controls** — **Tone** (noise-path highpass cutoff), **Snappy**
   (shell/noise mix), **Level** (output gain). All per-hit automatable: one
   voice morphs from rim-click ghost notes to full backbeats.

## 2. Physics

### Bridged-T resonator: frequency and Q from components

Roland's manual gives the design equations for each bridged-T network in terms
of its R and C values (per the Norgatronics derivation, verified 2026-09-17):

$$f_0 = \frac{1}{2\pi R C}, \qquad Q = \frac{\tau\,\omega_0}{2}, \qquad T_{decay} = \frac{\ln(10)\,Q}{\pi f_0}$$

$\tau$ = 1/e envelope time; $T_{decay}$ = manual "decay time" (amplitude to
1/10, −20 dB). Reference: revised low-shell network ($f_0$ = 173 Hz,
$Q$ = 16.3) → $T_{decay} \approx 69$ ms, matching simulation (67 ms); "typical"
high shell (476 Hz, quoted 60 ms) → $Q \approx 39$ — the high-Q ring that makes
the 808 shell sing rather than thud.

### Shell synthesis (two partials, one envelope law)

$$s(t) = \left[\sin(2\pi f_L t) + \sin(2\pi f_H t)\right]\,e^{-t/\tau_s}, \qquad \tau_s = \frac{T_{decay}}{\ln(10)},\quad f_H \approx 2 f_L$$

$f_L$ = 238 Hz, $T_{decay}$ = 60 ms nominal; transposition scales both partials
together (ratio locked = the circuit's character).

### Noise path (violet noise + RC envelope)

White noise $w[n]$ through a one-pole highpass (differentiator stand-in):

$$n_{hp}[n] = w[n] - w[n-1] + a\,n_{hp}[n-1], \qquad a = e^{-2\pi f_c/f_s}$$

with $f_c = 800 + 100 \cdot \mathrm{Tone}$ (Tone 0–10, the io-808 law), then the
RC attack-decay envelope $e_n(t) = (1 - e^{-t/\tau_a})\,e^{-t/\tau_n}$,
$\tau_n = 75\,\mathrm{ms}/\ln(10)$.

### Mix (Snappy = shell/noise balance)

$$y(t) = g\left[(1 - S)\,s(t) + S\,\frac{n(t)}{\max|n|}\right], \qquad S \in [0,1]$$

$S$ = Snappy (equal-power compensated); $g$ = Level. Ghost notes $S \approx$
0.2–0.4, backbeats $S \approx$ 0.6–0.8.

## 3. Python/NumPy implementation sketch

```python
import numpy as np

def snare_808(fs=44100, f_low=238.0, t_decay=0.060,
              tone=5.0, snappy=0.7, level=0.9, dur=0.5, seed=808):
    """TR-808-style snare hit. tone 0-10, snappy 0-1."""
    rng = np.random.default_rng(seed)
    n = int(fs * dur); t = np.arange(n) / fs
    tau_s = t_decay / np.log(10.0)
    f_hi = 2.0 * f_low
    shell = (np.sin(2 * np.pi * f_low * t)
             + np.sin(2 * np.pi * f_hi * t)) * np.exp(-t / tau_s)
    white = rng.standard_normal(n)
    fc = 800.0 + 100.0 * tone
    a = np.exp(-2 * np.pi * fc / fs)
    hp = np.empty(n); px = py = 0.0
    for i in range(n):                      # production: lfilter
        hp[i] = white[i] - px + a * py
        px, py = white[i], hp[i]
    tau_n = 0.075 / np.log(10.0)
    noise = hp * np.exp(-t / tau_n)
    noise /= (np.abs(noise).max() + 1e-12)
    return level * ((1 - snappy) * 0.5 * shell + snappy * noise)

# usage: stem[onset:onset+len(hit)] += velocity * snare_808(tone=sec_tone, ...)
```

**Live verification** (2026-09-17, `$MUSICOM_PYTHON`, NumPy; full script in
`verify_sp087.py`): zero-padded FFT peaks at 238.2/476.4 Hz; per-partial
(coherently demodulated) −20 dB times 69.6/69.5 ms vs ~60 ms nominal; $Q$ =
19.5/39.0 vs manual-derived 16.3/39.0; noise centroid 11.5 kHz (highpass
effective); 100% energy within 400 ms; bit-deterministic per seed.
ALL CHECKS PASS.

### Complexity

$\mathcal{O}(1)$ per sample per hit (2 sine evals + 1 noise sample + 1 one-pole
filter state); $\mathcal{O}(H \cdot D)$ per stem for $H$ hits of $D$ samples.
Deterministic per (seed, params) — byte-identical stems across renders.

## 4. Musical Elements Framework

| Element | Mapping |
|---|---|
| **PITCH** | Shell partials 238/476 Hz nominal (≈ B♭3/B♭4); per-section transposition scales both (ratio locked). Detuning off 2:1 morphs 808 → 606 → electronic tom. Tune $f_L$ to the section root for "tuned 808" (modern trap) or leave at 238 Hz for the classic crack. |
| **RHYTHM** | The hit IS the rhythm event: onset = trigger, velocity = strike strength. Backbeat (2 & 4), ghost-note subdivisions (low Snappy + low Level), rolls (re-fired envelopes, no voice stealing). |
| **HARMONY** | Shell partials are pitched (octave stack) — ring sympathetically with bass/keys near B♭. |
| **STRUCTURE** | Per-section (Tone, Snappy) preset = drum-mix macro-form: tight verse → bright chorus → breakdown rim-clicks (Snappy → 0.2). |
| **TEXTURE** | Snappy is the texture fader: shell = hollow/woody, noise = crisp/cracking. The 60–75 ms decay is naturally staccato — per the Method Hybridization rule, always bed 808 hits over a continuous layer (026 DPSM, pad, long 808 kick) for flow. |

## 5. UnitMatrix Integration

- **Rows (Voices)** = each percussion row renders through its own TASS
  instance (snare/clap/rim rows); pitched rows bypass to SP-001/SP-074. One
  shared noise buffer per section; per-hit shell phases reset — matches the
  hardware (shared noise transistor, independent shell).
- **Columns (Sections)** = per-section (Tone, Snappy, Tune) preset + pattern
  density; presets interpolate continuously (cutoff and mix are click-free).
- **Cells (MusicUnit)** = pitch → optional per-cell shell retune; rhythm →
  onsets are trigger times, velocity accents map to Level + slight Snappy lift;
  texture → ghost-note cells get low-Snappy renders automatically.
- **Flow**: `compose` (UnitMatrix → MIDI) → drum rows extracted →
  `produce(method="SP-087", params={tone, snappy, tune})` → per-hit render →
  sum → SP-007 EQ → SP-008 limiter → WAV/OGG. Pairs: SP-009/032/071
  (room/plate — the gated-80s snare is TASS + short plate + gate), SP-072
  (HPSS rebalance shell vs snap post-hoc), SP-073 (TSDE attack boost),
  SP-006 (humanize onsets pre-render).

## 6. Pitfalls (condensed)

1. **Measuring decay on the raw mix lies** — octave partials beat at $f_L$;
   rectified envelope hits nulls (~14 ms in testing) before the true decay.
   Measure per partial via coherent demodulation.
2. **−20 dB vs −60 dB confusion** — manual "decay time" = amplitude to 1/10.
   $\tau = T_{decay}/\ln(10)$, not $T/6.9$.
3. **White instead of violet noise** — flat noise = dull thud; always highpass
   ($f_c \geq 800$ Hz) before the envelope.
4. **Shared-noise correlation** — same buffer offset per hit = machine-gun
   flamming. Per-hit RNG stream (seed + hit index).
5. **Linear Snappy crossfade** dips mid-travel loudness — use equal-power law.
6. **Retuning one partial only** breaks the 2:1 ratio — scale both (Tune knob).
7. **Re-trigger clicks** — hits add into the stem (polyphonic accumulation),
   never truncate.
8. **Confusion with the 606 snare** — generic recipe, no bridged-T equations;
   use TASS when the 808 shell ring is wanted.
9. **Hybridization rule** — 60 ms hits alone are maximally staccato; bed on a
   continuous layer.

## 7. References

- Roland Corporation. *TR-808 Rhythm Composer Service Manual* (June 1981).
- Roland TR-808 — Wikipedia (fetched 2026-09-17).
- Reid, G. *Synth Secrets* — "Synthesizing Drums: The Snare Drum", Sound on Sound.
- vincentriemer/io-808 — `src/synth/drumModules/snareDrum.js` (476/238 Hz pair; fetched 2026-09-17).
- Simon-L/WDR-8-rack — WDR-8 Snare module notes (fetched 2026-09-17).
- Chowdhury, J. — WaveDigitalFilters `TR_808/SnareResonator` (R197 820 kΩ, C58/C59 27 nF; fetched 2026-09-17).
- Werner, K. J. — *Virtual Analog Modeling of Audio Circuitry Using Wave Digital Filters* (dissertation).
- Norgatronics (S. Norgate). 808 snare tuning investigation (Q/f/decay equations; fetched 2026-09-17).
- Archer, E. — *TR-808 Snare Drum DIY Project* analysis.
- simo-pandolfi/py78drums — Python per-sample WDF drum synthesis workflow.
