---
type: instrument
family: World
name: Taiko
midi_program: 116
gms: "Taiko Drum"
range_min: 36
range_max: 67
solo_range: [40, 55]
role: [accent, rhythm, drone, ornament]
synthesis: [modal, drum606, phase_mod]
---

# Taiko (Wadaiko)

## MIDI / GM

- **Program**: 116 (GM1 Taiko Drum — GM program numbers are 0-based; 116 is
  the 117th entry, "Taiko Drum")
- **Channel**: melodic channel (0–9); the GM116 taiko patch is a TUNED drum
  (pitch follows the played note). NOT channel 9 — channel 9 triggers the
  drum-kit map and the `Acoustic_Grand_Piano` program-0 fallback stem label
  (timpani lesson).
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 116 =
  "Taiko Drum" (verified from the phdr chunk). RenderPipeline stem label:
  GM_PROGRAMS[116] = "Taiko Drum" → `trackXX_Taiko_Drum.wav` — matches
  exactly, **no quirk**.
- GM neighbors: 112 Tinkle Bell, 113 Agogo, 114 Steel Drums, 115 Woodblock,
  117 Melodic Tom, 118 Synth Drum — the low-fidelity percussion block.
  Taiko is the deep festival voice; 117 Melodic Tom is its higher,
  melodic-fill cousin.

## Range

Sounding pitch. The GM taiko is a tuned drum like the timpano (no pedal, but
each head is rope-tension-tuned); pitch follows the played note. Real
instrument anchors: the ō-daiko's fundamental sits ~60–80 Hz (B1–E2),
chū-daiko ~A2–A3, shime/koda drums roughly an octave above the chū.

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 36–67 | C2–G4 | melodic taiko patch span |
| Low | 36–45 | C2–A2 | ō-daiko chest booms, kumi-daiko floor |
| Middle (festival) | 46–57 | A#2–A3 | chū-daiko: DON/DOKO, clearest pitch + body |
| High | 58–67 | A#3–G4 | shime/koda accents, slaps, rim cracks |

Practical composition core is E2–G3 (40–55) — the big festival drums. Below
C2 the SF2 patch thins out; above G4 you are writing shime-daiko territory,
which in real ensembles is a separate smaller instrument.

## Articulations

Kuchi-shoga rhythm syllables map directly onto strokes: **DON** = full fat
head-center stroke (let it ring), **DOKO** = lighter off-beat filler, **KA**
= rim crack (wood only), **SU** = rest.

| Technique | Velocity | Duration | Timbre |
|---|---|---|---|
| DON (full stroke) | 90–99 | 0.8× | fat head-center punch, the festival 1 |
| DOKO (light stroke) | 65–80 | 0.4× | off-beat gallop filler |
| KA (rim crack) | 80–95 | 0.15× | wood click on the shell edge, no tone |
| Slap | 85–95 | 0.25× | quick sharp head crack, bright accent |
| Roll (shime) | 60–75 | 0.06× | two-stick tremolo — the only sustain illusion |
| Muffled | 50–65 | 0.12× | hand-damped dead thud |
| Accent | 99 | 0.9× | hard marcato downbeat |
| Soft | 45–55 | 0.7× | quiet ensemble support |

## Timbre DNA

- **Harmonic content**: INHARMONIC membrane modal family (circular-head
  Bessel ratios ~1 : 1.6 : 2.1 : 2.65 — the timpani family) SITTING ON TOP OF
  a low hollowed-keyaki shell resonance ~60–110 Hz. The shell thump is the
  taiko's signature; the head's tuned (0,1) mode is what follows the note.
- **Attack**: ~2–5 ms — thick cedar bachi on tacked raw hide; heavier than a
  snare stick, slower than a hammer
- **Decay**: short ring, ~0.5–0.8 s (timpani ring is 1–3 s; the tacked head
  and dense hide kill energy fast)
- **Release**: no damper — the player lets each DON ring or muffles with the
  hand for the next stroke
