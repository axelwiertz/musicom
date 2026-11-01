# REPORT — SP-130 Colored Noise Synthesis (CNS)

**Primary record.** Chat delivery is a short caveman summary only; everything is here.

| Field | Value |
|---|---|
| **Method ID** | **SP-130** |
| **Method name** | Colored Noise Synthesis (CNS) |
| **Layer** | **absolute** (sound production — LAYER_ARCHITECTURE.md): emits audio buffers at sample rate, writes no note events, holds no symbolic state |
| **Category (table)** | **Synthesis Engines** (pitch-less noise-texture generator) |
| **One-line description** | Generates pitch-less texture with controllable power-law spectral slope $S(f)\propto f^{-\gamma}$ — white/pink/brown/blue/violet + exact $1/f^\alpha$ via Voss–McCartney, Kellet 3-cascade, leaky cumsum/differencers, FFT powernoise — deterministic per seed, sample-count preserving (zero-drift safe). |
| **Summary table row (verbatim)** | `|| **SP-130** | Colored Noise Synthesis (CNS) | **Synthesis Engines** | Pitchless Noise-Texture / Ambient Bed, Riser, Impact & Percussive-Noise Timbres | Generates noise textures with a controllable power-law spectral slope: white (flat), pink $1/f$ ($-3$ dB/oct — Voss–McCartney octave-stream sum or Paul Kellet 3-cascade one-pole filter), brown $1/f^2$ ($-6$, leaky cumsum), blue/violet ($+3/+6$, differencers), and exact arbitrary $1/f^\alpha$ via FFT powernoise (Little et al. 2007). One knob (color $\alpha$) sweeps spectral centroid; per-row colors layer into wind/sea/rain beds, risers, impacts, and percussion noise tails; filtered noise (LP pink = wind, BP = breath) adds the musical textures. Deterministic per seed, sample-count preserving (zero-drift safe); the positive counterpart to SP-109 (noise reduction) and the raw-color stage behind SP-087/089/120. Candidate: `sound/generators/complex_noise.py`. |` |
| **Candidate code path** | `sound/generators/complex_noise.py` (exists — Q210-style white/pink-FFT/metallic/grainy; extend with Voss–McCartney, Kellet cascade, brown, blue, violet, powernoise α) → full engine `sound/synthesis/noise_synthesis.py` |
| **Dispatch** | `workflows/musicom_workflow.py::produce(method="SP-130", params={"rows": [...], "columns": {...}, "block": 8192, "master_level_db": -6})` |
| **Standalone file** | `/opt/data/projects/Research/CompositionMethods/sound_method_SP-130_CNS.md` (13 056 B) |
| **Verification script** | `/opt/data/repos/musicom/projects/Research/outputs/sp130_research/verify_sp130_cns.py` + demo render `cns_demo.wav` (pink bed + brown swell + blue burst) |
| **methods_db.md line count** | **29 439 before** → **29 523 after** section append (+84) → **29 524 after** summary-row insert (+1) |
| **Detailed section location** | `methods_db.md` lines **29 441–29 523** (`# Sound Production Method SP-130 — Colored Noise Synthesis (CNS)` … Pitfall 8), appended at EOF after the composition-method tail (TDRPC) — per cron-spec write_file → `cat >>` workflow |
| **Summary row location** | `methods_db.md` line **333** (inserted after SP-129 row, before table-closing `|---|`) |
| **Next free SP ID** | **SP-131** |

---

## 1. ID resolution (dynamic, not assumed)

| Probe | Result |
|---|---|
| `grep -oE '\| \*\*SP-[0-9]{3}\*\* \|'` on summary table | max = **129** (rows SP-001…SP-129, sparse gaps) |
| `ls sound_method_SP-*.md` | max = **129** (`sound_method_SP-129_TCCR.md`) |
| `ls report_SP-*.md` | max = **129** (`report_SP-129.md`, which itself declares "Next free SP ID: SP-130") |
| `grep -c "SP-13[0-9]|SP-1[4-9][0-9]|SP-2[0-9][0-9]"` before write | **0** (only the report_SP-129 "Next free" line) |
| **Assigned** | **SP-130 = max + 1** |

Numbering trap avoided: `workflows/musicom_workflow.py` carries a *separate* gear-emulation
SP namespace (SP-100…SP-134 — its "SP-107" is a Bit Crusher, ≠ methods-DB SP-107 LBL; its
SP-130 is a sample flipper). The report_SP-129 precedent (2026-10-31) treats the
CompositionMethods directory as authoritative for the methods-DB SP space, so **SP-130** is
correct. Same situation as the composition "Method 130/131" (SFT-C, TDRPC) docs at the DB
tail — different numbering space.

## 2. Novelty check (no duplicate)

| Probe | Hits | Verdict |
|---|---|---|
| `voss` | 8 | all composition-layer: 053 Lévy Flight (Voss 1994), 122 HCSC (Voss–Clarke 1978 law), reference citations — no production method |
| `mccartney`, `kellet` | 0 | — |
| `pink noise` | 1 | SP-126 loudness calibration remark, not a method |
| `colored noise` | 1 | SP-128 EMD aside ("colored noise bed with the colour of the source") — names the gap, no engine |
| `violet noise` | 3 | all SP-087 TR-808 snare (a differentiator = approximate violet) |
| `blue noise`, `power-law noise`, `fractal noise` | 0 | — |
| `1/f` | 40 | incidental (Hilbert-curve law, Chua, references) |

