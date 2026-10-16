# -*- coding: utf-8 -*-
"""Pre-flight rework of HITL cand3 (ballad-hitl round0) to pass the 3-rule gate.

Source : Pop/ballad-hitl/HITL/round0/candidates/cand3-pViol-ldX-ar4-pdpuls-drful-bXo0.mid
Fixes  :
  - chord-tone quantize every pitched voice (lead/pad/arp) to its bar's triad
    (i-VI-III-VII region map, D aeolian), preserving register/octave + duration.
  - fix the single out-of-scale Eb (pc 3) in the bridge lead.
  - zero-drift: pad every voice to 28 bars = 53760 ticks (terminal landmark).
  - distinct MIDI channels per voice (orig put all 4 pitched voices on ch0 ->
    program-change collision in FluidSynth).
Uses the musicom engine (UnitMatrixComposer), NOT hand-rolled mido export.
"""
import shutil
from pathlib import Path

import mido

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

SRC = Path("/opt/data/repos/musicom/projects/Styles/Pop/ballad-hitl/HITL/round0/candidates/cand3-pViol-ldX-ar4-pdpuls-drful-bXo0.mid")
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/SP099-ir-designer-ballad-hitl-cand3")
MIDIDIR = OUT / "MIDI"
SCRIPTS = OUT / "Scripts"
for d in (MIDIDIR, SCRIPTS):
    d.mkdir(parents=True, exist_ok=True)

BPM = 72.0
TPB = 480
BAR = TPB * 4            # 1920
NBARS = 28
TOTAL = NBARS * BAR      # 53760

# ---- per-bar chord regions (bass-root triads, D aeolian) -------------------
CHORD_PCS = {
    "i":   {2, 5, 9},    # Dm
    "VI":  {10, 2, 5},   # Bb
    "III": {5, 9, 0},    # F
    "VII": {0, 4, 7},    # C
}
REGIONS = (["i"] * 2 + ["VI"] * 2 + ["i"] * 2 + ["VI"] * 2 +
           ["III"] * 2 + ["VII"] * 2 + ["III"] * 2 + ["VII"] * 2 +
           ["i"] * 2 + ["VI"] * 2 + ["VII"] * 2 + ["VI"] * 2 +
           ["i"] * 2 + ["VI"] * 2)
assert len(REGIONS) == NBARS, len(REGIONS)
BAR_CHORD = [CHORD_PCS[REGIONS[b]] for b in range(NBARS)]

# ---- voice identity: program -> (role, new_channel) ------------------------
VOICE_BY_PROG = {
    40: ("Lead", 0),   # Violin
    1:  ("Pad",  1),   # Piano
    42: ("Bass", 2),   # Cello
    41: ("Arp",  3),   # Viola
}

# ---- read source MIDI, collect per-voice events (absolute ticks) -----------
def read_events(path):
    mf = mido.MidiFile(str(path))
    voices = {}   # role -> list of (pitch, vel, start, end)
    drums = []
    for tr in mf.tracks:
        t = 0
        pending = {}
        progs = {}
        for m in tr:
            t += m.time
            if m.type == "program_change":
                progs[m.channel] = m.program
            if m.type == "note_on" and m.velocity > 0:
                pending[(m.channel, m.note)] = (t, m.velocity)
            elif (m.type == "note_off" or (m.type == "note_on" and m.velocity == 0)) \
                    and (m.channel, m.note) in pending:
                st, vel = pending.pop((m.channel, m.note))
                if m.channel == 9:
                    drums.append((m.note, vel, st, t))
                else:
                    prog = progs.get(m.channel)
                    if prog in VOICE_BY_PROG:
                        role, _ch = VOICE_BY_PROG[prog]
                        voices.setdefault(role, []).append((m.note, vel, st, t))
    return voices, drums

voices, drums = read_events(SRC)
print("voice note counts:", {k: len(v) for k, v in voices.items()}, "drums:", len(drums))

def quantize_pitch(p, bar):
    pcs = BAR_CHORD[bar]
    best = p
    best_d = 999
    for pc in pcs:
        cand = pc + 12 * round((p - pc) / 12.0)
        d = abs(cand - p)
        if d < best_d:
            best_d = d
            best = cand
    return int(best)

# ---- quantize pitched voices to chord tones --------------------------------
changes = 0
qvoices = {}
for role, evlist in voices.items():
    q = []
    for pitch, vel, st, en in evlist:
        bar = min(st // BAR, NBARS - 1)
        np_ = quantize_pitch(pitch, bar)
        if np_ != pitch:
            changes += 1
        q.append((np_, vel, st, en))
    qvoices[role] = q
print("pitch changes applied:", changes)

# ---- rebuild via UnitMatrixComposer ----------------------------------------
composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=4)
composer.create_matrix(num_voices=5, num_sections=1)

for role, prog, ch in [
    ("Lead", 40, 0), ("Pad", 1, 1), ("Bass", 42, 2), ("Arp", 41, 3),
]:
    composer.add_voice(role, program=prog, channel=ch)
composer.add_voice("Drums", program=0, channel=9)
composer.add_section("Full", bars=NBARS)

def make_unit(evlist, total):
    evs = []
    for pitch, vel, st, en in evlist:
        st = int(st); en = int(en)
        st = max(0, min(st, total - 1))
        en = max(st + 1, min(en, total))
        evs.append(MusicEvent(pitch=int(pitch), volume=int(vel), start_tick=st, end_tick=en))
    # terminal landmark -> forces len_ticks == total (zero-drift pad)
    evs.append(MusicEvent(pitch=0, volume=0, start_tick=total - 1, end_tick=total))
    return MusicUnit(events=evs)

for role, ch in [("Lead", 0), ("Pad", 1), ("Bass", 2), ("Arp", 3)]:
    composer.fill_voice_section(role, "Full", make_unit(qvoices[role], TOTAL))
composer.fill_voice_section("Drums", "Full", make_unit(drums, TOTAL))

ok, msg = composer.validate()
print("validate:", ok, msg)
assert ok, msg

# ---- phase-1 sidecar (preserve original) ----------------------------------
phase1 = MIDIDIR / (SRC.stem + "-phase1.mid")
shutil.copy2(str(SRC), str(phase1))

# ---- reworked (phase-2) export --------------------------------------------
out_mid = MIDIDIR / (SRC.stem + ".mid")
composer.to_midi(str(out_mid))
print("wrote", out_mid, out_mid.stat().st_size, "bytes")

# copy this script into the output Scripts dir
shutil.copy2(__file__, str(SCRIPTS / "rework_cand3.py"))
print("Done.")
