# -*- coding: utf-8 -*-
"""SP-021 Binaural HRTF Spatialization production pass - 2026-10-04 cron.

Source : Styles/Ragtime/001-ragtime-maple-leaf/MIDI/ragtime-maple-leaf.mid
         (ragtime boom-chick piano + banjo counter-roll, C major, 120 BPM,
          16 bars / 30720 ticks, 4/4:
           track1 PianoLH  ch0 prog1  bass/chords F1..G3  520 notes
           track2 PianoRH  ch1 prog1  ragged melody C4..C5 64 notes
           track3 Banjo    ch2 prog105 16th counter-rolls  256 notes)
Method : SP-021 -> sound.synthesis.binaural (SP_METHODS registry).
Layer  : ABSOLUTE - a binaural spatialization layer applied to the WHOLE
         rendered ragtime piece. Each of the 3 voices is rendered mono via
         FluidSynth (GM acoustic carrier), then positioned with
         Woodworth-Schlosberg ITD (head-radius sin+abs azimuth) + ILD
         (head-shadow lowpass), distance-attenuated, and summed to a stereo
         binaural image. No new notes written; the spatial layer re-sculpts
         the rendered tone/position of every voice.

Chain:
  source MIDI -> split into 3 per-voice MIDI (tempo track + remapped ch0)
  -> FluidSynth mono render per voice (SP-001 reference carrier)
  -> SP-021 Woodworth-Schlosberg binaural spatialization per voice
       (unique azimuth/distance, ITD delay + ILD head-shadow lowpass)
  -> stereo sum -> peak 0.89 -> normalize_to_lufs(-14) -> Limiter(-1 dB) LAST
  -> SP021-binaural-ragtime-maple-leaf.wav + .ogg (Opus 48k voip)
  -> stems: per-voice mono + per-voice binaural stereo
  -> pitch verification + silence/RMS on the wet mix
"""
import hashlib
import json
import os
import shutil
import subprocess
import wave
from pathlib import Path

import numpy as np
import mido
import scipy.signal as sig

SRC = Path("/opt/data/repos/musicom/projects/Styles/Ragtime/001-ragtime-maple-leaf/MIDI/ragtime-maple-leaf.mid")
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/SP021-binaural-ragtime-maple-leaf")
AUD = OUT / "Audio"
STEMS_MONO = AUD / "stems_mono"
STEMS_BIN = AUD / "stems_binaural"
MIDI_SPLIT = OUT / "MIDI"
ANALYSIS = OUT / "Analysis"
SCRIPTS = OUT / "Scripts"
for d in (AUD, STEMS_MONO, STEMS_BIN, MIDI_SPLIT, ANALYSIS, SCRIPTS):
    d.mkdir(parents=True, exist_ok=True)

SR = 44100
SEED = 20261004

# Track azimuth/distance assignments (radians) — a wide, stage-like binaural image:
#   PianoLH (boom-chick bass/chords) anchors center; PianoRH (ragged melody)
#   sits right-front; Banjo (16th counter-rolls) sits left.
TRACK_CONFIG = {
    "PianoLH": {"track_idx": 1, "channel": 0, "azimuth": 0.0, "distance": 1.30},
    "PianoRH": {"track_idx": 2, "channel": 1, "azimuth": 0.55, "distance": 1.00},
    "Banjo":   {"track_idx": 3, "channel": 2, "azimuth": -0.65, "distance": 1.10},
}

from sound.render.fluidsynth import discover_soundfont
from sound.effects.mastering import normalize_to_lufs, measure_lufs, Limiter

SF = discover_soundfont()
assert SF and os.path.exists(SF), "no soundfont"
print("soundfont:", SF)

FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
if not Path(FLUID).exists():
    FLUID = "fluidsynth"

shutil.copy2(str(SRC), str(OUT / "ragtime-maple-leaf.mid"))

# ---------------- parse source (mido read-only) ----------------
mid = mido.MidiFile(str(SRC))
src_tpb = mid.ticks_per_beat
tempo = 500000
for msg in mid.tracks[0]:
    if msg.type == "set_tempo":
        tempo = msg.tempo
        break
BPM = 60000000.0 / tempo
SPB = tempo / 1e6
print("src_tpb=%d tempo=%d bpm=%.2f tracks=%d" % (src_tpb, tempo, BPM, len(mid.tracks)))

