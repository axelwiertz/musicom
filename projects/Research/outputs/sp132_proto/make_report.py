"""Generate report_SP-132.md from the live DB (verbatim section + row)."""
import io, subprocess

BASE = "/opt/data/repos/musicom/projects/Research/CompositionMethods"
db = io.open(f"{BASE}/methods_db.md", encoding="utf-8").read()
lines = db.split("\n")

# verbatim summary row
row = next(l for l in lines if l.startswith("| **SP-132** |"))
# verbatim detailed section (last section in file)
start = next(i for i, l in enumerate(lines)
             if l.startswith("# Sound Production Method SP-132"))
section = "\n".join(lines[start:]).rstrip() + "\n"

header = """# Report — SP-132 Rotary Speaker Doppler–Amplitude-Modulation Spatialization (RSDA)

**Job:** sound-production research cron · executed autonomously
**Date:** 2026-11-03
**Primary record:** this file. Chat message is a stub only.

| Field | Value |
|---|---|
| Method ID | **SP-132** |
| Method name | Rotary Speaker Doppler–Amplitude-Modulation Spatialization |
| Acronym | RSDA |
| Layer | **absolute** (sound production — LAYER_ARCHITECTURE.md) |
| DB family | Sound Production Methods Framework → Post-Processing / DSP |
| Candidate code path | `sound/effects/rotary_speaker.py` (new); dispatch via `workflows/musicom_workflow.py::produce(method="SP-132", ...)` |
| Standalone write-up | `sound_method_SP-132_RSDA.md` |
| Reference prototype | `projects/Research/outputs/sp132_proto/{leslie_proto,crossover_check,run_doc_sketch}.py` |
| Line count before | **29 779** |
| Line count after | **29 874** (+95) |
| Next free SP ID | **SP-133** |

**One-line description:** models the Leslie rotary cabinet as a rotating point
source whose real propagation delay simultaneously produces Doppler frequency
modulation (`frx = f0(1 − vr/c)`) and directivity/1-over-r amplitude modulation,
split by an 800 Hz LR4 crossover into an independently-rotating treble horn and
bass drum, with motor-inertia speed changes and a two-mic stereo capture.

## ID resolution (dynamic, verified)

- Summary-table scan: highest `| **SP-NNN** |` row = **SP-131** (TMVF, line 336).
- File scan (`sound_method_SP-*.md`): highest = `131_TMVF.md`.
- `SP-160` in the DB is **not** a method ID — it is a bibliographic citation
  ("Leissa, A. W. (1973). *Vibration of Plates*. NASA SP-160", line 9449).
- `Method 132` / `Method 133` in the same file are **composition** methods
  (BIBDC, ZRNC) in a separate numbering space, not SP methods.
- ⇒ new ID = **SP-132**. No duplicate: no rotary/Leslie/Doppler-spatialization
  method exists (closest neighbours: SP-119 auto-pan = level-only pan law,
  SP-106 phaser = phase-only, SP-021/053/129 = HRTF/VBAP/transaural placement,
  SP-055 = frequency shifter).

## Full summary-table row (verbatim as written to methods_db.md)

```
{row}
```

## Technical mechanics summary

| Quantity | Expression / value | Verified |
|---|---|---|
| Received signal | `y(t) = g(t)·x(t − τp(t))`, `τp = d/c`, `c = 343 m/s` | model identity |
| Path length | `d(t) = sqrt(R² + r² − 2Rr cos(θ − φ))` | 0.400–0.600 m horn, 0.350–0.650 m drum |
| Delay swing | 0.583 ms (horn r=0.10, R=0.5) / 0.875 ms (drum r=0.15) | measured |
| Motor | `dω/dt = (ωt − ω)/τm` | 10–90 % = 0.769 s at τm = 0.35 s; settle 1 % = 1.57 s |
| Doppler | `frx = f0(1 − vr/c)`, `vr = Rrω sin(θ−φ)/d` | ±2.19 ¢ @ 50 rpm vs 2.11 theory; ±21.45 ¢ @ 400 rpm vs 21.01 (2.1 % err) |
| Doppler law | `Δcents = 1200 log2(1 + rω/c)`, pitch-independent, speed-linear | 40→800 rpm table monotone, error ≤3.7 % |
| FM index @1 kHz, 400 rpm | `β = 12.2 Hz / 6.67 Hz = 1.83` | derived from measurement |
| AM | `g = (R/d)·10^(−(A/20)(1−cos(θ−φ))/2)` | total = A + 3.5 dB (A=3→6.52, 6→9.52, 10→13.52, 15→18.52 dB) |
| Distance AM alone | 3.52 dB at R=0.5, r=0.10 | measured |
| Crossover | LR4 (2× Butterworth-2), fc = 800 Hz | `|Hlp+Hhp| = 1.000000`, 0.0000 dB max dev, −6.02 dB/band at fc |
| Cabinet comb | 2.5 ms, gain 0.8 | null 199 Hz, depth −19.1 dB |
| Stereo | mics ±90° | ITD swing 0.583 ms, correlation +0.334 |
| Doc sketch run | extracted from the .md and executed | length preserved 24000→24000, all finite |
| Determinism | seeded rotor phase | yes |

## Quirks / pitfalls hit during this job

1. **Patch fuzzy-match misfire.** The V4A/replace patcher matched an earlier
   occurrence of the anchor and appended the whole SP-132 table row to the tail
   of the previous (ZRNC) pitfalls list, producing `...with \\`validate()\\` gating.| **SP-132** | ...`.
   Detected by re-reading the patched region; repaired with an exact
   line-index script (`outputs/sp132_proto/repair_row.py`) that cuts the
   fragment and re-inserts it after the SP-131 row. Lesson: for a 2 000-char
   single-line insertion, anchor on the *whole* preceding row or use an index
   script — never on a bare header line.
2. **Pre-existing `||` double-pipe rows.** SP-130 and SP-131 summary rows had
   a `||` prefix (earlier patch damage). Both normalised to a single `|`
   (SP-131 by prefix replace, SP-130 likewise). Verified: `grep '^||'` now
   returns nothing.
3. **LaTeX backslash guard.** The new row and section were checked for `\\\\`
   double-escaping: 0 occurrences after line 29 776 (`grep -c '\\\\\\\\'` on the
   appended range). The row has 6 pipes = 5 columns, matching the header.
4. **Hilbert-IF measurement bias.** First prototype measured 6.41 ¢ at 40 rpm
   where theory says 2.11 ¢ — the AM sidebands corrupt the instantaneous-
   frequency estimate of the *full* model. Re-measured with AM and 1/d
   disabled; measurement then tracks theory to 1.6–3.7 %. Recorded as
   Pitfall #1 of the method (it is a genuine verification trap, not just a
   scripting bug).
5. **Comb null detection.** First `crossover_check.py` reported the "first
   null" at 3000 Hz because of a slicing index bug (`argmin(H[10:])+10`).
   Fixed by masking the band; deepest nulls now report 199 Hz (theory 200 Hz).
6. **`/tmp` is write-protected** in this environment — the prototype lives in
   `projects/Research/outputs/sp132_proto/` (which also satisfies the Research
   AGENTS.md output rule).
7. **Model-vs-hardware scope.** rpm values, crossover band split, dual-horn
   with one blocked throat are from hardware documentation; the numeric
   Doppler/AM/spin-up figures are from *this document's* NumPy reference
   implementation, labelled "measured" accordingly. No claim is made that a
   122 measures exactly ±21 ¢ — the radius is a model parameter (`Δcents`
   scales as `log2(1 + rω/c)`).

## Complete section text appended to methods_db.md

"""
io.open(f"{BASE}/report_SP-132.md", "w", encoding="utf-8").write(header.replace("{row}", row) + section)
print("written; section chars =", len(section), "row chars =", len(row))
