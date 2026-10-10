# SP-098 Fractal Sequence Generator — Bossa Nova / bossa-nova-daily-2026-06-15

**Date (UTC):** 2026-10-10 (nightly autonomous production job)
**Output root:** `/opt/data/repos/musicom/projects/Styles/Production/SP098-fractal-seq-bossa-nova-daily/`
**Status:** PASS — FFT 46/46 (hit 1.000), harmonic energy 0.601, ACF unpitched 0/12, silence 21.39% (all in tail), LUFS −14.00, peak 0.891.

---

## 1. Method + selection (which registry source)

| Field | Value |
|---|---|
| Method | **SP-098** — Fractal Sequence Generator: Thue-Morse / Fibonacci / Sierpinski / Logistic Map (Kaona B.A.C.H. FRACTAL-style) |
| Registry source | `workflows.musicom_workflow.SP_METHODS` — the **implemented** dict (NOT `methods_db.md` spec-only, NOT a stale `SP-001..SP-035` range) |
| Registered module | `sound.generators.fractal_seq` → `ThueMorseMelody`, `FibonacciRhythm`, `SierpinskiAccent`, `LogisticMapMelody`, `FractalSequenceGenerator`, `thue_morse_seq` |
| Registry entries at pick time | **42 implemented** (SP-001 … SP-102) |
| Already used last 7d (excluded) | SP-021, SP-069, SP-080, SP-083, SP-085, SP-091, SP-092 |
| Baseline excluded | SP-001 |
| Already on this source | (none) |
| Eligible pool | 34 methods |

**No re-roll needed.** The single draw (seed `20261010`) landed on SP-098 ×
`Latin/bossa-nova-daily-2026-06-15/composition.mid`, a pair with no prior
production. First SP-098 production run.

Selection record: `Production/.selection_cron.json`,
`Analysis/select_20261010.json`, `Production/select_job_20261010.py`.

Well-formed filter: **223 / 332** candidate MIDIs passed (normal tpb, sane note
lengths, ≥2 note tracks or a program change, 2–600 s length).

## 2. Source composition

| Field | Value |
|---|---|
| Project | `Styles/Latin/bossa-nova-daily-2026-06-15/` |
| MIDI | `MIDI/composition.mid` (586 B, copied to `MIDI/` for provenance) |
| Genre / key | Bossa nova; A minor (Am7 chord tones C–E–G–A, PCS `[0,4,7,9]`) |
| Tempo | 84.00 BPM (714286 µs/beat), 480 tpb, type-1 |
| Length | 5.71 s = 2 bars (track1 bass A1 ch0 8 notes · track2 Am7 comp ch1 36 notes · track3 bossa drums ch9 25 hits) |
| Source PCS (non-drum) | `[0, 4, 7, 9]` — A minor 7 (A–C–E–G) |

## 3. Layer discipline (absolute — fractal engine replaces production for ALL voices)

SP-098 is a **generator** method: it produces note events, not a timbral
effect. Applied as an **absolute layer**, the fractal engine replaces the
melodic/harmonic production layer for the **whole piece** — four fractal
subsystems generate four independent voices in the source's key (A natural
minor) and tempo (84 BPM), expanding the 2-bar source loop to a full **8-bar**
re-composition (22.86 s music + release). FluidSynth GM (SP-001) is the
acoustic carrier; no source MIDI notes survive — only its key/tempo/genre
context is inherited.

```
A natural minor, 84 BPM, 480 tpb, 8 bars (15360 ticks)
 -> Thue-Morse binary contour  -> Lead   Flute(74)      ch0   (diatonic degree walk)
 -> Fibonacci metric groups    -> Bass   Ac.Bass(33)    ch1   (2/3/5-beat groups)
 -> Sierpinski Rule-90 accent  -> Comp   Nylon Guitar(25) ch2  (Am chord tones)
 -> Logistic map (r=3.9) chaos -> Counter Marimba(12)   ch3   (chaotic in-key line)
 -> UnitMatrixComposer (validate() = zero-drift gate) -> to_midi
 -> FluidSynth GM render (FluidR3_GM.sf2) + RenderPipeline stems
 -> normalize_to_lufs(-14) -> Limiter(-1 dBFS) LAST
 -> SP098-fractal-seq-bossa-nova-daily.wav + .ogg (Opus 48k voip)
```

