# Report SP-141 — Supersaw Oscillator Stack Synthesis (SOSS)

- **Method name:** Supersaw Oscillator Stack Synthesis (SOSS)
- **Method ID:** SP-141
- **Layer:** **absolute** (sound production — LAYER_ARCHITECTURE.md; synthesis-engine source stage)
- **One-line description:** Stacks N free-running sawtooth oscillators detuned around one root (classic Roland JP-8000 supersaw: 7 saws) with polyBLEP anti-aliasing and Szabo-style output-feedback phase randomization ("the swirl"), plus a harmony quantizer for single-note scale/chord clusters — O(N) per sample.
- **Date:** 2026-11-14 (cron; no user present)
- **Next free SP ID after this entry:** **SP-142**

## Summary-table row (appended to methods_db.md, line 355)

```
| **SP-141** | Supersaw Oscillator Stack Synthesis (SOSS) | **Synthesis Engines** | Detuned-Saw Stack / Trance-Lead, Pad & Chord-Stab Timbres | Stacks N free-running sawtooth oscillators detuned around one root (classic JP-8000 supersaw: 7 saws, alternating ±S·{0, 1/3, 2/3, 1} ladder) with PolyBLEP anti-aliasing (median 33.4 dB alias suppression, check 7) and Szabo-style output-feedback phase randomization — the "swirl" (pitch-stable: phase offsets random-walk, f_i/fs untouched). Harmony quantizer snaps oscillators onto scale/chord tones (single-note chord). $O(N)$ per sample; deterministic per seed. Candidate: `sound/synthesis/supersaw_swarm.py` (extend: PolyBLEP + fb phase randomization + 7-saw mode). |
```

## Line counts

- methods_db.md before: **31 422** lines
- methods_db.md after: **31 499** lines (+76 for the detailed section +1 summary row = +77; the row was inserted mid-file so total delta = +77; section occupies lines 31424–31499, row at line 355)
- Standalone: `sound_method_SP-141_SOSS.md` (new)
- Report: `report_SP-141.md` (this file)

## Files produced

| File | Role |
| :--- | :--- |
| `/opt/data/projects/Research/CompositionMethods/methods_db.md` | summary row (line 355) + detailed section (lines 31424–31499) |
| `/opt/data/projects/Research/CompositionMethods/sound_method_SP-141_SOSS.md` | standalone full write-up + Python/NumPy implementation sketch + references |
| `/opt/data/projects/Research/CompositionMethods/report_SP-141.md` | this primary record |
| `/opt/data/projects/Research/CompositionMethods/_web141_soss/verify_sp141.py` | verified prototype — **13/13 checks pass** |
| `/opt/data/projects/Research/CompositionMethods/_web141_soss/verify_sp141_output.txt` | check log |
| `/opt/data/projects/Research/CompositionMethods/_web141_soss/sp141_demo.wav` | 6.60 s stereo demo (291 060 frames/ch, 1 164 284 B) |
| `/opt/data/projects/Research/CompositionMethods/_web141_soss/wiki_jp8000.html` | cached Wikipedia JP-8000 article |
| `/opt/data/projects/Research/CompositionMethods/_web141_soss/fix_backslashes_141.py` | LaTeX double-escape fixer (see Quirks) |

## Candidate code path

`sound/synthesis/supersaw_swarm.py` — the existing production `SupersawSwarm` (2×16-swarm SuperStarSaw-style variant with `_detune_ladder`, `_quantize_semitones`, `MorphPad`, harmony SCALES/CHORDS) is the repo antecedent; SP-141 is the spec to extend it with: polyBLEP saws (its `_saw` is a naive `2·phase−1`), the JP-8000/Szabo output-feedback phase randomization, and a classic 7-saw ladder mode (`n_osc=7`). Dispatch: `workflows/musicom_workflow.py::produce(method="SP-141", ...)`.

## Research provenance

