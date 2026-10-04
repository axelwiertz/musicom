# -*- coding: utf-8 -*-
"""Chanson Française composition study — "Champs-Élysées"-style.

Composes a bright, optimistic 1960s French-pop / chanson study through the
musicom engine, embodying the signature DNA:

  - march-like 4/4 at ~126 BPM (buoyant, walking strut)
  - musette accordion pad (the cabaret bed)          GM 21
  - strummed acoustic guitar (8th-note chord bed)    GM 25
  - light brass trumpet lead (singable hook)         GM 56
  - "swinging strings" (air an octave up)            GM 49
  - upright oom-pah bass (root-fifth march)          GM 32
  - light march drums (kick 1&3, snare 2&4, hat 8ths) ch9

Form: Intro - Verse - Chorus - Verse - Chorus - Outro (40 bars).
Harmony: I - V - vi - IV in C major (verse), resolving chorus.

Run:
    /opt/data/micromamba/envs/musicom/bin/python compose.py
"""
import os
import subprocess
from pathlib import Path

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.provenance import write_provenance
from visualization.grid import write_grid_visualization
from utilities.env import fluidsynth_bin
from sound.render.fluidsynth import discover_soundfont

PROJECT = Path(__file__).resolve().parent
MIDI_DIR = PROJECT / "MIDI"
AUDIO_DIR = PROJECT / "Audio"
ANALYSIS_DIR = PROJECT / "Analysis"

BPM = 126
TPB = 480
BPB = 4
BAR = TPB * BPB  # 1920 ticks

# --- GM program numbers (standard) ---
ACCORDION = 21
ACOUSTIC_GUITAR = 25
TRUMPET = 56
STRING_ENSEMBLE = 49
UPRIGHT_BASS = 32

# --- harmony: C-major I V vi IV, root-position triads in C3-C4 ---
CHORD = {
    "I":  [60, 64, 67],   # C E G
    "V":  [55, 59, 62],   # G B D
    "vi": [57, 60, 64],   # A C E
    "IV": [53, 57, 60],   # F A C
}
BASS_ROOT = {"I": 36, "V": 43, "vi": 45, "IV": 41}   # C2 G2 A2 F2

# --- melody (scale degrees; tonic C5 = 72) ---
DEG = {1: 72, 2: 74, 3: 76, 4: 77, 5: 79, 6: 81, 7: 83, 8: 84}
VERSE_MELODY = [
    [3, 3, 4, 5], [5, 3, 1, 1], [6, 5, 6, 3], [4, 3, 4, 5],
    [3, 3, 4, 5], [5, 3, 1, 1], [6, 5, 6, 3], [4, 3, 2, 1],
]
CHORUS_MELODY = [
    [5, 6, 5, 3], [3, 4, 3, 1], [6, 5, 3, 1], [4, 3, 2, 1],
    [5, 6, 5, 3], [3, 4, 3, 1], [5, 4, 3, 2], [1, 1, 1, 1],
]
OUTRO_MELODY = [
    [5, 6, 5, 3], [3, 4, 3, 1], [5, 3, 1, 1], [1, 1, 1, 1],
]

# --- form: (section name, bars, per-bar chords) ---
FORM = [
    ("Intro",   4, ["I", "I", "IV", "V"]),
    ("Verse1",  8, ["I", "V", "vi", "IV", "I", "V", "vi", "IV"]),
    ("Chorus1", 8, ["I", "V", "vi", "IV", "I", "V", "I", "I"]),
    ("Verse2",  8, ["I", "V", "vi", "IV", "I", "V", "vi", "IV"]),
    ("Chorus2", 8, ["I", "V", "vi", "IV", "I", "V", "I", "I"]),
    ("Outro",   4, ["I", "IV", "I", "I"]),
]
MELODY_BY_SECTION = {
    "Intro": None, "Verse1": VERSE_MELODY, "Verse2": VERSE_MELODY,
    "Chorus1": CHORUS_MELODY, "Chorus2": CHORUS_MELODY, "Outro": OUTRO_MELODY,
}


def unit(events, section_len):
    """Wrap events into a MusicUnit with a terminal landmark at section_len
    (zero-drift gate: every voice's section unit must end at the full length)."""
    u = MusicUnit()
    for e in events:
        u.add_event(e)
    u.add_event(MusicEvent(0, 0, section_len, section_len))
    return u


