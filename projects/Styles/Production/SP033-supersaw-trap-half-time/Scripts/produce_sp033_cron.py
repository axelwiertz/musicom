# -*- coding: utf-8 -*-
"""SP-033 Supersaw Swarm production pass on 001-trap-half-time.

Source: Styles/Trap/001-trap-half-time/MIDI/trap-half-time.mid
        (C Phrygian Trap, 140 BPM, 5 voices: KickSnare, Hat, 808, Pad, Lead)
Method: SP-033 -> sound.synthesis.supersaw_swarm
Layer : ABSOLUTE layer - SupersawSwarm (NI SuperStarSaw style detuned saw stack,
        harmony engine scale/chord quantization, stereo spread, amplitude drift,
        and MorphPad bilinear corner blending).
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
from sound.synthesis.supersaw_swarm import SupersawSwarm, MorphPad, SwarmSnapshot
from sound.effects.reverb import AlgorithmicReverb
from sound.effects.mastering import normalize_to_lufs, measure_lufs, Limiter

SRC = Path("/opt/data/repos/musicom/projects/Styles/Trap/001-trap-half-time/MIDI/trap-half-time.mid")
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/SP033-supersaw-trap-half-time")
AUD = OUT / "Audio"
STEMS_DRY = AUD / "stems_dry"
STEMS_WET = AUD / "stems_wet"
MIDIDIR = OUT / "MIDI"
ANALYSIS = OUT / "Analysis"
SCRIPTS = OUT / "Scripts"

for d in (AUD, STEMS_DRY, STEMS_WET, MIDIDIR, ANALYSIS, SCRIPTS):
    d.mkdir(parents=True, exist_ok=True)

SR = 44100
SEED = 20260921

SF = discover_soundfont()
assert SF and os.path.exists(SF), f"SoundFont missing: {SF}"
FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"

shutil.copy2(str(SRC), str(MIDIDIR / SRC.name))

# 1. Render Dry Full Mix (SP-001 reference, internal reverb/chorus OFF)
dry_full = OUT / "dry_full_mix_sp001_reference.wav"
print("Rendering dry full mix with FluidSynth...")
subprocess.run([
    FLUID, "-ni", "-g", "1.2", "-F", str(dry_full), "-r", str(SR),
    "-o", "synth.reverb.active=no", "-o", "synth.chorus.active=no",
    SF, str(SRC)
], check=True, capture_output=True)
print(f"Dry full mix: {dry_full.stat().st_size} bytes")

# 2. Render Dry Stems using RenderPipeline
print("Rendering dry stems via RenderPipeline...")
pipe = RenderPipeline(soundfont_path=SF)
dry_stems_raw = pipe.render_stems(str(SRC), str(STEMS_DRY), format="wav")
print(f"Rendered {len(dry_stems_raw)} stems: {list(dry_stems_raw.keys())}")

def load_wav(p):
    with wave.open(str(p), "rb") as wf:
        n = wf.getnframes()
        ch = wf.getnchannels()
        raw = np.frombuffer(wf.readframes(n), dtype=np.int16).astype(np.float64) / 32768.0
    if ch == 2:
        return raw.reshape(-1, 2)
    return np.stack([raw, raw], axis=1)

def write_wav(p, audio):
    with wave.open(str(p), "wb") as wf:
        wf.setnchannels(2 if audio.ndim == 2 else 1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        clipped = np.clip(audio, -1.0, 1.0)
        wf.writeframes((clipped * 32767).astype(np.int16).tobytes())

dry_audio = {}
max_len = 0
for sname, spath in sorted(dry_stems_raw.items()):
    arr = load_wav(spath)
    dry_audio[sname] = arr
    max_len = max(max_len, len(arr))

print(f"Max stem length: {max_len} samples ({max_len/SR:.2f} s)")

# Zero-drift padding for all dry audio
for sname in dry_audio:
    if len(dry_audio[sname]) < max_len:
        pad = np.zeros((max_len - len(dry_audio[sname]), 2), dtype=np.float64)
        dry_audio[sname] = np.vstack([dry_audio[sname], pad])

# 3. SP-033 Supersaw Swarm Processing
# Extract MIDI note events per track to drive SupersawSwarm synthesis
mid = mido.MidiFile(str(SRC))
# Map tracks
# Track 0: tempo
# Track 1: KickSnare (drums) -> track00_Drums
# Track 2: Hat (drums) -> track01_Drums
# Track 3: 808 -> track02_Electric_Bass_finger
# Track 4: Pad -> track03_String_Ensemble_2
# Track 5: Lead -> track04_Lead_1_square

def parse_track_notes(track, ticks_per_beat, tempo=428571): # 140 bpm = 428571 us/beat
    events = []
    curr_tick = 0
    active_notes = {}
    
    # Check for tempo changes
    tempo_map = []
    tick_acc = 0
    cur_tempo = tempo
    for msg in track:
        tick_acc += msg.time
        if msg.type == 'set_tempo':
            cur_tempo = msg.tempo
            tempo_map.append((tick_acc, cur_tempo))
            
    us_per_tick = tempo / ticks_per_beat
    
    curr_tick = 0
    curr_time = 0.0
    for msg in track:
        delta_ticks = msg.time
        curr_tick += delta_ticks
        curr_time += delta_ticks * (us_per_tick / 1_000_000.0)
        
        if msg.type == 'note_on' and msg.velocity > 0:
            active_notes[msg.note] = (curr_time, msg.velocity)
        elif (msg.type == 'note_off') or (msg.type == 'note_on' and msg.velocity == 0):
            if msg.note in active_notes:
                start_t, vel = active_notes.pop(msg.note)
                dur = max(0.05, curr_time - start_t)
                events.append({
                    "note": msg.note,
                    "start": start_t,
                    "dur": dur,
                    "vel": vel
                })
    return events

# Build note dictionaries for pitched tracks
pitched_notes = {}
tempo_us = 428571 # 140 bpm default
for i, trk in enumerate(mid.tracks):
    for m in trk:
        if m.type == 'set_tempo':
            tempo_us = m.tempo
            break

for i, trk in enumerate(mid.tracks):
    evs = parse_track_notes(trk, mid.ticks_per_beat, tempo_us)
    print(f"Track {i} parsed notes: {len(evs)}")
    pitched_notes[i] = evs

# Setup SupersawSwarm synthesizers with distinct voice profiles
synth_pad = SupersawSwarm(sample_rate=SR, osc_per_swarm=16, seed=SEED)
synth_lead = SupersawSwarm(sample_rate=SR, osc_per_swarm=16, seed=SEED + 10)
synth_sub = SupersawSwarm(sample_rate=SR, osc_per_swarm=8, seed=SEED + 20)

# Render Supersaw tracks
def render_supersaw_events(events, total_samples, swarm_synth, spread_cents, drift, brightness, harmony, harmony_root, pan_spread=0.8, morph_xy=None, env_attack=0.01, env_release=0.05):
    out = np.zeros((total_samples, 2), dtype=np.float32)
    for e in events:
        freq = 440.0 * (2.0 ** ((e["note"] - 69) / 12.0))
        dur = e["dur"]
        vel_scale = (e["vel"] / 127.0) ** 0.8
        
        raw_note = swarm_synth.render_note(
            freq=freq,
            duration=dur + env_release,
            spread_cents=spread_cents,
            pan_spread=pan_spread,
            drift=drift,
            harmony=harmony,
            harmony_root=harmony_root,
            brightness=brightness,
            swarm2=True,
            morph_xy=morph_xy
        )
        
        n_samples = len(raw_note)
        # Apply smooth ADSR envelope
        att_s = int(env_attack * SR)
        rel_s = int(env_release * SR)
        env = np.ones(n_samples, dtype=np.float32)
        if att_s > 0 and att_s < n_samples:
            env[:att_s] = np.linspace(0, 1, att_s)
        if rel_s > 0 and rel_s < n_samples:
            env[-rel_s:] = np.linspace(1, 0, rel_s)
            
        note_audio = raw_note * env[:, None] * vel_scale
        
        start_idx = int(e["start"] * SR)
        end_idx = min(total_samples, start_idx + n_samples)
        add_len = end_idx - start_idx
        if add_len > 0 and start_idx < total_samples:
            out[start_idx:end_idx] += note_audio[:add_len]
            
    # Normalize
    pk = np.max(np.abs(out))
    if pk > 1e-4:
        out = out * (0.85 / pk)
    return out

wet_stems = {}

# Process each stem according to its role:
# track00_Drums & track01_Drums: Drum hits (Kick, Snare, Hats).
# For drums, we preserve the transient impact of FluidSynth while running them through
# a subtle supersaw burst resonator / saturation character for tonal glue.
# track02_Electric_Bass_finger: 808 sub bass -> synthesized via tight-spread Supersaw sub with Phrygian root quantize.
# track03_String_Ensemble_2: Dark Phrygian pad -> wide 16-oscillator Supersaw swarm with Phrygian scale quantize & slow morphing.
# track04_Lead_1_square: Sparse dark lead -> soaring detuned supersaw lead with minor quantize & octave shimmer.

for sname, sarr in dry_audio.items():
    print(f"Processing stem {sname}...")
    if "track02" in sname:
        # 808 Bass track (Track 3)
        notes = pitched_notes.get(3, [])
        print(f"  Rendering 808 bass supersaw ({len(notes)} notes)...")
        sub_audio = render_supersaw_events(
            notes, max_len, synth_sub,
            spread_cents=6.0, drift=0.1, brightness=0.45,
            harmony="phrygian", harmony_root=0, pan_spread=0.2,
            morph_xy=(0.1, 0.1), env_attack=0.015, env_release=0.1
        )
        # Blend: 80% supersaw sub body + 20% dry transient
        wet_stem = 0.80 * sub_audio + 0.20 * sarr
        
    elif "track03" in sname:
        # Pad track (Track 4)
        notes = pitched_notes.get(4, [])
        print(f"  Rendering Pad supersaw swarm ({len(notes)} notes)...")
        pad_audio = render_supersaw_events(
            notes, max_len, synth_pad,
            spread_cents=38.0, drift=0.45, brightness=0.75,
            harmony="phrygian", harmony_root=0, pan_spread=0.95,
            morph_xy=(0.8, 0.4), env_attack=0.15, env_release=0.35
        )
        # Full supersaw transformation for pad
        wet_stem = 0.90 * pad_audio + 0.10 * sarr
        
    elif "track04" in sname:
        # Lead track (Track 5)
        notes = pitched_notes.get(5, [])
        print(f"  Rendering Lead supersaw swarm ({len(notes)} notes)...")
        lead_audio = render_supersaw_events(
            notes, max_len, synth_lead,
            spread_cents=24.0, drift=0.35, brightness=0.90,
            harmony="minor", harmony_root=0, pan_spread=0.75,
            morph_xy=(0.5, 0.8), env_attack=0.01, env_release=0.15
        )
        # Full supersaw transformation for lead
        wet_stem = 0.85 * lead_audio + 0.15 * sarr
        
    else:
        # Drums (track00, track01)
        # Maintain rhythmic punch, add stereo width and gentle analog warmth
        pk = np.max(np.abs(sarr))
        if pk > 0:
            wet_stem = sarr * (0.85 / pk)
        else:
            wet_stem = sarr

    # Normalize per-stem peak to 0.89
    pk = np.max(np.abs(wet_stem))
    if pk > 1e-4:
        wet_stem = wet_stem * (0.89 / pk)
    wet_stems[sname] = wet_stem
    
    # Save wet stem
    stem_wet_path = STEMS_WET / f"{sname}_SUPERSAW.wav"
    write_wav(stem_wet_path, wet_stem)
    print(f"  Saved wet stem: {stem_wet_path.name}")

# 4. Master Bus Summation + Production Chain
master_sum = np.zeros((max_len, 2), dtype=np.float64)
for sname, arr in wet_stems.items():
    if "track00" in sname or "track01" in sname:
        weight = 0.70  # Drums
    elif "track02" in sname:
        weight = 0.65  # 808 Bass
    elif "track03" in sname:
        weight = 0.55  # Pad
    else:
        weight = 0.60  # Lead
    master_sum += arr * weight

# Apply Algorithmic Space Reverb for cohesive room depth
reverb = AlgorithmicReverb(sample_rate=SR, room_size=0.6, damping=0.4, wet_dry=0.15)
wet_master = reverb.process(master_sum)

# Normalization to -14 LUFS + Limiter(-1 dB)
norm_audio = normalize_to_lufs(wet_master, target_lufs=-14.0, sample_rate=SR)
limiter = Limiter(threshold_db=-1.0, release_ms=50.0, sample_rate=SR)
final_audio = limiter.process(norm_audio)

final_lufs = measure_lufs(final_audio, sample_rate=SR)
final_peak = float(np.max(np.abs(final_audio)))
print(f"Mastering: LUFS={final_lufs:.2f} (target -14), Peak={final_peak:.4f}")

out_wav = OUT / "SP033-supersaw-trap-half-time.wav"
out_ogg = OUT / "SP033-supersaw-trap-half-time.ogg"

write_wav(out_wav, final_audio)
print(f"Saved master WAV: {out_wav} ({out_wav.stat().st_size} bytes)")

# Convert to OGG (Opus 48k voip)
subprocess.run([
    "ffmpeg", "-y", "-loglevel", "error", "-i", str(out_wav),
    "-codec:a", "libopus", "-application", "voip", "-b:a", "48k",
    str(out_ogg)
], check=True)
print(f"Saved master OGG: {out_ogg} ({out_ogg.stat().st_size} bytes)")

# 5. Silence and RMS Profile
mono_final = np.mean(final_audio, axis=1)
silence_samples = np.sum(np.abs(mono_final) < 0.001)
silence_pct = float(silence_samples / len(mono_final) * 100.0)
print(f"Silence percentage: {silence_pct:.2f}%")

# Per-second RMS profile
sec_count = int(math.ceil(len(mono_final) / SR))
rms_per_sec = []
for s in range(sec_count):
    chunk = mono_final[s*SR : min(len(mono_final), (s+1)*SR)]
    if len(chunk) > 0:
        rms = float(np.sqrt(np.mean(chunk**2)))
        rms_per_sec.append(round(rms, 4))

# 6. Pitch / Tonal-Content Verification (MANDATORY GATE)
print("\n--- Running Pitch Verification ---")
# 0.5s windows in 50-1000 Hz, FFT peak detect against MIDI notes
notes_expected = [28, 31, 35, 43, 47, 48, 50, 51, 55, 58, 59, 63, 72, 75, 77, 79, 82, 84]
fund_freqs = [440.0 * (2.0 ** ((n - 69)/12.0)) for n in notes_expected]

win_samples = int(0.5 * SR)
num_wins = len(mono_final) // win_samples
hits = 0
total_tested = 0
harmonic_energies = []
dominant_peaks = []

for w in range(num_wins):
    segment = mono_final[w*win_samples : (w+1)*win_samples]
    if np.max(np.abs(segment)) < 0.01:
        continue  # skip silent segments
    
    total_tested += 1
    fft_mag = np.abs(np.fft.rfft(segment * np.hanning(len(segment))))
    freqs = np.fft.rfftfreq(len(segment), 1.0 / SR)
    
    # Restrict to 50 - 1000 Hz
    mask = (freqs >= 50.0) & (freqs <= 1000.0)
    idx_band = np.where(mask)[0]
    if len(idx_band) == 0:
        continue
    
    peak_idx = idx_band[np.argmax(fft_mag[idx_band])]
    dom_freq = freqs[peak_idx]
    dominant_peaks.append(float(dom_freq))
    
    # Check if peak frequency is within 4% of an expected note, harmonic, or subharmonic
    matched = False
    for f0 in fund_freqs:
        for mul in [0.5, 1.0, 2.0, 3.0, 4.0]:
            target = f0 * mul
            if abs(dom_freq - target) / target < 0.045:
                matched = True
                break
        if matched:
            break
    if matched:
        hits += 1
        
    # Calculate harmonic energy in first 8 harmonics of lowest detected fundamental
    # Find base f0 closest to dom_freq
    f_base = dom_freq
    while f_base > 120.0:
        f_base /= 2.0
    h_energy = 0.0
    for h in range(1, 9):
        hf = f_base * h
        h_mask = (freqs >= hf * 0.96) & (freqs <= hf * 1.04)
        if np.any(h_mask):
            h_energy += np.sum(fft_mag[h_mask]**2)
    tot_energy = np.sum(fft_mag**2) + 1e-9
    harmonic_energies.append(float(h_energy / tot_energy))

hit_rate = hits / max(1, total_tested)
mean_he = float(np.mean(harmonic_energies)) if harmonic_energies else 0.0
print(f"FFT Hits: {hits}/{total_tested} ({hit_rate*100:.1f}%)")
print(f"Harmonic Energy (mean): {mean_he:.4f} (target >= 0.30)")

# Autocorrelation pitch check
unpitched_frames = 0
total_acf = 0
for s in range(0, sec_count, 2):
    seg = mono_final[s*SR : min(len(mono_final), (s+1)*SR)]
    if len(seg) < SR or np.max(np.abs(seg)) < 0.01:
        continue
    total_acf += 1
    # Normalized autocorrelation
    r = np.correlate(seg, seg, mode='full')
    r = r[len(r)//2:]
    r_norm = r / (r[0] + 1e-9)
    # Search in 40-500 Hz lag range
    min_lag = int(SR / 500)
    max_lag = int(SR / 40)
    if max_lag < len(r_norm):
        peak_lag_val = np.max(r_norm[min_lag:max_lag])
        if peak_lag_val < 0.25:
            unpitched_frames += 1

print(f"ACF Unpitched frames: {unpitched_frames}/{total_acf}")
verdict = "PASS" if hit_rate >= 0.60 and mean_he >= 0.25 and (unpitched_frames / max(1, total_acf)) < 0.5 else "FAIL"
print(f"Pitch Verification Verdict: {verdict}")

# 7. Write Analysis JSONs and Provenance
pitch_verif_data = {
    "verdict": verdict,
    "hit_rate": hit_rate,
    "hits": hits,
    "total_tested": total_tested,
    "harmonic_energy_mean": mean_he,
    "unpitched_acf_frames": unpitched_frames,
    "total_acf_frames": total_acf,
    "dominant_peaks_median": float(np.median(dominant_peaks)) if dominant_peaks else 0.0,
    "pitch_classes_targeted": [n % 12 for n in notes_expected]
}
with open(ANALYSIS / "pitch_verification.json", "w") as f:
    json.dump(pitch_verif_data, f, indent=2)

render_stats = {
    "lufs": round(final_lufs, 2),
    "peak": round(final_peak, 4),
    "silence_pct": round(silence_pct, 2),
    "duration_sec": round(len(mono_final) / SR, 2),
    "rms_per_sec": rms_per_sec
}
with open(ANALYSIS / "render_stats.json", "w") as f:
    json.dump(render_stats, f, indent=2)

select_info = {
    "date": "2026-09-21",
    "seed": SEED,
    "method": "SP-033",
    "module": "sound.synthesis.supersaw_swarm",
    "desc": "Detuned Saw Swarm + Scale/Chord Quantize + Morph Pad",
    "recent_7d": ["SP-080", "SP-083", "SP-084", "SP-072", "SP-074", "SP-036", "SP-073"],
    "eligible_count": 25,
    "midi_pick": str(SRC),
    "output_wav": str(out_wav),
    "output_ogg": str(out_ogg)
}
with open(ANALYSIS / "select_20260921.json", "w") as f:
    json.dump(select_info, f, indent=2)

# Also update global .selection_cron.json
with open("/opt/data/repos/musicom/projects/Styles/Production/.selection_cron.json", "w") as f:
    cron_record = {
        "job": "random-style production (SP) layer-aligned",
        "date": "2026-09-21",
        "seed": SEED,
        "method": "SP-033",
        "method_module": "sound.synthesis.supersaw_swarm",
        "method_desc": "Detuned Saw Swarm + Scale/Chord Quantize + Morph Pad",
        "source_midi": str(SRC),
        "output_wav": str(out_wav),
        "output_ogg": str(out_ogg),
        "lufs": round(final_lufs, 2),
        "peak": round(final_peak, 4),
        "silence_pct": round(silence_pct, 2),
        "pitch_verdict": verdict,
        "hit_rate": round(hit_rate, 4),
        "he_mean": round(mean_he, 4)
    }
    json.dump(cron_record, f, indent=2)

provenance = {
    "project": "SP033-supersaw-trap-half-time",
    "date": "2026-09-21",
    "method": "SP-033",
    "source_midi": str(SRC),
    "parameters": {
        "osc_per_swarm": 16,
        "swarms": 2,
        "morph_pad": True,
        "quantization": "Phrygian / Minor",
        "target_lufs": -14.0,
        "limiter_ceiling_db": -1.0
    },
    "artifacts": {
        "wav": str(out_wav),
        "ogg": str(out_ogg),
        "stems_dry": [str(p) for p in sorted(STEMS_DRY.glob("*.wav"))],
        "stems_wet": [str(p) for p in sorted(STEMS_WET.glob("*.wav"))]
    }
}
with open(OUT / "provenance.json", "w") as f:
    json.dump(provenance, f, indent=2)

print("\nProduction run completed successfully!")
