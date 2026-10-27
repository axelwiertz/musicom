# -*- coding: utf-8 -*-
"""SP-109 Tape-Stop / Turntable-Stop production pass (absolute layer) — WITH REWORK.

Source : Styles/Country/038-steel-guitar-demo/MIDI/country_ensemble_16bar.mid
         (G major country ensemble, 120 BPM, 480 TPB, 16 bars, 2 voices:
          acoustic bass prog 32 + steel acoustic guitar prog 25).
         PRE-FLIGHT FAIL: 448 off-grid onsets (rolled-chord strums at ~10-30
         tick offsets), 105 out-of-chord tones (passing/colour notes in the
         strum rolls), zero-drift FAIL (track ends 30480 vs 34330).

Method : SP-109 -> sound.effects.tape_stop (TapeStop, Cableguys TimeStop-style
         classic tape-stop). ABSOLUTE layer: applied to the whole rendered mix
         as a tape-stop OUTRO (final 2.5 s wind-down; pitch+time drop together,
         the signature vinyl-stop sound).

Pipeline: source MIDI -> 3-rule audit (FAIL -> rework) ->
          UnitMatrixComposer clean rebuild (16-bar G major, grid-locked,
          chord-tone exact, zero-drift) -> re-audit (PASS) ->
          FluidSynth dry render -> SP-109 classic tape-stop outro ->
          master() (country -14 LUFS, -1 dBTP) -> WAV + Opus OGG ->
          pitch/harmonic-energy/silence verification -> REPORT.md.
"""
import json
import os
import shutil
import subprocess
from pathlib import Path

import numpy as np
import mido

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from sound.render.fluidsynth import discover_soundfont
from sound.effects.mastering import master, target_for_style, measure_lufs
from sound.effects.tape_stop import TapeStop
from sound.utils.io import read_wav, write_wav

ROOT = Path("/opt/data/repos/musicom/projects/Styles")
SRC = ROOT / "Country/038-steel-guitar-demo/MIDI/country_ensemble_16bar.mid"
OUT = ROOT / "Production/SP109-tape-stop-038-steel-guitar-demo"
AUD = OUT / "Audio"
STEMS = AUD / "stems"
MIDIDIR = OUT / "MIDI"
ANALYSIS = OUT / "Analysis"
SCRIPTS = OUT / "Scripts"

for d in (AUD, STEMS, MIDIDIR, ANALYSIS, SCRIPTS):
    d.mkdir(parents=True, exist_ok=True)

SR = 44100
BPM = 120.0
TPB = 480
BAR = TPB * 4               # 1920
N_BARS = 16
TOTAL_TICKS = BAR * N_BARS  # 30720
GRID = 120                  # 16th note
SEED = 20261027
STYLE = "country"
STOP_TIME = 2.5             # tape-stop outro duration (seconds)

# G major pitch classes: G A B C D E F#
SCALE_PCS = {7, 9, 11, 0, 2, 4, 6}

# 16-bar country progression I-I-I-I IV-IV I-I V-V IV-IV I-I-I-I (G major)
PROG_ROOT_PC = [7, 7, 7, 7, 0, 0, 7, 7, 2, 2, 0, 0, 7, 7, 7, 7]
TRIADS = {
    7: {7, 11, 2},   # G major (I)  : G B D
    0: {0, 4, 7},    # C major (IV) : C E G
    2: {2, 6, 9},    # D major (V)  : D F# A
}

# voicings (root-position, comfortable steel-guitar register)
GUITAR_STRUM = {   # chord triad [root, 3rd, 5th]
    7: [55, 59, 62],   # G3 B3 D4
    0: [60, 64, 67],   # C4 E4 G4
    2: [62, 66, 69],   # D4 F#4 A4
}
GUITAR_CHICK = {   # the 5th on the "and" (8th off-beat)
    7: 62,   # D4
    0: 67,   # G4
    2: 69,   # A4
}
BASS_NOTES = {     # [root, 5th]
    7: (43, 50),   # G2 D3
    0: (48, 55),   # C3 G3
    2: (50, 57),   # D3 A3
}

FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"


