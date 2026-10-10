# REPORT — Pizzicato Strings (GM45) added 2026-10-10

## Instrument

- **Name**: Pizzicato Strings (GM1 "Pizzicato Strings")
- **Family**: Strings (6th entry: violin, viola, cello, double_bass, harp, **pizzicato_strings**)
- **Identity**: the string SECTION playing pizzicato (plucked, NOT bowed) — a
  rhythmic/ostinato colour voice (Tchaikovsky 4 scherzo, film-score plucked
  figures). NOT a sustain lead.
- **Program**: 45 (0-based GM1). Melodic channel (0–9) — channel 9 would
  trigger the drum map. MidiInstrument enum does not expose it (enum holds
  only 10 instruments); raw GM number used; the registry is the full KB.
- **Files**:
  - `Strings/pizzicato_strings/instrument.md`
  - `Strings/pizzicato_strings/pizzicato_strings.py`
  - `Strings/pizzicato_strings/pizzicato_test.mid` (120 bytes)
  - `Strings/pizzicato_strings/pizzicato_test.wav` (943,404 bytes ≈ 921 KB)
  - `Strings/pizzicato_strings/stems_pizzicato/track00_Pizzicato_Strings.wav` (943,404 bytes)
  - `Strings/pizzicato_strings/REPORT.md` (this file)
  - `_test/verify_pizzicato_strings.py` (verify script, ALL CHECKS PASSED)

## Range

| | MIDI | Pitches | Notes |
|---|---|---|---|
| Full range | 36–96 | C2–C7 | GM spec span of the whole section (contrabass→violin) |
| Solo range | 48–84 | C3–C6 | "decent pizz" register — section samples speak clearly |
| Sweet spot | 55–79 | G3–G5 | balanced: cello upper + viola + violin mid; round pluck |
| Low zone | 36–54 | C2–F#3 | bass/cello pizz — thick, present, SOME sustain; ostinato/bass lines |
| Mid zone | 55–76 | G3–E5 | viola/violin mid — balanced pluck, accompaniment home |
| High zone | 77–96 | F5–C7 | violin high — dry, thin, NO sustain; sparkle/accent only (>C6 very thin) |

Real-instrument facts (Tim Davies, deBreved "It's the Pizz"):
- Loudest real pizz ≈ a bow's **mezzo-forte** — never balance pizz vs full
  arco/brass at forte.
- Violin pizz: little sustain in the low register, none from the middle up;
  highest decent note ~C6 (84), above it tone thins progressively.
- Bass has the most presence and a thick tone with real sustain; the
  cello→bass hand-off is a big timbre change.
- Section pizz has natural timing looseness; players need space between
  plucks (one finger holds the bow). Write with a rhythmic lift.

## Articulations (velocity, duration_factor)

| Key | Velocity | Dur× | Meaning |
|---|---|---|---|
| pizz | 74 | 0.35 | standard finger pluck — dry ring, the default |
| ostinato | 68 | 0.20 | repeated rhythmic figure — bread and butter |
| secco | 58 | 0.12 | choked stop — very short dry tick |
| bass_pizz | 82 | 0.90 | low-string pluck let to ring (l.v./ring-over) |
| snap | 100 | 0.08 | Bartók snap — loud, percussive, little pitch |
| left_hand | 52 | 0.30 | weak pull-off, descending, pro effect |
| double_stop | 80 | 0.40 | two-string pluck (division); keep small |
| accent | 94 | 0.25 | marcato pluck — driving downbeat |

## Timbre DNA

- Finger-flesh pluck excitation (no bow noise, no sustain) — soft round
  attack with tiny nail transient; full string partial stack, register
  dependent (contrabass dark/thumpy → high violin thin/near-pure).
- Decay: dry and short — low strings 0.5–1.5 s, mid 0.3–0.8 s, high violin
  near-zero. Ensemble: slight detune chorus + timing looseness.
- Character: rhythmic, articulate, percussive-but-pitched.

## Role

rhythm, ostinato, bass, accompaniment, countermelody, accent — the #1 use is
plucked ostinato figures and plucked bass lines; chord accompaniment in
small (1–4 note) division; NOT sustain/pad, NOT dense chords.

## Synthesis Engine (musicom)

- **Primary: Karplus-Strong** (`sound/synthesis/karplus_strong.py`, SP-011) —
  plucked waveguide = exact physical model for a finger-plucked string.
  `KARPLUS_DEFAULTS = {loop_gain: 0.9960, excitation: "pluck", width: 0.55,
  lowpass_hz: 7500, noise_component: 0.03, role: "accent"}` — deliberately
  DRY (section pizz 0.3–1.5 s ring; high strings ~0 s), between clavi 0.9960
  and electric bass 0.9970.
- **Fallback: ModalSynth** `MODAL_PRESET = "string"` (harmonic stack, impulse
  excitation).
- **Cheap alt: PhaseModSynth** `FM_DEFAULTS = {sine, ratio 1.0, depth 1.2,
  attack 0.002, release 0.20}`.
