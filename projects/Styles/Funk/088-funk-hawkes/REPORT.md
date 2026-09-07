# REPORT — 088-funk-hawkes

**Project:** 088-funk-hawkes
**Style:** Funk
**Method:** 045 Hawkes Process Self-Exciting Composition (HPSEC)
**Layer:** concrete
**Date:** 2026-09-06 (nightly autonomous composition job)
**Seed:** 20260906
**Key:** F minor (F G Ab Bb C Db Eb), minor-pentatonic blues colour on the lead
**BPM:** 100 · 4/4 · 480 TPB (bar = 1920, 8th = 240, 16th = 120)
**Form:** 6 sections × 4 bars = 24 bars — Intro | Verse | Chorus | Break | Chorus2 | Outro (section = 7680 ticks)

---

## 1. Concept

Funk built on a Hawkes self-exciting point process (HPSEC, method 045). Each
musical event raises the conditional intensity λ(t); the sampled exponential
sojourn time τ ~ Exp(λ) is the inter-onset interval. Contagion produces
organic rhythmic clustering — bursts of funk hits separated by relaxations —
exactly the "push-pull" of a syncopated groove. An excitation kernel drives
brief upward pitch bursts (aftershock cascades) that the musicom rules layer
then locks to the 16th grid and harmonizes.

## 2. Progression (24 bars, roots + function)

```
i   VI  III VII | i   VI  i   v   | i   VI  III VII |
i   VI  i   v   | i   VI  III VII | VI  III i   i
```

(Fm Db Ab Eb | Fm Db Fm Cm | Fm Db Ab Eb | Fm Db Fm Cm | Fm Db Ab Eb | Db Ab Fm Fm)

Chord tone sets (diatonic triads, root-keyed):
- i (Fm): {53,56,60,65,68,72,77,80,84} · VI (Db): {49,53,56,61,65,68,73,77,80}
- III (Ab): {44,48,51,56,60,63,68,72,75} · VII (Eb): {51,55,58,63,67,70,75,79,82}
- v (Cm): {48,51,55,60,63,67,72,75,79}

Funk-octave bass alternates root (low) with octave pops (chorus) on the "and"
of every beat; 16th pickup pushes into the next bar in Chorus/Break sections.

## 3. Voices + instruments (all from the importable registry at
`/opt/data/repos/musicom/projects/Instruments/` — the source of truth)

| # | Voice | Instrument (registry) | GM | Channel | Register used | Role |
|---|-------|----------------------|----|---------|---------------|------|
| 0 | Lead | Trumpet (Brass/trumpet) | 56 | 0 | 54–86 (range) | Hawkes lead, 16th-grid, chord tones |
| 1 | Sax | Alto Sax (Woodwind/saxophone) | 65 | 1 | 60–88 | answering 8th counterline on beats 2 & 4 |
| 2 | Cello | Cello (Strings/cello) | 42 | 2 | 44–63 | sustained whole-bar triad pad |
| 3 | Piano | Piano (Keys/piano) | 1 | 3 | 60–88 | offbeat 16th stabs ("and" of every 8th) |
| 4 | Bass | Double Bass (Strings/double_bass) | 43 | 4 | 32–53 | funk octave pulse + 16th pushes |
| 5 | Drums | Drum Kit (Percussion/drum_kit, ch9) | 0 | 9 | GM drums | kick 1&3 (+1& 3& in choruses), snare 2&4, 16th hats, claps, crash |

## 4. Two-phase architecture

**Phase 1** (`MIDI/088-funk-hawkes-phase1.mid`) — raw generative draft:
- Single voice (Trumpet 56), NO harmony, NO bass, NO drums.
- Hawkes self-exciting process: base intensity μ=0.12, excitation α=0.55
  (each event raises λ by 0.55·current excitation, capped at 3.0), kernel
  decay β=0.006, random re-excitation p=0.28 → after-shock clusters.
- Rhythm: Ogata/Gillespie-thinned exponential sojourn times → fractional,
  OFF-GRID tick spacings (the raw fingerprint). 187 raw notes, 179 off-16th.
- Pitches: contagion-driven drift around section centers (62/66/74/64/74/60)
  with reflecting barriers [53,91] and tonic-centering — unquantized.

