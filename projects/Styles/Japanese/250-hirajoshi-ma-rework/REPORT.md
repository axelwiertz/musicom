# REPORT — 250-hirajoshi-ma-rework

Rework of **001-japanese-hirajoshi** (Japanese hōgaku study in D hirajoshi).

## Source identity (preserved)

| Field | Value |
|---|---|
| Genre | Japanese hōgaku |
| Key | D hirajoshi (D-Eb-G-Ab-C) |
| Tempo | 70 BPM |
| Instruments | koto, shakuhachi, shamisen, taiko (ch9) |
| Core motif | koto sparse plucks (beats 0/2.5/3.5/4.0/6.5); shakuhachi sustained wide-leap ornamented melody; shamisen 8th ostinato root+4th; ma (silence) structural |

## Audit result (source)

| Standard | Result |
|---|---|
| S1 engine (UnitMatrixComposer) | PASS |
| S2 zero-drift | PASS (4 voice tracks @ 30720) |
| S3 rhythm-grid | PASS (0 off-grid) |
| S4 >= 4 tracks | PASS (4 voices) |
| S5 two-phase artifacts (`-phase1.mid`) | **FAIL** |
| S6 provenance.json + index.html | **FAIL** |

`redesign_required = true` (S5+S6). Decision: **redesign** — rebuild through the
canonical two-phase UnitMatrixComposer workflow, preserving only the musical
identity above.

## What changed / what's new

- **Length**: 16 bars (4 sections) → **32 bars (8 sections)**: Jo / Ha / Ha2 /
  Kyu / Bridge / Kyu2 / Develop / Jo2.
- **Two-phase architecture**: Phase 1 raw stochastic contour walk (unquantized
  pitch_index + rhythm, single voice) → Phase 2 musicom rules (chord-tone
  quantization per bar, 16th-grid snap + dedup, register enforcement, voice-leading
  check, 4-voice assignment).
- **Per-section harmonic regions**: each section has its own 4-chord progression
  (quartal trichords on hirajoshi scale degrees). Section root taken from the
  **midpoint** chord, never bar-0 tonic.
  `section_roots_midpoint = [0, 2, 2, 3, 2, 3, 1, 0]`.

## Variation techniques (5, documented per section)

| Section | Technique |
|---|---|
| Jo (0) | sparse ma intro |
| Ha (1) | theme A (quantized raw contour) |
| Ha2 (2) | **transposition / register shift +12** |
| Kyu (3) | climax: register +12, koto arpeggio, shamisen 16th (**density rise**) |
| Bridge (4) | **augmentation** (durations x2, half-speed koto) |
| Kyu2 (5) | **inversion** around axis 74, re-quantized to chord |
| Develop (6) | **retrograde** contour + re-harmonize |
| Jo2 (7) | sparse ma outro, fade |

## Verification (real numbers, read-only mido)

- File sizes: all MIDI/WAV/OGG `> 40` bytes (asserted).
- **Zero-drift**: perfect + humanized = **4 voice tracks @ 61440 ticks** (equal).
  phase1 = 1 voice @ 61440.
- **Off-grid** (pitched onsets): perfect = **0**; humanized = **387** (>0 → jitter ran).
- **Scale violations** (pc ∉ D hirajoshi): perfect **0**, humanized **0**.
- **Chord violations** (pc ∉ bar chord, floor t//BAR): perfect **0**; humanized **3**
  (all onset-jitter boundary straddles, dist=2 ticks; pitch still in key).
- Humanization (style=classical, seed=2971897743): Koto 2.97 / Shakuhachi 2.95 /
  Shamisen 3.36 / Taiko 0.78 mean |shift| ticks (drums tightest, plucks loosest).

## Audio (mastered to target_for_style("classical") = −18 LUFS, −1 dBTP)

| Variant | LUFS | dBTP | silence ratio |
|---|---|---|---|
| perfect | −18.0 | −2.0 | 3.66% |
| humanized | −18.01 | −1.05 | 4.68% |

Both silence ratios well under the 30% flag. dBTP sits below the −1 dB ceiling
(expected for a sparse/dynamic piece — the limiter is a ceiling, not a target).

## Notes

- D hirajoshi is **pentatonic** (5 tones), so the canonical `Scale7ChordDegree`
  helper (heptatonic, //7) does not apply; the piece uses a 5-note analogue
  (`octave = deg//5`, `step = deg%5`) — same no-wrap pattern, correct for this scale.
- Koto motif fixed to use the chord of the bar each pluck actually lands in
  (previous version spilled beats 4.0/6.5 across the bar boundary).
- `make_unit` sorts events by start_tick — required so the humanizer's
  forward-clamp (retrograde sections) does not collapse note onsets.
