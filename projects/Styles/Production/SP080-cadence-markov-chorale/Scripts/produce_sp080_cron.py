# -*- coding: utf-8 -*-
"""SP-080 Cadence Engine rhythmic variator production pass.

Source: Styles/Experimental/064-markov-constraint-chorale/MIDI/064-markov-constraint-chorale.mid
        (G minor chorale, 84 BPM, 4 voices: Flute, 2x StringEnsemble, Bass)
Method: SP-080 -> sound.generators.cadence_variator
Layer : ABSOLUTE layer - CadenceEngine (Emergence Audio Envoy style) with 4 independent
        blocks, velocity/pitch/length/pan/combi-LP-HP lanes, master LFO, and FluxRandomizer.
        Applied across all voices and master bus.
"""
import os
import shutil
import json
import subprocess
import wave
from pathlib import Path
import numpy as np
import mido

from sound.render.fluidsynth import discover_soundfont
from sound.render.pipeline import RenderPipeline
from sound.generators.cadence_variator import CadenceEngine, FluxRandomizer
from sound.effects.filter import StateVariableFilter
from sound.effects.reverb import AlgorithmicReverb
from sound.effects.mastering import normalize_to_lufs, measure_lufs, Limiter

SRC = Path("/opt/data/repos/musicom/projects/Styles/Experimental/064-markov-constraint-chorale/MIDI/064-markov-constraint-chorale.mid")
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/SP080-cadence-markov-chorale")
AUD = OUT / "Audio"
STEMS_DRY = AUD / "stems_dry"
STEMS_WET = AUD / "stems_wet"
MIDIDIR = OUT / "MIDI"
ANALYSIS = OUT / "Analysis"
SCRIPTS = OUT / "Scripts"

for d in (AUD, STEMS_DRY, STEMS_WET, MIDIDIR, ANALYSIS, SCRIPTS):
    d.mkdir(parents=True, exist_ok=True)

SR = 44100
SEED = 20260920

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

# Determine max length across all stems
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

# 3. Build CadenceEngine and Per-Voice Modulation Profiles
# 064-markov-constraint-chorale is 84 BPM, 8 bars of 4/4 = 32 beats. Total time ~22.86s
BPM = 84.0
eng = CadenceEngine(bpm=BPM, master_lfo_rate=0.7, seed=SEED)

# Voice profiles mapping CadenceEngine layers & parameters
# Stems: track00_Flute, track01_String_Ensemble_1, track02_String_Ensemble_2, track03_Acoustic_Bass
voice_configs = {
    "track00_Flute": {
        "role": "Soprano Lead",
        "block_steps": [8, 6, 8, 7],   # Polyrhythmic blocks
        "rate": 2.0,                   # 16th note subdivision
        "direction": "forward",
        "feel": "straight",
        "flux_depth": 0.22,
        "flux_blocks": [0, 2],
        "hp_base": 250.0,
        "lp_base": 4500.0,
        "pan_width": 0.35,
        "gain": 1.05
    },
    "track01_String_Ensemble_1": {
        "role": "Alto Counterline",
        "block_steps": [7, 8, 6, 8],
        "rate": 1.5,                   # Dotted rhythm feel
        "direction": "pingpong",
        "feel": "swing",
        "flux_depth": 0.28,
        "flux_blocks": [1, 3],
        "hp_base": 180.0,
        "lp_base": 3800.0,
        "pan_width": -0.45,
        "gain": 0.95
    },
    "track02_String_Ensemble_2": {
        "role": "Tenor Harmony",
        "block_steps": [6, 8, 7, 5],
        "rate": 1.0,                   # 8th note rate
        "direction": "forward",
        "feel": "lurch",
        "flux_depth": 0.25,
        "flux_blocks": [0, 1, 2],
        "hp_base": 120.0,
        "lp_base": 3200.0,
        "pan_width": 0.45,
        "gain": 0.95
    },
    "track03_Acoustic_Bass": {
        "role": "Bass Foundation",
        "block_steps": [8, 8, 4, 8],
        "rate": 1.0,
        "direction": "forward",
        "feel": "straight",
        "flux_depth": 0.12,
        "flux_blocks": [0],
        "hp_base": 40.0,
        "lp_base": 2200.0,
        "pan_width": 0.0,
        "gain": 1.00
    }
}

wet_stems = {}
mix_bus = np.zeros((max_len, 2), dtype=np.float64)

