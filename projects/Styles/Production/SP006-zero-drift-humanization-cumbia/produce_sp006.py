# -*- coding: utf-8 -*-
"""
SP-006 - Zero-Drift Humanization production pass.

Source: /opt/data/projects/Styles/Latin/cumbia-daily-2026-06-22/composition.mid
        (Colombian Cumbia, D Dorian, 100 BPM, 2/4, 2-bar loop = 1920 ticks)

Method (methods_db SP-006): "Zero-Drift Humanization" - micro-timing jitter +
velocity humanization applied on top of a perfectly quantized groove, while
preserving strict absolute-track alignment (zero cumulative drift).

Production decisions (this run):
  * Loop the 2-bar source groove 4x (7680 ticks = 16 beats = 9.6 s at 100 BPM)
    so the study is a listenable length; each repetition re-rolls per-voice
    micro-timing/velocity from the same seeded RNG stream (deterministic).
  * Honor the source README instrumentation: Bombo Bass -> program 34
    (Acoustic Bass). Source MIDI omitted program changes; documented intent
    restored here. Drum voices (ch 9) keep GM percussion pitch map.
  * Post-render peak normalization to 0.89 (-1 dBFS) on full mix + stems.

Pipeline:
  1. Parse source MIDI with mido (ANALYSIS ONLY - no MIDI authoring here).
  2. Build a UnitMatrix via the canonical UnitMatrixComposer (5 voices x 1
     section, one cell per voice containing ALL loop repetitions).
  3. Per-voice humanization profiles (seeded RNG, reproducible):
       Bombo bass : sigma_t=2 ticks, vel sigma=8   (drummer, keeps downbeat)
       Llamador   : sigma_t=1.5 ticks, vel sigma=5 (metronomic pulse, alive)
       Alegre     : sigma_t=3 ticks, vel sigma=10  (syncopated conga accents)
       Maraca     : sigma_t=2 ticks, vel sigma=6   (continuous shaker lift)
       Accordion  : sigma_t=5 ticks, vel sigma=7, duration x0.97 (lead rubato)
     Timing jitter is forward-clamped (no negative deltas, no backtracking).
  4. validate() zero-drift gate MUST pass, then to_midi() export.
  5. Grid visualization (high-contrast, ticks_per_character=120 = 16th grid).
  6. RenderAudio: full mix WAV + Opus OGG + per-track stems
     (RenderPipeline, FluidSynth CLI, TimGM6mb.sf2), peak-normalized to 0.89.
  7. Verify: silence ratio, per-second RMS, zero-drift track-length readback
     (meta track excluded), humanization DNA stats.

Usage:
  /opt/data/micromamba/envs/musicom/bin/python produce_sp006.py <out_dir>
"""

import hashlib
import json
import os
import subprocess
import sys
import wave
from pathlib import Path

import mido
import numpy as np

SR = 44100
SF = "/opt/data/micromamba/envs/musicom/lib/python3.11/site-packages/pretty_midi/TimGM6mb.sf2"
FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
FFMPEG = "/usr/bin/ffmpeg"

SOURCE_MIDI = "/opt/data/projects/Styles/Latin/cumbia-daily-2026-06-22/composition.mid"
LOOP_TICKS = 1920      # 2 bars of 2/4 at 480 ticks/beat
LOOPS = 4              # loop repetitions for a listenable artifact
TRACK_TICKS = LOOP_TICKS * LOOPS
BPM = 100

# Voice design: name, program (GM, honored from source README), channel,
# sigma_t (ticks), vel_sigma, duration (scale, jitter)
VOICES = [
    {"name": "Bombo Bass",  "program": 34, "channel": 0, "sigma_t": 2.0,  "vel_sigma": 8.0,  "dur": (1.0, 0.0)},
    {"name": "Llamador",    "program": 0,  "channel": 9, "sigma_t": 1.5,  "vel_sigma": 5.0,  "dur": (1.0, 0.0)},
    {"name": "Alegre",      "program": 0,  "channel": 9, "sigma_t": 3.0,  "vel_sigma": 10.0, "dur": (1.0, 0.0)},
    {"name": "Maraca",      "program": 0,  "channel": 9, "sigma_t": 2.0,  "vel_sigma": 6.0,  "dur": (1.0, 0.0)},
    {"name": "Accordion",   "program": 22, "channel": 4, "sigma_t": 5.0,  "vel_sigma": 7.0,  "dur": (0.97, 0.008)},
]

