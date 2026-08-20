"""DX7 voice format parser — Rithmatic-style.

Parses Yamaha DX7 voice data in both packed (128-byte) and expanded
(155-byte) formats. Extracts operator parameters, algorithm, feedback,
and other synthesis parameters. Does NOT implement SysEx output (hardware-
dependent).

Replicated from: Rithmatic DX7 patch manager (synthtopia 2026-08-18).

Usage:
    from sound.synthesis.dx7_voice import DX7Voice, parse_dx7_packed

    # Parse a 128-byte packed DX7 voice
    voice = parse_dx7_packed(data_bytes)
    print(voice.algorithm)
    print(voice.operators[0].frequency_ratio)
"""

import struct
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

__all__ = ["DX7Operator", "DX7Voice", "parse_dx7_packed", "parse_dx7_expanded"]


@dataclass
class DX7Operator:
    """DX7 operator parameters."""
    # Envelope Generator (EG)
    eg_rate_1: int = 99  # 0-99
    eg_rate_2: int = 99
    eg_rate_3: int = 99
    eg_rate_4: int = 99
    eg_level_1: int = 99  # 0-99
    eg_level_2: int = 99
    eg_level_3: int = 99
    eg_level_4: int = 0
    # Level / Velocity Sensitivity
    output_level: int = 0  # 0-99
    vel_sensitivity: int = 0  # 0-7
    # Keyboard Scaling
    break_point: int = 39  # MIDI note 0-99
    key_depth_l: int = 0  # 0-99 (left depth)
    key_depth_r: int = 0  # 0-99 (right depth)
    key_scale_l: int = 0  # 0-3 (curve: -LIN, -EXP, +EXP, +LIN)
    key_scale_r: int = 0  # 0-3
    # Oscillator
    osc_mode: int = 1  # 0=ratio, 1=fixed
    frequency_coarse: int = 1  # 0-31
    frequency_fine: int = 0  # 0-99
    detune: int = 7  # 0-14 (7=center)
    # Amplitude Modulation
    amp_mod_sensitivity: int = 0  # 0-3

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'eg_rates': [self.eg_rate_1, self.eg_rate_2, self.eg_rate_3, self.eg_rate_4],
            'eg_levels': [self.eg_level_1, self.eg_level_2, self.eg_level_3, self.eg_level_4],
            'output_level': self.output_level,
            'vel_sensitivity': self.vel_sensitivity,
            'break_point': self.break_point,
            'key_depth': [self.key_depth_l, self.key_depth_r],
            'key_scale': [self.key_scale_l, self.key_scale_r],
            'osc_mode': self.osc_mode,
            'frequency': [self.frequency_coarse, self.frequency_fine],
            'detune': self.detune,
            'amp_mod_sensitivity': self.amp_mod_sensitivity,
        }


@dataclass
class DX7Voice:
    """DX7 voice (single patch)."""
    # Global parameters
    pitch_eg_rate_1: int = 99
    pitch_eg_rate_2: int = 99
    pitch_eg_rate_3: int = 99
    pitch_eg_rate_4: int = 99
    pitch_eg_level_1: int = 50
    pitch_eg_level_2: int = 50
    pitch_eg_level_3: int = 50
    pitch_eg_level_4: int = 50
    algorithm: int = 0  # 0-31
    feedback: int = 0  # 0-7
    osc_sync: int = 1  # 0=off, 1=on
    lfo_speed: int = 35  # 0-99
    lfo_delay: int = 0  # 0-99
    lfo_pitch_mod_depth: int = 0  # 0-99
    lfo_amp_mod_depth: int = 0  # 0-99
    lfo_sync: int = 0  # 0=off, 1=on
    lfo_waveform: int = 0  # 0=triangle, 1=saw down, 2=saw up, 3=square, 4=sine, 5=s&h
    pitch_mod_sensitivity: int = 3  # 0-7
    transpose: int = 24  # 0-48 (MIDI note)
    # Name
    name: str = "INIT VOICE"
    # Operators (6 operators, op1=carrier, op6=modulator in most algos)
    operators: List[DX7Operator] = None

    def __post_init__(self):
        if self.operators is None:
            self.operators = [DX7Operator() for _ in range(6)]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'pitch_eg_rates': [self.pitch_eg_rate_1, self.pitch_eg_rate_2,
                               self.pitch_eg_rate_3, self.pitch_eg_rate_4],
            'pitch_eg_levels': [self.pitch_eg_level_1, self.pitch_eg_level_2,
                                self.pitch_eg_level_3, self.pitch_eg_level_4],
            'algorithm': self.algorithm,
            'feedback': self.feedback,
            'osc_sync': self.osc_sync,
            'lfo': {
                'speed': self.lfo_speed,
                'delay': self.lfo_delay,
                'pitch_mod_depth': self.lfo_pitch_mod_depth,
                'amp_mod_depth': self.lfo_amp_mod_depth,
                'sync': self.lfo_sync,
                'waveform': self.lfo_waveform,
            },
            'pitch_mod_sensitivity': self.pitch_mod_sensitivity,
            'transpose': self.transpose,
            'name': self.name,
            'operators': [op.to_dict() for op in self.operators],
        }