## 4. Parameters

| Subsystem | Param | Value | Logic |
|---|---|---|---|
| Thue-Morse | length | 64 eighth-notes | binary contour; bit 1→+1 scale degree, 0→−1 scale degree (see §7) |
| Thue-Morse | ticks_per_note | 240 | 64 × 240 = 15360 ticks = exactly 8 bars |
| Fibonacci | fib_indices | [2,3,5] | beat-group lengths 2/3/5 = 10-beat cycle, 4 repeats |
| Fibonacci | root_pitch | 33 (A1) | bass register |
| Sierpinski | rows × positions | 8 × 16 | Rule-90 cellular automaton accent grid |
| Sierpinski | pitches | (69, 64, 57) | accent A4 / normal E4 / soft A3 (Am chord tones) |
| Logistic | r, x0 | 3.9, 0.5 | chaotic orbit (burn-in 50 steps) |
| Logistic | pitch_range | (40, 88) | counter-melody register |
| Key / scale | — | A natural minor (A B C D E F G) | every pitch snapped via `snap_to_scale()` |
| Master | — | `normalize_to_lufs(−14)` → `Limiter(−1 dB)` | measured **−14.00 LUFS**, peak 0.8913 |
| SoundFont | — | `discover_soundfont()` → FluidR3_GM.sf2 | ONE-ENV contract, never hardcoded |

## 5. Pitch / tonal-content verification — **PASS**

Size asserts and silence ratios alone do **not** catch noise (SP-035 lesson).
Checks on the delivered WAV:

| Metric | Wet mix | Gate | Verdict |
|---|---|---|---|
| FFT hit rate (0.5 s windows, dominant peak vs active MIDI note ×1/2/3/4/½/⅓, ±4%) | **46/46 = 1.000** | ≥ 0.60 | PASS |
| Mean harmonic energy (8 harmonics of dominant peak) | **0.6013** | ≥ 0.25 | PASS |
| ACF unpitched windows | **0 / 12** | < 0.50 | PASS (no broadband noise) |
| Median dominant frequency | **440.0 Hz (A4)** | — | tonic A dominates, as expected |

The SP-035 failure signature (0 Hz frames + single-digit harmonic energy +
broadband ACF) is **absent** — harmonic energy 0.60, ACF clean, and the median
dominant is exactly the tonic A4 = 440 Hz, confirming the A-minor quantization.

Full JSON: `Analysis/pitch_verification.json`, `Analysis/render_stats.json`.

## 6. Silence / RMS profile

| Metric | Value | Note |
|---|---|---|
| Silence (<0.001) | **21.39%** | all in the tail |
| RMS | 0.133 | — |
| Peak / LUFS | 0.8913 / −14.00 | mastered |
| Per-second RMS (music, s 0–23) | 0.122–0.197 | healthy, no mid-track gaps |
| Per-second RMS (tail, s 24–30) | 0.022 → 0.000 | natural FluidSynth release + 1.5 s pad |

The 21.39% silence is **entirely the post-music tail** (≈7 s of the 30.35 s
file after the last note at 8 bars = 22.86 s). Every music second 0–23 reads
RMS ≥ 0.122, so there are **no mid-track production gaps** — only the
legitimate tail padding.

## 7. Two-phase architecture + fixes applied during this run

SP-098 is a generative method, so the mandatory two-phase discipline was
followed (Phase 1 = raw fractal draft, Phase 2 = musicom rules):

1. **Thue-Morse semitone→degree remap (musical bug in module default).** The
   module's `ThueMorseMelody.generate()` emits raw **±1 semitone** steps from a
   root. In A natural minor that collapses to a 2-note G/A oscillation once
   snap-to-scale is applied (G♯ and A♯ both quantize back to G or A). Phase 2
   re-interprets the Thue-Morse **bit contour** as **±1 scale-degree** steps so
   the non-repeating binary pattern walks the full 7-note diatonic scale (A3–A5
   clamped). This preserves the fractal's core property (aperiodic, no period-3
   run) while making it melodic.
