# Sound Production Method SP-141 — Supersaw Oscillator Stack Synthesis (SOSS)

> Layer: **absolute** (sound production — LAYER_ARCHITECTURE.md). Candidate code path: `sound/synthesis/supersaw_swarm.py`.
> Verified prototype: `_web141_soss/verify_sp141.py` — **13/13 checks pass**; log `verify_sp141_output.txt`, demo `sp141_demo.wav` (6.60 s stereo).

### Source

- **Wikipedia: "Roland JP-8000"** (rev. 2026-10; cached `_web141_soss/wiki_jp8000.html`) — the Supersaw's origin and cultural context: "The supersaw is a waveform created by Roland for its JP-8000 and JP-8080 line of analog modeling synthesizers. It emulates the sound of multiple detuned sawtooth oscillators. The waveform is described as a free-run oscillator whose shape resembles 7 sawtooth oscillators detuned against each other over a period of time." Genre-defining for "anthem trance"; the JP-8080's boot pad *is* the Darude "Sandstorm" lead. The article's reference list also establishes the two canonical analyses below.
- **Szabo, A. (2010). "How to Emulate the Super Saw" (PDF)** — the canonical DSP reverse-engineering of the JP-8000 supersaw: the stack of detuned free-running saws and the **output-feedback phase randomization** that produces the signature "swirl" (a lowpassed portion of the output randomly modulating each oscillator's phase). Original PDF no longer hosted on `adamszabo.com` (404s verified 2026-11-14; live site and Wayback 2026-07-19 snapshot checked — no supersaw page); cited here via the Wikipedia reference list, which archives it (archived from the original 2016-04-29).
- **Shore, A. (2013-05-13). "An Analysis of Roland's Super Saw Oscillator and its Relation to Pads within Trance Music" (PDF)** — spectral analysis of the supersaw's detuned-partial clusters and its pad/trance usage; cited via the Wikipedia reference list.
- **Roland JP-8000 spec (Wikipedia infobox)**: OSC1 types = Super Saw / Triangle mod / Noise / Feedback / Square / Saw / Triangle; 8-voice polyphony, 2 osc/voice, virtual-analog subtractive, 12/24 dB resonant filter.
- **Välimäki, V. & Huovilainen, A. (2007). "Antialiasing Oscillators in Subtractive Synthesis."** *IEEE Signal Processing Magazine* 24(2), 116–125 — the PolyBLEP second-order residual (same primitive as SP-029).
- **Repo antecedent:** `sound/synthesis/supersaw_swarm.py` — an existing production `SupersawSwarm` (Native Instruments SuperStarSaw-style, reviewed MusicTech 2026-08-20): two independent 16-oscillator swarms, alternating detune ladder (`_detune_ladder`: 1, −1, 2, −2, … normalized to ±1), per-oscillator pan spread (equal-power), amplitude `drift`, a harmony engine (SCALES/CHORDS degree quantization — `_quantize_semitones`) and a bilinear 2×2 `MorphPad`. Its saw is a naive `2·phase−1` (aliasing documented here, check 7) and it has **no** JP-8000-style feedback phase randomization.
- **Novelty check (2026-11-14):** `grep -ci` on `methods_db.md` **before** entry: `supersaw` = 0, `super saw` = 0, `JP-8000` = 0, `feedback randomization` = 0; `swarm` = 27 (all Particle Swarm *Optimization* — an AI composition metaheuristic, unrelated). Adjacent-but-different: **SP-029** (one PolyBLEP saw + ladder filter — the source oscillator SOSS stacks); **SP-110** PWM (pulse via two saws); **SP-116** DSFS (closed-form bandlimited additive); **SP-047** (vector wavetable morph); **SP-097** SHOS (subharmonic division stack — SOSS's low mirror); **SP-095** TWEMS (fixed-ratio drawbar additive); **SP-074** (detuned piano strings, physical); **SP-102** AM (sidebands). **No SP method documents the detuned-saw stack with feedback phase randomization.**

### Layer

**absolute** (sound production — LAYER_ARCHITECTURE.md). SOSS is a synthesis engine: it consumes per-cell `MusicEvent`s (pitch, velocity, start_tick, end_tick) from a UnitMatrix voice and emits audio buffers — no timing authority beyond the events it is given, emits no events, decides nothing about composition. It is the *source* stage of the render chain, feeding filters/EQ (SP-029/SP-007), then space (SP-009/SP-032/SP-140), then bus dynamics (SP-008/SP-107), loudness (SP-126). Candidate code path: `sound/synthesis/supersaw_swarm.py` — extend the existing `SupersawSwarm` with polyBLEP saws, the JP-8000-style feedback phase randomization, and a classic 7-saw ladder mode; dispatch from `workflows/musicom_workflow.py::produce(method="SP-141", ...)`.

### Description

A trance lead that is seven leads at once: N *free-running* sawtooth oscillators, each detuned a few cents from one shared root and summed — the classic Roland JP-8000 Supersaw. The stack alone (fb=0) is a *detuned unison*: oscillators beat at |f_i − f_j| rates, a slow chorus-like pulsation while every partial stays in the root's harmonic grid. The signature extra ingredient is the **feedback phase randomization** (Szabo 2010): a lowpassed slice of the output continuously, unpredictably nudges each oscillator's *phase* (never its frequency), so the stack "swirls" — internal phasing wanders like a detuned analog ensemble while perceived pitch stays rock-solid. On top: polyBLEP anti-aliasing (median 33.4 dB alias-floor suppression over 202 measured fold bins), a harmony quantizer that snaps oscillators onto scale/chord tones (single-note chord from one key press), per-oscillator pan spread and amplitude drift for stereo width, O(N) per-sample cost (7 saws ≈ 2.3× realtime, 16 saws ≈ 1.4× realtime in pure Python at 44.1 kHz — check 11).

### Technical Mechanics

**1. The detuned stack (N=7 classic).** Each oscillator $i$ runs at
$$f_i = f_0\,2^{c_i/1200}, \qquad c_i = S\cdot\left[0,\;-\tfrac13,\;+\tfrac13,\;-\tfrac23,\;+\tfrac23,\;-1,\;+1\right] \quad (N=7)$$
— an alternating-sign symmetric ladder with magnitudes $\{0,\tfrac13,\tfrac23,1\}\cdot S$, outermost saws at exactly ±S cents, $\sum c_i = 0$ (detune ≠ transpose). Verified: ladder [0, −4, +4, −8, +8, −12, +12] cents @ S=12, sum 0 (check 1); outer saw 443.0604 Hz @ f0=440, +12 c (check 2). Output:
$$y[n] = \frac{1}{N}\sum_{i=1}^{N} \mathrm{saw}\big(\varphi_i[n]\big), \qquad \varphi_i[n+1] = \varphi_i[n] + f_i/f_s \pmod 1 \quad (\text{fb}=0)$$
Free-running initial phases (uniform [0,1), seeded per note).

**2. Beating = the detune chorus.** Pairs AM at $|f_i - f_j|$; the smallest ladder step $\Delta c = S/3$ gives the slowest beat $f_0(2^{\Delta c/1200}-1)$. Verified: dominant envelope modulation **0.500 Hz** @ f0=220 Hz, S=6 c — inside the predicted band [0.254, 0.764] Hz (check 3). Sub-Hz pulsation = the "detuned against each other over a period of time" motion — a slow chorus, not vibrato.

**3. PolyBLEP anti-aliasing.** Naive saw $2\varphi-1$ aliases hard; corrected saw subtracts the second-order residual (Välimäki–Huovilainen):
$$\mathrm{saw}_{\text{corr}}(\varphi, dt) = 2\varphi - 1 - p(\varphi, dt), \qquad p = \begin{cases} 2t' - t'^2 - 1, & \varphi < dt,\; t'=\varphi/dt \\ t'^2 + 2t' + 1, & \varphi > 1-dt,\; t'=(\varphi-1)/dt \\ 0, & \text{otherwise} \end{cases}$$
Verified: harmonic ratios 1 : 0.500 : 0.332 = ideal 1/k (check 8); alias-floor suppression **median 33.4 dB over 202 alias-image bins** (non-integer f0=331 Hz so folds land between harmonics; min 9.5 dB for folds just below Nyquist — polyBLEP's documented weak spot; max 75.2 dB mid-band; check 7).

**4. Feedback phase randomization (the Szabo swirl).** One-pole lowpass of the stack output drives per-oscillator phase offsets through smoothed random weights:
$$l_p[n] = l_p[n-1] + a\big(\bar y[n] - l_p[n-1]\big), \quad a = 1 - e^{-2\pi f_c/f_s}, \; f_c \approx 500\,\text{Hz}$$
$$\varphi_i[n+1] = \varphi_i[n] + \frac{f_i}{f_s} + \text{fb}\, l_p[n]\, w_i[n] \pmod 1, \qquad w_i[n+1] = w_i[n] + \alpha\big(\hat w_i - w_i[n]\big), \; \alpha \approx 0.01$$
with $\hat w_i$ a seeded per-oscillator uniform [−1, 1] draw. **The phase offset random-walks; the increment $f_i/f_s$ never changes** — pitch untouched (phase modulation, not FM). Verified: fb=0 → phase deviation from ideal linear trajectory 1.34e-14 cycles (machine-zero); fb=0.08 → deviation std **0.057 cycles** over 2 s (check 4); accumulated phase modulation −2.68 rad over 20 000 samples at fb=0.08 vs exactly 0 at fb=0 (check 5).

**5. Harmony quantization (scale/chord snapping).** Each oscillator's detune offset in semitones ($c_i/100$) snaps to the nearest degree of a scale or chord shape (continuous-space nearest-neighbour, octave-wrapped). Below ~0.5 st: no-op (all saws on root); at semitone-scale spreads: the stack spreads onto scale tones. Verified: major-scale snapping of the ±2.5-st ladder yields offsets [0, −1, 0, −1, 2, −3, 2] st — a root/3rd/2nd/4th cluster from one key press (check 10). Repo: `SCALES`/`CHORDS` tables + `_quantize_semitones`.

**6. Spread → partial clusters.** Each harmonic splits into sub-peaks spaced by the ladder; measured **5 peaks spanning 2.00 Hz** at harmonic 1 (f0=110 Hz, S=20 c), outer separation $\approx 2 f_0 (2^{S/1200}-1) = 2.55$ Hz predicted (check 9).

**7. Numerical.** O(N) per sample; t(N) = 262/429/754 ms for N = 7/16/32 over 0.6 s @ 44.1 kHz — linear (check 11); soft-normalized peak 1.0 (check 12); deterministic per seed, bit-identical same-seed rebuild (check 6); WAV artifact exact (check 13).

### Musical Elements Framework

- **PITCH**: root-exact by construction (zero-detune ladder element = pure saw at f0; $\sum c_i = 0$ keeps centre on root — detune ≠ transpose, contrast FM). Spread S = thickness dial (0 = single saw, ~6–15 c = chorus, semitones = cluster chord). fb swirl is pitch-stable phase movement. Harmony quantizer maps oscillators onto scale/chord tones — pitch-class clusters from one note.
- **RHYTHM**: the slow beats ARE the timbre's rhythm: 0.25–1.5 Hz envelope pulsation at 220 Hz, S=6 c (check 3) — the "chorus rate"; fb adds micro-unpredictability to internal phasing under any rhythmic grid. Note rhythm comes from the cell events; the classic trance stab = SOSS + fast amp envelope (SP-029 chain ADSR).
- **HARMONY**: one key press = unison in the stack centre, *chord* at the edges once the harmony quantizer engages (offsets [0, −1, 0, −1, 2, −3, 2] st, check 10) — the high-spectrum mirror of SP-097 SHOS. Multi-voice rows voicing chords give full harmonic function; dense detuned stacks mask tuning errors (the trance trick).
- **STRUCTURE**: section columns = {spread, fb, harmony, harmony_root, drift, pan_spread}; the classic build-up ramps spread 4→25 c and fb 0→0.3; chorus/break contrast = harmony snap (detune stack → scale cluster). Per-note seeded determinism makes cells reproducible; fb ramps are the macro-gesture ("swirl in").
- **TEXTURE**: (a) N (7 classic / 16 swarm) — density, (b) S — chorus width to cluster chord, (c) fb — swirl rate/presence (0 = static detune chorus, 0.3 = restless analog ensemble), (d) drift — per-oscillator amplitude shimmer, (e) pan_spread — stereo field, (f) harmony clusters — tonal density. Continuum: single-saw → tight unison → detuned chorus → scale cluster, all from one root, O(N).

### UnitMatrix Integration

**Voices = rows = supersaw instances.** Row $v$ carries `{n_osc, spread_cents, fb, fb_cutoff, drift, harmony, harmony_root, pan_spread, brightness}`. Example rows: "trance lead" (n_osc 7, S 10 c, fb 0.15, drift 0.2, pan 0.4), "supersaw pad" (n_osc 16, S 25 c, fb 0.3, harmony "minor", drift 0.4, pan 0.8), "bass stab" (n_osc 4, S 4 c, fb 0.05, octave down), "chord stab" (n_osc 7, S 120 c, harmony "maj7", harmony_root −12). Row seed = seed·101 + row (repo convention).

**Sections = columns = timbre states.** Column $j$ holds `{spread_scale, fb, harmony, harmony_root, drift, pan_spread, brightness}` — a column change is a timbre change (tight verse lead → wide build-up swirl → scale-cluster chorus). SOSS is sample-count preserving per cell; note released at a seam stops at the cell boundary (amp tails render into the margin — the SP-136/SP-138 seam rule).

**Cells = MusicUnit.** Cell (v, j): each `MusicEvent(pitch, velocity, start_tick, end_tick)` renders as a SOSS note — pitch → f0, end−start → duration, velocity → note gain; events end exactly at `section_len` (`_unit_from_events` zero-drift pattern). Deterministic per cell.

**Produce dispatch:** `produce(midi_path, method="SP-141", params={"rows": {"lead": {"n_osc": 7, "spread_cents": 10, "fb": 0.15}, "pad": {"n_osc": 16, "spread_cents": 25, "fb": 0.3, "harmony": "minor"}}, "columns": {"A": {"spread_scale": 1.0, "fb": 0.1}, "B": {"spread_scale": 2.5, "fb": 0.3}}, "fs": 44100})`. Stage order: **SOSS (source) or SP-001/SP-011/SP-134/... per row** → per-row filter (SP-029 chain) / EQ (SP-007) → spatialize (SP-021/SP-053/SP-119) → space/tail (SP-009/SP-032/SP-140) → bus dynamics (SP-008/SP-107) → loudness (SP-126) → dither (SP-122).

### Pitfalls

1. **Naive saw aliasing ruins the stack.** `2·phase−1` at 7× detune piles folded harmonics into a −27 dB hiss floor; polyBLEP cuts it by a median 33.4 dB (check 7). Do not ship the naive `_saw` of `supersaw_swarm.py` as-is for top-register leads — and know polyBLEP's limit: folds landing just below Nyquist get only ~10 dB; for very high leads consider 2× oversampling or SP-041 bandlimited wavetables.
2. **Ladder normalization traps.** If the ladder isn't normalized so the outermost saw is exactly ±S, the spread knob lies. If $\sum c_i \neq 0$, the stack's centre frequency shifts — detune silently becomes transpose.
3. **fb is phase, not frequency.** Adding `fb·lp·w` to the *frequency* turns the swirl into FM — the perceived pitch wobbles, destroying the supersaw's stable-pitch signature. Keep fb·lp·w in *cycles* (phase units), not radians.
4. **Free-running phases ≠ determinism by default.** Free-running means every render differs unless seeded. Seed per note/cell or the same cell renders differently every pass — breaks golden-audio regression nets (check 6).
5. **Low-register beats disappear.** At f0=55 Hz a 2-cent pair beats at 0.064 Hz — sub-audible, sounds like slow amplitude drift; use larger spreads or fewer saws in the bass.
6. **Harmony quantizer half-semitone bucket trap.** Offsets below ~0.5 st all snap to the root — a "harmony" setting with a small spread silently collapses the stack to unison. Only spreads ≳ 1 st create real clusters — verify with the offset histogram (check 10).
7. **Peak normalization hides RMS loss.** Soft-normalizing by peak makes a 16-saw stack quieter in RMS than a single saw at the same peak — against other voices the stack vanishes. Use RMS/equal-power matching per voice (or SP-126).
8. **Neighbour audit.** SP-029 (single PolyBLEP saw — the source oscillator); SP-110 PWM; SP-116 DSFS; SP-047 vector morph; SP-097 SHOS (subharmonic stack below f0 — the low mirror); SP-095 TWEMS (fixed drawbar ratios); SP-074 (detuned piano strings); SP-102 AM (sidebands). SOSS = the detuned free-running saw stack + feedback phase randomization, O(N). Repo: `sound/synthesis/supersaw_swarm.py` — extend per this spec.

### Implementation Sketch (Python/NumPy)

Core engine (numpy-free inner loop, deterministic per seed; ~40 lines):

```python
import numpy as np

def polyblep(t, dt):                       # second-order residual
    if t < dt:
        t /= dt
        return t + t - t * t - 1.0
    elif t > 1.0 - dt:
        t = (t - 1.0) / dt
        return t * t + t + t + 1.0
    return 0.0

def detune_ladder(n, spread_cents):        # alternating ±, outer = ±S
    idx = np.arange(n, dtype=np.float64)
    mag = (idx + 1) // 2
    sign = np.where(idx % 2 == 1, -1.0, 1.0)
    mag[0] = 0.0
    return sign * (mag / max(1, (n - 1) // 2)) * spread_cents

def render_soss(freq, duration, n_osc=7, spread_cents=12.0, fb=0.0,
                fb_cutoff=500.0, seed=None, harmony=None, drift=0.0,
                fs=44100):
    n = int(round(duration * fs))
    rng = np.random.RandomState(seed)
    ladder = detune_ladder(n_osc, spread_cents)
    midi = 69.0 + 12.0 * np.log2(max(freq, 1e-6) / 440.0)
    freqs = np.empty(n_osc)
    for i in range(n_osc):
        semi = midi + ladder[i] / 100.0
        if harmony is not None:            # snap to nearest scale degree
            semi = midi + _quantize_semitones(ladder[i] / 100.0, harmony)
        freqs[i] = 440.0 * 2.0 ** ((semi - 69.0) / 12.0)
    phase = rng.uniform(0.0, 1.0, n_osc)   # free-running phases
    w = rng.uniform(-1.0, 1.0, n_osc)      # swirl weights (smoothed)
    w_sm = w.copy()
    amps = 1.0 + drift * rng.uniform(-1.0, 1.0, n_osc)
    dphi, dt = freqs / fs, freqs / fs
    lp, a_lp = 0.0, (1.0 - np.exp(-2 * np.pi * fb_cutoff / fs)) if fb > 0 else 0.0
    out = np.empty(n)
    for j in range(n):
        s = 0.0
        for i in range(n_osc):
            s += amps[i] * (2.0 * phase[i] - 1.0 - polyblep(phase[i], dt[i]))
            phase[i] = (phase[i] + dphi[i]) % 1.0
        if fb > 0:                         # Szabo swirl: phase, not freq
            lp += a_lp * (s / n_osc - lp)
            w_sm += 0.01 * (w - w_sm)
            phase = (phase + fb * lp * w_sm) % 1.0
        out[j] = s / n_osc
    return out / np.max(np.abs(out))       # soft normalize
```

Verified numbers: ladder [0,−4,+4,−8,+8,−12,+12] @ S=12 (check 1); outer saw 443.0604 Hz (check 2); beat 0.500 Hz @ 220 Hz, S=6 (check 3); fb=0 phase deviation 1.34e-14 cycles vs fb=0.08 → 0.057 cycles (check 4); median alias suppression 33.4 dB (check 7); harmonics 1:0.500:0.332 (check 8); cluster 5 peaks / 2.00 Hz @ 110 Hz, S=20 (check 9); harmony offsets [0,−1,0,−1,2,−3,2] (check 10); t(7/16/32) = 262/429/754 ms per 0.6 s (check 11).

### References

1. Wikipedia, "Roland JP-8000" (rev. 2026-10) — cached `_web141_soss/wiki_jp8000.html`.
2. Szabo, A. (2010). "How to Emulate the Super Saw" (PDF; archived from original 2016-04-29 per the Wikipedia reference list).
3. Shore, A. (2013-05-13). "An Analysis of Roland's Super Saw Oscillator and its Relation to Pads within Trance Music" (PDF).
4. Välimäki, V. & Huovilainen, A. (2007). "Antialiasing Oscillators in Subtractive Synthesis." *IEEE Signal Processing Magazine* 24(2), 116–125.
5. Repo: `sound/synthesis/supersaw_swarm.py` (SupersawSwarm, 2×16 swarms, `_detune_ladder`, `_quantize_semitones`, `MorphPad`; MusicTech SuperStarSaw review 2026-08-20).
6. Prototype: `_web141_soss/verify_sp141.py` (13/13), log `verify_sp141_output.txt`, demo `sp141_demo.wav`.