**Phase 2** (`MIDI/088-funk-hawkes.mid`) — musicom rules post-process:
1. **Grid-lock FIRST** to the 16th grid (120 ticks) — mandatory rhythm-grid
   sync (078 rule).
2. Lead: snap to nearest F-minor-pentatonic degree (blues colour), then
   chord-tone quantize into trumpet range 54–86 using the GLOBAL bar lookup
   (`bar = s*BARS_PER + local_bar`) — 079 bugfix pattern.
3. Leap cap ≤ 9 semitones toward nearest chord tone of the destination bar.
4. Sax / cello / piano / bass / drums follow the bar chords on-grid.
5. `rules.voice_leading.VoiceLeadingRules(style="classical")` check on
   bass+lead outer voices per bar pair — 3 flags at bars 10/13/13 (hidden
   octave, parallel fifths, hidden fifth); all fixed by nudging the lead's
   first note of the following bar off the offending relation. Re-check: 0.
6. Zero-drift `validate()` gate on both phases: **OK / OK**.
7. `visualization.grid.write_grid_visualization` + provenance sidecars +
   `summary.json` + `audit.json` + `vl_audit.json`.

## 5. Grid audit (rhythm-grid sync — MANDATORY) — from `Analysis/audit.json`

Exported phase-2 MIDI, every track's onsets vs grid (READ-ONLY mido):

| Track | Voice | ch | n | 16th off (120) | 8th off (240) | out-of-scale | out-of-chord |
|-------|-------|----|---|---------------|---------------|--------------|--------------|
| 1 | Trumpet lead | 0 | 149 | **0** | 68* | 0 | 0 |
| 2 | Sax | 1 | 96 | **0** | **0** | 0 | 0 |
| 3 | Cello | 2 | 72 | **0** | **0** | 0 | 0 |
| 4 | Piano | 3 | 192 | **0** | 192* | 0 | 0 |
| 5 | Double Bass | 4 | 134 | **0** | 9* | 0 | 0 |
| 6 | Drums (ch9) | 9 | 352 | **0** | 64* | — (perc) | — (perc) |
| **TOTAL** | | | 995 | **0** | 333 | **0** | **0** |

\* 8th-off entries are intentional 16th placements (16th pushes, offbeat
stabs, 16th hats, ghost kicks) — all 16th-grid multiples (120). The contract
grid is the 16th; **0 off-grid (16th) on every voice**.

Phase 1 raw (by design unquantized): 187 notes, **179 off-16th / 181 off-8th**
— the raw Hawkes fingerprint preserved.

## 6. Harmony audit (scale + chord-tone — MANDATORY)

Audit scale = F aeolian superset (chords are diatonic F-aeolian triads; the
pentatonic snap + chord quantize lands every note on a chord tone, hence in
both sets). Every pitched voice's notes checked against the scale AND the
chord pcs of the GLOBAL bar where the onset starts:

| Track | Voice | out-of-scale | out-of-chord |
|-------|-------|--------------|--------------|
| 1 | Trumpet lead | **0** | **0** |
| 2 | Sax | **0** | **0** |
| 3 | Cello | **0** | **0** |
| 4 | Piano | **0** | **0** |
| 5 | Double Bass | **0** | **0** |
| 6 | Drums | n/a | n/a |

**Verdict: 0 out-of-scale, 0 out-of-chord across all 643 pitched notes.**

## 7. Zero-drift status

- Phase 1 `validate()`: **OK** — terminal landmark `MusicEvent(0,0,7679,7680)`
  per cell.
- Phase 2 `validate()`: **OK** — all 6 rows equal length (6 × 7680 = 46080
  ticks), terminal landmark per cell.
- Exports via `UnitMatrixComposer.to_midi()` (engine absolute-alignment).

## 8. Audio render + silence/RMS/tonal profile (SP-001 FluidSynth)

Rendered with `workflows.musicom_workflow.produce(midi, "SP-001")`
(FluidR3_GM via `discover_soundfont()` — never hardcoded), then
peak-normalized to −1 dB (`peaknorm`), OGG via ffmpeg opus voip 48k.