for sidx, (sname, arr) in enumerate(sorted(dry_audio.items())):
    cfg = voice_configs.get(sname, {
        "role": "General", "block_steps": [8, 8, 8, 8], "rate": 1.0,
        "direction": "forward", "feel": "straight", "flux_depth": 0.2,
        "flux_blocks": [0, 2], "hp_base": 100.0, "lp_base": 4000.0,
        "pan_width": 0.0, "gain": 1.0
    })
    
    # Configure CadenceLayer
    layer = eng.add_layer(
        name=sname,
        block_steps=cfg["block_steps"],
        rate=cfg["rate"],
        direction=cfg["direction"],
        feel=cfg["feel"],
        gain=cfg["gain"]
    )
    layer.lfo_rate = 0.3 + 0.15 * sidx
    layer.lfo_depth = 0.20
    
    # Customize block step filters
    for bidx, b in enumerate(layer.blocks):
        for st in range(b.steps):
            mod_factor = 1.0 + 0.3 * np.sin(2.0 * np.pi * st / b.steps)
            b.set_step(
                st,
                velocity=100.0 + 15.0 * np.cos(np.pi * st / max(1, b.steps)),
                pan=float(np.clip(cfg["pan_width"] + 0.15 * (st % 2 == 0 and 1 or -1), -1.0, 1.0)),
                hp=float(cfg["hp_base"] * mod_factor),
                lp=float(cfg["lp_base"] * mod_factor)
            )
            
    eng.flux = FluxRandomizer(depth=cfg["flux_depth"], blocks=cfg["flux_blocks"], seed=SEED + sidx * 17)
    
    # Render events for the layer over duration
    step_s = eng.step_seconds(layer)
    needed_steps = int(np.ceil((max_len / SR) / step_s))
    loops = int(np.ceil(needed_steps / max(1, layer.total_steps))) + 1
    
    events = eng.render_events(loops=loops, seed=SEED + sidx * 23, apply_flux=True)
    layer_events = [e for e in events if e["layer"] == sname]
    
    print(f"Layer {sname}: {len(layer_events)} Cadence events rendered across {loops} loops")
    
    # Apply Cadence parameter trajectories to stem audio
    # Construct continuous curves: gain envelope, pan, LP filter modulation
    gain_curve = np.ones(max_len, dtype=np.float64)
    pan_curve = np.full(max_len, cfg["pan_width"], dtype=np.float64)
    lp_curve = np.full(max_len, cfg["lp_base"], dtype=np.float64)
    hp_curve = np.full(max_len, cfg["hp_base"], dtype=np.float64)
    
    for ev in layer_events:
        t_start = ev["start"]
        t_len = ev["length"]
        i_start = int(t_start * SR)
        i_end = min(max_len, int((t_start + t_len) * SR))
        if i_start >= max_len:
            continue
        vel_scale = ev["velocity"] / 100.0
        # Smooth window for parameter transition
        seg_len = i_end - i_start
        if seg_len > 0:
            window = np.hanning(seg_len * 2)[seg_len:]  # release curve
            lfo_val = ev["lfo"]
            gain_curve[i_start:i_end] = (1.0 + 0.25 * (vel_scale - 1.0) + 0.15 * lfo_val)
            pan_curve[i_start:i_end] = ev["pan"] + 0.10 * lfo_val
            lp_curve[i_start:i_end] = np.clip(ev["lp"] * (1.0 + 0.20 * lfo_val), 400.0, 18000.0)
            hp_curve[i_start:i_end] = np.clip(ev["hp"], 20.0, 2000.0)
            
    # Apply time-varying filtering and stereo panning
    # Audio is stereo
    stem_audio = arr.copy()
    
    # Process through StateVariableFilter
    svf_l = StateVariableFilter(sample_rate=SR)
    svf_r = StateVariableFilter(sample_rate=SR)
    
    # Block-based processing for filter smoothing
    block_sz = 256
    filtered_audio = np.zeros_like(stem_audio)
    for b_start in range(0, max_len, block_sz):
        b_end = min(max_len, b_start + block_sz)
        cur_lp = float(np.mean(lp_curve[b_start:b_end]))
        cur_hp = float(np.mean(hp_curve[b_start:b_end]))
        
        # LP pass
        fl = svf_l.process(stem_audio[b_start:b_end, 0], cutoff=cur_lp, mode="lp")
        fr = svf_r.process(stem_audio[b_start:b_end, 1], cutoff=cur_lp, mode="lp")
        filtered_audio[b_start:b_end, 0] = fl
        filtered_audio[b_start:b_end, 1] = fr
        
    # Apply pan & gain
    wet_stem = np.zeros_like(stem_audio)
    # Pan law: constant power
    pan_clamped = np.clip(pan_curve, -1.0, 1.0)
    pan_angle = (pan_clamped + 1.0) * (np.pi / 4.0)
    left_gain = np.cos(pan_angle) * gain_curve * cfg["gain"]
    right_gain = np.sin(pan_angle) * gain_curve * cfg["gain"]
    
    wet_stem[:, 0] = filtered_audio[:, 0] * left_gain
    wet_stem[:, 1] = filtered_audio[:, 1] * right_gain
    
    # Peak normalize individual stem to 0.89
    stem_pk = np.max(np.abs(wet_stem))
    if stem_pk > 1e-9:
        wet_stem_norm = wet_stem * (0.89 / stem_pk)
    else:
        wet_stem_norm = wet_stem
        
    stem_out_path = STEMS_WET / f"{sname}_CADENCE.wav"
    write_wav(stem_out_path, wet_stem_norm)
    wet_stems[sname] = stem_out_path
    print(f"Wet stem {sname}: {stem_out_path.stat().st_size} bytes, peak={np.max(np.abs(wet_stem_norm)):.3f}")
    
    mix_bus += wet_stem

