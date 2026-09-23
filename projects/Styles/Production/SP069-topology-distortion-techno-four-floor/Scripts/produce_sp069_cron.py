# -*- coding: utf-8 -*-
"""SP-069 Topology Distortion production pass on 001-techno-four-floor.

Source: Styles/Techno/001-techno-four-floor/MIDI/techno-four-floor.mid
        (Techno four-on-the-floor, 132 BPM, 7 tracks: Bass, Lead Square,
         String Pad, Drums, 3x Piano-default tracks)
Method: SP-069 -> sound.effects.topology_distortion
Layer : ABSOLUTE layer - Switched Discrete Distortion Topology Bank
        (Teaching Machines FuzzBillion-style): 11 serial nonlinear stages,
        each a 10-position switch (bypass/transformer/tube/jfet/ge/si/diode/
        led/cmos/opamp), 10**11 distinct circuits. Applied uniformly across
        the whole piece (single master circuit), plus same circuit per stem.
"""
import os
import shutil
import json
import subprocess
import wave
import math
from pathlib import Path
import numpy as np

from sound.render.fluidsynth import discover_soundfont
from sound.render.pipeline import RenderPipeline
from sound.effects.topology_distortion import FuzzBillion, ELEMENT_NAMES
from sound.effects.mastering import normalize_to_lufs, measure_lufs, Limiter

SRC = Path("/opt/data/repos/musicom/projects/Styles/Techno/001-techno-four-floor/MIDI/techno-four-floor.mid")
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/SP069-topology-distortion-techno-four-floor")
AUD = OUT / "Audio"
STEMS_DRY = AUD / "stems_dry"
STEMS_WET = AUD / "stems_wet"
MIDIDIR = OUT / "MIDI"
ANALYSIS = OUT / "Analysis"
SCRIPTS = OUT / "Scripts"

for d in (AUD, STEMS_DRY, STEMS_WET, MIDIDIR, ANALYSIS, SCRIPTS):
    d.mkdir(parents=True, exist_ok=True)

SR = 44100
BPM = 132.0
SEED = 20260923

SF = discover_soundfont()
assert SF and os.path.exists(SF), f"SoundFont missing: {SF}"
FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
if not os.path.exists(FLUID):
    FLUID = "fluidsynth"

shutil.copy2(str(SRC), str(MIDIDIR / SRC.name))

# ---- SP-069 circuit: "vintage console overdrive" (11 switches, 0-9) --------
CIRCUIT = (1, 2, 4, 5, 3, 1, 4, 5, 8, 1, 4)
GAIN = 2.4
IO_MODE = "line"
CIRCUIT_NAME = " -> ".join(ELEMENT_NAMES[i] for i in CIRCUIT)

# ---------------------------------------------------------------------------
# 1. Render dry full mix (SP-001 reference)
dry_full = OUT / "dry_full_mix_sp001_reference.wav"
print("Rendering dry full mix with FluidSynth...")
cmd_dry = [FLUID, "-ni", "-g", "1.2", "-R", "0", "-C", "0", "-F", str(dry_full), SF, str(SRC)]
res = subprocess.run(cmd_dry, capture_output=True, text=True)
if res.returncode != 0 or not dry_full.exists() or dry_full.stat().st_size < 1000:
    raise RuntimeError(f"FluidSynth dry render failed: {res.stderr}")
print(f"Dry full mix: {dry_full.stat().st_size} bytes")

# 2. Extract dry stems via RenderPipeline
print("Rendering stems with RenderPipeline...")
pipeline = RenderPipeline(soundfont_path=SF, fluidsynth_bin=FLUID, sample_rate=SR)
stems_raw = pipeline.render_stems(str(SRC), str(STEMS_DRY), format="wav")
print(f"Rendered {len(stems_raw)} stems: {list(stems_raw.keys())}")

# --- wav io helpers (audio stored as (channels, samples) float32) -----------
def read_wav(p):
    with wave.open(str(p), "rb") as wf:
        nch = wf.getnchannels()
        sr = wf.getframerate()
        frames = wf.getnframes()
        data = wf.readframes(frames)
        samples = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
        if nch == 1:
            audio = np.vstack([samples, samples])
        else:
            audio = samples.reshape(-1, nch).T
        return audio, sr

def write_wav(p, audio, sr=SR):
    audio_clipped = np.clip(audio, -1.0, 1.0)
    audio_int16 = (audio_clipped * 32767.0).astype(np.int16)
    if audio_int16.ndim == 1:
        nch = 1
        data = audio_int16.tobytes()
    else:
        if audio_int16.shape[0] == 2:
            nch = 2
            data = audio_int16.T.reshape(-1).tobytes()
        else:
            nch = audio_int16.shape[0]
            data = audio_int16.T.reshape(-1).tobytes()
    with wave.open(str(p), "wb") as wf:
        wf.setnchannels(nch)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(data)

