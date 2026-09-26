# -*- coding: utf-8 -*-
"""205-amapiano-study — Amapiano (South African house substyle) composition.

Research-derived style DNA (see REPORT.md for sources):
  - Amapiano ("the pianos", isiZulu) emerged in South African townships
    (Pretoria/Gauteng) during the 2010s, global ~2019-2020. Draws from
    kwaito, deep house, jazz, soul, lounge.
  - Signature LOG DRUM: a tuned, pitched bass-percussion hybrid (FM synth,
    historically FL Studio DX10). Carries BOTH rhythm and a melodic bassline.
  - Rhodes/electric-piano soulful extended chords (maj7/min7/dom7/9).
  - Rolling shaker (16ths with velocity swing), soft 4-on-floor kick,
    clap on 2 & 4, restrained syncopated percussion.
  - Tempo 108-115 BPM (112 chosen). Jazzy soulful harmony, delayed reveals.

Two-phase architecture (musicom standard):
  Phase 1 (raw): single LogDrum voice, off-grid micro-jitter + chromatic
    random-walk pitch. Unquantized generative draft -> -phase1.mid.
  Phase 2 (rules): 16th-grid snap -> per-bar chord-tone quantize -> full
    5-voice amapiano texture (Rhodes, LogDrum, Sub, Kalimba lead, ch9 kit)
    -> .mid.

Key: A minor (natural + harmonic leading-tone G# on the V). Scale = union of
all chord tones = A harmonic minor (A B C D E F G G#).
Progression (i7 - VI7 - iv7 - V7, 1 bar each, 4-bar cycle):
  Am7 (A C E G) | Fmaj7 (F A C E) | Dm7 (D F A C) | E7 (E G# B D)
Form (36 bars): Intro(4) GrooveA(8) GrooveB(8) Breakdown(4) Climax(8) Outro(4)
  BPM 112, 4/4, 480 TPB (BAR=1920, 16th=120, 8th=240).

Engine only: structures + workflows.unitmatrix_composer + visualization +
workflows.provenance. mido used READ-ONLY in the verify script.
"""

import os
import json

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.provenance import write_provenance, AI_ASSISTED
from visualization.grid import write_grid_visualization

SEED = 20260926
rng = np.random.default_rng(SEED)

# ---------------------------------------------------------------- project dirs
PROJ = "/opt/data/repos/musicom/projects/Styles/African/205-amapiano-study"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

# ------------------------------------------------------------------- timing
BPM = 112
TPB = 480
BEATS = 4
BAR = TPB * BEATS          # 1920
QUARTER = TPB              # 480
EIGHTH = TPB // 2          # 240
SIXTEENTH = TPB // 4       # 120

# ------------------------------------------------------------------ harmony
# i7 - VI7 - iv7 - V7  (A harmonic minor: natural + G# leading tone)
CHORDS = ["Am7", "Fmaj7", "Dm7", "E7"]

# Rhodes voicings (close position, octave 3-4) — soulful 7th chords
CHORD_NOTES = {
    "Am7":   [57, 60, 64, 67],   # A3 C4 E4 G4
    "Fmaj7": [53, 57, 60, 64],   # F3 A3 C4 E4
    "Dm7":   [50, 53, 57, 60],   # D3 F3 A3 C4
    "E7":    [52, 56, 59, 62],   # E3 G#3 B3 D4
}

# Log drum roots (octave 2) + sub roots (octave 1) — clean separation
LOG_ROOT = {"Am7": 45, "Fmaj7": 41, "Dm7": 38, "E7": 40}     # A2 F2 D2 E2
SUB_ROOT = {"Am7": 33, "Fmaj7": 29, "Dm7": 26, "E7": 28}     # A1 F1 D1 E1

