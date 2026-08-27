# -*- coding: utf-8 -*-
"""
SP-012 — Vector Phase Shaping (VPS) production pass.

Source : 039-electric-blues daily v5 MIDI (Blues / distortion-guitar lead, prog 30,
         single track, 144 notes, pitch 52-60, ~36 s)
Method : SP-012 — Vector Phase Shaping (VPS), methods_db.md
         "Synthesis modifying phase distortion speed via dynamic vectors.
          Creates expressive sweeps and complex sidebands."

Core idea
---------
A carrier phase accumulator is warped by a *time-varying* phase-distortion
vector K(t). K(t) is itself driven by a slow LFO sweep (dynamic vector), so the
spectral brightness of every note sweeps expressively over time instead of
staying static. A simultaneous phase-modulation (PM) modulator injects
inharmonic sidebands for the "complex sidebands" character described in the
method. This gives the electric-blues lead a vocal, wavering, overdriven edge
that fits the 12-bar feel.

Pipeline
  1. Parse source MIDI with mido (read/analyze only — no authoring).
  2. Render every note with the VPS engine:
       - carrier: anti-aliased-ish saw via phase-shaping warp
       - dynamic distortion vector: LFO sweep of K (sweep_rate / sweep_depth)
       - PM sideband modulator (pm_index / pm_ratio)
       - velocity -> gain, per-note pan spread across the stereo field
  3. Mix: per-note sum -> soft-knee saturator -> algorithmic reverb
     (sound.effects.reverb.Freeverb) -> peak normalize to -1 dBFS.
  4. Write stereo WAV (library io.write_wav) -> OGG (Opus, 48k voip).
  5. Analysis: render_info.json + silence-gate check (skill's silent-render trap).

Usage:
  python produce_sp012.py
"""

import json
import os
import shutil
from pathlib import Path

import mido
import numpy as np

# library imports (editable install)
from sound.utils.io import write_wav
from sound.utils.envelope import ADSREnvelope
from sound.effects.reverb import Freeverb

SR = 44100
A440 = 440.0

OUT_ROOT = Path("/opt/data/projects/Styles/Production/SP012-vps-electric-blues")
SRC_MIDI = Path(
    "/opt/data/projects/Styles/Blues/039-electric-blues/"
    "daily-2026-06-27_blues_039-electric-blues-v5.mid"
)

# --- VPS synthesis parameters ----------------------------------------------
# Per-program voice map (single track here, but keep the structure general)
VPS_PARAMS = {
    "lead": {
        "carrier": "saw",
        "distortion": 2.5,       # base phase-distortion amount K
        "sweep_rate": 0.6,       # Hz — dynamic vector LFO (brightness sweep)
        "sweep_depth": 1.6,      # how far K wanders around its base
        "warp_power": 1.5,       # PD curve exponent (>>1 = harsher)
        "pm_index": 0.9,         # PM sideband depth (rad-ish)
        "pm_ratio": 2.0,         # modulator freq ratio (creates sidebands)
        "gain_db": -9.0,
        "pan_width": 0.7,
    },
}


# --- helpers ----------------------------------------------------------------
def midi_to_freq(m: int) -> float:
    return A440 * (2.0 ** ((m - 69) / 12.0))


def tick_to_sec(mid: mido.MidiFile, tick: int) -> float:
    """Convert an absolute tick to seconds honoring tempo map (track 0)."""
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
    """Extract (start_sec, end_sec, pitch, velocity, program, track) events."""
    events = []
    for ti, track in enumerate(mid.tracks):
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

    # smooth a touch with a 1-sample moving average (soften harsh aliasing)
    out = 0.5 * out + 0.5 * np.concatenate([out[:1], out[:-1]])

    # ADSR envelope
    env = ADSREnvelope(
        attack_time=0.004, decay_time=0.08, sustain_level=0.72,
        release_time=0.10, sample_rate=sr,
    ).generate(duration)
    if len(env) < n:
        env = np.pad(env, (0, n - len(env)))
    env = env[:n]

    return (out * env).astype(np.float32)


# --- main -------------------------------------------------------------------
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

    # tempo (bpm) from first set_tempo
    bpm = round(60_000_000 / next(
        (m.tempo for tr in mid.tracks for m in tr if m.type == "set_tempo"), 500000), 2)

    buf_len = int((total_dur + 2.5) * SR)
    mixL = np.zeros(buf_len, dtype=np.float64)
    mixR = np.zeros(buf_len, dtype=np.float64)

    p = VPS_PARAMS["lead"]
    per_note = []
    n_notes = len(events)

    for i, e in enumerate(events):
        dur = max(0.15, e["end"] - e["start"])
        freq = midi_to_freq(e["pitch"])
        sig = vps_render_note(freq, dur, p)

        # velocity -> gain
        vel_db = 20.0 * np.log10(e["velocity"] / 100.0) if e["velocity"] > 0 else -6.0
        g_lin = 10.0 ** ((p["gain_db"] + vel_db) / 20.0)
        sig = sig * g_lin

        # pan: spread across field, slight cyclic motion for blues swagger
        pan = 0.5 + 0.5 * p["pan_width"] * np.sin(2.0 * np.pi * (i / max(1, n_notes - 1)) * 1.0)

        s0 = int(e["start"] * SR)
        s1 = min(s0 + len(sig), buf_len)
        seg = sig[: s1 - s0].astype(np.float64)
        mixL[s0:s1] += seg * (1.0 - pan)
        mixR[s0:s1] += seg * pan

        per_note.append({
            "i": i, "pitch": e["pitch"], "freq_hz": round(freq, 2),
            "vel": e["velocity"], "start_s": round(e["start"], 3),
            "dur_s": round(dur, 3), "pan": round(pan, 3),
        })

    # ---- mix stage ---------------------------------------------------------
    # soft-knee saturator (overdrive warmth)
    mixL = soft_knee(mixL)
    mixR = soft_knee(mixR)

    # algorithmic reverb (Freeverb) for space
    stereo = np.stack([mixL, mixR], axis=1)
    reverb = Freeverb(sample_rate=SR, room_size=0.55, damping=0.5, wet_dry=0.22, width=0.8)
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

    # ---- write -------------------------------------------------------------
    wav_path = audio_dir / "SP012-electric-blues-vps.wav"
    ogg_path = audio_dir / "SP012-electric-blues-vps.ogg"
    write_wav(str(wav_path), np.stack([mixL, mixR], axis=1), SR)

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
        "synthesis_engine": "project-local VPS (vector phase shaping) + PM sidebands",
        "parameters": VPS_PARAMS,
        "mix": {
            "soft_knee": {"threshold": 0.82, "slope": 0.35},
            "reverb": "Freeverb(room_size=0.55, damping=0.5, wet_dry=0.22, width=0.8)",
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