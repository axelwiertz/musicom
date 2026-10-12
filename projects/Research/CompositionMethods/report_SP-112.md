# Report: SP-112 — Linear Arithmetic Synthesis (LASS)

## Identity

| Field | Value |
|---|---|
| **SP-ID** | SP-112 |
| **Method Name** | Linear Arithmetic Synthesis (LASS) |
| **Acronym** | LASS |
| **Layer** | **absolute** — Sound Production (Synthesis Engines) |
| **One-line description** | Roland D-50 (1987) hybrid: a one-shot PCM attack transient (hammer, pluck, breath "chiff") is crossfaded via an enveloped equal-power balance into a subtractive sustain body (PolyBLEP saw/PWM through a resonant lowpass) — sampler-grade attack realism, synthesizer-grade sustain control. |
| **Candidate code path** | `sound/synthesis/la_synthesis.py` |

## Summary Table Row (inserted, line 293)

```
| **SP-112** | Linear Arithmetic Synthesis (LASS) | **Synthesis Engines** | Hybrid PCM-Attack + Subtractive-Sustain (LA) Timbres | Hybrid synthesis (Roland D-50, 1987): a one-shot PCM attack transient (hammer, pluck, breath "chiff") is crossfaded via an enveloped equal-power balance into a subtractive sustain body (PolyBLEP saw/PWM through a resonant lowpass). Partial = PCM or synth source + TVA/TVF envelopes; two partials = tone. Sampler-grade attack realism, synthesizer-grade sustain control. $\mathcal{O}(1)$ per sample per partial. Candidate: `sound/synthesis/la_synthesis.py`. |
```

Inserted immediately after the SP-111 row (which was line 292), before the `|---|` separator. Single `|` prefix, matching the clean SP-111 row format (legacy rows above it carry stray `||`/`|||` prefixes — not replicated).

## DB Line-Count Delta

| Before | After | Δ |
|---|---|---|
| 24879 | 24970 | +91 lines (1 new summary row + 89-line detailed section + 1 newline from glue fix) |

Breakdown of the +89 appended section: `# Linear Arithmetic Synthesis (LASS) — SP-112` heading + ### Source (6 refs) + ### Layer + ### Description + ### Technical Mechanics (balance law, PCM read, synth partial, TVF key tracking, TVA velocity law, cost) + ### Musical Elements Framework (PITCH/RHYTHM/HARMONY/STRUCTURE/TEXTURE) + ### UnitMatrix Integration + ### Pitfalls (9 items) + `---` + Candidate code path line.

## Files Created/Modified

| File | Status |
|---|---|
| `methods_db.md` (summary table, line 293) | Modified — inserted SP-112 row |
| `methods_db.md` (detailed section, appended at tail: lines 24882–24970) | Modified — appended SP-112 detailed section |
| `sound_method_SP-112_LASS.md` | Created — standalone full write-up (with NumPy implementation sketch) |
| `report_SP-112.md` | Created — this report |
| `_temp_sp112.md` | Created then deleted (write_file + cat >> append workflow) |

## Detailed Section Text Appended

The section appended to `methods_db.md` starts with `# Linear Arithmetic Synthesis (LASS) — SP-112` and contains:

- **### Source** — 6 references: Wikipedia (LA synthesis, D-50 1987, LA32 chip, partial/tone/patch), Roland D-50 Owner's Manual + structure diagram (TVA/TVF/balance/pitch env/3 LFOs), Vail 2014 (The Synthesizer, OUP), Russ 1987 (Sound On Sound, "Is the Future Linear?"), SoundBridge 2023 tutorial, Munt MT-32 emulator (LA32 reimplementation).
- **### Layer** — absolute — Sound Production (Synthesis Engines); code path `sound/synthesis/la_synthesis.py`.
- **### Description** — hybrid timeline assembly; PCM attack + synthetic sustain + looped embellishment; the "linear arithmetic" name (timeline elements, add/subtract/ring-mod — NOT additive); position vs SP-002/SP-044 (sampling) and SP-029 (subtractive); "memory goes to the transient, synthesis goes to the tail."
- **### Technical Mechanics** — equal-power balance mix $y(n)=g_P E_P x_P + g_S E_S x_S$ with $g_P=\cos(\pi b/2)$, $g_S=\sin(\pi b/2)$; PCM read $p_{n+1}=p_n+f_0\Pi(n)/f_\text{sample}$ (one-shot + looped modes, interpolation); phase accumulator $\phi_{n+1}=(\phi_n+2\pi f_0\Pi/f_s)\bmod 2\pi$ with PolyBLEP saw/pulse; TVF cutoff $f_c(n)=f_{c0}+(f_{c1}-f_{c0})E_{TVF}+k_t(f_0-f_\text{ref})$; TVA velocity law $L_\text{peak}=L_0(\text{vel}/127)^\gamma$; D-50-style 4-segment envelopes (linear-in-dB TVA); cost $\mathcal{O}(1)$/sample/partial, $\mathcal{O}(2)$/voice.
- **### Musical Elements Framework** — PITCH (one $f_0$ drives both partials; shared pitch envelope; key tracking; partial detune), RHYTHM (TVA articulation; transient = physical onset identity; balance envelope as within-note gesture; velocity accent hierarchy), HARMONY (per-voice LA tones; Fantasia-style stack; embellishment inharmonic loops under consonant bodies), STRUCTURE (per-section balance style + filter schedule as tension arc), TEXTURE (balance position $b$ as texture axis; embellishment stratum; detune/chorus ensemble).
- **### UnitMatrix Integration** — Voices = rows (LA tone per voice); Sections = columns (parameter cluster $\theta_s$); Cells = MusicUnit (pitch→$f_0$, velocity→TVA/TVF, duration→release, articulation→balance style); per-cell block render; zero-drift invariant untouched.
- **### Pitfalls** — 9 items: naive PCM interpolation aliasing, one-shot truncation click, linear-balance 3 dB dip (equal-power fix), aliased sustain body (PolyBLEP), filter zipper (one-pole smoothing + key tracking), envelope segment shape, transient/body tuning drift (shared pitch envelope), per-cell state policy, "not a sampler" (chorus/reverb glue).
- **`---`** + **Candidate code path** — `sound/synthesis/la_synthesis.py` implements `LAPartial`, `LAVoice`, `balance_gains(b, law="equal_power")`, `la_preset(name)`, `LACellConfig`.

