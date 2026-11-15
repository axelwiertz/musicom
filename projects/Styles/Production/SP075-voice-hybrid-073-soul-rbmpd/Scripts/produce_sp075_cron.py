# -*- coding: utf-8 -*-
"""SP-075 Voice-Like Instrument Hybrid Render -- 073-soul-rbmpd (2026-11-15).

Source : Styles/Soul/073-soul-rbmpd — Soul / Method 048 RBMPD, C natural
         minor, 92 BPM, 24 bars (6 sections x 4). Lead voice was reworked by
         the pre-flight gate (grid-quantized to 16ths + chord-tone quantized
         against the correct global progression); original raw kept as a
         phase1 sidecar.

Method : SP-075 -> sound.render.hybrid (render_hybrid).
Layer  : ABSOLUTE — the whole piece is re-realized through SP-075. The Lead
         (the "singer") has no GM equivalent, so it becomes a talkbox
         (formant voice, Peter Frampton-style soul). Horns/Rhodes/Bass/Drums
         stay on the FluidSynth soundfont as the backing band.
         voice_instruments = ["talkbox", None, None, None, None] aligned to
         note-bearing tracks (Lead, Horns, Rhodes, Bass, Drums); tempo track 0
         skipped by parse_tracks().

Pitch verification against the EXPECTED MIDI note frequencies (SP-075 replaces
timbre, so dry-vs-wet spectral match is meaningless): each 0.5s window's FFT
dominant peak (50-1000 Hz) compared to the notes the MIDI sounds there.
"""
import json
import shutil
import subprocess
import time
from pathlib import Path

import numpy as np
import mido

from sound.render.hybrid import (
    render_hybrid, parse_tracks, _render_voice_track,
    _render_backing_fluidsynth, VOICE_VOWEL_CYCLE,
)
from sound.render.fluidsynth import discover_soundfont
from sound.render.pipeline import RenderPipeline
from sound.synthesis.voice_like import INSTRUMENTS
from sound.effects.mastering import master, target_for_style, measure_lufs
from sound.utils.io import read_wav, write_wav
from utilities.env import fluidsynth_bin

OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/SP075-voice-hybrid-073-soul-rbmpd")
SRC = OUT / "MIDI" / "073-soul-rbmpd.mid"          # reworked (gate-clean)
AUD = OUT / "Audio"
STEMS_DRY = AUD / "stems_dry"
STEMS_WET = AUD / "stems_wet"
ANALYSIS = OUT / "Analysis"
SCRIPTS = OUT / "Scripts"

for d in (AUD, STEMS_DRY, STEMS_WET, ANALYSIS, SCRIPTS):
    d.mkdir(parents=True, exist_ok=True)

SR = 44100
SEED = 20261115
STYLE = "Soul"
TARGET_LUFS = target_for_style(STYLE)     # -13.0
CEILING_DB = -1.0
VOICE_INSTRUMENTS = ["talkbox", None, None, None, None]
VOWELS = list("aoeauo")
VOICE_GAIN = 1.0
BACKING_GAIN = 1.0

SF = discover_soundfont()
assert SF and Path(SF).exists(), f"SoundFont missing: {SF}"
FLUID = fluidsynth_bin()

# source BPM
mf_src = mido.MidiFile(str(SRC))
BPM = 120.0
for tr in mf_src.tracks:
    for m in tr:
        if m.type == "set_tempo":
            BPM = round(60000000.0 / m.tempo, 2)
print("source BPM =", BPM, "| length_s =", round(mf_src.length, 2))

# ---------------------------------------------------------------------------
# 0. parse tracks
# ---------------------------------------------------------------------------
tracks, tpb, total_ticks = parse_tracks(str(SRC))
track_names = []
for t in tracks:
    label = "Drums" if t.channel == 9 else (
        "Lead" if t.index == 0 else "Horns" if t.index == 1 else
        "Rhodes" if t.index == 2 else "Bass" if t.index == 3 else
        f"prog{t.program}_ch{t.channel}")
    track_names.append(label)
print(f"note-bearing tracks={len(tracks)} tpb={tpb} total_ticks={total_ticks}")
for t in tracks:
    print(f"  idx={t.index} midi_track={t.midi_track} ch={t.channel} "
          f"prog={t.program} notes={len(t.notes)}")

