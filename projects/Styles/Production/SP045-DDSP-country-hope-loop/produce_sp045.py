# -*- coding: utf-8 -*-
"""SP-045 DDSP production pass for 001-country-hope-loop-v7.mid.

DDSP (Differentiable Digital Signal Processing, Engel et al. 2020):
audio = harmonic additive oscillator bank + filtered noise, + reverb.
Here driven directly from MIDI (f0 exact, velocity -> loudness), avoiding
the CREPE pitch tracker (Symbolic pitch available -> bypass tracker per
method pitfall #1). Vectorized per-note render; algorithmic reverb via
synthetic decaying-noise IR + FFT convolution.
"""
import json, hashlib, subprocess, sys
from pathlib import Path
import numpy as np
import mido

SR = 44100
OUT_DIR = Path('/opt/data/projects/Styles/Production/SP045-DDSP-country-hope-loop')
AUDIO_DIR = OUT_DIR / 'Audio'
MIDI_DIR = OUT_DIR / 'MIDI'
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
MIDI_DIR.mkdir(parents=True, exist_ok=True)

SRC = Path('/opt/data/projects/Styles/Country/001-country-hope-loop/MIDI/country-hope-loop-v7.mid')
DST_MIDI = MIDI_DIR / 'original_country_hope_loop_v7.mid'


def midi_to_hz(p): return 440.0 * 2.0 ** ((p - 69) / 12.0)


def parse_notes(path):
    m = mido.MidiFile(path)
    tpb = m.ticks_per_beat
    tempo = 500000  # default 120bpm; override from tempo events
    for tr in m.tracks:
        for msg in tr:
            if msg.type == 'set_tempo':
                tempo = msg.tempo
                break
        else:
            continue
        break
    sec_per_tick = tempo / 1e6 / tpb
    active = {}
    notes = []
    t = 0
    for msg in m.tracks[1]:
        t += msg.time
        if msg.type == 'note_on' and msg.velocity > 0 and msg.channel != 9:
            active[msg.note] = (t, msg.velocity)
        elif msg.type in ('note_off',) or (msg.type == 'note_on' and msg.velocity == 0):
            if msg.note in active:
                st, vel = active.pop(msg.note)
                notes.append((st * sec_per_tick, t * sec_per_tick, msg.note, vel))
    notes.sort(key=lambda x: x[0])
    return notes


def adsr(n, a, d, s, r):
    env = np.ones(n)
    na = max(1, int(a * SR))
    nd = max(1, int(d * SR))
    nr = max(1, int(r * SR))
    ns = n - na - nd - nr
    if ns < 0:
        ns = 0
        nr = max(1, n - na - nd)
        ns = 0
    env[:na] = np.linspace(0, 1, na)
    if nd > 0 and na + nd <= n:
        env[na:na + nd] = np.linspace(1, s, nd)
    if na + nd < n:
        env[na + nd:n] = s
    if nr > 0 and n - nr >= 0:
        env[n - nr:] = np.linspace(s, 0, nr)
    return env


def harmonic_profile(k, z):
    # timbre code z shapes partial rolloff. flute-ish: ~1/k^1.6, few bright
    base = 1.0 / (np.arange(1, k + 1) ** 1.6)
    bright = np.exp(-np.arange(1, k + 1) * z)
    return base * bright


def render_note(f0, dur, vel, z, K=48, vib=0.0):
    n = int(dur * SR)
    if n < 64:
        n = 64
    t = np.arange(n) / SR
    phase0 = 2 * np.pi * np.cumsum(f0 * (1.0 + vib * np.sin(2 * np.pi * 5.0 * t))) / SR
    amps = harmonic_profile(K, z)
    amps = amps / (amps.sum() + 1e-9)
    gain = 0.30 * (vel / 127.0) ** 1.5
    env = adsr(n, a=0.012, d=0.08, s=0.6, r=0.12)
    yh = np.zeros(n)
    # cap harmonics below Nyquist
    kmax = int(SR / (2 * f0)) if f0 > 0 else 1
    kmax = min(K, kmax)
    for k in range(1, kmax + 1):
        yh += amps[k - 1] * np.sin(k * phase0)
    yh *= env * gain
    # filtered noise (breath/transient), lowpassed, decaying
    rng = np.random.default_rng(int(f0 * 1000) % (2**32))
    noise = rng.standard_normal(n)
    nb = 24  # rough lowpass taps
    kernel = np.ones(nb) / nb
    noise = np.convolve(noise, kernel, mode='same')
    nenv = env ** 1.5
    yn = noise * nenv * gain * 0.15
    return yh + yn


def schroeder_reverb(x, fs, decay=0.5, rt=1.4):
    # synthetic decaying-noise IR + FFT convolution
    rng = np.random.default_rng(7)
    ir_len = int(rt * fs)
    t = np.arange(ir_len) / fs
    ir = rng.standard_normal(ir_len) * np.exp(-t * (3.0 / rt))
    # normalize
    ir = ir / (np.linalg.norm(ir) + 1e-9)
    out = np.convolve(x, ir)[:len(x)]
    return out, ir


def peaknorm(x):
    p = np.max(np.abs(x))
    if p > 0:
        return x * (0.89 / p)
    return x


