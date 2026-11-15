---
type: instrument
family: Percussion
name: Woodblock
midi_program: 115
gms: "Woodblock"
range_min: 60
range_max: 96
solo_range: [65, 84]
role: [rhythm, accent, ornament, color]
synthesis: [modal, phase_mod]
---

# Woodblock

## MIDI / GM

- **Program**: 115 (GM1 "Woodblock"; GM numbers are 0-based, so 115 is the
  116th entry)
- **Channel**: melodic channel (0–9), **NOT channel 9**. Channel 9 triggers the
  drum-kit map and the `Acoustic_Grand_Piano` program-0 fallback stem label
  (timpani/taiko/drum-kit lesson). The ch9 GM map does have its own woodblocks
  (note 76 Hi / 77 Low) — see the quirk section for when to use those instead.
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 115 =
  **"Woodblock"** (verified from the phdr chunk, bank 0). RenderPipeline stem
  label: `GM_PROGRAMS[115] = "Woodblock"` → `trackXX_Woodblock.wav` — matches
  exactly, **no quirk**.
- GM neighbours: 112 Tinkle Bell, 113 Agogo, 114 Steel Drums, **115 Woodblock**,
  116 Taiko Drum. Woodblock is the dry WOODEN tick of the set — the pitched
  metal bell (113 Agogo) and the membrane drum (116 Taiko) are its opposites.
- Distinct from: **claves** (GM ch9 note 75 — a solid hardwood rod, much higher
  pitched, ~1080 Hz measured), **muyu / temple block** (round fish-mouth block,
  no GM program), **cowbell** (GM ch9 note 56 — metal, long ring).

## Range

A woodblock has **no melodic range** — it is a tuned-but-fixed-pitch block. The
KB stores MIDI note numbers because that is what the sequencer writes; on the
FluidR3 GM115 patch note number is *nearly inert* (see the pitch-tracking quirk
below). The numbers below are the window in which the patch sounds like a
woodblock, not a playable scale.

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 60–96 | C4–C7 | patch-playable window (audible from C3 up, but pointless below C4) |
| Low / "low block" | 60–70 | C4–A#4 | darkest resampling — the big 8–9" low block colour |
| Mid (core, home) | 71–79 | B4–G5 | the patch's **natural, unresampled** centre: measured 410–440 Hz, i.e. where the sample actually lives |
| High / "high block" | 80–96 | G#5–C7 | thinner, more resampled tick — the high-block *illusion* (see quirk) |

Practical writing window is **C5–C6 (72–84)**; the home note for a repeated
ostinato is **72 (C5, ≈430 Hz measured)**. Real instrument: a hardwood
(usually maple) rectangular block 5"–9" long, hollowed through a narrow slit;
a matched set puts the low block ~400–500 Hz and the high block ~800–1200 Hz
(a fourth to an octave apart, not a scale).

## Articulations

| Technique | Velocity | Duration | Timbre |
|---|---|---|---|
| Open stroke (standard) | 88–98 | 0.25× | hard stick on the solid cheek — the dry "tock" |
| Accent | 100–112 | 0.30× | hard downbeat, maximum crack |
| Muted / damped | 62–75 | 0.12× | free hand or fingers clamp the block — dead click, no body |
| Rim / edge stroke | 80–92 | 0.10× | stick on the edge over the slit — sharpest, thinnest sound |
| Stick click | 55–65 | 0.08× | shoulder of the stick laid flat and pressed — soft "clop" |
| Double stroke | 84–95 | 0.18× | two bounces — the classic "tock-a" pair |
| Ghost | 28–45 | 0.10× | barely-there 16th, keeps the subdivision audible |
| Roll (single-stroke) | 52–68 | 0.06× | fast re-strikes at 32nd-note density — **no true sustain**, it is a repeated attack |

All durations are short by physics: the block's own decay is ~60–90 ms, so a
note-off later than ~1/16 has no audible effect. Articulation is carried by
**velocity and stroke placement**, never by length.

## Timbre DNA

- **Harmonic content**: an inharmonic wooden crack. Measured FluidR3 partials
  at note 72 relative to the fundamental (433 Hz): **1.0** (block body),
  **1.96×** (0.44 — the octave-ish "tock"), **2.18×** (0.53 — the inharmonic
  wooden clack that defines WOOD), **5.5×** (0.14 — the hard-stick tick).
  The 2.18× partial is what separates it from a marimba bar (harmonic 2:1).
- **Attack**: ~0.5–2 ms. The transient is most of the sound; there is no
  measured rise, only a drop.
- **Decay**: —90% of peak within **50 ms**; a faint tail (≈ −40 dB) runs to
  ~1.5 s, which is patch room-tone, not block resonance.
- **Release**: none — no damper. The sound is over before the finger lifts.
- **Vibrato**: none. No pitch bend idiom; a bent woodblock is a mistake.
- **Spectral centroid** (note 72, first 120 ms): **≈4.7 kHz** — brighter than
  marimba (3.0 kHz) and xylophone (3.4 kHz), darker than agogo (7.4 kHz).
  It lives in the same tick band as claves and side stick.
- **Character**: dry, hard, hollow, articulate, unmistakably *wooden*. Pure
  punctuation: it says "here", never "this note".

## Role in Arrangement

- Rhythm — the grid-keeper: an unbroken 8th/16th ostinato that makes the pulse
  explicit without adding weight (the orchestral "clock", the film cue tick).
- Accent — single strokes that mark section starts, hits and stops.
- Ornament — double strokes, rim ticks and 3–5 stroke pickups feeding a
  downbeat.
- Color — the "wooden" cue: horse hooves, machine rhythm, toy-box, tension
  (Shostakovich-style motor figures).
