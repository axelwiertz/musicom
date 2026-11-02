# Synth Bass 2 (GM39) — Nightly Instrument Research Report

**Date**: 2026-09-02 · **Family**: Bass · **Folder**: `Bass/synth_bass_2/`

## Instrument

GM39 **Synth Bass 2** = the **resonant analog synth bass** — the Roland
TB-303 acid voice. The 1981 TB-303 Bass Line (a pulse oscillator through a
self-oscillating 24 dB/oct low-pass filter, plus the two gesture buttons
that define the idiom: **accent** = velocity re-triggers the filter
envelope, **slide** = portamento) is the box whose quirks birthed acid
house in 1985–87 Chicago (Phuture "Acid Tracks", DJ Pierre, Armando,
Adonis) and became the bass of techno, electro, and synthwave. The squelch
sibling of Synth Bass 1 (GM38, the Minimoog-ish analog bass): HIGHER filter
resonance (0.85 vs 0.55), BRIGHTER cutoff (2400 vs 1800 Hz), BIGGER
filter-env re-open (0.8 vs 0.5 — the accent), pulse waveform vs saw. GM39
is the one that screams.

**Family context** (Bass family now complete as 5 voices):

| Program | Instrument | Voice |
|---|---|---|
| 32 | Acoustic Bass | upright pizz |
| 33 | Electric Bass (finger) | amplified magnetic-pickup |
| 35 | Fretless Bass | frets-pulled electric |
| 38 | Synth Bass 1 | oscillator + filter (Minimoog-ish) |
| 39 | Synth Bass 2 | oscillator + filter (TB-303 acid, this entry) |

## Program

- **MIDI_PROGRAM = 39** (GM Synth Bass 2; 0-indexed — matches FluidR3
  preset 39 AND the RenderPipeline `GM_PROGRAMS[39]`).
- **Not** in `structures/instrument.py` `MidiInstrument` enum (legacy
  10-only enum) — use raw `program=39` in `add_voice`; the registry is the
  full KB.
- Channel: melodic channel (0–9) — channel 9 triggers the drum-kit map.

## Range

- **RANGE_MIN = 21 (A0), RANGE_MAX = 96 (C7)** — GM patch span (empirical
  FluidR3 sweep). Idiomatic writing band 28–72 (E1–C5). The real TB-303
  keyboard spans only C2–C4 (36–60); the GM patch plays far wider.
- **SWEET_SPOT = (36, 55)** — C2–G3, the acid groove pocket: 16th-note
  sequences, root-fifth riffs.
- **SOLO_RANGE = (48, 72)** — C3–C5, the acid-lead squelch band.

Zones:

| Zone | MIDI | Register |
|---|---|---|
| sub | 21–35 | chest thump, felt > heard, single notes only |
| groove | 36–50 | PRIMARY — acid 16ths, root-fifth pocket, squelch band |
| mid | 51–62 | octave-displacement riffs, melodic fills, singing tone |
| high | 63–96 | acid-lead/solo register, cutting resonance, thin |

**Empirical FluidR3 pitch sweep** (velocity 90, held 0.5 s mid-note RMS,
notes 21/24/28/33/36/40/45/48/52/55/60/64/67/72/77/84/96/108):

```
note 21: rms=0.2533    note 24: rms=0.2510    note 28: rms=0.2347
note 33: rms=0.2152    note 36: rms=0.1986    note 40: rms=0.1789
note 45: rms=0.1561    note 48: rms=0.1431    note 52: rms=0.1338
note 55: rms=0.1289    note 60: rms=0.1258    note 64: rms=0.1243
note 67: rms=0.1242    note 72: rms=0.1271    note 77: rms=0.1275
note 84: rms=0.1246    note 96: rms=0.1268    note 108: rms=0.0000
audible: 17/18 notes — one gap at C8=108 only
```

Remarkably even rolloff 0.2533 → 0.1246 across FIVE octaves (A0–C7), no
gaps in the writing band. Bottom 21–35 sub band is LOUD (the patch is a
synth bass — sub is its job). C8 silent. SF2 never clips a composition.

## Role

bass, rhythm, groove, accent, lead — a monophonic line instrument (acid
bass lines, 16th-note sequences, offbeat accents, sub pedals), NOT a
harmony/pad voice (true monophonic — chords are NOT idiomatic), NOT a
sub-only voice (the resonance is the identity), NOT a warm/fat voice (that
is Synth Bass 1). The offbeat accent IS the acid rhythm signature.

## Articulations (velocity, duration_factor)

| Technique | Vel | Dur | Timbre |
|---|---|---|---|
| accent | 98 | 0.60 | filter-env re-trigger — the squelch burst (THE acid gesture) |
| slide | 66 | 1.0 | 303 portamento glide into the next note |
| squelch | 90 | 0.50 | high-resonance attack — filter peak "wow" |
| staccato | 76 | 0.30 | tight gated 16ths — the sequence default |
| legato | 68 | 1.0 | sustained gate — pad-like held bass |
| octave_jump | 82 | 0.40 | octave-displacement riff — house/electro signature |
| ghost | 40 | 0.15 | closed-gate tick — rhythmic filler, no pitch |

