# -*- coding: utf-8 -*-
"""SP-079 ACID SEQ (scale-locked acid sequencer + 303/202 voice) — 050-pcfg-daw-sync.

Source: Styles/Experimental/050-pcfg-daw-sync/MIDI/050-pcfg-daw-sync_Lead.mid
        (D Dorian PCFG lead line, 100 BPM, 8 bars, 124 staccato 16ths)
Method: SP-079 -> sound.generators.acid_seq (AcidSequencer, AcidVoice, MODES)
Layer : ABSOLUTE layer — the AcidVoice replaces the SoundFont production layer
        for the WHOLE piece: the source melody's notes are re-synthesised through
        the BS-203's three operating modes (303 / 202 / BB), NOT played by the
        GM flute. The AcidSequencer randomizer is not needed here — the source
        melody is already a scale-locked D-Dorian line, so the production pass
        uses only the AcidVoice (the sound layer) across all notes.
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

from workflows.musicom_workflow import _midi_to_notes
from sound.render.fluidsynth import discover_soundfont
from sound.generators.acid_seq import AcidVoice, MODES, SCALES, STEP_DIVISIONS
from sound.effects.mastering import normalize_to_lufs, measure_lufs, Limiter

SRC = Path("/opt/data/repos/musicom/projects/Styles/Experimental/050-pcfg-daw-sync/MIDI/050-pcfg-daw-sync_Lead.mid")
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/SP079-acid-seq-pcfg-daw-sync")
AUD = OUT / "Audio"
STEMS = AUD / "stems"
MIDIDIR = OUT / "MIDI"
ANALYSIS = OUT / "Analysis"
SCRIPTS = OUT / "Scripts"

for d in (AUD, STEMS, MIDIDIR, ANALYSIS, SCRIPTS):
    d.mkdir(parents=True, exist_ok=True)

SR = 44100
BPM = 100.0
SEED = 20260929
TAIL = 1.0            # seconds of release/tail after last note
MODE_GAINS = {"303": 0.60, "202": 0.50, "BB": 0.40}

SF = discover_soundfont()
assert SF and Path(SF).exists(), f"SoundFont missing: {SF}"
FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"

shutil.copy2(str(SRC), str(MIDIDIR / SRC.name))


# --------------------------------------------------------------------------
# 0. WAV helpers (defined before first use)
# --------------------------------------------------------------------------
def _read_wav(p):
    with wave.open(str(p), "rb") as wf:
        nch = wf.getnchannels()
        sr = wf.getframerate()
        n = wf.getnframes()
        raw = np.frombuffer(wf.readframes(n), dtype=np.int16).astype(np.float64) / 32768.0
    if nch == 2:
        return raw.reshape(-1, 2), sr
    return np.column_stack([raw, raw]), sr


def _write_wav(p, audio):
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


# --------------------------------------------------------------------------
# 1. Parse source notes
# --------------------------------------------------------------------------
notes = _midi_to_notes(str(SRC))
assert notes, "no notes parsed"
max_end = max(n["end"] for n in notes)
total_dur = max_end + TAIL
print(f"Notes: {len(notes)}, pitch {min(n['pitch'] for n in notes)}-{max(n['pitch'] for n in notes)}, "
      f"dur {min(n['end']-n['start'] for n in notes):.3f}-{max(n['end']-n['start'] for n in notes):.3f}s, "
      f"max_end={max_end:.3f}s total={total_dur:.3f}s")

# --------------------------------------------------------------------------
# 2. Dry reference (SP-001 FluidSynth, reverb/chorus off)
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
# 3. AcidVoice re-synthesis (the absolute production layer)
# --------------------------------------------------------------------------
BAR = 60.0 / BPM * 4.0     # 2.4 s per bar at 100 BPM

def render_acid(note_list, mode, amp=0.85):
    """Re-synthesise the source melody through the acid voice (one mode)."""
    v = AcidVoice(sample_rate=SR, mode=mode)
    total = int(round(total_dur * SR))
    buf = np.zeros(total)
    prev_offset = None
    for n in note_list:
        dur = n["end"] - n["start"]
        step_sec = dur                      # full slot = note duration
        gate = dur * 0.85                   # tight acid staccato gate
        accent = (n["start"] % BAR) < 0.03  # accent the bar downbeat (acid-style)
        slide = False                        # source is staccato: no legato ties
        a = amp * (n["velocity"] / 127.0)
        seg = v.render_step(
            offset=n["pitch"], step_sec=step_sec, gate_sec=gate,
            accent=accent, previous_offset=prev_offset, slide=slide,
            root_note=0, amp=a,
        )
        i0 = int(round(n["start"] * SR))
        i1 = min(total, i0 + seg.size)
        if i1 > i0:
            buf[i0:i1] += seg[: i1 - i0]
        prev_offset = n["pitch"]
    return buf


print("Rendering acid stems (303 / 202 / BB)...")
t0 = time.time()
mode_bufs = {}
for mode in ("303", "202", "BB"):
    b = render_acid(notes, mode, amp=0.85)
    # per-stem peak norm 0.89
    pk = float(np.max(np.abs(b))) or 1.0
    b = b * (0.89 / pk)
    mode_bufs[mode] = b
    stem_wav = STEMS / f"track00_Acid{mode}.wav"
    write_buf = np.column_stack([b, b])  # stereo duplicate
    _write_wav(stem_wav, write_buf)
    print(f"  mode {mode}: rms={np.sqrt(np.mean(b**2)):.4f} -> {stem_wav.name} ({stem_wav.stat().st_size} B)")
print(f"  acid stems done in {time.time()-t0:.1f}s")

# --------------------------------------------------------------------------
# 4. Full mix = layered acid (303 + 202 + BB), the whole BS-203 instrument
# --------------------------------------------------------------------------
mix = np.zeros(mode_bufs["303"].shape)
for mode, g in MODE_GAINS.items():
    mix += mode_bufs[mode] * g
mix = mix / max(1e-9, float(np.max(np.abs(mix)))) * 0.89   # peak norm 0.89
mix_stereo = np.column_stack([mix, mix])

lufs_norm = normalize_to_lufs(mix_stereo, target_lufs=-14.0, sample_rate=SR)
limiter = Limiter(threshold_db=-1.0, sample_rate=SR)
final_master = limiter.process(lufs_norm)  # (N, 2)

final_wav = OUT / "SP079-acid-seq-pcfg-daw-sync.wav"
final_ogg = OUT / "SP079-acid-seq-pcfg-daw-sync.ogg"
_write_wav(final_wav, final_master)
print(f"Wrote final WAV: {final_wav} ({final_wav.stat().st_size} bytes)")

subprocess.run([
    "ffmpeg", "-y", "-loglevel", "error", "-i", str(final_wav),
    "-codec:a", "libopus", "-application", "voip", "-b:a", "48k", str(final_ogg),
], check=True)
print(f"Wrote final OGG: {final_ogg} ({final_ogg.stat().st_size} bytes)")

# --------------------------------------------------------------------------
# 6. Verification: silence / RMS / LUFS / pitch fidelity / harmonic energy / ACF
# --------------------------------------------------------------------------
dry_mix, _ = _read_wav(dry_full)
wet_mix, _ = _read_wav(final_wav)
# align lengths
nmin = min(dry_mix.shape[0], wet_mix.shape[0])
dry_mix = dry_mix[:nmin]
wet_mix = wet_mix[:nmin]

meas_lufs = measure_lufs(wet_mix, sample_rate=SR)
peak_val = float(np.max(np.abs(wet_mix)))
mono_wet = 0.5 * (wet_mix[:, 0] + wet_mix[:, 1])
mono_dry = 0.5 * (dry_mix[:, 0] + dry_mix[:, 1])
silence_pct = float(np.sum(np.abs(mono_wet) < 0.001) / len(mono_wet)) * 100.0

rms_map = []
for s in range(len(mono_wet) // SR):
    seg = mono_wet[s * SR:(s + 1) * SR]
    rms_map.append(round(float(np.sqrt(np.mean(seg ** 2))), 4))

print(f"Master Stats: LUFS={meas_lufs:.2f}, Peak={peak_val:.4f}, Silence={silence_pct:.2f}%")


def midi_from_freq(f):
    return 69.0 + 12.0 * math.log2(max(1.0, f) / 440.0)


win = int(0.5 * SR)
n_wins = len(mono_wet) // win
freqs = np.fft.rfftfreq(win, 1.0 / SR)
mask = (freqs >= 50.0) & (freqs <= 2000.0)

checked = hits = 0
he_list, dom_list, misses = [], [], []
for w in range(n_wins):
    seg_w = mono_wet[w * win:(w + 1) * win]
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
    tot = np.sum(spec_w ** 2) + 1e-12
    he = 0.0
    for h in range(1, 9):
        tf = dom_w * h
        he += np.sum(spec_w[(freqs >= tf - 15) & (freqs <= tf + 15)] ** 2)
    he_list.append(float(he / tot))
    ratios = [1.0, 2.0, 3.0, 4.0, 0.5, 1.0 / 3.0]
    hit = any(abs(dom_w - dom_d * r) / (dom_d * r) < 0.04 for r in ratios)
    if hit:
        hits += 1
    else:
        misses.append({"t": round(w * 0.5, 2), "dom_w": round(dom_w, 1), "dom_d": round(dom_d, 1)})

hit_rate = hits / max(checked, 1)
he_mean = float(np.mean(he_list)) if he_list else 0.0

# ACF unpitched check (SP-035 failure signature: 0 Hz / broadband noise)
ds = 5
md = mono_wet[::ds]
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
# 7. Analysis artifacts + provenance
# --------------------------------------------------------------------------
mode_stats = {}
for mode in ("303", "202", "BB"):
    b = mode_bufs[mode]
    sp = np.abs(np.fft.rfft(b * np.hanning(b.size)))
    fr = np.fft.rfftfreq(b.size, 1.0 / SR)
    centroid = float(np.sum(fr * sp) / (np.sum(sp) + 1e-12))
    mode_stats[mode] = {
        "spec": MODES[mode].name,
        "env_decay": MODES[mode].env_decay,
        "env_slope": MODES[mode].env_slope,
        "drive": MODES[mode].drive,
        "resonance": MODES[mode].resonance,
        "clip": MODES[mode].clip,
        "spectral_centroid_hz": round(centroid, 1),
        "rms": round(float(np.sqrt(np.mean(b ** 2))), 4),
    }

render_stats = {
    "method": "SP-079",
    "method_module": "sound.generators.acid_seq",
    "layer": "absolute",
    "seed": SEED,
    "modes": mode_stats,
    "mode_gains_full_mix": MODE_GAINS,
    "scales_available": sorted(SCALES),
    "step_divisions": STEP_DIVISIONS,
    "n_notes": len(notes),
    "pitch_range": [min(n['pitch'] for n in notes), max(n['pitch'] for n in notes)],
    "accent_bar_downbeats": True,
    "slides": "none (staccato source, no legato ties)",
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
    "duration_sec": round(len(mono_wet) / SR, 2),
}
(ANALYSIS / "render_stats.json").write_text(json.dumps(render_stats, indent=2))
(ANALYSIS / "pitch_verification.json").write_text(json.dumps({
    "method": "SP-079",
    "project": "050-pcfg-daw-sync",
    "status": pitch_verdict,
    "dry_wet_hit_rate": hit_rate,
    "harmonic_energy_mean": he_mean,
    "acf_unpitched": unpitched,
    "acf_windows": acf_n,
    "windows_analyzed": checked,
    "median_dom_hz": render_stats["median_dom_hz"],
    "misses": misses[:12],
}, indent=2))

# grid visualization
grid_lines = [
    "SP-079 Acid Seq (BS-203 MacroAcidizer) — absolute-layer acid re-synthesis",
    f"source: 050-pcfg-daw-sync_Lead.mid  (D Dorian, 100 BPM, {len(notes)} notes)",
    "",
    "mode   instrument       env_decay  slope  drive  res   clip  centroid",
]
for mode in ("303", "202", "BB"):
    ms = mode_stats[mode]
    grid_lines.append(
        f"  {mode:4s} {ms['spec']:16s} {ms['env_decay']:9.2f} {ms['env_slope']:5.1f} "
        f"{ms['drive']:5.1f} {ms['resonance']:4.2f} {ms['clip']:5.2f} {ms['spectral_centroid_hz']:8.1f} Hz"
    )
grid_lines.append("")
grid_lines.append("accent map (bar downbeats, 8 bars @ 2.4s):")
bar_marks = ""
for b in range(8):
    t = b * BAR
    hit = any(abs(n["start"] - t) < 0.03 for n in notes)
    bar_marks += "█" if hit else "░"
grid_lines.append(f"  {bar_marks}  (█ = accented downbeat note present, ░ = downbeat rest)")
grid_lines.append("")
grid_lines.append("mode stems (each = full melody through that mode, peak 0.89):")
for mode in ("303", "202", "BB"):
    grid_lines.append(f"  Audio/stems/track00_Acid{mode}.wav")
grid_lines.append(f"full mix = sum({', '.join(f'{m}*{g}' for m, g in MODE_GAINS.items())}) -> LUFS -14 -> Limiter -1")
(ANALYSIS / "grid_visualization.txt").write_text("\n".join(grid_lines) + "\n")

provenance = {
    "job": "random-style production (SP) layer-aligned",
    "date": "2026-09-29",
    "seed": SEED,
    "method": "SP-079",
    "method_module": "sound.generators.acid_seq",
    "method_desc": "Scale-Locked Acid Sequencer + 303/202 Voice (BS-203 MacroAcidizer-style)",
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
