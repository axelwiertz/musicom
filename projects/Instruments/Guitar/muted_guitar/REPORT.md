# REPORT — Muted Guitar (GM28)

**Job**: Nightly Instrument Research Job — layer-aligned
**Date**: 2026-11-05
**Instrument**: Muted Guitar (palm-muted / fret-hand-damped electric guitar)
**Family**: Guitar (seventh entry)
**Files**: `Guitar/muted_guitar/instrument.md`, `Guitar/muted_guitar/muted_guitar.py`
**Verification**: `_test/verify_muted_guitar.py` (registry-backed, solo render)

---

## 1. Why this instrument

The KB had 79 instrument folders / 85 registry keys covering most GM programs,
but **GM 28 Electric Guitar (muted)** was an uncovered gap and the only
remaining common electric-guitar voice. It is not a duplicate of any existing
entry: the six guitar entries are nylon (24), steel (25), jazz (26), clean
(27), overdriven (29), distortion (30) — all sustaining voices. GM28 is the
opposite instrument: palm/fret-hand damping makes every note an attack plus a
short decay, which is a distinct arrangement role (rhythm-as-percussion, funk
chops, metal chugs), a distinct articulation set, and a distinct synthesis
parameterisation (a very lossy Karplus-Strong loop).

## 2. MIDI / GM