## Synthesis Engine

**MonoSynth primary** (`sound/synthesis/mono_synth.py`) — the subtractive
VCO → 24 dB ladder → ADSR architecture IS the 303:

```python
SYNTHESIS_DEFAULTS = {
    "waveform": "pulse",        # the 303's oscillator is a pulse wave
    "pulse_width": 0.5,         # ~50% duty — the classic 303 setting
    "sub_level": 0.25,          # sub one octave down = low-end weight
    "filter_cutoff": 2400.0,    # brighter than SB1 1800 — the acid voice
                                # lives higher so the sweep is audible
    "filter_resonance": 0.85,   # HIGH — the squelch band; near
                                # self-oscillation (players run it hot)
    "filter_env_amount": 0.8,   # per-note filter re-open = the accent/wow
    "filter_keytrack": 0.4,
    "env_a": 0.004,             # near-instant attack (the gate click)
    "env_d": 0.22,
    "env_s": 0.70,
    "env_r": 0.10,              # quick release — tight, no wash
    "saturation": 0.18,         # gentle analog drive
    "drift_amount": 0.002,
}
```

- **PhaseModSynth secondary** (`sound/synthesis/phase_mod.py`) — FM acid
  "rubber 303": saw carrier, sine mod ratio 1.0, depth 2.8, attack 0.004 s.
- **Karplus-Strong tertiary** (`sound/synthesis/karplus_strong.py`) —
  loop_gain 0.9955 (snappier than SB1 0.9960 — the acid is punchy/tight),
  lowpass_hz 1800. Not the physical model (no string), usable fallback.
- **ModalSynth `'string'`** — weak fallback (no resonant filter character).

Smoke tests (E2 = MIDI 40):
```
MonoSynth E2 (resonance 0.85): peak=0.800 head_rms=0.6638 mid_rms=0.6059 tail_rms=0.5143
Squelch band (0.8-3 kHz) energy = 27.5% of audible   <-- the resonance peak is REAL
PhaseModSynth E2: peak=0.771
```
The head→mid→tail profile (0.664 → 0.606 → 0.514) shows the gate envelope:
sustain holds (no collapse), the tail drop is the 0.10 s release only —
exactly how a synth bass behaves (unlike a decaying acoustic string).

## Production Defaults

```python
REVERB_TAIL = 0.9        # DRIEST bass in the library — 303 is direct-inject,
                         # resonance IS the effect; verb smears 16ths
EQ_BODY = (220, -3.0)    # cut low-mid mud (bigger than SB1 −2.5 — resonance
                         # pushes more energy into this band vs the kick)
EQ_PRESENCE = (1100, 2.5)# boost the squelch band (~1 kHz filter peak when
                         # the env opens — the acid "growl")
EQ_AIR = (6500, 1.5)     # gentle air shelf — 303 has a natural top roll-off
PAN = 0.0                # center — bass is universally mono
```

## Registration Proof

`instrument_registry.py` additions:

```python
_INSTRUMENT_MODULES["Bass.synth_bass_2.synth_bass_2"] = "synth_bass_2"
SYNTH_BASS_2 = ALL_INSTRUMENTS["synth_bass_2"]
# registry_table() role row: elif low == "synth bass 2": bass, rhythm, groove, accent, lead
```

Registry verification run (`/opt/data/micromamba/envs/musicom/bin/python
instrument_registry.py`) — new row in the table (line 7):

```
| Family | Instrument | Program | Range | Role |
|---|---|---|---|---|
| Bass | Acoustic Bass | 32 | 24–72 | bass, rhythm, countermelody, accent, melody |
| Bass | Electric Bass (finger) | 33 | 24–84 | bass, rhythm, countermelody, accent |
| Bass | Fretless Bass | 35 | 24–72 | bass, melody, countermelody, groove, slide, color |
| Bass | Synth Bass 1 | 38 | 24–84 | bass, rhythm, groove, accent |
| Bass | Synth Bass 2 | 39 | 21–96 | bass, rhythm, groove, accent, lead |   <-- NEW

=== Synth Bass 2 (Acid/TB-303, GM39) ===
  SYNTH_BASS_2.midi_program = 39 (should be 39)
  by_name('synth bass 2') = <Instrument Synth Bass 2 (family=Bass, program=39, range=21-96)>
  by_name('SYNTH BASS 2') = <Instrument Synth Bass 2 (family=Bass, program=39, range=21-96)>
  by_program(39) = <Instrument Synth Bass 2 (family=Bass, program=39, range=21-96)>
  by_program(38) = <Instrument Synth Bass 1 (family=Bass, program=38, range=24-84)> (distinct: synth bass 1)
  SYNTH_BASS_2.in_sweet_spot(48) = True
  SYNTH_BASS_2.in_sweet_spot(20) = False
  SYNTH_BASS_2.range_min = 21 SYNTH_BASS_2.range_max = 96
  SYNTH_BASS_2.stem_label = 'Synth_Bass_2'
```

