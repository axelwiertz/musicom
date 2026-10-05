---
type: instrument
family: Woodwind
name: Soprano Saxophone
midi_program: 64
gms: "Soprano Sax"
range_min: 54
range_max: 89
solo_range: [62, 84]
role: [lead, countermelody, ornament, accent]
synthesis: [phase_mod, additive]
---

# Soprano Saxophone

## MIDI / GM

- **Program**: 64 (GM1 Soprano Sax). NOT in `structures/instrument.py`
  `MidiInstrument` enum (only 10 instruments exposed); use raw `program=64`
  in `add_voice`.
- **Channel**: any melodic channel (0-9); solo/lead instrument
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 64 = `Soprano Sax`
  over TimGM6mb.sf2 (`Sop Sax v2.3`). Soprano is the brightest, most piercing
  sax patch — the SF2 patch has a focused reedy tone with fast reed attack.
- **Stem label**: pipeline `GM_PROGRAMS[64] = "Soprano Sax"` → sanitized to
  `trackXX_Soprano_Sax.wav`. NOTE: the stem label is `Soprano_Sax`, NOT "Saxophone"
  and NOT "Alto Sax" — match on the ACTUAL label `Soprano_Sax` in any stem-aware
  code, not the family name.
- **Program family note**: GM 64=Soprano, 65=Alto, 66=Tenor, 67=Baritone. Soprano
  (64) is the smallest and highest saxophone — the classical and New Orleans brass-band
  lead voice. This entry covers 64.

## Range

| Zone | MIDI | Pitches | Register | Character |
|---|---|---|---|---|
| Full range | 54–89 | F#3–F6 | concert soprano sax (written Ab3–G6) | brightest, most piercing sax |
| Sweet spot | 67–79 | G4–G5 | the soprano's singing register — cuts through any ensemble, lead melody focus | |
| Low (closed) | 54–63 | F#3–D#4 | reedy, slightly thin, crisp articulation — less projection than alto's low end | |
| Mid (core) | 64–74 | E4–D5 | bright commanding core — soprano's money register (Bechet, Bigard, Crawford) | |
| High (sopranino) | 75–89 | D#5–F6 | piercing screaming top — altissimo intensity, brilliant solo/scream territory | |

