# -*- coding: utf-8 -*-
"""SP-029 Subtractive Synthesis production pass on the samba-batucada composition.

Method (from methods_db.md SP-029):
Subtractive Synthesis with PolyBLEP Anti-Aliased Oscillators and Analog Filter
Emulation. PolyBLEP-corrected saw/square oscillators feed a Moog 4-pole ladder
filter with per-stage tanh saturation. Full ADSR envelope control for amplitude
and filter cutoff.

Source: /opt/data/projects/Styles/Latin/samba-batucada-daily-2026-06-18/composition.mid
  - 120 BPM, ticks_per_beat=10080
  - Track 1: kick (MIDI 36) at sixteenth offsets (0,1,2,3,6,7) of a 7-sixteenth bar
  - Track 2: agogo bell (MIDI 64 = E4) at every sixteenth (14 hits, 0.125 s each)

Signal flow per voice:
  PolyBLEP oscillator(s) -> mixer -> Moog ladder (envelope-modulated fc) -> VCA (ADSR)

  Kick  : sine (no alias) + pitch envelope 120->40 Hz, amplitude ADSR, short decay
          (surdo-like thump)
  Agogo : 2x detuned PolyBLEP square (PW 0.25), unison +7 cents, Moog lp sweep
          with resonance, band-limited (PolyBLEP) so the high E4 ring stays clean

Runs the full 1.75 s loop 4 times = 7.0 s delivery loop.
"""
import os
import json
import hashlib
import numpy as np
import wave

SR = 44100
BPM = 120.0
SEC_PER_SIXTEENTH = 60.0 / BPM / 4.0  # 0.125 s
LOOP_SEC = 7 * SEC_PER_SIXTEENTH      # 0.875 s per loop
REPEATS = 8                           # 7.0 s delivery
OUT_DIR = "/opt/data/projects/Styles/Production/SP029-subtractive-samba-batucada"
AUDIO_DIR = os.path.join(OUT_DIR, "Audio")
SRC_MIDI = "/opt/data/projects/Styles/Latin/samba-batucada-daily-2026-06-18/composition.mid"


# ---------------------------------------------------------------------------
# PolyBLEP oscillators (per methods_db.md SP-029 reference implementation)
# NOTE: local copy kept deliberately — SP-029's variant (falling-edge only,
# d in [0,1) + dead [-1,0) branch) differs from the standard 2-sample
# version in sound/synthesis/mono_synth.py. Changing it would alter the
# verified SP-029 audio output. For NEW code, prefer the shared polyblep.
# ---------------------------------------------------------------------------
def polyblep(phase, phase_inc):
    """PolyBLEP correction for a discontinuity at phase = 0 (vectorized)."""
    d = phase / (phase_inc + 1e-20)
    correction = np.zeros_like(d)
    m1 = (d >= 0) & (d < 1)
    correction[m1] = d[m1] + d[m1] - d[m1] ** 2 - 1.0
    m2 = (d >= -1) & (d < 0)
    correction[m2] = d[m2] + d[m2] + d[m2] ** 2 + 1.0
    return correction


def polyblep_saw(f0, fs, duration, phase_init=0.0):
    n = int(duration * fs)
    phase_inc = f0 / fs
    phase = np.mod(np.arange(n) * phase_inc + phase_init, 1.0)
    y_naive = 2.0 * phase - 1.0
    return y_naive - polyblep(phase, phase_inc)


def polyblep_square(f0, fs, duration, pulse_width=0.5, phase_init=0.0):
    n = int(duration * fs)
    phase_inc = f0 / fs
    phase = np.mod(np.arange(n) * phase_inc + phase_init, 1.0)
    y_naive = np.where(phase < pulse_width, 1.0, -1.0)
    rise = polyblep(phase, phase_inc)
    fall = polyblep(np.mod(phase - pulse_width, 1.0), phase_inc)
    return y_naive + rise - fall


def sine_wave(f0, fs, duration, phase_init=0.0):
    n = int(duration * fs)
    phase_inc = f0 / fs
    phase = np.mod(np.arange(n) * phase_inc + phase_init, 1.0)
    return np.sin(2.0 * np.pi * phase)


