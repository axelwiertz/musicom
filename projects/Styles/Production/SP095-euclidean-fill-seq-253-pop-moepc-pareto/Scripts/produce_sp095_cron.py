# -*- coding: utf-8 -*-
"""SP-095 Euclidean Fill Sequencer production pass (absolute layer).

Source : Styles/Pop/253-pop-moepc-pareto/MIDI/253-pop-moepc-pareto-perfect.mid
         (C-major I-V-vi-IV pop, 112 BPM, 480 TPB, 28 bars = 53760 ticks,
          5 voices: Piano lead / Synth Pad / Electric Bass / Glockenspiel /
          Drum Kit; grid-locked "perfect" variant = compositional truth).

Method : SP-095 -> sound.generators.euclidean_fill_seq (EuclideanFillSequencer,
         Maschine 3.7-style). ABSOLUTE layer: the whole 5-voice pop texture is
         replaced by a euclidean-fill-driven groove. Per-bar C-major chord
         triads (from the source's BAR_DEGREES) are re-voiced as three
         EuclideanFillSequencer voices (Bass / Chord / Sparkle) with Bjorklund
         primary pulses + probabilistic fills + live per-bar rotation, rendered
         through a FluidSynth carrier (SP-001) and mastered.

Pipeline: source MIDI -> 3-rule audit (grid/harmony/zero-drift)
          -> per-bar euclidean-fill note generation (3 voices)
          -> euclidean groove MIDI -> FluidSynth raw WAV + dry reference + stems
          -> master() (pop -9 LUFS, -1 dBTP) -> WAV + Opus OGG
          -> pitch/grid/harmony/silence verification -> REPORT.md.
"""
import json
import os
import shutil
import subprocess
from pathlib import Path

import numpy as np
import mido

from rules.progression import Scale7ChordDegree
from sound.render.fluidsynth import discover_soundfont
from sound.generators.euclidean_fill_seq import EuclideanFillSequencer, bjorklund
from sound.effects.mastering import master, target_for_style, measure_lufs

SRC = Path("/opt/data/repos/musicom/projects/Styles/Pop/253-pop-moepc-pareto/MIDI/253-pop-moepc-pareto-perfect.mid")
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/SP095-euclidean-fill-seq-253-pop-moepc-pareto")
AUD = OUT / "Audio"
STEMS = AUD / "stems"
MIDIDIR = OUT / "MIDI"
ANALYSIS = OUT / "Analysis"
SCRIPTS = OUT / "Scripts"

for d in (AUD, STEMS, MIDIDIR, ANALYSIS, SCRIPTS):
    d.mkdir(parents=True, exist_ok=True)

SR = 44100
BPM = 112.0
TPB = 480
BAR = 1920
N_BARS = 28
TOTAL_TICKS = BAR * N_BARS          # 53760
GRID = 120                          # 16th-note
STEP = 120                          # euclidean step ticks (16th)
SEED = 20261023
STYLE = "pop"

# C major (ionian): C D E F G A B
SCALE = [0, 2, 4, 5, 7, 9, 11]
KEY_ROOT = 60                       # C4
CMAJ_PCS = set(SCALE)

# C-major pop progression (I-V-vi-IV bestseller), 0-based degrees
# (I=0 ii=1 iii=2 IV=3 V=4 vi=5 vii=6) — 28 bars from the source compose.py.
BAR_DEGREES = [
    0, 0, 4, 4,                     # Intro  (I I V V)
    0, 4, 5, 3, 0, 4, 5, 3,         # Verse  (I V vi IV x2)
    3, 4, 0, 5, 3, 4, 0, 4,         # Chorus (IV V I vi IV V I V)
    5, 4, 3, 4,                     # Bridge (vi V IV V)
    0, 3, 4, 0,                     # Outro  (I IV V I)
]
assert len(BAR_DEGREES) == N_BARS

