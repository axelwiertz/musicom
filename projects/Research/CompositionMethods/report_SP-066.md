# Report — SP-066 Air-Jet Labium (Flute) Physical Modeling (FLUE)

- **Method name:** Air-Jet Labium (Flute) Physical Modeling (FLUE)
- **Method ID:** SP-066
- **Acronym:** FLUE (Flue-pipe / Flute Labium Unsteady Excitation)
- **Layer:** **absolute** (sound production — renders symbolic note events to raw audio)
- **Category:** Synthesis Engines (physical modeling, fluid-instability exciter)
- **One-line description:** Models the flute/flue pipe as a self-sustained fluid oscillator — an unstable air jet (Bernoulli velocity, convection at 0.4·vⱼ) flipping across the labium drives an open-open bore; no vibrating solid, the only fluid-instability exciter in the physical-model family.
- **Next free SP ID:** SP-067

## ID resolution

- Scanned `methods_db.md` summary table (rows `| **SP-NNN** |`): highest = SP-065 (line 162).
- Cross-checked standalone files `sound_method_SP-*.md` / `report_SP-*.md`: highest = SP-065 (`sound_method_SP-065_LIPS.md`, `report_SP-065.md`).
- Grepped for `SP-066` anywhere → only the SP-065 report's "Next free SP ID" line. No SP-066 file or table row existed → **SP-066 is free and new. Not a duplicate.**

## Summary-table row (appended after line 162, now line 163)

```
| **SP-066** | Air-Jet Labium (Flute) Physical Modeling (FLUE) | **Synthesis Engines** | Physical Flute / Flue-Organ Timbre | Models the flute/flue pipe as a self-sustained fluid oscillator: mouth pressure $p_m$ drives an unstable air jet (Bernoulli $v_j=C_v\sqrt{2p_m/\rho}$, convection at $0.4v_j$) that flips across the labium, injecting saturated acoustic flow $Q_{ac}=v_j b\,\mathrm{clip}(\eta_L/\eta_{\max})$ into an open-open bore (half-wave resonances $f_n=(n{+}1)c/2L_{eff}$). No vibrating solid — the only fluid-instability exciter; completes the family (reed SP-023, bow SP-024, lip-reed SP-065). Breath noise $\propto p_m$ separates flute from organ. $\mathcal{O}(1)$ per sample. |
```

Header columns matched exactly: `| Method ID | Method Name | Layer | Target Output | Description / Integration |`.

## Line-count before/after

- Before: **16463** lines.
- After detailed-section append (`cat >>`): **16553** lines (+90).
- After summary-row patch: **16554** lines (+1).
- **Net delta: +91 lines.**

## Artifacts

