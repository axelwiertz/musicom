# 246 — Balfolk Storytelling Jig

2-minute balfolk dance piece in **6/8 jig**, **D major**, dotted-quarter = 118 BPM.
Built through the musicom engine (UnitMatrixComposer → humanize → validate → to_midi).

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

## Humanization (always-on)

Style `balfolk` → folk profile, overridden per voice by instrument DNA:

| Voice | timing σ | layback | mean shift |
|---|---|---|---|
| Lead (violin) | 10 ms | +2 ms | 9.3 ticks |
| Chords (guitar) | 6 ms | +1 ms | 7.0 ticks |
| Bass (double bass) | 10 ms | +8 ms | 12.9 ticks (lays back) |
| Drums (kit) | 2 ms | 0 ms | 1.9 ticks (anchors) |

Seeded (246), zero-drift safe (forward-clamp + boundary-clamp + pinned landmark).

## Verification (measured)

| Check | Result |
|---|---|
| Zero-drift (track lengths) | ✅ 4 tracks × 172800 ticks, equal |
| Harmony (out-of-scale, D major) | ✅ 0 / 1536 pitched notes |
| Melody rest | ✅ 0 lead onsets in the 24 rest bars |
| Accompaniment through rest | ✅ 72/72 rest bars (3 tracks × 24) have content |
| Humanization applied | ✅ 1389 onsets off-grid (jitter ran) |
| Duration | ✅ 124 s (~2:04) |
| Master loudness | ✅ LUFS −16.0 (target −16, balfolk→folk), peak −1.46 dBTP |
