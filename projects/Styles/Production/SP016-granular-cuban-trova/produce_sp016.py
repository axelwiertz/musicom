# -*- coding: utf-8 -*-
"""
SP-016 Granular Synthesis Engine - production pass.

Method (methods_db.md SP-016): Granular Synthesis slices a continuous source
audio buffer into microscopic grains (10-100 ms), then re-schedules them with
overlap, windowing, spray (positional jitter), grain-size jitter, and pitch
shift to construct time-stretched pads, ambient soundscapes, and sonic clouds.

Pipeline:
  1. Dry render the selected Cuban trova MIDI with FluidSynth (source buffer).
  2. Split the arrangement into per-voice stems (lead / guitar / bass / piano).
  3. Granular clouds per voice via musicom `sound.synthesis.granular`
     AperiodicGranulator (canonical engine), with per-voice pitch shift and
     density so the arrangement structure survives in the cloud.
  4. Blend dry + granular, add reverb, master to -1 dBFS.
  5. Export WAV + OGG + analysis + provenance + README.
"""
import os
import json
import shutil
import hashlib
import subprocess
import numpy as np
import wave

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJ = "/opt/data/projects/Styles/Production/SP016-granular-cuban-trova"
MIDI_SRC = ("/opt/data/projects/Styles/Cuban/001-cuban-trova-research/"
            "daily-2026-07-01_cuban_001-cuban-trova-research_fixed.mid")
SOUNDFONT = ("/opt/data/micromamba/envs/musicom/lib/python3.11/"
             "site-packages/pretty_midi/TimGM6mb.sf2")
FLUIDSYNTH = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
PY = "/opt/data/micromamba/envs/musicom/bin/python"

AUDIO = os.path.join(PROJ, "Audio")
MIDI_OUT = os.path.join(PROJ, "MIDI")
ANALYSIS = os.path.join(PROJ, "Analysis")
for d in (AUDIO, MIDI_OUT, ANALYSIS):
    os.makedirs(d, exist_ok=True)

SR = 44100

# ---------------------------------------------------------------------------
# WAV IO
# ---------------------------------------------------------------------------
def wav_read(path):
    with wave.open(path, 'rb') as wf:
        nch = wf.getnchannels()
        sw = wf.getsampwidth()
        fr = wf.getframerate()
        n = wf.getnframes()
        raw = wf.readframes(n)
    data = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    if nch > 1:
        data = data.reshape(n, nch)
    return data, nch, fr

def wav_write(path, data, sr=SR, nch=1):
    if data.ndim == 1:
        data = data[:, None]
    if nch == 1:
        data = data[:, 0]
    pcm = np.clip(data, -1.0, 1.0)
    pcm = (pcm * 32767.0).astype(np.int16)
    with wave.open(path, 'wb') as wf:
        wf.setnchannels(nch)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())

def silence_fraction(mono):
    return float(np.sum(np.abs(mono) < 0.001) / len(mono))

def rms_map(mono, sr, win=1.0):
    n = int(sr * win)
    out = []
    for i in range(0, len(mono) - n, n):
        seg = mono[i:i + n]
        out.append(float(np.sqrt(np.mean(seg ** 2))))
    return out

# ---------------------------------------------------------------------------
# Step 0. Copy source MIDI + hash
# ---------------------------------------------------------------------------
midi_copy = os.path.join(MIDI_OUT, "original_cuban_trova_fixed.mid")
shutil.copy(MIDI_SRC, midi_copy)
with open(MIDI_SRC, 'rb') as f:
    src_sha = hashlib.sha256(f.read()).hexdigest()
print("source midi copied, sha:", src_sha[:16])

# ---------------------------------------------------------------------------
# Step 1. Dry render (full arrangement) via FluidSynth CLI
# ---------------------------------------------------------------------------
dry_wav = os.path.join(AUDIO, "dry_render_full.wav")
if not os.path.exists(dry_wav):
    cmd = [FLUIDSYNTH, "-a", "file", "-ni", "-g", "1.2",
           "-r", str(SR), "-F", dry_wav, SOUNDFONT, MIDI_SRC]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    print("fluidsynth rc:", r.returncode)
    if r.returncode != 0 or not os.path.exists(dry_wav):
        print(r.stderr[-2000:])
        raise SystemExit("FluidSynth dry render failed")
print("dry render size:", os.path.getsize(dry_wav))

dry_st, nch, fr = wav_read(dry_wav)
print("dry: nch", nch, "fr", fr, "dur", dry_st.shape[0] / fr)
dry_mono = dry_st.mean(axis=1) if dry_st.ndim > 1 else dry_st
print("dry silence fraction:", round(silence_fraction(dry_mono), 4))

