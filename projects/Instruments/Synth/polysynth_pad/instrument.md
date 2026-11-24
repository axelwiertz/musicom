---
type: instrument
family: Synth
name: Pad 3 (polysynth)
midi_program: 90
gms: "Pad 3 (polysynth)"
range_min: 36
range_max: 96
solo_range: [55, 84]
role: [pad, harmony, texture, drone, accent]
synthesis: [polysynth, additive, phase_mod]
---

# Pad 3 (polysynth) (GM90 — Pad 3)

## MIDI / GM

- **Program**: 90 (GM1 "Pad 3 (polysynth)"). The classic **analog polysynth
  pad**: a stack of detuned saw/triangle oscillators through a resonant
  low-pass filter with a slow attack and wide ensemble chorus — the Roland
  Juno-106 / JX-8P, Oberheim OB-X, Sequential Prophet-5, Korg Poly-61 pad
  family. The THIRD member of the KB's synth-pad block: GM88 "Pad 1 (new
  age)" is bright/digital glass (air + shimmer), GM89 "Pad 2 (warm)" is
  dark/round analog, and **GM90 is the middle** — rounder and slower than
  the new-age shimmer, but with MORE mid presence and a faster attack than
  the warm pad (the classic 80s pop-ballad / synthwave / Detroit-techno pad).
  FluidR3 preset 90 = **"Polysynth"** (verified from phdr — the ONLY synth
  pad whose SF2 name is the engine name).
- **Enum note**: `structures/instrument.py` `MidiInstrument` exposes only 10
  instruments and has NO polysynth constant — use the raw GM number 90; the
  registry is the full KB.
- **Channel**: melodic channel (0–9). Channel 9 with program 90 would trigger
  the drum-kit map and the ch9 program-0 fallback label
  `Acoustic_Grand_Piano` (ch9 quirk — see timpani lesson).
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 90 =
  **"Polysynth"** (verified from phdr). RenderPipeline stem label:
  GM_PROGRAMS[90] = "Pad 3 (polysynth)" → sanitized `trackXX_Pad_3_polysynth.wav`
  (spaces → `_`, parens stripped) — STEM_LABEL `Pad_3_polysynth` matches the
  pipeline's real sanitization, **no routing quirk**.

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 36–96 | C2–C7 | idiomatic writing band (GM patch plays the full keyboard) |
| Low | 36–55 | C2–G3 | sub/mid-bass pad — roots, drone bottom (mud below C2) |
| Mid | 56–79 | G3–G5 | PRIMARY chord-pad body — the workhorse band |
| High | 80–96 | G5–C7 | analog top — rounder than the new-age shimmer (filter rolls the saw off) |

Empirical FluidR3 pitch sweep (RMS, velocity 90, notes 36–108 step 12):
preset 90 audible everywhere in the writing band — no gaps, no ceiling —
SF2 never clips a composition (full sweep data in REPORT.md).

## Articulations

| Technique | Velocity | Duration | Timbre |
|---|---|---|---|
| Sustain | 65–82 | full | slow-swelling held pad — THE default gesture |
| Legato | 68 | 1.0× | seamless voice crossfade — chord changes |
| Swell | 80–88 | 1.0× | whole-bar crescendo — the ballad build |
| Bloom | 62–70 | 1.25× | extra-long swell past the bar — feeds the reverb, the analog signature |
| Staccato | 62–70 | 0.25× | short pad "blip" — rhythmic filter-pulse motif |
| Marcato | 82–90 | 0.85× | attack override — plucked/bell onset (Juno "pluck" style) |
| Drone | 58–64 | 1.0× | static sustained harmony — ambient bed |
| Accent | 84–94 | 0.9× | hard entrance — downbeat hit, then bloom |

## Timbre DNA

