# REPORT — 097-jazz-bebop-changes

**Project:** 097-jazz-bebop-changes
**Style:** Jazz (bebop head over rhythm-changes-style turnaround)
**Method:** ABS-002 Subset Walker (**ABSTRACT layer**) + ABS-001 tension-curve
steering + method-006 cadence close (forced V7 → I on the final two bars)
**Date:** 2026-09-17 (nightly autonomous composition job)
**Seed:** 20260917
**Key:** G major (G A B C D E F#) · **BPM:** 132 · 4/4 · 480 TPB
(bar = 1920, 8th = 240, 16th = 120)
**Form:** 6 sections × 4 bars = 24 bars — Intro | Head | Solo | Bridge |
Head2 | Outro (section = 7680 ticks, total 46080)
**Project dir:** `/opt/data/repos/musicom/projects/Styles/Jazz/097-jazz-bebop-changes`
(symlink alias `/opt/data/projects/Styles/Jazz/097-jazz-bebop-changes`)

---

## 1. Report contract — headline results

| Gate | Result |
|---|---|
| `validate()` phase 1 (raw) | **True / OK** |
| `validate()` phase 2 (rules) | **True / OK** |
| Grid audit phase 2 (16th = 120 @ 480 TPB) | **0 off-grid / 713 notes** (8th off-grid 43/713 = legit 16ths in the lead) |
| Grid audit phase 1 (raw fingerprint) | 142 off-grid / 148 notes (by design) |
| Harmony audit (scale + chord tones, all pitched voices) | **0 out-of-scale, 0 out-of-chord** (after 2 fixes, see §7) |
| Range audit (instrument registry) | **PASS** — Lead 59–79 (trumpet 54–86), Trombone 52–72 (40–78), Piano 60–79 (21–108), Bass 31–52 (28–74), Drums ch9 |
| Zero-drift (all tracks end at same tick) | **PASS** — max_end = 46080 ticks both phases |
| Silence / RMS | **PASS** — 8.78% total silence, only tail secs 45–46, peak 0.6263 |
| Tonal windows (FFT 50–1000 Hz) | 90/95 phase 2, 89/91 phase 1 |
| Voice-leading (classical, bass + lead) | 3 flags pre-fix → **0 after fix** |
| Engine-only authoring | **COMPLIANT** (midop used READ-ONLY in audit/range_check) |

Primary record: this file. Machine-readable mirrors: `Analysis/audit.json`,
`Analysis/summary.json`, `Analysis/render_stats.json`, `Analysis/vl_audit.json`.

## 2. Layer cadence (why abstract tonight)

The nightly layer rule is 6-of-7 concrete, 1-of-7 abstract. Recent run history:
085 (abstract) → 086 (concrete) → 087 (abstract) → 088 → 089 (abstract) →
090 (abstract) → 091 → 092 → 093 → 094 → 095 → 096 (concrete).
Concrete runs 091–096 completed the 6-night block; tonight is the **weekly
abstract-cadence run** (last abstract was 090). Methods 097/098 were never
claimed in the project tree (099 exists), so this project takes **097**.

## 3. Method (abstract layer)

The harmony comes entirely from the ABSTRACT layer: a walk over the 12TET
subset network (`rules.subset_network.PatternNetwork` over
`rules.patterns.standard_patterns()` ids) steered by a per-bar tension curve
(ABS-001), then a rules-layer cadence close (method 006, forced V7 → I).

- Walk pool: 12 G-major diatonic anchors (6 triads + 6 sevenths):
  `maj7(G I), min9(Am ii), min11(Bm iii), maj0(C IV), maj2(D V), min4(Em vi),
  min79(Am7 ii7), min711(Bm7 iii7), maj70(Cmaj7 IV7), dom72(D7 V7, T=7.0),
  min74(Em7 vi7), maj77(Gmaj7 I7)`
- 22 bars walked + forced `dom72 → maj7` (D7 → G) cadence bars 22/23
- Tension curve: `[2.0]*6 + [3.0]*6 + [5.0]*6 + [5.5]*3 + [2.0]*1`
  (head sway → solo rise → bridge lean → shout peak → head return) +
  forced [7.0, 2.0] cadence
- Engine quirk (same as 089/090): `walk(home=...)` never fires while
  `tension_curve` length == walk length (tension branch shadows home branch)
  — worked around with a 22-bar curve + rules-layer cadence bars 22/23.

**Walk (24 bars, pattern ids)**:
maj7 maj0 maj7 maj0 min9 min11 maj0 maj7 | min9 maj7 min11 maj0 |
maj70 min74 maj70 maj77 | min74 min79 min74 maj70 | min79 maj0 | dom72 maj7

**Progression (G-major functional reading, 24 bars)**:
I · IV · I · IV · ii · iii · IV · I · ii · I · iii · IV · IV7 · vi7 · IV7 ·
I7 · vi7 · ii7 · vi7 · IV7 · ii7 · IV · V7 · I
(G · C · G · C · Am · Bm · C · G · Am · G · Bm · C · Cmaj7 · Em7 · Cmaj7 ·
Gmaj7 · Em7 · Am7 · Em7 · Cmaj7 · Am7 · C · D7 · G)

Functional shape: the walk opens I–IV sways (bebop head feel), moves through
ii/iii color bars, peaks in the Bridge/Head2 with the seventh chords
(IV7–vi7–I7–ii7 = Cmaj7/Em7/Gmaj7/Am7 colors), and the **cadence-close rule
(method 006)** forced bar 22 to `dom72` (D7) so the piece ends V7 → I —
the bebop turnaround gesture.

## 4. Two-phase architecture

| Phase | Artifact | Content |
|---|---|---|
| 1 | `MIDI/097-jazz-bebop-changes-phase1.mid` | Raw abstract-layer draft: single trumpet voice, pitches sampled from the CURRENT WALKED ANCHOR tetrad pcs (+30% chromatic-approach neighbor = bebop enclosure color), swing-8th rhythm with fractional jitter (off-grid fingerprint), no harmony/bass/drums |
| 2 | `MIDI/097-jazz-bebop-changes.mid` | 16th-grid locked (120 @ 480 TPB), subset realization (tetrad tone / diatonic pass / approach-resolves-to-chord-tone) + chord-tone quantize per global bar (anchor realization), voice-leading check/correction, full 5-voice bebop texture |

Both phases passed their own zero-drift `validate()` gate.
078-lesson applied: ALL phase-2 pitched onsets snapped to the 16th grid
BEFORE chord-tone quantization; phase-1 keeps its raw off-grid fingerprint
(142/148 off-grid by design).

## 5. Voices (instrument_registry)

| Voice | Instrument | GM | Range (registry) | Used | Role |
|---|---|---|---|---|---|
| Lead | Trumpet | 56 | 54–86 | 59–79 | bebop head, chord tones + diatonic passes |
| Trombone | Trombone | 57 | 40–78 | 52–72 | answering counterline (beats 2 & 4, 8th pairs) |
| Piano | Acoustic Grand Piano | 1 | 21–108 | 60–79 | charleston comping (beat 1 + and-of-2, bridge adds stab) |
| Bass | Double Bass | 43 | 28–74 | 31–52 | walking quarters + diatonic beat-4 approach |
| Drums | Drum Kit (ch9) | 0 | GM | 36–51 | spang-a-lang ride, feathered kick 1&3, backbeat 2&4, brush intro/outro |

Texture by section: Intro brushes + half-note head, Head/Solo spang-a-lang
ride + charleston comp, Bridge press (kick every beat + crash), Head2 dance
return, Outro brush resolve.

## 6. Verification (real numbers)

### Grid audit (phase-2 MIDI, mido read-only) — `Analysis/audit.json`
| Voice | Notes | Off 16th | Off 8th |
|---|---|---|---|
| Lead (Trumpet, ch0) | 149 | 0 | 43 (legit 16ths) |
| Trombone (ch1) | 96 | 0 | 0 |
| Piano (ch2) | 156 | 0 | 0 |
| Bass (ch3) | 96 | 0 | 0 |
| Drums (ch9) | 228 | 0 | 0 |
| **Total** | **713** | **0** | — |

### Harmony audit (scale + chord-tone per bar, floor attribution)
| Voice | Out-of-scale | Out-of-chord |
|---|---|---|
| Lead (Trumpet) | 0 | 0 |
| Trombone | 0 | 0 |
| Piano | 0 | 0 |
| Bass | 0 | 0 |

Audit scale = strict G ionian pcs {G A B C D E F#}. Every phase-2 pitched
note is chord-quantized to a walked anchor whose pcs are diatonic in G, so
0/0 holds by construction. (Phase 1 carries the 30% chromatic-approach
color; phase 2 resolves approaches to the nearest chord tone — the
two-phase rules contract.)

### Phase-1 raw fingerprint
148 notes, 142/148 off the 16th grid (fractional jitter preserved in the
raw draft — the phase-1 point). Trumpet GM 56 single voice.

**Zero-drift**: all 5 phase-2 voice tracks length 46080 ticks (24 × 1920) —
identical. **Voice-leading**: 3 flags pre-fix (2 hidden octaves, 1 hidden
fifth, outer voices) → all corrected via chord-tone re-pick → re-check
**0 flags** (`Analysis/vl_audit.json`).

### Audio (SP-001 FluidSynth via `produce()`, discover_soundfont → FluidR3_GM.sf2)
- Full mix: 47.77 s, peak 0.6263, **silence ratio 8.78%** (< 30% ✓)
- RMS 0.073, tonal windows 90/95 (dominant FFT peak 50–1000 Hz present)
- Only silent seconds are 45–46 (legit tail decay after final G chord); **no
  mid-track gaps**
- Phase-1 render: 45.94 s, silence 12.64%, tonal 89/91 (trumpet draft
  audible, quieter by design — peak 0.2954)
- All artifacts: size > 40 B asserted; provenance.json sidecars written

## 7. Bugs found & fixed during completion

1. **Piano out-of-chord (9 notes)**: the comping pickup hit was placed at
   tick 2640 (= 2880−240) — beyond the bar boundary (1920) — so its
   notes were attributed to the NEXT bar's chord and audited out-of-chord.
   Fixed by moving the pickup to tick 1680 (and-of-4, inside the bar).
   Re-audit: 0.
2. **Bass out-of-chord (21 notes)**: the beat-4 scalar approach step
   (±2 semitones, then diatonic snap) could land on a pc outside the
   CURRENT bar's walked chord (e.g. Em bar landing on B♭-side snap). Fixed
   by auditing the snapped candidate against the current bar's chord pcs
   and falling back to the chord tone nearest the next root. Re-audit: 0.
3. **Voice-leading flags (3)**: hidden octave at bars 1, 5 and hidden fifth
   at bar 21 between bass + lead. Fixed with the 090-pattern
   `fix_hidden_fifth` nudge (lead first-note re-picked to a non-0/7-interval
   chord tone). Re-check: 0 flags.
4. **Import path fix**: `PatternNetwork` no longer lives in
   `rules.patterns` — imported from `rules.subset_network` (the sanctioned
   alias) after a first-run AttributeError.

## 8. Files

```
MIDI/097-jazz-bebop-changes-phase1.mid        (raw phase-1 draft, 1.4 KB)
MIDI/097-jazz-bebop-changes.mid               (phase-2 arrangement, 6.1 KB)
Audio/097-jazz-bebop-changes.wav/.ogg         (full mix, SP-001, 342 KB ogg)
Audio/097-jazz-bebop-changes-phase1.wav/.ogg  (phase-1 render, 391 KB ogg)
Analysis/grid_visualization.txt               (density grid)
Analysis/summary.json                         (project summary)
Analysis/vl_audit.json                        (voice-leading audit)
Analysis/audit.json                           (grid+harmony audit: PASS)
Analysis/render_stats.json                    (silence/RMS/tonal)
Scripts/compose.py, Scripts/audit.py, Scripts/render_audio.py,
Scripts/audio_stats.py, Scripts/range_check.py
compose.py / audit.py / render_audio.py / audio_stats.py (repo-root copies)
README.md / REPORT.md
```
