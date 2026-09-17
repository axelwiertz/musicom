"""Through-zero FM oscillator with per-note waveform stepping — Korg Prologue
"Elixir Volume 1" style (TZFM / STEPr user oscillators).

Replicable logic from the Synthtopia item "Korg Prologue Synthesizers Get
Expanded Synthesis Capabilities" (2026-09-10), describing Scott McAuley's Elixir
Volume 1 user-oscillator collection:

  * **TZFM** — "built with dual waveforms A & B — A has 46 wave shapes, B has 44,
    TZFM can be sent A to B, or B to A, with depth control, adjustable Ringmod,
    and adjustable Bitcrush … the shape knob fully left is Wave A, centre is Wave
    A & B mixed, fully right is Wave B."
  * **STEPr** — like TZFM, "but has the additional feature of being able to step
    through each of A & B's waveforms **per note pressed**, you can step A only,
    or B only, or both A & B together."

What is replicated here:
- ``build_bank_a`` / ``build_bank_b``: the 46 + 44 single-cycle wavetables,
  generated procedurally (sine, saw, ramp, triangle, pulse/PWM families, hard-sync
  sweeps, and harmonic-stack spectra with varying rolloff/even-odd balance) — the
  actual Elixir tables are proprietary, the *bank shape* is what matters.
- **Real through-zero FM**: the modulator is applied as a *phase offset*
  ``phi_carrier = accumulated_phase + depth * modulator[n]``.  Because the
  modulator's own waveform swings negative, the carrier phase instantaneously
  reverses direction — that is through-zero behaviour, and it is why TZFM sounds
  different from ordinary (AC-coupled) FM.
- **Mod direction** ``tzfm="A->B" | "B->A" | "off"``, **shape** crossfade
  (A → A/B mix → B, as on the hardware), **ringmod mix** (multiply carrier by
  modulator) and **bitcrush mix** (bit-depth quantization, the digital "dirt"
  the Elixir description calls out).
- ``SteppedOscillator`` (STEPr): per-note waveform stepping over both banks; the
  step mode selects A only, B only, or A and B together, and each note advances
  the index — so a held melody walks through the whole bank sequentially.

Not replicated: the compiled Prologue user-oscillator SDK binaries, the exact
46/44 proprietary tables, the hardware panel.

Usage:
    from sound.synthesis.tzfm import TZFMVoice, SteppedOscillator, BANKS

    v = TZFMVoice(sample_rate=44100)
    wav = v.render_note(57, 0.7, tzfm="A->B", depth=0.6, ringmod=0.3,
                        bitcrush=0.25, shape=0.5)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = [
    "TZFMVoice",
    "SteppedOscillator",
    "build_bank_a",
    "build_bank_b",
    "render_bank",
    "WAVE_SIZE",
    "midi_to_freq",
]

WAVE_SIZE = 2048
A440 = 440.0


def midi_to_freq(note: float) -> float:
    """Equal-tempered MIDI note (A4 = 440 Hz) -> Hz."""
    return A440 * (2.0 ** ((float(note) - 69.0) / 12.0))


def _phase(n: int = WAVE_SIZE) -> np.ndarray:
    return np.arange(n) / float(n)


def build_bank_a(n: int = 46) -> List[np.ndarray]:
    """Bank A: ``n`` single-cycle shapes (hard/edgy family)."""
    p = _phase(WAVE_SIZE)
    out: List[np.ndarray] = []
    out.append(np.sin(2 * np.pi * p))                       # 0 sine
    out.append(2.0 * p - 1.0)                               # 1 saw up
    out.append(1.0 - 2.0 * p)                               # 2 saw down
    out.append(np.sign(np.sin(2 * np.pi * p)))              # 3 square
    out.append(4.0 * np.abs(p - 0.5) - 1.0)                 # 4 triangle
    # PWM family
    for duty in np.linspace(0.05, 0.95, 12):
        out.append(np.where(p < duty, 1.0, -1.0))
    # hard-sync sweep: ramp reset early
    for frac in np.linspace(0.15, 0.95, 9):
        w = np.zeros(WAVE_SIZE)
        k = max(2, int(frac * WAVE_SIZE))
        w[:k] = np.linspace(-1, 1, k, endpoint=False)
        w[k:] = np.linspace(-1, 1, WAVE_SIZE - k, endpoint=False)
        out.append(w)
    # harmonic stacks: odd-only, even-tilted, bright
    for odd_only, rolloff, limit in ((True, 1.0, 24), (False, 1.0, 24),
                                     (True, 0.7, 32), (False, 0.7, 32),
                                     (True, 1.4, 16), (False, 1.4, 16)):
        h = np.zeros(WAVE_SIZE)
        for k in range(1, limit + 1):
            if odd_only and k % 2 == 0:
                continue
            h += np.sin(2 * np.pi * p * k) / (k ** rolloff)
        out.append(h)
    # folded / wavefolded shapes
    for drive in (1.5, 2.5, 4.0, 6.0, 9.0):
        out.append(np.sin(np.pi * np.clip(drive * (2.0 * p - 1.0), -8, 8) / 2.0))
    while len(out) < n:                                     # fill with detune-ish
        i = len(out)
        out.append(np.sin(2 * np.pi * p * (1 + 0.01 * i)))
    return [_norm(w) for w in out[:n]]


def build_bank_b(n: int = 44) -> List[np.ndarray]:
    """Bank B: ``n`` single-cycle shapes (softer / spectral family)."""
    p = _phase(WAVE_SIZE)
    out: List[np.ndarray] = []
    for rolloff in np.linspace(0.4, 2.2, 14):               # 14 saw-stack shades
        h = np.zeros(WAVE_SIZE)
        for k in range(1, 41):
            h += np.sin(2 * np.pi * p * k) / (k ** rolloff)
        out.append(h)
    for k0 in range(2, 12):                                 # 10 octave-shifted stacks
        h = np.zeros(WAVE_SIZE)
        for k in range(1, 25):
            h += np.sin(2 * np.pi * p * k * k0) / k
        out.append(h)
    for duty in np.linspace(0.1, 0.9, 8):                   # 8 rounded pulses
        out.append(np.tanh(2.5 * np.where(p < duty, 1.0, -1.0)))
    for m in range(1, 13):                                  # 12 formant-ish
        out.append(np.sin(2 * np.pi * p) * (0.6 + 0.4 * np.cos(2 * np.pi * m * p)))
    while len(out) < n:
        i = len(out)
        out.append(np.cos(2 * np.pi * p * (1 + 0.005 * i)))
    return [_norm(w) for w in out[:n]]


def _norm(w: np.ndarray) -> np.ndarray:
    peak = float(np.max(np.abs(w)))
    return w / peak if peak > 1e-12 else w


BANKS: Dict[str, int] = {"A": 46, "B": 44}


def render_bank(bank: str = "A") -> List[np.ndarray]:
    """Return bank ``A`` (46 shapes) or ``B`` (44 shapes)."""
    if bank.upper() == "A":
        return build_bank_a(BANKS["A"])
    if bank.upper() == "B":
        return build_bank_b(BANKS["B"])
    raise ValueError("bank must be 'A' or 'B'")


def _lookup(table: np.ndarray, phase: np.ndarray) -> np.ndarray:
    """Linear-interpolated wavetable lookup for an arbitrary phase array."""
    n = table.size
    x = np.mod(phase, 1.0) * n
    i0 = np.floor(x).astype(np.int64) % n
    i1 = (i0 + 1) % n
    frac = x - np.floor(x)
    return table[i0] * (1.0 - frac) + table[i1] * frac


@dataclass
class TZFMParams:
    """One TZFM/STEPr patch."""
    wave_a: int = 0
    wave_b: int = 0
    shape: float = 0.0        # 0 = A only, 0.5 = A+B mixed, 1 = B only
    tzfm: str = "off"         # "A->B", "B->A" or "off"
    depth: float = 0.0        # TZFM depth, in carrier cycles (can be > 1)
    ringmod: float = 0.0      # 0..1 dry/ring blend
    bitcrush: float = 0.0     # 0..1 quantization amount
    crush_bits: int = 8       # bit depth at bitcrush = 1
    ratio: float = 1.0        # modulator : carrier frequency ratio


class TZFMVoice:
    """Two-bank through-zero FM oscillator with ringmod + bitcrush.

    Args:
        sample_rate: sample rate in Hz.
        bank_a / bank_b: optional prebuilt wavetable banks (else built lazily).
    """

    def __init__(self, sample_rate: int = 44100,
                 bank_a: Optional[Sequence[np.ndarray]] = None,
                 bank_b: Optional[Sequence[np.ndarray]] = None):
        self.sr = int(sample_rate)
        self.bank_a: List[np.ndarray] = list(bank_a) if bank_a is not None else build_bank_a()
        self.bank_b: List[np.ndarray] = list(bank_b) if bank_b is not None else build_bank_b()

    # ----------------------------------------------------------------- helpers
    def _shape_mix(self, params: TZFMParams) -> Tuple[np.ndarray, np.ndarray]:
        wa = self.bank_a[params.wave_a % len(self.bank_a)]
        wb = self.bank_b[params.wave_b % len(self.bank_b)]
        return wa, wb

    def _osc(self, table: np.ndarray, freq: float, n: int) -> Tuple[np.ndarray, np.ndarray]:
        """Return ``(wave, cycles)`` where ``cycles`` is the un-wrapped phase."""
        cycles = np.arange(n) * (float(freq) / self.sr)
        return _lookup(table, cycles), cycles

    # ------------------------------------------------------------------ render
    def render(self, freq: float, duration: float = 1.0,
               params: Optional[TZFMParams] = None,
               amp: float = 0.8, attack: float = 0.003,
               release: float = 0.05) -> np.ndarray:
        """Render one note; returns a mono float array.

        The carrier phase is ``carrier_cycles + depth * modulator``, so a negative
        modulator excursion drives the phase *backwards* — genuine through-zero FM.
        """
        params = params or TZFMParams()
        n = max(1, int(duration * self.sr))
        wa, wb = self._shape_mix(params)

        if params.tzfm == "off":
            dry = _lookup(wa, np.arange(n) * (freq / self.sr))
            sig = dry if params.shape < 0.5 else dry  # single-table path
            # shape knob still blends A/B in the no-FM case
            mix = (1.0 - params.shape) * _lookup(wa, np.arange(n) * (freq / self.sr)) + \
                  params.shape * _lookup(wb, np.arange(n) * (freq / self.sr))
            sig = mix
            mod = None
            carrier_cycles = np.arange(n) * (freq / self.sr)
        else:
            carrier_tbl, mod_tbl = (wa, wb) if params.tzfm == "A->B" else (wb, wa)
            carrier_cycles = np.arange(n) * (freq / self.sr)
            mod, mod_cycles = self._osc(mod_tbl, freq * float(params.ratio), n)
            phase = carrier_cycles + float(params.depth) * mod
            sig = _lookup(carrier_tbl, phase)
            # shape knob crossfades the dry A/B blend on top of the FM result
            blend = (1.0 - params.shape) * _lookup(wa, carrier_cycles) + \
                    params.shape * _lookup(wb, carrier_cycles)
            sig = 0.5 * sig + 0.5 * blend

        if mod is None:
            mod = _lookup(wb, np.arange(n) * (freq / self.sr))

        if params.ringmod > 0.0:
            ring = sig * mod
            sig = (1.0 - params.ringmod) * sig + params.ringmod * ring

        if params.bitcrush > 0.0:
            bits = max(2, int(round(params.crush_bits * (1.0 - params.bitcrush) + 1)))
            q = 2.0 ** (bits - 1)
            crushed = np.round(np.clip(sig, -1.0, 1.0) * q) / q
            sig = (1.0 - params.bitcrush) * sig + params.bitcrush * crushed

        env = np.ones(n)
        na, nr = min(n, int(attack * self.sr)), min(n, int(release * self.sr))
        if na:
            env[:na] = np.linspace(0.0, 1.0, na)
        if nr:
            env[n - nr:] = np.linspace(1.0, 0.0, nr)
        sig = _norm(sig) * amp * env
        return sig.astype(np.float64)

    def render_note(self, midi_note: float, duration: float = 0.5,
                    **kwargs) -> np.ndarray:
        """Convenience wrapper: MIDI note in, mono buffer out."""
        return self.render(midi_to_freq(midi_note), duration, **kwargs)


class SteppedOscillator(TZFMVoice):
    """STEPr behaviour: advance the wavetable per *note press*.

    Args:
        step_a / step_b: how many shapes to advance in each bank per note
            (0 = freeze that bank).
        step_mode: "A", "B" or "AB" — matching the hardware's step-A-only /
            step-B-only / both selection.
    """

    def __init__(self, sample_rate: int = 44100, step_a: int = 1,
                 step_b: int = 1, step_mode: str = "AB", **kwargs):
        super().__init__(sample_rate=sample_rate, **kwargs)
        self.step_a = int(step_a)
        self.step_b = int(step_b)
        mode = str(step_mode).upper()
        if mode not in ("A", "B", "AB"):
            raise ValueError("step_mode must be 'A', 'B' or 'AB'")
        self.step_mode = mode
        self.note_count = 0

    def next_params(self, base: Optional[TZFMParams] = None) -> TZFMParams:
        """Return the patch for the *next* note and advance the bank indices."""
        base = base or TZFMParams()
        p = TZFMParams(**vars(base))
        idx = self.note_count
        if self.step_mode in ("A", "AB"):
            p.wave_a = (base.wave_a + idx * self.step_a) % len(self.bank_a)
        if self.step_mode in ("B", "AB"):
            p.wave_b = (base.wave_b + idx * self.step_b) % len(self.bank_b)
        self.note_count += 1
        return p

    def render_melody(self, notes: Sequence[Tuple[float, float, float]],
                      base: Optional[TZFMParams] = None,
                      tail: float = 0.2, reset: bool = True) -> Tuple[np.ndarray, List[int]]:
        """Render ``[(midi_note, start, dur), ...]``, stepping a bank per note.

        Returns ``(audio, wave_a_indices)`` so the caller can verify the stepping.
        """
        base = base or TZFMParams()
        if reset:
            self.note_count = 0
        total = max((s + d for _, s, d in notes), default=1.0) + tail
        buf = np.zeros(int(total * self.sr), dtype=np.float64)
        used: List[int] = []
        for m, start, dur in notes:
            p = self.next_params(base)
            used.append(p.wave_a)
            seg = self.render_note(m, dur, params=p)
            i0 = int(start * self.sr)
            i1 = min(len(buf), i0 + len(seg))
            if i1 > i0:
                buf[i0:i1] += seg[: i1 - i0]
        return buf, used


# ------------------------------------------------------------------------ demo
def demo() -> str:
    """Verify banks, through-zero phase reversal, ringmod, bitcrush, stepping."""
    sr = 44100
    a = build_bank_a()
    b = build_bank_b()
    print(f"bank A: {len(a)} shapes  bank B: {len(b)} shapes  "
          f"(Elixir spec: A=46, B=44)")
    assert len(a) == 46 and len(b) == 44
    assert all(len(w) == WAVE_SIZE for w in a + b)

    v = TZFMVoice(sample_rate=sr)
    f0 = midi_to_freq(57)

    # --- through zero: with a small depth the carrier phase reverses direction
    n_dbg = 400
    depth = 2.0
    carrier = np.arange(n_dbg) * (f0 / sr)
    mod_tbl = v.bank_b[0]
    mod = _lookup(mod_tbl, np.arange(n_dbg) * (f0 / sr))
    phase = carrier + depth * mod
    dphase = np.diff(phase)
    neg = int(np.sum(dphase < 0))
    print(f"through-zero: {neg}/{len(dphase)} samples with NEGATIVE instantaneous "
          f"phase slope at depth={depth} -> {'reversal present' if neg else 'NONE'}")
    assert neg > 0, "no through-zero reversal"

    base = TZFMParams(wave_a=1, wave_b=0, tzfm="A->B", depth=0.9, ratio=1.0)
    fm = v.render(f0, 0.5, base)
    tz = v.render(f0, 0.5, TZFMParams(wave_a=1, wave_b=0, tzfm="B->A", depth=0.9))
    off = v.render(f0, 0.5, TZFMParams(wave_a=1, wave_b=0, tzfm="off"))
    print(f"render: A->B peak={np.max(np.abs(fm)):.3f} B->A peak="
          f"{np.max(np.abs(tz)):.3f} off peak={np.max(np.abs(off)):.3f} "
          f"finite={np.all(np.isfinite(fm))}")
    assert not np.allclose(fm, tz), "modulation direction must change the output"

    def flat(x):
        X = np.abs(np.fft.rfft(x * np.hanning(x.size))) + 1e-12
        return float(np.exp(np.mean(np.log(X))) / np.mean(X))

    print(f"  spectral flatness: off={flat(off):.4f}  TZFM A->B={flat(fm):.4f} "
          f"(FM must add partials)")
    assert flat(fm) > flat(off)

    ring = v.render(f0, 0.5, TZFMParams(wave_a=0, wave_b=0, ringmod=1.0))
    print(f"  ringmod=1 RMS={np.sqrt(np.mean(ring ** 2)):.4f} "
          f"differs from dry: {not np.allclose(ring, off)}")
    assert not np.allclose(ring, off)

    clean = v.render(f0, 0.3, TZFMParams(wave_a=0, wave_b=0))
    crush = v.render(f0, 0.3, TZFMParams(wave_a=0, wave_b=0, bitcrush=1.0,
                                         crush_bits=4))
    print(f"  distinct levels: clean={len(np.unique(np.round(clean, 6)))} "
          f"bitcrush(4-bit)={len(np.unique(np.round(crush, 6)))}")
    assert len(np.unique(np.round(crush, 6))) < len(np.unique(np.round(clean, 6)))

    # --- STEPr: per-note waveform stepping
    stepper = SteppedOscillator(sample_rate=sr, step_a=1, step_b=1, step_mode="AB")
    mel = [(55, 0.0, 0.25), (57, 0.25, 0.25), (59, 0.5, 0.25), (60, 0.75, 0.25)]
    audio, used_a = stepper.render_melody(mel, TZFMParams(tzfm="A->B", depth=0.5))
    print(f"STEPr melody: len={len(audio)} peak={np.max(np.abs(audio)):.3f} "
          f"bank-A indices stepped per note: {used_a}")
    assert used_a == [0, 1, 2, 3]

    stepper2 = SteppedOscillator(sample_rate=sr, step_mode="A", step_a=2)
    print("  (mode) step A only ->  ", end="")
    _, used2 = stepper2.render_melody(mel)
    print(f"indices {used2} (stride 2)")
    assert used2 == [0, 2, 4, 6]

    stepper3 = SteppedOscillator(sample_rate=sr, step_mode="B", step_b=3)
    print("  (mode) step B only ->  ", end="")
    _, used3 = stepper3.render_melody(mel)
    print(f"bank-A frozen at {used3} (B bank advances instead)")
    assert used3 == [0, 0, 0, 0]
    print("  tzfm demo OK")
    return "ok"


if __name__ == "__main__":
    demo()
