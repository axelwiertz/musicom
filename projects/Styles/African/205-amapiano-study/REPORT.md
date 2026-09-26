# 205-amapiano-study — Amapiano Research + Composition Report

Date: 2026-09-26
Style: **Amapiano** — South African house substyle (substyle of African).

## 1. What Amapiano Is

"Amapiano" = isiZulu for **"the pianos"** — the genre is keyboard-led.

- **Origin**: South African townships (Pretoria / Gauteng), mid-2010s.
  Emerged from kwaito + deep house + jazz + soul + lounge. Went global
  ~2019-2020 (Kabza De Small, DJ Maphorisa).
- **Tempo**: slow end of house, **108-115 BPM** (112 used here). Slow tempo
  leaves room for syncopated log-drum movement.
- **Feel**: relaxed surface, rhythmically active underneath. Groove lives in
  the interplay of percussion, silence, harmony and bass — not raw energy.

## 2. Signature DNA (5 elements)

| Element | Amapiano rule | This composition |
|---|---|---|
| **Log drum** | Tuned FM bass-percussion (kick+808+plucked bass hybrid). Carries rhythm AND melodic bassline. Syncopated, velocity-varied. | GM 38 (Synth Bass 1), root/5th/octave chord tones, 16th-grid syncopation, climax 16th runs |
| **Chords** | Soulful electric piano (Rhodes), extended voicings (maj7/min7/dom7/9). | GM 4 (EP1), close-position 7th chords |
| **Shaker** | Rolling 16ths with swing + velocity movement (ghost notes). | Maracas (ch9 note 70), 16th velocity bounce pattern |
| **Kick/clap** | Soft controlled house kick 4-on-floor; clap on 2 & 4. | ch9 kick 36 (vel 88), clap 39 |
| **Sub + log separation** | Clear register split: sub below log drum. | Sub = octave 1 (26-33), log drum = octave 2-3 (38-57) |

## 3. Harmony

Soulful minor progression, 1 bar each, 4-bar cycle (i-VI-iv-V):

```
Am7 (A C E G) | Fmaj7 (F A C E) | Dm7 (D F A C) | E7 (E G# B D)
```

Scale = union of chord tones = **A harmonic minor** (natural minor + G#
leading tone on the V). Every pitched note is a chord tone (0 violations).

## 4. Form & arrangement (delayed reveals)

| Section | Bars | Active | Technique |
|---|---|---|---|
| Intro | 4 | shaker + kick + Rhodes offbeat stab + **guitar hook** | delayed reveal — NO log drum yet |
| GrooveA | 8 | + log drum + sub | groove drops |
| GrooveB | 8 | + kalimba lead | call-and-response |
| Breakdown | 4 | Rhodes + shaker only | space (drop kick/log/sub) |
| Climax | 8 | all + dense log 16th runs + conga + **guitar solo** | peak energy (kalimba drops, guitar takes lead) |
| Outro | 4 | progressive dropout (bar2 drop log/sub, bar3 shaker-only) | organic decay |

### Guitar solos (GM 27, clean electric)

Two solos, chord-tone + 9th color, all inside A harmonic minor:

- **Intro hook** (4 bars): rise → 9th → fall (bar 1), answering descent
  (bar 2), offbeat flourish (bar 3), leading-tone (G#) pickup that resolves
  into GrooveA's Am7 (bar 4).
- **Climax solo** (8 bars): statement arch (bars 1-2) → syncopated response
  (bars 3-4) → 16th-note arpeggio build (bar 5) → peak on the 9th (bar 6) →
  descending release (bar 7) → resolve to root (bar 8).

## 5. Two-phase architecture

- **Phase 1** (`-phase1.mid`): raw generative draft — single LogDrum voice,
  off-grid micro-jitter (±18 ticks), chromatic random-walk pitch (clamped
  36-60). Unquantized. Proves the generative source.
- **Phase 2** (`.mid`): musicom rules — 16th-grid snap, per-bar chord-tone
  quantization, dedup, full 5-voice arrangement, zero-drift gate.

## 6. Verification (real numbers)

**MIDI** (6 voice tracks, 69120 ticks = 36 bars, all equal):

| Check | Result |
|---|---|
| Zero-drift | **PASS** — 6 × 69120 ticks |
| Off-grid onsets | **0** / 517 pitched |
| Scale violations (A harmonic minor) | **0** |
| Chord-tone violations | **0** |

**Audio** (FluidSynth, FluidR3_GM.sf2, 44.1 kHz stereo):

| Check | Result |
|---|---|
| Duration | 79.23 s |
| Peak / RMS | 0.85 / 0.118 |
| Silence ratio | 3.1% (< 30% flag) |
| Log-drum fundamentals present | A2=110 ✓, F2=87 ✓, D2=73 ✓, E2=82 ✓ |

## 7. Files

- `MIDI/205-amapiano-study.mid` / `-phase1.mid`
- `Audio/205-amapiano-study.ogg` / `.wav`
- `Analysis/grid_visualization.txt`, `verify.json`, `render_stats.json`
- `compose.py`, `verify.py`, `verify_audio.py`
- `provenance.json`, `README.md`, `index.html`

## 8. Sources

- Splice — "What is Amapiano Music?" (log drum, BPM, piano)
- BeatStoraPon — "How to Make an Amapiano Beat" (108-115 BPM, element table)
- EDMProd — "What is Amapiano?" (log drum bassline)
- InspiredByBeatz — "How the Log Drum Sound is Created" (FM/hybrid, swing, ghost notes)
- HexLoops — "How to Program an Amapiano Log Drum Pattern" (tune to harmony)

## 9. Production pass (amapiano polish + sound effects)

`produce.py` — render stems → per-voice FX → SFX → section polish → mastering.

**Per-voice amapiano FX** (on per-track stems):

| Voice | Effect |
|---|---|
| Rhodes | lush Schroeder reverb (room 0.82, wet 0.30) — the spacey amapiano piano |
| LogDrum | sub-harmonic generator (depth 0.6) — adds deep "log" weight |
| Sub | clean, kept centered |
| Lead (kalimba) | light reverb (air) |
| Guitar | tape delay (0.32 s echo) + light reverb |
| Drums | light reverb (clap snap + air) |

**Sound effects (synthesized):**
- **Riser** (noise + sine sweep 150→4000 Hz, 2 s) into the Climax.
- **Sub drop** (sine sweep 130→45 Hz, 1.2 s) into GrooveA.

**Section polish:** intro LPF 1600 Hz + fade-in, breakdown LPF 2200 Hz,
outro LPF 1200 Hz + fade-out (60 ms crossfades).

**Mastering:** stereo imager (mono sub <100 Hz, widen highs >3 kHz) →
LUFS normalize −14 → limiter −1 dB.

**Production verification (real numbers):**

| Check | Result |
|---|---|
| LUFS (integrated) | −14.0 |
| Peak / RMS | 0.89 / 0.16 (no clipping) |
| Silence | 2.8% |
| Log-drum fundamentals | A2·F2·D2·E2 present (mag 2.0k-4.2k) |
| Sub content 20-60 Hz | 1161 (sub-harmonic present) |
| Riser energy ramp | 1.95 → 31.2 into Climax ✓ |
| Intro 6-12 kHz filtered | 0.03 vs 0.22 groove ✓ |
| Groove flatness (noise check) | 0.22 (clean — tonal, not noise) |

**Bug fixed (2026-09-26):** `sound.effects.tape_delay.TapeDelay`
self-oscillates at feedback 0.35 — its `out = delayed*(1-fb) + sat*fb`
formula plus a small-signal saturator gain > 1.0 gives a feedback loop gain
~1.3, so the guitar's intro notes kicked a sustained full-scale oscillation
(peak 1.34 / RMS 0.96 in silent regions) that smeared broadband noise across
every groove section (flatness 0.65 → 0.22 after fix). Replaced with a clean
single-tap manual echo overlay in `produce.py`.
