"""Voice-like virtual instruments — synthesized instruments that evoke the
human voice *without being voices*.

## The principle

Vocal familiarity is carried by the **formant envelope** — the resonant peaks
of a vocal tract — not by the vocal folds. Any harmonic-rich, non-vocal
excitation routed through a formant bank is heard as "voice". That is why a
sawtooth through a vowel filter reads as a choir "aah", and why the pipe
organ's *vox humana* stop (a reed pipe, not a voice) has been named after the
voice since the 16th century.

This module is a family of **non-vocal** instruments built on that principle.
None of them synthesizes a glottal pulse, aspiration-as-breath, or a singing
vocal tract — each has its own physical excitation:

| instrument   | excitation (real physics)      | why it sounds voice-like          |
|--------------|--------------------------------|-----------------------------------|
| vox_humana   | free reed + short resonator    | named for the voice since 1500s   |
| kazoo        | mirliton membrane buzz         | modulates whatever you hum        |
| jaw_harp     | plucked lamella (mouth = filter)| mouth cavity picks a harmonic     |
| didgeridoo   | lip reed + long bore           | mouth formants shape the drone    |
| singing_saw  | bowed steel friction           | ethereal, vibrato, formant glow   |
| talkbox      | instrument driven through mouth| the mouth IS the filter           |

## Mapping to the repo's instrument family

These are *instruments*, not voices: they have no consonants, no lyrics, no
TTS path. Contrast with `singing_voice.py` (a source-filter model of an actual
sung voice) and `vocal.py` (a formant guide-vocal utility).

References: Fant (1960) source-filter theory; Klatt (1980) parallel formant
synthesis; Fletcher & Rossing, *The Physics of Musical Instruments*;
Sundberg, *The Science of the Singing Voice*.

Usage
-----
    from sound.synthesis.voice_like import VoiceLikeInstrument, INSTRUMENTS

    vi = VoiceLikeInstrument("kazoo", sample_rate=44100)
    audio = vi.render_note(f0=220.0, duration=1.5, vowel="a")
    phrase = vi.render_phrase([(57, 0.5, "a"), (60, 0.5, "o")])
"""

from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

try:
    from scipy import signal as _sig
    _SCIPY = True
except ImportError:  # pragma: no cover - scipy is a hard dep in this env
    _SCIPY = False

__all__ = [
    "VOWEL_FORMANTS", "FORMANT_BANDWIDTHS", "INSTRUMENTS",
    "VoiceLikeInstrument", "render_phrase_wav", "demo",
]

# --------------------------------------------------------------------------- #
# Vocal-tract constants (Peterson & Barney 1952; Klatt 1980 bandwidths)        #
# --------------------------------------------------------------------------- #

#: First five formants (Hz) per vowel. The *only* thing that distinguishes
#: vowels is this envelope — not pitch, not source.
VOWEL_FORMANTS: Dict[str, Tuple[float, float, float, float, float]] = {
    "a": (730.0, 1090.0, 2440.0, 3300.0, 3850.0),
    "e": (530.0, 1840.0, 2480.0, 3500.0, 4000.0),
    "i": (270.0, 2290.0, 3010.0, 3500.0, 4100.0),
    "o": (570.0, 840.0, 2410.0, 3300.0, 3850.0),
    "u": (300.0, 870.0, 2240.0, 3300.0, 3850.0),
}

#: Klatt cascade bandwidths B1..B5 (Hz).
FORMANT_BANDWIDTHS: Tuple[float, float, float, float, float] = (
    90.0, 110.0, 170.0, 250.0, 300.0,
)

#: Didgeridoo bore: much longer than a vocal tract, so its resonances sit far
#: below speech formants. `tract_scale` shrinks the vowel's formants to the
#: bore's range, so the player's mouth shape still selects the drone's colour.
_DIDGE_TRACT_SCALE = 0.42


# --------------------------------------------------------------------------- #
# Filter primitives                                                            #
# --------------------------------------------------------------------------- #

