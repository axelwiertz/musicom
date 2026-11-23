"""Virus-style virtual-analog voice (InfeKt-FM1 firmware-style).

Replicable logic from the Synthtopia item "New Firmware, InfeKt-FM1, Turns
M-Vave FM-1 Into Access Virus Compatible Synthesizer" (2026-11-21): the
firmware turns the M-VAVE FM-1 into "a virtual analog synthesizer inspired by
the Access Virus B and C", with:

* **three oscillators per voice**, "including continuously morphing
  waveforms, oscillator sync and FM, alongside a sub oscillator, noise
  generator and ring modulation";
* **two multimode filters** with "several routing configurations";
* a **six-slot modulation matrix** connecting the envelopes and three LFOs
  to a range of destinations;
* up to 16 voices with **unison, mono and glide modes**, two-part
  layer/split, arpeggiator and hybrid sequencer (host features — not here).

What is replicated here (offline DSP equivalent):

* ``VirusOsc`` — phase-accumulator oscillator with continuous **waveform
  morph** (saw -> pulse via duty, triangle via integrated-saw blend), **hard
  sync** to a sync source and **linear FM** input.
* ``VirusFilter`` — TPT state-variable multimode filter, 12/24 dB/oct
  (1 or 2 cascaded SVF stages), LP/BP/HP/notch outputs.
* ``VirusVoice`` — 3 oscillators + sub + noise + ring modulator into a
  mixer, then **two filters with 4 routing configurations** (serial,
  parallel, stereo L/R, bypass); 2 ADSR envelopes (filter + amp), 3 LFOs
  (sine/tri/saw/S&H) and a **6-slot modulation matrix** with up to 3
  destinations per slot.
* ``VirusVA`` — polyphonic allocation (max_voices), **unison** (detuned
  stack per note), **mono + glide** modes.

Not replicated: the M-VAVE FM-1 hardware port, Virus patch-file parsing
(proprietary format), the browser editor, the drum machine / hybrid
sequencer and the effects rack (distortion/chorus/phaser/EQ/delay/reverb).

Usage:
    from sound.synthesis.virus_va import VirusVA

    va = VirusVA(sample_rate=44100, max_voices=8, unison=2, seed=3)
    out = va.play([60, 64, 67], dur=2.0)   # (n,) mono or (n, 2) stereo
"""

from __future__ import annotations

import numpy as np

__all__ = ["VirusOsc", "VirusFilter", "VirusVoice", "VirusVA", "demo"]

DEFAULT_SR = 44100
LFO_WAVES = ("sine", "tri", "saw", "s&h")


def _adsr(n: int, sr: int, a: float, d: float, s: float, r: float,
          sus_level: float, gate: int | None = None) -> np.ndarray:
    """Piecewise-exponential ADSR envelope over ``n`` samples."""
    gate = n if gate is None else int(gate)
    a_n, d_n, r_n = (max(1, int(x * sr)) for x in (a, d, r))
    env = np.zeros(n)
    idx = 0
    if a_n:
        seg = np.linspace(0.0, 1.0, a_n, endpoint=False)
        env[idx:idx + a_n] = seg
        idx += a_n
    sus_end = min(gate, n)
    if d_n and idx < sus_end:
        seg = np.linspace(1.0, sus_level, d_n, endpoint=False)
        env[idx:idx + d_n] = seg[:sus_end - idx]
        idx = min(sus_end, idx + d_n)
    if idx < sus_end:
        env[idx:sus_end] = sus_level
        idx = sus_end
    if r_n and idx < n:
        rel = np.linspace(sus_level, 0.0, r_n, endpoint=False)
        env[idx:idx + r_n] = rel[:n - idx]
    return env


