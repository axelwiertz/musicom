# REPORT — 303-funk-som-suite

**Project:** 303-funk-som-suite
**Style:** Funk
**Method:** 075 Self-Organizing Map Composition (SOM-C), extended
**Source:** 098-funk-som (audited 2026-11-14)
**Date:** 2026-11-14 (Nightly Rework Job)
**Seed:** 20261114 · **Humanize seed:** 100537415020 (md5-derived)
**Key:** F natural minor {F G Ab Bb C Db Eb} · **BPM:** 104 · 4/4 · 480 TPB
**Form:** 8 sections × 4 bars = 32 bars = 61,440 ticks (~73.8 s)

---

## 1. Audit result (source 098-funk-som)

| Standard | Result |
|---|---|
| 1 engine (not hand-rolled) | **PASS** — UnitMatrixComposer |
| 2 zero-drift | **PASS** — 5 voice tracks, all 46,080 ticks |
| 3 rhythm-grid sync | **PASS** — 0/576 pitched off-grid |
| 4 valid track setup | **PASS** — 5 voice tracks |
| 5 two-phase artifacts | **PASS** — `.mid` + `-phase1.mid` |
| 6 provenance.json + index.html | **FAIL** — both missing (only per-artifact sidecars) |

**Decision:** musical core fully compliant; failure is packaging-only. Identity
(Funk, F minor, 104 BPM, SOM-C method, trumpet-lead 5-voice texture) preserved
and **extended** into a longer, more varied suite. Non-compliant packaging fixed
in the new project (root `provenance.json` + `index.html` + dual-version export
+ mastering).

## 2. Longer + more varied

Source = 6 sections / 24 bars → new = 8 sections / 32 bars (N+2 sections, +33%).

| Section | Bars | Progression | Lead variation |
|---|---|---|---|
| Intro | 0–3 | i i iv v | baseline (lower register) |
| Verse | 4–7 | i VI iv v | baseline contour |
| Chorus | 8–11 | i III VII iv | register up, denser |
| Bridge | 12–15 | VI VII i v | **retrograde** contour |
| Verse2 | 16–19 | iv i VI v | **transposition +4th** (subdominant Bb) |
| Chorus2 | 20–23 | i III VII iv | **register shift +1 octave** |
| Breakdown | 24–27 | VI VII i i | **augmentation** (×2) + retrograde |
| Outro | 28–31 | i VI v i | baseline, sparse |

**Variation techniques (6):**
1. Transposition +4th / subdominant Bb region — Verse2
2. Register shift +1 octave — Chorus2
3. Retrograde contour — Bridge
4. Augmentation ×2 durations — Breakdown
5. Density contrast — Breakdown sparse (sax/piano tacet, sparse drums) vs Chorus full
6. Tenor Sax offbeat counterline — Verse/Chorus/Bridge/Verse2/Chorus2

## 3. Two-phase architecture

- **Phase 1** (`-phase1.mid`): raw 4×4 toroidal SOM trajectory walk, single
  Trumpet voice, unquantized pitch + continuous rhythm. 228 raw notes,
  220 off-grid, 99 out-of-scale, 168 out-of-chord (expected — pre-rules).
- **Phase 2** (`-perfect.mid` + `-humanized.mid`): musicom rules post-process
  (16th-grid snap, blanket chord-tone quantization per bar `t//BAR`, voice-leading
  leap cap ≤ 9, register clamp, dedup) + full 5-voice Funk arrangement.

## 4. Verification (read-only mido)

| Metric | perfect | humanized | phase1 |
|---|---|---|---|
| voice tracks | 5 | 5 | 1 |
| zero-drift (61,440 t) | true | true | true |
| pitched onsets | 696 | 696 | 228 |
| off-grid (≠ mult 120) | **0** | 634 (>0, jitter ran) | 220 |
| scale violations | **0** | **0** | 99 |
| chord violations | **0** | 9 (bar-seam jitter only) | 168 |
| strong-beat violations | **0** | **0** | 5 |

Humanization (funk style profile, timing 4 ms / layback 2 ms): drums tightest
(mean shift 1.03 t), bass lays back (8.45 t), lead loose (2.53 t). Recorded in
provenance.json (`humanize_profiles`) and Analysis/summary.json.

## 5. Artifacts

- MIDI: `MIDI/303-funk-som-suite-phase1.mid`, `-perfect.mid`, `-humanized.mid`
  (+ `.provenance.json` sidecars)
- Audio: `Audio/303-funk-som-suite-perfect.{wav,ogg}`, `-humanized.{wav,ogg}`
  (FluidSynth → `master()` @ −13 LUFS / −1 dBTP → Opus OGG)
- `provenance.json`, `index.html`, `README.md`, `Analysis/grid_visualization.txt`,
  `Analysis/verification.json`, `Analysis/rework_audit.json`, `Analysis/summary.json`
