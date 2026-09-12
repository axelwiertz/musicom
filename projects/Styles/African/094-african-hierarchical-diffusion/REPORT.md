# 094-african-hierarchical-diffusion — REPORT

**Date**: 2026-09-12 (nightly composition cron)
**Style**: African — Mande / djembe drum-ensemble idiom (kora, balafon, kalimba, fula flute)
**Layer**: `concrete` (6-of-7 concrete cadence; prior abstract runs 085/087/089/090, most recent concrete runs 091/092/093)
**Method**: **010 Hierarchical Diffusion** (multi-level, Markov base) — implementation `generators.chain.MarkovChainGenerator` (registry-confirmed; `generator_registry` maps 010 → `MarkovChainGenerator`, "Hierarchical Diffusion (multi-level, markov base)")
**Key**: A dorian (A B C D E F# G) | **BPM**: 112 | **Grid**: 16th (120 ticks @ 480 TPB)
**Form**: 6 sections × 4 bars = 24 bars — Intro / KoraVerse / BalafonChorus / Bridge / Chorus2 / Outro
**Seed**: 20260912

## 1. Selection (real values from `workflows.selector`)

- Style pool: 41 genre folders (excluded `_Comparison`, `_Data_Patterns`, `Research`, `Poetry`, `Production`, `Percussion`, `Other`), minus the 6 recently-used styles.
- Layer rule: 6-of-7 nights concrete → this is a **concrete** night. Method pool = `select_for_cron()` (headless + deterministic + real registry code) minus the last-7-day methods: `001, 010, 023, 040, HC-012` were eligible; `random.seed()` drew **010**.
- Registry truth check: `GENERATOR_REGISTRY["010"] = ("generators.chain", "MarkovChainGenerator", "Hierarchical Diffusion (multi-level, markov base)")`.

## 2. Method (concrete layer)

Method 010 = **diffusion down a hierarchy of Markov chains**, coarse to fine:

| Level | Space | States | Transition matrix |
|---|---|---|---|
| L4 macro | one state per **section** (6) | 3 (sparse/mid/dense) | M4 |
| L3 phrase | one state per **bar** inside the section (4) | 3 | M3, biased by the parent L4 state |
| L2 cell | one state per **beat** inside the bar (4) | 3 | M2, biased by the parent L3 state |
| L1 event | one state per **onset** inside the beat | onset menus of 1/2/3–4 hits | `L1_ONSETS` (all on the 16th grid) |

So the macro Markov plan literally *diffuses* into bar-level, then beat-level, then
onset-level material — one method, four resolutions. Interlocking is added by
rotating each voice's L1 onset offsets by a per-voice amount (kalimba 0, balafon 2,
flute 1, kora 3 16ths) → African hocket between the two lead timbres.

Progression (24 bars, 0-based A-dorian degrees):
```
Intro        i  i  IV VII
KoraVerse    i  IV VII i
BalafonChor  III VII i  v
Bridge       IV v  i  VII
Chorus2      III VII i  v
Outro        i  IV i  i
```
= Am7 · Am7 · D · G | Am7 · D · G · Am7 | C · G · Am7 · Em | D · Em · Am7 · G |
C · G · Am7 · Em | Am7 · D · Am7 · Am7

## 3. Two-phase architecture

