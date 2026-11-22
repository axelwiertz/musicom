# Style Spec — `sinterklaas` (Dutch Sinterklaas liedjes)

Analysis of the Dutch **Sinterklaas liedje** repertoire, distilled into a
musicom style. Canonical touchstones: *"Zie ginds komt de stoomboot"*,
*"Daar wordt aan de deur geklopt"* (Dag Sinterklaasje), *"Sinterklaasje kom
maar binnen"*, *"O kom er eens kijken"*, *"Zie de maan schijnt door de bomen"*,
*"Hoor de wind waait door de bomen"*, *"Sinterklaas kapoentje"*, *"De zak van
Sinterklaas"*.

## The core rule (style = instrument DNA × method paradigm × envelope)

```
sinterklaas = bell/recorder/brass-band DNA × organic-conjunct melody ×
              (4/4 march · 108–120 BPM · major · high continuous density)
```

## 1. Instrument DNA (non-negotiable identity)

| Role | Instrument | GM | Why |
|---|---|---|---|
| Lead (melody) | Recorder | 74 | the school-blokfluit sing-along — every liedje is a unison children's song |
| Pad (wash) | Celesta | 8 | the "magic bell" harmonic bed (schoentje/pepernoten glitter) |
| Bass | Tuba | 58 | oom-pah brass-band / street-organ (draaiorgel) bass |
| Arp (glitter) | Glockenspiel | 9 | bell arpeggio shimmer — the Sinterklaas "arrival" sparkle |
| Drums | Kit (ch9) | — | light march: kick 1&3, snare 2&4, soft 8th hats |

Swap the recorder/glockenspiel for a sax and the tuba for a walking double
bass and the piece reads as something else — the bells + oom-pah + school
flute ARE the identity.

## 2. Method paradigm → organic-conjunct

A liedje is a **singable, conjunct, contour-driven** tune — the
**Stochastic→organic** family (folk/chanson side), NOT rules-groove and NOT
nature-ambient. Melody DNA:

- **Conjunct / stepwise**, narrow range (a 6th to an octave) — children must
  sing it, so no big leaps. Max leap observed = a 3rd/4th.
- **Dotted "arrival" lilt** — dotted-8th + 16th on the phrase head ("SIN-ter-
  klaas" = ta-ka). The signature march gesture of the steamboat/arrival songs.
- **Question–answer phrasing** — 4-bar phrase rises to **V** (half cadence),
  the answer falls to **I** (authentic V–I, often via the leading tone).
- **Literal repetition + sequence** — children learn it by rote; verses are
  strophic (same tune, new words).

The harmony layer is the **Rules** complement: dead-simple I–IV–V with an
oom-pah bass and a light march. Every song is a functional-harmony skeleton
with a child's melody on top.

## 3. Envelope (density · tempo · key)

| Parameter | Value |
|---|---|
| Key center | **C / F / G major** (bright, reassuring) |
| Tempo | **108–120 BPM** (4/4 march). Sibling 6/8 "evening" lilt at dotted-quarter ~60–72. |
| Meter | **4/4** march (primary) · 6/8 lilt (secondary family: "Zie de maan", "Hoor de wind") |
| Form | **Strophic** (verse ×4) or intro–verse–refrain–verse–outro |
| Density | melody ~90% · oom-pah bass ~85% · bell/pad 100% · arp 100% (continuous) · drums ~45% (light march) |
| Loudness | **−16 LUFS** (folk/dynamic — not slammed) |

## 4. Engine wiring (done 2026-11-22)

| File | Entry added |
|---|---|
| `workflows/style_instruments.py` | `INSTRUMENTATION_BY_STYLE["sinterklaas"]` + aliases |
| `workflows/style_rhythm.py` | `_lead_sinterklaas` (conjunct dotted-pickup melody) + oom-pah bass + march drums |
| `workflows/musicom_workflow.py` | `STYLE_REGISTRY["sinterklaas"]` (112 BPM, 4/4, intro-verse-chorus form) + `strophic`/`aabb` form hints |
| `transformers/humanize.py` | `STYLE_HUMANIZE["sinterklaas"]` — organic 8 ms timing, 0.45 phrase_corr, 2 ms layback |
| `sound/effects/mastering.py` | `GENRE_LUFS["sinterklaas"] = -16` |

Resolvable via `compose(style="sinterklaas")`, `instrument_palette("sinterklaas")`,
`style_fillers("sinterklaas")`, `profile_for_style("sinterklaas")`,
`target_for_style("sinterklaas")`. Aliases: `sinterklaaslied`, `kinderlied`,
`sint lied`.

## 5. The example (318-sinterklaaslied)

32 bars, C major, 112 BPM, 4/4. Form: **Intro(4) → Verse(8) → Refrain(8) →
Verse(8) → Outro(4)**. Verse = the question–answer tune ending authentic
V–I; Refrain = the quarter-note sing-along hook; Outro = descending closure
with progressive dropout (bass+drums → arp → pad only). Harmony per bar:

```
Intro:  C C C C
Verse:  C C F G | C F G C
Refrain:C F C G | C F G C
Outro:  C C C C   (pedal, dropout)
```

Melody register **B4–A5** (10 semitones), fully diatonic, dotted lilt on
phrase heads.
