---
type: instrument
family: Woodwind
name: English Horn
midi_program: 69
gms: "English Horn"
range_min: 50
range_max: 85
solo_range: [52, 77]
role: [lead, countermelody, melody, harmony, accent]
synthesis: [phase_mod, additive]
---

# English Horn (Cor Anglais)

The English horn (French: *cor anglais*, Italian: *corno inglese*) is a double-reed woodwind instrument in the oboe family, pitched a perfect fifth lower than the standard concert oboe (tenor oboe in F). It features a distinctive pear-shaped bell (*liebesfuss*) and an angled metal crook (*bocal*) carrying the double reed. 

Renowned for its plaintive, soulful, and elegiac tone color, the English horn holds one of the most poignant solo voices in orchestral and cinematic literature—famously showcased in Antonín Dvořák's *Symphony No. 9 "From the New World"* (Largo theme) and Jean Sibelius's *The Swan of Tuonela*.

## MIDI / GM

- **Program**: 69 (0-indexed GM1/GM2 standard; 1-indexed GM #70 "English Horn").
- **Channel**: Any standard melodic channel (0–8, 10–15).
- **RenderPipeline stem label**: `trackXX_English_Horn.wav` ✓ (pipeline `GM_PROGRAMS[69] = "English Horn"`, FluidR3 preset 69 = `"English Horn"` — exact match, no quirk).
- **SoundFont (FluidR3_GM.sf2)**: Preset 69 provides authentic multi-sampled double-reed waveforms with characteristic liebesfuss acoustic resonance, warm body, and natural expressive vibrato across MIDI 45–85 (sharp cutoff above 85).

## Range

In traditional orchestral scores, the English horn is a transposing aerophone pitched in F: written notes sound a perfect fifth lower. In musicom and MIDI standard convention, sounding pitch is used directly:

| Zone | MIDI | Pitches | Character & Register |
|---|---|---|---|
| Full range | 50–85 | D3–C#6 | Sounding pitch range supported by FluidR3_GM.sf2 |
| Low | 50–56 | D3–G#3 | Deep, dark, husky, velvety, rich double-reed drone |
| Sweet Spot | 57–72 | A3–C5 | Plaintive, haunting, singing solo voice (Dvořák New World Largo) |
| Mid-High | 73–79 | C#5–G5 | Intense, expressive, poignant, penetrating melodic lines |
| Altissimo | 80–85 | G#5–C#6 | Thin, pinched, dramatic, seldom used in classical literature |

- **Sounding Range**: MIDI 50 to 85 (D3 to C#6, ~146.8 Hz to ~1108.7 Hz). Standard orchestral compass sounds E3–A5 (52–81); low extension bell/keys sound down to Eb3/D3 (51/50).
- **Solo Range**: MIDI 52 to 77 (E3 to F5, ~164.8 Hz to ~698.5 Hz) — the quintessential pastoral and elegiac register.
- **Sweet Spot**: MIDI 57 to 72 (A3 to C5, ~220.0 Hz to ~523.3 Hz) — maximum emotional depth, warmth, and carrying power.

## Articulations

| Technique | MIDI Velocity | Duration | Character |
|---|---|---|---|
| Legato | 74–86 | 1.05 | Seamless cantabile, smooth lyrical phrasing (default) |
| Espressivo | 80–92 | 1.10 | Soulful melodic line with prominent expressive vibrato swell |
| Tenuto | 68–78 | 0.90 | Deliberate, held note with gentle reed separation |
| Staccato | 58–72 | 0.30 | Short, rounded, double-tongued articulation with warm body |
| Accent | 88–102 | 0.85 | Incisive double-reed tonguing, emphatic melodic entry |
| Pianissimo | 45–58 | 1.00 | Breath-supported whisper, distant pastoral melancholy |

## Timbre DNA

- **Harmonic Profile**: Wide conical bore combined with the pear-shaped bulbous bell (*liebesfuss*) attenuates high piercing frequencies that characterize the soprano oboe, instead concentrating energy in the warm lower-mid band (400–1000 Hz) and creating a hollow, nasal, mournful formant around 1.8–2.4 kHz.
- **Envelope**: Mild reed attack transient (40–70 ms), sustained breath body with low turbulence hiss, natural double-reed release (80–120 ms).
- **Vibrato**: Characteristic double-reed vibrato at 4.5–5.5 Hz, narrow pitch depth (±15–25 cents), opening up on sustained notes.

## Role in Arrangement

- **Pastoral / Lyrical Lead**: Solemn, mournful melodies; rustic and nostalgic themes.
- **Countermelody**: Rich counter-melodies below violins/flutes or weaving between clarinets and cellos.
- **Harmony / Woodwind Choir**: Fills the crucial tenor woodwind register between oboe/clarinet and bassoon.
- **Accent / Dramatic Interjections**: Solemn heraldic or ominous low-register phrases.
- **NOT high lead**: Lacks the cutting piercing brilliance of the soprano oboe above G5.
- **NOT rhythm**: Sustained acoustic wind instrument.

## Synthesis Engines (musicom)

1. **PhaseModSynth (`phase_mod`) — Primary Recommendation**:
   - Carrier: saw wave (double-reed rich even/odd harmonics).
   - Modulator: sine wave, `mod_freq_ratio: 1.0` (fundamental tracking).
   - `mod_depth: 2.2` (rounder and warmer than soprano oboe's 2.5, darker harmonic cutoff).
   - Attack: 0.06 s (sluggish reed inertia compared to soprano oboe), Release: 0.12 s.

2. **AdditiveSynth (`additive`) — Alternative**:
   - Rich harmonic series up to 20 partials.
   - Boost partials 2 through 4 (fundamental + lower octave/fifth warmth).
   - Distinct resonance hump at 1.8–2.2 kHz (liebesfuss cavity formant).

## Production Defaults

- **Reverb Tail**: 2.2 s (warm concert hall acoustics cradle the melancholic tone without blurring articulation).
- **EQ**:
  - Body: +2.0 dB at 600 Hz (enhances the round liebesfuss resonance).
  - Boxiness Cut: -1.5 dB at 350 Hz (removes chesty congestion).
  - Presence: +2.0 dB at 2.2 kHz (delicate reed formant definition).
  - Air: -1.0 dB high shelf above 8 kHz (maintains intimate, mellow darkness).
- **Pan**: +0.10 (slightly right of center in traditional woodwind seating, placed beside the 2nd oboe).

## FluidSynth & Pipeline Behavior

- **GM Program**: 69 (0-indexed).
- **RenderPipeline Stem**: `trackXX_English_Horn.wav` (pipeline `GM_PROGRAMS[69] == "English Horn"`).
- **FluidR3_GM.sf2**: Preset 69 is named `"English Horn"`. Audibility verified across MIDI 50–85 (RMS 0.027–0.048 with zero dropouts). Complete absence of sound above note 85 (preset upper key limit = 85 / C#6).
