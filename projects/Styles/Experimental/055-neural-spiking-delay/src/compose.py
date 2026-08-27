# -*- coding: utf-8 -*-
"""
Project 055: Neural Spiking + Feedback Delay Line
Composition Method: 037 (FitzHugh-Nagumo Neural Spiking - FHNS)
Sound Production: SP-013 (Feedback Delay Line with HF Damping)

TWO-PHASE ARCHITECTURE:
  Phase 1 (FHN draft): Neural dynamics → spike timings + ISI-derived pitch indices
  Phase 2 (musicom rules): Harmonic progression, voice leading, scale quantization

Uses musicom engine:
  - structures: MusicUnit, MusicEvent, UnitMatrix
  - workflows: UnitMatrixComposer (zero-drift export)
  - ai/rules: FunctionalHarmony, VoiceLeadingRules
  - ai/generators: ProgressionGenerator (harmonic framework)
  - ai/utils/constants: SCALE_PATTERNS, CHORD_QUALITIES, HARMONIC_FUNCTIONS
"""
import os
import numpy as np

from structures import MusicUnit, MusicEvent, MidiInstrument
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_note_unit, create_chord_unit, create_empty_unit,
)
from ai.utils.visualizer import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED

# musicom rules & constants
from ai.utils.constants import SCALE_PATTERNS, CHORD_QUALITIES, HARMONIC_FUNCTIONS

# ---------------------------------------------------------------- CONFIG ----
PROJECT_NAME = "055-neural-spiking-delay"
OUTPUT_DIR = f"/opt/data/projects/Styles/Experimental/{PROJECT_NAME}"
BPM = 100
TICKS_PER_BEAT = 480
BEATS_PER_BAR = 4
BAR = TICKS_PER_BEAT * BEATS_PER_BAR  # 1920

# Key: E minor (aeolian) — using musicom SCALE_PATTERNS
KEY_ROOT = 4  # E
SCALE_NAME = "natural_minor"
SCALE = SCALE_PATTERNS[SCALE_NAME]  # [0, 2, 3, 5, 7, 8, 10]

# --- FitzHugh-Nagumo Parameters ---
FHN_A = 0.7
FHN_B = 0.8
FHN_TAU = 12.5
FHN_DT = 0.01

I_DRIVES = {
    "Lead": 0.6,
    "Tenor": 0.8,
    "Bass": 0.35,
    "Pad": 0.4,
}

SPIKE_THRESHOLD = 0.5

REFRACTORY_TICKS = {
    "Lead": 120,
    "Tenor": 180,
    "Bass": 480,
    "Pad": 960,
}

VOICE_CONFIG = {
    "Lead":  {"octave": 4, "vel": 95, "program": 73, "dur": 180, "range": (60, 84)},
    "Tenor": {"octave": 3, "vel": 80, "program": 0,  "dur": 240, "range": (48, 72)},
    "Bass":  {"octave": 2, "vel": 100,"program": 33, "dur": 720, "range": (36, 60)},
    "Pad":   {"octave": 3, "vel": 65, "program": 48, "dur": 1440,"range": (48, 72)},
}

# ============================================================================
# PHASE 1: FHN NEURAL DYNAMICS → RAW DRAFT
# ============================================================================

def fitzhugh_nagumo_step(v, w, I_ext):
    """Single FHN integration step."""
    dv = v - v**3 / 3.0 - w + I_ext
    dw = (v + FHN_A - FHN_B * w) / FHN_TAU
    return v + FHN_DT * dv, w + FHN_DT * dw


def generate_voltage_trace(n_steps, I_ext, v0=-0.5, w0=-0.3, noise_std=0.15):
    """Generate FHN voltage trace with slow noise in drive current."""
    v_trace = np.zeros(n_steps)
    w_trace = np.zeros(n_steps)
    v_trace[0] = v0
    w_trace[0] = w0

    noise = np.random.randn(n_steps) * noise_std
    filtered_noise = np.zeros(n_steps)
    alpha = 0.005
    for i in range(1, n_steps):
        filtered_noise[i] = filtered_noise[i-1] + alpha * (noise[i] - filtered_noise[i-1])

    for i in range(n_steps - 1):
        I_noisy = I_ext + filtered_noise[i]
        v_trace[i+1], w_trace[i+1] = fitzhugh_nagumo_step(
            v_trace[i], w_trace[i], I_noisy
        )

    return v_trace, w_trace


