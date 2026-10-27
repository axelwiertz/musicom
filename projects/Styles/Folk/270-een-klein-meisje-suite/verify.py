# -*- coding: utf-8 -*-
# READING ONLY (analysis) — mido used to audit generated MIDI, never to author.
import os, json, mido

BASE = "/opt/data/projects/Styles/Folk/270-een-klein-meisje-suite"
MIDI = os.path.join(BASE, "MIDI")
PROJ = "270-een-klein-meisje-suite"

TPB = 480
BAR = 1920
KEY_PCS = {7, 9, 11, 0, 2, 4, 6}          # G Major
INTERVALS = [0, 2, 4, 5, 7, 9, 11]
QUALITY = {1: (0, 4, 7), 2: (0, 3, 7), 3: (0, 3, 7), 4: (0, 4, 7),
           5: (0, 4, 7), 6: (0, 3, 7), 7: (0, 3, 6)}
# flat per-bar degree (8 sections x 4 bars)
BAR_DEGREES = ([1, 4, 5, 1] + [1, 6, 2, 5] + [6, 4, 3, 5] + [4, 5, 6, 1]
               + [5, 2, 5, 6] + [6, 4, 5, 1] + [1, 5, 6, 4] + [4, 5, 1, 1])
assert len(BAR_DEGREES) == 32, len(BAR_DEGREES)

def chord_pc_set(d):
    root_pc = (7 + INTERVALS[d - 1]) % 12
    return {(root_pc + iv) % 12 for iv in QUALITY[d]}


def audit(path):
    mid = mido.MidiFile(path)
    tracks = mid.tracks
    lens = [sum(m.time for m in t) for t in tracks]
    n_voice = len(tracks) - 1
    drift = len(set(lens[1:])) == 1
    pitched = 0
    offgrid = 0
    scale_viol = 0
    chord_viol = 0
    for t in tracks[1:]:
        abs_t = 0
        for m in t:
            abs_t += m.time
            if m.type == 'note_on' and m.velocity > 0:
                if m.channel == 9:
                    continue
                pitched += 1
                if not (abs_t % 120 == 0 or abs_t % 240 == 0):
                    offgrid += 1
                pc = m.note % 12
                if pc not in KEY_PCS:
                    scale_viol += 1
                bar = min(abs_t // BAR, 31)
                if pc not in chord_pc_set(BAR_DEGREES[bar]):
                    chord_viol += 1
    return dict(tracks=len(tracks), voice=n_voice, lens=lens[1:], drift=drift,
                pitched=pitched, offgrid=offgrid, scale_viol=scale_viol,
                chord_viol=chord_viol)


report = {}
for tag in ("phase1", "perfect", "humanized"):
    p = os.path.join(MIDI, f"{PROJ}-{tag}.mid")
    sz = os.path.getsize(p)
    r = audit(p)
    report[tag] = dict(size=sz, size_ok=sz > 40, **r)
    print(f"--- {tag} ---")
    print(f"  size={sz} ok={sz>40} tracks={r['tracks']} voices={r['voice']}")
    print(f"  lens={r['lens']} drift={r['drift']}")
    print(f"  pitched={r['pitched']} offgrid={r['offgrid']} scale_viol={r['scale_viol']} chord_viol={r['chord_viol']}")

with open(os.path.join(BASE, "Analysis", "verify_report.json"), "w") as f:
    json.dump(report, f, indent=2)
print("VERIFY_OK")