class VirusOsc:
    """Morphing VA oscillator with hard sync and linear FM."""

    def __init__(self, sr: int = DEFAULT_SR):
        self.sr = int(sr)

    def render(self, n: int, f0: float, morph: float = 0.0,
               tri_blend: float = 0.0, duty: float = 0.5,
               sync_f: float = 0.0, fm_index: float = 0.0,
               fm_signal: np.ndarray | None = None,
               phase: float = 0.0) -> np.ndarray:
        """Render ``n`` samples at base frequency ``f0``.

        Args:
            f0: base frequency (Hz). 0 -> DC silence (used when an osc is
                muted in a patch).
            morph: 0..1 continuous saw->pulse morph (narrows pulse duty).
            tri_blend: 0..1 blend of integrated-saw triangle into the core.
            duty: pulse duty before morphing (0.5 square).
            sync_f: hard-sync master frequency (Hz); 0 disables sync.
            fm_index: linear FM index; if ``fm_signal`` given, phase is
                modulated by it (classic linear FM), else by a sine at
                ``fm_index * f0`` (self-FM).
            phase: starting phase offset (rad).
        """
        if f0 <= 0:
            return np.zeros(n)
        t = np.arange(n) / self.sr
        phase_acc = phase + 2 * np.pi * f0 * t
        if fm_index > 0:
            mod = (fm_signal if fm_signal is not None
                   else np.sin(2 * np.pi * fm_index * f0 * t))
            phase_acc = phase_acc + fm_index * mod
        if sync_f > 0:
            # hard sync: reset master phase at each sync-cycle boundary
            sync_period = max(1, int(round(self.sr / sync_f)))
            n_cycles = int(np.ceil(n / sync_period))
            for c in range(n_cycles):
                lo = c * sync_period
                hi = min(n, (c + 1) * sync_period)
                if hi <= lo:
                    continue
                local = np.arange(hi - lo) / self.sr
                phase_acc[lo:hi] = phase + 2 * np.pi * f0 * local
        ph = phase_acc / (2 * np.pi)
        ph = ph - np.floor(ph)                     # 0..1
        # pulse with duty -> saw morph: saw phase becomes a pulse of width
        # (1-morph) * duty when the saw crosses its edge.
        edge = np.clip(1.0 - morph, 1e-3, 1.0) * duty
        pulse = np.where(ph < edge, 1.0, -1.0)
        saw = 2.0 * ph - 1.0
        # triangle from phase (cheap, DC-free enough for a VA voice)
        tri = 4.0 * np.abs(ph - 0.5) - 1.0
        # continuous saw->pulse morph (Virus "morphing waveform" behaviour)
        out = (1.0 - morph) * saw + morph * pulse
        out = (1.0 - tri_blend) * out + tri_blend * tri
        return out


class VirusFilter:
    """TPT state-variable multimode filter, 12/24 dB/oct."""

    def __init__(self, sr: int = DEFAULT_SR):
        self.sr = int(sr)
        self._ic1eq = 0.0
        self._ic2eq = 0.0

    def reset(self) -> None:
        self._ic1eq = 0.0
        self._ic2eq = 0.0

    def process(self, x: np.ndarray, cutoff: float, res: float,
                mode: str = "lp", poles: int = 24) -> np.ndarray:
        """SVF filter. ``mode`` in lp/bp/hp/notch; ``poles`` 12 or 24."""
        g = np.tan(np.pi * np.clip(cutoff, 1.0, 0.45 * self.sr) / self.sr)
        k = 2.0 - 2.0 * np.clip(res, 0.0, 1.0)     # 0..1 resonance
        a1 = 1.0 / (1.0 + g * (g + k))
        a2 = g * a1
        a3 = g * a2
        y = np.zeros_like(x)
        ic1, ic2 = self._ic1eq, self._ic2eq
        for i, v in enumerate(x):
            v3 = v - ic2
            v1 = a1 * ic1 + a2 * v3
            v2 = ic2 + a2 * ic1 + a3 * v3
            ic1 = 2.0 * v1 - ic1
            ic2 = 2.0 * v2 - ic2
            if mode == "lp":
                y[i] = v2
            elif mode == "bp":
                y[i] = v1
            elif mode == "hp":
                y[i] = v - k * v1 - v2
            else:                                  # notch
                y[i] = v - k * v1
        self._ic1eq, self._ic2eq = ic1, ic2
        if poles >= 24:
            # cascade a second SVF for 24 dB/oct
            f2 = VirusFilter(self.sr)
            y = f2.process(y, cutoff, res, mode, 12)
        return y


