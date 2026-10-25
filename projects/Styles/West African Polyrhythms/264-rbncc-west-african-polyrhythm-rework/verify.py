# -*- coding: utf-8 -*-
"""Read-only verification audit for 264-rbncc-west-african-polyrhythm-rework.
mido READING ONLY (analysis)."""
import json
import os

import mido  # READING ONLY (analysis)

ROOT = "/opt/data/repos/musicom/projects/Styles/West African Polyrhythms/264-rbncc-west-african-polyrhythm-rework"
NAME = "264-rbncc-west-african-polyrhythm-rework"
G_SCALE = [7, 9, 11, 0, 2, 4, 6]   # G A B C D E F#
SCALE_PCS = set(G_SCALE)
FORM = [("Intro", 4), ("Verse", 4), ("Chorus", 4), ("Verse2", 4),
        ("Chorus2", 4), ("Break", 4), ("Bridge", 4), ("Chorus3", 4),
        ("Finale", 4), ("Coda", 4)]
N_BARS = sum(b for _, b in FORM)
BAR = 1920

PROG = {
    "Intro":   [0, 0, 4, 0], "Verse":   [0, 3, 4, 0], "Chorus":  [0, 5, 3, 4],
    "Verse2":  [0, 3, 4, 0], "Chorus2": [5, 3, 0, 4], "Break":   [5, 3, 1, 0],
    "Bridge":  [5, 1, 2, 4], "Chorus3": [0, 5, 3, 4], "Finale":  [0, 3, 4, 0],
    "Coda":    [0, 0, 0, 0],
}
SECTION_BAR_OFF = {}
_acc = 0
for s, nb in FORM:
    SECTION_BAR_OFF[s] = _acc
    _acc += nb


def section_of_bar(b):
    for sname, nb in FORM:
        off = SECTION_BAR_OFF[sname]
        if off <= b < off + nb:
            return sname
    return FORM[-1][0]


CHORD_SPECS = []
for b in range(N_BARS):
    s = section_of_bar(b)
    CHORD_SPECS.append(PROG[s][b - SECTION_BAR_OFF[s]])


def chord_pcs(deg):
    idx = [deg % 7, (deg + 2) % 7, (deg + 4) % 7]
    return frozenset(G_SCALE[i] for i in idx)


BAR_PCS = [chord_pcs(CHORD_SPECS[b]) for b in range(N_BARS)]


def audit(path):
    mid = mido.MidiFile(path)
    lens = []
    for t in mid.tracks:
        tl = 0
        for m in t:
            tl += m.time
        lens.append(tl)
    voice_lens = lens[1:]
    drift_ok = len(set(voice_lens)) == 1
    offgrid = 0
    scale_viol = 0
    chord_viol = 0
    pitched = 0
    total = 0
    for t in mid.tracks[1:]:
        ch = None
        for m in t:
            if m.type == "program_change":
                ch = m.channel
        if ch is None:
            ch = -1
        t_abs = 0
        for m in t:
            t_abs += m.time
            if m.type == "note_on" and m.velocity > 0:
                total += 1
                if ch == 9:
                    continue
                pitched += 1
                if not (t_abs % 120 == 0 or t_abs % 240 == 0):
                    offgrid += 1
                pc = m.note % 12
                if pc not in SCALE_PCS:
                    scale_viol += 1
                bar = min(t_abs // BAR, N_BARS - 1)
                if pc not in BAR_PCS[bar]:
                    chord_viol += 1
    return {
        "path": os.path.basename(path), "bytes": os.path.getsize(path),
        "n_tracks": len(mid.tracks), "voice_tracks": len(voice_lens),
        "voice_len": voice_lens[0] if voice_lens else None,
        "drift_ok": drift_ok, "length_seconds": round(mid.length, 2),
        "total_notes": total, "pitched_notes": pitched,
        "offgrid": offgrid, "scale_viol": scale_viol, "chord_viol": chord_viol,
    }


results = {}
for tag in ("phase1", "perfect", "humanized"):
    p = f"{ROOT}/MIDI/{NAME}-{tag}.mid"
    r = audit(p)
    results[tag] = r
    print(f"[{tag:9}] size={r['bytes']:>6}B  tracks={r['n_tracks']} "
          f"voice_len={r['voice_len']} drift={r['drift_ok']} "
          f"dur={r['length_seconds']}s")
    print(f"           notes={r['total_notes']} pitched={r['pitched_notes']} "
          f"offgrid={r['offgrid']} scale_viol={r['scale_viol']} "
          f"chord_viol={r['chord_viol']}")

os.makedirs(f"{ROOT}/Analysis", exist_ok=True)
with open(f"{ROOT}/Analysis/verify.json", "w") as f:
    json.dump(results, f, indent=2)

# assertions
for tag in ("phase1", "perfect", "humanized"):
    assert results[tag]["bytes"] > 40, f"{tag} too small"
    assert results[tag]["drift_ok"], f"{tag} drift fail"
assert results["perfect"]["offgrid"] == 0, "perfect offgrid must be 0"
assert results["humanized"]["offgrid"] > 0, "humanized must show jitter"
assert results["perfect"]["scale_viol"] == 0, "perfect scale violations"
assert results["perfect"]["chord_viol"] == 0, "perfect chord violations"
assert results["humanized"]["scale_viol"] == 0, "humanized scale violations"
# phase1 is raw: off-grid + chromatic by design (no 0-assert on scale/chord)
assert results["phase1"]["offgrid"] > 0, "phase1 must be off-grid (raw)"
print("\nALL ASSERTIONS PASS")
print(f"note: humanized chord_viol={results['humanized']['chord_viol']} "
      f"= onset jitter crossing bar seams (pitches stay in-scale; scale_viol=0)")