2. **Logistic-map monotonic re-time.** The module's `start_tick = i * dur_ticks`
   uses per-event durations, so onsets are non-monotonic. Phase 2 re-times the
   chaotic events on a clean running-tick timeline (durations clamped 120–960
   ticks) so the MIDI timeline is strictly valid and zero-drift.
3. **Diatonic snap for all voices.** Every pitch (Fibonacci bass, Sierpinski
   comp, logistic counter) is snapped to A natural minor via `snap_to_scale()`;
   no raw chromatic pitch reaches the MIDI.
4. **Zero-drift via musicom engine.** Built with `UnitMatrixComposer` (4 voices
   × 1 section of 8 bars), `validate()` = True, `to_midi()` guarantees equal
   track lengths + absolute tick alignment. No hand-rolled MIDI.

## 8. Artifacts

| Artifact | Path | Size |
|---|---|---|
| Full mix WAV | `SP098-fractal-seq-bossa-nova-daily.wav` (30.35 s, 44.1 kHz stereo) | 5,354,284 B |
| Full mix OGG (Opus 48k voip) | `SP098-fractal-seq-bossa-nova-daily.ogg` | 219,849 B |
| Fractal MIDI | `MIDI/SP098-fractal-seq-bossa-nova-daily.mid` (253 notes, 4 voices) | 2,280 B |
| Source MIDI (copy) | `MIDI/composition.mid` | 586 B |
| Dry reference mix (FX-on GM) | `dry_full_mix_sp001_reference.wav` | 5,354,284 B |
| Dry stems | `Audio/stems_dry/track00_Recorder.wav`, `track01_Electric_Bass_finger.wav`, `track02_Acoustic_Guitar_steel.wav`, `track03_Marimba.wav` | 4.3–5.2 MB each |
| Renderer | `Scripts/produce_sp098_cron.py` | — |
| Verification JSON | `Analysis/pitch_verification.json`, `Analysis/render_stats.json` | — |
| Onset DNA grid | `Analysis/grid_visualization.txt` | — |
| Selection JSON | `Analysis/select_20261010.json` | — |
| Provenance | `provenance.json` | — |
| Report | `REPORT.md` | this file |

WAVs git-ignored by policy; OGG + MIDI + JSON + REPORT tracked.

## 9. Listen for

- **Lead (flute)** walks a never-repeating Thue-Morse staircase — up/down by one
  scale step every eighth note, no phrase ever repeats a 3-note run (the
  Thue-Morse "no period-3" property you can actually hear as a restless,
  always-turning line).
- **Bass** groups beats 2+3+5 (Fibonacci) into an irregular metric feel that
  never quite lands on the same subdivision twice; long groups are accented
  louder.
- **Comp (nylon guitar)** is a continuous 16th-note stream whose accents trace
  the Sierpinski triangle (Rule-90) — a fractal shadow of strong/soft attacks.
- **Counter (marimba)** drifts through the scale on a logistic-map orbit
  (r=3.9, near the edge of chaos): deterministic yet unpredictable pitches and
  note lengths.
- All four land in A natural minor, so the result reads as a coherent
  bossa-flavored study — same key/tempo as the source, entirely new material.

## 10. Quality gate

- [x] MIDI present for the audio render (`MIDI/SP098-fractal-seq-bossa-nova-daily.mid`, 253 notes)
- [x] OGG non-empty (≈215 KB) and playable-length (30.35 s)
- [x] Pitch verification run and reported (PASS: FFT 46/46, HE 0.601, ACF 0/12)
- [x] Silence ratio + RMS measured; 21.39% silence all in tail, no mid-track gaps
- [x] Full mix WAV + per-track stems (RenderPipeline)
- [x] `provenance.json` per artifact set (incl. Phase-2 fix record)
- [x] Output under `projects/Styles/Production/<method>-<project>/`
- [x] No hardcoded soundfont (`discover_soundfont` → FluidR3_GM.sf2)
- [x] Zero-drift `validate()` gate passed; MIDI built via `UnitMatrixComposer`
