# -*- coding: utf-8 -*-
"""SP-081 RANDOM8 (8-channel quantized random CV) — 004-baroque-counterpoint-inversion.

Source: Styles/Baroque/004-baroque-counterpoint-inversion/midi/004_counterpoint_study.mid
        (C-minor subject + mirror inversion, 120 BPM, 8 quarter notes, 2 voices)
Method: SP-081 -> sound.modular.random8 (Random8, SCALES_15, STYLES)
Layer : ABSOLUTE layer — ONE Random8 instance's 8 CV channels modulate a
        single global parameter matrix across the WHOLE mix (per-voice/per-track
        application is a later refinement). The Random8 is a control-voltage
        SOURCE, not an audio renderer, so the absolute-layer realization maps
        its 8 quantized random CV streams onto a global modulation matrix:
        filter cutoff/resonance, pan, gain, reverb wet, HPF, width, trim.
"""
import json
import shutil
import subprocess
import wave
import math
import time
from pathlib import Path

import numpy as np
import mido

from sound.render.fluidsynth import discover_soundfont
from sound.modular.random8 import Random8, SCALES_15, STYLES
from sound.effects.filter import StateVariableFilter
from sound.effects.reverb import AlgorithmicReverb
from sound.effects.mastering import normalize_to_lufs, measure_lufs, Limiter

SRC = Path("/opt/data/repos/musicom/projects/Styles/Baroque/004-baroque-counterpoint-inversion/midi/004_counterpoint_study.mid")
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/SP081-random8-baroque-counterpoint-inversion")
AUD = OUT / "Audio"
STEMS_DRY = AUD / "stems_dry"
STEMS_WET = AUD / "stems_wet"
MIDIDIR = OUT / "MIDI"
ANALYSIS = OUT / "Analysis"
SCRIPTS = OUT / "Scripts"

for d in (AUD, STEMS_DRY, STEMS_WET, MIDIDIR, ANALYSIS, SCRIPTS):
    d.mkdir(parents=True, exist_ok=True)

SR = 44100
BPM = 120.0
SEED = 20260928
N_TRIGS = 16          # one trigger per eighth-note (8 beats = 16 eighth-notes)
MUSICAL_DUR = 4.0     # 8 beats at 120 BPM = 4.0 s (80640 ticks @ tpb 10080)

SF = discover_soundfont()
assert SF and Path(SF).exists(), f"SoundFont missing: {SF}"
FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"

shutil.copy2(str(SRC), str(MIDIDIR / SRC.name))

# --------------------------------------------------------------------------
# 1. Render dry full mix (SP-001 reference; reverb OFF, chorus OFF)
# --------------------------------------------------------------------------
dry_full = OUT / "dry_full_mix_sp001_reference.wav"
print("Rendering dry full mix with FluidSynth (reverb/chorus off)...")
res = subprocess.run([
    FLUID, "-ni", "-g", "1.2", "-F", str(dry_full), "-r", str(SR),
    "-o", "synth.reverb.active=no", "-o", "synth.chorus.active=no",
    SF, str(SRC),
], capture_output=True, text=True)
if res.returncode != 0 or not dry_full.exists() or dry_full.stat().st_size < 1000:
    raise RuntimeError(f"FluidSynth dry render failed: {res.stderr[-500:]}")
print(f"Dry full mix: {dry_full.stat().st_size} bytes")

# --------------------------------------------------------------------------
# 2. Render dry stems (2 voice tracks; same reverb/chorus-off settings)
# --------------------------------------------------------------------------
mid = mido.MidiFile(str(SRC))
dry_stem_paths = {}
track_idx = 0
for i, tr in enumerate(mid.tracks):
    has_notes = any(m.type in ('note_on', 'note_off') for m in tr)
    if not has_notes:
        continue
    prog, ch = 0, 0
    for m in tr:
        if m.type == 'program_change':
            prog, ch = m.program, m.channel
            break
    if ch == 0 and prog == 0:
        note_chans = {m.channel for m in tr if m.type == 'note_on'}
        if note_chans == {9}:
            ch = 9
    inst_name = "Drums" if ch == 9 else ("Acoustic_Grand_Piano" if prog == 0 else f"Program_{prog}")
    stem_name = f"track{track_idx:02d}_{inst_name}"
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
    stem_mid = STEMS_DRY / f"{stem_name}.mid"
    sm.save(str(stem_mid))
    stem_wav = STEMS_DRY / f"{stem_name}.wav"
    subprocess.run([
        FLUID, "-ni", "-g", "1.2", "-F", str(stem_wav), "-r", str(SR),
        "-o", "synth.reverb.active=no", "-o", "synth.chorus.active=no",
        SF, str(stem_mid),
    ], check=True, capture_output=True)
    stem_mid.unlink()
    dry_stem_paths[stem_name] = stem_wav
    print(f"Dry stem {stem_name}: {stem_wav.stat().st_size} bytes")
    track_idx += 1

