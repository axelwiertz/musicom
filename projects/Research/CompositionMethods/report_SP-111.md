# Report: SP-111 — Duffing Oscillator Nonlinear Synthesis (DONS)

## Identity

| Field | Value |
|---|---|
| **SP-ID** | SP-111 |
| **Method Name** | Duffing Oscillator Nonlinear Synthesis (DONS) |
| **Acronym** | DONS |
| **Layer** | **absolute** — Sound Production (Synthesis Engines) |
| **One-line description** | Integrates the forced damped Duffing oscillator at audio rate; displacement $x(t)$ is the output sample. Drive frequency = pitch, drive amplitude = one-knob chaos sweep (sine → odd-harmonic mode-locked → double-well strange attractor). |
| **Candidate code path** | `sound/synthesis/duffing_synth.py` |

## Summary Table Row (inserted)

```
| **SP-111** | Duffing Oscillator Nonlinear Synthesis (DONS) | **Synthesis Engines** | Forced-Nonlinear-Oscillator / Chaotic & Harmonic Organic Timbres | Integrates the forced damped Duffing oscillator $\ddot{x}+\delta\dot{x}+\alpha x+\beta x^3=\gamma\cos(\omega t)$ at audio rate; displacement $x(t)$ IS the sample. Drive frequency $\omega$ = pitch; drive amplitude $\gamma$ = one-knob chaos sweep (pure sine → odd-harmonic mode-locked → double-well strange attractor); seedable initial conditions give deterministic-per-note organic variation. $\mathcal{O}(1)$ per sample. Candidate: `sound/synthesis/duffing_synth.py`. |
```

## DB Line-Count Delta

| Before | After | Δ |
|---|---|---|
| 24697 | 24800 | +103 lines (~1 new summary row + ~102 detailed section + 1 temp removal) |

## Files Created/Modified

| File | Status |
|---|---|
| `methods_db.md` (summary table, line 291) | Modified — inserted SP-111 row |
| `methods_db.md` (detailed section, appended after previous entry at tail) | Modified — appended SP-111 detailed section |
| `sound_method_SP-111_DONS.md` | Created — standalone full write-up |
| `report_SP-111.md` | Created — this report |
| `_temp_sp111.md` | Created then deleted (heredoc workaround) |

## Detailed Section Text Appended

The section appended to `methods_db.md` starts with `# Duffing Oscillator Nonlinear Synthesis (DONS) — SP-111` and contains:

- ### Source — 6 references (Duffing 1918, Essl 2019, Spanedda 2025, Holopainen, Wikipedia)
- ### Layer — absolute (Sound Production — Synthesis Engines), code path `sound/synthesis/duffing_synth.py`
- ### Description — forced nonlinear oscillator as pitched chaotic synthesis method; comparison to SP-057 (autonomous, unpitched) and the linear oscillator family; three dynamical regimes: linear-ish, mode-locked, chaotic
- ### Technical Mechanics — Duffing equation $\ddot{x} + \delta\dot{x} + \alpha x + \beta x^3 = \gamma\cos(\omega t)$, state-space form, semi-implicit Euler discretization, pitch via drive frequency, backbone curve $\omega_{\text{eff}}(A) = \sqrt{\alpha + 3\beta A^2/4}$, jump resonance hysteresis, odd-harmonic generation ($x^3$ term), double-well chaos ($\alpha < 0$), seedable initial conditions, cost $\mathcal{O}(1)$ per sample
- ### Musical Elements Framework — PITCH (drive ω = f0, hardening detuning, double-well snapping), RHYTHM (drive gating, percussive ping, viscous decay), HARMONY (odd-harmonic series, per-voice chaos mix, Arnold-tongue subharmonics), STRUCTURE (γ sweep as tension arc), TEXTURE (distance from chaos threshold)
- ### UnitMatrix Integration — voices as independent integrators, sections as parameter clusters θₛ, continuous state across seams for zero-drift, cell filling: MIDI onset → ω + vel × γ → render block
- ### Pitfalls — 7 items: numerical blow-up (clamp x), aliasing (2× OS + LPF), chaos threshold portability (offline atlas), pitch ambiguity above threshold, DC offset (DC blocker), envelope step clicks (one-pole smoothing), efficiency vs. linear oscillators

