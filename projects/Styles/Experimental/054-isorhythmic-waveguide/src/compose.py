# -*- coding: utf-8 -*-
"""054-isorhythmic-waveguide
Method 032: Isorhythmic Talea-Color Mapping (ITCM)
SP-023: Digital Waveguide Woodwind (Clarinet) Synthesis concept

Medieval isorhythm: coprime talea (rhythm, length 7) and color (pitch, length 5)
cycle independently, creating shifting alignment patterns across the timeline.
Three voices: Lead clarinet, Tenor clarinet (talea offset +2), Bass bassoon.
Key: D Dorian. Tempo: 80 BPM. Form: ABA'.
"""
import os

from structures import MusicUnit, MusicEvent, MidiInstrument, MidiPercussion
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_note_unit, create_chord_unit, create_empty_unit,
)
from ai.utils.visualizer import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED

# ---------------------------------------------------------------- CONFIG -----
PROJECT_NAME = "054-isorhythmic-waveguide"
OUTPUT_DIR = f"/opt/data/projects/Styles/Experimental/{PROJECT_NAME}"
BPM = 80
TICKS_PER_BEAT = 480
BEATS_PER_BAR = 4
BAR = TICKS_PER_BEAT * BEATS_PER_BAR  # 1920
STEP = BAR // 16  # 120 ticks per 16th-note grid step

# --- Isorhythmic Parameters ---
# Talea: 7-step rhythm pattern (4 onsets, Euclidean-like distribution)
TALEA_LEAD = [1, 0, 1, 1, 0, 1, 0]
TALEA_TENOR = [0, 1, 0, 1, 1, 0, 1]  # complement/offset by 2 steps
TALEA_BASS = [1, 0, 0, 1, 0, 0, 1]   # 3 onsets in 7 (sparser)

# Color: D Dorian pitch sequences (length 5, coprime with 7)
COLOR_LEAD_A = [62, 65, 69, 67, 64]   # D4 F4 A4 G4 E4
COLOR_LEAD_B = [64, 67, 69, 65, 62]   # retrograde: E4 G4 A4 F4 D4
COLOR_TENOR_A = [55, 57, 60, 58, 53]  # G3 A3 C4 B3 F3
COLOR_TENOR_B = [53, 58, 60, 57, 55]  # retrograde
COLOR_BASS_A = [38, 41, 43, 40, 36]   # D2 F2 G2 E2 D2
COLOR_BASS_B = [36, 40, 43, 41, 38]   # retrograde

NOTE_DUR_LEAD = STEP * 2   # eighth note
NOTE_DUR_TENOR = STEP * 3  # dotted eighth
NOTE_DUR_BASS = STEP * 6   # quarter+half (sustained)


def build_isorhythmic_unit(talea, color, section_ticks, note_dur, base_vel=90):
    """Walk timeline: talea gates onsets, color provides pitches."""
    events = []
    tick = 0
    talea_idx = 0
    color_idx = 0

    while tick < section_ticks:
        if talea[talea_idx % len(talea)] == 1:
            pitch = color[color_idx % len(color)]
            end = min(tick + note_dur, section_ticks)
            events.append(MusicEvent(
                pitch=pitch, volume=base_vel,
                start_tick=tick, end_tick=end
            ))
            color_idx += 1
        talea_idx += 1
        tick += STEP

    unit = MusicUnit(events=events)
    return unit