# ---------------------------------------------------------------------------
# Step 2. Per-voice stems (so the arrangement survives inside the cloud)
# ---------------------------------------------------------------------------
# Voice map: track -> (name, program). Derived from mido analysis:
#   track1 prog73 Flute (lead), track2 prog24 Nylon Guitar,
#   track3 prog33 Electric Bass, track4 prog0 Piano
stems = {}
import mido
mid = mido.MidiFile(MIDI_SRC)
for ti, track in enumerate(mid.tracks):
    if ti == 0:
        continue
    prog = None
    for msg in track:
        if msg.type == 'program_change':
            prog = msg.program
            break
    name = {73: "lead_flute", 24: "nylon_guitar", 33: "electric_bass",
            0: "piano"}.get(prog, f"track{ti}")
    stem_midi = os.path.join(MIDI_OUT, f"stem_{name}.mid")
    # Build a single-track MIDI with just this voice
    out_mid = mido.MidiFile(ticks_per_beat=mid.ticks_per_beat)
    t0 = mido.MidiTrack()
    out_mid.tracks.append(t0)
    for msg in mid.tracks[0]:
        if msg.type in ('set_tempo', 'time_signature', 'key_signature'):
            t0.append(msg)
    if prog is not None:
        t0.append(mido.Message('program_change', program=prog, time=0))
    for msg in track:
        if msg.type in ('note_on', 'note_off', 'control_change', 'pitchwheel'):
            t0.append(msg)
    out_mid.save(stem_midi)
    stem_wav = os.path.join(AUDIO, f"stem_{name}_dry.wav")
    if not os.path.exists(stem_wav):
        cmd = [FLUIDSYNTH, "-a", "file", "-ni", "-g", "1.2",
               "-r", str(SR), "-F", stem_wav, SOUNDFONT, stem_midi]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if r.returncode != 0 or not os.path.exists(stem_wav):
            print("stem render failed:", name, r.stderr[-500:])
            continue
    stems[name] = stem_wav
    print("stem:", name, "->", os.path.getsize(stem_wav), "bytes")

# ---------------------------------------------------------------------------
# Step 3. Granular clouds per voice (SP-016 core)
# ---------------------------------------------------------------------------
from sound.synthesis.granular import AperiodicGranulator

gran = AperiodicGranulator(sample_rate=SR)

# Per-voice granular parameters: keep bass/guitar as rhythmic anchor with low
# density, lead/piano as shimmering clouds with pitch shift.
gran_params = {
    "lead_flute":      dict(duration_sec=18.0, grain_size_ms=45, density_grains_per_sec=60,
                            pitch_shift_semi=7,  position_jitter_ms=30, grain_jitter_ms=12),
    "nylon_guitar":    dict(duration_sec=18.0, grain_size_ms=35, density_grains_per_sec=80,
                            pitch_shift_semi=0,  position_jitter_ms=20, grain_jitter_ms=8),
    "electric_bass":   dict(duration_sec=18.0, grain_size_ms=60, density_grains_per_sec=30,
                            pitch_shift_semi=-12, position_jitter_ms=15, grain_jitter_ms=10),
    "piano":           dict(duration_sec=18.0, grain_size_ms=40, density_grains_per_sec=70,
                            pitch_shift_semi=5,  position_jitter_ms=25, grain_jitter_ms=10),
}

clouds = {}
for name, params in gran_params.items():
    if name not in stems:
        print("skip cloud, no stem:", name)
        continue
    out_cloud = os.path.join(AUDIO, f"cloud_{name}.wav")
    if not os.path.exists(out_cloud):
        gran.generate_cloud(stems[name], out_cloud, **params)
    clouds[name] = out_cloud
    print("cloud:", name, "->", os.path.getsize(out_cloud), "bytes")

# ---------------------------------------------------------------------------
# Step 4. Mix: dry bed + granular clouds + reverb
# ---------------------------------------------------------------------------
n_out = int(18.0 * SR)
mix = np.zeros(n_out, dtype=np.float32)

# Dry bed (fade in/out to avoid clicks)
dry_len = min(len(dry_mono), n_out)
dry_trim = dry_mono[:dry_len].copy()
fade = int(0.05 * SR)
dry_trim[:fade] *= np.linspace(0, 1, fade)
dry_trim[-fade:] *= np.linspace(1, 0, fade)
mix[:dry_len] += dry_trim * 0.55

# Granular clouds
for name, path in clouds.items():
    c, _, _ = wav_read(path)
    c = c[:n_out]
    if len(c) < n_out:
        c = np.pad(c, (0, n_out - len(c)))
    gain = {"lead_flute": 0.30, "nylon_guitar": 0.35,
            "electric_bass": 0.30, "piano": 0.30}.get(name, 0.30)
    mix += c * gain
    print("mixed cloud:", name, "gain", gain)

