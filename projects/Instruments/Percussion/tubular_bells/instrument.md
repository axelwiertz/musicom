---
type: instrument
family: Percussion
name: Tubular Bells
midi_program: 14
gms: "Tubular Bells"
range_min: 60
range_max: 78
solo_range: [60, 78]
role: [accent, color, drone, lead, ornament]
synthesis: [modal, karplus, phase_mod]
---

# Tubular Bells (Orchestral Chimes)

Struck brass tubes suspended in a rectangular frame, played with rawhide or
synthetic mallets. The orchestral tintinnabuli voice — church bells without
a bell tower. The iconic sonority of Tchaikovsky's 1812 Overture, Berlioz's
Symphonie Fantastique "Witches' Sabbath" chime, Mahler's "Resurrection"
Symphony, and the Mike Oldfield theme that gives the instrument its name.

## MIDI / GM

- **Program**: 14 (GM1 Tubular Bells — 0-based GM 14; sometimes listed as
  GM #15 in 1-indexed tables)
- **Channel**: melodic channel (0–9). NOT channel 9 — channel 9 triggers
  the drum-kit map and the `Acoustic_Grand_Piano` program-0 fallback stem
  label (timpani lesson). The GM drum-kit has no tubular bells map.
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 14 =
  "Tubular Bells" (verified from the phdr chunk). RenderPipeline stem
  label: GM_PROGRAMS[14] = "Tubular Bells" → `trackXX_Tubular_Bells.wav`
  — matches exactly, **no quirk**.
- GM neighbours: 10 Music Box, 11 Vibraphone, 12 Marimba, 13 Xylophone,
  15 Dulcimer — the pitched-mallet/metallophone block. Tubular bells are
  the only BRASS-TUBE struck voice here, distinct from the arch-tuned
  aluminium/aluminum bars and rosewood bars.

## Range

Standard 1.5-octave orchestral chimes set (C4–F5, 18 brass tubes). Some
manufacturers extend to C4–G5 (19 tubes). The range is deliberately limited
— tubular bells are a **colour instrument**, not a melodic voice.

| Zone | MIDI | Pitches | Character |
|---|---|---|---|
| Full range | 60–78 | C4–F5 | standard 1.5-octave orchestral chimes |
| Low | 60–66 | C4–C#5 | deep, full church-bell bloom (the Tchaikovsky C4) |
| Middle (sweet) | 67–72 | D5–C5 | balanced chime tone, sweet spot |
| High | 73–78 | C#5–F5 | thinner, brighter, shorter ring; punctuation accents |

The practical ceiling is ~F5 (78). Above that, the tubes get too short to
produce the characteristic "bell" timbre and sound more like a glockenspiel
bar. The fundamental octave C4–C5 (60–72) is the idiomatic register.

## Articulations

| Technique | Velocity | Duration | Character |
|---|---|---|---|
| Stroke | 75–90 | full | standard rawhide mallet — round, warm, full ring |
| Hard | 90–105 | 0.8× | brighter hammer blow, more upper partials |
| Soft | 55–70 | full | light tap, muted bell colour |
| Roll | 65–80 | 0.06× | rapid alternation between two tubes |
| Muted (hand-damped) | 60–78 | 0.2× | choked short — rhythmic accent only |
| Accent (sforzando) | 92–108 | 0.9× | marcato marcato stroke for drama |

## Timbre DNA

- **Harmonic content**: INHARMONIC partial stack — the free-free brass tube's
  bending-mode ratios approximate **1 : 2.76 : 5.40 : 8.93**, similar to a
  solid metal bar (glockenspiel) but shifted upward because brass's lower
  Young's modulus and the hollow-tube section raise the overtone ratios. The
  result is a warm, fundamental-rich "church bell" sound that is neither as
  crystalline as the glockenspiel (steel bars) nor as mellow as the vibraphone
  (arch-tuned aluminium with resonator tubes).
- **Attack**: ~2–5 ms — rawhide or nylon hammer on brass. Soft enough to avoid
  a harsh click (unlike the polyball-on-rosewood of the xylophone).
- **Decay**: long — ~1.5–3 seconds for the fundamental, depending on tube
  size and suspension (the longest ring in the mallet/metal tube family,
  comparable to vibraphone pedal-down sustain).
- **Release**: natural tube ring; the player damps by hand for shorter notes.
  No damper pedal (unlike vibraphone's piano-style sustain pedal).
- **Vibrato**: none natural; a bow vibrato is possible (bowed chime is rare).
- **Character**: dark, round, warm, bell-like — intentionally reminiscent of
  a small church bell or cow bell without the clang.

## Role in Arrangement

- **Accent / Color**: the idiomatic role — dramatic punctuation (the "Dies
  Irae" chime, the coronation bell, the 1812 cannon substitute). Single
  strokes on C4, G4, C5 are the classic orchestral deployment.
- **Drone / Pedal**: sustained C4/G4 chime as a tone-dropping "bell" effect
  (the "time is passing" colour in Mahler).
- **Lead / Melody**: only within the narrow 1.5-octave range and in sparse,
  resonant textures; dense passagework becomes mud.
- **Ornamentation**: the roll (two mallet alternation) for dramatic crescendo;
  the glissando slide (possible but rare).
- **NOT** a melodic keyboard percussion (no chromatic runs, no chord comping,
  no bass voice). NOT a harmony voice — too resonant and limited in range;
  double-stops only at tonal intervals (octave, fifth) for bell resonance.
- **NOT** a general-purpose mallet — use for specific bell/church effects.

## Synthesis Engines (musicom)

1. **ModalSynth** (`sound/synthesis/modal.py`) — **primary**, impulse-excited
   resonator bank with custom `TUBULAR_BELLS_MODES` at the struck-tube ratios
   **1 : 2.76 : 5.40 : 8.93** and decay rates 0.50–2.00 (slow — the tube
   rings for seconds). The fundamental dominates (1.00 amp) with the 2.76×
   overtone as the richest partial (0.55). The stock `'bell'` preset is the
   closest bank but models a generic metallic bar, not a brass tube.

2. **Karplus-Strong** (`sound/synthesis/karplus_strong.py`, SP-011) —
   demoted fallback. The tube is struck, not plucked, so a KS waveguide is
   the wrong excitation family; loop_gain 0.9970 gives the long metallic
   ring (~1.5–2.5 s, comparable to glockenspiel 0.9980).

3. **PhaseModSynth** — FM bell: sine carrier, mod ratio 2.76 (the dominant
   bell overtone), depth 1.8, attack 0.001, release 2.0. Decent chime
   substitute.

## Production

- **Reverb**: hall/church 2.0–2.8 s — tubular bells IDIOMATICALLY need a
  large acoustic space to bloom. The reverb IS part of the instrument's
  sound (no chime sounds "dry"). REVERB_TAIL = 2.5 s is the default.
- **EQ**: cut ~300 Hz to tame any tube-frame box resonance; boost ~2.5 kHz
  for hammer attack + bell overtone definition; 7 kHz shelf for brass
  shimmer.
- **Pan**: center solo; chimes sit center-rear in the orchestral percussion
  layout, behind the mallet instruments (marimba, vibraphone).
- **Layering**: octave doubling (C4 + C5) for the full bell chime. Avoid
  unison same-pitch doubling (comb-filtering buzz — the 2026-09-01 lesson).
  A tubular bell can layer with a timpani roll for dramatic orchestral
  punctuation.

## Verification

- GM14 → stem `trackXX_Tubular_Bells.wav` (label matches, no quirk)
- FluidR3 preset 14 = "Tubular Bells" (verified from phdr chunk)
- Solo render passes 4–8 kHz spectral gate (warm bell tone, no comb buzz)
- Zero-drift: struck units end flush at BAR (terminal landmark)
- Empirical FluidR3 pitch sweep (RMS, notes 60–78): preset 14 audible across
  the full span, no gaps — SF2 never clips a composition

## Instrument.md companion

`tubular_bells.py` — importable constants. Registered in
`instrument_registry.py` (2026-09-26) as
`Percussion.tubular_bells.tubular_bells` → key `tubular_bells`, constant
`TUBULAR_BELLS`.