# ===========================================================================
# 0. Pre-flight 3-rule audit (generic, on any MIDI)
# ===========================================================================
def audit(path):
    mf = mido.MidiFile(str(path))
    grid_off = off8 = out_scale = out_chord = 0
    track_ends = []
    total_notes = 0
    for tr in mf.tracks:
        chans = {m.channel for m in tr if m.type in ("note_on", "note_off")}
        is_drum = 9 in chans
        t = 0
        n_notes = 0
        for m in tr:
            t += m.time
            if m.type == "note_on" and m.velocity > 0:
                n_notes += 1
                total_notes += 1
                if is_drum:
                    continue
                if (t % GRID) != 0:
                    grid_off += 1
                if (t % 240) != 0:
                    off8 += 1
                pc = m.note % 12
                if pc not in SCALE_PCS:
                    out_scale += 1
                bar = min(t // BAR, N_BARS - 1)
                if pc not in TRIADS[PROG_ROOT_PC[bar]]:
                    out_chord += 1
        if n_notes:
            track_ends.append(t)
    zero_drift = len(set(track_ends)) == 1
    return {"grid_off": grid_off, "off8": off8, "out_scale": out_scale,
            "out_chord": out_chord, "zero_drift": zero_drift,
            "track_ends": sorted(set(track_ends)), "total_notes": total_notes}


shutil.copy2(str(SRC), str(MIDIDIR / "source_original.mid"))
shutil.copy2(str(SRC), str(MIDIDIR / "reworked-phase1.mid"))  # raw phase-1 character
before = audit(SRC)
print("PREFLIGHT source (BEFORE rework):", before)

# ===========================================================================
# 1. REWORK — clean 16-bar G major country ensemble (UnitMatrixComposer)
# ===========================================================================
composer = UnitMatrixComposer(bpm=int(BPM), ticks_per_beat=TPB, beats_per_bar=4)
composer.create_matrix(num_voices=2, num_sections=1)
composer.add_voice("Bass", program=32, channel=0)          # Acoustic Bass
composer.add_voice("SteelGuitar", program=25, channel=1)   # Acoustic Guitar (steel)
composer.add_section("A", bars=N_BARS)

bass_events = []
guitar_events = []
for bar in range(N_BARS):
    root_pc = PROG_ROOT_PC[bar]
    base = bar * BAR
    root_n, fifth_n = BASS_NOTES[root_pc]
    # bass: root-5th-root-5th quarter notes (faithful to original)
    for i in range(4):
        pitch = root_n if i % 2 == 0 else fifth_n
        st = base + i * 480
        bass_events.append(MusicEvent(pitch=pitch, volume=90, start_tick=st, end_tick=st + 440))
    # steel guitar: full strum on downbeats + 5th "chick" on the 8th off-beats
    strum = GUITAR_STRUM[root_pc]
    chick = GUITAR_CHICK[root_pc]
    for i in range(4):
        st = base + i * 480
        for p in strum:
            guitar_events.append(MusicEvent(pitch=p, volume=70, start_tick=st, end_tick=st + 420))
        ck = base + i * 480 + 240
        guitar_events.append(MusicEvent(pitch=chick, volume=60, start_tick=ck, end_tick=ck + 200))

# terminal landmark (pitch 0) anchors each voice's unit to TOTAL_TICKS
bass_events.append(MusicEvent(pitch=0, volume=0, start_tick=TOTAL_TICKS - 10, end_tick=TOTAL_TICKS))
guitar_events.append(MusicEvent(pitch=0, volume=0, start_tick=TOTAL_TICKS - 10, end_tick=TOTAL_TICKS))

composer.fill_voice_section("Bass", "A", MusicUnit(events=bass_events))
composer.fill_voice_section("SteelGuitar", "A", MusicUnit(events=guitar_events))

ok, msg = composer.validate()
print("rework validate():", ok, msg)
assert ok, "rework zero-drift FAIL: %s" % msg

reworked_midi = MIDIDIR / "reworked.mid"
composer.to_midi(str(reworked_midi))
print("wrote reworked.mid:", reworked_midi.stat().st_size, "bytes")

after = audit(reworked_midi)
print("PREFLIGHT reworked (AFTER rework):", after)
assert after["grid_off"] == 0, "rework grid sync FAIL: %r" % after
assert after["out_scale"] == 0, "rework out-of-scale FAIL: %r" % after
assert after["out_chord"] == 0, "rework out-of-chord FAIL: %r" % after
assert after["zero_drift"], "rework zero-drift FAIL: %r" % after
print("PREFLIGHT PASS: reworked composition clean on all three rules.")

# ===========================================================================
# 2. FluidSynth dry render (SP-001 carrier)
# ===========================================================================
SF = discover_soundfont()
assert SF and os.path.exists(SF), "SoundFont missing: %r" % SF
print("SoundFont:", SF)


def render(midi_path, out_wav):
    r = subprocess.run([FLUID, "-ni", "-R", "0", "-C", "0", "-g", "1.2",
                        "-F", str(out_wav), SF, str(midi_path)],
                       capture_output=True, text=True, timeout=900)
    if r.returncode != 0 or not out_wav.exists() or out_wav.stat().st_size < 1000:
        raise RuntimeError("FluidSynth render failed: %s" % r.stderr[-500:])
    return out_wav


dry_wav = OUT / "dry_full_mix_reworked_reference.wav"
render(reworked_midi, dry_wav)
print("dry reference (reworked):", dry_wav.stat().st_size, "bytes")

# ===========================================================================
# 3. SP-109 classic tape-stop OUTRO (absolute layer, whole mix)
# ===========================================================================
dry_audio, sr = read_wav(str(dry_wav))
assert sr == SR, "unexpected sample rate %d" % sr
if dry_audio.ndim == 1:
    dry_audio = np.column_stack([dry_audio, dry_audio])
dry_tm = np.asarray(dry_audio, dtype=np.float64)          # [n, 2]

tail_len = int(STOP_TIME * SR)
assert tail_len < dry_tm.shape[0], "piece shorter than tape-stop window"
body = dry_tm[:-tail_len]
tail = dry_tm[-tail_len:]

ts = TapeStop(sample_rate=SR, gain_comp=True)
stopped_tail = ts.process(tail, mode="classic", stop_time_sec=STOP_TIME)
proc = np.concatenate([body, stopped_tail], axis=0)
print("SP-109 applied: body=%d + stopped_tail=%d -> %d samples"
      % (body.shape[0], stopped_tail.shape[0], proc.shape[0]))

raw_wav = OUT / "SP109_tape_stop_raw.wav"
write_wav(str(raw_wav), proc.astype(np.float32), SR, normalize=False)
print("SP-109 raw (tape-stop outro):", raw_wav.stat().st_size, "bytes")

# ===========================================================================
# 4. Master (country target, -1 dBTP ceiling)
# ===========================================================================
TARGET_LUFS = target_for_style(STYLE)
CEILING_DB = -1.0
print("mastering (target %.1f LUFS, ceiling %.1f dBTP)..." % (TARGET_LUFS, CEILING_DB))
mastered_tm, rep = master(proc, target_lufs=TARGET_LUFS, ceiling_db=CEILING_DB,
                          sample_rate=SR)
print("master report: LUFS %.2f, true peak %.2f dBTP"
      % (float(rep.get("integrated_lufs", 0)), float(rep.get("true_peak_db", 0))))

final_wav = OUT / "SP109-tape-stop-038-steel-guitar-demo.wav"
final_ogg = OUT / "SP109-tape-stop-038-steel-guitar-demo.ogg"
write_wav(str(final_wav), mastered_tm.astype(np.float32), SR, normalize=False)
r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(final_wav),
                    "-codec:a", "libopus", "-application", "voip", "-b:a", "48k",
                    str(final_ogg)], capture_output=True, text=True, timeout=180)