def _resonator(freq: float, bw: float, sr: int) -> Tuple[float, float, float]:
    """Second-order resonator with **unity peak gain** at `freq`.

    Poles at ``r * exp(±j*2*pi*f/sr)`` with ``r = exp(-pi*bw/sr)`` (so `bw`
    is the -3 dB bandwidth, as in Klatt). For poles inside the unit circle the
    denominator is ``1 - 2r*cos(th) z^-1 + r^2 z^-2``, i.e. ``a1 = -2r*cos(th)``
    and ``a2 = +r^2``. (Sign matters: ``a2 = -r^2`` would place the poles
    *outside* the circle and the filter diverges.)

    ``b0`` is solved so the response peaks at 1.0 near `freq`, which makes
    parallel formant gains comparable across the spectrum (a DC-normalized
    section would make F1 swamp F3). Because |H| = b0 / |denominator|, unity
    peak gain needs the *minimum* of |denominator| over the resonance — using
    the maximum instead overshoots the gain by 6-40x and the bank clips.

    Returns ``(b0, a1, a2)`` for ``H(z) = b0 / (1 + a1 z^-1 + a2 z^-2)``.
    """
    r = np.exp(-np.pi * bw / sr)
    th = 2.0 * np.pi * freq / sr
    a1 = -2.0 * r * np.cos(th)
    a2 = r * r
    # sample the denominator magnitude in a window around the pole angle and
    # take the MIN -> b0 that yields unity peak gain at resonance
    ws = th + np.linspace(-0.12, 0.12, 41)
    z = np.exp(-1j * ws)
    den = np.abs(1.0 + a1 * z + a2 * z ** 2)
    b0 = float(den.min())
    return b0, float(a1), float(a2)


def _formant_bank(
    x: np.ndarray,
    formants: Sequence[float],
    bandwidths: Sequence[float],
    gains: Sequence[float],
    sr: int,
    mode: str = "cascade",
    antiformant: Optional[Tuple[float, float, float]] = None,
) -> np.ndarray:
    """Route `x` through a formant bank — the vocal tract.

    mode="cascade" (default, physically correct for vowels)
        Series of second-order resonators, each normalized to **unity DC
        gain** (``b0 = 1 + a1 + a2``), exactly as in Klatt's cascade branch.
        This matters: because every section is unity at DC but resonant at its
        formant, the *higher* formants receive progressively more gain (F3
        lands ~+30 dB relative to its input). That boost automatically
        counteracts the source's 1/f rolloff, so the summed output envelope
        tracks the formants instead of the source. A cascade of all-pole
        sections is also genuinely all-pole, which is what makes its output
        analysable by LPC (see :func:`lpc_spectral_envelope`).

    mode="parallel"
        Sum of unity-peak resonators scaled by `gains` (Klatt's parallel
        branch). Useful for buzz sources and inharmonic excitation, but note
        it is a *pole-zero* system, so LPC will not recover its formants.

    `antiformant` = (freq, bw, depth) subtracts a resonator, creating a
    spectral *notch* — the "honk" of a kazoo or a nasal vowel.
    """
    if not _SCIPY:  # pragma: no cover
        return x.copy()
    x = np.asarray(x, dtype=np.float64)

    if mode == "cascade":
        y = x
        for f, bw in zip(formants, bandwidths):
            if f <= 40.0 or f >= 0.45 * sr:
                continue
            r = np.exp(-np.pi * float(bw) / sr)
            a1 = -2.0 * r * np.cos(2.0 * np.pi * float(f) / sr)
            a2 = r * r
            b0 = 1.0 + a1 + a2          # unity DC gain -> self-compensating
            y = _sig.lfilter([b0], [1.0, a1, a2], y)
        if antiformant is not None:
            af, abw, adepth = antiformant
            b0, a1, a2 = _resonator(float(af), float(abw), sr)
            y = y - adepth * _sig.lfilter([b0], [1.0, a1, a2], y)
        return y

    out = np.zeros_like(x)
    for f, bw, g in zip(formants, bandwidths, gains):
        if g <= 0.0 or f <= 40.0 or f >= 0.45 * sr:
            continue
        b0, a1, a2 = _resonator(float(f), float(bw), sr)
        out += g * _sig.lfilter([b0], [1.0, a1, a2], x)
    if antiformant is not None:
        af, abw, adepth = antiformant
        b0, a1, a2 = _resonator(float(af), float(abw), sr)
        out -= adepth * _sig.lfilter([b0], [1.0, a1, a2], x)
    return out