- **Harmonic content**: saw-stack fundamental with a low-pass rolloff — the
  body lives in the low-mid + 2–3 kHz presence (measured FluidR3 solo
  spectral centroid sits between the warm pad's ~1.8–2.5 kHz and the
  new-age shimmer; more saw edge than warm_pad's triangle-only roundness)
- **Attack**: 200–450 ms slow swell — between warm_pad 0.45 and
  synth_strings_1 0.03; chords ENTER, they don't stab
- **Decay/sustain**: indefinite while held (sustain 0.85), release 0.6 s —
  tails feed the reverb
- **Chorus**: the widest detune in the pad family (±7 cents × 4 unison
  voices) — the analog ensemble blur IS the identity
- **Character**: round, present, enveloping — "the chord you can hug, with
  a pulse"; instantly 80s ballad / synthwave / techno; the middle sibling
  between GM88 (glass) and GM89 (dark)

## Role in Arrangement

- **Pad** — the harmonic canvas: sustained chords, the song-bed voice
- **Harmony** — 3–5 note chords fully idiomatic (the analog stack blooms in
  space)
- **Texture** — ambient beds, evolving swells, drone washes
- **Drone** — static sustained harmony / root pedals (low zone 36–55)
- **Accent** — soft marcato entrances on downbeats (NOT stabs — slow attack
  smears; use synth_brass_1 for stabs)
- **NOT** a lead voice (slow attack — melodic runs smear; the lead pad role
  goes to synth_voice), NOT a rhythm/comp voice, NOT a bass voice (use the
  Bass family)
- Polyphonic: chords fully idiomatic; unison doubling with another melodic
  patch on the same pitches is NOT (comb-filter rule — the 2026-09-01
  lesson; pad-stacking unison is the classic buzz machine)

## Synthesis Engines (musicom)

1. **Polysynth** (`sound/synthesis/polysynth.py`, PolyVoice) — **primary**.
   This is the ONE instrument in the KB whose GM name IS the engine: the
   polyBLEP subtractive architecture (3 oscillators + multimode filter +
   ADSR + unison) is the exact physical model of the analog polysynth pad.
   `POLYSYNTH_DEFAULTS`: saw core + ±7-cent detuned saw + triangle body
   (osc3_level 0.7), **low-pass 1800 Hz** (between warm_pad 1400 and
   synth_brass_1 2800 — rounder than warm but with more mid presence),
   resonance 0.3, env attack 0.35 s / sustain 0.85 / release 0.6, **4
   unison voices** (the widest chorus in the Synth family).
2. **Additive** (`sound/synthesis/additive.py`) — **secondary**, the
   pad-family engine (synth_pad/warm_pad precedent):
   `ADDITIVE_HARMONICS["pad_polysynth"]` =
   [1.0, 0.75, 0.55, 0.38, 0.25, 0.15, 0.09] — strong fundamental, faster
   rolloff than pad_newage. SYNTHESIS_DEFAULTS: attack 0.35 s, detune
   ±0.012, stack 4, release 0.6, sustain 0.9, **decay_S 1e-4** (the
   2026-10-12 additive quirk — a pad recipe MUST use decay_S ~1e-4 or the
   chord collapses).
3. **PhaseModSynth** (`sound/synthesis/phase_mod.py`) — **tertiary** FM pad:
   saw carrier, ratio 1.0, depth 1.8 (between warm 1.5 and synth_brass_1
   3.2 — the analog pad fattens, never honks), attack 0.4, release 0.6.

## Production

- **Reverb**: hall 2.6–3.2 s — REVERB_TAIL 3.0 s; same as warm_pad: the
  analog pad blooms in a big hall but keeps body (new-age 88 needs the full
  3.2 air wash; the polysynth pad is rounder, so 3.0 keeps it grounded)
- **EQ**: cut ~250 Hz (the saw stack + triangle sub piles the low-mid
  fast — same cut as warm_pad); boost ~2.8 kHz +2 dB (the mid BODY presence
  band: brighter than warm_pad's 2400, more saw edge); gentle 8 kHz +1.5 dB
  air shelf (the low-pass rolls the saw off by design)
- **Pan**: center for the composed stem; ±0.4 L/R spread on wide stereo
  swells (same as the other pads)

## Layering / writing quirks

- Idiomatic doubling is **octaves or zone-splitting** (55–79 + 80–96),
  NEVER unison with another melodic patch on the same pitches (the
  2026-09-01 comb-filter lesson)
- Hold chords ≥ 1.5–2 s or the slow attack never speaks (same pad-writing
  quirk as synth_pad/warm_pad); write a gap before chord changes or the
  swell smears into the next harmony
- The polysynth pad is the MIDDLE choice: when the arrangement needs glass
  (Enya-style air), GM88; dark round (ballads, ambient underscores), GM89;
  round-but-present 80s analog body (synthwave, pop ballads, techno beds),
  GM90
- GM91 "Pad 4 (choir)" = Space Voice, GM92 "Pad 5 (bowed)" = Bowed Glass,
  GM93 "Pad 6 (metallic)", GM94 "Pad 7 (halo)", GM95 "Pad 8 (sweep)" are
  future sibling candidates — GM90 is the analog member of the Pad 88–95
  family

## Verification

- GM90 → stem `trackXX_Pad_3_polysynth.wav` (GM_PROGRAMS[90] = "Pad 3
  (polysynth)" sanitized; FluidR3 preset 90 = "Polysynth" — internal SF2
  name matches the engine name, **no routing quirk**)
- `by_name('polysynth pad')` / `by_name('pad 3 (polysynth)')` →
  Pad 3 (polysynth), `by_program(90)` → Pad 3 (polysynth) (distinct from
  88 synth_pad / 89 warm_pad), `in_sweet_spot(72)` = True,
  `in_sweet_spot(24)` = False
- Empirical pitch sweep: preset 90 audible across the full writing band, no
  gaps (full RMS table in REPORT.md)
- Buzz check: solo render passes the 4–8 kHz spectral gate (single voice +
  single patch, no comb-filtering)
- Zero-drift: pad chord ends flush at BAR (terminal landmark)
- Engine smoke: Polysynth pad chord sustains (tail_rms/peak ≥ 0.5 — the
  analog pad holds, it doesn't decay); Additive pad chord holds (late
  envelope with decay_S 1e-4)

## Stem label / quirks

- GM_PROGRAMS[90] = "Pad 3 (polysynth)" → sanitized stem `Pad_3_polysynth`
  (spaces → underscore, parens stripped) — STEM_LABEL matches the pipeline's
  real sanitization, **no routing quirk**
- FluidR3 preset 90 = "Polysynth" — the internal SF2 name IS the engine
  name (unlike 88 "Fantasia" / 89 "Warm Pad"); stems are labelled from
  GM_PROGRAMS, not the SF2
- Enum `MidiInstrument` has NO polysynth constant (10-instrument legacy
  enum) — use raw GM 90; the registry is the full KB
- Channel quirk: melodic channel (0–9) — channel 9 triggers the drum map
- FluidR3 polysynth preset is a full-keyboard patch (no per-note ceiling) —
  never clips; the slow attack means short blips bloom into the next note —
  write stabs with a gap or accept the smear (same as synth_voice/warm_pad)