- Pairs with: **any** low percussion for a hi/lo split (taiko, timpani, drum
  kit kick), claves for a Latin layer, pizzicato strings or marimba for a
  wooden family, and any melodic lead as a punctuation colour.
- NOT a melodic voice: the GM115 patch does not transpose (see quirk) — do not
  write melodies or bass lines on it.
- NOT a harmony/chord voice: one block, one stroke, monophonic.
- NOT a sustain/pad voice and NOT a substitute for a snare backbeat (no noise
  burst, no snare wires).

## Synthesis Engines (musicom)

1. **ModalSynth** (`sound/synthesis/modal.py`) — **primary**. A hollow hardwood
   block is a damped-sinusoid bank with a very short ring. Custom
   `WOODBLOCK_MODES` uses the *measured* FluidR3 ratios (1 : 1.96 : 2.18 :
   3.44 : 5.5) with decay rates 70–230, i.e. ~70 ms to −60 dB — an order of
   magnitude faster than the marimba bank (8–20) and faster than claves would
   be. The stock `'drum'` preset is the wrong shape (membrane-like low modes,
   no 2.18× wooden partial) and `'marimba'` rings far too long.
2. **PhaseModSynth** (`sound/synthesis/phase_mod.py`) — cheap alternative:
   sine carrier, **non-integer** mod ratio 3.4 (inharmonic = wood, integer =
   pitched bar), depth 1.8, attack 0.5 ms, release 60 ms.
3. **DrumMachine** (`sound/effects/tape_delay.py` path, via `SYNTHESIS_DEFAULTS`)
   — only when the block is part of a ch9 kit pattern, not for a melodic-track
   woodblock part.
4. **Karplus-Strong — EXPLICITLY REJECTED**: there is no string and no
   resonator tube. A KS loop's harmonic series is the wrong structure (the
   timpani / taiko / agogo precedent).

## Production

- **Reverb**: **0.75 s** — the driest entry in the KB. A woodblock is close-mic'd
  in orchestral and studio use; anything longer blurs the tick into a wood
  "clop" and destroys its function as a marker.
- **EQ**: cut ~600 Hz (−2 dB) — the hollow-slit boxiness; boost ~3.6 kHz
  (+2.5 dB) for the stick crack; shelf +1.5 dB at 10 kHz for the dry top.
  Do not low-pass: the tick band is the instrument.
- **Pan**: +0.15 (slightly right) for a solo/mix placement; centre when the
  block is the only percussion.
- **Layering**: never double the same MIDI pitches with a second patch
  (comb-filter buzz — the 2026-09-01 lesson). Layer by *role* instead (kick
  under the accents, claves in the gaps, marimba on the pitches).
- **Level**: the melodic GM115 patch peaks ≈0.34 at vel 100, while the ch9
  woodblocks peak ≈0.55 — if you switch a part from ch9 to GM115 it drops
  ~4.5 dB, so re-balance rather than raising velocity past 110.

## Idiom / writing quirks

- **Quirk (measured, important): FluidR3 GM115 barely pitch-tracks.** Sweeping
  notes 50→98 moves the spectral peak only **330 Hz → 580 Hz** (a 1.76× span
  where full transposition would be 16×). Note number is a *timbre* control,
  not a pitch control: the patch always sounds like the same woodblock. The
  sample's natural pitch sits at **note ≈68 (G#4, 410 Hz measured)** — write
  the ostinato there or at 72 and treat everything else as colour.
- **Consequence**: high-vs-low block contrast cannot be had from GM115. For a
  real hi/lo pair use the **ch9 GM percussion woodblocks**, note 76 (Hi) and
  77 (Low) — measured 380 Hz / 280 Hz in FluidR3 (a fifth apart; the "Hi"
  block is low-ish in this SF2), peak ≈0.55, stem label falls back to the
  drum-kit `Acoustic_Grand_Piano` name.
- **Write rhythm, not melody**: 1–2 bar cells that repeat. Velocity accents
  carry the pattern; timing should be tight (Percussion humanize DNA: 2.5 ms
  sigma, 0 layback, 0.01 duration sigma — the block must sit on the grid).
- **No rolls in the sustained sense**: a woodblock roll is 32nd-note re-strikes.
  Writing whole/half notes implies a ring that does not exist.
- **Leave space**: the tick is a high-frequency transient; back-to-back 16ths
  at high velocity turn into a hiss layer. Alternate full and ghost strokes.
- **Flam pairs beat single hits**: the double stroke ("tock-a") is the idiom's
  signature; a bare downbeat reads as a metronome.

## Verification

- GM115 → stem `trackXX_Woodblock.wav` (label matches, no quirk)
- FluidR3 preset 115 = **"Woodblock"** (verified from the phdr chunk, bank 0)
- Pitch-tracking quirk quantified: notes 50–98 → 330–580 Hz peak (measured)
- Decay quantified: −90% within 50 ms, faint tail to ~1.5 s (measured)
- Velocity response: near-linear, peak 0.014 (vel 20) → 0.490 (vel 120)
- Solo render passes the 4–8 kHz spectral gate (no comb buzz, no doubling)
- Zero-drift: unit ends flush at BAR (terminal landmark), `validate()` True
- Empirical FluidR3 pitch sweep (RMS, notes 48–96): preset 115 audible
  13/13 probes, no gaps, level flat within 24% — the SF2 never clips a part

## Instrument.md companion

`woodblock.py` — importable constants. Registered in `instrument_registry.py`
(nightly, 2026-09-02 slot) as `Percussion.woodblock.woodblock` → key
`woodblock`, constant `WOODBLOCK`.
