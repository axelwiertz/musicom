# 264-rbncc-west-african-polyrhythm-rework

West African Polyrhythms — G major · 112 BPM · 4/4 · 10 sections × 4 bars = 40 bars.

Nightly rework (2026-10-25) of `210-rbncc-west-african-polyrhythm`, rebuilt from
scratch through the canonical `UnitMatrixComposer` engine while preserving the
musical identity: Method 082 **Random Boolean Network Criticality Composition**
(N=16, K=2, p=0.5 → edge of chaos; transient 1, attractor cycle 12) whose
12-step cycle against the 16-sixteenth bar produces the signature **3:4
cross-rhythm**.

## Voices

| Voice | Instrument | GM | Channel |
|---|---|---|---|
| Gankogui | Marimba (timeline bell) | 12 | 0 |
| LeadKora | Kalimba (RBN melody) | 108 | 1 |
| BassDunun | Double Bass (3+3+2 pulse) | 43 | 2 |
| Balafon | Xylophone (RBN counter) | 13 | 3 |
| Drums | Drum Kit | — | 9 |

## Form & variation (8 techniques)

Intro (register shift + sparse) → Verse (base 3:4 motif) → Chorus (density
rise) → Verse2 (transposition +2) → Chorus2 (inversion) → Break (retrograde +
darker vi–IV–ii–I) → Bridge (high register + balafon counterline) → Chorus3
(augmentation ×2) → Finale (diminution + density) → Coda (retrograde recap +
fade).

## Verification

- Zero-drift: 5 voice tracks × 76800 ticks (identical).
- `-perfect.mid`: 0 off-grid / 0 out-of-scale / 0 out-of-chord.
- `-humanized.mid`: 893 off-grid onsets (jitter proof), 0 out-of-scale.

## Files

- `MIDI/…-phase1.mid` (raw RBN draft) · `…-perfect.mid` · `…-humanized.mid`
- `Audio/…-perfect.ogg` · `…-humanized.ogg`
- `index.html` dashboard · `REPORT.md` · `Analysis/verify.json`

See `REPORT.md` for the full audit + method breakdown.
