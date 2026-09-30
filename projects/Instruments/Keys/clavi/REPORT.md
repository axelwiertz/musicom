# Clavi (Hohner Clavinet D6) — Instrument Research Report

**Date**: 2026-09-30
**Family**: Keys (seventh entry)
**Instrument**: Clavi (GM7) — the rubber-hammer struck-string electric
clavichord, invented by Ernst Zacharias for Hohner (1964). The funkiest
keyboard ever built: Stevie Wonder "Superstition", Billy Preston
"Outa-Space", Herbie Hancock "Chameleon", Led Zeppelin "Trampled Under
Foot", Steely Dan "Kid Charlemagne" solo.

## Instrument

| Field | Value |
|---|---|
| GM Program | **7** (GM1 Clavi — 0-based; GM_PROGRAMS[7] = "Clavi") |
| Pipeline stem label | `trackXX_Clavi.wav` (GM_PROGRAMS[7] = "Clavi") |
| FluidR3 preset | 7 = "Clavinet" (phdr-verified) — cosmetic expansion, no routing impact |
| Range (MIDI) | 29–89 (F1–F6, standard 60-key Clavinet D6) |
| Sweet spot | 48–72 (C3–C5 — the funky rhythm guitar register) |
| Solo range | 29–89 (full 60-key compass) |
| Role | lead, rhythm, accent, ornament, countermelody |
| Synthesis engine | **Karplus-Strong** (primary), ModalSynth 'string' (fallback) |

## Range & zones

| Zone | MIDI | Pitches | Character |
|---|---|---|---|
| Low (bass) | 29–47 | F1–B2 | thumpy, percussive, rubbery — the funk bass zone |
| Middle (sweet) | 48–72 | C3–C5 | funky rhythm guitar register — the iconic voice |
| High (treble) | 73–89 | C#5–F6 | bright, clucky, nasal — wah lead register |

## Articulations

| Technique | Velocity | Duration | Character |
|---|---|---|---|
| Pluck | 75–85 | full | standard rubber-hammer strike |
| Chord chop | 95–108 | 0.7× | funk chord stab (Superstition) |
| Hard | 100 | 0.8× | accented — brighter attack |
| Soft | 55–70 | full | gentle touch |
| Staccato | 70–85 | 0.2× | tight funk cut |
| Muted | 60–75 | 0.4× | hand-damped nasal |
| Accent | 90–105 | 0.9× | sforzando |
| Wah | 80–95 | 0.6× | wah-pedal note |

## Synthesis engine

**Karplus-Strong** (`sound/synthesis/karplus_strong.py`, SP-011) —
struck waveguide with rubber mute damping. The clavinet IS a
rubber-tipped hammer striking a steel string with a rubber mute at the
bridge — the exact physical model is a struck waveguide with high
damping. Key parameters:

- `loop_gain`: **0.9960** — SHORTEST in the plucked/struck KB set
  (harpsichord 0.9980, harp 0.9985, sitar 0.9975, banjo 0.9960). The
  rubber mute kills energy ~2–3× faster than the harpsichord's cloth
  damper. Ring ~0.3–1.5 s.
- `noise_component`: **0.03** — the rubber "cluck" at note onset, the
  clavinet's signature percussive attack. Higher than any other KS
  instrument in the KB.
- `width`: 0.3 — focused, mono-like stereo (compact keyboard).

ModalSynth 'string' preset is the fallback (harmonic stack, fast decay).
PhaseModSynth gives a passable FM electric piano substitute.

## Production defaults

- **Reverb**: 1.0 s — short room/plate. The clavinet is a DRY instrument;
  too much reverb washes out the percussive attack.
- **EQ body**: cut 400 Hz (−2.5 dB) — reduce boxy case resonance.
- **EQ presence**: boost 2.5 kHz (+3.0 dB) — the midrange "honk" that
  cuts through a funk mix (1–3 kHz identity zone).
- **EQ air**: 7 kHz (+1.5 dB) — subtle string shimmer (rubber mute rolls
  off above 6 kHz naturally).
- **Pan**: 0.0 (center solo); L 20–30 for a funk section placement.
- **Effects (idiomatic)**: wah pedal / auto-wah / envelope filter, phaser,
  amp simulation (Fender Twin, Leslie). The clavinet was designed to be
  plugged into an amplifier.