# ground-truth pitched notes per voice (all voices are pitched here; no ch9 perc)
pitched_notes = []   # (pitch, start_sec, end_sec)
track_summary = {}
for ti, tr in enumerate(mid.tracks[1:], start=1):
    t = 0
    active = {}
    evs = []
    for msg in tr:
        t += msg.time
        if msg.type == "note_on" and msg.velocity > 0:
            active[msg.note] = t
        elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
            if msg.note in active:
                s = active.pop(msg.note)
                evs.append((msg.note, s, t))
    track_summary[ti] = evs
    for (p, s, e) in evs:
        pitched_notes.append((p, s * SPB / src_tpb, e * SPB / src_tpb))

for ti, evs in sorted(track_summary.items()):
    ps = sorted({p for p, _, _ in evs})
    print("track %d: n=%d pitch range %s..%s" % (ti, len(evs), min(ps), max(ps)))
print("pitched notes total: %d" % len(pitched_notes))

# ---------------- split MIDI per voice ----------------
split_paths = {}
for name, cfg in TRACK_CONFIG.items():
    src_tr = mid.tracks[cfg["track_idx"]]
    new_mid = mido.MidiFile(ticks_per_beat=src_tpb)

    # tempo track
    tt = mido.MidiTrack()
    new_mid.tracks.append(tt)
    tt.append(mido.MetaMessage("set_tempo", tempo=tempo, time=0))
    tt.append(mido.MetaMessage("end_of_track", time=0))

    # data track: remap to channel 0, preserve program change
    dt = mido.MidiTrack()
    new_mid.tracks.append(dt)
    for msg in src_tr:
        if msg.type in ("note_on", "note_off", "program_change", "control_change"):
            m2 = msg.copy()
            if hasattr(m2, "channel"):
                m2.channel = 0
            dt.append(m2)
    dt.append(mido.MetaMessage("end_of_track", time=0))

    out_path = MIDI_SPLIT / ("voice_%s.mid" % name.lower())
    new_mid.save(str(out_path))
    split_paths[name] = out_path
    print("split %s -> %s" % (name, out_path))

# ---------------- render per-voice mono via FluidSynth ----------------
def run(cmd):
    rr = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if rr.returncode != 0:
        raise RuntimeError("cmd failed %s: %s" % (cmd, rr.stderr[-800:]))
    return rr

mono_paths = {}
for name, path in split_paths.items():
    wav_path = STEMS_MONO / ("%s_mono.wav" % name.lower())
    run([FLUID, "-ni", "-g", "1.2", "-F", str(wav_path), "-r", str(SR),
         "-o", "synth.reverb.active=no", "-o", "synth.chorus.active=no",
         SF, str(path)])
    print("render %s -> %s (%d B)" % (name, wav_path, wav_path.stat().st_size))
    mono_paths[name] = wav_path

def load_mono(p):
    with wave.open(str(p), "rb") as wf:
        n, ch = wf.getnframes(), wf.getnchannels()
        raw = np.frombuffer(wf.readframes(n), dtype=np.int16).astype(np.float64) / 32768.0
    if ch == 2:
        raw = raw.reshape(-1, 2).mean(axis=1)
    return raw

def write_wav(p, audio, sr=44100):
    a = np.clip(np.asarray(audio), -1.0, 1.0)
    ints = (a * 32767.0).astype(np.int16)
    ch = 1 if a.ndim == 1 else a.shape[1]
    with wave.open(str(p), "wb") as wf:
        wf.setnchannels(ch)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(ints.tobytes())

# also produce a dry full-mix reference (SP-001 carrier) for comparison
dry_full = OUT / "dry_full_mix_sp001_reference.wav"
run([FLUID, "-ni", "-g", "1.2", "-F", str(dry_full), "-r", str(SR),
     "-o", "synth.reverb.active=no", "-o", "synth.chorus.active=no",
     SF, str(SRC)])
print("dry full mix %d B" % dry_full.stat().st_size)

mono = {name: load_mono(mono_paths[name]) for name in mono_paths}
# trim all voices to the same length (shortest = piece duration)
dur = min(len(x) for x in mono.values())
print("piece duration %.2fs" % (dur / SR))

