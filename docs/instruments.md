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

**Harp added** (2026-09-14): GM46, Strings-family fifth entry — the only
plucked member of the classical strings block (47-string double-action
pedal harp; instrument.md + harp.py), verified end-to-end UnitMatrixComposer →
zero-drift ✓ → MIDI → FluidSynth WAV ✓; RenderPipeline stem label
`trackXX_Orchestral_Harp.wav` ✓ (GM_PROGRAMS[46] = "Orchestral Harp",
FluidR3 preset 46 = "Harp" — one-word SF2 spelling, cosmetic only, no
routing impact). Karplus-Strong recommended (plucked waveguide, loop_gain
0.9985 — HIGHEST of the plucked set, above sitar 0.9975: tail ratio
0.0083 vs 0.0050 sitar-class and 0.0013 dull control at the 1–2 s window;
harp strings are the longest and least-damped in the KB — no dampers
exist, the harpist damps by hand). ModalSynth 'string' preset is the
fallback; HARP_MODES custom bank (near-harmonic 1:2:3:4:5 stack, decay
rates 0.22–1.20) measured late(1.0–1.5 s) rms/peak 0.497 vs the marimba
preset's 0.0001 — second-longest modal ring after vibraphone 0.445.
Range 24–103 = C1–G7, the full 47-string concert grand (widest range in
the KB after the piano). Solo-render spectral check: 4–8 kHz buzz 2.4%
(no comb-filtering). Empirical FluidR3 pitch sweep (RMS, notes 12–108):
preset 46 audible 12/12, no gaps — BUT smooth treble rolloff, no cliff:
bass strings ~0.024 rms, top octave (≥ 84) ~0.0024–0.0037 (≈10× quieter,
like real nylon trebles); use higher velocities/doubled octaves for
melody above C6. Identity: GM46 = orchestral pedal harp — diatonic per
pedal setting (7 double-action pedals retune one pitch class across all
47 strings), no dampers, glissando + arpeggio are the idiomatic texture;
line + arpeggio/harmony voice (4 notes per hand, 8 simultaneous), NOT a
bass voice (wire strings muddy fast in a mix) and NOT a rhythmic strum
voice.