# ---------------------------------------------------------------------------
# Moog 4-pole ladder filter with per-stage tanh saturation
# ---------------------------------------------------------------------------
def moog_ladder(x, fc, resonance, fs, beta=1.5):
    """fc: scalar or per-sample array. resonance in [0,4). beta = drive."""
    n = len(x)
    y = np.zeros(n)
    y1p = y2p = y3p = y4p = 0.0
    fc_arr = np.full(n, fc) if np.isscalar(fc) else fc
    for i in range(n):
        alpha = np.pi * fc_arr[i] / fs
        a = alpha / (1.0 + alpha)
        b = 1.0 / (1.0 + alpha)
        x0 = np.tanh(beta * (x[i] - resonance * y4p))
        y1 = np.tanh(beta * (a * x0 + b * y1p))
        y2 = np.tanh(beta * (a * y1 + b * y2p))
        y3 = np.tanh(beta * (a * y2 + b * y3p))
        y4 = a * y3 + b * y4p
        y[i] = y4
        y1p, y2p, y3p, y4p = y1, y2, y3, y4
    return y


# ---------------------------------------------------------------------------
# ADSR envelope (exponential segments, per methods_db.md)
# ---------------------------------------------------------------------------
def adsr(n_samples, fs, attack=0.01, decay=0.1, sustain=0.7, release=0.2,
         gate_duration=None):
    if gate_duration is None:
        gate_duration = n_samples / fs
    env = np.zeros(n_samples)
    a_s = int(attack * fs)
    d_s = int(decay * fs)
    r_s = int(release * fs)
    gate_s = int(gate_duration * fs)
    tau_a = max(attack / 5.0, 0.001)
    tau_d = max(decay / 5.0, 0.001)
    tau_r = max(release / 5.0, 0.001)
    n = 0
    while n < n_samples:
        if n < a_s:
            env[n] = 1.0 - np.exp(-n / fs / tau_a)
        elif n < a_s + d_s:
            env[n] = sustain + (1.0 - sustain) * np.exp(-(n - a_s) / fs / tau_d)
        elif n < gate_s:
            env[n] = sustain
        elif n < gate_s + r_s:
            env[n] = sustain * np.exp(-(n - gate_s) / fs / tau_r)
        else:
            env[n] = 0.0
        n += 1
    return env


def midi_to_freq(m):
    return 440.0 * (2.0 ** ((m - 69) / 12.0))


# event map from the source MIDI (7-sixteenth bar @120 BPM)
KICK_OFFSETS = [0, 1, 2, 3, 6, 7]      # surdo accents
AGOGO_OFFSETS = list(range(7))          # E4 bell every sixteenth


# ---------------------------------------------------------------------------
# Voices
# ---------------------------------------------------------------------------
def render_kick(dur=0.22, fs=SR):
    """Surdo-style kick: sine with pitch envelope 120->40 Hz + short ADSR."""
    n = int(dur * fs)
    t = np.arange(n) / fs
    freq = 40.0 + 80.0 * np.exp(-t / 0.035)          # pitch envelope
    phase = 2.0 * np.pi * np.cumsum(freq) / fs
    osc = np.sin(phase)
    amp = adsr(n, fs, attack=0.002, decay=0.16, sustain=0.0,
               release=0.05, gate_duration=0.18)
    return osc * amp * 0.9


def render_agogo(note=64, dur=0.28, fs=SR):
    """Agogo bell: 2 detuned PolyBLEP squares -> Moog ladder sweep + ADSR."""
    f0 = midi_to_freq(note)                            # E4 = 329.63 Hz
    n = int(dur * fs)
    osc = np.zeros(n)
    for cents in (-7.0, 7.0):
        osc += polyblep_square(f0 * 2.0 ** (cents / 1200.0), fs, dur,
                               pulse_width=0.25) / 2.0
    # filter envelope: open then close -> metallic 'dong' -> ring
    filt_env = adsr(n, fs, attack=0.001, decay=0.09, sustain=0.35,
                    release=0.10, gate_duration=dur - 0.08)
    fc = np.clip(900.0 + filt_env * 9000.0, 20, fs / 2 - 100)
    yf = moog_ladder(osc, fc, resonance=1.8, fs=fs, beta=1.6)
    amp = adsr(n, fs, attack=0.001, decay=0.10, sustain=0.30,
               release=0.09, gate_duration=dur - 0.06)
    return yf * amp * 0.55


# ---------------------------------------------------------------------------
# Render the full loop from the MIDI event map
# ---------------------------------------------------------------------------
def render_loop(fs=SR):
    length = int(LOOP_SEC * fs)
    kick = np.zeros(length)
    agogo = np.zeros(length)

    kick_offsets = KICK_OFFSETS
    agogo_offsets = AGOGO_OFFSETS

    for s in agogo_offsets:
        start = int(s * SEC_PER_SIXTEENTH * fs)
        buf = render_agogo(64, dur=0.28, fs=fs)
        end = min(start + len(buf), length)
        agogo[start:end] += buf[: end - start]

    for s in kick_offsets:
        start = int(s * SEC_PER_SIXTEENTH * fs)
        buf = render_kick(dur=0.22, fs=fs)
        end = min(start + len(buf), length)
        kick[start:end] += buf[: end - start]

    return kick, agogo


