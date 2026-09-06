# Report — SP-065 Brass Lip-Reed Physical Modeling (LIPS)

- **Method name:** Brass Lip-Reed Physical Modeling (LIPS)
- **Method ID:** SP-065
- **Acronym:** LIPS (Lip-Reed Instrument Physical Synthesis)
- **Layer:** **absolute** (sound production — renders symbolic note events to raw audio)
- **Category:** Synthesis Engines (physical modeling, exciter–resonator)
- **One-line description:** Models brass as a nonlinear self-oscillating loop — a lip valve (damped mass-spring with unilateral contact, Bernoulli flow) coupled to a flaring bore + bell resonator via a reflection function — pitch from bore length, brightness from blowing pressure.
- **Next free SP ID:** SP-066

## ID resolution

- Scanned `methods_db.md` summary table (rows `| **SP-NNN** |`): highest = SP-064 (line 160).
- Cross-checked standalone files `sound_method_SP-*.md` / `report_SP-*.md`: highest = SP-064 (`sound_method_SP-064_SRG.md`, `report_SP-064.md`).
- No SP-065 anywhere in table or files → **SP-065 is free and new**. Not a duplicate.

## Summary-table row (appended after line 160)

```
| **SP-065** | Brass Lip-Reed Physical Modeling (LIPS) | **Synthesis Engines** | Physical Brass Timbre (Trumpet/Trombone/Horn) | Models brass as a nonlinear self-oscillating loop: a lip valve (damped mass-spring with unilateral contact, Bernoulli flow $u \propto y\sqrt{|\Delta p|}$) coupled to a flaring bore + bell resonator via a reflection function $p[n]=\sum h[k]u[n-k]$. Pitch from bore length $L$ (valves/slide), bent by lip resonance; blowing pressure $p_m$ scales the nonlinearity so louder = brighter (free velocity→filter). Completes the physical-model family (reed SP-023, bow SP-024, plate SP-040, string SP-011/033/048). $\mathcal{O}(M)$ per sample. |
```

Header columns matched exactly: `| Method ID | Method Name | Layer | Target Output | Description / Integration |`.

## Line-count before/after

- Before: **16257** lines.
- After: **16333** lines.
- Delta: **+76** lines (detailed section appended).

## Artifacts

- **Standalone file:** `/opt/data/projects/Research/CompositionMethods/sound_method_SP-065_LIPS.md` (extended math + NumPy implementation sketch + references).
- **DB detailed section:** appended to `methods_db.md`, header `# Brass Lip-Reed Physical Modeling (LIPS) (Method SP-065)` at line 16259.
- **Candidate code path:** `sound/synthesis/lip_reed.py` (new module alongside `bowed.py`, `modal.py`, `karplus_strong.py` in `/opt/data/repos/musicom/sound/synthesis/`).

## Layer classification

Every SP-* method is **absolute** (sound production — per `LAYER_ARCHITECTURE.md`). LIPS is a **Synthesis Engines** method (physical modeling), consuming `MusicUnit` note events and rendering audio buffers. It does NOT emit symbolic MIDI (that would be `concrete`) and does not design pitch pools (that would be `abstract`).

## Technical mechanics (summary)

Brass = a **feedback oscillator**: mouth pressure $p_m$ drives a **lip valve** (damped mass-spring, displacement $y \ge 0$ with unilateral contact) that throttles Bernoulli airflow $u = w y \sqrt{2|p_m-p|/\rho}\,\mathrm{sgn}(p_m-p)$; the flow drives the **bore + bell** resonator, whose returned mouthpiece pressure $p$ closes the lips.

- **Lip ODE:** $m_r \ddot y + r_r \dot y + k_r(y-y_0) = (p_m-p)S$, with $\omega_r=\sqrt{k_r/m_r}$ the lip resonance (≈ played note) and $Q_r$ the quality factor.
- **Bore:** reflection-function form $p[n]=\sum_{k=0}^{M-1} h[k]u[n-k]$, $h=\mathcal{F}^{-1}\{Z(\omega)\}$; closed-pipe resonances $f_k\approx(2k+1)c/(4L)$ compressed by the flare; bell = frequency-dependent reflector/radiator (highs radiate, lows reflect).
- **Coupling:** per-sample fixed-point iteration (2–4 iters) or Cook's table-lookup junction to solve $(u,p)$ jointly (explicit step is unstable).
- **Pitch** = bore length $L$ (valves/slide), bent by $\omega_r$ and $p_m$. **Brightness** = $p_m$ (stronger nonlinearity → more harmonics → *fortissimo = brassy*).
- **Cost:** $\mathcal{O}(M)$ per sample, $M\approx 50$ ms FIR; vectorizable across voices; deterministic per seed.

