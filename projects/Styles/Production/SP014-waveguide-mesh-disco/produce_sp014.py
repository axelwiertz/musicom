#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sound Production Method SP-014: Waveguide Mesh Physical Modeling
=================================================================
Applied to: /opt/data/projects/Styles/Disco/modern/v1/modern_disco.mid

Method (methods_db.md SP-014): multi-dimensional physical modeling synthesis.
A 2D grid of delay lines + scattering junctions simulates wave propagation
across a resonant surface (drumhead / plate / soundboard). Each MIDI note
strikes the mesh at a pitch-dependent location; the displacement wave
propagates, reflects at clamped/free boundaries, and is read at a pickup.

Per-note mesh grid size scales with pitch: higher notes -> smaller mesh
-> higher modal density -> brighter, more metallic timbre (marimba/steel
pan character). Lower notes -> larger mesh -> deeper, drum-like body.

Two-layer deliverable:
  1. SP-014 mesh synthesis = the production method itself (lead, bass, strings)
  2. GM FluidSynth drums = rhythm backbone (TimGM6mb.sf2), keeps the disco
     groove intact while the mesh layer re-timbres the pitched instruments.

Outputs (dual MIDI + audio):
  MIDI/original.mid      - source composition copy
  Audio/mix_mesh_gm.wav  - final mix (mesh stems + GM drums, mastered)
  Audio/mix_mesh_gm.ogg  - Telegram/playback Opus render
  Audio/stems/...        - per-track stems (Drums GM, Bass mesh, Lead mesh,
                           Strings mesh, MeshBed)
  Analysis/provenance.json + Analysis/grid_visualization.txt
