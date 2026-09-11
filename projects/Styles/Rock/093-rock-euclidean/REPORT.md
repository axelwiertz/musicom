# 093-rock-euclidean — Rock × Method 012 (Euclidean Groove Locking)

**Style:** Rock (E aeolian / natural minor) · **Tempo:** 128 BPM
**Method:** 012 Euclidean Groove Locking (Bjorklund) — implementation
`generators.rhythm.euclidian`
**Layer:** `concrete` (6-of-7 concrete cadence; last abstract run was 090)
**Seed:** 20260911 · **Run:** nightly autonomous composition job, 2026-09-11

---

## 1. Report contract — headline results

| Gate | Result |
|---|---|
| `validate()` phase 1 (raw) | **True / OK** |
| `validate()` phase 2 (rules) | **True / OK** |
| Grid audit phase 2 (16th = 120 @ 480 TPB) | **0 off-grid / 972 notes** |
| Grid audit phase 1 (raw fingerprint) | 48 off-grid / 54 notes (by design) |
| Harmony audit (scale + chord tones, all pitched voices) | **0 out-of-scale, 0 out-of-chord** |
| Range audit (instrument registry) | **PASS** (all 5 pitched voices in range) |
| Zero-drift (all tracks end at same tick) | **PASS** — max_end = 46080 ticks on both phases |
| Phase-1 pitch ground truth (known MIDI notes) | **PASS 54/54** fundamentals present, 54/54 harmonic ratio > 0.30 |
| Phase-2 tonal check (polyphonic mix) | **PASS** — 80.7 % of windows on a 12TET note, chroma top-3 in key 97.9 %, 84/93 autocorrelation frames pitched |
| Silence / RMS | **PASS** — 19.34 % total silence, all of it the post-music DAW tail (mid-track silent seconds: none), peak 0.857 |

Primary record: this file. Machine-readable mirrors: `Analysis/audit.json`,
`Analysis/summary.json`, `Analysis/tonal_check.json`,
`Analysis/render_stats.json`, `Analysis/render_info.json`,
`Analysis/concept.json`.

---

## 2. Selection (auditable)

Nightly selection is seeded deterministically from the run date
(`Analysis/../Research/selection/night_2026-09-11.json`).

- **Style pool:** 46 genre folders under `projects/Styles/` (excluding
  `_Comparison`, `_Data_Patterns`, `Research`, `Poetry`, `Production`,
  `Percussion`, `Other`). Seed 20260911 → **Rock**.
- **Method pool:** `workflows.selector.select_for_cron()` = headless + deterministic
  methods that HAVE registry code: `001, 010, 012, 018, 023, 040, HC-012`.
  Excluding the last 7 days of use (`002` 086, `003` 091, `018` 092, `045` 088)
  leaves `001, 010, 012, 023, 040, HC-012`; seed → **012**.
- **Layer cadence:** 6-of-7 concrete. The most recent abstract run was 090
  (2026-09-08); 091 and 092 were concrete, so tonight is **concrete**.

---

## 3. Method mechanics (Method 012, concrete)

Method 012 *Euclidean Groove Locking* distributes *k* onsets as evenly as
possible across *n* steps (Bjorklund). The repo's implementation is
`generators.rhythm.euclidian(onsets, timesteps)`, which returns the **interval
list** between onsets; cumulative sums of that list give the onset positions.

Every rhythm in phase 2 is derived from an `euclidian()` call, with the step
value chosen so that `sum(intervals) * step_ticks == BAR` (1920). This is what
"locking" means here: the Euclidean cell is metric, so the mathematical
evenness of the algorithm and the human grid coincide.

| Voice | Euclidean (k, n) | step ticks | Onset ticks in the bar |
|---|---|---|---|
| Lead (fiddle) | `euclidian(6, 16)` | 120 (16th) | 0, 360, 720, 1080, 1440, 1800 |
| Guitar | `euclidian(4, 16)` | 120 (16th) | 0, 480, 960, 1440 |
| Piano | `euclidian(3, 8)` | 240 (8th) | 0, 720, 1440 (rotated per bar/section) |
| Organ | `euclidian(1, 4)` | 480 | 0 (whole-bar sustain) |
| Bass | `euclidian(8, 8)` | 240 (8th) | 0, 240, …, 1680 |
| Kick | `euclidian(4, 16)` | 120 | 0, 480, 960, 1440 |
| Snare | `euclidian(2, 8)` rot 2 | 240 | 480, 1440 (the backbeat) |
| Hi-hat | `euclidian(8, 16)` | 120 | 0, 240, …, 1680 |