# ---------------------------------------------------------------------------
# 1. dry full mix (SP-001 reference, reverb/chorus off)
# ---------------------------------------------------------------------------
dry_full = OUT / "dry_full_mix_sp001_reference.wav"
print("Rendering dry full mix (SP-001 reference)...")
r = subprocess.run([
    FLUID, "-ni", "-g", "1.2", "-F", str(dry_full), "-r", str(SR),
    "-o", "synth.reverb.active=no", "-o", "synth.chorus.active=no",
    SF, str(SRC),
], capture_output=True, text=True, timeout=900)
if r.returncode != 0 or not dry_full.exists() or dry_full.stat().st_size < 1000:
    raise RuntimeError(f"FluidSynth dry render failed: {r.stderr[-500:]}")
print(f"Dry full mix: {dry_full.stat().st_size} bytes")

# ---------------------------------------------------------------------------
# 2. SP-075 hybrid render (canonical full mix)
# ---------------------------------------------------------------------------
hybrid_raw = OUT / "hybrid_raw_mono.wav"
print("Rendering SP-075 hybrid (talkbox lead + FluidSynth backing)...")
t0 = time.time()
info = render_hybrid(
    str(SRC), VOICE_INSTRUMENTS, str(hybrid_raw),
    sr=SR, bpm=BPM, vowels=VOWELS,
    voice_gain=VOICE_GAIN, backing_gain=BACKING_GAIN, seed=SEED,
)
print(f"  hybrid done in {time.time()-t0:.1f}s: {info['seconds']:.2f}s, "
      f"tracks={info['tracks']}, backing_rendered={info['backing_rendered']}")

# ---------------------------------------------------------------------------
# 3. master: target LUFS (-13 soul) + true-peak limit -1 dBTP
# ---------------------------------------------------------------------------
mix, _sr = read_wav(str(hybrid_raw))
if mix.ndim == 1:
    mix = np.column_stack([mix, mix])
mix = np.asarray(mix, dtype=np.float32)
assert _sr == SR, f"unexpected sr {_sr}"
print("hybrid mix shape:", mix.shape, "peak", float(np.max(np.abs(mix))))

mastered, rep = master(mix, target_lufs=TARGET_LUFS, ceiling_db=CEILING_DB,
                       sample_rate=SR)
print("master report: LUFS %.2f, true peak %.2f dBTP"
      % (float(rep.get("integrated_lufs", 0)), float(rep.get("true_peak_db", 0))))

final_wav = OUT / "SP075-voice-hybrid-073-soul-rbmpd.wav"
final_ogg = OUT / "SP075-voice-hybrid-073-soul-rbmpd.ogg"
write_wav(str(final_wav), mastered.astype(np.float32), SR, normalize=False)
r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(final_wav),
                    "-codec:a", "libopus", "-application", "voip", "-b:a", "48k",
                    str(final_ogg)], capture_output=True, text=True, timeout=180)
assert r.returncode == 0 and final_ogg.stat().st_size > 10000, \
    "ogg encode failed: %s" % r.stderr[-300:]
print("final WAV:", final_wav.stat().st_size, "final OGG:", final_ogg.stat().st_size)

# ---------------------------------------------------------------------------
# 4. wet stems (talkbox lead + fluidsynth backing)
# ---------------------------------------------------------------------------
print("Rendering wet stems...")
wet_stem_paths = {}
for i, key in enumerate(VOICE_INSTRUMENTS):
    if key is None:
        continue
    seg = _render_voice_track(tracks[i], key, tpb, BPM, SR,
                              vowels=VOWELS, seed=SEED + i * 7919)
    name = f"track{i:02d}_{track_names[i]}_{key}"
    write_wav(str(STEMS_WET / f"{name}.wav"), seg, SR, normalize=False)
    wet_stem_paths[name] = STEMS_WET / f"{name}.wav"
    print(f"  wet voice stem {name}: {len(seg)/SR:.2f}s")

mute = [tracks[i].midi_track for i in range(len(VOICE_INSTRUMENTS))
        if VOICE_INSTRUMENTS[i] is not None]
backing_wav = _render_backing_fluidsynth(str(SRC), mute,
                                         str(STEMS_WET / "_backing.wav"),
                                         tpb, SR)
if backing_wav:
    b, _ = read_wav(backing_wav)
    if b.ndim > 1:
        b = b.mean(axis=1)
    name = "track_backing_fluidsynth"
    write_wav(str(STEMS_WET / f"{name}.wav"), b, SR, normalize=False)
    wet_stem_paths[name] = STEMS_WET / f"{name}.wav"
    Path(backing_wav).unlink()
    print(f"  wet backing stem {name}: {len(b)/SR:.2f}s")

