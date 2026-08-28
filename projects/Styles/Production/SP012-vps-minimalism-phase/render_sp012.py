#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SP-012 — Vector Phase Shaping (VPS) production pass on a Minimalism phase piece.

Source : 001-minimalism-phase-study — Steve Reich "Clapping Music"-style phase
         piece. 120 BPM, 8 sections x 3 bars, 48 s. Voices:
         MarimbaA/MarimbaB (GM 12, C-pent marimba cells, one phase-walks +1 beat
         per section), Pad (GM 49, sustained C triad), Bass (GM 33, C2 pedal),
         Perc (GM 0 / ch9, E(5,16) kick).
Method : SP-012 — Vector Phase Shaping (VPS) per methods_db.md:
         "Synthesis modifying phase distortion speed via dynamic vectors.
          Creates expressive sweeps and complex sidebands."

Core idea (same as SP012-vps-electric-blues, generalized to 5 voices)
---------------------------------------------------------------------
Each note's carrier phase is warped by a time-varying phase-distortion vector
K(t), itself swept by a slow LFO (dynamic vector) so spectral brightness
sweeps over time. A simultaneous phase-modulation (PM) modulator injects
inharmonic sidebands. Per-voice VPS parameters let the minimalism layers
keep their roles: marimba cells get sharp percussive PD, the pad gets a slow
wide brightness sweep, the bass gets deep stable K, the kick keeps a very
short percussive envelope.

The Reich phase process is preserved: identical cells, phase walk — only the
TIMBRE layer is produced by VPS synthesis.

Pipeline
  1. Parse source MIDI with mido (read/analyze only — no authoring).
  2. Render every note with the VPS engine (carrier saw via phase warp,
     dynamic K LFO, PM sidebands, velocity gain, pan spread).
  3. Mix: per-note sum -> soft-knee saturator -> Freeverb -> -1 dBFS peak.
  4. Write stereo WAV (normalize=False — we peak-normalized ourselves).
     -> OGG (Opus 48k voip).
  5. Analysis: render_info.json + silence gate + FFT pitch verification.

Usage:
  python render_sp012.py
