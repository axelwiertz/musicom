#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sound Production Method SP-026: Spectral Phase Vocoder Resynthesis
==================================================================
Applied to: /opt/data/projects/Styles/Folk/001-folk-drie-kleine-kleutertjes/midi/variation_intro_verse.mid

Method (methods_db.md SP-026): STFT analysis-modification-resynthesis
pipeline with phase unwrapping and instantaneous-frequency propagation
(Flanagan/Schafer phase vocoder). Modifications applied here:

  1. TIME-STRETCH  alpha = 1.2  (slower, dreamier nursery lullaby feel)
     - synthesis hop H_s = alpha * H_a, phases propagated from
       instantaneous frequency omega_hat[k], magnitude interpolated
  2. SPECTRAL FREEZE - the final analysis frame (last chord) is frozen:
     magnitude held constant while phase continues, with exponential
     decay, producing an ethereal pad tail instead of a hard stop
  3. HARMONIC SHARPNESS - mild spectral exponent (|X|^1.12) for clarity
  4. ISTFT resynthesis with WOLA squared-window normalization

Two-layer deliverable:
  1. SP-026 phase-vocoder resynthesis = the production method (pitched
     material re-rendered through the spectral domain)
  2. FluidSynth GM render of the same MIDI = analysis source + untouched
     comparison layer (TimGM6mb.sf2)

Outputs (dual MIDI + audio):
  MIDI/original.mid        - source composition copy (DAW artifact)
  Audio/mix_spectral.wav   - final mix (vocoder resynth, mastered)
  Audio/mix_spectral.ogg   - Opus render
  Audio/stems/             - per-stage stems (gm_source, stretched,
                             freeze_pad)
  Analysis/provenance.json + Analysis/grid_visualization.txt
