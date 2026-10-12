---
type: instrument
family: Synth
name: Synth Pad
midi_program: 88
gms: "Pad 1 (new age)"
range_min: 36
range_max: 96
solo_range: [55, 84]
role: [pad, harmony, texture, drone, accent]
synthesis: [additive, phase_mod, polysynth]
---

# Synth Pad (Pad 1, new age)

## MIDI / GM

- **Program**: 88 (GM1 "Pad 1 (new age)" — the classic slow-attack digital
  synth pad: Roland D-50-era LA synthesis, detuned oscillator stack + chorus
  + long swell). GM program numbers are 0-based, so 88 is the 89th entry.
- **Enum note**: `structures/instrument.py` `MidiInstrument.SYNTH_PAD = 88` —
  for once the enum value matches the raw GM program exactly (unlike
  `FLUTE = 74` / `STRING_ENSEMBLE = 49`, which are legacy off-by-ones). The
  registry is still the full KB; 88 really is "Pad 1 (new age)".
- **Channel**: melodic channel (0–9). Channel 9 with program 88 would trigger
  the drum-kit map and the program-0 fallback label `Acoustic_Grand_Piano`
  (ch9 quirk — see timpani lesson).
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 88 = 
  **"Fantasia"** (verified from phdr — FluidR3 names the GM "Pad 1 (new
  age)" patch "Fantasia"; cosmetic only, **no routing impact**; preset 89 =
  "Warm Pad" is the darker mid-heavy sibling). RenderPipeline stem label:
  GM_PROGRAMS[88] = "Pad 1 (new age)" → sanitized
  `trackXX_Pad_1_new_age.wav` — matches STEM_LABEL "Pad_1_new_age", **no
  quirk** (parens are the only wrinkle: strip them, spaces → underscores).

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 36–96 | C2–C7 | GM pad patch span (plays the whole keyboard; idiomatic band) |
| Low | 36–55 | C2–G3 | sub/mid-bass root zone — drone bottom, deep swells (mud below C2) |
| Mid | 56–79 | G3–G5 | primary chord-pad body — the workhorse band for 3–5 note chords |
| High | 80–96 | G5–C7 | shimmer top — new-age sparkle, upper octave doubling |

Empirical FluidR3 pitch sweep (RMS, notes 36–108 step 12): preset 88
audible EVERYWHERE — 36–96 strong (RMS 603–865), 108 audible but soft (RMS
392). GM pad patches are full-keyboard: **no patch ceiling** (contrast:
timpani/pizzicato die at 102+). Range 36–96 is the idiomatic *writing* band
(mud below C2, noise-shimmer above C7), NOT a physical limit. The pad has
no acoustic range limit (it is a synth).

## Articulations

| Technique | Velocity | Duration | Timbre |
|---|---|---|---|
| Sustain | 65–80 | full | slow-swelling pad — the default gesture |
| Legato | 60–75 | full | seamless voice crossfade — chord changes |
| Swell | 78–90 | full | crescendo swell — whole-bar build (Enya/Vangelis move) |
| Staccato | 60–70 | 1/4 | short pad "blip" — rhythmic filter-pulse motif |
| Marcato | 82–90 | 0.85× | attack override — plucked/bell onset (D-50 style) |
| Drone | 55–70 | full | static sustained harmony — ambient bed |
| Accent | 85–92 | 0.9× | hard entrance — downbeat hit, then bloom |

## Timbre DNA

- **Harmonic content**: dense detuned stack (the synth "ensemble" — 3–5
  slightly-detuned voices per note), strong fundamental, warm body 200–600 Hz,
  deliberate shimmer 5–10 kHz. The "new age" patch leans brighter/glassier
  than "warm" (GM89, Pad 2): more upper-partial weight, bell-like edge
- **Attack**: 0.4–1.0 s swell — the SLOW onset IS the identity; a pad that
  starts instantly is a stab, not a pad. Velocity mostly affects the final
  swell level, not the onset bite (LA-synth feature)
- **Decay/sustain**: indefinite while held (synthesizer — no physical decay);
  release = filter/amp fade 0.4–0.6 s into the reverb
- **Vibrato**: ensemble detune (±0.6–1.5%) + chorus, not solo vibrato —
  the "chorus width" is the pad's motion
- **Character**: lush, wide, glassy, spacious; the default
  ambient/cinematic/electronic pad voice; "new age" = Kitaro/Enya territory

## Role in Arrangement

- **Pad** (primary — orchestration.md's "Synth Pad" for the Pad role:
  "Strings (sustained), Synth Pad, Organ" — the last pad-role voice with NO
  KB entry after string_ensemble landed 2026-10-11)
- Harmony — sustained chords under a lead; the electronic comping voice
- Texture — atmospheric bed, risers, whole-bar swells
- Drone — static foundation (ambient/minimal) with the low zone (36–55)
- Accent — marcato entrances, downbeat hits that bloom
- NOT a rhythm/percussive voice, NOT a lead line — it is the harmonic
  canvas; melody moves need faster patches (this is why FM_DEFAULTS exists
  for stabs, but the KB default is the sustained pad)

