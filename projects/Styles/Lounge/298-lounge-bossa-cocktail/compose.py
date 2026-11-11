# -*- coding: utf-8 -*-
"""298-lounge-bossa-cocktail — a lounge / bossa-cocktail composition.

F major, 92 BPM, 4/4. ii-V-I jazz harmony with 7th chords over a bossa groove:
Flute (lead) + Rhodes (harmony pad) + Double Bass (bossa root/fifth) + Nylon
Guitar (batida comp) + soft brushed Drums. Form: Intro(4) A1(8) A2(8) B(8)
A3(8) Outro(4) = 40 bars.

Uses the musicom engine (UnitMatrixComposer), cell-local ticks, zero-drift
landmarks, and export_dual (perfect + humanized).
"""

import os
import sys

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.humanize import export_dual
from workflows.provenance import write_provenance, AI_ASSISTED
from utilities.env import repo_root

# --- instrument registry (not pip-installed; lives under projects/Instruments)
_instr_dir = os.path.join(repo_root(), "projects", "Instruments")
if _instr_dir not in sys.path:
    sys.path.insert(0, _instr_dir)
from instrument_registry import by_name  # noqa: E402

BPM = 92
TPB = 480
BAR = 1920
EIGHTH = 240
SIXTEENTH = 120
SEED = 298

VOICES = [
    ("Flute", "flute", 73, 0),          # lead
    ("Rhodes", "rhodes", 4, 1),         # harmony pad (electric piano 1)
    ("Bass", "double_bass", 43, 2),     # upright
    ("Guitar", "acoustic_guitar", 24, 3),  # nylon bossa batida
    ("Drums", "drum_kit", 0, 9),        # brushed kit
]

FORM = [("Intro", 4), ("A1", 8), ("A2", 8), ("B", 8), ("A3", 8), ("Outro", 4)]

# chord tones (close-position 7th voicings) + bass root
CHORDS = {
    "Fmaj7":  {"root": 41, "tones": [53, 57, 60, 64]},   # F3 A3 C4 E4
    "Gm7":    {"root": 43, "tones": [55, 58, 62, 65]},   # G3 Bb3 D4 F4
    "C7":     {"root": 36, "tones": [48, 52, 55, 58]},   # C3 E3 G3 Bb3
    "Am7":    {"root": 45, "tones": [57, 60, 64, 67]},   # A3 C4 E4 G4
    "D7":     {"root": 38, "tones": [50, 54, 57, 60]},   # D3 F#3 A3 C4
    "Bbmaj7": {"root": 46, "tones": [58, 62, 65, 69]},   # Bb3 D4 F4 A4
}

_SECTION_PROG = {
    "Intro": ["Fmaj7", "Gm7", "C7", "Fmaj7"],
    "A":     ["Fmaj7", "Fmaj7", "Gm7", "C7", "Am7", "D7", "Gm7", "C7"],
    "B":     ["Bbmaj7", "Bbmaj7", "Am7", "D7", "Gm7", "C7", "Fmaj7", "Fmaj7"],
    "Outro": ["Fmaj7", "Gm7", "C7", "Fmaj7"],
}


def chords_for(section_names):
    """Flatten per-section chord names into one list (one per bar)."""
    out = []
    for sname in section_names:
        kind = "B" if sname == "B" else ("A" if sname.startswith("A") else
                 "Outro" if sname == "Outro" else "Intro")
        out.extend(_SECTION_PROG[kind])
    return out


# --- melody (bossa-syncopated, diatonic F major, chord-aware) ---------------
# each bar = list of (pitch, onset_in_bar, duration). All pitches in F major.

MELODY_A = [
    [(84, 0, 600), (81, 720, 500)],                       # Fmaj7: C A
    [(81, 0, 400), (79, 480, 300), (81, 960, 500)],       # Fmaj7: A G A
    [(82, 0, 500), (86, 720, 500), (79, 1440, 400)],      # Gm7: Bb D G
    [(88, 0, 500), (84, 720, 400), (82, 1320, 500)],      # C7: E C Bb
    [(81, 0, 500), (84, 720, 400), (88, 1200, 600)],      # Am7: A C E
    [(86, 0, 400), (84, 480, 300), (81, 960, 500)],       # D7: D C A
    [(79, 0, 500), (82, 720, 400), (86, 1200, 500)],      # Gm7: G Bb D
    [(84, 0, 500), (79, 720, 400), (76, 1320, 500)],      # C7: C G E
]

MELODY_B = [
    [(82, 0, 600), (86, 720, 500), (89, 1200, 500)],      # Bbmaj7: Bb D F(89)
    [(86, 0, 500), (82, 720, 400), (86, 1200, 500)],      # Bbmaj7: D Bb D
    [(81, 0, 500), (84, 720, 400), (88, 1200, 600)],      # Am7: A C E
    [(86, 0, 400), (84, 480, 300), (81, 960, 500)],       # D7: D C A
    [(79, 0, 500), (82, 720, 400), (86, 1200, 500)],      # Gm7: G Bb D
    [(84, 0, 500), (88, 720, 400), (82, 1320, 500)],      # C7: C E Bb
    [(77, 0, 600), (81, 720, 500), (84, 1200, 500)],      # Fmaj7: F A C
    [(84, 0, 600), (79, 720, 400), (77, 1320, 800)],      # Fmaj7: C G F
]

MELODY_INTRO = [
    [(84, 0, 900)],                                        # Fmaj7: C sustained
    [(79, 480, 700)],                                      # Gm7: G
    [(82, 720, 700)],                                      # C7: Bb (the 7th)
    [(77, 0, 1200)],                                       # Fmaj7: F resolve
]

