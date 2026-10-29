# SP-127 — STRAIGHT Pitch-Adaptive Spectral Resynthesis (PASR)

**Layer:** absolute (sound production — LAYER_ARCHITECTURE.md)
**Category:** Synthesis Engines — High-Fidelity Vocoder / Voice & Timbre Morphing Resynthesis
**Candidate code path:** `sound/synthesis/straight_vocoder.py` (`STRAIGHTAnalyzer`, `STRAIGHTSynthesizer`), consumed by `sound/render/pipeline.py` as a per-voice post-render stage.
**DB entry:** `/opt/data/projects/Research/CompositionMethods/methods_db.md` — summary row line 326, detailed section at line 28879.

---

## 1. What it is

STRAIGHT ("Speech Transformation and Representation using Adaptive Interpolation of weiGHTed spectrum", Kawahara 1999) is a high-fidelity analysis-synthesis vocoder. It decomposes a quasi-periodic signal into three **mutually independent** parameters:

| Parameter | Meaning | Musical knob |
|---|---|---|
| $F_0(t)$ | instantaneous-frequency-based fundamental | PITCH (independent of timbre) |
| $P(\omega,t)$ | pitch-ripple-free spectral envelope | TIMBRE BODY (independent of pitch) |
| $a(\omega,t)$ | per-band aperiodicity (periodic/noise ratio) | TEXTURE / breathiness / roughness |

Resynthesis = minimum-phase-filtered mixed excitation: a pitch-synchronous impulse train (periodic part) blended with white noise (aperiodic part) by $a(\omega,t)$, filtered by the minimum-phase impulse response of $P(\omega,t)$. Changing one parameter moves only that perceptual dimension — "perceptually isomorphic decomposition" (Kawahara 2006).

Contrast with DB neighbours: SP-026 phase vocoder (envelope is NOT pitch-adaptive; pitch shift moves spectral peaks), SP-028 LPC (all-pole only; no spectral zeros), SP-037 PSOLA (time-domain splicing; no spectral morphing), SP-046 channel vocoder (imposes a modulator envelope on a carrier; no source resynthesis), SP-108 MQ (sinusoidal tracks only; no aperiodicity component).

---

## 2. Analysis — extended math

**F0 via instantaneous frequency (IF).** STFT phase $\phi(\omega,t)=\arg X(\omega,t)$; the IF of bin $\omega$ is

$$\lambda(\omega,t) = \frac{\partial}{\partial t}\phi(\omega,t) \;\approx\; \frac{\phi(\omega,t+h)-\phi(\omega,t-h)}{2h}.$$

For a signal with fundamental $F_0$, the IF is nearly constant across the bandwidth of each harmonic (the "repetitive structure" property). The fundamental is read from the IF values inside the first-harmonic passband:

$$\hat{F}_0(t) = \mathrm{median}\big\{\lambda(\omega,t) : \omega \in [\tfrac12 F_0,\, \tfrac32 F_0]\big\},$$

which is octave-error-resistant and reverberation-robust (Kawahara, Estill & Fujimura 1998).

**Pitch-adaptive windowing.** Window length scales with the local period $T_0 = 1/\hat{F}_0$: $L_w \approx m T_0$ (STRAIGHT uses on the order of $m \approx 3$, Blackman-class). Short-time spectrum

$$X(\omega,t) = \int x(\tau)\, w_{T_0}(\tau-t)\, e^{-j\omega\tau}\, d\tau .$$

**TANDEM two-sample power spectrum (2008).** Two power spectra, one with window $w(t)$, one with the window advanced by half a period $w'(t) = w(t - T_0/2)$; their average