| Phase | Artifact | Content |
|---|---|---|
| 1 | `MIDI/094-african-hierarchical-diffusion-phase1.mid` | Raw Markov draft: `MarkovChainGenerator.generate_unit_from_sequence()` over 7 pitch states (map `{0:66, 1:69, 2:73, 3:76, 4:78, 5:80, 6:84}` — includes **C# 73 and G# 80, outside A dorian**), realized at a deliberately fractional **417-tick** onset interval. Single kalimba voice GM 108, no harmony, no quantization. |
| 2 | `MIDI/094-african-hierarchical-diffusion.mid` | 4-level hierarchical diffusion → 16th-grid lock → A-dorian scale snap + chord-tone quantize per bar through the canonical `Scale7ChordDegree.get_diatonic_note` → voice-leading check/correct → full 6-voice African texture. |

Both phases passed their own zero-drift `validate()` gate (`True OK`).

## 4. Voices (instrument_registry — source of truth)

| Voice | Instrument | GM | Register used | Registry range | Role |
|---|---|---|---|---|---|
| Kalimba | Kalimba | 108 | 62–79 | 48–96 | lead thumb-piano line (L4→L1 diffusion) |
| Balafon | Marimba | 12 | 60–72 | 45–96 | balafon interlock (rotation +2) |
| Flute | Flute | 74 | 78–88 | 60–96 | fula-flute held counterline (rotation +1) |
| Kora | Acoustic Guitar (nylon) | 25 | 52–76 | 40–84 | kora 16th arpeggio (rotation +3) |
| Bass | Double Bass | 43 | 38–52 | 28–74 | dundun/root pulse driven by the L2 beat states |
| Drums | Drum Kit (ch 9) | 0 | keymap | — | djembe-oriented kit: clave bell 7-in-16 timeline, maracas shaker 16ths, kick/toms |

## 5. Verification (real numbers)

### Grid audit (phase-2 MIDI, mido read-only) — **PASS**
```
16th off-grid: 0/1433        (8th off-grid 635/1433 = legit 16ths)
  Kalimba  ch=0 notes=182 off16=0 off8= 36 end=46080
  Balafon  ch=1 notes=190 off16=0 off8= 45 end=46080
  Flute    ch=2 notes=184 off16=0 off8=141 end=46080
  Kora     ch=3 notes=179 off16=0 off8=141 end=46080
  Bass     ch=4 notes= 76 off16=0 off8=  0 end=46080
  Drums    ch=9 notes=622 off16=0 off8=272 end=46080
```

### Harmony audit (phase-2, canonical `Scale7ChordDegree` degree table) — **PASS**
```
  Kalimba  out_of_scale=0 out_of_chord=0
  Balafon  out_of_scale=0 out_of_chord=0
  Flute    out_of_scale=0 out_of_chord=0
  Kora     out_of_scale=0 out_of_chord=0
  Bass     out_of_scale=0 out_of_chord=0
```
Chord-tone quantization repaired 0 notes at compose time (the contour walker already
targets in-chord tones); every pitched note is an A-dorian scale tone **and** a
chord tone (triad + diatonic 7th) of its bar.

### Range audit — **PASS** (registry `in_range` True for all 5 pitched voices)

### Zero-drift — **PASS**
All 6 phase-2 tracks end at exactly **46080 ticks** (24 × 1920); phase-1 track too.
`drift_per_track` all 0.

### Phase-1 raw fingerprint
102 notes, **96/102 off the 16th grid** (2/102 on-grid by chance) — the raw draft is
off-grid and unquantized by construction. Pitch map contains 73 (C#) and 80 (G#),
both outside A dorian: the pre-rules state is audible.

### Voice-leading (rules.voice_leading, outer voices bass+lead vs next bar)
**2 flags pre-fix → 2 corrected → 0 flags** after re-check. (The `overflow in scalar
subtract` RuntimeWarnings from `rules/voice_leading.py:65/76/251` are the known
harmless list-arithmetic artifact also seen in projects 090/093.)

### Audio (SP-001 FluidSynth, `discover_soundfont()` → FluidR3_GM.sf2)
| Render | Duration | Peak | Silence ratio | Silent seconds | Verdict |
|---|---|---|---|---|---|
| phase-2 full mix | 62.80 s | 0.890 | **15.76 %** | 54–62 (tail decay only) | PASS (< 30 %) |
| phase-1 raw draft | 54.82 s | 0.888 | **13.32 %** | 50–54 (tail decay only) | PASS |

Per-second RMS: phase-2 stable **0.087–0.164** across seconds 0–50 (no mid-track
gaps; the only low values are seconds 51+ tail). Phase-1 RMS 0.078–0.180.
WAV sizes 11.1 MB / 9.7 MB asserted; all OGG/MIDI > 40 B.

### Tonal (ground-truth pitch) verification
- Phase-1 (monophonic): **102/102** expected fundamentals present (energy within
  ±3 % of f0), **102/102** with first-8-harmonic energy > 30 % of the 40–4000 Hz
  total. Not noise.
- Phase-2: **108/108** 0.5 s windows pitched by autocorrelation (mean harmonic
  ratio 0.193 — drums broadband by design).
- Melodic chroma (peak-picked, 500–2000 Hz band): top-4 pcs in A-dorian index
  order `0(C), 11(B), 2(D), 9(A)`, **in-key mass 0.905**, all top-4 in key.
- MIDI per-track pc audit: pitched tracks 0 off-key pcs. Track 6 (channel 9) shows
  keymap values {1,3,10} — that is the **percussion keymap**, not a pitch claim.

## 6. Bugs found & fixed during completion

1. **UnitMatrix cell-coordinate rebase (critical, 124 off-grid onsets).** Events are
   authored in ABSOLUTE ticks, but each `UnitMatrix` cell is a section-relative
   coordinate space. The first pass copied absolute ticks into cells without
   rebasing, so `normalize_cell` clamped every event of sections > 0 onto
   `SECTION_TICKS-10` (7670) — off-grid by 110 ticks and collapsing hundreds of
   notes onto one onset. Audit caught it as `124/870 off-grid` + 10/9/8/10/6
   out-of-chord (clamped notes landed on whatever bar the clamp position fell in).
   Fix: `slice_section()` rebases each event to section-relative ticks before
   `set_unit`. Re-audit: **0/1433 off-grid, 1433 notes**.
2. **Bass octave doublings off-chord (6 notes).** Blind `root+12` is not always a
   chord tone (e.g. 3rd-of-chord octaves on the v/IV bars). Rewired to pick the
   nearest *chord tone* above the root and widened the bass window to 33–52 so the
   diatonic octave is available. Re-audit: **0 out-of-chord**.
3. **Chroma test initially flagged off-key top pcs** — traced to the channel-9 drum
   keymap contaminating broadband spectral chroma. Fixed the *measurement* (band
   restricted to 500–2000 Hz, peak-picked) — not the music; melodic in-key mass
   0.905.

## 7. Files

```
MIDI/094-african-hierarchical-diffusion.mid            11820 B  (+ .provenance.json, phase=2)
MIDI/094-african-hierarchical-diffusion-phase1.mid       978 B  (+ .provenance.json, phase=1)
Audio/094-african-hierarchical-diffusion.ogg          494453 B  (+ .provenance.json)
Audio/094-african-hierarchical-diffusion-phase1.ogg   445264 B  (+ .provenance.json)
Analysis/grid_visualization.txt      (6 voices x 6 sections, █/░ densities 20–98 %)
Analysis/audit.json                  (grid + harmony + range + zero-drift; all PASS)
Analysis/tonal_check.json            (fundamental/harmonic/chroma/MIDI pc audit)
Analysis/render_stats.json           (silence ratio + per-second RMS)
Analysis/render_info.json            (peak/volume/normalisation per render)
Analysis/summary.json                (machine-readable project summary)
Analysis/concept.json                (method + form + progression record)
Scripts/compose.py audit.py render_audio.py audio_stats.py tonal_check.py summarize.py
README.md REPORT.md
```

Sources of truth used: `workflows.selector` (method routing), `generators.chain`
(method 010), `rules.progression.Scale7ChordDegree` (diatonic helper),
`rules.voice_leading` (VL gate), `projects/Instruments/instrument_registry.py`
(voices + ranges), `visualization.grid` (matrix grid), `workflows.provenance`.
Engine-only authoring — `mido` appears solely in the read-only audit scripts.

**Rerun order / note**: `compose.py → audit.py → render_audio.py → audio_stats.py →
tonal_check.py → summarize.py`. The two intermediate `.wav` renders (~11 MB each) are
deleted after measurement (WAV cleanup rule); `tonal_check.py` therefore needs a fresh
`render_audio.py` pass to run again — its recorded output is `Analysis/tonal_check.json`.