## Synthesis Engines (musicom)

1. **Additive** (`sound/synthesis/additive.py`, SoundWave) — **primary**.
   The pad IS a detuned harmonic stack — same engine as the organ and
   string-ensemble pads, but wider: `ADDITIVE_HARMONICS.pad_warm`
   [1.0, 0.8, 0.6, 0.45, 0.3, 0.2, 0.12] / `pad_newage`
   [1.0, 0.65, 0.5, 0.35, 0.22, 0.15, 0.1, 0.06] (relative weights —
   normalize to sum 1.0 before `apply_overtones`), attack 0.55 s, detune
   ±0.012 (2× the string section ±0.006 — the synth chorus), stack 4
   voices/note, release 0.5 s, sustain 0.9. Verified post-2026-10-11
   additive-tail fix: the envelope holds the sustain, no mid-note collapse.
   **Engine quirk (found 2026-10-12)**: `apply_overtones` leaves
   `self.frequency` at the TOP partial (~7× fundamental), so
   `get_adsr_weights`' grid interval ≈ 1/(duration×top_partial) s and the
   decay rates are PER-GRID-STEP — use decay_S ≈ 1e-4 (not 1e-3) to hold a
   2 s chord (verified late-sustain envelope 0.79 with 1e-4).
2. **PhaseModSynth** (`sound/synthesis/phase_mod.py`) — classic analog-pad
   alternative: saw carrier, sine modulator ratio 1.0, depth 2.0, attack
   0.6 s, release 0.5 s, sustain 0.85 (FM_DEFAULTS). Subtle PM warms the
   saw stack — the "analog string machine" cousin of the D-50 digital pad.
3. **polysynth** (`sound/synthesis/polysynth.py`) — polyBLEP subtractive
   alternative for brighter/edgier pads (open filter).

## Production

- **Reverb**: hall/ambient 3.0–3.5 s — the LONGEST tail in the KB
  (string ensemble 2.6, harp 2.2). The synth pad is the quintessential
  bloom-in-space voice; REVERB_TAIL 3.2 s
- **EQ**: cut ~300 Hz (synth chords pile up 250–400 Hz fast); boost
  ~3.8 kHz presence; highshelf +9.5 kHz — the new-age AIR is the identity
  (contrast: string ensemble *cuts* 8.5 kHz — the pad wants sparkle)
- **Pan**: center for the composed stem; ±0.4 L/R spread on wide stereo
  swells (double the string-ensemble ±0.3 — pads can go wider)
- **Layering**: idiomatic doubling is OCTAVES (pad + pad 8vb, or pad under
  a real string/choir pad) — never unison with another melodic patch on
  the same pitches (comb-filtering — the 2026-09-01 lesson). Two pads
  with complementary zones (55–79 + 80–96) is the classic new-age stack

## Verification

- GM88 → stem `trackXX_Pad_1_new_age.wav` (GM_PROGRAMS[88] = "Pad 1 (new
  age)", sanitized; FluidR3 preset 88 = "Fantasia" — cosmetic SF2 name
  difference) — **no routing quirk**
- Enum `MidiInstrument.SYNTH_PAD = 88` matches the registry program (the
  rare exact match — noted so nobody "fixes" it later)
- `by_name('synth pad')` → Synth Pad, `by_program(88)` → Synth Pad,
  `in_sweet_spot(72)` = True, `in_sweet_spot(24)` = False
- Empirical pitch sweep: preset 88 audible throughout 36–96, no gaps
- Buzz check: solo chord render passes the 4–8 kHz spectral gate
  (single voice + single patch, no comb-filtering)
- Zero-drift: sustained chord ends flush at BAR (terminal landmark)
- Engine smoke: additive envelope sustains (post-fix); PhaseModSynth
  saw pad slow-attacks (onset RMS ≪ sustain RMS)

## Stem label / quirks

- GM_PROGRAMS[88] = "Pad 1 (new age)" → sanitized stem `Pad_1_new_age`
  (parens stripped, spaces → underscores) — matches STEM_LABEL, **no
  routing quirk**
- FluidR3 preset 88 = "Fantasia" (SF2 internal name ≠ GM label — cosmetic;
  the pipeline labels stems from GM_PROGRAMS, so stems say Pad_1_new_age)
- Enum `SYNTH_PAD = 88` is CORRECT for once — do not "correct" it to 87
  or 89 (composition jobs in Styles/ send 88 for Pad voices; the registry
  entry now documents the exact patch those jobs render)
- The GM "new age" (88) vs "warm" (89) distinction: 89 = darker mid-heavy
  pad (a future Synth-family candidate); 88 = the glassy shimmer pad
- Channel quirk: melodic channel (0–9) — channel 9 triggers the drum map
- FluidR3 pad presets are full-keyboard patches (no per-note ceiling like
  timpani/pizzicato) — never clips, but keep chords ≥2 s so the slow
  attack actually speaks