# Euclidean voice configs (all EuclideanFillSequencer instances)
VOICES = {
    "Bass":     dict(pulses=4, steps=16, fill_density=0.00, dur=300,
                     program=33, channel=2, oct_shift=-24, cycle=(0, 2)),
    "Chord":    dict(pulses=5, steps=16, fill_density=0.25, dur=200,
                     program=88, channel=1, oct_shift=0, cycle=(0, 1, 2)),
    "Sparkle":  dict(pulses=7, steps=16, fill_density=0.40, dur=120,
                     program=9, channel=3, oct_shift=12, cycle=(0, 1, 2, 0)),
}

FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"


def diatonic(degree):
    return Scale7ChordDegree.get_diatonic_note(KEY_ROOT, SCALE, degree)


def triad_of(bar):
    d = BAR_DEGREES[bar]
    return [diatonic(d), diatonic(d + 2), diatonic(d + 4)]


def read_wav(p):
    import wave
    with wave.open(str(p), "rb") as wf:
        nch = wf.getnchannels()
        sr = wf.getframerate()
        data = wf.readframes(wf.getnframes())
        samples = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
        if nch == 1:
            return np.vstack([samples, samples]), sr
        return samples.reshape(-1, nch).T, sr


def write_wav(p, audio, sr=SR):
    import wave
    audio = np.clip(np.asarray(audio, dtype=np.float32), -1.0, 1.0)
    if audio.ndim == 1:
        nch, interleaved = 1, audio
    elif audio.shape[0] == 2:
        nch, interleaved = 2, audio.T.reshape(-1)
    else:
        nch, interleaved = audio.shape[0], audio.T.reshape(-1)
    data = (interleaved * 32767.0).astype(np.int16).tobytes()
    with wave.open(str(p), "wb") as wf:
        wf.setnchannels(nch)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(data)


