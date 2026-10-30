# -*- coding: utf-8 -*-
# READING ONLY (analysis) — mido used to audit generated MIDI, never to author.
import os, json
import mido  # READING ONLY (analysis)
from structures import MusicUnit, MusicEvent  # musicom structures (read-only companion)

PROJ = "/opt/data/projects/Styles/Groove/274-groove-sieve-rework"
MIDI = os.path.join(PROJ, "MIDI")
BASE = "274-groove-sieve-rework"
BAR = 1920
KEY_ROOT_PC = 7
KEY_PCS = {7, 9, 10, 0, 2, 3, 5}          # G natural minor
SCALE_INTERVALS = [0, 2, 3, 5, 7, 8, 10]
DEGREE_STEP = {'i': 0, 'ii': 1, 'III': 2, 'iv': 3, 'v': 4, 'VI': 5, 'VII': 6}
QUALITY = {'i': (0, 3, 7), 'ii': (0, 3, 6), 'III': (0, 4, 7), 'iv': (0, 3, 7),
           'v': (0, 3, 7), 'VI': (0, 4, 7), 'VII': (0, 4, 7)}

SECTIONS = [
    ("Intro",     4, ['i', 'VII', 'i', 'VII']),
    ("VerseA",    4, ['i', 'III', 'iv', 'v']),
    ("VerseB",    4, ['i', 'iv', 'v', 'VI']),
    ("Chorus",    4, ['III', 'VII', 'i', 'iv']),
    ("Bridge",    4, ['VI', 'III', 'VII', 'v']),
    ("VerseC",    4, ['i', 'III', 'iv', 'v']),
    ("Chorus2",   4, ['III', 'VII', 'i', 'iv']),
    ("Outro",     4, ['i', 'VI', 'VII', 'i']),
]


def chord_pcs(deg):
    root = (KEY_ROOT_PC + SCALE_INTERVALS[DEGREE_STEP[deg]]) % 12
    return {(root + q) % 12 for q in QUALITY[deg]}


bar_degree = []
bar_chord_pcs = []
for sname, bars, prog in SECTIONS:
    for b in range(bars):
        bar_degree.append(prog[b])
        bar_chord_pcs.append(chord_pcs(prog[b]))
assert len(bar_degree) == 32


def audit(path):
    res = {}
    m = mido.MidiFile(path)
    tracks = m.tracks[1:]
    lens = []
    for tr in tracks:
        t = 0
        for msg in tr:
            t += msg.time
        lens.append(t)
    res['tracks'] = len(tracks)
    res['all_equal_len'] = len(set(lens)) == 1
    res['len'] = lens[0] if lens else 0
    res['lens'] = lens

    off = 0
    pitched = 0
    scale_viol = 0
    chord_viol = 0
    per_voice = []
    for tr in tracks:
        ch = None
        for x in tr:
            if x.type == 'program_change':
                ch = x.channel
        if ch == 9:
            continue
        pv = dict(pitched=0, off_grid=0, scale_viol=0, chord_viol=0)
        t = 0
        for msg in tr:
            t += msg.time
            if msg.type != 'note_on' or msg.velocity == 0 or msg.note == 0:
                continue
            pitched += 1
            pv['pitched'] += 1
            if not (t % 120 == 0 or t % 240 == 0):
                off += 1
                pv['off_grid'] += 1
            if (msg.note % 12) not in KEY_PCS:
                scale_viol += 1
                pv['scale_viol'] += 1
            bar = min(t // BAR, 31)
            if (msg.note % 12) not in bar_chord_pcs[bar]:
                chord_viol += 1
                pv['chord_viol'] += 1
        per_voice.append(pv)
    res['pitched_onsets'] = pitched
    res['off_grid'] = off
    res['scale_viol'] = scale_viol
    res['chord_viol'] = chord_viol
    res['per_voice'] = per_voice
    return res


summary = {}
for variant in ["phase1", "perfect", "humanized"]:
    p = os.path.join(MIDI, f"{BASE}-{variant}.mid")
    sz = os.path.getsize(p)
    assert sz > 40, f"{p} too small: {sz}"
    r = audit(p)
    r['size_bytes'] = sz
    summary[variant] = r
    print(f"--- {variant} ---")
    print(f"  size={sz} tracks={r['tracks']} equal_len={r['all_equal_len']} "
          f"len={r['len']}")
    print(f"  pitched={r['pitched_onsets']} off_grid={r['off_grid']} "
          f"scale_viol={r['scale_viol']} chord_viol={r['chord_viol']}")
    print(f"  per_voice={r['per_voice']}")

with open(os.path.join(PROJ, "Analysis", "verify.json"), "w") as f:
    json.dump(summary, f, indent=2)
print("VERIFY_OK")
