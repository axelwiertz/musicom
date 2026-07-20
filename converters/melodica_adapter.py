# Copyright (c) 2026 Axel Wiertz / Musicom
#
# Licensed under the MIT License.

"""
converters/melodica_adapter.py — Adapter between Melodica parametric outputs and Musicom UnitMatrix.

This adapter provides formal interface boundaries between Melodica's continuous beat representation 
and Musicom's discrete UnitMatrix block structure. Enables zero-drift conversion and programmatic cell segmentation.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import numpy as np

from structures import MusicUnit, MusicEvent, UnitMatrix

@dataclass
class MelodicaExchangeNote:
    """Interoperability note specification matching Melodica's Note/NoteInfo payloads."""
    pitch: int
    start_beat: float
    duration_beats: float
    velocity: int = 100
    cc_data: Dict[int, List[Tuple[float, int]]] = field(default_factory=dict) # CC_NUM -> list of (beat, val)


class MelodicaToMatrixConverter:
    """Converts linear, parametric Melodica track payloads into discrete Musicom structures."""

    def __init__(self, bpm: float = 120.0, ticks_per_beat: int = 960) -> None:
        self.bpm = bpm
        self.ticks_per_beat = ticks_per_beat

    def to_music_unit(
        self, 
        notes: List[MelodicaExchangeNote], 
        start_beat: float, 
        end_beat: float
    ) -> MusicUnit:
        """
        Segments and packs continuous Melodica notes falling into a specific [start_beat, end_beat) cell.
        Translates floats strictly to integer ticks preventing long-term drift.
        """
        music_events: List[MusicEvent] = []
        
        start_tick = int(round(start_beat * self.ticks_per_beat))
        end_tick = int(round(end_beat * self.ticks_per_beat))
        cell_length_ticks = end_tick - start_tick

        for note in notes:
            note_start_tick = int(round(note.start_beat * self.ticks_per_beat))
            note_duration_ticks = int(round(note.duration_beats * self.ticks_per_beat))
            note_end_tick = note_start_tick + note_duration_ticks

            # Check if note begins within this cell boundary [start_tick, end_tick)
            if note_start_tick >= start_tick and note_start_tick < end_tick:
                # Calculate start relative to cell origin
                rel_start = note_start_tick - start_tick
                # Clamp end tick to cell boundaries to prevent overflow into next unit
                rel_end = min(note_end_tick - start_tick, cell_length_ticks)
                
                if rel_end > rel_start:
                    event = MusicEvent(
                        pitch=note.pitch,
                        volume=note.velocity,
                        start_tick=rel_start,
                        end_tick=rel_end
                    )
                    music_events.append(event)

        return MusicUnit(events=music_events)

    def populate_matrix(
        self, 
        melodica_tracks: Dict[str, List[MelodicaExchangeNote]], 
        section_boundaries_beats: List[float]
    ) -> UnitMatrix:
        """
        Builds and populates a valid, symmetric Musicom UnitMatrix from multi-track Melodica streams.
        
        Args:
            melodica_tracks: Dict mapping Track Names to List of MelodicaExchangeNotes.
            section_boundaries_beats: Timeline offsets marking section boundaries in beats.
                                      Example: [0.0, 16.0, 32.0, 48.0] defines 3 sections.
        """
        if len(section_boundaries_beats) < 2:
            raise ValueError("Must provide at least two boundary markers to define one section.")

        num_voices = len(melodica_tracks)
        num_sections = len(section_boundaries_beats) - 1
        
        # Instantiate UnitMatrix using Musicom core (shape instead of rows/cols)
        matrix = UnitMatrix(shape=(num_voices, num_sections))
        
        for r_idx, (track_name, notes) in enumerate(sorted(melodica_tracks.items())):
            # Populate matrix cells row by row
            for c_idx in range(num_sections):
                start = section_boundaries_beats[c_idx]
                end = section_boundaries_beats[c_idx + 1]
                
                cell_unit = self.to_music_unit(notes, start, end)
                matrix.set_unit((r_idx, c_idx), cell_unit)
                
        return matrix