assert r.returncode == 0 and final_ogg.stat().st_size > 10000, "ogg encode failed"
print("final WAV:", final_wav.stat().st_size, "final OGG:", final_ogg.stat().st_size)

# ===========================================================================
# 5. Stems (dry, pre-effect, per-instrument)
# ===========================================================================
try:
    from sound.render.pipeline import RenderPipeline
    pipeline = RenderPipeline(soundfont_path=SF, fluidsynth_bin=FLUID, sample_rate=SR)
    stems = pipeline.render_stems(str(reworked_midi), str(STEMS), format="wav")
    print("rendered %d stems" % len(stems))
except Exception as e:
    stems = {}
    print("stem render skipped:", repr(e)[:200])

# ===========================================================================
# 6. Verification
# ===========================================================================
meas_lufs = float(measure_lufs(mastered_tm, sample_rate=SR))
peak_val = float(np.max(np.abs(mastered_tm)))
mono_final = 0.5 * (mastered_tm[:, 0] + mastered_tm[:, 1])
silence_pct = float(np.sum(np.abs(mono_final) < 0.001) / len(mono_final)) * 100.0
rms = float(np.sqrt(np.mean(mono_final ** 2)))
rms_map = [round(float(np.sqrt(np.mean(mono_final[i:i + SR] ** 2))), 4)
           for i in range(0, len(mono_final), SR)]
