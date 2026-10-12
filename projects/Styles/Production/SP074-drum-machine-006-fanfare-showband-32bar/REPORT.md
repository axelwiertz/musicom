# SP-074 Eight-Channel Sample Drum Machine — Fanfare / 006-fanfare-showband-32bar

**Date (UTC):** 2026-10-12 (nightly autonomous production job)
**Output root:** `/opt/data/repos/musicom/projects/Styles/Production/SP074-drum-machine-006-fanfare-showband-32bar/`
**Status:** PASS — synth pitch 117/117 (hit 1.000), harmonic energy 0.474, drum envelope grid 8.80 Hz (exact), ACF unpitched 0/30, silence 2.74 %, LUFS −14.00, peak 0.8913.

---

## 1. Method + selection (which registry source)

| Field | Value |
|---|---|
| Method | **SP-074** — Eight-Channel Sample Drum Machine + Sequencer (Erica Synths Bullfrog Drums style) |
| Registry source | `workflows.musicom_workflow.SP_METHODS` — the **implemented** dict (NOT `methods_db.md` spec-only, NOT a stale `SP-001..SP-035` range) |
| Registered module | `sound.generators.drum_machine` → `BullfrogDrums`, `Kit`, `SampleChannel`, `CVChannel`, `synthesize_drum_samples` |
| Registry entries at pick time | **45 implemented** (SP-001 … SP-105) |
| Already used last 7d (excluded) | SP-026, SP-069, SP-080, SP-085, SP-091, SP-092, SP-098 |
| Baseline excluded | SP-001 |
| Already on this source | (none) |
| Eligible pool | 37 methods |

Selection record: `Production/.selection_cron.json`, `Analysis/select_20261012.json`,
`Production/select_job_20261012.py`.

Well-formed filter: **227 / 336** candidate MIDIs passed (normal tpb, sane note
lengths, ≥2 note tracks or a program change, 2–600 s length).

## 2. Source composition

| Field | Value |
|---|---|
| Project | `Styles/Fanfare/006-fanfare-showband-32bar/` |
| MIDI | `MIDI/showband32.mid` (6026 B, copied to `MIDI/` for provenance) |
| Genre / key | Fanfare showband; **Bb major** (pcs `{10,0,2,3,5,7,9}`) |
| Tempo | 132.00 BPM (454545 µs/beat), 480 tpb, type-1 |
| Length | 58.18 s = 32 bars × 1920 ticks = 61440 ticks |
| Voices | Trumpet prog56 ch0 (147 notes, lead) · Trombone prog57 ch1 (96 notes, harmony) · Tuba prog58 ch2 (80 notes, bass) · GM snare ch9 (356 hits, note 38 only — marching/paradiddle/roll) |
| Chord plan | A bars 0-7 & 16-23 `[1,4,7,3,6,2,5,1]`, B bars 8-15 `[6,2,5,1,4,2,5,5]`, C bars 24-31 `[1,5,4,5,1,4,5,1]` (diatonic Bb major) |
| Source PCS (non-drum) | `{0,2,3,5,7,9,10}` — fully diatonic to Bb major |

## 3. Pre-flight rules-adherence gate — FAIL (grid sync) → REWORK → PASS

| Rule | Before | After rework | Evidence |
|---|---|---|---|
| 1. Grid sync (onsets on 16th = 120 grid) | **FAIL — 246 off-grid** | **PASS — 0** | source had ±6-tick humanization on every pitched onset |
| 2. Harmony (in-key AND chord-tone) | PASS — 0 out-of-scale, 0 out-of-chord | PASS — 0 / 0 | all non-drum notes ∈ Bb major AND a root/3rd/5th of their bar's chord |
| 3. Zero-drift (equal track length) | PASS — all tracks 61440 | PASS — all tracks 61440 | 4 note tracks end exactly at 61440 |

**Rework applied (two-phase):**
1. Saved the humanized original as `MIDI/showband32-phase1.mid` (phase-1 raw character preserved).
2. Grid-quantized every pitched `note_on`/`note_off` to the 16th-note grid (120 ticks) via
   onset-snap, with `note_off` snapped against its own `note_on` (min duration one grid step)
   so the track stays monotonic. Drum track (ch9) left untouched (rule 1 audits pitched voices only).