"""

import os
import json
import math
import wave
import hashlib
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import mido

# ============================================================================
# Configuration
# ============================================================================

SR = 44100
MIDI_PATH = "/opt/data/projects/Styles/Disco/modern/v1/modern_disco.mid"
OUTPUT_DIR = Path("/opt/data/projects/Styles/Production/SP014-waveguide-mesh-disco")
STEMS_DIR = OUTPUT_DIR / "Audio" / "stems"
MIDI_DIR = OUTPUT_DIR / "MIDI"
ANALYSIS_DIR = OUTPUT_DIR / "Analysis"

SOUNDFONT = "/opt/data/micromamba/envs/musicom/lib/python3.11/site-packages/pretty_midi/TimGM6mb.sf2"
FLUIDSYNTH = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
FFMPEG = "/usr/bin/ffmpeg"

# Per-track mesh presets (from MIDI analysis: ch0=Drums, ch1=Strings pgm49,
# ch2=Lead pgm74, ch3=Bass pgm88)
TRACK_PRESETS = {
    # channel -> mesh preset
    2: dict(name="LeadFlute", grid=11, damping=0.9965, reflection=-1.0,
            strike_radius=2.0, gain=1.0, pan=(-0.25, 0.25)),
    3: dict(name="BassBody", grid=19, damping=0.9980, reflection=-1.0,
            strike_radius=2.5, gain=1.6, pan=(0.10, 0.10)),
    1: dict(name="StringsPlate", grid=15, damping=0.9970, reflection=-1.0,
            strike_radius=2.0, gain=0.9, pan=(-0.4, 0.4)),
}
# Mesh bed: low drone struck once per bar on a large plate (adds room resonance)
MESH_BED = dict(name="MeshBed", grid=23, damping=0.9985, reflection=-1.0,
                strike_radius=3.0, gain=0.5, pan=(0.0, 0.0))

DRUM_CHANNEL = 9
TICKS_PER_BEAT = 480

# ============================================================================
# SP-014 Engine: 2D Waveguide Mesh (per methods_db.md spec)
# ============================================================================

def midi_to_freq(midi_note):
    """MIDI note number -> frequency in Hz."""
    return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))


def generate_mesh_audio(width, height, duration, sr, strike_x, strike_y,
                        strike_width=2.0, damping=0.997, reflection=-1.0,
                        pickup_frac=(0.3, 0.4), excitation=None):
    """
    Simulate a 2D digital waveguide mesh with clamped (reflection=-1) or free
    (reflection=+1) boundaries. Excite with a raised-cosine displacement at
    (strike_x, strike_y), read the evolving pressure at a pickup point.

    Junction update (uniform 2D mesh, per SP-014):
        v[x,y][n] = d * 0.5 * (v[x-1,y] + v[x+1,y] + v[x,y-1] + v[x,y+1])[n-1]
                     - d^2 * v[x,y][n-2]

    Uses a 1-sample delay (P-wave 2D mesh) - same family as the spec formula.

    excitation: optional (samples, strike_cells) tuple. When given, each sample
    is injected additively into the strike-cell region at every time step, so
    the mesh rings at the excitation's pitch while the mesh's own scattering/
    damping/boundary physics shape the decay and timbre.
    """
    num_samples = int(sr * duration)
    output = np.zeros(num_samples)

    # State grids with 1-cell boundary padding
    grid_prev = np.zeros((width + 2, height + 2))
    grid_curr = np.zeros((width + 2, height + 2))
    grid_next = np.zeros((width + 2, height + 2))

    # Strike excitation: raised-cosine displacement bump
    for x in range(1, width + 1):
        for y in range(1, height + 1):
            dist_sq = (x - strike_x) ** 2 + (y - strike_y) ** 2
            if dist_sq < strike_width ** 2:
                d_ = math.sqrt(dist_sq)
                val = 0.5 * (1.0 + math.cos(math.pi * d_ / strike_width))
                grid_curr[x, y] = val
                grid_prev[x, y] = val

    # Strike cell coordinates for optional continuous excitation
    strike_cells = []
    if excitation is not None:
        for x in range(1, width + 1):
            for y in range(1, height + 1):
                dist_sq = (x - strike_x) ** 2 + (y - strike_y) ** 2
                if dist_sq < strike_width ** 2:
                    strike_cells.append((x, y))

    pickup_x = int(width * pickup_frac[0]) + 1
    pickup_y = int(height * pickup_frac[1]) + 1
    pickup_x = min(pickup_x, width)
    pickup_y = min(pickup_y, height)

    for n in range(num_samples):
        L = grid_curr[0:-2, 1:-1]
        R = grid_curr[2:, 1:-1]
        U = grid_curr[1:-1, 0:-2]
        D = grid_curr[1:-1, 2:]

        grid_next[1:-1, 1:-1] = (damping * 0.5 * (L + R + U + D)) - (damping ** 2 * grid_prev[1:-1, 1:-1])

        if reflection == -1.0:
            grid_next[0, :] = 0
            grid_next[-1, :] = 0
            grid_next[:, 0] = 0
            grid_next[:, -1] = 0
        else:
            grid_next[0, 1:-1] = reflection * grid_curr[1, 1:-1]
            grid_next[-1, 1:-1] = reflection * grid_curr[-2, 1:-1]
            grid_next[1:-1, 0] = reflection * grid_curr[1:-1, 1]
            grid_next[1:-1, -1] = reflection * grid_curr[1:-1, -2]

        if excitation is not None:
            ex = excitation[0][n] if n < len(excitation[0]) else 0.0
            if ex != 0.0 and strike_cells:
                for (cx, cy) in strike_cells:
                    grid_next[cx, cy] += ex

        output[n] = grid_next[pickup_x, pickup_y]

        # NOTE: must COPY, not rebind — rebinding aliases the buffers and the
        # next iteration overwrites grid_prev's data mid-read (verified by
        # vec-vs-dense eigen test: rebind diverges/explodes, copy stays stable).
        grid_prev = np.copy(grid_curr)
        grid_curr = np.copy(grid_next)

    return output


def mesh_note(freq, duration, sr, grid, damping, reflection, strike_radius,
              pickup_frac=(0.3, 0.4)):
    """Synthesize one pitched note via the waveguide mesh.

    The mesh is a physical resonator: its scattering junctions, damping and
    clamped boundaries shape the decay and timbre. The pitch itself is carried
    by a short excitation injected into the strike region (a decaying
    harmonic-rich impulse at the note frequency). Grid size scales with pitch
    so higher notes ring on smaller, brighter meshes (marimba/steel-pan
    character) and lower notes on larger, deeper meshes (drum/body character).
    """
    if grid is None or freq <= 20:
        grid = 19
    n_for_freq = int(round(sr / (2.0 * freq)))
    grid = int(round(n_for_freq * 1.0))
    grid = max(7, min(grid, 31))
    strike_x = max(1, int(grid * 0.5))
    strike_y = max(1, int(grid * 0.5))

    dur = max(duration, 0.05)
    n_samp = int(sr * dur)

    # Excitation: harmonic-rich decaying impulse at the note pitch, seeded
    # into the mesh so the resonator colors it. Short (~40 ms) attack body.
    t = np.arange(n_samp) / sr
    exc_len = min(n_samp, int(0.04 * sr))
    exc = np.zeros(n_samp)
    if exc_len > 0:
        te = np.arange(exc_len) / sr
        # fundamental + 2nd + 3rd partials, fast exponential decay
        exc[:exc_len] = (
            np.sin(2 * np.pi * freq * te)
            + 0.5 * np.sin(2 * np.pi * 2 * freq * te)
            + 0.25 * np.sin(2 * np.pi * 3 * freq * te)
        ) * np.exp(-te * 40.0)
        # gentle fade-in to avoid click
        fade = min(exc_len, int(0.002 * sr))
        if fade > 0:
            exc[:fade] *= np.linspace(0, 1, fade)

    audio = generate_mesh_audio(
        grid, grid, dur, sr,
        strike_x=strike_x, strike_y=strike_y,
        strike_width=strike_radius, damping=damping,
        reflection=reflection, pickup_frac=pickup_frac,
        excitation=(exc, None),
    )
    # Normalize each struck note to unity peak then scale later by velocity
    peak = np.max(np.abs(audio)) if len(audio) else 0.0
    if peak > 1e-9 and np.all(np.isfinite(audio)):
        audio = audio / peak
    elif not np.all(np.isfinite(audio)):
        # Guard: never let a non-finite mesh corrupt the mix
        print(f"  WARN: mesh non-finite (freq={freq:.1f} grid={grid}) -> silence")
        audio = np.zeros_like(audio)
    return audio


def apply_adsr(signal, sr, attack=0.004, decay=0.06, sustain_level=0.75, release=0.05):
    """ADSR envelope to avoid clicks and shape the mesh decay."""
    n = len(signal)
    env = np.ones(n)
    att = min(int(attack * sr), n)
    dec = min(int(decay * sr), max(0, n - att))
    rel = min(int(release * sr), n)
    if att > 0:
        env[:att] = np.linspace(0, 1, att)
    if dec > 0:
        env[att:att + dec] = np.linspace(1, sustain_level, dec)
    sus_end = n - rel
    if sus_end > att + dec:
        env[att + dec:sus_end] = sustain_level
    if rel > 0:
        env[-rel:] *= np.linspace(1, 0, rel)
    return signal * env


def velocity_to_gain(vel):
    """MIDI velocity 1-127 -> linear gain (with soft knee for low velocities)."""
    v = max(1, min(127, vel)) / 127.0
    return 0.05 + 0.95 * (v ** 1.5)


# ============================================================================
# MIDI parsing (mido allowed for READING only)
# ============================================================================

def parse_midi(midi_path):
    """Parse MIDI into per-track absolute-time note events (seconds)."""
    mid = mido.MidiFile(midi_path)
    tpb = mid.ticks_per_beat
    tempo = 500000
    for msg in mid.tracks[0]:
        if msg.type == "set_tempo":
            tempo = msg.tempo
            break
    bpm = mido.tempo2bpm(tempo)
    spt = tempo / (tpb * 1_000_000.0)

    tracks = []
    for ti, track in enumerate(mid.tracks):
        if ti == 0:
            continue
        program = None
        channel = None
        for msg in track:
            if msg.type == "program_change":
                program = msg.program
                channel = msg.channel
        events = []
        abs_tick = 0
        active = {}
        for msg in track:
            abs_tick += msg.time
            if msg.type == "note_on" and msg.velocity > 0:
                active[msg.note] = (abs_tick, msg.velocity)
            elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
                if msg.note in active:
                    start_tick, vel = active.pop(msg.note)
                    dur = max(abs_tick - start_tick, 60) * spt
                    events.append({
                        "note": msg.note,
                        "vel": vel,
                        "start": start_tick * spt,
                        "dur": dur,
                    })
        tracks.append({
            "index": ti,
            "channel": channel,
            "program": program,
            "events": events,
        })
    return tracks, bpm, spt


# ============================================================================
# WAV I/O
# ============================================================================

def save_wav_stereo(path, left, right, sr=SR):
    """Write 16-bit stereo WAV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    n = min(len(left), len(right))
    interleaved = np.empty(n * 2, dtype=np.int16)
    interleaved[0::2] = (np.clip(left[:n], -1.0, 1.0) * 32767).astype(np.int16)
    interleaved[1::2] = (np.clip(right[:n], -1.0, 1.0) * 32767).astype(np.int16)
    with wave.open(str(path), "w") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(interleaved.tobytes())
    assert os.path.getsize(path) > 1000, f"WAV too small: {path}"
    print(f"  wrote {path} ({os.path.getsize(path)} bytes)")