print("LUFS=%.2f peak=%.4f silence=%.2f%% rms=%.4f"
      % (meas_lufs, peak_val, silence_pct, rms))


def pitch_verify(audio_tm, pcs):
    mono_ = 0.5 * (audio_tm[:, 0] + audio_tm[:, 1])
    wl = int(0.5 * SR)
    nw = len(mono_) // wl
    hits = valid = 0
    he_list = []
    for w in range(nw):
        seg = mono_[w * wl:(w + 1) * wl]
        if np.max(np.abs(seg)) < 0.01:
            continue
        valid += 1
        win = np.hanning(len(seg))
        spec = np.abs(np.fft.rfft(seg * win))
        freqs = np.fft.rfftfreq(len(seg), 1.0 / SR)
        mask = (freqs >= 50.0) & (freqs <= 1000.0)
        sub = spec[mask]
        subf = freqs[mask]
        dom = subf[np.argmax(sub)]
        midi_val = 69.0 + 12.0 * np.log2(max(1.0, dom) / 440.0)
        pc = round(midi_val) % 12
        if pc in pcs:
            hits += 1
        tot = np.sum(spec ** 2) + 1e-12
        he = 0.0
        for h in range(1, 9):
            tf = dom * h
            hband = (freqs >= tf - 15.0) & (freqs <= tf + 15.0)
            he += np.sum(spec[hband] ** 2)
        he_list.append(float(he / tot))
    hit_rate = hits / max(1, valid)
    he_mean = float(np.mean(he_list)) if he_list else 0.0
    return hit_rate, he_mean, valid


hit_final, he_final, valid_final = pitch_verify(mastered_tm, SCALE_PCS)
hit_dry, he_dry, valid_dry = pitch_verify(dry_tm, SCALE_PCS)
he_retention = (he_final / he_dry) if he_dry > 0 else 0.0
# the tape-stop outro deliberately detunes the final ~2.5 s -> a few windows
# legitimately drop out of key; hit threshold still comfortably met.
pitch_verdict = "PASS" if (hit_final >= 0.60 and he_final >= 0.30) else "FAIL"
print("Pitch verify: final hit=%.4f HE=%.4f | dry hit=%.4f HE=%.4f | retention=%.3f -> %s"
      % (hit_final, he_final, hit_dry, he_dry, he_retention, pitch_verdict))

# ===========================================================================
# 7. Artifacts: render_stats + provenance
# ===========================================================================
(ANALYSIS / "render_stats.json").write_text(json.dumps({
    "lufs": meas_lufs, "peak": peak_val, "silence_pct": silence_pct,
    "rms": rms, "rms_per_sec": rms_map,
    "hit_rate_final": hit_final, "he_final": he_final, "valid_windows_final": valid_final,
    "hit_rate_dry": hit_dry, "he_dry": he_dry, "valid_windows_dry": valid_dry,
    "he_retention": he_retention, "pitch_verdict": pitch_verdict,
    "tape_stop_mode": "classic", "tape_stop_seconds": STOP_TIME,
    "n_stems": len(stems) if isinstance(stems, dict) else 0,
    "target_lufs": TARGET_LUFS,
}, indent=2))

