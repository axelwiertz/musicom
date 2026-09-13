# Instruments — musicom lookup registry

Importable instrument constants for compositions. Each instrument folder has
`instrument.md` (full research reference) + `<name>.py` (constants).

**Orchestration layer**: `orchestrator.py` + `orchestration.md` — role→instrument
mapping, register allocation, section dynamics, velocity balance. Turns the
instrument KB into arrangement decisions. Verified end-to-end (2026-08-21).

**Verified end-to-end** (2026-08-20): violin+piano+drumkit composition through
UnitMatrixComposer → zero-drift validate ✓ → MIDI → FluidSynth WAV ✓.

**Viola added** (2026-08-23): GM41, full strings-family entry (instrument.md +
viola.py), verified end-to-end UnitMatrixComposer → zero-drift ✓ → MIDI →
FluidSynth WAV ✓; RenderPipeline stem label `trackXX_Viola.wav` ✓ (no quirk).

**Double Bass added** (2026-08-24): GM43, strings-family bass entry
(instrument.md + double_bass.py), verified end-to-end UnitMatrixComposer →
zero-drift ✓ → MIDI → FluidSynth WAV ✓; RenderPipeline stem label
`trackXX_Contrabass.wav` ✓ (label is "Contrabass", not "Double_Bass" — matches
pipeline GM_PROGRAMS[43] and SF2 preset name; no quirk).

**Clarinet added** (2026-08-25): GM71, woodwind-family entry
(instrument.md + clarinet.py), verified end-to-end UnitMatrixComposer →
zero-drift ✓ → MIDI → FluidSynth WAV ✓; RenderPipeline stem label
`trackXX_Clarinet.wav` ✓ (GM_PROGRAMS[71] = "Clarinet", SF2 preset 71 =
Clarinet; no quirk).

**French Horn added** (2026-08-26): GM60, brass-family entry
(instrument.md + french_horn.py), verified end-to-end UnitMatrixComposer →
zero-drift ✓ → MIDI → FluidSynth WAV ✓; RenderPipeline stem label
`trackXX_French_Horn.wav` ✓ (GM_PROGRAMS[60] = "French Horn"; SF2 preset 60
= "French Horns" plural — cosmetic label difference only, no routing impact).

**Tuba added** (2026-08-27): GM58, brass-family bass entry
(instrument.md + tuba.py), verified end-to-end UnitMatrixComposer →
zero-drift ✓ → MIDI → FluidSynth WAV ✓; RenderPipeline stem label
`trackXX_Tuba.wav` ✓ (GM_PROGRAMS[58] = "Tuba", SF2 preset 58 = "Tuba" —
labels match exactly, no quirk).

**Bassoon added** (2026-08-28): GM70, woodwind-family bass entry
(instrument.md + bassoon.py), verified end-to-end UnitMatrixComposer →
zero-drift ✓ → MIDI → FluidSynth WAV ✓; RenderPipeline stem label
`trackXX_Bassoon.wav` ✓ (GM_PROGRAMS[70] = "Bassoon", SF2 preset 70 =
"Bassoon" — labels match exactly, no quirk).

**Oboe added** (2026-08-29): GM68, woodwind-family double-reed entry
(instrument.md + oboe.py), verified end-to-end UnitMatrixComposer →
zero-drift ✓ → MIDI → FluidSynth WAV ✓; RenderPipeline stem label
`trackXX_Oboe.wav` ✓ (GM_PROGRAMS[68] = "Oboe"; SF2 preset 68 = "Oboe (Orch)"
— cosmetic suffix only, no routing impact).

**Saxophone added** (2026-08-30): GM65, woodwind-family single-reed entry
(instrument.md + saxophone.py), verified end-to-end UnitMatrixComposer →
zero-drift ✓ → MIDI → FluidSynth WAV ✓; RenderPipeline stem label
`trackXX_Alto_Sax.wav` ✓ (GM_PROGRAMS[65] = "Alto Sax" — labeled "Alto_Sax",
NOT "Saxophone"; SF2 preset 65 = "AltoSax (TB) v2.3" — cosmetic suffix only,
no routing impact).

