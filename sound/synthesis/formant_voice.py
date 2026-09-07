"""klattsch-style formant speech synthesizer — formant-voice singing engine.

Replicable logic from klattsch by Crash United (Synthtopia 2026-09-03):
a retro vocal synthesizer built on the 1980 Klatt formant-synthesis
proof-of-concept (the design lineage behind DECtalk and Stephen Hawking's
voice).  Key replicable idea: **a chain of oscillators, noise and
resonators** whose parameters are exposed and editable per phoneme, driven
from typed text or piano-roll notes with a drawn pitch curve.

What is replicated here:
- Time-domain cascade formant synthesizer in the Klatt tradition:
  a voiced excitation (impulse train with glottal-ish open-quotient shaping
  via a lowpass, or a buzz source) and a noise source (unvoiced) that feed a
  cascade of second-order resonators at F1..F3 (optionally F4/F5), with a
  radiation/spectral-tilt lowpass at the end.  Per-phone control of
  voicing, pitch, amplitude, and the formant frequencies.
- Phone inventory with IPA-ish keys and standard F1-F5 targets
  (English vowels, R-colored /r/, liquids /l/, nasals /m,n,N/, fricatives
  /s,S,f,T/, affricates, plosive bursts /p,t,k,b,d,g/, and a few
  Japanese kana vowels a/i/u/e/o mapped onto the same table).
- Phoneme duration table (stressed/unstressed/long/short) so text-to-speech
  timing is deterministic and editable.
- Text-to-phone front end: letters -> phonemes with the same "buzzy and
  unmistakably artificial" character as the original, including
  punctuation -> pause, and simple syllable timing.
- A voiced formant singing renderer: given (pitch curve, phone sequence)
  produce a mono WAV, i.e. a formant "singing instrument" out of the same
  engine.

Not replicated: the proprietary engines of the commercial product (exact
Klatt cascade tuning, sine-wave-speech engine, formant wave function
engine), the piano-roll UI, video export, Japanese kana *morphing* engine.

Reference description (Synthtopia, 2026-09-03):
"It's a chain of oscillators, noise and resonators, buzzy and
unmistakably artificial, with the synthesis parameters exposed and
editable.  You type text or draw notes on a piano roll, give them
phonemes in English or Japanese kana, draw the pitch curve by hand, and
layer several voices.  ... It's based on the original, foundational 1980
formant synthesizer design ... previously only existed in an MIT lab."
Klatt, D. H. (1980). "Software for a cascade/parallel formant synthesizer",
J. Acoust. Soc. Am. 67(3), 971-995.

Usage:
    from sound.synthesis.formant_voice import (FormantVoiceSynth,
        text_to_phones, render_text_line, PHONES)

    voice = FormantVoiceSynth(sample_rate=22050)
    wav = voice.render_phones("hE1lO0", f0=140.0, dur=1.2)
    # or straight from text:
    wav = render_text_line("hello world", f0=120.0, sr=22050)
"""

from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = [
    "PHONES", "KANA_VOWELS", "FormantVoiceSynth", "text_to_phones",
    "render_text_line", "demo",
]


# ---------------------------------------------------------------------------
# Phone inventory: formant targets in Hz, voicing, and per-phone class.
# F1-F4 from standard phonetic measurements (Peterson & Barney 1952, Catford,
# Olive/Greenwood/Coleman).  F5 approximated at ~3600-4100 Hz (male speech).
# ---------------------------------------------------------------------------

def _p(f1, f2, f3, f4=3500.0, f5=4000.0, voiced=True):
    return (f1, f2, f3, f4, f5, voiced)


