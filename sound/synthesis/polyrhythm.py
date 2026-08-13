"""4-part polyrhythmic arpeggiator — Memory V style.

Independent arpeggio parts at different clock divisions (steps per beat),
generating interleaved patterns and rendering via PolyVoice.

Usage:
    arp = PolyrhythmicArp(sample_rate=44100)
    arp.add_part([60, 64, 67], division=4)   # 16ths
    arp.add_part([48, 55], division=3)       # triplets
    events = arp.generate(bpm=120, total_steps=16)
"""

from typing import List, Dict, Optional

__all__ = ["PolyrhythmicArp"]


class PolyrhythmicArp:
    """Multi-part arpeggiator with per-part clock divisions."""

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.parts: List[Dict] = []  # {notes, division, mode, octaves, gate}

    def add_part(self, notes: List[int], division: int = 4,
                 mode: str = "up", octaves: int = 1, gate: float = 0.8):
        """Add an arpeggio part.

        Args:
            notes: MIDI pitches held for this part.
            division: Steps per beat (4=16ths, 3=triplets, 6=16th triplets, 8).
            mode: 'up', 'down', 'up_down', 'random'.
            octaves: Octave span.
            gate: Gate fraction of each step.
        """
        if not notes:
            raise ValueError("notes must not be empty")
        self.parts.append({
            "notes": list(notes),
            "division": max(1, division),
            "mode": mode,
            "octaves": max(1, octaves),
            "gate": gate,
        })

    def _order(self, notes: List[int], mode: str, octaves: int) -> List[int]:
        """Expand notes per mode/octaves (wraps for up/down)."""
        import random
        asc = sorted(notes)
        spread = []
        for oct in range(octaves):
            spread.extend([n + 12 * oct for n in asc])
        if mode == "up":
            return spread
        if mode == "down":
            return spread[::-1]
        if mode == "up_down":
            return spread + spread[-2:0:-1]
        if mode == "random":
            seq = spread[:]
            random.shuffle(seq)
            return seq
        return spread

    def generate(self, bpm: float = 120.0, total_steps: int = 16,
                 velocity: int = 100) -> List[Dict]:
        """Generate interleaved arpeggio events.

        Returns:
            List of {midi, start_sec, duration_sec, velocity, part, step}.
        """
        events: List[Dict] = []
        beat_sec = 60.0 / bpm

        for part_idx, part in enumerate(self.parts):
            division = part["division"]
            step_sec = beat_sec / division
            seq = self._order(part["notes"], part["mode"], part["octaves"])
            n_steps = total_steps
            for i in range(n_steps):
                midi = seq[i % len(seq)]
                events.append({
                    "midi": midi,
                    "start_sec": i * step_sec,
                    "duration_sec": step_sec * part["gate"],
                    "velocity": velocity,
                    "part": part_idx,
                    "step": i,
                })
        events.sort(key=lambda e: (e["start_sec"], e["part"]))
        return events

    def render(self, bpm: float = 120.0, total_steps: int = 16) -> "np.ndarray":
        """Render all parts into one mono buffer via PolyVoice."""
        import numpy as np
        from sound.synthesis.polysynth import PolyVoice

        np_ = np  # local alias for the quoted return type
        events = self.generate(bpm=bpm, total_steps=total_steps)
        if not events:
            return np.zeros(0, dtype=np.float32)

        voice = PolyVoice(self.sample_rate)
        max_end = max(e["start_sec"] + e["duration_sec"] for e in events)
        n_samples = int(max_end * self.sample_rate) + int(0.1 * self.sample_rate)
        out = np.zeros(n_samples, dtype=np.float32)

        for e in events:
            freq = 440.0 * (2.0 ** ((e["midi"] - 69) / 12.0))
            note = voice.render_note(freq, e["duration_sec"])
            start = int(e["start_sec"] * self.sample_rate)
            end = min(start + len(note), n_samples)
            out[start:end] += note[:end - start]

        peak = np.max(np.abs(out))
        if peak > 1.0:
            out = out / peak
        return out