## Technical Mechanics Summary

**Core equation**: Forced, damped Duffing oscillator:
$$\ddot{x} + \delta\dot{x} + \alpha x + \beta x^3 = \gamma\cos(\omega t)$$

**State-space** (1st-order form integrated at audio rate):
$$\frac{dx}{dt} = v, \quad \frac{dv}{dt} = -\delta v - \alpha x - \beta x^3 + \gamma\cos(\omega t)$$

**Solver**: Semi-implicit Euler (symplectic, stable for audio-range α at fs ≥ 44.1 kHz). Step size h = 1/fs.

**Parameter regime atlas**:
| Regime | α | β | δ | γ | Output character |
|---|---|---|---|---|---|
| Linear/pure sine | >0 | tiny | moderate | tiny | Sine-like tone |
| Hardening spring | >0 | >0 | low-moderate | low-moderate | Bright, odd-harmonic brass-like |
| Mode-locked subharmonic | >0 | >0 | low | moderate | Rich harmonic, period-n windows |
| Double-well chaos | <0 | >0 | low | moderate-high | Broadband, noise-like, "breathed" |
| Ueda attractor | 0 | >0 | low | moderate | Canonical strange attractor, gong-like |

**Pitch control**: Drive frequency ω = 2πf0. Hardening detunes pitch upward with amplitude — compensate by lowering f0 for high-velocity notes or exploit as expression.

**Output**: x(t) → tanh(x * 1.5) soft-clip → DC block → float32 sample.

## Quirks / Pitfalls Encountered During Implementation

1. **LaTeX double-escape**: The `patch` tool's new_string parameter must use single backslashes `\ddot` — but the initial write introduced `\\ddot`. Fixed by a second targeted replacement. Known pitfall #1 from the task.

2. **Table row prefix `||`**: Several existing rows in the summary table have a shared `||` prefix (lines 288–290 show `|| **SP-108**`, `|||| **SP-109**`, `||| **SP-110**`). My inserted row correctly uses a single `|` prefix, matching the clean format.

3. **Temp file resolution**: `write_file resolved path to `/opt/data/repos/musicom/projects/Research/CompositionMethods/` via symlink — no issue, same file. But the `cat >>` append used the direct path which also resolved correctly.

4. **Line-count accuracy**: Before: 24697 lines. After summary row + detailed section: 24800 lines = +103. The detailed section has ~102 lines; the summary row + spacer adds ~1 net (one row replaces `|---` with row + `|---`).

5. **Summary table anchor uniqueness**: `|---` matched 141 occurrences. Had to use the full SP-110 row as unique anchor to perform the row insertion.

6. **`read_file` pagination**: The DB is 24,800 lines. Multiple `read_file` calls with offset+limit were required to understand the structure at the tail. The end-of-file is line 24697+ (after the Costas section).

## Next Free SP ID

SP-112

## Grok-ready — Method Hybridization targets

- **DONS + SP-110 PWM**: DMA a pure PWM pad through a DONS response filter? Actually better: DONS chaotic oscillator → SP-029 subtractive filter → stable harmonic texture from chaotic source.
- **DONS + SP-059 FDLMS**: Modulate the drive phase with time-varying delay — the hardening/softening interaction gives unusual spectral animation.
- **DONS + SP-053 VBAP**: Place multiple DONS voices at different chaos levels on the 3D sphere; the chaos-threshold distance becomes spatial depth.
- **DONS + SP-085 NMF-C**: Decompose a DONS chaos block via NMF into basis spectra; then cross-synthesize with a pure-tone corpus — hybridizing chaotic and harmonic.