# ---------------------------------------------------------------------------
# 3. Apply SP-069 distortion (single master circuit) to the full mix
fb = FuzzBillion(sample_rate=SR)
fb.code = CIRCUIT
fb.gain = GAIN
fb.io_mode = IO_MODE

dry_audio, _sr = read_wav(dry_full)
print(f"Dry full mix shape: {dry_audio.shape} (channels, samples)")

# profile the circuit harmonic signature (documentation)
prof220 = fb.profile(freq=220.0, seconds=0.5, code=CIRCUIT, gain=GAIN)
prof110 = fb.profile(freq=110.0, seconds=0.5, code=CIRCUIT, gain=GAIN)
print(f"Circuit profile 220Hz: {prof220}")
print(f"Circuit profile 110Hz: {prof110}")

dist_audio = fb.process(dry_audio, code=CIRCUIT, gain=GAIN, io_mode=IO_MODE)
dist_audio = dist_audio.astype(np.float32)

# 4. Apply the SAME circuit per dry stem (documentation + DAW import)
print("Applying SP-069 circuit per stem...")
stem_wet_paths = {}
for name, p in stems_raw.items():
    a, _ = read_wav(p)
    a_d = fb.process(a, code=CIRCUIT, gain=GAIN, io_mode=IO_MODE).astype(np.float32)
    pmax = float(np.max(np.abs(a_d)))
    if pmax > 1e-6:
        a_d = a_d * (0.89 / pmax)
    out_path = STEMS_WET / f"{name}_TOPOLOGY.wav"
    write_wav(out_path, a_d, sr=SR)
    stem_wet_paths[name] = str(out_path)
print(f"Wrote {len(stem_wet_paths)} wet stems")

# ---------------------------------------------------------------------------
# 5. Master: normalize -14 LUFS, Limiter(-1 dBFS)
#    mastering expects (samples, channels); dist_audio is (channels, samples)
master_in = dist_audio.T  # (N, 2)
normed = normalize_to_lufs(master_in, target_lufs=-14.0, sample_rate=SR)
limiter = Limiter(threshold_db=-1.0, sample_rate=SR)
limited = limiter.process(normed)  # (N, 2)
final_master = limited.T  # back to (channels, samples)

final_wav = OUT / "SP069-topology-distortion-techno-four-floor.wav"
final_ogg = OUT / "SP069-topology-distortion-techno-four-floor.ogg"
write_wav(final_wav, final_master, sr=SR)
print(f"Wrote final WAV: {final_wav} ({final_wav.stat().st_size} bytes)")

cmd_ogg = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(final_wav),
           "-codec:a", "libopus", "-application", "voip", "-b:a", "48k", str(final_ogg)]
subprocess.run(cmd_ogg, check=True)
print(f"Wrote final OGG: {final_ogg} ({final_ogg.stat().st_size} bytes)")

# ---------------------------------------------------------------------------
# 6. Verification
measured_lufs = measure_lufs(final_master.T, sample_rate=SR)
peak_val = float(np.max(np.abs(final_master)))
mono_mix = 0.5 * (final_master[0] + final_master[1])
silence_ratio = float(np.sum(np.abs(mono_mix) < 0.001) / len(mono_mix)) * 100.0
mono_corr = float(np.corrcoef(final_master[0], final_master[1])[0, 1])

# per-second RMS profile (detect mid-track gaps vs legit tail padding)
sec = SR
n_sec = len(mono_mix) // sec
rms_per_sec = []
for s in range(n_sec):
    seg = mono_mix[s * sec:(s + 1) * sec]
    rms_per_sec.append(float(np.sqrt(np.mean(seg ** 2) + 1e-12)))

print(f"Master Stats: LUFS={measured_lufs:.2f}, Peak={peak_val:.4f}, "
      f"Silence={silence_ratio:.2f}%, MonoCorr={mono_corr:.3f}")
print(f"RMS per second (first 20s): {[round(r,3) for r in rms_per_sec[:20]]}")

# Pitch verification: FFT dominant peak per 0.5s window in 50-1000 Hz
# Source key: Bb-based techno. Observed pitch classes: Bb(10) A(9) C(0) D(2) Eb(3) E(4)
REF_PCS = {0, 2, 3, 4, 9, 10}

window_len = int(0.5 * SR)
num_windows = len(mono_mix) // window_len
fft_hits = 0
valid_windows = 0
harmonic_energies = []
dominant_freqs = []

