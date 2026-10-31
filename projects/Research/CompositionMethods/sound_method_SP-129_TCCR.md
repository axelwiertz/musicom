# Sound Production Method SP-129 — Transaural Crosstalk-Cancelled Binaural Rendering (TCCR)

**ID:** SP-129
**Layer:** absolute (sound production — LAYER_ARCHITECTURE.md)
**Category:** Post-Processing / DSP (spatialization — 2-channel loudspeaker binaural rendering)
**Candidate code path:** `sound/effects/transaural.py`
**Dispatch:** `workflows/musicom_workflow.py::produce(method="SP-129", params={...})`
**Status:** documented + numerically verified 2026-10-31 (scripts:
`projects/Research/outputs/sp129_research/verify_sp129_tcc.py`,
`verify_sp129_tables.py`)

---

## 1. One-line definition

A binaural (ear-signal) bus is pre-distorted by the regularized inverse of the
2×2 speaker→ear acoustic plant so that, at a specific listening position, the
far-ear paths from the two loudspeakers cancel acoustically — reproducing
headphone-style 3-D imaging over an ordinary stereo pair, at the price of a
positional "sweet spot" that fails asymmetrically.

---

## 2. Why it exists (the gap it fills)

SP-021 in this DB produces binaural audio with a Woodworth–Schlosberg ITD/ILD
head model — i.e. **headphone** audio. Its own pitfall list in `methods_db.md`
already names the missing half: *"Binaural (SP-021) works only with headphones
(or requires crosstalk cancellation that is listener-position-dependent)."*
SP-129 is that crosstalk cancellation, specified.

Over loudspeakers the headphone assumption breaks: each ear receives **both**
channels. A binaural pair therefore arrives as a blurred, in-head image. The fix
is not panning (SP-053 VBAP) and not field synthesis (SP-043 WFS, SP-034 HOA) —
it is **inverting the acoustics at the ears**.

Nothing about the method is new physics (Atal & Schroeder, 1966); what is new in
this DB entry is the *engineering contract*: which numbers it actually achieves,
where it collapses, and how it attaches to the UnitMatrix pipeline.

---

## 3. Full mathematics

### 3.1 The plant

Speakers $s\in\{L,R\}$ at positions $\mathbf{p}_s$; ears $e\in\{L,R\}$ at
$\mathbf{p}_e$ (interaural axis perpendicular to the facing direction, $\pm a$,
head radius $a=0.0875$ m). Free-field, direct-path model:

$$r_{es}=\lVert\mathbf{p}_s-\mathbf{p}_e\rVert,\qquad
\tau_{es}=\frac{r_{es}}{c},\qquad
h_{es}(f)=\frac{A_{es}(f)}{r_{es}}\,e^{-j2\pi f\tau_{es}}$$

with a first-order contralateral head shadow

$$A_{es}(f)=\begin{cases}1, & e=s\\[2pt] \bigl(1+jf/f_c\bigr)^{-1}, & e\ne s\end{cases},
\qquad f_c\approx\frac{c}{2\pi a}\approx 624\ \text{Hz}\quad(a=8.75\ \text{cm})$$

(one-pole Brown–Duda style; a measured HRTF replaces $A_{es}$ with the actual
$\mathrm{HRTF}_{e,s}(f)$ and makes the model exact at the cost of a measurement).

The received ear signals are $\mathbf{E}(f)=\mathbf{H}(f)\mathbf{S}(f)$ with

$$\mathbf{H}(f)=\begin{bmatrix} h_{LL} & h_{LR}\\ h_{RL} & h_{RR}\end{bmatrix}.$$

For a midline listener and a symmetric pair, $h_{LL}=h_{RR}\equiv h_s$ and
$h_{LR}=h_{RL}\equiv h_o$, i.e. $\mathbf{H}$ is **complex symmetric**.

### 3.2 Exact inverse

Want $\mathbf{E}=\mathbf{B}$ (the binaural target, e.g. from SP-021), so
$\mathbf{S}=\mathbf{C}\mathbf{B}$, $\mathbf{C}=\mathbf{H}^{-1}$:

$$\mathbf{H}^{-1}=\frac{1}{h_s^2-h_o^2}\begin{bmatrix} h_s & -h_o\\ -h_o & h_s\end{bmatrix}.$$

