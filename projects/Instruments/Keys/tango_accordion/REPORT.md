# REPORT — Tango Accordion / Bandoneón (GM23)

**Job**: Nightly instrument research (layer-aligned), run 2026-10-30
**Instrument**: Tango Accordion — the GM slot for the **bandoneón**
**Family**: Keys (free-reed aerophone, sibling of `accordion` GM21)
**Files added**: `Keys/tango_accordion/instrument.md`, `Keys/tango_accordion/tango_accordion.py`
**Registered**: `instrument_registry.py` (`tango_accordion`, convenience constant `TANGO_ACCORDION`)

---

## 1. What the instrument is

The bandoneón (Spanish *bandoneón*, German *Bandonion*) is a bisonoric
button concertina named after the German instrument dealer **Heinrich Band**
(1821–1860, Krefeld), who developed it around 1846 from Carl Friedrich Uhlig's
German concertina — originally for religious and popular music, as a portable
substitute for a church organ. German and Italian emigrants and sailors brought
it to the Río de la Plata **around 1870**, where it was adopted into the nascent
tango (a descendant of the milonga), and by 1910 German makers were producing
bandoneons expressly for the Argentine/Uruguayan market (25,000 shipped to
Argentina in 1930 alone). It is also used in Chamamé.

Why it sounds the way it does:

- **Bisonoric**: each button sounds a *different note* on push vs pull. The
  right and left hand layouts are also different, so a player learns four
  keyboard layouts; many tango players play almost entirely on the draw stroke
  and close the bellows with the air-release button.
