# 223-rock-euclidean-extended — Rework of 093-rock-euclidean (Rock × Method 012)

**Rework job:** nightly senior-rework agent, 2026-10-05.
**Source:** `Styles/Rock/093-rock-euclidean` (2026-09-11).
**Style:** Rock · **Key:** E aeolian (natural minor) · **Tempo:** 128 BPM · 4/4.
**Method:** 012 Euclidean Groove Locking (`generators.rhythm.euclidian`).

---

## 1. Audit result (source = 093-rock-euclidean)

| Standard | Result |
|---|---|
| 1. Engine, not hand-rolled (`UnitMatrixComposer`) | **PASS** |
| 2. Zero-drift (all voice tracks equal length) | **PASS** (6 tracks × 46080) |
| 3. Rhythm-grid sync (pitched onsets on 8th/16th) | **PASS** (0 off-grid / 648) |
| 4. Valid track setup (>= 4 voices) | **PASS** (6 voices) |
| 5. Two-phase artifacts (`<id>.mid` + `-phase1.mid`) | **PASS** |
| 6. provenance.json + index.html | **FAIL** — `index.html` missing |

**Decision:** `redesign_required = true` (one standard failed). The gap is a
documentation artifact only — every engine/code standard passed. Rebuilt
preserving the musical identity, extended the form, and added the missing
dashboard.

Full machine record: `Styles/Rock/093-rock-euclidean/Analysis/rework_audit.json`.

## 2. What changed (identity preserved, form extended)

| Aspect | Source (093) | Rework (223) |
|---|---|---|
| Sections | 6 (Intro·Verse·Chorus·Bridge·Chorus2·Outro) | 8 (+Verse2, +Solo) |
| Bars | 24 | 32 |
| Voices | 6 | 7 (+ Flute counterline) |
| Lead register | fixed 60–96 | + octave-shift in choruses |

Preserved: Rock feel, E aeolian, 128 BPM, fiddle-lead texture, guitar chank,
piano stab, organ pad, double-bass 8th drive, GM kit, the syncopated
`euclidian(6,16)` lead cell and its scale-degree contour.

## 3. Variation techniques (7, all diatonic-safe in E aeolian)

1. **Augmentation** — Intro & Outro lead rhythm `euclidian(6,16)@120` →
   `euclidian(3,4)@480` (half-note spacing; note durations 360 vs 118).
2. **Transposition** — Verse2 lead contour starts +5 scale degrees (E4 → C5,
   pool index 2 → 7).
3. **Register shift** — Chorus & Chorus2 lead move up one octave (72–96 pool
   instead of 60–96).
4. **Inversion** — Bridge lead contour = negated motif deltas
   (`[-x for x in MOTIF]`).
5. **Diminution** — Solo lead rhythm `euclidian(8,8)@240` (8th-note run, densest
   section).
6. **Retrograde** — Outro lead contour = reversed motif (`MOTIF[::-1]`).
7. **Density rise** — drum kit: Intro kick-only → Verse +hat → Verse2 +snare →
   Chorus full +crash → Bridge +tom fills → Chorus2 full → Solo full +tom fills →
   Outro sparse.

## 4. Per-section harmonic regions (no bar-0 tonic bug)

Each 4-bar section has its own short progression; section roots are read from
the **midpoint chord** (bar index 2), never the bar-0 tonic.

```
Intro   i    i    VI  VII   (midpoint VI)
Verse   i    VI   III VII   (midpoint III)
Verse2  VI   III  VII i     (midpoint VII)   [transposed]
Chorus  VI   VII  i    i    (midpoint i)
Bridge  iv   VI   III VII   (midpoint III)   [inverted lead]
Chorus2 VI   VII  i    i    (midpoint i)
Solo    i    III  VII VI    (midpoint VII)   [diminished lead]
Outro   i    i    VI  i     (midpoint VI)    [retrograde lead]
```

Section midpoint degrees: `VI III VII i III i VII VI` — no all-tonic collapse.

## 5. Two-phase architecture

- **Phase 1** (`MIDI/223-rock-euclidean-extended-phase1.mid`, 981 B): single
  voice (fiddle), Euclidean intervals at a fractional tick unit + unquantized
  pitch walk. Raw fingerprint: **93 / 102 onsets off-grid** (by design).
- **Phase 2** (`MIDI/223-rock-euclidean-extended.mid`, 10633 B): 7 voices,
  musicom rules post-process — grid lock (078), chord-tone quantization per bar
  (`t // BAR`), `Scale7ChordDegree.get_diatonic_note` routing (no `% 7`
  wrappers), voice-leading check/correction (`VoiceLeadingRules`, classical),
  register enforcement, zero-drift normalization.

Voice-leading: **13 flags (parallel/hidden fifths+octaves) → 13 corrected**.

## 6. Verification (read-only mido audit)

| Gate | Phase 2 (rules) | Phase 1 (raw) |
|---|---|---|
| File size > 40 B | 10633 ✓ | 981 ✓ |
| Zero-drift (voice tracks) | 7 tracks × 61440 ✓ | 1 track × 61440 ✓ |
| Pitched onsets | 896 | 102 |
| **Off-grid** | **0** ✓ | 93 (raw fingerprint) |
| **Scale violations** (pc ∉ E aeolian) | **0** ✓ | n/a (raw) |
| **Chord violations** (pc ∉ bar chord) | **0** ✓ | n/a (raw) |

## 7. Audio render (SP-001 FluidSynth + FluidR3_GM.sf2 → Opus)

- `Audio/223-rock-euclidean-extended.wav` — 13 MB, 44.1 kHz stereo, 72.86 s,
  peak 0.994 (normalized 0.895 → −1 dBFS on the OGG).
- `Audio/223-rock-euclidean-extended.ogg` — 491 KB, Opus 48 kbps voip, 72.85 s.
- **Silence check:** total silence 15.3 % (all release/reverb tail); music-body
  (first 60 s) has **0 silent seconds**, per-second RMS ≈ 0.10–0.14. No
  mid-track gaps → not the silent-render trap.

## 8. Files

```
223-rock-euclidean-extended/
├── compose.py                  # single-file canonical UnitMatrixComposer workflow
├── MIDI/   223-rock-euclidean-extended.mid        (+ .provenance.json)
│           223-rock-euclidean-extended-phase1.mid (+ .provenance.json)
├── Audio/  223-rock-euclidean-extended.wav
│           223-rock-euclidean-extended.ogg
├── Analysis/ grid_visualization.txt · rework_verify.json
├── Scripts/ verify.py           # read-only mido audit
├── README.md
├── REPORT.md
└── index.html                  # VoltAgent dashboard
```

Rerun: `$MUSICOM_PYTHON compose.py` (env `musicom`).
