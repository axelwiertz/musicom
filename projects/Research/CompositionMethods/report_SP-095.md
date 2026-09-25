# Report SP-095 — Tonewheel Electromagnetic Modeling Synthesis (TWEMS)

## Method Identity
- **ID:** SP-095
- **Name:** Tonewheel Electromagnetic Modeling Synthesis
- **Acronym:** TWEMS
- **Layer:** absolute (Sound Production — Synthesis Engines)
- **Summary table row:**
  `| **SP-095** | Tonewheel Electromagnetic Modeling Synthesis (TWEMS) | **Synthesis Engines** | Electromechanical Organ / Drawbar-Composite Timbre | Models the Hammond tonewheel generator: 91 rotating disks with magnetic pickups produce 9 drawbar partials (harmonic ratios 0.5, 1.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0) with key-click transient (6th harmonic burst + staggered contact bounce), harmonic foldback at keyboard extremes, 5 Hz synchronous-motor tremolo, 6-position scanner vibrato/chorus (time-varying phase-shift delay), and the Leslie rotating speaker cabinet (Doppler time-varying delay + tremolo + crossover-filtered horn/drum paths). $\mathcal{O}(P)$ per sample ($P=9$ partials). Candidate: `sound/synthesis/twems.py`. |`

## File Paths
- **methods_db.md:** `/opt/data/projects/Research/CompositionMethods/methods_db.md`
- **Standalone file:** `/opt/data/projects/Research/CompositionMethods/sound_method_SP-095_TWEMS.md`
- **Report file:** `/opt/data/projects/Research/CompositionMethods/report_SP-095.md` (this file)
- **Candidate code path:** `sound/synthesis/twems.py`

## Line Count
- **Before append:** 20,309 lines
- **After append:** 20,492 lines
- **Delta:** +183 lines (detailed section appended to methods_db.md)
- **New standalone file:** ~280 lines

## Verification
- `grep "SP-095" methods_db.md` — confirms both summary row and detailed section present
- `ls sound_method_SP-095_TWEMS.md` — standalone file exists
- `ls report_SP-095.md` — report file exists
- Summary table parses correctly with 5 columns (Method ID, Method Name, Layer, Target Output, Description)

## Page Quirks / Pitfalls Hit
1. **Triple-pipe prefix on SP-093/094 rows**: Previous entries had `|||` prefix instead of `|`. Fixed by patching all three rows (SP-093, SP-094, SP-095) from `||`/`|||` to single `|`.
2. **read_file line number ambiguity**: The `LINE_NUM|CONTENT` format means a line displayed as `193||| **SP-093**` has content `|| **SP-093**` (the first `|` after `193` is the read_file separator, not content).
3. **Foldback edge artifacts**: Naive foldback table causes octave discontinuities; smooth crossfade needed.
4. **Per-sample sin calls**: 9 partials × polyphony = heavy; use wavetable lookup with phase accumulation.
5. **Leslie Doppler aliasing**: Fractional delay interpolation must be bandlimited (Thiran allpass recommended).

## Technical Mechanics Summary

TWEMS models the Hammond tonewheel organ as a complete electromechanical system:
1. **Tonewheel generator**: 91 rotating disks, 9 drawbar partials per key (ratios 0.5, 1.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0)
2. **Key-click**: 6th harmonic burst + staggered 9-pole contact bounce
3. **Foldback**: Harmonic pitch duplication at keyboard extremes (only 91 tonewheels for 96+ combos)
4. **Tremolo**: 5 Hz amplitude modulation from synchronous motor pole jitter
5. **Scanner vibrato/chorus**: 6-position tapped phase-shift delay line
6. **Leslie cabinet**: Doppler shift (time-varying fractional delay) + horn directional pattern + 800 Hz crossover for horn/drum split
7. **Percussion**: 2nd or 3rd harmonic transient at note-on (B3 only)

## Next Free SP ID
- SP-096 (highest existing is SP-095)

## References
1. Pekonen, Pihlajamäki & Välimäki (2011). "Computationally efficient Hammond organ synthesis." *DAFx-11*.
2. Smith, J. O. (2010). *Physical Audio Signal Processing*, Ch. 7.
3. Puckette, M. (2006). *The Theory and Technique of Electronic Music*, Ch. 2.
4. Electric Druid. "Technical aspects of the Hammond Organ."
5. Hammond Organ Company (1935). Patent 1,956,350.

---

*Generated 2026-09-25 by sound-production research cron job. Next free SP: 096.*