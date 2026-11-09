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

**Ocarina added** (2026-09-27): GM79, Woodwind-family vessel flute entry — the
globular ceramic fipple flute (Zelda ocarina, Pikachu kazoo rip-off, the
purest tone in the woodwind family: near-sinusoidal fundamental with
extremely weak upper partials, chamber suppresses overblow) (instrument.md +
ocarina.py), verified end-to-end UnitMatrixComposer → zero-drift ✓ → MIDI (111
bytes) → FluidSynth WAV (760 KB) ✓; RenderPipeline stem label
`trackXX_Ocarina.wav` ✓ (GM_PROGRAMS[79] = "Ocarina", FluidR3 preset 79 =
"Ocarina" — labels match exactly, **no quirk**). PhaseModSynth recommended
(sine carrier + sine modulator, ratio 1.0, depth 0.8 — shallowest in the
woodwind set, reflecting the near-sine vessel flute tone; attack 0.06 s for
gradual chamber fill; no reed/edge-tone transient). Additive fallback with 4
partials (weights 0.9, 0.3, 0.1, 0.03 — strongest fundamental falloff of any
Woodwind). Solo-render spectral check: 4–8 kHz buzz 1.0% (near-sine tone —
cleanest in the set, well below 20% gate). Range 55–96 (G3–C7 sounding);
sweet spot 72–84 (C5–C6). Identity quirk: the ocarina is the ONLY vessel
flute in the KB (Helmholtz resonator, not a tube flute) — its range is
inherently limited to about an octave+a-fourth on a single chamber, so
composition should keep lines within roughly G3–C6 (55–84) for idiomatic
tone; above C6 the patch thins out. Mono-line quirk: ocarina is a single
breath line (vessel), NOT a harmony/pad voice — no dense chords.

**Music Box added** (2026-09-29): GM10, Percussion-family seventh entry — the
mechanical pinned-cylinder lamellophone (steel-comb teeth plucked by pins on a
revolving cylinder; the iconic wind-up toy and jewellery-box tinkle)
(instrument.md + music_box.py), verified end-to-end UnitMatrixComposer →
zero-drift ✓ → MIDI (120 bytes) → FluidSynth WAV (855 KB) ✓; RenderPipeline
stem label `trackXX_Music_Box.wav` ✓ (GM_PROGRAMS[10] = "Music Box", FluidR3
preset 10 = "Music Box" — labels match exactly, **no quirk**). ModalSynth
primary with stock 'bell' preset and custom `MUSIC_BOX_MODES` bank at near-harmonic
1:2:3:4 ratios with fast decay rates 4-12 (steel tine = clamped cantilever, not
free-free bar). Karplus-Strong secondary (tine IS plucked — waveguide model fits;
loop_gain 0.9950 for short steel-ring ~0.5-1.0 s). Solo-render spectral check:
4–8 kHz buzz 9.6% (below 20% gate, no comb-filtering). Range 60–96 (C4–C7);
sweet spot 72–84 (C5–C6). Identity quirk: music box is a MONOPHONIC mechanical
instrument — composition jobs MUST write single-note lines, NOT chords (a real
music box physically cannot play two notes simultaneously on the same tine).

**Pan Flute added** (2026-10-01): GM75, World-family entry — South American
Andean panpipes (zampoña/siku/antara), the stopped-pipe breath instrument
made of cane tubes; the only stopped-pipe aerophone in the KB (tube is
closed at one end — only odd partials 1,3,5,7). Verified end-to-end
UnitMatrixComposer → zero-drift ✓ → MIDI (111 bytes) → FluidSynth WAV (731
KB) ✓; RenderPipeline stem label `trackXX_Pan_Flute.wav` ✓ (GM_PROGRAMS[75]
= "Pan Flute", FluidR3 preset 75 = "Pan Flute" — labels match exactly, **no
quirk**). PhaseModSynth recommended (stopped-pipe flue tone: sine carrier +
sine modulator, mod_depth 1.2 — shallowest pure-toned flue set — between
ocarina 0.8 and shakuhachi 2.0; attack 0.05 s for gentle breath onset;
release 0.15 s). Additive fallback with odd-only partials
(1:0.9, 3:0.35, 5:0.15, 7:0.05) — strongest fundamental dominance of the
World wind set. Solo-render spectral check: 4–8 kHz buzz 1.5% (clean single
voice, well below 20% gate). Empirical FluidR3 pitch sweep (RMS, notes
55–100): preset 75 audible across full range (no gaps or dropouts).
Registered in `instrument_registry.py` as PAN_FLUTE convenience constant.
Line-instrument quirk: each tube produces one pitch — no dense chords or
harmony; the arqa/ira siku pairs alternate rapidly for melodic lines, not
vertical harmonies.