**Organ added** (2026-08-31): GM19, keys-family second entry
(instrument.md + organ.py), verified end-to-end UnitMatrixComposer →
zero-drift ✓ → MIDI → FluidSynth WAV ✓; RenderPipeline stem label
`trackXX_Church_Organ.wav` ✓ (GM_PROGRAMS[19] = "Church Organ", SF2 preset 19
= "Church Organ" — labels match exactly, no quirk). Additive engine bug
FIXED: `get_adsr_weights` used invalid `np.convolve(rotation='same')` →
`mode='same'` (broke the organ's recommended engine path).

**Marimba added** (2026-09-01): GM12, percussion-family melodic entry
(instrument.md + marimba.py), verified end-to-end UnitMatrixComposer →
zero-drift ✓ → MIDI → FluidSynth WAV ✓; RenderPipeline stem label
`trackXX_Marimba.wav` ✓ (GM_PROGRAMS[12] = "Marimba", SF2 preset 12 =
"Marimba" — labels match exactly, no quirk). ModalSynth dedicated
`'marimba'` preset confirmed (fast exponential decay, impulse excitation).
Note: `instrument_registry._load_all` previously overwrote ALL percussion
GM_NAMEs with "Drum Kit" — fixed to only override drum_kit.

**Sitar added** (2026-09-02): GM104, new **World** family entry
(instrument.md + sitar.py), verified end-to-end UnitMatrixComposer →
zero-drift ✓ → MIDI → FluidSynth WAV ✓; RenderPipeline stem label
`trackXX_Sitar.wav` ✓ (GM_PROGRAMS[104] = "Sitar", FluidR3 preset 104 =
"Sitar" — labels match exactly, no quirk). Karplus-Strong recommended
(plucked waveguide, high loop_gain 0.9975 → long jivari ring confirmed vs
dull 0.990 control: 3.3× tail energy). Registry `_FIELDS` extended with
`karplus_defaults` so synth-engine presets load through the registry.

**Koto added** (2026-09-02): GM107, World-family second entry
(instrument.md + koto.py), verified end-to-end UnitMatrixComposer →
zero-drift ✓ → MIDI → FluidSynth WAV ✓; RenderPipeline stem label
`trackXX_Koto.wav` ✓ (GM_PROGRAMS[107] = "Koto", FluidR3 preset 107 =
"Koto" — labels match exactly, no quirk). Karplus-Strong recommended
(plucked waveguide, loop_gain 0.9970 → long koto ring between guitar and
sitar; ~2× tail energy vs 0.990 dull control confirmed). Hirajoshi tuning
quirk: koto is NOT chromatic — composition jobs write in-scale pentatonic
lines, not dense harmony.

**Shamisen added** (2026-09-04): GM106, World-family third entry
(instrument.md + shamisen.py), verified end-to-end UnitMatrixComposer →
zero-drift ✓ → MIDI → FluidSynth WAV ✓; RenderPipeline stem label
`trackXX_Shamisen.wav` ✓ (GM_PROGRAMS[106] = "Shamisen", FluidR3 preset
106 = "Shamisen" — labels match exactly, no quirk). Karplus-Strong
recommended (plucked waveguide, loop_gain 0.9955 → punchy dry ring between
guitar and koto; ring advantage vs 0.990 dull control confirmed). Empirical
FluidR3 pitch sweep (RMS, notes 24–96): preset 106 audible across the whole
span, no gaps — SF2 never clips a composition. Line-instrument quirk:
shamisen is a monophonic bachi line voice (folk/theatre), not a harmony
voice — no dense chords.

**Kalimba added** (2026-09-05): GM108, World-family fourth entry
(instrument.md + kalimba.py), verified end-to-end UnitMatrixComposer →
zero-drift ✓ → MIDI → FluidSynth WAV ✓; RenderPipeline stem label
`trackXX_Kalimba.wav` ✓ (GM_PROGRAMS[108] = "Kalimba", FluidR3 preset 108 =
"Kalimba" — labels match exactly, no quirk). Karplus-Strong recommended
(plucked waveguide, loop_gain 0.9940 — metal tine ring clearly above the
0.990 dull control: 0.014 vs 0.008 tail ratio at 0.2–0.6 s, 1.7×, and SHORTER
than sitar 0.023 — metal tines decay faster than sympathetic strings).
ModalSynth 'bell' preset (inharmonic metal-bar modes) is the fallback.
Solo-render spectral check: 4–8 kHz buzz 4.3% (no comb-filtering).
Measurement note: the kalimba ring is short — verify with the 0.2–0.6 s
window, NOT the 1–2 s window used for sitar/koto (both readings sit at the
noise floor there).

**Banjo added** (2026-09-06): GM105, World-family fifth entry
(instrument.md + banjo.py), verified end-to-end UnitMatrixComposer →
zero-drift ✓ → MIDI → FluidSynth WAV ✓; RenderPipeline stem label
`trackXX_Banjo.wav` ✓ (GM_PROGRAMS[105] = "Banjo", FluidR3 preset 105 =
"Banjo" — labels match exactly, no quirk). Karplus-Strong recommended
(plucked waveguide, loop_gain 0.9960 — head-snap ring clearly above the
0.990 dull control: 0.019 vs 0.008 tail ratio at 0.2–0.6 s, 2.4×, and SHORTER
than sitar 0.023 — taut head decays faster than sympathetic strings).
ModalSynth 'string' preset is the fallback. Solo-render spectral check:
4–8 kHz buzz 5.4% (no comb-filtering). Empirical FluidR3 pitch sweep
(RMS, notes 24–96): preset 105 audible across the whole span, no gaps — SF2
never clips a composition. Line/rhythm-instrument quirk: banjo is a
roll/strum voice (Scruggs T-I-M-T-M-I-T-M + clawhammer), not a harmony
voice — no dense chords.

**Dulcimer added** (2026-09-07): GM15, Keys-family third entry
(instrument.md + dulcimer.py), verified end-to-end UnitMatrixComposer →
zero-drift ✓ → MIDI → FluidSynth WAV ✓; RenderPipeline stem label
`trackXX_Dulcimer.wav` ✓ (GM_PROGRAMS[15] = "Dulcimer", FluidR3 preset 15 =
"Dulcimer" — labels match exactly, no quirk). Identity note: GM15 "Dulcimer"
is the **hammered** dulcimer (cimbalom/santur/yangqin struck-string zither),
NOT the Appalachian lap dulcimer. ModalSynth recommended (impulse-excited
resonator bank; 'string' preset + custom struck-string modes with
fast-decaying harmonic partials). Karplus-Strong alt (loop_gain 0.9975 →
bright ring 0.023 vs 0.008 dull control, 2.9×). Solo-render spectral check:
4–8 kHz buzz 4.1% (no comb-filtering). Chordal voice OK (folk styles play
2–4 note rolled chords); NOT a bass voice.

**Bagpipe added** (2026-09-08): GM109, Woodwind-family sixth entry
(instrument.md + bagpipe.py), verified end-to-end UnitMatrixComposer →
zero-drift ✓ → MIDI → FluidSynth WAV ✓; RenderPipeline stem label
`trackXX_Bag_pipe.wav` ✗ **QUIRK**: GM_PROGRAMS[109] = "Bag pipe" (two
words) — the actual stem label is `Bag_pipe`, NOT `Bagpipe`; STEM_LABEL
matches the pipeline's real label ("Bag_pipe") so stem-file lookups work.
FluidR3 preset 109 = "BagPipe" (cosmetic only). PhaseModSynth recommended
(sustained double-reed chanter: saw carrier, mod_depth 4.5 — highest of the
woodwind set — for the piercing reed wall; attack 0.03 s = reeds already
blown by bag pressure, no breath transient; sustain confirmed 0.464
late-window ratio, no collapse). Identity: GM109 = Great Highland Bagpipe —
monophonic 9-note chanter (A3–A4, mixolydian on D) over a constant drone;
line-instrument quirk: modal melody over a pedal, NO dense harmony. Range
53–96 is the GM-patch span (empirical FluidR3 sweep 8/8 notes audible);
real chanter register is 57–69.

**Steel Drums added** (2026-09-09): GM114, Percussion-family third entry
(instrument.md + steel_drums.py), verified end-to-end UnitMatrixComposer →
zero-drift ✓ → MIDI → FluidSynth WAV ✓; RenderPipeline stem label
`trackXX_Steel_Drums.wav` ✓ (GM_PROGRAMS[114] = "Steel Drums", FluidR3
preset 114 = "Steel Drums" — labels match exactly, no quirk). Identity:
GM114 = Trinidadian steelpan (pan) family — lead/tenor pan chromatic
melodic instrument; line + harmony voice (2–4 note chords idiomatic), NOT a
bass voice. ModalSynth recommended (impulse-excited struck-membrane bank;
'pan' custom modes f0, 2.0×, 2.7×, 3.6× with decays 12–28 — see PAN_MODES;
MODAL_PRESET 'marimba' is the closest stock bank, 'bell' the metallic alt).
Karplus-Strong fallback loop_gain 0.9950 (metallic ping 0.016 vs 0.008 dull
control, 2.0×, between kalimba 0.9940 and banjo 0.9960). Solo-render
spectral check: 4–8 kHz buzz 0.6% (no comb-filtering). Empirical FluidR3
pitch sweep (RMS, notes 24–96): preset 114 audible across the whole span,
no gaps — SF2 never clips a composition. Range 55–96 is the lead-pan
register (sweep proves the patch plays the full GM span).

**Shenai added** (2026-09-10): GM111, World-family sixth entry
(instrument.md + shenai.py), verified end-to-end UnitMatrixComposer →
zero-drift ✓ → MIDI → FluidSynth WAV ✓; RenderPipeline stem label
`trackXX_Shanai.wav` ✗ **QUIRK**: GM_PROGRAMS[111] = "Shanai" (GM2 spec
spelling) — the stem label is `Shanai`, NOT `Shenai`; the instrument is the
North Indian shehnai (also "shenai"), and FluidR3 preset 111 = "Shenai"
(cosmetic only). STEM_LABEL matches the pipeline's real label ("Shanai") so
stem-file lookups work. PhaseModSynth recommended (continuous-tone double
reed: saw carrier, mod_freq_ratio 1.5, mod_depth 3.2 — between oboe 2.5 and
bagpipe 4.5; attack 0.06 = real reed transient, sustain confirmed 0.400
late-window ratio, no collapse). Identity: GM111 = shehnai — monophonic
continuous raga line over a tanpura-style Sa-Pa drone; line-instrument quirk:
modal melody over a pedal, NO dense harmony. Range 55–96 is the GM-patch span
(empirical FluidR3 sweep 8/8 notes audible); real shehnai register is 62–84
(D4–C6). Solo-render spectral check: 4–8 kHz buzz 1.3% (no comb-filtering).

**Fiddle added** (2026-09-11): GM110, World-family seventh entry — the
folk-fiddle double of the classical violin (same GDAE tuning/dimensions,
different idiom: flat vibrato, aggressive bow drive, rosin noise).
instrument.md + fiddle.py), verified end-to-end UnitMatrixComposer →
zero-drift ✓ → MIDI → FluidSynth WAV ✓; RenderPipeline stem label
`trackXX_Fiddle.wav` ✓ (GM_PROGRAMS[110] = "Fiddle", FluidR3 preset 110 =
"Fiddle" — labels match exactly, no quirk — distinct from the "Shanai"
quirk at 111). BowedString recommended (friction waveguide, bow_velocity
0.24 > concert-violin 0.2 for folk drive, bow_force 1.8, noise 0.025
rosin; sustain confirmed 0.572 late-window ratio, no collapse). ModalSynth
'string' preset = pizzicato fallback. Solo-render spectral check: 4–8 kHz
buzz 2.9% (no comb-filtering). Empirical FluidR3 pitch sweep (RMS, notes
55–96): preset 110 audible 8/8, no gaps — SF2 never clips a composition.
Line-instrument quirk: fiddle is a monophonic bow line (double-stops with
open-string drones allowed), NOT a harmony voice — no dense chords.

