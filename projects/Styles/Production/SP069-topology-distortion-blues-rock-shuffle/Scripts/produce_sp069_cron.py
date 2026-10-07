# -*- coding: utf-8 -*-
"""SP-069 Topology Distortion production pass on 018-rock-apprenticeship Study 02.

Source: Styles/Hybrid/018-rock-apprenticeship/MIDI/study-02-blues-rock-shuffle-engine.mid
        (Blues-rock shuffle boogie in E blues, 112 BPM, 4/4 triplet shuffle,
         5 tracks: ch0 Overdriven Guitar 29, ch1 Electric Bass finger 33,
         ch2 Distortion Guitar 30, + ch9 drums)
Method: SP-069 -> sound.effects.topology_distortion (FuzzBillion-style)
Layer : ABSOLUTE layer - Switched Discrete Distortion Topology Bank. 11 serial
        nonlinear stages, each a 10-position switch (0 bypass, 1 transformer,
        2 tube, 3 JFET, 4 germanium-pair, 5 silicon-pair, 6 single-diode clamp,
        7 LED-pair, 8 CMOS hard clip, 9 op-amp rail foldback). 10**11 circuits.
"""
import os
import shutil
import json
import subprocess
import wave
import math
from pathlib import Path
import numpy as np
import mido

from sound.render.fluidsynth import discover_soundfont
from sound.render.pipeline import RenderPipeline
from sound.effects.topology_distortion import FuzzBillion, ELEMENT_NAMES
from sound.effects.mastering import normalize_to_lufs, measure_lufs, Limiter

SRC = Path("/opt/data/repos/musicom/projects/Styles/Hybrid/018-rock-apprenticeship/MIDI/study-02-blues-rock-shuffle-engine.mid")
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/SP069-topology-distortion-blues-rock-shuffle")
AUD = OUT / "Audio"
STEMS_DRY = AUD / "stems_dry"
STEMS_WET = AUD / "stems_wet"
MIDIDIR = OUT / "MIDI"
ANALYSIS = OUT / "Analysis"
SCRIPTS = OUT / "Scripts"

for d in (AUD, STEMS_DRY, STEMS_WET, MIDIDIR, ANALYSIS, SCRIPTS):
    d.mkdir(parents=True, exist_ok=True)

SR = 44100
BPM = 112.0
SEED = 20261007

# SP-069 parameters (absolute layer, applied to whole mix)
CIRCUIT = (3, 5, 1, 4, 9, 9, 9, 1, 4, 2, 8)   # random_circuit(seed=20261007)
GAIN = 2.2
IO_MODE = "line"

SF = discover_soundfont()
assert SF and os.path.exists(SF), f"SoundFont missing: {SF}"
FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"

shutil.copy2(str(SRC), str(MIDIDIR / SRC.name))

# Compute source pitch-class vocabulary from the MIDI (for pitch verification)
_src_pcs = set()
for _tr in mido.MidiFile(str(SRC)).tracks:
    for _m in _tr:
        if _m.type == "note_on" and _m.velocity > 0:
            _src_pcs.add(_m.note % 12)
SRC_PCS = sorted(_src_pcs)
print("Source PCS:", SRC_PCS)


def read_wav(p):
    with wave.open(str(p), "rb") as wf:
        nch = wf.getnchannels()
        sr = wf.getframerate()
        data = wf.readframes(wf.getnframes())
        samples = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
        if nch == 1:
            audio = np.vstack([samples, samples])
        else:
            audio = samples.reshape(-1, nch).T
        return audio, sr


def write_wav(p, audio, sr=SR):
    audio = np.clip(audio, -1.0, 1.0)
    if audio.ndim == 1:
        nch = 1
        interleaved = audio
    elif audio.shape[0] == 2:
        nch = 2
        interleaved = audio.T.reshape(-1)
    else:
        nch = audio.shape[0]
        interleaved = audio.T.reshape(-1)
    data = (interleaved * 32767.0).astype(np.int16).tobytes()
    with wave.open(str(p), "wb") as wf:
        wf.setnchannels(nch)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(data)


def mono_correlation(audio2n):
    L = audio2n[0]
    R = audio2n[1]
    num = np.sum(L * R)
    den = math.sqrt(np.sum(L * L) * np.sum(R * R)) + 1e-12
    return float(num / den)


# 1. Dry full mix (SP-001 reference)
dry_full = OUT / "dry_full_mix_sp001_reference.wav"
print("Rendering dry full mix with FluidSynth...")
cmd_dry = [FLUID, "-ni", "-g", "1.2", "-R", "0", "-C", "0", "-F", str(dry_full), SF, str(SRC)]
res = subprocess.run(cmd_dry, capture_output=True, text=True)
if res.returncode != 0 or not dry_full.exists() or dry_full.stat().st_size < 1000:
    raise RuntimeError(f"FluidSynth dry render failed: {res.stderr}")