| Field | Value |
|---|---|
| MIDI program | **28** (zero-based GM; GM1 program 29) |
| GM name | `Electric Guitar (muted)` |
| Pipeline stem label | `GM_PROGRAMS[28] = "Electric Guitar (muted)"` → `trackXX_Electric_Guitar_muted.wav` |
| STEM_LABEL | `Electric_Guitar_muted` (matches the pipeline's sanitized label) |
| FluidR3 preset 28 | **"Palm Muted Guitar"** (verified from the SF2 `phdr` chunk) |
| Channel | any melodic channel (polyphonic, 6 strings) |

**Quirk (cosmetic, no routing impact)**: the SF2 names the *technique*
("Palm Muted Guitar"), the pipeline names the GM2 *program*
("Electric Guitar (muted)"). Same class as the existing "Jazz Guitar",
"Bag pipe" and "Shanai" label quirks.

## 3. Range

| Field | MIDI | Pitches |
|---|---|---|
| RANGE_MIN / RANGE_MAX | **28–84** | E1–C6 (GM patch span) |
| Real instrument | 40–76 | E2–E6 (standard 22-fret guitar) |
| SOLO_RANGE | **(40, 76)** | E2–E6, the real neck |
| SWEET_SPOT | **(40, 64)** | E2–E4, funk/metal rhythm heart |

Zones:

| Zone | MIDI | Use |
|---|---|---|
| `low_chug` | 28–47 | Palm-muted low-E/A chugs; metal riff atom; fundamental thump, no ring |
| `mid_chop` | 48–64 | 16th chord chops, single-note funk lines, double stops, scratches |
| `high` | 65–84 | Short muted stabs, dead-string fills; thin/clicky above ~E5 |

Empirical FluidR3 sweep (velocity 100, notes 28/33/38/40/43/45/48/52/55/59/62/
64/67/71/74/76/79/84): **18/18 audible, no gaps**. RMS 0.1217 at E1 (28),
0.0664 at E2 (40), 0.0317 at E4 (64), 0.0055 at C6 (84) — present but weak at
the top; write the top octave sparingly.

## 4. Role

`rhythm, comp, groove, accent, texture, melody`

- **Rhythm / groove** — a continuous 16th-note stream of chops and scratches;
  the guitar functions as part of the percussion section and defines the
  subdivision, not the harmony.
- **Comp** — 3–4 note chops and double stops only; 6-string barres become a
  percussive smear.
- **Accent** — palm-release open chords as the contrast that makes mutes read.
- **Texture** — fret-hand dead-string "chika" (unpitched).
- **Melody** — short staccato single notes / octave hooks ONLY; not a
  sustaining lead (use clean/jazz/distortion for that).

## 5. Articulations (velocity, duration factor)

```python
ARTICULATIONS = {
    "palm_mute":   (82, 0.18),  # default: palm edge at bridge, pitched, fast decay
    "chug":        (92, 0.08),  # low-E/A 16th chug, dead stop — metal riff atom
    "funk_chop":   (78, 0.12),  # 16th chord chop on upbeats (the "chick")
    "muted_strum": (72, 0.10),  # full-strum rake, fully damped ("shhk")
    "scratch":     (38, 0.05),  # fret-hand dead-string scratch, no pitch
    "staccato":    (80, 0.22),  # single-note muted lead, pitch defined
    "open_accent": (90, 0.60),  # palm released — chord rings; contrast accent
    "double_stop": (76, 0.15),  # two-note muted double stop
    "octave":      (74, 0.30),  # octave funk hook
    "slide":       (70, 0.25),  # muted fret-hand slide
    "bend":        (78, 0.40),  # short bluesy bend, then damped
    "ghost_note":  (30, 0.04),  # near-inaudible 16th filler
    "accent":      (90, 0.12),  # hard muted hit on the "1"
}
```

## 6. Synthesis

**Primary: Karplus-Strong** (`sound/synthesis/karplus_strong.py`) — still a
plucked string, but a very lossy waveguide loop (the mute).

```python
SYNTHESIS = "karplus_strong"
KARPLUS_DEFAULTS = {
    "loop_gain": 0.9850,      # lowest in the guitar family; ~0.2–0.4 s decay
    "excitation": "pick",     # hard plectrum attack = the articulation
    "width": 0.30,            # bright pick transient, damping eats the tail
    "lowpass_hz": 2200,       # palm flesh + bridge pickup rolloff
    "noise_component": 0.030, # pick scrape + palm slap are part of the sound
}
```

**Secondary: ModalSynth** — stock `'string'` bank, impulse excitation, very
fast decay rates (~12/26/44/66/90 vs jazz guitar 4/10/18/28/40).

**Tertiary: PhaseModSynth** — saw carrier, `mod_freq_ratio` 1.0,
`mod_depth` 2.0, `attack` 0.004 s, `release` 0.08 s (the mute).

## 7. Production defaults

| Parameter | Value |
|---|---|
| REVERB_TAIL | 0.9 s (deliberately dry — 16th detail must stay articulate) |
| EQ_BODY | (220, −1.5) — trim palm-mute thump vs bass |
| EQ_PRESENCE | (3200, +2.5) — pick-attack click; the voice has no sustained energy |
| EQ_AIR | (8000, +0.5) — minimal air; damping removes the top by design |
| PAN | −0.25 (double hard L/R at ±0.6 for funk/metal) |

`midi_to_freq` included (A4 = 440 Hz standard).

## 8. Registration proof

`instrument_registry.py` — added to `_INSTRUMENT_MODULES`:
```python
    "Guitar.clean_electric.clean_electric": "clean_electric",
    "Guitar.muted_guitar.muted_guitar": "muted_guitar",
```
and convenience constant:
```python
JAZZ_GUITAR = ALL_INSTRUMENTS["jazz_guitar"]
MUTED_GUITAR = ALL_INSTRUMENTS["muted_guitar"]
```

Verification run output (excerpt — full `registry_table()` printed by the
script):

```
Registry: by_name('muted_guitar') = <Instrument Electric Guitar (muted) (family=Guitar, program=28, range=28-84)>
Registry: by_name('muted guitar')  = <Instrument Electric Guitar (muted) (family=Guitar, program=28, range=28-84)>
Registry: by_name('Electric Guitar (muted)') = <Instrument Electric Guitar (muted) (family=Guitar, program=28, range=28-84)>
Registry: by_program(28) = <Instrument Electric Guitar (muted) (family=Guitar, program=28, range=28-84)>
Registry: by_program(27) = <Instrument Electric Guitar (clean) (family=Guitar, program=27, range=28-84)> (distinct: clean electric)
Registry: ALL_INSTRUMENTS count = 86
...
| Guitar | Electric Guitar (muted) | 28 | 28–84 | rhythm, comp, groove, accent, texture, melody |
...
Muted Guitar: program=28 gm='Electric Guitar (muted)' stem='Electric_Guitar_muted' range=28-84 sweet=(40, 64) solo=(40, 76)
Muted Guitar: zones={'low_chug': (28, 47), 'mid_chop': (48, 64), 'high': (65, 84)}
Muted Guitar: art=['palm_mute', 'chug', 'funk_chop', 'muted_strum', 'scratch', 'staccato', 'open_accent', 'double_stop', 'octave', 'slide', 'bend', 'ghost_note', 'accent']
Muted Guitar: synth=karplus_strong modal='string' ks={'loop_gain': 0.985, 'excitation': 'pick', 'width': 0.3, 'lowpass_hz': 2200, 'noise_component': 0.03}
Muted Guitar: reverb=0.9s eq=(220, -1.5),(3200, 2.5),(8000, 0.5) pan=-0.25
Muted Guitar: E2=82.4Hz A2=110.0Hz C3=130.8Hz E4=329.6Hz

=== Muted Guitar (Palm Mute, GM28) ===
  MUTED_GUITAR.midi_program = 28 (should be 28)
  by_name('muted guitar') = <Instrument Electric Guitar (muted) (family=Guitar, program=28, range=28-84)>
  by_name('Electric Guitar (muted)') = <Instrument Electric Guitar (muted) (family=Guitar, program=28, range=28-84)>
  by_program(28) = <Instrument Electric Guitar (muted) (family=Guitar, program=28, range=28-84)>
  by_program(27) = <Instrument Electric Guitar (clean) (family=Guitar, program=27, range=28-84)> (distinct: clean electric)
  MUTED_GUITAR.in_sweet_spot(45) = True
  MUTED_GUITAR.in_sweet_spot(80) = False
  MUTED_GUITAR.range_min = 28 MUTED_GUITAR.range_max = 84
  MUTED_GUITAR.stem_label = 'Electric_Guitar_muted'
```

## 9. Verification results

Composition: 1 bar, 1 section, 104 bpm. Voice 0 = Muted Guitar SOLO
(16th-note funk chops + palm-muted octave hook). Voice 1 = drum-kit context
(ch9). **No second melodic patch on the same pitches** (2026-09-01
comb-filter rule).

| Check | Result |
|---|---|
| Zero-drift (`validate()`) | **True (OK)** |
| MIDI export | `_test/muted_guitar_test.mid` — **467 bytes** (> 40 ✓) |
| WAV render (SOLO, FluidR3) | `_test/muted_guitar_test.wav` — **791,340 bytes** (> 40 ✓) |
| SoundFont resolution | `discover_soundfont()` → `/opt/data/micromamba/envs/musicom/share/soundfonts/FluidR3_GM.sf2` (148,358,590 B) |
| Spectral buzz check | 4–8 kHz = **0.1%** (gate 20%) — clean |
| Karplus-Strong smoke | A2/0.6 s/vel 100 → peak 0.693, tail_rms/peak **0.013** (mute damps) |
| SF2 preset name | preset 28 = **"Palm Muted Guitar"** |
| Pipeline stem label | `GM_PROGRAMS[28]` = **"Electric Guitar (muted)"** == `STEM_LABEL.replace('_',' ')` |
| Stems rendered | `track00_Electric_Guitar_muted.wav` (791,340 B), `track01_Drums.wav` (835,628 B) |

Command:

```bash
cd /opt/data/repos/musicom && \
/opt/data/micromamba/envs/musicom/bin/python projects/Instruments/_test/verify_muted_guitar.py
# -> ALL CHECKS PASSED
```

Registry table run:

```bash
cd /opt/data/projects/Instruments && \
/opt/data/micromamba/envs/musicom/bin/python instrument_registry.py
# -> full registry_table() including the Muted Guitar row + verification lines
```

## 10. Quirks found / notes

1. **SF2 vs pipeline naming** — preset 28 is "Palm Muted Guitar" in FluidR3;
   the pipeline labels it "Electric Guitar (muted)". Cosmetic only; STEM_LABEL
   follows the pipeline.
2. **One-shot patch** — a long MIDI note does not produce a long sound; the
   patch is a dedicated muted sample set that decays regardless of note
   length. Correct behaviour, but it means `open_accent` is the only way to
   get a ringing chord.
3. **Loop gain floor** — 0.9850 is the lowest in the guitar family; KS with
   the family's usual 0.997 would ring for seconds and defeat the instrument.
4. **Velocity-critical** — the patch has little natural sustain, so a flat
   velocity layer disappears in a mix; ghosts 30–40, chops 75–82, accents 90+.
5. **Doubling** — two takes of the SAME part hard L/R is the standard
   funk/metal production technique; stacking a *different* melodic patch on
   the same pitches is the 2026-09-01 comb-filter bug and was not done here.
6. Pre-existing README/registry inconsistencies (`Vox Humana` listed twice in
   `registry_table()`, duplicate SITAR constant) were left untouched — out of
   scope for this instrument.