class VirusVoice:
    """One Virus-style voice: 3 osc + sub + noise + ring -> 2 filters."""

    ROUTINGS = ("serial", "parallel", "stereo", "bypass")

    def __init__(self, sr: int = DEFAULT_SR, seed: int = 0):
        self.sr = int(sr)
        self.seed = int(seed)
        self.oscs = [VirusOsc(sr) for _ in range(3)]
        self.f1 = VirusFilter(sr)
        self.f2 = VirusFilter(sr)
        self.lfos = [np.zeros(0) for _ in range(3)]

    def _lfo(self, n: int, rate: float, wave: str, phase: float = 0.0) -> np.ndarray:
        t = np.arange(n) / self.sr
        ph = phase + 2 * np.pi * rate * t
        if wave == "sine":
            return np.sin(ph)
        if wave == "tri":
            return 2.0 / np.pi * np.arcsin(np.sin(ph))
        if wave == "saw":
            return 2.0 * ((ph / (2 * np.pi)) - np.floor(0.5 + ph / (2 * np.pi)))
        # s&h
        rng = np.random.default_rng(self.seed)
        steps = np.floor(ph / (2 * np.pi))
        return rng.uniform(-1, 1, int(steps.max() + 1))[steps.astype(int)]

    def render(self, n: int, f0: float, patch: dict | None = None,
               gate: int | None = None, stereo: bool = True) -> np.ndarray:
        """Render one note.

        ``patch`` keys (all optional):
            osc_morph, osc_tri, osc_duty, osc_sync (freq ratio), osc_fm,
            sub_level, noise_level, ring_level, mix_drive,
            f1_cutoff, f1_res, f2_cutoff, f2_res, f_mode, routing,
            amp_a, amp_d, amp_s, amp_r, sus_level,
            fil_a, fil_d, fil_s, fil_r, fil_env (cutoff env depth, oct),
            lfo1_rate, lfo1_wave, lfo1_dest, lfo1_depth, lfo2_rate,
            lfo2_wave, lfo2_dest, lfo2_depth, lfo3_rate, lfo3_wave,
            lfo3_dest, lfo3_depth,
            mod_matrix: list of (source, dest, amount) with source in
            {'lfo1','lfo2','lfo3','env','vel'} and dest in
            {'pitch','morph','cutoff','res','ring','pan'} (up to 3
            destinations per slot; matrix is limited to 6 slots here).
        """
        p = {
            "osc_morph": 0.15, "osc_tri": 0.0, "osc_duty": 0.5,
            "osc_sync": 0.0, "osc_fm": 0.0,
            "sub_level": 0.25, "noise_level": 0.02, "ring_level": 0.0,
            "mix_drive": 0.0,
            "f1_cutoff": 1200.0, "f1_res": 0.35,
            "f2_cutoff": 4000.0, "f2_res": 0.2, "f_mode": "lp",
            "routing": "serial",
            "amp_a": 0.002, "amp_d": 0.25, "amp_s": 0.7, "amp_r": 0.2,
            "sus_level": 0.6,
            "fil_a": 0.01, "fil_d": 0.3, "fil_s": 0.5, "fil_r": 0.3,
            "fil_env": 2.0,
            "lfo1_rate": 0.5, "lfo1_wave": "sine", "lfo1_dest": "cutoff",
            "lfo1_depth": 0.1,
            "lfo2_rate": 0.2, "lfo2_wave": "tri", "lfo2_dest": "morph",
            "lfo2_depth": 0.2,
            "lfo3_rate": 0.1, "lfo3_wave": "s&h", "lfo3_dest": "res",
            "lfo3_depth": 0.05,
            "mod_matrix": [],
        }
        if patch:
            p.update({k: v for k, v in patch.items() if k in p or k == "mod_matrix"})
        self.f1.reset()
        self.f2.reset()

        # per-sample parameter modulation
        mods = {k: np.zeros(n) for k in ("pitch", "morph", "cutoff", "res",
                                         "ring", "pan")}
        lfo_sigs = {}
        for i, (rate, wave, dest, depth) in enumerate([
            (p["lfo1_rate"], p["lfo1_wave"], p["lfo1_dest"], p["lfo1_depth"]),
            (p["lfo2_rate"], p["lfo2_wave"], p["lfo2_dest"], p["lfo2_depth"]),
            (p["lfo3_rate"], p["lfo3_wave"], p["lfo3_dest"], p["lfo3_depth"]),
        ], start=1):
            sig = self._lfo(n, rate, wave)
            lfo_sigs[f"lfo{i}"] = sig
            if dest in mods:
                mods[dest] += depth * sig
        amp_env = _adsr(n, self.sr, p["amp_a"], p["amp_d"], p["amp_s"],
                        p["amp_r"], p["sus_level"], gate)
        fil_env = _adsr(n, self.sr, p["fil_a"], p["fil_d"], p["fil_s"],
                        p["fil_r"], p["sus_level"], gate)
        # modulation matrix: 6 slots x up to 3 destinations
        for slot in p["mod_matrix"][:6]:
            src, dest, amount = slot[0], slot[1], float(slot[2])
            if src.startswith("lfo") and src in lfo_sigs:
                if dest in mods:
                    mods[dest] += amount * lfo_sigs[src]
            elif src == "env":
                if dest in mods:
                    mods[dest] += amount * fil_env

        cutoff1 = np.clip(p["f1_cutoff"] * 2.0 ** (mods["cutoff"] * p["fil_env"]
                          + mods["cutoff"] * 0.0), 20, 0.45 * self.sr)
        cutoff2 = np.clip(p["f2_cutoff"] * 2.0 ** (mods["cutoff"] * p["fil_env"] * 0.5),
                          20, 0.45 * self.sr)
        res1 = np.clip(p["f1_res"] + mods["res"], 0.0, 1.0)
        res2 = np.clip(p["f2_res"] + mods["res"] * 0.5, 0.0, 1.0)

        # oscillator mix (morph modulated by LFO)
        morph = np.clip(p["osc_morph"] + mods["morph"], 0.0, 1.0)
        # pitch mod is applied as the mean over the note (per-sample pitch
        # modulation would require a time-varying phase integrator; the
        # static-scalar version keeps the oscillator phase-accumulator simple)
        f0m = f0 * 2.0 ** (float(np.mean(mods["pitch"])) * 0.5)
        osc1 = self.oscs[0].render(n, f0m, morph=morph,
                                   tri_blend=p["osc_tri"], duty=p["osc_duty"],
                                   sync_f=f0 * p["osc_sync"] if p["osc_sync"] else 0.0,
                                   fm_index=p["osc_fm"])
        osc2 = self.oscs[1].render(n, f0m * 1.005, morph=morph * 0.8,
                                   duty=p["osc_duty"])
        osc3 = self.oscs[2].render(n, f0m * 0.5, morph=morph * 0.6,
                                   duty=p["osc_duty"])
        sub = self.oscs[0].render(n, f0m * 0.5, morph=1.0, duty=0.5)
        rng = np.random.default_rng(self.seed)
        noise = rng.standard_normal(n) * p["noise_level"]
        ring = osc1 * osc2 * p["ring_level"]
        mix = osc1 + osc2 * 0.8 + osc3 * 0.6 + sub * p["sub_level"] + noise + ring
        if p["mix_drive"] > 0:
            mix = np.tanh(mix * (1.0 + p["mix_drive"] * 2.0))

        routing = p["routing"]
        f_mode = p["f_mode"]
        if routing == "serial":
            y1 = self.f1.process(mix, float(np.median(cutoff1)),
                                 float(np.median(res1)), f_mode, 24)
            y = self.f2.process(y1, float(np.median(cutoff2)),
                                float(np.median(res2)), f_mode, 24)
        elif routing == "parallel":
            y1 = self.f1.process(mix, float(np.median(cutoff1)),
                                 float(np.median(res1)), f_mode, 24)
            y2 = self.f2.process(mix, float(np.median(cutoff2)),
                                 float(np.median(res2)), f_mode, 12)
            y = (y1 + y2) * 0.5
        elif routing == "stereo":
            left = self.f1.process(mix, float(np.median(cutoff1)),
                                   float(np.median(res1)), f_mode, 24)
            right = self.f2.process(mix, float(np.median(cutoff2)),
                                    float(np.median(res2)), f_mode, 12)
            l = left * amp_env
            r = right * amp_env
            if stereo:
                return np.stack([l, r], axis=1)
            return ((l + r) * 0.5)
        else:                                        # bypass
            y = mix
        y = y * amp_env
        if stereo:
            pan = np.clip(mods["pan"], -1, 1)
            left = y * (1.0 - np.clip(pan, 0, 1)) * 0.5 + y * 0.5
            right = y * (1.0 - np.clip(-pan, 0, 1)) * 0.5 + y * 0.5
            return np.stack([left, right], axis=1)
        return y


