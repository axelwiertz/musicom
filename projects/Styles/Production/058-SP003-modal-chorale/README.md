# 058-SP003 — Markov Chorale × Modal Physical Modeling (Plate/Bar)

**Production pass** applying **SP-003 Modal Physical Modeling (Plate/Bar)** to an
existing Musicom composition.

| Field | Value |
|---|---|
| Source composition | `Styles/Experimental/058-markov-chorale/MIDI/058-markov-chorale.mid` |
| Source method | 058 Markov-Chorale (autonomous composition job) |
| Production method | **SP-003** — Modal Physical Modeling (Plate/Bar) |
| Method layer | Synthesis Engines |
| Tempo | 90 BPM |
| Pitched voices rendered | 3 (SATB-style registers) |
| Notes | 32 |
| Render duration | 12.0 s (10 s music + 2 s ring-out tail) |

## What was done

Each MIDI voice was mapped to a **struck modal object** — a bank of parallel
second-order resonant biquads, each biquad one eigenmode of a vibrating solid
(the SP-003 physics; mechanics per methods_db SP-042 modal-bank spec):

| Voice (register) | Modal preset | Character |
|---|---|---|
| highest (mean ~66.8) | `marimba_bar` | warm woody, tuned modes 1:4:10 |
| mid (mean ~66.7) | `glass_bar` | bright glassy, inharmonicity 0.25 |
| lowest (mean ~51.0) | `rectangular_plate` | deep resonant plate, 20 modes |

Per note:
- **PITCH** → eigenfrequency table scaled by `f0 = 440*2^((n-69)/12)`
- **VELOCITY** → excitation amplitude + mallet hardness (louder = harder mallet)
- **RHYTHM** → note-onset triggers force impulse (soft half-sine mallet /
  hard Dirac impulse); object rings with **natural modal decay** — no envelope
  generator, re-strikes layer naturally
- Damping `gamma = gamma_int + rad(f)` — high modes radiate fast → "bright
  attack, warm sustain" of real struck bars/plates

Post: DC removed, peak normalized **-0.9 dBFS**, mild stereo widening (8 ms
complementary comb), 48 kbps Opus for Telegram delivery.

## Listen for

- **Attack→decay shape**: every note is a physical strike ringing out — no
  sustained pads, all decay-driven.
- **Register = object type**: low voice = dark plate boom, high voices = woody/
  glassy bar partials (fundamental + strong 4× and 10× partials).
- **The Markov harmony**: source is a 058 Markov-rule chorale; modal decay
  lets chord tones blur into each other — re-strikes before full decay create
  natural layered texture.

## Quality gate

| Check | Result |
|---|---|
| WAV size | 2,116,844 B (non-empty) |
| OGG size | 84,387 B (non-empty, plays) |
| Silence ratio | 11.5 % (tail only — acceptable) |
| Per-second RMS | active all 12 s, tail fade at end |
| Spectral content | fundamental + inharmonic partials across 50–4000 Hz |

## Files

```
058-SP003-modal-chorale/
├── README.md
├── provenance.json          # source + method + render params
├── sp003_modal_render.py    # renderer (NumPy + scipy, modal biquad bank)
├── MIDI/
│   └── 058-markov-chorale-original.mid
└── Audio/
    ├── 058-markov-chorale-SP003-modal-plate.wav
    └── 058-markov-chorale-SP003-modal-plate.ogg
```