def save_wav(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = np.clip(data, -1.0, 1.0)
    pcm = (data * 32767.0).astype(np.int16)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    os.makedirs(AUDIO_DIR, exist_ok=True)
    kick, agogo = render_loop()

    # master: agogo lead, kick body; soft-clip tanh glue
    master = 0.9 * agogo + 1.0 * kick
    master = np.tanh(1.5 * master)
    peak = np.max(np.abs(master))
    if peak > 0:
        master = master / peak * 0.89          # normalize to ~-1 dBFS

    # 8x loop for delivery (~7 s)
    full = np.tile(master, REPEATS)
    # tiny crossfade at loop seam to avoid clicks
    fade = int(0.005 * SR)
    ramp = np.linspace(0, 1, fade)
    full[:fade] *= ramp
    full[-fade:] *= ramp[::-1]

    kick_loop = np.tile(kick, REPEATS)
    agogo_loop = np.tile(agogo, REPEATS)

    wav_mix = os.path.join(AUDIO_DIR, "SP029-samba-batucada-subtractive.wav")
    wav_kick = os.path.join(AUDIO_DIR, "stem_kick_surdo.wav")
    wav_agogo = os.path.join(AUDIO_DIR, "stem_agogo_polyblep.wav")
    save_wav(wav_mix, full)
    save_wav(wav_kick, kick_loop)
    save_wav(wav_agogo, agogo_loop)

    for p in (wav_mix, wav_kick, wav_agogo):
        assert os.path.getsize(p) > 40, "empty output: " + p
        print(p, os.path.getsize(p), "bytes")

    # provenance
    prov = {
        "job": "production-9a2813f77dac",
        "source_midi": SRC_MIDI,
        "source_midi_sha256": sha256(SRC_MIDI),
        "production_method": "SP-029",
        "production_method_name": "Subtractive Synthesis with PolyBLEP Anti-Aliased Oscillators and Analog Filter Emulation",
        "composition_analysis": {
            "bpm": 120,
            "ticks_per_beat": 10080,
            "loop_seconds": 0.875,
            "kick_midi_note": 36,
            "agogo_midi_note": 64,
            "agogo_hits_per_loop": 14,
            "kick_hits_per_loop": 6,
            "voice_map": {
                "track1": "kick/surdo (MIDI 36) sixteenth accents 0,1,2,3,6,7",
                "track2": "agogo bell E4 (MIDI 64) every sixteenth"
            }
        },
        "synthesis_parameters": {
            "sample_rate": 44100,
            "kick": {
                "oscillator": "sine + pitch envelope 120->40 Hz (tau 35 ms)",
                "adsr": "A 2ms D 160ms S 0 R 50ms"
            },
            "agogo": {
                "oscillator": "2x PolyBLEP square PW 0.25, unison detune +/-7 cents",
                "filter": "Moog 4-pole ladder, resonance 1.8, beta 1.6",
                "filter_fc": "900 Hz base + 9000 Hz envelope depth (open->close sweep)",
                "adsr": "A 1ms D 100ms S 0.30 R 90ms"
            },
            "master": {
                "mix": "0.9 agogo + 1.0 kick",
                "glue": "tanh(1.5x) soft saturation",
                "normalize": "-1 dBFS peak",
                "loop_repeats": 8
            }
        },
        "render_engine": "pure numpy/scipy-free subtractive synthesis (methods_db.md SP-029 reference implementation)",
        "outputs": {
            "full_mix_wav": wav_mix,
            "stem_kick_wav": wav_kick,
            "stem_agogo_wav": wav_agogo,
        },
    }
    prov_path = os.path.join(OUT_DIR, "provenance.json")
    with open(prov_path, "w") as f:
        json.dump(prov, f, indent=2)

    # grid visualization
    grid = []
    grid.append("SP-029 samba-batucada rhythm DNA (one 7-sixteenth loop @120 BPM)")
    grid.append("sixteenth: 0     1     2     3     4     5     6")
    grid.append("agogo   : " + "".join("█     " for _ in AGOGO_OFFSETS))
    kline = ["░" if i not in KICK_OFFSETS else "█" for i in range(7)]
    grid.append("kick    : " + "     ".join(kline))
    grid.append("(agogo = every sixteenth E4; kick = surdo accents on 0,1,2,3,6,7)")
    with open(os.path.join(OUT_DIR, "Analysis", "grid_visualization.txt"), "w") as f:
        f.write("\n".join(grid) + "\n")

    print("provenance.json written")
    print("grid written")


if __name__ == "__main__":
    main()