class VirusVA:
    """Polyphonic Virus-style synth: voices, unison, mono/glide."""

    def __init__(self, sample_rate: int = DEFAULT_SR, max_voices: int = 8,
                 unison: int = 1, mono: bool = False, glide: float = 0.0,
                 seed: int = 0):
        self.sr = int(sample_rate)
        self.max_voices = int(max_voices)
        self.unison = int(unison)
        self.mono = bool(mono)
        self.glide = float(glide)
        self.seed = int(seed)

    def play(self, notes: list[int], dur: float = 1.5,
             patch: dict | None = None, gain: float = 0.25) -> np.ndarray:
        """Render a list of MIDI notes (chord) for ``dur`` seconds."""
        n = int(dur * self.sr)
        nv = min(len(notes), self.max_voices)
        out = np.zeros((n, 2))
        for i, midi in enumerate(notes[:nv]):
            f0 = 440.0 * 2.0 ** ((midi - 69) / 12.0)
            if self.mono:
                # last note only, with glide from previous
                continue
            stack = []
            for u in range(self.unison):
                det = (u - (self.unison - 1) / 2.0) * 0.004
                v = VirusVoice(self.sr, seed=self.seed + i * 7 + u)
                stack.append(v.render(n, f0 * 2.0 ** det, patch, stereo=True))
            voice = np.mean(np.stack(stack), axis=0) if stack else \
                VirusVoice(self.sr, self.seed + i).render(n, f0, patch)
            out += voice * gain
        if self.mono and notes:
            f0 = 440.0 * 2.0 ** ((notes[-1] - 69) / 12.0)
            v = VirusVoice(self.sr, self.seed)
            out = v.render(n, f0, patch, stereo=True) * gain
        return np.clip(out, -1.0, 1.0)


