# -*- coding: utf-8 -*-
"""Studio Grand Extended — HARMONY REWORK (pre-flight gate fix).

The original compose.py had two bugs that broke the harmony rule:
  1. Per-section chord collapse: every build_*(...) call used ``chords[0]``
     (the FIRST chord of each 4-bar section) for ALL 4 bars, so the intended
     I-IV-V-vi progression (PROGRESSION) was never actually played — only C
     and F sounded.  Fix: pass ``chords[bar]`` per bar.
  2. Lead melody used FIXED semitone offsets (root+10 -> Bb, root+19 -> C#)
     -> out-of-scale notes; countermelody used scale tones (not chord tones).
     Fix: chord-tone arpeggios only (all notes = chord tones of their bar,
     all diatonic to C major).

Result: every pitched onset lands on the 16th grid, every pitched note is a
chord tone of its bar (hence in C major), all tracks span exactly 61440 ticks.
"""
import os
import sys

from structures import MusicUnit, MusicEvent, MidiInstrument
from workflows.unitmatrix_composer import UnitMatrixComposer
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED

TPB = 480
BPM = 110
BEATS_PER_BAR = 4
BAR = TPB * BEATS_PER_BAR          # 1920
SECTION = BAR * 4                  # 7680 (4 bars per section)

WHOLE = BAR
HALF = BAR // 2
QUARTER = BAR // 4
EIGHTH = BAR // 8
SIXTEENTH = BAR // 16

# Chord voicings (all diatonic to C major; notes are chord tones only)
CHORDS = {
    'C':  {'bass': 36, 'notes': [48, 55, 60, 64]},   # C3 G3 C4 E4  (C: C E G)
    'G':  {'bass': 43, 'notes': [43, 50, 55, 59]},   # G2 D3 G3 B3  (G: G B D)
    'F':  {'bass': 41, 'notes': [41, 48, 53, 57]},   # F2 C3 F3 A3  (F: F A C)
    'Am': {'bass': 45, 'notes': [45, 52, 57, 60]},   # A2 E3 A3 C4  (Am: A C E)
}

# Intended per-bar progression (4 bars per section, 8 sections = 32 bars)
PROGRESSION = [
    ['C', 'C', 'G', 'G'],      # Intro
    ['C', 'C', 'G', 'G'],      # V1a
    ['C', 'C', 'F', 'C'],      # V1b
    ['F', 'C', 'G', 'Am'],     # ChA
    ['F', 'C', 'G', 'C'],      # ChB
    ['C', 'Am', 'G', 'G'],     # V2a
    ['C', 'Am', 'F', 'C'],     # V2b
    ['F', 'C', 'G', 'C'],      # Outro
]
SECTION_NAMES = ['Intro', 'V1a', 'V1b', 'ChA', 'ChB', 'V2a', 'V2b', 'Outro']

# Chord-tone lead arpeggios (MIDI pitches, chord tones only, 8 per chord)
LEAD_ARP = {
    'C':  [72, 67, 64, 60, 64, 67, 72, 76],   # C6 G5 E5 C5 E5 G5 C6 E6
    'G':  [71, 67, 62, 59, 62, 67, 71, 74],   # B4 G4 D4 B3 D4 G4 B4 D5
    'F':  [72, 69, 65, 60, 65, 69, 72, 77],   # C6 A4 F4 C5 F4 A4 C6 F5
    'Am': [72, 69, 64, 60, 64, 69, 72, 76],   # C6 A4 E4 C5 E4 A4 C6 E5
}

# Chord-tone countermelody colours (7 per chord, isorhythmic colour cycle)
COLORS = {
    'C':  [60, 64, 67, 72, 67, 64, 60],   # C5 E5 G5 C6 G5 E5 C5
    'G':  [59, 62, 67, 71, 67, 62, 59],   # B3 D4 G4 B4 G4 D4 B3
    'F':  [60, 65, 69, 72, 69, 65, 60],   # C5 F4 A4 C6 A4 F4 C5
    'Am': [60, 64, 69, 72, 69, 64, 60],   # C5 E4 A4 C6 A4 E4 C5
}

# Isorhythmic talea (rhythm cycle length 5) x colour (pitch cycle length 7)
TALEA = [QUARTER, EIGHTH, HALF, EIGHTH, QUARTER]   # 480 240 960 240 480


