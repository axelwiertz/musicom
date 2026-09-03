---
type: instrument
family: World
name: Koto
midi_program: 107
gms: "Koto"
range_min: 51
range_max: 90
solo_range: [57, 84]
role: [lead, melody, ornament, drone, harmony]
synthesis: [karplus, modal, phase_mod]
---

# Koto

## MIDI / GM

- **Program**: 107 (GM1 Koto — GM program numbers are 0-based; 107 is the
  108th entry, "Koto")
- **Channel**: melodic channel; 13-string plucked zither, long ringing decay
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 107 = "Koto"
  (TimGM6mb fallback also has preset 107 = "Koto"). RenderPipeline stem
  label: GM_PROGRAMS[107] = "Koto" → `trackXX_Koto.wav` — matches exactly,
  **no quirk**. (Confirmed from GM_PROGRAMS list source + SF2 phdr chunk.)
- GM neighbors: 104 Sitar, 105 Banjo, 106 Shamisen, 108 Kalimba — all in the
  same "World plucked" block of GM1.

## Range

13-string koto, strings numbered 1 (low) to 13 (high), sounding pitch.

| Zone | MIDI | Pitches | Strings | Register |
|---|---|---|---|---|
| Full range | 51–90 | D#3–F#6 | 1–13 | standard koto |
| Low (bass) | 51–60 | D#3–C4 | 13–9 | warm, dark, long ring |
| Middle (melody) | 61–76 | C#4–E5 | 8–4 | primary melodic register |
| High | 77–90 | F5–F#6 | 3–1 | bright, thin, cutting |

Practical melodic ceiling ~D6 (86) on most instruments; 86–90 zone is
tension-pitch + high ornament only. Oshi (left-hand press) bends any note up
~2–3 semitones. Base tuning hirajoshi (D G A D F on strings 1–5); the koto
is NOT chromatic — write hirajoshi/in-scale pentatonic lines, not dense
chromatic harmony.

## Articulations

| Technique | Velocity | Duration | Timbre |
|---|---|---|---|
| Pluck (tsume) | 70–90 | full decay | ivory-pick stroke, round attack + sawari shimmer |
| Oshi (press bend) | 65–85 | 1.5–1.7× | pitch bend up 2–3 semitones, vocal quality |
| Hajiki (flick) | 80–95 | 1/3 | fast snap ornament, bright |
| Kakute (strum/arpeggio) | 60–75 | 1/4 | rolled across strings, harp-like |
| Mute (damp) | 40–55 | 1/8 | palm-choked, dry percussive |

## Timbre DNA

- **Harmonic content**: harmonic partial stack with a *sawari* partial — a
  slightly detuned overtone (from the string resting on the movable bridge)
  that beats against the fundamental for the koto's characteristic buzz-tinge
- **Attack**: 3–10 ms (tsume strike) — fast, round onset (rounder than
  sitar's mizrab, less percussive than guitar)
- **Decay**: long — 2.5–3.5 s ring on low/mid strings; faster on high
- **Release**: natural string decay; no damper pedal; palm dampens
- **Vibrato**: oshi-based pitch vibrato (left-hand press), not amplitude
- **Character**: clear, resonant, gently buzzing "plucked zither" — the
  in-between of harp (soft) and sitar (metallic)

## Role in Arrangement

- Lead melody (mid register) — hirajoshi pentatonic lines
- Ornamentation (hajiki snaps, oshi bends)
- Drone layer (open low strings + ostinato patterns)
- Sparse countermelody / call-response with flute or shakuhachi
- Harmony in *small* clusters only (kakute strums, 2–3 strings) — idiomatic
  koto chords are stacked 4ths/2nds, not tertian
- NOT a dense harmony/pad instrument

## Synthesis Engines (musicom)

1. **Karplus-Strong** (`sound/synthesis/karplus_strong.py`, SP-011) —
   **primary**. Plucked waveguide = the correct physical model. `loop_gain`
   ~0.9970 (low damping) = long ring with a touch of brightness — between a
   guitar (0.996) and sitar (0.9975); `width` ~0.45 for spread.
2. **ModalSynth** (`sound/synthesis/modal.py`) preset `'string'` — harmonic
   stack with moderate decay; the "clean koto" fallback (no sawari partial).
3. **PhaseModSynth** — cheap koto: saw carrier, mod ratio 3.0, depth 2.5,
   attack 0.002, release 0.3. Twangy, less authentic.

## Production

- **Reverb**: room 1.0–1.5 s — koto ring is inherently dry; a short room
  keeps pluck transients clear, hall 1.8–2.0 s max for solo ballad space
- **EQ**: cut ~300 Hz paulownia-body boxiness; boost ~3.2 kHz for tsume
  click + sawari shimmer; gentle 8.5 kHz shelf for air (avoid hype — silk
  strings are warm, not glassy)
- **Delay**: not idiomatic; if used, subtle 1/4 or dotted-8th at low mix
- **Pan**: center solo; 0.2–0.35 spread in ensemble writing

## Verification

- GM107 → stem `trackXX_Koto.wav` (label matches, no quirk)
- FluidR3 preset 107 = "Koto" (verified from phdr chunk)
- Solo render passes 4–8 kHz spectral gate (round pluck, no comb buzz)
- Zero-drift: plucked units end flush at BAR (terminal landmark)

## Instrument.md companion

`koto.py` — importable constants. Registered in `instrument_registry.py`
(2026-09-02) as `World.koto.koto` → key `koto`, constant `KOTO`.