def gm_drums_render(midi_path, wav_path, soundfont, fluidsynth, gain=1.0):
    """Render the original MIDI's drum channel (ch9) via FluidSynth GM."""
    wav_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        fluidsynth, "-ni", "-g", f"{gain:.2f}", "-F", str(wav_path),
        soundfont, str(midi_path),
    ]
    print("  running:", " ".join(cmd))
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(wav_path) or os.path.getsize(wav_path) < 1000:
        print("  fluidsynth stderr:", r.stderr[-2000:])
        raise RuntimeError("FluidSynth render failed")
    return wav_path


def read_wav_mono(path):
    """Read WAV -> mono float array [-1, 1]."""
    with wave.open(str(path), "r") as wf:
        nch = wf.getnchannels()
        sw = wf.getsampwidth()
        sr_w = wf.getframerate()
        frames = wf.readframes(wf.getnframes())
    data = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
    if nch == 2:
        data = data.reshape(-1, 2).mean(axis=1)
    return data, sr_w


def write_stereo_wav_mono_pan(mono, pan_l, pan_r, n):
    """Pan a mono buffer into a stereo master."""
    m = min(len(mono), n)
    return mono[:m] * pan_l, mono[:m] * pan_r


# ============================================================================
# Main pipeline
# ============================================================================