`euclidian(2, 8)` unrotated is `[0, 960]` (downbeats 1 and 3); rotating by two
steps gives `[480, 1440]` — the rock backbeat on 2 and 4. The rotation is the
only "human" edit applied to the algorithm's output, and it is stated in code
(`euclid_onsets(..., rot=2)`).

The lead's 6-in-16 pattern is the syncopation engine of the piece: it puts
onsets on 0, 360, 720, 1080, 1440, 1800 — two of them (360, 1080) fall on the
"e" of the beat and two (1800) on the "a" of beat 4, producing the offbeat
push that separates rock from four-on-the-floor disco. It is rotated per bar
(`rot = (bar + section) % 3`) so the cell does not become a loop.

---

## 4. Two-phase architecture

### Phase 1 — raw generative draft (`MIDI/093-rock-euclidean-phase1.mid`, 548 B)

Single voice (`LeadRaw`, GM 110 fiddle), **no harmony, no chord tones, no other
voices**. The generator output is used raw:

- The `euclidian(k, n)` interval list is walked at a **fractional tick unit**
  solved from the section span (`SECTION_TICKS / total_pattern_steps`),
  then jittered ±6 % per onset. The resulting steps are essentially never
  multiples of 120 or 240.
- Pitch is an unquantized random walk (`r.choice([-5,-3,-2,-1,1,2,3,4,7]) +
  0.9·N(0,1)`) — no scale snap, no chord context.
- Sections use different pairs `(6,16) (3,8) (4,16) (7,16) (2,8)` so the raw
  draft has five different Euclidean densities.

Verified raw fingerprint: **48 / 54 onsets off the 16th grid** — the draft is
deliberately not grid-locked, which is the point of phase 1.

### Phase 2 — musicom rules post-process (`MIDI/093-rock-euclidean.mid`, 7987 B)

1. **Grid lock (078 mandatory rule).** Every phase-2 onset is generated
   directly from a metric Euclidean cell (`120`/`240`/`480` step values), so
   quantization is structural rather than a post-hoc snap. Audit: 0 off-grid.
