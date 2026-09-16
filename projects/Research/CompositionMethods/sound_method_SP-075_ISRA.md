# Sound Production Method SP-075 — Image-Source Room Acoustics Synthesis (ISRA)

**Layer:** absolute (sound production — Post-Processing / DSP)
**Category:** Post-Processing / DSP | **Target Output:** Physically Simulated Room Impulse Response / Geometric Spatialization

### One-line description

Renders acoustic spaces — not just sounds in them — by mirroring every sound source
geometrically across the walls, floor, and ceiling of a shoebox room: each mirror
image is a legitimate echo path, so a room impulse response (RIR) with correct early
reflections, flutter echoes, and a physically ordered reverberant tail is generated
analytically from nothing but room dimensions, wall absorption, and the speed of sound
(Allen & Berkley 1979).

### Layer classification

Per `LAYER_ARCHITECTURE.md`, every SP-* method is **absolute** (sound production:
audio stems → WAV/OGG). ISRA is an *absolute*-layer method in the Post-Processing / DSP
class: it consumes rendered per-voice stems (or the summed mix) and produces roomed
audio. Candidate code path: `sound/effects/image_source_room.py` — sibling of
`sound/effects/room_reverb.py` (SP-009 convolutive / SP-032 FDN / SP-058 spring /
SP-071 Dattorro plate). Plugs into `workflows.musicom_workflow.produce(method="SP-075")`
as a post-render spatialization pass.

### Source

Allen, J. B., & Berkley, D. A. (1979). "Image method for efficiently simulating
small-room acoustics." *JASA* 66(4), 943–950. Extended to arbitrary polyhedra by
Borish (1984); production-grade reference implementation: **pyroomacoustics**
(Scheibler, Bezzam & Dokmanić, ICASSP 2018), whose docs state it provides a "Fast C++
implementation of the image source model and ray tracing for general polyhedral rooms
to efficiently generate room impulse responses" (verified from pyroomacoustics
readthedocs, 2026-09-16). Precise shoebox image-source construction verified against
pyroomacoustics source (`room.cpp`, `image_source_shoebox`): image positions
$\mathrm{loc}[d] = q_d L_d + \mathrm{step}_d$ with
$\mathrm{step}_d = s_d$ for even $|q_d|$ and $L_d - s_d$ for odd $|q_d|$; per-axis
attenuation $= \beta_{\text{west}}^{p_1}\beta_{\text{east}}^{p_2}$ with
$(p_1, p_2) = (q/2, (q+1)/2)$ for $q>0$ and $(|(q{-}1)/2|, |q/2|)$ for $q<0$; total
order $= \sum_d |q_d|$; the image lattice is the **L1 ball** of radius $R$
($\sum_d|q_d| \le R$), not the naive cube.

### Description

The image-source method (ISM) computes a room impulse response in closed form by
exploiting specular reflection: every sound path that bounces off $k$ flat walls is
equivalent to a *straight* path from a mirror image of the source reflected across
those walls. Unroll all bounces → tile space with mirrored rooms → each image source
at distance $d_q$ from the receiver contributes one impulse delayed by $d_q/c$ and
attenuated by $1/d_q$ (spherical spreading) times the product of the reflection
coefficients of the walls it crossed. Summing all images up to reflection order $R$
yields the exact early-reflection structure of the room (including flutter echoes
between parallel walls and the discrete-to-diffuse transition); convolving any dry
signal with this RIR places it physically in the room. Unlike sampled/IR reverb
(SP-009) the room is parametric — dimensions, absorption, source and receiver
positions are all continuous control knobs, and unlike FDN/plate/spring algorithms
(SP-032/071/058) the early reflections are *physically correct* rather than
statistically plausible.

### Technical Mechanics

#### 1. The image lattice (shoebox room)