print(f"Dry full mix: {dry_full.stat().st_size} bytes")

# 2. Dry stems via RenderPipeline
print("Rendering dry stems with RenderPipeline...")
pipeline = RenderPipeline(soundfont_path=SF, fluidsynth_bin=FLUID, sample_rate=SR)
stems_raw = pipeline.render_stems(str(SRC), str(STEMS_DRY), format="wav")
print(f"Rendered {len(stems_raw)} stems: {list(stems_raw.keys())}")

# 3. Apply SP-069 Topology Distortion to the full mix (absolute layer)
dry_audio, sr = read_wav(dry_full)
print(f"Dry mix shape: {dry_audio.shape}, sr={sr}")

fb = FuzzBillion(sample_rate=SR)
fb.code = CIRCUIT
chain = " -> ".join(ELEMENT_NAMES[i] for i in CIRCUIT)
print(f"Circuit ({GAIN} gain, {IO_MODE}): {chain}")
prof = fb.profile(freq=220.0, code=CIRCUIT, gain=GAIN)
print(f"Circuit profile @220Hz: centroid={prof['centroid']:.1f} Hz, harmonic_ratio={prof['harmonic_ratio']:.4f}, peak={prof['peak']:.4f}")

wet_audio = fb.process(dry_audio, code=CIRCUIT, gain=GAIN, io_mode=IO_MODE)  # (2, N) float64
print(f"Wet mix shape: {wet_audio.shape}")

# 4. Master: normalize to -14 LUFS, then Limiter(-1 dBFS)
print("Mastering: normalize_to_lufs(-14) + Limiter(-1 dBFS)...")
wet_tm = np.asarray(wet_audio).T.astype(np.float32)  # (N, 2) time-major
lufs_norm = normalize_to_lufs(wet_tm, target_lufs=-14.0, sample_rate=SR)
limiter = Limiter(threshold_db=-1.0, sample_rate=SR)
final_tm = limiter.process(lufs_norm)  # (N, 2)
final_master = final_tm.T  # (2, N)

final_wav = OUT / "SP069-topology-distortion-blues-rock-shuffle.wav"
final_ogg = OUT / "SP069-topology-distortion-blues-rock-shuffle.ogg"
write_wav(final_wav, final_master, sr=SR)
print(f"Wrote final WAV: {final_wav} ({final_wav.stat().st_size} bytes)")

cmd_ogg = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(final_wav),
           "-codec:a", "libopus", "-application", "voip", "-b:a", "48k", str(final_ogg)]
subprocess.run(cmd_ogg, check=True)
print(f"Wrote final OGG: {final_ogg} ({final_ogg.stat().st_size} bytes)")

# 5. Per-stem wet copies (same circuit per voice, convenience for DAW import)
print("Applying same circuit to dry stems...")
for name, path in stems_raw.items():
    s_audio, s_sr = read_wav(path)
    s_wet = fb.process(s_audio, code=CIRCUIT, gain=GAIN, io_mode=IO_MODE)
    s_wet = np.asarray(s_wet).astype(np.float32)
    out_name = name + "_TOPOLOGY"
    write_wav(STEMS_WET / f"{out_name}.wav", s_wet, sr=s_sr)
print(f"Wrote {len(stems_raw)} wet stems to {STEMS_WET}")

# 6. Verification
measured_lufs = float(measure_lufs(final_tm, sample_rate=SR))
peak_val = float(np.max(np.abs(final_master)))
mono_mix = 0.5 * (final_master[0] + final_master[1])
silence_ratio = float(np.sum(np.abs(mono_mix) < 0.001) / len(mono_mix)) * 100.0
mono_corr = mono_correlation(final_master)
print(f"Master Stats: LUFS={measured_lufs:.2f}, Peak={peak_val:.4f}, Silence={silence_ratio:.2f}%, MonoCorr={mono_corr:.3f}")


def pitch_verify(audio_2n, pcs):
    """Return (hit_rate, mean_harmonic_energy, valid_windows, dominant_freqs)."""
    mono = 0.5 * (audio_2n[0] + audio_2n[1])
    window_len = int(0.5 * SR)
    num_windows = len(mono) // window_len
    fft_hits = 0
    valid_windows = 0
    harmonic_energies = []
    dominant_freqs = []
    for w in range(num_windows):
        seg = mono[w * window_len:(w + 1) * window_len]
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
        dom_f = sub_freqs[np.argmax(sub_spec)]
        dominant_freqs.append(float(dom_f))
        midi_val = 69.0 + 12.0 * math.log2(max(1.0, dom_f) / 440.0)
        round_midi = round(midi_val)
        midi_diff = abs(midi_val - round_midi)
        tot_energy = np.sum(fft_spec ** 2) + 1e-12
        h_energy = 0.0
        for h in range(1, 9):
            target_f = dom_f * h
            h_mask = (freqs >= target_f - 15.0) & (freqs <= target_f + 15.0)
            h_energy += np.sum(fft_spec[h_mask] ** 2)
        harmonic_energies.append(h_energy / tot_energy)
        if midi_diff < 0.45:
            pc = round_midi % 12
            if pc in pcs:
                fft_hits += 1
    hit_rate = fft_hits / max(1, valid_windows)
    mean_he = float(np.mean(harmonic_energies)) if harmonic_energies else 0.0
    return hit_rate, mean_he, valid_windows, dominant_freqs