## Musical Elements Framework mapping

| Element | Mechanism |
|---|---|
| PITCH | bore length sets resonance series; lip resonance + pressure select/bend the mode |
| RHYTHM | onset = $p_m$ ramp; tongue = $p_m$ interrupt; slur = move $\omega_r$ |
| HARMONY | one voice = one bore+lip pair; chord = N parallel instances; mute = per-voice filter |
| STRUCTURE | per-section bore/mute/pressure schedule; crescendo = $p_m$ ramp; doits/falls = $\omega_r$ glide |
| TEXTURE | $p_m$→brightness, $Q_r$→free/tight buzz, flare/mute→color, unison detune→section warmth |

## UnitMatrix Integration

- **Rows (Voices)** = one LIPS instance per row (trumpet 1/2, trombone, tuba); render independently, sum.
- **Columns (Sections)** = `{STRUCTURE}` carries mute on/off, section dynamic ($p_m$ baseline), articulation mode.
- **Cells (MusicUnit)** = `{PITCH}`→bore length + lip resonance; `{RHYTHM}`→$p_m$ envelope; `{TEXTURE}`→velocity→$p_m$ peak→brightness + mute type.
- **Flow:** note-event consumer (unlike SP-064's continuous pad) → section buffer → post-FX (SP-007/008/009/032). Deterministic → zero-drift gate unaffected (audio layer).

## Complete section text appended

The full appended section (### Source / ### Layer / ### Description / ### Technical Mechanics / ### Musical Elements Framework / ### UnitMatrix Integration / ### Pitfalls / ### Comparison With Related Methods / ### References) is in `methods_db.md` at line 16259 and mirrored in the standalone `sound_method_SP-065_LIPS.md`. Both are byte-identical in content.

## Quirks / pitfalls hit during this run

1. **Web search unavailable** — no search tool in this cron environment; `curl` to Wikipedia returned no usable text (empty grep, exit 0). Used established DSP/physical-modeling literature from knowledge (McIntyre-Schumacher-Woodhouse, Adachi-Sato, Cook, Causse-Kergomard-Lurton, Fletcher-Rossing). No fabricated measurements; the NumPy sketch is explicitly flagged as a placeholder-bore sketch.
2. **Backslash escape scare** — the `patch` tool and `search_files` render a literal single backslash as `\\` in their JSON output. Verified via `cat -A` + `grep -o '\\' | wc -l`: my SP-065 summary row has 5 backslashes (`\propto`, `\sqrt`, `\Delta`, `\sum`, `\mathcal`) — single-backslash, matching the pre-existing convention on SP-064 (2 backslashes: `\log_2`, `\mathcal`). **No double-escape.**
3. **`||` prefix** — checked with `grep -n '^||'` → zero matches. **No normalization needed.**
4. **Pre-existing table anomaly (not mine):** the summary table omits a `---` separator between the block ending at SP-050 (line 146) and the SP-051+ rows — those rows (SP-051..064) sit under the same header block without a re-emitted header. I inserted my row directly after SP-064 (line 160) before the existing `---`, preserving the file's existing layout exactly.
5. **`_temp_sp065.md`** was written via `write_file`, concatenated via `cat >>`, then removed — per the cron-safe append workflow (heredoc/execute_code blocked). Confirmed removed (no temp file remains).

## Verification commands run

```
wc -l methods_db.md                                -> 16333
grep -n 'SP-065' methods_db.md                     -> lines 161 (row), 16259 (header), 16321 (comparison table)
grep -n '^||' methods_db.md                        -> (none)
grep -o '\\' line 161 | wc -l                      -> 5 (single-backslash, correct)
ls sound_method_SP-065_LIPS.md                     -> present
```