Off-diagonal terms are the cancellation feeds: $L$'s speaker also emits
$-h_o/(h_s^2-h_o^2)$ of $R$'s signal. The denominator $h_s^2-h_o^2=(h_s-h_o)(h_s+h_o)$
is the whole design problem.

### 3.3 Shuffler (sum/difference) form — Cooper & Bauck 1989

Rotate the coordinates: $u=s_L+s_R$, $v=s_L-s_R$. Then

$$\mathbf{E}_u=(h_s+h_o)\,u,\qquad \mathbf{E}_v=(h_s-h_o)\,v,$$

because $\mathbf{H}$ becomes **diagonal** in this basis. The inverse is two scalar
filters:

$$C_{\text{sum}}=\frac{1}{h_s+h_o},\qquad C_{\text{diff}}=\frac{1}{h_s-h_o},$$

$$\mathbf{C}=\frac12\begin{bmatrix} C_{\text{sum}}+C_{\text{diff}} & C_{\text{sum}}-C_{\text{diff}}\\[2pt] C_{\text{sum}}-C_{\text{diff}} & C_{\text{sum}}+C_{\text{diff}}\end{bmatrix}.$$

This is not an approximation: measured against the matrix inverse it reproduces
the same filter to a **−292 dB** crosstalk residual (they differ only in the DC
bin). Architecturally it matters because **all robustness work localizes to one
filter** — $C_{\text{diff}}$ — and because $C_{\text{sum}}$ is always benign
($\lvert h_s+h_o\rvert$ never approaches zero when $h_s,h_o$ point the same way).

### 3.4 Regularized inverse (Kirkeby–Nelson)

$$\mathbf{C}(f)=\mathbf{H}^{H}\bigl(\mathbf{H}\mathbf{H}^{H}+\beta\mathbf{I}\bigr)^{-1}
=\bigl(\mathbf{H}^{H}\mathbf{H}+\beta\mathbf{I}\bigr)^{-1}\mathbf{H}^{H}$$

is the solution of $\min_{\mathbf{C}}\lVert\mathbf{H}\mathbf{C}-\mathbf{I}\rVert^2+\beta\lVert\mathbf{C}\rVert^2$.
$\beta$ is a Wiener-style noise-to-signal ratio: it caps the corrective gain where
$\mathbf{H}$ is ill-conditioned (low frequency, and the 1–2 kHz region where
$h_s-h_o$ passes through a null) at the cost of residual crosstalk there.

### 3.5 Time-domain (fast deconvolution) form

For a filter of length $N_f$ and target $\boldsymbol{\delta}$ (a unit impulse with
$N_{\text{pre}}$ samples of pre-delay):

$$\mathbf{c}=\bigl(\mathbf{H}^{\mathsf{T}}\mathbf{H}+\beta\mathbf{I}\bigr)^{-1}\mathbf{H}^{\mathsf{T}}\boldsymbol{\delta},$$

where $\mathbf{H}$ is the $(N_f+N_h-1)\times N_f$ convolution matrix of the modelled
responses. Solved by FFT (circular embedding of size $\ge 2N_f$) → 2–4 FFTs per
block. This is the form that also handles **per-ear measured HRTFs** and
**multi-position** targets (Hollebon et al. 2021: one target per seat, per-loudspeaker
regularization).

### 3.6 Bass management (band-limited TCC, Bai & Lee 2006)

Below the frequency where the head shadow vanishes, $h_o\to h_s$ and
$C_{\text{diff}}\to\infty$. Replace the raw difference filter by a gain-capped
version,

$$\tilde C_{\text{diff}}(f)=\begin{cases} C_{\text{diff}}(f), & \lvert C_{\text{diff}}\rvert\le G_{\max}\\ G_{\max}e^{j\angle C_{\text{diff}}}, & \text{otherwise}\end{cases}$$

which is exactly a frequency-dependent soft-knee limiter on the cancellation path.
Under the cap the difference channel is attenuated, so the band becomes
effectively mono — the honest trade, since a band that both ears hear identically
carries no localizable information anyway.

---

## 4. Measured performance (this machine, NumPy 1.26 / SciPy 1.17)

Test rig: $f_s=48$ kHz, $N=2^{17}$, speakers $\pm30°$ at 1.0 m, head radius
8.75 cm, one-pole 700 Hz shadow, 8-note harmonic test signal, virtual source at
$+30°$. Numbers are *model* results (a real room is worse — see Pitfall 3).