# --------------------------------------------------------------------------
# 3. WAV helpers (internal convention: (N, 2) float64 = samples x channels)
# --------------------------------------------------------------------------
def read_wav(p):
    with wave.open(str(p), "rb") as wf:
        nch = wf.getnchannels()
        sr = wf.getframerate()
        n = wf.getnframes()
        raw = np.frombuffer(wf.readframes(n), dtype=np.int16).astype(np.float64) / 32768.0
    if nch == 2:
        return raw.reshape(-1, 2), sr
    return np.column_stack([raw, raw]), sr


def write_wav(p, audio):
    clipped = np.clip(audio, -1.0, 1.0)
    if clipped.ndim == 1:
        nch, data = 1, (clipped * 32767.0).astype(np.int16).tobytes()
    else:
        nch = 2
        data = (clipped * 32767.0).astype(np.int16).reshape(-1).tobytes()
    with wave.open(str(p), "wb") as wf:
        wf.setnchannels(nch)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(data)


dry_mix, sr = read_wav(dry_full)
N = dry_mix.shape[0]
print(f"Dry mix: shape={dry_mix.shape}, sr={sr}, duration={N/sr:.2f}s")

# --------------------------------------------------------------------------
# 4. Random8 CV generation -> per-sample modulation curves (0..1)
# --------------------------------------------------------------------------
r8 = Random8(seed=SEED)
r8.set_preset(0, style="drift", scale="dorian", slide=0.35)
r8.set_preset(1, style="uniform", scale="major", dividr=2)
r8.set_preset(2, style="steps", scale=None, probability=0.8)
r8.set_preset(3, style="bell", scale="natural_minor", slide=0.3)
r8.set_preset(4, style="drift", scale="mixolydian", slide=0.5)
r8.set_preset(5, style="burst", scale="whole_tone", slide=0.3)
r8.set_preset(6, style="steps", scale="hirajoshi", attenuate=0.6)
r8.set_preset(7, style="triangle", scale=None, dividr=4)

cv = r8.process(n_trigs=N_TRIGS)  # (8, N_TRIGS), values 0..1
snapshot = r8.snapshot()

# trigger grid spans the musical 4.0 s; np.interp clamps past the end (tail hold)
xp = np.linspace(0.0, MUSICAL_DUR, N_TRIGS)
t_axis = np.arange(N) / sr

def curve(ch):
    return np.interp(t_axis, xp, cv[ch]).astype(np.float64)

# parameter mappings
cutoff_curve   = 500.0 * (9000.0 / 500.0) ** curve(0)   # 500..9000 Hz (log)
pan_curve      = 2.0 * curve(1) - 1.0                    # -1..+1
gain_curve     = 0.70 + 0.30 * curve(2)                  # 0.70..1.0
wet_curve      = 0.06 + 0.30 * curve(3)                  # 0.06..0.36
hpf_curve      = 20.0 * (80.0 / 20.0) ** curve(4)        # 20..80 Hz
width_curve    = 0.6 + 0.8 * curve(5)                    # 0.6..1.4
reson_curve    = 0.15 + 0.55 * curve(6)                  # 0.15..0.70
trim_curve     = 0.92 + 0.08 * curve(7)                  # 0.92..1.0

print("Random8 CV stats (per channel min/max):")
for c in range(8):
    print(f"  ch{c}: {cv[c].min():.3f}..{cv[c].max():.3f}")