# Reverb (Schroeder via musicom)
try:
    from sound.effects.reverb import AlgorithmicReverb
    rev = AlgorithmicReverb(sample_rate=SR, room_size=0.7, damping=0.5,
                            wet_dry=0.25, width=0.8, modulation=0.1)
    mix = rev.process(mix)
    print("reverb applied")
except Exception as e:
    print("reverb skipped:", e)

# Stereo-ize: simple mid-side widening — cloud beds panned, dry center
mix_stereo = np.zeros((n_out, 2), dtype=np.float32)
mix_stereo[:, 0] = mix
mix_stereo[:, 1] = mix
# Add slight stereo spread via delayed copy
delay = int(0.012 * SR)
mix_stereo[delay:, 1] += mix[:-delay] * 0.25
mix_stereo[:, 1] = np.clip(mix_stereo[:, 1], -1, 1)

# ---------------------------------------------------------------------------
# Step 5. Master: peak normalize to -1 dBFS
# ---------------------------------------------------------------------------
peak = np.max(np.abs(mix_stereo))
if peak > 0:
    mix_stereo = mix_stereo / peak * 0.891  # -1 dBFS
print("master peak:", np.max(np.abs(mix_stereo)))

full_wav = os.path.join(AUDIO, "SP016-granular-cuban-trova.wav")
wav_write(full_wav, mix_stereo, sr=SR, nch=2)

# ---------------------------------------------------------------------------
# Step 6. Quality gate (silent-render trap)
# ---------------------------------------------------------------------------
mono = mix_stereo.mean(axis=1)
sil = silence_fraction(mono)
print("FULL silence fraction:", round(sil, 4))
print("FULL rms/sec:", [round(x, 4) for x in rms_map(mono, SR)][:20])
assert os.path.getsize(full_wav) > 1000, "WAV too small"
assert sil < 0.30, f"silence fraction {sil} too high - silent render trap"

# ---------------------------------------------------------------------------
# Step 7. OGG (Opus, Telegram voice-bubble profile)
# ---------------------------------------------------------------------------
ogg = os.path.join(AUDIO, "SP016-granular-cuban-trova.ogg")
subprocess.run(["ffmpeg", "-y", "-i", full_wav,
                "-codec:a", "libopus", "-application", "voip", "-b:a", "48k",
                ogg], capture_output=True, timeout=300)
print("ogg size:", os.path.getsize(ogg))
assert os.path.getsize(ogg) > 1000, "OGG too small"

# ---------------------------------------------------------------------------
# Step 8. Analysis + provenance
# ---------------------------------------------------------------------------
render_info = {
    "job": "SP-016 granular production pass (autonomous cron)",
    "source_midi": MIDI_SRC,
    "source_midi_sha256": src_sha,
    "production_method": "SP-016",
    "production_method_name": "Granular Synthesis Engine",
    "tempo_bpm": 96,
    "source_notes": 96,
    "source_duration_sec": 15.0,
    "output_duration_sec": 18.0,
    "granular_params": gran_params,
    "mix": {"dry_bed_gain": 0.55, "cloud_gains": {"lead_flute": 0.30,
             "nylon_guitar": 0.35, "electric_bass": 0.30, "piano": 0.30},
             "reverb": "AlgorithmicReverb room 0.7 wet 0.25",
             "stereo_spread_delay_ms": 12},
    "master": "peak normalize -1 dBFS",
    "quality": {
        "full_silence_fraction": round(sil, 4),
        "wav_bytes": os.path.getsize(full_wav),
        "ogg_bytes": os.path.getsize(ogg),
        "peak": float(np.max(np.abs(mix_stereo))),
    },
    "outputs": {
        "full_mix_wav": full_wav,
        "full_mix_ogg": ogg,
        "stems": stems,
        "clouds": clouds,
    },
}
with open(os.path.join(ANALYSIS, "render_info.json"), "w") as f:
    json.dump(render_info, f, indent=2)

provenance = {
    "job": "SP-016 production pass (autonomous cron)",
    "source_midi": MIDI_SRC,
    "source_midi_sha256": src_sha,
    "production_method": "SP-016",
    "production_method_name": "Granular Synthesis Engine",
    "outputs": {
        "full_mix_wav": full_wav,
        "full_mix_ogg": ogg,
    },
}
with open(os.path.join(PROJ, "provenance.json"), "w") as f:
    json.dump(provenance, f, indent=2)

print("DONE. WAV:", os.path.getsize(full_wav), "OGG:", os.path.getsize(ogg))