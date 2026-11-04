# Agogô — research + verification report

**Date**: 2026-09-02 (nightly instrument job)
**Family**: World (11th entry)
**Files**: `instrument.md`, `agogo.py`, `REPORT.md`
**Registry**: `World.agogo.agogo` → key `agogo`, constant `AGOGO`

---

## 1. Instrument identity

**Agogô** — the Yoruba-derived multiple hand-bell of West Africa, carried to
Brazil through the slave trade. A Brazilian agogô is a pair (sometimes three
or four) of conical sheet-metal bells welded to a curved metal handle,
struck with a wooden or metal stick. The two-bell set is tuned roughly a
**third to a fourth apart**, and the player alternates between the bells to
play a fixed cyclic **timeline** pattern — the timekeeper of samba, samba de
roda, batucada, capoeira and candomblé, and the Brazilian cousin of the
Afro-Cuban clave.

Distinct from:
- **Cowbell** — one square-section bell, no paired-pitch timeline.
- **Woodblock (GM115)** — hollow wooden slit, dry knock, no metal ring.
- **Tinkle Bell (GM112)** — high sparkle, no timeline function.
- **Taiko (GM116)** — big drum, low accent, not a metal timeline.

## 2. MIDI / GM

| Item | Value |
|---|---|
| GM program | **113** (0-based; the 114th GM entry, "Agogo") |
| Channel | melodic channel 0–9 (patch is **pitched**) |
| FluidR3_GM.sf2 preset 113 | `"Agogo"` (read from the phdr chunk) |
| RenderPipeline `GM_PROGRAMS[113]` | `"Agogo"` |
| Stem file | `track00_Agogo.wav` — **no quirk** |
| Registry stem_label | `"Agogo"` |

GM neighbours: 112 Tinkle Bell, 114 Steel Drums, 115 Woodblock, 116 Taiko
Drum.

## 3. Range

| Zone | MIDI | Pitches | Register |
|---|---|---|---|
| Full (patch) | 55–96 | G3–C7 | GM pitched-bell span |
| Low | 55–66 | G3–F#4 | large low bell (agogô grande / candomblé gã) |
| Mid (core) | 67–79 | G4–G5 | the standard samba pair |
| High | 80–96 | G#5–C7 | agogô-mirim small bell |

- `RANGE_MIN = 55`, `RANGE_MAX = 96`
- `SOLO_RANGE = (67, 84)` — G4–C6, the real two-bell pair + a 3-bell set
- `SWEET_SPOT = (69, 81)` — A4–A5 (low bell A4, high bell a fourth up at D5)

Empirical FluidR3 pitch sweep (RMS, velocity 100):

| MIDI | 43 | 48 | 52 | 55 | 58 | 60 | 64 | 67 | 72 | 76 | 79 | 84 | 88 | 91 | 96 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| RMS | .0125 | .0117 | .0112 | .0107 | .0104 | .0099 | .0094 | .0089 | .0079 | .0073 | .0068 | .0060 | .0051 | .0048 | .0039 |

**15/15 audible, no gaps**, smooth rolloff, peak ≈ 0.25–0.33 — SF2 never
clips a composition.

## 4. Articulations (`ARTICULATIONS`, velocity + duration_factor)

One stick, two bells, **one note at a time** — never simultaneous strikes.

| Key | Velocity | Duration ×| Meaning |
|---|---|---|---|
| `open_high` | 96 | 0.6 | high bell free ring — the "teleco" |
| `open_low` | 92 | 0.8 | low bell, fatter bronze ring — the "tá" |
| `alternating` | 84 | 0.5 | the timeline: high/low 16ths |
| `muted` | 70 | 0.15 | hand clamp / bell body — dead click |
| `rim` | 88 | 0.10 | rim tick, sharpest sound |
| `double` | 94 | 0.35 | stick-bounce flam (virada) |
| `ghost` | 40 | 0.12 | barely-there 16th |
| `accent` | 104 | 0.55 | hard downbeat "1" |
| `roll` | 66 | 0.08 | single-bell tremolo — only sustain illusion |

## 5. Timbre DNA

- **Partials**: tuned metal — dominant fundamental, strong near-octave
  (~2×), then short inharmonic tail ~2.72× / ~4.07× / ~5.4×. Far more
  pitched than a Western cast bell (no minor-third tierce dominance), far
  brighter than a woodblock.
- **Attack**: ~1–3 ms (hard stick on thin sheet metal); the click is part of
  the sound.
