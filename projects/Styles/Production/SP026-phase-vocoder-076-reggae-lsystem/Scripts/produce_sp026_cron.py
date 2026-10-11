#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SP-026 Spectral Phase Vocoder Resynthesis production pass on Reggae/076-reggae-lsystem.

Source : Styles/Reggae/076-reggae-lsystem/MIDI/076-reggae-lsystem.mid
         (reggae, 96 BPM, 480 tpb, 24 bars = 46080 ticks = 60.0 s:
          track1 Hammond Organ prog17 ch0 (120 notes, Am skank),
          track2 Elec Guitar jazz prog27 ch1 (240 notes, Am skank),
          track3 Elec Bass finger prog33 ch2 (144 notes, Am/G/C walk),
          track4 GM drums ch9 (272 hits, kick/snare/hihat one-drop))

Method : SP-026 -> sound.effects.phase_vocoder (SP_METHODS registry).
         Spectral Phase Vocoder Resynthesis — Flanagan time-stretch +
         harmonic sharpening (freeze disabled; see Phase-2 note).

Layer  : ABSOLUTE. The phase vocoder re-synthesizes the WHOLE mixed signal
         (all 4 voices together): time axis is stretched by alpha=1.2 and the
         spectrum is re-emphasised |X|^1.12. Pitch content is preserved
         (STFT phase propagation), only time + spectral tilt change. FluidSynth
         GM (SP-001) is the acoustic carrier (dry reference first).

Chain:
  source.mid -> fluidsynth -ni -R0 -C0 -g1.2 (dry full mix, FluidR3_GM.sf2)
  -> dry stems (RenderPipeline)
  -> phase_vocoder(alpha=1.2, freeze=False, sharpness=1.12) per channel on full
     mix + each stem (absolute layer)
  -> normalize_to_lufs(-14) -> Limiter(-1 dBFS) LAST
  -> SP026-phase-vocoder-076-reggae-lsystem.wav + .ogg (Opus 48k voip)
  -> pitch verification + silence/RMS -> provenance + REPORT.md