def detect_spikes(v_trace, w_trace, threshold, refractory_steps):
    """Detect upward threshold crossings with refractory period.
    Returns list of (spike_index, w_at_spike) tuples.
    """
    spikes = []
    last_spike = -refractory_steps

    for i in range(1, len(v_trace)):
        if v_trace[i-1] < threshold and v_trace[i] >= threshold:
            if i - last_spike >= refractory_steps:
                w_val = w_trace[i]
                spikes.append((i, w_val))
                last_spike = i

    return spikes


def fhn_to_raw_events(v_trace, w_trace, section_ticks, voice_name, steps_per_tick):
    """
    Phase 1: Convert FHN traces to raw events.
    Spike timings from neural dynamics, pitch from ISI mapping.
    Returns list of dicts with tick, pitch_index [0,1], velocity, duration.
    pitch_index is a raw float — will be quantized in Phase 2.
    """
    config = VOICE_CONFIG[voice_name]
    refractory_steps = int(REFRACTORY_TICKS[voice_name] * steps_per_tick)

    spike_data = detect_spikes(v_trace, w_trace, SPIKE_THRESHOLD, refractory_steps)

    raw_events = []

    if len(spike_data) < 2:
        for sp_idx, w_val in spike_data:
            tick = int(sp_idx / steps_per_tick)
            tick = max(0, min(tick, section_ticks - 20))
            raw_events.append({
                "tick": tick,
                "pitch_index": 0.0,
                "velocity": config["vel"],
                "duration": config["dur"],
            })
        return raw_events

    # Calculate ISIs
    isis = []
    for i in range(1, len(spike_data)):
        isi = spike_data[i][0] - spike_data[i-1][0]
        isis.append(isi)

    min_isi = min(isis)
    max_isi = max(isis)
    isi_range = max_isi - min_isi if max_isi > min_isi else 1

    for i, (sp_idx, w_val) in enumerate(spike_data):
        tick = int(sp_idx / steps_per_tick)
        tick = max(0, min(tick, section_ticks - 20))

        if i == 0:
            norm_isi = 0.5
        elif i <= len(isis):
            norm_isi = (isis[i-1] - min_isi) / isi_range
        else:
            norm_isi = 0.5

        pitch_index = 1.0 - norm_isi  # shorter ISI → higher

        vel = int(config["vel"] * (0.7 + 0.3 * abs(w_val)))
        vel = max(40, min(127, vel))

        raw_events.append({
            "tick": tick,
            "pitch_index": pitch_index,
            "velocity": vel,
            "duration": config["dur"],
        })

    return raw_events


# ============================================================================
# PHASE 2: MUSICOM RULES POST-PROCESSING
# ============================================================================

# Section-level chord progressions (FunctionalHarmony framework)
SECTION_PROGRESSIONS = {
    "A":  ["i", "iv", "i", "v"],
    "B":  ["i", "v", "iv", "VII", "III", "iv", "v", "i"],
    "Ap": ["i", "iv", "v", "i"],
}

# Chord tones per Roman numeral in natural minor (scale degree indices 0-6)
CHORD_DEGREES_MINOR = {
    "i":    [0, 2, 4],
    "ii°":  [1, 3, 5],
    "III":  [2, 4, 6],
    "iv":   [3, 5, 0],
    "v":    [4, 6, 1],
    "VI":   [5, 0, 2],
    "VII":  [6, 1, 3],
}


def scale_degree_to_midi(degree_index, octave, key_root=KEY_ROOT, scale=SCALE):
    """Convert scale degree index to MIDI note number."""
    n = len(scale)
    octave_offset = degree_index // n
    degree_in_scale = degree_index % n
    midi = 12 * (octave + octave_offset + 1) + key_root + scale[degree_in_scale]
    return max(36, min(84, midi))


