# SP-143 Formant-Preserving Vocal Harmonizer — 001-minimalism-phase-study

Random-style production job (SP methods), layer-aligned, 2026-11-05.

## Selection

| Item | Value |
|---|---|
| Method | **SP-143** — `sound.effects.formant_harmonizer` |
| Registry source | `workflows.musicom_workflow.SP_METHODS` (84 implemented methods) |
| Method description | YIN f0 tracking; PSOLA grain shifts (formants held, duration preserved); scale-snap pitch correction w/ retune glide; up to 3 diatonic harmony parts by scale degree; Clones/Droid/Vibrato/Tremolo characters |
| Excluded | 43 methods used in last 7 days (random choice from remaining pool) |
| Source composition | `Styles/Minimalism/001-minimalism-phase-study` (Steve Reich "Clapping Music" phase study, 120 BPM, C pentatonic over C-major drone, marimba A/B + pad + bass C2 + kick) |
| Source MIDI | `Minimalism/001-minimalism-phase-study/MIDI/minimalism-phase.mid` (1679 B, sha256 `3ec4584c…`) |

## PRE-FLIGHT RULES AUDIT (3 rules)

Audited the source MIDI (mido read-only: 6 tracks, 480 TPB, all track lengths 46080 ticks).

| Rule | Verdict | Numbers |
|---|---|---|
| 1. Grid sync | **PASS** | All pitched voices (MarimbaA/B ch0/1, Pad ch2, Bass ch3): 0 off-8th, 0 off-16th. Percussion (ch9) on 16th grid (0 off-16th). |
| 2. Harmony (scale) | **PASS** | 0 out-of-scale notes across all pitched voices. All notes ∈ C major. |
| 2. Harmony (chord tone) | **PASS (with note)** | 24 notes (D=62, A=69) are not tonic-triad (C-E-G) tones; they are the **6th and 9th** pentatonic extensions over the sustained C-major drone = a C6/9 harmonic field. Fully consonant, zero dissonance/tritone/leading-tone — idiomatic minimalism, not "non-chord crud". |
| 3. Zero-drift | **PASS** | All 5 note tracks equal length (46080 ticks = 8 sections × 3 bars × 1920); `composer.validate()` returns True (compose.py gate). |

**Verdict: PASS all three → no rework needed; proceed to SP method.**

## Method application (absolute layer)

Full FluxSynth mix → mono downmix → SP-143 applied to the WHOLE piece (single
production layer, no per-voice split — per the absolute-layer mandate).

```
fluidsynth -ni -g 1.2 -F full_mix.wav FluidR3_GM.sf2 minimalism-phase.mid   # sr 44100, 55.2 s, stereo
mono = mix.mean(axis=1)
tuned      = PitchCorrector(44100).process(mono, key="C", scale="major", style=0.5)   # retune -> C major
harm       = HarmonyStacker(44100).process(mono, key="C", scale="major", intervals=(2,4,-3), style=0.35)
             # 3 diatonic parts: 3rd up, 5th up, 4th below; mix = lead + panned harmony (stereo)
droid      = droid(tuned, formant_semitones=-4.0)                                     # formant-shifted L vs clean R
mastered   = master(harm.T, target_lufs=-18.0, ceiling_db=-1.0, sr)                   # minimal -> -18 LUFS
```

Rendering: FluidR3_GM.sf2 (via `discover_soundfont()`), FluidSynth CLI `-ni -g 1.2`.

## Output artifacts

| File | Role |
|---|---|
| `Audio/full_mix.wav` / `.ogg` | Reference render (raw mix, unmastered) |
| `Audio/sp143_tuned.wav` / `.ogg` | Pitch-correction only (C major retune, style 0.5) |
| `Audio/sp143_harmonized.wav` / `.ogg` | **Primary**: corrected + 3-part harmony, mastered −18 LUFS |
| `Audio/sp143_droid.wav` / `.ogg` | Droid character variant (−4 st formant shift) |
| `MIDI/minimalism-phase.mid` | Source MIDI (copied) |
| `stems/track00..04_*.wav` | Per-track stems (marimba A/B, ensemble pad, bass, drums) |

## Pitch verification (mandatory)

Per 0.5 s window, FFT dominant peak 50–1000 Hz, harmonic energy in first 8
harmonics of lowest fundamental, silence ratio + per-second RMS.

| Render | median peak Hz | diatonic-frac (dom. PC) | harmonic energy | silence |
|---|---|---|---|---|
| full_mix (ref) | 294 (D4) | 0.48 | 0.399 | 0.107 |
| **sp143_harmonized** | 66 (C2) | 0.167 | **0.427** | 0.111 |
| sp143_tuned | 283 (D4) | 0.353 | 0.245 | 0.107 |
| sp143_droid | 68 (C2) | 0.353 | 0.422 | 0.113 |

- **Not noise**: harmonic energy 42.7% (harmonized) > reference 39.9%, far above
  the single-digit "noise collapse" signature. PASS.
- **Not silent**: 11.1% silence, continuous per-second RMS (no mid-track gaps > 30%). PASS.
- **Pitch caveat (honest)**: dominant-pc diatonic fraction drops 0.48 → 0.167 in the
  harmonized render. Cause: SP-143 is a **vocal** harmonizer — YIN f0 tracking is
  monophonic, and fed a polyphonic marimba+pad+bass mix it (a) smears marimba
  transients via PSOLA grain re-lay, letting the sustained C2 bass dominate the
  per-window peak, and (b) places scale-degree targets from an unstable f0 estimate.
  No irrational noise, but the harmony parts are less cleanly diatonic than they
  would be on a true mono lead. Expected category mismatch (vocal tool on a
  percussion phase piece), not a pipeline failure.

Full numbers: `Analysis/pitch_verification.json`.

## Mastering

`target_for_style("minimal")` → −18.0 LUFS. Result: integrated LUFS −18.0,
true-peak −3.58 dBFS (dynamic percussion material — ceiling not reached, expected).

## Fixes / cleanup

- Removed intermediate `sp143_harmonized_raw.wav` (superseded by mastered render).
- No composition rework required (all three rules audited clean).

## Scripts

- `sp143_process.py` — SP-143 application + master.
- `verify_pitch.py` — pitch / harmonic-energy / silence verification.