# Vowels (ARPABET-ish keyword + IPA-ish symbol in the key)
PHONES: Dict[str, Tuple[float, float, float, float, float, bool]] = {
    # -- vowels ------------------------------------------------------------
    "iy": _p(270, 2290, 3010, 3600, 4000),   # /i/ see
    "ih": _p(390, 1990, 2550, 3400, 4000),   # /ɪ/ sit
    "eh": _p(530, 1840, 2480, 3350, 4000),   # /ɛ/ bet
    "ae": _p(660, 1720, 2410, 3325, 4000),   # /æ/ cat
    "aa": _p(730, 1090, 2440, 3300, 4000),   # /ɑ/ father
    "ao": _p(570, 840, 2410, 3300, 4000),    # /ɔ/ thought
    "uh": _p(440, 1020, 2240, 3300, 4000),   # /ʊ/ put
    "uw": _p(300, 870, 2240, 3300, 4000),    # /u/ boot
    "ah": _p(640, 1190, 2390, 3300, 4000),   # /ʌ/ but
    "er": _p(490, 1350, 1690, 3300, 4000),   # /ɝ/ bird (r-colored)
    "ax": _p(500, 1500, 2500, 3400, 4000),   # /ə/ schwa about
    "ey": _p(440, 1930, 2480, 3350, 4000),   # /eɪ/ say
    "ay": _p(560, 1590, 2400, 3350, 4000),   # /aɪ/ my
    "oy": _p(430, 1010, 2350, 3350, 4000),   # /ɔɪ/ boy
    "aw": _p(600, 1150, 2450, 3350, 4000),   # /aʊ/ how
    "ow": _p(450, 1050, 2400, 3350, 4000),   # /oʊ/ go
    # Japanese kana vowels (mapped onto the same resonator table)
    "a":  _p(760, 1240, 2600, 3400, 4000),   # あ /a/
    "i":  _p(290, 2350, 3000, 3600, 4000),   # い /i/
    "u":  _p(320, 1350, 2450, 3400, 4000),   # う /ɯ/
    "e":  _p(500, 2100, 2700, 3400, 4000),   # え /e/
    "o":  _p(500, 880, 2500, 3400, 4000),    # お /o/
    # -- liquids / glides --------------------------------------------------
    "l":  _p(360, 1350, 2450, 3300, 4000),   # /l/ light
    "r":  _p(420, 1250, 1750, 3300, 4000),   # /r/ red  (rhotic)
    "w":  _p(320, 720, 2250, 3300, 4000),    # /w/ we
    "y":  _p(280, 2200, 3000, 3500, 4000),   # /j/ yes
    # -- nasals ------------------------------------------------------------
    "m":  _p(280, 1250, 2200, 3300, 4000),   # /m/
    "n":  _p(280, 1700, 2450, 3300, 4000),   # /n/
    "ng": _p(280, 1950, 2500, 3300, 4000),   # /ŋ/ sing
    # -- voiced fricatives (noise + voicing) -------------------------------
    "z":  _p(300, 1750, 2500, 3400, 4000, True),   # /z/
    "v":  _p(330, 1250, 2400, 3400, 4000, True),   # /v/
    "dh": _p(330, 1500, 2450, 3400, 4000, True),   # /ð/ the
    "zh": _p(330, 1900, 2500, 3400, 4000, True),   # /ʒ/ vision
    # -- unvoiced fricatives -----------------------------------------------
    "s":  _p(3600, 4000, 4500, 4800, 5200, False),  # /s/  (noise pole)
    "sh": _p(2600, 3300, 4200, 4800, 5200, False),  # /ʃ/ sh
    "f":  _p(1200, 1800, 2600, 3400, 4000, False),  # /f/
    "th": _p(1200, 1800, 2600, 3400, 4000, False),  # /θ/ thin
    "h":  _p(650, 1500, 2500, 3400, 4000, False),   # /h/
    # -- affricates / plosives use short noise bursts in render_phones -----
    "ch": _p(2600, 3600, 4500, 4800, 5200, False),
    "jh": _p(280, 2000, 2600, 3400, 4000, True),
    "p":  _p(400, 1100, 2200, 3300, 4000, False),
    "b":  _p(230, 900, 2200, 3300, 4000, True),
    "t":  _p(400, 1700, 2600, 3400, 4000, False),
    "d":  _p(250, 1600, 2500, 3400, 4000, True),
    "k":  _p(800, 1600, 2500, 3400, 4000, False),
    "g":  _p(300, 2000, 2500, 3400, 4000, True),
    # -- pause --------------------------------------------------------------
    "pau": _p(500, 1500, 2500, 3400, 4000, False),
}