# 4. Master Bus Processing (Spatial diffusion reverb + LUFS normalization + Limiter)
print("Processing master bus...")
# Subtle acoustic space for chorale cohesion
master_rev = AlgorithmicReverb(sample_rate=SR, room_size=0.65, damping=0.45, wet_dry=0.18, width=0.85)
mix_rev = master_rev.process(mix_bus)

# Normalize to -14.0 LUFS
mix_lufs = normalize_to_lufs(mix_rev, target_lufs=-14.0, sample_rate=SR)

# Master Limiter (-1.0 dBFS)
limiter = Limiter(threshold_db=-1.0, release_ms=80.0)
final_mix = limiter.process(mix_lufs)

final_wav = OUT / "SP080-cadence-markov-chorale.wav"
final_ogg = OUT / "SP080-cadence-markov-chorale.ogg"
write_wav(final_wav, final_mix)
print(f"Master WAV: {final_wav.stat().st_size} bytes")

subprocess.run([
    "ffmpeg", "-y", "-loglevel", "error", "-i", str(final_wav),
    "-codec:a", "libopus", "-application", "voip", "-b:a", "48k",
    str(final_ogg)
], check=True)
print(f"Master OGG: {final_ogg.stat().st_size} bytes")

# 5. Metrics & Verification
mono_mix = (final_mix[:, 0] + final_mix[:, 1]) * 0.5
silence_pct = float(np.sum(np.abs(mono_mix) < 0.001) / len(mono_mix)) * 100.0
meas_lufs = measure_lufs(final_mix, SR)
meas_peak = float(np.max(np.abs(final_mix)))
print(f"Master stats: LUFS={meas_lufs:.2f}, Peak={meas_peak:.4f}, Silence={silence_pct:.2f}%")

# Active note intervals from MIDI for pitch verification
mid = mido.MidiFile(str(SRC))
tpb = mid.ticks_per_beat
tempo = 500000
for msg in mid.tracks[0]:
    if msg.type == "set_tempo":
        tempo = msg.tempo
        break
sec_per_tick = tempo / 1e6 / tpb

def midi_to_freq(m):
    return 440.0 * (2.0 ** ((m - 69.0) / 12.0))

intervals = {}
for tr in mid.tracks:
    abstick = 0
    active = {}
    for msg in tr:
        abstick += msg.time
        if msg.type == 'note_on' and msg.velocity > 0:
            if hasattr(msg, 'channel') and msg.channel != 9:
                active[msg.note] = abstick
        elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
            if hasattr(msg, 'channel') and msg.channel != 9:
                if msg.note in active:
                    s = active.pop(msg.note)
                    intervals.setdefault(msg.note, []).append((s * sec_per_tick, abstick * sec_per_tick))

win = int(0.5 * SR)
n_wins = len(mono_mix) // win
freqs = np.fft.rfftfreq(win, 1.0 / SR)
mask = (freqs >= 50) & (freqs <= 2000)

checked = ok = 0
he_list, low_notes, dom_list, misses = [], [], [], []