- **Decay**: ~0.8–1.5 s free ring; high bell dies before low bell.
- **Release**: no damper; the free hand or the next stroke stops the ring.
- **Vibrato**: none.
- **Character**: bright, cutting, insistent — a timekeeper, not a colourist.

## 6. Role

`rhythm` (timeline patterns — primary), `accent` (downbeat "1"), `ornament`
(rim ticks, flams, virada rolls), `drone` (repeated single-bell offbeat
pedal).

NOT a melodic lead, NOT a harmony/chord voice, NOT a bass voice.

## 7. Synthesis engine

**Primary — ModalSynth** (`sound/synthesis/modal.py`), custom `AGOGO_MODES`:

```python
AGOGO_MODES = [
    (440.0, 1.00, 2.2),     # fundamental (A4 ref) — the bell's pitch
    (880.0, 0.42, 3.4),     # ~2x near-octave partner — "two-tone" clarity
    (1195.0, 0.22, 4.8),    # ~2.72x inharmonic metal partial
    (1790.0, 0.12, 6.2),    # ~4.07x bright rim shimmer
    (2380.0, 0.06, 7.0),    # ~5.4x top sparkle
]
```

`decay` is a **rate** (higher = faster). 2.2–7.0 gives the ~1 s agogo ring —
longer than marimba (8–20) / xylophone (9–20), close to taiko (2.6–6.0) but
brighter, shorter than vibraphone (0.30–1.10). Stock `MODAL_PRESET = 'bell'`
is the closest bank but models a **Western cast bell** (minor-third tierce,
very slow tail).

**Secondary — PhaseModSynth**: sine carrier, **non-integer** mod ratio 2.72
(inharmonic FM = classic bell recipe), depth 2.4, attack 0.001, release 0.9.
**Tertiary — Additive** (1 : 2 : 2.72 : 4.07 partial stack).
**Karplus-Strong — EXPLICITLY REJECTED**: struck metal, no string; a KS loop
is a harmonic series, the wrong partial structure (timpani/taiko precedent).

Smoke test (ModalSynth, 22.05 kHz, 1.5 s, impulse):

```
peak=0.900  head_rms=0.4124  mid_rms=0.1452  late(1.0–1.5s)_rms=0.0295
late/peak=0.0328   (bell still ringing at 1 s — not a click)
partial 2.00x = 29.5% of f0
partial 2.72x = 11.2% of f0
partial 4.07x =  4.8% of f0
```

## 8. Production defaults

| Param | Value | Reason |
|---|---|---|
| `REVERB_TAIL` | 1.3 s | street/roda instrument — dry, must cut a full bateria |
| `EQ_BODY` | (420 Hz, −1.5 dB) | boxy low-mid under the bell fundamental |
| `EQ_PRESENCE` | (3200 Hz, +2.5 dB) | stick-on-metal clank |
| `EQ_AIR` | (9000 Hz, +1.0 dB) | sheet-metal shimmer — never low-pass a bell |
| `PAN` | 0.0 | centre solo; bateria spread +0.15 opposite the tamborim |

## 9. Constants (`agogo.py`)

`MIDI_PROGRAM=113`, `GM_NAME="Agogo"`, `STEM_LABEL="Agogo"`,
`RANGE_MIN=55`, `RANGE_MAX=96`, `SOLO_RANGE=(67,84)`,
`SWEET_SPOT=(69,81)`, `ZONES`, `ARTICULATIONS` (9), `SYNTHESIS="modal"`,
`MODAL_PRESET="bell"`, `AGOGO_MODES` (5), `FM_DEFAULTS`,
`REVERB_TAIL`, `EQ_BODY`, `EQ_PRESENCE`, `EQ_AIR`, `PAN`, `midi_to_freq()`.

Registry `_FIELDS` extended with `agogo_modes` so the custom bank loads
through the registry (`AGOGO.agogo_modes`).

## 10. Registration proof

`_INSTRUMENT_MODULES` gained `"World.agogo.agogo": "agogo"`; constant
`AGOGO = ALL_INSTRUMENTS["agogo"]`; `registry_table()` role branch
`elif low == "agogo"`.

Full run: `cd /opt/data/projects/Instruments && python instrument_registry.py`
→ exit 0, **85 instruments** loaded (86 table lines incl. header).

Row in `registry_table()`:

```
| World | Agogo | 113 | 55–96 | rhythm, accent, ornament, drone |
```

Verification lines printed by the module:

```
  AGOGO.midi_program = 113 (should be 113)
  by_name('agogo') = <Instrument Agogo (family=World, program=113, range=55-96)>
  by_program(113) = <Instrument Agogo (family=World, program=113, range=55-96)>
  AGOGO.in_sweet_spot(72) = True
```