**Tubular Bells added** (2026-09-26): GM14, Percussion-family seventh entry —
the struck brass tube chimes (orchestral tintinnabuli; Tchaikovsky 1812,
Mahler Resurrection, Mike Oldfield theme) (instrument.md + tubular_bells.py),
verified end-to-end UnitMatrixComposer → zero-drift ✓ → MIDI (91 bytes) →
FluidSynth WAV (4.12 MB) ✓; RenderPipeline stem label
`trackXX_Tubular_Bells.wav` ✓ (GM_PROGRAMS[14] = "Tubular Bells", FluidR3
preset 14 = "Tubular Bells" — labels match exactly, **no quirk**). ModalSynth
recommended with a custom `TUBULAR_BELLS_MODES` bank at the struck-brass-tube
ratios **1 : 2.76 : 5.40 : 8.93** (free-free bending modes) and decay rates
0.50/0.80/1.20/2.00 (slow — brass tube rings for 1.5-3 s; between vibraphone
0.30–1.10 and marimba 8–20). The stock `'bell'` preset is the closest bank
but models a generic metallic bar, not a brass tube; the custom bank gives
the warm church-bell fundamental overtone. Karplus-Strong demoted (tube is
struck, not plucked; loop_gain 0.9970 → long metallic ring ~1.5-2.5 s,
comparable to glockenspiel 0.9980). Solo-render spectral check: 4–8 kHz buzz
3.1% (no comb-filtering). Range 60–78 (C4–F5, standard 1.5-octave 18-tube
set); sweet spot 60–72 (C4–C5 fundamental octave — the bell's roundest bloom).
Empirical FluidR3 pitch sweep (RMS, notes 60–78): preset 14 audible across
the full span, no gaps — SF2 never clips a composition. Identity quirk:
GM14 is a **colour instrument** with limited 1.5 octave range — used for
accent/ceremonial punctuation, NOT for melodic passagework; use sparingly,
one stroke at a time. Channel quirk: melodic channel (0–9) with program 14
— channel 9 would trigger the drum-kit map and the `Acoustic_Grand_Piano`
program-0 fallback label (timpani lesson).

**Brass Section added** (2026-10-15): GM61, Brass-family ensemble entry — the
full brass tutti patch (trumpets, trombones, french horns, tuba) in a single
multi-sample patch; the iconic fanfare/orchestral stab voice (instrument.md +
brass_section.py), verified end-to-end UnitMatrixComposer → zero-drift ✓ →
MIDI (92 bytes) → FluidSynth WAV (795 KB) ✓; RenderPipeline stem label
`trackXX_Brass_Section.wav` ✓ (GM_PROGRAMS[61] = "Brass Section", FluidR3
preset 61 = "Brass Section" — labels match exactly, **no quirk**).
PhaseModSynth recommended (saw carrier, mod_depth 2.8, attack 0.06 s —
sustained multi-brass ensemble). Solo-render spectral check: 4–8 kHz buzz
1.5% (clean single voice, well below 20% gate). Empirical FluidR3 pitch sweep
confirms audibility across full 36–96 span. Registered in `instrument_registry.py`
as BRASS_SECTION convenience constant. Ensemble voice quirk: use for tutti
fanfares/harmonies, NOT for solo lines (use individual brass patches for that).

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
| Strings | Pizzicato Strings | 45 | 36–96 | rhythm, ostinato, bass, accompaniment, countermelody, accent |
| Strings | String Ensemble 1 | 48 | 28–96 | harmony, pad, melody, countermelody, accent |
| Keys | Piano | 1 | 21–108 | harmony, melody, bass, rhythm |
| Keys | Church Organ | 19 | 36–96 | harmony, pad, bass, rhythm, accent |
| Keys | Dulcimer | 15 | 48–96 | lead, melody, ornament, rhythm, harmony |
| Keys | Electric Piano 1 | 4 | 36–96 | harmony, melody, bass, accent, color |
| Keys | Electric Piano 2 | 5 | 36–96 | harmony, melody, bass, accent, color |
| Keys | Harpsichord | 6 | 29–89 | harmony, continuo, melody, ornament, countermelody, accent |
| Keys | Celesta | 8 | 48–108 | lead, melody, ornament, arpeggio, countermelody, accent |
| Keys | Accordion | 21 | 36–96 | harmony, melody, bass, rhythm, ornament |
| Keys | Tango Accordion | 23 | 41–96 | lead, melody, ornament, harmony, accent, pad |
| Keys | Reed Organ | 20 | 36–96 | harmony, pad, melody, drone, ornament |
| Keys | Clavi | 7 | 29–89 | lead, rhythm, accent, ornament, countermelody |
| Keys | Honky-tonk Piano | 3 | 33–96 | rhythm, harmony, melody, bass, ornament, color |
| Keys | Drawbar Organ | 16 | 24–89 | harmony, pad, comp, lead, bass, rhythm, drone, accent |
| Keys | Electric Piano 1 (Rhodes) | 4 | 36–96 | harmony, melody, bass, accent, color |
| Brass | Trumpet | 56 | 54–86 | lead, accent, fanfare |
| Brass | Muted Trumpet | 59 | 54–86 | lead, countermelody, accent, melody, ornament |
| Brass | Trombone | 57 | 40–78 | bass, counter, accent, harmony |
| Brass | Brass Section | 61 | 36–96 | lead, accent, fanfare, counter, harmony, pad |
| Brass | French Horn | 60 | 41–84 | harmony, counter, accent, lead |
| Brass | Tuba | 58 | 26–72 | bass, harmony, accent, rhythm |
| Woodwind | Flute | 73 | 60–96 | lead, counter, ornament |
| Woodwind | Harmonica | 22 | 48–96 | lead, harmony, accent |
| Woodwind | Oboe | 68 | 52–92 | lead, counter, harmony, accent |
| Woodwind | Clarinet | 71 | 52–96 | lead, counter, harmony, accent |
| Woodwind | English Horn | 69 | 50–85 | lead, countermelody, melody, harmony, accent |
| Woodwind | Piccolo | 72 | 72–108 | lead, melody, ornament, accent, countermelody |
| Woodwind | Alto Saxophone | 65 | 49–88 | lead, counter, accent, harmony |
| Woodwind | Bagpipe | 109 | 53–96 | lead, melody, ornament, drone, accent |
| Woodwind | Baritone Saxophone | 67 | 36–80 | bass, harmony, accent, lead, countermelody |
| Woodwind | Bassoon | 70 | 34–88 | bass, harmony, counter, lead |
| Guitar | Acoustic Guitar (nylon) | 24 | 40–84 | harmony, rhythm, strum |
| Guitar | Acoustic Guitar (steel) | 25 | 40–86 | harmony, rhythm, strum, lead, melody, ornament, countermelody |
| Guitar | Electric Guitar (jazz) | 26 | 28–84 | harmony, rhythm, comp, lead, melody, ornament, countermelody, accent |
| Guitar | Electric Guitar (clean) | 27 | 28–84 | harmony, rhythm, strum, lead, melody, ornament, countermelody, accent |
| Guitar | Electric Guitar (muted) | 28 | 28–84 | rhythm, comp, groove, accent, texture, melody |
| Guitar | Overdriven Guitar | 29 | 28–84 | lead, melody, accent, rhythm, strum, countermelody |
| Guitar | Distortion Guitar | 30 | 28–84 | lead, melody, accent, rhythm, power-chord strum, countermelody |
| Bass | Electric Bass (finger) | 33 | 24–84 | bass, rhythm, countermelody, accent |
| Bass | Acoustic Bass | 32 | 24–72 | bass, rhythm, countermelody, accent, melody |
| Bass | Fretless Bass | 35 | 24–72 | bass, melody, countermelody, groove, slide, color |
| Bass | Synth Bass 1 | 38 | 24–84 | bass, rhythm, groove, accent |
| Percussion | Drum Kit | ch9 | 35–81 | rhythm, groove, accent |
| Percussion | Glockenspiel | 9 | 79–108 | lead, melody, ornament, accent, countermelody |
| Percussion | Marimba | 12 | 45–96 | lead, melody, accent, countermelody, harmony |
| Percussion | Steel Drums | 114 | 55–96 | lead, melody, accent, countermelody, harmony, rhythm |
| Percussion | Timpani | 47 | 36–65 | accent, rhythm, bass, drone |
| Percussion | Tubular Bells | 14 | 60–78 | accent, color, drone, lead, ornament |
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
| World | Agogo | 113 | 55–96 | rhythm, accent, ornament, drone |
| World | Pan Flute | 75 | 55–100 | lead, melody, ornament, drone, accent |
| World | Shakuhachi | 77 | 55–100 | lead, melody, ornament, drone, accent |
| Synth | Pad 1 (new age) | 88 | 36–96 | pad, harmony, texture, drone, accent |
| Synth | Pad 2 (warm) | 89 | 36–96 | pad, harmony, texture, drone, accent |
| Synth | Orchestra Hit | 55 | 36–96 | accent, stab, rhythm, punctuation, texture, lead |
| Synth | Lead 3 (calliope) | 82 | 60–96 | lead, melody, ornament, accent, countermelody |
| Synth | Synth Brass 1 | 62 | 36–96 | lead, harmony, accent, stab, pad, countermelody |
| Synth | Synth Voice | 54 | 36–96 | lead, melody, harmony, pad, countermelody, accent |
| Vocal | Choir Aahs | 52 | 40–88 | pad, harmony, melody, countermelody, anthem, texture |
| Woodwind | Bagpipe | 109 | 53–96 | lead, melody, ornament, drone, accent |
| Woodwind | Ocarina | 79 | 55–96 | lead, harmony, accent |

## Stem label quirks (RenderPipeline)

GM_PROGRAMS list is **0-indexed** (index N = GM program N). Verified 2026-08-22 against pipeline source + TimGM6mb.sf2 phdr.

| Program | Expected label | Actual label |
|---|---|---|
| 40 | Violin | Violin ✓ |
| 41 | Viola | Viola ✓ |
| 42 | Cello | Cello ✓ |
| 43 | Contrabass | Contrabass ✓ (labeled "Contrabass", not "Double_Bass") |
| 45 | Pizzicato Strings | Pizzicato_Strings ✓ (GM_PROGRAMS[45] = "Pizzicato Strings"; FluidR3 preset 45 = "Pizzicato Section" — internal SF2 name differs cosmetically, **no routing impact**) |
| 46 | Orchestral Harp | Orchestral_Harp ✓ (GM_PROGRAMS[46] = "Orchestral Harp"; FluidR3 preset 46 = "Harp" — one-word SF2 spelling, cosmetic only) |
| 5 | Electric Piano 2 | Electric_Piano_2 ✓ (GM_PROGRAMS[5] + FluidR3 preset 5 both "Electric Piano 2"; internal SF2 name "Legend EP 2" — cosmetic only, **no routing impact**) |
| 3 | Honky-tonk Piano | Honky-tonk_Piano ✓ (GM_PROGRAMS[3] = "Honky-tonk Piano"; the sanitizer keeps the HYPHEN — only spaces/parens/slashes are rewritten. FluidR3 preset 3 = "Honky Tonk" — hyphen dropped in the SF2 name, cosmetic only, **no routing impact**; STEM_LABEL = "Honky-tonk_Piano") |
|| 1 | Acoustic Grand Piano | **Bright_Acoustic_Piano** ✗ (list[1]) |
| 6 | Harpsichord | Harpsichord ✓ (GM_PROGRAMS[6] + FluidR3 preset 6 both "Harpsichord") |
| 7 | Clavi | **Clavi** ✓ (pipeline GM_PROGRAMS[7] = "Clavi"; FluidR3 preset 7 = "Clavinet" — cosmetic expansion, no routing impact; STEM_LABEL = "Clavi" matches pipeline) |
| 16 | Drawbar Organ | Drawbar_Organ ✓ (GM_PROGRAMS[16] = "Drawbar Organ"; FluidR3 bank-0 preset 16 = "DrawbarOrgan" — no space in the SF2 name, cosmetic only, **no routing impact**; STEM_LABEL = "Drawbar_Organ") |
| 8 | Celesta | Celesta ✓ (GM_PROGRAMS[8] + FluidR3 preset 8 both "Celesta") |
| 69 | English Horn | English_Horn ✓ (GM_PROGRAMS[69] + FluidR3 preset 69 both "English Horn") |
| 9 | Glockenspiel | Glockenspiel ✓ (GM_PROGRAMS[9] + FluidR3 preset 9 both "Glockenspiel") |
| 56 | Trumpet (correct GM) | Trumpet ✓ |
| 59 | Muted Trumpet | Muted_Trumpet ✓ (GM_PROGRAMS[59] + FluidR3 preset 59 both "Muted Trumpet") |
| 57 | Trombone | Trombone ✓ |
| 58 | Tuba | Tuba ✓ |
| 60 | French Horn | French Horn ✓ (SF2 preset is "French Horns" plural — cosmetic) |
| 61 | Brass Section | Brass_Section ✓ (GM_PROGRAMS[61] + FluidR3 preset 61 both "Brass Section" — labels match exactly, **no quirk**) |
| 70 | Bassoon | Bassoon ✓ |
| 72 | Piccolo | Piccolo ✓ (GM_PROGRAMS[72] + FluidR3 preset 72 both "Piccolo") |
| 68 | Oboe | Oboe ✓ (SF2 preset is "Oboe (Orch)" — cosmetic suffix only) |
| 65 | Alto Sax (correct GM) | **Alto_Sax** (labeled "Alto Sax", not "Saxophone") |
| 74 | Flute | **Recorder** ✗ |
| 15 | Dulcimer | Dulcimer ✓ (GM_PROGRAMS[15] + FluidR3 preset 15 both "Dulcimer") |
| 19 | Church Organ | Church_Organ ✓ (GM_PROGRAMS[19] + SF2 preset 19 both "Church Organ") |
| 20 | Reed Organ | Reed_Organ ✓ (GM_PROGRAMS[20] + FluidR3 preset 20 both "Reed Organ" — labels match exactly, **no quirk**) |
| 25 | Acoustic Guitar (nylon) |
| 12 | Marimba | Marimba ✓ |
| 14 | Tubular Bells | Tubular_Bells ✓ (GM_PROGRAMS[14] = "Tubular Bells"; FluidR3 preset 14 = "Tubular Bells" — labels match exactly, no quirk) |
| 47 | Timpani | Timpani ✓ (GM_PROGRAMS[47] + FluidR3 preset 47 both "Timpani") |
| 11 | Vibraphone | Vibraphone ✓ (GM_PROGRAMS[11] + FluidR3 preset 11 both "Vibraphone") |
| 13 | Xylophone | Xylophone ✓ (GM_PROGRAMS[13] + FluidR3 preset 13 both "Xylophone") |
| 104 | Sitar | Sitar ✓ (GM_PROGRAMS[104] + FluidR3 preset 104 both "Sitar") |
| 105 | Banjo | Banjo ✓ (GM_PROGRAMS[105] + FluidR3 preset 105 both "Banjo") |
| 54 | Synth Voice | Synth_Voice ✓ (GM_PROGRAMS[54] + FluidR3 preset 54 both "Synth Voice" — labels match exactly, **no quirk**) |
| 107 | Koto | Koto ✓ (GM_PROGRAMS[107] + FluidR3 preset 107 both "Koto") |
| 106 | Shamisen | Shamisen ✓ (GM_PROGRAMS[106] + FluidR3 preset 106 both "Shamisen") |
| 108 | Kalimba | Kalimba ✓ (GM_PROGRAMS[108] + FluidR3 preset 108 both "Kalimba") |
| 109 | Bagpipe | **Bag_pipe** ✗ (GM_PROGRAMS[109] = "Bag pipe" — two words; FluidR3 preset 109 = "BagPipe") |
| 111 | Shanai | **Shanai** ✗ (GM_PROGRAMS[111] = "Shanai" — GM2 spec spelling; instrument = Shenai, FluidR3 preset 111 = "Shenai") |
| 110 | Fiddle | Fiddle ✓ (GM_PROGRAMS[110] + FluidR3 preset 110 both "Fiddle") |
| 77 | Shakuhachi | Shakuhachi ✓ **no quirk** (GM_PROGRAMS[77] + FluidR3 preset 77 both "Shakuhachi") |
| 75 | Pan Flute | Pan_Flute ✓ (GM_PROGRAMS[75] = "Pan Flute"; FluidR3 preset 75 = "Pan Flute" — labels match exactly, **no quirk**) |
| 52 | Choir Aahs | Choir_Aahs ✓ (GM_PROGRAMS[52] = "Choir Aahs"; FluidR3 preset 52 = "Ahh Choir" — cosmetic SF2 spelling, **no routing impact**) |
|| 22 | Harmonica | Harmonica ✓ (GM_PROGRAMS[22] + FluidR3 preset 22 both "Harmonica") |
|| 79 | Ocarina | Ocarina ✓ (GM_PROGRAMS[79] + FluidR3 preset 79 both "Ocarina") |
|| 114 | Steel Drums | Steel Drums ✓ (GM_PROGRAMS[114] + FluidR3 preset 114 both "Steel Drums") |
|| 116 | Taiko Drum | Taiko Drum ✓ (GM_PROGRAMS[116] + FluidR3 preset 116 both "Taiko Drum") |
|| 113 | Agogo | Agogo ✓ (GM_PROGRAMS[113] = "Agogo"; FluidR3 preset 113 = "Agogo" — labels match exactly, **no quirk**) |
||| 66 | Tenor Sax | Tenor_Sax ✓ (GM_PROGRAMS[66] = "Tenor Sax"; FluidR3 preset 66 = "Tenor Sax" — labels match exactly, **no quirk**) |
||| 67 | Baritone Sax | Baritone_Sax ✓ (GM_PROGRAMS[67] = "Baritone Sax"; FluidR3 preset 67 = "Baritone Sax" — labels match exactly, **no quirk**) |
|||| 21 | Accordion | Accordion ✓ (GM_PROGRAMS[21] = "Accordion"; FluidR3 preset 21 = "Accordian" — archaic SF2 spelling, cosmetic only, no routing impact) |
||| 10 | Music Box | Music_Box ✓ (GM_PROGRAMS[10] = "Music Box"; FluidR3 preset 10 = "Music Box" — labels match exactly, **no quirk**) |
||| 4 | Electric Piano 1 | Electric_Piano_1 ✓ (GM_PROGRAMS[4] = "Electric Piano 1"; FluidR3 preset 4 = "Rhodes EP" — internal SF2 name, cosmetic only, no routing impact) |
||| ch9/pgm0 | Drums | **Acoustic_Grand_Piano** ✗ (program-0 fallback) |
||| 24 | Acoustic Guitar (nylon) | Acoustic_Guitar_nylon ✓ (GM_PROGRAMS[24] = "Acoustic Guitar (nylon)"; FluidR3 preset 24 = "Nylon String Guitar" — internal SF2 name differs cosmetically, no routing impact) |
|| 26 | Electric Guitar (jazz) | Electric_Guitar_jazz ✓ (GM_PROGRAMS[26] = "Electric Guitar (jazz)" — GM2 spec spelling; FluidR3 preset 26 = "Jazz Guitar" — SF2 uses the common name, cosmetic only, **no routing impact**; STEM_LABEL = "Electric_Guitar_jazz" matches pipeline) |
||| 25 | Acoustic Guitar (steel) | Acoustic_Guitar_steel ✓ (GM_PROGRAMS[25] = "Acoustic Guitar (steel)"; FluidR3 preset 25 = "Steel String Guitar" — internal SF2 name differs cosmetically, no routing impact) |
| 48 | String Ensemble 1 | String_Ensemble_1 ✓ (GM_PROGRAMS[48] = "String Ensemble 1"; FluidR3 preset 48 = "Strings" — one-word SF2 spelling, cosmetic only, **no quirk**) |
|| 88 | Pad 1 (new age) | Pad_1_new_age ✓ (GM_PROGRAMS[88] = "Pad 1 (new age)" → sanitized `Pad_1_new_age` — parens stripped, spaces → underscore; FluidR3 preset 88 = **"Fantasia"** — SF2 internal name differs from GM label, cosmetic only, **no routing impact**; preset 89 = "Warm Pad" is the darker sibling) |
|| 38 | Synth Bass 1 | Synth_Bass_1 ✓ (GM_PROGRAMS[38] = "Synth Bass 1"; FluidR3 preset 38 = "Synth Bass 1" — labels match exactly, **no quirk**) |
| 35 | Fretless Bass | Fretless_Bass ✓ (GM_PROGRAMS[35] + FluidR3 preset 35 both "Fretless Bass" — labels match exactly, **no quirk**) |
| 23 | Tango Accordion | Tango_Accordion ✓ (GM_PROGRAMS[23] = "Tango Accordion"; FluidR3 preset 23 = "Bandoneon" — SF2 internal name differs, cosmetic only, **no routing impact**) |
||| 44 | Tremolo Strings | Tremolo_Strings ✓ (GM_PROGRAMS[44] = "Tremolo Strings"; FluidR3 preset 44 = "Tremolo" — one-word SF2 spelling, cosmetic only, **no routing impact**) |
||| 30 | Distortion Guitar | Distortion_Guitar ✓ (GM_PROGRAMS[30] + FluidR3 preset 30 both "Distortion Guitar" — labels match exactly, **no quirk**) |
||| 62 | Synth Brass 1 | Synth_Brass_1 ✓ (GM_PROGRAMS[62] = "Synth Brass 1"; FluidR3 preset 62 = "Synth Brass 1" — labels match exactly, **no quirk**) |
||| 32 | Acoustic Bass | Acoustic_Bass ✓ (GM_PROGRAMS[32] = "Acoustic Bass"; FluidR3 preset 32 = "Acoustic Bass" — labels match exactly, **no quirk**) |
|||| 82 | Lead 3 (calliope) | Lead_3_calliope ✓ (GM_PROGRAMS[82] = "Lead 3 (calliope)" → sanitized `Lead_3_calliope` — parens stripped, spaces → underscore; FluidR3 preset 82 = **"Calliope Lead"** — SF2 internal name differs from the GM label, cosmetic only, **no routing impact**; stems are labelled from GM_PROGRAMS) |
|||| 89 | Pad 2 (warm) | Pad_2_warm ✓ (GM_PROGRAMS[89] = "Pad 2 (warm)" → sanitized `Pad_2_warm` — parens stripped, spaces → underscore; FluidR3 preset 89 = **"Warm Pad"** — SF2 internal name differs from the GM label, cosmetic only, **no routing impact**; STEM_LABEL = "Pad_2_warm" matches the pipeline's real label) |
|||| 55 | Orchestra Hit | Orchestra_Hit ✓ (GM_PROGRAMS[55] = "Orchestra Hit"; FluidR3 preset 55 = "Orchestra Hit" — labels match exactly, **no quirk**) |

> **Known off-by-one in existing entries**: ~~`trumpet.py` uses 57~~ **FIXED 2026-08-27**: trumpet is now 56 (SF2 preset 56=`SoloTrumpet`). `piano.py`=1 → actually Bright Acoustic Piano (GM #2) — cosmetic label difference only, no routing impact. Legacy registry rows kept as-is for piano; new instruments use 0-indexed programs matching pipeline+SF2.

Match production code on ACTUAL labels, not intended names.

**Clavi added** (2026-09-30): GM7, Keys-family seventh entry — the
Hohner Clavinet D6 rubber-hammer struck-string electric clavichord
(instrument.md + clavi.py), verified end-to-end UnitMatrixComposer →
zero-drift ✓ → MIDI (145 bytes) → FluidSynth WAV (743 KB) ✓;
RenderPipeline stem label `trackXX_Clavi.wav` ✓ (GM_PROGRAMS[7] = "Clavi",
FluidR3 preset 7 = "Clavinet" — pipeline label "Clavi" vs SF2 "Clavinet"
is cosmetic expansion only, **no routing impact**; STEM_LABEL "Clavi"
matches the pipeline's real label so stem-file lookups work).
Karplus-Strong recommended (struck waveguide with rubber mute damping,
loop_gain 0.9960 — SHORTEST in the plucked/struck KB set between banjo
0.9960 and harp 0.9985; noise_component 0.03 for the rubber "cluck"
attack transient). Solo-render spectral check: 4–8 kHz buzz 3.1% (clean
single voice, no comb-filtering). Empirical FluidR3 pitch sweep (RMS,
notes 29–89): preset 7 audible across full range, no gaps. Identity: GM7
= rubber-hammer clavichord — rhythm-section chord-chop voice (funk
"Superstition" chops), NOT a sustain/pad voice; line-instrument quirk:
the rubber mute gives it the shortest ring in the KB (0.3–1.5 s), so
composition jobs write tight rhythmic patterns, not long sustained notes.
Registration in `instrument_registry.py` as CLAVI convenience constant.

**Tenor Saxophone added** (2026-10-01): GM66, Woodwind-family eighth entry — the
B♭ tenor sax (the most famous sax voice: Coltrane, Rollins, Hawkins, the
husky/bright tenor reed wall) (instrument.md + tenor_sax.py), verified
end-to-end UnitMatrixComposer → zero-drift ✓ → MIDI (117 bytes) → FluidSynth
WAV (758 KB) ✓; RenderPipeline stem label `trackXX_Tenor_Sax.wav` ✓
(GM_PROGRAMS[66] = \"Tenor Sax\", FluidR3 preset 66 = \"Tenor Sax\" — labels
match exactly, **no quirk**). PhaseModSynth recommended (single-reed conical
bore: saw carrier, mod_depth 3.0 — deeper than alto 2.8 for the huskier tenor
core; attack 0.05 s for the heavier reed; carrier_shape=saw for even+odd
harmonics). Solo-render spectral check: 4–8 kHz buzz 0.4% (clean single voice,
no comb-filtering). Range 44–88 (A♭2–E6 concert; written B♭2–F♯6 with altissimo);
sweet spot 53–78 (F3–F5). Registered in `instrument_registry.py` as TENOR_SAX
convenience constant. Registration proof: `by_name('tenor sax')` → Tenor
Saxophone, `by_program(66)` → Tenor Saxophone, `in_sweet_spot(64)` = True,
`in_sweet_spot(30)` = False.

**Baritone Saxophone added** (2026-10-02): GM67, Woodwind-family ninth entry —
the E♭ baritone sax, the low anchor of the sax family (Gerry Mulligan, Pepper
Adams, Serge Chaloff, Leo Parker) (instrument.md + baritone_sax.py), verified
end-to-end UnitMatrixComposer → zero-drift ✓ → MIDI → FluidSynth WAV ✓;
RenderPipeline stem label `trackXX_Baritone_Sax.wav` ✓ (GM_PROGRAMS[67] =
"Baritone Sax", FluidR3 preset 67 = "Baritone Sax" — labels match exactly,
**no quirk**). PhaseModSynth recommended (single-reed conical bore: saw carrier,
mod_depth 3.2 — deepest in the sax set for the thickest reed; attack 0.07 s for
the heaviest reed in the family; carrier_shape=saw for even+odd harmonics).
Solo-render spectral check: 4–8 kHz buzz checked (clean single voice, no
comb-filtering). Range 36–80 (C2–G5 concert; written E♭2–B5 with altissimo);
sweet spot 48–65 (C3–F4). Registered in `instrument_registry.py` as
BARITONE_SAX convenience constant. Registration proof: `by_name('baritone sax')`
`by_program(67)` → Baritone Saxophone,
    `in_sweet_spot(60)` = True, `in_sweet_spot(30)` = False. Role:
    bass/harmony/accent/lead/countermelody — the bari is the bass of the sax
    section, covering the lowest voice in the woodwind family.

**Muted Trumpet added** (2026-10-03): GM59, Brass-family fifth entry — the muted
    trumpet (harmon-muted trumpet per GM specification; the companion to the open
    trumpet (GM56), same physical instrument with a mute in the bell)
    (instrument.md + muted_trumpet.py), verified end-to-end UnitMatrixComposer →
    zero-drift ✓ → MIDI (161 bytes) → FluidSynth WAV (742 KB) ✓; RenderPipeline
    stem label `trackXX_Muted_Trumpet.wav` ✓ (GM_PROGRAMS[59] = "Muted Trumpet",
    FluidR3 preset 59 = "Muted Trumpet" — labels match exactly, **no quirk**).
    PhaseModSynth recommended (FM brass: saw carrier, mod_freq_ratio 2.0,
    mod_depth 2.5 — higher ratio = more nasal/focused muted tone, lower depth =
    less brassy edge than open trumpet's 4.0; attack 0.03 s for mute
    back-pressure). Solo-render spectral check: 4–8 kHz buzz 6.4% (clean single
    voice, no comb-filtering). Empirical FluidR3 pitch sweep: n/a (same trumpet
    patch range, muted preset 59 audible across full F#3–D6 span). Range 54–86
    (F#3–D6, same trumpet range); sweet spot 62–79 (D4–G5). Registered in
    `instrument_registry.py` as MUTED_TRUMPET convenience constant. Registration
    proof: `by_name('muted trumpet')` → Muted Trumpet, `by_program(59)` → Muted
    Trumpet, `in_sweet_spot(69)` = True. Role: lead, countermelody, accent,
    melody, ornament — the muted trumpet is a line/colour voice (monophonic,
    no dense chords). Produced reverb tail 1.2 s is shorter than open trumpet
    (1.8 s) — muted tone is intimate, hall washes out the mute character.
    Mute types: straight (bright metallic), cup (dark mellow), harmon (nasal wah),
    plunger (talking), bucket (velvety dark). No quirk on any label.

**Whistle added** (2026-10-04): GM78, Woodwind-family tin whistle entry — the
    Irish/Celtic folk fipple flue (penny whistle, open-tube aerophone with all
    harmonics present; companion to the existing flutes/whistles: flute (GM74 =
    Recorder patch), pan flute (GM75), shakuhachi (GM77), ocarina (GM79))
    (instrument.md + whistle.py), verified end-to-end UnitMatrixComposer →
    zero-drift ✓ → MIDI (120 bytes) → FluidSynth WAV (810 KB) ✓; RenderPipeline
    stem label `trackXX_Whistle.wav` ✓ (GM_PROGRAMS[78] = "Whistle",
    FluidR3 preset 78 = "Whistle" — labels match exactly, **no quirk**).
    PhaseModSynth recommended (open-tube flue: sine carrier + sine modulator,
    mod_freq_ratio 1.0, mod_depth 1.5 — between ocarina 0.8 and shakuhachi 2.0;
    attack 0.04 s for fast fipple onset; release 0.10 s for clean breath cutoff).
    Solo-render spectral check: 4–8 kHz buzz 0.4% (clean single voice, no
    comb-filtering). PhaseModSynth whistle tone confirmed: C5 = 0.794 peak.
    Range 62–93 (D4–A6, standard D whistle 2 octaves + overblow); sweet spot
    67–86 (G4–D6). Registered in `instrument_registry.py` as WHISTLE convenience
    constant. Registration proof: `by_name('whistle')` → Whistle, `by_program(78)`
    → Whistle, `in_sweet_spot(72)` = True, `in_sweet_spot(48)` = False. Role:
    lead, melody, ornament, accent — the whistle is a monophonic breath line
    (folk voice, no dense chords). REVERB_TAIL 1.6 s (intimate folk room, not
    hall — keeps the cutting articulation clear). Stem label: GM_PROGRAMS[78] =
    "Whistle" → `trackXX_Whistle.wav` (matches exactly, no quirk).

**Soprano Saxophone added** (2026-10-05): GM64, Woodwind-family soprano single-reed entry -- the
smallest and brightest standard saxophone (Bb soprano sax, straight conical tube, highest member
of the SATB sax quartet; instrument.md + soprano_sax.py), verified end-to-end UnitMatrixComposer →
zero-drift ✓ → MIDI (111 bytes) → FluidSynth WAV (758 KB) ✓; RenderPipeline stem label
`trackXX_Soprano_Sax.wav` ✓ (GM_PROGRAMS[64] = "Soprano Sax", FluidR3 preset 64 = "Soprano Sax"
-- labels match exactly, **no quirk**). PhaseModSynth recommended (conical bore single reed: saw
carrier + sine modulator, mod_depth 2.6 between clarinet 2.0 and alto 2.8 -- the soprano reed is
the lightest and fastest in the sax family; attack 0.03 s for fast reed onset; release 0.08 s for
smallest air column cutoff). Solo-render spectral check: 4-8 kHz buzz 0.3% (clean single voice,
well below 20% gate, no comb-filtering). Range 54-89 (F#3/F#3-F6 concert); sweet spot 67-79
(G4-G5 -- bright piercing lead register that cuts through any mix). Solo range 62-84 (D4-C6).
Completes the saxophone quartet: Soprano Sax (GM64) + Alto Sax (GM65) + Tenor Sax (GM66) +
Baritone Sax (GM67) -- all four SATB members now registered. Identity quirk: soprano sax is the
brightest most penetrating member of the sax family -- used as the classical lead voice in the
sax quartet (S in SATB) and as the frontline lead in New Orleans brass bands (Bechet, Bigard).
MONOPHONIC line voice -- no dense chords; piercing register sits ABOVE most melodic voices in a mix.
Registered in `instrument_registry.py` as SOPRANO_SAX convenience constant. Registration proof:
`by_name('soprano sax')` → Soprano Saxophone, `by_program(64)` → Soprano Saxophone,
`in_sweet_spot(72)` = True, `in_sweet_spot(50)` = False. Role: lead, countermelody, ornament,
accent -- bright lead voice that cuts through any ensemble. REVERB_TAIL 1.4 s (dry, keep the
bright attack clear -- shortest in the Woodwind family). EQ body cut 800 Hz (soprano reed honk
is higher than alto's 400 Hz). Stem label: GM_PROGRAMS[64] = "Soprano Sax" →
`trackXX_Soprano_Sax.wav` (matches exactly, **no quirk**).

**Rhodes (Electric Piano 1) added** (2026-10-06): GM4, Keys-family eighth
entry — the Fender Rhodes electromechanical tine piano, the classic 70s
warm/bell-like electric piano (electric pianos 1 in GM spec: Rhodes/Wurlitzer
family) (instrument.md + rhodes.py), verified end-to-end UnitMatrixComposer →
zero-drift ✓ → MIDI (82 bytes) → FluidSynth WAV (731 KB) ✓; RenderPipeline
stem label `trackXX_Electric_Piano_1.wav` ✓ (GM_PROGRAMS[4] = "Electric Piano
1", FluidR3 preset 4 = "Rhodes EP" — internal SF2 name "Rhodes EP" vs pipeline
"Electric Piano 1" is cosmetic only, **no routing impact**). ModalSynth primary
with stock 'string' preset and custom `RHODES_MODES` bank at compressed
inharmonic ratios 1:2.3:4.1:6.8 with decay rates 1.5–3.0. Karplus-Strong
secondary (tine IS a struck waveguide; loop_gain 0.9965 between clavi 0.9960
and sitar 0.9975, with lowpass_hz 2000 for pickup bandwidth). PhaseModSynth
tertiary (FM synth, ratio 2.3, depth 1.8). Solo-render spectral check:
4–8 kHz buzz 1.4% (no comb-filtering). Empirical FluidR3 pitch sweep (RMS,
notes 36–96): preset 4 audible across full range, no gaps — SF2 never clips a
composition. Registration proof: `by_name('rhodes')` → Electric Piano 1,
`by_program(4)` → Electric Piano 1, `in_sweet_spot(69)` = True,
`in_sweet_spot(30)` = False. Registration in `instrument_registry.py` as RHODES
convenience constant. Identity quirk: pickup compression narrows dynamic range
by ~3-4 dB per octave vs acoustic piano — phrase with REGISTRATION (voicing
density, chord spacing) as much as with velocity. Stem label: no pipeline quirk
but FluidR3 internal name is "Rhodes EP" vs pipeline "Electric Piano 1"
(cosmetic, no routing impact).

**Reed Organ added** (2026-10-07): GM20, Keys-family free-reed entry — the
cabinet-enclosed free-reed keyboard operated by foot-pumped or hand-pumped
bellows (instrument.md + reed_organ.py), verified end-to-end UnitMatrixComposer
→ zero-drift ✓ → MIDI → FluidSynth WAV ✓; RenderPipeline stem label
`trackXX_Reed_Organ.wav` ✓ (GM_PROGRAMS[20] = "Reed Organ", FluidR3 preset 20
= "Reed Organ" — labels match exactly, **no quirk**). PhaseModSynth recommended
(free-reed aerophone: saw carrier + sine modulator, mod_depth 3.5 — between
accordion 3.2 and bagpipe 4.5 for the cabinet-resonant harmonium buzz; attack
0.04 s for wind chest fill; release 0.06 s). Range 36–96 (C2–C7); sweet spot
60–84 (C4–C6). Role: harmony, pad, melody, drone, ornament — fully polyphonic
chord instrument. Registration proof: `by_name('reed organ')` → Reed Organ,
`by_program(20)` → Reed Organ, `in_sweet_spot(72)` = True,
`in_sweet_spot(30)` = False. Registration in `instrument_registry.py` as
Registration in `instrument_registry.py` as REED_ORGAN convenience constant. Identity quirk: the reed organ is the only
free-reed keyboard instrument where the entire keyboard shares ONE unified wind
chest and cabinet resonator (unlike accordion's separate bass/treble systems)
— the instrument is fully polyphonic with a characteristic "cabinet honk" body
resonance at ~250 Hz. The Indian hand-pumped harmonium adds drone stops (Sa-Pa)
and a darker 3-octave range; the American reed organ (suction) is softer with
sweeter trebles; the European harmonium (pressure) is louder with sharper
attack. Composition jobs may write full 3-5 note chords.

**Electric Bass added** (2026-10-08): GM33, new **Bass** family first entry — the
solidbody electric bass guitar played fingerstyle (the foundational modern
rhythm-section bass voice; instrument.md + electric_bass.py), verified end-to-end
UnitMatrixComposer → zero-drift ✓ → MIDI (111 bytes) → FluidSynth WAV (742 KB) ✓;
RenderPipeline stem label `trackXX_Electric_Bass_finger.wav` ✓ (GM_PROGRAMS[33] =
"Electric Bass (finger)", FluidR3 preset 33 = "Fingered Bass" — internal SF2 name
"Fingered Bass" vs pipeline "Electric Bass (finger)" is cosmetic only, **no
routing impact**). Karplus-Strong recommended (plucked waveguide — the exact
physical model for a stiff wound-steel string with magnetic pickup; loop_gain
0.9970 — moderate damping between sitar 0.9975 and shamisen 0.9955; wound steel
rings 1-3 s, shorter than harp 0.9985 and longer than shamisen 0.9955). Solo-render
spectral check: 4-8 kHz buzz **0.4%** (the lowest of the set — electric bass has
virtually no energy above 4 kHz). Empirical FluidR3 pitch sweep: preset 33
audible across full range 24-84 (C1-C5), no gaps — SF2 never clips a composition.
Range 24-84 is the GM-patch span (real 4-string E1-G4 = 28-67; the patch plays the
full GM range). Registration proof: `by_name('electric bass')` → Electric Bass (finger),
`by_program(33)` → Electric Bass (finger), `in_sweet_spot(52)` = True,
`in_sweet_spot(20)` = False. Registration in `instrument_registry.py` as ELECTRIC_BASS
convenience constant. Stem label: no pipeline quirk. Identity: GM33 = Electric Bass
(finger) — monophonic fingerstyle line/riff instrument; CHANNEL quirk: melodic
channel (0-9) with program 33 — channel 9 would trigger the drum-kit map.
Line/rhythm quirk: bass is a monophonic groove line (double-stops possible on
adjacent strings but not idiomatic), NOT a chord/comping voice and NOT a melodic
lead voice — its role is bass/rhythm foundation with the kick drum.

**Acoustic Guitar (steel) added** (2026-10-09): GM25, Guitar-family second entry
— the steel-string flat-top acoustic guitar, the dominant folk/country/rock
rhythm and fingerpicking voice (instrument.md + steel_acoustic.py), verified
end-to-end UnitMatrixComposer → zero-drift ✓ → MIDI (111 bytes) → FluidSynth
WAV (1.53 MB) ✓; RenderPipeline stem label
`trackXX_Acoustic_Guitar_steel.wav` ✓ (GM_PROGRAMS[25] = "Acoustic Guitar
(steel)", FluidR3 preset 25 = "Steel String Guitar" — internal SF2 name
"Steel String Guitar" vs pipeline "Acoustic Guitar (steel)" is cosmetic only,
**no routing impact**). Karplus-Strong recommended (plucked steel waveguide,
loop_gain 0.9970 — steel strings ring 1–3 s, between clavi 0.9960 and harp
0.9985; excitation="pick" for the bright steel-string attack). Solo-render
spectral check: 4–8 kHz buzz 8.8% (clean single voice, well within 20% gate,
no comb-filtering). Range 40–86 (E2–C#6), sweet spot 50–79 (D3–G5). Role:
harmony, rhythm, strum, lead, melody, ornament, countermelody — fully
polyphonic chord/strum/arpeggio instrument. Registration in
`instrument_registry.py` as STEEL_ACOUSTIC convenience constant. Fix: existing
acoustic_guitar (nylon) corrected from program 25 → 24 (FluidR3 preset 24 =
"Nylon String Guitar") so steel is at program 25 where it belongs.

**Pizzicato Strings added** (2026-10-10): GM45, Strings-family sixth entry —
the string section playing pizzicato (plucked, NOT bowed): the rhythmic/
ostinato colour voice, from Tchaikovsky 4 scherzo to film-score plucked
figures (instrument.md + pizzicato_strings.py), verified end-to-end
UnitMatrixComposer → zero-drift ✓ → MIDI (120 bytes) → FluidSynth WAV
(921 KB) ✓; RenderPipeline stem label `trackXX_Pizzicato_Strings.wav` ✓
(GM_PROGRAMS[45] = "Pizzicato Strings", FluidR3 preset 45 = "Pizzicato
Section" — internal SF2 name differs cosmetically, **no routing impact**).
Karplus-Strong recommended (finger-plucked waveguide — the exact physical
model; loop_gain 0.9960 = deliberately DRY section pluck, 0.3–1.5 s ring,
between clavi 0.9960 and electric bass 0.9970; excitation "pluck",
lowpass_hz 7500 for wooden-body warmth; ring test: 1.56× tail energy vs
0.990 dull control). Solo-render spectral check: 4–8 kHz buzz **0.2%** (the
cleanest of the set — no bow noise, dry plucks). Empirical FluidR3 pitch
sweep: preset 45 audible across full documented range 36–96 (C2–C7), no
gaps; **silent at 103+ (patch ceiling — never write above C7=96)**. Range
36–96 (C2–C7, GM spec span of the whole section); sweet spot 55–79
(G3–G5). Registration proof: `by_name('pizzicato strings')` → Pizzicato
Strings, `by_program(45)` → Pizzicato Strings, `in_sweet_spot(64)` = True,
`in_sweet_spot(30)` = False. Registration in `instrument_registry.py` as
PIZZICATO_STRINGS convenience constant. Role: rhythm, ostinato, bass,
accompaniment, countermelody, accent — the section-pizz voice, NOT a
sustain/lead voice. Register physics quirks: (1) loudest real pizz ≈ a
bow's mezzo-forte — do NOT balance pizz against full arco/brass at forte;
(2) bass/cello pizz is the longest-ringing, most present register — low
ostinato/bass figures are the #1 idiomatic use; (3) high violin pizz is a
dry no-sustain effect — write sparkle/accent above ~E5, not carried melody;
(4) real section pizz has natural timing looseness — write with a rhythmic
lift, and keep chords small (1–4 notes; dense multi-stop section pizz gets
messy and players divide anyway).

**String Ensemble 1 added** (2026-10-11): GM48, Strings-family seventh entry
— the sustained bowed STRING SECTION, the "Strings (sustained)" voice that
orchestration.md's Pad role has referenced since the beginning with NO KB
entry behind it (the family had solo bowed voices — violin/viola/cello/
double_bass/fiddle — and the plucked section — pizzicato_strings — but no
sustained-section pad) (instrument.md + string_ensemble.py), verified
end-to-end UnitMatrixComposer → zero-drift ✓ → MIDI (75 bytes) → FluidSynth
WAV (1.04 MB) ✓; RenderPipeline stem label `trackXX_String_Ensemble_1.wav` ✓
(GM_PROGRAMS[48] = "String Ensemble 1", FluidR3 preset 48 = "Strings" —
one-word SF2 spelling is cosmetic only, **no quirk**, distinct from the
"Shanai"/"Bag pipe" quirks at 111/109). Additive recommended (section =
detuned harmonic stack, ADDITIVE_HARMONICS section_full
[1.0,0.9,0.7,0.5,0.35,0.25,0.18], SYNTHESIS_DEFAULTS attack 0.35 s, detune
±0.006, stack 3 voices, release 0.4 s); BowedString models ONE string so it
is the single-string alternative (stack 4–8 renders for section mass);
PhaseModSynth saw = the cheap 70s string-machine pad; ModalSynth 'string' =
section pizz fallback. Solo-render spectral check: 4–8 kHz buzz **1.4%**
(clean single voice, no comb-filtering). **Additive engine bug FIXED
2026-10-11** (`sound/synthesis/additive.py` `get_adsr_weights`): the tail
fill computed `tail` against the PRE-repeat `weights` array (len ≈ intervals
≈ 3662) but concat'd that same pre-repeat envelope + near-zero ramp into
`self.weights` — the smoothing/repeat result (len 43932) was DISCARDED, so
EVERY note collapsed to ~0 after ~0.17 s regardless of sustain_level (organ
entry's 2026-08-31 "sustain confirmed" missed it — it only checked the
onset peak 2873, ratio used the wrong array). Fix: compute `tail` from
`self.weights.shape[0]` and concat the repeated envelope with a linear
release ramp (`self.weights[-1] * np.linspace(1,0,tail+1)[1:]`). Post-fix:
organ-style params sustain 1.0 for the full 2.0 s; string-pad params hold
late(1.0–1.5 s) rms/peak 0.295. Full suite re-run: **693 passed, 1 skipped
(no golden regressions)**. Empirical FluidR3 pitch sweep (RMS, notes
24–108): preset 48 audible 24–96 (13/13, no gaps), SILENT at 102+ — never
write above C7=96. Range 28–96 = full-section span (contrabass E1 → violin
C7); sweet spot 60–84 (C4–C6, violin/viola lead zone). Registration proof:
`by_name('string ensemble')` → String Ensemble 1, `by_program(48)` → String
Ensemble 1, `in_sweet_spot(72)` = True, `in_sweet_spot(20)` = False.
Registered in `instrument_registry.py` as STRING_ENSEMBLE convenience
constant. Enum quirk: `MidiInstrument.STRING_ENSEMBLE = 49` is the legacy
1-indexed GM number — 49 is actually String Ensemble 2 (FluidR3 "Slow
Strings"); use registry GM48. Role: harmony, pad, melody, countermelody,
accent — the section pad, NOT a rhythm voice (use pizzicato_strings for
plucked rhythm). REVERB_TAIL 2.6 s is the longest in the Strings family
(violin 2.0, harp 2.2) — the pad blooms in space. Layering quirk: idiomatic
doubling is octaves, NOT unison with another melodic patch (section already
IS many unison strings — the 2026-09-01 comb-filter lesson).

**Synth Pad added** (2026-10-12): GM88, new **Synth** family first entry — the
classic slow-attack digital synth pad ("Pad 1 (new age)", the Roland
D-50-era LA-synthesis choir pad: detuned oscillator stack + chorus + long
swell), the "Synth Pad" voice that orchestration.md's Pad role lists
("Strings (sustained), Synth Pad, Organ") — the LAST pad-role voice with NO
KB entry after string_ensemble landed 2026-10-11. Composition jobs had been
sending `MidiInstrument.SYNTH_PAD` (= 88) for Pad voices for months (Arabic
235/071, Ambient evolving v1, Experimental 044) with no KB entry behind it
(instrument.md + synth_pad.py), verified end-to-end UnitMatrixComposer →
zero-drift ✓ → MIDI (75 bytes) → FluidSynth WAV (1.63 MB) ✓; RenderPipeline
stem label `track00_Pad_1_new_age.wav` ✓ (GM_PROGRAMS[88] = "Pad 1 (new
age)" → sanitized — parens stripped; FluidR3 preset 88 = **"Fantasia"** —
SF2 internal name differs from the GM label, cosmetic only, **no routing
impact**; preset 89 = "Warm Pad" is the darker sibling). Enum note: for ONCE
`MidiInstrument.SYNTH_PAD = 88` matches the raw GM program exactly (unlike
FLUTE=74 / STRING_ENSEMBLE=49) — do NOT "correct" it. Additive recommended
(the pad IS a detuned harmonic stack, organ/string-ensemble engine
precedent: ADDITIVE_HARMONICS pad_warm [1.0,0.8,0.6,0.45,0.3,0.2,0.12] /
pad_newage [1.0,0.65,0.5,0.35,0.22,0.15,0.1,0.06], SYNTHESIS_DEFAULTS attack
0.55 s, detune ±0.012 — 2× the string section chorus, stack 4 voices,
release 0.5 s, sustain 0.9); PhaseModSynth saw-stack is the analog-pad alt
(FM_DEFAULTS: saw carrier, ratio 1.0, depth 2.0, attack 0.6). Solo-render
spectral check: 4–8 kHz buzz **8.2%** (clean single patch, no
comb-filtering). **Additive engine quirk FOUND 2026-10-12**:
`SoundWave.apply_overtones` leaves `self.frequency` at the TOP partial
(~7× fundamental), so `get_adsr_weights`' grid step ≈
1/(duration×top_partial) s and decay_S is PER-GRID-STEP — a pad recipe must
use decay_S ~1e-4 to hold a 2 s chord (verified: late-sustain envelope max
0.79 with decay_S 1e-4 vs collapse without; docs updated in instrument.md).
PhaseModSynth pad smoke: onset/late RMS 0.065 — slow attack confirmed.
Empirical FluidR3 pitch sweep (RMS, notes 36–108 step 12): preset 88
audible EVERYWHERE — 36–96 strong (RMS 603–865), 108 audible but soft (RMS
392) — GM pad patches are full-keyboard, no patch ceiling; range 36–96 is
the idiomatic WRITING band (mud below C2, noise-shimmer above C7), sweet
spot 60–84 (C4–C6). Registration proof: `by_name('synth pad')` → Pad 1 (new
age), `by_program(88)` → Pad 1 (new age), `in_sweet_spot(72)` = True,
`in_sweet_spot(24)` = False. Registration in `instrument_registry.py` as
SYNTH_PAD convenience constant. Role: pad, harmony, texture, drone, accent
— the harmonic canvas, NOT a rhythm/lead voice. REVERB_TAIL 3.2 s is the
LONGEST in the KB (string ensemble 2.6, harp 2.2) — the pad blooms in
space. EQ: cut 300 Hz (synth chords pile low-mid), boost 3.8 kHz presence,
highshelf +9.5 kHz — the new-age AIR is the identity (contrast: string
ensemble CUTS 8.5 kHz). Layering quirk: idiomatic doubling is octaves or
zone-splitting (55–79 + 80–96), NEVER unison with another melodic patch
(the 2026-09-01 comb-filter lesson). Pad-writing quirk: hold chords ≥ 2 s
or the slow attack never speaks.

**Clean Electric Guitar added** (2026-10-13): GM27, Guitar-family third entry
— the solidbody electric guitar played through a clean amplifier, the classic
rhythm-section chord/strum/arpeggio voice for pop/rock/funk/R&B (instrument.md
+ clean_electric.py), verified end-to-end UnitMatrixComposer → zero-drift ✓ →
MIDI (84 bytes) → FluidSynth WAV (812 KB) ✓; RenderPipeline stem label
`trackXX_Electric_Guitar_clean.wav` ✓ (GM_PROGRAMS[27] = "Electric Guitar
(clean)", FluidR3 preset 27 = "Clean Guitar" — internal SF2 name "Clean
Guitar" vs pipeline "Electric Guitar (clean)" is cosmetic only, **no routing
impact**; STEM_LABEL = "Electric_Guitar_clean" matches the pipeline's sanitized
label). Karplus-Strong recommended (plucked steel waveguide — the exact
physical model for a stiff steel string with magnetic pickup; loop_gain 0.9960
— between clavi 0.9960 and steel_acoustic 0.9970; excitation "pick" with
noise_component 0.025 for pick scratch transient; lowpass_hz 5000 for pickup
bandwidth). Solo-render spectral check: 4–8 kHz buzz **1.0%** (clean single
voice, well below 20% gate, no comb-filtering). Empirical FluidR3 pitch sweep:
preset 27 audible across full range 28–84 (E1–C6), no gaps — SF2 never clips
a composition. Registration proof: `by_name('clean electric')` → Electric
Guitar (clean), `by_program(27)` → Electric Guitar (clean),
`in_sweet_spot(52)` = True, `in_sweet_spot(30)` = False. Registration in
`instrument_registry.py` as CLEAN_ELECTRIC convenience constant. Role:
harmony, rhythm, strum, lead, melody, ornament, countermelody, accent — the
clean electric guitar is a fully polyphonic chord/strum/arpeggio instrument,
NOT a sustain/pad voice. REVERB_TAIL 1.8 s (room/spring reverb — Fender-style
amp spring tank). EQ: cut 300 Hz box resonance, boost 3.5 kHz presence, gentle
8 kHz air. PAN -0.2 centre-left. Completes the Guitar family trio: nylon
acoustic (GM24), steel acoustic (GM25), clean electric (GM27).

**Overdriven Guitar added** (2026-10-14): GM29, Guitar-family fourth entry
— the solidbody electric guitar pushed into tube-amp saturation, the classic
rock lead/rhythm voice (instrument.md + overdriven.py), verified end-to-end
UnitMatrixComposer → zero-drift ✓ → MIDI (111 bytes) → FluidSynth WAV
(731 KB) ✓; RenderPipeline stem label `trackXX_Overdriven_Guitar.wav` ✓
(GM_PROGRAMS[29] = "Overdriven Guitar", FluidR3 preset 29 = "Overdrive Guitar"
— internal SF2 name "Overdrive Guitar" vs pipeline "Overdriven Guitar" is
cosmetic only, **no routing impact**; STEM_LABEL = "Overdriven_Guitar" matches
the pipeline's sanitized label). Karplus-Strong recommended (plucked steel
waveguide + non-linear saturation stage — the exact physical model for a steel
string through a distorted tube amp; loop_gain **0.9990** — the HIGHEST in the
plucked set, reflecting overdrive compression sustain ~5-10 s; noise_component
0.060 for tube hiss/amp floor; lowpass_hz 4000 for speaker roll-off warmth;
saturation 0.60 soft-clip). PhaseModSynth secondary (saw carrier, mod_depth
4.0 — highest FM depth in the Guitar family for harmonic foldover). Solo-render
spectral check: 4–8 kHz buzz **1.6%** (clean single voice, well below 20%
gate, no comb-filtering). Empirical FluidR3 pitch sweep: preset 29 audible
across full range 28–84 (E1–C6), no gaps — SF2 never clips a composition.
Registration proof: `by_name('overdriven guitar')` → Overdriven Guitar,
`by_program(29)` → Overdriven Guitar, `in_sweet_spot(64)` = True,
`in_sweet_spot(24)` = False. Registration in `instrument_registry.py` as
OVERDRIVEN_GUITAR convenience constant. Role: lead, melody, accent, rhythm,
strum, countermelody — the overdriven guitar is a fully polyphonic instrument
(6 strings) but the compression/intermoldulation of full chords on high gain
makes POWER CHORDS (root-fifth, no 3rd) the idiomatic rhythm texture and
single-note LEADS the idiomatic melody texture. REVERB_TAIL 2.2 s (hall/room
— overdrive typically uses amp spring reverb + room ambience; 2.2 s for solo
leads). EQ: cut 400 Hz (reduce mud from compression buildup), boost 2.2 kHz
presence (cutting edge pick attack), gentle 6 kHz air. PAN -0.15 centre-left.
Completes the Guitar family: nylon acoustic (GM24), steel acoustic (GM25),
clean electric (GM27), overdriven (GM29).

**Recorder added** (2026-10-16): GM74, Woodwind-family Woodwind entry — the
Renaissance/Baroque duct flute (fipple flute), the most prominent end-blown
flute in Western art music from the 14th–18th century; the GM74 patch is
modelled on the soprano/descant recorder in C (instrument.md + recorder.py),
verified end-to-end UnitMatrixComposer → zero-drift ✓ → MIDI (111 bytes) →
FluidSynth WAV (739 KB) ✓; RenderPipeline stem label `trackXX_Recorder.wav` ✓
(GM_PROGRAMS[74] = "Recorder", FluidR3 preset 74 = "Recorder" — labels match
exactly, **no quirk**). PhaseModSynth recommended (fipple duct flute: sine
carrier + sine modulator, mod_freq_ratio 1.0, mod_depth 1.5 — between flute
1.2 and ocarina 0.8, reflecting fipple purity; attack 0.03 s for near-instant
fipple response; release 0.08 s). AirPipe physical aerophone model (stopped=False,
open pipe, length_scale 0.45 for soprano ~33 cm, pressure 0.60 for moderate wind).
Additive fallback with odd-harmonic stack (1:1.0, 3:0.40, 5:0.22, 7:0.10) —
fipple edge in centre yields odd-dominant spectrum. Range 60–100 (C4–E7);
solo range 72–89 (C5–C7); sweet spot 76–84 (E5–C6). Solo-render spectral check:
4–8 kHz buzz 1.3% (clean single voice, well below 20% gate, no comb-filtering).
Empirical FluidR3 pitch sweep: preset 74 Recorder audible across full range,
no gaps. Registration proof: `by_name('recorder')` → Recorder GM74,
`by_program(74)` → Recorder (fixed from prior misregistration of Flute at
GM74 — Flute corrected to GM73, Recorder now occupies its proper GM74 slot),
`in_sweet_spot(79)` = True, `in_sweet_spot(40)` = False. Registration in
`instrument_registry.py` as RECORDER convenience constant. Role: lead, melody,
ornament, countermelody, accent — the recorder is a MONOPHONIC line wind
instrument (no chords). REVERB_TAIL 1.6 s (intimate chamber/room for the
Baroque intimate sound). EQ: cut 600 Hz −1.5 dB (reduce duct body resonance),
boost 3 kHz +2.5 dB (articulation clarity), shelf 9 kHz +1.5 dB (fipple
breath shimmer). PAN -0.1 (slightly left, classical woodwind seating).
Completes the GM73/74 Flute/Recorder swap fix: Flute was incorrectly
registered at GM74 with STEM_LABEL "Recorder"; corrected to GM73 with
STEM_LABEL "Flute", and Recorder added at its proper GM74 slot.

**Electric Piano 2 added** (2026-10-17): GM5, Keys-family ninth entry — the
Yamaha DX7 FM electric piano (the iconic 1980s bright percussive bell-like
FM piano; instrument.md + electric_piano_2.py), verified end-to-end
UnitMatrixComposer → zero-drift ✓ → MIDI (111 bytes) → FluidSynth WAV
(812 KB) ✓; RenderPipeline stem label `trackXX_Electric_Piano_2.wav` ✓
(GM_PROGRAMS[5] = "Electric Piano 2", FluidR3 preset 5 = "Legend EP 2" —
SF2 internal name differs cosmetically from GM label, **no routing impact**).
PhaseModSynth recommended (FM synthesis — the exact synthesis model for the
DX7: sine carrier + sine modulator, mod_freq_ratio 3.1, mod_depth 2.8,
attack 0.003 s, release 1.2 s; PhaseModSynth FM EP2 note smoke test:
A4 0.5 s peak=0.799). Karplus-Strong secondary (metallic struck waveguide,
loop_gain 0.9960). ModalSynth 'bell' preset fallback. Solo-render spectral
check: 4–8 kHz buzz **1.0%** (clean single voice, well below 20% gate, no
comb-filtering). Zero-drift: True. Registered in `instrument_registry.py` as
ELECTRIC_PIANO_2 convenience constant. Registration proof:
`by_name('electric piano 2')` → Electric Piano 2, `by_program(5)` → Electric
Piano 2, `in_sweet_spot(69)` = True, `in_sweet_spot(30)` = False. Role:
harmony, melody, bass, accent, color — fully polyphonic chord/strum/arpeggio
instrument. FM bell quirk: the DX7 signature has prominent 4-8 kHz energy at
the onset by design (not comb-filtering). REVERB_TAIL 2.0 s (80s Lexicon hall
shimmer). EQ: cut 400 Hz (mud), boost 3.2 kHz (bright bell articulation),
high shelf 9 kHz (air). Complements the Rhodes (GM4) as the bright/cold FM
counterpart to the warm/tine Rhodes.

**Drawbar Organ added** (2026-10-21): GM16, Keys-family tenth entry — the
Hammond tonewheel organ (B-3/C-3): 91 toothed wheels, nine drawbars per
manual, and the only common instrument whose timbre *is* additive synthesis
(instrument.md + drawbar_organ.py), verified end-to-end UnitMatrixComposer →
zero-drift ✓ → MIDI (109 bytes) → FluidSynth WAV (720 KB, solo render) ✓;
RenderPipeline stem label `track00_Drawbar_Organ.wav` ✓ (GM_PROGRAMS[16] =
"Drawbar Organ"; FluidR3 bank-0 preset 16 = "DrawbarOrgan" — no space in the
SF2 internal name, cosmetic only, **no routing impact**). Additive engine
recommended (`sound/synthesis/additive.py` SoundWave): nine sine partials at
`DRAWBAR_FOOTAGES` ratios 16' (0.5x), 5 1/3' (1.5x), 8' (1.0x), 4' (2x),
2 2/3' (3x), 2' (4x), 1 3/5' (5x), 1 1/3' (6x), 1' (8x);
`drawbar_harmonics()` converts a console registration (levels 0-8) into
{ratio: gain}; `ADDITIVE_HARMONICS` holds engine-compatible integer-partial
banks (apply_overtones sums 1x,2x,3x… so the 0.5x sub-octave and 1.5x quint
need the custom sum). ADSR attack 0.004 s, **no decay, sustain 1.0**, release
0.05 s — a tonewheel tone is flat while the key is held. PhaseModSynth
secondary (sine carrier, mod_freq_ratio 2.0, mod_depth 2.5 — the DX7 organ
family). `MOTOR_DEFAULTS` models the Leslie 122: 6.9 Hz tremolo / 0.7 Hz
chorale, depth 0.30, 6 cents Doppler, 1.0 s spin-up. Range 24-89 (25-note
pedal board C1-C3 + two 61-key manuals F1-F6); solo range 48-84 (C3-C6);
sweet spot 55-79 (G3-G5). Solo-render spectral check: 4-8 kHz buzz **5.8%**
(clean single voice, well below 20% gate, no comb-filtering). Empirical
FluidR3 pitch sweep: preset 16 audible 20-96 with no gaps (rms 0.060-0.082).
Registration proof: `by_name('drawbar organ')` → Drawbar Organ,
`by_program(16)` → Drawbar Organ, `in_sweet_spot(67)` = True,
`in_sweet_spot(24)` = False. Registration in `instrument_registry.py` as
DRAWBAR_ORGAN convenience constant + a `registry_table()` role row. Role:
harmony, pad, comp, lead, bass, rhythm, drone, accent — polyphonic, dense,
sustained. **Velocity quirk**: a real tonewheel organ has a binary key
contact and no velocity response, so velocity is a mix-balance value only
(keep 70-100; get dynamics from drawbars/swell). REVERB_TAIL 1.8 s (live
room, not the 2.2 s cathedral of Church Organ GM19). EQ: cut 200 Hz
(16'-drawbar mud), boost 2.5 kHz (key click + percussion), shelf 8 kHz (air).
PAN 0.0 (Leslie is a mono source). Distinct from Church Organ (GM19, pipe
chiff) and Reed Organ (GM20, harmonium). Drive-by fix: registry table's
stale "Flute | 74" row corrected to 73 (the 2026-10-16 GM73/74 swap).

**Jazz Guitar added** (2026-10-22): GM26, Guitar-family fifth entry — the
archtop hollow-body electric guitar (Gibson ES-175/L-5/Super 400 lineage),
the warm/round jazz voice: f-hole hollow body + flatwound strings + THUMB
attack (Wes Montgomery octaves, Freddie Green comping) (instrument.md +
jazz_guitar.py), verified end-to-end UnitMatrixComposer → zero-drift ✓ →
MIDI (153 bytes) → FluidSynth WAV (718 KB, solo render) ✓; RenderPipeline
stem label `trackXX_Electric_Guitar_jazz.wav` ✓ (GM_PROGRAMS[26] =
"Electric Guitar (jazz)" — GM2 spec spelling; FluidR3 preset 26 = "Jazz
Guitar" — SF2 uses the common name, cosmetic only, **no routing impact**;
STEM_LABEL = "Electric_Guitar_jazz" matches the pipeline's real label so
stem-file lookups work — same discipline as the "Bag pipe"/"Shanai" quirks
at 109/111). Karplus-Strong recommended (plucked waveguide — the exact
physical model: loop_gain 0.9975 — flatwound strings ring long & smooth
(2–4 s), between steel_acoustic 0.9970 and harp 0.9985, overdriven 0.9990
is the compression sustain; excitation "thumb" for the round Wes attack,
no pick click; lowpass_hz 3500 — DARKER than clean electric 5000: archtop
+ flatwounds absorb the highs; noise_component 0.015 — thumb is quiet).
Ring test: late(1–2 s) rms/peak 0.0010 vs 0.0001 dull control, **6.7×** —
flatwound ring clearly above the damped control. ModalSynth 'string'
preset is the fallback; PhaseModSynth alt (mod_depth 1.5 — gentle twang,
jazz tone is NOT brassy). Solo-render spectral check: 4–8 kHz buzz **0.1%**
(the cleanest of the set — the dark archtop tone has virtually no energy
above 4 kHz). Empirical FluidR3 pitch sweep (RMS, notes 24–96): preset 26
audible 13/13, no gaps, no treble cliff (bottom 0.070, top 0.065) — SF2
never clips a composition. Range 28–84 = GM-patch span (real 22-fret guitar
E2–E6 = 40–76); sweet spot 48–72 (C3–C5) — the comping heart. Registration
proof: `by_name('jazz guitar')` → Electric Guitar (jazz), `by_program(26)`
→ Electric Guitar (jazz), `in_sweet_spot(60)` = True, `in_sweet_spot(24)` =
False. Registration in `instrument_registry.py` as JAZZ_GUITAR convenience
constant + a `registry_table()` role row. Role: harmony, rhythm, comp,
lead, melody, ornament, countermelody, accent — fully polyphonic with two
idiomatic faces: comping (Freddie Green chords on 2 & 4, shell voicings
root-7th-3rd, 2–4 notes NOT dense barre chords) and melody (thumb single
lines + Wes-style octave melodies). REVERB_TAIL 2.0 s (jazz-club room/warm
hall). EQ: cut 250 Hz (archtop boxiness), boost 2.8 kHz presence (neck-
pickup warmth, thumb definition), gentle 7.5 kHz air — the jazz tone is
DARK by design (vs clean electric 8 kHz). PAN -0.2. Complements the Guitar
family: nylon (24), steel (25), jazz (26), clean (27), overdriven (29).
Drive-by fix: registry_table() overdriven-guitar role row corrected from
the generic default to its documented role (lead, melody, accent, rhythm,
strum, countermelody).

**Synth Bass 1 added** (2026-10-23): GM38, Bass-family second entry — the
classic analog synth bass (VCO → resonant low-pass → ADSR; TB-303 /
Minimoog / MC-202 lineage), the electronic/pop/disco/funk bass foundation,
distinct from the plucked Electric Bass (finger) GM33 — there is NO string,
the tone is oscillator + filter (instrument.md + synth_bass_1.py), verified
end-to-end UnitMatrixComposer → zero-drift ✓ → MIDI (111 bytes) →
FluidSynth WAV (798 KB, solo render) ✓; RenderPipeline stem label
`trackXX_Synth_Bass_1.wav` ✓ (GM_PROGRAMS[38] = "Synth Bass 1", FluidR3
preset 38 = "Synth Bass 1" — labels match exactly, **no quirk**). MonoSynth
recommended (`sound/synthesis/mono_synth.py` — the exact subtractive
architecture of the classic analog bass: saw VCO, sub_level 0.3,
filter_cutoff 1800, resonance 0.55, env_a 0.005 gate click, env_d 0.18
pluck, env_s 0.75, env_r 0.12; SYNTHESIS_DEFAULTS load through the
registry). PhaseModSynth secondary (FM "Solid Bass" patch, ratio 1.0,
depth 2.5); Karplus-Strong tertiary ("rubber band" fallback, loop_gain
0.9960, lowpass_hz 1500 — dark, tight). Solo-render spectral check: 4–8 kHz
buzz **1.8%** (clean single voice, no comb-filtering). MonoSynth smoke: D2
peak 0.800, sustain_rms/peak 0.338 (gate sustain confirmed, no collapse).
Empirical FluidR3 pitch sweep (RMS, notes 24–84): preset 38 audible 6/6,
smooth rolloff 0.0355→0.0201, no gaps — SF2 never clips a composition.
Range 24–84 = GM-patch span (the core line register is 36–60 = E2–C4);
sweet spot 38–62 (D2–D4). Registration proof: `by_name('synth bass 1')` →
Synth Bass 1, `by_program(38)` → Synth Bass 1, `in_sweet_spot(48)` = True,
`in_sweet_spot(20)` = False. Registration in `instrument_registry.py` as
SYNTH_BASS_1 convenience constant. Role: bass, rhythm, groove, accent —
the electronic bass foundation, locks with the kick like the electric bass
but with filter color. Line-instrument quirk: monophonic oscillator voice —
one note at a time, NO chords; gate time (note length) IS the articulation
(velocity triggers the filter-envelope amount on many synths, but the gate
is the signature). Channel quirk: melodic channel (0–9) with program 38 —
channel 9 would trigger the drum-kit map. REVERB_TAIL 1.0 s (small
room/plate — the shortest in the Bass family; synth bass is almost always
dry). EQ: cut 250 Hz (mud), boost 900 Hz (growl), gentle 6 kHz air — DARK
by design (vs electric bass 5 kHz shelf). Completes the Bass family pair:
finger electric (GM33) + synth (GM38).

**Tremolo Strings added** (2026-10-24): GM44, Strings-family eighth entry —
the bowed STRING SECTION playing rapid repeated bow strokes (the
film-score tension texture; the "bathroom mirror" / every-thriller-
underscore staple) (instrument.md + tremolo_strings.py), verified
end-to-end UnitMatrixComposer → zero-drift ✓ → MIDI (93 bytes) →
FluidSynth WAV (1.24 MB, solo render) ✓; RenderPipeline stem label
`trackXX_Tremolo_Strings.wav` ✓ (GM_PROGRAMS[44] = "Tremolo Strings",
FluidR3 preset 44 = "Tremolo" — one-word SF2 spelling, cosmetic only,
**no routing impact**). Additive recommended (section = detuned harmonic
stack, String Ensemble 1 precedent; SYNTHESIS_DEFAULTS attack 0.02 — the
bow is ALREADY moving, no slow onset; detune ±0.006, stack 3, release
0.2; `tremolo_hz` 7.0 documented — the tremolo is NOT a musicom synthesis
parameter, write it at the note layer (fast repeated 16ths/32nds) or AM a
long note at 7 Hz in production; the FluidR3 patch carries deep built-in
AM, measured trem-ripple 1.00 on every note). BowedString secondary
(bow_velocity 0.26 — tremolo bowing is driven — faster than fiddle 0.24
and section 0.2; bow_force 1.6); PhaseModSynth saw "string machine" +
AM alt; ModalSynth 'string' = section pizz fallback. Additive smoke:
A3 note late(1.0–1.5 s) rms/peak 0.241 (sustain holds, no collapse);
envelope-AM peak measured at exactly 7.00 Hz (the documented tremolo
rate). Solo-render spectral check: 4–8 kHz buzz **1.5%** (clean single
voice, no comb-filtering). Empirical FluidR3 pitch sweep (RMS, notes
24–96): preset 44 audible EVERY note (rms 0.030–0.045, no gaps), SILENT
at 108+ — never write above C7=96. Range 24–96 = full-section span
(contrabass C1 → violin C7; patch plays the full span, unlike String
Ensemble 1's 28 floor); sweet spot 60–84 (C4–C6); solo range 53–89
(F3–A6). Registration proof: `by_name('tremolo strings')` → Tremolo
Strings, `by_program(44)` → Tremolo Strings, `in_sweet_spot(72)` = True,
`in_sweet_spot(24)` = True (24–96 full range), `in_sweet_spot(100)` =
False. Registration in `instrument_registry.py` as TREMOLO_STRINGS
convenience constant + a `registry_table()` role row. Role: accent,
tension, texture, harmony, pad, countermelody — the chattering tension
voice, NOT a solo melody voice (the AM masks pitch clarity — solo lines
go to violin/string_ensemble) and NOT a bass voice (low tremolo is
rumble, not pitch). REVERB_TAIL 2.4 s (between string_ensemble 2.6 and
violin 2.0 — 2.6 is TOO long, the tremolo muddies in a huge tail). EQ:
cut 250 Hz (tremolo doubles section mass in the low-mid), boost 3 kHz
bow-stroke bite, gentle 8.5 kHz air. Channel quirk: melodic channel (0–9)
with program 44 — channel 9 would trigger the drum-kit map. Layering
quirk: idiomatic doubling is octaves or a low sustained string BELOW —
NEVER unison with another melodic patch (the 2026-09-01 comb-filter
lesson; a section tremolo + unison flute on the same pitch is a buzz
machine). Completes the Strings family bowed block: violin/viola/cello/
double_bass/fiddle (solo) + pizzicato (plucked section) + string_ensemble
(sustained section) + tremolo (chattering section).

**Distortion Guitar added** (2026-10-25): GM30, Guitar-family sixth entry —
the high-gain rock/metal guitar, the HEAVIER sibling of Overdriven Guitar
GM29 (harder clipping, more compression sustain, darker speaker roll-off)
(instrument.md + distortion_guitar.py), verified end-to-end
UnitMatrixComposer → zero-drift ✓ → MIDI (93 bytes) → FluidSynth WAV (743 KB,
solo render) ✓; RenderPipeline stem label `trackXX_Distortion_Guitar.wav` ✓
(GM_PROGRAMS[30] = "Distortion Guitar", FluidR3 preset 30 = "Distortion
Guitar" — labels match exactly, **no quirk**). Karplus-Strong recommended
(plucked waveguide + HARD non-linear saturation stage — the exact physical
model; loop_gain **0.9992** — HIGHEST in the plucked set, above overdriven
0.9990: late(1–2 s) rms/peak 0.0069 vs 0.0013 dull control, **5.4×** —
hard-clip compression sustain; saturation 0.85 hard clip vs overdriven 0.60
soft knee; lowpass_hz 3800 darker than overdriven 4000; noise_component
0.080 highest in the Guitar family). PhaseModSynth secondary (mod_depth 4.5
— highest FM depth in the family — harmonic foldover = the scream);
additive tertiary (clipped-wave harmonic stack). Solo-render spectral check:
4–8 kHz buzz **1.6%** (clean single voice, no comb-filtering). Empirical
FluidR3 pitch sweep (RMS, notes 28–84): preset 30 audible 6/6, no gaps —
SF2 never clips a composition. Range 28–84 = GM-patch span (real 22-fret
guitar E2–E6 = 40–76); sweet spot 52–72 (E3–C5). Registration proof:
`by_name('distortion guitar')` → Distortion Guitar, `by_program(30)` →
Distortion Guitar, `in_sweet_spot(64)` = True, `in_sweet_spot(24)` = False.
Registration in `instrument_registry.py` as DISTORTION_GUITAR convenience
constant. Role: lead, melody, accent, rhythm, power-chord strum,
countermelody — the heavy rock/metal voice; single-note leads + root-fifth
power chords idiomatic, dense chords intermodulate into a wash (never
full-position chords on high gain). Writing quirks: dynamic range compressed
to ~10 dB — crescendos via note density, not velocity; vel ≤ 50 =
clean/crunch sample layer, 60–100 = classic distortion, ≥ 110 = max gain
(sustain up, separation down); palm-muted 16th chugs (vel 55–70, short
durations) are the metal rhythm engine; low E (41 Hz) weak on distortion
(speaker roll-off) — keep lines above MIDI 40. REVERB_TAIL 2.4 s (big
rock/metal stage — longest in the Guitar family). Selection note: GM80
"Lead 1 (square)" was the first candidate but the voice_like **talkbox**
member already claims program 80 / stem `Lead_1_square` as its FluidSynth
MIDI-export stand-in — a real registration there would collide on
`by_program(80)` and on the stem filename; GM30 has zero collisions.
Completes the Guitar family: nylon (24), steel (25), jazz (26), clean (27),
overdriven (29), distortion (30).

**Choir added** (2026-10-26): GM52, Vocal-family third entry — the sampled
**mixed chorus** singing a wordless open "ah" (SATB ensemble, the anthem/
pad/cinematic voice), distinct from the formant-synth SOLO `human_voice`
(GM53 stand-in) and from the six non-vocal `voice_like` members
(instrument.md + choir.py), verified end-to-end UnitMatrixComposer →
zero-drift ✓ → MIDI (81 bytes) → FluidSynth WAV (1.08 MB, solo render,
FluidR3 via `discover_soundfont()`) ✓; RenderPipeline stem label
`trackXX_Choir_Aahs.wav` ✓ (GM_PROGRAMS[52] = "Choir Aahs", FluidR3 preset 52
= "Ahh Choir" — cosmetic SF2 spelling, **no routing impact**). Additive
recommended (`additive.py` SoundWave — a chorus IS a formant-shaped harmonic
stack: choir_ah weights [1.0, 0.72, 0.55, 0.60, 0.34, 0.22, 0.14, 0.09] with
the "ah" formants F1 730 / F2 1090 / F3 2440 Hz; attack 0.18 s — a section
breathes in together, slower than a soloist 0.05 s, faster than a pad 0.55 s;
detune ±0.009 between string-section ±0.006 and synth-pad ±0.012; stack 5;
release 0.45; sustain 0.88; breath 0.10). Additive smoke: late-sustain
envelope weight 0.718 (collapse gate ≥ 0.45; decay_S 1e-4 per-grid-step quirk
inherited from synth_pad — and `get_adsr_weights` length proportions MUST sum
to 1.0, it asserts). SingingVoice secondary: 4–5 voices, alto profile,
vibrato 5.2 Hz ±0.28 st (narrower than a soloist's ±0.45), aspiration 0.22,
shimmer 0.05, per-voice seeds; single voice peak 0.800 sustain/peak 0.290,
5-voice detuned stack rms 0.0878 but raw sum peaks 1.722 → **normalize the
stack** before summing. PhaseModSynth tertiary (sine FM "vocal pad", ratio
2.0, depth 1.6). Solo-render spectral check: 4–8 kHz buzz **2.0%** (clean
single voice, no comb-filtering). Empirical FluidR3 pitch sweep (RMS, notes
24–96): preset 52 audible EVERY note (963 / 988 / 904 / 1065 / 1015 / 1167 /
1360 / 1363 / 1388 for 24/36/40/48/60/72/84/88/96 — no gaps), RMS RISES with
pitch, so balance soprano ~8–12 velocity units under the bass. Range 40–88 =
real SATB span E2–E6 (patch plays wider; extremes thin out); sweet spot 48–76
(C3–E5), solo range 55–79. Registration proof: `by_name('choir')` and
`by_name('choir aahs')` → Choir Aahs, `by_program(52)` → Choir Aahs,
`by_program(53)` → Human Voice (distinct), `in_sweet_spot(64)` = True,
`in_sweet_spot(24)` = False. Registration in `instrument_registry.py` as
CHOIR convenience constant + a `registry_table()` role row. Role: pad,
harmony, melody (slow sustained lines only), countermelody, anthem, texture —
NOT a bass voice below E2, NOT a comping/rhythm voice (every onset is a
~100–300 ms breath, so fast stabs blur), NOT a melisma soloist (use
`human_voice`). REVERB_TAIL 2.8 s (hall/church; between string_ensemble 2.6
and synth_pad 3.2 — dry choir sounds like a Mellotron). EQ: cut 350 Hz
(stacked "ah" formants mud up the low-mid), boost 3 kHz vowel presence,
gentle 7 kHz air (a choir is not a cymbal). Layering quirk: octaves or
thirds/sixths with a different patch — NEVER unison with another melodic
patch on the same pitches (choir + string ensemble unison = the 2026-09-01
comb-filter buzz). Channel quirk: melodic channel (0–9); channel 9 triggers
the drum map. Selection note: the first candidate was a Synth Lead at GM81
"Lead 2 (sawtooth)", but **both GM80 and GM81 are claimed by voice_like
stand-ins** (talkbox / singing_saw — the latter also owns the
`Lead_2_sawtooth` stem filename), so that registration failed
`by_program(81)` uniqueness; GM52 has zero collisions. Opens the Vocal
family beyond `human_voice` + `voice_like`.

**Fretless Bass added** (2026-10-27): GM35, **Bass-family third entry** — the
solidbody bass with the frets pulled and the board filled/sanded, so pitch
comes from finger POSITION: continuous portamento slides, a nasal vocal
"mwah" midrange from the compliant fingerboard stop, and no fretwire click
on attack (Jaco Pastorius, Pino Palladino, Mick Karn, Sting, Tony Franklin,
Gary Willis are the reference players). Distinct from the fretted Electric
Bass (finger) GM33 — same body/electronics family, different string stop —
and from the fretted-adjacent Synth Bass 1 GM38 (oscillator + filter, no
string at all). GM35 was completely unclaimed (33, 38 were the only Bass
rows), so `by_program(35)` and the `trackXX_Fretless_Bass.wav` filename are
collision-free. Files: `Bass/fretless_bass/instrument.md` +
`fretless_bass.py`. Verified end-to-end UnitMatrixComposer (1 bar, 1 section,
Fretless Bass + drum-kit context) → **zero-drift ✓** → MIDI 172 bytes →
FluidSynth WAV **751,148 bytes** SOLO render (FluidR3 via
`discover_soundfont()`) ✓; RenderPipeline stems on disk
`track00_Fretless_Bass.wav` (751,148 B) + `track01_Drums.wav` (706,092 B) ✓;
stem label `GM_PROGRAMS[35]` = **"Fretless Bass"** and FluidR3 preset 35 =
**"Fretless Bass"** — labels match exactly, **no quirk**; solo-render
spectral 4–8 kHz buzz **4.6%** (clean single voice, dark mid-forward
timbre). Empirical FluidR3 pitch sweep (RMS at velocity 90, notes
24/28/33/40/45/50/55/60/62/67/72): 1817 / 1740 / 1826 / 1940 / 2430 / 1877 /
1842 / 1809 / 1766 / 1519 / 1043 — every note audible, **no gaps**, level
essentially flat 24–62 (the 45 peak is the patch's own "mwah" sample) and
falling at 72 where the fundamental thins → keep sustained lines at or below
C4 and use 63–72 only for exposed fills. Range 24–72 (C1–C5; standard
4-string is E1–G3 = 28–55, 5-string adds B0 = 23), sweet spot 33–55 (A1–G3),
solo range 28–60. Registration proof: `by_name('fretless bass')` /
`by_name('FRETLESS BASS')` → Fretless Bass, `by_program(35)` → Fretless Bass
(distinct from 33 / 38), `in_sweet_spot(43)` = True, `in_sweet_spot(24)` =
False, `stem_label = 'Fretless_Bass'`; `registry_table()` row
"| Bass | Fretless Bass | 35 | 24–72 | bass, melody, countermelody, groove,
slide, color |". Synthesis: **Karplus-Strong primary** (SP-011 — a plucked
string waveguide IS the physical model; `loop_gain` 0.9975, slightly longer
than the fretted bass 0.9970 because the bare board damps the top of the
string less than a fret crown; `lowpass_hz` 2200 — darker than the fretted
bass, which is where the nasal "mwah" lives; width 0.55; role bass),
**BowedString secondary for ARCO only** (bow_velocity 0.18, bow_force 1.4,
bow_position 0.18 sul tasto, lpf_coef 0.6, slow 0.16 s attack — a bowed
electric bass reads as a cello), **ModalSynth `'string'` weak fallback**.
Smoke tests: Karplus E2 peak 0.290, head_rms 0.0069 → tail_rms 0.0005 (real
string decay, not a DC plateau); BowedString constructs and renders.
Production: REVERB_TAIL 1.6 s (a touch longer than the fretted bass 1.4 —
the vocal quality wants air), EQ cut 250 Hz / **boost 800 Hz +3 dB** (the
"mwah" formant — THE fretless EQ move) / 5 kHz air shelf for fingerboard
squeak, PAN centre. Quirks: (1) **SF2 does not honour portamento** — FluidR3
preset 35 bakes some slides into velocity layers but a MIDI CC5/CC65
portamento assignment is ignored, so write a slide as a fast chromatic run of
short notes (e.g. 44 → 45 at 16th-note spacing) unless the renderer applies
pitch-bend; (2) monotimbral and effectively monophonic — no chords (thumb-
position dyads are an overdub, not a patch behaviour), so never ask the
composer for a 3-note "fretless chord"; (3) **no unison doubling** with
another melodic patch on the same pitches (the 2026-09-01 comb-filter rule) —
octaves or a low bass note an octave+ below are fine, and a drum kit is fine.
Role: bass, melody (mid register 51–62 only), countermelody, groove, slide,
color — NOT a pad/chord voice, NOT a slap voice (slap needs frets), NOT a
high lead above C4.

**Synth Brass 1 added** (2026-10-29): GM62, **Synth-family second entry** —
the classic analog synth brass (saw stack + resonant low-pass + fast-ADSR;
the "brassy stab" voice of funk/disco/synth-pop/film — Prophet-5/OB-Xa
brass patches, EW&F "Shining Star" stab, Gary Numan/Depeche Mode brass
swells), distinct from the acoustic Brass family (PhaseModSynth saw carriers
at 56–61): GM62's tone is an oscillator + filter, no physical instrument
(instrument.md + synth_brass_1.py), verified end-to-end UnitMatrixComposer →
**zero-drift ✓** → MIDI 184 bytes → FluidSynth WAV **794,668 bytes** SOLO
render (FluidR3 via `discover_soundfont()`) ✓; RenderPipeline stems on disk
`track00_Synth_Brass_1.wav` (794,668 B) + `track01_Drums.wav` (706,092 B) ✓;
stem label `GM_PROGRAMS[62]` = **"Synth Brass 1"** and FluidR3 preset 62 =
**"Synth Brass 1"** — labels match exactly, **no quirk** (contrast: GM74
Flute → "Recorder", GM109 → "Bag pipe", GM111 → "Shanai"); solo-render
spectral 4–8 kHz buzz **2.6%** (clean single voice, no comb-filtering).
Synthesis: **Polysynth primary** (`sound/synthesis/polysynth.py` PolyVoice —
polyBLEP subtractive, THE analog-brass architecture: saw osc stack, osc2
detuned +7 cents, thin square sub, 24dB low-pass cutoff 2800 Hz resonance
0.45, ADSR attack 0.015 s / decay 0.18 / sustain 0.75 / release 0.25, 2
unison voices; POLYSYNTH_DEFAULTS/SYNTHESIS_DEFAULTS load through the
registry), **PhaseModSynth secondary** (FM brass, saw carrier ratio 1.0
depth 3.2 — between brass_section 2.8 and overdriven 4.0, the synth edge),
**Additive tertiary** (brass rolloff stack). Smoke tests: Polysynth G4 peak
1.404 sustain/peak 0.162 (holds, no collapse); PhaseModSynth G4 peak 0.764.
Empirical FluidR3 pitch sweep (RMS, velocity 90, notes 36/48/60/72/84/96/
108): preset 62 audible **7/7, no gaps** (RMS 2153–2427, essentially flat
across the whole span — full-keyboard patch, no ceiling) — SF2 never clips a
composition. Range 36–96 = idiomatic writing band (C2–C7; patch plays the
full keyboard); sweet spot 55–79 (G3–G5 — the funk stab/punch zone), solo
range 48–84 (C3–C6). Registration proof: `by_name('synth brass 1')` /
`by_name('SYNTH BRASS 1')` → Synth Brass 1, `by_program(62)` → Synth Brass 1
(distinct from 61 brass_section / 63 synth brass 2), `in_sweet_spot(67)` =
True, `in_sweet_spot(24)` = False, `stem_label = 'Synth_Brass_1'`;
`registry_table()` row "| Synth | Synth Brass 1 | 62 | 36–96 | lead,
harmony, accent, stab, pad, countermelody |". Role: lead (unison brass,
72–84 piercing top), harmony (stab chords + brass-pad swells), accent (sfz
hits, marcato downbeats, risers), stab (the signature — short gates ≤ 0.3
bar), pad (sustained swells), countermelody — **NOT** a bass voice (use
synth_bass_1 / electric_bass), NOT an acoustic-brass substitute (no
physical articulation). Polyphonic: 3–5 note stab chords fully idiomatic.
REVERB_TAIL 2.2 s (hall/plate — shorter than brass_section 2.5: synth stabs
want a drier punch than a real brass tutti; longer than synth bass 1.0). EQ:
cut 300 Hz (saw + square sub crowd the low-mid), boost 2.8 kHz (the brassy
bite band), 8 kHz air shelf. Enum note: `MidiInstrument` has NO synth-brass
constant (10-instrument legacy enum) — use raw GM 62; the registry is the
full KB. Channel quirk: melodic channel (0–9) — channel 9 triggers the drum
map (timpani lesson). Layering quirk: octave doubling (+ brass_section for
the hybrid analog/acoustic wall) — NEVER unison with another melodic patch
on the same pitches (the 2026-09-01 comb-filter rule).

**Tango Accordion / Bandoneón added** (2026-10-30): GM23, **Keys-family free-
reed entry** — the bandoneón, the bisonoric German concertina (Heinrich Band,
Krefeld ~1846) that German/Italian emigrants carried to the Río de la Plata
around 1870 and that became the melodic soul of the orquesta típica (Arolas,
Troilo, Piazzolla). Distinct from `accordion` GM21: button-operated,
bisonoric (different note on push vs pull, no register switches), and every
note sounds TWO reeds tuned an octave apart — the octave coupling is the
timbre identity, not musette detune. Files: `Keys/tango_accordion/
instrument.md` + `tango_accordion.py`. Verified end-to-end
UnitMatrixComposer (1 bar, 1 section, bandoneón SOLO + drum-kit context) →
**zero-drift ✓** → MIDI **181 bytes** → FluidSynth WAV **777,004 bytes**
SOLO render (FluidR3 via `discover_soundfont()`) ✓; RenderPipeline stems on
disk `track00_Tango_Accordion.wav` (777,004 B) + `track01_Drums.wav`
(706,092 B) ✓; solo-render spectral 4–8 kHz buzz **8.0%** (clean single
voice, no comb-filtering). Stem-label **quirk**: `GM_PROGRAMS[23]` =
**"Tango Accordion"** but FluidR3 preset 23 = **"Bandoneon"** — internal SF2
name differs from the GM label, cosmetic only (the pipeline names stems from
GM_PROGRAMS), no routing impact. Synthesis: **PhaseModSynth primary** (a free
reed is a phase-modulated oscillator — saw carrier, sine modulator ratio 1.0,
depth 3.4: edgier than accordion 3.2, below bagpipe 4.5; attack 0.018 s,
release 0.07 s, sustain 0.82) **plus the octave-coupled second reed as a
second PhaseModSynth voice one octave up at amplitude 0.45**
(`FM_DEFAULTS["octave_double"]`) — do NOT detune it, the pair is tuned in
octaves. Smoke: A4 + octave reed peak 1.135, sustain/peak 0.301 (holds, no
collapse). Additive secondary (octave-heavy stack h2/h1 = 0.55; normalize
before `apply_overtones()` — the API asserts the weights sum to 1.0),
ModalSynth `'tube'` fallback. Empirical FluidR3 pitch sweep (RMS, velocity
90, notes 24/36/41/48/60/72/84/96/108): **9/9 audible, no gaps**
(1613/1559/1479/1434/1362/1055/1530/1569/1360 — flat, dip at C5, rise above
C6) — full-keyboard patch, SF2 never clips a composition. Spectral centroid
(solo, held notes): **C4 3568 Hz, C6 5999 Hz** (vs synth brass 1744 Hz at
C4 — a genuinely bright, nasal voice). Range 41–96 = F2–C7 practical written
band (physical 142-tone/71-key Rheinische system spans "fast fünf Oktaven" per
de.wikipedia; fr.wikipedia says the tessitura approaches six octaves once the
octave-coupled voice is counted; endpoints vary by system), sweet spot 57–84
(A3–C6, the cantabile tango register), solo range 53–91. Registration proof:
`by_name('tango accordion')` / `by_name('TANGO ACCORDION')` → Tango Accordion,
`by_program(23)` → Tango Accordion (distinct from 21 Accordion), 
`in_sweet_spot(72)` = True, `in_sweet_spot(30)` = False, `stem_label =
'Tango_Accordion'`; `registry_table()` row "| Keys | Tango Accordion | 23 |
41–96 | lead, melody, ornament, harmony, accent, pad |"; convenience constant
`TANGO_ACCORDION`. Articulations use tango vocabulary: cantabile, marcato
(acento), picado, fuelle, llorón (the cry), arrastre (drag/slide), chasquido
(bellows whip), golpe (box tap), sforzando. Production: REVERB_TAIL 1.8 s
(tango salon/hall — longer than accordion 1.4, shorter than string_ensemble
2.6), EQ cut 250 Hz (wooden-box boom), boost 3 kHz (reed edge), 7.5 kHz air
shelf, PAN centre (±0.2 for left/right-hand spread). Writing quirks: (1) SF2
ignores portamento — write `arrastre` as a fast chromatic grace run; (2) the
real instrument is bisonoric and its layout is not scale-friendly (players
work almost entirely on the draw stroke) — write the sounding line, not
push/pull alternation; (3) ensemble role is a single melodic line or two-note
dyads even though the patch is polyphonic — dense low chords mud; (4) NEVER
unison doubling with another melodic patch on the same pitches (2026-09-01
comb-filter rule) — octaves/thirds/sixths or a drum kit are fine. Role: lead,
melody, ornament, harmony, accent, pad — NOT a bass voice, NOT a Stradella
chord-comp voice, NOT a folk-musette accordion (that is GM21).

**Synth Voice added** (2026-10-31): GM54, **Synth-family voice-lead entry** —
the classic analog/digital synthesizer "choir" (Roland VP-330 choir preset,
CS-80 "voice", Vangelis Blade Runner / Jarre Oxygene synthwave leads): a
detuned saw/square oscillator stack through a vowel (formant) filter, slow
breathy attack, delayed LFO vibrato. Files: `Synth/synth_voice/
instrument.md` + `synth_voice.py`. Verified end-to-end UnitMatrixComposer
(1 bar, 1 section, Synth Voice SOLO + drum-kit context) → **zero-drift ✓** →
MIDI **155 bytes** → FluidSynth WAV **971,052 bytes** SOLO render (FluidR3
via `discover_soundfont()`) ✓; RenderPipeline stems on disk
`track00_Synth_Voice.wav` (971,052 B) + `track01_Drums.wav` (706,092 B) ✓;
solo-render spectral 4–8 kHz buzz **15.7%** (clean single voice, no
comb-filtering; the patch is genuinely bright — centroid C4 4626 Hz / C6
6068 Hz — so the buzz band carries real formant energy, still under the 20%
gate). Stem-label: **no quirk** — `GM_PROGRAMS[54]` = "Synth Voice" AND
FluidR3 preset 54 = "Synth Voice", labels match exactly. Synthesis:
**PhaseModSynth primary** (`sound/synthesis/phase_mod.py` — saw carrier,
sine modulator ratio 1.0, depth 2.6: between synth_pad 2.0 and synth_brass_1
3.2 — a voice is softer than a horn, edgier than a pad; attack 0.25 s = the
breath, release 0.35, sustain 0.85; FM_DEFAULTS/SYNTHESIS_DEFAULTS load
through the registry), **Additive secondary** (formant-weighted harmonic
stack, choir.py precedent: weights [1.0, 0.78, 0.62, 0.55, 0.40, 0.28, 0.18,
0.10] — brighter top than the real choir, normalized to sum 1.0 for
`apply_overtones`), **Polysynth tertiary** (saw + square stack, 6-cent
detune, low-pass 3200 Hz resonance 0.6 = the vowel peak, slow gate 0.25 s,
3 unison voices). Smoke tests: PhaseModSynth G4 peak 0.768 sustain/peak
0.282 (holds, no collapse); Additive envelope peak 1.000; Polysynth G4 peak
1.439. Empirical FluidR3 pitch sweep (RMS, velocity 90, notes 24/36/48/60/
72/84/96/108): preset 54 audible **8/8, no gaps** (RMS 1308–2067 — bottom
24 loudest at 2067, C4 dips to 1308, treble recovers) — full-keyboard patch,
SF2 never clips a composition. Range 36–96 = idiomatic writing band (C2–C7;
patch plays the full keyboard), sweet spot 55–79 (G3–G5 — the vocal-register
heart), solo range 60–84 (C4–C6 — the "singing" band). Registration proof:
`by_name('synth voice')` / `by_name('SYNTH VOICE')` → Synth Voice,
`by_program(54)` → Synth Voice (distinct from 52 Choir Aahs / 53 Voice
Oohs), `in_sweet_spot(67)` = True, `in_sweet_spot(24)` = False,
`stem_label = 'Synth_Voice'`; `registry_table()` row "| Synth | Synth Voice
| 54 | 36–96 | lead, melody, harmony, pad, countermelody, accent |";
convenience constant `SYNTH_VOICE`. Role: lead (sustained voice-lead lines,
60–84), melody (the "singing" patch of synthwave/retro-pop/film), harmony
(2–3 note voice pads), pad (sustained vowel beds — slow attack hides chord
entrances), countermelody, accent — NOT a bass voice (use synth_bass_1 /
electric_bass), NOT a real-choir substitute (that is GM52 Choir Aahs), NOT a
stab patch (slow attack — stabs bloom, write gaps). Polyphonic: pads and
2–3 note harmonies fully idiomatic; unison melody + octave doubling is the
width trick. REVERB_TAIL 2.8 s (hall/plate — same as choir: a voice is
ALWAYS in a room; shorter than synth_pad 3.2 so leads keep presence). EQ:
cut 350 Hz (oscillator stack + vowel formants pile up in the low-mid), boost
2.4 kHz (the F3 vowel band — "ah" intelligibility), gentle 8.5 kHz air shelf
(bright but NOT sibilant). PAN centre (±0.3 L/R spread on wide doubled-lead
swells). Enum note: `MidiInstrument` has NO synth-voice constant (10-
instrument legacy enum, 1-based) — use raw GM 54; the registry is the full
KB. Channel quirk: melodic channel (0–9) — channel 9 triggers the drum map.
Writing quirks: (1) the slow attack means short staccato notes bloom into
the next — write stabs with a gap or accept the smear; (2) GM55 "Orchestra
Hit" is the one-shot stab sibling and GM53 "Voice Oohs" the sampled solo
voice — both still future candidates; (3) NEVER unison doubling with another
melodic patch on the same pitches (2026-09-01 comb-filter rule) — octaves/
thirds or a drum kit are fine.

**Acoustic Bass added** (2026-11-01): GM32, **Bass-family fourth entry** — the
upright double bass played PIZZICATO: the jazz walking-bass / bluegrass slap /
rockabilly thump voice (Ray Brown, Paul Chambers, Ron Carter, Charlie Haden,
NHØP, Stanley Clarke). The same instrument as the orchestral Contrabass
(GM43) but in its plucked idiom — finger-plucked gut/steel strings over a huge
wooden body, fundamental-rich woody thump, NO electronics in the signal path
(instrument.md + acoustic_bass.py), verified end-to-end UnitMatrixComposer
(1 bar, 1 section, Acoustic Bass SOLO + drum-kit context) → **zero-drift ✓** →
MIDI **172 bytes** → FluidSynth WAV **727,852 bytes** SOLO render (FluidR3 via
`discover_soundfont()`) ✓; RenderPipeline stems on disk
`track00_Acoustic_Bass.wav` (727,852 B) + `track01_Drums.wav` (706,092 B) ✓;
stem label `GM_PROGRAMS[32]` = **"Acoustic Bass"** and FluidR3 preset 32 =
**"Acoustic Bass"** — labels match exactly, **no quirk**; solo-render spectral
4–8 kHz buzz **5.3%** (clean single voice, no comb-filtering). Synthesis:
**Karplus-Strong primary** (SP-011 — a plucked string waveguide IS the physical
model: loop_gain 0.9975 — long pizz ring, between electric bass 0.9970 and
harp 0.9985, matching the sitar/fretless class; `lowpass_hz` 1600 — the DARKEST
of the plucked basses: the huge wooden body rolls the top off into the woody
thump band, THE acoustic-bass signature; noise_component 0.02 finger scrape),
**BowedString secondary for ARCO only** (bow_velocity 0.18, bow_force 1.3,
bow_position 0.20 sul tasto, lpf_coef 0.6, attack 0.14 s — a bowed acoustic
bass reads as a woody cello), **ModalSynth `'string'` weak fallback**.
Smoke tests: Karplus E2 peak 0.290, head_rms 0.0069 → tail_rms 0.0005 (real
string decay, not a DC plateau); BowedString constructs and renders.
Empirical FluidR3 pitch sweep (RMS, velocity 90, notes 24/28/33/36/40/45/48/
52/55/60/64/67/72): preset 32 audible **13/13, no gaps** (0.1274 → 0.0497,
smooth rolloff, no treble cliff; patch also plays 20–96, wider than the
idiomatic band) — SF2 never clips a composition. Range 24–72 = idiomatic
writing band (C1–C5; real 4-string upright is E1–G4 = 28–67, 5-string adds
B0 = 23), sweet spot 40–57 (E2–A3 — the jazz walking pocket), solo range
36–60 (C2–C4). Registration proof: `by_name('acoustic bass')` /
`by_name('ACOUSTIC BASS')` → Acoustic Bass, `by_program(32)` → Acoustic Bass
(distinct from 33 electric / 35 fretless / 38 synth / 43 contrabass),
`in_sweet_spot(48)` = True, `in_sweet_spot(20)` = False, `stem_label =
'Acoustic_Bass'`; `registry_table()` row "| Bass | Acoustic Bass | 32 | 24–72 |
bass, rhythm, countermelody, accent, melody |"; convenience constant
`ACOUSTIC_BASS`. Role: bass, rhythm, countermelody, accent, melody — the
acoustic bass is a monophonic line instrument (walking bass, root-fifth
groove, slap patterns), NOT a chord/comping voice and NOT a pad; the pizz
ring IS the identity (long, woody, fundamental-rich). Production: REVERB_TAIL
1.8 s (jazz-club room — the upright lives in a small wooden room, not a hall;
double_bass 1.8 precedent), EQ cut 220 Hz (body boxiness — the woody thump
itself is LOWER ~100 Hz, keep it), boost 700 Hz (finger attack / pizz growl),
4 kHz air shelf (finger scrape), PAN centre. Writing quirks: (1) monophonic —
never ask the composer for a 3-note "acoustic bass chord" (double-stops on
adjacent strings are a rare overdub); (2) SF2 honours no portamento — write a
slide as a fast chromatic run or pitch-bend; (3) slap is velocity-hungry
(vel ≥ 90 for the rockabilly thwack) while the walking line sits 65–80;
(4) **no unison doubling** with another melodic patch on the same pitches
(2026-09-01 comb-filter rule) — octaves or a low bass note an octave+ below
are fine, and a drum kit is fine.

**Synth Bass 2 added** (2026-09-02): GM39, **Bass-family fifth entry** — the
RESONANT analog synth bass: the Roland TB-303 acid voice (pulse oscillator
through a self-oscillating 24 dB/oct low-pass, accent + slide gesture
buttons), the sound that birthed acid house (Phuture "Acid Tracks", DJ
Pierre, Armando) and the bass of techno/electro/synthwave. The squelch
sibling of Synth Bass 1 (GM38, Minimoog-ish analog): HIGHER filter resonance
(0.85 vs 0.55), BRIGHTER cutoff (2400 vs 1800 Hz), BIGGER filter-env
re-open (0.8 vs 0.5 — the accent), pulse waveform vs saw. Files:
`Bass/synth_bass_2/instrument.md` + `synth_bass_2.py`. Verified end-to-end
UnitMatrixComposer (1 bar, 1 section, Synth Bass 2 SOLO + drum-kit context)
→ **zero-drift ✓** → MIDI **190 bytes** → FluidSynth WAV **715,308 bytes**
SOLO render (FluidR3 via `discover_soundfont()`) ✓; RenderPipeline stems on
disk `track00_Synth_Bass_2.wav` (715,308 B) + `track01_Drums.wav` (706,092 B)
✓; solo-render spectral 4–8 kHz buzz **4.8%** (clean single voice, no
comb-filtering — the acid resonance lives in the 0.8–3 kHz squelch band,
below the buzz gate). Stem-label: **no quirk** — `GM_PROGRAMS[39]` =
"Synth Bass 2" AND FluidR3 preset 39 = "Synth Bass 2", labels match exactly.
Synthesis: **MonoSynth primary** (`sound/synthesis/mono_synth.py` — the
subtractive VCO → 24dB ladder → ADSR architecture IS the 303; pulse
waveform, resonance 0.85 near self-oscillation, filter_env_amount 0.8 =
the accent, cutoff 2400; SYNTHESIS_DEFAULTS load through the registry),
**PhaseModSynth secondary** (FM acid "rubber 303": saw carrier, sine mod
ratio 1.0, depth 2.8, attack 0.004), **Karplus-Strong tertiary** (loop_gain
0.9955 — snappier than SB1's 0.9960; the acid is punchy/tight), ModalSynth
`'string'` weak fallback. Smoke tests: MonoSynth E2 peak 0.800, head_rms
0.664 → mid_rms 0.606 → tail_rms 0.514 (sustain holds, no collapse — gate
release only), squelch band 0.8–3 kHz = **27.5%** of audible energy (the
resonance peak is REAL); PhaseModSynth E2 peak 0.771. Empirical FluidR3
pitch sweep (RMS, velocity 90, notes 21/24/28/33/36/40/45/48/52/55/60/64/
67/72/77/84/96/108): preset 39 audible **17/18, one gap at C8=108 only**
(RMS 0.2533 at A0 → 0.1246 at C7, remarkably even rolloff, no gaps in the
writing band; bottom 21–35 sub band is LOUD) — full-keyboard patch down to
A0, SF2 never clips a composition. Range 21–96 = GM patch span (A0–C7;
idiomatic writing band 28–72 E1–C5), sweet spot 36–55 (C2–G3 — the acid
groove pocket: 16th-note sequences, root-fifth riffs), solo range 48–72
(C3–C5 — the acid-lead squelch band). Registration proof:
`by_name('synth bass 2')` / `by_name('SYNTH BASS 2')` → Synth Bass 2,
`by_program(39)` → Synth Bass 2 (distinct from 38 synth bass 1 / 32
acoustic / 33 finger / 35 fretless), `in_sweet_spot(48)` = True,
`in_sweet_spot(20)` = False, `stem_label = 'Synth_Bass_2'`;
`registry_table()` row "| Bass | Synth Bass 2 | 39 | 21–96 | bass, rhythm,
groove, accent, lead |"; convenience constant `SYNTH_BASS_2`. Role: bass
(acid bass lines, root-fifth sequences, sub pedals — locks with the kick),
rhythm (16th-note acid sequences — the pattern IS the melody), groove
(offbeat accent = the acid rhythm signature), accent (squelch stabs,
octave-jump hits), lead (acid-lead solos 63–84 — screaming resonant lines)
— NOT a harmony/pad voice (true monophonic instrument; chords are NOT
idiomatic), NOT a sub-only voice (the resonance is the identity, sub is
just the bottom), NOT a warm/fat voice (that is Synth Bass 1). Production:
REVERB_TAIL 0.9 s (the DRIEST bass in the library — the 303 is direct-inject
and the resonance IS the effect; verb smears 16th-note sequences), EQ cut
220 Hz −3 dB (bigger than SB1 — resonance pushes energy into the low-mid
mud against the kick), boost 1.1 kHz (the squelch band — the ~1 kHz filter
peak when the env opens, the acid "growl"), 6.5 kHz air shelf (the 303 has
a natural top roll-off), PAN centre. Writing quirks: (1) monophonic —
never ask the composer for a 3-note "acid bass chord"; (2) the accent IS
the performance — velocity ≥ 95 for the offbeat squelch, keep the 16ths at
72–82; (3) SF2 honours no portamento — write a 303 slide as pitch-bend or
a fast chromatic run; (4) **no unison doubling** with another melodic patch
on the same pitches (2026-09-01 comb-filter rule) — octaves or a low bass
note an octave+ below are fine, and a drum kit is fine.

**Calliope added** (2026-11-03): GM82, **Synth-family fourth entry** — the
GM Lead-family patch modelled on the steam calliope ("steam piano"): a bank
of steam-driven organ pipes / brass whistles played from a keyboard, the
sound of circus, carnival, fairground and Mississippi riverboat. The patch
reads as a mellow, slightly breathy pipe lead: near-sine pipe fundamentals
with a touch of chiff, fast valve-like attack, sustained while held. Files:
`Synth/calliope/instrument.md` + `calliope.py`. Verified end-to-end
UnitMatrixComposer (1 bar, 1 section, Calliope SOLO + drum-kit context)
→ **zero-drift ✓** → MIDI **188 bytes** → FluidSynth WAV **1,001,772 bytes**
SOLO render (FluidR3 via `discover_soundfont()`) ✓; RenderPipeline stems on
disk `track00_Lead_3_calliope.wav` (1,001,772 B) + `track01_Drums.wav`
(706,092 B) ✓; stem label `GM_PROGRAMS[82]` = **"Lead 3 (calliope)"** →
sanitized `Lead_3_calliope` (parens stripped, spaces → underscore) and
FluidR3 preset 82 = **"Calliope Lead"** — SF2 internal name differs
cosmetically, **no routing quirk** (stems are labelled from GM_PROGRAMS);
solo-render spectral 4–8 kHz buzz **3.5%** (clean single voice, no
comb-filtering — measured 11.2% at the C6 probe, lower in the mid
register). Synthesis: **PhaseModSynth primary** (the pipe recipe: sine
carrier + sine modulator, mod_freq_ratio 1.0, mod_depth **1.8** — between
flute 1.5 and shakuhachi 2.0: a pipe is brighter than a flute, mellower
than the reed voices 2.2–4.5; attack 0.02 s = fast valve opening, release
0.12 s = dry pipe cutoff, sustain 0.9; SYNTHESIS_DEFAULTS load through the
registry), **Additive secondary** (mellow harmonic pipe stack [1.0, 0.55,
0.30, 0.18, 0.10, 0.05] — strong fundamental, gentle rolloff, no reed
brightness), **AirPipe tertiary** (the physical model — a pressure-driven
flue pipe IS the calliope physics: steam pressure = the air supply; open
pipe stopped=False, pressure 0.6 below the 0.75 overblow threshold so the
pipe stays on the fundamental, length_scale 1.0; AIRPIPE_DEFAULTS). Smoke
tests: PhaseModSynth C5 peak 0.796, mid_rms 0.3795 → tail_rms 0.2940
(sustain holds, release decays — no collapse); AirPipe C5 peak 1.704;
Additive C5 peak 2753. Empirical FluidR3 pitch sweep (RMS, velocity 90,
notes 24–108 step 6): preset 82 audible **15/15, no gaps** (RMS 670–2125,
even; bottom C1 loudest 2125, treble rolls gently to 670 at C8; spectral
centroid ~2230 Hz at C6 — mellow for a lead) — full-keyboard patch, SF2
never clips a composition. Range 60–96 = idiomatic writing band (C4–C7,
the real steam rack ~3 octaves; the GM patch plays 24–108), sweet spot
72–84 (C5–C6 — the classic fairground tune register), solo range 67–89
(G4–A6). Registration proof: `by_name('calliope')` /
`by_name('LEAD 3 (CALLIOPE)')` → Calliope, `by_program(82)` → Calliope
(distinct from 88 pad / 62 brass / 54 voice / 80–81 lead-1/lead-2
voice-like members), `in_sweet_spot(72)` = True, `in_sweet_spot(48)` =
False, `stem_label = 'Lead_3_calliope'`; `registry_table()` row
"| Synth | Lead 3 (calliope) | 82 | 60–96 | lead, melody, ornament, accent,
countermelody |"; convenience constant `CALIOPE`. Role: lead (carnival/
circus cue melodies — the oom-pah tune, "Entrance of the Gladiators"
register), melody (retro/fantasy top lines, the "toy town" voice),
ornament (trills + chiff blips ARE the idiom), accent (downbeat pipe
stabs), countermelody (second pipe voice, thirds/sixths) — NOT a bass
voice, NOT a pad (pipes are rhythmic and per-key; the slow-attack pad role
is synth_pad GM88); light 2–3 note pipe chords are OK (calliopes are
played two-handed) but dense harmony smears. Production: REVERB_TAIL 2.0 s
(fairground space — shorter than the pad family 3.2 s because calliope
phrases are rhythmic and the pipes carry their own steam), EQ cut 400 Hz
−2.5 dB (pipe-stack low-mid boxiness), boost 3 kHz (the whistle/chiff
presence band), 9 kHz air shelf (steam shimmer), PAN centre. Writing
quirks: (1) the fast attack keeps short chiff notes dry and separated —
no smear (contrast the synth-voice bloom); (2) no built-in vibrato (steam
pressure is constant) — MIDI pitch-bend is the only idiomatic wobble;
(3) **no unison doubling** with another melodic patch on the same pitches
(2026-09-01 comb-filter rule) — octaves or thirds (+ same patch 8va = the
full pipe rack) or a drum kit are fine, and a tuba/bass oom-pah an octave+
below + snare = the complete circus band.

**Agogo added** (2026-09-02): GM113, **World-family eleventh entry** — the
Yoruba-derived Brazilian multiple hand-bell (two-to-four conical sheet-metal
bells on a curved handle, struck with one stick), the TIMEKEEPER of samba,
batucada, samba de roda, capoeira and candomblé (instrument.md + agogo.py),
verified end-to-end UnitMatrixComposer (1 bar, 1 section, Agogo SOLO +
drum-kit context) → **zero-drift ✓** → MIDI **263 bytes** → FluidSynth WAV
**813,100 bytes** SOLO render (FluidR3 via `discover_soundfont()`) ✓;
RenderPipeline stems on disk `track00_Agogo.wav` (813,100 B) +
`track01_Drums.wav` (849,708 B) ✓; stem label `GM_PROGRAMS[113]` =
**"Agogo"** and FluidR3 preset 113 = **"Agogo"** — labels match exactly,
**no quirk**. ModalSynth recommended with a custom `AGOGO_MODES` bank
(tuned fundamental 440 Hz + near-octave 2.0× partner + inharmonic 2.72× /
4.07× / 5.4× metal tail, decay rates 2.2–7.0 = the ~1 s agogo ring, between
vibraphone 0.30–1.10 and taiko 2.6–6.0); stock `'bell'` preset is the
closest bank but models a Western CAST bell (minor-third tierce).
PhaseModSynth fallback uses a NON-integer mod ratio 2.72 (inharmonic FM bell
recipe); **Karplus-Strong EXPLICITLY REJECTED** (struck metal, no string —
the timpani/taiko precedent). ModalSynth smoke test: peak 0.900, head_rms
0.4124 → mid_rms 0.1452 → late(1.0–1.5 s) rms 0.0295 (late/peak 0.0328 —
still ringing at 1 s), partials 2.0× = 29.5%, 2.72× = 11.2%, 4.07× = 4.8%
of f0 (PITCHED bell, fundamental dominant). Solo-render spectral check:
4–8 kHz buzz **19.6%** — passes the 20% gate but is the BRIGHTEST reading in
the KB: the agogo's stick-on-sheet-metal clank is genuinely broadband
(top bins 446 Hz = the A4 low bell, 1660 Hz, 2284 Hz), and the render is a
single voice so there is no comb-filtering; production EQ (+2.5 dB at
3.2 kHz presence, +1 dB at 9 kHz air) is what keeps it cutting through a
bateria. Empirical FluidR3 pitch sweep (RMS, velocity 100, notes
43/48/52/55/58/60/64/67/72/76/79/84/88/91/96): preset 113 audible
**15/15, no gaps**, smooth rolloff 0.0125 → 0.0039 — SF2 never clips a
composition. Range 55–96 = GM patch span (G3–C7); solo range 67–84
(G4–C6) is the REAL two-bell pair (low bell ~A4–C5, high bell a fourth up);
sweet spot 69–81 (A4–A5). Registration proof: `by_name('agogo')` /
`by_name('Agogo')` → Agogo, `by_program(113)` → Agogo (distinct from 112
Tinkle Bell / 114 Steel Drums / 115 Woodblock / 116 Taiko Drum),
`in_sweet_spot(72)` = True, `in_sweet_spot(48)` = False,
`stem_label = 'Agogo'`; `registry_table()` row "| World | Agogo | 113 |
55–96 | rhythm, accent, ornament, drone |"; convenience constant `AGOGO`.
Registry `_FIELDS` extended with `agogo_modes` so the custom bank loads
through the registry. Role: rhythm (the timeline — a fixed cyclic 16th
figure, the Brazilian analogue of the Afro-Cuban clave), accent (hard
downbeat strokes on the "1"), ornament (rim ticks, flams, short rolls at
viradas), drone (repeated single-bell offbeat pedal) — NOT a melodic lead,
NOT a harmony/chord voice (ONE stick, two bells, one note at a time — never
simultaneous strikes), NOT a bass voice (bells sit above 400 Hz).
Production: REVERB_TAIL 1.3 s (street/roda instrument — dry and cutting,
shorter than the taiko 1.6), EQ cut 420 Hz −1.5 dB (boxy low-mid under the
bell fundamental), boost 3.2 kHz (stick-on-metal clank), 9 kHz air shelf
(sheet-metal shimmer — never low-pass a bell), PAN centre (bateria spread
+0.15, opposite the tamborim). Writing quirks: (1) TIMELINE not fills —
write 1–2 bar patterns and loop them; (2) two pitches alternating (low bell
root, high bell a fourth above), never struck together; (3) straight 16ths,
metronomic — humanize with a tiny timing sigma, accents carry the groove;
(4) ghost 16ths at velocity 30–48 are what make the pattern breathe;
(5) **no unison doubling** with another melodic patch on the same pitches
(2026-09-01 comb-filter rule) — octaves or a different bell pitch are fine,
drums are fine.

**Muted Guitar added** (2026-11-05): GM28, **Guitar-family seventh entry** —
the palm-muted / fret-hand-damped solid-body electric guitar (instrument.md +
muted_guitar.py), the shortest, most percussive guitar voice: a pitched
"chunk" instead of a sustaining note. Verified end-to-end UnitMatrixComposer
(1 bar, 1 section, 104 bpm, Muted Guitar 16th-note funk chops SOLO on ch0 +
drum-kit context on ch9) → **zero-drift ✓** → MIDI **467 bytes** → FluidSynth
WAV **791,340 bytes** SOLO render (track 0 = muted guitar only, FluidR3 via
`discover_soundfont()` — no second melodic patch on the same pitches) →
solo-render spectral check 4–8 kHz buzz **0.1%** (cleanest guitar reading in
the KB; the mute removes high-frequency sustain rather than adding buzz).
RenderPipeline stems on disk `track00_Electric_Guitar_muted.wav`
(791,340 B) + `track01_Drums.wav` (835,628 B) ✓. Stem label
`GM_PROGRAMS[28]` = **"Electric Guitar (muted)"** → sanitized
`Electric_Guitar_muted`; FluidR3 preset 28 = **"Palm Muted Guitar"** — the
SF2 names the TECHNIQUE, the pipeline names the GM2 program; **cosmetic name
quirk only, no routing impact** (same class as "Jazz Guitar" / "Bag pipe" /
"Shanai"). STEM_LABEL = `Electric_Guitar_muted` matches the pipeline's real
label. Karplus-Strong recommended — muted guitar is still a plucked string,
but with a very lossy waveguide loop: **loop_gain 0.9850** (the lowest in the
guitar family; ~0.2–0.4 s decay vs 0.9970+ open strings), excitation "pick",
width 0.30, lowpass_hz 2200, noise_component 0.030 (pick scrape + palm slap
are part of the sound). KS smoke test (A2, 0.6 s, vel 100): peak 0.693,
late-200 ms tail_rms/peak **0.013** — the mute actually damps. ModalSynth
fallback = stock `'string'` bank with very fast decay rates (~12/26/44/66/90,
several times faster than jazz guitar 4/10/18/28/40); PhaseMod fallback =
saw carrier, mod_depth 2.0, attack 0.004 s, release 0.08 s (the mute).
Empirical FluidR3 pitch sweep (28/33/38/40/43/45/48/52/55/59/62/64/67/71/74/
76/79/84, velocity 100): preset 28 audible **18/18, no gaps**, RMS 0.12 at
E1 → 0.0055 at C6; real writing zone 40–76 (E2–E6), money zone 40–55.
Range 28–84 = GM patch span; SOLO_RANGE (40, 76); SWEET_SPOT (40, 64).
Registration proof: `by_name('muted_guitar')` / `by_name('muted guitar')` /
`by_name('Electric Guitar (muted)')` → Electric Guitar (muted),
`by_program(28)` → Electric Guitar (muted) (distinct from 27 Clean Electric
and 29 Overdriven), `in_sweet_spot(45)` = True, `in_sweet_spot(80)` = False,
`stem_label = 'Electric_Guitar_muted'`; `registry_table()` row "| Guitar |
Electric Guitar (muted) | 28 | 28–84 | rhythm, comp, groove, accent,
texture, melody |"; convenience constant `MUTED_GUITAR`. Role: rhythm (16th
chops/scratches — the guitar as percussion), comp (3–4 note chops, NOT
6-string barres), groove (the mute duration IS the subdivision), accent
(palm-release open chords as contrast), texture (dead-string "chika"),
melody (short staccato single notes / octave hooks only) — NOT a sustaining
lead, NOT a pad, NOT a bass. Production: REVERB_TAIL 0.9 s (deliberately dry
— long tails blur the 16th detail), EQ cut 220 Hz −1.5 dB (palm-mute thump
vs bass), boost 3.2 kHz +2.5 dB (pick-attack click — the instrument has no
sustained energy so this is what makes it audible), 8 kHz air shelf only
+0.5 dB (damping removes the top by design), PAN −0.25 (double hard L/R at
±0.6 in funk/metal). Writing quirks: (1) NOT a sustain voice — every note is
attack + decay; if a phrase needs sustain, wrong patch; (2) alternate
funk_chop 0.12 / scratch 0.05 / ghost_note 0.04 durations so the hand-motion
groove reads, all-identical durations sound mechanical; (3) velocity IS the
dynamic (30–40 ghosts, 75–82 chops, 90+ accents) because the patch has little
natural sustain; (4) the FluidR3 patch is a one-shot — a long MIDI note does
NOT ring, use `open_accent` when you want the chord to ring; (5) **no unison
doubling** of two different melodic patches on the same pitches (2026-09-01
comb-filter rule) — two takes of the SAME part hard L/R is the standard
funk/metal production technique, not unison doubling.

**Warm Pad added** (2026-11-06): GM89, **Synth-family fifth entry** — the
classic WARM ANALOG synth pad ("Pad 2 (warm)": detuned triangle/saw stack
through a low-pass with slow attack + wide chorus — the 80s ballad /
synthwave / ambient bed; Juno-60 warm programs, OB-X pads, Vangelis
*Charlots of Fire* beds). The **DARK sibling of synth_pad GM88** ("Pad 1
(new age)") — the synth_pad entry already flagged FluidR3 preset 89 =
"Warm Pad" as the darker sibling; this entry claims it. Files:
`Synth/warm_pad/instrument.md` + `warm_pad.py`. Verified end-to-end
UnitMatrixComposer (1 bar, 1 section, 100 bpm, Warm Pad SOLO on ch0 —
C major / A minor pad chords — + drum-kit context on ch9) → **zero-drift ✓**
→ MIDI **177 bytes** → FluidSynth WAV **1,305,900 bytes** SOLO render
(FluidR3 via `discover_soundfont()`) ✓; RenderPipeline stems on disk
`track00_Pad_2_warm.wav` (1,305,900 B) + `track01_Drums.wav` (849,708 B) ✓;
solo-render spectral 4–8 kHz buzz **5.2%** (clean single voice, no
comb-filtering — a DARK pad, well under the 20% gate). Stem-label:
GM_PROGRAMS[89] = **"Pad 2 (warm)"** → sanitized `Pad_2_warm` (parens
stripped, spaces → underscore; STEM_LABEL matches the pipeline's real
sanitization, **no routing quirk**) and FluidR3 preset 89 = **"Warm Pad"**
(SF2 internal name differs cosmetically, no routing impact). Synthesis:
**Additive primary** (`sound/synthesis/additive.py` — the pad IS a detuned
harmonic stack, synth_pad/string_ensemble/organ precedent:
`ADDITIVE_HARMONICS["pad_warm"]` = [1.0, 0.78, 0.58, 0.40, 0.26, 0.15,
0.08] — strong fundamental, FASTER rolloff than pad_newage; weights are
RELATIVE, normalize to sum 1.0 before `apply_overtones()`), SYNTHESIS_DEFAULTS
attack 0.45 s (between string_ensemble 0.35 and synth_pad 0.55), detune
±0.015 (widest in the pad family — the analog chorus IS the identity),
stack 3, release 0.6, **decay_S 1e-4** (the 2026-10-12 additive quirk:
late-sustain envelope max **0.828** with decay_S 1e-4 vs **0.014** with
0.005 — collapse; measured). **Polysynth secondary** (PolyVoice — the
polyBLEP subtractive architecture IS the analog warm-pad model:
triangle core + 2 detuned saws ±7c, **low-pass 1400 Hz** — half of
synth_brass_1's 2800, the darkness IS the point —, resonance 0.35, env
attack 0.45/sustain 0.8/release 0.6, filter env follows the amp;
sustain holds: hold_ratio 1.90 vs release window). **PhaseModSynth
tertiary** (FM pad, saw carrier ratio 1.0, depth 1.5 — gentle, warm pads
are NOT brassy). Empirical FluidR3 pitch sweep (RMS, velocity 90, notes
36–108 step 12): preset 89 audible **7/7, no gaps** (RMS 760–1354,
essentially flat across the whole span, gentle treble rolloff; C8=108
still audible) — full-keyboard patch, SF2 never clips a composition.
Range 36–96 = idiomatic writing band (C2–C7), sweet spot 60–84 (C4–C6),
solo range 55–84. Registration proof: `by_name('warm pad')` /
`by_name('Pad 2 (warm)')` → Warm Pad, `by_program(89)` → Warm Pad (distinct
from 88 synth_pad), `in_sweet_spot(72)` = True, `in_sweet_spot(24)` =
False, `stem_label = 'Pad_2_warm'`; `registry_table()` row "| Synth | Pad 2
(warm) | 89 | 36–96 | pad, harmony, texture, drone, accent |"; convenience
constant `WARM_PAD`. Role: pad, harmony, texture, drone, accent — the
anti-new-age dark bed (ballads, synthwave verses, ambient underscores);
NOT a lead (slow attack smears), NOT rhythm/comp, NOT bass. Production:
REVERB_TAIL 3.0 s (between string_ensemble 2.6 and synth_pad 3.2 — blooms
in a big hall but keeps more body than the new-age shimmer), EQ cut 250 Hz
(the strong fundamental piles the low-mid fast — lower than synth_pad's
300), boost 2.4 kHz (the warm BODY band, contrast new-age 3.8 kHz), gentle
7.5 kHz air shelf (warmth rolls the top off, contrast new-age 9.5 kHz
+2.0), PAN centre. Writing quirks: (1) hold chords ≥ 1.5–2 s or the slow
attack never speaks; (2) pad-stacking unison (warm pad + another pad/
string on the same pitches) is the definitive comb-filter buzz — octaves
or zone-splitting only; (3) GM90 "Pad 3 (polysynth)" / GM92 "Pad 5
(bowed)" / GM93 "Pad 6 (metallic)" / GM94 "Pad 7 (halo)" remain future
sibling candidates.

**Honky-tonk Piano added** (2026-11-07): GM3 (0-based program 3 = 4th GM
entry), **Keys-family eleventh entry** — the deliberate-detune tack/saloon
piano (ragtime, stride, boogie-woogie, country honky-tonk). Verified end-to-end
through the registry: UnitMatrixComposer stride bar → zero-drift ✓ → MIDI
(245 B) → FluidSynth WAV solo (808,748 B) ✓; RenderPipeline stem label
`track00_Honky-tonk_Piano.wav` ✓ (GM_PROGRAMS[3] = "Honky-tonk Piano" — the
sanitizer keeps the HYPHEN, only spaces/parens/slashes are rewritten; FluidR3
preset 3 = "Honky Tonk", hyphen dropped, cosmetic only, no routing impact).
Synthesis **ModalSynth primary** with a custom `HONKY_TONK_MODES` bank where
every partial is DOUBLED at a +17-cent twin (440.0 / 444.3 Hz): envelope-AM
measurement on the rendered bank gives a **4.50 Hz beat** (gate 3.5–5.5) with
AM depth 1.25, vs the no-twin control whose dominant envelope peak is 8.50 Hz
— the beating IS the instrument, not an artifact. Additive secondary
(`ADDITIVE_HARMONICS["honky_tonk"]` = [1.0, 0.62, 0.44, 0.27, 0.16, 0.09, 0.04],
stack 2, detune ±0.010); PhaseModSynth tertiary (ratio 2.01, depth 1.6). Range
33–96 (A1–C7 — real piano A0–C8, but the patch is mud below A1 and tack-noise
above C7), sweet spot 55–84, solo 48–84; zones bass 33–47 / mid_low 48–59 /
mid 60–71 / high 72–96. Role: rhythm, harmony, melody, bass, ornament, color.
Solo render 4–8 kHz buzz 0.5% (clean, no comb filtering). Empirical FluidR3
pitch sweep (RMS, notes 24–108 step 12): audible 8/8, no gaps (968→100, the
natural upright rolloff). Production: REVERB_TAIL 1.4 s (small wooden ROOM,
not a hall — a hall smears the tack attack), EQ cut 300 Hz cabinet boom, boost
1800 Hz nasal honk, air shelf 8 kHz +1.5. Registration proof:
`by_name('honky tonk')` / `by_name('Honky-tonk Piano')` → Honky-tonk Piano,
`by_program(3)` → Honky-tonk Piano, `in_sweet_spot(67)` True /
`in_sweet_spot(24)` False, `stem_label = 'Honky-tonk_Piano'`; `registry_table()`
row "| Keys | Honky-tonk Piano | 3 | 33–96 | rhythm, harmony, melody, bass,
ornament, color |"; convenience constant `HONKY_TONK`. Writing quirks: (1) the
detuned unisons mean sustained notes inherently wobble — do NOT also stack a
second melodic patch on the same pitches (double beating = seasick); (2) keep
tack-piano chords OPEN (3 notes max in the mid) — thick closed voicings turn the
dense detuned spectrum to mush; (3) it is a rhythmic/piercing voice, not a
sub-bass foundation — pair with a real bass below A1. Remaining sibling
candidates: GM31 "Guitar harmonics", GM55 "Orchestra Hit", GM49 "String
Ensemble 2", GM36 "Slap Bass 1".

**Orchestra Hit added** (2026-11-09): GM55, **Synth-family sixth entry** —
the iconic ONE-SHOT ensemble stab (dense layered brass + strings + choir
stack fired with a razor attack + fast exponential decay — the
punctuation of 80s pop, hip-hop, film trailers and game scores: Yes
"Owner of a Lonely Heart", MTV/network ident stabs, beat drops)
(instrument.md + orchestra_hit.py), verified end-to-end UnitMatrixComposer
(1 bar, 1 section, Orchestra Hit SOLO on ch0 + drum-kit context on ch9)
→ **zero-drift ✓** → MIDI **205 bytes** → FluidSynth WAV **851,500 bytes**
SOLO render (FluidR3 via `discover_soundfont()`) ✓; RenderPipeline stems
on disk `track00_Orchestra_Hit.wav` (851,500 B) + `track01_Drums.wav`
(835,628 B) ✓; stem label `GM_PROGRAMS[55]` = **"Orchestra Hit"** AND
FluidR3 preset 55 = **"Orchestra Hit"** — labels match exactly, **no
quirk** (contrast GM74 Flute → "Recorder", GM109 → "Bag pipe", GM111 →
"Shanai"); solo-render spectral 4–8 kHz buzz **2.4%** (clean single
voice, no comb-filtering). Synthesis: **Additive primary**
(`sound/synthesis/additive.py` — the classic recipe IS a dense harmonic
stack with a razor attack + fast exponential decay:
`ADDITIVE_HARMONICS["orchestra_hit"]` [1.0, 0.88, 0.75, 0.60, 0.45,
0.32, 0.20, 0.12], SYNTHESIS_DEFAULTS attack 0.005 s, decay_S 0.002 —
FAST collapse = the one-shot behaviour, contrast the pads' 1e-4 hold
recipe —, sustain_level 0.35, detune ±0.008, stack 3), **PhaseModSynth
secondary** (saw carrier ratio 1.0, depth 3.5 — between synth_brass_1
3.2 and overdriven 4.0 —, attack 0.005, release 0.40, sustain 0.30),
**Polysynth tertiary** (saw stack, low-pass 3500, razor gate 0.005,
decay 0.4, sustain 0.3, 3 unison). Smoke tests: Additive stack peak
113.8; PhaseModSynth stab peak 0.750. Empirical FluidR3 pitch sweep
(RMS, velocity 90, notes 36/48/60/72/84/96): preset 55 audible **6/6,
no gaps** (1345 → 374, smooth rolloff, loudest at the bottom) —
full-keyboard patch, SF2 never clips a composition. Range 36–96 =
idiomatic writing band, sweet spot 55–79 (G3–G5 — the classic hit
register), solo range 48–84. Registration proof: `by_name('orchestra
hit')` → Orchestra Hit, `by_program(55)` → Orchestra Hit (distinct from
54 Synth Voice / 56 Trumpet / 62 Synth Brass 1), `in_sweet_spot(67)` =
True, `in_sweet_spot(24)` = False, `stem_label = 'Orchestra_Hit'`;
`registry_table()` row "| Synth | Orchestra Hit | 55 | 36–96 | accent,
stab, rhythm, punctuation, texture, lead |"; convenience constant
`ORCHESTRA_HIT`. Role: accent (downbeat hits, drop stabs, sfz smashes —
the punctuation voice), stab (rhythmic hit patterns), rhythm (the hit
can BE the rhythmic hook), punctuation/texture (riser bottoms, section
markers — sparse use = maximum impact), lead (rare unison-hit accents
72–84) — NOT a pad/harmony voice (no sustain — use synth_pad/warm_pad/
string_ensemble), NOT a bass voice. **One-shot quirk**: the FluidR3
patch is a sample — it fires once per note-on and decays; a long MIDI
note does NOT sustain (the muted-guitar lesson). Write short strikes
(≤ 0.2 bar) and let the decay + reverb work. Production: REVERB_TAIL
1.8 s (hits want PUNCH, not wash — a one-shot in a 3 s verb is a
smear), EQ cut 300 Hz / boost 2.5 kHz presence (the stab bite band) /
9 kHz air shelf, PAN centre (±0.3 L/R spread on wide doubled hits).
Selection note: GM55 was collision-free — `by_program(55)` had no owner
and the stem `Orchestra_Hit` was unclaimed. Remaining sibling
candidates: GM31 "Guitar harmonics", GM49 "String Ensemble 2", GM36
"Slap Bass 1".