Room $[0,L_x]\times[0,L_y]\times[0,L_z]$, source $\mathbf{s}$, receiver
$\mathbf{r}$, wall reflection coefficients $\beta_{x_1},\beta_{x_2},\beta_{y_1},
\beta_{y_2},\beta_{z_1},\beta_{z_2}\in[0,1)$ ($\beta=\sqrt{1-\alpha}$ from absorption
$\alpha$). For every lattice point $\mathbf{q}=(q_x,q_y,q_z)\in\mathbb{Z}^3$ with
$|\mathbf{q}|_1 \le R$ the Allen–Berkley image position (per axis $d$):

$$
\mathrm{loc}_d = q_d L_d + \begin{cases} s_d & |q_d| \text{ even} \\ L_d - s_d & |q_d| \text{ odd}\end{cases}
$$

#### 2. Per-image attenuation (exact Allen–Berkley index form)

The number of bounces off each of the two walls normal to axis $d$ is
$(p_1,p_2) = (q_d/2,\ (q_d{+}1)/2)$ for $q_d>0$ and
$(|(q_d{-}1)/2|,\ |q_d|/2)$ for $q_d<0$ (0,0 for $q_d=0$). The image's broadband
gain:

$$
g_{\mathbf{q}} = \frac{\prod_{d}\ \beta_{d_1}^{\,p_1(d)}\ \beta_{d_2}^{\,p_2(d)}}{4\pi\, d_{\mathbf{q}}},
\qquad d_{\mathbf{q}} = \|\mathbf{r} - \mathbf{loc}(\mathbf{q})\|_2
$$

(the $1/4\pi d$ is the spherical-spreading term; $\beta=0$ = fully absorbing wall,
$\beta\to 1$ = hard concrete).

#### 3. The impulse response

$$
h(t) = \sum_{|\mathbf{q}|_1 \le R} g_{\mathbf{q}}\; \delta\!\left(t - \tfrac{d_{\mathbf{q}}}{c}\right)
$$

Fractional delays $d_{\mathbf{q}}/c \cdot f_s$ land between samples → Lagrange
fractional-delay interpolation (3rd/5th order) or a windowed-sinc kernel per image.

#### 4. Frequency-dependent walls (the modern necessity)

Scalar $\beta$ gives flat absorption → comb-colored RIRs. Per-band ISM (pyroomacoustics
`n_bands`): run the model with a $\beta$ vector per octave band and filter each image's
impulse with the band's fractionally-delayed, band-limited kernel — equivalently,
convolve each impulse with a minimum-phase lowpass whose gain is
$\prod_d \beta_{d,b}^{p(d)}$ in band $b$. High frequencies die on bounces; the tail
darkens naturally, exactly as in real rooms.

#### 5. Echo-density structure (why it sounds like a room)

Path-length statistics of the image lattice give the classic room-acoustics result:
echo density grows as $\frac{dE}{dt} \propto t^2$ (polynomial growth toward the
Schroeder frequency $f_S \approx 2000\sqrt{RT_{60}/V}$, above which the response is
statistically diffuse). The ISM reproduces the *early* part exactly and the diffuse
tail approximately (up to order $R$); Lehmann et al. (2010) give the closed-form
RT60/integration-time estimator used to bound $R$.

#### 6. Render chain

```text
dry stem per voice  ⊛  h_v(t)  →  roomed voice
sum over voices (± per-voice source position)  →  mix → limiter
RIR length: fs · (RT60 target) samples; order R chosen so β̄^(2R) < −60 dB
```

#### 7. NumPy implementation sketch

