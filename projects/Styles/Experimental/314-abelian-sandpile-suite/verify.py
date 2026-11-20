# -*- coding: utf-8 -*-
# READING ONLY (analysis) — mido used to audit generated MIDI, never to author.
import os, json, mido

BASE = "/opt/data/projects/Styles/Experimental/314-abelian-sandpile-suite"
MIDI = os.path.join(BASE, "MIDI")
PROJ = "314-abelian-sandpile-suite"

TPB = 480
BAR = 1920
GRID = 120          # 16th
KEY_PCS = {2, 4, 5, 7, 9, 10, 0}      # D natural minor
INTERVALS = [0, 2, 3, 5, 7, 8, 10]
QUALITY = {1: (0, 3, 7), 2: (0, 3, 6), 3: (0, 4, 7), 4: (0, 3, 7),
           5: (0, 3, 7), 6: (0, 4, 7), 7: (0, 4, 7)}
# through-composed S1..S8 (4 bars each = 32 bars)
BAR_DEGREES = ([1, 3, 6, 7] + [1, 4, 1, 5] + [6, 7, 1, 5] + [4, 1, 7, 6]
               + [1, 6, 4, 5] + [3, 7, 1, 6] + [1, 3, 6, 7] + [1, 4, 7, 1])
assert len(BAR_DEGREES) == 32, len(BAR_DEGREES)


def chord_pc_set(d):
    root_pc = (2 + INTERVALS[d - 1]) % 12
    return {(root_pc + iv) % 12 for iv in QUALITY[d]}


def audit(path):
    mid = mido.MidiFile(path)
    tracks = mid.tracks
    lens = [sum(m.time for m in t) for t in tracks]
    drift = len(set(lens[1:])) == 1 if len(lens) > 1 else True
    per_voice = []
    for t in tracks[1:]:
        abs_t = 0
        ch = None
        p = dict(pitched=0, offgrid=0, out_of_scale=0, out_of_chord=0)
        for m in t:
            abs_t += m.time
            if m.type == "program_change":
                ch = m.channel
            elif m.type == "note_on" and m.velocity > 0:
                if ch == 9:
                    continue
                p["pitched"] += 1
                if abs_t % GRID != 0 and abs_t % (2 * GRID) != 0:
                    p["offgrid"] += 1
                pc = m.note % 12
                bar = min(abs_t // BAR, len(BAR_DEGREES) - 1)
                if pc not in KEY_PCS:
                    p["out_of_scale"] += 1
                if pc not in chord_pc_set(BAR_DEGREES[bar]):
                    p["out_of_chord"] += 1
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
    print(f"  size={sz} ok={sz > 40} tracks={r['tracks']} voices={r['voice']} "
          f"drift={r['drift']}")
    print(f"  lens={r['lens']}")
    print(f"  pitched={r['pitched']} offgrid={r['offgrid']} "
          f"out_of_scale={r['out_of_scale']} out_of_chord={r['out_of_chord']}")
    print(f"  per_voice={r['per_voice']}")

with open(os.path.join(BASE, "Analysis", "verify_report.json"), "w") as f:
    json.dump(report, f, indent=2)
print("VERIFY_OK")