# ===========================================================================
# 1. Pre-flight 3-rule audit on the SOURCE (perfect MIDI)
# ===========================================================================
def audit(path):
    mf = mido.MidiFile(str(path))
    grid_off = out_scale = out_chord = 0
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
                if (m.note % 12) not in CMAJ_PCS:
                    out_scale += 1
                bar = min(t // BAR, N_BARS - 1)
                if (m.note % 12) not in {n % 12 for n in triad_of(bar)}:
                    out_chord += 1
        if n_notes:
            track_ends.append(t)
    zero_drift = len(set(track_ends)) == 1
    return {"grid_off": grid_off, "out_scale": out_scale, "out_chord": out_chord,
            "zero_drift": zero_drift, "track_ends": sorted(set(track_ends)),
            "total_notes": total_notes}


shutil.copy2(str(SRC), str(MIDIDIR / "source_original.mid"))
before = audit(SRC)
print("PREFLIGHT source (perfect):", before)
assert before["grid_off"] == 0, "grid sync FAIL on source"
assert before["out_scale"] == 0, "out-of-scale FAIL on source"
assert before["out_chord"] == 0, "out-of-chord FAIL on source"
assert before["zero_drift"], "zero-drift FAIL on source"

# ===========================================================================
# 2. SP-095 euclidean-fill generative pass (absolute layer)
# ===========================================================================
groove_events = {v: [] for v in VOICES}   # voice -> list[(pitch, vel, start, end)]

for bar in range(N_BARS):
    triad = triad_of(bar)
    b0 = bar * BAR
    for vname, cfg in VOICES.items():
        pulses = cfg["pulses"]
        steps = cfg["steps"]
        # live rotation: bass stays anchored, chord + sparkle morph per bar
        if vname == "Bass":
            rotation = 0
        elif vname == "Chord":
            rotation = bar % steps
        else:
            rotation = (bar * 3) % steps
        seq = EuclideanFillSequencer(
            pulses=pulses, steps=steps, rotation=rotation,
            fill_density=cfg["fill_density"], fill_velocity_factor=0.6,
            primary_velocity_range=(88, 118), swing=0.0,
            seed=SEED * 101 + bar * 7 + list(VOICES).index(vname),
        )
        evs = seq.generate(num_bars=1, time_per_step=STEP)
        cyc = cfg["cycle"]
        oct_shift = cfg["oct_shift"]
        dur = cfg["dur"]
        k = 0
        for e in evs:
            pitch = triad[cyc[k % len(cyc)]] + oct_shift
            k += 1
            start = b0 + e["start"]
            end = min(b0 + BAR, start + dur)
            groove_events[vname].append((pitch, int(e["velocity"]), start, end))

total_gen = sum(len(v) for v in groove_events.values())
print("SP-095 generated events:", {v: len(groove_events[v]) for v in groove_events})
gen_pcs = sorted({p % 12 for v in groove_events.values() for (p, _, _, _) in v})
print("generated pitch classes:", gen_pcs)
assert set(gen_pcs) <= CMAJ_PCS, "generated notes out of C major"

# ===========================================================================
# 3. Write euclidean groove MIDI (mido) — zero-drift padded
# ===========================================================================
def build_track(pc_program, channel, events):
    tr = mido.MidiTrack()
    tr.append(mido.Message("program_change", program=pc_program, channel=channel, time=0))
    ons = [(s, "on", p, v) for (p, v, s, e) in events]
    offs = [(e, "off", p, 0) for (p, v, s, e) in events]
    all_ev = sorted(ons + offs, key=lambda x: (x[0], 0 if x[1] == "off" else 1))
    prev = 0
    for t, kind, pitch, vel in all_ev:
        dt = t - prev
        if dt < 0:
            dt = 0
        prev += dt
        if kind == "on":
            tr.append(mido.Message("note_on", note=pitch, velocity=vel, channel=channel, time=dt))
        else:
            tr.append(mido.Message("note_off", note=pitch, velocity=0, channel=channel, time=dt))
    if prev < TOTAL_TICKS:
        tr.append(mido.MetaMessage("end_of_track", time=TOTAL_TICKS - prev))
    else:
        tr.append(mido.MetaMessage("end_of_track", time=0))
    return tr


mid = mido.MidiFile(ticks_per_beat=TPB)
tr0 = mido.MidiTrack()
tr0.append(mido.MetaMessage("set_tempo", tempo=int(round(60000000 / BPM)), time=0))
tr0.append(mido.MetaMessage("time_signature", numerator=4, denominator=4, time=0))
tr0.append(mido.MetaMessage("end_of_track", time=TOTAL_TICKS))
mid.tracks.append(tr0)
for vname, cfg in VOICES.items():
    mid.tracks.append(build_track(cfg["program"], cfg["channel"], groove_events[vname]))
groove_midi = MIDIDIR / "SP095-euclidean-groove.mid"
mid.save(str(groove_midi))
print("wrote", groove_midi, groove_midi.stat().st_size, "bytes")

# output audit (should be clean: 0 off-grid, 0 out-of-scale, 0 out-of-chord)
out_audit = audit(groove_midi)
print("OUTPUT audit (euclidean groove):", out_audit)
assert out_audit["grid_off"] == 0
assert out_audit["out_scale"] == 0
assert out_audit["out_chord"] == 0
assert out_audit["zero_drift"]

# ===========================================================================
# 4. Render (FluidSynth SP-001 carrier)
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


dry_wav = OUT / "dry_full_mix_source_reference.wav"
render(SRC, dry_wav)
print("dry reference:", dry_wav.stat().st_size, "bytes")

raw_wav = OUT / "SP095_euclidean_fill_raw.wav"
render(groove_midi, raw_wav)
print("SP-095 raw:", raw_wav.stat().st_size, "bytes")

try:
    from sound.render.pipeline import RenderPipeline
    pipeline = RenderPipeline(soundfont_path=SF, fluidsynth_bin=FLUID, sample_rate=SR)
    stems = pipeline.render_stems(str(groove_midi), str(STEMS), format="wav")
    print("rendered %d stems" % len(stems))
except Exception as e:
    stems = {}
    print("stem render skipped:", repr(e)[:200])

# ===========================================================================
# 5. Master
# ===========================================================================
TARGET_LUFS = target_for_style(STYLE)      # pop -> -9.0
CEILING_DB = -1.0

raw_audio, sr = read_wav(raw_wav)          # (2, N)
raw_tm = raw_audio.T.astype(np.float32)    # (N, 2)
print("mastering (target %s LUFS, ceiling %s dBTP)..."
      % (TARGET_LUFS, CEILING_DB))
mastered_tm, rep = master(raw_tm, target_lufs=TARGET_LUFS, ceiling_db=CEILING_DB,
                          sample_rate=SR)
print("master report: LUFS %.2f, true peak %.2f dBTP"
      % (float(rep.get("integrated_lufs", 0)), float(rep.get("true_peak_db", 0))))
final_master = mastered_tm.T                # (2, N)

final_wav = OUT / "SP095-euclidean-fill-seq-253-pop-moepc-pareto.wav"
final_ogg = OUT / "SP095-euclidean-fill-seq-253-pop-moepc-pareto.ogg"
write_wav(final_wav, final_master, sr=SR)
r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(final_wav),
                    "-codec:a", "libopus", "-application", "voip", "-b:a", "48k",
                    str(final_ogg)], capture_output=True, text=True, timeout=180)