def build_composer():
    c = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TICKS_PER_BEAT, beats_per_bar=BEATS_PER_BAR)
    c.create_matrix(num_voices=3, num_sections=3)

    # Voices — clarinet (71) for lead/tenor, bassoon (70) for bass
    c.add_voice("Lead", program=71, channel=0)
    c.add_voice("Tenor", program=71, channel=1)
    c.add_voice("Bass", program=70, channel=2)

    # Sections: A (4 bars), B (4 bars), A' (4 bars)
    c.add_section("A", bars=4)
    c.add_section("B", bars=4)
    c.add_section("Ap", bars=4)

    section_ticks = 4 * BAR  # 7680

    # --- Section A: forward talea, forward color ---
    lead_a = build_isorhythmic_unit(TALEA_LEAD, COLOR_LEAD_A, section_ticks, NOTE_DUR_LEAD, base_vel=95)
    tenor_a = build_isorhythmic_unit(TALEA_TENOR, COLOR_TENOR_A, section_ticks, NOTE_DUR_TENOR, base_vel=80)
    bass_a = build_isorhythmic_unit(TALEA_BASS, COLOR_BASS_A, section_ticks, NOTE_DUR_BASS, base_vel=70)
    c.fill_voice_section("Lead", "A", lead_a)
    c.fill_voice_section("Tenor", "A", tenor_a)
    c.fill_voice_section("Bass", "A", bass_a)

    # --- Section B: retrograde color (contrast) ---
    lead_b = build_isorhythmic_unit(TALEA_LEAD, COLOR_LEAD_B, section_ticks, NOTE_DUR_LEAD, base_vel=100)
    tenor_b = build_isorhythmic_unit(TALEA_TENOR, COLOR_TENOR_B, section_ticks, NOTE_DUR_TENOR, base_vel=85)
    bass_b = build_isorhythmic_unit(TALEA_BASS, COLOR_BASS_B, section_ticks, NOTE_DUR_BASS, base_vel=75)
    c.fill_voice_section("Lead", "B", lead_b)
    c.fill_voice_section("Tenor", "B", tenor_b)
    c.fill_voice_section("Bass", "B", bass_b)

    # --- Section A': forward again, higher velocity (climax) ---
    lead_ap = build_isorhythmic_unit(TALEA_LEAD, COLOR_LEAD_A, section_ticks, NOTE_DUR_LEAD, base_vel=110)
    tenor_ap = build_isorhythmic_unit(TALEA_TENOR, COLOR_TENOR_A, section_ticks, NOTE_DUR_TENOR, base_vel=95)
    bass_ap = build_isorhythmic_unit(TALEA_BASS, COLOR_BASS_A, section_ticks, NOTE_DUR_BASS, base_vel=80)
    c.fill_voice_section("Lead", "Ap", lead_ap)
    c.fill_voice_section("Tenor", "Ap", tenor_ap)
    c.fill_voice_section("Bass", "Ap", bass_ap)

    return c


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "MIDI"), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "Audio"), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "Analysis"), exist_ok=True)

    composer = build_composer()

    # Zero-drift gate
    ok, msg = composer.validate()
    if not ok:
        raise SystemExit(f"Validation failed: {msg}")

    midi_path = os.path.join(OUTPUT_DIR, "MIDI", f"{PROJECT_NAME}.mid")
    composer.to_midi(midi_path)

    size = os.path.getsize(midi_path)
    if size <= 40:
        raise SystemExit(f"MIDI empty/corrupt: {size} bytes")

    # Grid visualization
    write_grid_visualization(
        composer.matrix,
        os.path.join(OUTPUT_DIR, "Analysis", "grid_visualization.txt"),
        ticks_per_character=240, bpm=BPM
    )

    # Provenance
    write_provenance(
        midi_path, classification=AI_ASSISTED,
        generator=f"{PROJECT_NAME}/src/compose.py",
        parameters={
            "bpm": BPM,
            "method": "032-ITCM",
            "sp_method": "SP-023-WaveguideWoodwind",
            "talea_lead": TALEA_LEAD,
            "talea_tenor": TALEA_TENOR,
            "talea_bass": TALEA_BASS,
            "color_lead_a": COLOR_LEAD_A,
            "color_tenor_a": COLOR_TENOR_A,
            "color_bass_a": COLOR_BASS_A,
            "key": "D Dorian",
            "form": "ABA'",
            "talea_length": 7,
            "color_length": 5,
        },
        notes="Isorhythmic talea (7-step rhythm) x color (5-pitch D Dorian). "
              "Coprime lengths create shifting alignment. "
              "SP-023: Clarinet patches (MIDI 71) evoke waveguide woodwind timbre."
    )

    print(f"OK: {midi_path} ({size} bytes)")
    print(f"Validation: {ok} — {msg}")


if __name__ == "__main__":
    main()