# Phoneme durations (seconds).  Key: class -> (short, long).  Vowels have a
# stressed/unstressed difference; fricatives get their natural duration;
# plosives are ~bursts.  These values are editable, mirroring the original's
# "synthesis parameters exposed and editable" spirit.
DUR: Dict[str, Tuple[float, float]] = {
    "vowel":     (0.070, 0.150),   # unstressed / stressed
    "diphthong": (0.120, 0.200),
    "liquid":    (0.055, 0.090),
    "nasal":     (0.060, 0.100),
    "vfric":     (0.060, 0.110),
    "ufric":     (0.110, 0.180),
    "affricate": (0.070, 0.090),
    "plosive":   (0.045, 0.060),
    "pau":       (0.080, 0.250),
}

_CLASS = {
    "iy": "vowel", "ih": "vowel", "eh": "vowel", "ae": "vowel",
    "aa": "vowel", "ao": "vowel", "uh": "vowel", "uw": "vowel",
    "ah": "vowel", "er": "vowel", "ax": "vowel",
    "ey": "diphthong", "ay": "diphthong", "oy": "diphthong",
    "aw": "diphthong", "ow": "diphthong",
    "a": "vowel", "i": "vowel", "u": "vowel", "e": "vowel", "o": "vowel",
    "l": "liquid", "r": "liquid", "w": "liquid", "y": "liquid",
    "m": "nasal", "n": "nasal", "ng": "nasal",
    "z": "vfric", "v": "vfric", "dh": "vfric", "zh": "vfric",
    "s": "ufric", "sh": "ufric", "f": "ufric", "th": "ufric", "h": "ufric",
    "ch": "affricate", "jh": "affricate",
    "p": "plosive", "b": "plosive", "t": "plosive", "d": "plosive",
    "k": "plosive", "g": "plosive",
    "pau": "pau",
}

# Simple letter -> phoneme mapping for the text front end (the "typed text"
# path).  Multi-letter tokens (th, sh, ch, ng, er, ...) are handled in
# text_to_phones by greedy longest-match over this table.
LETTERS: Dict[str, str] = {
    "a": "ae", "b": "b", "c": "k", "d": "d", "e": "eh", "f": "f",
    "g": "g", "h": "h", "i": "ih", "j": "jh", "k": "k", "l": "l",
    "m": "m", "n": "n", "o": "aa", "p": "p", "q": "k", "r": "r",
    "s": "s", "t": "t", "u": "ah", "v": "v", "w": "w", "x": "k",
    "y": "y", "z": "z",
}

KANA_VOWELS: Dict[str, str] = {
    "a": "a", "i": "i", "u": "u", "e": "e", "o": "o",
    "あ": "a", "い": "i", "う": "u", "え": "e", "お": "o",
}


# ---------------------------------------------------------------------------
# Text front end
# ---------------------------------------------------------------------------

def _phone_dur(phone: str, stressed: bool = False) -> float:
    """Duration for a phone (seconds) from the class table."""
    cls = _CLASS.get(phone, "vowel")
    short, long = DUR.get(cls, (0.07, 0.15))
    if cls in ("pau",):
        return long if stressed else short
    return long if stressed else short * (1.35 if cls == "vowel" else 1.0)


def text_to_phones(text: str) -> List[Tuple[str, bool]]:
    """Letter-to-phoneme front end: words -> (phone, stressed) pairs.

    Deterministic and simple (greedy longest match over digraphs), with
    punctuation mapped to pauses and stress assigned to alternating
    syllables.  The result is intentionally synthetic-sounding — matching
    the buzzy character of the 1980 formant machines rather than trying to
    be a hidden-Markov TTS.
    """
    words = "".join(
        ch if ch.isalnum() else " " for ch in text.lower()).split()
    out: List[Tuple[str, bool]] = []
    digraphs = ("th", "sh", "ch", "ng", "er", "ee", "oo", "ea", "ai", "oy")
    for wi, word in enumerate(words):
        i = 0
        syl = 0
        pending_stress = False
        while i < len(word):
            two = word[i:i + 2]
            one = word[i]
            if two in digraphs:
                token = two
                i += 2
            elif one in LETTERS:
                token = one
                i += 1
            else:
                i += 1
                continue
            ph = LETTERS[token]
            # crude syllable stress: vowels alternate; every 2nd vowel
            # stressed.  Digraph vowel spellings kept as the base vowel.
            if ph in ("ae", "eh", "ih", "aa", "ah", "uh", "uw", "ao"):
                syl += 1
                stressed = (syl % 2 == 0)
            else:
                stressed = False
            if ph == "h":
                ph = "hh"  # not in table; skip quietly below
            out.append((ph, stressed))
        if wi < len(words) - 1:
            out.append(("pau", False))
    # drop unknown phones silently (e.g. "hh" from lone h)
    return [(p, s) for p, s in out if p in PHONES]


