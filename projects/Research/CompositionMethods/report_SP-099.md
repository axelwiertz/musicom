# Research Report: SP-099 — Comb Filter Resonance Synthesis (CFRS)

## Summary

| Field | Value |
|---|---|
| **Method ID** | SP-099 |
| **Method Name** | Comb Filter Resonance Synthesis (CFRS) |
| **Layer** | absolute (sound production — synthesis engine) |
| **Paradigm** | Sound Production / Synthesis Engines |
| **One-line Description** | Generates pitched sound by exciting a feedback comb filter with impulses, noise bursts, or oscillator pings, ringing at delay-line resonant frequencies. |
| **Candidate Code Path** | `sound/synthesis/comb_resonance.py` |
| **Produce Dispatch** | `produce(midi_path, method="SP-099", params={...})` |

## Summary Table Row Added

```
| **SP-099** | Comb Filter Resonance Synthesis (CFRS) | **Synthesis Engines** | Resonator-Based Pitched Timbre / Metallic, Plucked & Percussive Textures | Generates pitched sound by exciting a feedback comb filter with short-duration impulses, noise bursts, or oscillator pings, ringing at the delay-line resonant frequencies $f_0 = f_s / K$. Four modes: impulse-excited (plucked percussion), noise-excited (pitched drone/hiss), oscillator-excited (resonant-body tone), and parallel comb bank (inharmonic bell clusters). Fractional delay for exact equal-temperament tuning; allpass dispersion chain for metallic inharmonicity. $\mathcal{O}(1)$ per sample per comb. Candidate: `sound/synthesis/comb_resonance.py`. |
```

## Database Statistics

| Metric | Value |
|---|---|
| **Lines before** | 21584 (original count) |
| **Lines after** | 21943 |
| **Line count delta** | +359 |
| **File size before** | 2,104,425 bytes |
| **File size after** | 2,130,506 bytes |

## Standalone File

| File | Path |
|---|---|
| Sound method doc | `/opt/data/projects/Research/CompositionMethods/sound_method_SP-099_CFRS.md` |
| Report (this) | `/opt/data/projects/Research/CompositionMethods/report_SP-099.md` |

## Next Free SP ID

**SP-100** — the next method should use SP-100.

## Full Section Text Appended

The following section was appended to `methods_db.md` under the Sound Production Methods Framework section, after the last existing SP-098 detailed section:

```markdown
# Sound Production Method SP-099 — Comb Filter Resonance Synthesis (CFRS)

### Source
Smith III, J. O. (2010). *Physical Audio Signal Processing*. W3K Publishing. Ch. 2–3 (Delay Lines, Feedback Comb Filters). — Dattorro, J. (1997). "Effect Design, Part 1: Reverberator and Other Filters." *JAES* 45(9). — Karplus, K. & Strong, A. (1983). "Digital Synthesis of Plucked-String and Drum Timbres." *Computer Music Journal* 7(2), 43–55. — Jaffe, D. A. & Smith, J. O. (1983). "Extensions of the Karplus-Strong Plucked-String Algorithm." *CMJ* 7(2), 56–69. — Välimäki, V. et al. (2012). "Fifty Years of Artificial Reverberation." *IEEE Trans. Audio, Speech & Lang. Process.* 20(5), 1421–1448. — Puckette, M. (2007). *The Theory and Technique of Electronic Music*. World Scientific. Ch. 4 (Filters). — Dodge, C. & Jerse, T. A. (1997). *Computer Music: Synthesis, Composition, and Performance* (2nd ed.). Schirmer. pp. 129–137. — Roads, C. (1996). *The Computer Music Tutorial*. MIT Press. Ch. 6 (Delay-Line Based Synthesis).

### Layer
**absolute** — sound production (synthesis engine; translates symbolic note triggers, MIDI pitch, velocity, and articulation parameters into continuous time-domain audio samples via delay-line comb filter resonance). The candidate code path is `sound/synthesis/comb_resonance.py`, pluggable into `workflows.musicom_workflow.produce(method="SP-099")`.

### Description
**Comb Filter Resonance Synthesis (CFRS)** generates pitched sound by exciting a feedback comb filter with short-duration excitation signals — impulses, noise bursts, filtered noise, or oscillator pings — and letting the feedback delay line ring at its resonant frequencies. Unlike Karplus-Strong (SP-011), which places a one-pole lowpass filter inside the feedback loop to model frequency-dependent string damping and uses an initial noise burst as the only excitation, CFRS offers the pure, uncolored comb filter as both an effect and a synthesis building block. The feedback comb filter's frequency response consists of equally spaced peaks at harmonics of $f_0 = f_s / K$ (where $K$ is the delay length in samples) and notches at frequencies halfway between the peaks. When driven by an impulse train, noise burst, or sustain oscillator, the filter selectively boosts its resonant modes, producing metallic ringing, plucked percussive tones, body-resonance textures, and pitched noise cloud timbres.

The method generalizes across four modes of operation:
1. Impulse-Excited Comb (IEC): A single impulse or short noise burst triggers the comb to ring at $f_0$, producing plucked-string or struck-percussive tones with no lowpass decay — all harmonics decay at the same rate, giving bright, metallic timbres.
2. Noise-Excited Comb (NEC): Continuous filtered noise drives the comb, producing a pitched noise texture with tone centered at $f_0$ — the resonator picks the fundamental and harmonics out of the broadband noise, creating a drone-like pitched hiss.
3. Oscillator-Excited Comb (OEC): A pitched oscillator (sine, saw, square from the oscillator's spectrum) drives the comb. The comb emphasizes its resonant modes, creating formant-like spectral bumps that shift when the input pitch or the comb delay changes — akin to a spectral resonator bank.
4. Parallel Comb Bank (PCB): Multiple comb filters with coprime delay lengths and per-comb feedback gains run in parallel from a shared excitation, producing dense, evolving pitched textures with inharmonic or pseudo-chordal character. This is the resonator-bank approach analogous to modal synthesis (SP-042) but built from delay lines rather than biquad modes.

### Technical Mechanics
#### 1. Feedback Comb Filter (the Core Resonator)
Difference equation: $y[n] = x[n] + g \cdot y[n - K]$

$z$-domain: $H(z) = 1/(1 - g z^{-K})$

Peaks at $f_k = k \cdot f_s/K$ for $k=1,2,\dots$

$T_{60} = -3K \log 10 / (f_s \log g)$

#### 2. Fractional Delay (Linear, Allpass, Lagrange4)
#### 3. Excitation Models (IEC, NEC, OEC, PCB)
#### 4. Dispersion via Allpass Chain
#### 5. Python/NumPy implementation sketch

### Musical Elements Framework
PITCH: delay length → pitch; RHYTHM: gate-triggered + decay; HARMONY: single comb harmonic, PCB inharmonic; STRUCTURE: section CFRS parameters; TEXTURE: 4 excitation modes × PCB density × dispersion.

### UnitMatrix Integration
Rows = voices as CFRS instances; columns = sections with CFRS config; cells = notes rendered per voice; produce() dispatch.

### Pitfalls
1. Stability (g < 1)
2. DC buildup (DC blocker needed)
3. Pitch quantization without fractional delay
4. Aliasing at high pitches (oversample)
5. Phase cancellation in PCB
6. Confusion with Karplus-Strong (SP-011)
7. PCB memory at long decays
```