```python
import numpy as np
from scipy.signal import fftconvolve

def rir_shoebox(src, rec, room, beta, fs, c=343.0, order=5):
    """Allen-Berkley shoebox RIR. beta = (bx1,bx2,by1,by2,bz1,bz2)."""
    L = np.asarray(room, float); s = np.asarray(src, float); r = np.asarray(rec, float)
    n_max = int(fs * (np.linalg.norm(L) * (2 * order + 1)) / c) + 64
    h = np.zeros(n_max)
    B = np.asarray(beta, float)          # [x1, x2, y1, y2, z1, z2]
    for qx in range(-order, order + 1):
        for qy in range(-order, order + 1):
            for qz in range(-order, order + 1):
                if abs(qx) + abs(qy) + abs(qz) > order:   # L1 ball bound
                    continue
                q = (qx, qy, qz)
                loc = np.empty(3)
                for d in range(3):
                    loc[d] = q[d] * L[d] + (s[d] if abs(q[d]) % 2 == 0 else L[d] - s[d])
                dist = np.linalg.norm(r - loc)
                if dist < 1e-9:
                    continue
                # per-axis bounce counts (Allen-Berkley p1/p2)
                gain = 1.0
                for d, qd in enumerate(q):
                    if qd > 0:
                        p1, p2 = qd // 2, (qd + 1) // 2
                    elif qd < 0:
                        p1, p2 = abs((qd - 1) // 2), abs(qd // 2)
                    else:
                        p1, p2 = 0, 0
                    gain *= B[2 * d] ** p1 * B[2 * d + 1] ** p2
                gain /= (4 * np.pi * dist)
                tau = dist / c * fs                      # in samples (fractional)
                i0 = int(tau); frac = tau - i0
                if i0 + 1 < n_max:
                    h[i0]     += gain * (1 - frac)       # linear fractional delay;
                    h[i0 + 1] += gain * frac             # use Lagrange-3 in production
    return h

# usage: y = fftconvolve(dry_stem, rir_shoebox(...))[:len(dry_stem)+len(h)-1]
```

Production variant: per-band β (3–8 octave bands), Lagrange/sinc fractional delay,
visibility culling (images occluded by walls in polyhedral rooms — Borish), and
optional directional receiver (SP-021 HRTF convolution per image for binaural room
sim).

### Complexity

$\mathcal{O}((2R{+}1)^3)$ images with $\mathcal{O}(1)$ work each (R=8 → 4913 images,
sub-second in NumPy), plus one $\mathcal{O}(N\log N)$ FFT convolution per voice stem.
Deterministic per (geometry, β, fs) — no randomness unless scattering is added.

### Musical Elements Framework

| Element | Mapping |
|---|---|
| **PITCH** | Room axial/tangential modes $f_{lmn}=\tfrac{c}{2}\sqrt{(\ell/L_x)^2+(m/L_y)^2+(n/L_z)^2}$ color registers: small rooms boost 80–300 Hz (bathroom bloom), halls have sub-audible modes. Choosing $L$ per section aligns room modes with (or deliberately against) the section's tonal center — organ-builder practice. Direct-to-reverb ratio (DRR) is a register-independent distance cue. |
| **RHYTHM** | Early-reflection pattern (first 20–80 ms) is the room's rhythmic fingerprint: parallel walls → periodic flutter echo (a physical tremolo at $c/2L$), asymmetric rooms → scattered echoes. Pre-delay = $d_{1st}/c$; longer pre-delay perceptually detaches transients from the wash → tighter perceived groove at identical tempo. Echo density grows $\propto t^2$ from discrete to diffuse. |
| **HARMONY** | Frequency-dependent absorption = the room's spectral EQ: hard walls (β→1) keep triads bright and ringing; absorbent walls (studio, β≈0.5) dry harmonics down. Modal support in the bass can sympathetically reinforce the key's tonic register; overlapping sustained notes in a long-RT60 room smear into emergent harmony wash (the physical basis of cathedral-organ voicing). |
| **STRUCTURE** | Per-section room schedule = macro-form: close-mic intro → room verse → hall chorus → cathedral bridge/outro; continuous morph of $(L, \beta, \mathbf{r})$ across a section = walking-through-the-building form. DRR trajectory (near→far) is a narrative distance arc independent of dynamics. |
| **TEXTURE** | Echo density + decay time = perceived space size; β spectrum = warm/bright surface; flutter = rhythmic texture; the diffuse tail is a canonical continuous-fill layer for the Method Hybridization rule (sparse 011/032 rhythmic layers + ISRA room wash = flowing groove — the Disco v2→v3 fix). Per-voice source positions give geometric mixing (front row vs back row voices). |