# --------------------------------------------------------------------------- #
# Instrument specifications                                                    #
# --------------------------------------------------------------------------- #

def _tilt(t: float, odd_only: float = 1.0) -> Callable[[int], float]:
    """Harmonic amplitude law ``a_k = k**-t`` (even harmonics scaled by
    `odd_only` < 1 to model square-ish reed spectra).

    The exponent is attached to the returned callable as ``.tilt`` so the
    formant bank can compensate for the source rolloff without the number
    being written down twice.
    """
    def amp(k: int) -> float:
        a = float(k) ** (-t)
        if k % 2 == 0:
            a *= odd_only
        return a
    return amp


def _violin_like_amp(k: int) -> float:
    return float(k) ** (-1.15)


#: The family. Each entry is a non-vocal excitation + a vocal-tract colour.
INSTRUMENTS: Dict[str, dict] = {
    "vox_humana": dict(
        label="Vox Humana",
        gm_name="Reed Organ",
        midi_program=20,
        source="reed",
        amp=_tilt(0.75, odd_only=0.35),   # squarish reed spectrum
        harmonics=140,
        range=(48, 84),
        gains=(1.00, 0.80, 0.55, 0.30, 0.18),
        mode="cascade",
        antiformant=(1150.0, 260.0, 0.35),   # hollower, "short resonator"
        vibrato=(5.2, 0.32),                 # tremulant
        noise=0.012,
        release=0.14,
        note="Free reed + very short resonator; the organ stop literally named "
             "for the voice (16th c.). Played with a tremulant.",
    ),
    "kazoo": dict(
        label="Kazoo",
        gm_name="Muted Trumpet",
        midi_program=59,
        source="membrane",
        amp=_tilt(0.35, odd_only=0.9),   # bright, buzzy
        harmonics=170,
        range=(50, 86),
        gains=(0.45, 1.00, 0.95, 0.55, 0.35),
        mode="cascade",
        antiformant=(1000.0, 300.0, 0.55),   # deep nasal notch = the "honk"
        buzz=(3100.0, 0.55),                 # mirliton membrane resonance
        vibrato=(5.0, 0.22),
        noise=0.02,
        release=0.06,
        note="Mirliton: a vibrating membrane colours whatever is sung into it. "
             "Bright, nasal, buzzy — the classic 'hum through paper' voice.",
    ),
    "jaw_harp": dict(
        label="Jaw Harp",
        gm_name="Shamisen",
        midi_program=106,
        source="lamella",
        amp=_tilt(1.0),
        harmonics=140,
        range=(36, 74),
        gains=(0.55, 0.70, 1.00, 0.45, 0.25),
        mode="cascade",
        antiformant=(1500.0, 400.0, 0.30),
        pluck=(0.004, 0.85),                 # sharp attack, slow drone decay
        drone=(0.30, 0.22),                  # twanging reed partial
        vibrato=(4.6, 0.18),
        noise=0.008,
        release=0.05,
        note="Plucked metal lamella in front of the mouth: the mouth cavity "
             "selects one overtone, so a fixed pluck sounds like a sung vowel.",
    ),
    "didgeridoo": dict(
        label="Didgeridoo",
        gm_name="Reed Organ",
        midi_program=20,
        source="lipreed",
        amp=_tilt(1.05, odd_only=0.75),
        harmonics=150,
        range=(24, 55),
        tract_scale=_DIDGE_TRACT_SCALE,
        gains=(1.00, 0.75, 0.50, 0.28, 0.15),
        mode="cascade",                      # long bore -> true formant tube
        vibrato=(3.4, 0.22),
        drift=(0.35, 0.06),                  # unstable lip-reed pitch
        noise=0.055,                         # heavy breath
        circular=(0.13, 0.9),                # circular-breathing swell
        release=0.22,
        note="Lip reed into a long wooden bore. Mouth formants shape the drone, "
             "so it is heard as a voice inside a tube — the 'vocal' drone.",
    ),
    "singing_saw": dict(
        label="Singing Saw",
        gm_name="Lead 2 (sawtooth)",
        midi_program=81,
        source="friction",
        amp=_violin_like_amp,
        harmonics=90,
        range=(55, 91),
        gains=(1.00, 0.62, 0.42, 0.22, 0.12),
        mode="cascade",
        vibrato=(4.4, 0.62),                 # signature wide vocal vibrato
        detune=(0.0035, 0.55),               # shimmer / metal wooble
        noise=0.02,
        release=0.30,
        note="Bowed steel blade: near-harmonic friction tone with a wide "
             "vibrato. Ethereal and uncannily voice-like without a lung in it.",
    ),
    "talkbox": dict(
        label="Talkbox",
        gm_name="Lead 1 (square)",
        midi_program=80,
        source="saw",
        amp=_tilt(0.92),
        harmonics=120,
        range=(45, 84),
        gains=(1.00, 0.92, 0.62, 0.34, 0.20),
        mode="cascade",
        drive=1.9,                            # amp/compression grit
        vibrato=(5.4, 0.30),
        noise=0.01,
        release=0.10,
        morph=True,                           # vowel glide a->o etc.
        note="An instrument driven by a tube into the player's mouth: the "
             "mouth IS the filter. The classic 'talking' lead voice.",
    ),
}