SEED = 260825


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_track(mid: mido.MidiFile, track) -> list:
    """Return (program, channel, notes) with notes = [(abs_start, abs_end, pitch, vel)].

    Handles same-pitch overlapping note_ons (velocity-layered double strikes)
    via a per-pitch stack: note_off pops the oldest active entry for that
    pitch, so layered pairs are NOT collapsed/lost.
    """
    program, channel = 0, 0
    for m in track:
        if m.type == "program_change":
            program, channel = m.program, m.channel
    notes = []
    abstick = 0
    active = {}
    for m in track:
        abstick += m.time
        if m.type == "note_on" and m.velocity > 0:
            active.setdefault(m.note, []).append((abstick, m.velocity))
        elif m.type == "note_off" or (m.type == "note_on" and m.velocity == 0):
            if m.note in active and active[m.note]:
                s, v = active[m.note].pop(0)  # FIFO: oldest layer first
                notes.append((s, abstick, m.note, v))
    return program, channel, sorted(notes)


def humanize_notes(notes: list, sigma_t: float, vel_sigma: float,
                   dur: tuple, rng: np.random.Generator,
                   base: int, span: int) -> tuple:
    """Apply forward-clamped timing jitter + velocity humanization.

    Args:
        notes: [(rel_start, rel_end, pitch, vel)] relative to loop start
        base: absolute tick offset of this loop repetition
        span: loop length in ticks (clamp window = [base, base+span])

    Returns (events, shifts, stats); events have absolute ticks in
    [base, base+span], strictly non-backtracking per track
    (min_start = prior event start, preserving overlapping/layered notes).
    shifts = per-note timing deviation in ticks.
    """
    out = []
    prev_start = base
    shifts = []
    for (s, e, p, v) in notes:
        jitter = int(round(rng.normal(0.0, sigma_t)))
        ns = max(prev_start, base + s + jitter)
        dc = dur[0] + float(rng.normal(0.0, dur[1]))
        ne = ns + max(30, int((e - s) * dc))
        if ne > base + span:
            ne = base + span
            ns = min(ns, ne - 30)
        nv = int(np.clip(v + rng.normal(0.0, vel_sigma), 20, 127))
        out.append((ns, ne, p, nv))
        shifts.append(ns - (base + s))
        prev_start = ns
    stats = {
        "mean_abs_shift_ticks": float(np.mean(np.abs(shifts))) if shifts else 0.0,
        "max_abs_shift_ticks": float(np.max(np.abs(shifts))) if shifts else 0.0,
        "n_notes": len(out),
    }
    return out, shifts, stats


def normalize_wav(path: str, target_peak: float = 0.89) -> float:
    """Peak-normalize a 16-bit WAV in place. Returns applied gain."""
    with wave.open(path, "rb") as w:
        sr = w.getframerate()
        nch = w.getnchannels()
        sw = w.getsampwidth()
        n = w.getnframes()
        raw = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768.0
    peak = float(np.max(np.abs(raw))) if len(raw) else 0.0
    if peak <= 0.0:
        return 1.0
    gain = target_peak / peak
    scaled = np.clip(raw * gain, -1.0, 1.0)
    data = (scaled * 32767.0).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(nch)
        w.setsampwidth(sw)
        w.setframerate(sr)
        w.writeframes(data.tobytes())
    return float(gain)


