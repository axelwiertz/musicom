# -*- coding: utf-8 -*-
# READING ONLY (analysis) -- read-only mido audits of the exported MIDIs.
import json
import os
import mido

PROJ = "304-trap-bibd-suite"
BASE = "/opt/data/projects/Styles/Trap/" + PROJ
MIDI_DIR = os.path.join(BASE, "MIDI")

KEY_PCS = {4, 6, 7, 9, 11, 0, 2}      # E natural minor
CHORD_PCS = {"i": {4, 7, 11}, "VI": {0, 4, 7},
             "III": {7, 11, 2}, "VII": {2, 6, 9}}
_VERSE_PROG = ["i", "VI", "III", "VII", "i", "VI", "III", "VII"]
BAR_PROG = _VERSE_PROG * 4
TOTAL_BARS = len(BAR_PROG)            # 32
BAR = 1920
BARS_PER = 8
STRONG = (0, 960)

BAR_PCS = [CHORD_PCS[c] for c in BAR_PROG]

# BIBD schedule (active pitched voices per verse; drums always active)
BIBD_ACTIVE = {
    0: {"Lead", "Pluck", "Pad"},
    1: {"Lead", "Pluck", "Bass"},
    2: {"Lead", "Pad", "Bass"},
    3: {"Pluck", "Pad", "Bass"},
}
# track order in the exported MIDI = VOICES order
VOICE_ORDER = ["Lead", "Pluck", "Pad", "Bass", "Drums"]


def audit(path):
    mid = mido.MidiFile(path)
    lengths = []
    for tr in mid.tracks[1:]:
        lengths.append(sum(m.time for m in tr if not m.is_meta))
    drift_ok = len(set(lengths)) == 1
    track_len = lengths[0] if drift_ok else lengths

    off120 = 0
    scale_viol = 0
    chord_viol = 0
    strong_viol = 0
    pitched = 0
    drum = 0
    per_voice = []
    for ti, tr in enumerate(mid.tracks[1:]):
        t = 0
        n = 0
        for m in tr:
            if not m.is_meta:
                t += m.time
            if m.type != "note_on" or m.velocity == 0:
                continue
            if m.channel == 9:
                drum += 1
                n += 1
                continue
            pitched += 1
            n += 1
            if t % 120 != 0:
                off120 += 1
            pc = m.note % 12
            bar = min(t // BAR, TOTAL_BARS - 1)
            in_scale = pc in KEY_PCS
            in_chord = pc in BAR_PCS[bar]
            if not in_scale:
                scale_viol += 1
            if not in_chord:
                chord_viol += 1
            if (t % BAR) in STRONG and not (in_scale and in_chord):
                strong_viol += 1
        per_voice.append(n)
    return {
        "tracks": len(mid.tracks) - 1,
        "track_len": track_len,
        "zero_drift": drift_ok,
        "pitched": pitched,
        "drum": drum,
        "off120": off120,
        "scale_violations": scale_viol,
        "chord_violations_blanket": chord_viol,
        "strong_beat_violations": strong_viol,
        "per_voice_note_counts": per_voice,
    }


def audit_bibd(path):
    """Confirm the BIBD ensemble schedule: tacet voices have 0 notes in their
    rest verse, active voices have >0. Returns per-verse violation count."""
    mid = mido.MidiFile(path)
    # map voice track -> (name, events by verse)
    bars_per_sec = 8
    sec_ticks = bars_per_sec * BAR
    violations = 0
    # accumulate note-on count per (voice, verse)
    counts = {}
    for ti, tr in enumerate(mid.tracks[1:]):
        vname = VOICE_ORDER[ti] if ti < len(VOICE_ORDER) else f"tr{ti}"
        t = 0
        for m in tr:
            if not m.is_meta:
                t += m.time
            if m.type != "note_on" or m.velocity == 0:
                continue
            if m.channel == 9:
                continue
            sec = min(t // sec_ticks, 3)
            counts.setdefault((vname, sec), 0)
            counts[(vname, sec)] += 1
    for sec in range(4):
        active = BIBD_ACTIVE[sec]
        for vname in ("Lead", "Pluck", "Pad", "Bass"):
            n = counts.get((vname, sec), 0)
            if vname in active and n == 0:
                violations += 1
            if vname not in active and n > 0:
                violations += 1
    return violations, counts


report = {}
for ver in ("phase1", "perfect", "humanized"):
    p = os.path.join(MIDI_DIR, PROJ + "-" + ver + ".mid")
    assert os.path.getsize(p) > 40, "empty/corrupt: %s" % p
    report[ver] = audit(p)

perf = report["perfect"]
hum = report["humanized"]

assert perf["zero_drift"], "perfect zero-drift FAILED"
assert hum["zero_drift"], "humanized zero-drift FAILED"

assert perf["off120"] == 0, "perfect off-grid != 0 (%s)" % perf["off120"]
assert perf["scale_violations"] == 0, "perfect scale violations != 0 (%s)" % perf["scale_violations"]
assert perf["strong_beat_violations"] == 0, "perfect strong-beat violations != 0"
# NOTE: chord_violations_blanket counts weak notes that are scale-tone-but-not-
# chord-tone. Under the TIERED pitch discipline these are LEGAL (weak notes snap
# to scale only; strong notes snap to scale AND chord). 0 strong-beat violations
# + 0 scale violations is the correct gate. We report the blanket count for
# information only.

assert hum["off120"] > 0, "humanized off-grid == 0 (jitter did not run)"
assert hum["scale_violations"] == 0, "humanized scale violations != 0 (%s)" % hum["scale_violations"]
assert hum["strong_beat_violations"] == 0, "humanized strong-beat violations != 0 (%s)" % hum["strong_beat_violations"]

bibd_viol, bibd_counts = audit_bibd(os.path.join(MIDI_DIR, PROJ + "-perfect.mid"))
assert bibd_viol == 0, "BIBD schedule violation: %s" % bibd_viol

out = {"project": PROJ, "report": report,
       "bibd_schedule_violations": bibd_viol,
       "bibd_voice_section_counts": {f"{k[0]}@{k[1]}": v for k, v in sorted(bibd_counts.items())},
       "verdict": "PASS"}
print(json.dumps(out, indent=2))
with open(os.path.join(BASE, "Analysis", "verification.json"), "w") as f:
    json.dump(out, f, indent=2, default=str)
print("VERIFY_OK")