# Lead pool per chord: root, 3rd, 5th, 7th (pure chord tones; the 9th color
# already lives in the Rhodes 7th-chord voicings)
LEAD_TONES = {
    "Am7":   [69, 72, 76, 79],  # A4 C5 E5 G5
    "Fmaj7": [65, 69, 72, 76],  # F4 A4 C5 E5
    "Dm7":   [62, 65, 69, 72],  # D4 F4 A4 C5
    "E7":    [64, 68, 71, 74],  # E4 G#4 B4 D5
}

# Guitar solo pool: root, 3rd, 5th, 7th, 9th (color on top). E7 uses the b9
# (F natural) so every tone stays inside A harmonic minor. Ascending register.
GUITAR_TONES = {
    "Am7":   [69, 72, 76, 79, 83],  # A4 C5 E5 G5 B5
    "Fmaj7": [65, 69, 72, 76, 79],  # F4 A4 C5 E5 G5
    "Dm7":   [62, 65, 69, 72, 76],  # D4 F4 A4 C5 E5
    "E7":    [64, 68, 71, 74, 77],  # E4 G#4 B4 D5 F5(b9)
}

# ------------------------------------------------------------------ form
SECTIONS = [
    ("Intro",     4),
    ("GrooveA",   8),
    ("GrooveB",   8),
    ("Breakdown", 4),
    ("Climax",    8),
    ("Outro",     4),
]
TOTAL_BARS = sum(b for _, b in SECTIONS)

# Section -> active roles
SECTION_ROLES = {
    "Intro":     {"rhodes": "stab",  "log": False, "sub": False, "lead": False, "guitar": True,  "drums": "basic"},
    "GrooveA":   {"rhodes": "full",  "log": True,  "sub": True,  "lead": False, "guitar": False, "drums": "full"},
    "GrooveB":   {"rhodes": "full",  "log": True,  "sub": True,  "lead": True,  "guitar": False, "drums": "full"},
    "Breakdown": {"rhodes": "full",  "log": False, "sub": False, "lead": False, "guitar": False, "drums": "shaker"},
    "Climax":    {"rhodes": "full",  "log": "dense", "sub": True, "lead": False, "guitar": True,  "drums": "dense"},
    "Outro":     {"rhodes": "full",  "log": True,  "sub": True,  "lead": False, "guitar": False, "drums": "basic"},
}

# Global bar index -> chord (continuous i-VI-iv-V cycle across the whole piece)
def section_start_bars():
    starts, gb = {}, 0
    for name, bars in SECTIONS:
        starts[name] = gb
        gb += bars
    return starts

SECTION_START = section_start_bars()

def chord_for(name, bar_in_section):
    global_bar = SECTION_START[name] + bar_in_section
    return CHORDS[global_bar % 4]


# ----------------------------------------------------------------- helpers
def landmark(section_ticks):
    return MusicEvent(pitch=0, volume=0,
                      start_tick=section_ticks - 10, end_tick=section_ticks)


def section_unit(events, section_ticks):
    """Wrap events in a MusicUnit whose length == section_ticks (zero-drift)."""
    if not events or events[-1].end_tick < section_ticks:
        events.append(landmark(section_ticks))
    return MusicUnit(events=events)


def snap16(t):
    return int(round(t / SIXTEENTH) * SIXTEENTH)


# --------------------------------------------------------------- log drum
LOG_PATTERN = {   # 16th steps (0..15) per bar, by cycle position
    0: [0, 3, 6, 10, 12, 14],            # i   (Am7)
    1: [3, 6, 8, 10, 12, 14],            # VI  (Fmaj7)
    2: [0, 3, 6, 8, 11, 14],             # iv  (Dm7)
    3: [3, 6, 8, 10, 12, 14, 15],        # V   (E7, busier -> tension)
}
LOG_DENSE = {     # climax 16th runs
    0: [3, 6, 8, 10, 11, 12, 14],
    1: [3, 6, 8, 10, 11, 12, 13, 14],
    2: [0, 3, 6, 8, 10, 11, 12, 14],
    3: [3, 6, 8, 10, 11, 12, 13, 14, 15],
}


