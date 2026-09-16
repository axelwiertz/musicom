# REPORT — Taiko (GM116) — nightly instrument job 2026-09-16

## Instrument

**Taiko** (Wadaiko) — GM program **116** ("Taiko Drum"), new **World**
family entry (eighth member; after fiddle 2026-09-11). The Japanese
kumi-daiko festival drum: tacked cowhide head on a hollowed keyaki
(zelkova)-log shell, struck with thick cedar bachi, played on a slanted
stand. Ceremonial/theatrical accent voice — pairs with the KB's koto,
shamisen, shenai (completes a Japanese ensemble: koto + shamisen + shenai +
taiko). Chosen from the remaining GM116/113/115/112 World block; musically
strongest candidate (rhythm backbone for the existing World melody
instruments).

## Files written

- `World/taiko/instrument.md` — full research (YAML frontmatter + sections)
- `World/taiko/taiko.py` — importable constants
- `_test/verify_taiko.py` — registry-backed verification script
- `_test/taiko_test.mid` (126 bytes), `_test/taiko_test.wav` (1,041,452
  bytes), `_test/stems_taiko/track00_Taiko_Drum.wav` + bass stem
- `instrument_registry.py` — registered (module + constant + role + checks)
- `registry.md` — changelog entry, Registry table row, stem-label table row

## Registration (registry proof)

`_INSTRUMENT_MODULES` entry `"World.taiko.taiko": "taiko"`, constant
`TAIKO = ALL_INSTRUMENTS["taiko"]`, role branch ("taiko drum" → accent,
rhythm, drone, ornament), `__main__` verification lines. Full
`registry_table()` run (2026-09-16):

```
| World | Taiko Drum | 116 | 36–67 | accent, rhythm, drone, ornament |
```

Verification lines:

```
TAIKO.midi_program = 116 (should be 116)
by_name('taiko') = <Instrument Taiko Drum (family=World, program=116, range=36-67)>
by_name('taiko drum') = <Instrument Taiko Drum (family=World, program=116, range=36-67)>
by_program(116) = <Instrument Taiko Drum (family=World, program=116, range=36-67)>
TAIKO.in_sweet_spot(50) = True
Registry: ALL_INSTRUMENTS count = 41
```

Full run: `cd /opt/data/projects/Instruments &&
/opt/data/micromamba/envs/musicom/bin/python instrument_registry.py` —
prints the full 41-instrument table including the Taiko row above.

## Constants (all through the registry)

| Constant | Value |
|---|---|
| MIDI_PROGRAM | 116 |
| GM_NAME / STEM_LABEL | "Taiko Drum" (both; FluidR3 preset 116 = "Taiko Drum") |
| RANGE_MIN–MAX | 36–67 (C2–G4, melodic taiko patch span) |
| SOLO_RANGE | (40, 55) E2–G3 — chū-daiko festival core |
| SWEET_SPOT | (45, 57) A2–A3 — fullest chest tone |
| ZONES | low 36–45 (ō-daiko booms), mid 46–57 (festival DON/DOKO), high 58–67 (shime/koda slaps) |
| ARTICULATIONS | don (96, 0.8), doko (74, 0.4), ka_rim (88, 0.15), slap (90, 0.25), roll (70, 0.06), muffle (58, 0.12), accent (99, 0.9), soft (50, 0.7) |
| SYNTHESIS / MODAL_PRESET | modal / "drum" (closest stock bank; too fast, no body) |
| TAIKO_MODES | (90, 1.0, 2.6) shell · (110, 0.70, 2.8) head (0,1) · (176, 0.35, 3.5) 1.6× · (234, 0.22, 4.5) 2.13× · (290, 0.12, 6.0) 2.64× |
| DRUM606_DEFAULTS | freq 80, decay 1.4, pitch_sweep 1.45 |
| FM_DEFAULTS | sine carrier, ratio 1.59, depth 1.0, attack 0.001, release 0.8 |
| REVERB_TAIL | 1.6 s (between xylophone 0.9 tight and timpani 2.2 hall) |
| EQ_BODY / PRESENCE / AIR | (300, −1.5) / (1800, +2.0) / (6000, +0.5) |
| PAN | 0.0 (kumi-daiko arc −0.3..+0.3, ō-daiko slightly left) |

midi_to_freq: standard `440 · 2^((m−69)/12)`.

## Role

accent, rhythm, drone, ornament — kuchi-shoga rhythm spine (DON don DOKO
DON) under koto/shamisen/shenai lines, kabuki/noh punctuation, kumi-daiko
downbeat landings. NOT a melodic lead (patch is tuned but the idiom is
rhythm + accent), NOT a bass melodic voice.

