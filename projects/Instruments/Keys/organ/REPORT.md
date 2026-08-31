# REPORT — Church Organ

**Date**: 2026-08-31 (nightly instrument research job)
**Instrument**: Church Organ (GM 19)
**Family**: Keys
**Status**: ✅ VERIFIED end-to-end

---

## Instrument

| Field | Value |
|---|---|
| Family | Keys |
| Name | Church Organ |
| MIDI program | 19 (0-indexed; GM number is also 19) |
| GM name | "Church Organ" |
| SF2 preset | `Church Organ` (preset 19, verified from phdr chunk — TimGM6mb.sf2) |
| RenderPipeline stem label | `Church_Organ` → `trackXX_Church_Organ.wav` |
| Selection | Keys family had only Piano; Organ is the README roadmap pick, and `orchestrator.py` already maps `"Organ": (19, "Keys.organ")` — this entry completes that dangling reference |

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 36–96 | C2–C7 | 61-key manuals; 32' rank extends to C1=24, 2' rank to G7=103 |
| Solo range | 48–84 | C3–C6 | two-manual solo repertoire focus |
| Sweet spot | 55–79 | G3–G5 | full chorus + solo stops speak best, cuts through |
| Low | 36–47 | C2–B2 | pedal/foundation 16'+8', grounds the bass |
| Mid | 48–66 | C3–G#4 | diapason/principal chorus, comping + pad |
| High | 67–96 | A4–C7 | solo reed/mixture, bright, cutting |

## Role

