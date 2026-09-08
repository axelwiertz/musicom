# Report — SP-067 Kelly-Lochbaum Acoustic Tube Model (Vocal Tract Physical Modeling) (KLAT)

- **Method name:** Kelly-Lochbaum Acoustic Tube Model (Vocal Tract Physical Modeling) (KLAT)
- **Method ID:** SP-067
- **Acronym:** KLAT (Kelly-Lochbaum Acoustic Tube)
- **Layer:** **absolute** (sound production — renders symbolic note events to raw audio)
- **Category:** Synthesis Engines (physical modeling / scattering junction)
- **One-line description:** Models the vocal tract as an N-section lossless acoustic transmission line: the area function $A_i$ (vowel geometry) sets each junction's reflection coefficient $k_i=\frac{A_i-A_{i+1}}{A_i+A_{i+1}}$, and forward/backward pressure waves scatter through the two-port Kelly-Lochbaum lattice. A glottal pulse train (voiced) or frication noise (unvoiced) excites the glottal end; a $1-z^{-1}$ radiation load terminates the lips. Formants emerge from the area-function geometry — no formant filters.
- **Next free SP ID:** SP-068

## ID resolution

- Scanned `methods_db.md` summary table (rows `| **SP-NNN** |`): highest = SP-066 (line 164 pre-append).
- Cross-checked standalone files `sound_method_SP-*.md` / `report_SP-*.md`: highest = SP-066 (`sound_method_SP-066_FLUE.md`, `report_SP-066.md`).
- Grepped for `SP-067` anywhere → only the SP-066 report's "Next free SP ID: SP-067" line. No SP-067 file or table row existed → **SP-067 is free and new. Not a duplicate.**
- Grepped for vocal-tract coverage before choosing: SP-015 (PFVF), SP-025 (FOF), SP-028 (LPC), SP-038 (VOSIM), SP-046 (channel vocoder), SP-045 (DDSP), SP-061 (CLS) all model the vocal resonator *parametrically* or *neurally* — none is a scattering-junction / area-function physical tract model. **KLAT fills a genuine gap.**

## Summary-table row (appended after line 164, now line 165)

```
| **SP-067** | Kelly-Lochbaum Acoustic Tube Model (Vocal Tract Physical Modeling) (KLAT) | **Synthesis Engines** | Physical Vocal / Vowel / Formant Timbres | Models the vocal tract as an N-section lossless acoustic transmission line: the area function $A_i$ (vowel geometry) sets each junction's reflection coefficient $k_i=\frac{A_i-A_{i+1}}{A_i+A_{i+1}}$, and forward/backward pressure waves scatter through the two-port Kelly-Lochbaum lattice ($p^+_{i+1}=(1+k_i)p^+_i+k_i p^-_{i+1}$). A glottal pulse train (voiced) or frication noise (unvoiced) excites the glottal end; a $1-z^{-1}$ radiation load terminates the lips. Formants emerge from the area-function geometry — no formant filters. The physical/scattering-junction member of the vocal family (vs parametric SP-015/025/028/038/046). $\mathcal{O}(N)$ per sample, N≈8–20. |
```

Header columns matched exactly: `| Method ID | Method Name | Layer | Target Output | Description / Integration |`.

## Line-count before/after

- Before: **16623** lines.
- After detailed-section append (`cat >>`): **16718** lines (+95).
- After summary-row patch: **16719** lines (+1).
- Final verified count (Python, split on `\n`): **16720** lines (trailing newline yields an empty final element; `wc -l` reports 16719). Net delta vs 16623: **+96 lines** (95 section + 1 summary row).

## Artifacts

- **Standalone file:** `/opt/data/projects/Research/CompositionMethods/sound_method_SP-067_KLAT.md` (8684 bytes — extended physics, NumPy implementation sketch, references).
- **DB detailed section:** appended to `methods_db.md`, header `# Kelly-Lochbaum Acoustic Tube Model (Vocal Tract Physical Modeling) (Method SP-067)` at line 16625.
- **DB summary row:** line 165.
- **DB comparison table row:** line 16708 (`| **SP-067 KLAT** | ... |`).
- **Candidate code path:** `sound/synthesis/kelly_lochbaum.py` in `/opt/data/repos/musicom/sound/synthesis/` (sibling to existing `vocal.py`, `formant_voice.py`, `karplus_strong.py`, `bowed.py`).

## Layer classification

Every SP-* method is **absolute** (sound production — per `LAYER_ARCHITECTURE.md`). KLAT is a **Synthesis Engines** method (physical modeling): it consumes `MusicUnit` note events and renders audio buffers. It emits no symbolic MIDI (that would be `concrete`) and designs no pitch pools (that would be `abstract`).

## Technical mechanics (summary)