Full output: `_test/registry_out_synth_bass_2.txt`. Registry load count:
82 → **83**.

## Verification Results

Verify script: `_test/verify_synth_bass_2.py` (structural template
`_test/verify_acoustic_bass.py`; audio render = INSTRUMENT SOLO ONLY per the
2026-09-01 comb-filter rule — drums ride along for context but are excluded
from the solo render).

```
Registry: <Instrument Synth Bass 2 (family=Bass, program=39, range=21-96)>
Synth Bass 2: program=39 gm='Synth Bass 2' stem='Synth_Bass_2' sweet=(36, 55) A4=440.0Hz
Synth Bass 2: zones={'sub': (21, 35), 'groove': (36, 50), 'mid': (51, 62), 'high': (63, 96)}
Synth Bass 2: art=['accent', 'slide', 'squelch', 'staccato', 'legato', 'octave_jump', 'ghost'] synth=mono_synth modal_preset=string reverb=0.9s pan=0.0

Zero-drift: True (OK)
MIDI: /opt/data/projects/Instruments/_test/synth_bass_2_test.mid (190 bytes)
SoundFont: /opt/data/micromamba/envs/musicom/share/soundfonts/FluidR3_GM.sf2  (discover_soundfont())
WAV (solo): /opt/data/projects/Instruments/_test/synth_bass_2_test.wav (715308 bytes)
Spectral check: 4-8kHz buzz energy = 4.8% (OK, < 20% gate, no comb-filtering)

Stem label: GM_PROGRAMS[39] = 'Synth Bass 2'   (matches exactly, no quirk)
SF2 preset 39 -> 'Synth Bass 2'                (phdr-verified, matches)

Stems rendered (2 files):
  track00_Synth_Bass_2.wav (715308 bytes)
  track01_Drums.wav (706092 bytes)

MonoSynth E2 (resonance 0.85): peak=0.800 head_rms=0.6638 mid_rms=0.6059 tail_rms=0.5143
Squelch band (0.8-3 kHz) energy = 27.5% of audible
PhaseModSynth E2: peak=0.771
ALL CHECKS PASSED
```

## Stem-Label Quirks

**None.** `GM_PROGRAMS[39]` = "Synth Bass 2" (pipeline), FluidR3 preset 39 =
"Synth Bass 2" (phdr-verified), `STEM_LABEL = "Synth_Bass_2"` — all three
agree. Contrast with the known quirks elsewhere: GM74 Flute → "Recorder",
GM109 → "Bag pipe", GM111 → "Shanai".

## Writing Quirks (for composition jobs)

1. **Monophonic** — the TB-303 is a true monophonic instrument. Never ask
   for a 3-note "acid bass chord".
2. **The accent IS the performance** — velocity ≥ 95 for the offbeat
   squelch burst; keep the 16th-note sequence body at 72–82. The groove
   lives in the velocity contrast.
3. **SF2 honours no portamento** — write a 303 slide as pitch-bend or a
   fast chromatic run.
4. **No unison doubling** with another melodic patch on the same pitches
   (2026-09-01 comb-filter rule) — octaves or a low bass note an octave+
   below are fine, and a drum kit is fine.
5. **Spectral note**: the acid resonance lives in the 0.8–3 kHz squelch
   band (27.5% of the MonoSynth output's audible energy) — this is the
   instrument's identity, NOT the 4–8 kHz comb-filter buzz the gate looks
   for (solo render measured 4.8%). Don't EQ it out; boost EQ_PRESENCE
   (1100 Hz) instead.
6. Humanize DNA: family Bass (5.0 ms timing, 4.0 vel, 8.0 ms layback — the
   bass lays back, bass-family precedent) via `humanize_dna` "bass" branch.

## Files Written

- `Bass/synth_bass_2/instrument.md` — full research reference
- `Bass/synth_bass_2/synth_bass_2.py` — importable constants
- `instrument_registry.py` — module dict entry + `SYNTH_BASS_2` constant +
  registry_table role row + verification block (registry load count 82 → 83)
- `registry.md` — changelog entry (2026-09-02), Registry table row
- `README.md` — count refresh (83 registry / 77 folders)
- `_test/verify_synth_bass_2.py` — end-to-end verification (zero-drift,
  MIDI, solo WAV, spectral, stem label, SF2 phdr, stems on disk,
  MonoSynth + PhaseModSynth smoke)
- `_test/sweep_synth_bass_2.py` — FluidR3 pitch sweep
- `_test/registry_out_synth_bass_2.txt` — registry verification output
- `_test/verify_synth_bass_2_out.txt` — verify script output