Path lengths: ipsilateral 1.0465 m, contralateral 0.9592 m → **ITD 0.254 ms**
(12.2 samples @48 kHz) — a fractional-delay problem, never an integer shift.

**Regularization sweep** (band 100 Hz–16 kHz, worst-case $|\mathbf{H}\mathbf{C}-\mathbf{I}|$):

| $\beta$ | max $\lvert C\rvert$ dB | crosstalk residual dB | total error dB |
|---|---|---|---|
| 0 | 18.58 | −260.0 | −126.0 |
| $10^{-8}$ | 18.58 | −117.1 | −125.9 |
| $10^{-6}$ | 18.58 | −77.1 | −103.1 |
| $10^{-4}$ | 18.35 | **−37.4** | −63.3 |
| $10^{-3}$ | 16.50 | −19.3 | −44.7 |
| $10^{-2}$ | 8.71 | −8.7 | −32.4 |
| $10^{-1}$ | −0.06 | −6.6 | −27.4 |

Exact inversion is numerically reachable ($-260$ dB): every audible failure is a
**model** failure, not a solver failure.

**Per-band suppression** ($\beta=10^{-3}$): 20–80 Hz −23.7, 80–200 Hz −19.7,
200–500 Hz −19.3, 0.5–1 kHz −37.8, 1–2 kHz −58.5, 2–4 kHz −63.3, 4–8 kHz −68.8,
8–16 kHz −74.3 dB.

**Conditioning** ($\beta=0$, raw inverse): $\lvert h_s\rvert/\lvert h_o\rvert$ at
20–80 Hz is within **0.7 dB**, so $\lvert h_s-h_o\rvert$ sits **21.8 dB** below
$\lvert h_s\rvert$ → $C_{\text{diff}}$ wants +21.8 dB. At 2–8 kHz the ratio is
20.4 dB, so $C_{\text{diff}}$ needs only +1.9 dB.

**Gain cap** (bass management): +18 dB cap → −11.9 dB residual in 20–200 Hz with
0.5–8 kHz untouched; +12 dB → −8.5 / −18.8 dB; +6 dB → −7.2 / −10.3 dB.

**Head pose** ($\beta=10^{-3}$, band 500 Hz–8 kHz):

| pose | suppression | total error |
|---|---|---|
| centred | −37.8 dB | −44.7 dB |
| lateral 2 cm | −31.8 dB | −26.6 dB |
| lateral 5 cm | −22.1 dB | −18.6 dB |
| yaw 2° | −35.1 dB | −38.5 dB |
| yaw 5° | −30.6 dB | −33.0 dB |
| yaw 10° | −24.4 dB | −27.8 dB |
| forward 2 cm | −7.9 dB | −32.7 dB |
| forward 5 cm | **+0.1 dB** | −25.3 dB |
| back 5 cm | **+0.4 dB** | −24.9 dB |

**Array mismatch**: filters designed for $\pm30°$ played over $\pm15°$ → −1.1 dB
(no cancellation); over $\pm45°$ → −2.5 dB.

**Mono fold-down**: hard-left virtual source loses 2.3 dB in mono; a centre
source loses 0.0 dB (its difference channel is idle, measured side energy
−283 dB relative).

### 4.1 The causal L-tap design: latency is the lever, not filter length

The exact inverse is non-causal — it is centred at $-$146 samples (the plant's
propagation delay). A causal, 8192-tap implementation therefore cancels only as
well as the inverse's tail fits inside the pre-delay. Measured (48 kHz, 0.5–8 kHz
suppression):

| total pre-delay | 3.0 ms | 5.5 ms | 8.0 ms | 11.0 ms | 13.7 ms | 21.0 ms |
|---|---|---|---|---|---|---|
| suppression | −10.2 dB | −27.9 dB | −47.5 dB | −47.5 dB | **−55.8 dB** | −61.3 dB |

Filter length is *not* the lever: at a fixed pre-delay, $L=2048$, $L=4096$ and
$L=8192$ measure the same (until the pre-delay exceeds the window, where $L=2048$
collapses). End-to-end closed loop with the 13.7 ms design (delay-aligned):
−41.6 dB error on a centre image, −35.5 dB on a hard-left target, recovered
inter-ear level ratio within 0.1 dB of the target. That is the real deployment
constraint: 8–14 ms of latency, which rules out monitor-path use.

