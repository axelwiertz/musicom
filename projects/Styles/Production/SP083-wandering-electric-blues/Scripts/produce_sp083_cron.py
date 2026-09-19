# -*- coding: utf-8 -*-
"""Production pass for SP-083 (Sound Dust Drift Clouds / Wandering Engine).

Source: Styles/Blues/039-electric-blues/daily-2026-06-27_blues_039-electric-blues-unitmatrix.mid
Method: SP-083 -> sound.modular.wandering
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
from sound.modular.wandering import DriftCloudsVoice, WanderingEngine, Portal
from sound.effects.mastering import normalize_to_lufs, measure_lufs, Limiter

SRC = Path("/opt/data/repos/musicom/projects/Styles/Blues/039-electric-blues/daily-2026-06-27_blues_039-electric-blues-unitmatrix.mid")
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/SP083-wandering-electric-blues")
AUD = OUT / "Audio"
STEMS_DRY = AUD / "stems_dry"
STEMS_WET = AUD / "stems_wet"
MIDIDIR = OUT / "MIDI"
ANALYSIS = OUT / "Analysis"
SCRIPTS = OUT / "Scripts"

for d in (AUD, STEMS_DRY, STEMS_WET, MIDIDIR, ANALYSIS, SCRIPTS):
    d.mkdir(parents=True, exist_ok=True)

SR = 44100
SEED = 20260919

SF = discover_soundfont()
assert SF and os.path.exists(SF), "SoundFont missing"
FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"

shutil.copy2(str(SRC), str(MIDIDIR / SRC.name))

# 1. Render Dry Full Mix
dry_full = OUT / "dry_full_mix_sp001_reference.wav"
print("Rendering dry full mix with FluidSynth...")
subprocess.run([
    FLUID, "-ni", "-g", "1.2", "-F", str(dry_full), "-r", str(SR),
    "-o", "synth.reverb.active=no", "-o", "synth.chorus.active=no",
    SF, str(SRC)
], check=True, capture_output=True)
print(f"Dry full mix: {dry_full.stat().st_size} bytes")

# 2. Render Dry Stems
mid = mido.MidiFile(str(SRC))
dry_stem_paths = {}

GM_NAMES = {
    30: "Overdriven_Guitar",
    33: "Electric_Bass_finger"
}

tracks_with_notes = []
for i, tr in enumerate(mid.tracks):
    has_notes = any(m.type in ('note_on', 'note_off') for m in tr)
    if has_notes:
        tracks_with_notes.append((i, tr))

for idx, (orig_idx, tr) in enumerate(tracks_with_notes):
    # determine name
    prog = 0
    ch = 0
    for m in tr:
        if m.type == 'program_change':
            prog = m.program
            ch = m.channel
            break
    if ch == 0 and prog == 0:
        note_chans = {m.channel for m in tr if m.type == 'note_on'}
        if note_chans == {9}:
            ch = 9
    
    if ch == 9:
        inst_name = "Drums"
    else:
        inst_name = GM_NAMES.get(prog, f"Program_{prog}")
    
    stem_name = f"track{idx:02d}_{inst_name}"
    stem_mid = STEMS_DRY / f"{stem_name}.mid"
    stem_wav = STEMS_DRY / f"{stem_name}.wav"
    
    sm = mido.MidiFile(ticks_per_beat=mid.ticks_per_beat)
    tt = mido.MidiTrack()
    for m in mid.tracks[0]:
        if m.type == 'set_tempo':
            tt.append(m)
            break
    sm.tracks.append(tt)
    vt = mido.MidiTrack()
    for m in tr:
        vt.append(m)
    sm.tracks.append(vt)
    sm.save(str(stem_mid))
    
    subprocess.run([
        FLUID, "-ni", "-g", "1.2", "-F", str(stem_wav), "-r", str(SR),
        "-o", "synth.reverb.active=no", "-o", "synth.chorus.active=no",
        SF, str(stem_mid)
    ], check=True, capture_output=True)
    os.unlink(str(stem_mid))
    dry_stem_paths[stem_name] = stem_wav
    print(f"Dry stem {stem_name}: {stem_wav.stat().st_size} bytes")

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

# Determine max length
dry_audio = {}
max_len = 0
for sname, spath in dry_stem_paths.items():
    arr = load_wav(spath)
    dry_audio[sname] = arr
    max_len = max(max_len, len(arr))

# Pad all dry audio to max_len
for sname in dry_audio:
    if len(dry_audio[sname]) < max_len:
        pad = np.zeros((max_len - len(dry_audio[sname]), 2), dtype=np.float64)
        dry_audio[sname] = np.vstack([dry_audio[sname], pad])

# 3. SP-083 Wandering Engine + DriftCloudsVoice Processing
# Voice Profiles
configs = {
    "track00_Overdriven_Guitar": {
        "cloud_drift": 1.0,
        "shadow_drift": 0.4,
        "mod_wheel": 0.65,
        "routes": [("drift", "filter_cutoff", 0.45), ("drift", "pan", 0.5), ("portal", "eq_tilt", 0.3)],
        "surprise": 0.3,
        "shadow_shift": 180, # samples delay for shadow layer
        "gain": 1.0
    },
    "track01_Electric_Bass_finger": {
        "cloud_drift": 0.5,
        "shadow_drift": 0.2,
        "mod_wheel": 0.5,
        "routes": [("drift", "filter_cutoff", 0.25), ("drift", "pan", 0.15)],
        "surprise": 0.1,
        "shadow_shift": 300,
        "gain": 0.95
    },
    "track02_Drums": {
        "cloud_drift": 0.6,
        "shadow_drift": 0.25,
        "mod_wheel": 0.7,
        "routes": [("drift", "pan", 0.35), ("drift", "filter_cutoff", 0.2)],
        "surprise": 0.2,
        "shadow_shift": 80,
        "gain": 0.9
    }
}

wet_stems = {}
mix_bus = np.zeros((max_len, 2), dtype=np.float64)

for sname, arr in dry_audio.items():
    cfg = configs[sname]
    mono = (arr[:, 0] + arr[:, 1]) * 0.5
    shift = cfg["shadow_shift"]
    shadow = np.roll(mono, shift)
    # smooth wrap
    shadow[:shift] = 0.0
    
    voice = DriftCloudsVoice(
        sample_rate=SR,
        cloud_drift=cfg["cloud_drift"],
        shadow_drift=cfg["shadow_drift"],
        mod_wheel=cfg["mod_wheel"],
        seed=SEED + len(wet_stems) * 10
    )
    for src, dst, dep in cfg["routes"]:
        voice.portal.add_route(src, dst, dep)
    if cfg["surprise"] > 0:
        voice.portal.surprise(amount=cfg["surprise"])
        
    wet = voice.render(mono, shadow, n_blocks=64)
    # Peak norm stem to 0.89
    pk = np.max(np.abs(wet))
    if pk > 1e-9:
        wet_norm = wet * (0.89 / pk)
    else:
        wet_norm = wet
    
    wet_stem_path = STEMS_WET / f"{sname}_WANDERING.wav"
    write_wav(wet_stem_path, wet_norm)
    wet_stems[sname] = wet_stem_path
    print(f"Wet stem {sname}: {wet_stem_path.stat().st_size} bytes, peak={np.max(np.abs(wet_norm)):.3f}")
    
    mix_bus += wet * cfg["gain"]

# Master Mix Bus
peak = np.max(np.abs(mix_bus))
if peak > 1e-9:
    mix_bus = mix_bus * (0.89 / peak)

mix_lufs = normalize_to_lufs(mix_bus, target_lufs=-14.0, sample_rate=SR)
limiter = Limiter(threshold_db=-1.0)
final_mix = limiter.process(mix_lufs)

final_wav = OUT / "SP083-wandering-electric-blues.wav"
final_ogg = OUT / "SP083-wandering-electric-blues.ogg"
write_wav(final_wav, final_mix)
print(f"Master mix WAV: {final_wav.stat().st_size} bytes")

subprocess.run([
    "ffmpeg", "-y", "-loglevel", "error", "-i", str(final_wav),
    "-codec:a", "libopus", "-application", "voip", "-b:a", "48k",
    str(final_ogg)
], check=True)
print(f"Master mix OGG: {final_ogg.stat().st_size} bytes")

# 4. Metrics & Pitch Verification
mono_mix = (final_mix[:, 0] + final_mix[:, 1]) * 0.5
silence_pct = float(np.sum(np.abs(mono_mix) < 0.001) / len(mono_mix)) * 100.0
meas_lufs = measure_lufs(final_mix, SR)
meas_peak = float(np.max(np.abs(final_mix)))
print(f"Master stats: LUFS={meas_lufs:.2f}, Peak={meas_peak:.4f}, Silence={silence_pct:.2f}%")

# Active note intervals from MIDI for pitch verification
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

pitch_ver = {
    "windows_checked": checked,
    "dominant_peak_hit_rate": round(hit_rate, 4),
    "harmonic_energy_mean_8h": round(he_mean, 4),
    "acf_windows": acf_n,
    "acf_unpitched": unpitched,
    "lowest_midi_notes_seen": sorted(set(low_notes))[:10],
    "median_dom_hz": round(float(np.median(dom_list)), 1) if dom_list else 0.0,
    "misses": misses[:12],
    "method": "FFT dominant peak per 0.5 s window, 50-2000 Hz, +/-4% vs active MIDI fund harmonics",
    "verdict": ("PASS" if (hit_rate >= 0.60 and (unpitched / max(acf_n, 1)) < 0.50) else "FAIL")
}
print(f"Pitch verdict: {pitch_ver['verdict']}")

with open(ANALYSIS / "pitch_verification.json", "w") as f:
    json.dump(pitch_ver, f, indent=2)

# Render Stats
rms_s = [float(np.sqrt(np.mean(mono_mix[i:i + SR] ** 2))) for i in range(0, len(mono_mix), SR)]
render_stats = {
    "duration_s": round(len(final_mix) / SR, 2),
    "lufs": round(meas_lufs, 2),
    "peak": round(meas_peak, 4),
    "silence_pct": round(silence_pct, 2),
    "rms_per_sec": [round(x, 4) for x in rms_s]
}
with open(ANALYSIS / "render_stats.json", "w") as f:
    json.dump(render_stats, f, indent=2)

# Provenance JSON
prov = {
    "job": "random-style production (SP) layer-aligned",
    "date": "2026-09-19",
    "method": "SP-083",
    "method_module": "sound.modular.wandering",
    "method_desc": "Non-LFO Wandering Engine + Portal + Drift Clouds Voice (Sound Dust-style)",
    "source_midi": str(SRC),
    "output_wav": str(final_wav),
    "output_ogg": str(final_ogg),
    "lufs": round(meas_lufs, 2),
    "peak": round(meas_peak, 4),
    "silence_pct": round(silence_pct, 2),
    "pitch_verdict": pitch_ver["verdict"],
    "hit_rate": pitch_ver["dominant_peak_hit_rate"],
    "he_mean": pitch_ver["harmonic_energy_mean_8h"]
}
with open(OUT / "provenance.json", "w") as f:
    json.dump(prov, f, indent=2)

shutil.copy2(__file__, str(SCRIPTS / "produce_sp083_cron.py"))
print("Done production script execution.")
