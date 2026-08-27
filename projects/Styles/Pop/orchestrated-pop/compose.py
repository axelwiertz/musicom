# -*- coding: utf-8 -*-
"""
Orchestrated Pop — full pipeline through Instruments KB + orchestrator.

Composition (Phase 1):
  - Framework: C major, 120 BPM, 4/4, I-V-vi-IV
  - Roles from orchestrator.ORCHESTRATION_PRESETS["pop"] (+ counter)
  - Registers from orchestrator.allocate_registers (non-crossing)
  - Velocity from orchestrator.velocity_for (balance)
  - Section dynamics from orchestrator.section_roles
  - Instruments from the Instruments KB (Strings.violin, Keys.piano,
    Brass.trumpet, Woodwind.flute, Percussion.drum_kit, Strings.cello)

Output: MIDI (zero-drift), grid, provenance.
"""

import os
import sys

sys.path.insert(0, "/opt/data/projects/Instruments")

from orchestrator import (
    ORCHESTRATION_PRESETS, allocate_registers, velocity_for,
    section_roles, instrument_program, ROLE_PROFILES,
)
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED

BPM = 120
TPB = 480
BPB = 4
BAR = TPB * BPB

PRESET = "pop"
ROLES = ["melody", "harmony", "bass", "rhythm", "pad", "counter"]
SECTIONS = ["Intro", "Verse", "Chorus", "Bridge", "Outro"]
BARS = {s: ORCHESTRATION_PRESETS[PRESET]["bars"][s] for s in SECTIONS}

REGISTERS = allocate_registers(ROLES)

# Instruments per role (from KB mapping in orchestrator)
INSTRUMENTS = {role: ROLE_PROFILES[role]["primary"] for role in ROLES}

PROG = ['C', 'G', 'Am', 'F']
CHORDS = {
    'C': [60, 64, 67], 'G': [55, 59, 62],
    'Am': [57, 60, 64], 'F': [53, 57, 60],
}
C_MAJ = [60, 62, 64, 65, 67, 69, 71, 72]


def qchord(p, chord):
    tones = (CHORDS[chord] + [t + 12 for t in CHORDS[chord]]
             + [t - 12 for t in CHORDS[chord]])
    return min(tones, key=lambda t: abs(t - p))


def chord_prog(bar_idx, section):
    """Progression per section: verse/chorus I-V-vi-IV, bridge vi-IV-I-V."""
    if section == "Bridge":
        return ['Am', 'F', 'C', 'G'][bar_idx % 4]
    return PROG[bar_idx % 4]


def landmark(unit, ticks):
    if len(unit.data) == 0 or unit.len_ticks() < ticks:
        last = unit.len_ticks() if len(unit.data) else 0
        unit.add_event(MusicEvent(0, 0, last, ticks))