def build_logdrum(chord, global_bar, dense):
    """Syncopated, tuned log-drum bassline (root/fifth/octave of the chord)."""
    root = LOG_ROOT[chord]
    tones = [root, root + 7, root + 12, root + 7]   # root, 5th, octave, 5th
    pat = LOG_DENSE[global_bar % 4] if dense else LOG_PATTERN[global_bar % 4]
    events = []
    for hi, step in enumerate(pat):
        pitch = tones[hi % len(tones)]
        vel = 96 if step % 4 == 0 else 86
        t0 = step * SIXTEENTH
        events.append(MusicEvent(pitch=pitch, volume=vel,
                                 start_tick=t0, end_tick=t0 + SIXTEENTH))
    return events


# ------------------------------------------------------------------ rhodes
def build_rhodes(chord, stab):
    """Sustained soulful Rhodes bed + optional syncopated offbeat stab."""
    notes = CHORD_NOTES[chord]
    events = [MusicEvent(pitch=p, volume=56, start_tick=0, end_tick=BAR)
              for p in notes]
    if stab:
        t0 = 14 * SIXTEENTH                       # "and" of 4
        events += [MusicEvent(pitch=p, volume=74,
                              start_tick=t0, end_tick=t0 + EIGHTH)
                   for p in notes]
    return events


# -------------------------------------------------------------------- sub
def build_sub(chord):
    """Deep sustained sub: root (2 beats) + fifth (2 beats), octave 1."""
    root = SUB_ROOT[chord]
    fifth = root + 7
    return [
        MusicEvent(pitch=root, volume=78, start_tick=0, end_tick=QUARTER * 2),
        MusicEvent(pitch=fifth, volume=70,
                   start_tick=QUARTER * 2, end_tick=BAR),
    ]


# -------------------------------------------------------------------- lead
LEAD_MOTIF = [0, 1, 2, 1, 3, 2]          # chord-tone pool indices (call)
LEAD_RESP  = [2, 1, 3, 2, 0, 3, 1]       # response, resolves


def build_lead(chord, bar_in_cycle):
    """Sparse kalimba call-and-response, chord tones only."""
    tones = LEAD_TONES[chord]
    events = []
    if bar_in_cycle % 2 == 0:             # call bar
        seq = LEAD_MOTIF
    else:                                 # response bar
        seq = LEAD_RESP
    for i, idx in enumerate(seq):
        t0 = i * EIGHTH
        vel = 88 if i % 2 == 0 else 72
        events.append(MusicEvent(pitch=tones[idx % len(tones)], volume=vel,
                                 start_tick=t0, end_tick=t0 + EIGHTH))
    return events


# ------------------------------------------------------------ guitar solos
# (step_in_16ths, tone_idx, dur_in_16ths). tone_idx into GUITAR_TONES
# (0=root 1=3rd 2=5th 3=7th 4=9th/b9).
#
# Intro = 4-bar hook: rise->9th->fall (bar0), answer descends (bar1), offbeat
# flourish (bar2), leading-tone pickup into GrooveA (bar3).
INTRO_SEQ = {
    0: [(0, 0, 3), (3, 1, 2), (6, 2, 3), (10, 4, 2), (12, 3, 2)],   # rise → 9th → fall
    1: [(0, 4, 3), (4, 3, 2), (6, 2, 3), (10, 1, 2), (12, 0, 4)],   # answer descends
    2: [(0, 3, 2), (2, 2, 2), (4, 4, 2), (6, 3, 2), (8, 2, 2),
        (11, 1, 3)],                                                  # offbeat flourish
    3: [(0, 2, 2), (4, 3, 2), (8, 1, 4), (12, 1, 4)],               # leading-tone pickup
}