### UnitMatrix Integration

- **Rows (Voices)** = each voice rendered to its own dry stem with its own source
  position $\mathbf{s}_v$ in the room → level/dryness differences emerge *geometrically*
  (close voice = loud+dry, far voice = soft+wet) without touching per-voice gains.
  A stereo pair of receivers per voice gives the full stereo room image.
- **Columns (Sections)** = `{STRUCTURE}` → per-section room preset: dimensions $L$,
  6-wall β (or per-band β vector), source/receiver geometry, pre-delay. A section-level
  "architecture plan" (the room schedule) is the spatial orchestration layer; morphing
  between presets = continuous section transitions.
- **Cells (MusicUnit)** = `{PITCH}` → optional per-cell source height/distance (register
  staging); `{RHYTHM}` → cell onsets trigger physically-generated echo patterns — no
  per-note delay programming, the room does it; `{HARMONY}` → room-mode alignment with
  the section's tonal center; `{TEXTURE}` → per-cell DRR via receiver distance and
  β-bandwidth choices.
- **Flow**: `compose` (UnitMatrix → MIDI) → dry render per voice (SP-001 FluidSynth /
  SP-011 KS / SP-029 subtractive / SP-074 piano) → `produce(method="SP-075",
  params={room, beta, positions, order})` → per-voice RIR + fftconvolve → sum →
  SP-008 limiter → WAV/OGG. Pairs: SP-009 (SP-075 *generates* what SP-009 *measures*;
  hybrid = ISRA early reflections + measured-IR tail), SP-032/071 (ISM early + FDN/plate
  diffuse tail — the standard hybrid), SP-058 (spring tank on top for vintage color),
  SP-021 (per-image HRTF = binaural room simulation), SP-034 (encode ISM images into
  HOA B-format for head-tracked immersive render), SP-053 VBAP (object placement in
  arrays vs ISRA room reconstruction — complementary spatialization philosophies).

### Pitfalls

1. **Scalar β = comb-filter coloration.** Flat absorption → all frequencies decay
   identically → metallic ringing RIR. Fix: per-band β (3–8 octave bands) with
   band-filtered images, or per-image one-pole lowpass whose cutoff falls with
   reflection order.
2. **Flutter echo between parallel walls.** Hard parallel walls produce periodic
   echoes at $2L/c$ — musically useful (slap) but can dominate. Fix: jitter high-order
   image positions ±1% or add a scattering coefficient (pyroomacoustics
   `shoebox_scattering`) that decorrelates high-order images.
3. **Truncated tail (too-low order R).** RIR ends mid-decay → gated sound. Fix: choose
   $R$ so $\bar\beta^{2R} < -60$ dB relative to direct path, or crossfade the ISM tail
   into an FDN (SP-032) — the standard hybrid RT60 completion.