MELODY_OUTRO = [
    [(84, 0, 800)],                                        # Fmaj7: C
    [(79, 480, 600)],                                      # Gm7: G
    [(88, 720, 600)],                                      # C7: E
    [(77, 0, 1500)],                                       # Fmaj7: F (final)
]


def lead_events(chords, melody, section_bars):
    evs = []
    for b, ch in enumerate(chords):
        base = b * BAR
        for (pitch, on, dur) in melody[b % len(melody)]:
            end = min(base + on + dur, base + BAR)
            evs.append(MusicEvent(pitch, 88, base + on, end))
    return evs


def bass_events(chords):
    evs = []
    for b, ch in enumerate(chords):
        base = b * BAR
        root = CHORDS[ch]["root"]
        fifth = root + 7
        evs.append(MusicEvent(root, 92, base, base + 420))
        evs.append(MusicEvent(fifth, 86, base + 720, base + 720 + 250))
        evs.append(MusicEvent(root, 92, base + 960, base + 960 + 420))
        evs.append(MusicEvent(fifth, 86, base + 1680, base + 1680 + 240))
    return evs


def rhodes_events(chords):
    evs = []
    for b, ch in enumerate(chords):
        base = b * BAR
        for t in CHORDS[ch]["tones"]:
            evs.append(MusicEvent(t, 62, base, base + BAR))
    return evs


def guitar_events(chords):
    """Bossa batida: syncopated comp, quick 3-note strums of chord tones."""
    BOSSAPOS = [0, 720, 1200, 1680]  # 4 bossa syncopation hits per bar
    evs = []
    for b, ch in enumerate(chords):
        base = b * BAR
        tones = CHORDS[ch]["tones"]
        for p in BOSSAPOS:
            for i in range(3):  # quick upward strum
                t = tones[i % len(tones)] + 12
                evs.append(MusicEvent(t, 72, base + p + i * 20, base + p + i * 20 + 90))
    return evs


def drum_events(chords):
    """Soft bossa kit: kick 1&3, cross-stick 2&4, airy off-beat ride."""
    evs = []
    for b in range(len(chords)):
        base = b * BAR
        evs.append(MusicEvent(36, 78, base, base + 90))
        evs.append(MusicEvent(36, 72, base + 960, base + 960 + 90))
        evs.append(MusicEvent(37, 75, base + 480, base + 480 + 80))
        evs.append(MusicEvent(37, 75, base + 1440, base + 1440 + 80))
        for e in range(8):
            if e % 2 == 1:
                evs.append(MusicEvent(51, 55, base + e * 240, base + e * 240 + 60))
    return evs


def _unit(events, section_len):
    unit = MusicUnit()
    for e in events:
        unit.add_event(e)
    unit.add_event(MusicEvent(0, 0, section_len, section_len))
    return unit


def main():
    section_names = [s for s, _ in FORM]
    bars_per = [b for _, b in FORM]
    section_chords = []  # per-section chord lists
    cursor = 0
    for sname, nbars in FORM:
        kind = "B" if sname == "B" else ("A" if sname.startswith("A") else
                 "Outro" if sname == "Outro" else "Intro")
        section_chords.append(_SECTION_PROG[kind])
        cursor += nbars

    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=4)
    composer.create_matrix(num_voices=len(VOICES), num_sections=len(FORM))
    for vname, _inst, prog, ch in VOICES:
        composer.add_voice(vname, program=prog, channel=ch)
    for sname, nbars in FORM:
        composer.add_section(sname, bars=nbars)

    melody_map = {"Intro": MELODY_INTRO, "A1": MELODY_A, "A2": MELODY_A,
                  "B": MELODY_B, "A3": MELODY_A, "Outro": MELODY_OUTRO}

    for si, (sname, nbars) in enumerate(FORM):
        section_len = nbars * BAR
        chords = section_chords[si]
        builders = {
            "Flute": lead_events(chords, melody_map[sname], nbars),
            "Rhodes": rhodes_events(chords),
            "Bass": bass_events(chords),
            "Guitar": guitar_events(chords),
            "Drums": drum_events(chords),
        }
        for vname, _inst, _p, _c in VOICES:
            composer.fill_voice_section(vname, sname,
                                        _unit(builders[vname], section_len))

    ok, msg = composer.validate()
    if not ok:
        raise RuntimeError(f"validate() failed: {msg}")

    out_dir = os.path.join(repo_root(), "projects", "Styles", "Lounge",
                           "298-lounge-bossa-cocktail")
    midi_dir = os.path.join(out_dir, "MIDI")
    audio_dir = os.path.join(out_dir, "Audio")
    os.makedirs(midi_dir, exist_ok=True)
    os.makedirs(audio_dir, exist_ok=True)

    # humanization DNA per voice
    hz = {}
    for vname, inst, _p, _c in VOICES:
        try:
            hz[vname] = by_name(inst).humanize_dna
        except Exception:
            hz[vname] = None

    base = os.path.join(midi_dir, "298-lounge-bossa-cocktail")
    summary = export_dual(composer, base + "-perfect.mid", base + "-humanized.mid",
                          style="lounge", seed=SEED, bpm=BPM, instruments=hz)

    for mid in (base + "-perfect.mid", base + "-humanized.mid"):
        write_provenance(
            artifact_path=mid,
            classification=AI_ASSISTED,
            generator="298-lounge-bossa-cocktail/compose.py",
            sources=["style:lounge", "key:F major", "bpm:92",
                     "harmony:ii-V-I+7ths", "groove:bossa"],
            parameters={"bpm": BPM, "form": FORM, "seed": SEED},
        )

    print("validate OK:", msg)
    print("perfect   :", base + "-perfect.mid")
    print("humanized :", base + "-humanized.mid", summary)


if __name__ == "__main__":
    main()