# Climax = 8-bar arc: statement (0-1) -> syncopated response (2-3) ->
# 16th arpeggio build (4) -> peak on 9th (5) -> descend (6) -> resolve (7).
CLIMAX_SEQ = {
    0: [(0, 0, 2), (2, 1, 2), (4, 2, 2), (6, 3, 2), (8, 4, 2),
        (10, 3, 2), (12, 2, 2), (14, 1, 2)],                         # statement (arch)
    1: [(0, 2, 2), (2, 3, 2), (4, 4, 2), (6, 3, 2), (8, 2, 2),
        (10, 1, 2), (12, 0, 4)],                                     # answer descends
    2: [(0, 3, 2), (2, 4, 2), (4, 3, 2), (6, 2, 2), (9, 4, 2),
        (11, 3, 2), (13, 1, 2)],                                     # syncopated response
    3: [(0, 4, 2), (2, 3, 2), (4, 2, 2), (6, 1, 2), (8, 3, 2),
        (10, 2, 2), (12, 1, 4)],                                     # → leading tone
    4: [(0, 0, 1), (1, 1, 1), (2, 2, 1), (3, 3, 1), (4, 4, 1),
        (5, 3, 1), (6, 2, 1), (7, 3, 1), (8, 4, 1), (9, 3, 1),
        (10, 2, 1), (11, 3, 1), (12, 4, 1), (13, 3, 1), (14, 2, 1),
        (15, 1, 1)],                                                 # 16th build
    5: [(0, 4, 2), (2, 3, 2), (4, 2, 2), (6, 4, 3), (9, 3, 2),
        (11, 2, 2), (13, 1, 2)],                                     # peak on 9th
    6: [(0, 3, 2), (2, 2, 2), (4, 1, 2), (6, 2, 2), (8, 1, 2),
        (10, 0, 4)],                                                 # descend
    7: [(0, 3, 2), (4, 2, 2), (8, 1, 2), (12, 0, 4)],               # resolve to root
}


def build_guitar(chord, cyc, bar_in_section, solo_type):
    """Melodic guitar solo (chord tones + 9th color), clean electric."""
    tones = GUITAR_TONES[chord]
    seq = INTRO_SEQ[cyc] if solo_type == "intro" else CLIMAX_SEQ[bar_in_section % 8]
    events = []
    for step, idx, dur16 in seq:
        pitch = tones[idx % len(tones)]
        vel = 96 if step % 4 == 0 else 74
        t0 = step * SIXTEENTH
        events.append(MusicEvent(pitch=pitch, volume=vel,
                                 start_tick=t0, end_tick=t0 + dur16 * SIXTEENTH))
    return events


# ------------------------------------------------------------------- drums
SHAKER_VEL = [92, 52, 76, 52, 92, 52, 76, 52,
              92, 52, 76, 52, 92, 58, 76, 52]   # rolling 16th swing bounce


def build_drums(mode):
    """Amapiano kit: soft 4-on-floor kick, clap 2&4, rolling maracas shaker."""
    events = []
    if mode in ("full", "basic", "dense"):
        for b in (0, 4, 8, 12):           # soft controlled 4-on-floor kick
            events.append(MusicEvent(pitch=36, volume=88,
                                     start_tick=b * SIXTEENTH,
                                     end_tick=b * SIXTEENTH + EIGHTH))
        for b in (4, 12):                 # hand clap on 2 & 4
            events.append(MusicEvent(pitch=39, volume=82,
                                     start_tick=b * SIXTEENTH,
                                     end_tick=b * SIXTEENTH + EIGHTH))
    # rolling shaker (all modes) — the amapiano bounce
    for s in range(16):
        events.append(MusicEvent(pitch=70, volume=SHAKER_VEL[s],
                                 start_tick=s * SIXTEENTH,
                                 end_tick=s * SIXTEENTH + 60))
    if mode == "dense":                   # conga accents in climax
        for s in (3, 11):
            events.append(MusicEvent(pitch=63, volume=80,
                                     start_tick=s * SIXTEENTH,
                                     end_tick=s * SIXTEENTH + 80))
    return events