# --------------------------------------------------------------------------
# 5. Apply the absolute-layer modulation matrix
# --------------------------------------------------------------------------
def block_svf(signal_mono, cutoff_curve, reson_curve, mode):
    """StateVariableFilter with block-varying cutoff/resonance (state persists)."""
    filt = StateVariableFilter(SR)
    BLK = 512
    out = np.empty_like(signal_mono)
    n = len(signal_mono)
    for s in range(0, n, BLK):
        e = min(s + BLK, n)
        c = float(cutoff_curve[(s + e) // 2])
        q = float(reson_curve[(s + e) // 2])
        out[s:e] = filt.process(signal_mono[s:e], cutoff=c, resonance=q, mode=mode)
    return out


print("Applying SP-081 Random8 absolute-layer modulation matrix...")
t0 = time.time()

# 5a. LPF (ch0 cutoff / ch6 resonance) + HPF (ch4) per channel
lp_l = block_svf(dry_mix[:, 0], cutoff_curve, reson_curve, "lp")
lp_r = block_svf(dry_mix[:, 1], cutoff_curve, reson_curve, "lp")
filt = np.column_stack([lp_l, lp_r])
hp_l = block_svf(filt[:, 0], hpf_curve, np.full_like(hpf_curve, 0.5), "hp")
hp_r = block_svf(filt[:, 1], hpf_curve, np.full_like(hpf_curve, 0.5), "hp")
filt = np.column_stack([hp_l, hp_r])

# 5b. pan (ch1) + width (ch5) via mid/side
mid = 0.5 * (filt[:, 0] + filt[:, 1])
side = 0.5 * (filt[:, 0] - filt[:, 1]) * width_curve
L = mid + side
R = mid - side
pan_angle = (pan_curve + 1.0) * (math.pi / 4.0)
g_l = np.cos(pan_angle) * math.sqrt(2.0)
g_r = np.sin(pan_angle) * math.sqrt(2.0)
L = L * g_l
R = R * g_r

# 5c. gain tremolo (ch2)
L = L * gain_curve
R = R * gain_curve
spatial = np.column_stack([L, R])

# 5d. reverb wet crossfade (ch3) — reverb computed at wet_dry=1.0 (pure wet)
reverb = AlgorithmicReverb(sample_rate=SR, room_size=0.55, damping=0.45,
                           wet_dry=1.0, width=0.85)
wet_only = reverb.process(spatial)
wet_w = wet_curve[:, None]
out = spatial * (1.0 - wet_w) + wet_only * wet_w

# 5e. master trim (ch7)
out = out * trim_curve[:, None]

print(f"  modulation matrix done in {time.time()-t0:.1f}s")

# --------------------------------------------------------------------------
# 6. Master: LUFS -14 + Limiter(-1 dB) LAST
# --------------------------------------------------------------------------
lufs_norm = normalize_to_lufs(out, target_lufs=-14.0, sample_rate=SR)
limiter = Limiter(threshold_db=-1.0, sample_rate=SR)
final_master = limiter.process(lufs_norm)  # (N, 2)

final_wav = OUT / "SP081-random8-baroque-counterpoint-inversion.wav"
final_ogg = OUT / "SP081-random8-baroque-counterpoint-inversion.ogg"
write_wav(final_wav, final_master)
print(f"Wrote final WAV: {final_wav} ({final_wav.stat().st_size} bytes)")

subprocess.run([
    "ffmpeg", "-y", "-loglevel", "error", "-i", str(final_wav),
    "-codec:a", "libopus", "-application", "voip", "-b:a", "48k", str(final_ogg),
], check=True)
print(f"Wrote final OGG: {final_ogg} ({final_ogg.stat().st_size} bytes)")

# --------------------------------------------------------------------------
# 7. Wet stems (same absolute-layer modulation, per stem)
# --------------------------------------------------------------------------
print("Rendering wet stems (same absolute-layer modulation per stem)...")
max_len = N
for name, spath in dry_stem_paths.items():
    a, _ = read_wav(spath)
    if a.shape[0] < max_len:
        a = np.vstack([a, np.zeros((max_len - a.shape[0], 2), dtype=np.float64)])
    lp_l = block_svf(a[:, 0], cutoff_curve, reson_curve, "lp")
    lp_r = block_svf(a[:, 1], cutoff_curve, reson_curve, "lp")
    f = np.column_stack([lp_l, lp_r])
    hp_l = block_svf(f[:, 0], hpf_curve, np.full_like(hpf_curve, 0.5), "hp")
    hp_r = block_svf(f[:, 1], hpf_curve, np.full_like(hpf_curve, 0.5), "hp")
    f = np.column_stack([hp_l, hp_r])
    m2 = 0.5 * (f[:, 0] + f[:, 1])
    s2 = 0.5 * (f[:, 0] - f[:, 1]) * width_curve
    L2 = (m2 + s2) * g_l * gain_curve
    R2 = (m2 - s2) * g_r * gain_curve
    sp = np.column_stack([L2, R2])
    wo = reverb.process(sp)
    sp2 = sp * (1.0 - wet_w) + wo * wet_w
    sp2 = sp2 * trim_curve[:, None]
    pk = np.max(np.abs(sp2))
    if pk > 1e-6:
        sp2 = sp2 * (0.89 / pk)
    write_wav(STEMS_WET / f"{name}_RANDOM8.wav", sp2)
print("Wet stems done.")

# --------------------------------------------------------------------------
# 8. Verification: silence / RMS / LUFS / pitch fidelity / harmonic energy / ACF
# --------------------------------------------------------------------------
meas_lufs = measure_lufs(final_master, sample_rate=SR)
peak_val = float(np.max(np.abs(final_master)))
mono_mix = 0.5 * (final_master[:, 0] + final_master[:, 1])
mono_dry = 0.5 * (dry_mix[:, 0] + dry_mix[:, 1])
silence_pct = float(np.sum(np.abs(mono_mix) < 0.001) / len(mono_mix)) * 100.0

rms_map = []
for s in range(len(mono_mix) // SR):
    seg = mono_mix[s * SR:(s + 1) * SR]
    rms_map.append(round(float(np.sqrt(np.mean(seg ** 2))), 4))

print(f"Master Stats: LUFS={meas_lufs:.2f}, Peak={peak_val:.4f}, Silence={silence_pct:.2f}%")

# pitch fidelity + harmonic energy + ACF on the wet mix
def midi_from_freq(f):
    return 69.0 + 12.0 * math.log2(max(1.0, f) / 440.0)

win = int(0.5 * SR)
n_wins = len(mono_mix) // win
freqs = np.fft.rfftfreq(win, 1.0 / SR)
mask = (freqs >= 50.0) & (freqs <= 2000.0)

checked = hits = 0
he_list, dom_list, misses = [], [], []
for w in range(n_wins):
    seg_w = mono_mix[w * win:(w + 1) * win]
    seg_d = mono_dry[w * win:(w + 1) * win]
    if np.sqrt(np.mean(seg_d ** 2)) < 0.01:
        continue
    spec_w = np.abs(np.fft.rfft(seg_w * np.hanning(win)))
    spec_d = np.abs(np.fft.rfft(seg_d * np.hanning(win)))
    fw = freqs[mask]; sw = spec_w[mask]; sd = spec_d[mask]
    dom_w = float(fw[int(np.argmax(sw))])
    dom_d = float(fw[int(np.argmax(sd))])
    checked += 1
    dom_list.append(dom_w)
    # harmonic energy of wet: 8 harmonics of the wet dominant (lowest) peak
    tot = np.sum(spec_w ** 2) + 1e-12
    he = 0.0
    for h in range(1, 9):
        tf = dom_w * h
        he += np.sum(spec_w[(freqs >= tf - 15) & (freqs <= tf + 15)] ** 2)
    he_list.append(float(he / tot))
    # wet vs dry dominant: allow octave/harmonic shift (filter reshapes spectrum)
    ratios = [1.0, 2.0, 3.0, 4.0, 0.5, 1.0 / 3.0]
    hit = any(abs(dom_w - dom_d * r) / (dom_d * r) < 0.04 for r in ratios)
    if hit:
        hits += 1
    else:
        misses.append({"t": round(w * 0.5, 2), "dom_w": round(dom_w, 1),
                       "dom_d": round(dom_d, 1)})

hit_rate = hits / max(checked, 1)
he_mean = float(np.mean(he_list)) if he_list else 0.0

# ACF unpitched check (SP-035 failure signature: 0 Hz / broadband noise)
ds = 5
md = mono_mix[::ds]
sd = SR // ds
ww = sd
unpitched = acf_n = 0
for w in range(0, len(md) // ww, 2):
    seg = md[w * ww:(w + 1) * ww]
    if len(seg) < ww or np.sqrt(np.mean(seg ** 2)) < 0.01:
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

pitch_verdict = "PASS" if (hit_rate >= 0.60 and he_mean >= 0.25
                           and (unpitched / max(acf_n, 1)) < 0.50) else "FAIL"
print(f"Pitch verification: windows={checked}, dry-wet hit_rate={hit_rate:.4f}, "
      f"harmonic_energy={he_mean:.4f}, ACF unpitched={unpitched}/{acf_n} -> {pitch_verdict}")

# --------------------------------------------------------------------------
# 9. Analysis artifacts + provenance
# --------------------------------------------------------------------------
render_stats = {
    "method": "SP-081",
    "method_module": "sound.modular.random8",
    "layer": "absolute",
    "random8_seed": SEED,
    "n_trigs": N_TRIGS,
    "channels": snapshot,
    "scales": sorted(SCALES_15),
    "styles": sorted(STYLES),
    "lufs": round(meas_lufs, 2),
    "peak": peak_val,
    "silence_pct": round(silence_pct, 2),
    "rms_per_second": rms_map,
    "windows_checked": checked,
    "dry_wet_hit_rate": round(hit_rate, 4),
    "harmonic_energy_mean": round(he_mean, 4),
    "acf_windows": acf_n,
    "acf_unpitched": unpitched,
    "pitch_verdict": pitch_verdict,
    "median_dom_hz": round(float(np.median(dom_list)), 1) if dom_list else 0.0,
    "duration_sec": round(len(mono_mix) / SR, 2),
}
(ANALYSIS / "render_stats.json").write_text(json.dumps(render_stats, indent=2))
(ANALYSIS / "pitch_verification.json").write_text(json.dumps({
    "method": "SP-081",
    "project": "004-baroque-counterpoint-inversion",
    "status": pitch_verdict,
    "dry_wet_hit_rate": hit_rate,
    "harmonic_energy_mean": he_mean,
    "acf_unpitched": unpitched,
    "acf_windows": acf_n,
    "windows_analyzed": checked,
    "median_dom_hz": render_stats["median_dom_hz"],
    "misses": misses[:12],
}, indent=2))

# grid visualization: Random8 channel -> destination map
grid_lines = [
    "SP-081 Random8 — absolute-layer modulation matrix",
    f"seed={SEED} n_trigs={N_TRIGS} (eighth-note grid, 8 beats @ 120 BPM)",
    "",
    "ch  style      scale            -> destination (mapping)",
]
dest = [
    ("drift", "dorian", "LPF cutoff 500-9000 Hz (log)"),
    ("uniform", "major", "stereo pan -1..+1 (constant power)"),
    ("steps", "unquantised", "gain tremolo 0.70..1.0"),
    ("bell", "natural_minor", "reverb wet 0.06..0.36 (crossfade)"),
    ("drift", "mixolydian", "HPF cutoff 20-80 Hz"),
    ("burst", "whole_tone", "stereo width 0.6..1.4 (mid/side)"),
    ("steps", "hirajoshi", "LPF resonance 0.15..0.70"),
    ("triangle", "unquantised", "master trim 0.92..1.0"),
]
for i, (st, sc, d) in enumerate(dest):
    vals = cv[i]
    bar = "".join("█" if v >= 0.5 else "░" for v in vals)
    grid_lines.append(f"  ch{i} {st:9s} {sc:16s} -> {d}")
    grid_lines.append(f"      CV[{bar}]  ({vals.min():.2f}..{vals.max():.2f})")
grid_lines.append("")
grid_lines.append("stems (wet, same absolute params):")
for name in sorted(dry_stem_paths):
    grid_lines.append(f"  {name}_RANDOM8.wav")
(ANALYSIS / "grid_visualization.txt").write_text("\n".join(grid_lines) + "\n")

provenance = {
    "job": "random-style production (SP) layer-aligned",
    "date": "2026-09-28",
    "seed": SEED,
    "method": "SP-081",
    "method_module": "sound.modular.random8",
    "method_desc": "8-Channel Quantized Random CV Source (Befaco/Mylar Melodies RANDOM8-style)",
    "layer": "absolute",
    "source_midi": str(SRC),
    "output_wav": str(final_wav),
    "output_ogg": str(final_ogg),
    "lufs": round(meas_lufs, 2),
    "peak": peak_val,
    "silence_pct": round(silence_pct, 2),
    "pitch_verdict": pitch_verdict,
    "dry_wet_hit_rate": round(hit_rate, 4),
    "he_mean": round(he_mean, 4),
}
(OUT / "provenance.json").write_text(json.dumps(provenance, indent=2))
(Path("/opt/data/repos/musicom/projects/Styles/Production/.selection_cron.json")).write_text(json.dumps(provenance, indent=2))

print("Done. pitch_verdict=", pitch_verdict)
