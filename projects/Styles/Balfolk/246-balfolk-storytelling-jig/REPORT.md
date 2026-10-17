# 246 — Balfolk Storytelling Jig

2-minute balfolk dance piece in **6/8 jig**, **D major**, dotted-quarter = 118 BPM.
Built through the musicom engine (UnitMatrixComposer → validate → to_midi).

## Requirement → solution

> "a rhythm of a few bars storytelling, followed by a bar silence" (clarified:
> only the melody rests — the accompaniment plays on underneath).

Each **sentence** = 4 bars of storytelling melody + **1 bar of melody rest**
(the tune takes a breath; guitar/bass/drums keep the groove, holding a
dominant V turnaround). 24 sentences across three passes.

## Form (3 passes × AABB)

| Pass | Register | Narrative role |
|---|---|---|
| 1 | D4 | statement ("once upon a time") |
| 2 | D4 | development |
| 3 | D5 | climax + resolution (octave lift) |

Each pass = A A B B. A part = D-major home (question on V, answer on I).
B part = G-centred lift (IV). 120 bars × 1.017 s = ~2:04.

## Methods (balfolk-suited, from methods_db.md)

| ID | Method | How applied here |
|---|---|---|
| **004** | Prosodic Narrative Coupling | question phrase rises (unresolved), answer falls (resolved); 6/8 downbeats carry velocity accents (syllable stress) |
| **005** | Prosodic Syntax Mapping | sentence boundary → cadence + the 1-bar melody rest (rest placement) |
| **006** | Cadence & Closure Mapping | question → V (half cadence), answer → I (authentic) |
| **007** | Narrative Arc Register Planning | three passes rise D4 → D5 (story builds) |
| **008** | Call-Response Voice Allocation | question = leaner texture, answer fuller |

## Ensemble

| Voice | Instrument | GM | Role |
|---|---|---|---|
| Lead | Violin | 40 | storytelling melody (jig lilt); rests the 5th bar |
| Chords | Acoustic Guitar | 25 | off-beat 6/8 strum — plays through the rest |
| Bass | Double Bass | 43 | dotted-quarter pulse — plays through the rest |
| Drums | Drum Kit | ch9 | tapan: kick on 1, rim on 4 — plays through the rest |

## Rhythm

6/8 jig "jig-gi-ty" lilt: each dotted-quarter group = dotted-8th + 16th + 8th.
Onsets all on the 16th grid (120 ticks) **before humanization**. ticks_per_beat
= 720 (dotted quarter), beats_per_bar = 2 → BAR = 1440 = one 6/8 measure.

## Dual-version render (2026-10-17)

Two artifacts side by side for A/B listening:

| Version | MIDI | Audio | Description |
|---|---|---|---|
| **perfect** | `...-perfect.mid` | `...-perfect.ogg` | grid-locked concrete layer, no humanization |
| **humanized** | `...-humanized.mid` | `...-humanized.ogg` | style=balfolk folk profile + instrument DNA, seeded 246 |

### Humanization profile (humanized only)

| Voice | timing σ | layback | mean shift | max shift |
|---|---|---|---|---|
| Lead (violin) | 10 ms | +2 ms | 9.3 ticks | **46 ticks** |
| Chords (guitar) | 6 ms | +1 ms | 7.0 ticks | 28 ticks |
| Bass (double bass) | 10 ms | +8 ms | 12.9 ticks (lays back) | **48 ticks** |
| Drums (kit) | 2 ms | 0 ms | 1.9 ticks (anchors) | 9 ticks |

Seeded (246), zero-drift safe (forward-clamp + boundary-clamp + pinned landmark).
Note: max shift up to 48 ticks ≈ a full 16th-note (120t) / third of an 8th —
audibly loosens the jig lilt.

## Verification (measured)

| Check | perfect | humanized |
|---|---|---|
| Zero-drift (track lengths) | ✅ 4 × 172800 | ✅ 4 × 172800 |
| Harmony (out-of-scale, D major) | ✅ 0 / 1536 | ✅ 0 / 1536 |
| Melody rest | ✅ 0 lead onsets in 24 rest bars | ✅ 0 |
| Accompaniment through rest | ✅ 72/72 rest bars | ✅ 72/72 |
| Off-grid onsets | ✅ 0 (grid-locked) | 1389 (jitter ran) |
| Duration | ✅ 124 s (~2:04) | ✅ 124 s (~2:04) |
| Master loudness | −16.0 LUFS, −3.87 dBTP | −16.0 LUFS, −2.93 dBTP |

## Sustain fix (2026-10-17)

"Too much staccato" → lengthened the accompaniment sustain (lead jig lilt kept):

| Voice | before | after |
|---|---|---|
| Chords (guitar strum) | 240t / 170 ms | 480t / **339 ms** (rings) |
| Bass (double bass) | 360t / 254 ms | 600t / **424 ms** (sustains beat) |
| Lead (violin) | 85–254 ms | unchanged (jig lilt) |
| Drums | 85 ms | unchanged (hits) |
