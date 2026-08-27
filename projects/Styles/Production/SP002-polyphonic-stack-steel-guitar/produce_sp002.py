# -*- coding: utf-8 -*-
"""
SP-002 — VST3 Polyphonic Stacking production pass.

Source: 038-steel-guitar-demo (Country, 80 BPM, 12 s, 32 notes, D4/E4/G4)
Method: SP-002 — VST3 Polyphonic Stacking (methods_db.md SP-002)
        "Renders voices independently through virtual instruments, then sums outputs in NumPy."

Since no VST3 plugins are available in this headless environment, we implement
the *spirit* of SP-002: each voice gets its own synthesis engine (virtual instrument),
renders independently, then sums in NumPy.

Voice allocation by pitch register:
  - Voice 1 (Low, D4): BowedString (sustaining cello-like)
  - Voice 2 (Mid, E4): ResonatorBank (modal pluck)
  - Voice 3 (High, G4): PhaseModSynth (bell-like harmonic)

Pipeline:
  1. Parse source MIDI with mido (analysis-only).
  2. Split notes by pitch into 3 voices.
  3. Render each voice independently through its synthesis engine.
  4. Sum all voices in NumPy with per-voice gain + stereo panning.
  5. Mix: soft-knee bus → stereo WAV → OGG.

Usage:
  python produce_sp002.py
"""

import json
import os
import shutil
from pathlib import Path

import mido
import numpy as np

# library imports (editable install)
from sound.synthesis.bowed import BowedString
from sound.synthesis.modal import ResonatorBank, ResonatorMode
from sound.synthesis.phase_mod import PhaseModSynth
from sound.utils.io import write_wav

SR = 44100
A440 = 440.0

OUT_ROOT = Path("/opt/data/projects/Styles/Production/SP002-polyphonic-stack-steel-guitar")
SRC_MIDI = Path(
    "/opt/data/projects/Styles/Country/038-steel-guitar-demo/"
    "daily-2026-06-26_country_038-steel-guitar-v5.mid"
)

# --- voice design -----------------------------------------------------------
# Each voice = its own synthesis engine (virtual instrument)
VOICE_PARAMS = {
    "low": {
        "gain_db": -1.0,
        "pan": -0.35,  # left
        "engine": "bowed_string",
        "bow_pos": 0.12,
        "bow_vel": 0.22,
        "bow_force": 1.6,
    },
    "mid": {
        "gain_db": -8.0,
        "pan": 0.0,  # center
        "engine": "modal_pluck",
        "modes": [
            {"freq_ratio": 1.0, "amp": 1.0, "decay": 4.0},
            {"freq_ratio": 2.0, "amp": 0.28, "decay": 3.0},
            {"freq_ratio": 3.0, "amp": 0.10, "decay": 2.5},
        ],
    },
    "high": {
        "gain_db": -9.0,
        "pan": 0.35,  # right
        "engine": "phase_mod",
        "carrier": "sine",
        "modulator": "sine",
        "ratio": 1.0,
        "index": 0.8,
    },
}


# --- helpers ----------------------------------------------------------------
def midi_to_freq(m: int) -> float:
    return A440 * (2.0 ** ((m - 69) / 12.0))


def tick_to_sec(mid: mido.MidiFile, tick: int) -> float:
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


def allocate_voice(pitch: int) -> str:
    """Split notes into voices by pitch register."""
    if pitch <= 62:  # D4 and below
        return "low"
    elif pitch <= 64:  # E4
        return "mid"
    else:  # F4 and above (G4 in this piece)
        return "high"


def render_bowed_string(freq: float, duration: float, p: dict, sr: int = SR) -> np.ndarray:
    """Voice 1: BowedString (sustaining cello-like)."""
    bs = BowedString(sample_rate=sr)
    audio = bs.render(
        freq=freq,
        duration=duration,
        bow_velocity=p["bow_vel"],
        bow_force=p["bow_force"],
        bow_position=p["bow_pos"],
    )
    return audio