4. **Fractional delay quantization.** Rounding $d/c$ to whole samples detunes the
   early reflections and brightens/hash-out the tail. Fix: Lagrange-3/5 or windowed-sinc
   fractional delay per image (same machinery as SP-074's dispersion allpass).
5. **$\mathcal{O}((2R{+}1)^3)$ cost explosion.** R=15 → 29,791 images. Fix: L1-ball
   bound (already $\sim6\times$ fewer than the cube for R=8), vectorized image-lattice
   construction in NumPy, and cap R by RT60 need (Lehmann 2010 estimator).
6. **Degenerate geometry.** Receiver coincident with an image (or outside the room) →
   zero/NaN distances and impulsive artifacts. Fix: clamp src/rec inside
   $[\epsilon, L-\epsilon]$; assert $d_{\mathbf{q}} > 0$; validate $\beta\in[0,1)$.
7. **β ≥ 1 instability.** $\beta\ge1$ means energy *gain* per bounce → exponentially
   exploding RIR. Hard-clamp β and assert.
8. **Direct-path dominance / dry confusion.** Receiver too close to the source → dry
   signal dominates, method indistinguishable from SP-009's tap line. Fix: place
   receiver beyond the critical distance $r_c \approx 0.057\sqrt{V/RT_{60}}$ or scale
   the direct image separately.
9. **Confusion with SP-009 (convolutive reverb).** SP-009 convolves with a *measured*
   IR — fixed real rooms, no parameters. ISRA *synthesizes* the IR from geometry:
   arbitrary/nonexistent rooms, per-section room morphing, per-voice positions. They
   compose: ISRA early reflections + measured tail.
10. **Convolution cost.** 5 s RIR × long stems → always `fftconvolve` (or partitioned
   convolution for streaming); time-domain convolution of long RIRs is prohibitively
   slow.
11. **Occlusion ignored in shoebox.** The classic Allen–Berkley shoobx model assumes
   all images visible (hard walls only). For partitions/furniture, use the
   visibility-culled polyhedral ISM (Borish) or hybrid ray-tracing
   (pyroomacoustics's hybrid ISM+rays) — otherwise reflections pass through walls.
   (Classic Allen–Berkley shoebox assumes all images visible; image positions remain
   well-defined for any (L, s) with 0 < s < L.)

### Comparison With Related Methods

- **SP-009 Convolutive Reverberation**: measured IR vs *parametric* IR. ISRA can
  reproduce SP-009's room *and* every room that doesn't exist.
- **SP-032 FDN / SP-071 Dattorro plate / SP-058 spring**: statistically diffuse tails,
  statistically tuned early reflections. ISRA is exact in the early field — the hybrid
  (ISM early + FDN tail) is industry practice (pyroomacoustics hybrid kernel).
- **SP-040 FDTD room acoustics**: wave-exact (diffraction, interference) at
  $\mathcal{O}(f_s^3)$-scale grid cost. ISM is ray/geometric approximation:
  $\mathcal{O}((2R{+}1)^3)$ once per geometry, exact specular reflections, no
  diffraction — the right tool below ~2–4 kHz for shoebox rooms.
- **SP-021 Binaural / SP-034 HOA / SP-053 VBAP**: spatialization *renderers* that
  assume a spatial model; ISRA is the *room generator* that can feed them (per-image
  HRTF or B-format encoding).
- **SP-050 Spectral Delay / SP-026 Phase vocoder**: signal-domain processors; ISRA
  operates at the geometry level, before any per-sample processing.

### References

- Allen, J. B., & Berkley, D. A. (1979). "Image method for efficiently simulating
  small-room acoustics." *JASA* 66(4), 943–950.
- Peterson, P. M. (1986). "Simulating the response of multiple microphones to a single
  acoustic source in a reverberant room." *JAES* 34(8), 603–612.
- Borish, J. (1984). "Extension of the image source model to arbitrary polyhedra."
  *JASA* 75(6), 1827–1836.
- Scheibler, R., Bezzam, E., & Dokmanić, I. (2018). "Pyroomacoustics: A Python package
  for audio room simulation and array processing algorithms." *Proc. IEEE ICASSP*.
- Kuttruff, H. (2016). *Room Acoustics* (6th ed.). Spon Press — geometrical room
  acoustics / image sources chapters.
- Savioja, L., & Svensson, U. P. (2015). "Overview of geometrical room acoustics
  modelling techniques." *JASA* 138(2), 708–730.
- Vorländer, M. (2007). *Auralization*. Springer — image-source modeling chapter.
- Lehmann, E. A., Johansson, A. M., & Nordholm, S. (2010). "Reverberation-time
  prediction method for room impulse responses simulated with the image-source model."
  *Applied Acoustics* 71(3), 244–249.