1. **Discretization:** N sections, $\Delta x = c/(2 f_s)$ → one-sample round-trip per section.
2. **Reflection coefficients:** $k_i = \frac{A_i - A_{i+1}}{A_i + A_{i+1}}$ from the area function.
3. **Scattering junction:** $p^+_{i+1} = (1+k_i)p^+_i + k_i p^-_{i+1}$; $p^-_i = k_i p^+_i + (1-k_i)p^-_{i+1}$ — unitary, lossless.
4. **Glottal source:** Rosenberg/LF pulse train (voiced) or band-limited noise (unvoiced/aspiration), −12 dB/oct rolloff.
5. **Lip radiation:** $R(z) = 1 - z^{-1}$ (+6 dB/oct tilt); net −6 dB/oct spectral tilt.
6. **Formants emerge:** uniform tube → $f_n = (2n+1)c/4L$; constrictions shift F1/F2; vowels = Fant area functions; transitions = area-function interpolation.
7. **Time-varying tract:** ramp $A_i(t)$ (not $k_i$) for diphthongs/gestures.
8. **Losses:** per-junction loss factor for formant bandwidth.

**Cost:** $\mathcal{O}(N)$ per sample (N ≈ 8–20), real-time, vectorizable, deterministic per seed.

## Musical Elements Framework mapping

| Element | Mechanism |
|---|---|
| PITCH | $f_0$ → glottal period $T_0$; glissando = continuous $f_0$ ramp; vibrato = $f_0$ LFO (~5–6 Hz) |
| RHYTHM | onset = glottal pulse-train start; articulation = glottal closure (legato/staccato); consonant = noise burst + formant transient |
| HARMONY | one voice = one tract; chord = N instances; shared vs independent vowels = blend vs separation |
| STRUCTURE | per-section vowel schedule = area-function trajectory; section boundary = phoneme/target change |
| TEXTURE | voicing mode (voiced/unvoiced/whisper/breathy); vowel = formant shape; breathiness = aspiration noise mix |

## UnitMatrix Integration

- **Rows (Voices)** = one KLAT instance per vocal voice; render independently, sum, spatialize (SP-021/034/043).
- **Columns (Sections)** = `{STRUCTURE}` carries vowel/lyric schedule + voicing mode + breathiness.
- **Cells (MusicUnit)** = `{PITCH}` → $f_0$ (+ glissando/vibrato); `{RHYTHM}` → glottal onset/duration/articulation; `{TEXTURE}` → vowel index + voicing/breathiness + velocity.
- **Flow:** `kelly_lochbaum(note_spec, vowel)` per note → glottal source → scattering lattice → radiation filter → section buffer → mix → post-FX (SP-007/008/009/032). Note-event consumer; deterministic; `validate()` zero-drift gate unaffected (audio layer). Forms a full vocal chain with SP-045 DDSP (f0/loudness extraction) and SP-061 CLS (cepstral resonator cross-synthesis).

## Complete section text appended

The full appended section (### Source / ### Layer / ### Description / ### Technical Mechanics / ### Musical Elements Framework / ### UnitMatrix Integration / ### Pitfalls / ### Comparison With Related Methods / ### References) is in `methods_db.md` at line 16625 and mirrored (with extended math + NumPy sketch) in the standalone `sound_method_SP-067_KLAT.md`.

## Quirks / pitfalls hit during this run

1. **No web search tool available in cron** (same as SP-065/SP-066 reports) — relied on established physical-modeling / speech-synthesis literature (Kelly & Lochbaum 1962, Markel & Gray 1976, Rabiner & Schafer 1978, Fant 1960, Rosenberg 1971, Smith 2010, Zölzer 2011). NumPy sketch explicitly flagged as topology-only (coefficients not calibrated audio).
2. **Backslash-escape verification** — grep `-o '\\'` throws "Trailing backslash" (regex ambiguity), and `grep -o '\\\\'` reported a misleading 2. Resolved with a byte-level Python check: my SP-067 summary row (line 165) has **2 single backslashes** (`\frac`, `\mathcal{O}`) and **0 double backslashes** — no double-escaping. The `grep -c '\\\\'` confusion came from shell+regex escaping, not the file.
3. **`||` prefix check** — `grep -c '^||' methods_db.md` → 0. The `||` in `read_file` output is the line-number delimiter plus the content's leading `|`, not a file defect (same as SP-066 report noted).
4. **Append workflow** — `_temp_sp067.md` written via `write_file`, concatenated via `cat >>`, removed. Confirmed removed.
5. **Line-count reporting nuance** — `wc -l` reports 16719 (counts newlines); Python `split('\n')` yields 16720 (trailing empty element). Reported both; net delta +96.
6. **Chose KLAT over other candidates** — it is the *physical/scattering-junction* member of the vocal family; every existing vocal method (SP-015/025/028/038/046/045/061) is parametric or neural. Verified no Kelly/Lochbaum/area-function/tube-model method already exists in the DB.
7. **`/tmp` write denied** — the verify script could not be written to `/tmp` (protected path); wrote it into the working directory instead, ran it, removed it.

## Verification commands run

```
wc -l methods_db.md                                      -> 16719
grep -n 'SP-067' methods_db.md                           -> 165 (row), 16625 (header), 16708 (comparison)
grep -c '^||' methods_db.md                              -> 0 (no double-pipe prefix)
python byte-check: line 165 single-backslash = 2, double = 0  -> no double-escape
ls sound_method_SP-067_KLAT.md                           -> present (8684 bytes)
```

## Next free SP ID

**SP-068**