assert r.returncode == 0 and final_ogg.stat().st_size > 10000, "ogg encode failed: %s" % r.stderr[-300:]
print("final WAV:", final_wav.stat().st_size, "final OGG:", final_ogg.stat().st_size)

# ===========================================================================
# 6. Verification
# ===========================================================================
meas_lufs = float(measure_lufs(mastered_tm, sample_rate=SR))
peak_val = float(np.max(np.abs(final_master)))
mono = 0.5 * (final_master[0] + final_master[1])
silence_pct = float(np.sum(np.abs(mono) < 0.001) / len(mono)) * 100.0
rms = float(np.sqrt(np.mean(mono ** 2)))
rms_map = [round(float(np.sqrt(np.mean(mono[i:i + SR] ** 2))), 4)
           for i in range(0, len(mono), SR)]
print("LUFS=%.2f peak=%.4f silence=%.2f%% rms=%.4f"
      % (meas_lufs, peak_val, silence_pct, rms))


def pitch_verify(audio_2n, pcs):
    mono_ = 0.5 * (audio_2n[0] + audio_2n[1])
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


hit_rate, he_mean, valid = pitch_verify(final_master, CMAJ_PCS)
dry_hit, dry_he, dry_valid = pitch_verify(raw_audio, CMAJ_PCS)
he_retention = (he_mean / dry_he) if dry_he > 0 else 0.0
pitch_verdict = "PASS" if (hit_rate >= 0.60 and he_mean >= 0.30) else "FAIL"
print("Pitch verify: valid=%d hit=%.4f mean_HE=%.4f | dry hit=%.4f HE=%.4f | retention=%.3f -> %s"
      % (valid, hit_rate, he_mean, dry_hit, dry_he, he_retention, pitch_verdict))

# ===========================================================================
# 7. Artifacts: render_stats + provenance
# ===========================================================================
(ANALYSIS / "render_stats.json").write_text(json.dumps({
    "lufs": meas_lufs, "peak": peak_val, "silence_pct": silence_pct,
    "rms": rms, "rms_per_sec": rms_map,
    "hit_rate": hit_rate, "mean_harmonic_energy": he_mean, "valid_windows": valid,
    "dry_hit_rate": dry_hit, "dry_he": dry_he, "he_retention": he_retention,
    "pitch_verdict": pitch_verdict,
    "n_generated_notes": total_gen,
    "generated_pitch_classes": gen_pcs,
    "n_stems": len(stems) if isinstance(stems, dict) else 0,
    "target_lufs": TARGET_LUFS,
}, indent=2))