## Registration proof

`instrument_registry.py` updated:
- `_INSTRUMENT_MODULES` entry: `"Keys.clavi.clavi": "clavi"`
- convenience constant: `CLAVI = ALL_INSTRUMENTS["clavi"]`
- verification lines added to `__main__`

Registry run output (showing the new row + verification):

```
| Keys | Clavi | 7 | 29–89 | lead, rhythm, accent, ornament, countermelody |
...
  CLAVI.midi_program = 7 (should be 7)
  by_name('clavi') = <Instrument Clavi (family=Keys, program=7, range=29-89)>
  by_program(7) = <Instrument Clavi (family=Keys, program=7, range=29-89)>
  CLAVI.in_sweet_spot(60) = True
  CLAVI.range_min = 29 CLAVI.range_max = 89
```

Verified via import through the registry: `from instrument_registry import
by_name; by_name('clavi')` resolves to the Clavi Instrument object.

## Verification results (verify_clavi.py)

| Check | Result |
|---|---|
| Zero-drift validate | **TRUE (OK)** — 1-voice unit ends flush at BAR |
| MIDI export | `Keys/clavi/clavi_test.mid` (145 bytes) ✓ > 40 |
| FluidSynth WAV (SOLO render) | `Keys/clavi/clavi_test.wav` (743,212 bytes) ✓ |
| Spectral check (4–8 kHz buzz) | **3.1%** — OK, clean single voice, no comb-filtering |
| Stem label (pipeline GM_PROGRAMS[7]) | "Clavi" — STEM_LABEL matches, no quirk |
| FluidR3 preset 7 phdr | "Clavinet" (cosmetic — pipeline says "Clavi") |
| Stem render | `track00_Clavi.wav` (743,212 bytes) ✓ |
| KarplusStrong smoke | C4 peak 0.314, tail ratio 0.0013 — rubber mute kills energy fast ✓ |
| ModalSynth 'string' | peak 0.900, tail ratio 0.063 ✓ |

### Key measurements

- **Karplus-Strong rubber-mute decay**: tail_rms/peak 0.0013 at 0.5 s —
  the SHORTEST ring in the plucked/struck set. The rubber mute at the
  bridge kills string energy fast, confirming the 0.9960 loop_gain choice
  (vs harpsichord 0.9980 which rings 2–5 s).

## Quirks & lessons found

1. **Stem label "Clavi" vs SF2 "Clavinet"**: pipeline GM_PROGRAMS[7] =
   "Clavi" (GM abbreviation), while FluidR3 preset 7 = "Clavinet" (full
   name). This is cosmetic only — the MIDI program number 7 selects the
   preset, so routing is unaffected. STEM_LABEL = "Clavi" matches the
   pipeline's real label so stem-file lookups work.
2. **Shortest ring in the KB**: the clavinet decays in 0.3–1.5 s (rubber
   mute), faster than any plucked/struck instrument in the set. Composition
   jobs MUST write tight rhythmic patterns, NOT long sustained notes.
3. **No velocity sensitivity**: real clavinet has fixed rubber-hammer
   strike force; velocity is a creative affordance in the KB. Dynamics
   come from signal processing (wah, envelope filter, amp), not the key.
4. **NOT a sustain/pad voice**: never use clavinet for held chords or
   ambient textures — it dies too fast.
5. **Melodic channel (0–9)**: program 7 on channel 9 would trigger the
   drum-kit map and the `Acoustic_Grand_Piano` program-0 fallback label
   (timpani lesson).

## Files

- `instrument.md` — full research reference
- `clavi.py` — importable constants (MIDI_PROGRAM, GM_NAME, STEM_LABEL,
  RANGE_MIN/MAX, SOLO_RANGE, ZONES, ARTICULATIONS, SYNTHESIS,
  KARPLUS_DEFAULTS, CLAVI_MODES, FM_DEFAULTS, REVERB_TAIL, EQ_*, PAN,
  midi_to_freq)
- `verify_clavi.py` — the verification script (ALL CHECKS PASSED)
- `clavi_test.mid`, `clavi_test.wav`, `stems_clavi/` — artifacts

Registered in `instrument_registry.py` → key `clavi`, constant `CLAVI`.