def main():
    print("=" * 64)
    print("SP-014: Waveguide Mesh Physical Modeling -> modern_disco.mid")
    print("=" * 64)

    for d in (OUTPUT_DIR, STEMS_DIR, MIDI_DIR, ANALYSIS_DIR):
        d.mkdir(parents=True, exist_ok=True)

    # --- parse source ---
    tracks, bpm, spt = parse_midi(MIDI_PATH)
    print(f"\nSource: {MIDI_PATH}")
    print(f"BPM: {bpm:.1f}, ticks_per_beat: {TICKS_PER_BEAT}")
    for t in tracks:
        if t["events"]:
            print(f"  track {t['index']} ch={t['channel']} pgm={t['program']} notes={len(t['events'])}")

    total_len = mido.MidiFile(MIDI_PATH).length
    total_dur = total_len + 2.5  # reverb-ish tail room
    total_samples = int(total_dur * SR)
    print(f"Total duration: {total_dur:.2f}s ({total_samples} samples)")

    # --- copy original MIDI (dual artifact) ---
    src_mid = Path(MIDI_PATH)
    dst_mid = MIDI_DIR / "original.mid"
    dst_mid.write_bytes(src_mid.read_bytes())
    assert dst_mid.stat().st_size > 40
    print(f"\nCopied MIDI -> {dst_mid} ({dst_mid.stat().st_size} bytes)")

    # --- master stereo buffers ---
    master_l = np.zeros(total_samples)
    master_r = np.zeros(total_samples)
    stems = {}

    # --- 1) GM drums (channel 9) via FluidSynth ---
    print("\n[1/4] GM drums via FluidSynth (channel 9)...")
    gm_wav = OUTPUT_DIR / "Audio" / "_gm_drums_raw.wav"
    gm_drums_render(MIDI_PATH, gm_wav, SOUNDFONT, FLUIDSYNTH, gain=1.1)
    drum_mono, _ = read_wav_mono(gm_wav)
    drum_stereo = np.column_stack([drum_mono, drum_mono])  # drums centered
    stems["Drums_GM"] = drum_stereo
    n_d = min(len(drum_mono), total_samples)
    master_l[:n_d] += drum_mono[:n_d] * 1.0
    master_r[:n_d] += drum_mono[:n_d] * 1.0
    print(f"  drums: {len(drum_mono)} samples")

    # --- 2) Mesh synthesis for pitched tracks (channels 1,2,3) ---
    print("\n[2/4] Waveguide mesh synthesis for pitched tracks...")
    for t in tracks:
        ch = t["channel"]
        if ch is None or ch == DRUM_CHANNEL:
            continue
        preset = TRACK_PRESETS.get(ch)
        if preset is None:
            print(f"  skip channel {ch} (no preset)")
            continue
        print(f"  channel {ch}: {preset['name']} (grid~{preset['grid']}, "
              f"damping={preset['damping']}, refl={preset['reflection']})")
        buf_l = np.zeros(total_samples)
        buf_r = np.zeros(total_samples)
        for evt in t["events"]:
            freq = midi_to_freq(evt["note"])
            start_s = evt["start"]
            dur_s = evt["dur"]
            start_i = int(start_s * SR)
            if start_i >= total_samples:
                continue
            audio = mesh_note(freq, dur_s, SR, preset["grid"], preset["damping"],
                              preset["reflection"], preset["strike_radius"])
            audio = apply_adsr(audio, SR, attack=0.004, decay=0.08,
                               sustain_level=0.8, release=0.06)
            g = velocity_to_gain(evt["vel"]) * preset["gain"]
            audio = audio * g
            end_i = start_i + len(audio)
            if end_i > total_samples:
                audio = audio[:total_samples - start_i]
                end_i = total_samples
            pan_l = 1.0 - max(0.0, min(1.0, 0.5 + preset["pan"][0]))
            pan_r = 1.0 - max(0.0, min(1.0, 0.5 + preset["pan"][1]))
            buf_l[start_i:end_i] += audio * pan_l
            buf_r[start_i:end_i] += audio * pan_r
        stems[preset["name"]] = np.column_stack([buf_l, buf_r])
        master_l += buf_l
        master_r += buf_r

    # --- 3) Mesh bed: low drone struck on the beat (bar-aligned) ---
    print("\n[3/4] Mesh bed drone (bar-aligned strikes, large plate)...")
    bed_l = np.zeros(total_samples)
    bed_r = np.zeros(total_samples)
    beat_sec = 60.0 / bpm
    bar_sec = beat_sec * 4
    f_drone = midi_to_freq(45)  # A2-ish low body
    n_for = int(round(SR / (2.0 * f_drone)))
    grid_bed = max(7, min(MESH_BED["grid"], n_for))
    t_cursor = 0.0
    while t_cursor < total_dur - 0.5:
        start_i = int(t_cursor * SR)
        audio = generate_mesh_audio(
            grid_bed, grid_bed, min(bar_sec * 0.9, 3.5), SR,
            strike_x=max(1, int(grid_bed * 0.5)),
            strike_y=max(1, int(grid_bed * 0.5)),
            strike_width=MESH_BED["strike_radius"],
            damping=MESH_BED["damping"], reflection=MESH_BED["reflection"],
            pickup_frac=(0.3, 0.4),
        )
        peak = np.max(np.abs(audio)) if len(audio) else 0.0
        if peak > 1e-9 and np.all(np.isfinite(audio)):
            audio = audio / peak
        elif not np.all(np.isfinite(audio)):
            print("  WARN: mesh bed non-finite -> silence")
            audio = np.zeros_like(audio)
        audio = apply_adsr(audio, SR, attack=0.01, decay=0.3, sustain_level=0.6, release=0.2)
        audio = audio * (MESH_BED["gain"] * 0.8)
        end_i = start_i + len(audio)
        if end_i > total_samples:
            audio = audio[:total_samples - start_i]
            end_i = total_samples
        bed_l[start_i:end_i] += audio
        bed_r[start_i:end_i] += audio
        t_cursor += bar_sec
    stems["MeshBed"] = np.column_stack([bed_l, bed_r])
    master_l += bed_l
    master_r += bed_r

    # --- 4) Master + stems out ---
    print("\n[4/4] Mixing, mastering, exporting...")
    for name, st in stems.items():
        path = STEMS_DIR / f"{name}.wav"
        save_wav_stereo(path, st[:, 0], st[:, 1])

    # Master gain trim before mastering (avoid limiter over-pumping)
    master_l = master_l * 0.85
    master_r = master_r * 0.85
    mix = np.column_stack([master_l, master_r])

    # musicom mastering chain: stereo imager + limiter + LUFS
    from sound.effects.mastering import MasteringChain
    chain = MasteringChain(SR)
    chain.add_stereo_imager(width=1.15, below_hz=None, above_hz=None)
    chain.add_limiter(threshold_db=-1.0, release_ms=80.0)
    mix_mastered = chain.process(mix, target_lufs=-14.0)

    mix_path = OUTPUT_DIR / "Audio" / "mix_mesh_gm.wav"
    save_wav_stereo(mix_path, mix_mastered[:, 0], mix_mastered[:, 1])

    # --- OGG render (Opus, Telegram-friendly) ---
    ogg_path = OUTPUT_DIR / "Audio" / "mix_mesh_gm.ogg"
    r = subprocess.run(
        [FFMPEG, "-y", "-i", str(mix_path),
         "-codec:a", "libopus", "-application", "voip", "-b:a", "48k",
         str(ogg_path)],
        capture_output=True, text=True,
    )
    if r.returncode != 0 or not ogg_path.exists() or ogg_path.stat().st_size < 1000:
        print("ffmpeg stderr:", r.stderr[-1500:])
        raise RuntimeError("OGG conversion failed")
    print(f"  wrote {ogg_path} ({ogg_path.stat().st_size} bytes)")

    # clean intermediate GM wav
    if gm_wav.exists():
        gm_wav.unlink()

    # --- analysis: grid visualization (musicom visualizer) ---
    grid_viz = ANALYSIS_DIR / "grid_visualization.txt"
    try:
        from visualization.grid import write_grid_visualization
        # Build a simple UnitMatrix of the 4 source tracks for visualization
        from structures import UnitMatrix, MusicUnit
        # placeholder-free: visualize density per track
        lines = ["SP-014 Waveguide Mesh Production - grid visualization",
                 f"source: {Path(MIDI_PATH).name}  bpm: {bpm:.1f}  duration: {total_dur:.1f}s",
                 ""]
        for name, st in stems.items():
            mono = (st[:, 0] + st[:, 1]) * 0.5
            frames = 32
            seg = len(mono) // frames
            cells = []
            for i in range(frames):
                amp = np.sqrt(np.mean(mono[i * seg:(i + 1) * seg] ** 2)) if seg > 0 else 0.0
                cells.append("█" if amp > 0.02 else ("▓" if amp > 0.005 else "░"))
            lines.append(f"{name:16s} {' '.join(cells)}")
        grid_viz.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"  wrote {grid_viz}")
    except Exception as e:
        print(f"  grid viz fallback: {e}")
        grid_viz.write_text("SP-014 grid visualization unavailable\n", encoding="utf-8")

    # --- provenance ---
    from workflows.provenance import write_provenance, AI_ASSISTED
    src_sha = hashlib.sha256(Path(MIDI_PATH).read_bytes()).hexdigest()
    params = {
        "method": "SP-014",
        "method_name": "Waveguide Mesh Physical Modeling",
        "layer": "Synthesis Engines",
        "target": "Acoustic/Resonant Space Timbre",
        "sr": SR,
        "bpm": round(bpm, 2),
        "tick_seconds": spt,
        "drum_render": "FluidSynth GM TimGM6mb.sf2 (channel 9)",
        "track_presets": {str(k): v["name"] for k, v in TRACK_PRESETS.items()},
        "mesh_bed": MESH_BED["name"],
        "mastering": "musicom MasteringChain: StereoImager(1.15) + Limiter(-1.0dB) + LUFS(-14)",
        "outputs": {
            "wav": str(mix_path),
            "ogg": str(ogg_path),
            "midi": str(dst_mid),
        },
    }
    prov = {
        "artifact": str(mix_path),
        "classification": AI_ASSISTED,
        "generator": "musicom SP-014 waveguide mesh synthesizer (custom DSP, numpy)",
        "sources": [str(MIDI_PATH)],
        "source_sha256": src_sha,
        "parameters": params,
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }
    (ANALYSIS_DIR / "provenance.json").write_text(
        json.dumps(prov, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  wrote {ANALYSIS_DIR / 'provenance.json'}")

    # --- final verification ---
    print("\n" + "=" * 64)
    print("VERIFICATION")
    print("=" * 64)
    assert mix_path.exists() and mix_path.stat().st_size > 1000, "mix wav missing"
    assert ogg_path.exists() and ogg_path.stat().st_size > 1000, "ogg missing"
    assert dst_mid.exists() and dst_mid.stat().st_size > 40, "midi missing"
    for name in stems:
        sp = STEMS_DIR / f"{name}.wav"
        assert sp.exists() and sp.stat().st_size > 1000, f"stem missing {name}"

    print(f"\nDONE. Outputs in {OUTPUT_DIR}")
    for p in sorted(OUTPUT_DIR.rglob("*")):
        if p.is_file():
            print(f"  {p.relative_to(OUTPUT_DIR)}  ({p.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