**Xylophone added** (2026-09-15): GM13, Percussion-family sixth entry — the
orchestral rosewood-bar xylophone, the bright dry ancestor of the marimba
(1 octave up, arch-cut bars, ~0.4 s ring) (instrument.md + xylophone.py),
verified end-to-end UnitMatrixComposer → zero-drift ✓ → MIDI → FluidSynth
WAV ✓; RenderPipeline stem label `trackXX_Xylophone.wav` ✓ (GM_PROGRAMS[13]
= "Xylophone", FluidR3 preset 13 = "Xylophone" — labels match exactly, no
quirk). ModalSynth recommended with a custom `XYLOPHONE_MODES` bank at the
rosewood arch ratios **1 : 3 : 6** (fundamental, octave+fifth 12th,
compressed near-3-octave 17th — the octave partial is DISCARDED by the arch
cut, unlike the marimba's harmonic 1:2:3 stack) and decay rates 9/14/20:
late(1.0–1.5 s) rms/peak **0.0000** vs the marimba preset's 0.0001 — a DRY
bar (the first KB instrument whose modal bank measures BELOW the marimba
preset; ring advantage is irrelevant, dryness IS the identity). Decay
confirmed across 0.1–0.4 s (rms ratio 0.162) and fundamental dominance
confirmed (3× partial 27.3%, 6× 9.1% of f0). Karplus-Strong demoted to
fallback (bar is struck, not plucked; loop_gain 0.9935 → tail ratio 0.0145
vs 0.0093 dull control at the 0.2–0.5 s window, only 1.56× — xylophone is
the SHORTEST ring of the struck/plucked set, ordering check confirmed
xylophone 0.0145 < kalimba 0.0155 < banjo 0.0202; measure short-ring
instruments in the 0.2–0.5 s window, NOT 1–2 s). SOLO-render spectral check:
4–8 kHz buzz 0.4% (no comb-filtering). Empirical FluidR3 pitch sweep (RMS,
notes 53–89): preset 13 audible 10/10, no gaps — SF2 never clips a
composition. Identity: GM13 = orchestral concert xylophone (4 octaves,
F3–F6), NOT the toy glockenspiel (steel bars, GM9); line + accent voice
(double-stops OK), NOT a bass voice and NOT a chord-sustain pad — rolls are
the only sustain. Registry `_FIELDS` extended with `xylophone_modes`.

**Taiko added** (2026-09-16): GM116, World-family eighth entry — the Japanese
kumi-daiko festival drum (tacked cowhide head on a hollowed keyaki-log
shell, thick cedar bachi; the ceremonial accent voice that pairs with the
KB's koto/shamisen/shenai) (instrument.md + taiko.py), verified end-to-end
UnitMatrixComposer → zero-drift ✓ → MIDI → FluidSynth WAV ✓; RenderPipeline
stem label `trackXX_Taiko_Drum.wav` ✓ (GM_PROGRAMS[116] = "Taiko Drum",
FluidR3 preset 116 = "Taiko Drum" — labels match exactly, no quirk).
ModalSynth recommended with a custom `TAIKO_MODES` bank: the tuned (0,1)
head mode (110 Hz at the A2 reference) coupled to inharmonic Bessel
partners (1.6×/2.13×/2.64× — the timpani family) AND a low hollowed-shell
mode at ~90 Hz, the chest thump that IS the taiko's identity; measured
shell band 60–110 Hz = 40.7% of total energy (head band 21.9%, 1.6× partner
11.8%), and late(1.0–1.5 s) rms/peak 0.019 vs the timpani bank's 0.134 —
the taiko rings ~7× shorter than a timpano (tacked hide + dense body kill
energy fast; decay rates 2.6–6.0 sit between timpani 0.9–3.0 and marimba
8–20). DrumSynth606 `tom` (DRUM606_DEFAULTS freq 80, decay 1.4, sweep
1.45) covers the strike thump; Karplus-Strong is EXPLICITLY REJECTED (no
string — the timpani precedent). Solo-render spectral check: 4–8 kHz buzz
4.4% (no comb-filtering). Empirical FluidR3 pitch sweep (RMS, notes 36–67):
preset 116 audible 8/8, no gaps — SF2 never clips a composition. Range
36–67 is the melodic-taiko patch span (real ō-daiko fundamental ~60–80 Hz =
B1–E2; the composition core is E2–G3 = the chū-daiko festival zone).
Identity: GM116 is a TUNED drum (pitch follows the note, like a timpano
without the pedal) but the IDIOM is rhythm + accent, not melody — kuchi-
shoga strokes (DON/DOKO/KA/SU) land the ensemble on the 1; distinct from
GM117 Melodic Tom (higher, tom-tuned for melodic fills). Line/rhythm
quirk: accent/rhythm/drone voice over koto/shamisen lines, NOT a melodic
lead and NOT a bass melodic voice. Channel quirk: melodic channel (0–9)
with program 116 — channel 9 would trigger the drum-kit map and the
`Acoustic_Grand_Piano` program-0 fallback label (timpani lesson).

**Harpsichord added** (2026-09-17): GM6, Keys-family fourth entry — the
quill-plucked Baroque keyboard (one jack, one pluck, per key; the ONLY
plucked member of the Keys family) (instrument.md + harpsichord.py),
verified end-to-end UnitMatrixComposer → zero-drift ✓ → MIDI (144 bytes) →
FluidSynth WAV (761 KB) ✓; RenderPipeline stem label
`trackXX_Harpsichord.wav` ✓ (GM_PROGRAMS[6] = "Harpsichord", FluidR3
preset 6 = "Harpsichord" — labels match exactly, no quirk).
Karplus-Strong recommended (quill-plucked waveguide = the exact physical
model; loop_gain 0.9980 — between harp 0.9985 and sitar 0.9975: tail
ratio 0.0063 vs harp 0.0083 and sitar 0.0050 at the 1–2 s window, dull
control 0.0013 — ring ordering harp > harpsichord > sitar CONFIRMED:
strings ring 2–5 s while the key holds, then the cloth damper stops them
clean on release). ModalSynth 'string' preset is the fallback; custom
`HARPSICHORD_MODES` bank models the 8'+4' registration — a near-harmonic
stack with an explicit octave DOUBLE (4' choir at 0.55 amp stacked with
the 0.45 octave partial = octave band 1.00 vs fundamental 1.00), decay
rates 0.35–0.90; measured late(1.0–1.5 s) rms/peak 0.345 vs the marimba
preset's 0.0001. KS spectral check on the solo render confirms the
signature: 2nd partial **107.8% of f0** (the 4' octave double is the
loudest partial — no other KB instrument has this), 3rd 86.0%. Solo
spectral gate: 4–8 kHz buzz 9.1% (OK, no comb-filtering). Empirical
FluidR3 pitch sweep (RMS, notes 29–89): preset 6 audible 10/10, no gaps
— SF2 never clips a composition (bottom F1 rms 0.035, top F6 0.0175, no
harp-style treble cliff). Range 29–89 = F1–F6, the modern 61-note
concert double-manual compass (historic Ruckers/Taskin: 36–84). Identity
quirk: **no touch dynamics** — the quill plucks at fixed displacement,
so composition jobs keep velocities in the 84–100 band and phrase with
registration (density, octave doubling, choir choice) + trills/mordents
(the trill is the sustain mechanism on fast-dying plucked strings), NOT
velocity swells. Channel quirk: melodic channel (0–9) with program 6.

**Glockenspiel added** (2026-09-19): GM9, Percussion-family pitched metal entry
(instrument.md + glockenspiel.py), verified end-to-end UnitMatrixComposer →
zero-drift ✓ → MIDI (144 bytes) → FluidSynth WAV (1.69 MB) ✓; RenderPipeline stem label
`trackXX_Glockenspiel.wav` ✓ (GM_PROGRAMS[9] = "Glockenspiel", FluidR3 preset 9 =
"Glockenspiel" — labels match exactly, no quirk). ModalSynth primary with stock
'bell' preset and custom `GLOCKENSPIEL_MODES` steel bar inharmonic resonator bank
(fundamental C6 + 2.71x + 5.15x + 8.43x partials, decay rates 2.5–9.0). Verified
sounding range 79–108 (G5–C8, 2.5-octave orchestra bells) and sweet spot 84–100 (C6–E7).
Empirical FluidR3 pitch sweep confirms audibility across full sounding range and
down to MIDI 55 (G3) for transposed scores, no gaps. Single-voice solo render avoids
comb-filtering. Karplus-Strong fallback with loop_gain 0.9980 for sustained metallic ringing.

**Piccolo added** (2026-09-20): GM72, Woodwind-family seventh entry — the
orchestral octave flute (half the length of the concert flute, sounds 1 octave
higher than written; instrument.md + piccolo.py), verified end-to-end
UnitMatrixComposer → zero-drift ✓ → MIDI (144 bytes) → FluidSynth WAV (768 KB) ✓;
RenderPipeline stem label `trackXX_Piccolo.wav` ✓ (GM_PROGRAMS[72] = "Piccolo",
FluidR3 preset 72 = "Piccolo" — labels match exactly, no quirk, distinct from
GM74 Flute which maps to "Recorder"). PhaseModSynth recommended (sine carrier +
sine modulator, ratio 1.0, depth 1.2, attack 0.04 s, release 0.10 s) producing
sweet focused flue tone without artificial harshness. Physical aerophone model
AirPipe supported (`stopped=False`, `length_scale=0.5`, `pressure=0.65`).
Range 72–108 (C5–C8 sounding pitch); sweet spot 84–96 (C6–C7); solo range
79–101 (G5–F7). Solo-render spectral check: 4–8 kHz buzz 3.3% (well within 20%
gate, clean single voice, no comb-filtering). Empirical FluidR3 pitch sweep
(RMS, notes 72–108): preset 72 audible across full range (RMS 0.048–0.103, no
gaps or dropouts). Registry verified with full verification suite.

**Celesta added** (2026-09-21): GM8, Keys-family fifth entry — the keyboard
metallophone (felt-covered hammers striking steel plates suspended over wooden
resonance boxes, patented 1886 by Auguste Mustel; Sugar Plum Fairy color)
(instrument.md + celesta.py), verified end-to-end UnitMatrixComposer →
zero-drift ✓ → MIDI (144 bytes) → FluidSynth WAV (1.06 MB) ✓; RenderPipeline
stem label `trackXX_Celesta.wav` ✓ (GM_PROGRAMS[8] = "Celesta", FluidR3 preset 8
= "Celesta" — labels match exactly, no quirk). ModalSynth primary with stock
'bell' preset and custom `CELESTA_MODES` (steel plate + wooden cavity coupling
at 1.0x, 2.76x, 5.40x, 8.90x, decay rates 3.2–8.5). Verified sounding range
48–108 (C3–C8, 5-octave concert instrument) and sweet spot 72–96 (C5–C7).
Empirical FluidR3 pitch sweep confirms audibility across full sounding range
(RMS 0.063–0.113, no gaps or dropouts). Single-voice solo render avoids
comb-filtering (4–8 kHz buzz 4.5% vs 20% gate). Karplus-Strong fallback
(`loop_gain: 0.9970`) for warm natural metallophone decay.

**English Horn added** (2026-09-22): GM69, Woodwind-family tenor double-reed
entry — the cor anglais (bulbous pear-shaped bell *liebesfuss*, curved bocal;
famous New World Largo / Swan of Tuonela elegiac solo color) (instrument.md +
english_horn.py), verified end-to-end UnitMatrixComposer → zero-drift ✓ →
MIDI (144 bytes) → FluidSynth WAV (741 KB) ✓; RenderPipeline stem label
`trackXX_English_Horn.wav` ✓ (GM_PROGRAMS[69] = "English Horn", FluidR3 preset 69
= "English Horn" — labels match exactly, no quirk). PhaseModSynth recommended
(saw carrier + sine mod, ratio 1.0, depth 2.2, attack 0.06 s, release 0.12 s)
for authentic warm double-reed resonance. Sounding range 50–85 (D3–C#6); sweet spot
57–72 (A3–C5); solo range 52–77 (E3–F5). Solo-render spectral check: 4–8 kHz buzz
0.8% (clean single voice, well below 20% gate). Empirical FluidR3 pitch sweep
(RMS, notes 48–87): preset 69 audible across full 50–85 compass (RMS 0.027–0.048),
hard cutoff above note 85 (C#6 upper limit). Registered in `instrument_registry.py`.

**Harmonica added** (2026-09-24): GM22, Woodwind-family free-reed aerophone entry —
the mouth-blown cousin of the accordion (same free-reed physics, smaller reeds,
breath-controlled dynamics instead of bellows) (instrument.md + harmonica.py),
verified end-to-end UnitMatrixComposer → zero-drift ✓ → MIDI (111 bytes) →
FluidSynth WAV (736 KB) ✓; RenderPipeline stem label `trackXX_Harmonica.wav` ✓
(GM_PROGRAMS[22] = "Harmonica", FluidR3 preset 22 = "Harmonica" — labels match
exactly, **no quirk**). PhaseModSynth recommended (free-reed aerophone: saw
carrier + mod_depth 2.5 between flute 1.5 and accordion 3.2, attack 0.010 s =
fastest reed onset in KB, release 0.04 = near-instant breath cutoff). Solo-render
spectral check: 4–8 kHz buzz 2.3% (clean single voice, well below 20% gate).
Empirical FluidR3 pitch sweep (notes 48–96): preset 22 audible across full range
(13/13 notes play, no gaps). Registered in `instrument_registry.py` as HARMONICA
convenience constant. Note: bend simulation requires MIDI pitch-bend events — GM
patch is clean chromatic, no natural reed bend. REVERB_TAIL 1.2 s is the shortest
in the Woodwind family (intentional dry tone).

**Shakuhachi added** (2026-09-25): GM77, World-family ninth entry — the Japanese
end-blown bamboo flute (1.8 shaku, ~54.5 cm; the Zen meditation flute that
pairs with koto, shamisen, taiko in traditional sankyoku ensemble). Verified
end-to-end UnitMatrixComposer → zero-drift ✓ → MIDI (150 bytes) → FluidSynth
WAV (1.27 MB) ✓; RenderPipeline stem label `trackXX_Shakuhachi.wav` ✓
(GM_PROGRAMS[77] = "Shakuhachi", FluidR3 preset 77 = "Shakuhachi" — labels
match exactly, **no quirk**). PhaseModSynth recommended (end-blown bamboo
flute: sine carrier + sine modulator, mod_freq_ratio 1.0, mod_depth 2.0,
attack 0.06 s, release 0.20 s — breathier than flute with richer upper
harmonics). Additive fallback with noise floor above 6 kHz for muraiki breath
character. Range 55–100 (G3–E7, standard 2-octave D4–D6 on 1.8 shaku);
solo range 62–86 (D4–D6). Solo-render spectral check: 4–8 kHz buzz 0.6%
(clean single voice, well below 20% gate). Empirical FluidR3 pitch sweep
(RMS, notes 55–100): preset 77 audible across full range (no gaps or
dropouts). Registered in `instrument_registry.py` as SHAKUCHACHI convenience
constant. Line-instrument quirk: monophonic bamboo flute — no dense chords
or harmony; pentatonic writing is idiomatic (D minor pentatonic); meri/kari
bending via MIDI pitch-bend events for authentic Zen-style glissando.

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
| Strings | Orchestral Harp | 46 | 24–103 | harmony, arpeggio, glissando, melody, countermelody, accent |
| Strings | Viola | 41 | 48–91 | harmony, counter, lead, accent |
| Strings | Cello | 42 | 36–84 | bass, lead, counter, harmony |
| Strings | Double Bass | 43 | 28–74 | bass, rhythm, accent, harmony |
| Keys | Piano | 1 | 21–108 | harmony, melody, bass, rhythm |
| Keys | Church Organ | 19 | 36–96 | harmony, pad, bass, rhythm, accent |
| Keys | Dulcimer | 15 | 48–96 | lead, melody, ornament, rhythm, harmony |
| Keys | Harpsichord | 6 | 29–89 | harmony, continuo, melody, ornament, countermelody, accent |
|| Keys | Celesta | 8 | 48–108 | lead, melody, ornament, arpeggio, countermelody, accent |
|| Keys | Accordion | 21 | 36–96 | harmony, melody, bass, rhythm, ornament |
|| Brass | Trumpet | 56 | 54–86 | lead, accent, fanfare |
| Brass | Trombone | 57 | 40–78 | bass, counter, accent, harmony |
| Brass | French Horn | 60 | 41–84 | harmony, counter, accent, lead |
| Brass | Tuba | 58 | 26–72 | bass, harmony, accent, rhythm |
| Woodwind | Flute | 74 | 60–96 | lead, counter, ornament |
| Woodwind | Harmonica | 22 | 48–96 | lead, harmony, accent |
| Woodwind | Oboe | 68 | 52–92 | lead, counter, harmony, accent |
| Woodwind | Clarinet | 71 | 52–96 | lead, counter, harmony, accent |
| Woodwind | English Horn | 69 | 50–85 | lead, countermelody, melody, harmony, accent |
| Woodwind | Piccolo | 72 | 72–108 | lead, melody, ornament, accent, countermelody |
| Woodwind | Alto Saxophone | 65 | 49–88 | lead, counter, accent, harmony |
| Woodwind | Bassoon | 70 | 34–88 | bass, harmony, counter, lead |
| Guitar | Acoustic | 25 | 40–84 | harmony, rhythm, strum |
| Percussion | Drum Kit | ch9 | 35–81 | rhythm, groove, accent |
| Percussion | Glockenspiel | 9 | 79–108 | lead, melody, ornament, accent, countermelody |
| Percussion | Marimba | 12 | 45–96 | lead, melody, accent, countermelody, harmony |
| Percussion | Steel Drums | 114 | 55–96 | lead, melody, accent, countermelody, harmony, rhythm |
| Percussion | Timpani | 47 | 36–65 | accent, rhythm, bass, drone |
| Percussion | Vibraphone | 11 | 48–89 | lead, melody, harmony, countermelody, accent |
| Percussion | Xylophone | 13 | 53–89 | lead, melody, ornament, accent, countermelody |
| World | Sitar | 104 | 55–96 | lead, melody, ornament, drone |
| World | Banjo | 105 | 46–93 | lead, melody, ornament, rhythm, accent |
| World | Koto | 107 | 51–90 | lead, melody, ornament, drone, harmony |
| World | Shamisen | 106 | 45–89 | lead, melody, ornament, drone, countermelody |
| World | Kalimba | 108 | 48–96 | lead, melody, ornament, drone, harmony |
| World | Shenai | 111 | 55–96 | lead, melody, ornament, drone, accent |
| World | Fiddle | 110 | 55–96 | lead, melody, ornament, countermelody, accent |
| World | Taiko Drum | 116 | 36–67 | accent, rhythm, drone, ornament |
| World | Shakuhachi | 77 | 55–100 | lead, melody, ornament, drone, accent |
| Woodwind | Bagpipe | 109 | 53–96 | lead, melody, ornament, drone, accent |

## Stem label quirks (RenderPipeline)

GM_PROGRAMS list is **0-indexed** (index N = GM program N). Verified 2026-08-22 against pipeline source + TimGM6mb.sf2 phdr.

| Program | Expected label | Actual label |
|---|---|---|
| 40 | Violin | Violin ✓ |
| 41 | Viola | Viola ✓ |
| 42 | Cello | Cello ✓ |
| 43 | Contrabass | Contrabass ✓ (labeled "Contrabass", not "Double_Bass") |
| 46 | Orchestral Harp | Orchestral_Harp ✓ (GM_PROGRAMS[46] = "Orchestral Harp"; FluidR3 preset 46 = "Harp" — one-word SF2 spelling, cosmetic only) |
| 1 | Acoustic Grand Piano | **Bright_Acoustic_Piano** ✗ (list[1]) |
| 6 | Harpsichord | Harpsichord ✓ (GM_PROGRAMS[6] + FluidR3 preset 6 both "Harpsichord") |
| 8 | Celesta | Celesta ✓ (GM_PROGRAMS[8] + FluidR3 preset 8 both "Celesta") |
| 69 | English Horn | English_Horn ✓ (GM_PROGRAMS[69] + FluidR3 preset 69 both "English Horn") |
| 9 | Glockenspiel | Glockenspiel ✓ (GM_PROGRAMS[9] + FluidR3 preset 9 both "Glockenspiel") |
| 56 | Trumpet (correct GM) | Trumpet ✓ |
| 57 | Trombone | Trombone ✓ |
| 58 | Tuba | Tuba ✓ |
| 60 | French Horn | French Horn ✓ (SF2 preset is "French Horns" plural — cosmetic) |
| 70 | Bassoon | Bassoon ✓ |
| 72 | Piccolo | Piccolo ✓ (GM_PROGRAMS[72] + FluidR3 preset 72 both "Piccolo") |
| 68 | Oboe | Oboe ✓ (SF2 preset is "Oboe (Orch)" — cosmetic suffix only) |
| 65 | Alto Sax (correct GM) | **Alto_Sax** (labeled "Alto Sax", not "Saxophone") |
| 74 | Flute | **Recorder** ✗ |
| 15 | Dulcimer | Dulcimer ✓ (GM_PROGRAMS[15] + FluidR3 preset 15 both "Dulcimer") |
| 19 | Church Organ | Church Organ ✓ (GM_PROGRAMS[19] + SF2 preset 19 both "Church Organ") |
| 25 | Acoustic Guitar (nylon) | Acoustic_Guitar_nylon ✓ |
| 12 | Marimba | Marimba ✓ |
| 47 | Timpani | Timpani ✓ (GM_PROGRAMS[47] + FluidR3 preset 47 both "Timpani") |
| 11 | Vibraphone | Vibraphone ✓ (GM_PROGRAMS[11] + FluidR3 preset 11 both "Vibraphone") |
| 13 | Xylophone | Xylophone ✓ (GM_PROGRAMS[13] + FluidR3 preset 13 both "Xylophone") |
| 104 | Sitar | Sitar ✓ (GM_PROGRAMS[104] + FluidR3 preset 104 both "Sitar") |
| 105 | Banjo | Banjo ✓ (GM_PROGRAMS[105] + FluidR3 preset 105 both "Banjo") |
| 107 | Koto | Koto ✓ (GM_PROGRAMS[107] + FluidR3 preset 107 both "Koto") |
| 106 | Shamisen | Shamisen ✓ (GM_PROGRAMS[106] + FluidR3 preset 106 both "Shamisen") |
| 108 | Kalimba | Kalimba ✓ (GM_PROGRAMS[108] + FluidR3 preset 108 both "Kalimba") |
| 109 | Bagpipe | **Bag_pipe** ✗ (GM_PROGRAMS[109] = "Bag pipe" — two words; FluidR3 preset 109 = "BagPipe") |
| 111 | Shanai | **Shanai** ✗ (GM_PROGRAMS[111] = "Shanai" — GM2 spec spelling; instrument = Shenai, FluidR3 preset 111 = "Shenai") |
| 110 | Fiddle | Fiddle ✓ (GM_PROGRAMS[110] + FluidR3 preset 110 both "Fiddle") |
| 77 | Shakuhachi | Shakuhachi ✓ **no quirk** (GM_PROGRAMS[77] + FluidR3 preset 77 both "Shakuhachi") |
| 22 | Harmonica | Harmonica ✓ (GM_PROGRAMS[22] + FluidR3 preset 22 both "Harmonica") |
| 114 | Steel Drums | Steel Drums ✓ (GM_PROGRAMS[114] + FluidR3 preset 114 both "Steel Drums") |
|| 116 | Taiko Drum | Taiko Drum ✓ (GM_PROGRAMS[116] + FluidR3 preset 116 both "Taiko Drum") |
|| 21 | Accordion | Accordion ✓ (GM_PROGRAMS[21] = "Accordion"; FluidR3 preset 21 = "Accordian" — archaic SF2 spelling, cosmetic only, no routing impact) |
|| ch9/pgm0 | Drums | **Acoustic_Grand_Piano** ✗ (program-0 fallback) |

> **Known off-by-one in existing entries**: ~~`trumpet.py` uses 57~~ **FIXED 2026-08-27**: trumpet is now 56 (SF2 preset 56=`SoloTrumpet`). `piano.py`=1 → actually Bright Acoustic Piano (GM #2) — cosmetic label difference only, no routing impact. Legacy registry rows kept as-is for piano; new instruments use 0-indexed programs matching pipeline+SF2.

Match production code on ACTUAL labels, not intended names.