def parse_dx7_packed(data: bytes) -> DX7Voice:
    """Parse a 128-byte packed DX7 voice.

    The packed format is used in 32-voice bulk dumps and .syx files.
    Each voice is 128 bytes (155 bytes expanded).

    Args:
        data: 128 bytes of packed DX7 voice data.

    Returns:
        Parsed DX7Voice object.
    """
    if len(data) < 128:
        raise ValueError(f"Expected 128 bytes, got {len(data)}")

    voice = DX7Voice()
    # Parse operators (6 operators, 17 bytes each = 102 bytes)
    for op_idx in range(6):
        op = DX7Operator()
        base = op_idx * 17
        # EG rates and levels (8 bytes)
        op.eg_rate_1 = data[base + 0]
        op.eg_rate_2 = data[base + 1]
        op.eg_rate_3 = data[base + 2]
        op.eg_rate_4 = data[base + 3]
        op.eg_level_1 = data[base + 4]
        op.eg_level_2 = data[base + 5]
        op.eg_level_3 = data[base + 6]
        op.eg_level_4 = data[base + 7]
        # Level and velocity (2 bytes)
        op.output_level = data[base + 8]
        op.vel_sensitivity = data[base + 9] & 0x07
        # Keyboard scaling (5 bytes)
        op.break_point = data[base + 10]
        op.key_depth_l = data[base + 11]
        op.key_depth_r = data[base + 12]
        op.key_scale_l = data[base + 13] & 0x03
        op.key_scale_r = (data[base + 13] >> 4) & 0x03
        # Oscillator (3 bytes)
        op.osc_mode = (data[base + 14] >> 6) & 0x01
        op.frequency_coarse = data[base + 14] & 0x1F
        op.frequency_fine = data[base + 15]
        op.detune = data[base + 16] & 0x0F
        op.amp_mod_sensitivity = (data[base + 16] >> 4) & 0x03
        voice.operators[op_idx] = op

    # Global parameters (26 bytes, starting at offset 102)
    base = 102
    voice.pitch_eg_rate_1 = data[base + 0]
    voice.pitch_eg_rate_2 = data[base + 1]
    voice.pitch_eg_rate_3 = data[base + 2]
    voice.pitch_eg_rate_4 = data[base + 3]
    voice.pitch_eg_level_1 = data[base + 4]
    voice.pitch_eg_level_2 = data[base + 5]
    voice.pitch_eg_level_3 = data[base + 6]
    voice.pitch_eg_level_4 = data[base + 7]
    voice.algorithm = data[base + 8] & 0x1F
    voice.osc_sync = (data[base + 8] >> 5) & 0x01
    voice.feedback = data[base + 9] & 0x07
    voice.lfo_speed = data[base + 10]
    voice.lfo_delay = data[base + 11]
    voice.lfo_pitch_mod_depth = data[base + 12]
    voice.lfo_amp_mod_depth = data[base + 13]
    voice.lfo_sync = (data[base + 14] >> 4) & 0x01
    voice.lfo_waveform = data[base + 14] & 0x05
    voice.pitch_mod_sensitivity = data[base + 15] & 0x07
    voice.transpose = data[base + 16]
    # Name (10 bytes, ASCII)
    name_bytes = data[base + 17:base + 27]
    voice.name = ''.join(chr(b & 0x7F) for b in name_bytes).strip()

    return voice