# --------------------------------------------------------------------------- #
# Engine                                                                       #
# --------------------------------------------------------------------------- #

class VoiceLikeInstrument:
    """A voice-like instrument: non-vocal excitation -> vocal-tract colour.

    Parameters
    ----------
    name : str
        Key in :data:`INSTRUMENTS`.
    sample_rate : int
        Sampling rate in Hz.
    seed : int
        RNG seed — renders are deterministic for a given seed.
    """

    def __init__(self, name: str, sample_rate: int = 44100, seed: int = 0):
        if name not in INSTRUMENTS:
            raise ValueError(
                f"Unknown instrument {name!r}. Use: {sorted(INSTRUMENTS)}")
        self.name = name
        self.spec = INSTRUMENTS[name]
        self.sr = int(sample_rate)
        self.seed = int(seed)
        self._rng = np.random.default_rng(seed)

    # ------------------------------------------------------------- sources
    def _f0_track(self, f0: float, n: int) -> np.ndarray:
        """f0 contour with vibrato, optional pitch drift, and onset scoop."""
        t = np.arange(n) / self.sr
        f = np.full(n, float(f0), dtype=np.float64)
        vib = self.spec.get("vibrato")
        if vib:
            rate, depth = vib
            # delayed vibrato: singers/instruments ease it in; depth in semitones
            onset = np.clip(t / 0.35, 0.0, 1.0)
            f = f * (2.0 ** (depth * onset * np.sin(2 * np.pi * rate * t) / 12.0))
        drift = self.spec.get("drift")
        if drift:
            amount, rate = drift
            f = f * (1.0 + amount * np.sin(2 * np.pi * rate * t + 1.1))
        return f

    def _harmonic_source(self, f0_track: np.ndarray) -> np.ndarray:
        """Band-limited harmonic sum — the shared, non-vocal excitation.

        No glottal pulse, no Rosenberg/LF flow model: just a harmonic series
        with the instrument's own amplitude law. The timbre therefore comes
        from the *formant bank*, not from a voice source.

        Normalized by the **sum of the amplitude law** (not by the observed
        peak). Peak-normalizing would divide out the source's spectral
        character, which is what distinguishes these instruments.
        """
        n = len(f0_track)
        phase = np.cumsum(2.0 * np.pi * f0_track / self.sr)
        fmax = float(np.max(f0_track))
        kmax = int(min(self.spec.get("harmonics", 120),
                       0.45 * self.sr / max(fmax, 1e-6)))
        amp = self.spec["amp"]
        out = np.zeros(n, dtype=np.float64)
        norm = 0.0
        for k in range(1, kmax + 1):
            a = amp(k)
            if a < 1e-4:
                continue
            out += a * np.sin(k * phase + self._rng.uniform(0.0, 2.0 * np.pi))
            norm += a
        return out / max(norm, 1e-12)

    def _excite(self, f0_track: np.ndarray) -> np.ndarray:
        """Excitation of the instrument's physical source."""
        n = len(f0_track)
        src = self._harmonic_source(f0_track)
        t = np.arange(n) / self.sr

        pluck = self.spec.get("pluck")
        if pluck:
            # plucked lamella: sharp attack, exponential decay, plus a
            # twanging partial that decays slower than the rest
            attack, decay = pluck
            a_n = max(1, int(attack * self.sr))
            env = np.exp(-t * decay)
            if a_n > 1:
                env[:a_n] *= np.linspace(0.0, 1.0, a_n)
            env = env / (np.max(env) + 1e-12)
            src = src * env
            drone = self.spec.get("drone")
            if drone:
                frac, d_rate = drone
                src = src + frac * np.sin(2 * np.pi * f0_track[0] * 2.0 * t) * \
                    np.exp(-t * d_rate)

        buzz = self.spec.get("buzz")
        if buzz:
            # mirliton membrane: amplitude modulation by a high resonance ->
            # sidebands, heard as a nasal buzz on top of the tone
            f_b, depth = buzz
            src = src * (1.0 + depth * np.sin(2 * np.pi * f_b * t))

        detune = self.spec.get("detune")
        if detune:
            # friction-tone shimmer: a slightly detuned copy
            ratio, mix = detune
            ph2 = np.cumsum(2.0 * np.pi * f0_track * (1.0 + ratio) / self.sr)
            harm = np.sin(ph2) + 0.5 * np.sin(2 * ph2) + 0.2 * np.sin(3 * ph2)
            src = (1.0 - mix) * src + mix * harm / (np.max(np.abs(harm)) + 1e-12)

        drive = self.spec.get("drive")
        if drive:
            src = np.tanh(drive * src) / np.tanh(drive)

        noise = float(self.spec.get("noise", 0.0))
        if noise > 0.0:
            src = src + noise * self._rng.normal(0.0, 1.0, n)

        return src

    # ---------------------------------------------------------------- note
    def formants_for(self, vowel: str) -> Tuple[float, ...]:
        """The formant set this instrument uses for `vowel`.

        An instrument with `tract_scale` (a bore much longer than a vocal
        tract, e.g. didgeridoo) scales the vowel's formants into its own
        resonance range, so the player's mouth shape still steers the colour.
        """
        base = self.spec.get("formants", VOWEL_FORMANTS.get(vowel, VOWEL_FORMANTS["a"]))
        scale = self.spec.get("tract_scale")
        if scale:
            base = tuple(f * scale for f in base)
        return tuple(float(f) for f in base)

    def render_note(
        self,
        f0: float,
        duration: float,
        vowel: str = "a",
        vowel_end: Optional[str] = None,
        attack: float = 0.02,
    ) -> np.ndarray:
        """Render one note.

        Parameters
        ----------
        f0 : float
            Fundamental in Hz.
        duration : float
            Seconds.
        vowel : str
            Vowel whose formants colour the tone ('a','e','i','o','u').
        vowel_end : str, optional
            If given (and the instrument supports morphing, e.g. talkbox),
            the formants glide from `vowel` to `vowel_end` across the note.
        attack : float
            Attack time in seconds.

        Returns
        -------
        np.ndarray
            Mono float64 audio in [-1, 1].
        """
        n = max(1, int(duration * self.sr))
        f0_track = self._f0_track(f0, n)
        src = self._excite(f0_track)

        formants = self.formants_for(vowel)
        gains = self.spec["gains"]
        bws = FORMANT_BANDWIDTHS
        mode = self.spec.get("mode", "parallel")
        y_a = _formant_bank(src, formants, bws, gains, self.sr, mode=mode,
                            antiformant=self.spec.get("antiformant"))

        if vowel_end and self.spec.get("morph"):
            f2 = self.formants_for(vowel_end)
            y_b = _formant_bank(src, f2, bws, gains, self.sr, mode=mode,
                                antiformant=self.spec.get("antiformant"))
            t = np.arange(n) / self.sr
            x = np.linspace(0.0, 1.0, n) ** 1.3      # ease-in glide
            y = y_a * (1.0 - x) + y_b * x
        else:
            y = y_a

        # DC block. A radiated pressure has no DC term, but a parallel formant
        # bank passes DC at ~unity gain, and that offset leaks into the lowest
        # FFT bins. First-order highpass at ~30 Hz (well below any f0) removes
        # it without touching the audible band.
        if _SCIPY:
            y = _sig.lfilter([1.0, -1.0], [1.0, -0.99573], y)

        # circular-breathing swell (didgeridoo): slow amplitude bloom
        circ = self.spec.get("circular")
        if circ:
            rate, depth = circ
            t = np.arange(n) / self.sr
            y = y * (1.0 - depth + depth * (0.5 + 0.5 * np.sin(2 * np.pi * rate * t)))

        # amplitude envelope
        env = np.ones(n, dtype=np.float64)
        a_n = max(1, int(attack * self.sr))
        if a_n > 1:
            env[:a_n] = np.linspace(0.0, 1.0, a_n)
        r_n = max(1, int(self.spec.get("release", 0.12) * self.sr))
        if r_n > 1:
            env[-r_n:] *= np.linspace(1.0, 0.0, r_n)
        y = y * env

        peak = float(np.max(np.abs(y)))
        if peak > 0.0:
            y = y / peak * 0.85
        return y

    # -------------------------------------------------------------- phrase
    def render_phrase(
        self,
        notes: Sequence[Tuple[int, float, str]],
        gap: float = 0.02,
        tail: float = 0.25,
    ) -> np.ndarray:
        """Render a monophonic phrase.

        `notes` = sequence of (midi_note, duration_seconds, vowel).
        """
        chunks: List[np.ndarray] = []
        gap_n = int(gap * self.sr)
        for midi_note, dur, vow in notes:
            f0 = 440.0 * 2.0 ** ((float(midi_note) - 69.0) / 12.0)
            chunks.append(self.render_note(f0, dur, vowel=vow))
            if gap_n:
                chunks.append(np.zeros(gap_n, dtype=np.float64))
        if tail:
            chunks.append(np.zeros(int(tail * self.sr), dtype=np.float64))
        out = np.concatenate(chunks) if chunks else np.zeros(1)
        peak = float(np.max(np.abs(out)))
        if peak > 0.0:
            out = out / peak * 0.9
        return out


