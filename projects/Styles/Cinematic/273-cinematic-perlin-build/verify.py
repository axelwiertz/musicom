# -*- coding: utf-8 -*-
# READING ONLY (analysis) -- mido used to audit generated MIDI, never to author.
import os, json, mido
from structures import MusicUnit, MusicEvent  # musicom structures (read-only companion)

BASE = "/opt/data/projects/Styles/Cinematic/273-cinematic-perlin-build"
MIDI = os.path.join(BASE, "MIDI")
PROJ = "273-cinematic-perlin-build"

TPB = 480
BAR = 1920
KEY_PCS = {2, 4, 5, 7, 9, 10, 0}           # D minor (aeolian)
INTERVALS = [0, 2, 3, 5, 7, 8, 10]
QUALITY = {1: (0, 3, 7), 2: (0, 3, 6), 3: (0, 4, 7), 4: (0, 3, 7),
           5: (0, 3, 7), 6: (0, 4, 7), 7: (0, 4, 7)}
# cinematic-build: Intro 4 / Build 8 / Rise 8 / Peak 8 / Resolve 4 = 32 bars
BAR_DEGREES = ([1, 1, 6, 7]
               + [1, 6, 3, 7, 1, 6, 3, 7]
               + [6, 7, 1, 5, 4, 7, 1, 5]
               + [1, 6, 3, 7, 1, 6, 3, 7]
               + [1, 6, 7, 1])
assert len(BAR_DEGREES) == 32, len(BAR_DEGREES)


def chord_pc_set(d):
    root_pc = (2 + INTERVALS[d - 1]) % 12
    return {(root_pc + iv) % 12 for iv in QUALITY[d]}


def audit(path):
    mid = mido.MidiFile(path)
    tracks = mid.tracks
    lens = [sum(m.time for m in t) for t in tracks]
    drift = len(set(lens[1:])) == 1
    STRONG = (0, 960)   # beats 1 & 3 within a bar
    per_voice = []
    for t in tracks[1:]:
        abs_t = 0
        p = dict(pitched=0, offgrid=0, strong_viol=0, weak_out_of_scale=0)
        for m in t:
            abs_t += m.time
            if m.type == 'note_on' and m.velocity > 0:
                if m.channel == 9:
                    continue
                p["pitched"] += 1
                if not (abs_t % 120 == 0 or abs_t % 240 == 0):
                    p["offgrid"] += 1
                pc = m.note % 12
                bar = min(abs_t // BAR, 31)
                in_scale = pc in KEY_PCS
                in_chord = pc in chord_pc_set(BAR_DEGREES[bar])
                if (abs_t % BAR) in STRONG:
                    if not (in_scale and in_chord):
                        p["strong_viol"] += 1
                else:
                    if not in_scale:
                        p["weak_out_of_scale"] += 1
        per_voice.append(p)
    agg = {k: sum(v[k] for v in per_voice) for k in per_voice[0]}
    return dict(tracks=len(tracks), voice=len(tracks) - 1, lens=lens[1:],
                drift=drift, per_voice=per_voice, **agg)


report = {}
for tag in ("phase1", "perfect", "humanized"):
    p = os.path.join(MIDI, f"{PROJ}-{tag}.mid")
    sz = os.path.getsize(p)
    r = audit(p)
    report[tag] = dict(size=sz, size_ok=sz > 40, **r)
    print(f"--- {tag} ---")
    print(f"  size={sz} ok={sz>40} tracks={r['tracks']} voices={r['voice']} "
          f"drift={r['drift']}")
    print(f"  lens={r['lens']}")
    print(f"  pitched={r['pitched']} offgrid={r['offgrid']} "
          f"strong_viol={r['strong_viol']} weak_out_of_scale={r['weak_out_of_scale']}")
    print(f"  per_voice={r['per_voice']}")

with open(os.path.join(BASE, "Analysis", "verify_report.json"), "w") as f:
    json.dump(report, f, indent=2)
print("VERIFY_OK")