Standard soprano sax has keywork down to written Ab3 (concert F#3=54). The low
Bb3 (concert G#3=56) is a common bell-note extension on many modern instruments.
Altissimo extends the upper range to approximately written G6 (concert F6=89) with
skilled players.

## Articulations

| Technique | MIDI velocity | Duration | Timbre |
|---|---|---|---|
| Legato | 75–90 | full note | smooth vocal, the sax default; soprano legato is lighter and faster-responding than alto |
| Tenuto | 65–80 | ~0.9 note | slight separation, expressive |
| Staccato | 62–75 | ~1/8 note | short, crisp, fast articulation (lightest reed in the sax family = fastest tongue) |
| Accent/marcato | 88–105 | full note, strong onset | sharp reed attack, punchy — soprano cuts hardest in the section |
| Slap tongue | 70–85 | < 0.1 note | percussive reed pop — extended technique, soprano is brighter/more percussive than alto |
| Growl / overblow | 70–85 | full note | reed growl, dirty altissimo — New Orleans brass band, R&B scream |
| Vibrato (narrow) | 70–85 | sustained | soprano vibrato is narrower and faster than alto/tenor; classical keeps it minimal (French tradition), jazz makes it wide |
| Fall / scoop | 60–75 | glissando (pitch bend) | lip/finger slide — lighter reed = easier bends than larger saxes |

## Timbre DNA

- **Harmonic content**: strong fundamental + bright even AND odd harmonics
  (conical bore, single reed — same family as alto/tenor/baritone). The soprano's
  smaller body and shorter tube favour upper harmonics more than the alto: the
  tone is brighter, reedier, with a characteristic "ring" in the 2-5 kHz band.
  Higher fundamental than any other sax (writes at concert pitch but transposes
  Bb — the SMALLEST air column in the standard family).
- **Attack**: 20–40 ms (lightest fastest reed onset in the sax family). Soprano
  reed is the thinnest and responds near-instantaneously — no breath lag.
- **Decay**: sustained (breath-driven, no natural decay while blowing; the SMALL
  bore means less air volume = slightly faster stop than alto on release)
- **Release**: 30–80 ms (fastest shut-off in the sax family)
- **Noise component**: breath hiss (continuous, low level) + reed buzz transient
  at attack; growl overblow is prominent due to the small bore favouring overblown
  partials.
- **Vibrato**: natural 5–7 Hz, MODERATE width (±0.2–0.4 semitone) — narrower than
  alto/tenor; classical soprano uses very little vibrato (French Conservatoire
  tradition), jazz uses wider for expression

## Role in Arrangement

- **Lead melody** (sweet spot G4–G5 — the soprano sax is the definitive lead voice
  in the sax section: New Orleans brass band frontline, classical sax quartet
  S in SATB, piercing funk/pop lines)
- **Countermelody** (soaring descant above vocal/trumpet/strings; the soprano's
  register sits above most other melodic voices)
- **Accent/ornament** (screams, falls, bends at the top; section hits with the
  trumpet in brass band)
- **NOT bass** (no low register; soprano's usable range starts where tenor's sweet
  spot ends)
- **NOT rhythm** (sustained melodic voice; occasional rhythmic stab aside)
- **NOT harmony pad** (monophonic line voice — no sustained chords; doubles only
  in unison/octave sax section writing)

## Timbre / Texture

- **Brightness**: the brightest member of the standard saxophone family
- **Penetration**: extreme — the soprano sax can cut through a full brass band
- **Range vs Alto**: sounds roughly a fourth higher than alto (Bb vs Eb transposition);
  tone is thinner, more reedy, less "vocal" than the alto
- **Range vs Clarinet**: soprano sax is conical bore (brighter, more projecting)
  vs clarinet's cylindrical bore; the sax has a wider more aggressive sound

## Synthesis Engines (musicom)

1. **PhaseModSynth** (primary) — soprano sax: saw carrier + sine modulator,
   mod_freq_ratio 1.0, mod_depth 2.6 (between clarinet 2.0 and alto 2.8 — the
   soprano reed is lighter and brighter than alto but conical bore keeps it
   reedier than clarinet). Fast attack 0.03 s (lightest reed in the sax family),
   release 0.08 s (smallest air column). This is the canonical engine.
2. **Additive** (fallback) — sawtooth-ish harmonic stack (6 partials, weights
   matching a conical-bore single-reed: strong fundamental, strong 2nd and 3rd,
   roll off above 5th). Add envelope: attack 0.04, decay 0.08, sustain 0.9,
   release 0.08. Use when PhaseModSynth is unavailable.
3. **BowedString** — NOT applicable (no bow).

## Production

- **Reverb**: room/plate 1.0–1.8 s (soprano is intentionally DRY compared to alto's
  bigger hall reverb — the bright attack needs clarity, not wash). REVERB_TAIL=1.4 s.
- **EQ**: cut ~800 Hz (soprano reed honk is higher-frequency than alto's 400 Hz body
  honk because the instrument is smaller). Boost ~2.8 kHz for presence (the soprano's
  cutting ring). High shelf ~6.5 kHz for shimmer/breath.
- **Delay**: subtle eighth-note delay in pop production; percussion with slapback
  in rockabilly.
- **Pan**: center for solo; +0.3 to +0.45 in sax section (panned against baritone's
  -0.2 to -0.35 for the classic stereo sax quartet image).

## FluidSynth / SF2 Notes

- `discover_soundfont()` prefers FluidR3_GM.sf2 (preset 64 = `Soprano Sax` — clean,
  focused patch with fast reed attack). TimGM6mb.sf2 fallback has `Sop Sax (TB) v2.3`
  (TB = TimBrasse — brighter, thinner, more aggressive than FluidR3).
- Empirical FluidR3 pitch sweep expected: preset 64 audible across the full 54–89
  span with smooth energy on the fundamental band. No gaps expected.
- Soprano sax SF2 patches tend to have a naturally nasal/"ducky" quality in the
  mid register — this is IDIOMATIC (the soprano sax has a more vocal/reedy timbre
  than the alto), NOT a defect.
- No key-switching or velocity layers; single-layer patch with natural velocity→loudness.

## Verification

- Render stem label: `trackXX_Soprano_Sax.wav` — verify against GM_PROGRAMS[64]
- Solo spectral check: 4–8 kHz buzz should be < 15% (soprano sax is naturally bright
  with strong 2-5 kHz energy; the 4-8 kHz band should show edge energy as expected
  from a reed instrument, NOT comb-filtered unison cancellation)
- Zero-drift: UnitMatrixComposer validate() passes with BAR-compliant event durations