def build_role_unit(role, section, s_idx):
    bars_n = BARS[section]
    lo, hi = REGISTERS[role]
    vel = velocity_for(role)
    unit = MusicUnit()

    if role == "melody":
        for bar in range(bars_n):
            chord = chord_prog(bar, section)
            for beat in range(4):
                idx = (s_idx * 16 + bar * 4 + beat) % len(C_MAJ)
                p = qchord(C_MAJ[idx], chord)
                p = max(lo, min(hi, p))
                st = bar * BAR + beat * (BAR // 4)
                unit.add_event(MusicEvent(p, vel, st, st + BAR // 4))

    elif role == "counter":
        # octave-below echo of melody at half density (call-response)
        for bar in range(bars_n):
            chord = chord_prog(bar, section)
            for beat in range(2):
                idx = (s_idx * 8 + bar * 2 + beat) % len(C_MAJ)
                p = qchord(C_MAJ[idx], chord) - 12
                p = max(lo, min(hi, p))
                st = bar * BAR + beat * (BAR // 2) + BAR // 2  # offbeat answer
                unit.add_event(MusicEvent(p, vel, st, st + BAR // 2))

    elif role == "harmony":
        for bar in range(bars_n):
            chord = chord_prog(bar, section)
            for p in CHORDS[chord]:
                pp = p
                if pp < lo:
                    pp += 12
                if lo <= pp <= hi:
                    unit.add_event(MusicEvent(pp, vel, bar * BAR, (bar + 1) * BAR))

    elif role == "bass":
        for bar in range(bars_n):
            root = CHORDS[chord_prog(bar, section)][0]
            p = root - 12 if root - 12 >= lo else root
            for beat in range(2):
                st = bar * BAR + beat * (BAR // 2)
                unit.add_event(MusicEvent(p, vel, st, st + BAR // 2))

    elif role == "pad":
        for bar in range(bars_n):
            root = CHORDS[chord_prog(bar, section)][0]
            for p in [root - 12, root - 5, root + 4]:
                if lo <= p <= hi:
                    unit.add_event(MusicEvent(p, vel, bar * BAR, (bar + 1) * BAR))

    elif role == "rhythm":
        kick = [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]
        snare = [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]
        hat = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
        step = BAR // 16
        for bar in range(bars_n):
            if section == "Intro" and bar < 2:
                continue  # build-in
            if section == "Outro" and bar >= 2:
                continue  # dropout
            for i in range(16):
                if kick[i]:
                    st = bar * BAR + i * step
                    unit.add_event(MusicEvent(36, vel + 15, st, st + step))
                if snare[i]:
                    st = bar * BAR + i * step
                    unit.add_event(MusicEvent(38, vel + 5, st, st + step))
                if hat[i]:
                    st = bar * BAR + i * step
                    unit.add_event(MusicEvent(42, vel - 15, st, st + step))

    landmark(unit, bars_n * BAR)
    return unit


def build_composer():
    comp = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    comp.create_matrix(num_voices=len(ROLES), num_sections=len(SECTIONS))

    for i, role in enumerate(ROLES):
        inst_name = INSTRUMENTS[role]
        prog = instrument_program(inst_name)
        ch = 9 if role == "rhythm" else i
        comp.add_voice(f"{role}({inst_name})", program=prog, channel=ch)

    for s in SECTIONS:
        comp.add_section(s, bars=BARS[s])

    for s_idx, section in enumerate(SECTIONS):
        active = section_roles(section) or ROLES  # fallback: all
        for r, role in enumerate(ROLES):
            if role in active:
                comp.set_unit(r, s_idx, build_role_unit(role, section, s_idx))
            else:
                u = MusicUnit()
                u.add_event(MusicEvent(0, 0, 0, BARS[section] * BAR))
                comp.set_unit(r, s_idx, u)

    ok, msg = comp.validate()
    if not ok:
        raise ValueError(f"Zero-drift validation failed: {msg}")
    return comp


def compose_to(project_dir):
    os.makedirs(os.path.join(project_dir, 'MIDI'), exist_ok=True)
    os.makedirs(os.path.join(project_dir, 'Analysis'), exist_ok=True)

    comp = build_composer()
    midi_path = os.path.join(project_dir, 'MIDI', 'orchestrated_pop.mid')
    comp.to_midi(midi_path)
    assert os.path.getsize(midi_path) > 40, "Empty MIDI!"

    grid_path = os.path.join(project_dir, 'Analysis', 'grid_visualization.txt')
    write_grid_visualization(
        comp.matrix, grid_path,
        voice_names=[f"{r}({INSTRUMENTS[r]})" for r in ROLES], bpm=BPM,
    )

    write_provenance(
        midi_path, AI_ASSISTED,
        "musicom orchestrator + Instruments KB (pop preset)",
        sources=["orchestrator.py", "Instruments registry", "I-V-vi-IV"],
        parameters={
            "bpm": BPM, "roles": ROLES,
            "instruments": INSTRUMENTS,
            "registers": REGISTERS,
        },
        notes="Orchestrated pop: roles->instruments->registers->dynamics->balance",
    )
    return midi_path, grid_path


if __name__ == '__main__':
    out = '/opt/data/projects/Styles/Pop/orchestrated-pop'
    midi, grid = compose_to(out)
    print(f"MIDI: {midi} ({os.path.getsize(midi)} bytes)")
    print(f"Grid: {grid}")
    print("Instruments:", INSTRUMENTS)
    print("Registers:", REGISTERS)