provenance = {
    "job": "random-style production (SP) layer-aligned",
    "date": "2026-10-27",
    "seed": SEED,
    "method": "SP-109",
    "method_module": "sound.effects.tape_stop",
    "method_desc": "Tape-Stop / Turntable-Stop Processor — Classic mode "
                   "(rate-ramp resample: pitch+time drop together) "
                   "(Cableguys TimeStop-style)",
    "layer": "ABSOLUTE",
    "params": {
        "sample_rate": SR, "bpm": BPM, "ppqn": TPB,
        "meter": "4/4", "bar_ticks": BAR, "n_bars": N_BARS,
        "tape_stop_mode": "classic", "tape_stop_seconds": STOP_TIME,
        "tape_stop_gain_comp": True,
        "carrier": "FluidSynth SP-001 (FluidR3_GM, dry -R 0 -C 0 -g 1.2)",
        "target_lufs": TARGET_LUFS, "ceiling_db": CEILING_DB,
    },
    "source_midi": str(SRC),
    "reworked_midi": str(reworked_midi),
    "source_bpm": BPM,
    "source_key": "G major",
    "source_pitch_classes": sorted(SCALE_PCS),
    "bar_roots": PROG_ROOT_PC,
    "output_wav": str(final_wav),
    "output_ogg": str(final_ogg),
    "raw_wav": str(raw_wav),
    "dry_reference_wav": str(dry_wav),
    "lufs": meas_lufs, "peak": peak_val, "silence_pct": silence_pct, "rms": rms,
    "pitch_verdict": pitch_verdict, "hit_rate": hit_final, "he_mean": he_final,
    "he_dry": he_dry, "he_retention": he_retention,
    "preflight_source_before_rework": before,
    "preflight_source_after_rework": after,
}
(OUT / "provenance.json").write_text(json.dumps(provenance, indent=2))

