# 086-son-markov-guajira

Cuban son (guajira-leaning) montuno study — **Method 002 Markov Probabilistic
Transitions** (CONCRETE layer), two-phase architecture.

## Concept
A-minor Cuban son with a Markov-chain degree path driving the tres lead.
Tumbao bass, guajeo piano montuno, 3-2/2-3 son clave (woodblock in the drum
voice), trumpet answers, nylon-guitar comp. 104 BPM, AAB form.

## Key & Tempo
- Key: A minor (aeolian; bars 10/14/23 use the V7 = E7 with harmonic-minor G#)
- Tempo: 104 BPM · Meter: 4/4 · 480 TPB

## Form (24 bars = 6 × 4)
| Section | Bars | Harmony (A minor) |
|---|---|---|
| ClaveIntro | 1-4 | i pedal (clave call) |
| SonA | 5-8 | i – VII – VI – i |
| Montuno | 9-12 | ii° – i – V7 – i |
| SonA2 | 13-16 | iv – VII – V7 – i |
| Montuno2 | 17-20 | VI – iv – VII – i |
| Outro | 21-24 | i – VII – V7 – i (cadence home) |

## Two-phase artifacts
- `MIDI/086-son-markov-guajira-phase1.mid` — RAW Markov draft: single marimba
  voice, unquantized (72/192 onsets off-grid by design), no harmony.
- `MIDI/086-son-markov-guajira.mid` — Phase 2: chord-tone quantized, grid
  snapped (16th = 120), full son texture, zero-drift validated.

## Voices (engine registry + GM)
| Voice | Instrument | Program |
|---|---|---|
| Lead | Tres (nylon-guitar stand-in; not in registry) | 24 |
| Montuno | Piano (registry) | 1 |
| Comp | Acoustic Guitar (registry) | 25 |
| Bass | Contrabass (registry) | 43 |
| Trumpet | Trumpet (registry) | 56 |
| Drums | GM kit ch9 + woodblock clave | — ch9 |

## Verification
- Grid audit: 0 off-grid onsets (16th) for all pitched voices.
- Harmony audit: 0 out-of-scale, 0 out-of-chord for all pitched voices.
- Zero drift: validate() passed for both phase MIDIs.
- Render: SP-001 FluidSynth → WAV → OGG; 62.3 s, silence 10.8 % (tail only).

## Files
```
MIDI/086-son-markov-guajira-phase1.mid (+ provenance)
MIDI/086-son-markov-guajira.mid (+ provenance)
Audio/086-son-markov-guajira.wav / .ogg
Analysis/audit.json · grid_visualization.txt · render_stats.json · summary.json
REPORT.md
```