Verify-script (imports **through the registry**, `by_name('agogo')`):

```
registry: by_name('agogo') -> <Instrument Agogo (family=World, program=113, range=55-96)>
registry: by_name('Agogo') -> <Instrument Agogo (family=World, program=113, range=55-96)>
registry: by_program(113) -> <Instrument Agogo (family=World, program=113, range=55-96)>
registry: AGOGO is ALL_INSTRUMENTS['agogo'] -> True
registry: in_sweet_spot(72)=True in_sweet_spot(48)=False in_range(60)=True
```

Proximity check: `by_program(114)` → Steel Drums, `by_program(116)` → Taiko
Drum, `by_program(112)` → Tinkle Bell — 113 resolves uniquely to Agogo.

## 11. End-to-end verification (`_test/verify_agogo.py`)

```
Zero-drift: True (OK)
MIDI: _test/agogo_test.mid (263 bytes)
WAV (solo): _test/agogo_test.wav (813100 bytes)
Spectral check: 4-8kHz buzz energy = 19.6% (OK)
Stem labels: [112]='Tinkle Bell' [113]='Agogo' [114]='Steel Drums' [115]='Woodblock'
SF2: /opt/data/micromamba/envs/musicom/share/soundfonts/FluidR3_GM.sf2
SF2 preset 113 -> 'Agogo'
Stems rendered: track00_Agogo.wav (813100 bytes), track01_Drums.wav (849708 bytes)
ALL CHECKS PASSED
```

- Composition: 1 bar, 1 section, **Agogo SOLO voice** (samba timeline:
  A4/D5 alternating 16ths with accents + ghosts, ends flush at BAR) plus a
  **drum-kit context** track on channel 9 (kick + shaker hits). No second
  melodic patch → no unison doubling, no comb filtering.
- FluidSynth via `discover_soundfont()` (FluidR3_GM.sf2), `-ni -g 1.2`.
- Zero-drift: terminal `MusicEvent(0, 0, len_ticks, BAR)` landmark on both
  units → `validate()` True.
- MIDI 263 B > 40 B ✓, WAV 813,100 B > 40 B ✓, stems > 40 B ✓.

## 12. Quirks found / notes

1. **Spectral brightness is the highest in the KB — 19.6%** (gate 20%).
   Not comb filtering: the render is a single voice, and the spectrum shows
   real bell partials (top bins 446 Hz = A4 low bell, 1660 Hz, 2284 Hz) plus
   the broad stick-on-sheet-metal clank. The agogo is simply a bright metal
   instrument; the 3.2 kHz presence EQ and 9 kHz air shelf are the intended
   production shaping. This is the only instrument so far that sits within
   0.5 percentage points of the buzz gate — worth remembering if the gate is
   ever tightened.
2. **Stem label — no quirk**: `GM_PROGRAMS[113] = "Agogo"` and FluidR3 preset
   113 = `"Agogo"`. Contrast 109 `"Bag pipe"` and 111 `"Shanai"`.
3. **Pitched-patch trap**: GM113 is a *pitched* percussion patch — it must
   be written on a melodic channel with a real MIDI note (the two bells are
   two pitches). Channel 9 would trigger the drum-kit map and the
   `Acoustic_Grand_Piano` program-0 fallback label (timpani/taiko lesson).
4. **One stick = monophonic**: simultaneous two-bell strikes are not
   idiomatic; the pair is an *alternation*.
5. **Timeline, not melody**: writing quirks documented in `instrument.md`
   and the registry changelog (loop 1–2 bar patterns; straight 16ths; ghost
   notes at velocity 30–48).
6. **Registry `_FIELDS`** needed `agogo_modes` (same pattern as
   `xylophone_modes` / `celesta_modes`) for the custom modal bank to load
   through `Instrument` objects.

## 13. Files touched

- `World/agogo/instrument.md` (new)
- `World/agogo/agogo.py` (new)
- `World/agogo/REPORT.md` (new, this file)
- `instrument_registry.py` — module map, `AGOGO` constant, `_FIELDS`,
  `registry_table()` role branch, `__main__` verification lines
- `registry.md` — registry table row, stem-quirk row, dated changelog entry
- `README.md` — stale counts corrected (79 folders / 85 registry keys)
- `_test/verify_agogo.py` (new), `_test/agogo_test.mid`, `_test/agogo_test.wav`,
  `_test/stems_agogo/`