---

## 5. NumPy implementation sketch

```python
import numpy as np
from numpy.fft import rfft, irfft, rfftfreq
from scipy.signal import fftconvolve

FS, C, A = 48000, 343.0, 0.0875           # head radius
FC = C / (2 * np.pi * A)                   # ~624 Hz shadow corner

def plant(n, span_deg=60.0, dist=1.0, fs=FS, shadow_hz=FC):
    """2x2 speaker->ear frequency responses. Rows = ears, cols = speakers."""
    f = rfftfreq(n, 1 / fs)
    th = np.deg2rad(span_deg / 2)
    spk = np.array([[dist*np.cos(th),  dist*np.sin(th)],      # L
                    [dist*np.cos(th), -dist*np.sin(th)]])     # R
    ears = np.array([[0.0, -A], [0.0, A]])                    # interaural axis = y
    w = 2j * np.pi * f
    H = np.zeros((2, 2, f.size), complex)
    for e in range(2):
        for s in range(2):
            r = np.linalg.norm(spk[s] - ears[e])
            h = np.exp(-w * r / C) / r
            if e != s:
                h /= (1 + w / (2 * np.pi * shadow_hz))        # head shadow
            H[e, s] = h
    return H, f

def invert(H, beta=1e-4):
    C_ = np.empty_like(H)
    for k in range(H.shape[2]):
        h = H[:, :, k]
        C_[:, :, k] = h.conj().T @ np.linalg.inv(h @ h.conj().T + beta * np.eye(2))
    return C_

def shuffler(H, gmax_db=18.0):
    """Cooper-Bauck form: two scalar filters, gain-capped difference."""
    hs, ho = H[0, 0], H[1, 0]
    cs, cd = 1 / (hs + ho), 1 / (hs - ho)
    lim = 10 ** (gmax_db / 20)
    over = np.abs(cd) > lim
    cd = np.where(over, lim * np.exp(1j * np.angle(cd)), cd)   # bass management
    C_ = np.empty_like(H)
    for k in range(H.shape[2]):
        C_[:, :, k] = 0.5 * np.array([[cs[k] + cd[k], cs[k] - cd[k]],
                                      [cs[k] - cd[k], cs[k] + cd[k]]])
    return C_

def design(latency_ms=13.7, L=8192, span_deg=60.0, dist=1.0, gmax_db=18.0):
    """Causal L-tap cancellation IRs (2,2,L). latency_ms = TOTAL pre-delay."""
    n = 4 * L
    H, f = plant(n, span_deg, dist)
    C_ = shuffler(H, gmax_db)
    C_ *= np.exp(-2j * np.pi * f * latency_ms * 1e-3)   # delay -> causal filter
    ir = irfft(C_, n, axis=-1)[..., :L]
    t, tail = np.arange(L), int(0.75 * L)               # taper the IR tail
    w = np.ones(L); w[tail:] = 0.5 * (1 + np.cos(np.pi * (t[tail:] - tail) / (L - tail)))
    return ir * w

def process(x, ir):
    """x: (2, N) binaural bus -> (2, N) speaker feed, delayed by latency_ms."""
    y = np.zeros_like(x)
    for o in range(2):
        for i in range(2):
            y[o] += fftconvolve(x[i], ir[o, i])[:x.shape[1]]
    return y
```

Notes on the sketch: (i) the loop over bins can be replaced by a closed-form
batched 2×2 inverse; (ii) `latency_ms` is the **total** pre-delay and it is the
real design parameter — see §4.1; (iii) `process` is applied to the **summed**
binaural bus, once — never per voice; (iv) `import fftconvolve` from
`scipy.signal` at the top of the file. The block was executed as written and
checked against the frequency-domain filter it was designed from (see §4.1 for
the resulting numbers).

---

## 6. UnitMatrix integration (summary)

| Matrix element | SP-129 role |
|---|---|
| **Rows = voices** | each row owns a static $(az, el, dist, width)$ seat; rows are placed by SP-021-style HRTF *before* the inverse |
| **Columns = sections** | each column is a *scene* (seat map + room assumption + bass band); scene changes are crossfaded ≥ 20–25 ms across the seam |
| **Cells = MusicUnit** | cells only produce the binaural bus; they carry **no** filters, because the inverse is source-independent (contrast SP-043 WFS, which is per-source-per-speaker) |
| **Cost** | one 2×2 (or 2 scalar) filter for the entire piece, regardless of voice count |

