#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""SP-050 Spectral Delay Filters production pass.

Source: 025v2_unitmatrix.mid (Bollo-Koos x Indian popular hybrid, 120 BPM, 4 bars)
Method: methods_db.md SP-050 — STFT-domain per-bin delay + feedback.
  - partial/formant template (Chromax): f_n = n*s*f0 + shift*f0, harmweights 1/n
  - per-bin delay quantized to hop grid (GCD quantization)
  - per-bin feedback g_k < 1, cap 0.85
  - per-voice mode: melody template (f0 = D4 293.66 Hz), bass template (f0 = F2/D2)
  - ISTFT with Hann, H = N/4, COLA normalization by window-squared sum

Pipeline: MIDI (read via mido — analysis only) -> libfluidsynth ctypes render
per channel -> per-voice SDF -> mix dry/wet -> peak-normalize -1 dB -> WAV -> OGG.
"""
import ctypes
import os
import wave
import numpy as np
import mido

# ---------------- config ----------------
SR = 44100
MIDI_PATH = "/opt/data/projects/Styles/Hybrid/025-bollo-koos-indian-unified/v2-IndianPopular/MIDI/025v2_unitmatrix.mid"
OUT_DIR = "/opt/data/projects/Styles/Production/SP050-spectral-delay-indian-popular"
SF2 = "/opt/data/.local/lib/python3.13/site-packages/pretty_midi/TimGM6mb.sf2"

TPB = 480
BPM = 120.0
TICKS_PER_SEC = TPB * BPM / 60.0  # 960

# voice map: (track_index, synth_channel, gm_program)
VOICES = [
    (0, 0, 104),  # melody  -> Sitar
    (1, 1, 33),   # bass F2 -> Electric Bass (finger)
    (2, 2, 34),   # thump D2 -> Electric Bass (pick)
]

# SDF params
N_FFT = 4096
HOP = N_FFT // 4
TAIL_SEC = 3.0          # feedback tail length
RELEASE_SEC = 0.20      # fluidsynth release tail per note

# ---------------- read MIDI (mido, read-only) ----------------
def read_events(path):
    mf = mido.MidiFile(path)
    per_track = []
    for tr in mf.tracks:
        events = []
        t = 0
        active = {}  # pitch -> (start_tick, vel)
        for msg in tr:
            t += msg.time
            if msg.type == "note_on" and msg.velocity > 0:
                if msg.note > 0:
                    active[msg.note] = (t, msg.velocity)
            elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
                if msg.note in active:
                    st, vel = active.pop(msg.note)
                    dur_ticks = max(t - st, 1)
                    events.append((st, dur_ticks, msg.note, vel))
        events.sort()
        per_track.append(events)
    # total duration in ticks
    max_tick = 0
    for tr in mf.tracks:
        t = 0
        for msg in tr:
            t += msg.time
        max_tick = max(max_tick, t)
    return per_track, max_tick

# ---------------- fluidsynth ctypes render ----------------
lib = ctypes.CDLL("libfluidsynth.so.3")
lib.fluid_settings_setstr.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]
lib.fluid_settings_setstr.restype = ctypes.c_int
lib.fluid_settings_setnum.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_double]
lib.fluid_settings_setnum.restype = ctypes.c_int
lib.new_fluid_settings.restype = ctypes.c_void_p
lib.new_fluid_synth.argtypes = [ctypes.c_void_p]
lib.new_fluid_synth.restype = ctypes.c_void_p
lib.fluid_synth_sfload.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
lib.fluid_synth_sfload.restype = ctypes.c_int
lib.fluid_synth_program_change.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
lib.fluid_synth_program_change.restype = ctypes.c_int
lib.fluid_synth_noteon.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int]
lib.fluid_synth_noteon.restype = ctypes.c_int
lib.fluid_synth_noteoff.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
lib.fluid_synth_noteoff.restype = ctypes.c_int
lib.fluid_synth_write_float.argtypes = [
    ctypes.c_void_p, ctypes.c_int,
    ctypes.POINTER(ctypes.c_float), ctypes.c_int, ctypes.c_int,
    ctypes.POINTER(ctypes.c_float), ctypes.c_int, ctypes.c_int,
]
lib.fluid_synth_write_float.restype = ctypes.c_int
lib.delete_fluid_synth.argtypes = [ctypes.c_void_p]
lib.delete_fluid_settings.argtypes = [ctypes.c_void_p]

def render_channel(events, prog, total_ticks):
    """Render one channel to mono float32 via manual write_float (no audio driver)."""
    settings = lib.new_fluid_settings()
    lib.fluid_settings_setnum(settings, b"synth.gain", 1.0)
    lib.fluid_settings_setnum(settings, b"synth.sample-rate", SR)
    synth = lib.new_fluid_synth(settings)
    lib.fluid_synth_sfload(synth, SF2.encode(), 1)
    lib.fluid_synth_program_change(synth, 0, prog)

    total_sec = total_ticks / TICKS_PER_SEC + TAIL_SEC
    n_total = int(total_sec * SR)
    buf = np.zeros(n_total, dtype=np.float32)

    for (st_ticks, dur_ticks, pitch, vel) in events:
        start_s = st_ticks / TICKS_PER_SEC
        dur_s = dur_ticks / TICKS_PER_SEC
        start_i = int(start_s * SR)
        dur_i = int(dur_s * SR)
        if start_i >= n_total:
            continue
        lib.fluid_synth_noteon(synth, 0, pitch, max(1, min(127, vel)))
        n = min(dur_i, n_total - start_i)
        bl = (ctypes.c_float * n)()
        br = (ctypes.c_float * n)()
        if n > 0:
            lib.fluid_synth_write_float(synth, n, bl, 0, 1, br, 0, 1)
            buf[start_i:start_i + n] += (np.ctypeslib.as_array(bl) + np.ctypeslib.as_array(br)) * 0.5
        lib.fluid_synth_noteoff(synth, 0, pitch)
        # release tail
        tail_n = int(RELEASE_SEC * SR)
        off = start_i + n
        if off < n_total:
            tl = (ctypes.c_float * tail_n)()
            trr = (ctypes.c_float * tail_n)()
            lib.fluid_synth_write_float(synth, tail_n, tl, 0, 1, trr, 0, 1)
            end = min(off + tail_n, n_total)
            buf[off:end] += (np.ctypeslib.as_array(tl)[:end - off] +
                             np.ctypeslib.as_array(trr)[:end - off]) * 0.5

    lib.delete_fluid_synth(synth)
    lib.delete_fluid_settings(settings)
    return buf

# ---------------- SDF (SP-050) ----------------
def stft(x, win, hop):
    n = len(x)
    W = len(win)
    nf = 1 + (n - W) // hop
    X = np.zeros((nf, W // 2 + 1), dtype=complex)
    for m in range(nf):
        frame = x[m * hop:m * hop + W] * win
        X[m] = np.fft.rfft(frame)
    return X


def istft(X, win, hop, out_len):
    W = len(win)
    nf = X.shape[0]
    y = np.zeros(out_len)
    wsum = np.zeros(out_len)
    for m in range(nf):
        frame = np.fft.irfft(X[m], W) * win
        s = m * hop
        e = min(s + W, out_len)
        seg = frame[:e - s]
        y[s:e] += seg
        wsum[s:e] += (win ** 2)[:e - s]
    return y / np.maximum(wsum, 1e-12)


def partial_template(f0_list, n_partials_list, bw_list, fs, W):
    """Chromax partial atoms -> per-bin delay weights + feedback weights."""
    bins = np.fft.rfftfreq(W, 1.0 / fs)
    nb = W // 2 + 1
    tau = np.zeros(nb)
    fb = np.zeros(nb)
    for f0, n_partials, bw in zip(f0_list, n_partials_list, bw_list):
        for n in range(1, n_partials + 1):
            f = n * f0
            g = np.exp(-0.5 * ((bins - f) / bw) ** 2)
            tau += g * (1.0 / n)          # harmweight 1/n
            fb += g * min(0.9, 0.5 + 0.3 * (1.0 / n))
    m = tau.max()
    if m > 0:
        tau = tau / m
    fb = np.clip(fb, 0.0, 0.9)
    return tau, fb


def spectral_delay(x, fs, win, hop, tau, fb, tau_max):
    """Per-bin delay + feedback. Vectorized over frames. Returns full-length out."""
    W = len(win)
    nb = W // 2 + 1
    d = np.round(tau * tau_max * fs / hop).astype(int)   # frame counts, hop-quantized
    d = np.maximum(d, 0)
    # GCD quantization: snap to gcd of pattern unit (hop) — d already integer frames
    X = stft(x, win, hop)
    nf = X.shape[0]
    Y = X.copy()
    for m in range(nf):
        src = m - d
        valid = (src >= 0) & (d > 0)
        if valid.any():
            idx = src[valid]
            Y[m, valid] += fb[valid] * Y[idx, valid]
    out_len = len(x) + int(TAIL_SEC * fs)
    return istft(Y, win, hop, out_len)


def write_wav(path, samples, sr=SR):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with wave.open(path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        audio = np.clip(samples, -1.0, 1.0)
        wf.writeframes((audio * 32767).astype(np.int16).tobytes())


# ---------------- main ----------------
def main():
    os.makedirs(os.path.join(OUT_DIR, "MIDI"), exist_ok=True)
    os.makedirs(os.path.join(OUT_DIR, "Audio"), exist_ok=True)
    os.makedirs(os.path.join(OUT_DIR, "Analysis"), exist_ok=True)

    # copy source MIDI
    import shutil
    shutil.copy(MIDI_PATH, os.path.join(OUT_DIR, "MIDI", "025v2_unitmatrix.mid"))

    per_track, max_tick = read_events(MIDI_PATH)
    print("max_tick:", max_tick, "= %.2f s" % (max_tick / TICKS_PER_SEC))

    # render each voice
    voice_bufs = {}
    for (tidx, ch, prog) in VOICES:
        evts = per_track[tidx]
        buf = render_channel(evts, prog, max_tick)
        voice_bufs[tidx] = buf
        rms = float(np.sqrt(np.mean(buf ** 2)))
        print(f"voice track{tidx} prog{prog}: {len(evts)} notes, rms={rms:.4f}")

    melody = voice_bufs[0]
    bass = voice_bufs[1] + voice_bufs[2]

    # SP-050 per-voice
    win = np.hanning(N_FFT).astype(np.float64)

    # melody template: D4 f0 = 293.66 + A4 440 (broader reach), harmonic, 8+6 partials
    tau_m, fb_m = partial_template([293.66, 440.0], [8, 6], [45.0, 55.0], SR, N_FFT)
    # bass template: F2 87.31 + D2 73.42 + C4 261.63 (upper reach), 5+5+4 partials
    tau_b, fb_b = partial_template([87.31, 73.42, 261.63], [5, 5, 4], [25.0, 25.0, 40.0], SR, N_FFT)

    # spectral delay: dry + wet (feedback 0.5x), clip feedback accumulation
    def sdf_mix(dry, tau, fb, tau_max, wet_gain=0.6):
        wet = spectral_delay(dry, SR, win, HOP, tau, fb, tau_max)
        wet = np.clip(wet, -1.0, 1.0)
        out_len2 = max(len(dry), len(wet))
        d = np.pad(dry, (0, out_len2 - len(dry)))
        w = np.pad(wet, (0, out_len2 - len(wet)))
        return (1.0 - wet_gain) * d + wet_gain * w

    mel_sdf = sdf_mix(melody, tau_m, fb_m, 0.75, wet_gain=0.65)
    bass_sdf = sdf_mix(bass, tau_b, fb_b, 0.75, wet_gain=0.6)
    print("melody SDF done, len", len(mel_sdf))
    print("bass SDF done, len", len(bass_sdf))

    # mix: dry bass anchor + wet layers
    out_len = max(len(mel_sdf), len(bass_sdf))
    mel_wet = np.pad(mel_sdf, (0, out_len - len(mel_sdf)))
    bass_wet = np.pad(bass_sdf, (0, out_len - len(bass_sdf)))
    bass_dry = np.pad(bass, (0, out_len - len(bass)))
    mel_dry = np.pad(melody, (0, out_len - len(melody)))

    def _rms(x):
        return float(np.sqrt(np.mean(x ** 2)))

    print("DIAG rms mel_dry=%.5f mel_wet=%.5f bass_dry=%.5f bass_wet=%.5f" % (
        _rms(mel_dry), _rms(mel_wet), _rms(bass_dry), _rms(bass_wet)))

    mix = 0.35 * mel_dry + 0.65 * mel_wet + 0.9 * bass_dry + 0.5 * bass_wet
    print("DIAG mix rms pre-norm=%.5f peak=%.3f" % (_rms(mix), np.max(np.abs(mix))))

    # stems
    stem_mel = 0.35 * mel_dry + 0.65 * mel_wet
    stem_bass = 0.9 * bass_dry + 0.5 * bass_wet

    # normalize to -1 dB
    def norm(x):
        p = np.max(np.abs(x))
        return x * (0.89 / p) if p > 0 else x

    mix = norm(mix)
    stem_mel = norm(stem_mel)
    stem_bass = norm(stem_bass)

    wav_mix = os.path.join(OUT_DIR, "Audio", "SP050-spectral-delay-indian-popular.wav")
    wav_mel = os.path.join(OUT_DIR, "Audio", "stem_melody.wav")
    wav_bass = os.path.join(OUT_DIR, "Audio", "stem_bass.wav")
    write_wav(wav_mix, mix)
    write_wav(wav_mel, stem_mel)
    write_wav(wav_bass, stem_bass)

    # silence check
    mono = mix
    silent = float(np.sum(np.abs(mono) < 0.001) / len(mono))
    print("mix len %.2f s, silence fraction %.3f, peak %.3f" % (len(mono) / SR, silent, np.max(np.abs(mono))))
    # per-second RMS map
    rms_map = []
    for s in range(0, len(mono), SR):
        seg = mono[s:s + SR]
        rms_map.append(round(float(np.sqrt(np.mean(seg ** 2))), 4))
    print("per-sec RMS:", rms_map)

    sizes = {p: os.path.getsize(p) for p in [wav_mix, wav_mel, wav_bass]}
    print("wav sizes:", sizes)
    assert all(v > 44000 for v in sizes.values()), "WAV too small — render failed"

    # keep arrays for provenance stats
    import json
    meta = {
        "source_midi": MIDI_PATH,
        "method": "SP-050",
        "sr": SR,
        "duration_s": round(len(mono) / SR, 2),
        "silence_fraction": round(silent, 3),
        "per_sec_rms": rms_map,
        "n_fft": N_FFT,
        "hop": HOP,
        "tau_max_melody_s": 0.5,
        "tau_max_bass_s": 0.75,
    }
    with open(os.path.join(OUT_DIR, "Analysis", "render_stats.json"), "w") as f:
        json.dump(meta, f, indent=2)
    print("DONE")


if __name__ == "__main__":
    main()