# ---------------- SP-021 binaural spatialization ----------------
def first_order_lowpass_const(x, fc, fs):
    if fc >= fs / 2.0:
        return x.astype(np.float64)
    alpha = (2.0 * np.pi * fc / fs) / (2.0 * np.pi * fc / fs + 1.0)
    b = [alpha]
    a = [1.0, -(1.0 - alpha)]
    return sig.lfilter(b, a, x).astype(np.float64)

def const_fractional_delay(x, d):
    d_int = int(np.floor(d))
    d_frac = d - d_int
    n = len(x)
    if d_int <= 0:
        y = x.copy()
        return y
    y = np.zeros(n, dtype=np.float64)
    y[d_int:] = x[:n - d_int]
    if d_frac > 0:
        y2 = np.zeros(n, dtype=np.float64)
        if d_int + 1 < n:
            y2[d_int + 1:] = x[:n - (d_int + 1)]
        y = (1.0 - d_frac) * y + d_frac * y2
    return y

def binaural_spatialize(x, az, distance, fs, head_radius=0.0875, c=343.0):
    """Woodworth-Schlosberg ITD + head-shadow ILD for a constant azimuth."""
    attn = 1.0 / max(distance, 1.0)
    xa = x * attn

    az = (az + np.pi) % (2 * np.pi) - np.pi
    abs_az = abs(az)
    tau = (head_radius / c) * (np.sin(abs_az) + abs_az)
    tau_samples = tau * fs

    delay_l = tau_samples if az >= 0.0 else 0.0
    delay_r = 0.0 if az >= 0.0 else tau_samples

    delayed_l = const_fractional_delay(xa, delay_l)
    delayed_r = const_fractional_delay(xa, delay_r)

    f_min, f_max, p = 1000.0, 20000.0, 2.0
    fc_l = (f_min + (f_max - f_min) * ((1.0 + np.cos(az)) / 2.0) ** p) if az >= 0.0 else f_max
    fc_r = (f_min + (f_max - f_min) * ((1.0 + np.cos(az)) / 2.0) ** p) if az < 0.0 else f_max

    out_l = first_order_lowpass_const(delayed_l, fc_l, fs)
    out_r = first_order_lowpass_const(delayed_r, fc_r, fs)
    return np.column_stack([out_l, out_r])

# process each voice
stereo_sum_l = None
stereo_sum_r = None
bin_paths = {}
for name, cfg in TRACK_CONFIG.items():
    x = mono[name][:dur]
    az = cfg["azimuth"]
    dist = cfg["distance"]
    st = binaural_spatialize(x, az, dist, SR)
    bin_paths[name] = STEMS_BIN / ("%s_binaural.wav" % name.lower())
    write_wav(bin_paths[name], st)
    print("%s: az=%.2f rad (%.1f deg) dist=%.2f  Lpeak=%.3f Rpeak=%.3f" %
          (name, az, np.degrees(az), dist,
           float(np.max(np.abs(st[:, 0]))), float(np.max(np.abs(st[:, 1])))))

    if stereo_sum_l is None:
        stereo_sum_l = st[:, 0].copy()
        stereo_sum_r = st[:, 1].copy()
    else:
        stereo_sum_l += st[:, 0]
        stereo_sum_r += st[:, 1]

wet = np.column_stack([stereo_sum_l, stereo_sum_r])
print("wet mix dur %.2fs" % (wet.shape[0] / SR))

# ---------------- master ----------------
wet_n = wet / max(1e-9, float(np.max(np.abs(wet)))) * 0.89
wet_lufs = normalize_to_lufs(wet_n, -14.0, SR)
final = Limiter(threshold_db=-1.0).process(wet_lufs)
lufs_val = measure_lufs(final, SR)
peak_val = float(np.max(np.abs(final)))
print("LUFS=%.2f peak=%.4f dur=%.2fs" % (lufs_val, peak_val, len(final) / SR))

WET_WAV = OUT / "SP021-binaural-ragtime-maple-leaf.wav"
write_wav(WET_WAV, final)
print("wet WAV %d B" % WET_WAV.stat().st_size)

