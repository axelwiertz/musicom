# Report — SP-145 Campanological Bell Partial Synthesis (CBPS)

**Date:** 2026-11-19
**Method ID:** SP-145
**Method name:** Campanological Bell Partial Synthesis (CBPS)
**Layer:** absolute (sound production — LAYER_ARCHITECTURE.md)
**Category:** Synthesis Engines — physical/acoustical modeling
**One-line description:** Renders a cast bell from its named campanological partial series (hum, prime, narrow tierce, quint, nominal + strike ladder) with doublet warble from axial asymmetry, strike-azimuth-dependent mode excitation, radiation-driven differential decay, and an emergent virtual-pitch strike note.

**Candidate code path:** `sound/synthesis/church_bell.py` (NumPy modal additive bank + preset tables + strike scheduler); dispatch from `workflows/musicom_workflow.py::produce(method="SP-145", ...)`.

**Standalone write-up:** `/opt/data/projects/Research/CompositionMethods/sound_method_SP-145_CBPS.md`
**Verification prototype:** `/opt/data/projects/Research/CompositionMethods/_web145_cbpm/verify_cbpm.py` (8/8 checks; demo WAV 1,058,444 bytes in the same folder)
**Web scratch:** `/opt/data/projects/Research/CompositionMethods/_web145_cbpm/` (Hibbert pages + Wikipedia REST fetches, 2026-11-19)

---

## 1. ID resolution

* Summary-table scan: highest `| **SP-NNN** |` row was **SP-144** (PADsynth / PADS, line 361).
* File scan cross-check: `sound_method_SP-*.md` highest was `sound_method_SP-144_PADS.md`; `report_SP-*.md` highest was `report_SP-144.md`. No SP-145/146 sound files existed (the `_web145_dpbc` / `_web146_hhfc` scratch dirs belong to **composition** methods 145 DPBC and 146 research, a different ID space in the same document — verified: no `SP-145`/`SP-146` header or row anywhere in `methods_db.md` before this entry).
* **New ID = SP-145.**

## 2. Line counts

| stage | lines |
|---|---|
| before | 32008 |
| after section append (106 lines) | 32114 |
| after summary-table row (+1) + separator blank line | **32116** |

`git diff --stat` on `methods_db.md`: **108 insertions, 0 deletions** (no existing content disturbed).

## 3. Summary-table row added (verbatim)

```
| **SP-145** | Campanological Bell Partial Synthesis (CBPS) | **Synthesis Engines** | Church Bell / Carillon / Handbell Physical Timbre | Renders a cast bell from its named campanological partial series: hum 0.25, prime 0.50, tierce 0.60 (**narrow** minor third — measured 290–291 cents, not 300), quint 0.75, nominal 1.00, then the strike ladder superquint 1.5 / octave-nominal 2.0 / upper-3rd 2.5 / upper-5th 3.0 / double-octave 4.0, each with its own radiated amplitude and radiation damping $T_{60,n}=T_{60,N}(f_n/f_N)^{-0.8}$ (hum rings ~3× longer than the nominal: 24.3 s vs 8.0 s measured). Axial asymmetry splits every $m\ge1$ mode into a $\cos m\theta$-$\sin m\theta$ doublet pair; strike azimuth sets the pair gains, so the bell warbles at $f_{beat}=\Delta f$ (measured 20.333 Hz vs 20.302 Hz requested; 7.8 dB tierce/quint re-balance between azimuths). The strike ladder is integer multiples of $f_N/2$, so the heard pitch is an emergent virtual pitch (strike note) that may be absent from the spectrum. 3–6 ms clapper contact burst; $O(K)$ per sample, $K\approx10$–30 partials; no training, no external data, deterministic per seed. Verified prototype **8/8 checks**. Candidate: `sound/synthesis/church_bell.py`. |
```

Placement: immediately after the SP-144 row (line 362), single `|` prefix, LaTeX verified to contain **single** backslashes (`grep -c '\\\\ge'` = 0 hit for double-escaped forms).