def parse_dx7_expanded(data: bytes) -> DX7Voice:
    """Parse a 155-byte expanded DX7 voice.

    The expanded format is used for single-voice SysEx dumps.

    Args:
        data: 155 bytes of expanded DX7 voice data.

    Returns:
        Parsed DX7Voice object.
    """
    if len(data) < 155:
        raise ValueError(f"Expected 155 bytes, got {len(data)}")

    voice = DX7Voice()
    # Expanded format: each parameter is one byte
    # Operators (6 operators, 21 bytes each = 126 bytes)
    for op_idx in range(6):
        op = DX7Operator()
        base = op_idx * 21
        op.eg_rate_1 = data[base + 0]
        op.eg_rate_2 = data[base + 1]
        op.eg_rate_3 = data[base + 2]
        op.eg_rate_4 = data[base + 3]
        op.eg_level_1 = data[base + 4]
        op.eg_level_2 = data[base + 5]
        op.eg_level_3 = data[base + 6]
        op.eg_level_4 = data[base + 7]
        op.output_level = data[base + 8]
        op.vel_sensitivity = data[base + 9]
        op.break_point = data[base + 10]
        op.key_depth_l = data[base + 11]
        op.key_depth_r = data[base + 12]
        op.key_scale_l = data[base + 13]
        op.key_scale_r = data[base + 14]
        op.osc_mode = data[base + 15]
        op.frequency_coarse = data[base + 16]
        op.frequency_fine = data[base + 17]
        op.detune = data[base + 18]
        op.amp_mod_sensitivity = data[base + 19]
        # byte 20 is unused/reserved
        voice.operators[op_idx] = op

    # Global parameters (29 bytes, starting at offset 126)
    base = 126
    voice.pitch_eg_rate_1 = data[base + 0]
    voice.pitch_eg_rate_2 = data[base + 1]
    voice.pitch_eg_rate_3 = data[base + 2]
    voice.pitch_eg_rate_4 = data[base + 3]
    voice.pitch_eg_level_1 = data[base + 4]
    voice.pitch_eg_level_2 = data[base + 5]
    voice.pitch_eg_level_3 = data[base + 6]
    voice.pitch_eg_level_4 = data[base + 7]
    voice.algorithm = data[base + 8]
    voice.feedback = data[base + 9]
    voice.osc_sync = data[base + 10]
    voice.lfo_speed = data[base + 11]
    voice.lfo_delay = data[base + 12]
    voice.lfo_pitch_mod_depth = data[base + 13]
    voice.lfo_amp_mod_depth = data[base + 14]
    voice.lfo_sync = data[base + 15]
    voice.lfo_waveform = data[base + 16]
    voice.pitch_mod_sensitivity = data[base + 17]
    voice.transpose = data[base + 18]
    # Name (10 bytes)
    name_bytes = data[base + 19:base + 29]
    voice.name = ''.join(chr(b & 0x7F) for b in name_bytes).strip()

    return voice


def demo() -> str:
    """Parse a sample DX7 voice and return summary."""
    # Create a minimal "INIT VOICE" packed data
    data = bytearray(128)
    # Set some reasonable defaults
    # Operator 1: carrier with moderate output
    data[8] = 80  # output level
    data[9] = 3   # velocity sensitivity
    # Algorithm 5 (a common one)
    data[110] = 5
    # Name: "TEST VOICE"
    name = b"TEST VOICE"
    data[119:119 + len(name)] = name

    voice = parse_dx7_packed(bytes(data))
    lines = [
        f"DX7 Voice Parser demo:",
        f"  Name: {voice.name}",
        f"  Algorithm: {voice.algorithm}",
        f"  Feedback: {voice.feedback}",
        f"  LFO speed: {voice.lfo_speed}",
        f"  Op1 output level: {voice.operators[0].output_level}",
        f"  Op1 vel sensitivity: {voice.operators[0].vel_sensitivity}",
        f"  Total operators: {len(voice.operators)}",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    print(demo())