# ===========================================================================
# 8. REPORT.md
# ===========================================================================
REPORT = """# SP-109 Tape-Stop / Turntable-Stop — production report

- **Date**: 2026-10-27
- **Job**: random-style production (SP), layer-aligned
- **Method**: SP-109 (`sound.effects.tape_stop`) — TapeStop processor, classic
  mode (rate-ramp resample: pitch AND time drop together, the vinyl/turntable
  stop sound). Cableguys TimeStop-style offline render.
- **Layer**: ABSOLUTE (whole rendered mix processed as one layer; the effect is
  applied as a tape-stop OUTRO over the final {stop_s}s).

## Selection
- **Registry source**: `workflows.musicom_workflow.SP_METHODS` (69 registered;
  {pool_size} in pool after excluding recent-7-day {recent_excluded} and
  baseline SP-001).
- **Source composition**: `Styles/Country/038-steel-guitar-demo/MIDI/country_ensemble_16bar.mid`
  (G major country ensemble, 120 BPM, 480 TPB, 16 bars, 2 voices — acoustic
  bass prog 32 + steel acoustic guitar prog 25).

## Pre-flight audit (3 rules) — **FAIL on source, REWORKED before production**

| rule | before (source) | after (rework) |
|---|---|---|
| Grid sync (16th = 120 ticks) | **FAIL** off-grid = {g_before} | **PASS** off-grid = {g_after} |
| Harmony (G major scale + chord tones) | out-of-scale = {s_before}, out-of-chord = **{c_before}** | out-of-scale = {s_after}, out-of-chord = {c_after} |
| Zero-drift (equal track ends) | **FAIL** ends = {e_before} | **PASS** ends = {e_after} |

The source is an early (June 24) ensemble whose steel-guitar strums are
rolled-chord grace notes (onsets at ~10-30 tick offsets -> 448 off-grid) with
105 non-chord passing/colour tones, and whose two tracks end at different
ticks (30480 vs 34330). It was rebuilt with `UnitMatrixComposer` as a clean
16-bar G major country ensemble faithful to the original DNA: bass
root-5th-root-5th quarter notes over the I-I-I-I IV-IV I-I V-V IV-IV I-I-I-I
progression, steel guitar downbeat strums + 8th-note 5th "chicks". All onsets
grid-locked, all notes chord tones in G major, both tracks end at 30720 ticks
(`validate()` PASS). Raw character preserved in `MIDI/reworked-phase1.mid`.

## SP-109 absolute layer (classic tape-stop outro)
- Carrier: FluidSynth (FluidR3_GM) full-mix render of the reworked MIDI, dry
  (`-R 0 -C 0 -g 1.2`), 44100 Hz.
- Effect: `TapeStop(mode="classic", stop_time_sec={stop_s}, gain_comp=True)` on
  the final {stop_s} s of the mix (the last phrase). Playback rate ramps 1.0 →
  ~0 (exponential), so the piece ends as if a turntable was stopped — pitch and
  time falling together. The preceding body is untouched.
- Mastered to {tgt:.0f} LUFS (country target), −1 dBTP ceiling.

## Verification
- **Pitch**: dominant-peak-in-key hit rate = {hit_final:.4f} ({valid_final}
  windows; the tape-stop outro deliberately detunes the last ~{stop_s} s, which
  is the desired effect) → **{pitch_verdict}**
- **Harmonic energy (8 harmonics of dominant)**: final {he_final:.4f} vs dry
  {he_dry:.4f} (retention {he_retention:.3f})
- **Silence**: {silence_pct:.2f}%
- **RMS**: {rms:.4f}
- **LUFS**: {meas_lufs:.2f}  **true peak**: {peak_val:.4f}

## Files
- `{final_wav}` ({wav_bytes} bytes)
- `{final_ogg}` ({ogg_bytes} bytes)
- `{raw_wav}` (tape-stop applied, pre-master)
- `{dry_wav}` (dry reworked source reference, pre-production)
- `MIDI/source_original.mid` (original source)
- `MIDI/reworked.mid` (clean grid-locked rework)
- `MIDI/reworked-phase1.mid` (raw phase-1 character sidecar)
- `Audio/stems/` ({n_stems} dry per-instrument stems, pre-effect)
- `provenance.json`, `Analysis/render_stats.json`

## Notes
- SP-109 is a transition/outro effect, not a continuous processor. Applying it
  across the whole track would slow the entire piece from bar 1 (unmusical);
  the idiomatic use — and the one applied here — is a wind-down over the final
  phrase. `modern` (granular pitch-only drop, time-locked) and `loop`
  (capture+retrigger stutter) modes remain available in the module.
- The composition was brought to rule-clean state before any sound change, per
  the pre-flight gate: 448 off-grid + 105 out-of-chord + zero-drift fail →
  all three to 0.
""".format(
    stop_s=STOP_TIME,
    pool_size=len(json.loads((OUT.parent / ".selection_cron.json").read_text()).get("pool_methods", [])),
    recent_excluded=", ".join(sorted(json.loads((OUT.parent / ".selection_cron.json").read_text()).get("recent_excluded", []))),
    g_before=before["grid_off"], g_after=after["grid_off"],
    s_before=before["out_scale"], s_after=after["out_scale"],
    c_before=before["out_chord"], c_after=after["out_chord"],
    e_before=before["track_ends"], e_after=after["track_ends"],
    tgt=TARGET_LUFS,
    hit_final=hit_final, valid_final=valid_final, pitch_verdict=pitch_verdict,
    he_final=he_final, he_dry=he_dry, he_retention=he_retention,
    silence_pct=silence_pct, rms=rms, meas_lufs=meas_lufs, peak_val=peak_val,
    final_wav=final_wav, final_ogg=final_ogg, raw_wav=raw_wav, dry_wav=dry_wav,
    wav_bytes=final_wav.stat().st_size, ogg_bytes=final_ogg.stat().st_size,
    n_stems=len(stems) if isinstance(stems, dict) else 0,
)
(OUT / "REPORT.md").write_text(REPORT)
print("REPORT.md written")

# copy scripts into project
for s in ("select_job_20261027.py",):
    srcp = OUT.parent / s
    if srcp.exists():
        try:
            shutil.copy2(str(srcp), str(SCRIPTS / s))
        except shutil.SameFileError:
            pass
try:
    shutil.copy2(__file__, str(SCRIPTS / "produce_sp109_cron.py"))
except shutil.SameFileError:
    pass

print("Done.")