2. **Harmonic context.** 24-bar diatonic progression in E aeolian, all roots
   routed through the canonical helper
   `Scale7ChordDegree.get_diatonic_note(KEY_ROOT, AEOLIAN, degree)` — **no
   local `% 7` index wrappers** (the skill's diatonic-note rule).
3. **Chord-tone quantization.** Every pitched note is snapped to the nearest
   member of its bar's diatonic triad, via a scale snap then a chord snap.
4. **Voice-leading check/correction.** `rules.voice_leading.VoiceLeadingRules`
   (`style="classical"`) checks the outer voices (bass + lead) bar to bar:
   **6 flags raised (parallel/hidden fifths or octaves), 6 corrected**, none
   remaining.
5. **Texture.** Six voices from the instrument registry (source of truth, not
   the 10-entry `MidiInstrument` enum).
6. **Zero-drift.** Each cell is normalized to the exact section boundary with a
   terminal silent landmark `MusicEvent(0, 0, SECTION_TICKS-1, SECTION_TICKS)`
   when needed; `validate()` returns **True** on both phases.

---

## 5. Composition brief

| Field | Value |
|---|---|
| Title | 093-rock-euclidean |
| Genre / sub | Rock — minor-key driving rock, Euclidean rhythm study |
| Emotional target | Forward drive, minor-mode urgency, mechanical-but-musical groove |
| Key / mode | E aeolian (natural minor): E F♯ G A B C D |
| Tempo / meter | 128 BPM, 4/4, 16th subdivision (120 ticks @ 480 TPB) |
| Form | 6 sections × 4 bars = 24 bars: Intro · Verse · Chorus · Bridge · Chorus2 · Outro |
| Length | 45 s of music + FluidSynth release tail = 57.9 s render |
| Instrumentation | Fiddle lead, acoustic guitar chank, piano stabs, organ pad, double bass, GM drum kit |

### Progression (diatonic degrees, 0-based; 24 bars)

```
Intro   i    i    VI  VII
Verse   i    VI   III VII
Chorus  VI   VII  i    i
Bridge  iv   VI   III VII
Chorus2 VI   VII  i    i
Outro   i    i    VI  i
```

Rendered roots: `Ei Ei CVI DVII | Ei CVI GIII DVII | CVI DVII Ei Ei |
Aiv CVI GIII DVII | CVI DVII Ei Ei | Ei Ei CVI Ei`

Functional reading: the verse is a tonic→♭VI→♭III→♭VII loop, the chorus flips
the gravity by starting on ♭VI and resolving to i, the bridge substitutes iv
(the only subdominant arrival) for colour, and the outro lands on a plagal
♭VI→i close instead of a dominant — a modal-rock ending.

### Voices (instrument registry)

| Row | Voice | Instrument | GM prog | Channel | Range | Sweet spot |
|---|---|---|---|---|---|---|
| 0 | Lead | Fiddle | 110 | 0 | 55–96 | 62–86 |
| 1 | Guitar | Acoustic Guitar (nylon) | 25 | 1 | 40–84 | — |
| 2 | Piano | Acoustic Grand Piano | 1 | 2 | 21–108 | — |
| 3 | Organ | Church Organ | 19 | 3 | 36–96 | 55–79 |
| 4 | Bass | Double Bass | 43 | 4 | 28–74 | 40–55 |
| 5 | Drums | Drum Kit | 0 | 9 | GM kit map | — |

Note on instrument choice: the registry has no electric/distortion guitar
(program 30 would be raw-program-only), so the "rock chank" is played on the
researched **acoustic** guitar (GM 25) — honest with the KB rather than
inventing an unregistered instrument.

### Lead melodic DNA

Grid from `euclidian(6, 16)` rotated per bar; contour from a fixed
scale-degree step motif applied over the E-aeolian pool (60–96), then
chord-quantized to the bar's triad and leap-capped at 10 semitones toward the
nearest chord tone. The motif is mostly stepwise with occasional 3rd/4th
leaps — an idiomatic rock-tune contour rather than a random walk. The
phase-1 draft supplies only the *pitch register centre* per section (its mean
pitch seeds the pool index), preserving the two-phase separation: phase 1
owns the raw material's character, phase 2 owns idiom.

---

## 6. Grid audit, per voice (phase 2)

```
16th off-grid: 0/972        (8th off-grid 56/972 = legitimate 16th-note placements)

Lead(fiddle)  prog=110 ch=0  notes=120  off16=0  off8=56  end=46080
Guitar        prog= 25 ch=1  notes=192  off16=0  off8= 0  end=46080
Piano         prog=  1 ch=2  notes= 72  off16=0  off8= 0  end=46080
Organ         prog= 19 ch=3  notes= 72  off16=0  off8= 0  end=46080
Bass          prog= 43 ch=4  notes=192  off16=0  off8= 0  end=46080
Drums         prog=  0 ch=9  notes=324  off16=0  off8= 0  end=46080
```

The 56 off-8th onsets are all on the lead, and they are exactly the `e`/`a`
16th placements produced by the rotated `euclidian(6,16)` cell — i.e. the
method working as designed, not drift.

## 7. Harmony audit, per voice (phase 2)

```
Lead(fiddle)  out_of_scale=0  out_of_chord=0
Guitar        out_of_scale=0  out_of_chord=0
Piano         out_of_scale=0  out_of_chord=0
Organ         out_of_scale=0  out_of_chord=0
Bass          out_of_scale=0  out_of_chord=0
```

Every pitched note belongs to E aeolian **and** to its bar's diatonic triad.
Fix applied during development: the guitar dyad builder originally searched
the whole 40–84 range for a fifth, which admitted the ♭7 from the *scale* on
the ♭VI chord (24 out-of-chord notes). It now searches only the bar's chord
tones, falling back to the nearest higher chord tone — 24 → 0.

## 8. Range audit (instrument registry)

```
Lead(fiddle)  Fiddle                   min=72 max=95  range=[55,96]  in_range=True
Guitar        Acoustic Guitar (nylon)  min=50 max=60  range=[40,84]  in_range=True
Piano         Acoustic Grand Piano     min=55 max=78  range=[21,108] in_range=True
Organ         Church Organ             min=55 max=66  range=[36,96]  in_range=True
Bass          Double Bass              min=36 max=57  range=[28,74]  in_range=True
```

## 9. Zero-drift

```
phase-2: max_end=46080 ticks   drift_ok=True
phase-1: max_end=46080 ticks   drift_ok=True
```

46080 ticks = 24 bars × 1920. Every track in both artifacts ends on exactly the
same tick — the `UnitMatrixComposer.to_midi()` off-before-on / pad-tail
guarantee, no hand-written MIDI anywhere.

## 10. Audio render + statistics

Rendered with **SP-001** (FluidSynth + `FluidR3_GM.sf2` → WAV → ffmpeg Opus).

| Artifact | Bytes | Notes |
|---|---|---|
| `MIDI/093-rock-euclidean-phase1.mid` | 548 | raw draft, 1 voice |
| `MIDI/093-rock-euclidean.mid` | 7 987 | rules layer, 6 voices |
| `Audio/093-rock-euclidean.wav` | 10 206 542 | 44.1 kHz stereo, peak 0.857 *(deleted before commit — regenerable, `.gitignore`d)* |
| `Audio/093-rock-euclidean.ogg` | 404 221 | Opus 48 kbps voip |
| `Audio/093-rock-euclidean-phase1.wav` | 8 291 150 | peak 0.862 *(deleted before commit — regenerable)* |
| `Audio/093-rock-euclidean-phase1.ogg` | 387 975 | Opus 48 kbps voip |

WAV cleanup: both raw/intermediate WAVs were removed before commit per the
skill's WAV-cleanup rule; the tracked deliverables are the two OGGs, the two
MIDIs and their provenance sidecars. `Scripts/run_all.sh` regenerates the WAVs
byte-for-byte.

**Silence / RMS (phase 2):** duration 57.86 s, silence ratio **0.1934**,
per-second RMS ≈ 0.09–0.11 for the whole 45 s of music, then a smooth decay to
the noise floor; **mid-track silent seconds: none**. The 19.3 % "silence" is
entirely the post-music release/reverb tail (12.9 s), which is normal for a
SoundFont render — the trap the skill warns about (mid-track gaps) is absent.

**Gain fix applied:** FluidSynth's `-g 1.2` output clipped at the DAC rail
(peak 1.0000, 101 clipped frames). The render pipeline was changed to `-g 1.0`
then normalized to −1 dBFS (0.89) with `ffmpeg -af volume=`.
`peaknorm` is **not** present in this ffmpeg build (8.1.1 exposes only
`volume`, `loudnorm`, `dynaudnorm`), so the skill's fallback path was used and
verified: peak after normalization **0.857** (measured), 0 clipped frames.

## 11. Pitch verification (mandatory — size/silence asserts do not catch noise)

**(A) Phase-1 ground truth.** All 54 exported lead notes were checked against
their exact MIDI frequency: **54/54 fundamentals present** (energy within ±3 %
of f0 is ≥ 2 % of the strongest bin; in fact 53/54 are the strongest bin
itself), and **54/54 have harmonic energy in the first 8 harmonics above 30 %**
of the 40–4000 Hz total (typical 0.55–0.65). Verdict **PASS**.

**(B) Phase-2 polyphonic mix.** 93 spectral windows: dominant-peak median
330 Hz, **80.7 % of windows land on a 12TET note**; chroma top-3 pitch classes
inside E aeolian in **97.9 %** of windows; **84 of 93 autocorrelation frames
carry a pitch** (median f0 82.4 Hz = the bass E2 region) — 0 pitched frames
would have meant noise. Verdict **PASS tonal**.

Methodological note (documented for the next run): a naive "sum of max
single-bin energies / total" harmonic test reports 0.055 on a dense polyphonic
SoundFont mix even when the audio is unambiguously tonal, because the spectrum
is *spread* across many bins per harmonic. The test must **sum band energy**
around each harmonic rather than take a single-bin max — with the sum form the
same mix reads 0.162 and the monophonic ground-truth test reads 0.55–0.65.
The first version of `Scripts/tonal_check.py` had this flaw and was fixed.

## 12. Method rationale (why 012 + Rock)

Method 012 is a **concrete, grid-locked, local-memory** rhythm method with no
tonal gravity of its own. That is precisely what rock needs: the genre's
identity is carried by a *locked, repeating, physically-playable* rhythm
cell and a *simple* diatonic loop, not by harmonic sophistication. Euclidean
distribution gives the cell mathematical evenness and a family of
character-shifting variants (6/16 is syncopated, 4/16 is square, 2/8 rotated
is the backbeat) that all remain in the same metric family — so the drum kit,
the bass and the lead are all "the same pattern at different resolutions",
which is the aesthetic of machine-tight rock.

The two-phase split matters here: phase 1 uses the *same algorithm* at a
fractional tick unit, so the raw draft is Euclidean in *interval* but not in
*metre* (micro-timing wander, no key). Phase 2 keeps the algorithm and swaps
in metric alignment + tonic gravity. The listener hears the same generating
idea in two states: pre-metric and locked.

**Next useful variable** (for a future iteration): alter the *step value*
rather than the (k, n) pair — running `euclidian(6,16)` at a 240-tick step
produces a two-bar hemiola cycle that fights the 4/4 bar line, which is the
classic prog/post-rock device. A second candidate: keep the cell but change
the harmonic rhythm so the progression moves every *two* bars, letting the
Euclidean cell and the chord cycle go out of phase.

---

## 13. Fixes applied during this run

1. **Guitar out-of-chord dyads (24 → 0):** fifth search restricted to the
   bar's chord tones instead of the whole scale window.
2. **Lead instrument label:** the audit's GM-program label table was keyed on
   the wrong fiddle program (40 vs 110); corrected, which also re-enabled the
   range audit for the lead.
3. **Phase-1 draft too thin (29 → 54 notes):** the raw walk originally used a
   fixed 417-tick unit, which ran out of section before emitting the requested
   event count on short sections; the unit is now solved from the section span.
4. **Harmonic-energy test form:** single-bin max → summed band energy (see §11).
5. **Clipped render:** `-g 1.2` → `-g 1.0` + −1 dBFS volume normalization
   (peak 1.0000 → 0.857, clipped frames 101 → 0).
6. **Grid visualization slot width:** `BAR // 2` (960) → `BAR // 8` (240), so
   the 8 slot columns per bar really are 8th notes as the legend claims.

## 14. Compliance

- Engine only: `structures` + `workflows.unitmatrix_composer` +
  `generators.rhythm` + `rules.progression` + `rules.voice_leading`.
  No raw `mido` authoring anywhere (mido is imported read-only in the audit,
  summary and tonal-check scripts, marked `# READING ONLY (analysis)`).
- `projects/Research/preflight_check.py` → **✅ COMPLIANT (exit 0)**.
- Provenance sidecars written for phase-1 MIDI, phase-2 MIDI, and both OGGs.

## 15. File inventory

```
093-rock-euclidean/
├── MIDI/   093-rock-euclidean-phase1.mid (+ .provenance.json)
│           093-rock-euclidean.mid        (+ .provenance.json)
├── Audio/  093-rock-euclidean.wav / .ogg (+ .provenance.json)
│           093-rock-euclidean-phase1.wav / .ogg (+ .provenance.json)
├── Analysis/ audit.json · concept.json · summary.json · tonal_check.json
│            render_info.json · render_stats.json
│            grid_visualization.txt · matrix_grid.txt
├── Scripts/ compose.py · audit.py · render_audio.py · audio_stats.py
│            tonal_check.py · summarize.py · audio_provenance.py · run_all.sh
├── README.md
└── REPORT.md
```

Rerun the whole pipeline with
`bash projects/Styles/Rock/093-rock-euclidean/Scripts/run_all.sh`.