"""

import json
import os
import shutil
from pathlib import Path

import mido
import numpy as np

from sound.utils.io import write_wav
from sound.utils.envelope import ADSREnvelope
from sound.effects.reverb import Freeverb

SR = 44100
A440 = 440.0

OUT_ROOT = Path("/opt/data/projects/Styles/Production/SP012-vps-minimalism-phase")
SRC_MIDI = Path(
    "/opt/data/projects/Styles/Minimalism/001-minimalism-phase-study/"
    "MIDI/minimalism-phase.mid"
)
NAME = "SP012-vps-minimalism-phase"

# --- VPS per-voice parameters ------------------------------------------------
# Program 12 marimba: sharp PD, moderate sweep, fast attack marimba-like.
# Program 49 pad: slow wide brightness sweep, larger PM for evolving shimmer.
# Program 33 bass: deep K, low PM, strong gain to anchor the pedal.
# Program 0 perc (kick, ch9): very short percussive note, high K = thump click.
VPS_PARAMS = {
    12: dict(role="Marimba",   carrier="saw", distortion=3.2, sweep_rate=0.9,
             sweep_depth=1.2,  warp_power=1.4, pm_index=0.7, pm_ratio=2.0,
             gain_db=-8.0, pan_width=0.85, env=dict(attack=0.002, decay=0.06,
             sustain=0.55, release=0.05)),
    49: dict(role="Pad",       carrier="saw", distortion=1.6, sweep_rate=0.25,
             sweep_depth=2.4,  warp_power=1.2, pm_index=1.1, pm_ratio=3.0,
             gain_db=-12.0, pan_width=0.4, env=dict(attack=0.35, decay=0.5,
             sustain=0.9, release=0.6)),
    33: dict(role="Bass",      carrier="saw", distortion=2.8, sweep_rate=0.5,
             sweep_depth=1.0,  warp_power=1.5, pm_index=0.4, pm_ratio=1.0,
             gain_db=-7.0, pan_width=0.3, env=dict(attack=0.004, decay=0.1,
             sustain=0.85, release=0.15)),
    0:  dict(role="Kick",      carrier="saw", distortion=4.5, sweep_rate=2.0,
             sweep_depth=1.5,  warp_power=2.0, pm_index=0.3, pm_ratio=0.5,
             gain_db=-6.0, pan_width=0.2, env=dict(attack=0.001, decay=0.04,
             sustain=0.2, release=0.03)),
}
DEFAULT_PARAMS = dict(role="Unknown", carrier="saw", distortion=2.5, sweep_rate=0.6,
                      sweep_depth=1.6, warp_power=1.5, pm_index=0.9, pm_ratio=2.0,
                      gain_db=-9.0, pan_width=0.7, env=dict(attack=0.004,
                      decay=0.08, sustain=0.72, release=0.10))


def midi_to_freq(m: int) -> float:
    return A440 * (2.0 ** ((m - 69) / 12.0))


def tick_to_sec(mid: mido.MidiFile, tick: int) -> float:
    """Convert an absolute tick to seconds honoring the tempo map (track 0)."""
    abs_tempos = []
    at = 0
    for m in mid.tracks[0]:
        at += m.time
        if m.type == "set_tempo":
            abs_tempos.append((at, m.tempo))
    if not abs_tempos:
        abs_tempos = [(0, 500000)]

    sec = 0.0
    prev_tick = 0
    cur_tempo = abs_tempos[0][1]
    for at, tmp in abs_tempos:
        if tick <= at:
            break
        sec += (at - prev_tick) * cur_tempo / mid.ticks_per_beat / 1_000_000
        prev_tick = at
        cur_tempo = tmp
    sec += (tick - prev_tick) * cur_tempo / mid.ticks_per_beat / 1_000_000
    return sec


def parse_notes(mid: mido.MidiFile):
    """Extract (start_sec, end_sec, pitch, velocity, program, channel, track)."""
    events = []
    for ti, track in enumerate(mid.tracks):
        if ti == 0:
            continue  # conductor track
        program, channel = 0, 0
        for m in track:
            if m.type == "program_change":
                program, channel = m.program, m.channel
        abstick = 0
        active = {}
        for m in track:
            abstick += m.time
            if m.type == "note_on" and m.velocity > 0:
                active[m.note] = (abstick, m.velocity)
            elif m.type in ("note_off",) or (m.type == "note_on" and m.velocity == 0):
                if m.note in active:
                    s, vel = active.pop(m.note)
                    events.append({
                        "track": ti, "program": program, "pitch": m.note,
                        "velocity": vel,
                        "start": tick_to_sec(mid, s),
                        "end": tick_to_sec(mid, abstick),
                    })
    events.sort(key=lambda e: e["start"])
    return events


def soft_knee(x: np.ndarray, thresh: float = 0.82, slope: float = 0.35) -> np.ndarray:
    y = np.where(np.abs(x) <= thresh, x, thresh + (np.abs(x) - thresh) * slope)
    return np.sign(x) * y


def vps_render_note(freq: float, duration: float, p: dict, sr: int = SR) -> np.ndarray:
    """Vector Phase Shaping render of a single note.

    Phase-shaping: the carrier phase phi is warped by a dynamic distortion
    vector K(t) (LFO-swept), then a PM modulator adds sidebands.
    """
    n = int(duration * sr)
    if n <= 0:
        return np.zeros(0, dtype=np.float32)
    t = np.arange(n) / sr

    # carrier phase accumulator
    ph = (freq * t) % 1.0

    # dynamic distortion vector K(t): slow LFO sweeping the warp amount
    lfo = 0.5 + 0.5 * np.sin(2.0 * np.pi * p["sweep_rate"] * t)
    K = p["distortion"] * (1.0 + p["sweep_depth"] * (2.0 * lfo - 1.0))
    K = np.clip(K, 0.0, 12.0)

    # phase-distortion warp: S-curve on |2phi-1|^power
    d = np.sign(ph - 0.5) * np.abs(2.0 * ph - 1.0) ** p["warp_power"]
    ph_warp = (ph + K * d) % 1.0

    # PM sideband modulator
    pm_ph = (freq * p["pm_ratio"] * t) % 1.0
    ph_final = (ph_warp + p["pm_index"] * np.sin(2.0 * np.pi * pm_ph)) % 1.0

    # carrier lookup: saw = 2*phi - 1
    out = 2.0 * ph_final - 1.0

    # 1-sample moving average (soften harsh aliasing)
    out = 0.5 * out + 0.5 * np.concatenate([out[:1], out[:-1]])

    # ADSR envelope
    env_p = p["env"]
    env = ADSREnvelope(
        attack_time=env_p["attack"], decay_time=env_p["decay"],
        sustain_level=env_p["sustain"], release_time=env_p["release"],
        sample_rate=sr,
    ).generate(duration)
    if len(env) < n:
        env = np.pad(env, (0, n - len(env)))
    env = env[:n]

    return (out * env).astype(np.float32)


def main():
    audio_dir = OUT_ROOT / "Audio"
    analysis_dir = OUT_ROOT / "Analysis"
    midi_dir = OUT_ROOT / "MIDI"
    for d in (audio_dir, analysis_dir, midi_dir):
        d.mkdir(parents=True, exist_ok=True)

    # copy source MIDI into project
    shutil.copy2(SRC_MIDI, midi_dir / SRC_MIDI.name)

    mid = mido.MidiFile(str(SRC_MIDI))
    events = parse_notes(mid)
    total_dur = mid.length
    print(f"notes={len(events)} total_dur={total_dur:.2f}s")

    bpm = round(60_000_000 / next(
        (m.tempo for tr in mid.tracks for m in tr if m.type == "set_tempo"), 500000), 2)

    buf_len = int((total_dur + 3.0) * SR)
    mixL = np.zeros(buf_len, dtype=np.float64)
    mixR = np.zeros(buf_len, dtype=np.float64)

    per_note = []
    n_notes = len(events)

    for i, e in enumerate(events):
        p = VPS_PARAMS.get(e["program"], DEFAULT_PARAMS)
        dur = max(0.15, e["end"] - e["start"])
        freq = midi_to_freq(e["pitch"])
        sig = vps_render_note(freq, dur, p)

        # velocity -> gain
        vel_db = 20.0 * np.log10(e["velocity"] / 100.0) if e["velocity"] > 0 else -6.0
        g_lin = 10.0 ** ((p["gain_db"] + vel_db) / 20.0)
        sig = sig * g_lin

        # pan: role-based spread + slow cyclic motion per note
        pan = 0.5 + 0.5 * p["pan_width"] * np.sin(2.0 * np.pi * (i / max(1, n_notes - 1)))

        s0 = int(e["start"] * SR)
        s1 = min(s0 + len(sig), buf_len)
        seg = sig[: s1 - s0].astype(np.float64)
        mixL[s0:s1] += seg * (1.0 - pan)
        mixR[s0:s1] += seg * pan

        if i % 200 == 0:
            print(f"  note {i}/{n_notes} pitch={e['pitch']} dur={dur:.2f}s prog={e['program']}")

        per_note.append({
            "i": i, "pitch": e["pitch"], "freq_hz": round(freq, 2),
            "vel": e["velocity"], "start_s": round(e["start"], 3),
            "dur_s": round(dur, 3), "pan": round(pan, 3),
            "program": e["program"],
        })

    # ---- mix stage ---------------------------------------------------------
    # soft-knee saturator (overdrive warmth)
    mixL = soft_knee(mixL)
    mixR = soft_knee(mixR)

    # algorithmic reverb (Freeverb) for space
    stereo = np.stack([mixL, mixR], axis=1)
    reverb = Freeverb(sample_rate=SR, room_size=0.5, damping=0.6, wet_dry=0.20, width=0.8)
    stereo = reverb.process(stereo)

    mixL = stereo[:, 0]
    mixR = stereo[:, 1]

    # peak normalize to -1 dBFS
    peak = max(np.max(np.abs(mixL)), np.max(np.abs(mixR)))
    if peak > 0:
        norm = 10 ** (-1.0 / 20.0) / peak
        mixL *= norm
        mixR *= norm

    # ---- silence gate (skill: silent-render trap) --------------------------
    mono = 0.5 * (mixL + mixR)
    silent_frac = float(np.sum(np.abs(mono) < 0.001) / len(mono))
    print(f"silence fraction: {silent_frac:.3f}")
    assert silent_frac < 0.30, f"SUSPECT render: {silent_frac:.1%} silence"

    # ---- FFT pitch verification -------------------------------------------
    def fft_pitch_frames(sig, sr, lo=50.0, hi=1000.0):
        """Dominant FFT peak per 0.5 s window in [lo,hi] Hz."""
        win = int(0.5 * sr)
        hop = int(0.25 * sr)
        out = []
        for t0 in range(0, len(sig) - win, hop):
            seg = sig[t0:t0 + win] * np.hanning(win)
            if np.max(np.abs(seg)) < 0.01:
                out.append(0.0)
                continue
            spec = np.abs(np.fft.rfft(seg))
            freqs = np.fft.rfftfreq(win, 1.0 / sr)
            mask = (freqs >= lo) & (freqs <= hi)
            if mask.sum() == 0:
                out.append(0.0)
                continue
            f = freqs[mask][np.argmax(spec[mask])]
            out.append(float(f))
        return out

    frames = fft_pitch_frames(mono, SR)
    detected = [f for f in frames if f > 0]
    print(f"pitch frames: {len(detected)}/{len(frames)} detected")
    if detected:
        print(f"  range {min(detected):.0f}-{max(detected):.0f} Hz, "
              f"median {np.median(detected):.0f} Hz")

    # ---- per-second RMS map ------------------------------------------------
    secs = int(total_dur)
    rms_map = []
    for s in range(secs):
        seg = mono[s * SR:(s + 1) * SR]
        rms = float(np.sqrt(np.mean(seg ** 2))) if len(seg) else 0.0
        rms_map.append(round(rms, 5))
    print(f"per-second RMS: {rms_map}")

    # ---- write -------------------------------------------------------------
    wav_path = audio_dir / f"{NAME}.wav"
    ogg_path = audio_dir / f"{NAME}.ogg"
    write_wav(str(wav_path), np.stack([mixL, mixR], axis=1), SR, normalize=False)

    os.system(
        f'ffmpeg -y -loglevel error -i "{wav_path}" '
        f'-codec:a libopus -application voip -b:a 48k "{ogg_path}"'
    )

    # ---- analysis artifacts -------------------------------------------------
    dur_out = len(mixL) / SR
    info = {
        "source_midi": str(SRC_MIDI),
        "method": "SP-012",
        "method_name": "Vector Phase Shaping (VPS)",
        "bpm": bpm,
        "total_notes": len(events),
        "output_seconds": round(dur_out, 3),
        "silence_fraction": round(silent_frac, 4),
        "rms_per_second": rms_map,
        "pitch_verification": {
            "frames_detected": len(detected),
            "frames_total": len(frames),
            "range_hz": [round(min(detected), 1), round(max(detected), 1)] if detected else None,
            "median_hz": round(float(np.median(detected)), 1) if detected else None,
        },
        "synthesis_engine": "project-local VPS (vector phase shaping) + PM sidebands",
        "parameters": {str(k): {kk: vv for kk, vv in v.items() if kk != "role"}
                       for k, v in VPS_PARAMS.items()},
        "mix": {
            "soft_knee": {"threshold": 0.82, "slope": 0.35},
            "reverb": "Freeverb(room_size=0.5, damping=0.6, wet_dry=0.20, width=0.8)",
            "normalize_db": -1.0,
        },
        "note_count": len(per_note),
    }
    (analysis_dir / "render_info.json").write_text(json.dumps(info, indent=2))

    # provenance
    prov = {
        "job": "SP-012 production pass (autonomous cron)",
        "source_midi": str(SRC_MIDI),
        "production_method": "SP-012",
        "production_method_name": "Vector Phase Shaping (VPS)",
        "outputs": {
            "full_mix_wav": str(wav_path),
            "full_mix_ogg": str(ogg_path),
        },
    }
    (OUT_ROOT / "provenance.json").write_text(json.dumps(prov, indent=2))

    # ---- checks -------------------------------------------------------------
    for pth in (wav_path, ogg_path):
        sz = pth.stat().st_size
        print(f"{pth.name}: {sz} bytes")
        assert sz > 1000, f"output too small: {pth}"

    print("DONE", wav_path, ogg_path)


if __name__ == "__main__":
    main()