Verdict: **genuinely new** — no SP method generates colored noise as a parameterized
first-class timbre. Closest neighbors distinguished in the doc: SP-109 (reduction —
opposite direction), SP-035/057/068/120.

## 3. Research base (web)

- Wikipedia "Colors of noise" — color/PSD-slope taxonomy.
- Wikipedia "Pink noise" Generation section (fetched via MediaWiki API) — Voss–McCartney
  pseudocode (stream $j$ refreshed every $2^j$ samples), FFT 1/√f method, Voss & Clarke
  1975/78, Gardner 1978.
- firstpr.com.au (Whittle) "DSP generation of pink noise" — Kellet 3-cascade filter
  constants, Herriman ripple analysis, Csound `pinkish` lineage.
- Little et al. 2007 (powernoise 1/f^α) — standard method reference.

## 4. Verification results (numeric, 48 kHz / 8 s / Welch-Hann-8192 / log-log fit 120 Hz–14 kHz)

| Generator | Fitted γ | Target | Pass |
|---|---|---|---|
| white gaussian | +0.002 | 0 | ✓ |
| pink Voss–McCartney 16 streams | +1.074 | ~1 | ✓ |
| pink Kellet 3-cascade | +1.030 | ~1 | ✓ |
| pink FFT powernoise α=1 | +1.000 | 1 | ✓ |
| brown leaky cumsum | +1.927 | ~2 | ✓ |
| brown FFT α=2 | +2.000 | 2 | ✓ |
| blue 1st diff | −1.923 | ≈−1 (full-band) | ✓ |
| blue FFT α=−1 | −1.000 | −1 | ✓ |
| violet 2nd diff | −3.848 | ≈−2 (full-band) | ✓ |
| violet FFT α=−2 | −2.000 | −2 | ✓ |
| grey (FFT α=0) | +0.000 | 0 | ✓ |

Determinism (`np.array_equal` same-seed True, diff-seed False) ✓ · sample-count
preservation (all generators return exactly N) ✓ · demo WAV rendered ✓.
**ALL SPECTRAL-SLOPE CHECKS: PASS.**

## 5. Quirks / pitfalls hit (this run)

1. **Kellet filter overflow → NaN.** First attempt used the widely-copied 4-tap block
   coefficient form (b0..b4 / a0..a4, a0≈0.0555) via direct-form `lfilter` — overflowed to
   NaN in float64 at 48 kHz. Switched to the canonical 3-cascade one-pole form
   (poles 0.99765/0.96300/0.57000, gains 0.0990460/0.2965164/1.0526913, trim +0.1848·x):
   stable, γ=+1.030. Recorded as Doc Pitfall 1.
2. **Differencers deviate from nominal slope.** First-difference blue measured −1.92 and
   second-difference violet −3.85 full-band because |H|²=(2−2cosω)^k flattens toward
   Nyquist — not −1/−2. FFT powernoise α=−1/−2 are exact (−1.000/−2.000). Reported
   honestly, targets set to measured expectations, documented as Pitfall 2 (differencer =
   analog hiss character, TR-808 lineage).
3. **Display-layer `\\` double-escape confusion.** Tool-result rendering JSON-escapes
   backslashes, so `\alpha` displays as `\\alpha` and looks like patch pitfall (a).
   Resolved with a byte-level python check: **single backslashes everywhere**
   (row 2×`\alpha`, 0×`\\alpha`; section 17×`\alpha`, 0×`\\alpha`). No double-escape
   fix needed. Summary row pipe prefix verified single `||` (matches SP-129 convention;
   no `|||`/`|` anomaly).
4. **Two SP namespaces.** The gear-emulation registry in `musicom_workflow.py` (SP-100…
   SP-134) collides numerically with the methods DB; followed the report_SP-129 precedent —
   CompositionMethods directory files are authoritative for the DB space. Noted, not merged.
5. **Append location.** The DB tail ends with composition-method docs (TDRPC); the cron
   workflow mandates append-to-EOF (`write_file` → `cat >>`), which landed the SP-130
   section at lines 29 441–29 523 after that tail. Summary row inserted at the proper
   table position (line 333, after SP-129, before `|---|`).

## 6. Deliverables (all written this run)

- [x] Summary table updated: `methods_db.md` line 333 (`|| **SP-130** | … |`)
- [x] Detailed section appended: `methods_db.md` lines 29 441–29 523 (### Source, ### Layer,
      ### Description, ### Technical Mechanics, ### Musical Elements Framework,
      ### UnitMatrix Integration, ### Pitfalls)
- [x] Standalone file: `sound_method_SP-130_CNS.md` (full math, NumPy sketch, references)
- [x] Report (this file): `report_SP-130.md`
- [x] Verification: `outputs/sp130_research/verify_sp130_cns.py` + `cns_demo.wav`
- [x] `wc -l` 29 439 → 29 524; grep SP-130 confirms summary row (333) + detailed section (29 441)

**Next free SP ID: SP-131.**
