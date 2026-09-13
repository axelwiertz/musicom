# -*- coding: utf-8 -*-
"""Singing-voice synthesis — source-filter vocal-tract model.

A dedicated human-voice virtual instrument. Unlike `formant_voice.py` (a
Klatt-cascade *speech* synthesizer driven by an impulse train), this engine
models the physical chain that produces the characteristic timbre of a
* sung * voice:

    glottal source  ->  vocal tract  ->  radiation
    (asymmetric        (formant          (+6 dB/oct at
     flow derivative)   resonators)       the lips)

The single most important improvement over an impulse-train source is the
**glottal pulse**. Real vocal folds open gradually and snap shut quickly;
the closing produces a sharp negative spike in the volume-velocity
derivative that carries the high harmonics ("brassiness", the "ring" that
separates a voice from a buzz). We use the modified-Rosenberg source from
Klatt & Klatt (1990, KLSYN88), which reproduces this asymmetric open/close.

Chain (per sample, fully vectorized):

  1.  f0 track = base pitch + vibrato (delayed onset) + jitter (random walk)
  2.  glottal-flow derivative g'(t): KLSYN88 asymmetric pulse train at f0
  3.  aspiration: shaped breath noise added to the source (breathy voice)
  4.  vocal tract: cascade of 5 second-order resonators at F1..F5 (the
      vowel), with Klatt bandwidths
  5.  singer's formant: a parallel 2.8-3.2 kHz resonator (Sundberg's "ring",
      what lets a trained voice project over an orchestra)
  6.  radiation: the flow derivative already embodies the +6 dB/oct lip
      characteristic; an optional spectral tilt trims synthetic harshness
  7.  shimmer: per-pulse amplitude micro-perturbation + note envelope

Voice types (soprano/alto/tenor/bass) set a default f0 band and a vocal-tract
length scale (female ~1.18 x male formants), which is what makes a soprano
"ah" brighter than a bass "ah" at the same fundamental.

References:
  - Fant, G. (1960). *Acoustic Theory of Speech Production.*
  - Rosenberg, A. E. (1971). "Effect of glottal pulse shape on the quality
    of natural vowels." J. Acoust. Soc. Am. 49(2B), 583-590.
  - Klatt, D. H. & Klatt, L. C. (1990). "Analysis, synthesis, and perception
    of voice quality variations among female and male talkers." J. Acoust.
    Soc. Am. 87(2), 820-857.
  - Peterson, G. E. & Barney, H. L. (1952). "Control methods used in a study
    of the vowels." J. Acoust. Soc. Am. 24(2), 175-184.
  - Sundberg, J. (1974). "Articulatory interpretation of the 'singing
    formant'." J. Acoust. Soc. Am. 55(4), 838-844.

Usage:
    from sound.synthesis.singing_voice import SingingVoice

    voice = SingingVoice(voice_type="alto")
    wav = voice.render_note(69, dur=1.0, vowel="a")   # A4 "ah"
    phrase = voice.render_phrase([(67, 0.5, "a"), (69, 0.5, "e"),
                                  (71, 1.0, "i")])
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

try:
    import scipy.signal as signal
    _SCIPY = True
except ImportError:  # pragma: no cover
    _SCIPY = False

from ..utils.io import write_wav
from ..utils.pitch import midi_to_freq

__all__ = [
    "VOICE_TYPES", "VOWEL_FORMANTS", "SingingVoice", "render_phrase_wav",
    "demo",
]


# ---------------------------------------------------------------------------
# Vowel formants (Peterson & Barney 1952; F4/F5 after Klatt 1980, male talker).
# Each entry: (F1, F2, F3, F4, F5) in Hz. Bandwidths come from the cascade
# table below (Klatt: B1=90, B2=110, B3=170, B4=250, B5=300 Hz).
# ---------------------------------------------------------------------------

VOWEL_FORMANTS: Dict[str, Tuple[float, float, float, float, float]] = {
    "iy": (270, 2290, 3010, 3600, 4000),   # /i/ see
    "ih": (390, 1990, 2550, 3400, 4000),   # /ɪ/ sit
    "eh": (530, 1840, 2480, 3350, 4000),   # /ɛ/ bet
    "ae": (660, 1720, 2410, 3325, 4000),   # /æ/ cat
    "aa": (730, 1090, 2440, 3300, 4000),   # /ɑ/ father
    "ao": (570, 840, 2410, 3300, 4000),    # /ɔ/ thought
    "uh": (440, 1020, 2240, 3300, 4000),   # /ʊ/ put
    "uw": (300, 870, 2240, 3300, 4000),    # /u/ boot
    "ah": (640, 1190, 2390, 3300, 4000),   # /ʌ/ but
    "er": (490, 1350, 1690, 3300, 4000),   # /ɝ/ bird (r-colored)
    "ax": (500, 1500, 2500, 3400, 4000),   # /ə/ schwa
    # sung / "neutral" vowels, very common in bel-canto (Italian vowels)
    "a":  (730, 1090, 2440, 3300, 4000),   # /a/ (≈ aa)
    "e":  (530, 1840, 2480, 3350, 4000),   # /e/ (≈ eh)
    "i":  (270, 2290, 3010, 3600, 4000),   # /i/ (≈ iy)
    "o":  (570, 840, 2410, 3300, 4000),    # /o/ (≈ ao)
    "u":  (300, 870, 2240, 3300, 4000),    # /u/ (≈ uw)
}

# Klatt cascade resonator bandwidths (Hz), B1..B5.
_BANDWIDTHS = (90.0, 110.0, 170.0, 250.0, 300.0)


# ---------------------------------------------------------------------------
# Voice types: default f0 band (Hz) and vocal-tract length scale. A shorter
# vocal tract (female/child) raises every formant, brightening the timbre at
# the same fundamental — the acoustic basis of "voice type".
# ---------------------------------------------------------------------------

@dataclass
class VoiceProfile:
    name: str
    f0_center: float          # Hz — a typical comfortable singing pitch
    formant_scale: float      # >1 shortens the tract (raises formants)
    singer_formant_hz: float  # the "ring" resonator frequency

    def scale_formants(self, formants):
        return tuple(f * self.formant_scale for f in formants)

    def scale_bandwidths(self):
        return tuple(b * self.formant_scale for b in _BANDWIDTHS)


VOICE_TYPES: Dict[str, VoiceProfile] = {
    "soprano": VoiceProfile("soprano", 440.0, 1.18, 3200.0),
    "alto":    VoiceProfile("alto", 330.0, 1.12, 3000.0),
    "tenor":   VoiceProfile("tenor", 220.0, 1.00, 2800.0),
    "bass":    VoiceProfile("bass", 165.0, 0.92, 2600.0),
    # a neutral "solo voice" default: mid register, mild tract scale
    "solo":    VoiceProfile("solo", 262.0, 1.05, 2900.0),
}


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

class SingingVoice:
    """Source-filter singing-voice synthesizer.

    Parameters
    ----------
    sample_rate : int
        Output sample rate in Hz.
    voice_type : str
        One of VOICE_TYPES (soprano/alto/tenor/bass/solo). Sets the default
        pitch band and vocal-tract scale.
    open_quotient : float
        OQ: fraction of each glottal cycle the folds are open (0.4-0.8).
        Lower = breathier/lighter (more open), higher = pressed/bright.
    speed_quotient : float
        SQ: rise/fall asymmetry of the glottal pulse (1.0-3.0). Higher =
        faster closure = more high-harmonic "ring".
    """
    def __init__(
        self,
        sample_rate: int = 44100,
        voice_type: str = "alto",
        open_quotient: float = 0.65,
        speed_quotient: float = 1.8,
    ):
        if not _SCIPY:
            raise ImportError(
                "SingingVoice needs scipy.signal for the vocal-tract "
                "resonators; install scipy or use formant_voice.FormantVoiceSynth")
        self.sr = int(sample_rate)
        self.profile = VOICE_TYPES[voice_type]
        self.voice_type = voice_type
        self.oq = float(open_quotient)
        self.sq = float(speed_quotient)

    # ------------------------------------------------------------------ source
    def _glottal_flow_derivative(self, f0_inst: np.ndarray,
                                 amp: float = 1.0) -> np.ndarray:
        """Modified-Rosenberg (KLSYN88) glottal-flow derivative pulse train.

        f0_inst: per-sample instantaneous fundamental (Hz). The pulse is an
        asymmetric open (half-cosine rise) / close (sharper fall) cycle; the
        flow DERIVATIVE has a sharp negative spike at glottal closure, which
        is the physical source of the voice's high-frequency "brass".

        Vectorized: phase is accumulated, then the KLSYN88 piecewise shape is
        evaluated from the within-cycle position of each sample.
        """
        sr = self.sr
        n = len(f0_inst)
        # phase in cycles, per sample
        phase = np.cumsum(np.clip(f0_inst, 20.0, 2000.0) / sr) % 1.0
        # period in samples (per sample) and within-cycle time
        period = np.clip(sr / np.clip(f0_inst, 20.0, 2000.0), 2.0, None)
        tau = phase * period              # samples into the current cycle

        # KLSYN88 timings from OQ and SQ
        oq = np.clip(self.oq, 0.3, 0.9)
        sq = np.clip(self.sq, 0.7, 4.0)
        te = oq * period                 # closure sample offset
        tp = te * sq / (sq + 1.0)        # peak-flow sample offset
        tfall = te - tp                  # closing duration

        # Excitation = d/dt of the volume velocity.
        #   rise  (0..tp):   g = 0.5 (1 - cos(pi t/tp))      -> + half-sine
        #   fall  (tp..te):  g = cos(pi (t-tp)/(2 tfall))    -> - quarter-sine
        #   closed(te..T0): g = 0
        # The derivative of the fall phase ends at a negative spike at te.
        out = np.zeros(n, dtype=np.float64)

        rise = tau < tp
        if rise.any():
            tt = tau[rise] / np.clip(tp[rise], 1e-3, None)
            out[rise] = (np.pi / 2.0) * np.sin(np.pi * tt) / \
                np.clip(tp[rise], 1e-3, None)

        fall = (~rise) & (tau < te)
        if fall.any():
            tt = (tau[fall] - tp[fall]) / np.clip(tfall[fall], 1e-3, None)
            out[fall] = -(np.pi / 2.0) * np.sin(np.pi * tt / 2.0) / \
                np.clip(tfall[fall], 1e-3, None)

        return out * amp

    def _vocal_tract_cascade(self, src: np.ndarray, formants: Sequence[float],
                             bandwidths: Sequence[float]) -> np.ndarray:
        """Cascade of 5 second-order resonators at F1..F5.

        Each section: H(z) = (1 - a1 - a2) / (1 - a1 z^-1 - a2 z^-2) so the
        DC/peak gain is unity — the cascade stays stable and the spectral
        envelope follows the formant peaks without runaway gain.
        """
        y = src.astype(np.float64)
        for f, bw in zip(formants, bandwidths):
            f = float(f)
            if f <= 40.0 or f >= 0.45 * self.sr:
                continue
            r = np.exp(-np.pi * bw / self.sr)
            a1 = 2.0 * r * np.cos(2.0 * np.pi * f / self.sr)
            a2 = -(r * r)
            b0 = 1.0 - a1 - a2
            y = signal.lfilter([b0], [1.0, -a1, -a2], y)
        return y

    def _singer_formant(self, x: np.ndarray, center_hz: float,
                        q: float = 6.0) -> np.ndarray:
        """Parallel resonator adding the 'singer's formant' (vocal ring)."""
        if center_hz <= 40.0 or center_hz >= 0.45 * self.sr:
            return x
        bw = center_hz / q
        r = np.exp(-np.pi * bw / self.sr)
        a1 = 2.0 * r * np.cos(2.0 * np.pi * center_hz / self.sr)
        a2 = -(r * r)
        b0 = 1.0 - a1 - a2
        # parallel: add a fraction of the resonated copy
        y = signal.lfilter([b0], [1.0, -a1, -a2], x)
        return x + 0.35 * y

    # -------------------------------------------------------------- helpers
    def _f0_track(self, f0: float, n: int, vibrato_hz: float = 5.5,
                  vibrato_semitones: float = 0.45, vibrato_delay: float = 0.25,
                  vibrato_ramp: float = 0.3, jitter_semitones: float = 0.05,
                  seed: int = 0) -> np.ndarray:
        """Instantaneous f0: base + delayed vibrato + random-walk jitter."""
        t = np.arange(n) / self.sr
        # vibrato with delayed onset and a linear ramp-in
        delay_n = int(vibrato_delay * self.sr)
        ramp = np.clip((np.arange(n) - delay_n) / (vibrato_ramp * self.sr),
                       0.0, 1.0)
        vib = vibrato_semitones * ramp * np.sin(2.0 * np.pi * vibrato_hz * t)
        # jitter: tiny smoothed random walk (pitch irregularity)
        rng = np.random.default_rng(seed)
        steps = max(1, n // 64)
        coarse = rng.normal(0.0, jitter_semitones, size=n // steps + 2)
        jitter = np.interp(np.arange(n), np.arange(len(coarse)) * steps, coarse)
        # first-order smooth so jitter is a wobble, not sample noise
        alpha = 0.02
        jitter = signal.lfilter([alpha], [1.0, -(1.0 - alpha)], jitter)
        return f0 * 2.0 ** ((vib + jitter) / 12.0)

    def _note_envelope(self, n: int, attack: float = 0.04,
                       release: float = 0.09, legato: bool = False) -> np.ndarray:
        env = np.ones(n, dtype=np.float64)
        a = min(int(attack * self.sr), n)
        r = min(int(release * self.sr), n)
        if a > 0 and not legato:
            env[:a] = np.linspace(0.0, 1.0, a)
        if r > 0:
            env[-r:] *= np.linspace(1.0, 0.0, r)
        return env

    # ---------------------------------------------------------------- render
    def render_note(
        self,
        midi: int,
        dur: float,
        vowel: str = "a",
        amp: float = 0.9,
        vibrato_hz: float = 5.5,
        vibrato_semitones: float = 0.45,
        aspiration: float = 0.0,
        shimmer: float = 0.03,
        seed: int = 0,
    ) -> np.ndarray:
        """Render one sung note to mono float audio in [-1, 1].

        midi : MIDI pitch (f0 = midi_to_freq(midi)).
        dur  : seconds.
        vowel: VOWEL_FORMANTS key ('a','e','i','o','u','iy','eh',...).
        aspiration: 0..1 breath-noise mix (0 = clean, 1 = breathy).
        shimmer: 0..1 amplitude micro-perturbation depth.
        """
        vowel = vowel if vowel in VOWEL_FORMANTS else "a"
        formants = self.profile.scale_formants(VOWEL_FORMANTS[vowel])
        bws = self.profile.scale_bandwidths()
        f0 = midi_to_freq(midi)
        n = max(1, int(self.sr * dur))

        f0_inst = self._f0_track(f0, n, vibrato_hz=vibrato_hz,
                                 vibrato_semitones=vibrato_semitones,
                                 seed=seed)
        src = self._glottal_flow_derivative(f0_inst, amp=amp)

        # aspiration: shaped breath noise mixed into the source
        if aspiration > 0.0:
            rng = np.random.default_rng(seed + 1)
            noise = rng.standard_normal(n) * 0.5
            # breath noise is concentrated 1-5 kHz (turbulence), highpass
            noise = signal.lfilter([1.0, -1.0], [1.0, -0.95], noise)
            src = src + aspiration * 0.6 * noise

        out = self._vocal_tract_cascade(src, formants, bws)
        out = self._singer_formant(out, self.profile.singer_formant_hz)

        # shimmer: per-pulse amplitude wobble (voice "richness")
        if shimmer > 0.0:
            rng = np.random.default_rng(seed + 2)
            steps = max(1, n // 64)
            coarse = rng.normal(1.0, shimmer, size=n // steps + 2)
            sh = np.interp(np.arange(n), np.arange(len(coarse)) * steps, coarse)
            out = out * sh

        out = out * self._note_envelope(n)

        pk = np.max(np.abs(out))
        if pk > 1e-12:
            out = out / pk * min(1.0, amp)
        return out.astype(np.float32)

    def render_phrase(
        self,
        notes: Sequence[Tuple[int, float, str]],
        amp: float = 0.9,
        legato: bool = True,
        aspiration: float = 0.0,
        seed: int = 0,
    ) -> np.ndarray:
        """Render a sequence of (midi, dur_sec, vowel) notes to mono audio.

        legato: crossfade note boundaries ~15 ms so the line glides like a
        single breath, rather than re-attacking each syllable.
        """
        parts: List[np.ndarray] = []
        for i, (midi, dur, vowel) in enumerate(notes):
            seg = self.render_note(midi, dur, vowel, amp=amp,
                                   aspiration=aspiration, seed=seed + i)
            parts.append(seg)
        if not parts:
            return np.zeros(0, dtype=np.float32)
        if not legato or len(parts) == 1:
            return np.concatenate(parts).astype(np.float32)

        # 15 ms crossfade between adjacent notes
        xf = int(0.015 * self.sr)
        out = parts[0]
        for seg in parts[1:]:
            if xf >= len(out) or xf >= len(seg):
                out = np.concatenate([out, seg])
                continue
            fade = np.linspace(0.0, 1.0, xf)
            tail = out[-xf:] * (1.0 - fade)
            head = seg[:xf] * fade
            out = np.concatenate([out[:-xf], tail + head, seg[xf:]])
        pk = np.max(np.abs(out))
        if pk > 1e-12:
            out = out / pk * min(1.0, amp)
        return out.astype(np.float32)

    def render_unit(self, unit, output_path: str, vowels=None,
                    ticks_per_beat: int = 480, bpm: int = 120,
                    aspiration: float = 0.0) -> str:
        """Render a MusicUnit melody as a monophonic singing-voice WAV.

        Mirrors FormantVocalGuide.render_melody so it drops into a composition
        pipeline: each audible event's pitch + tick span becomes a sung note.
        """
        sec_per_tick = 60.0 / (bpm * ticks_per_beat)
        events = [e for e in unit.events if e.pitch > 0]
        vowels = vowels or ["a"]
        notes = []
        for i, e in enumerate(events):
            dur = (e.end_tick - e.start_tick) * sec_per_tick
            if dur <= 0:
                continue
            notes.append((e.pitch, dur, vowels[i % len(vowels)]))
        wav = self.render_phrase(notes, aspiration=aspiration)
        write_wav(output_path, wav, self.sr)
        return output_path


# ---------------------------------------------------------------------------
# Convenience
# ---------------------------------------------------------------------------

def render_phrase_wav(notes: Sequence[Tuple[int, float, str]],
                      output_path: str, voice_type: str = "alto",
                      sample_rate: int = 44100, aspiration: float = 0.0) -> str:
    """One-call helper: render (midi, dur, vowel) -> WAV file."""
    voice = SingingVoice(sample_rate=sample_rate, voice_type=voice_type)
    wav = voice.render_phrase(notes, aspiration=aspiration)
    write_wav(output_path, wav, sample_rate)
    return output_path


def demo() -> None:
    """Render a few vowels + a phrase and print spectral evidence.

    Formant peaks should land near the vowel's F1/F2 (e.g. /a/ F1~730,
    /i/ F1~270 F2~2290 scaled by the voice profile).
    """
    sr = 44100
    voice = SingingVoice(sample_rate=sr, voice_type="alto")

    def _peak(wav, lo, hi):
        spec = np.abs(np.fft.rfft(wav * np.hanning(len(wav))))
        freqs = np.fft.rfftfreq(len(wav), 1.0 / sr)
        band = (freqs >= lo) & (freqs <= hi)
        return float(freqs[band][np.argmax(spec[band])]) if band.any() else 0.0

    for vowel in ("a", "i", "u"):
        wav = voice.render_note(57, 0.8, vowel)          # A3
        p1 = _peak(wav, 100, 1200)
        p2 = _peak(wav, 1200, 3500)
        print(f"  vowel /{vowel}/: len={len(wav)} "
              f"peak={np.max(np.abs(wav)):.2f} "
              f"F1~{p1:.0f}Hz F2~{p2:.0f}Hz")

    # a short phrase
    phrase = [(60, 0.4, "a"), (62, 0.4, "a"), (64, 0.4, "e"),
              (65, 0.8, "i"), (64, 0.4, "o"), (62, 0.4, "u"),
              (60, 1.0, "a")]
    wav = voice.render_phrase(phrase)
    print(f"  phrase: len={len(wav)} rms={np.sqrt(np.mean(wav ** 2)):.3f}")
    print("  singing-voice demo OK")


if __name__ == "__main__":
    demo()