OGG_OUT = OUT / "SP021-binaural-ragtime-maple-leaf.ogg"
r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(WET_WAV),
                    "-codec:a", "libopus", "-application", "voip", "-b:a", "48k",
                    str(OGG_OUT)], capture_output=True, text=True, timeout=180)
assert r.returncode == 0, "ffmpeg failed: %s" % r.stderr[-300:]
assert OGG_OUT.stat().st_size > 10000, "OGG empty"
print("WAV %d B  OGG %d B" % (WET_WAV.stat().st_size, OGG_OUT.stat().st_size))

# ---------------- silence / RMS ----------------
mono_final = (final[:, 0] + final[:, 1]) * 0.5
dry_m = load_mono(dry_full)
dry_m = dry_m[:len(mono_final)]
sil = float(np.sum(np.abs(mono_final) < 0.001) / len(mono_final))
sil_dry = float(np.sum(np.abs(dry_m) < 0.001) / len(dry_m))
rms_s = [float(np.sqrt(np.mean(mono_final[i:i + SR] ** 2))) for i in range(0, len(mono_final), SR)]
rms_dry = [float(np.sqrt(np.mean(dry_m[i:i + SR] ** 2))) for i in range(0, len(dry_m), SR)]
print("silence wet=%.4f dry=%.4f" % (sil, sil_dry))

# ---------------- pitch verification ----------------
def midi_to_freq(nn):
    return 440.0 * (2.0 ** ((nn - 69) / 12.0))

all_notes = {}
for (p, s, e) in pitched_notes:
    all_notes.setdefault(p, []).append((s, e))

win = int(0.5 * SR)
n_wins = len(mono_final) // win
freqs = np.fft.rfftfreq(win, 1.0 / SR)
mask = (freqs >= 50) & (freqs <= 2000)
checked = ok = 0
he_list, low_notes, dom_list, misses = [], [], [], []
for w in range(n_wins):
    t0w, t1w = w * 0.5, w * 0.5 + 0.5
    act = set()
    for pitch, lst in all_notes.items():
        for (a, b) in lst:
            if a < t1w and b > t0w:
                act.add(pitch)
                break
    if not act:
        continue
    seg = mono_final[w * win:(w + 1) * win]
    if len(seg) < win or float(np.sqrt(np.mean(seg ** 2))) < 0.01:
        continue
    spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
    f_band, s_band = freqs[mask], spec[mask]
    dom = float(f_band[int(np.argmax(s_band))])
    funds = sorted(midi_to_freq(p) for p in act)
    hit = any(abs(dom - c) / c < 0.04 for f in funds for c in (f, f * 2, f * 3, f / 2))
    checked += 1
    ok += 1 if hit else 0
    if not hit:
        misses.append({"t": round(t0w, 2), "dom": round(dom, 1), "act": sorted(act)})
    f0 = midi_to_freq(min(act))
    har = sum(s_band[np.abs(f_band - f0 * k) < max(15, f0 * 0.02)].sum() for k in range(1, 8))
    he_list.append(float(har / max(float(s_band.sum()), 1e-12)))
    low_notes.append(min(act))
    dom_list.append(dom)
hit_rate = ok / max(checked, 1)
he_mean = float(np.mean(he_list)) if he_list else 0.0
print("pitch windows=%d hit=%.4f he=%.4f" % (checked, hit_rate, he_mean))

# ACF unpitched check
ds = 5
md = mono_final[::ds]
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
print("acf windows=%d unpitched=%d" % (acf_n, unpitched))

pitch_ver = {
    "windows_checked": checked,
    "dominant_peak_hit_rate": round(hit_rate, 4),
    "harmonic_energy_mean_8h": round(he_mean, 4),
    "acf_windows": acf_n,
    "acf_unpitched": unpitched,
    "lowest_midi_notes_seen": sorted(set(low_notes))[:12],
    "median_dom_hz": round(float(np.median(dom_list)), 1) if dom_list else 0.0,
    "misses": misses[:12],
    "method": "FFT dominant peak per 0.5s window, 50-2000 Hz, +/-4% vs active MIDI fund or x2/x3//2",
    "verdict": ("PASS" if (hit_rate >= 0.60 and he_mean >= 0.30 and (unpitched / max(acf_n, 1)) < 0.50) else "FAIL"),
}
print("pitch verdict: %s" % pitch_ver["verdict"])
with open(ANALYSIS / "pitch_verification.json", "w") as f:
    json.dump(pitch_ver, f, indent=2)

