"""Composition entry point — musicom engine only.

Copy this template, rename the project folder, edit the CONFIG + build_matrix().
Everything below uses the sanctioned zero-drift workflow. Do NOT import raw mido
for authoring, and do NOT add sys.path hacks (musicom is installed editable).
"""
import os

from structures import MusicUnit, MusicEvent, MidiInstrument
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_note_unit, create_chord_unit, create_empty_unit,
)
from ai.utils.visualizer import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED

# ---------------------------------------------------------------- CONFIG -----
PROJECT_NAME = "template_project"
OUTPUT_DIR = f"/opt/data/projects/Research/outputs/{PROJECT_NAME}"
BPM = 120
TICKS_PER_BEAT = 480
BEATS_PER_BAR = 4
BAR = TICKS_PER_BEAT * BEATS_PER_BAR


def build_composer() -> UnitMatrixComposer:
    """Define voices, sections, and fill cells. Edit this."""
    c = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TICKS_PER_BEAT, beats_per_bar=BEATS_PER_BAR)
    c.create_matrix(num_voices=2, num_sections=1)
    c.add_voice("Lead", program=MidiInstrument.FLUTE, channel=0)
    c.add_voice("Bass", program=MidiInstrument.BASS, channel=1)
    c.add_section("A", bars=1)

    c.fill_voice_section("Lead", "A", create_note_unit(72, BAR))
    c.fill_voice_section("Bass", "A", create_note_unit(36, BAR))
    return c


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    composer = build_composer()

    ok, msg = composer.validate()          # zero-drift gate
    if not ok:
        raise SystemExit(f"Validation failed (track drift): {msg}")

    midi_path = os.path.join(OUTPUT_DIR, f"{PROJECT_NAME}.mid")
    composer.to_midi(midi_path)

    # verify-don't-trust
    size = os.path.getsize(midi_path)
    if size <= 40:
        raise SystemExit(f"MIDI empty/corrupt: {size} bytes")

    # grid + provenance
    write_grid_visualization(
        composer.matrix, os.path.join(OUTPUT_DIR, "grid_visualization.txt"),
        ticks_per_character=240, bpm=BPM)
    write_provenance(
        midi_path, classification=AI_ASSISTED, generator=f"{PROJECT_NAME}/compose.py",
        parameters={"bpm": BPM}, notes="Composed via musicom UnitMatrixComposer.")

    print(f"OK: {midi_path} ({size} bytes)")


if __name__ == "__main__":
    main()
