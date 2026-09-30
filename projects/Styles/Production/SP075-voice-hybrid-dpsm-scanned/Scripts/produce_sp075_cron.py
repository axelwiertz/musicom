# -*- coding: utf-8 -*-
"""SP-075 Voice-Like Instrument Hybrid Render -- 049-dpsm-scanned.

Source: Styles/Experimental/049-dpsm-scanned/MIDI/049-dpsm-scanned.mid
        (Deconstructive Phase-Shift Minimalism, 110 BPM, C Dorian, 8 bars,
         3 voices: Piano1 static loop / Piano2 phase-shifting loop / Bass roots)
Method: SP-075 -> sound.render.hybrid (render_hybrid)
Layer : ABSOLUTE layer -- the whole piece is re-realized through the SP-075
        production method. Voice-like instruments have NO GM soundfont
        equivalent, so the hybrid maps the two melodic "lead" voices onto
        voice-like synthesized instruments (singing_saw + talkbox) and keeps
        the harmonic foundation (Bass) on the FluidSynth soundfont backing.
        voice_instruments = ["singing_saw", "talkbox", None] aligned to the
        note-bearing tracks (Piano1, Piano2, Bass); tempo track 0 is skipped
        by parse_tracks().

Pitch verification is against the EXPECTED MIDI note frequencies (not the dry
piano render) -- SP-075 REPLACES the timbre, so a dry-vs-wet spectral-dominant
match is meaningless. Instead each 0.5s window's FFT dominant peak (50-1000 Hz)
is compared to the notes the source MIDI actually sounds in that window.
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

from sound.render.hybrid import (
    render_hybrid, parse_tracks, _render_voice_track,
    _render_backing_fluidsynth, VOICE_VOWEL_CYCLE,
)
from sound.render.fluidsynth import discover_soundfont
from sound.synthesis.voice_like import INSTRUMENTS
from sound.effects.mastering import normalize_to_lufs, measure_lufs, Limiter
from utilities.env import fluidsynth_bin

SRC = Path("/opt/data/repos/musicom/projects/Styles/Experimental/049-dpsm-scanned/MIDI/049-dpsm-scanned.mid")
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/SP075-voice-hybrid-dpsm-scanned")
AUD = OUT / "Audio"
STEMS_DRY = AUD / "stems_dry"
STEMS_WET = AUD / "stems_wet"
MIDIDIR = OUT / "MIDI"
ANALYSIS = OUT / "Analysis"
SCRIPTS = OUT / "Scripts"

for d in (AUD, STEMS_DRY, STEMS_WET, MIDIDIR, ANALYSIS, SCRIPTS):
    d.mkdir(parents=True, exist_ok=True)

SR = 44100
BPM = 110.0
SEED = 20260930
VOICE_INSTRUMENTS = ["singing_saw", "talkbox", None]
VOWELS = list("aoeauo")  # 6-vowel "singing" cycle
VOICE_GAIN = 1.0
BACKING_GAIN = 1.0

SF = discover_soundfont()
assert SF and Path(SF).exists(), f"SoundFont missing: {SF}"
FLUID = fluidsynth_bin()

shutil.copy2(str(SRC), str(MIDIDIR / SRC.name))

# ---------------------------------------------------------------------------
# 0. parse tracks (note-bearing only, track 0 skipped)
# ---------------------------------------------------------------------------
tracks, tpb, total_ticks = parse_tracks(str(SRC))
track_names = []
for t in tracks:
    label = "Drums" if t.channel == 9 else (
        "Piano1" if t.index == 0 else "Piano2" if t.index == 1 else
        f"prog{t.program}_ch{t.channel}")
    track_names.append(label)
print(f"note-bearing tracks={len(tracks)} tpb={tpb} total_ticks={total_ticks}")
for t in tracks:
    print(f"  idx={t.index} midi_track={t.midi_track} ch={t.channel} "
          f"prog={t.program} notes={len(t.notes)}")

# ---------------------------------------------------------------------------
# 1. dry full mix (SP-001 reference, reverb/chorus off) -- comparison only
# ---------------------------------------------------------------------------
dry_full = OUT / "dry_full_mix_sp001_reference.wav"
print("Rendering dry full mix (SP-001 reference)...")
res = subprocess.run([
    FLUID, "-ni", "-g", "1.2", "-F", str(dry_full), "-r", str(SR),
    "-o", "synth.reverb.active=no", "-o", "synth.chorus.active=no",
    SF, str(SRC),
], capture_output=True, text=True)
if res.returncode != 0 or not dry_full.exists() or dry_full.stat().st_size < 1000:
    raise RuntimeError(f"FluidSynth dry render failed: {res.stderr[-500:]}")
print(f"Dry full mix: {dry_full.stat().st_size} bytes")

# ---------------------------------------------------------------------------
# 2. dry stems (per-track FluidSynth, reference)
# ---------------------------------------------------------------------------
mid = mido.MidiFile(str(SRC))
dry_stem_paths = {}
for ti in range(len(tracks)):
    info = tracks[ti]
    label = track_names[ti]
    stem_name = f"track{ti:02d}_{label}"
    sm = mido.MidiFile(ticks_per_beat=mid.ticks_per_beat)
    tt = mido.MidiTrack()
    for m in mid.tracks[0]:
        if m.type == "set_tempo":
            tt.append(m)
            break
    sm.tracks.append(tt)
    vt = mido.MidiTrack()
    for m in mid.tracks[info.midi_track]:
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

# ---------------------------------------------------------------------------
# 3. WAV helpers (local: (N,2) float64 stereo or (N,) mono)
# ---------------------------------------------------------------------------
def read_wav(p):
    with wave.open(str(p), "rb") as wf:
        nch = wf.getnchannels()
        sr = wf.getframerate()
        n = wf.getnframes()
        raw = np.frombuffer(wf.readframes(n), dtype=np.int16).astype(np.float64) / 32768.0
    if nch == 2:
        return raw.reshape(-1, 2), sr
    return raw, sr


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


# ---------------------------------------------------------------------------
# 4. SP-075 hybrid render (canonical full mix)
# ---------------------------------------------------------------------------
hybrid_raw = OUT / "hybrid_raw_mono.wav"
print("Rendering SP-075 hybrid (voice-like lead + FluidSynth bass backing)...")
t0 = time.time()
info = render_hybrid(
    str(SRC),
    VOICE_INSTRUMENTS,
    str(hybrid_raw),
    sr=SR,
    bpm=BPM,
    vowels=VOWELS,
    voice_gain=VOICE_GAIN,
    backing_gain=BACKING_GAIN,
    seed=SEED,
)
print(f"  hybrid render done in {time.time()-t0:.1f}s: {info['seconds']:.2f}s, "
      f"tracks={info['tracks']}, backing_rendered={info['backing_rendered']}")

# ---------------------------------------------------------------------------
# 5. wet stems: each voice-like track synthesized + bass backing rendered
# ---------------------------------------------------------------------------
print("Rendering wet stems (per-track)...")
wet_stem_paths = {}
for i, key in enumerate(VOICE_INSTRUMENTS):
    if key is None:
        continue
    seg = _render_voice_track(tracks[i], key, tpb, BPM, SR,
                              vowels=VOWELS, seed=SEED + i * 7919)
    name = f"track{i:02d}_{track_names[i]}_{key}"
    write_wav(STEMS_WET / f"{name}.wav", seg)
    wet_stem_paths[name] = STEMS_WET / f"{name}.wav"
    print(f"  wet voice stem {name}: {len(seg)/SR:.2f}s")

# bass backing stem (mute voice-like tracks, keep bass)
mute = [tracks[i].midi_track for i in range(len(VOICE_INSTRUMENTS))
        if VOICE_INSTRUMENTS[i] is not None]
backing_wav = _render_backing_fluidsynth(str(SRC), mute,
                                         str(STEMS_WET / "_backing_bass.wav"),
                                         tpb, SR)
if backing_wav:
    b, _ = read_wav(backing_wav)
    if b.ndim > 1:
        b = b.mean(axis=1)
    name = f"track02_{track_names[2]}_fluidsynth"
    write_wav(STEMS_WET / f"{name}.wav", b)
    wet_stem_paths[name] = STEMS_WET / f"{name}.wav"
    Path(backing_wav).unlink()
    print(f"  wet backing stem {name}: {len(b)/SR:.2f}s")

# ---------------------------------------------------------------------------
# 6. master: LUFS -14 + Limiter(-1 dB) LAST
# ---------------------------------------------------------------------------
mix, _ = read_wav(hybrid_raw)
if mix.ndim > 1:
    mix = mix.mean(axis=1)
print(f"Hybrid mix: {mix.shape}, sr={SR}, duration={len(mix)/SR:.2f}s")

lufs_norm = normalize_to_lufs(mix, target_lufs=-14.0, sample_rate=SR)
limiter = Limiter(threshold_db=-1.0, sample_rate=SR)
final_mono = limiter.process(lufs_norm)
final_stereo = np.column_stack([final_mono, final_mono])

final_wav = OUT / "SP075-voice-hybrid-dpsm-scanned.wav"
final_ogg = OUT / "SP075-voice-hybrid-dpsm-scanned.ogg"
write_wav(final_wav, final_stereo)
print(f"Wrote final WAV: {final_wav} ({final_wav.stat().st_size} bytes)")

subprocess.run([
    "ffmpeg", "-y", "-loglevel", "error", "-i", str(final_wav),
    "-codec:a", "libopus", "-application", "voip", "-b:a", "48k", str(final_ogg),
], check=True)
print(f"Wrote final OGG: {final_ogg} ({final_ogg.stat().st_size} bytes)")

# ---------------------------------------------------------------------------
# 7. verification
# ---------------------------------------------------------------------------
meas_lufs = measure_lufs(final_mono, sample_rate=SR)
peak_val = float(np.max(np.abs(final_mono)))
mono_mix = final_mono

silence_pct = float(np.sum(np.abs(mono_mix) < 0.001) / len(mono_mix)) * 100.0
rms_map = []
for s in range(len(mono_mix) // SR):
    seg = mono_mix[s * SR:(s + 1) * SR]
    rms_map.append(round(float(np.sqrt(np.mean(seg ** 2))), 4))

print(f"Master Stats: LUFS={meas_lufs:.2f}, Peak={peak_val:.4f}, "
      f"Silence={silence_pct:.2f}%")

# expected note timeline from the source MIDI
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
n_wins = len(mono_mix) // win
freqs = np.fft.rfftfreq(win, 1.0 / SR)
mask_fund = (freqs >= 50.0) & (freqs <= 1000.0)

checked = hits = 0
he_list, dom_list, misses = [], [], []
for w in range(n_wins):
    ws = w * 0.5
    we = ws + 0.5
    seg_w = mono_mix[w * win:(w + 1) * win]
    if np.sqrt(np.mean(seg_w ** 2)) < 0.005:
        continue
    # notes overlapping the window (release tails included)
    exp = [f for (s, e, f) in all_notes if e > ws and s < we]
    if not exp:
        continue
    spec_w = np.abs(np.fft.rfft(seg_w * np.hanning(win)))
    fw = freqs[mask_fund]
    sw = spec_w[mask_fund]
    dom = float(fw[int(np.argmax(sw))])
    checked += 1
    dom_list.append(dom)
    # harmonic energy: fraction of total spectral energy within +/-15 Hz of
    # any expected note's harmonics (1..8), each bin counted once
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
    # match: dominant fundamental within 4% of an expected note (octave/harmonic)
    ratios = [1.0, 2.0, 3.0, 4.0, 0.5, 1.0 / 3.0]
    hit = False
    for ef in exp:
        for r in ratios:
            if abs(dom - ef * r) / (ef * r) < 0.04:
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
print(f"Pitch verification: windows={checked}, midi-note hit_rate={hit_rate:.4f}, "
      f"harmonic_energy={he_mean:.4f}, ACF unpitched={unpitched}/{acf_n} -> {pitch_verdict}")

# ---------------------------------------------------------------------------
# 8. analysis artifacts + provenance + report
# ---------------------------------------------------------------------------
render_stats = {
    "method": "SP-075",
    "method_module": "sound.render.hybrid",
    "method_desc": "Voice-Like Instrument Hybrid Render (synthesized voice tracks + SoundFont backing)",
    "layer": "absolute",
    "voice_instruments": VOICE_INSTRUMENTS,
    "vowels": VOWELS,
    "voice_gain": VOICE_GAIN,
    "backing_gain": BACKING_GAIN,
    "seed": SEED,
    "bpm": BPM,
    "sr": SR,
    "tracks": [{"index": t.index, "midi_track": t.midi_track, "channel": t.channel,
                "program": t.program, "notes": len(t.notes)} for t in tracks],
    "available_instruments": sorted(INSTRUMENTS),
    "lufs": round(meas_lufs, 2),
    "peak": peak_val,
    "silence_pct": round(silence_pct, 2),
    "rms_per_second": rms_map,
    "windows_checked": checked,
    "midi_note_hit_rate": round(hit_rate, 4),
    "harmonic_energy_mean": round(he_mean, 4),
    "acf_windows": acf_n,
    "acf_unpitched": unpitched,
    "pitch_verdict": pitch_verdict,
    "median_dom_hz": round(float(np.median(dom_list)), 1) if dom_list else 0.0,
    "duration_sec": round(len(mono_mix) / SR, 2),
}
(ANALYSIS / "render_stats.json").write_text(json.dumps(render_stats, indent=2))
(ANALYSIS / "pitch_verification.json").write_text(json.dumps({
    "method": "SP-075",
    "project": "049-dpsm-scanned",
    "status": pitch_verdict,
    "midi_note_hit_rate": hit_rate,
    "harmonic_energy_mean": he_mean,
    "acf_unpitched": unpitched,
    "acf_windows": acf_n,
    "windows_analyzed": checked,
    "median_dom_hz": render_stats["median_dom_hz"],
    "misses": misses[:12],
}, indent=2))

grid_lines = [
    "SP-075 Voice-Like Instrument Hybrid -- absolute layer (049-dpsm-scanned)",
    f"seed={SEED} bpm={BPM} vowels={''.join(VOWELS)}",
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

provenance = {
    "job": "random-style production (SP) layer-aligned",
    "date": "2026-09-30",
    "seed": SEED,
    "method": "SP-075",
    "method_module": "sound.render.hybrid",
    "method_desc": "Voice-Like Instrument Hybrid Render (synthesized voice tracks + SoundFont backing)",
    "layer": "absolute",
    "source_midi": str(SRC),
    "output_wav": str(final_wav),
    "output_ogg": str(final_ogg),
    "voice_instruments": VOICE_INSTRUMENTS,
    "lufs": round(meas_lufs, 2),
    "peak": peak_val,
    "silence_pct": round(silence_pct, 2),
    "pitch_verdict": pitch_verdict,
    "midi_note_hit_rate": round(hit_rate, 4),
    "he_mean": round(he_mean, 4),
}
(OUT / "provenance.json").write_text(json.dumps(provenance, indent=2))

report = f"""# SP-075 Voice-Like Instrument Hybrid Render — 049-dpsm-scanned