def pad_to_section(events):
    for e in events:
        if e.end_tick > SECTION:
            e.end_tick = SECTION
    if not events or events[-1].end_tick < SECTION:
        events.append(MusicEvent(pitch=0, volume=0, start_tick=SECTION - 10,
                                 end_tick=SECTION))


def build_piano(chords, section_idx, section_name):
    events = []
    for bar in range(4):
        c = CHORDS[chords[bar]]
        bar_t = bar * BAR
        chord = c['notes']
        if section_name == 'Intro':
            events.append(MusicEvent(pitch=c['bass'], volume=60, start_tick=bar_t,
                                     end_tick=bar_t + HALF))
            for p in chord:
                events.append(MusicEvent(pitch=p, volume=55, start_tick=bar_t,
                                         end_tick=bar_t + HALF))
            for p in chord:
                events.append(MusicEvent(pitch=p, volume=45, start_tick=bar_t + HALF,
                                         end_tick=bar_t + BAR))
        elif section_name.startswith('V'):
            events.append(MusicEvent(pitch=c['bass'], volume=75, start_tick=bar_t,
                                     end_tick=bar_t + BAR - 100))
            for p in chord:
                events.append(MusicEvent(pitch=p, volume=70, start_tick=bar_t,
                                         end_tick=bar_t + BAR - 100))
        elif section_name.startswith('Ch'):
            events.append(MusicEvent(pitch=c['bass'], volume=90, start_tick=bar_t,
                                     end_tick=bar_t + QUARTER))
            for p in chord:
                events.append(MusicEvent(pitch=p, volume=85, start_tick=bar_t,
                                         end_tick=bar_t + QUARTER))
            events.append(MusicEvent(pitch=c['bass'], volume=70, start_tick=bar_t + QUARTER,
                                     end_tick=bar_t + BAR - 100))
            for p in chord:
                events.append(MusicEvent(pitch=p, volume=65, start_tick=bar_t + QUARTER,
                                         end_tick=bar_t + BAR - 100))
        elif section_name == 'Outro':
            dur = BAR + bar * 200
            events.append(MusicEvent(pitch=c['bass'], volume=65 - bar * 8,
                                     start_tick=bar_t, end_tick=bar_t + dur))
            for p in chord:
                events.append(MusicEvent(pitch=p, volume=60 - bar * 8,
                                         start_tick=bar_t, end_tick=bar_t + dur))
    pad_to_section(events)
    return MusicUnit(events=events)