- **Standalone file:** `/opt/data/projects/Research/CompositionMethods/sound_method_SP-066_FLUE.md` (9460 bytes — extended physics, NumPy implementation sketch, references).
- **DB detailed section:** appended to `methods_db.md`, header `# Air-Jet Labium (Flute) Physical Modeling (FLUE) (Method SP-066)` at line 16465.
- **DB summary row:** line 163.
- **DB comparison table row:** line 16542.
- **Candidate code path:** `sound/synthesis/flute_jet.py` in `/opt/data/repos/musicom/sound/synthesis/` (sibling to existing `bowed.py`, `karplus_strong.py`, `modal.py`; future sibling of SP-065's `lip_reed.py`).

## Layer classification

Every SP-* method is **absolute** (sound production — per `LAYER_ARCHITECTURE.md`). FLUE is a **Synthesis Engines** method (physical modeling): it consumes `MusicUnit` note events and renders audio buffers. It emits no symbolic MIDI (that would be `concrete`) and designs no pitch pools (that would be `abstract`).

## Technical mechanics (summary)

Flute = a **fluid self-oscillator**, the only physical-model exciter with no vibrating solid:

1. **Jet formation (Bernoulli):** $v_j = C_v\sqrt{2p_m/\rho}$, $C_v\approx0.6$.
2. **Convection:** transverse jet disturbance travels at $u_c\approx0.4v_j$; transit delay $\tau_j = L_j/u_c$ (depends on $p_m$ → dynamic delay).
3. **Deflection:** $\eta_L(\omega)=G_j e^{-j\omega\tau_j}H_{LP}(j\omega)u_n(\omega)$, $G_j=L_j/v_j$ (delay line + one-pole jet LP).
4. **Edge split (nonlinear):** $Q_{ac}=v_j b\cdot\mathrm{clip}(\eta_L/\eta_{\max},-1,1)$ — the soft-clip is the harmonic source; harder blowing → brighter.
5. **Bore:** open-open tube, half-wave resonances $f_n=(n{+}1)c/2L_{eff}$; mouth pressure $p=Z_p Q_{ac}$.
6. **Regeneration:** loop gain ≥ 1, loop phase $=2\pi n$; overblow selects higher mode; jet-delay phase → "octave stretch" sharpness.
7. **Breath noise:** turbulence $\propto p_m$, one-pole LP ≈ 3–6 kHz — separates flute from organ.

**Cost:** $\mathcal{O}(1)$ per sample + delay reads; vectorizable; deterministic (seeded breath-noise RNG). Waveguide realization per Cook/STK `StkFlute`: bore delay + open-end reflection filter + jet delay + jet/lip filters + DC blocker.

## Musical Elements Framework mapping

| Element | Mechanism |
|---|---|
| PITCH | finger holes → $L_{eff}$ → $f_n$; embouchure selects/overblows mode; jet delay bends pitch sharp at high modes |
| RHYTHM | onset = $p_m$ ramp (tongue = interrupt); articulation = $p_m$ envelope; flutter-tongue = 20 Hz $p_m$ mod |
| HARMONY | one voice = one jet+bore pair; chord = N instances; overblow = partial shift; breath ratio changes blend |
| STRUCTURE | per-section fingering/embouchure/dynamic/breath schedule |
| TEXTURE | $p_m$ → brightness (edge saturation); breath ratio → airy vs pure; vibrato = embouchure LFO |

## UnitMatrix Integration

- **Rows (Voices)** = one FLUE instance per voice (flute 1/2, alto flute, piccolo); render independently, sum, spatialize (SP-021/034/043).
- **Columns (Sections)** = `{STRUCTURE}` carries fingering schedule, overblow mode, section dynamic, breath level.
- **Cells (MusicUnit)** = `{PITCH}` → bore length + overblow flag; `{RHYTHM}` → $p_m$ envelope; `{TEXTURE}` → velocity → $p_m$ peak → brightness + breath mix.
- **Flow:** note-event consumer → section buffer → mix → post-FX (SP-007/008/009/032). Deterministic; `validate()` zero-drift gate unaffected (audio layer).

## Complete section text appended

Full appended section (### Source / ### Layer / ### Description / ### Technical Mechanics / ### Musical Elements Framework / ### UnitMatrix Integration / ### Pitfalls / ### Comparison With Related Methods / ### References) is in `methods_db.md` at line 16465 and mirrored in the standalone `sound_method_SP-066_FLUE.md`.

## Quirks / pitfalls hit during this run

1. **No web search tool in cron** — same as SP-065: no search tool available; relied on established physical-modeling literature (Coltman 1968, Fletcher 1976, Fletcher & Rossing 1998, Howe 1975, Cook 1992/STK, De la Cuadra 2005, Verge et al. 1994–97). NumPy sketch explicitly flagged as placeholder coefficients (loop topology only, not calibrated audio).
2. **Backslash escape verification** — `patch`/`search_files` JSON renders a literal backslash as `\\`; verified against the actual file with `grep -o '\\' | wc -l`: my SP-066 row (line 163) has **9 single backslashes** (`\sqrt`, `\rho`, `\,`, `\mathrm`, `\eta`×2, `\max`, `\propto`, `\mathcal`) and **0 double backslashes** (`grep -o '\\\\' | wc -l` → 0). No double-escape; matches the pre-existing SP-064/SP-065 convention.
3. **`||` prefix check** — `grep -n '^||'` → zero matches. No normalization needed (file uses single `|` row prefixes; the `||` seen in read_file output is the line-number `|` delimiter plus the content's leading `|`).
4. **Append workflow** — `_temp_sp066.md` written via `write_file`, concatenated via `cat >>`, removed. Confirmed removed (no temp file remains).
5. **Chose FLUE (flute/flue-pipe jet-drive) over other candidates** — it uniquely completes the exciter taxonomy (reed/bow/lip-reed/air-jet); no existing SP method covers a fluid-instability oscillator (verified: no flute/jet/labium/flue match in the DB).

## Verification commands run

```
wc -l methods_db.md                                -> 16554
grep -n 'SP-066' methods_db.md                     -> 163 (row), 16465 (header), 16542 (comparison table)
grep -n '^||' methods_db.md                        -> (none)
sed -n '163p' methods_db.md | grep -o '\\' | wc -l -> 9 (single-backslash, correct)
sed -n '163p' methods_db.md | grep -o '\\\\' | wc -l -> 0 (no double-escape)
ls sound_method_SP-066_FLUE.md                     -> present (9460 bytes)
```