**Timpani added** (2026-09-12): GM47, Percussion-family fourth entry — the
pitched kettledrums (pedal-tuned copper-bowl membrane drums, felt sticks);
the instrument `orchestration.md` and `orchestrator.py` already referenced
as the Accent role's secondary voice with no KB entry behind it
(instrument.md + timpani.py), verified end-to-end UnitMatrixComposer → zero-drift ✓ → MIDI
→ FluidSynth WAV ✓; RenderPipeline stem label `trackXX_Timpani.wav` ✓
(GM_PROGRAMS[47] = "Timpani" = FluidR3 preset 47 — labels match exactly, no
quirk). ModalSynth recommended (impulse-excited resonator bank) with a custom
`TIMPANI_MODES` bank built on the ideal circular-membrane Bessel ratios
1 : 1.594 : 2.136 : 2.296 : 2.653 — the first KB instrument with an INHARMONIC
partial set rather than a harmonic series — with LOW decay rates 0.9–3.0
(marimba uses 8–20; the `decay` arg is a rate, so timpani need the opposite
end): late(1.0–1.5 s) rms/peak 0.134 and 1.59× partial band energy 23.7%,
vs the marimba preset's 0.0001 (~1000× longer ring). MODAL_PRESET 'drum' is
the closest stock bank but decays far too fast (damped/covered character
only); DrumSynth606 `tom` (DRUM606_DEFAULTS freq 110, decay 0.9, sweep 1.35)
covers the strike thump; Karplus-Strong is EXPLICITLY REJECTED — there is no
string, and a KS loop's harmonic series is the wrong partial structure (first
instrument in the KB where KS is rejected rather than demoted). Solo-render
spectral check: 4–8 kHz buzz 0.3% (no comb-filtering — lowest of the set).
Empirical FluidR3 pitch sweep (RMS, notes 24–84): preset 47 audible 15/15, no
gaps — SF2 never clips a composition. Registry `_FIELDS` extended with
`drum606_defaults`. Range 36–65 = C2 (32-inch drum) to F4 (piccolo-timpano
ceiling; Milhaud asks F#4=66); real four-drum set is D2–A3 (38–57), each drum
covering about a perfect fifth. Pitched-instrument quirk: MUST use a melodic
channel (0–9) with program 47 — channel 9 would trigger the drum-kit map and
the `Acoustic_Grand_Piano` program-0 fallback label. Muffling is inherent
playing (the head out-rings the written note); REVERB_TAIL 2.2 s is the
longest in the instrument set.

**Vibraphone added** (2026-09-13): GM11, Percussion-family fifth entry — the
struck-aluminium-bar metallophone with resonator tubes, a piano-style sustain
pedal and the motor tremolo (instrument.md + vibraphone.py), verified
end-to-end UnitMatrixComposer → zero-drift ✓ → MIDI → FluidSynth WAV ✓;
RenderPipeline stem label `trackXX_Vibraphone.wav` ✓ (GM_PROGRAMS[11] =
"Vibraphone" + FluidR3 preset 11 = "Vibraphone" — labels match exactly, no
quirk). ModalSynth recommended with a custom `VIBRAPHONE_MODES` bank at the
arch-tuned ratios **1 : 4 : 10** (fundamental, 2 octaves, octave+major 3rd)
and LOW decay rates 0.30/0.60/1.10: late(1.0–1.5 s) rms/peak **0.445** vs the
marimba preset's 0.0001 — a ~4400× longer ring, the inverse of the timpani
case (which used the same ModalSynth `decay`-as-rate argument at the opposite
extreme). Fundamental dominance confirmed (4× partial 13.0% and 10× 4.1% of
f0). MOTOR_DEFAULTS (rate 5.0 Hz, depth 0.35) define the namesake amplitude
tremolo — measured AM peak at the motor rate = 0.670 of the nearby envelope
max. Identity: GM11 = vibraphone (vibraharp) — mellow arch-tuned aluminium
bars, NON-transposing, second-most-popular solo keyboard-percussion after the
marimba; line + harmony voice (four-mallet pianistic comping), NOT a bass
voice. Range 48–89 = 4-octave models from C3 to the standard F6 top; the
standard 3-octave instrument is F3–F6 (53–89). Solo-render spectral check:
4–8 kHz buzz 0.8% (no comb-filtering). Empirical FluidR3 pitch sweep (RMS,
notes 36–96): preset 11 audible 13/13, no gaps — SF2 never clips a
composition. Karplus-Strong demoted to fallback (the bar is struck, not
plucked; loop_gain 0.9975 approximates the multi-second ring only).

## Python usage

```python
# From anywhere (Instruments is under projects/)
import sys
sys.path.insert(0, "/opt/data/projects/Instruments")
from Strings.violin.violin import MIDI_PROGRAM, SWEET_SPOT
from Keys.piano.piano import midi_to_freq
from Percussion.drum_kit.drum_kit import KIT, beat_pattern

# In UnitMatrixComposer
composer.add_voice("Violin", program=MIDI_PROGRAM, channel=0)
```

Zero-drift pitfall: drum units MUST end with a terminal landmark
(`MusicEvent(0,0,len_ticks,BAR)`) or validate() fails — see `_test/`.

## Registry

| Family | Instrument | Program | Range | Role |
|---|---|---|---|---|
| Strings | Violin | 40 | 55–103 | lead, counter, accent |
| Strings | Viola | 41 | 48–91 | harmony, counter, lead, accent |
| Strings | Cello | 42 | 36–84 | bass, lead, counter, harmony |
| Strings | Double Bass | 43 | 28–74 | bass, rhythm, accent, harmony |
| Keys | Piano | 1 | 21–108 | harmony, melody, bass, rhythm |
| Keys | Church Organ | 19 | 36–96 | harmony, pad, bass, rhythm, accent |
| Keys | Dulcimer | 15 | 48–96 | lead, melody, ornament, rhythm, harmony |
| Brass | Trumpet | 56 | 54–86 | lead, accent, fanfare |
| Brass | Trombone | 57 | 40–78 | bass, counter, accent, harmony |
| Brass | French Horn | 60 | 41–84 | harmony, counter, accent, lead |
| Brass | Tuba | 58 | 26–72 | bass, harmony, accent, rhythm |
| Woodwind | Flute | 74 | 60–96 | lead, counter, ornament |
| Woodwind | Oboe | 68 | 52–92 | lead, counter, harmony, accent |
| Woodwind | Clarinet | 71 | 52–96 | lead, counter, harmony, accent |
| Woodwind | Alto Saxophone | 65 | 49–88 | lead, counter, accent, harmony |
| Woodwind | Bassoon | 70 | 34–88 | bass, harmony, counter, lead |
| Guitar | Acoustic | 25 | 40–84 | harmony, rhythm, strum |
| Percussion | Drum Kit | ch9 | 35–81 | rhythm, groove, accent |
| Percussion | Marimba | 12 | 45–96 | lead, melody, accent, countermelody, harmony |
| Percussion | Steel Drums | 114 | 55–96 | lead, melody, accent, countermelody, harmony, rhythm |
| Percussion | Timpani | 47 | 36–65 | accent, rhythm, bass, drone |
| Percussion | Vibraphone | 11 | 48–89 | lead, melody, harmony, countermelody, accent |
| World | Sitar | 104 | 55–96 | lead, melody, ornament, drone |
| World | Banjo | 105 | 46–93 | lead, melody, ornament, rhythm, accent |
| World | Koto | 107 | 51–90 | lead, melody, ornament, drone, harmony |
| World | Shamisen | 106 | 45–89 | lead, melody, ornament, drone, countermelody |
| World | Kalimba | 108 | 48–96 | lead, melody, ornament, drone, harmony |
| World | Shenai | 111 | 55–96 | lead, melody, ornament, drone, accent |
| World | Fiddle | 110 | 55–96 | lead, melody, ornament, countermelody, accent |
| Woodwind | Bagpipe | 109 | 53–96 | lead, melody, ornament, drone, accent |

## Stem label quirks (RenderPipeline)

GM_PROGRAMS list is **0-indexed** (index N = GM program N). Verified 2026-08-22 against pipeline source + TimGM6mb.sf2 phdr.

| Program | Expected label | Actual label |
|---|---|---|
| 40 | Violin | Violin ✓ |
| 41 | Viola | Viola ✓ |
| 42 | Cello | Cello ✓ |
| 43 | Contrabass | Contrabass ✓ (labeled "Contrabass", not "Double_Bass") |
| 1 | Acoustic Grand Piano | **Bright_Acoustic_Piano** ✗ (list[1]) |
| 56 | Trumpet (correct GM) | Trumpet ✓ |
| 57 | Trombone | Trombone ✓ |
| 58 | Tuba | Tuba ✓ |
| 60 | French Horn | French Horn ✓ (SF2 preset is "French Horns" plural — cosmetic) |
| 70 | Bassoon | Bassoon ✓ |
| 68 | Oboe | Oboe ✓ (SF2 preset is "Oboe (Orch)" — cosmetic suffix only) |
| 65 | Alto Sax (correct GM) | **Alto_Sax** (labeled "Alto Sax", not "Saxophone") |
| 74 | Flute | **Recorder** ✗ |
| 15 | Dulcimer | Dulcimer ✓ (GM_PROGRAMS[15] + FluidR3 preset 15 both "Dulcimer") |
| 19 | Church Organ | Church Organ ✓ (GM_PROGRAMS[19] + SF2 preset 19 both "Church Organ") |
| 25 | Acoustic Guitar (nylon) | Acoustic_Guitar_nylon ✓ |
| 12 | Marimba | Marimba ✓ |
| 47 | Timpani | Timpani ✓ (GM_PROGRAMS[47] + FluidR3 preset 47 both "Timpani") |
| 11 | Vibraphone | Vibraphone ✓ (GM_PROGRAMS[11] + FluidR3 preset 11 both "Vibraphone") |
| 104 | Sitar | Sitar ✓ (GM_PROGRAMS[104] + FluidR3 preset 104 both "Sitar") |
| 105 | Banjo | Banjo ✓ (GM_PROGRAMS[105] + FluidR3 preset 105 both "Banjo") |
| 107 | Koto | Koto ✓ (GM_PROGRAMS[107] + FluidR3 preset 107 both "Koto") |
| 106 | Shamisen | Shamisen ✓ (GM_PROGRAMS[106] + FluidR3 preset 106 both "Shamisen") |
| 108 | Kalimba | Kalimba ✓ (GM_PROGRAMS[108] + FluidR3 preset 108 both "Kalimba") |
| 109 | Bagpipe | **Bag_pipe** ✗ (GM_PROGRAMS[109] = "Bag pipe" — two words; FluidR3 preset 109 = "BagPipe") |
| 111 | Shanai | **Shanai** ✗ (GM_PROGRAMS[111] = "Shanai" — GM2 spec spelling; instrument = Shenai, FluidR3 preset 111 = "Shenai") |
| 110 | Fiddle | Fiddle ✓ (GM_PROGRAMS[110] + FluidR3 preset 110 both "Fiddle") |
| 114 | Steel Drums | Steel Drums ✓ (GM_PROGRAMS[114] + FluidR3 preset 114 both "Steel Drums") |
| ch9/pgm0 | Drums | **Acoustic_Grand_Piano** ✗ (program-0 fallback) |

> **Known off-by-one in existing entries**: ~~`trumpet.py` uses 57~~ **FIXED 2026-08-27**: trumpet is now 56 (SF2 preset 56=`SoloTrumpet`). `piano.py`=1 → actually Bright Acoustic Piano (GM #2) — cosmetic label difference only, no routing impact. Legacy registry rows kept as-is for piano; new instruments use 0-indexed programs matching pipeline+SF2.

Match production code on ACTUAL labels, not intended names.