# ======================================================================
# PHASE 1 — raw generative draft (single LogDrum voice, off-grid, chromatic)
# ======================================================================
def generate_phase1():
    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB,
                                  beats_per_bar=BEATS)
    composer.create_matrix(num_voices=1, num_sections=len(SECTIONS))
    composer.add_voice("Raw_LogDrum", program=38, channel=0)

    raw_pitch = 45
    for s_name, s_bars in SECTIONS:
        composer.add_section(s_name, bars=s_bars)
        section_ticks = s_bars * BAR
        events = []
        for bar in range(s_bars):
            base = bar * BAR
            for i, hit in enumerate(np.array([0, 3, 6, 10, 12, 14])):
                jitter = int(rng.integers(-18, 18))
                t0 = base + hit * SIXTEENTH + jitter
                t0 = max(0, min(t0, base + BAR - 40))
                raw_pitch += int(rng.integers(-3, 4))
                raw_pitch = int(np.clip(raw_pitch, 36, 60))
                dur = int(rng.integers(90, 160))
                events.append(MusicEvent(pitch=raw_pitch, volume=88,
                                         start_tick=t0,
                                         end_tick=min(t0 + dur, base + BAR)))
        composer.fill_voice_section(
            "Raw_LogDrum", s_name, section_unit(events, section_ticks))

    ok, msg = composer.validate()
    assert ok, "Phase 1 validate failed: " + msg
    p1 = os.path.join(MIDI_DIR, "205-amapiano-study-phase1.mid")
    composer.to_midi(p1)
    assert os.path.getsize(p1) > 40, "phase1 midi empty"
    write_provenance(
        p1, classification=AI_ASSISTED,
        generator="musicom.workflows.unitmatrix_composer",
        parameters={"project": "205-amapiano-study", "phase": 1,
                    "style": "Amapiano (South African house)", "key": "A minor",
                    "bpm": BPM, "seed": SEED,
                    "method": "raw off-grid log-drum chromatic walk",
                    "source": "amapiano research brief"})
    print("Phase 1 MIDI:", p1, os.path.getsize(p1), "bytes")
    return p1