# --------------------------------------------------------------------------- #
# Convenience                                                                  #
# --------------------------------------------------------------------------- #

def render_phrase_wav(
    output_path: str,
    notes: Sequence[Tuple[int, float, str]],
    instrument: str = "vox_humana",
    sample_rate: int = 44100,
    seed: int = 0,
) -> str:
    """Render a phrase to a mono 16-bit WAV and return the path."""
    import wave

    vi = VoiceLikeInstrument(instrument, sample_rate=sample_rate, seed=seed)
    audio = vi.render_phrase(notes)
    pcm = np.clip(audio, -1.0, 1.0)
    pcm = (pcm * 32767.0).astype("<i2")
    with wave.open(output_path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        w.writeframes(pcm.tobytes())
    return output_path


def lpc_spectral_envelope(
    x: np.ndarray,
    sr: int,
    order: int = 24,
    n_points: int = 2048,
    preemph: float = 0.97,
) -> Tuple[np.ndarray, np.ndarray]:
    """LPC spectral envelope — the standard way to read formants off a signal.

    A plain FFT of a harmonic-rich tone shows one spike per harmonic; the
    *formants* only appear once the harmonic structure is smoothed away. Linear
    prediction does exactly that: it fits an all-pole model of the vocal tract
    to the signal (autocorrelation method, normal equations solved via the
    Toeplitz structure), and ``1/|A(e^jw)|`` is the tract envelope.

    A light pre-emphasis (0.97) is standard practice — it flattens the glottal
    source tilt so the formant peaks are not masked by the overall rolloff.

    Returns ``(freqs, envelope)`` over 0..sr/2.
    """
    x = np.asarray(x, dtype=np.float64)
    if x.ndim > 1:
        x = x[:, 0]
    if preemph:
        x = np.append(x[:1], x[1:] - preemph * x[:-1])
    if len(x) < order * 4:
        raise ValueError("signal too short for the requested LPC order")

    nfft = 1 << int(np.ceil(np.log2(max(2 * len(x), 64))))
    X = np.fft.rfft(x, nfft)
    r = np.fft.irfft(np.abs(X) ** 2)[: order + 1]
    if r[0] <= 0:
        return np.linspace(0.0, sr / 2.0, n_points), np.zeros(n_points)

    if _SCIPY:
        from scipy.linalg import solve_toeplitz
        a = solve_toeplitz((r[:order], r[:order]), -r[1: order + 1])
    else:  # pragma: no cover - fallback without scipy
        R = np.array([[r[abs(i - j)] for j in range(order)] for i in range(order)])
        a = np.linalg.solve(R, -r[1: order + 1])

    w = np.linspace(0.0, np.pi, n_points)
    A = np.ones(n_points, dtype=np.complex128)
    for i, ai in enumerate(a, start=1):
        A += ai * np.exp(-1j * w * i)
    env = np.sqrt(r[0]) / (np.abs(A) + 1e-12)
    freqs = w / (2.0 * np.pi) * sr
    return freqs, env


def envelope_peaks(
    freqs: np.ndarray,
    env: np.ndarray,
    lo: float = 150.0,
    hi: float = 4200.0,
    n: int = 3,
    min_sep: float = 200.0,
) -> List[float]:
    """The `n` strongest envelope maxima in [lo, hi], ascending.

    Works on a smooth envelope (see :func:`lpc_spectral_envelope`) — do not
    call it on a raw FFT magnitude, where every harmonic reads as a peak.
    """
    m = (freqs >= lo) & (freqs <= hi)
    f, e = freqs[m], env[m]
    if len(f) < 3:
        return []
    cand = [(float(e[i]), float(f[i])) for i in range(1, len(e) - 1)
            if e[i] >= e[i - 1] and e[i] >= e[i + 1]]
    cand.sort(reverse=True)
    picked: List[float] = []
    for _, fr in cand:
        if all(abs(fr - p) > min_sep for p in picked):
            picked.append(fr)
        if len(picked) == n:
            break
    return sorted(picked)


def demo() -> None:  # pragma: no cover - informational
    """Print the family table."""
    print(f"{'key':14s} {'label':14s} {'GM':28s} note")
    for k, s in INSTRUMENTS.items():
        print(f"{k:14s} {s['label']:14s} {s['gm_name']:28s} {s['note'][:52]}")