## Job
- **Type**: random-style production (SP) layer-aligned (nightly cron)
- **Date**: 2026-09-30
- **Seed**: {SEED}
- **Registry source**: `SP_METHODS` in `workflows/musicom_workflow.py` (single source of truth)
- **Registry size**: 35 implemented methods
- **Recent (7-day) excluded**: SP-011, SP-024, SP-032, SP-069, SP-070, SP-079, SP-081

## Selection
- **Method**: SP-075 — `sound.render.hybrid`
- **Description**: Voice-Like Instrument Hybrid Render (synthesized voice tracks + SoundFont backing)
- **Source composition**: `Styles/Experimental/049-dpsm-scanned/MIDI/049-dpsm-scanned.mid`
  - Deconstructive Phase-Shift Minimalism (Method 026) + Scanned Synthesis (SP-018)
  - 110 BPM, C Dorian, 8 bars, 3 voices, 17.45 s

## Method application (absolute layer)
SP-075 is an absolute-layer production method: the whole piece is re-realized
through it. Voice-like instruments have **no GM soundfont equivalent**, so the
hybrid maps the melodic lead voices onto synthesized voice-like instruments and
keeps the harmonic foundation on the FluidSynth soundfont.

Note-bearing tracks (tempo track 0 skipped by `parse_tracks()`):
| track | voice | program/ch | engine | instrument |
|-------|-------|-----------|--------|-----------|
| 0 | Piano1 (static loop)  | 0/0 | voice_like | `singing_saw` |
| 1 | Piano2 (phase-shift)  | 0/1 | voice_like | `talkbox` |
| 2 | Bass (roots)         | 32/2 | fluidsynth | soundfont |