def render_modal_pluck(freq: float, duration: float, p: dict, sr: int = SR) -> np.ndarray:
    """Voice 2: ResonatorBank (modal pluck)."""
    bank = ResonatorBank(sample_rate=sr)
    for m in p["modes"]:
        bank.add_mode(
            freq=freq * m["freq_ratio"],
            amplitude=m["amp"],
            decay=m["decay"],
        )
    # Excite with impulse (delta function)
    audio = bank.excite_impulse(duration=duration)
    return audio


def render_phase_mod(freq: float, duration: float, p: dict, sr: int = SR) -> np.ndarray:
    """Voice 3: PhaseModSynth (bell-like harmonic)."""
    pm = PhaseModSynth(sample_rate=sr)
    # Configure for bell-like timbre (FM-ish sidebands from mod depth)
    audio = pm.render_note(
        freq=freq,
        duration=duration,
        carrier_shape=p["carrier"],
        mod_shape=p["modulator"],
        mod_freq_ratio=p["ratio"],
        mod_depth=p["index"],
        volume=0.8,
        attack=0.005,
        decay=0.15,
        sustain_level=0.5,
        release=0.25,
    )
    return audio


def render_voice(events: list, voice_name: str, sr: int = SR) -> np.ndarray:
    """Render all events for one voice through its synthesis engine.

    For sustaining engines (bowed string), notes are extended legato to the
    next onset so the stacked texture stays continuous across structural rests.
    """
    if not events:
        return np.zeros(0, dtype=np.float32)

    p = VOICE_PARAMS[voice_name]
    engine = p["engine"]

    # Calculate total duration needed
    max_end = max(e["end"] for e in events)
    total_samples = int(max_end * sr) + int(2.0 * sr)  # 2.0s reverb tail
    mix = np.zeros(total_samples, dtype=np.float32)

    # next-onset lookup for legato extension (sustaining voices only)
    onsets = sorted(e["start"] for e in events)

    def next_onset(t: float) -> float:
        for o in onsets:
            if o > t + 1e-6:
                return o
        return t + 0.5

    for e in events:
        dur = max(0.15, e["end"] - e["start"])
        freq = midi_to_freq(e["pitch"])

        if engine == "bowed_string":
            # legato: sustain until just before the next onset (fills rests)
            dur = max(dur, min(2.0, next_onset(e["start"]) - e["start"] + 0.05))
            audio = render_bowed_string(freq, dur, p, sr)
        elif engine == "modal_pluck":
            # pluck: keep attack character, but let the resonance ring
            dur = max(dur, 0.9)
            audio = render_modal_pluck(freq, dur, p, sr)
        elif engine == "phase_mod":
            # bell: long release so the 4 sparse high notes bloom
            dur = max(dur, min(1.5, next_onset(e["start"]) - e["start"] + 0.4))
            audio = render_phase_mod(freq, dur, p, sr)
        else:
            raise ValueError(f"Unknown engine: {engine}")

        # Velocity -> gain
        vel_db = 20.0 * np.log10(e["velocity"] / 100.0) if e["velocity"] > 0 else -6.0
        g_lin = 10.0 ** ((p["gain_db"] + vel_db) / 20.0)
        audio = audio * g_lin

        # Place in mix buffer
        s0 = int(e["start"] * sr)
        s1 = min(s0 + len(audio), total_samples)
        mix[s0:s1] += audio[: s1 - s0]

    return mix


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

    # Split events by voice
    voice_events = {"low": [], "mid": [], "high": []}
    for e in events:
        v = allocate_voice(e["pitch"])
        voice_events[v].append(e)

    print(f"voice allocation: low={len(voice_events['low'])} mid={len(voice_events['mid'])} high={len(voice_events['high'])}")

    # Render each voice independently
    voice_audio = {}
    for vname, vevents in voice_events.items():
        if vevents:
            print(f"rendering voice '{vname}' ({len(vevents)} notes)...")
            voice_audio[vname] = render_voice(vevents, vname, SR)
        else:
            print(f"voice '{vname}' has no notes, skipping")

    # Sum all voices with stereo panning
    max_len = max(len(a) for a in voice_audio.values()) if voice_audio else 0
    mixL = np.zeros(max_len, dtype=np.float64)
    mixR = np.zeros(max_len, dtype=np.float64)

    for vname, audio in voice_audio.items():
        p = VOICE_PARAMS[vname]
        pan = p["pan"]
        gain_l = (1.0 - pan) * 0.5
        gain_r = (1.0 + pan) * 0.5
        mixL[: len(audio)] += audio * gain_l
        mixR[: len(audio)] += audio * gain_r

    # ---- mix stage ---------------------------------------------------------
    # soft-knee saturator
    def soft_knee(x, thresh=0.82, slope=0.35):
        y = np.where(np.abs(x) <= thresh, x, thresh + (np.abs(x) - thresh) * slope)
        return np.sign(x) * y

    mixL = soft_knee(mixL)
    mixR = soft_knee(mixR)

    # ---- reverb ------------------------------------------------------------
    # algorithmic reverb (Schroeder/Moorer) — fills structural rests + space
    from sound.effects.reverb import AlgorithmicReverb
    stereo = np.stack([mixL, mixR], axis=1)
    reverb = AlgorithmicReverb(room_size=0.65, damping=0.5, wet_dry=0.28)
    stereo = reverb.process(stereo)
    mixL = stereo[:, 0]
    mixR = stereo[:, 1]

    # ---- DC blocker (high-pass at 45 Hz, 2nd order) — FINAL STAGE ----------
    # BowedString waveform is asymmetric (positive-biased); soft-knee saturation
    # rectifies the bias into DC (measured +0.206 L / +0.103 R after saturator).
    # Blocker must run AFTER sat/reverb to remove the induced offset.
    from scipy.signal import butter, lfilter
    b_dc, a_dc = butter(2, 45.0, btype="high", fs=SR)
    mixL = lfilter(b_dc, a_dc, mixL)
    mixR = lfilter(b_dc, a_dc, mixR)

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
    wav_path = audio_dir / "SP002-polyphonic-stack-steel-guitar.wav"
    ogg_path = audio_dir / "SP002-polyphonic-stack-steel-guitar.ogg"
    write_wav(str(wav_path), np.stack([mixL, mixR], axis=1), SR)

    os.system(
        f'ffmpeg -y -loglevel error -i "{wav_path}" '
        f'-codec:a libopus -application voip -b:a 48k "{ogg_path}"'
    )

    # ---- analysis artifacts -------------------------------------------------
    dur_out = len(mixL) / SR
    info = {
        "source_midi": str(SRC_MIDI),
        "method": "SP-002",
        "method_name": "VST3 Polyphonic Stacking",
        "bpm": bpm,
        "total_notes": len(events),
        "output_seconds": round(dur_out, 3),
        "silence_fraction": round(silent_frac, 4),
        "synthesis_engine": "per-voice independent synthesis engines (bowed_string + modal_pluck + phase_mod)",
        "voice_allocation": {
            "low": {"notes": len(voice_events["low"]), "engine": "BowedString"},
            "mid": {"notes": len(voice_events["mid"]), "engine": "ResonatorBank"},
            "high": {"notes": len(voice_events["high"]), "engine": "PhaseModSynth"},
        },
        "parameters": VOICE_PARAMS,
        "mix": {
            "soft_knee": {"threshold": 0.82, "slope": 0.35},
            "normalize_db": -1.0,
        },
    }
    (analysis_dir / "render_info.json").write_text(json.dumps(info, indent=2))

    # provenance
    prov = {
        "job": "SP-002 production pass (autonomous cron)",
        "source_midi": str(SRC_MIDI),
        "production_method": "SP-002",
        "production_method_name": "VST3 Polyphonic Stacking",
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