# ---------------------------------------------------------------------------
# 5. dry stems (RenderPipeline per-track soundfont)
# ---------------------------------------------------------------------------
try:
    pipeline = RenderPipeline(soundfont_path=SF, fluidsynth_bin=FLUID,
                              sample_rate=SR)
    dry_stems = pipeline.render_stems(str(SRC), str(STEMS_DRY), format="wav")
    print("dry stems:", list(dry_stems))
    stems_ok = True
except Exception as exc:
    print("dry stems FAILED:", exc)
    dry_stems = {}
    stems_ok = False

# ---------------------------------------------------------------------------
# 6. verification (pitch vs expected notes + silence + RMS + ACF)
# ---------------------------------------------------------------------------
mono = 0.5 * (mastered[:, 0] + mastered[:, 1])

meas_lufs = float(measure_lufs(mastered, sample_rate=SR))
peak_val = float(np.max(np.abs(mono)))
silence_pct = float(np.sum(np.abs(mono) < 0.001) / len(mono)) * 100.0
rms_map = [round(float(np.sqrt(np.mean(mono[i:i + SR] ** 2))), 4)
           for i in range(0, len(mono), SR)]
print(f"LUFS={meas_lufs:.2f} peak={peak_val:.4f} silence={silence_pct:.2f}%")


def midi_to_freq(p):
    return 440.0 * 2.0 ** ((p - 69) / 12.0)


sec_per_tick = 60.0 / (BPM * tpb)
all_notes = []
for t in tracks:
    for n in t.notes:
        all_notes.append((n["start_ticks"] * sec_per_tick,
                          n["end_ticks"] * sec_per_tick,
                          midi_to_freq(n["pitch"])))

win = int(0.5 * SR)
n_wins = len(mono) // win
freqs = np.fft.rfftfreq(win, 1.0 / SR)
mask_fund = (freqs >= 50.0) & (freqs <= 1000.0)

checked = hits = 0
he_list, dom_list, misses = [], [], []
for w in range(n_wins):
    ws = w * 0.5
    we = ws + 0.5
    seg_w = mono[w * win:(w + 1) * win]
    if np.sqrt(np.mean(seg_w ** 2)) < 0.005:
        continue
    exp = [f for (s, e, f) in all_notes if e > ws and s < we]
    if not exp:
        continue
    spec_w = np.abs(np.fft.rfft(seg_w * np.hanning(win)))
    fw = freqs[mask_fund]
    sw = spec_w[mask_fund]
    dom = float(fw[int(np.argmax(sw))])
    checked += 1
    dom_list.append(dom)
    tot = np.sum(spec_w ** 2) + 1e-12
    he_mask = np.zeros(len(freqs), dtype=bool)
    for ef in exp:
        for h in range(1, 9):
            tf = ef * h
            if tf >= freqs[-1]:
                continue
            he_mask |= (freqs >= tf - 15) & (freqs <= tf + 15)
    he = float(np.sum(spec_w[he_mask] ** 2) / tot)
    he_list.append(he)
    ratios = [1.0, 2.0, 3.0, 4.0, 0.5, 1.0 / 3.0]
    hit = False
    for ef in exp:
        for rr in ratios:
            if abs(dom - ef * rr) / (ef * rr) < 0.04:
                hit = True
                break
        if hit:
            break
    if hit:
        hits += 1
    else:
        misses.append({"t": round(ws, 2), "dom": round(dom, 1),
                       "expected": [round(x, 1) for x in sorted(set(exp))]})

hit_rate = hits / max(checked, 1)
he_mean = float(np.mean(he_list)) if he_list else 0.0

# ACF unpitched check (SP-035 failure signature: broadband noise)
ds = 5
md = mono[::ds]
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
print(f"Pitch verification: windows={checked}, hit_rate={hit_rate:.4f}, "
      f"harmonic_energy={he_mean:.4f}, ACF unpitched={unpitched}/{acf_n} "
      f"-> {pitch_verdict}")