- **Vibrato**: none
- **Character**: huge, chest-felt, ceremonial; a vertical ACCENT instrument
  (the whole point of kumi-daiko is the ensemble landing together on the 1),
  not a melodic voice

## Role in Arrangement

- Accent — downbeat DON hits, kabuki/noh punctuation (the Atare hits)
- Rhythm — kuchi-shoga patterns (DON don DOKO DON) as the groove spine of a
  World/Japanese-style track; galloping DOKO runs as energy building
- Drone — repeated low chū strokes anchor the tanpura-like bed under koto /
  shakuhachi-style lines (pairs naturally with the KB's koto, shamisen,
  shenai)
- Ornament — rim cracks and shime rolls as transitions/fills
- NOT a melodic lead: the patch is tuned, but taiko idiom is rhythm + accent
- NOT a bass melodic voice — it is a drum; use a real bass instrument under it

## Synthesis Engines (musicom)

1. **ModalSynth** (`sound/synthesis/modal.py`) — **primary**, impulse-excited
   resonator bank with a custom `TAIKO_MODES` bank: tuned (0,1) head mode
   (110 Hz at the A2 reference) coupled to inharmonic membrane partners and
   the low shell mode (~90 Hz, the chest thump), decay rates 2.6–6.0 —
   shorter than timpani's 0.9–3.0 rates? No: LONGER numbers = faster decay
   (ModalSynth decay is a rate). Taiko rates sit between timpani (0.9–3.0)
   and marimba (8–20). The stock `'drum'` preset is the closest bank but
   decays too fast and has no shell body.
2. **DrumSynth606** (`sound/synthesis/drum_synth_606.py`) — the strike thump:
   `DRUM606_DEFAULTS` with freq 80 (below the 606 tom's 110), decay 1.4
   (3× the 606 tom's 0.3), pitch_sweep 1.45 (hard head-tension drop).
3. **PhaseModSynth** — cheap taiko: sine carrier, mod ratio 1.59 (the (1,1)
   membrane partner), depth 1.0, attack 0.001, release 0.8. Boxy, less
   authentic.
4. **Karplus-Strong — EXPLICITLY REJECTED**: there is no string; a KS loop's
   harmonic series is the wrong partial structure (the timpani precedent).

## Production

- **Reverb**: 1.4–1.8 s — festival hall/air; long enough to give the DON
  space, short enough not to smear successive strokes. Between the xylophone
  (0.9, tight) and the timpani (2.2, hall).
- **EQ**: cut ~300 Hz box honk (keep the 60–110 Hz shell chest intact);
  boost ~1.8 kHz for the raw-hide head slap (lower than the mallet bars'
  ~2.5 kHz because the bachi-on-hide attack is duller/woodier); very small
  6 kHz air shelf — leather noise, not cymbal shimmer
- **Pan**: center solo; kumi-daiko ensembles spread −0.3..+0.3 with the
  ō-daiko slightly left (stage-left convention)
- **Layering**: pairs with koto/shamisen/shenai melody + a low drone; layer a
  Woodblock (GM115) rim crack on the same downbeats for the KA texture —
  NEVER a second pitched patch in unison on the taiko's pitches (comb
  buzz — the 2026-09-01 lesson)

## Verification

- GM116 → stem `trackXX_Taiko_Drum.wav` (label matches, no quirk)
- FluidR3 preset 116 = "Taiko Drum" (verified from phdr chunk)
- Solo render passes 4–8 kHz spectral gate (low chest thump, no comb buzz)
- Zero-drift: struck units end flush at BAR (terminal landmark)
- Empirical FluidR3 pitch sweep (RMS, notes across range): preset 116
  audible across the full span, no gaps — SF2 never clips a composition

## Instrument.md companion

`taiko.py` — importable constants. Registered in `instrument_registry.py`
(2026-09-16) as `World.taiko.taiko` → key `taiko`, constant `TAIKO`.