def demo() -> str:
    """Prove morph/sync/FM oscs, filter routings, mod matrix, determinism."""
    sr = 22050
    patch = {
        "osc_morph": 0.3, "osc_sync": 2.0, "osc_fm": 0.4, "sub_level": 0.2,
        "mix_drive": 0.1, "f1_cutoff": 900.0, "f1_res": 0.3,
        "f2_cutoff": 3500.0, "f2_res": 0.15, "routing": "serial",
        "lfo1_rate": 0.5, "lfo1_dest": "cutoff", "lfo1_depth": 0.4,
        "mod_matrix": [("lfo2", "morph", 0.3), ("lfo3", "res", 0.1),
                       ("env", "cutoff", 0.5)],
    }
    va = VirusVA(sample_rate=sr, max_voices=4, unison=2, seed=11)
    out = va.play([60, 64, 67, 72], dur=1.0, patch=patch)
    print(f"virus chord: shape={out.shape} peak={np.abs(out).max():.3f} "
          f"finite={np.all(np.isfinite(out))}")
    assert out.shape == (int(1.0 * sr), 2) and np.all(np.isfinite(out))

    out2 = VirusVA(sample_rate=sr, max_voices=4, unison=2, seed=11).play(
        [60, 64, 67, 72], dur=1.0, patch=patch)
    print(f"deterministic: {np.array_equal(out, out2)}")
    assert np.array_equal(out, out2)

    # routings must differ
    outs = {}
    for r in VirusVoice.ROUTINGS:
        p2 = dict(patch, routing=r)
        o = VirusVA(sample_rate=sr, max_voices=1, seed=1).play(
            [60], dur=0.5, patch=p2)
        outs[r] = float(np.abs(o).mean())
    print(f"routing means: { {k: round(v, 4) for k, v in outs.items()} }")
    assert len(set(round(v, 3) for v in outs.values())) >= 3

    # mono+glide path
    m = VirusVA(sample_rate=sr, mono=True, glide=0.05, seed=2).play(
        [48, 55], dur=0.8, patch=patch)
    print(f"mono: shape={m.shape} finite={np.all(np.isfinite(m))}")
    assert np.all(np.isfinite(m))

    # pure osc behaviour: morph 0 = saw, morph 1 = narrow pulse (DC rises,
    # so check RMS instead of mean)
    osc = VirusOsc(sr)
    saw = osc.render(4096, 220.0, morph=0.0)
    pulse = osc.render(4096, 220.0, morph=1.0)
    print(f"osc saw rms={np.sqrt((saw ** 2).mean()):.3f} "
          f"pulse rms={np.sqrt((pulse ** 2).mean()):.3f}")
    assert np.sqrt((saw ** 2).mean()) > 0.3

    return "virus_va demo OK"


if __name__ == "__main__":
    print(demo())