- Ring verification: Karplus 0.9960 vs 0.990 dull control at A2 — tail
  (0.5–1.0 s) RMS ratio **1.56×** → the pizz pluck rings audibly longer.

## Production Defaults

- REVERB_TAIL = 2.0 s (hall; MUST NOT smear the pluck transient — 2.0 s is
  the ceiling; dry room 0.8–1.2 s for intimate passages)
- EQ_BODY = (300 Hz, −2.5 dB) — tame section boxiness
- EQ_PRESENCE = (2500 Hz, +2.5 dB) — fingertip wood+string attack
- EQ_AIR = (8000 Hz, +1.5 dB) — subtle sparkle (high violin already thin)
- PAN = 0.0 (center solo; −0.15…−0.25 section seating; ±0.3 double-tracked)

## Registration Proof (instrument_registry.py)

Module added: `"Strings.pizzicato_strings.pizzicato_strings": "pizzicato_strings"`
Convenience constant: `PIZZICATO_STRINGS = ALL_INSTRUMENTS["pizzicato_strings"]`
Role mapping added to `registry_table()`; verification block added to `__main__`.

`python instrument_registry.py` → registry_table() row + verification:

```
| Strings | Pizzicato Strings | 45 | 36–96 | rhythm, ostinato, bass, accompaniment, countermelody, accent |
...
=== Pizzicato Strings (GM45) ===
  PIZZICATO_STRINGS.midi_program = 45 (should be 45)
  by_name('pizzicato strings') = <Instrument Pizzicato Strings (family=Strings, program=45, range=36-96)>
  by_program(45) = <Instrument Pizzicato Strings (family=Strings, program=45, range=36-96)>
  PIZZICATO_STRINGS.in_sweet_spot(64) = True
  PIZZICATO_STRINGS.in_sweet_spot(30) = False
  PIZZICATO_STRINGS.range_min = 36 PIZZICATO_STRINGS.range_max = 96
  PIZZICATO_STRINGS.stem_label = 'Pizzicato_Strings'
```

## Verification Results (verify_pizzicato_strings.py — ALL CHECKS PASSED)

- **Registration**: `by_name('pizzicato strings')` and `by_program(45)` both
  resolve to the Pizzicato Strings Instrument (imported THROUGH the registry)
- **Zero-drift**: `validate() = True (OK)` — 1 voice × 1 section, A-minor
  ostinato (A3 C4 E4 A4 E4 C4 A3 C4), eighth-note plucks ending flush at
  BAR=1920 (terminal landmark)
- **MIDI**: `pizzicato_test.mid` = **120 bytes** (> 40 ✓)
- **WAV (SOLO render, 1 voice only — no unison doubling)**: via
  `discover_soundfont()` → **FluidR3_GM.sf2**; `pizzicato_test.wav` =
  **943,404 bytes** (> 40 ✓)
- **Spectral gate**: 4–8 kHz buzz = **0.2%** (≤ 20% ✓; the cleanest of the
  registered set — no bow noise, dry plucks)
- **Stem label**: `GM_PROGRAMS[45] = "Pizzicato Strings"` →
  `track00_Pizzicato_Strings.wav` ✓ — **no quirk**; `STEM_LABEL =
  "Pizzicato_Strings"` matches pipeline sanitized name
- **SF2 preset**: FluidR3 preset 45 = `"Pizzicato Section"` (phdr-verified)
  — internal name differs cosmetically from pipeline label, **no routing
  impact**
- **Full pipeline stem render**: 1 stem file, 943,404 bytes, named
  `track00_Pizzicato_Strings.wav` ✓
- **Pitch sweep (FluidR3 preset 45, RMS @100 vel)**: notes 24–96 all audible
  (0.059–0.18 RMS); **silent at 103+ (patch ceiling)** — documented range
  36–96 never clips; never write above C7=96

## Quirks Found

1. **Stem label**: GM_PROGRAMS[45] = "Pizzicato Strings" — matches, **no
   quirk**. SF2 preset internal name is "Pizzicato Section" (cosmetic).
2. **Patch ceiling**: preset 45 is SILENT at MIDI 103/108 (probed 24–108,
   audible 24–96). Composition jobs must stay ≤ 96 (C7) per documented range.
3. **Channel**: melodic channel required — channel 9 = drum map + stem
   mislabel fallback (same rule as timpani/taiko/electric bass).
4. **Register physics (real instrument)**: pizz volume ceiling ≈
   mezzo-forte; high violin pizz has no sustain (effect register only);
   bass/cello pizz is the longest-ringing most present zone. Dense
   multi-stop section pizz gets messy — players divide anyway.
5. **Not a lead voice**: dry decays mean pizz carries rhythm/accent, not
   sustained melody — write ostinati, plucked bass, chord division.

## registry.md Updated

- Registry table: added row `| Strings | Pizzicato Strings | 45 | 36–96 | rhythm, ostinato, bass, accompaniment, countermelody, accent |`
- Stem-label quirks table: added program 45 row (match, SF2 cosmetic diff)
- Changelog: "**Pizzicato Strings added** (2026-10-10)" entry appended.