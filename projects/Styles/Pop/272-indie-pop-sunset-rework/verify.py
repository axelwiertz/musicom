# -*- coding: utf-8 -*-
"""Read-only verification audit for the rework artifacts."""
import os, json
import mido  # READING ONLY (analysis)

PROJ = os.path.dirname(os.path.abspath(__file__))
MIDI = os.path.join(PROJ, "MIDI")
BASE = "272-indie-pop-sunset-rework"
KEY_PCS = [2, 4, 5, 7, 9, 11, 0]
BAR = 1920

# per-bar degree per section (global bar -> chord tones pcs) for chord-violation check
SECTIONS = [
    ("Intro", 2, ['i', 'VII']),
    ("VerseA", 4, ['i', 'IV', 'i', 'v']),
    ("PreChorus", 2, ['VII', 'IV']),
    ("Chorus", 4, ['i', 'III', 'VII', 'IV']),
    ("VerseB", 4, ['i', 'VII', 'IV', 'v']),
    ("Bridge", 4, ['v', 'ii', 'VII', 'IV']),
    ("FinalChorus", 4, ['i', 'III', 'VII', 'IV']),
    ("Outro", 2, ['i', 'i']),
]
OFFSETS = [0, 2, 3, 5, 7, 9, 10]
CHORD_DEG = {
    'i': [0, 2, 4], 'ii': [1, 3, 5], 'III': [2, 4, 6], 'IV': [3, 5, 0],
    'v': [4, 6, 1], 'vi°': [5, 0, 2], 'VII': [6, 1, 3],
}
def chord_pcs(deg):
    return sorted({(2 + OFFSETS[s % 7]) % 12 for s in CHORD_DEG[deg]})

bar_degree = []          # global bar index -> degree name
bar_chord_pcs = []       # global bar index -> set of chord-tone pcs
for sname, bars, prog in SECTIONS:
    for b in range(bars):
        bar_degree.append(prog[b])
        bar_chord_pcs.append(set(chord_pcs(prog[b])))

def audit(path):
    res = {}
    m = mido.MidiFile(path)
    tracks = m.tracks[1:]          # skip tempo/conductor track 0
    lens = []
    for tr in tracks:
        t = 0
        for msg in tr:
            t += msg.time
        lens.append(t)
    res['tracks'] = len(tracks)
    res['all_equal_len'] = len(set(lens)) == 1
    res['len'] = lens[0] if lens else 0

    off = 0; pitched = 0
    scale_viol = 0; chord_viol = 0
    for tr in tracks:
        pc = [x for x in tr if x.type == 'program_change']
        ch = pc[0].channel if pc else -1
        t = 0
        for msg in tr:
            t += msg.time
            if msg.type != 'note_on' or msg.velocity == 0 or msg.note == 0:
                continue
            if ch == 9:
                continue   # drums skipped
            pitched += 1
            if not (t % 120 == 0 or t % 240 == 0):
                off += 1
            if (msg.note % 12) not in KEY_PCS:
                scale_viol += 1
            bar = t // BAR
            if bar < len(bar_chord_pcs) and (msg.note % 12) not in bar_chord_pcs[bar]:
                chord_viol += 1
    res['pitched_onsets'] = pitched
    res['off_grid'] = off
    res['scale_viol'] = scale_viol
    res['chord_viol'] = chord_viol
    return res


summary = {}
for variant in ["perfect", "humanized", "phase1"]:
    p = os.path.join(MIDI, f"{BASE}-{variant}.mid")
    sz = os.path.getsize(p)
    assert sz > 40, f"{p} too small: {sz}"
    r = audit(p)
    r['size_bytes'] = sz
    summary[variant] = r

print(json.dumps(summary, indent=2))
with open(os.path.join(PROJ, "Analysis", "verify.json"), "w") as f:
    json.dump(summary, f, indent=2)
print("verify.json written")