Web research (curl; DDG/Bing/SearX/Google all bot-walled from this host — Google/Bing served shells or junk, DDG served a captcha; Wikipedia and adamszabo.com fetched directly):
- **Wikipedia "Roland JP-8000"** fetched and cached (`wiki_jp8000.html`): Supersaw origin (7 detuned free-running saws), trance-genre impact, infobox (OSC1 Super Saw/Feedback types), and the reference list naming the two canonical analyses.
- **Szabo (2010) "How to Emulate the Super Saw"** — identified from the Wikipedia reference list; the original PDF is no longer hosted (`adamszabo.com/supersaw.pdf` and variants all 404; live homepage and Wayback 2026-07-19 snapshot checked — no supersaw page); cited via the archived Wikipedia reference (honest note in the entry).
- **Shore (2013)** supersaw analysis — cited via the Wikipedia reference list.
- **Välimäki & Huovilainen (2007)** polyBLEP — the alias-suppression primitive.
- Repo antecedent read in full: `sound/synthesis/supersaw_swarm.py` (370 lines).

## Technical mechanics summary (all numbers measured by `verify_sp141.py`, 13/13)

1. **Stack:** $f_i = f_0 2^{c_i/1200}$, ladder $c = S·[0,−⅓,+⅓,−⅔,+⅔,−1,+1]$ (N=7) — alternating sign, sum 0, outer ±S. Measured [0,−4,+4,−8,+8,−12,+12] @ S=12; outer 443.0604 Hz @ f0=440 (+12 c).
2. **Beating:** dominant envelope modulation 0.500 Hz @ f0=220, S=6 c (predicted band [0.254, 0.764] Hz).
3. **PolyBLEP:** median 33.4 dB alias suppression over 202 alias-image bins (min 9.5 dB near-Nyquist — documented weak spot; max 75.2 dB); harmonic ratios 1:0.500:0.332 (ideal 1/k).
4. **Feedback phase randomization (Szabo swirl):** one-pole LP (fc≈500 Hz) of output × smoothed per-osc random weight → phase offset random-walks, f_i/fs untouched (phase, not FM). fb=0: deviation 1.34e-14 cycles (machine-zero); fb=0.08: 0.057 cycles std over 2 s; accumulated phase −2.68 rad vs 0.
5. **Harmony quantizer:** snaps oscillator semitone offsets to nearest scale/chord degree (octave-wrapped); measured major-scale offsets [0,−1,0,−1,2,−3,2] st @ S=250 c.
6. **Spread clusters:** 5 sub-peaks spanning 2.00 Hz @ f0=110, S=20 c (predicted outer sep 2.55 Hz).
7. **Cost/determinism:** O(N)/sample; t(7/16/32)=262/429/754 ms per 0.6 s @ 44.1 kHz (linear); seed → bit-identical; soft-normalized peak 1.0; WAV artifact exact.

## Verified prototype (13/13 checks pass)

`_web141_soss/verify_sp141.py` — pure Python/NumPy (musicom env, numpy 1.26.4). Checks: (1) ladder geometry, (2) oscillator frequencies, (3) beating band, (4) phase random-walk vs fb (trace mode), (5) phase accumulation fb on/off, (6) seed determinism, (7) polyBLEP alias suppression (median), (8) 1/k harmonics, (9) spread cluster, (10) harmony snapping, (11) O(N) cost, (12) normalization, (13) WAV artifact. Prototype iterations that failed first and were fixed: n_osc=1 divide-by-zero in the ladder (k=0), check-2 probe indexing, naive half-half correlation measure replaced by a direct phase-deviation trace, Hilbert-phase residual rejected in favor of the trace, integer-f0 fold-bin contamination replaced by non-integer f0 with median over 202 bins, harmony test spread raised to semitone scale, fmax bound for the fold bin.

## Quirks / pitfalls hit during execution