provenance = {
    "job": "random-style production (SP) layer-aligned",
    "date": "2026-10-23",
    "seed": SEED,
    "method": "SP-095",
    "method_module": "sound.generators.euclidean_fill_seq",
    "method_desc": "Euclidean Fill Sequencer w/ Live Rotation (Maschine 3.7 Euclidean Sequencer-style)",
    "layer": "ABSOLUTE",
    "params": {
        "sample_rate": SR, "bpm": BPM, "ppqn": TPB,
        "step_ticks": STEP, "step_resolution": "16th",
        "voices": VOICES,
        "carrier_program": {v: VOICES[v]["program"] for v in VOICES},
        "carrier": "FluidSynth SP-001 (FluidR3_GM)",
        "fill_velocity_factor": 0.6, "swing": 0.0,
        "target_lufs": TARGET_LUFS, "ceiling_db": CEILING_DB,
    },
    "source_midi": str(SRC),
    "groove_midi": str(groove_midi),
    "source_bpm": BPM,
    "source_key": "C major (ionian)",
    "source_pitch_classes": sorted(CMAJ_PCS),
    "bar_degrees": BAR_DEGREES,
    "output_wav": str(final_wav),
    "output_ogg": str(final_ogg),
    "raw_wav": str(raw_wav),
    "dry_reference_wav": str(dry_wav),
    "lufs": meas_lufs, "peak": peak_val, "silence_pct": silence_pct, "rms": rms,
    "pitch_verdict": pitch_verdict, "hit_rate": hit_rate, "he_mean": he_mean,
    "dry_he": dry_he, "he_retention": he_retention,
    "preflight_source": before,
    "output_audit": out_audit,
}
(OUT / "provenance.json").write_text(json.dumps(provenance, indent=2))

