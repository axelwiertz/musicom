"""Microtonal MIDI utilities — pitch bend computation + MIDI export.

Compute 14-bit MIDI pitch bend values from target frequencies,
and export MIDI files with per-note microtonal tuning.

Usage:
    cents = MidiUtils.frequency_to_cents(440.0, reference_note=69)
    bend = MidiUtils.cents_to_pitch_bend(cents)

    exporter = MicrotonalExporter()
    exporter.build_midi_with_pitch_bends(notes, "out.mid")
"""

import math
from typing import List, Dict

__all__ = ["MidiUtils", "MicrotonalExporter"]


class MidiUtils:
    """Static helpers for microtonal MIDI computation."""

    @staticmethod
    def frequency_to_cents(freq: float, reference_freq: float = 440.0) -> float:
        """Convert a frequency to cents offset from a reference frequency."""
        if freq <= 0:
            return 0.0
        return 1200.0 * math.log2(freq / reference_freq)

    @staticmethod
    def cents_to_pitch_bend(cents: float, range_semitones: float = 2.0) -> int:
        """Convert cents offset to signed MIDI pitch bend value (-8192..8191).

        Args:
            cents: Offset in cents from the base note.
            range_semitones: Pitch bend range in semitones (default 2.0 = ±200 cents).

        Returns:
            Signed 14-bit value (-8192..8191); 0 = center (no bend).
        """
        max_cents = range_semitones * 100.0
        ratio = cents / max_cents  # -1.0 to +1.0
        ratio = max(-1.0, min(1.0, ratio))
        return int(round(ratio * 8191))

    @staticmethod
    def frequency_to_pitch_bend(freq: float, base_note: int = 69,
                                range_semitones: float = 2.0) -> tuple:
        """Compute (base_note, bend_value) for a target frequency.

        Returns:
            (midi_note, bend_value) where bend_value is signed (-8192..8191).
        """
        if freq <= 0:
            return (base_note, 0)
        exact_note = 69 + 12 * math.log2(freq / 440.0)
        nearest = int(round(exact_note))
        nearest_freq = 440.0 * (2.0 ** ((nearest - 69) / 12.0))
        cents_off = 1200.0 * math.log2(freq / nearest_freq)
        bend = MidiUtils.cents_to_pitch_bend(cents_off, range_semitones)
        return (nearest, bend)


class MicrotonalExporter:
    """Export MIDI files with per-note pitch bend microtuning."""

    def __init__(self, ticks_per_beat: int = 480):
        self.ticks_per_beat = ticks_per_beat

    def build_midi_with_pitch_bends(self, notes: List[Dict], file_path: str):
        """Write a MIDI file with pitch bend messages per note.

        Args:
            notes: List of dicts:
                {pitch: int, start_tick: int, duration_ticks: int,
                 channel: int = 0, bend_cents: float = 0.0}
            file_path: Output .mid path.
        """
        import mido

        mid = mido.MidiFile(ticks_per_beat=self.ticks_per_beat)
        track = mido.MidiTrack()
        mid.tracks.append(track)

        # Tempo meta
        track.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(120), time=0))

        # Build event list: (tick, kind, channel, ...)
        events = []
        for note in notes:
            ch = note.get("channel", 0)
            pitch = note["pitch"]
            start = note["start_tick"]
            dur = note["duration_ticks"]
            bend_cents = note.get("bend_cents", 0.0)

            bend_val = MidiUtils.cents_to_pitch_bend(bend_cents)
            events.append((start, "pitch_bend", ch, bend_val))
            events.append((start, "note_on", ch, pitch, 100))
            events.append((start + dur, "note_off", ch, pitch, 0))
            events.append((start + dur, "pitch_bend_reset", ch))

        # Sort by tick, then by type priority (bend before on, off before reset)
        type_order = {"pitch_bend": 0, "note_on": 1, "note_off": 2, "pitch_bend_reset": 3}
        events.sort(key=lambda e: (e[0], type_order.get(e[1], 99)))

        # Convert absolute ticks to delta ticks
        prev_tick = 0
        for ev in events:
            tick = ev[0]
            delta = tick - prev_tick
            prev_tick = tick

            kind = ev[1]
            ch = ev[2]
            if kind == "pitch_bend":
                # mido pitchwheel takes the signed 14-bit value directly
                track.append(mido.Message("pitchwheel", channel=ch,
                                          pitch=ev[3], time=delta))
            elif kind == "note_on":
                _, _, _, pitch, vel = ev
                track.append(mido.Message("note_on", channel=ch,
                                          note=pitch, velocity=vel, time=delta))
            elif kind == "note_off":
                _, _, _, pitch, vel = ev
                track.append(mido.Message("note_off", channel=ch,
                                          note=pitch, velocity=vel, time=delta))
            elif kind == "pitch_bend_reset":
                track.append(mido.Message("pitchwheel", channel=ch,
                                          pitch=0, time=delta))

        mid.save(file_path)