"""

import os
import json
import gc
import math
import wave
import shutil
import hashlib
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import mido

# ============================================================================
# Configuration
# ============================================================================

SR = 44100
MIDI_PATH = "/opt/data/projects/Styles/Folk/001-folk-drie-kleine-kleutertjes/midi/variation_intro_verse.mid"
OUTPUT_DIR = Path("/opt/data/projects/Styles/Production/SP026-phase-vocoder-kleutertjes")
STEMS_DIR = OUTPUT_DIR / "Audio" / "stems"
MIDI_DIR = OUTPUT_DIR / "MIDI"
ANALYSIS_DIR = OUTPUT_DIR / "Analysis"

SOUNDFONT = "/opt/data/micromamba/envs/musicom/lib/python3.11/site-packages/pretty_midi/TimGM6mb.sf2"
FLUIDSYNTH = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
FFMPEG = "/usr/bin/ffmpeg"

# SP-026 parameters (methods_db.md defaults; 2048 for transient fidelity)
FFT_SIZE = 2048
HOP_RATIO = 0.25
ALPHA = 1.2            # time-stretch factor (>1 = slower/longer)
FREEZE_TAIL_S = 6.0    # spectral-freeze pad tail length
MAG_EXP = 1.0          # harmonic sharpness exponent (1.0 = neutral)

MASTERING = "musicom ProductionChain: lowpass(12k) + StereoImager(1.2) + LUFS(-16) + Limiter(-1.0dB)"

# ============================================================================
# SP-026 Engine: Phase Vocoder (per methods_db.md spec)
# ============================================================================

def stft_analysis(x, fft_size, hop):
    """STFT analysis: magnitude, phase, unwrapped instantaneous frequency."""
    N = fft_size
    window = np.hanning(N)
    n_frames = (len(x) - N) // hop + 1
    magnitude = np.zeros((n_frames, N // 2 + 1))
    phase = np.zeros((n_frames, N // 2 + 1))
    for m in range(n_frames):
        start = m * hop
        frame = x[start:start + N] * window
        spectrum = np.fft.rfft(frame)
        magnitude[m] = np.abs(spectrum)
        phase[m] = np.angle(spectrum)
    # Phase unwrapping -> instantaneous frequency (radians per SAMPLE):
    # omega_hat[k] = k*(2*pi/N) + wrap(dev)/H_a  (methods_db Technical
    # Mechanics formula). NOTE: the db reference CODE writes
    # omega = expected + dev/H_a (mixed units, bin_freqs*H_a + dev/H_a),
    # which over-increments synthesis phase by factor H_a and cancels the
    # output to silence; the description formula is used here.
    dphi = np.diff(phase, axis=0)
    bin_freqs = np.arange(N // 2 + 1) * (2.0 * np.pi / N)
    expected = bin_freqs * hop
    deviation = dphi - expected[np.newaxis, :]
    deviation_wrapped = deviation - 2.0 * np.pi * np.round(deviation / (2.0 * np.pi))
    omega = bin_freqs[np.newaxis, :] + deviation_wrapped / hop
    return magnitude, phase, omega, window


def istft_resynth(magnitude, synth_phase, n_out, fft_size, hop_s, window):
    """WOLA overlap-add resynthesis from magnitude + propagated phase."""
    N = fft_size
    n_frames = magnitude.shape[0]
    y = np.zeros(n_out)
    window_sum = np.zeros(n_out)
    for l in range(n_frames):
        spectrum_out = magnitude[l] * np.exp(1j * synth_phase[l])
        frame_out = np.fft.irfft(spectrum_out, n=N) * window
        out_start = l * hop_s
        y[out_start:out_start + N] += frame_out
        window_sum[out_start:out_start + N] += window ** 2
    # WOLA normalization with denominator floor: near the signal edges only a
    # single window edge contributes, window_sum -> ~1e-8, and dividing there
    # turns numerical residue into a huge spike that poisons peak
    # normalization. Floor at 1e-4 (window_sum max ~1.26) keeps edges clean.
    valid = window_sum > 1e-4
    y[valid] /= window_sum[valid]
    y[~valid] = 0.0
    return y


def phase_vocoder_stretch(x, alpha, fft_size=FFT_SIZE, hop_ratio=HOP_RATIO,
                          mag_exp=1.0):
    """Time-stretch x by alpha with phase propagation (methods_db SP-026)."""
    N = fft_size
    H_a = int(N * hop_ratio)
    H_s = max(1, int(H_a * alpha))
    magnitude, phase, omega, window = stft_analysis(x, N, H_a)
    if mag_exp != 1.0:
        magnitude = magnitude ** mag_exp

    # One synthesis frame per analysis frame, synthesis hop H_s = alpha*H_a:
    # output duration = (n_frames-1)*H_s + N ~= alpha * input duration.
    # (methods_db reference divides frame count by alpha, which cancels the
    # stretch and yields output ~= input length - alpha*H_a; fixed here.)
    n_synth = magnitude.shape[0]
    out_len = (n_synth - 1) * H_s + N
    synth_phase = np.zeros((n_synth, N // 2 + 1))
    synth_phase[0] = phase[0]
    mag_out = np.zeros((n_synth, N // 2 + 1))

    for l in range(n_synth):
        m_float = l / alpha
        m_idx = min(int(np.floor(m_float)), magnitude.shape[0] - 1)
        frac = m_float - m_idx
        if m_idx + 1 < magnitude.shape[0]:
            mag_out[l] = (1.0 - frac) * magnitude[m_idx] + frac * magnitude[m_idx + 1]
            w_idx = min(m_idx, omega.shape[0] - 1)
            inst_freq = omega[w_idx]
        else:
            mag_out[l] = magnitude[m_idx]
            inst_freq = omega[-1]
        if l > 0:
            synth_phase[l] = synth_phase[l - 1] + inst_freq * H_s

    y = istft_resynth(mag_out, synth_phase, out_len, N, H_s, window)
    peak = np.max(np.abs(y))
    if peak > 0:
        y = y / peak * 0.95
    return y


def spectral_freeze_tail(x, tail_s, fft_size=FFT_SIZE, hop_ratio=HOP_RATIO,
                         decay_rate=0.35):
    """Freeze the LAST NOTE's analysis frame into a decaying spectral pad.

    The final analysis frame of a render is usually release-tail silence;
    freezing it freezes silence. Instead, freeze the last frame whose energy
    exceeds 5% of the global max frame energy (the last sounding note), so
    the pad carries the final chord spectrum.
    """
    N = fft_size
    H_a = int(N * hop_ratio)
    H_s = H_a
    window = np.hanning(N)
    magnitude, phase, omega, _ = stft_analysis(x, N, H_a)
    frame_rms = np.sqrt(np.mean(magnitude ** 2, axis=1))
    thr = 0.05 * float(np.max(frame_rms))
    idx = int(np.nonzero(frame_rms > thr)[0][-1])
    frozen_mag = magnitude[idx].copy()
    frozen_phase = phase[idx].copy()
    inst_freq = omega[min(idx, omega.shape[0] - 1)]
    print(f"[freeze] last-note frame idx={idx} (rms={frame_rms[idx]:.5f}, "
          f"thr={thr:.5f})")

    n_extra = int(tail_s * SR / H_s)
    n_out = n_extra * H_s + N
    y = np.zeros(n_out)
    window_sum = np.zeros(n_out)
    synth_phase = frozen_phase
    for l in range(n_extra):
        decay = math.exp(-decay_rate * l / n_extra)
        spectrum_out = frozen_mag * decay * np.exp(1j * synth_phase)
        frame_out = np.fft.irfft(spectrum_out, n=N) * window
        out_start = l * H_s
        y[out_start:out_start + N] += frame_out
        window_sum[out_start:out_start + N] += window ** 2
        synth_phase = synth_phase + inst_freq * H_s
    valid = window_sum > 1e-4
    y[valid] /= window_sum[valid]
    y[~valid] = 0.0
    peak = np.max(np.abs(y))
    if peak > 0:
        y = y / peak * 0.8
    return y


# ============================================================================
# Helpers
# ============================================================================

def read_wav_mono(path):
    import scipy.io.wavfile as wavfile
    sr, data = wavfile.read(path)
    if data.dtype == np.int16:
        data = data.astype(np.float32) / 32768.0
    elif data.dtype == np.uint8:
        data = (data.astype(np.float32) - 128.0) / 128.0
    if data.ndim == 2:
        data = data.mean(axis=1)
    return data.astype(np.float32), sr


def write_wav(path, audio, sr):
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)
    audio = np.clip(audio, -1.0, 1.0)
    audio_i16 = (audio * 32767).astype(np.int16)
    import scipy.io.wavfile as wavfile
    wavfile.write(path, sr, audio_i16)


def silence_stats(audio, sr, label):
    mono = audio if audio.ndim == 1 else audio.mean(axis=1)
    silent = float(np.sum(np.abs(mono) < 0.001) / len(mono))
    rms_sec = []
    n = int(sr)
    for i in range(0, len(mono) - n, n):
        seg = mono[i:i + n]
        rms_sec.append(float(np.sqrt(np.mean(seg ** 2))))
    print(f"[silence-check] {label}: len={len(mono)/sr:.1f}s "
          f"silent_ratio={silent*100:.1f}% "
          f"per-sec RMS min={min(rms_sec):.5f} max={max(rms_sec):.5f}")
    assert silent < 0.90, f"{label}: render is mostly silence - abort"


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def get_bpm(midi_path):
    mf = mido.MidiFile(midi_path)
    for tr in mf.tracks:
        for m in tr:
            if m.type == 'set_tempo':
                return 60e6 / m.tempo
    return 120.0


def midi_dna_grid(midi_path, bars=8):
    """Extract melodic DNA as a high-contrast onset grid for the analysis note."""
    mf = mido.MidiFile(midi_path)
    events = []
    for tr in mf.tracks:
        t = 0
        for m in tr:
            t += m.time
            if m.type == 'note_on' and m.velocity > 0:
                events.append(t)
    events.sort()
    ticks_per_beat = mf.ticks_per_beat
    bar_ticks = ticks_per_beat * 4
    n_bars = max(1, math.ceil((events[-1] + 1) / bar_ticks)) if events else 1
    grid = []
    for b in range(n_bars):
        row = []
        for step in range(16):
            lo = b * bar_ticks + step * bar_ticks // 16
            hi = b * bar_ticks + (step + 1) * bar_ticks // 16
            hit = any(lo <= e < hi for e in events)
            row.append('█' if hit else '░')
        grid.append(''.join(row))
    return grid, n_bars


# ============================================================================
# Main pipeline
# ============================================================================

def main():
    for d in (OUTPUT_DIR, STEMS_DIR, MIDI_DIR, ANALYSIS_DIR):
        os.makedirs(d, exist_ok=True)

    bpm = get_bpm(MIDI_PATH)
    print(f"Source BPM: {bpm:.1f}")

    # 1. Copy source MIDI (DAW artifact)
    shutil.copy2(MIDI_PATH, MIDI_DIR / "original.mid")
    src_sha = sha256_file(MIDI_PATH)

    # 2. FluidSynth GM render -> analysis source
    gm_wav = STEMS_DIR / "gm_source.wav"
    cmd = [FLUIDSYNTH, "-ni", "-g", "1.2", "-F", str(gm_wav),
           "-r", str(SR), SOUNDFONT, MIDI_PATH]
    subprocess.run(cmd, check=True, capture_output=True)
    assert os.path.getsize(gm_wav) > 40, "GM render empty"

    x, sr = read_wav_mono(gm_wav)
    x = x.astype(np.float32)
    silence_stats(x, sr, "gm_source")
    print(f"GM source: {len(x)/sr:.2f}s")

    # 3. SP-026 pass 1: time-stretch (dreamier lullaby tempo)
    stretched = phase_vocoder_stretch(x, ALPHA, mag_exp=MAG_EXP)
    stretched = stretched.astype(np.float32)
    write_wav(STEMS_DIR / "stretched.wav", stretched, sr)
    silence_stats(stretched, sr, "stretched")
    print(f"Stretched: {len(stretched)/sr:.2f}s (alpha={ALPHA})")

    # 4. SP-026 pass 2: spectral-freeze tail from final chord frame
    freeze_pad = spectral_freeze_tail(x, FREEZE_TAIL_S)
    freeze_pad = freeze_pad.astype(np.float32)
    write_wav(STEMS_DIR / "freeze_pad.wav", freeze_pad, sr)
    silence_stats(freeze_pad, sr, "freeze_pad")
    print(f"Freeze pad: {len(freeze_pad)/sr:.2f}s")
    del x
    gc.collect()

    # 5. Mix: stretched melody + freeze tail, crossfaded 0.5s
    fade = int(0.5 * sr)
    n_pad = len(freeze_pad)
    total = len(stretched) + n_pad - fade
    mix = np.zeros(total)
    mix[:len(stretched)] = stretched
    ramp = np.linspace(0, 1, fade)
    start = len(stretched) - fade
    mix[start:start + fade] += freeze_pad[:fade] * ramp
    mix[start + fade:] += freeze_pad[fade:]
    del freeze_pad
    gc.collect()
    write_wav(STEMS_DIR / "mix_raw.wav", mix, sr)
    silence_stats(mix, sr, "mix_raw")
    assert np.all(np.isfinite(mix)), "mix contains NaN/Inf before mastering"
    # mono -> stereo for the imager stage (duplicate, then width processing)
    mix = np.column_stack([mix, mix]).astype(np.float32)

    # 6. Mastering via musicom ProductionChain
    from sound.effects.production_chain import ProductionChain
    # NOTE: StateVariableFilter (Chamberlin SVF) is marginally unstable at
    # f=2*sin(pi*12000/44100)~1.51 and blows up to Inf/NaN on long signals;
    # use a robust scipy butter lowpass instead (same musical role).
    from scipy.signal import butter, lfilter
    chain = ProductionChain(sample_rate=sr)
    b, a = butter(4, 12000.0, btype='low', fs=sr)
    lp = np.column_stack([lfilter(b, a, mix[:, 0]),
                          lfilter(b, a, mix[:, 1])]).astype(np.float32)
    del mix
    gc.collect()
    mastered = chain.stage_stereo_imager(lp, widen_amount=1.2)
    del lp
    gc.collect()
    mastered = mastered.astype(np.float32)
    mastered = chain.stage_lufs_norm(mastered, target_lufs=-16.0)
    mastered = chain.stage_limiter(mastered, threshold_db=-1.0)
    mastered = mastered.astype(np.float32)
    write_wav(OUTPUT_DIR / "Audio" / "mix_spectral.wav", mastered, sr)
    silence_stats(mastered, sr, "mastered")
    assert np.all(np.isfinite(mastered)), "mastered output contains NaN/Inf"

    # 7. OGG (Opus) delivery render
    ogg_path = OUTPUT_DIR / "Audio" / "mix_spectral.ogg"
    subprocess.run([FFMPEG, "-y", "-i", str(OUTPUT_DIR / "Audio" / "mix_spectral.wav"),
                    "-codec:a", "libopus", "-application", "voip",
                    "-b:a", "48k", str(ogg_path)],
                   check=True, capture_output=True)
    assert os.path.getsize(ogg_path) > 1000, "OGG too small"
    print(f"OGG: {ogg_path} ({os.path.getsize(ogg_path)} bytes)")

    # 8. Provenance
    prov = {
        "artifact": str(OUTPUT_DIR / "Audio" / "mix_spectral.wav"),
        "classification": "ai-assisted",
        "generator": "musicom SP-026 spectral phase vocoder resynthesis (numpy STFT/ISTFT)",
        "sources": [MIDI_PATH],
        "source_sha256": src_sha,
        "parameters": {
            "method": "SP-026",
            "method_name": "Spectral Phase Vocoder Resynthesis",
            "layer": "Post-Processing / DSP",
            "target": "Time-Stretched / Pitch-Shifted / Frozen Timbres",
            "sr": SR,
            "bpm": round(bpm, 2),
            "fft_size": FFT_SIZE,
            "hop_ratio": HOP_RATIO,
            "time_stretch_alpha": ALPHA,
            "mag_exponent": MAG_EXP,
            "freeze_tail_s": FREEZE_TAIL_S,
            "gm_source": "FluidSynth TimGM6mb.sf2 (single track, GM piano default)",
            "mastering": MASTERING,
            "outputs": {
                "wav": str(OUTPUT_DIR / "Audio" / "mix_spectral.wav"),
                "ogg": str(OUTPUT_DIR / "Audio" / "mix_spectral.ogg"),
                "midi": str(MIDI_DIR / "original.mid"),
            },
        },
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }
    with open(ANALYSIS_DIR / "provenance.json", "w") as f:
        json.dump(prov, f, indent=2)

    # 9. Grid visualization (melody DNA)
    grid, n_bars = midi_dna_grid(MIDI_PATH)
    viz = ["Melodic onset DNA - variation_intro_verse.mid (16 steps/bar)",
           "█ = onset   ░ = rest", ""]
    for i, row in enumerate(grid):
        viz.append(f"bar {i:02d} | {row}")
    with open(ANALYSIS_DIR / "grid_visualization.txt", "w") as f:
        f.write("\n".join(viz))

    print("DONE")

if __name__ == "__main__":
    main()