## Technical Mechanics Summary

**Core equation** (per-sample voice mix):
$$y(n) = \cos\!\big(\tfrac{\pi}{2} b(n)\big)\,E_P(n)\,x_P(n) + \sin\!\big(\tfrac{\pi}{2} b(n)\big)\,E_S(n)\,x_S(n)$$

| Component | Equation | Role |
|---|---|---|
| PCM read rate | $r(n) = f_0\,\Pi(n)/f_\text{sample}$ | Attack transient pitch = note pitch; one-shot or looped |
| Synth phase | $\phi_{n+1} = (\phi_n + 2\pi f_0\Pi/f_s) \bmod 2\pi$ | Sustain pitch; saw/PWM + PolyBLEP |
| Filter cutoff | $f_c(n) = f_{c0} + (f_{c1}-f_{c0})E_{TVF}(n) + k_t(f_0-f_\text{ref})$ | Brightness envelope + key tracking |
| TVA peak | $L_\text{peak} = L_0(\text{vel}/127)^\gamma$ | Velocity → level + filter opening |
| Balance gains | $g_P=\cos(\pi b/2)$, $g_S=\sin(\pi b/2)$ | Equal-power crossfade (no 3 dB dip) |

**Architecture**: 2 partials per tone (PCM + synth, each with TVA/TVF), balance $b(t)\in[0,1]$ places elements along the note's timeline; embellishment looped waveforms as third stratum. **Cost**: $\mathcal{O}(1)$ per sample per partial.

## Quirks / Pitfalls Encountered During Implementation

1. **No trailing newline at EOF → glued heading**: the DB's last line (`Candidate code path: \`rules/fourier_pc_spectra.py\` — … via \`rules/realize.py\`.` — line 24879) had no trailing newline, so `cat >>` glued my heading onto it (`...rules/realize.py`.# Linear Arithmetic Synthesis (LASS) — SP-112`). Detected via grep, fixed with a targeted patch (split into two lines). The +1 line in the delta comes from this fix.
2. **LaTeX double-escape check**: verified with `grep -F` fixed-string matching — 0 lines with `\\mathcal` (double backslash, the known pitfall) and 2 lines with `\mathcal` (single, correct) across the SP-112 row + section. Single backslashes confirmed in the file.
3. **Row prefix `||` normalization**: inserted row uses single `|` (matches SP-111 row). Legacy rows above (SP-108..SP-110) carry `||`/`|||` prefixes — left untouched, not replicated.
4. **Temp-file workflow**: write_file created `_temp_sp112.md` (resolved through the symlink to `/opt/data/repos/musicom/projects/Research/CompositionMethods/` — same file), appended with `cat >>`, then removed. Verified removal.
5. **Anchor uniqueness**: used the unique tail of the SP-111 row (`$\mathcal{O}(1)$ per sample. Candidate: \`sound/synthesis/duffing_synth.py\`. |` + `|---|`) as the patch anchor — 141 `|---` occurrences exist, so the full-row tail is the safe anchor.
6. **`read_file` pagination**: DB 24,970 lines; multiple offset/limit reads required to pin the summary-table header (line 192–193), the SP-111 row, and the tail structure.

## Next Free SP ID

SP-113

## Grok-ready — Method Hybridization targets

- **LASS + SP-110 PWM**: the synth partial already IS a PWM voice — swap the SP-110 bare oscillator for the LA pair to give PWM pads a physical attack (the classic "D-50 string pad" recipe).
- **LASS + SP-029 subtractive**: route the PCM attack through the SP-029 Moog ladder for "processed transient" realism; or use the LA synth partial to feed the SP-029 filter chain for extra coloration.
- **LASS + SP-059 FDLMS**: LA body + ensemble chorus = the D-50's internal chorus emulation; per-voice detune already present, chorus widens the stack.
- **LASS + SP-009/SP-032 reverb**: the famous D-50 "Fantasia" space is 60% the internal reverb — LA voice → SP-032 FDN tail reproduces the signature.
- **LASS + SP-044 concatenative**: use SP-044's corpus to SELECT the attack transient table (feature-matched pluck/hammer/breath), then LA assembles transient + synthesized body — corpus-driven attack selection with fully synthetic sustain.
- **LASS + SP-096 HSOS**: hard-sync the synth partial (slave to the PCM read clock) for aggressive hybrid leads — synchronized transient + tearing body.