# Pitch verification: blues-rock shuffle in E blues; reference = source PCS
hit_rate, mean_he, valid_windows, dominant_freqs = pitch_verify(final_master, SRC_PCS)

# Dry reference comparison (SP-001 no-distortion render) — the tonal baseline
dry_hit, dry_he, dry_valid, _ = pitch_verify(dry_audio, SRC_PCS)
he_retention = (mean_he / dry_he) if dry_he > 0 else 0.0

# Verdict: distortion is tonal if (a) pitch hit-rate stays high AND
# (b) harmonic energy did not collapse vs the clean reference (noise would
# collapse HE to ~4-16%; we require >=50% retention).
pitch_verdict = "PASS" if (hit_rate >= 0.60 and he_retention >= 0.50) else "FAIL"
print(f"Pitch Verification: valid={valid_windows}, hits={hit_rate:.4f}, mean_HE_wet={mean_he:.4f}")
print(f"Dry reference: hit={dry_hit:.4f}, mean_HE_dry={dry_he:.4f}, HE_retention={he_retention:.3f}")
print(f"Pitch Verdict: {pitch_verdict}")

# Silence/RMS profile
rms = float(np.sqrt(np.mean(mono_mix ** 2)))
print(f"Overall RMS: {rms:.4f}, silence: {silence_ratio:.2f}%")

# 7. Write analysis + provenance
(ANALYSIS / "render_stats.json").write_text(json.dumps({
    "lufs": measured_lufs, "peak": peak_val, "silence_pct": silence_ratio,
    "mono_correlation": mono_corr, "rms": rms,
    "valid_windows": valid_windows, "hit_rate": hit_rate,
    "mean_harmonic_energy": mean_he, "pitch_verdict": pitch_verdict,
    "dry_mean_harmonic_energy": dry_he, "he_retention": he_retention,
}, indent=2))

(ANALYSIS / "pitch_verification.json").write_text(json.dumps({
    "method": "SP-069", "project": "018-rock-apprenticeship",
    "scale": "E blues (source PCS)", "pcs": SRC_PCS,
    "status": pitch_verdict, "hit_rate": hit_rate,
    "harmonic_energy_mean": mean_he, "dry_harmonic_energy_mean": dry_he,
    "he_retention": he_retention, "windows_analyzed": valid_windows,
    "median_freq_hz": float(np.median(dominant_freqs)) if dominant_freqs else 0.0,
}, indent=2))

provenance = {
    "job": "random-style production (SP) layer-aligned",
    "date": "2026-10-07",
    "seed": SEED,
    "method": "SP-069",
    "method_module": "sound.effects.topology_distortion",
    "method_desc": "Switched Discrete Distortion Topology Bank (FuzzBillion-style)",
    "params": {"circuit": list(CIRCUIT), "gain": GAIN, "io_mode": IO_MODE, "fs": SR},
    "source_midi": str(SRC),
    "output_wav": str(final_wav),
    "output_ogg": str(final_ogg),
    "lufs": measured_lufs, "peak": peak_val, "silence_pct": silence_ratio,
    "mono_correlation": mono_corr,
    "pitch_verdict": pitch_verdict, "hit_rate": hit_rate, "he_mean": mean_he,
    "dry_he_mean": dry_he, "he_retention": he_retention,
}
(OUT / "provenance.json").write_text(json.dumps(provenance, indent=2))
(Path("/opt/data/repos/musicom/projects/Styles/Production/.selection_cron.json")).write_text(json.dumps(provenance, indent=2))

(ANALYSIS / "select_20261007.json").write_text(json.dumps({
    "date": "2026-10-07", "method": "SP-069",
    "method_module": "sound.effects.topology_distortion",
    "source_midi": str(SRC),
    "recent_excluded": sorted(["SP-021", "SP-072", "SP-075", "SP-080", "SP-083", "SP-086", "SP-091"]),
    "registry_total": 40,
    "note": "first draw landed on Country/012-country-country-uke/MIDI/country_uke_8bars.mid (degenerate: tpb 10080, no programs) -> re-rolled to well-formed candidate",
}, indent=2))

print("Done.")