Stage order (authoritative): render → per-row HRTF/pan → sum → **SP-129** →
room (SP-009/SP-032) → dynamics (SP-008) → loudness (SP-126) → dither (SP-122).
TCC **before** reverb is not a preference; reflections re-inject the crosstalk the
filter removed.

---

## 7. References

1. Atal, B. S., Schroeder, M. R. (1966). "Apparent sound source translator." *JASA* **40**(4), 770–779.
2. Cooper, D. H., Bauck, J. L. (1989). "Prospects for transaural recording." *JAES* **37**(1/2), 3–19.
3. Bauck, J. L., Cooper, D. H. (1993). "Developments in transaural stereo." *Proc. IEEE ASSP Workshop Appl. Sig. Proc. Audio Acoust.*, 114–117. DOI 10.1109/aspaa.1993.379983.
4. Kirkeby, O., Orduna, F., Nelson, P. A. (1993). "Inverse filtering in sound reproduction." *Applied Signal Processing* **26**, 261–266.
5. Kirkeby, O., Nelson, P. A. (1999). "Digital filter design for inversion problems in sound reproduction." *J. Sound and Vibration* **223**(4), 583–605.
6. Bai, M. R., Lee, C.-C. (2006). "Development and implementation of cross-talk cancellation system in spatial audio reproduction based on subband filtering." *JSV* **290**, 1269–1289. DOI 10.1016/j.jsv.2005.05.016.
7. Bai, M. R., Lee, C.-C. (2007). "Subband approach to bandlimited cross-talk cancellation system in spatial sound reproduction." *EURASIP J. Audio, Speech, Music Proc.* **2007**, 071948. DOI 10.1155/2007/71948.
8. Ward, D. B., Elko, G. W. (1998). "Optimum loudspeaker spacing for robust crosstalk cancellation." *Proc. ICASSP*, 3541–3544. DOI 10.1109/icassp.1998.679636.
9. Ward, D. B., Elko, G. W. (1999). "Effect of loudspeaker position on the robustness of acoustic crosstalk cancellation." *IEEE SPL* **6**, 106–108. DOI 10.1109/97.755428.
10. Hollebon, J., Fazi, F. M., Simón Gálvez, M. (2021). "A multiple listener crosstalk cancellation system using loudspeaker-dependent regularization." *JAES* **69**, 191–203. DOI 10.17743/jaes.2020.0067.
11. Marchand, S., Meaux, T. (2021). "Synthetic transaural audio rendering (STAR): a perceptive 3D audio spatialization method." *JAES* **69**(7/8), 497–505. DOI 10.17743/jaes.2021.0015.
12. Marchand, S., Meaux, T. (2023). "STAR: extension to full 3D spatialization." *JAES*, 596–606. DOI 10.17743/jaes.2022.0098.
13. Vidal, A., Herzog, P., Lambourg, C. (2023). "Comparison of transaural configurations inside usual rooms." *JAES*, 202–215. DOI 10.17743/jaes.2022.0055.
14. Huang, X., Zhao, S., Li, J. (2026). "An optimal control point distribution method for two-channel crosstalk cancellation." *JASA*, 2539–2551. DOI 10.1121/10.0043134.

---

## 8. Adjacent DB methods (do not confuse)

| Existing | What it does | Why SP-129 is different |
|---|---|---|
| SP-021 binaural | ITD/ILD HRTF for **headphones** | headphones have no crosstalk to cancel; SP-129 assumes a two-speaker plant and an ear position |
| SP-053 VBAP | amplitude panning over an array | no ear model, no inversion; localizes by level |
| SP-043 WFS / SP-034 HOA | wavefield / spherical-harmonic reconstruction | physical field synthesis over many speakers; SP-129 is a 2-channel ear-level inverse |
| SP-075 image-source | room reflections | models the room, not the listener's head |
| SP-119 auto-pan | dynamic stereo movement | 1-D amplitude motion, no phantom-source correction |
| SP-009/032 reverb | space | must come **after** SP-129 |