- **No register switches**: a bandoneón always uses the same reed sets
  (unlike the multi-rank piano accordion's musette stops).
- **Octave-coupled reeds**: every note sounds **two reeds tuned an octave
  apart**. This is the instrument's timbre identity — a hollow, nasal, cutting
  cry — not the accordion's 2–5-cent musette chorus.
- **Split timbre by hand**: the left hand sits inside a wooden box (nasal,
  muted); the right hand is bright and sharp.
- **Standard system**: the Argentine tango instrument is the **142-tone,
  71-key Rheinische (rheinische Lage) system**; 152-tone variants exist, plus
  the unisonoric Kusserow/Peguri "chromatic" systems (popular in Europe, not in
  Argentina — the tango repertoire is idiomatic to the bisonoric layout).
- Reference players: Eduardo Arolas, Vicente Greco, Pedro Maffia, Pedro
  Laurenz, Aníbal Troilo, **Ástor Piazzolla** (bandoneonist in Troilo's
  orchestra 1939–44; *nuevo tango*, e.g. "Fugata", 1969), Dino Saluzzi,
  Juan José Mosalini, Rodolfo Mederos.

Ensemble context: the **orquesta típica** = at least two bandoneones, two
violins, piano, double bass (+ flute, sometimes clarinet/guitars); the classic
**sextet** = 2 bandoneones + 2 violins + piano + bass. Tango is in 2/4 or 4/4.

**Distinct from `accordion` (GM21)**: piano keyboard + Stradella chord buttons,
unisonoric, musette-detuned multi-rank chorus, folk/pop voice. The bandoneón is
button-operated, bisonoric, octave-coupled, and is the tango voice.

## 2. MIDI / GM facts

| Item | Value |
|---|---|
| GM program | **23** (0-based; 24th GM entry) |
| GM1 name | "Tango Accordion" |
| Roland GS / Yamaha XG | "Bandoneon" / "TangoAccordion" |
| `MidiInstrument` enum | **no constant** — legacy 10-instrument enum (PIANO=0, CHURCH_ORGAN=20, ACOUSTIC_GUITAR=25, VIOLIN=41, STRING_ENSEMBLE=49, TRUMPET=57, FLUTE=74, SYNTH_PAD=88, BASS=33); use raw 23 |
| Channel | melodic 0–9 (channel 9 = drum map, ch9 quirk) |
| FluidR3 preset 23 | **"Bandoneon"** (verified from the `phdr` chunk) |
| RenderPipeline stem | `GM_PROGRAMS[23]` = "Tango Accordion" → `trackXX_Tango_Accordion.wav` |

## 3. Range

| Zone | MIDI | Pitches | Character |
|---|---|---|---|
| Full range | **41–96** | F2–C7 | practical written band (≈4½ octaves) |
| bass | 41–59 | F2–B3 | left hand in the wooden box — nasal, muted |
| low_mid | 60–67 | C4–G4 | hand overlap — full, woody body |
| cantabile | 68–79 | G#4–G5 | the tango singing register (most expressive) |
| high | 80–91 | G#5–G6 | bright, sharp right hand — ornaments |
| top | 92–96 | G6–C7 | thin, squealing — rhetorical accents only |

- **SOLO_RANGE** = (53, 91) F3–G6, **SWEET_SPOT** = (57, 84) A3–C6.
- Physical compass: de.wikipedia — "Insgesamt kann über fast fünf Oktaven
  gespielt werden" (nearly five octaves); fr.wikipedia — the tessitura
  "approche six octaves" once the octave-coupled second voice is counted.
  Endpoints vary by system (142 vs 152 tones), so F2–C7 is documented as the
  practical written band for the standard tango instrument.
- Empirical FluidR3 sweep (RMS, velocity 90, notes 24–108):

```
  note  24: RMS =   1613.3 AUDIBLE      note  72: RMS =   1054.7 AUDIBLE
  note  36: RMS =   1559.1 AUDIBLE      note  84: RMS =   1530.3 AUDIBLE
  note  41: RMS =   1478.9 AUDIBLE      note  96: RMS =   1569.1 AUDIBLE
  note  48: RMS =   1433.7 AUDIBLE      note 108: RMS =   1360.4 AUDIBLE
  note  60: RMS =   1362.1 AUDIBLE
  → 9/9 audible, no gaps (full-keyboard patch; SF2 never clips a composition)
```

## 4. Role

`lead, melody, ornament, harmony, accent, pad`
(humanize: melodic → style governs timing/layback, Keys-family velocity DNA)

- **Lead / melody** — the tango frontline; cantabile register 68–79; the two
  bandoneones of an orquesta típica play thirds/sixths, octaves, or call and
  response.
- **Ornament** — arrastre slides, llorón cries, picado pickups, chasquido
  bellows whips.
- **Harmony / pad** — sustained swell beds; the patch is polyphonic (chords
  stack) but the ensemble role is a single line or two-note dyads.
- **Accent** — marcato stabs, golpe box knocks on the habanera-inflected
  phrasing.
- **NOT**: a bass voice (down to F2, but the part belongs to double bass /
  cello), a Stradella chord-comp voice, or a folk-musette accordion (GM21).

## 5. Synthesis engine recommendation

**Primary: PhaseModSynth** (`sound/synthesis/phase_mod.py`) — a free reed is a
phase-modulated oscillator.

```python
FM_DEFAULTS = {
    "carrier_shape": "saw",     # symmetric reed: even + odd harmonics
    "mod_shape": "sine",
    "mod_freq_ratio": 1.0,
    "mod_depth": 3.4,           # accordion 3.2 < bandoneón 3.4 < bagpipe 4.5
    "attack": 0.018,            # heavy reed speaks almost instantly
    "release": 0.07,            # choked, reedy stop at the button
    "sustain_level": 0.82,      # bellows hold the level
    "octave_double": 0.45,      # THE tell: second reed one octave up at 45%
}
SYNTHESIS = "phase_mod"
SYNTHESIS_DEFAULTS = {"instrument": "tango_accordion", **FM_DEFAULTS}
```

The octave-coupled pair is modelled as a **second PhaseModSynth voice one
octave above at amplitude 0.45** — tuned in octaves, NOT detuned by cents
(detune would be a piano accordion musette, a different instrument).

Secondary/fallbacks:

```python
ADDITIVE_DEFAULTS = {
    "harmonic_count": 10,
    "harmonic_weights": [1.0, 0.55, 0.42, 0.30, 0.22, 0.14, 0.11, 0.08,
                         0.06, 0.045],   # h2/h1 = 0.55 → the octave reed
    "attack": 0.02, "release": 0.08,
}
MODAL_PRESET = "tube"   # closed-tube/reed-ish fallback (accordion uses "string")
```

## 6. All constants (`tango_accordion.py`)

```python
MIDI_PROGRAM = 23
GM_NAME = "Tango Accordion"
STEM_LABEL = "Tango_Accordion"

RANGE_MIN = 41          # F2 — lowest left-hand reed
RANGE_MAX = 96          # C7 — top of the right-hand keyboard
SOLO_RANGE = (53, 91)   # F3–G6
SWEET_SPOT = (57, 84)   # A3–C6 — the tango cantabile register

ZONES = {
    "bass": (41, 59),        # left hand in the wooden box: nasal, muted
    "low_mid": (60, 67),     # hand-overlap: full, woody body
    "cantabile": (68, 79),   # THE tango melody register
    "high": (80, 91),        # bright, sharp right hand
    "top": (92, 96),         # thin, squealing rhetorical top
}

ARTICULATIONS = {
    "cantabile": (70, 1.0),   "sustain": (76, 1.0),
    "marcato": (92, 0.85),    "picado": (82, 0.22),
    "fuelle": (78, 0.5),      "lloron": (74, 1.0),
    "arrastre": (86, 0.65),   "chasquido": (96, 0.12),
    "golpe": (100, 0.08),     "sforzando": (98, 0.55),
}

SYNTHESIS = "phase_mod"
FM_DEFAULTS = {
    "carrier_shape": "saw", "mod_shape": "sine", "mod_freq_ratio": 1.0,
    "mod_depth": 3.4, "attack": 0.018, "release": 0.07,
    "sustain_level": 0.82, "octave_double": 0.45,
}
SYNTHESIS_DEFAULTS = {"instrument": "tango_accordion", **FM_DEFAULTS}
ADDITIVE_DEFAULTS = {
    "harmonic_count": 10,
    "harmonic_weights": [1.0, 0.55, 0.42, 0.30, 0.22, 0.14, 0.11, 0.08,
                         0.06, 0.045],   # normalize before apply_overtones()
    "attack": 0.02, "release": 0.08,
}
MODAL_PRESET = "tube"

REVERB_TAIL = 1.8        # s — tango salon/hall (accordion 1.4, strings 2.6)
EQ_BODY = (250, -2.0)    # cut wooden-box boom / left-hand nasal resonance
EQ_PRESENCE = (3000, 2.5)  # the reed edge that cuts through an ensemble
EQ_AIR = (7500, 0.8)     # gentle valve/key air
PAN = 0.0                # centre; ±0.2 for left/right-hand spread

def midi_to_freq(midi): return 440.0 * 2.0 ** ((midi - 69) / 12.0)
```

## 7. Registration proof (`instrument_registry.py`)

Edits:
1. `_INSTRUMENT_MODULES`: `"Keys.tango_accordion.tango_accordion": "tango_accordion"`
2. Convenience constant: `TANGO_ACCORDION = ALL_INSTRUMENTS["tango_accordion"]`
3. `registry_table()` role branch:
   `elif low == "tango accordion": role = "lead, melody, ornament, harmony, accent, pad"`
4. `__main__` verification block for GM23

Verification run (`cd /opt/data/projects/Instruments && \
/opt/data/micromamba/envs/musicom/bin/python instrument_registry.py`, exit 0):

```
| Keys | Tango Accordion | 23 | 41–96 | lead, melody, ornament, harmony, accent, pad |
...
=== Tango Accordion (Bandoneon, GM23) ===
  TANGO_ACCORDION.midi_program = 23 (should be 23)
  by_name('tango accordion') = <Instrument Tango Accordion (family=Keys, program=23, range=41-96)>
  by_name('TANGO ACCORDION') = <Instrument Tango Accordion (family=Keys, program=23, range=41-96)>
  by_program(23) = <Instrument Tango Accordion (family=Keys, program=23, range=41-96)>
  by_program(21) = <Instrument Accordion (family=Keys, program=21, range=36-96)> (distinct: piano accordion)
  TANGO_ACCORDION.in_sweet_spot(72) = True
  TANGO_ACCORDION.in_sweet_spot(30) = False
  TANGO_ACCORDION.range_min = 41 TANGO_ACCORDION.range_max = 96
  TANGO_ACCORDION.stem_label = 'Tango_Accordion'
```

Full run log saved at `_test/registry_out_tango.txt` (the complete
`registry_table()` + every historical verification line, 386 lines).

## 8. End-to-end verification

Script: `_test/verify_tango_accordion.py` (template: `verify_synth_brass_1.py`).
Audio render is **INSTRUMENT SOLO ONLY** (one melodic voice, one track) — the
2026-09-01 comb-filter rule. A drum-kit track rides along for context but is
excluded from the solo render.

| Check | Result |
|---|---|
| Registry import (`from instrument_registry import by_name, TANGO_ACCORDION`) | ✅ same object via name and program 23 |
| UnitMatrixComposer (1 bar, 1 section, bandoneón + drums) `validate()` | ✅ **zero-drift True** |
| MIDI export | ✅ **181 bytes** (> 40) |
| SoundFont resolution | ✅ `discover_soundfont()` → FluidR3_GM.sf2 (not hardcoded) |
| FluidSynth WAV, solo voice 0 | ✅ **777,004 bytes** (> 40) |
| 4–8 kHz spectral buzz (solo) | ✅ **8.0%** (gate ≤ 20%) |
| RenderPipeline stems | ✅ `track00_Tango_Accordion.wav` 777,004 B + `track01_Drums.wav` 706,092 B |
| Stem label | `GM_PROGRAMS[23]` = "Tango Accordion" → `Tango_Accordion` ✅ |
| SF2 preset name | preset 23 = "Bandoneon" (cosmetic mismatch, no routing impact) |
| PhaseModSynth A4 + octave reed | ✅ peak 1.135, sustain/peak 0.301 (no collapse) |
| Additive octave stack | ✅ peak 63.0 (h2/h1 = 0.55) |
| Pitch sweep 24–108 | ✅ 9/9 audible, no gaps |
| Spectral centroid (solo) | C4 **3568 Hz**, C6 **5999 Hz** — bright/nasal |

Script output tail:

```
Zero-drift: True (OK)
MIDI: .../tango_accordion_test.mid (181 bytes)
SoundFont: .../FluidR3_GM.sf2
WAV (solo): .../tango_accordion_test.wav (777004 bytes)
Spectral check: 4-8kHz buzz energy = 8.0% (OK)
Stem label: GM_PROGRAMS[23] = 'Tango Accordion'
SF2 preset 23 -> 'Bandoneon'
Stems rendered (2 files):
  track00_Tango_Accordion.wav (777004 bytes)
  track01_Drums.wav (706092 bytes)
PhaseModSynth bandoneón A4 + octave reed: peak=1.135 sustain_rms=0.3412 sustain/peak=0.301
Additive bandoneón stack: peak=63.0 (h2/h1 = 0.55 — the octave reed)
...
Spectral centroid note 60: 3568 Hz
Spectral centroid note 84: 5999 Hz
ALL CHECKS PASSED
```

Artifacts on disk: `_test/tango_accordion_test.mid`, `_test/tango_accordion_test.wav`,
`_test/stems_tango_accordion/`, `_test/sweep_tango_accordion.py` (standalone
patch sweep), `_test/registry_out_tango.txt`.

## 9. Quirks found

1. **Stem label vs SF2 name** — `GM_PROGRAMS[23]` = "Tango Accordion" (that is
   what names the stem) but FluidR3 preset 23 is "Bandoneon". Cosmetic only;
   the RenderPipeline derives filenames from `GM_PROGRAMS`, never from the SF2.
2. **No enum constant** — `MidiInstrument` is a 10-instrument legacy enum with
   no accordion-family member; use raw GM 23, the registry is the full KB.
3. **Channel 9** — if program 23 is sent on channel 9 the drum map fires and
   the stem falls back to `Acoustic_Grand_Piano` (timpani lesson).
4. **SF2 ignores portamento** (CC5/CC65) — `arrastre` slides must be written as
   fast chromatic grace runs, not controller slides.
5. **Bisonoric reality not modellable** — push/pull changes the note on the
   real instrument; a MIDI patch cannot. Write the sounding line only; do not
   write same-button alternation figures.
6. **Additive API** — `SoundWave.apply_overtones()` asserts the partial weights
   sum to 1.0; the documented weights are relative, normalize at the call site
   (`w / w.sum()`). Recorded in a comment in `tango_accordion.py`.
7. **Ensemble vs patch polyphony** — the patch stacks chords fine, but the
   idiomatic bandoneón part is a single line (or two-note dyads). Dense low
   chords mud up the 250 Hz region.
8. **No unison doubling** — never put another melodic patch on the same
   pitches (comb filtering). Octaves, thirds/sixths, or drums are fine.

## 10. Files changed

```
new  Keys/tango_accordion/instrument.md
new  Keys/tango_accordion/tango_accordion.py
new  Keys/tango_accordion/REPORT.md          (this file)
new  _test/verify_tango_accordion.py
new  _test/sweep_tango_accordion.py
new  _test/registry_out_tango.txt
mod  instrument_registry.py   (+ module entry, + TANGO_ACCORDION,
                               + registry_table role branch, + __main__ block)
mod  registry.md              (+ table row, + stem-label row, + 2026-10-30 changelog)
```
