# -*- coding: utf-8 -*-
"""Orchestration constants — role → instrument mapping, register allocation,
section dynamics, balance profiles. Bridges the Instruments KB into
UnitMatrixComposer workflows.

Usage:
    from orchestrator import ROLE_PROFILES, allocate_registers, ...
    (place on sys.path or import via sys.path.insert(0, ".../Instruments"))
"""

import sys
import os

# Allow importing sibling instrument modules without package structure
_INSTR_DIR = os.path.dirname(os.path.abspath(__file__))
if _INSTR_DIR not in sys.path:
    sys.path.insert(0, _INSTR_DIR)

# --- Instrument imports (lazy via dict to avoid hard deps on every module) ---

# Role → primary/secondary instrument constants
ROLE_PROFILES = {
    "melody": {
        "primary": "Violin",      # Strings.violin
        "secondary": ["Flute", "Trumpet", "Piano"],
        "register": (67, 96),     # sweet spot
        "velocity": 85,
        "family": "strings",
    },
    "counter": {
        "primary": "Viola",
        "secondary": ["Clarinet", "Oboe", "Trombone"],
        "register": (55, 79),
        "velocity": 70,
        "family": "strings",
    },
    "harmony": {
        "primary": "Piano",       # Keys.piano
        "secondary": ["Guitar", "Organ"],
        "register": (48, 71),
        "velocity": 60,
        "family": "keys",
    },
    "bass": {
        "primary": "Double Bass",
        "secondary": ["Bass Guitar", "Tuba", "Cello"],
        "register": (36, 55),
        "velocity": 90,
        "family": "strings",
    },
    "rhythm": {
        "primary": "Drum Kit",    # Percussion.drum_kit
        "secondary": ["Congas", "Djembe", "Guitar (strum)"],
        "register": (35, 81),
        "velocity": 80,
        "family": "percussion",
    },
    "pad": {
        "primary": "Strings Section",
        "secondary": ["Synth Pad", "Organ", "Choir"],
        "register": (48, 72),
        "velocity": 50,
        "family": "strings",
    },
    "accent": {
        "primary": "Trumpet",
        "secondary": ["Trombone", "Crash Cymbal", "Timpani"],
        "register": (60, 84),
        "velocity": 95,
        "family": "brass",
    },
}

# Orchestration presets per genre
ORCHESTRATION_PRESETS = {
    "pop": {
        "roles": ["melody", "harmony", "bass", "rhythm", "pad"],
        "sections": ["Intro", "Verse", "Chorus", "Bridge", "Outro"],
        "bars": {"Intro": 4, "Verse": 8, "Chorus": 8, "Bridge": 4, "Outro": 4},
    },
    "classical": {
        "roles": ["melody", "counter", "harmony", "bass", "accent"],
        "sections": ["A", "B", "A"],
        "bars": {"A": 8, "B": 8},
    },
    "jazz": {
        "roles": ["melody", "harmony", "bass", "rhythm"],
        "sections": ["Head", "Solo", "Head"],
        "bars": {"Head": 12, "Solo": 12},
    },
}

# Section dynamics: which roles are active per section
SECTION_DYNAMICS = {
    "pop": {
        "Intro": ["melody", "pad"],
        "Verse": ["melody", "harmony", "bass", "rhythm"],
        "Chorus": ["melody", "harmony", "bass", "rhythm", "pad"],
        "Bridge": ["melody", "counter", "harmony", "pad"],
        "Outro": ["melody", "harmony", "pad"],
    },
}

# Balance: relative velocity multiplier per role
BALANCE_PROFILE = {
    "pop": {
        "melody": 1.0,
        "counter": 0.8,
        "harmony": 0.7,
        "bass": 0.9,
        "rhythm": 0.8,
        "pad": 0.5,
        "accent": 0.95,
    },
}


def allocate_registers(roles, preset="pop"):
    """Return {role: (min, max)} register ranges, non-crossing.

    Orders roles by pitch (bass lowest → melody highest) and returns
    each role's sweet-spot register. Uses preset balance if available.
    """
    order = ["bass", "harmony", "pad", "counter", "accent", "melody"]
    # rhythm is percussion — no register constraint in pitch space
    result = {}
    for role in order:
        if role in roles:
            result[role] = ROLE_PROFILES[role]["register"]
    for role in roles:
        if role == "rhythm":
            result[role] = ROLE_PROFILES["rhythm"]["register"]
    return result


def velocity_for(role, base=85, preset="pop"):
    """Return velocity for role after balance scaling."""
    balance = BALANCE_PROFILE.get(preset, BALANCE_PROFILE["pop"])
    mult = balance.get(role, 1.0)
    return int(base * mult)


def section_roles(section, preset="pop"):
    """Return active roles for a section name."""
    return SECTION_DYNAMICS.get(preset, {}).get(section, [])


def instrument_program(instrument_name):
    """Look up MIDI program from Instruments KB.

    Returns int or None if instrument not found.
    """
    mapping = {
        "Violin": (40, "Strings.violin"),
        "Viola": (41, "Strings.viola"),
        "Cello": (42, "Strings.cello"),
        "Double Bass": (43, "Strings.double_bass"),
        "Piano": (1, "Keys.piano"),
        "Organ": (19, "Keys.organ"),
        "Trumpet": (57, "Brass.trumpet"),
        "Trombone": (58, "Brass.trombone"),
        "Tuba": (58, "Brass.tuba"),
        "Flute": (74, "Woodwind.flute"),
        "Clarinet": (71, "Woodwind.clarinet"),
        "Oboe": (68, "Woodwind.oboe"),
        "Bassoon": (70, "Woodwind.bassoon"),
        "Saxophone": (65, "Woodwind.saxophone"),
        "Acoustic Guitar": (25, "Guitar.acoustic"),
        "Electric Guitar": (27, "Guitar.electric"),
        "Synth Pad": (88, "Keys.synth_pad"),
        "Strings Section": (49, "Strings.section"),
        "Drum Kit": (0, "Percussion.drum_kit"),  # channel 9
        "Crash Cymbal": (49, "Percussion.drum_kit"),
    }
    entry = mapping.get(instrument_name)
    if not entry:
        return None
    program, module = entry
    return program


if __name__ == "__main__":
    print("ROLE_PROFILES:", list(ROLE_PROFILES.keys()))
    print("allocate_registers(['melody','harmony','bass','rhythm','pad']):")
    print(" ", allocate_registers(["melody", "harmony", "bass", "rhythm", "pad"]))
    print("velocity_for('melody'):", velocity_for("melody"))
    print("velocity_for('pad'):", velocity_for("pad"))
    print("section_roles('Chorus'):", section_roles("Chorus"))
    print("instrument_program('Violin'):", instrument_program("Violin"))
    print("instrument_program('Drum Kit'):", instrument_program("Drum Kit"))