"""
import hashlib
import json
import shutil
import subprocess
import wave
from pathlib import Path

import numpy as np

from sound.render.fluidsynth import discover_soundfont
from sound.render.pipeline import RenderPipeline
from sound.effects.phase_vocoder import phase_vocoder
from sound.effects.mastering import normalize_to_lufs, measure_lufs, Limiter

SRC = Path("/opt/data/repos/musicom/projects/Styles/Reggae/076-reggae-lsystem/MIDI/076-reggae-lsystem.mid")
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/SP026-phase-vocoder-076-reggae-lsystem")
AUD = OUT / "Audio"
STEMS_DRY = AUD / "stems_dry"
STEMS_WET = AUD / "stems_wet"
MIDIDIR = OUT / "MIDI"
ANALYSIS = OUT / "Analysis"
SCRIPTS = OUT / "Scripts"

for d in (AUD, STEMS_DRY, STEMS_WET, MIDIDIR, ANALYSIS, SCRIPTS):
    d.mkdir(parents=True, exist_ok=True)

SR = 44100
TPB = 480
BPM = 96.0
SPB = 60.0 / BPM          # 0.625 s/beat
BAR_TICKS = TPB * 4       # 1920
N_BARS = 24
TOTAL_TICKS = BAR_TICKS * N_BARS   # 46080
SEED = 20261011

# SP-026 parameters
ALPHA = 1.2               # time-stretch (alpha > 1 = slower/longer)
SHARPNESS = 1.12          # spectral emphasis |X|^sharpness
FREEZE = False            # freeze disabled — see Phase-2 note (decay-tail bug)
N_FFT = 2048
HOP = 512

FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    if r.returncode != 0:
        raise RuntimeError("cmd failed %s: %s" % (cmd, r.stderr[-800:]))
    return r


# ===========================================================================
# Ground-truth note list (dry seconds) for pitch verification, non-drum voices
# ===========================================================================
import mido

mf = mido.MidiFile(str(SRC))
all_notes = []      # (pitch, start_s, end_s) in DRY seconds
drum_channels = set()
for tr in mf.tracks:
    chans = {m.channel for m in tr if m.type in ("note_on", "note_off")}
    is_drum = 9 in chans
    t = 0
    on = {}
    for m in tr:
        t += m.time
        if m.type == "note_on" and m.velocity > 0:
            if is_drum:
                continue
            on[m.note] = t
        elif m.type == "note_off" and m.note in on:
            s = on.pop(m.note)
            all_notes.append((m.note, s * SPB / TPB, t * SPB / TPB))
        elif m.type == "note_on" and m.velocity == 0 and m.note in on:
            s = on.pop(m.note)
            all_notes.append((m.note, s * SPB / TPB, t * SPB / TPB))

print("ground-truth notes (non-drum):", len(all_notes))
print("pitch range:", min(p for p, _, _ in all_notes), "-", max(p for p, _, _ in all_notes))

# ===========================================================================
# Pre-flight three-rule audit (re-run; record numbers)
# ===========================================================================
grid_off = 0
scale_pcs = {9, 11, 0, 2, 4, 5, 7}   # A natural minor
out_of_scale = 0
for tr in mf.tracks:
    chans = {m.channel for m in tr if m.type in ("note_on", "note_off")}
    is_drum = 9 in chans
    t = 0
    for m in tr:
        t += m.time
        if m.type == "note_on" and m.velocity > 0:
            if is_drum:
                continue
            if (t % 120) != 0:
                grid_off += 1
            if (m.note % 12) not in scale_pcs:
                out_of_scale += 1
track_ends = []
for tr in mf.tracks:
    t = 0
    for m in tr:
        t += m.time
    if t > 0:
        track_ends.append(t)
zero_drift = len(set(track_ends)) == 1
print("PREFLIGHT grid_off=%d out_of_scale=%d track_ends=%s zero_drift=%s"
      % (grid_off, out_of_scale, sorted(set(track_ends)), zero_drift))
assert grid_off == 0, "grid sync FAILED"
assert out_of_scale == 0, "harmony FAILED"
assert zero_drift, "zero-drift FAILED"

# copy source MIDI alongside
shutil.copy2(str(SRC), str(MIDIDIR / SRC.name))

# ===========================================================================
# Render: FluidSynth dry full mix (FX off) + dry stems
# ===========================================================================
SF = discover_soundfont()
assert SF and Path(SF).exists(), "SoundFont missing: %r" % SF
print("SoundFont:", SF)

dry_full = OUT / "dry_full_mix_sp001_reference.wav"
print("Rendering dry full mix (FluidSynth, reverb/chorus OFF)...")
run([FLUID, "-ni", "-R", "0", "-C", "0", "-g", "1.2", "-F", str(dry_full),
     "-r", str(SR), SF, str(SRC)])
print("dry full mix:", dry_full.stat().st_size, "bytes")

print("Rendering dry stems (RenderPipeline)...")
pipe = RenderPipeline(soundfont_path=SF, fluidsynth_bin=FLUID, sample_rate=SR)
stems = pipe.render_stems(str(SRC), str(STEMS_DRY), format="wav")
print("dry stems:", sorted(stems.keys()))


def read_wav(p):
    with wave.open(str(p), "rb") as wf:
        nch = wf.getnchannels()
        sr = wf.getframerate()
        n = wf.getnframes()
        raw = np.frombuffer(wf.readframes(n), dtype=np.int16).astype(np.float64) / 32768.0
    if nch == 2:
        return raw.reshape(-1, 2), sr
    return np.column_stack([raw, raw]), sr


def write_wav(p, audio, sr=SR):
    a = np.clip(np.asarray(audio), -1.0, 1.0)
    if a.ndim == 1:
        data = (a * 32767.0).astype(np.int16).tobytes()
        nch = 1
    else:
        data = (a * 32767.0).astype(np.int16).reshape(-1).tobytes()
        nch = a.shape[1]
    with wave.open(str(p), "wb") as wf:
        wf.setnchannels(nch)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(data)


def apply_pv_stereo(audio, sr=SR):
    """Absolute-layer phase vocoder: per channel, same params."""
    out = []
    for ch in range(audio.shape[1]):
        out.append(phase_vocoder(audio[:, ch], sr=sr, alpha=ALPHA,
                                 freeze=FREEZE, sharpness=SHARPNESS,
                                 n_fft=N_FFT, hop=HOP))
    return np.stack(out, axis=1)


# ===========================================================================
# Apply SP-026 (absolute layer) to full mix
# ===========================================================================
mix, _sr = read_wav(dry_full)
print("dry mix shape:", mix.shape, "sr", _sr, "dur_s", round(len(mix)/_sr, 2))
wet_mix = apply_pv_stereo(mix, _sr)
print("wet mix shape:", wet_mix.shape, "dur_s", round(len(wet_mix)/_sr, 2))

# ===========================================================================
# Master: normalize_to_lufs(-14) -> Limiter(-1 dBFS) LAST
# ===========================================================================
mix_norm = normalize_to_lufs(wet_mix, target_lufs=-14.0, sample_rate=SR)
limiter = Limiter(threshold_db=-1.0, sample_rate=SR)
final = limiter.process(mix_norm)          # (N, 2)

final_wav = OUT / "SP026-phase-vocoder-076-reggae-lsystem.wav"
final_ogg = OUT / "SP026-phase-vocoder-076-reggae-lsystem.ogg"
write_wav(final_wav, final)
print("final WAV:", final_wav.stat().st_size, "bytes")

r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(final_wav),
                    "-codec:a", "libopus", "-application", "voip", "-b:a", "48k",
                    str(final_ogg)], capture_output=True, text=True, timeout=180)
assert r.returncode == 0, "ffmpeg failed: %s" % r.stderr[-300:]
assert final_ogg.stat().st_size > 10000, "OGG empty"
print("final OGG:", final_ogg.stat().st_size, "bytes")

# ===========================================================================
# Wet stems (same absolute-layer params, per-stem DAW convenience)
# ===========================================================================
stem_meta = []
for name, sp in sorted(stems.items()):
    a, sr = read_wav(sp)
    w = apply_pv_stereo(a, sr)
    out_p = STEMS_WET / (Path(sp).stem + "_PV.wav")
    write_wav(out_p, w, sr)
    stem_meta.append((name, sp, out_p, round(len(w)/sr, 2)))
    print("wet stem %s -> %s (%.2f s)" % (name, out_p.name, len(w)/sr))

# ===========================================================================
# Verification: silence / RMS / LUFS / pitch fidelity / harmonic energy / ACF
# ===========================================================================
meas_lufs = measure_lufs(final, sample_rate=SR)
peak_val = float(np.max(np.abs(final)))
mono = 0.5 * (final[:, 0] + final[:, 1])
silence_pct = float(np.sum(np.abs(mono) < 0.001) / len(mono)) * 100.0
rms = float(np.sqrt(np.mean(mono ** 2)))
rms_map = [round(float(np.sqrt(np.mean(mono[i:i + SR] ** 2))), 4)
           for i in range(0, len(mono), SR)]
print("LUFS=%.2f peak=%.4f silence=%.2f%% rms=%.4f" % (meas_lufs, peak_val, silence_pct, rms))


def midi_to_freq(n):
    return 440.0 * (2.0 ** ((n - 69) / 12.0))


# time-stretch: wet note times ~= dry times * ALPHA
win = int(0.5 * SR)
n_wins = len(mono) // win
freqs = np.fft.rfftfreq(win, 1.0 / SR)
mask = (freqs >= 50.0) & (freqs <= 3000.0)

checked = hits = 0
he_list, dom_list, misses = [], [], []
for w in range(n_wins):
    t0, t1 = w * 0.5, w * 0.5 + 0.5
    act = set()
    for (p, a, b) in all_notes:
        # wet = dry * ALPHA
        if a * ALPHA < t1 and b * ALPHA > t0:
            act.add(p)
    if not act:
        continue
    seg = mono[w * win:(w + 1) * win]
    if len(seg) < win or float(np.sqrt(np.mean(seg ** 2))) < 0.01:
        continue
    spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
    f_band, s_band = freqs[mask], spec[mask]
    dom = float(f_band[int(np.argmax(s_band))])
    dom_list.append(dom)
    funds = sorted(midi_to_freq(p) for p in act)
    hit = any(abs(dom - c) / c < 0.04 for f in funds for c in (f, f * 2, f * 3, f * 4, f / 2, f / 3))
    checked += 1
    hits += 1 if hit else 0
    if not hit:
        misses.append({"t": round(t0, 2), "dom": round(dom, 1), "act": sorted(act)})
    tot = np.sum(s_band ** 2) + 1e-12
    he = 0.0
    for k in range(1, 9):
        tf = dom * k
        he += np.sum(s_band[(f_band >= tf - 15.0) & (f_band <= tf + 15.0)] ** 2)
    he_list.append(float(he / tot))

hit_rate = hits / max(checked, 1)
he_mean = float(np.mean(he_list)) if he_list else 0.0

# ACF unpitched check
ds = 5
md = mono[::ds]
sd = SR // ds
ww = sd
unpitched = acf_n = 0
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

pitch_verdict = "PASS" if (hit_rate >= 0.60 and he_mean >= 0.25
                           and (unpitched / max(acf_n, 1)) < 0.50) else "FAIL"
print("pitch windows=%d hit=%.4f he=%.4f acf_unpitched=%d/%d -> %s"
      % (checked, hit_rate, he_mean, unpitched, acf_n, pitch_verdict))

# ===========================================================================
# Grid visualization (source onset DNA)
# ===========================================================================
grid_lines = [
    "SP-026 Phase Vocoder — source onset DNA (A minor, 96 BPM, 24 bars, 480 tpb)",
    "rows = voices, columns = 16th-note slots per bar, '#'=onset '.'=rest",
    "",
]
slot_ticks = TPB // 4   # 120 (16th)
from collections import defaultdict

per_track = defaultdict(list)
for tr in mf.tracks:
    chans = {m.channel for m in tr if m.type in ("note_on", "note_off")}
    if 9 in chans:
        continue
    t = 0
    prog = None
    for m in tr:
        t += m.time
        if m.type == "program_change":
            prog = m.program
        if m.type == "note_on" and m.velocity > 0:
            per_track[prog].append(t)

names = {17: "Organ", 27: "Guitar", 33: "Bass"}
for prog, onsets in per_track.items():
    row = []
    for b in range(N_BARS):
        for s in range(16):
            b0 = b * BAR_TICKS + s * slot_ticks
            b1 = b0 + slot_ticks
            has = any(b0 <= o < b1 for o in onsets)
            row.append("#" if has else ".")
    grid_lines.append("%-8s %s" % (names.get(prog, "prog%d" % prog), "".join(row)))
grid_lines.append("")
grid_lines.append("SP-026 absolute layer: alpha=1.2 time-stretch + |X|^1.12 sharpen on the WHOLE mix.")
(ANALYSIS / "grid_visualization.txt").write_text("\n".join(grid_lines) + "\n")
print("\n".join(grid_lines))

# ===========================================================================
# Provenance + analysis JSON
# ===========================================================================
def sha256(p):
    h = hashlib.sha256()
    with open(str(p), "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

(ANALYSIS / "render_stats.json").write_text(json.dumps({
    "method": "SP-026", "method_module": "sound.effects.phase_vocoder",
    "layer": "absolute", "seed": SEED,
    "alpha": ALPHA, "sharpness": SHARPNESS, "freeze": FREEZE,
    "n_fft": N_FFT, "hop": HOP,
    "key": "A natural minor", "bpm": BPM, "bars": N_BARS, "ticks_per_beat": TPB,
    "source_duration_s": 60.0, "wet_duration_s": round(len(mono) / SR, 2),
    "preflight": {"grid_off": grid_off, "out_of_scale": out_of_scale,
                  "zero_drift": zero_drift, "track_ends": sorted(set(track_ends))},
    "n_notes_total": len(all_notes),
    "pitch_range": [min(p for p, _, _ in all_notes), max(p for p, _, _ in all_notes)],
    "lufs": round(meas_lufs, 2), "peak": round(peak_val, 4),
    "silence_pct": round(silence_pct, 2), "rms": round(rms, 4),
    "rms_per_second": rms_map,
    "windows_checked": checked, "hit_rate": round(hit_rate, 4),
    "harmonic_energy_mean": round(he_mean, 4),
    "acf_windows": acf_n, "acf_unpitched": unpitched,
    "pitch_verdict": pitch_verdict,
    "median_dom_hz": round(float(np.median(dom_list)), 1) if dom_list else 0.0,
    "stems_wet": [{"stem": n, "src": str(s), "out": str(o), "dur_s": d}
                  for n, s, o, d in stem_meta],
}, indent=2))

(ANALYSIS / "pitch_verification.json").write_text(json.dumps({
    "method": "SP-026", "project": "Reggae/076-reggae-lsystem",
    "key": "A natural minor", "status": pitch_verdict,
    "hit_rate": round(hit_rate, 4), "harmonic_energy_mean": round(he_mean, 4),
    "acf_unpitched": unpitched, "acf_windows": acf_n,
    "windows_analyzed": checked,
    "median_dom_hz": round(float(np.median(dom_list)), 1) if dom_list else 0.0,
    "note_times_used": "dry_seconds_scaled_by_alpha(1.2)",
    "misses": misses[:12],
}, indent=2))

provenance = {
    "job": "random-style production (SP) layer-aligned",
    "date": "2026-10-11",
    "seed": SEED,
    "method": "SP-026",
    "method_module": "sound.effects.phase_vocoder",
    "method_desc": "Spectral Phase Vocoder Resynthesis",
    "layer": "absolute (phase vocoder re-synthesizes the WHOLE mix: time-stretch + sharpen)",
    "selection_source": "workflows.musicom_workflow.SP_METHODS registry (42 implemented)",
    "source_midi": str(SRC),
    "source_sha256": sha256(SRC),
    "output_midi": str(MIDIDIR / SRC.name),
    "output_wav": str(final_wav),
    "output_ogg": str(final_ogg),
    "params": {
        "key": "A natural minor", "bpm": BPM, "bars": N_BARS,
        "alpha": ALPHA, "sharpness": SHARPNESS, "freeze": FREEZE,
        "n_fft": N_FFT, "hop": HOP,
    },
    "preflight": {"grid_off": grid_off, "out_of_scale": out_of_scale,
                  "zero_drift": zero_drift},
    "lufs": round(meas_lufs, 2), "peak": round(peak_val, 4),
    "silence_pct": round(silence_pct, 2), "rms": round(rms, 4),
    "pitch_verdict": pitch_verdict, "hit_rate": round(hit_rate, 4),
    "he_mean": round(he_mean, 4),
    "phase2_notes": (
        "freeze=False because phase_vocoder()'s freeze branch applies the exponential "
        "decay envelope to y[tail_len*sr:] (i.e. from 2 s to END), which for a 60 s "
        "source would suppress ~97% of the audio (verified empirically: a steady 4 s "
        "chord's RMS fell 0.54->0.03 by second 3). Pure Flanagan time-stretch "
        "(alpha=1.2) + |X|^1.12 spectral sharpening is used instead; freeze omitted. "
        "Pitch verification maps source note times by alpha=1.2 (linear stretch)."
    ),
}
(OUT / "provenance.json").write_text(json.dumps(provenance, indent=2))

(ANALYSIS / "select_20261011.json").write_text(json.dumps({
    "date": "2026-10-11", "method": "SP-026",
    "method_module": "sound.effects.phase_vocoder",
    "source_midi": str(SRC),
    "recent_excluded": ["SP-021", "SP-069", "SP-080", "SP-085", "SP-091", "SP-092", "SP-098"],
    "registry_total": 42, "n_well_formed": 225, "n_candidates": 334,
}, indent=2))

if str(Path(__file__).resolve()) != str((SCRIPTS / "produce_sp026_cron.py").resolve()):
    shutil.copy2(__file__, str(SCRIPTS / "produce_sp026_cron.py"))
print("Done. pitch_verdict=", pitch_verdict)