`voice_instruments = ["singing_saw", "talkbox", None]` — the two DPSM pianos
(an identical 16th-note loop, one static, one phase-shifting) become a
"singing saw" + "talkbox" duet whose phase drift is now audible as two
different voices sliding out of phase; the bass stays a real bass.

## Parameters
- bpm = {BPM} (read from MIDI tempo 545455 us/qn), sr = {SR}
- vowels = {''.join(VOWELS)} (6-vowel "singing" cycle, per-note articulation)
- voice_gain = {VOICE_GAIN}, backing_gain = {BACKING_GAIN}
- seed = {SEED} (per-track voice seed = seed + idx*7919)
- available voice-like instruments: {sorted(INSTRUMENTS)}

## Verification
Pitch verification is against the **expected MIDI note frequencies** (not the
dry piano render): SP-075 replaces timbre, so a dry-vs-wet spectral-dominant
match is meaningless. Each 0.5s window's FFT dominant peak (50-1000 Hz) is
compared to the notes the source MIDI sounds in that window.
- **Pitch verdict**: {pitch_verdict}
- MIDI-note hit rate: {hit_rate:.4f} (>= 0.60 required)
- harmonic energy (at expected notes' harmonics, 1..8): {he_mean:.4f} (>= 0.25 required)
- ACF unpitched windows: {unpitched}/{acf_n} (< 0.50 required)
- LUFS: {meas_lufs:.2f}, peak: {peak_val:.4f}, silence: {silence_pct:.2f}%
- RMS per second: {rms_map}

## Files
- final WAV: `{final_wav}` ({final_wav.stat().st_size} bytes)
- final OGG: `{final_ogg}` ({final_ogg.stat().st_size} bytes)
- dry reference: `{dry_full}`
- dry stems: `Audio/stems_dry/` ({len(dry_stem_paths)} files)
- wet stems: `Audio/stems_wet/` ({len(wet_stem_paths)} files)
- provenance: `provenance.json`, render stats: `Analysis/render_stats.json`
- pitch verification: `Analysis/pitch_verification.json`, grid: `Analysis/grid_visualization.txt`

## Fixes applied
1. **`sound/synthesis/voice_like.py` release-envelope bug**: `render_note()` set
   `env[-r_n:] *= linspace(1,0,r_n)` with `r_n` = release_samples unclamped.
   For short notes (DPSM 16th notes are ~0.114 s = 5011 samples) shorter than
   the release (singing_saw release = 0.30 s = 13230 samples), this produced a
   broadcast error (`(5011,)` vs `(13230,)`) and crashed every note. Fixed by
   clamping `r_n = min(r_n, n)` (and `a_n = min(a_n, n)` for the attack) so the
   envelope never exceeds the note length. Correct and minimal.
"""
(OUT / "REPORT.md").write_text(report)

# update the shared selection marker (matches prior jobs)
(Path("/opt/data/repos/musicom/projects/Styles/Production/.selection_cron.json")).write_text(
    json.dumps(provenance, indent=2))

print("Done. pitch_verdict=", pitch_verdict)