# ---------------------------------------------------------------------------
# 7. artifacts
# ---------------------------------------------------------------------------
(ANALYSIS / "render_stats.json").write_text(json.dumps({
    "method": "SP-075", "method_module": "sound.render.hybrid",
    "method_desc": "Voice-Like Instrument Hybrid Render (synthesized voice tracks + SoundFont backing)",
    "layer": "absolute", "voice_instruments": VOICE_INSTRUMENTS,
    "vowels": VOWELS, "voice_gain": VOICE_GAIN, "backing_gain": BACKING_GAIN,
    "seed": SEED, "bpm": BPM, "sr": SR,
    "target_lufs": TARGET_LUFS, "ceiling_db": CEILING_DB,
    "tracks": [{"index": t.index, "midi_track": t.midi_track, "channel": t.channel,
                "program": t.program, "notes": len(t.notes)} for t in tracks],
    "available_instruments": sorted(INSTRUMENTS),
    "lufs": round(meas_lufs, 2), "peak": peak_val,
    "silence_pct": round(silence_pct, 2), "rms_per_second": rms_map,
    "windows_checked": checked, "midi_note_hit_rate": round(hit_rate, 4),
    "harmonic_energy_mean": round(he_mean, 4),
    "acf_windows": acf_n, "acf_unpitched": unpitched,
    "pitch_verdict": pitch_verdict,
    "median_dom_hz": round(float(np.median(dom_list)), 1) if dom_list else 0.0,
    "duration_sec": round(len(mono) / SR, 2),
    "stems_ok": stems_ok, "n_dry_stems": len(dry_stems),
}, indent=2))

(ANALYSIS / "pitch_verification.json").write_text(json.dumps({
    "method": "SP-075", "project": "073-soul-rbmpd",
    "status": pitch_verdict, "midi_note_hit_rate": hit_rate,
    "harmonic_energy_mean": he_mean, "acf_unpitched": unpitched,
    "acf_windows": acf_n, "windows_analyzed": checked,
    "median_dom_hz": round(float(np.median(dom_list)), 1) if dom_list else 0.0,
    "misses": misses[:12],
}, indent=2))

grid_lines = [
    "SP-075 Voice-Like Instrument Hybrid -- absolute layer (073-soul-rbmpd)",
    f"seed={SEED} bpm={BPM} target_lufs={TARGET_LUFS} vowels={''.join(VOWELS)}",
    "",
    "track -> engine -> instrument",
]
for i, t in enumerate(tracks):
    engine = "voice_like" if (i < len(VOICE_INSTRUMENTS) and VOICE_INSTRUMENTS[i]) else "fluidsynth"
    inst = VOICE_INSTRUMENTS[i] if i < len(VOICE_INSTRUMENTS) else None
    grid_lines.append(f"  track{i:02d} {track_names[i]:10s} -> {engine:11s} "
                      f"{inst if inst else 'soundfont'} (prog {t.program}, ch {t.channel}, {len(t.notes)} notes)")
grid_lines.append("")
grid_lines.append("wet stems:")
for name in sorted(wet_stem_paths):
    grid_lines.append(f"  {name}.wav")
(ANALYSIS / "grid_visualization.txt").write_text("\n".join(grid_lines) + "\n")

# provenance.json — include pre-flight audit + rework numbers
rework_audit = {}
rpath = OUT / "MIDI" / "rework_audit.json"
if rpath.exists():
    rework_audit = json.loads(rpath.read_text())

provenance = {
    "job": "random-style production (SP) layer-aligned",
    "date": "2026-11-15", "seed": SEED,
    "method": "SP-075", "method_module": "sound.render.hybrid",
    "method_desc": "Voice-Like Instrument Hybrid Render (synthesized voice tracks + SoundFont backing)",
    "layer": "absolute",
    "source_midi": str(SRC),
    "source_project": "Soul/073-soul-rbmpd",
    "source_key": "C natural minor", "source_bpm": BPM,
    "preflight": {
        "zero_drift": "PASS (46080)", "in_scale": "PASS (0)",
        "grid_sync": "FAIL (27003 off-grid lead) -> FIXED",
        "chord_tone": "FAIL (4766 out-of-chord lead) -> FIXED",
        "rework_audit": rework_audit,
    },
    "voice_instruments": VOICE_INSTRUMENTS,
    "output_wav": str(final_wav), "output_ogg": str(final_ogg),
    "dry_reference_wav": str(dry_full),
    "target_lufs": TARGET_LUFS, "ceiling_db": CEILING_DB,
    "lufs": round(meas_lufs, 2), "peak": peak_val,
    "silence_pct": round(silence_pct, 2),
    "pitch_verdict": pitch_verdict,
    "midi_note_hit_rate": round(hit_rate, 4), "he_mean": round(he_mean, 4),
    "stems_ok": stems_ok, "n_dry_stems": len(dry_stems),
}
(OUT / "provenance.json").write_text(json.dumps(provenance, indent=2))

# copy this script + rework script for reproducibility
shutil.copy(__file__, SCRIPTS / "produce_sp075_cron.py")
print("DONE")