$$P_{\mathrm{TS}}(\omega,t) = \tfrac12\Big( |X_w(\omega,t)|^2 + |X_{w'}(\omega,t)|^2 \Big)$$

cancels the first-order pitch ripple for perfectly periodic signals (the TANDEM condition: complementary windows with $|W|^2 + |W'|^2 = \mathrm{const}$ over the analysis band). Residual ripple is removed by **F0-proportional smoothing**: a zero-phase lowpass along the log-frequency axis whose cutoff scales with $\hat{F}_0$ (the 1999 STRAIGHT smoothing). Result: an envelope $P(\omega,t)$ invariant under pitch changes — the defining property.

**Aperiodicity.** Reconstruct the periodic component $x_{\mathrm{per}}(t) = \sum_n A_n(t)\cos(2\pi n\hat{F}_0 t + \theta_n(t))$ with locally estimated amplitudes/phases; residual $r(t) = x(t) - x_{\mathrm{per}}(t)$. In band $b$ (log-spaced or ERB):

$$a_b(t) = \frac{E_b^{(\mathrm{aper})}}{E_b^{(\mathrm{per})} + E_b^{(\mathrm{aper})}}, \qquad E_b^{(\cdot)} = \int_{\omega \in b} |X_{(\cdot)}(\omega,t)|^2\, d\omega .$$

$a_b \to 0$: tonal; $a_b \to 1$: noisy.

---

## 3. Resynthesis — extended math

**Minimum-phase envelope.** From the power envelope:

$$H_{\mathrm{mp}}(\omega,t) = \exp\Big( \tfrac12 \ln P(\omega,t) + \tfrac{j}{2}\,\mathcal{H}\{\ln P(\cdot,t)\}(\omega) \Big),$$

where $\mathcal{H}$ is the Hilbert transform. Equivalently in the cepstral domain: real cepstrum $c(\tau) = \tfrac12\,\mathcal{F}^{-1}\{\ln P(\omega)\}$; keep the causal half $c_+(\tau)$ (double it, zero the anticausal part); $h_{\mathrm{mp}}(t) = \mathcal{F}^{-1}\{\exp(2\,c_+(\tau))\}$. Minimum phase concentrates energy at onset — the reason STRAIGHT output sounds "natural" rather than phasey.

**Mixed excitation.** Periodic excitation $e_p(t) = \sum_k \delta(t - kT_0)$ (phase-locked to the analysis grid); noise excitation $e_n(t) \sim \mathcal{N}(0,1)$ (seeded for reproducibility). The per-band aperiodicity shapes the excitation spectrum:

$$E(\omega,t) = \big(1 - a(\omega,t)\big)\, E_p(\omega,t) + a(\omega,t)\, E_n(\omega).$$

Frame output $Y(\omega,t) = E(\omega,t)\, H_{\mathrm{mp}}(\omega,t)$, overlap-added (hop 1–5 ms).

**The three independent knobs.**

| Operation | Math |
|---|---|
| Transpose (formant-preserving) | $\hat{F}_0(t) \leftarrow r\,\hat{F}_0(t)$; $P,\ a$ unchanged |
| Time-stretch | resample the parameter trajectories $P(\hat{t}), a(\hat{t})$; $\hat{F}_0$ unchanged |
| Timbre morph A→B | $\ln P_\alpha = (1-\alpha)\ln P_A + \alpha \ln P_B$; $a_\alpha = (1-\alpha)a_A + \alpha a_B$ |
| Texture (breathiness) | $a(\omega,t) \leftarrow \gamma\, a(\omega,t)$ (scale toward 1 = noisier) |

---

## 4. Python/NumPy implementation sketch

```python
import numpy as np
from scipy.signal import get_window, stft, istft
from scipy.fft import rfft, irfft

class STRAIGHTAnalyzer:
    """Analysis: {F0(t), P(omega,t), a(omega,t)} from a mono buffer."""

    def __init__(self, fs=44100.0, hop_ms=5.0, window_periods=3.0, n_fft=2048):
        self.fs = fs
        self.hop = int(fs * hop_ms / 1000.0)
        self.window_periods = window_periods
        self.n_fft = n_fft
        self._win_cache = {}          # per pitch-class window cache (Pitfall 6)

    def _pitch_window(self, t0):
        """Pitch-adaptive Blackman window, length ~ window_periods * T0, cached."""
        key = int(round(self.fs / t0))            # quantize to pitch class
        if key not in self._win_cache:
            L = int(self.window_periods * self.fs / t0)
            L = min(max(L, 64), self.n_fft)       # clamp
            self._win_cache[key] = get_window("blackman", L)
        return self._win_cache[key]

    def f0_if(self, x, t_center, win):
        """IF-based F0: phase-derivative median inside first-harmonic band."""
        # STFT slice at t_center; unwrap phase; dphi/dt; median over band
        ...

    def analyze(self, x):
        f0 = np.zeros(len(range(0, len(x), self.hop)))
        P  = np.zeros((self.n_fft // 2 + 1, f0.size))
        a  = np.zeros_like(P)
        for k, t in enumerate(range(0, len(x), self.hop)):
            w = self._pitch_window(f0_prev)          # needs F0; iterate 2x
            X = rfft(x[t:t + w.size] * w, self.n_fft)
            f0[k] = self.f0_if(x, t, w)
            # TANDEM: repeat with window advanced by T0/2, average powers
            # P[:,k] = 0.5*(|X_w|^2 + |X_w'|^2)  smoothed F0-proportionally
            # a[:,k] = residual-energy ratio per band
        return f0, P, a


class STRAIGHTSynthesizer:
    """Resynthesis: minimum-phase envelope * mixed excitation, overlap-add."""

    def min_phase(self, P_frame):
        logP = np.log(np.maximum(P_frame, 1e-12))
        c = irfft(logP)                              # real cepstrum
        c_plus = np.zeros_like(c); c_plus[0] = c[0]; c_plus[1:n_fft//2] = 2*c[1:n_fft//2]
        return irfft(np.exp(rfft(c_plus)))            # minimum-phase impulse response

    def synthesize(self, f0, P, a, seed=0, transpose=1.0, morph=None):
        rng = np.random.default_rng(seed)
        y = np.zeros(int(len(f0) * self.hop) + self.n_fft)
        for k in range(f0.size):
            T0 = self.fs / max(f0[k] * transpose, 1.0)
            h = self.min_phase(P[:, k])               # envelope FIR
            e_p = np.zeros(self.n_fft); e_p[::int(T0)] = 1.0      # impulse train
            e_n = rng.standard_normal(self.n_fft)     # seeded noise
            E = (1 - a[:, k]) * rfft(e_p) + a[:, k] * rfft(e_n)
            frame = irfft(E * rfft(h, self.n_fft), self.n_fft)
            y[k*self.hop : k*self.hop + self.n_fft] += frame    # overlap-add
        return y
```

Notes: `stft/istft` from SciPy give the vectorized frame machinery; the F0 estimate needs a 2-pass scheme (coarse F0 → pitch window → refine). The periodic reconstruction for $a$ is a per-band harmonic fit; for a production version use the residual after harmonic comb subtraction. Complexity: $O(N_{\mathrm{fft}} \log N_{\mathrm{fft}})$ per frame per voice — real-time for one voice at 5 ms hops in NumPy.

---

## 5. Musical Elements Framework (summary)

- **PITCH** — F0 contour is an explicit, editable trajectory; transpose = rescale contour, envelope fixed ⇒ formant-preserving (unlike SP-026). Portamento/vibrato/microtonal retuning in F0 domain, zero spectral side effects.
- **RHYTHM** — lives in trajectory switching at hop resolution (1–5 ms); voiced/unvoiced segmentation from $a$; time-stretch = trajectory resampling (pitch preserved, opposite trade from SP-026).
- **HARMONY** — per-voice analysis (rows), summed resynthesis; envelope swap/interpolation between rows = "timbre harmony" (vertical sonorities of spectral bodies). Not the SP-046 robot voice.
- **STRUCTURE** — columns = morph automation {F0 transform, envelope target + $\alpha_s$, aperiodicity target}; parameter-domain crossfades are artifact-free; morph schedule = macro-form.
- **TEXTURE** — $a(\omega,t)$ per-band periodic/noise ratio: tonal↔breathy↔noise continuum, hybrid textures, roughness via sub-audio $a$ modulation; envelope body from ANY analyzed source.

## 6. UnitMatrix Integration (summary)

- **Voices = rows = independent analysis streams**: each rendered stem → $\{F_0^v, P^v, a^v\}$; per-row transpose, envelope target (timbre matrix orthogonal to pitch matrix), aperiodicity gain.
- **Sections = columns = parameter automation**: per-column F0 transform / envelope target + $\alpha_s$ / aperiodicity target; seams crossed by interpolating parameters (log-mag envelope, linear $a$) — no clicks, no retiming.
- **Cells = MusicUnit**: cell pitches → F0 contour (per-cell portamento policy); onsets/durations → trajectory time axis; velocity → excitation strength & breathiness.
- **Dispatch**: `produce(midi_path, method="SP-127", params={"analysis_hop_ms": 5.0, "f0_transpose": 0.0, "morph_target": "row_3", "aperiodicity_gain": 1.0, "min_phase": True, "preserve_attacks": True})`. Order: render → SP-127 → mix → SP-008 → SP-126 → SP-122.
- **Reproducibility**: analysis deterministic; noise excitation seeded per row (recorded in provenance) or replaced by deterministic noise.

## 7. Pitfalls (headline list)

1. F0 errors are catastrophic (octave error ⇒ ripple + wrong excitation period); cross-check with YIN/autocorrelation, median-filter contour.
2. Only quasi-periodic material: per-voice monophonic rows, never full mixes (unless aperiodic path is the goal).
3. Minimum phase smears transients — parallel dry attack path (SP-118) for percussive material.
4. Aperiodicity frame-limited at low F0 (bass rows need ≥ 20–30 ms frames → coarser rhythm).
5. Envelope smoothing ∝ F0: detail smoothed away is gone — sharpen in envelope domain before resynthesis.
6. Cache pitch-adaptive windows per pitch class; fixed windows reintroduce ripple.
7. Not SP-046: STRAIGHT cross-synthesis = envelope swap between two analyzed sources, not modulator-on-carrier.
8. Budget analysis cost per row; full 16-row matrices need per-row downsampling or parallel analysis.
9. Noise excitation must be seeded for reproducible renders.
10. Formant-preserving transposition is clean ≈ ±1 octave; beyond that, morph the envelope toward a register that exists.

## 8. References

1. Kawahara, H., Masuda-Katsuse, I., de Cheveigné, A. (1999). "Restructuring speech representations using a pitch-adaptive time–frequency smoothing and an instantaneous-frequency-based F0 extraction: Possible role of a repetitive structure in sounds." *Speech Communication* 27(3–4), 187–227. (Crossref-verified 2026-10-29.)
2. Kawahara, H., Estill, J., Fujimura, O. (1998). "An instantaneous-frequency-based pitch extraction method for high-quality speech transformation: revised version of the algorithm." *ICSLP 1998*, Sydney. (Crossref-verified.)
3. Kawahara, H. (2006). "STRAIGHT, exploitation of the other aspect of VOCODER: Perceptually isomorphic decomposition of speech sounds." *Acoustical Science and Technology* 27(6), 233–239. (Crossref-verified.)
4. Kawahara, H., Morise, M., Takahashi, T., Nisimura, R., Irino, T., Banno, H. (2008). "Tandem-STRAIGHT: A temporally stable power spectral representation for periodic signals and applications to interference-free spectrum, F0, and aperiodicity estimation." *ICASSP 2008*, 4333–4336. (Crossref-verified.)
5. arXiv:2603.07584 (2026-03-08). "Analysis-Driven Procedural Generation of an Engine Sound Dataset with Embedded Control Annotations" — pitch-adaptive spectral analysis applied to non-speech quasi-periodic sources (engine recordings). (arXiv-verified 2026-10-29.)