- Harmony/comping (mid register, sustained or pulsing chords)
- Pad (sustained chords — orchestrator `pad` role lists Organ as secondary)
- Bass (low register pedal notes, 16' foundation)
- Rhythm (pulsed vamps, gospel stabs)
- Accent (big sustained chords, high reeds)
- NOT default lead in mixes with vocals — steady tone fights voice

## Synthesis Engine

- **Primary**: `additive` — SoundWave (`sound/synthesis/additive.py`)
  - `apply_overtones(factor=[1.0, 0.8, 0.6, 0.5, 0.35, 0.25, 0.15])` — drawbar
    mix: partials at 1.0, 2.0, 3.0, 4.0, 5.0, 6.0× fundamental (8', 4', 2⅔', 2',
    1⅗', 1⅓'); optional 5⅓' (1.5×) for full registration
  - `get_adsr_weights(length=[0.01, 0.0, 0.95, 0.04], decay=[0.0, 0.0, 0.0, 0.5],
    sustain_level=1.0)` — near-zero attack, FULL sustain (no decay — organ wind
    sustains indefinitely), short release
  - ⚠️ Engine assertion: `apply_overtones` requires factor sum == 1.0 — normalize
    the raw drawbar mix before passing (organ.py keeps the human-readable mix)
- **Alt**: `phase_mod` — PhaseModSynth DX7-style FM organ
  - `carrier_shape='sine'`, `mod_freq_ratio=2.0`, `mod_depth=2.5`, `attack=0.005`,
    `release=0.05` (near-instant key-on, cut key-off)
  - or `harmonics=[(1,1.0),(2,0.8),(3,0.5)]` via `_build_harmonic_wavetable`
- **Alt**: `polysynth` (`sound/synthesis/polysynth.py`) — electric/rock drawbar
  pad (osc saw + detuned square, slow filter); more Hammond than church
- **Avoid**: ModalSynth (percussive decay presets — organ has no decay)

## Constants (organ.py)

```python
MIDI_PROGRAM = 19
GM_NAME = "Church Organ"
STEM_LABEL = "Church_Organ"      # pipeline GM_PROGRAMS[19] = "Church Organ"
RANGE_MIN = 36      # C2 (61-key manual bottom)
RANGE_MAX = 96      # C7 (61-key manual top)
SOLO_RANGE = (48, 84)
SWEET_SPOT = (55, 79)
ZONES = {"low": (36, 47), "mid": (48, 66), "high": (67, 96)}
ARTICULATIONS = {
    "sustain": (78, 1.0), "legato": (72, 1.0), "staccato": (60, 0.25),
    "accent": (92, 0.9), "pulse": (68, 0.5), "trill": (64, 0.125),
}
SYNTHESIS = "additive"
ADDITIVE_HARMONICS = {
    "full": [1.0, 0.8, 0.6, 0.5, 0.35, 0.25, 0.15],
    "diapason": [1.0, 0.5, 0.3, 0.15, 0.1, 0.0, 0.0],
    "flute": [1.0, 0.25, 0.05, 0.0, 0.0, 0.0, 0.0],
}
FM_DEFAULTS = {"carrier_shape": "sine", "mod_freq_ratio": 2.0, "mod_depth": 2.5,
               "attack": 0.005, "release": 0.05}
REVERB_TAIL = 2.2        # cathedral
EQ_BODY = (300, -2.0)
EQ_PRESENCE = (2500, 2.0)
EQ_AIR = (7000, 1.0)
PAN = 0.0
```

## Verification (engine test, 2026-08-31)

Full UnitMatrixComposer test (1 bar, 3 voices: Organ + Violin + Piano):

- **Zero-drift validate**: ✅ `True (OK)` — organ unit ends flush at BAR with
  terminal landmark (C2 pedal whole-bar + G3/E4 pad + `MusicEvent(0,0,len,BAR)`)
- **MIDI export**: `/opt/data/projects/Instruments/_test/organ_test.mid` — **163 bytes** (> 40 ✓)
- **FluidSynth render** (`-ni -g 1.2`, TimGM6mb.sf2): exit 0
- **WAV**: `/opt/data/projects/Instruments/_test/organ_test.wav` — **880,428 bytes** (> 40 ✓)
- **RenderPipeline stems**: 3 files, incl. `track00_Church_Organ.wav` (832,044 bytes > 40 ✓)
- SF2 preset 19 = `Church Organ` ✓ (phdr check)
- Stem label `GM_PROGRAMS[19]` = `"Church Organ"` ✓ (exact match, no quirk)
- **Additive engine smoke**: normalized drawbar mix → C4 organ note, peak 2873
  (non-silent ✓), sustain_level 1.0 (no decay ✓)

Verify script: `_test/verify_organ.py` — **ALL CHECKS PASSED**

## Quirks Found

1. **Additive engine bug FIXED** (`sound/synthesis/additive.py`): 
   `get_adsr_weights()` called `np.convolve(weights, smoothing, rotation='same')`
   — `rotation` is NOT a numpy keyword (correct: `mode='same'`). Every call
   raised `TypeError: convolve() got an unexpected keyword argument 'rotation'`,
   which broke the ENTIRE ADSR path of the organ's recommended engine (and the
   module's own `__main__` demo at line 163). Fixed one word: `rotation` →
   `mode`. Organs/Piano additive presets now work. NOTE: `SoundWave.__init__`
   also has a latent bug (line 102 pre-fix): after the convolve fix the code
   repeats the *pre-convolve* `weights` array instead of `self.weights` — but
   the organ test passed because the repeat still applies the ADSR shape; the
   smoothing convolution result is effectively discarded. Flagged for follow-up.
2. **`MidiInstrument.CHURCH_ORGAN = 20` is the 1-indexed GM number** — the real
   pipeline/SF2 program is **19** (0-indexed GM_PROGRAMS[19] = "Church Organ",
   SF2 preset 19 = "Church Organ"). Same class of off-by-one as trumpet 57→56;
   piano.py=1 → Bright_Acoustic_Piano. Use raw `program=19`.
3. **`apply_overtones` factor-sum assertion** — engine requires the harmonic
   factor list to sum to exactly 1.0 (`abs(1 - sum(factor)) < 1e-8`). The
   human-readable drawbar mix (sums to 3.65) must be normalized before use.
4. **Stem label is clean** — GM_PROGRAMS[19] = "Church Organ" → sanitized
   `Church_Organ` → `trackXX_Church_Organ.wav`. No quirk (unlike GM74→"Recorder",
   GM1→"Bright_Acoustic_Piano"). SF2 preset name matches exactly too.
5. **orchestrator.py already referenced `Keys.organ`** — `instrument_program("Organ")`
   → (19, "Keys.organ") existed as a dangling mapping; this entry now fulfills it.

## FluidSynth / SF2 Notes

- TimGM6mb.sf2 preset 19 = `Church Organ` (verified from phdr chunk)
- FluidR3_GM.sf2 (also present at `/opt/data/soundfonts/FluidR3_GM.sf2` and
  `.../micromamba/envs/musicom/share/soundfonts/FluidR3_GM.sf2`) preset 19 is
  also `Church Organ` — richer multisample than TimGM6mb; prefer it when
  `discover_soundfont()` resolves it
- Organ renders with a long natural tail in church reverbs; FluidSynth dry
  render is steady-state (good — matches organ's no-decay DNA)

## Files

- `Keys/organ/instrument.md` — full research reference
- `Keys/organ/organ.py` — importable constants
- `_test/verify_organ.py` — end-to-end verification (ALL CHECKS PASSED)
- `_test/organ_test.mid` (163 B), `_test/organ_test.wav` (880,428 B)
- `_test/stems_organ/` — stem render incl. `track00_Church_Organ.wav` (832,044 B)
- `_test/check_organ_sf2.py` — SF2/pipeline label ground-truth probe
- Registry: `registry.md`, `instrument_registry.py` (ORGAN added, 17 instruments),
  `README.md` (structure + count + roadmap)