| File | Size | Duration | Silence ratio | Peak | RMS | Tonal windows |
|------|------|----------|---------------|------|-----|---------------|
| Audio/088-funk-hawkes.wav | 10,626,894 B | 60.24 s | **4.4%** | 0.89 | 0.084 | 118/120 |
| Audio/088-funk-hawkes.ogg | ~424 KB | — | — | — | — | — |
| Audio/088-funk-hawkes-phase1.wav | 10,566,990 B | 59.9 s | 19.0%* | 0.37 | 0.037 | 112/119 |
| Audio/088-funk-hawkes-phase1.ogg | ~517 KB | — | — | — | — | — |

Silent seconds (mix): only second 59 (final tail) of 60 — no mid-track dead
zones. \* Phase-1 raw is a sparse solo trumpet draft (no accompaniment) —
19% silence expected and consistent with prior phase-1 renders. FFT dominant
peaks 50–1000 Hz present in 118/120 mix windows — tonal content confirmed,
**no silent-WAV trap, no noise render**.

## 9. Voice-leading audit (`Analysis/vl_audit.json`)

- Pre-fix flags: 3 (bar 10 hidden octave; bar 13 parallel fifths + hidden
  fifth — root-position funk texture where bass root + lead fifth is idiomatic,
  but flagged by the strict classical style).
- Fix: nudge lead's first note of the destination bar to a chord tone that is
  not a 5th/8ve above the bass. Post-fix re-check: **0 flags**.
- The single-voice melodic lines themselves are leap-capped (≤ 9 semitones).

## 10. File paths

```
MIDI/088-funk-hawkes.mid            (provenance.json sidecar)
MIDI/088-funk-hawkes-phase1.mid     (provenance.json sidecar)
Audio/088-funk-hawkes.wav/.ogg      (+ provenance sidecars)
Audio/088-funk-hawkes-phase1.wav/.ogg (+ provenance sidecars)
Analysis/grid_visualization.txt
Analysis/audit.json
Analysis/vl_audit.json
Analysis/render_stats.json
Analysis/summary.json
README.md
compose.py / audit.py / render_audio.py / audio_stats.py / audio_provenance.py / normalize.py
REPORT.md
```

All MIDI/JSON/text artifacts > 40 bytes (size asserts passed). Zero-drift
validate PASS on both phases. AUDIT PASS: 0 off-grid (16th), 0 out-of-scale,
0 out-of-chord. Voice-leading: 3 flags found, 0 remaining after fixes.

## 11. Fixes / notes applied this run

1. **Grid-lock before chord-quantize** (078/079 rule) — snapping first keeps
   the bar lookup (`bar = s*4 + start//BAR`) consistent with the chord pool.
2. **Lead register clamp**: chord-tone pool built in trumpet range 54–86
   (`chord_tones(root, lo=54, hi=86)`) instead of a generic 48–88 window —
   keeps the lead inside the registry instrument range; the pool already
   spans octaves so nearest-in-pool is register-correct (no separate octave
   variant pass needed).
3. **Scale snap = minor pentatonic**: lead colour is F minor pentatonic
   (blues/funk); final quantize lands on the aeolian diatonic chord tones of
   the bar, verified 0 out-of-scale against the aeolian superset.
4. **Voice index fix**: cello pad targets voice index 2 (row 2) and sax
   counterline voice index 1 — matched to the VOICES list order.
5. **Normalization**: SP-001 adapter does not normalize; rendered WAV peaked
   at 1.0 → `peaknorm=level=-1` applied to both WAVs, OGGs re-encoded.

## 12. Method rationale (why Method 045 + Funk)

Hawkes self-excitation IS groove punctuation: every hit raises the
probability of the next hit, so events cluster into syncopated bursts
(contagion) then relax — the organic push-pull a funk rhythm section plays.
Phase 1 keeps the raw point process audible (fractional sojourn times,
contagion pitch bursts); Phase 2 is the musicom rules layer: 16th grid lock,
pentatonic snap + chord-tone quantize, leap capping, voice-leading fixes, and
the full funk texture (octave bass pulse, offbeat piano stabs, backbeat
drums) — turning the self-exciting process into a danceable F-minor funk
piece.