def build_strings(chords, section_idx, section_name):
    events = []
    for bar in range(4):
        c = CHORDS[chords[bar]]
        bar_t = bar * BAR
        if section_name == 'Intro':
            if bar >= 2:
                vol = 40 + (bar - 2) * 10
                for p in c['notes']:
                    events.append(MusicEvent(pitch=p + 12, volume=vol, start_tick=bar_t,
                                             end_tick=bar_t + BAR))
        elif section_name in ['V1a', 'V2a']:
            vol = 60 if section_idx < 4 else 65
            for p in c['notes']:
                events.append(MusicEvent(pitch=p + 12, volume=vol, start_tick=bar_t,
                                         end_tick=bar_t + BAR))
        elif section_name in ['V1b', 'V2b', 'ChB']:
            for beat in range(4):
                t = bar_t + beat * QUARTER
                for p in c['notes']:
                    events.append(MusicEvent(pitch=p + 12, volume=65, start_tick=t,
                                             end_tick=t + QUARTER // 2))
        elif section_name == 'ChA':
            for beat in range(8):
                t = bar_t + beat * EIGHTH
                vol = 80 + (10 if beat % 2 == 0 else -10)
                for p in c['notes']:
                    events.append(MusicEvent(pitch=p + 12, volume=vol, start_tick=t,
                                             end_tick=t + EIGHTH))
        elif section_name == 'Outro':
            if bar < 3:
                for p in c['notes']:
                    events.append(MusicEvent(pitch=p + 12, volume=60, start_tick=bar_t,
                                             end_tick=bar_t + BAR))
    pad_to_section(events)
    return MusicUnit(events=events)


def build_bass(chords, section_idx, section_name):
    events = []
    for bar in range(4):
        c = CHORDS[chords[bar]]
        bar_t = bar * BAR
        if section_name == 'Intro':
            pass
        elif section_name.startswith('V'):
            events.append(MusicEvent(pitch=c['bass'], volume=85, start_tick=bar_t,
                                     end_tick=bar_t + HALF))
            events.append(MusicEvent(pitch=c['bass'], volume=75, start_tick=bar_t + HALF,
                                     end_tick=bar_t + BAR))
        elif section_name.startswith('Ch'):
            for beat in range(4):
                t = bar_t + beat * QUARTER
                vol = 90 if beat == 0 else 80
                events.append(MusicEvent(pitch=c['bass'], volume=vol, start_tick=t,
                                         end_tick=t + QUARTER - 50))
        elif section_name == 'Outro':
            if bar < 3:
                events.append(MusicEvent(pitch=c['bass'], volume=70, start_tick=bar_t,
                                         end_tick=bar_t + BAR))
    pad_to_section(events)
    return MusicUnit(events=events)


def build_drums(chords, section_idx, section_name):
    events = []
    for bar in range(4):
        bar_t = bar * BAR
        if section_name == 'Intro':
            pass
        elif section_name.startswith('V'):
            events.append(MusicEvent(pitch=36, volume=100, start_tick=bar_t,
                                     end_tick=bar_t + 120))
            events.append(MusicEvent(pitch=36, volume=100, start_tick=bar_t + HALF,
                                     end_tick=bar_t + HALF + 120))
            events.append(MusicEvent(pitch=38, volume=90, start_tick=bar_t + QUARTER,
                                     end_tick=bar_t + QUARTER + 120))
            events.append(MusicEvent(pitch=38, volume=90, start_tick=bar_t + HALF + QUARTER,
                                     end_tick=bar_t + HALF + QUARTER + 120))
            for i in range(8):
                t = bar_t + i * EIGHTH
                vol = 60 if i % 2 == 0 else 45
                events.append(MusicEvent(pitch=42, volume=vol, start_tick=t, end_tick=t + 60))
        elif section_name.startswith('Ch'):
            events.append(MusicEvent(pitch=36, volume=110, start_tick=bar_t,
                                     end_tick=bar_t + 120))
            events.append(MusicEvent(pitch=36, volume=110, start_tick=bar_t + HALF,
                                     end_tick=bar_t + HALF + 120))
            events.append(MusicEvent(pitch=36, volume=95, start_tick=bar_t + HALF + EIGHTH,
                                     end_tick=bar_t + HALF + EIGHTH + 120))
            events.append(MusicEvent(pitch=38, volume=100, start_tick=bar_t + QUARTER,
                                     end_tick=bar_t + QUARTER + 120))
            events.append(MusicEvent(pitch=38, volume=100, start_tick=bar_t + HALF + QUARTER,
                                     end_tick=bar_t + HALF + QUARTER + 120))
            for i in range(16):
                t = bar_t + i * SIXTEENTH
                vol = 65 if i % 4 == 0 else 50
                events.append(MusicEvent(pitch=42, volume=vol, start_tick=t, end_tick=t + 40))
            if bar == 0:
                events.append(MusicEvent(pitch=49, volume=85, start_tick=bar_t,
                                         end_tick=bar_t + 960))
        elif section_name == 'Outro':
            if bar < 3:
                events.append(MusicEvent(pitch=36, volume=100, start_tick=bar_t,
                                         end_tick=bar_t + 120))
                events.append(MusicEvent(pitch=36, volume=100, start_tick=bar_t + HALF,
                                         end_tick=bar_t + HALF + 120))
                events.append(MusicEvent(pitch=38, volume=90, start_tick=bar_t + QUARTER,
                                         end_tick=bar_t + QUARTER + 120))
                events.append(MusicEvent(pitch=38, volume=90, start_tick=bar_t + HALF + QUARTER,
                                         end_tick=bar_t + HALF + QUARTER + 120))
    pad_to_section(events)
    return MusicUnit(events=events)


def build_lead(chords, section_idx, section_name):
    events = []
    for bar in range(4):
        arp = LEAD_ARP[chords[bar]]
        bar_t = bar * BAR
        if section_name == 'Intro':
            pass
        elif section_name.startswith('V'):
            for q in range(4):
                note = arp[(bar * 4 + q) % 8]
                t = bar_t + q * QUARTER
                events.append(MusicEvent(pitch=note, volume=72, start_tick=t,
                                         end_tick=t + QUARTER - 80))
        elif section_name.startswith('Ch'):
            for e in range(8):
                note = arp[(bar * 8 + e) % 8]
                t = bar_t + e * EIGHTH
                vol = 85 if e % 2 == 0 else 75
                events.append(MusicEvent(pitch=note, volume=vol, start_tick=t,
                                         end_tick=t + EIGHTH - 40))
        elif section_name == 'Outro':
            if bar < 2:
                for h in range(2):
                    note = arp[(bar * 2 + h) % 8]
                    t = bar_t + h * HALF
                    events.append(MusicEvent(pitch=note, volume=68, start_tick=t,
                                             end_tick=t + HALF - 100))
    pad_to_section(events)
    return MusicUnit(events=events)


def build_countermelody(chords, section_idx, section_name):
    """Isorhythmic talea (len 5) x colour (len 7).  Pitch drawn from the
    CURRENT bar's chord colour -> every note is a chord tone of its bar."""
    events = []
    talea_pos = 0
    t = 0
    while t < SECTION:
        dur = TALEA[talea_pos % len(TALEA)]
        bar = min(t // BAR, 3)
        color = COLORS[chords[bar]]
        pitch = color[(talea_pos * 3 + section_idx) % len(color)]
        if section_name in ('Intro', 'Outro'):
            vol = 0
        elif section_name.startswith('Ch'):
            vol = 82
        else:
            vol = 60
        if vol > 0 and t + dur <= SECTION:
            events.append(MusicEvent(pitch=pitch, volume=vol, start_tick=t,
                                     end_tick=t + dur - 40))
        t += dur
        talea_pos += 1
    pad_to_section(events)
    return MusicUnit(events=events)


def main():
    out_dir = sys.argv[1] if len(sys.argv) > 1 else (
        "/opt/data/repos/musicom/projects/Styles/Classical/studio_grand_extended/v1")
    midi_path = os.path.join(out_dir, "studio_grand_extended.mid")

    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
    composer.create_matrix(num_voices=6, num_sections=8)

    composer.add_voice("Piano", program=MidiInstrument.PIANO, channel=0)
    composer.add_voice("Strings", program=MidiInstrument.STRING_ENSEMBLE, channel=1)
    composer.add_voice("Bass", program=MidiInstrument.BASS, channel=2)
    composer.add_voice("Drums", program=0, channel=9)
    composer.add_voice("Lead", program=MidiInstrument.FLUTE, channel=3)
    composer.add_voice("Countermelody", program=MidiInstrument.FLUTE, channel=4)

    for name in SECTION_NAMES:
        composer.add_section(name, bars=4)

    for sec_idx in range(8):
        name = SECTION_NAMES[sec_idx]
        chords = PROGRESSION[sec_idx]
        composer.fill_voice_section("Piano", name, build_piano(chords, sec_idx, name))
        composer.fill_voice_section("Strings", name, build_strings(chords, sec_idx, name))
        composer.fill_voice_section("Bass", name, build_bass(chords, sec_idx, name))
        composer.fill_voice_section("Drums", name, build_drums(chords, sec_idx, name))
        composer.fill_voice_section("Lead", name, build_lead(chords, sec_idx, name))
        composer.fill_voice_section("Countermelody", name,
                                    build_countermelody(chords, sec_idx, name))

    ok, msg = composer.validate()
    print(f"Validation: {'PASS' if ok else 'FAIL'} - {msg}")
    if not ok:
        sys.exit(1)

    composer.to_midi(midi_path)
    assert os.path.getsize(midi_path) > 40, "empty/corrupt output"

    grid_path = os.path.join(out_dir, "grid_visualization.txt")
    write_grid_visualization(composer.matrix, grid_path, ticks_per_character=480,
                             voice_names=["Piano", "Strings", "Bass", "Drums", "Lead"],
                             bpm=BPM)

    write_provenance(midi_path, AI_ASSISTED, "studio_grand_extended",
                     parameters={"bpm": BPM, "key": "C major", "bars": 32,
                                 "rework": "harmony-gate-fix: per-bar chords + chord-tone lead/countermelody",
                                 "structure": "Intro(4) + V1(8) + Chorus(8) + V2(8) + Outro(4)"})
    print(f"Reworked MIDI written: {midi_path} ({os.path.getsize(midi_path)} bytes)")


if __name__ == "__main__":
    main()