for w in range(n_wins):
    t0w, t1w = w * 0.5, w * 0.5 + 0.5
    act = set()
    for pitch, lst in intervals.items():
        for (a, b) in lst:
            if a < t1w and b > t0w:
                act.add(pitch)
                break
    if not act:
        continue
    seg = mono_mix[w * win:(w + 1) * win]
    if len(seg) < win or float(np.sqrt(np.mean(seg ** 2))) < 0.01:
        continue
    spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
    f_band, s_band = freqs[mask], spec[mask]
    dom = float(f_band[int(np.argmax(s_band))])
    funds = sorted(midi_to_freq(p) for p in act)
    hit = any(abs(dom - c) / c < 0.04 for f in funds for c in (f, f * 2, f * 3, f / 2, f * 4))
    checked += 1
    ok += 1 if hit else 0
    if not hit:
        misses.append({"t": round(t0w, 2), "dom": round(dom, 1), "act": sorted(act)})
    f0 = midi_to_freq(min(act))
    har = sum(s_band[np.abs(f_band - f0 * k) < max(15, f0 * 0.02)].sum() for k in range(1, 9))
    he_list.append(float(har / max(float(s_band.sum()), 1e-12)))
    low_notes.append(min(act))
    dom_list.append(dom)

hit_rate = ok / max(checked, 1)
he_mean = float(np.mean(he_list)) if he_list else 0.0
print(f"Pitch verification: windows={checked}, hit_rate={hit_rate:.4f}, harmonic_energy={he_mean:.4f}")

# ACF check
ds = 5
md = mono_mix[::ds]
sd = SR // ds
ww = sd
unpitched, acf_n = 0, 0
for w in range(0, len(md) // ww, 2):
    seg = md[w * ww:(w + 1) * ww]
    if len(seg) < ww or float(np.sqrt(np.mean(seg ** 2))) < 0.01:
        continue
    seg = seg - seg.mean()
    ac = np.correlate(seg, seg, mode="full")[len(seg) - 1:]
    if ac[0] < 1e-12:
        continue
    ac = ac / ac[0]
    lo, hi = int(sd / 1000.0), int(sd / 50.0)
    if hi >= len(ac):
        continue
    pk = float(np.max(ac[lo:hi]))
    acf_n += 1
    if pk < 0.30:
        unpitched += 1
print(f"ACF check: windows={acf_n}, unpitched={unpitched}")

verdict = "PASS" if hit_rate >= 0.60 and he_mean >= 0.25 and unpitched < acf_n * 0.5 else "FAIL"

# Save Verification & Stats JSON
pitch_data = {
    "verdict": verdict,
    "windows_checked": checked,
    "dominant_peak_hit_rate": round(hit_rate, 4),
    "harmonic_energy_mean_8h": round(he_mean, 4),
    "acf_windows": acf_n,
    "acf_unpitched": unpitched,
    "lowest_midi_notes_seen": sorted(set(low_notes))[:10],
    "median_dom_hz": round(float(np.median(dom_list)), 1) if dom_list else 0.0,
    "misses": misses[:10]
}
with open(ANALYSIS / "pitch_verification.json", "w") as f:
    json.dump(pitch_data, f, indent=2)

render_stats = {
    "sr": SR,
    "duration_s": round(len(final_mix) / SR, 2),
    "samples": len(final_mix),
    "silence_pct": round(silence_pct, 2),
    "lufs": round(meas_lufs, 2),
    "peak": round(meas_peak, 4),
    "stems_count": len(wet_stems),
    "wav_bytes": final_wav.stat().st_size,
    "ogg_bytes": final_ogg.stat().st_size
}
with open(ANALYSIS / "render_stats.json", "w") as f:
    json.dump(render_stats, f, indent=2)

# Copy grid visualization from source project
src_grid = Path("/opt/data/repos/musicom/projects/Styles/Experimental/064-markov-constraint-chorale/Analysis/grid_visualization.txt")
if src_grid.exists():
    shutil.copy2(str(src_grid), str(ANALYSIS / "grid_visualization.txt"))

# Save Provenance
prov = {
    "job": "random-style production (SP) layer-aligned",
    "date": "2026-09-20",
    "seed": SEED,
    "method": "SP-080",
    "method_module": "sound.generators.cadence_variator",
    "method_desc": "Cadence Engine Rhythmic Variator w/ Flux Randomizer (Emergence Audio Envoy-style)",
    "source_midi": str(SRC),
    "output_wav": str(final_wav),
    "output_ogg": str(final_ogg),
    "lufs": round(meas_lufs, 2),
    "peak": round(meas_peak, 4),
    "silence_pct": round(silence_pct, 2),
    "pitch_verdict": verdict,
    "hit_rate": round(hit_rate, 4),
    "he_mean": round(he_mean, 4)
}
with open(OUT / "provenance.json", "w") as f:
    json.dump(prov, f, indent=2)

with open("/opt/data/projects/Styles/Production/.selection_cron.json", "w") as f:
    json.dump(prov, f, indent=2)

print("\nSUCCESS: Production completed with verdict:", verdict)