stats = {
    "duration_s": round(len(final) / SR, 2),
    "silence_ratio_wet": round(sil, 4),
    "silence_ratio_dry": round(sil_dry, 4),
    "peak": round(peak_val, 4),
    "lufs": round(lufs_val, 2),
    "rms_per_second_wet": [round(r, 4) for r in rms_s],
    "rms_per_second_dry": [round(r, 4) for r in rms_dry],
    "wav_bytes": WET_WAV.stat().st_size,
    "ogg_bytes": OGG_OUT.stat().st_size,
    "dry_wav_bytes": dry_full.stat().st_size,
    "n_pitched_notes": len(pitched_notes),
    "track_config": {k: {"azimuth_rad": v["azimuth"], "azimuth_deg": round(np.degrees(v["azimuth"]), 1),
                          "distance": v["distance"]} for k, v in TRACK_CONFIG.items()},
    "head_radius_m": 0.0875,
    "speed_of_sound": 343.0,
}
with open(ANALYSIS / "render_stats.json", "w") as f:
    json.dump(stats, f, indent=2)

# ---------------- grid visualization (source rhythm DNA) ----------------
BAR = src_tpb * 4
bar_ticks = BAR
grid_lines = []
grid_lines.append("SP-021 source rhythm DNA - ragtime-maple-leaf.mid (C major, 120 BPM, 16 bars)")
grid_lines.append("rows = voices, columns = bars, '#'=onset '.'=rest")
name_by_track = {1: "PianoLH", 2: "PianoRH", 3: "Banjo"}
for ti, evs in sorted(track_summary.items()):
    n_bars = 1 + max((e // bar_ticks) for _, s, e in evs)
    row = [name_by_track.get(ti, "track %d" % ti)]
    for b in range(n_bars):
        b0, b1 = b * bar_ticks, (b + 1) * bar_ticks
        has = any(s < b1 and e > b0 for _, s, e in evs)
        row.append("#" if has else ".")
    grid_lines.append(" ".join(row))
grid_text = "\n".join(grid_lines) + "\n"
(ANALYSIS / "grid_visualization.txt").write_text(grid_text)
print(grid_text)

# ---------------- provenance ----------------
def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

prov = {
    "job": "random-style production pass (SP) - LAYER-ALIGNED 2026-10-04",
    "selection_source": "workflows.musicom_workflow.SP_METHODS registry (38 implemented)",
    "seed": SEED,
    "composition_source": str(SRC),
    "composition_sha256": sha256(str(SRC)),
    "production_method": "SP-021",
    "production_method_name": "Binaural HRTF Spatialization",
    "registered_module": "sound.synthesis.binaural",
    "layer_discipline": "absolute layer: SP-021 is a spatialization layer applied to the WHOLE ragtime render (per-voice Woodworth-Schlosberg ITD+ILD positioning, summed to stereo binaural image); no new notes written; FluidSynth GM render is the acoustic carrier",
    "sp021_params": {
        "head_radius_m": 0.0875,
        "speed_of_sound_ms": 343.0,
        "ild_f_min_hz": 1000.0,
        "ild_f_max_hz": 20000.0,
        "ild_exponent": 2.0,
        "track_config": {k: {"azimuth_rad": v["azimuth"], "azimuth_deg": round(np.degrees(v["azimuth"]), 2),
                              "distance": v["distance"]} for k, v in TRACK_CONFIG.items()},
    },
    "fixes": [],
    "checks": {"pitch_verification": pitch_ver, "silence_wet": round(sil, 4),
               "silence_dry": round(sil_dry, 4), "lufs": round(lufs_val, 2),
               "peak": round(peak_val, 4)},
    "artifacts": {"wav": str(WET_WAV), "ogg": str(OGG_OUT),
                  "dry_reference": str(dry_full),
                  "stems_mono": {k: str(v) for k, v in mono_paths.items()},
                  "stems_binaural": {k: str(v) for k, v in bin_paths.items()}},
}
with open(OUT / "provenance.json", "w") as f:
    json.dump(prov, f, indent=2)
print("provenance.json written")
print("DONE")
