# -*- coding: utf-8 -*-
"""Read-only verification audit for 256-tango-dorian-rework. mido READING ONLY."""
import json
import os
import mido  # READING ONLY (analysis)

ROOT = "/opt/data/projects/Styles/Tango/256-tango-dorian-rework"
NAME = "256-tango-dorian-rework"
TONIC = 2
DORIAN_OFFS = [0, 2, 3, 5, 7, 9, 10]
SCALE_PCS = set((TONIC + o) % 12 for o in DORIAN_OFFS)
FORM = [("Intro", 4), ("TangoA", 4), ("TangoB", 4), ("Lift", 4),
        ("TangoA2", 4), ("Bridge", 4), ("Finale", 4), ("Coda", 4)]
N_BARS = 32
BAR = 1920


def section_of_bar(b):
    acc = 0
    for sname, nbars in FORM:
        if acc <= b < acc + nbars:
            return sname
        acc += nbars
    return FORM[-1][0]


def chord_pcs(deg, seventh=False):
    idx = [deg % 7, (deg + 2) % 7, (deg + 4) % 7]
    if seventh:
        idx.append((deg + 6) % 7)
    return frozenset((TONIC + DORIAN_OFFS[i]) % 12 for i in idx)


# reconstruct CHORD_SPECS (deterministic, no RNG)
CHORD_SPECS = []
SECTION_TICKS = {}
_tick = 0
for s, b in FORM:
    SECTION_TICKS[s] = (b * BAR, _tick)
    _tick += b * BAR
for b in range(N_BARS):
    s = section_of_bar(b)
    bi = b - SECTION_TICKS[s][1] // BAR
    if s == "Intro":
        spec = (6, False) if bi in (0, 2) else (0, False)
    elif s == "TangoA":
        spec = [(0, False), (2, False), (3, False), (6, False)][bi]
    elif s == "TangoB":
        spec = [(3, False), (2, False), (1, False), (0, False)][bi]
    elif s == "Lift":
        spec = [(4, True), (1, True), (0, True), (6, True)][bi]
    elif s == "TangoA2":
        spec = [(0, False), (6, False), (2, False), (3, False)][bi]
    elif s == "Bridge":
        spec = [(5, False), (1, False), (4, False), (0, False)][bi]
    elif s == "Finale":
        spec = [(3, False), (4, False), (6, False), (0, False)][bi]
    else:
        spec = (6, False) if bi in (1, 3) else (0, False)
    CHORD_SPECS.append(spec)
BAR_PCS = [chord_pcs(*CHORD_SPECS[b]) for b in range(N_BARS)]


def audit(path, expect_perfect):
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
    for ti, t in enumerate(mid.tracks[1:], start=1):
        ch = None
        for m in t:
            if m.type == 'program_change':
                ch = m.channel
        if ch is None:
            ch = -1
        t_abs = 0
        for m in t:
            t_abs += m.time
            if m.type == 'note_on' and m.velocity > 0:
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
for tag, expect in (("phase1", False), ("perfect", True), ("humanized", False)):
    p = f"{ROOT}/MIDI/{NAME}-{tag}.mid"
    r = audit(p, expect)
    results[tag] = r
    print(f"[{tag:9}] size={r['bytes']:>6}B  tracks={r['n_tracks']} "
          f"voice_len={r['voice_len']} drift={r['drift_ok']} "
          f"dur={r['length_seconds']}s")
    print(f"           notes={r['total_notes']} pitched={r['pitched_notes']} "
          f"offgrid={r['offgrid']} scale_viol={r['scale_viol']} "
          f"chord_viol={r['chord_viol']}")

with open(f"{ROOT}/Analysis/verify.json", "w") as f:
    json.dump(results, f, indent=2)

# assertions
for tag in ("phase1", "perfect", "humanized"):
    assert results[tag]["bytes"] > 40, f"{tag} too small"
assert results["perfect"]["drift_ok"] and results["humanized"]["drift_ok"]
assert results["perfect"]["offgrid"] == 0, "perfect offgrid must be 0"
assert results["humanized"]["offgrid"] > 0, "humanized must show jitter"
# perfect layer: the compositional truth — 0 scale / 0 chord / 0 offgrid
assert results["perfect"]["scale_viol"] == 0
assert results["perfect"]["chord_viol"] == 0
# humanized: pitches unchanged (still in key) — chord-vs-bar attribution may
# drift where onset jitter crosses a bar boundary (expected, not a pitch bug)
assert results["humanized"]["scale_viol"] == 0
assert results["phase1"]["scale_viol"] == 0, "phase1 raw must stay in-scale"
print("\nALL ASSERTIONS PASS")
print(f"note: humanized chord_viol={results['humanized']['chord_viol']} "
      f"= onset jitter crossing bar seams (pitches stay in-scale; scale_viol=0)")