# ===========================================================================
# 8. REPORT.md
# ===========================================================================
REPORT = """# SP-095 Euclidean Fill Sequencer — production report

- **Date**: 2026-10-23
- **Job**: random-style production (SP), layer-aligned
- **Method**: SP-095 (`sound.generators.euclidean_fill_seq`) — Euclidean Fill
  Sequencer w/ Live Rotation (Maschine 3.7-style). Bjorklund Euclidean primary
  pulses + probabilistic lower-velocity fills + live per-bar rotation.
- **Layer**: ABSOLUTE (whole-piece texture re-voicing; note material preserved
  as per-bar chord-tone re-grooving).

## Selection
- **Registry source**: `workflows.musicom_workflow.SP_METHODS` (55 pickable in
  pool; recent-7-day SP-090/092/099/101/105/108/111 excluded).
- **Source composition**: `Styles/Pop/253-pop-moepc-pareto/MIDI/253-pop-moepc-pareto-perfect.mid`
  (C-major I-V-vi-IV pop, 112 BPM, 480 TPB, 28 bars, 5 voices — Piano lead /
  Synth Pad / Electric Bass / Glockenspiel / Drum Kit; grid-locked "perfect"
  variant used as the compositional truth).
- **Selection note**: the first seeded shuffle pick (single-pitch C5 ostinato,
  `Other/unknown-daily-2026-06-05`) was rejected as degenerate (<3 pitch
  classes — musically meaningless, cannot carry a production pass). A
  "musically meaningful" gate (>=3 distinct pitch classes) was added to the
  selector and the re-roll landed on 253-pop-moepc-pareto. Documented in
  `.selection_cron.json` under `rejected_degenerate`.

## Pre-flight audit (3 rules) — PASS, no rework needed
| rule | result |
|---|---|
| Grid sync (16th = 120 ticks) | **PASS** — off-grid = {grid_off} |
| Harmony (in key + chord tone) | **PASS** — out-of-scale = {out_scale}, out-of-chord = {out_chord} (C major, per-bar triads) |
| Zero-drift (equal track ends) | **PASS** — 5 note tracks, end = {track_end} ticks |

## SP-095 absolute layer (euclidean-fill groove)
Per-bar C-major triad (from the source `BAR_DEGREES` I-V-vi-IV progression) is
re-voiced as three `EuclideanFillSequencer` voices:

| Voice | pulses/steps | fill_density | rotation | register | program |
|---|---|---|---|---|---|
| Bass | 4/16 | 0.00 | fixed 0 | chord root/fifth −24 | 33 Electric Bass |
| Chord | 5/16 | 0.25 | +1/bar | triad root/3rd/5th | 88 Synth Pad |
| Sparkle | 7/16 | 0.40 | +3/bar | chord tones +12 | 9 Glockenspiel |

- Primary velocity 88-118, fill velocity factor 0.6, swing 0.0 (grid-locked).
- **Live rotation**: chord layer advances 1 step/bar, sparkle 3 steps/bar →
  the groove morphs through the 28 bars while the bass stays anchored.
- {n_gen} generated notes, pitch classes {gen_pcs} (all in C major).
- Rendered through FluidSynth (FluidR3_GM) carrier at 44100 Hz, mastered to
  pop −9 LUFS target, −1 dBTP ceiling.

## Output audit (the generated groove, mirror of the 3 rules) — PASS
| rule | result |
|---|---|
| Grid sync | **PASS** — off-grid = {o_grid} |
| Harmony | **PASS** — out-of-scale = {o_scale}, out-of-chord = {o_chord} |
| Zero-drift | **PASS** — 3 note tracks, end = {o_end} ticks |

## Verification
- **Pitch**: dominant-peak-in-key hit rate = {hit_rate:.4f} ({valid} windows) → **{pitch_verdict}**
- **Harmonic energy (8 harmonics of dominant)**: {he_mean:.4f} (dry reference {dry_he:.4f}, retention {he_retention:.3f})
- **Silence**: {silence_pct:.2f}%
- **RMS**: {rms:.4f}
- **LUFS**: {meas_lufs:.2f}  **true peak**: {peak_val:.4f}

## Files
- `{final_wav}` ({wav_bytes} bytes)
- `{final_ogg}` ({ogg_bytes} bytes)
- `{raw_wav}` (pre-master)
- `{dry_wav}` (dry source reference, pre-production)
- `MIDI/source_original.mid` (reference copy)
- `MIDI/SP095-euclidean-groove.mid` (generated euclidean-fill groove)
- `Audio/stems/` ({n_stems} per-voice stems)
- `provenance.json`, `Analysis/render_stats.json`

## Notes
- SP-095 is a rhythm/groove generator (drum-machine-style). Its absolute-layer
  application re-voices the source harmony as a euclidean-fill arpeggio
  groove; the Bjorklund pulses carry the primary hits and the probabilistic
  fills add the lower-velocity connective tissue, exactly the method's two
  headline features (fills + live rotation).
""".format(
    grid_off=before["grid_off"], out_scale=before["out_scale"],
    out_chord=before["out_chord"], track_end=before["track_ends"][0],
    n_gen=total_gen, gen_pcs=gen_pcs,
    o_grid=out_audit["grid_off"], o_scale=out_audit["out_scale"],
    o_chord=out_audit["out_chord"], o_end=out_audit["track_ends"][0],
    hit_rate=hit_rate, valid=valid, pitch_verdict=pitch_verdict,
    he_mean=he_mean, dry_he=dry_he, he_retention=he_retention,
    silence_pct=silence_pct, rms=rms, meas_lufs=meas_lufs, peak_val=peak_val,
    final_wav=final_wav, final_ogg=final_ogg, raw_wav=raw_wav, dry_wav=dry_wav,
    wav_bytes=final_wav.stat().st_size, ogg_bytes=final_ogg.stat().st_size,
    n_stems=len(stems) if isinstance(stems, dict) else 0,
)
(OUT / "REPORT.md").write_text(REPORT)
print("REPORT.md written")

# copy scripts into project
for s in ("select_job_20261023.py",):
    srcp = OUT.parent / s
    if srcp.exists():
        try:
            shutil.copy2(str(srcp), str(SCRIPTS / s))
        except shutil.SameFileError:
            pass
try:
    shutil.copy2(__file__, str(SCRIPTS / "produce_sp095_cron.py"))
except shutil.SameFileError:
    pass

print("Done.")
