# REPORT: Clean Electric Guitar (GM 27) — Added 2026-10-13

## Instrument identity

- **Program**: 27 (GM1 Electric Guitar clean)
- **GM name**: "Electric Guitar (clean)"
- **Pipeline label**: `GM_PROGRAMS[27] = "Electric Guitar (clean)"`
- **SF2 preset**: 27 = "Clean Guitar" (FluidR3_GM — cosmetic SF2 name, no routing)
- **Family**: Guitar (third member: nylon acoustic GM24, steel acoustic GM25, clean electric GM27)

## Constants

| Field | Value |
|---|---|
| MIDI_PROGRAM | 27 |
| GM_NAME | "Electric Guitar (clean)" |
| STEM_LABEL | "Electric_Guitar_clean" |
| RANGE_MIN | 28 (E1) |
| RANGE_MAX | 84 (C6) |
| SOLO_RANGE | (43, 76) |
| SWEET_SPOT | (52, 72) |
| SYNTHESIS | "karplus_strong" |
| KARPLUS_DEFAULTS | loop_gain=0.9960, excitation="pick", lowpass_hz=5000, noise=0.025 |
| MODAL_PRESET | "string" |
| REVERB_TAIL | 1.8 s |
| EQ_BODY | (300, -3.0) |
| EQ_PRESENCE | (3500, 2.5) |
| EQ_AIR | (8000, 1.5) |
| PAN | -0.2 |

## Registration proof

```
by_name('clean electric') -> <Instrument Electric Guitar (clean) (family=Guitar, program=27, range=28-84)>
by_program(27) -> <Instrument Electric Guitar (clean) (family=Guitar, program=27, range=28-84)>
CLEAN_ELECTRIC.midi_program = 27
CLEAN_ELECTRIC.in_sweet_spot(52) = True
CLEAN_ELECTRIC.in_sweet_spot(30) = False
```

### Registry table excerpt

```
| Guitar | Acoustic Guitar (nylon) | 24 | 40–84 | lead, harmony, accent |
| Guitar | Acoustic Guitar (steel) | 25 | 40–86 | harmony, rhythm, strum, lead, melody, ornament, countermelody |
| Guitar | Electric Guitar (clean) | 27 | 28–84 | harmony, rhythm, strum, lead, melody, ornament, countermelody, accent |
```

## Verification results

### Zero-drift
- `validate() = True (OK)` — one voice, one bar, terminal landmark at BAR=1920 ticks

### MIDI
- Path: `/opt/data/projects/Instruments/_test/clean_electric_test.mid`
- Size: **84 bytes** (> 40 ✅)

### WAV (FluidSynth solo render)
- SoundFont: FluidR3_GM.sf2 (auto-resolved via `discover_soundfont()`)
- Path: `/opt/data/projects/Instruments/_test/clean_electric_test.wav`
- Size: **812,332 bytes** (> 40 ✅)
- **Spectral check**: 4–8 kHz buzz = 1.0% (OK, < 20% gate)

### Stem render (RenderPipeline)
- 1 stem file: `track00_Electric_Guitar_clean.wav` (812,332 bytes)
- Stem label matches pipeline's sanitized GM_PROGRAMS[27] = "Electric Guitar (clean)"
  → `Electric_Guitar_clean` ✅

## Synthesis engine recommendation

### Primary: Karplus-Strong (sound/synthesis/karplus_strong.py)

Clean electric guitar IS a plucked stiff steel string with magnetic pickup.
The waveguide (loop_gain 0.9960) models the wound steel string precisely.

### Secondary: ModalSynth (sound/synthesis/modal.py)
Stock 'string' preset with impulse excitation.

### Tertiary: PhaseModSynth (sound/synthesis/phase_mod.py)
FM approximation (saw carrier, ratio 1.0, depth 2.0) for cheap emulation.

## Quirks found

**Stem label — no quirk.** `GM_PROGRAMS[27] = "Electric Guitar (clean)"` →
sanitized `Electric_Guitar_clean`. FluidR3 preset 27 = "Clean Guitar" (cosmetic
SF2 name difference only). Pipeline label and STEM_LABEL match ✅.

**Pickup bandpass**: The magnetic pickup acts as a bandpass filter (~80 Hz – 5 kHz).
The SF2 samples already encode this rolloff — no additional EQ needed in the
render chain for the synthetic samples.

**Palm-mute idiom**: The clean electric's most characteristic rhythm articulation
is palm-muting (GM velocity ~50, duration 0.12) — composition jobs writing clean
electric should use rhythmic chord stabs and strums, NOT long sustained notes
(the string decays naturally in 1–3 s).

**No channel quirk**: Standard melodic channel (0–9) with program 27. Channel 9
would trigger drum kit.

## Files created

| File | Path |
|---|---|
| instrument.md | `/opt/data/projects/Instruments/Guitar/clean_electric/instrument.md` |
| constants | `/opt/data/projects/Instruments/Guitar/clean_electric/clean_electric.py` |
| verification | `/opt/data/projects/Instruments/Guitar/clean_electric/verify_clean_electric.py` |

## Files modified

| File | Change |
|---|---|
| instrument_registry.py | Added `"Guitar.clean_electric.clean_electric": "clean_electric"` to `_INSTRUMENT_MODULES`, added `CLEAN_ELECTRIC` convenience constant, updated registry_table role |
| registry.md | Added "Clean Electric Guitar added" changelog entry |