def build_lead(section_len, chords, melody):
    events = []
    if melody:
        for bar, degrees in enumerate(melody):
            for i, deg in enumerate(degrees):
                start = bar * BAR + i * (BAR // 4)
                events.append(MusicEvent(DEG[deg], 95, start, start + 480))
    return unit(events, section_len)


def build_accordion(section_len, chords):
    events = []
    for bar, roman in enumerate(chords):
        tones = [p - 12 for p in CHORD[roman]]          # C3 register bed
        for p in tones:
            events.append(MusicEvent(p, 62, bar * BAR, (bar + 1) * BAR))
    return unit(events, section_len)


def build_guitar(section_len, chords):
    events = []
    for bar, roman in enumerate(chords):
        tones = CHORD[roman]
        for i in range(8):                               # 8th-note strum
            p = tones[i % 3]
            start = bar * BAR + i * (BAR // 8)
            events.append(MusicEvent(p, 74, start, start + 200))
    return unit(events, section_len)


def build_strings(section_len, chords, chorus=False):
    events = []
    vel = 58 if chorus else 44                          # swell into chorus
    for bar, roman in enumerate(chords):
        tones = [p + 12 for p in CHORD[roman]]          # C5 register air
        for p in tones:
            events.append(MusicEvent(p, vel, bar * BAR, (bar + 1) * BAR))
    return unit(events, section_len)


def build_bass(section_len, chords):
    events = []
    for bar, roman in enumerate(chords):
        root = BASS_ROOT[roman]
        fifth = root + 7
        for beat in range(4):                            # oom-pah root-fifth
            p = root if beat % 2 == 0 else fifth
            start = bar * BAR + beat * (BAR // 4)
            events.append(MusicEvent(p, 90, start, start + 400))
    return unit(events, section_len)


def build_drums(section_len, chords):
    events = []
    for bar in range(len(chords)):
        base = bar * BAR
        events.append(MusicEvent(36, 95, base, base + 120))             # kick 1
        events.append(MusicEvent(38, 90, base + 480, base + 600))       # snare 2
        events.append(MusicEvent(36, 88, base + 960, base + 1080))      # kick 3
        events.append(MusicEvent(38, 88, base + 1440, base + 1560))     # snare 4
        for h in range(8):                                               # hat 8ths
            events.append(MusicEvent(42, 52, base + h * 240, base + h * 240 + 100))
    return unit(events, section_len)


def main():
    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    composer.create_matrix(num_voices=6, num_sections=len(FORM))
    composer.add_voice("Lead", program=TRUMPET, channel=0)
    composer.add_voice("Accordion", program=ACCORDION, channel=1)
    composer.add_voice("Guitar", program=ACOUSTIC_GUITAR, channel=2)
    composer.add_voice("Strings", program=STRING_ENSEMBLE, channel=3)
    composer.add_voice("Bass", program=UPRIGHT_BASS, channel=4)
    composer.add_voice("Drums", program=0, channel=9)

    for name, bars, chords in FORM:
        composer.add_section(name, bars=bars)

    for name, bars, chords in FORM:
        sec_len = bars * BAR
        chorus = name.startswith("Chorus")
        composer.fill_voice_section("Lead", name,
                                    build_lead(sec_len, chords, MELODY_BY_SECTION[name]))
        composer.fill_voice_section("Accordion", name, build_accordion(sec_len, chords))
        composer.fill_voice_section("Guitar", name, build_guitar(sec_len, chords))
        composer.fill_voice_section("Strings", name, build_strings(sec_len, chords, chorus))
        composer.fill_voice_section("Bass", name, build_bass(sec_len, chords))
        composer.fill_voice_section("Drums", name, build_drums(sec_len, chords))

    ok, msg = composer.validate()
    assert ok, f"zero-drift gate failed: {msg}"

    MIDI_DIR.mkdir(parents=True, exist_ok=True)
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

    midi_path = MIDI_DIR / "chanson-champs-study.mid"
    composer.to_midi(str(midi_path))
    assert os.path.getsize(midi_path) > 40, "empty MIDI"

    # grid visualization + provenance
    write_grid_visualization(composer.matrix, str(ANALYSIS_DIR / "grid_visualization.txt"),
                             voice_names=[v["name"] for v in composer.voices], bpm=BPM)
    write_provenance(
        artifact_path=str(midi_path),
        classification="ai-assisted",
        generator="chanson_study.compose",
        sources=["STYLE_REGISTRY:chanson", "user:chanson-francaise-brief"],
        parameters={"bpm": BPM, "key": "C", "form": [n for n, _, _ in FORM]},
    )

    # render -> WAV -> OGG (FluidSynth, gain 1.2)
    sf = discover_soundfont()
    wav_path = AUDIO_DIR / "chanson-champs-study.wav"
    ogg_path = AUDIO_DIR / "chanson-champs-study.ogg"
    r = subprocess.run(
        [fluidsynth_bin(), "-ni", "-g", "1.2", "-F", str(wav_path), sf, str(midi_path)],
        capture_output=True, text=True)
    assert r.returncode == 0 and wav_path.stat().st_size > 1000, f"fluidsynth failed: {r.stderr[-400:]}"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav_path),
                    "-codec:a", "libopus", "-application", "voip", "-b:a", "48k",
                    str(ogg_path)], capture_output=True, text=True)

    print(f"MIDI: {midi_path} ({os.path.getsize(midi_path)} B)")
    print(f"WAV:  {wav_path} ({wav_path.stat().st_size} B)")
    print(f"OGG:  {ogg_path} ({ogg_path.stat().st_size} B)")
    return midi_path, ogg_path


if __name__ == "__main__":
    main()