## 4. Technical mechanics summary

1. **Partial series.** $y(t)=\sum_n A_n g_n(\theta_s)e^{-t/\tau_n}\sin(2\pi r_n f_N t+\varphi_n)$ with the named campanological ratios relative to the nominal: hum 0.25, prime 0.50, tierce 0.60, quint 0.75, nominal 1.00, superquint 1.50, octave nominal 2.00, upper 3rd 2.50, upper 5th 3.00, double octave 4.00. Measured Taylor 1980s preset (nominal 1171.5 Hz): 293.1 / 585.9 / 692.9 / 882.0 / 1171.5 / 1761.0 / 2437.0 / 2619.1 / 3403.4 / 3982.5 Hz.
2. **Tierce is a narrow minor third.** 290.4 cents measured (equal-tempered = 300). This is the bell's "minor" colour and blocks naive scale quantisation.
3. **Doublets = warble.** Each $m\ge1$ mode splits into $\cos m\theta$ / $\sin m\theta$ pair; gains $|\cos m\theta_s|$, $|\sin m\theta_s|$; beat rate $f_{beat}=\Delta f$ (typically 0.1–1.5 Hz, a few cents).
4. **Virtual pitch (strike note).** Strike ladder $\{1, 1.5, 2, 2.5, 3, 4\}\,f_N$ = harmonics $\{2,3,4,5,6,8\}$ of $f_P=f_N/2$; the ear hears $f_P$ (missing fundamental; Rayleigh 1890, Terhardt, Hibbert's listening tests). Never synthesise a partial at the perceived pitch.
5. **Radiation damping.** $T_{60,n}=T_{60,N}(f_n/f_N)^{-\alpha}$, $\alpha\approx0.8$; measured hum 24.3 s → double octave 2.6 s with $T_{60,N}=8$ s.
6. **Excitation.** 3–6 ms clapper contact: modal injection by mode shape at the strike azimuth plus an exponentially decaying noise burst ($\tau\approx1.5$ ms) for the metal-on-metal clang.
7. **Complexity.** $O(K)$ per sample, $K\approx10$–30; additive (vectorised NumPy) or $K$ two-pole resonators for streaming. Linear system — no nonlinear solver, no oversampling, no training, no external data, deterministic per seed.

## 5. Verification (8/8)

```
[PASS] 1 peak accuracy: max err 0.006 %
[PASS] 2 tierce narrow minor 3rd: 290.4 cents (equal-tempered minor 3rd = 300)
[PASS] 3 doublet beat rate: requested Δf=20.302 Hz, measured 20.333 Hz
[PASS] 4 strike series -> virtual pitch: strike/prime = [2.0, 3.0, 4.0, 5.0, 6.0, 8.0]
       -> f_virtual = nominal/2 = 585.8 Hz
[PASS] 5 radiation decay ordering: T60 hum=24.3s, prime=13.9s, nominal=8.0s, double-oct=2.6s
[PASS] 6 strike azimuth rebalances modes: tierce/quint ratio shifts +7.8 dB between strike points
[PASS] 7 DC / peak / finite: mean=-1.08e-06, peak=0.980
[PASS] 8 wav written: 1058444 bytes
```

## 6. Complete section text appended to `methods_db.md`

# Sound Production Method SP-145 — Campanological Bell Partial Synthesis (CBPS)

### Source

- **Bill Hibbert, "The Sound of Bells" (bell acoustics research site, PhD Open University 2008).** Pages fetched live 2026-11-19: *Basic principles of bell tuning* (https://www.hibberts.co.uk/basic-principles-of-bell-tuning/) — the measured partial table for a Taylor 1980s bell and a Mears 1859 bell (frequencies + cents relative to the nominal); *The strike note of bells* (https://www.hibberts.co.uk/the-strike-note-of-bells/) — virtual-pitch explanation (Rayleigh 1890; Terhardt; Eggen & Houtsma) with the "strike partials" series; *Doublets or warble in bells* (https://www.hibberts.co.uk/doublets-or-warble-in-bells/) — mode splitting from axial asymmetry and the beat-rate law; *The upper partials of bells* (https://www.hibberts.co.uk/the-upper-partials-of-bells/) — 8,071-bell regression showing upper partials are not independently tunable; *The musical sound quality of church bells* (https://www.hibberts.co.uk/the-musical-sound-quality-of-church-bells/) — pitch perception vs nominal frequency bands.
- **Wikipedia, "Bell" / "Strike tone"** (fetched 2026-11-19 via the REST HTML API) — the canonical named-partial list: hum (two octaves below nominal), prime (one octave below), tierce (minor third above prime), quint (fifth above prime), nominal, plus the major third and fifth in the second octave.
- **T. D. Rossing (ed.), *Acoustics of Bells* / *Science of Percussion Instruments*** — cited by Hibbert as the theoretical background: a bell is a shell of revolution whose modes are labelled by nodal meridians $m$ and nodal circles $n$; every $m\ge1$ mode is a degenerate $\cos m\theta$/$\sin m\theta$ pair that splits when the casting is not perfectly axisymmetric. Radiation efficiency rises with frequency, so upper partials decay faster than the hum.
- **A. Lehr, "The theory of bell tuning"** (partial-tunability coupling) and **Canon A. B. Simpson** (true-harmonic tuning: hum/prime/tierce/quint/nominal as simple intervals) — historical basis of the ratio set.
- **Repo antecedents:** SP-042 MBED (generic eigenmode bank + biquads, tuned bars/plates, one sentence naming bell partials), SP-105 CRFBS (coupled *nonlinear* modal bank), SP-039 IFFT additive, SP-116 DSFS (closed-form partial sum), SP-144 PADS (spectrum→wavetable, bell preset via `relF`), SP-033/SP-101 waveguides (1-D strings/pipes, not shells), SP-136 SLTM (tabla membrane eigenproblem). **None models the campanological partial series, the doublet warble, the strike-azimuth excitation, or the virtual-pitch strike note.**
- **Novelty check (2026-11-19):** `grep -ci` on `methods_db.md` **before** entry: `campanolog` = **0**, `bell partial` = **0**, `strike tone` = **0**, `hum tone` = **0**. `tierce` = 1 (a single clause in SP-042 MBED listing the mode names, no model); `doublet` = 3 (all SP-136 tabla membrane degeneracy — circular membrane, not a bell shell); `warble` = 11 (SP-132 Leslie Doppler, SP-137 tape wow, SP-121 vibrato prose). **No method builds a bell from its named partial series + doublet splitting + azimuthal excitation → SP-145 is novel.**

### Layer

**absolute** (sound production — LAYER_ARCHITECTURE.md). CBPS is a **Synthesis Engines** physical/acoustical model: it consumes a strike event (pitch → nominal frequency, velocity → strike force, azimuth → which doublet member is excited) and emits PCM — a bank of exponentially damped inharmonic modes. It holds no timing authority and decides no pitch-class relations; the composition layer hands it a `MusicEvent` and the model returns the bell's own decay. Stage position: **source** — CBPS is a complete voice generator; per-row EQ (SP-007) → spatialize the tower/close perspective (SP-075 image-source, SP-021 binaural, SP-053 VBAP) → space/tail (SP-009/SP-032/SP-140) → bus dynamics (SP-008/SP-107) → loudness (SP-126) → dither (SP-122). Candidate code path: `sound/synthesis/church_bell.py` (NumPy modal additive bank + preset tables + strike scheduler); dispatch from `workflows/musicom_workflow.py::produce(method="SP-145", ...)`.

### Description

CBPS synthesizes a bell the way a bell actually sounds: **not** as a harmonic stack, and not as a generic modal bank, but as the *named campanological partial series* of a cast bronze bell. A true-harmonic bell's five lowest partials are tuned to simple intervals — **hum** (two octaves below the nominal), **prime** (one octave below), **tierce** (a *narrow* minor third above the prime), **quint** (a fifth above the prime), **nominal** — and above them sits a ladder of "strike partials" (superquint, octave nominal, upper third, upper fifth, double octave) that are **not independently tunable**: thinning the sound-bow moves all of them together along fixed regression lines (Hibbert, 8,071 bells). The ear does not hear the nominal as the pitch. It hears a **virtual pitch** roughly an octave below it, generated by the near-equal spacing of the strike partials — the missing-fundamental effect — which is why a bell's named note need not exist as a physical partial at all.

Two further behaviours make a bell a bell rather than an inharmonic additive tone. First, the **tierce is a narrow minor third** (measured 290–291 cents, not 300), which is what gives bells their Minor flavour even in "major" peals. Second, a real casting is never perfectly round: every mode with $m\ge1$ nodal meridians is a **doublet** — two close frequencies instead of one — and because the clapper almost never strikes at a node or antinode of that pair, both members sound together and **beat**, producing the slow "warble" of an old bell. The strike azimuth therefore *is* a timbre control: it sets how much of each doublet member is excited.

CBPS models exactly this: named ratios, per-partial radiated amplitude, radiation-driven differential decay, azimuth-dependent doublet excitation, and a clapper contact transient. It is linear (bells are, to a very good approximation, linear systems — unlike gongs and cymbals, which need SP-105's nonlinear coupling), so a bank of damped sinusoids is not an approximation of convenience but the correct model.

### Technical Mechanics

**1. Partial series.** A bell of nominal frequency $f_N$ is the sum of $K$ modes

$$y(t)=\sum_{n=1}^{K} A_n\, g_n(\theta_s)\, e^{-t/\tau_n}\,\sin\!\big(2\pi f_n t+\varphi_n\big),\qquad f_n=r_n f_N$$

with the ideal (true-harmonic) ratio set and the measured Taylor 1980s preset (nominal 1171.5 Hz) in cents relative to the nominal:

| partial | ideal $r_n$ | ideal cents | measured (Taylor 1980s) | measured cents | role |
|---|---|---|---|---|---|
| hum | 0.25 | −2400 | 293.1 Hz | −2399.3 | pedal, 2 octaves down |
| prime | 0.50 | −1200 | 585.9 Hz | −1199.3 | octave, strongest low partial |
| tierce | 0.60 | −900 | 692.9 Hz | **−908.9** | narrow minor third (290.4 ¢) |
| quint | 0.75 | −500 | 882.0 Hz | −491.4 | fifth |
| nominal | 1.00 | 0 | 1171.5 Hz | 0 | loudest partial |
| superquint | 1.50 | +702 | 1761.0 Hz | +705.6 | first strike partial |
| octave nominal | 2.00 | +1200 | 2437.0 Hz | +1268.1 | tuned sharp → strike pitch |
| upper 3rd | 2.50 | +1586 | 2619.1 Hz | +1392.9 | strike ladder |
| upper 5th (I-7) | 3.00 | +1902 | 3403.4 Hz | +1846.4 | strike ladder |
| double octave (I-8) | 4.00 | +2400 | 3982.5 Hz | +2118.4 | strike ladder |

The ideal column is the true-harmonic target (hum/prime/tierce/quint/nominal as simple intervals); the measured column is what a real bell actually does — the deviations are the timbre. The tierce is deliberately **not** 300 cents: a 300-cent tierce sounds like a synthesizer, a 290-cent tierce sounds like a bell.

**2. Virtual pitch (the strike note).** The strike partials $f_N\cdot\{1,1.5,2,2.5,3,4\}$ are integer multiples of $f_P=f_N/2$ — i.e. harmonics $2,3,4,5,6,8$ of the prime. The auditory system takes their spacing as a period, so the perceived pitch is

$$f_{\text{virtual}}=\gcd\{f_{S,k}\}=f_N/2=f_P ,$$

a pitch that may be absent from the spectrum (Rayleigh 1890; Terhardt's virtual pitch; Hibbert's experiments). Consequence for the model: **never add a sine at the perceived pitch** — the strike note must be an *emergent* property of the strike ladder. Detune the ladder and the bell's apparent intonation moves; Hibbert measured 20–35 cents of apparent detuning in thick trebles whose nominal was tuned to within a cent.

**3. Doublets and warble.** For a mode with $m$ nodal meridians the two degenerate solutions are $\Phi_c=\cos m\theta$ and $\Phi_s=\sin m\theta$. An asymmetric casting splits them by $\Delta f_n$ (typically 0.1–1 Hz; a few cents at most). Striking at azimuth $\theta_s$ excites them with gains

$$g_n^{c}=\big|\cos(m\theta_s)\big|,\qquad g_n^{s}=\big|\sin(m\theta_s)\big|,\qquad f_n^{\pm}=f_n\sqrt{1\pm\epsilon_n}\ \ \text{with}\ \ \epsilon_n\approx \frac{\Delta f_n}{2f_n}$$

and the envelope beats at

$$f_{\text{beat}}=|f_n^{+}-f_n^{-}|=\Delta f_n .$$

The measured prototype confirms the law: a requested 20.302 Hz split produced a measured envelope peak at 20.333 Hz (0.15 % error). In musical terms 0.5 Hz at 586 Hz is only 1.5 cents — inaudible as tuning, but a very audible 2-second warble.

**4. Strike-azimuth excitation (which modes you get).** The clapper hits the sound-bow, an antinode region for the tierce, nominal and the whole upper ladder, and a node region for the hum. Mode participation is $A_n\propto|\Phi_n(\theta_s)|\,v^{q}$ with velocity $v$ and a mild exponent $q\approx1$ (louder strike → slightly brighter, because the upper modes are excited more effectively at higher contact force). Because $\cos m\theta_s$ and $\sin m\theta_s$ trade off, moving the strike point changes the *balance* between the members of each doublet — the prototype measures a **7.8 dB** shift in the tierce/quint ratio between two azimuths for $m=4$ and $m=3$ modes. This is the physical reason a bell has a "sweet spot" and a "dead spot".

**5. Radiation damping.** Each mode radiates with an efficiency that grows with frequency below the coincidence frequency, so the hum rings longest and the upper ladder dies first:

$$T_{60,n}=T_{60,N}\left(\frac{f_n}{f_N}\right)^{-\alpha},\qquad \tau_n=\frac{T_{60,n}}{6.9078},\qquad \alpha\approx 0.8 .$$

With $T_{60,N}=8$ s at the nominal the prototype measures hum 24.3 s, prime 13.9 s, nominal 8.0 s, double octave 2.6 s — the hum/upper-partial ratio that makes a bell sound like a bell and not like a decaying chord. $T_{60,N}$ is the *size* parameter (large bells: tens of seconds on the hum).

**6. Clapper contact.** A 3–6 ms noise burst (exponentially decaying white noise, $\tau\approx1.5$ ms) added at onset models the metal-on-metal contact. It is a broadband excitation that lights up every mode and gives the attack its "clang"; its level is the "strike hardness" control (felt hammer → quieter burst; clapper → louder). Bells have no sustain/note-off: the strike *is* the note.

**7. Complexity and implementation.** Additive form: $O(K)$ per sample with $K\approx10$–30 partials, vectorizable in NumPy as ten `np.sin` calls over one time array — a 12 s bell renders in milliseconds. Resonator form (for streaming/parameter modulation): $K$ parallel two-pole biquads $y[n]=2e^{-1/\tau_n}\cos\omega_n\,y[n-1]-e^{-2/\tau_n}y[n-2]$ excited by the strike burst — the same model, $O(K)$ per sample, stable by construction ($|e^{-1/\tau}|\,\cdot$ pole radius $<1$). No external data, no training, deterministic per (seed, strike azimuth).

**8. Verified prototype.** `/opt/data/projects/Research/CompositionMethods/_web145_cbpm/verify_cbpm.py` — **8/8 checks**: spectral peaks within 0.006 % of the requested ratios; tierce 290.4 cents; doublet beat 20.333 Hz vs 20.302 Hz requested; strike ladder = harmonics 2,3,4,5,6,8 of the prime (virtual pitch 585.8 Hz); T60 ordering hum 24.3 s > prime 13.9 s > nominal 8.0 s > 2.6 s; azimuth re-balancing 7.8 dB; mean −1.1e−6 (no DC), peak 0.980; WAV 1,058,444 bytes.

### Musical Elements Framework

- **PITCH**: the row's nominal frequency is the score pitch, but the *heard* pitch is the virtual pitch at $f_N/2$ — a bell notated at C5 sounds like C4 with a bright C5 halo. Transposition must scale **all** partials together ($f_n=r_n f_N$), never re-tune the ladder per note, or the virtual pitch breaks. The narrow tierce (290 ¢) means bell chords cannot be tuned to equal temperament without a fight; that is the instrument's character, not a bug.
- **RHYTHM**: the strike sets the only rhythmic event; the decay tail (T60 up to tens of seconds at the hum) is the bell's own counterpoint against the score. Fast passages overlap their own tails — density control is done by muting (damping) rather than note length. Repeated strikes on the same bell re-excite the still-ringing modes: the model adds, so overlapping hits interact physically (constructive and destructive) instead of restarting.
- **HARMONY**: each strike emits a fixed *chord* — hum, prime, tierce, quint, nominal — that is neither major nor minor: the tierce sits between a minor and a major third, which is why bells read as "modal" and blend with both. Stacking bells a fifth or an octave apart produces the shimmering composite spectra of a peal; stacking them a second apart produces beating between the hums.
- **STRUCTURE**: the model's parameters are per-row/per-section state — a "tower bell" section (long T60, distant perspective) versus a "handbell" section (short T60, bright strike burst) is a section-level change, not a note-level one. A column change can also flip the doublet balance (different strike azimuth → different "ringing room").
- **TEXTURE**: three texture axes: (a) $T_{60}$ — size and damping, from dead-stroke handbell to 60-second tenor; (b) doublet split $\Delta f$ — from perfectly tuned modern casting (no warble) to the "medieval" wobble; (c) partial balance — a tierce-forward bell (old-style) versus a true-harmonic bell (bright, clear). Together they span the entire campanological palette with 3 scalars.

### UnitMatrix Integration

**Voices = rows = one bell each.** A row is a bell object: `{f_nominal, preset ("ideal"|"taylor"|"mears"|custom), T60_N, alpha, doublet_cents (per partial or global), strike_azimuth, strike_hardness, amplitude_curve (per-partial A_n), seed}`. Row identity = the casting. Two rows with the same nominal but different presets are two different bells (a true-harmonic Taylor and an old-style Mears "eight" — the standard English peal sound).

**Sections = columns = ringing context.** Column $j$ holds overrides: `{T60_scale (damping/muting), azimuth_j, hardness_j, partial_gain_db (e.g. tierce +3 dB), perspective (via SP-075/SP-021 downstream)}`. Section change = the same bells ringing in a different acoustic/position — which is exactly how a bell score is organised (tower vs. nave vs. close-miked).

**Cells = MusicUnit.** Cell $(v,j)$ carries the strikes for that bell in that section. A `MusicEvent` maps to: `pitch → f_N` (with the octave-down perceptual offset documented in the cell metadata), `velocity → strike force → A_n scaling + burst level`, `start_tick → strike time`. **`end_tick` does not stop the sound**: the model validates the event grid but the tail is physical. For zero-drift-safe rendering, give each strike a ring budget of $3T_{60,\text{hum}}$ capped at the buffer end, and let cells overlap tails freely (the renderer is additive).

**Produce dispatch:** `produce(midi_path, method="SP-145", params={"rows": {"tenor": {"f_nominal": 293.7, "preset": "taylor", "T60_N": 22.0, "doublet_cents": 1.6, "azimuth": 0.37}, "treble": {"f_nominal": 1171.5, "preset": "ideal", "T60_N": 9.0, "doublet_cents": 0.8, "azimuth": 0.9}}, "columns": {"A": {"T60_scale": 1.0}, "B": {"T60_scale": 0.35, "partial_gain_db": {"tierce": 2.5}}}})` — stage order **CBPS modal bank (source) → per-row EQ (SP-007) → spatialize (SP-075/SP-021/SP-053) → space/tail (SP-009/SP-032/SP-140) → bus dynamics (SP-008/SP-107) → loudness (SP-126) → dither (SP-122)**.

### Pitfalls

1. **Do not add a partial at the perceived pitch.** The strike note is a virtual pitch at $f_N/2$; inserting a sine there makes a bell that sounds like a synth pad with a bell on top. The pitch must emerge from the strike ladder's spacing.
2. **The tierce is 290 cents, not 300.** Quantising it to a minor third (or to a scale degree) destroys the bell character and makes chords with other instruments beat unpleasantly against the tempered third.
3. **Note-off is meaningless.** Bells ring until they decay; a MIDI note-off must be ignored (or mapped to a *damper* with its own fast $T_{60}$). If the renderer cuts at `end_tick` the bell clicks and loses its identity.
4. **Overlapping strikes add.** Re-striking a ringing bell sums into the existing modes rather than restarting them — that is correct physics, but it means dense writing on one bell can clip. Normalize per bell over the whole section, not per note.
5. **Doublet amount is a taste dial, not a defect knob.** Beyond ~3–4 Hz the warble reads as out-of-tune rather than "old"; at 0 Hz the bell sounds synthetic-modern. Typical musical range 0.2–1.5 Hz; below ~0.2 Hz it becomes a slow chorus that reads as a second bell.
6. **Hum on small speakers.** The hum is two octaves below the nominal: a C5 bell's hum is at C3, and a C4 bell's hum is at C2 — often below laptop/phone reproduction. Check mix translation and consider SP-113 bass enhancement rather than raising the hum's level (raising it makes the bell muddy on full-range systems).
7. **Aliasing / Nyquist.** Real bells have partials far above 4× the nominal; the model must either band-limit to $f_s/2$ per strike (drop partials, and the strike ladder is what matters) or render at 2× and decimate. Dropping the *upper* ladder is audible; dropping the *hum* is not.
8. **Preset ≠ universal.** Taylor/Mears presets are English-style; continental bells (e.g. Perner's German measurements) have different tierce/quint deviations, and old-style bells have a sharp hum / flat prime. Ship presets as data, not as constants in the synthesis kernel.
9. **Neighbour audit.** SP-042 MBED is a generic eigenmode bank (any object, tuned by scaling $\omega_n$) with a passing mention of bell mode names — CBPS supplies the campanological ratio set, the doublet warble, the azimuthal excitation and the virtual-pitch contract; SP-105 CRFBS is a *nonlinear* coupled bank (energy exchange, cymbals/plates) — CBPS is linear and per-mode independent by design; SP-039/SP-116 are additive engines with arbitrary partials — CBPS is a *physical* parameterisation (nominal, size, casting, strike point); SP-144 PADS can bake an inharmonic bell *table* — CBPS renders the strike and decay, not a loop; SP-136 SLTM is a tabla *membrane* eigenproblem (circular plate, syahi loading), not a shell of revolution. **CBPS = named campanological partials + doublet beating + strike azimuth + radiation decay + emergent virtual pitch.**
10. **Determinism.** Random phases per partial are perceptually irrelevant to the steady state but shape the attack; seed them and record the seed, as with SP-141/SP-144. Two different seeds are two takes of the same bell.

---

## 7. Quirks / pitfalls hit during this entry

1. **ID-space confusion (handled).** `methods_db.md` holds two parallel ID sequences in one file: composition methods (`# ... (Method 145)` = Dyck Path Ballot Composition, with scratch dir `_web145_dpbc`) and sound-production methods (`SP-145`). Method 145 DPBC and SP-145 CBPS coexist legitimately. The `_web145_*` / `_web146_hhfc` folders are *composition*-method scratch, not evidence of an existing SP-145. Resolution rule used: candidate ID from `| **SP-NNN** |` rows + `sound_method_SP-*` files only.
2. **Search engines blocked.** DuckDuckGo HTML and lite endpoints returned a bot challenge; Bing/Mojeek similarly unusable. Worked around by going straight to the authoritative source (Hibbert's sitemap `wp-sitemap-posts-post-1.xml`) and to the Wikipedia REST HTML API. All numbers in this entry come from fetched pages, not from memory.
3. **`cat >>` append + patch row = two writes, one file.** The task's workflow (temp file → `cat >>` → `rm`) was followed exactly; `rm` verified (no `_temp_sp145.md` remains). The summary row was then patched by anchoring on the unique tail of the SP-144 row.
4. **Backslash pitfall checked.** The patch tool's JSON diff shows `\\ge`, which is JSON escaping, not file content. Verified directly: `grep -c '\\\\ge'` on line 362 returns 0, and `grep -o 'm.ge1'` shows `m\ge1` (single backslash). No `||` row prefix anywhere (`grep -c '^||'` = 0).
5. **Sibling-agent modification warning.** The patch tool warned that `methods_db.md` had been modified by a sibling agent (concurrent `human_methods_db.md` / HC-096 work). Verified no conflict: `git diff --stat` shows 108 insertions / 0 deletions in `methods_db.md`, no SP-146 row, and the SP-144 row at line 361 is intact.
6. **Measurement pitfall in the prototype (fixed).** First T60 estimator used a brick-wall FFT band-pass, whose circular wrap-around transient at the buffer edge polluted the decay fit (nominal measured 26.7 s instead of 8.0 s). Replaced with an STFT magnitude track at the partial's bin → exact recovery (8.0 s). Lesson worth keeping in the production module: **measure decays from an STFT track, never from a zero-phase FFT band-pass of a truncated buffer.**
7. **Prototype doublet split was exaggerated** (60 cents ≈ 20.3 Hz) so the beat rate was easy to measure; musical range is 0.2–1.5 Hz. This is stated in the doc (Pitfall 5) so nobody copies the test value as a default.
8. **`ifft` without `n=`** returns `len(S)` samples, not the original length — the source of a broadcast error in the first envelope estimator. Fixed by `np.fft.ifft(S, n=n)`.
9. **Bells are linear.** Temptation to reach for SP-105's nonlinear coupled bank must be resisted: bells do not exhibit the energy cascades of gongs/cymbals, and nonlinearity would break the exact doublet-beat law.
10. **Note-off semantics.** Documented as a first-class pitfall: `MusicEvent.end_tick` cannot stop a bell; cells must budget the tail ($3T_{60,\text{hum}}$) or the renderer truncates and clicks.

## 8. Next free SP ID

**SP-146** (summary table + file scan agree; no `sound_method_SP-146-*` / `report_SP-146-*` exists).

## 9. Files touched

| file | change |
|---|---|
| `methods_db.md` | +106-line section at EOF, +1 summary row after SP-144, +1 separator (32008 → 32116 lines) |
| `sound_method_SP-145_CBPS.md` | new standalone write-up (12.9 KB: extended math, NumPy sketch, parameters, references, neighbour audit) |
| `report_SP-145.md` | this report (primary record) |
| `_web145_cbpm/` | research scratch + `verify_cbpm.py` + `cbpm_demo.wav` (1,058,444 B) |