for w in range(num_windows):
    seg = mono_mix[w * window_len:(w + 1) * window_len]
    if np.max(np.abs(seg)) < 0.01:
        continue
    valid_windows += 1
    win = np.hanning(len(seg))
    fft_spec = np.abs(np.fft.rfft(seg * win))
    freqs = np.fft.rfftfreq(len(seg), 1.0 / SR)
    mask = (freqs >= 50.0) & (freqs <= 1000.0)
    if not np.any(mask):
        continue
    sub_spec = fft_spec[mask]
    sub_freqs = freqs[mask]
    peak_idx = np.argmax(sub_spec)
    dom_f = sub_freqs[peak_idx]
    dominant_freqs.append(float(dom_f))

    midi_val = 69.0 + 12.0 * math.log2(max(1.0, dom_f) / 440.0)
    round_midi = round(midi_val)
    midi_diff = abs(midi_val - round_midi)

    # harmonic energy in first 8 harmonics of dom_f (incl. fundamental)
    h_energy = 0.0
    tot_energy = float(np.sum(fft_spec ** 2)) + 1e-12
    for h in range(1, 9):
        target_f = dom_f * h
        h_mask = (freqs >= target_f - 15.0) & (freqs <= target_f + 15.0)
        h_energy += float(np.sum(fft_spec[h_mask] ** 2))
    harmonic_energies.append(h_energy / tot_energy)

    if midi_diff < 0.5:
        pc = round_midi % 12
        if pc in REF_PCS:
            fft_hits += 1

hit_rate = fft_hits / max(1, valid_windows)
mean_he = float(np.mean(harmonic_energies)) if harmonic_energies else 0.0
print(f"Pitch Verification: valid_windows={valid_windows}, hits={fft_hits}, "
      f"hit_rate={hit_rate:.4f}, mean_HE={mean_he:.4f}")

pitch_verdict = "PASS" if (hit_rate >= 0.60 and mean_he >= 0.25) else "FAIL"
print(f"Pitch Verdict: {pitch_verdict}")

# ---------------------------------------------------------------------------
# 7. Artifacts
render_stats = {
    "method": "SP-069",
    "module": "sound.effects.topology_distortion",
    "circuit": list(CIRCUIT),
    "circuit_name": CIRCUIT_NAME,
    "gain": GAIN,
    "io_mode": IO_MODE,
    "lufs": measured_lufs,
    "peak": peak_val,
    "silence_pct": silence_ratio,
    "mono_correlation": mono_corr,
    "rms_per_sec": rms_per_sec,
    "valid_windows": valid_windows,
    "hit_rate": hit_rate,
    "mean_harmonic_energy": mean_he,
    "pitch_verdict": pitch_verdict,
    "circuit_profile_220hz": prof220,
    "circuit_profile_110hz": prof110,
}
(ANALYSIS / "render_stats.json").write_text(json.dumps(render_stats, indent=2))

pitch_json = {
    "method": "SP-069",
    "project": "001-techno-four-floor",
    "source_key_pcs": sorted(REF_PCS),
    "status": pitch_verdict,
    "hit_rate": hit_rate,
    "harmonic_energy_mean": mean_he,
    "windows_analyzed": valid_windows,
    "median_freq_hz": float(np.median(dominant_freqs)) if dominant_freqs else 0.0,
}
(ANALYSIS / "pitch_verification.json").write_text(json.dumps(pitch_json, indent=2))

provenance = {
    "job": "random-style production (SP) layer-aligned",
    "date": "2026-09-23",
    "seed": SEED,
    "method": "SP-069",
    "method_module": "sound.effects.topology_distortion",
    "method_desc": "Switched Discrete Distortion Topology Bank (FuzzBillion-style)",
    "source_midi": str(SRC),
    "source_project": "Techno/001-techno-four-floor",
    "circuit": list(CIRCUIT),
    "circuit_name": CIRCUIT_NAME,
    "gain": GAIN,
    "io_mode": IO_MODE,
    "output_wav": str(final_wav),
    "output_ogg": str(final_ogg),
    "lufs": measured_lufs,
    "peak": peak_val,
    "silence_pct": silence_ratio,
    "mono_correlation": mono_corr,
    "pitch_verdict": pitch_verdict,
    "hit_rate": hit_rate,
    "he_mean": mean_he,
}
(OUT / "provenance.json").write_text(json.dumps(provenance, indent=2))
(Path("/opt/data/repos/musicom/projects/Styles/Production/.selection_cron.json")).write_text(json.dumps(provenance, indent=2))

select_json = {
    "date": "2026-09-23",
    "seed": SEED,
    "method": "SP-069",
    "method_module": "sound.effects.topology_distortion",
    "source_midi": str(SRC),
    "excluded_recent_methods": ["SP-090", "SP-033", "SP-080", "SP-083", "SP-084", "SP-072"],
}
(ANALYSIS / "select_20260923.json").write_text(json.dumps(select_json, indent=2))

try:
    if os.path.abspath(__file__) != os.path.abspath(str(SCRIPTS / "produce_sp069_cron.py")):
        shutil.copy2(__file__, str(SCRIPTS / "produce_sp069_cron.py"))
except Exception as e:
    print(f"note: script self-copy skipped: {e}")
print("Done produce script execution.")