## Synthesis engine

**ModalSynth** (`sound/synthesis/modal.py`) primary, with custom
`TAIKO_MODES`: tuned circular-head (0,1) mode (110 Hz at the A2 reference,
pitch-shifts with the played note — timpani convention) coupled to
inharmonic Bessel partners 1.6×/2.13×/2.64× (the membrane family) AND a low
hollowed-keyaki shell mode ~90 Hz — the chest thump that IS the taiko
sound. Measured: shell band 60–110 Hz = **40.7%** of total energy (head
band 21.9%, 1.6× partner 11.8%); late(1.0–1.5 s) rms/peak **0.019** vs the
timpani bank's 0.134 — taiko rings ~7× shorter than a timpano (tacked hide
kills energy; decay rates 2.6–6.0 sit between timpani 0.9–3.0 and marimba
8–20). Stock 'drum' preset confirmed too-fast (late 0.0000).
**DrumSynth606** `tom` (freq 80, decay 1.4, sweep 1.45) = strike thump alt,
peak 1.000, len 1.82 s. **Karplus-Strong EXPLICITLY REJECTED** (no string —
timpani precedent). PhaseModSynth = cheap fallback (ratio 1.59 = the (1,1)
partner).

## Verification results (verify_taiko.py, all passed)

- **Registry import**: `by_name('taiko')` / `by_program(116)` → Taiko Drum
  Instrument object ✓ (import THROUGH the registry, not the raw module)
- **Zero-drift**: True (OK) — 1 bar, 2 voices, last event ends flush at 1920
- **MIDI**: `_test/taiko_test.mid` — 126 bytes (> 40 ✓)
- **WAV solo render** (voice 0 only, `discover_soundfont()` →
  FluidR3_GM.sf2, fluidsynth `-ni -g 1.2`): 1,041,452 bytes (> 40 ✓)
- **Spectral buzz gate**: 4–8 kHz buzz 4.4% (OK, no comb-filtering — solo
  render, no unison doubling; context was ONE low bass note at E1, an
  octave below the taiko floor)
- **Stem label**: GM_PROGRAMS[116] = 'Taiko Drum' →
  `track00_Taiko_Drum.wav` on disk (labels match exactly, **no quirk**)
- **SF2 preset 116** (phdr chunk of FluidR3_GM.sf2) = 'Taiko Drum' ✓
- **ModalSynth custom bank**: shell body 40.7% dominant, 1.6× partner 11.8%,
  ring ordering taiko 0.0187 < timpani 0.1344 ✓
- **DrumSynth606 thump**: peak 1.000, 1.82 s ✓
- **FluidR3 pitch sweep** (RMS ≥ 0.005 threshold, notes 36/40/45/50/55/60/
  64/67): **8/8 audible** (RMS 0.105–0.140, monotone decrease up the range,
  no gaps — SF2 never clips a composition)

## Quirks found

- **No stem-label quirk**: GM_PROGRAMS[116] = "Taiko Drum" AND FluidR3
  preset 116 = "Taiko Drum" — both match exactly (unlike Bag_pipe/Shanai).
- **Tuned-drum channel quirk** (timpani lesson applies): GM116 is pitched —
  MUST use a melodic channel (0–9) with program 116. Channel 9 would
  trigger the drum-kit map and the `Acoustic_Grand_Piano` program-0
  fallback stem label.
- **Identity quirk**: GM116 is a TUNED drum (pitch follows the note) but
  the taiko IDIOM is rhythm + accent, not melody. Distinct from GM117
  Melodic Tom (higher, tom-tuned for melodic fills).
- **Range note**: 36–67 is the melodic patch span; the real ō-daiko
  fundamental sits ~60–80 Hz (B1–E2) and the composition core is E2–G3
  (chū-daiko festival zone). Above G4 you are writing shime-daiko
  territory — a separate smaller drum in real ensembles.
- **KS rejected** (first World-family instrument where KS is rejected
  rather than demoted; timpani was the first KB-wide).
- **Neighbor quirk context**: GM112 label "Tinkle Bell" vs FluidR3 preset
  "Tinker Bell" (spotted in the phdr sweep, not part of this entry).

## Registry state

`instrument_registry.py` loads 41 instruments (34 solo + 6 voice-like
family members + umbrella). Taiko visible to the nightly
`daily-algorithmic-composition-production` composition job as
`TAIKO` / `by_name("taiko")` / `by_program(116)`.
