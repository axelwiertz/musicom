---
name: style-method-instrument
type: Reference
title: Style → Method → Instrument Affinity Matrix
resource: https://github.com/axelwiertz/musicom
tags: [music, style, methods, instruments, affinity, okf]
timestamp: 2026-10-10T12:00:00Z
---

# Style → Method → Instrument Affinity Matrix

Canonical mapping of **which composition methods + instruments belong to a
style**. This is the synthesis layer above `methods_db.md`,
`human_methods_db.md`, and the `Instruments/` registry. It answers, for any
style, "what do I generate with, and what do I play it on."

## Core rule

A style is the product of three orthogonal decisions:

```
style = instrument DNA  ×  method paradigm  ×  (density · tempo · key)
```

- **Instrument DNA** — the non-negotiable identity (log drum = amapiano,
  accordion = chanson, sax = jazz). Swap it and the style reads as something
  else.
- **Method paradigm** — *how* the material is generated, independent of the
  instrument (stochastic vs rules vs nature-led vs AI vs set-theory).
- **Envelope** — density floor, tempo band, key center. The same method +
  instruments at the wrong tempo lands in the wrong genre.

## 1. Method paradigm → style affinity

| Paradigm | Methods (IDs) | Best suited styles |
|---|---|---|
| **Stochastic** | 002 Markov · 023 Tendency Masking · 041 ACOPF · 045 Hawkes · 053 Lévy | Jazz, blues, folk, pop melody — organic, contour-driven lines |
| **Rules** | 011 Euclidean · 025 Xenakis Sieve · 032 Isorhythmic · 033 WFC · 056 Species Counterpoint | Disco, house, techno, contemporary classical, minimal process |
| **Nature-led** | 026 DPSM · 030 Turing · 031 Boids · 038 Kuramoto · 043 Attractor | Ambient, minimal, experimental — flowing continuous texture |
| **AI** | 042 NST · 046 VAE · 057 GAN · 058 Neural-ODE | Style transfer, texture, hybrid — any genre |
| **Set-theory (ABS)** | ABS-001..005 (Z-swap · parsimonious VL · complement) | Tonal styles — classical crossover, pop, film |

### Hybridization rule (non-negotiable)

Sparse rhythmic methods (011 Euclidean, 032 Isorhythmic) produce staccato,
gap-filled texture. Always pair them with **one continuous layer** (026 DPSM
arpeggios, sustained pad, or walking bass) or the output reads "staccato
instead of flowing." See `genre-composition-patterns` for the worked density
tables.

## 2. Instrument family → style

Ground truth = `projects/Instruments/registry.md` + `instrument_registry.py`
(`by_name()` resolves GM preset names; a typo raises rather than skipping).

| Family | GM programs | Styles |
|---|---|---|
| Brass | 56 trumpet · 57 trombone · 58 tuba · 60 horn | Jazz, funk, big band, fanfare, mariachi |
| Strings | 40 violin · 41 viola · 42 cello · 43 bass · 46 harp · 110 fiddle | Classical, folk, cinematic, pop pads |
| Woodwind | 65 sax · 68 oboe · 69 eng horn · 70 bassoon · 71 clarinet · 72 piccolo · 74 flute · 22 harmonica | Classical, folk, world, blues (harmonica) |
| Keys | 0 piano · 4 Rhodes · 6 harpsichord · 8 celesta · 15 dulcimer · 19 organ | Universal — piano=all, Rhodes=soul/amapiano, organ=gospel |
| World | 104 sitar · 105 banjo · 106 shamisen · 107 koto · 108 kalimba · 111 shenai · 114 steel drums · 116 taiko | Indian, Japanese, African, Caribbean, folk |
| Percussion | 9 glock · 11 vibes · 12 marimba · 13 xylo · 47 timpani · ch9 kit | Mallet keys, orchestral accent, all rhythm |

## 3. Verified style DNA

Signature instrument + method + envelope per style (each pinned by a worked
composition in `projects/Styles/` or a `genre-composition-patterns` reference).

| Style | Signature instrument (GM) | Methods | Tempo | Key |
|---|---|---|---|---|
| Disco | Strings, brass, elec bass | 011 Euclidean + 026 DPSM + pad | 118–126 | Dm/Em/Am/C |
| Pop | Piano 0, string pad, bass | 002 Markov + 011 + 023 | 100–126 | C/G/D, Am |
| Blues | Acoustic guitar 25, bass, harmonica 22 | shuffle + 002/023 walking bass | 80–120 | blues keys |
| Jazz | Alto sax 65, piano, bass | 002 + 023 + swing comp | swing | — |
| Minimal | Marimba 12, strings, pad | phase/DPSM process + Euclidean anchor | metronomic | C/G/D, modal |
| Amapiano | Log drum (GM38), Rhodes 4, shaker | 011 groove + sustained Rhodes + sub | 108–115 | Am/Dm/F#m |
| Chanson | Accordion 21, guitar 25, trumpet 56, strings 49 | conjunct melody + I–V–vi–IV | 120–128 | C/G/F |
| House/Techno | Synth, filtered arps, drones | 011 four-floor + 026 arps + sidechain | 120–130 | minor |

## 4. Instrumentation as a palette (per-project)

`musicom-instrument-orchestration` defines named **palettes** (one instrument
per role) so a project can swap its whole lineup without forking the
framework — use this when auditioning variants. Pitfalls:

- **Range-check the whole palette**, not just the lead (a texture layer an
  octave low sat below the clarinet's 52 floor).
- **Stem routing key off track index**, not GM name (a name match breaks the
  moment the palette changes).

## 5. Style selection in the engine

`workflows/musicom_workflow.py` `STYLE_REGISTRY` carries bpm/form/motion/
default-voices per style; `workflows/selector.py` routes methods by a
`TaskProfile` (tonal gravity, metric binding, memory depth, corpus,
determinism, style). The affinity tables here are the *knowledge*; the
registry + selector are the *truth*. A method is routable only if
`generator_registry` has real code for it.
