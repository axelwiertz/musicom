# -*- coding: utf-8 -*-
"""V4: loop phone with PERIOD-SYNCHRONOUS tiling (pitch-preserving, fast).

Fix for V3 hang: V3's loop_to_dur while-loop never advanced when
len(rest)==0 at the tail (pos stuck -> infinite loop at 100% CPU).

V4 tiling: precompute integer repeats, crossfade with FIXED hop =
len(seg)-XFADE (always advances). Vectorized, no while-loop stall.
"""
import mido
import numpy as np
import os
import wave

SR = 44100
OUT = "/opt/data/repos/musicom/projects/Styles/Production/SP036-formant-lsystem-choir"
SRC = OUT + "/MIDI/lsystem_study.mid"
TEMPO_US = 545455
TPB = 480

MELODY_VOWELS = ["aa", "ey", "iy", "ow", "uw", "ah", "ae", "ay"]
DARK_VOWELS = ["ao", "uw", "ow", "uh", "aa"]
DRONE_PHONE = "uw"
XF = int(0.008 * SR)


def midi_to_freq(m):
    return 440.0 * (2.0 ** ((m - 69) / 12.0))


def tick_to_sec(tick):
    return tick * TEMPO_US / TPB / 1e6


def parse_tracks(path):
    mid = mido.MidiFile(path)
    tracks = []
    for ti, tr in enumerate(mid.tracks):
        prog, ch = None, None
        for msg in tr:
            if msg.type == "program_change":
                prog, ch = msg.program, msg.channel
                break
        abstick = 0
        active = {}
        notes = []
        for msg in tr:
            abstick += msg.time
            if msg.type == "note_on" and msg.velocity > 0:
                active[msg.note] = (abstick, msg.velocity)
            elif msg.type in ("note_off",) or (msg.type == "note_on" and msg.velocity == 0):
                if msg.note in active:
                    s, vel = active.pop(msg.note)
                    notes.append({"pitch": msg.note, "start": tick_to_sec(s),
                                  "end": tick_to_sec(abstick), "vel": vel})
        notes.sort(key=lambda e: e["start"])
        tracks.append({"idx": ti, "prog": prog, "ch": ch, "notes": notes})
    return tracks


def adsr(n, sr, attack=0.008, release=0.040):
    a = max(1, int(attack * sr))
    r = max(1, int(release * sr))
    env = np.ones(n)
    env[:min(a, n)] = np.linspace(0.0, 1.0, min(a, n))
    if r < n:
        env[n - r:] = np.linspace(1.0, 0.0, r)
    return env