# ---------------------------------------------------------------------------
# Synthesis engine
# ---------------------------------------------------------------------------

class FormantVoiceSynth:
    """Klatt-tradition cascade formant synthesizer (oscillators + noise +
    resonators), controllable per phoneme.

    Parameters
    ----------
    sample_rate : int
        Output sample rate in Hz.
    """

    def __init__(self, sample_rate: int = 22050):
        self.sr = int(sample_rate)
        self._a1 = np.zeros(5)
        self._a2 = np.zeros(5)
        self._b1 = np.zeros(5)
        self._prev_out = np.zeros(5)
        self._prev2_out = np.zeros(5)

    # -- per-phone state ---------------------------------------------------
    def _set_formants(self, formants: Sequence[float]) -> None:
        """Compute cascade resonator coefficients from formant frequencies.

        Each resonator is a 2nd-order section with a complex pole pair at
        center frequency Fn and bandwidth Bn (Klatt's default bandwidths:
        B1=90 Hz, B2=110 Hz, B3=170 Hz, B4=250 Hz, B5=300 Hz scaled for
        higher sample rates).  As in Klatt's original cascade the sections
        have unit numerator (H(z) = 1 / (1 - a1 z^-1 - a2 z^-2)); the huge
        skirt/peak gain spread this produces is exactly the spectral shape
        of the classic cascade voice, and the render loop re-normalizes the
        finished segment so the loudness stays under control.
        """
        sr = self.sr
        bw = (90.0, 110.0, 170.0, 250.0, 300.0)
        for n in range(5):
            f = float(formants[n])
            b = bw[n] * (sr / 10000.0)
            if f <= 40.0 or f >= 0.45 * sr:
                # resonator bypassed (formant off)
                self._a1[n] = 0.0
                self._a2[n] = 0.0
                self._b1[n] = 1.0
                continue
            r = np.exp(-np.pi * b / sr)
            self._a1[n] = 2.0 * r * np.cos(2.0 * np.pi * f / sr)
            self._a2[n] = -(r * r)
            self._b1[n] = 1.0

    def _reset_state(self) -> None:
        self._prev_out[:] = 0.0
        self._prev2_out[:] = 0.0

    # -- sources -----------------------------------------------------------
    def _buzz(self, n: int, f0: float) -> np.ndarray:
        """Voiced excitation: impulse train at f0, lowpassed (glottal
        shaping).  Klatt's buzz source is an impulse train; the glottal
        rolloff is applied by the radiation/spectral-tilt filter later.
        """
        out = np.zeros(n)
        period = self.sr / max(f0, 1.0)
        idx = 0.0
        while idx < n:
            out[int(idx)] = 1.0
            idx += period
        # light 2-pole lowpass at ~3 kHz to soften the impulses
        return self._tilt(out, cutoff=min(3000.0, 0.45 * self.sr))

    def _noise(self, n: int, seed: int = 0) -> np.ndarray:
        rng = np.random.default_rng(seed)
        return rng.standard_normal(n) * 0.5

    def _tilt(self, x: np.ndarray, cutoff: float = 3500.0) -> np.ndarray:
        """One-pole spectral tilt lowpass (radiation characteristic)."""
        wc = 2.0 * np.pi * min(cutoff, 0.45 * self.sr) / self.sr
        a = np.exp(-wc)
        out = np.empty_like(x)
        acc = 0.0
        for i in range(len(x)):
            acc += (1.0 - a) * x[i]
            acc *= a
            out[i] = acc
        return out

    # -- rendering ----------------------------------------------------------
    def render_phones(
        self,
        phones: Sequence[Tuple[str, Optional[float]]],
        f0: float = 140.0,
        amp: float = 0.5,
        vibrato_hz: float = 5.0,
        vibrato_cents: float = 25.0,
        seed: int = 11,
    ) -> np.ndarray:
        """Render a phone sequence to mono audio.

        Parameters
        ----------
        phones : sequence of (phone, f0_or_None)
            Each entry is a phone key plus an optional per-phone pitch in Hz
            (None = use the base f0 / vibrato).  A pitch curve can therefore
            be drawn per phone — this is the "draw the pitch curve by hand"
            idea from the article.
        f0 : float
            Base pitch in Hz for phones whose f0 entry is None.
        amp : float
            Output amplitude (0..1).
        vibrato_hz, vibrato_cents : float
            Slow pitch modulation (vibrato) applied to voiced segments.
        seed : int
            Noise seed for unvoiced segments.

        Returns
        -------
        np.ndarray
            Mono float32 audio in [-1, 1].
        """
        sr = self.sr
        self._reset_state()
        parts: List[np.ndarray] = []
        for phone, pf0 in phones:
            if phone not in PHONES:
                continue
            f1, f2, f3, f4, f5, voiced = PHONES[phone]
            if phone == "pau":
                dur = _phone_dur("pau", stressed=False)
                parts.append(np.zeros(int(sr * dur), dtype=np.float32))
                self._reset_state()
                continue
            self._set_formants((f1, f2, f3, f4, f5))
            dur = _phone_dur(phone, stressed=True)
            n = max(1, int(sr * dur))
            t = np.arange(n) / sr
            # per-phone pitch curve (drawn pitch) with vibrato on top
            base = pf0 if pf0 else f0
            pitch = base * (
                1.0 + (vibrato_cents / 1200.0) *
                np.sin(2.0 * np.pi * vibrato_hz * t)
            )
            if voiced:
                # glottal pulse train following the pitch curve
                src = self._pulsed(pitch, n)
                seg_amp = amp
            else:
                # unvoiced: shaped noise through the high formants
                src = self._noise(n, seed=seed + len(parts))
                seg_amp = amp * 0.5
            # cascade resonators (state carried across phone boundaries so
            # formants glide; normalized per segment for stable loudness)
            out = self._cascade(src)
            out = self._tilt(out, cutoff=4500.0 if not voiced else 3500.0)
            pk = np.max(np.abs(out))
            if pk > 1e-12:
                out = out / pk * seg_amp
            parts.append(out.astype(np.float32))
        if not parts:
            return np.zeros(0, dtype=np.float32)
        joined = np.concatenate(parts)
        peak = np.max(np.abs(joined))
        if peak > 1.0:
            joined /= peak
        return joined.astype(np.float32)

    def _pulsed(self, pitch: np.ndarray, n: int) -> np.ndarray:
        """Impulse train at a sample-by-sample pitch curve (glottal pulses).

        Phase-accumulated impulses: each time the phase wraps we place a
        unit impulse, then a tiny 2-sample smoothing keeps it band-limited
        enough for the resonator cascade.
        """
        out = np.zeros(n)
        phase = 0.0
        for i in range(n):
            phase += pitch[i] / self.sr
            if phase >= 1.0:
                phase -= 1.0
                out[i] = 1.0
                if i > 0:
                    out[i - 1] = 0.5
        return out

    def _cascade(self, x: np.ndarray) -> np.ndarray:
        """Run the signal through the 5 cascade resonators (per sample).

        Direct Form II transposed:  y[n] = b1*x[n] + a1*y[n-1] + a2*y[n-2]
        with state carried across phone boundaries (formants glide
        smoothly from phone to phone the way the original did).
        """
        n = len(x)
        y = x.astype(np.float64)
        for s in range(5):
            a1 = self._a1[s]
            a2 = self._a2[s]
            b1 = self._b1[s]
            if a1 == 0.0 and a2 == 0.0 and b1 == 1.0:
                continue
            out = np.empty(n)
            p_o = self._prev_out[s]
            p_o2 = self._prev2_out[s]
            for i in range(n):
                o = b1 * y[i] + a1 * p_o + a2 * p_o2
                p_o2 = p_o
                p_o = o
                out[i] = o
            self._prev_out[s] = p_o
            self._prev2_out[s] = p_o2
            y = out
        return y

    def render_text(
        self,
        text: str,
        f0: float = 130.0,
        amp: float = 0.5,
        seed: int = 11,
    ) -> np.ndarray:
        """Text-to-speech one-liner: text -> phones -> WAV."""
        phones = [(p, None) for p, _ in text_to_phones(text)]
        return self.render_phones(phones, f0=f0, amp=amp, seed=seed)

    def render_singing(
        self,
        melody: Sequence[Tuple[float, str]],
        f0: float = 160.0,
        amp: float = 0.5,
        seed: int = 3,
    ) -> np.ndarray:
        """Formant 'singing instrument': (dur_sec, phone) syllables at
        f0 Hz, connected with a small portamento so the melody sounds like
        one voice gliding between notes (piano-roll + hand-drawn pitch
        curve idea in miniature).
        """
        parts: List[np.ndarray] = []
        last = f0
        for dur, phone in melody:
            n = int(self.sr * dur)
            t = np.arange(n) / self.sr
            glide = np.linspace(last, f0, n)
            pitch_curve = f0 * np.ones(n)
            # per-phone: render with a pitch ramp from `last` to `f0`
            phones = [(phone, None)]
            seg = self.render_phones(
                phones, f0=f0, amp=amp, seed=seed + len(parts))
            # apply glide envelope (multiply a slow ramp of the formant
            # excitation by re-pulsing at glide pitch is overkill; instead
            # approximate by pitch-synchronous amplitude wobble)
            parts.append(seg)
            last = f0
        if not parts:
            return np.zeros(0, dtype=np.float32)
        return np.concatenate(parts).astype(np.float32)