3. Re-exported `MIDI/showband32.mid`, re-ran the audit → **all three rules clean (0/0/0, zero-drift true)**.

Harmony needed **no** rework (already 0 out-of-scale, 0 out-of-chord). The only
violation was the source's deliberate micro-timing humanization (±6 ticks) which
breaks rule 1; quantized away for the production pass, raw kept in the phase1 sidecar.

## 4. Layer discipline (absolute — generator replaces production for ALL voices)

SP-074 is a **generator** method: it produces a full Bullfrog Drums performance,
not a timbral effect. Applied as an **absolute layer**, the 8-channel drum machine
re-produces the WHOLE piece — the 7 sample drum channels replace the percussion
(the source's GM snare), and the 8th channel (the Bullfrog **CV lane**, "sequence
the Bullfrog Synth") carries the key/genre context by driving a Bb-major trumpet
voice (FluidSynth GM prog 56 as the stand-in synth). No source MIDI notes survive;
only key (Bb major), tempo (132 BPM), form (32 bars) and the fanfare rhythm DNA are inherited.

```
Bb major, 132 BPM, 480 tpb, 32 bars (61440 ticks)
 -> 7 sample channels: kick / snare / hat / tom / clap / rim / cymbal
    (fanfare rhythm DNA: marching pulse, paradiddle eighths in B, 16th roll+flams in C)
 -> CV lane (ch8): 64-step X0X pattern = 4-bar Bb-major harmonic cell I-IV-vii°-iii
    [root+fifth per bar], looped 8x -> FluidSynth trumpet (prog 56)
 -> dry reference: fluidsynth -ni -R0 -C0 -g1.2 (reworked source, FluidR3_GM.sf2)
 -> drum bus + synth bus -> mix -> normalize_to_lufs(-14) -> Limiter(-1 dBFS) LAST
 -> SP074-drum-machine-006-fanfare-showband-32bar.wav + .ogg (Opus 48k voip)
```

## 5. Parameters

| Param | Value | Logic |
|---|---|---|
| Drum channels | 7 (kick/snare/hat/tom/clap/rim/cymbal) | `Kit.demo_kit()` factory samples |
| Kit shaping | kick decay 1.0, snare 0.85, hat 0.6, tom pitch 0.9, clap pan −0.25, rim pan +0.25, cymbal decay 1.2 | Bullfrog per-channel param set |
| Kick | steps 0 & 8 every bar (+4,12 in C) | marching pulse beats 1 & 3 |
| Snare | A: backbeat 4/12 + ghost 2/6/10/14 · B: paradiddle eighths · C: 16th crescendo roll + flams @4,12 | fanfare roll/paradiddle DNA |
| Hat | eighths (A/B), 16ths (C) | subdivision drive |
| Tom/Clap/Rim/Cymbal | tom fills @bar 7/15/23 · clap @every 4th bar · rim cadence @3,7,11,… · cymbal crash @section starts | section/cadence markers |
| Swing / flams | swing 0.12 · flams {(snare,step):1} in C | subtle human feel |
| CV cell | chords `[1,4,7,3]` (I IV vii° iii), root+fifth each, single-octave scale degrees | 4-bar Bb-major harmonic loop |
| Synth voice | FluidSynth trumpet prog56 ch0, root (beats 1-2) + fifth (beats 3-4) per bar | CV-lane readback, looped 8× |
| Key / scale | Bb major | every CV degree snapped via `Scale7ChordDegree.get_diatonic_note` |
| Master | `normalize_to_lufs(−14)` → `Limiter(−1 dB)` | measured **−14.00 LUFS**, peak 0.8913 |
| SoundFont | `discover_soundfont()` → FluidR3_GM.sf2 | ONE-ENV contract, never hardcoded |

## 6. Pitch / tonal-content verification — **PASS**

Drum machines are unpitched by design, so pitch verification is split:

| Metric | Synth bus (CV trumpet) | Full mix | Gate | Verdict |
|---|---|---|---|---|
| FFT hit rate (0.5 s windows, dominant peak vs active trumpet note ×1/2/3/4/½/⅓, ±4 %) | **117/117 = 1.000** | 1.000 | ≥ 0.60 | PASS |
| Mean harmonic energy (8 harmonics of dominant peak) | **0.4739** | 0.4671 | ≥ 0.25 | PASS |
| ACF unpitched windows | — | **0 / 30** | < 0.50 | PASS (no broadband noise) |
| Drum envelope grid peak | **8.80 Hz** (expected 8.80 Hz = 16th-note rate) | — | ±5 % | PASS (drums on 16th grid) |

The SP-035 failure signature (0 Hz frames + single-digit harmonic energy + broadband
ACF) is **absent**. Harmonic energy 0.474 on the trumpet voice and a drum envelope
that peaks exactly at the 16th-note rate confirm the drum machine produced clean,
tonally-coherent, grid-locked output.

Full JSON: `Analysis/pitch_verification.json`, `Analysis/render_stats.json`,
`Analysis/cv_sequence.json`.

## 7. Fixes & discoveries during run

1. **Mido delta-recompute drift (quantize bug).** First quantize pass snapped only
   `note_on` onsets and recomputed deltas with `prev = snapped_abs_t[i]`. When a
   humanized `note_off` (e.g. 483) preceded a `note_on` snapped down to 480, the
   `dt<0 → 0` clamp fired but `prev` used the *snapped* (not *emitted*) time,
   silently shifting the whole tail → zero-drift broke (track ends 61440 vs 61442)
   and 21 onsets stayed off-grid. Fix: pair each `note_on` with its `note_off`,
   snap both to grid with `note_off ≥ note_on + 120`, and advance `prev += dt`
   (actual emitted time). Result: grid 0 off, zero-drift intact.
2. **CV lane is a 64-step X0X pattern, not 512.** `CVChannel.set()` stores
   `step % 64`, so programming 32 bars wrapped every 4 bars and only the last 4
   survived (8 entries). The Bullfrog CV lane is a 4-bar (64-step) loop by design.
   Fix: program an explicit 4-bar Bb-major harmonic cell `I-IV-vii°-iii` and loop
   it 8× for the synth voice (documented; the audible result is unchanged).
3. **Chord-tone audit pc-ordering.** `sorted(SCALE_PCS)` sorts numerically to
   `[0,2,3,5,7,9,10]` but Bb major ascending from tonic is `[10,0,2,3,5,7,9]`; the
   naive sort made degree-1 chord read as `{C,Eb,G}` instead of `{Bb,D,F}` (323
   false "out-of-chord"). Fix: explicit tonic-ascending pc list.

## 8. Silence / RMS / LUFS profile

| Metric | Value |
|---|---|
| LUFS (integrated) | **−14.00** |
| Peak | **0.8913** (−1.0 dBFS, at the limiter ceiling) |
| Silence ratio | **2.74 %** (release tail only, no mid-track gaps) |
| RMS | 0.1468 |
| Length | 59.18 s (drums) / 58.18 s source + release tail |

Per-second RMS map in `Analysis/render_stats.json`.

## 9. Files

| Path | Size | Note |
|---|---|---|
| `SP074-drum-machine-006-fanfare-showband-32bar.wav` | 10,439,716 | final mix (stereo 44.1k int16) |
| `SP074-drum-machine-006-fanfare-showband-32bar.ogg` | 553,904 | Opus 48k voip (Telegram) |
| `dry_full_mix_sp001_reference.wav` | 10,680,620 | FluidSynth SP-001 dry reference of reworked source |
| `Audio/stems/drum_machine_7ch.wav` | 10,439,716 | 7-channel drum bus |
| `Audio/stems/cv_synth_trumpet.wav` | 10,669,868 | CV-driven trumpet synth bus |
| `MIDI/showband32.mid` | 6,026 | reworked (grid-quantized, validate-clean) |
| `MIDI/showband32-phase1.mid` | 6,026 | original humanized (phase-1 raw character) |
| `MIDI/showband32-cv-synth.mid` | 634 | CV-driven trumpet voice (64 notes, 61440 ticks) |
| `provenance.json`, `Analysis/*.json`, `Analysis/grid_visualization.txt` | — | full record |