def analyze_wav(path: str) -> dict:
    """Silence ratio + per-second RMS map + peak. Accepts mono or stereo WAV."""
    with wave.open(path, "rb") as w:
        sr = w.getframerate()
        nch = w.getnchannels()
        n = w.getnframes()
        raw = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768.0
    if nch == 2:
        raw = raw.reshape(-1, 2).mean(axis=1)
    dur = len(raw) / sr
    peak = float(np.max(np.abs(raw))) if len(raw) else 0.0
    silence = float(np.sum(np.abs(raw) < 0.001) / len(raw)) if len(raw) else 1.0
    rms_map = []
    for sec in range(int(dur) + 1):
        seg = raw[sec * sr:(sec + 1) * sr]
        rms_map.append(round(float(np.sqrt(np.mean(seg ** 2))) if len(seg) else 0.0, 4))
    return {"sample_rate": sr, "channels": nch, "duration_s": round(dur, 3),
            "peak": round(peak, 4), "silence_ratio": round(silence, 4),
            "rms_per_second": rms_map}


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main(out_dir: str) -> int:
    root = Path(out_dir)
    for sub in ("MIDI", "Audio", "Audio/stems", "Analysis"):
        (root / sub).mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(SEED)

    # 1. parse source
    mid = mido.MidiFile(SOURCE_MIDI)
    assert mid.ticks_per_beat == 480, "unexpected tpb"
    parsed = []
    for track in mid.tracks:
        prog, ch, notes = parse_track(mid, track)
        if notes:
            parsed.append((prog, ch, notes))
    assert len(parsed) == len(VOICES), f"voice count mismatch: {len(parsed)} vs {len(VOICES)}"
    src_sha = sha256_file(SOURCE_MIDI)

    # 2-4. build matrix + humanize (looped) + export via canonical composer
    from structures import MusicUnit, MusicEvent
    from workflows.unitmatrix_composer import UnitMatrixComposer
    from visualization.grid import write_grid_visualization

    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=480, beats_per_bar=4)
    composer.create_matrix(num_voices=len(VOICES), num_sections=1)
    for v in VOICES:
        composer.add_voice(v["name"], program=v["program"], channel=v["channel"])
    composer.add_section("Loop", bars=1)

    hz_stats = {}
    for i, (prog, ch, notes) in enumerate(parsed):
        v = VOICES[i]
        all_events = []
        all_shifts = []
        n_total = 0
        for rep in range(LOOPS):
            base = rep * LOOP_TICKS
            hz, shifts, stats = humanize_notes(notes, v["sigma_t"], v["vel_sigma"], v["dur"],
                                               rng, base, LOOP_TICKS)
            all_events.extend(hz)
            all_shifts.extend([abs(x) for x in shifts])
            n_total += stats["n_notes"]
        evts = [MusicEvent(pitch=p, volume=vel, start_tick=s, end_tick=e)
                for (s, e, p, vel) in all_events]
        # force exact row length TRACK_TICKS (zero-drift invariant)
        max_end = max((e for (s, e, p, vel) in all_events), default=0)
        if max_end < TRACK_TICKS:
            evts.append(MusicEvent(pitch=0, volume=0,
                                   start_tick=TRACK_TICKS - 10,
                                   end_tick=TRACK_TICKS))
        composer.set_unit(i, 0, MusicUnit(events=evts))
        hz_stats[v["name"]] = {
            "sigma_t": v["sigma_t"], "vel_sigma": v["vel_sigma"],
            "n_notes_total": n_total, "loops": LOOPS,
            "mean_abs_shift_ticks": round(float(np.mean(all_shifts)), 2) if all_shifts else 0.0,
            "max_abs_shift_ticks": int(max(all_shifts)) if all_shifts else 0,
        }

    ok, msg = composer.validate()
    print("VALIDATE:", ok, msg)
    assert ok, f"zero-drift gate failed: {msg}"

    midi_path = root / "MIDI" / "SP006-cumbia-zero-drift-humanized.mid"
    composer.to_midi(str(midi_path))
    assert os.path.getsize(midi_path) > 40, "empty MIDI"

    # grid visualization
    grid_path = root / "Analysis" / "grid_visualization.txt"
    write_grid_visualization(composer.matrix, str(grid_path),
                             ticks_per_character=120,
                             voice_names=[v["name"] for v in VOICES],
                             bpm=BPM, mode="D Dorian cumbia 2/4 x4")

    # 6. render full mix + ogg + stems
    from sound.render import RenderPipeline
    pipeline = RenderPipeline(fluidsynth_bin=FLUID, soundfont_path=SF,
                              sample_rate=SR, gain=1.2)
    wav_path = root / "Audio" / "SP006-cumbia-zero-drift-humanized.wav"
    pipeline.render_to_wav(str(midi_path), str(wav_path), soundfont=SF)
    wav_gain = normalize_wav(str(wav_path), 0.89)

    stems_dir = root / "Audio" / "stems"
    stems = pipeline.render_stems(str(midi_path), str(stems_dir),
                                  soundfont=SF, format="wav")
    stem_gains = {}
    for name, p in stems.items():
        stem_gains[name] = normalize_wav(p, 0.89)

    # ogg from normalized mix
    ogg_path = root / "Audio" / "SP006-cumbia-zero-drift-humanized.ogg"
    subprocess.run([FFMPEG, "-y", "-loglevel", "error",
                    "-i", str(wav_path),
                    "-codec:a", "libopus", "-application", "voip", "-b:a", "48k",
                    str(ogg_path)], check=True)

    # 7. verification
    mix_stats = analyze_wav(str(wav_path))
    stem_stats = {}
    for name, p in stems.items():
        stem_stats[name] = analyze_wav(p)

    # zero-drift readback check (skip meta-only track 0)
    back = mido.MidiFile(str(midi_path))
    lengths = []
    for tr in back.tracks:
        has_notes = any(m.type in ("note_on", "note_off") for m in tr)
        if not has_notes:
            continue
        lengths.append(sum(m.time for m in tr))
    drift_ok = len(set(lengths)) == 1

    human_dna = {
        "seed": SEED,
        "loops": LOOPS,
        "per_voice": hz_stats,
        "velocity_before": {v["name"]: [vv for (s, e, p, vv) in parsed[i][2]]
                            for i, v in enumerate(VOICES)},
        "zero_drift_readback": {"track_lengths": lengths, "all_equal": drift_ok},
    }
    with open(root / "Analysis" / "humanization_dna.json", "w") as f:
        json.dump(human_dna, f, indent=2)
    with open(root / "Analysis" / "render_stats.json", "w") as f:
        json.dump({"full_mix": mix_stats, "stems": stem_stats,
                   "normalization": {"full_mix_gain": wav_gain,
                                     "stem_gains": stem_gains}}, f, indent=2)

    prov = {
        "job": "production-pass",
        "timestamp": "2026-08-25T00:00:00Z",
        "source_midi": SOURCE_MIDI,
        "source_midi_sha256": src_sha,
        "method": "SP-006",
        "production_method": "SP-006",
        "method_name": "Zero-Drift Humanization",
        "method_source": "methods_db.md#SP-006",
        "humanization": {k: v for k, v in human_dna.items()
                         if k != "velocity_before" and isinstance(v, dict)},
        "render": {
            "engine": "FluidSynth CLI",
            "soundfont": SF,
            "sample_rate": SR,
            "gain": 1.2,
            "ogg": "libopus voip 48k",
            "peak_norm_db": -1.0,
            "gm_programs": {v["name"]: v["program"] for v in VOICES},
            "source_documented_instruments": {"Bombo Bass": 34, "Llamador": 45,
                                              "Alegre": 63, "Maraca": 70,
                                              "Accordion": 22},
        },
        "artifacts": [
            "MIDI/SP006-cumbia-zero-drift-humanized.mid",
            "Audio/SP006-cumbia-zero-drift-humanized.wav",
            "Audio/SP006-cumbia-zero-drift-humanized.ogg",
            "Analysis/grid_visualization.txt",
            "Analysis/humanization_dna.json",
            "Analysis/render_stats.json",
            "README.md",
        ],
        "assistance": "AI_ASSISTED",
    }
    with open(root / "provenance.json", "w") as f:
        json.dump(prov, f, indent=2)

    print("MIX_STATS:", json.dumps(mix_stats))
    print("STEMS:", json.dumps({k: v["silence_ratio"] for k, v in stem_stats.items()}))
    print("STEM_GAINS:", json.dumps({k: round(v, 4) for k, v in stem_gains.items()}))
    print("ZERO_DRIFT:", drift_ok, lengths)
    print("DONE")
    return 0


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else \
        "/opt/data/projects/Styles/Production/SP006-zero-drift-humanization-cumbia"
    raise SystemExit(main(out))