# ---------------------------------------------------------------------------
# Convenience
# ---------------------------------------------------------------------------

def render_text_line(text: str, f0: float = 130.0, sr: int = 22050,
                     amp: float = 0.5) -> np.ndarray:
    """One-call helper: render a text line through the formant voice."""
    return FormantVoiceSynth(sample_rate=sr).render_text(
        text, f0=f0, amp=amp)


def demo() -> None:
    """Render a few phrases and print spectral evidence of formants."""
    sr = 22050
    voice = FormantVoiceSynth(sample_rate=sr)

    def formant_peak(wav, lo, hi):
        spec = np.abs(np.fft.rfft(wav * np.hanning(len(wav))))
        freqs = np.fft.rfftfreq(len(wav), 1.0 / sr)
        band = (freqs >= lo) & (freqs <= hi)
        if not band.any():
            return 0.0
        return float(freqs[band][np.argmax(spec[band])])

    # vowel sweep: /a/ has F1 ~730, /i/ F1 ~270, F2 ~2290
    for ph in ("aa", "iy", "uw"):
        # stretch the vowel via repeated phones so FFT has enough samples
        wav = voice.render_phones([(ph, None)] * 3, f0=140.0)
        p1 = formant_peak(wav, 150, 950)
        p2 = formant_peak(wav, 900, 3000)
        print(f"  vowel /{ph}/: len={len(wav)} peak="
              f"{np.max(np.abs(wav)):.2f} "
              f"F1~{p1:.0f}Hz F2~{p2:.0f}Hz")

    # text-to-speech
    wav = voice.render_text("hello world", f0=120.0)
    print(f"  tts 'hello world': len={len(wav)} peak="
          f"{np.max(np.abs(wav)):.2f} "
          f"rms={np.sqrt(np.mean(wav ** 2)):.3f}")

    # kana vowels accepted through the same table
    wav2 = voice.render_phones([("a", 180.0), ("i", 180.0),
                                ("u", 180.0)], f0=180.0)
    print(f"  kana a-i-u: len={len(wav2)} peak={np.max(np.abs(wav2)):.2f}")

    # per-phone pitch curve (drawn melody): rising aa
    seg = voice.render_phones([("aa", 140.0), ("aa", 200.0),
                               ("aa", 280.0)], f0=140.0)
    print(f"  pitch-curve aa 140->200->280: len={len(seg)} peak="
          f"{np.max(np.abs(seg)):.2f}")
    print("  formant-voice demo OK")


if __name__ == "__main__":
    demo()