def write_wav(path, x):
    x = np.clip(x, -1.0, 1.0)
    data = (x * 32767).astype(np.int16)
    import wave
    with wave.open(str(path), 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(data.tobytes())


def analyze(x, path):
    mono = x.astype(np.float64)
    silent = float(np.sum(np.abs(mono) < 0.001) / len(mono))
    rms_per_s = []
    hop = SR
    for i in range(0, len(mono), hop):
        seg = mono[i:i + hop]
        rms_per_s.append(float(np.sqrt(np.mean(seg ** 2))) if len(seg) else 0.0)
    import json as J
    J.dump({"silence_fraction": silent, "rms_per_second": rms_per_s,
            "peak": float(np.max(np.abs(mono)))}, open(path, 'w'), indent=2)
    return silent


def main():
    notes = parse_notes(SRC)
    total_dur = max(e for _, e, _, _ in notes) + 1.5
    total = int(total_dur * SR)
    L = total + SR  # reverb tail room
    rng = np.random.default_rng(42)
    # rebuild stems exactly by rendering harmonic & noise separately
    mix2 = np.zeros(L)
    harm2 = np.zeros(L)
    noise2 = np.zeros(L)
    for st, en, pitch, vel in notes:
        dur = en - st
        f0 = midi_to_hz(pitch)
        n = int(dur * SR)
        if n < 64:
            n = 64
        t = np.arange(n) / SR
        z = 1.2 + 0.8 * rng.random()
        vib = 0.002 if pitch > 50 else 0.0
        phase0 = 2 * np.pi * np.cumsum(f0 * (1.0 + vib * np.sin(2 * np.pi * 5.0 * t))) / SR
        amps = harmonic_profile(48, z)
        amps = amps / (amps.sum() + 1e-9)
        gain = 0.30 * (vel / 127.0) ** 1.5
        env = adsr(n, 0.012, 0.08, 0.6, 0.12)
        kmax = min(48, int(SR / (2 * f0))) if f0 > 0 else 1
        yh = np.zeros(n)
        for k in range(1, kmax + 1):
            yh += amps[k - 1] * np.sin(k * phase0)
        yh *= env * gain
        rng2 = np.random.default_rng(int(f0 * 1000) % (2**32))
        noise_sig = rng2.standard_normal(n)
        nb = 24
        noise_sig = np.convolve(noise_sig, np.ones(nb) / nb, mode='same')
        yn = noise_sig * (env ** 1.5) * gain * 0.15
        idx = int(st * SR)
        e = min(idx + n, L)
        mix2[idx:e] += (yh + yn)[:e - idx]
        harm2[idx:e] += yh[:e - idx]
        noise2[idx:e] += yn[:e - idx]

    # reverb on full mix
    wet, ir = schroeder_reverb(mix2, SR)
    wet = wet * 0.35
    out = mix2 * 0.75 + wet

    out = peaknorm(out)
    harm2 = peaknorm(harm2)
    noise2 = peaknorm(noise2)
    mix2 = peaknorm(mix2)

    wav = AUDIO_DIR / 'SP045-DDSP-country-hope-loop-fullmix.wav'
    ogg = AUDIO_DIR / 'SP045-DDSP-country-hope-loop-fullmix.ogg'
    write_wav(wav, out)
    write_wav(AUDIO_DIR / 'stem_harmonic.wav', harm2)
    write_wav(AUDIO_DIR / 'stem_noise.wav', noise2)

    # ogg
    subprocess.run(['ffmpeg', '-y', '-i', str(wav), '-codec:a', 'libopus',
                    '-application', 'voip', '-b:a', '48k', str(ogg)],
                   check=True, capture_output=True)

    # copy original midi
    import shutil
    shutil.copyfile(SRC, DST_MIDI)

    # analysis
    sil = analyze(out, OUT_DIR / 'analysis.json')

    # provenance
    sha = hashlib.sha256(SRC.read_bytes()).hexdigest()
    prov = {
        "job": "nightly SP production",
        "composition_source": {
            "path": str(SRC), "sha256": sha,
            "track_count": 2, "notes": len(notes),
            "pitch_range": [min(n[2] for n in notes), max(n[2] for n in notes)],
            "duration_s": round(total_dur, 2),
            "tempo_bpm": 96.0,
        },
        "production_method": {
            "id": "SP-045",
            "name": "Differentiable Digital Signal Processing (DDSP)",
            "layer": "Synthesis Engines",
            "description": ("Harmonic additive oscillator bank (48 partials) + time-varying "
                            "lowpassed noise, driven from MIDI f0 (bypass tracker) and "
                            "velocity->loudness; synthetic decaying-noise IR reverb."),
        },
        "params": {
            "sample_rate": SR, "n_harmonics": 48, "noise_taps": 24,
            "noise_gain": 0.15, "reverb_mix": 0.35, "reverb_rt60": 1.4,
            "vibrato_hz": 5.0, "attack_s": 0.012, "release_s": 0.12,
        },
        "outputs": {
            "full_mix_wav": "Audio/SP045-DDSP-country-hope-loop-fullmix.wav",
            "full_mix_ogg": "Audio/SP045-DDSP-country-hope-loop-fullmix.ogg",
            "stem_harmonic": "Audio/stem_harmonic.wav",
            "stem_noise": "Audio/stem_noise.wav",
            "original_midi": "MIDI/original_country_hope_loop_v7.mid",
        },
        "analysis": {"silence_fraction": sil,
                     "out_dur_s": round(len(out) / SR, 2)},
    }
    (OUT_DIR / 'provenance.json').write_text(json.dumps(prov, indent=2))

    print("DONE")
    print("notes", len(notes), "dur_s", round(total_dur, 2))
    print("out_len", len(out), "wav_bytes", wav.stat().st_size)
    print("silence_fraction", round(sil, 4))
    print("ogg_bytes", ogg.stat().st_size)


if __name__ == '__main__':
    main()