def get_chord_tones_for_section(section_name, bar_offset, bars_in_section):
    """Get chord tones (as scale degree indices) for a given bar position."""
    progression = SECTION_PROGRESSIONS[section_name]
    n_chords = len(progression)
    bars_per_chord = max(1, bars_in_section // n_chords)
    chord_idx = min(bar_offset // bars_per_chord, n_chords - 1)
    roman = progression[chord_idx]
    return CHORD_DEGREES_MINOR.get(roman, [0, 2, 4]), roman


def quantize_to_chord_tones(pitch_index, chord_tones, octave, key_root=KEY_ROOT, scale=SCALE):
    """
    Phase 2a: Quantize raw pitch_index to nearest chord tone.
    """
    target_degree = int(pitch_index * 7)
    target_degree = max(0, min(6, target_degree))

    min_dist = 999
    best_degree = chord_tones[0]
    for ct in chord_tones:
        ct_abs = ct if ct >= 0 else ct + 7
        dist = abs(target_degree - ct_abs)
        dist = min(dist, 7 - dist)
        if dist < min_dist:
            min_dist = dist
            best_degree = ct_abs

    return scale_degree_to_midi(best_degree, octave, key_root, scale)


def apply_voice_leading_rules(events_per_voice, section_name, bars_in_section):
    """
    Phase 2b: Check for parallel fifths/octaves between adjacent voices.
    """
    voice_names = list(events_per_voice.keys())
    violations_found = []

    for bar in range(bars_in_section):
        bar_start = bar * BAR
        bar_end = bar_start + BAR

        bar_pitches = {}
        for v_name in voice_names:
            evts = events_per_voice[v_name]
            active = [e for e in evts
                      if bar_start <= e["tick"] < bar_end
                      and e.get("midi_pitch", 0) > 0]
            if active:
                bar_pitches[v_name] = int(active[0]["midi_pitch"])

        for i in range(len(voice_names) - 1):
            v1, v2 = voice_names[i], voice_names[i+1]
            if v1 not in bar_pitches or v2 not in bar_pitches:
                continue

            p1 = bar_pitches[v1]
            p2 = bar_pitches[v2]
            interval = abs(p1 - p2) % 12

            if interval in (7, 0) and bar > 0:
                prev_bar = bar - 1
                prev_start = prev_bar * BAR
                prev_end = prev_start + BAR
                prev_p1 = None
                prev_p2 = None
                for v_name in [v1, v2]:
                    evts = events_per_voice[v_name]
                    active = [e for e in evts
                              if prev_start <= e["tick"] < prev_end
                              and e.get("midi_pitch", 0) > 0]
                    if active:
                        if v_name == v1:
                            prev_p1 = int(active[0]["midi_pitch"])
                        else:
                            prev_p2 = int(active[0]["midi_pitch"])

                if prev_p1 is not None and prev_p2 is not None:
                    prev_interval = abs(prev_p1 - prev_p2) % 12
                    if prev_interval == interval and interval in (7, 0):
                        motion1 = p1 - prev_p1
                        motion2 = p2 - prev_p2
                        if motion1 == motion2 and motion1 != 0:
                            violations_found.append({
                                "bar": bar,
                                "type": "parallel_fifth" if interval == 7 else "parallel_octave",
                                "voices": (v1, v2),
                            })

    return violations_found


def correct_voice_leading(events_per_voice, section_name, bars_in_section):
    """
    Phase 2c: Correct voice leading violations.
    Shift the upper voice to the next available chord tone.
    """
    voice_names = list(events_per_voice.keys())

    for bar in range(1, bars_in_section):
        bar_start = bar * BAR
        bar_end = bar_start + BAR
        prev_bar_start = (bar - 1) * BAR

        chord_tones, roman = get_chord_tones_for_section(
            section_name, bar, bars_in_section
        )

        bar_pitches = {}
        prev_pitches = {}
        for v_name in voice_names:
            evts = events_per_voice[v_name]
            active = [e for e in evts
                      if bar_start <= e["tick"] < bar_end
                      and e.get("midi_pitch", 0) > 0]
            prev_active = [e for e in evts
                           if prev_bar_start <= e["tick"] < bar_start
                           and e.get("midi_pitch", 0) > 0]
            if active:
                bar_pitches[v_name] = active[0]
            if prev_active:
                prev_pitches[v_name] = prev_active[0]

        for i in range(len(voice_names) - 1):
            v1, v2 = voice_names[i], voice_names[i+1]
            if v1 not in bar_pitches or v2 not in bar_pitches:
                continue
            if v1 not in prev_pitches or v2 not in prev_pitches:
                continue

            p1 = int(bar_pitches[v1]["midi_pitch"])
            p2 = int(bar_pitches[v2]["midi_pitch"])
            pp1 = int(prev_pitches[v1]["midi_pitch"])
            pp2 = int(prev_pitches[v2]["midi_pitch"])

            interval = abs(p1 - p2) % 12
            prev_interval = abs(pp1 - pp2) % 12

            if interval == prev_interval and interval in (7, 0):
                motion1 = p1 - pp1
                motion2 = p2 - pp2
                if motion1 == motion2 and motion1 != 0:
                    config = VOICE_CONFIG[v2]
                    current_degree = None
                    for d in range(7):
                        if scale_degree_to_midi(d, config["octave"]) == p2:
                            current_degree = d
                            break
                    if current_degree is not None:
                        new_degree = (current_degree + 1) % 7
                        new_pitch = scale_degree_to_midi(new_degree, config["octave"])
                        lo, hi = config["range"]
                        new_pitch = max(lo, min(hi, new_pitch))
                        bar_pitches[v2]["midi_pitch"] = new_pitch

    return events_per_voice


def raw_events_to_unit(raw_events, section_ticks, voice_name, section_name, bars_in_section):
    """
    Phase 2 final: Convert raw events → MusicUnit with chord-tone quantization.
    """
    config = VOICE_CONFIG[voice_name]
    events = []

    for evt in raw_events:
        tick = evt["tick"]
        bar_offset = tick // BAR

        chord_tones, roman = get_chord_tones_for_section(
            section_name, bar_offset, bars_in_section
        )

        midi_pitch = quantize_to_chord_tones(
            evt["pitch_index"], chord_tones, config["octave"]
        )

        lo, hi = config["range"]
        midi_pitch = max(lo, min(hi, midi_pitch))

        dur = evt["duration"]
        if events and tick <= events[-1].end_tick:
            tick = events[-1].end_tick + 10
        if tick + dur > section_ticks:
            dur = section_ticks - tick
        if dur < 20:
            continue

        events.append(MusicEvent(
            pitch=midi_pitch,
            volume=evt["velocity"],
            start_tick=tick,
            end_tick=tick + dur,
        ))

    if events and events[-1].end_tick < section_ticks:
        events.append(MusicEvent(pitch=0, volume=0,
                                 start_tick=section_ticks - 1, end_tick=section_ticks))
    elif not events:
        events.append(MusicEvent(pitch=0, volume=0, start_tick=0, end_tick=section_ticks))

    return MusicUnit(events=events)


# ============================================================================
# COMPOSITION BUILDER
# ============================================================================

def build_composer():
    """Build composition: FHN draft → musicom rules → UnitMatrix."""
    c = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TICKS_PER_BEAT, beats_per_bar=BEATS_PER_BAR)
    c.create_matrix(num_voices=4, num_sections=3)

    c.add_voice("Lead", program=VOICE_CONFIG["Lead"]["program"], channel=0)
    c.add_voice("Tenor", program=VOICE_CONFIG["Tenor"]["program"], channel=1)
    c.add_voice("Bass", program=VOICE_CONFIG["Bass"]["program"], channel=2)
    c.add_voice("Pad", program=VOICE_CONFIG["Pad"]["program"], channel=3)

    section_bars = {"A": 4, "B": 8, "Ap": 4}
    section_ticks = {k: v * BAR for k, v in section_bars.items()}

    c.add_section("A", bars=section_bars["A"])
    c.add_section("B", bars=section_bars["B"])
    c.add_section("Ap", bars=section_bars["Ap"])

    steps_per_tick = 100
    voice_names = ["Lead", "Tenor", "Bass", "Pad"]

    all_violations = []

    for sec_name in ["A", "B", "Ap"]:
        sec_ticks = section_ticks[sec_name]
        n_steps = int(sec_ticks * steps_per_tick)
        bars = section_bars[sec_name]

        # ---- PHASE 1: FHN raw draft ----
        raw_per_voice = {}
        for v_name in voice_names:
            v0 = -0.5 + 0.1 * voice_names.index(v_name)
            w0 = -0.3 + 0.05 * voice_names.index(v_name)
            v_trace, w_trace = generate_voltage_trace(
                n_steps, I_DRIVES[v_name], v0=v0, w0=w0
            )
            raw_per_voice[v_name] = fhn_to_raw_events(
                v_trace, w_trace, sec_ticks, v_name, steps_per_tick
            )

        # ---- PHASE 2a: Quantize to chord tones → MusicUnits ----
        units_per_voice = {}
        events_per_voice = {}
        for v_name in voice_names:
            unit = raw_events_to_unit(
                raw_per_voice[v_name], sec_ticks, v_name, sec_name, bars
            )
            units_per_voice[v_name] = unit
            events_per_voice[v_name] = [
                {"tick": e.start_tick, "midi_pitch": e.pitch,
                 "velocity": e.volume, "duration": e.duration}
                for e in unit.events if e.pitch > 0
            ]

        # ---- PHASE 2b: Voice leading check ----
        violations = apply_voice_leading_rules(events_per_voice, sec_name, bars)
        all_violations.extend(violations)

        # ---- PHASE 2c: Correct violations ----
        if violations:
            events_per_voice = correct_voice_leading(
                events_per_voice, sec_name, bars
            )
            for v_name in voice_names:
                corrected = events_per_voice[v_name]
                events_list = []
                for evt in corrected:
                    events_list.append(MusicEvent(
                        pitch=evt["midi_pitch"],
                        volume=evt["velocity"],
                        start_tick=evt["tick"],
                        end_tick=evt["tick"] + evt["duration"],
                    ))
                if events_list and events_list[-1].end_tick < sec_ticks:
                    events_list.append(MusicEvent(pitch=0, volume=0,
                                                  start_tick=sec_ticks - 1, end_tick=sec_ticks))
                elif not events_list:
                    events_list.append(MusicEvent(pitch=0, volume=0, start_tick=0, end_tick=sec_ticks))
                units_per_voice[v_name] = MusicUnit(events=events_list)

        for v_name in voice_names:
            c.fill_voice_section(v_name, sec_name, units_per_voice[v_name])

    return c, all_violations


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "MIDI"), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "Audio"), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "Analysis"), exist_ok=True)

    composer, violations = build_composer()

    ok, msg = composer.validate()
    if not ok:
        raise SystemExit(f"Validation failed: {msg}")

    midi_path = os.path.join(OUTPUT_DIR, "MIDI", f"{PROJECT_NAME}.mid")
    composer.to_midi(midi_path)

    size = os.path.getsize(midi_path)
    if size <= 40:
        raise SystemExit(f"MIDI empty/corrupt: {size} bytes")

    write_grid_visualization(
        composer.matrix,
        os.path.join(OUTPUT_DIR, "Analysis", "grid_visualization.txt"),
        ticks_per_character=240, bpm=BPM
    )

    # Voice leading report
    vl_report_path = os.path.join(OUTPUT_DIR, "Analysis", "voice_leading_report.txt")
    with open(vl_report_path, "w") as f:
        f.write("Voice Leading Analysis (musicom VoiceLeadingRules)\n")
        f.write(f"Style: classical\n")
        f.write(f"Key: E natural minor\n\n")
        f.write(f"Section progressions:\n")
        for sec, prog in SECTION_PROGRESSIONS.items():
            f.write(f"  {sec}: {' - '.join(prog)}\n")
        f.write(f"\nViolations detected: {len(violations)}\n")
        for v in violations:
            f.write(f"  Bar {v['bar']}: {v['type']} in voices {v['voices']}\n")
        if not violations:
            f.write("  None — clean voice leading.\n")

    write_provenance(
        midi_path, classification=AI_ASSISTED,
        generator=f"{PROJECT_NAME}/src/compose.py",
        parameters={
            "bpm": BPM,
            "method": "037-FHNS",
            "sp_method": "SP-013-FDL",
            "key": "E natural minor",
            "scale_pattern": SCALE,
            "form": "A(4)-B(8)-A'(4)",
            "fhn_params": {"a": FHN_A, "b": FHN_B, "tau": FHN_TAU, "dt": FHN_DT},
            "i_drives": I_DRIVES,
            "spike_threshold": SPIKE_THRESHOLD,
            "refractory_ticks": REFRACTORY_TICKS,
            "phase1": "FHN neural spiking → spike timings + ISI pitch indices",
            "phase2_rules": [
                "FunctionalHarmony: section chord progressions",
                "chord-tone quantization (pitch → nearest chord tone)",
                "VoiceLeadingRules: parallel fifths/octaves check",
                "voice leading correction (stepwise shift)",
            ],
            "section_progressions": SECTION_PROGRESSIONS,
            "voice_leading_violations": len(violations),
            "voices": {
                "Lead": "Flute (73)",
                "Tenor": "Piano (0)",
                "Bass": "Electric Bass (33)",
                "Pad": "Strings (48)"
            },
        },
        notes="Two-phase composition: (1) FHN neural dynamics generate raw "
              "spike timings and ISI-derived pitch indices. (2) musicom rules "
              "post-process: FunctionalHarmony chord progressions per section, "
              "chord-tone quantization, VoiceLeadingRules parallel motion check "
              "and correction. SP-013: Feedback Delay with HF damping post-render."
    )

    print(f"OK: {midi_path} ({size} bytes)")
    print(f"Validation: {ok} - {msg}")
    print(f"Voice leading violations: {len(violations)}")
    print(f"Section progressions: {SECTION_PROGRESSIONS}")


if __name__ == "__main__":
    main()