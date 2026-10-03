---
type: instrument
family: Brass
name: Muted Trumpet
midi_program: 59
gms: "Muted Trumpet"
range_min: 54
range_max: 86
solo_range: [60, 84]
role: [lead, countermelody, accent, melody, ornament]
synthesis: [phase_mod, modal, additive]
---

# Muted Trumpet

## MIDI / GM

- **Program**: 59 (GM1 Muted Trumpet)
- **Channel**: melodic channel; monophonic brass instrument
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 59 = "Muted Trumpet"
  (TimGM6mb fallback also has preset 59 = "Muted Trumpet"). RenderPipeline stem
  label: GM_PROGRAMS[59] = "Muted Trumpet" → `trackXX_Muted_Trumpet.wav` — matches
  exactly, **no quirk**.

## Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full range | 54–86 | F#3–D6 | practical muted trumpet range |
| Low | 54–65 | F#3–F4 | dark, breathy, less projection with mute |
| Middle | 66–79 | F#4–G5 | primary muted register — focused, nasal |
| High | 80–86 | G#5–D6 | bright, cutting — mute brightens altissimo |

The same physical range as open trumpet (F#3–D6). Muting does not affect
pitch range; it modifies timbre, attack transient, and projection. The
sweet spot for muted playing is D4–G5 (62–79) — the mute sounds most
characteristic here, with focused nasal tone.

## Articulations

| Technique | Velocity | Duration | Description |
|---|---|---|---|
| Sustain (straight mute) | 75–85 | full | standard metallic mute, even tone, slightly brighter |
| Staccato | 60–70 | 1/4 | crisp, dry — cup mute jazz stabs |
| Marcato | 88–100 | full accented | hard attack — harmon "wah" opening |
| Cup mute | 60–72 | full | dark, mellow, warm — jazz ballad texture |
| Harmon (stem in) | 70–85 | full | nasal, buzzy — "wah" with stem motion |
| Plunger | 80–95 | 3/5 | talking effect — hand over bell, growl |
| Bucket mute | 55–65 | full | very dark, soft, velvety — intimate passages |
| Flutter-tongue | 70–80 | full | tremolo through the mute |

### Mute types (GM59 default = harmon)

| Mute | Timbre | Musical context |
|---|---|---|
| **Straight** | Bright, metallic, piercing | Orchestral tutti, march, classical |
| **Cup** | Dark, mellow, round | Jazz ballads, soft ensembles |
| **Harmon** | Nasal, buzzy, wah-wah | Miles Davis style, bebop, pop |
| **Plunger** | Talking, growling | Dixieland, funk, R&B |
| **Bucket** | Very dark, soft, velvety | Intimate passages, background texture |

## Timbre DNA

- **Harmonic content**: similar to trumpet (strong odd harmonics 3, 5, 7)
  but the mute acts as a frequency-dependent filter — straight mute boosts
  2–5 kHz region (metallic ring), cup mute attenuates above 5 kHz, harmon
  mute creates a narrow bandpass resonance around 1–3 kHz ("wah" peak)
- **Attack**: 15–50 ms — slightly slower than open trumpet (mute back-pressure
  resists air column)
- **Decay**: sustained while blown; muted release is faster (less room ring)
- **Mute resonance**: the mute cavity adds its own filter — the characteristic
  "wah" of a harmon comes from moving the stem in/out, changing the filter
  centre frequency
- **Character**: focused, nasal, intimate, less brassy than open trumpet;
  can sound plaintive (cup), piercing (straight), or talking (plunger)

## Role in Arrangement

- Lead melody — jazz ballad, intimate passages (cup/harmon)
- Countermelody — call-response with open trumpet or sax
- Accent/stabs — harmon wah hits, brass section punctuation
- Special colour — plunger solo, harmon whisper, cup-mute soft pad
- NOT bass, NOT rhythm section — muted trumpet is a line/colour voice
- Monophonic — one note at a time (though harmon can sustain while moving)

## Synthesis Engines (musicom)

1. **PhaseModSynth** (`sound/synthesis/phase_mod.py`, FM brass) —
   **primary**. Same saw carrier as trumpet but with `mod_freq_ratio: 2.0`
   (higher = more nasal/focused) and `mod_depth: 2.5` (lower = less brassy
   edge). This produces the characteristic muted timbre: focused, nasal,
   less aggressive than open trumpet.

2. **ModalSynth** `'brass'` preset — generic modal resonator; usable
   fallback for straight-mute approximation.

3. **Additive** — odd-harmonic stack with a bandpass filter at 2 kHz
   to simulate the mute cavity resonance; best for harmon-mute timbre.

## Production

- **Reverb**: room/small hall 1.0–1.4 s — muted trumpet is an intimate
  sound, big hall reverb washes out the mute character
- **EQ**: cut 300–500 Hz (mute honk/boxiness), boost 3–4 kHz (mute buzz),
  gentle shelf above 8 kHz (harmon sizzle)
- **Compression**: light 2:1 for jazz ballads; moderate 3:1 for funk
  plunger work
- **Delay**: slapback 80 ms for plunger/wah; none for classical
- **Pan**: centre for solo; -0.15 to -0.25 for section work

## Verification

- GM59 renders as `trackXX_Muted_Trumpet.wav` in RenderPipeline stems
- GM_PROGRAMS[59] = "Muted Trumpet" — stem label matches, no quirk
- FluidR3 preset 59 = "Muted Trumpet" — SF2 label matches
- FM synthesis: mod_freq_ratio 2.0, mod_depth 2.5 → nasal focused tone
- Solo render spectral check: 4–8 kHz energy < 20% (no comb-filtering)