# ======================================================================
# PHASE 2 — rules composition: full 5-voice amapiano arrangement
# ======================================================================
def generate_phase2():
    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB,
                                  beats_per_bar=BEATS)
    composer.create_matrix(num_voices=6, num_sections=len(SECTIONS))
    composer.add_voice("Rhodes",  program=4,  channel=0)   # Electric Piano 1
    composer.add_voice("LogDrum", program=38, channel=1)   # Synth Bass 1 (FM)
    composer.add_voice("Sub",     program=39, channel=2)   # Synth Bass 2
    composer.add_voice("Lead",    program=108, channel=3)  # Kalimba
    composer.add_voice("Guitar",  program=27, channel=4)   # Electric Guitar (clean)
    composer.add_voice("Drums",   program=0,  channel=9)   # GM percussion

    for s_name, s_bars in SECTIONS:
        composer.add_section(s_name, bars=s_bars)
        section_ticks = s_bars * BAR
        role = SECTION_ROLES[s_name]

        rhodes_ev, log_ev, sub_ev, lead_ev, guitar_ev, drums_ev = (
            [], [], [], [], [], [])
        for bar in range(s_bars):
            base = bar * BAR
            chord = chord_for(s_name, bar)
            global_bar = SECTION_START[s_name] + bar
            cyc = global_bar % 4

            # Rhodes: full sustained bed (breakdown keeps it), intro = stab only
            rh = build_rhodes(chord, stab=(role["rhodes"] == "stab"))
            rhodes_ev += [MusicEvent(pitch=e.pitch, volume=e.volume,
                                     start_tick=base + e.start_tick,
                                     end_tick=base + e.end_tick) for e in rh]

            # Log drum (with Outro progressive dropout: silent bars 2-3)
            if role["log"] and not (s_name == "Outro" and bar >= 2):
                lg = build_logdrum(chord, global_bar,
                                   dense=(role["log"] == "dense"))
                log_ev += [MusicEvent(pitch=e.pitch, volume=e.volume,
                                      start_tick=base + e.start_tick,
                                      end_tick=base + e.end_tick) for e in lg]

            # Sub bass (with Outro dropout: silent bars 2-3)
            if role["sub"] and not (s_name == "Outro" and bar >= 2):
                sb = build_sub(chord)
                sub_ev += [MusicEvent(pitch=e.pitch, volume=e.volume,
                                      start_tick=base + e.start_tick,
                                      end_tick=base + e.end_tick) for e in sb]

            # Lead (kalimba call/response, GrooveB only)
            if role["lead"]:
                ld = build_lead(chord, cyc)
                lead_ev += [MusicEvent(pitch=e.pitch, volume=e.volume,
                                       start_tick=base + e.start_tick,
                                       end_tick=base + e.end_tick) for e in ld]

            # Guitar solos (Intro + Climax)
            if role["guitar"]:
                solo_type = "intro" if s_name == "Intro" else "climax"
                gt = build_guitar(chord, cyc, bar, solo_type)
                guitar_ev += [MusicEvent(pitch=e.pitch, volume=e.volume,
                                         start_tick=base + e.start_tick,
                                         end_tick=base + e.end_tick) for e in gt]

            # Drums (Outro progressive dropout: bar 3 -> shaker only)
            dmode = role["drums"]
            if s_name == "Outro" and bar == 3:
                dmode = "shaker"
            dr = build_drums(dmode)
            drums_ev += [MusicEvent(pitch=e.pitch, volume=e.volume,
                                    start_tick=base + e.start_tick,
                                    end_tick=base + e.end_tick) for e in dr]

        composer.fill_voice_section("Rhodes", s_name,
                                    section_unit(rhodes_ev, section_ticks))
        composer.fill_voice_section("LogDrum", s_name,
                                    section_unit(log_ev, section_ticks))
        composer.fill_voice_section("Sub", s_name,
                                    section_unit(sub_ev, section_ticks))
        composer.fill_voice_section("Lead", s_name,
                                    section_unit(lead_ev, section_ticks))
        composer.fill_voice_section("Guitar", s_name,
                                    section_unit(guitar_ev, section_ticks))
        composer.fill_voice_section("Drums", s_name,
                                    section_unit(drums_ev, section_ticks))

    ok, msg = composer.validate()
    assert ok, "Phase 2 validate failed: " + msg

    p2 = os.path.join(MIDI_DIR, "205-amapiano-study.mid")
    composer.to_midi(p2)
    assert os.path.getsize(p2) > 40, "phase2 midi empty"

    write_grid_visualization(
        composer.matrix,
        os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
        ticks_per_character=240,
        voice_names=["Rhodes", "LogDrum", "Sub", "Lead", "Guitar", "Drums"],
        bpm=BPM)

    write_provenance(
        p2, classification=AI_ASSISTED,
        generator="musicom.workflows.unitmatrix_composer",
        parameters={
            "project": "205-amapiano-study", "phase": 2,
            "style": "Amapiano (South African house)", "key": "A minor",
            "bpm": BPM, "seed": SEED,
            "progression": "i7 - VI7 - iv7 - V7 (Am7 Fmaj7 Dm7 E7)",
            "log_drum": "FM synth bass (GM 38), tuned root/5th/octave, syncopated",
            "rhodes": "Electric Piano 1 (GM 4) soulful 7th chords",
            "form": "Intro(4) GrooveA(8) GrooveB(8) Breakdown(4) Climax(8) Outro(4)",
            "source": "amapiano research brief"})

    print("Phase 2 MIDI:", p2, os.path.getsize(p2), "bytes")
    return p2


if __name__ == "__main__":
    print("=== Phase 1 raw draft ===")
    generate_phase1()
    print("=== Phase 2 rules composition ===")
    generate_phase2()
    print("Done.")