1. **LaTeX double-escape (pitfall a):** my `write_file` content carried `\\cdot`-style doubled backslashes into the appended section; `fix_backslashes_141.py` (chr(92)-based, escaping-proof) collapsed `\\`→`\` on lines 31424–31499 only (18 lines fixed), preserving the `\begin{cases}` row separator as `\\`. The patch tool re-doubled backslashes when I tried fixing the fixer — hence chr(92).
2. **`||` table-row prefix (pitfall b):** the patch tool inserted my summary row with a `||` prefix (the file's older rows carry the same quirk); normalized line 355 back to a single `|` and re-verified by grep + read.
3. **Search engines bot-walled:** DDG captcha, Bing junk results, Google JS shell, SearX instances blocked — Wikipedia/adamszabo.com fetched directly instead; Szabo PDF confirmed offline (404 on live + Wayback), cited via the Wikipedia archive note.
4. **Concurrent writer:** methods_db.md grew 31347 → 31422 lines between my first read and append (another cron job's entry); re-verified max SP-ID (still SP-140) and the SP-140 row anchor before inserting.
5. **`_web141/` cache dir collision:** the ACMTPC job owns `_web141/`; my cache/prototype dir is `_web141_soss/`.
6. **Inline `python3 -c` blocked** by the approval gate in this cron env — all helper logic written to script files and run with `$MUSICOM_PYTHON`.

## Complete section text appended (methods_db.md lines 31424–31499)

# Sound Production Method SP-141 — Supersaw Oscillator Stack Synthesis (SOSS)

### Source

- **Wikipedia: "Roland JP-8000"** (rev. 2026-10; cached `_web141_soss/wiki_jp8000.html`) — the Supersaw's origin and cultural context: "The supersaw is a waveform created by Roland for its JP-8000 and JP-8080 line of analog modeling synthesizers. It emulates the sound of multiple detuned sawtooth oscillators. The waveform is described as a free-run oscillator whose shape resembles 7 sawtooth oscillators detuned against each other over a period of time." Genre-defining for "anthem trance"; the JP-8080's boot pad *is* the Darude "Sandstorm" lead. The article's reference list also establishes the two canonical analyses below.
- **Szabo, A. (2010). "How to Emulate the Super Saw" (PDF)** — the canonical DSP reverse-engineering of the JP-8000 supersaw: the stack of detuned free-running saws and the **output-feedback phase randomization** that produces the signature "swirl" (a lowpassed portion of the output randomly modulating each oscillator's phase). Original PDF no longer hosted on `adamszabo.com` (404s verified 2026-11-14; live site and Wayback 2026-07-19 snapshot checked — no supersaw page); cited here via the Wikipedia reference list, which archives it (archived from the original 2016-04-29).
- **Shore, A. (2013-05-13). "An Analysis of Roland's Super Saw Oscillator and its Relation to Pads within Trance Music" (PDF)** — spectral analysis of the supersaw's detuned-partial clusters and its pad/trance usage; cited via the Wikipedia reference list.
- **Roland JP-8000 spec (Wikipedia infobox)**: OSC1 types = Super Saw / Triangle mod / Noise / Feedback / Square / Saw / Triangle; 8-voice polyphony, 2 osc/voice, virtual-analog subtractive, 12/24 dB resonant filter. The "Feedback" oscillator is the JP-8000's second signature (a looped/feedback waveform); the Supersaw is the stack.
- **Välimäki, V. & Huovilainen, A. (2007). "Antialiasing Oscillators in Subtractive Synthesis."** *IEEE Signal Processing Magazine* 24(2), 116–125 — the PolyBLEP second-order residual used here for alias suppression (same primitive as SP-029).
- **Repo antecedent:** `sound/synthesis/supersaw_swarm.py` — an existing production `SupersawSwarm` (Native Instruments SuperStarSaw-style, reviewed MusicTech 2026-08-20): two independent 16-oscillator swarms, alternating detune ladder (`_detune_ladder`: 1, −1, 2, −2, … normalized to ±1), per-oscillator pan spread (equal-power), amplitude `drift`, a harmony engine (SCALES/CHORDS degree quantization — `_quantize_semitones`) and a bilinear 2×2 `MorphPad`. Its saw is a naive `2·phase−1` (aliasing documented here, check 7) and it has **no** JP-8000-style feedback phase randomization — SP-141 documents the full architecture and the missing swirl, and is the spec to extend that module with (polyBLEP + fb phase randomization + classic 7-saw ladder).
- **Novelty check (2026-11-14):** `grep -ci` on `methods_db.md` **before** entry: `supersaw` = **0**, `super saw` = **0**, `JP-8000` = **0**, `feedback randomization` = **0**, `swarm` = 27 — **all 27 are Particle Swarm Optimization Composition (PSOC)**, an AI *optimization* composition method (particles in parameter space), unrelated to oscillator stacks. Adjacent-but-different: **SP-029** (one PolyBLEP saw + Moog ladder filter — the source *oscillator* SOSS stacks; its only detune mention is a brief unison extension bullet, n_osc 1–4); **SP-110** PWM (pulse via two saws); **SP-116** DSFS (closed-form bandlimited additive sum — different construction, no detune stack); **SP-047** (4-wavetable vector morph); **SP-097** SHOS (subharmonic *division* stack below f0 — the low mirror of SOSS); **SP-095** TWEMS (drawbar *harmonic* additive stack — fixed integer ratios, no detune, no phase randomization); **SP-074** PHSP (2–3 detuned piano *strings* — physical, not saw oscillators); **SP-102** AM (sidebands). **No SP method documents the detuned-saw stack with feedback phase randomization.** The repo module `sound/synthesis/supersaw_swarm.py` is the production antecedent; the JP-8000/Szabo mechanism itself is not yet in the DB.
- **Verified prototype for this document:** `_web141_soss/verify_sp141.py`, log `_web141_soss/verify_sp141_output.txt`, audio `_web141_soss/sp141_demo.wav` (6.60 s stereo, 291 060 frames/ch, 1 164 284 B) — **13/13 checks pass** (all numbers quoted below are measured).

### Layer

**absolute** (sound production — LAYER_ARCHITECTURE.md). SOSS is a synthesis engine: it consumes per-cell `MusicEvent`s (pitch, velocity, start_tick, end_tick) from a UnitMatrix voice and emits audio buffers — it holds no timing authority beyond the events it is given, emits no events, and decides nothing about composition. It is the *source* stage of the render chain (a voice oscillator), feeding filters/EQ (SP-029/SP-007), then space (SP-009/SP-032/SP-140), then bus dynamics (SP-008/SP-107) and loudness (SP-126). Candidate code path: `sound/synthesis/supersaw_swarm.py` — the existing `SupersawSwarm` (2×16-swarm production variant) — extend with: polyBLEP saws (`_saw` is currently a naive phase saw), the JP-8000-style feedback phase randomization, and a classic 7-saw ladder mode (`n_osc=7`); dispatch from `workflows/musicom_workflow.py::produce(method="SP-141", ...)`.

### Description

A trance lead that is seven leads at once: N *free-running* sawtooth oscillators, each detuned a few cents from one shared root and summed — the classic Roland JP-8000 Supersaw, the sound that defined 1990s anthem trance and still powers modern EDM/pop leads and pads. The stack alone (fb=0) is a *detuned unison*: the oscillators beat against each other at |f_i − f_j| rates, so the tone breathes with a slow chorus-like amplitude pulsation while every partial stays in the harmonic grid of the root. The signature extra ingredient is the **feedback phase randomization**: a lowpassed slice of the output is fed back to continuously, unpredictably nudge each oscillator's phase (never its frequency), so the stack "swirls" — the internal phasing of the detuned saws wanders like a detuned analog ensemble while the perceived pitch stays rock-solid. On top: polyBLEP anti-aliasing (median 33 dB alias-floor suppression over 202 measured fold bins), a harmony quantizer that snaps oscillators onto scale/chord tones (a single-note chord from one key press), per-oscillator pan spread and amplitude drift for stereo width, and O(N) per-sample cost (7 saws ≈ 2.3× realtime, 16 saws ≈ 1.4× realtime in pure Python at 44.1 kHz — check 11). SOSS is the *stack itself*: the source oscillator stage of SP-029's subtractive chain, extended from one saw to N detuned saws with the swirl mechanism.

SOSS is that stack, discretized per note/cell with seeded determinism (free-running phases, feedback weights, and drift all derive from a per-note seed; fb=0 gives exact linear phase trajectories, 1.34e-14 cycle deviation — check 4).

### Technical Mechanics

**1. The detuned stack (N=7 classic).** Each oscillator $i$ runs at
$$f_i = f_0\,2^{c_i/1200}, \qquad c_i = S\cdot\left[0,\;-\tfrac13,\;+\tfrac13,\;-\tfrac23,\;+\tfrac23,\;-1,\;+1\right] \quad (N=7)$$
— an alternating-sign symmetric ladder with magnitudes $\{0,\tfrac13,\tfrac23,1\}\cdot S$, so the outermost saws sit exactly ±S cents and the sum $\sum c_i = 0$ (the stack's centre frequency is the root, detune ≠ transpose). Verified: ladder [0, −4, +4, −8, +8, −12, +12] cents @ S=12, sum 0, max |c| = S (check 1); outer saw = 443.0604 Hz @ f0=440, +12 cents (check 2). Output:
$$y[n] = \frac{1}{N}\sum_{i=1}^{N} \mathrm{saw}\big(\varphi_i[n]\big), \qquad \varphi_i[n+1] = \varphi_i[n] + f_i/f_s \pmod 1 \quad (\text{fb}=0)$$
Free-running initial phases (uniform [0,1) per note, seeded).

**2. Beating = the detune chorus.** Each pair (i, j) amplitude-modulates at $|f_i - f_j|$; the smallest ladder step $\Delta c = S/3$ gives the slowest beat $f_0(2^{\Delta c/1200}-1)$. Verified: dominant envelope modulation **0.500 Hz** @ f0=220 Hz, S=6 c — inside the predicted band [0.254, 0.764] Hz set by the Δc=2 c and S=6 c pairs (check 3). This sub-Hz pulsation is the "detuned against each other over a period of time" motion of the Wikipedia description — perceptually a slow chorus, not vibrato.

**3. PolyBLEP anti-aliasing.** Naive saw $2\varphi-1$ aliases hard; the corrected saw subtracts the second-order residual (Välimäki–Huovilainen):
$$\mathrm{saw}_{\text{corr}}(\varphi, dt) = 2\varphi - 1 - p(\varphi, dt), \qquad p = \begin{cases} 2t' - t'^2 - 1, & \varphi < dt,\; t'=\varphi/dt \\ t'^2 + 2t' + 1, & \varphi > 1-dt,\; t'=(\varphi-1)/dt \\ 0, & \text{otherwise} \end{cases}$$
Verified: harmonic ratios 1 : 0.500 : 0.332 = the ideal 1/k (check 8); alias-floor suppression **median 33.4 dB over 202 alias-image bins** (non-integer f0=331 Hz so folds land between harmonics; min 9.5 dB for folds just below Nyquist — polyBLEP's documented weak spot, max 75.2 dB mid-band; check 7).

**4. Feedback phase randomization (the Szabo swirl).** A one-pole lowpass of the stack output drives per-oscillator phase offsets through smoothed random weights:
$$l_p[n] = l_p[n-1] + a\big(\bar y[n] - l_p[n-1]\big), \quad a = 1 - e^{-2\pi f_c/f_s}, \; f_c \approx 500\,\text{Hz}$$
$$\varphi_i[n+1] = \varphi_i[n] + \frac{f_i}{f_s} + \text{fb}\, l_p[n]\, w_i[n] \pmod 1, \qquad w_i[n+1] = w_i[n] + \alpha\big(\hat w_i - w_i[n]\big), \; \alpha \approx 0.01$$
with $\hat w_i$ a seeded per-oscillator uniform [−1, 1] draw. **The phase offset random-walks; the increment $f_i/f_s$ never changes** — pitch is untouched (this is phase modulation, not FM). Verified: fb=0 → phase deviation from the ideal linear trajectory 1.34e-14 cycles (machine-zero); fb=0.08 → deviation std **0.057 cycles** over 2 s (check 4); accumulated phase modulation −2.68 rad over 20 000 samples at fb=0.08 vs exactly 0 at fb=0 (check 5). The swirl is the *random-walking inter-oscillator phasing* — the sound stays in tune while its internal texture drifts forever, never repeating a phase relationship.

**5. Harmony quantization (scale/chord snapping).** Each oscillator's detune offset (in semitones, $c_i/100$) is snapped to the nearest degree of a scale or chord shape (continuous-space nearest-neighbour, octave-wrapped). Below ~0.5 st the quantizer is a no-op (all saws on the root — pure detune); at semitone-scale spreads it spreads the stack onto scale tones. Verified: major-scale snapping of the ±2.5-st ladder yields offsets [0, −1, 0, −1, 2, −3, 2] st — a root/3rd/2nd/4th cluster from one key press (check 10). Repo: `SCALES`/`CHORDS` tables + `_quantize_semitones` in `supersaw_swarm.py`.

**6. Spread → partial clusters.** Each harmonic splits into a cluster of sub-peaks spaced by the detune ladder; measured **5 peaks spanning 2.00 Hz** at harmonic 1 (f0=110 Hz, S=20 c) with outer separation $\approx 2 f_0 (2^{S/1200}-1) = 2.55$ Hz predicted (check 9). Cluster width is the spectral thickness dial.

**7. Numerical.** O(N) per sample (N saws + N polyBLEP evals + 1 feedback LP); measured t(N) = 262/429/754 ms for N = 7/16/32 over 0.6 s @ 44.1 kHz — linear in N (check 11); soft-normalized peak exactly 1.0 (check 12); deterministic per seed (bit-identical same-seed rebuild, different-seed differs — check 6); WAV artifact exact 44 + 4·frames·ch bytes (check 13).

### Musical Elements Framework

- **PITCH**: root-exact by construction — the zero-detune ladder element is the pure saw at f0, and $\sum c_i = 0$ keeps the stack's centre on the root (detune ≠ transpose; contrast FM's index-dependent pitch shift). Spread S = thickness dial (0 = single saw, ~6–15 c = chorus, semitones = cluster chord). fb swirl is pitch-stable phase movement — the perceived pitch never wanders (checks 4–5). Harmony quantizer maps oscillators onto scale/chord tones — pitch-class clusters from one note.
- **RHYTHM**: the slow beats ARE the rhythm layer of the timbre: 0.25–1.5 Hz envelope pulsation at 220 Hz with S=6 c (check 3) — the "chorus rate"; fb adds micro-unpredictability to the internal phasing (a quasi-random phase texture under any rhythmic grid). Note rhythm comes from the cell's events; the classic trance stab is SOSS + a fast amplitude envelope (the filter/amp ADSR of the SP-029 chain) — the stack supplies the dense detuned attack.
- **HARMONY**: a single key press is a *unison* in the middle of the stack but a *chord* at the edges once the harmony quantizer engages (offsets [0, −1, 0, −1, 2, −3, 2] st, check 10) — the high-spectrum mirror of SP-097 SHOS's subharmonic stack. Multi-voice rows voicing chords on top give full harmonic function; dense detuned stacks mask tuning errors of big chords (the trance trick).
- **STRUCTURE**: section columns = {spread, fb, harmony, harmony_root, drift, pan_spread} — the classic build-up is a column sequence ramping spread 4→25 c and fb 0→0.3; a chorus/break contrast is a harmony snap (detune stack → scale cluster). Per-note seeded determinism makes every cell reproducible; fb ramps are the macro-gesture ("swirl in").
- **TEXTURE**: (a) N (7 classic / 16 swarm) — density, (b) S — chorus width to cluster chord, (c) fb — swirl rate/presence (0 = static detune chorus, 0.3 = restless analog ensemble), (d) drift — per-oscillator amplitude shimmer, (e) pan_spread — stereo field, (f) harmony clusters — tonal density. The texture continuum is single-saw → tight unison → detuned chorus → scale cluster, all from one root and O(N).

### UnitMatrix Integration

**Voices = rows = supersaw instances.** Row $v$ carries `{n_osc, spread_cents, fb, fb_cutoff, drift, harmony, harmony_root, pan_spread, brightness}`. Example rows: "trance lead" (n_osc 7, S 10 c, fb 0.15, drift 0.2, pan 0.4), "supersaw pad" (n_osc 16, S 25 c, fb 0.3, harmony "minor", drift 0.4, pan 0.8), "bass stab" (n_osc 4, S 4 c, fb 0.05, one octave down), "chord stab" (n_osc 7, S 120 c, harmony "maj7", harmony_root −12). Each row renders its cells through its own seeded instance (row seed = seed·101 + row, the repo's per-voice seeding convention).

**Sections = columns = timbre states.** Column $j$ holds `{spread_scale, fb, harmony, harmony_root, drift, pan_spread, brightness}` — a column change is a timbre change (tight verse lead → wide build-up swirl → scale-cluster chorus). The classic build is a monotone column ramp; a breakdown snaps fb to 0 (pure detune) and S to a semitone cluster. SOSS is sample-count preserving per cell; a note released at a seam simply stops at the cell boundary (amp envelope tails render into the buffer margin — no re-timing across seams, the SP-136/SP-138 seam rule).

**Cells = MusicUnit.** Cell (v, j): each `MusicEvent(pitch, velocity, start_tick, end_tick)` renders as a SOSS note — pitch → f0, end−start → duration, velocity → note gain (before the soft normalize); events end exactly at `section_len` (the `_unit_from_events` zero-drift pattern). Deterministic per cell (seeded by cell id); same cell → bit-identical audio (check 6).

**Produce dispatch:** `produce(midi_path, method="SP-141", params={"rows": {"lead": {"n_osc": 7, "spread_cents": 10, "fb": 0.15}, "pad": {"n_osc": 16, "spread_cents": 25, "fb": 0.3, "harmony": "minor"}}, "columns": {"A": {"spread_scale": 1.0, "fb": 0.1}, "B": {"spread_scale": 2.5, "fb": 0.3}}, "fs": 44100})`. Stage order: **SOSS (source) or SP-001/SP-011/SP-134/... per row** → per-row filter (SP-029 chain) / EQ (SP-007) → spatialize (SP-021/SP-053/SP-119) → space/tail (SP-009/SP-032/SP-140) → bus dynamics (SP-008/SP-107) → loudness (SP-126) → dither (SP-122). SOSS = the voice oscillator; everything downstream is shared with the other source methods. NOTE (2026-11-14): the `produce()` dispatch map in `workflows/musicom_workflow.py` carries a parallel surveillance namespace whose SP numbering diverges from methods_db (see `hermes_agent/surveillance.md`); methods_db numbering is authoritative.

### Pitfalls

1. **Naive saw aliasing ruins the stack.** `2·phase−1` at 7× detune piles folded harmonics into a −27 dB hiss floor; polyBLEP cuts it by a median 33.4 dB (check 7). Do not ship the naive `_saw` of `supersaw_swarm.py` as-is for top-register leads — and know polyBLEP's limit: folds landing just below Nyquist get only ~10 dB (min of the measured distribution); for very high leads consider 2× oversampling or SP-041 bandlimited wavetables.
2. **Ladder normalization traps.** If the ladder isn't normalized so the outermost saw is exactly ±S, the spread knob lies (S≠S). If $\sum c_i \neq 0$, the stack's centre frequency shifts — detune silently becomes transpose. The alternating-sign construction guarantees both (check 1); verify with the frequency check (check 2).
3. **fb is phase, not frequency.** Adding `fb·lp·w` to the *frequency* turns the swirl into FM — the perceived pitch wobbles (a detuned-vibrato mess), destroying the supersaw's stable-pitch signature. The mechanism requires the random walk to live in the phase offset (check 4: pitch trajectory untouched, deviation only in phase). Also keep fb·lp·w in *cycles* (phase units), not radians, or the swirl gain is off by 2π.
4. **Free-running phases ≠ determinism by default.** Free-running means every render differs unless seeded. Seed per note/cell (row seed = seed·101 + row) or the same cell renders differently on every pass — breaks golden-audio regression nets (check 6 exists because this bit twice).
5. **Low-register beats disappear.** At f0=55 Hz a 2-cent pair beats at 0.064 Hz — sub-audible, the bass just sounds like slow amplitude drift; use larger spreads or fewer saws in the bass (the pad row of the repo demo already widens S for low swarms).
6. **Harmony quantizer half-semitone bucket trap.** Offsets below ~0.5 st all snap to the root — a "harmony" setting with a small spread silently collapses the stack to unison (measured all-zero offsets before the fix in the prototype; the repo demo's 45-cent harmony shows the same near-collapse). Only spreads ≳ 1 st create real clusters — verify with the offset histogram (check 10).
7. **Peak normalization hides RMS loss.** Soft-normalizing by peak makes a 16-saw stack quieter in RMS than a single saw at the same peak — against other voices the stack vanishes in the mix. Use RMS/equal-power matching per voice (or the DB's SP-126 loudness stage) rather than per-voice peak normalization.
8. **Neighbour audit.** SP-029 = the single PolyBLEP saw + ladder filter that SOSS stacks (its unison-detune bullet is a 1–4 saw extension, not the stack architecture); SP-110 PWM = pulse via two saws; SP-116 DSFS = closed-form bandlimited additive (no detune stack, no swirl); SP-047 = 4-table vector morph; SP-097 SHOS = subharmonic *division* stack below f0 (SOSS's low mirror); SP-095 TWEMS = fixed-ratio drawbar additive (no detune); SP-074 = 2–3 detuned piano strings (physical); SP-102 AM = sidebands. SOSS = the detuned free-running saw stack + feedback phase randomization, O(N). Repo: `sound/synthesis/supersaw_swarm.py` (2×16-swarm production variant, `_detune_ladder`, `_quantize_semitones`, `MorphPad` — extend with polyBLEP + fb phase randomization + 7-saw mode per this spec; the classic JP-8000/Szabo mechanism is the DB's first).
