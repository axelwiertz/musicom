# -*- coding: utf-8 -*-
"""Per-note strict-slot attribution on isolated wet stems (gap-aware windows)."""
import json
import mido
import numpy as np
import wave

SR = 44100
OUT = "/opt/data/repos/musicom/projects/Styles/Production/SP036-formant-lsystem-choir"
TEMPO_US = 545455
TPB = 480


def read_mono(path):
    with wave.open(path, "r") as wf:
        n = wf.getnframes()
        ch = wf.getnchannels()
        raw = wf.readframes(n)
    a = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
    if ch > 1:
        a = a.reshape(-1, ch).mean(axis=1)
    return a


def midi_to_freq(m):
    return 440.0 * (2.0 ** ((m - 69) / 12.0))


def parse_tracks(path):
    mid = mido.MidiFile(path)
    out = []
    for ti, tr in enumerate(mid.tracks):
        prog = None
        for msg in tr:
            if msg.type == "program_change":
                prog = msg.program
                break
        abstick = 0
        active = {}
        notes = []
        for msg in tr:
            abstick += msg.time
            if msg.type == "note_on" and msg.velocity > 0:
                active[msg.note] = abstick
            elif msg.type in ("note_off",) or (msg.type == "note_on" and msg.velocity == 0):
                if msg.note in active:
                    s = active.pop(msg.note)
                    notes.append({"pitch": msg.note,
                                  "start": s * TEMPO_US / TPB / 1e6,
                                  "end": abstick * TEMPO_US / TPB / 1e6})
        out.append({"idx": ti, "prog": prog, "notes": sorted(notes, key=lambda e: e["start"])})
    return out


def dom_peak(seg, sr, lo=50, hi=1000):
    w = seg * np.hanning(len(seg))
    spec = np.abs(np.fft.rfft(w))
    freqs = np.fft.rfftfreq(len(seg), 1.0 / sr)
    band = (freqs >= lo) & (freqs <= hi)
    fb, sb = freqs[band], spec[band]
    return float(fb[np.argmax(sb)]), spec, freqs


def harm_share(spec, freqs, f0, nh=8, hi=1000):
    band = (freqs >= 50) & (freqs <= hi)
    tot = float(np.sum(spec[band] ** 2)) + 1e-12
    e = 0.0
    for k in range(1, nh + 1):
        fk = f0 * k
        if fk > hi:
            break
        b = np.argmin(np.abs(freqs - fk))
        lo, hi2 = max(0, b - 2), min(len(spec), b + 3)
        e += float(np.sum(spec[lo:hi2] ** 2))
    return e / tot


tracks = parse_tracks(OUT + "/MIDI/lsystem_study.mid")
melody_notes = next(t["notes"] for t in tracks if t["prog"] == 80)
drone_notes = next(t["notes"] for t in tracks if t["prog"] == 88)
mel_stem = read_mono(OUT + "/Audio/stems_wet/track01_Lead_1_square.wav")
dro_stem = read_mono(OUT + "/Audio/stems_wet/track02_Pad_1_new_age.wav")

RES = 0.030  # 30 ms window floor (33 Hz bins)


def attribute(stem, notes, label):
    self_hits = neigh = other = skipped = 0
    ratios = []
    details = []
    for i, n in enumerate(notes):
        f0 = midi_to_freq(n["pitch"])
        # gap to next onset on SAME voice
        gap = (notes[i + 1]["start"] - n["start"]) if i + 1 < len(notes) else (n["end"] - n["start"])
        wlen = min(max(n["end"] - n["start"], RES), 0.150, 0.80 * gap)
        if wlen < RES:
            skipped += 1
            continue
        s0 = int(n["start"] * SR)
        seg = stem[s0:s0 + int(wlen * SR)]
        if len(seg) < int(RES * SR) or np.max(np.abs(seg)) < 1e-4:
            skipped += 1
            continue
        dom, spec, freqs = dom_peak(seg, SR)
        ratios.append(harm_share(spec, freqs, f0))
        # candidates: self f0 x1-4, prev/next note f0 x1-4
        def match(p):
            f = midi_to_freq(p)
            return any(abs(dom - f * k) / (f * k) <= 0.02 for k in (1, 2, 3, 4))
        if match(n["pitch"]):
            self_hits += 1
            res = "self"
        elif (i > 0 and match(notes[i - 1]["pitch"])) or (i + 1 < len(notes) and match(notes[i + 1]["pitch"])):
            neigh += 1
            res = "neigh"
        else:
            other += 1
            res = "other"
        details.append((round(n["start"], 2), n["pitch"], round(dom, 1), round(f0, 1),
                        round(wlen * 1000), res))
    tot = self_hits + neigh + other
    print(f"{label}: notes={len(notes)} slots={tot} skipped={skipped} "
          f"self={self_hits} neigh={neigh} other={other} "
          f"self_rate={self_hits/tot:.3f} tonal={(self_hits+neigh)/tot:.3f} "
          f"med_harm={float(np.median(ratios)) if ratios else 0:.3f}")
    for d in details:
        if d[5] == "other":
            print(f"  other t={d[0]}s pitch={d[1]} dom={d[2]}Hz f0={d[3]}Hz win={d[4]}ms")
    return self_hits, neigh, other, skipped, ratios


ms, mn, mo, mk, mrat = attribute(mel_stem, melody_notes, "melody")
ds, dn, do, dk, drat = attribute(dro_stem, drone_notes, "drone")

with open(OUT + "/Analysis/strict_slot.json", "w") as f:
    json.dump({"melody": {"self": ms, "neigh": mn, "other": mo, "skipped": mk,
                          "med_harm": float(np.median(mrat)) if mrat else 0},
               "drone": {"self": ds, "neigh": dn, "other": do, "skipped": dk,
                         "med_harm": float(np.median(drat)) if drat else 0}}, f, indent=2)
