# -*- coding: utf-8 -*-
"""Verify orchestration workflow: roles → registers → sections → MIDI → WAV."""
import sys
sys.path.insert(0, "/opt/data/projects/Instruments")

from orchestrator import (
    ROLE_PROFILES, allocate_registers, velocity_for,
    section_roles, instrument_program, ORCHESTRATION_PRESETS,
)
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

# --- Orchestration decisions ---
preset = "pop"
roles = ORCHESTRATION_PRESETS[preset]["roles"]
registers = allocate_registers(roles)

print("Roles:", roles)
print("Registers:", registers)
for role in roles:
    print(f"  {role}: program={instrument_program(ROLE_PROFILES[role]['primary'])} "
          f"vel={velocity_for(role)} range={registers[role]}")

# --- Build composition ---
comp = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
comp.create_matrix(num_voices=len(roles), num_sections=5)

for i, role in enumerate(roles):
    prog = instrument_program(ROLE_PROFILES[role]["primary"])
    if role == "rhythm":
        prog = 0
        ch = 9
    else:
        ch = i
    comp.add_voice(role.capitalize(), program=prog, channel=ch)

sections = ["Intro", "Verse", "Chorus", "Bridge", "Outro"]
for s in sections:
    comp.add_section(s, bars=ORCHESTRATION_PRESETS[preset]["bars"][s])

BAR = 1920
C_MAJ = [60, 62, 64, 65, 67, 69, 71, 72]
PROG = ['C', 'G', 'Am', 'F']
CHORDS = {'C': [60, 64, 67], 'G': [55, 59, 62], 'Am': [57, 60, 64], 'F': [53, 57, 60]}

def qchord(p, chord):
    tones = CHORDS[chord] + [t + 12 for t in CHORDS[chord]] + [t - 12 for t in CHORDS[chord]]
    return min(tones, key=lambda t: abs(t - p))

for s_idx, section in enumerate(sections):
    active = section_roles(section)
    bars_n = ORCHESTRATION_PRESETS[preset]["bars"][section]
    for r, role in enumerate(roles):
        if role not in active:
            unit = MusicUnit()
            unit.add_event(MusicEvent(0, 0, 0, bars_n * BAR))
            comp.set_unit(r, s_idx, unit)
            continue
        unit = MusicUnit()
        lo, hi = registers[role]
        vel = velocity_for(role)
        if role == "bass":
            # half notes on root
            for bar in range(bars_n):
                root = CHORDS[PROG[bar % 4]][0]
                p = max(lo, min(hi, root - 12 if root - 12 >= lo else root))
                for beat in range(2):
                    st = bar * BAR + beat * (BAR // 2)
                    unit.add_event(MusicEvent(p, vel, st, st + BAR // 2))
        elif role == "harmony":
            # whole-bar chords
            for bar in range(bars_n):
                chord = PROG[bar % 4]
                for p in CHORDS[chord]:
                    if lo <= p <= hi or p + 12 <= hi:
                        pp = p + 12 if p < lo else p
                        unit.add_event(MusicEvent(pp, vel, bar * BAR, (bar + 1) * BAR))
        elif role == "melody":
            # quarter notes up the scale
            for bar in range(bars_n):
                for beat in range(4):
                    idx = (s_idx * 4 + bar * 4 + beat) % len(C_MAJ)
                    p = qchord(C_MAJ[idx], PROG[bar % 4])
                    p = max(lo, min(hi, p))
                    st = bar * BAR + beat * (BAR // 4)
                    unit.add_event(MusicEvent(p, vel, st, st + BAR // 4))
        elif role == "pad":
            # sustained 5ths
            for bar in range(bars_n):
                root = CHORDS[PROG[bar % 4]][0]
                for p in [root - 12, root - 5]:
                    if lo <= p <= hi:
                        unit.add_event(MusicEvent(p, vel, bar * BAR, (bar + 1) * BAR))
        elif role == "rhythm":
            # beat-aligned kick/snare/hat
            kick = [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]
            snare = [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]
            step = BAR // 16
            for bar in range(bars_n):
                for i in range(16):
                    if kick[i]:
                        st = bar * BAR + i * step
                        unit.add_event(MusicEvent(36, vel, st, st + step))
                    if snare[i]:
                        st = bar * BAR + i * step
                        unit.add_event(MusicEvent(38, vel, st, st + step))
        # zero-drift landmark
        if unit.len_ticks() < bars_n * BAR:
            unit.add_event(MusicEvent(0, 0, unit.len_ticks(), bars_n * BAR))
        comp.set_unit(r, s_idx, unit)

ok, msg = comp.validate()
print(f"\nZero-drift: {ok} ({msg})")
assert ok, f"validate failed: {msg}"

import os
out_dir = "/opt/data/projects/Instruments/_test"
os.makedirs(out_dir, exist_ok=True)
midi_path = os.path.join(out_dir, "orchestration_test.mid")
comp.to_midi(midi_path)
print(f"MIDI: {midi_path} ({os.path.getsize(midi_path)} bytes)")

# Render
import subprocess
from _test.render_audio import render_midi, spectral_buzz_check
sf2_legacy = "/opt/data/micromamba/envs/musicom/lib/python3.11/site-packages/pretty_midi/TimGM6mb.sf2"
fl = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
wav = os.path.join(out_dir, "orchestration_test.wav")
r = subprocess.run([fl, "-ni", "-g", "1.2", "-F", wav, sf2_legacy, midi_path], capture_output=True)
print(f"FluidSynth exit: {r.returncode}, WAV: {os.path.getsize(wav)} bytes" if os.path.exists(wav) else f"FluidSynth FAILED: {r.stderr[:200]}")

# Onset grid audit (rhythm alignment)
import mido
mid = mido.MidiFile(midi_path)
for trk in mid.tracks:
    ch = None
    for m in trk:
        if m.type == "program_change":
            ch = m.channel
            break
    if ch == 9:
        t = 0
        off = []
        for m in trk:
            t += m.time
            if m.type == "note_on" and m.velocity > 0 and t % (BAR // 16) != 0:
                off.append(t)
        print(f"DRUMS off-grid onsets: {len(off)}")