def save_wav(path, audio, sr=SR, stereo=False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    a = np.clip(np.asarray(audio, dtype=np.float64), -1.0, 1.0)
    with wave.open(path, "w") as wf:
        wf.setnchannels(2 if stereo else 1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes((a * 32767).astype(np.int16).tobytes())


def read_wav_mono(path):
    with wave.open(path, "r") as wf:
        n = wf.getnframes()
        ch = wf.getnchannels()
        raw = wf.readframes(n)
    a = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
    if ch > 1:
        a = a.reshape(-1, ch).mean(axis=1)
    return a


def tile_period_sync(seg, period_samples, n_target):
    """Repeat seg by glottal periods: hop = n_target tiling via reshape.

    seg is one phone unit (quasi-periodic voiced). Take hop = period_samples
    grid: out[t] = seg[t mod M] with M = round to whole periods fitting seg,
    crossfade over XF at each seg boundary to hide the reset click.
    """
    seg = np.asarray(seg, dtype=np.float64)
    M = len(seg)
    if M >= n_target:
        return seg[:n_target].copy()
    h = min(XF, M // 4)
    f_out = np.cos(np.linspace(0, np.pi / 2, h)) ** 2
    f_in = np.sin(np.linspace(0, np.pi / 2, h)) ** 2
    out = np.zeros(n_target)
    out[:M] = seg
    pos = M
    while pos < n_target:
        take = min(M, n_target - pos + h)
        chunk = seg[:take]
        m = min(h, take, n_target - pos)
        if m > 0:
            base = pos - m
            out[base:pos] = out[base:pos] * f_out[:m] + chunk[:m] * f_in[:m]
            rest = take - m
            if rest > 0:
                out[pos:pos + rest] = chunk[m:m + rest]
                pos += rest
            else:
                # tail shorter than xfade: done after blend
                pos = n_target
        else:
            out[pos:pos + take] = chunk[:take]
            pos += take
    return out


def main():
    from sound.synthesis.formant_voice import FormantVoiceSynth
    tracks = parse_tracks(SRC)
    dry = read_wav_mono(OUT + "/dry_full_mix.wav")
    n_total = len(dry)
    synth = FormantVoiceSynth(sample_rate=SR)
    melody_bus = np.zeros(n_total)
    drone_bus = np.zeros(n_total)

    for t in tracks:
        if not t["notes"]:
            continue
        is_melody = (t["prog"] == 80)
        for i, n in enumerate(t["notes"]):
            f0 = float(min(max(midi_to_freq(n["pitch"]), 40.0), 1000.0))
            dur = max(0.05, n["end"] - n["start"])
            vel_gain = float(np.clip((n["vel"] / 90.0) ** 1.2, 0.30, 1.15))
            phone = ((DARK_VOWELS[i % len(DARK_VOWELS)] if n["pitch"] < 50
                      else MELODY_VOWELS[i % len(MELODY_VOWELS)]) if is_melody
                     else DRONE_PHONE)
            seed = (1000 + i) if is_melody else (7000 + i)
            seg = np.asarray(synth.render_phones([(phone, f0)], f0=f0, amp=0.5,
                                                 seed=seed), dtype=np.float64)
            period = max(1, int(round(SR / f0)))
            tiled = tile_period_sync(seg, period, int(dur * SR))
            tiled = tiled * adsr(len(tiled), SR) * vel_gain
            s0 = int(n["start"] * SR)
            s1 = min(n_total, s0 + len(tiled))
            if is_melody:
                melody_bus[s0:s1] += tiled[:s1 - s0]
            else:
                drone_bus[s0:s1] += tiled[:s1 - s0]
        print(f"wet {'melody' if is_melody else 'drone'} track{t['idx']} done", flush=True)

    print(f"melody peak_raw={np.max(np.abs(melody_bus)):.4f} "
          f"drone peak_raw={np.max(np.abs(drone_bus)):.4f}", flush=True)
    for name, bus in (("track01_Lead_1_square", melody_bus), ("track02_Pad_1_new_age", drone_bus)):
        p = np.max(np.abs(bus))
        save_wav(OUT + f"/Audio/stems_wet/{name}.wav", bus / p * 0.89 if p > 1e-9 else bus)

    content_end = max(n["end"] for t in tracks for n in t["notes"])
    keep = int((content_end + 2.0) * SR)
    import math
    def gains(pan):
        return math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)
    glm, grm = gains(-0.25)
    gld, grd = gains(0.30)
    left = melody_bus * glm + drone_bus * 0.85 * gld
    right = melody_bus * grm + drone_bus * 0.85 * grd
    wet = np.column_stack([left, right])[:keep]
    pk = np.max(np.abs(wet))
    wet = wet / pk * 0.89 if pk > 1e-9 else wet

    from sound.effects.mastering import normalize_to_lufs, Limiter, measure_lufs
    print(f"pre-LUFS={measure_lufs(wet, sample_rate=SR):.2f}", flush=True)
    wet_lufs = normalize_to_lufs(wet, target_lufs=-14.0, sample_rate=SR)
    final = Limiter(threshold_db=-1.0, release_ms=100, sample_rate=SR).process(wet_lufs)
    print(f"final peak={np.max(np.abs(final)):.4f} LUFS={measure_lufs(final, sample_rate=SR):.2f}",
          flush=True)
    save_wav(OUT + "/SP036-formant-lsystem-choir.wav", final, stereo=True)
    print("WAV written", flush=True)


if __name__ == "__main__":
    main()