## Technical Mechanics Summary

| Component | Equation / Algorithm | Complexity |
|---|---|---|
| Feedback Comb | $y[n] = x[n] + g \cdot y[n-K]$ | $\mathcal{O}(1)$ |
| Fractional Delay (linear) | Lagrange/linear interpolation | $\mathcal{O}(1)$ |
| Allpass Dispersion | $H_{ap}(z) = (c+z^{-1})/(1+cz^{-1})$ chain | $\mathcal{O}(M)$ |
| Noise Excitation | Uniform RNG + exponential envelope | $\mathcal{O}(1)$ |
| Parallel Comb Bank | Sum over $C$ independent combs | $\mathcal{O}(C)$ |
| PCB + dispersion + frac delay | Combined per-sample | $\mathcal{O}(C \cdot M)$ |

## Quirks and Pitfalls Hit

1. **Summary table [|| vs ||| bug]**: The initial patch inserted `|||` (triple pipe) instead of `||` at row start because the patch tool matched the old_string format differently from the actual bytes. Fixed with a second patch targeting the triple-pipe version. Root cause: the `read_file` tool's line-number display (adding leading `||`) confused which byte pattern the patch `old_string` should match. The `cat -A` verification step was critical.

2. **SP ID verification**: The highest existing SP was SP-098 (confirmed via table scan + grep). The detailed sections for SP-094 through SP-098 exist in the DB. No gap above SP-098. SP-099 confirmed free.

3. **No existing sound_method_SP-099*.md or report_SP-099*.md files**: Both were created fresh as new files.

4. **Web research**: Wikipedia comb filter page (truncated), Julius Smith's CCRMA JOS site (not reachable with web_extract), and the Nonlinear Labs C15 documentation provided sufficient technical detail. The core equations are well-established (Smith & Dattorro 1990s).

## Verification

- `wc -l` confirms methods_db.md has 21943 lines (+359 from original 21584)
- Grep for `SP-099` confirms summary row at line 268 and detailed section at end of file
- Standalone file: `sound_method_SP-099_CFRS.md` (10,066 bytes)
- Report file: `report_SP-099.md` (this file)

## Candidate Code Tree

```
sound/
  synthesis/
    comb_resonance.py    <-- new module for SP-099
      CombFilterResonance class
        render_note()
        render_parallel_bank()
```

## Integration Points

| Integration | Description |
|---|---|
| `workflows.musicom_workflow.produce(method="SP-099")` | Renders MIDI → WAV via CFRS |
| `UnitMatrix` voice rows | Each voice = one CFRS instance or PCB group |
| `UnitMatrix` section columns | Section-level CFRS parameter defaults |
| Per-note SP-099 params | feedback, excitation, dispersion, noise_burst_ms, noise_filter_cutoff |
| SP-011 (Karplus-Strong) | CFRS noise burst + loop lowpass = KS; add-filter variant |
| SP-032 (FDN Reverb) | CFRS parallel comb bank + unitary feedback matrix = FDN |
| SP-052 (CORDIS-ANIMA) | CFRS is the delay-line core of mass-interaction networks |

*Appended 2026-09-29 by sound-production research cron job. Layer tag: absolute. Paradigm: Sound Production / Synthesis Engines. ID SP-099 confirmed free at append time. Next free SP ID: 100.*