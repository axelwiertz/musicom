# -*- coding: utf-8 -*-
"""SP-115 Chord-Driven 3-Track Generative Arranger (Midicake UNA-style) production pass.

Source : Styles/Experimental/262-harmonic-chorale-variations
         (F major chorale, 92 BPM, 4/4, 480 TPB, 24 bars = 46080 ticks;
          4 voices SATB: Soprano Flute 73 / Alto Strings 48 / Tenor Cello 42 /
          Bass Contrabass 43; harmony per section I-vi-IV-V and variants).
         Selected MIDI = -humanized.mid (selector pick); -perfect.mid is the
         grid-locked compositional truth used as production source.

Method : SP-115 -> sound.generators.chord_arranger (ChordDrivenArranger).
         ABSOLUTE layer: the WHOLE production layer is replaced by a
         chord-driven 3-track generative arrangement (chord/rhythm pad +
         arpeggiated melody + harmony-following bass) fed by the source's
         24-bar F-major harmony.  Pure MIDI-event level (no audio DSP);
         the arrangement is rendered via FluidSynth + master().

Pipeline: source MIDI -> 3-rule pre-flight audit (grid/harmony/zero-drift)
          -> extract 24-bar chord plan (I-vi-IV-V family, F major)
          -> ChordDrivenArranger.generate(chords, macros) -> 3 tracks
          -> serialize MIDI (tempo 92, programs 48/73/43) -> FluidSynth dry
          -> master() (-14 LUFS experimental fallback, -1 dBTP) -> WAV + OGG
          -> per-track stems -> pitch/silence/RMS verification -> REPORT.md.
"""
import json
import os
import shutil
import subprocess
from pathlib import Path

import numpy as np
import mido

from sound.generators.chord_arranger import ChordDrivenArranger, QUALITIES
from sound.render.fluidsynth import discover_soundfont
from sound.effects.mastering import master, target_for_style, measure_lufs
from sound.utils.io import read_wav, write_wav

# ---- paths -------------------------------------------------------------
SRC_PERFECT = Path("/opt/data/repos/musicom/projects/Styles/Experimental/"
                   "262-harmonic-chorale-variations/MIDI/"
                   "262-harmonic-chorale-variations-perfect.mid")
SRC_HUMANIZED = Path("/opt/data/repos/musicom/projects/Styles/Experimental/"
                     "262-harmonic-chorale-variations/MIDI/"
                     "262-harmonic-chorale-variations-humanized.mid")
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/"
           "SP115-chord-arranger-262-harmonic-chorale-variations")
AUD = OUT / "Audio"
STEMS = AUD / "stems"
MIDIDIR = OUT / "MIDI"
ANALYSIS = OUT / "Analysis"
SCRIPTS = OUT / "Scripts"

for d in (AUD, STEMS, MIDIDIR, ANALYSIS, SCRIPTS):
    d.mkdir(parents=True, exist_ok=True)

# ---- constants ---------------------------------------------------------
SR = 44100
TPB = 480
BAR = 1920                 # 4/4 bar
GRID = 120                 # 16th note
BPM = 92.0
N_BARS = 24
TOTAL_TICKS = BAR * N_BARS  # 46080
SEED = 20261031
STYLE = "Experimental"     # -> GENRE_LUFS has no "experimental" key -> -14.0
TARGET_LUFS = target_for_style(STYLE)
CEILING_DB = -1.0
FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"

# F major pitch classes: F G A Bb C D E
FMAJ_PCS = {0, 2, 4, 5, 7, 9, 10}

# 24-bar chord plan (root_midi, quality) — F major chorale harmony,
# cross-checked against the source's beat-1 voicing (see analysis).
CHORD_PLAN = [
    (53, "maj"), (50, "min"), (58, "maj"), (60, "maj"),   # A: I vi IV V
    (60, "maj"), (58, "maj"), (50, "min"), (53, "maj"),   # B: V IV vi I
    (60, "maj"), (53, "maj"), (55, "min"), (60, "maj"),   # C: V I ii V
    (58, "maj"), (55, "min"), (60, "maj"), (53, "maj"),   # D: IV ii V I
    (53, "maj"), (58, "maj"), (55, "min"), (60, "maj"),   # E: I IV ii V
    (58, "maj"), (60, "maj"), (53, "maj"), (53, "maj"),   # F: IV V I I
]
assert len(CHORD_PLAN) == N_BARS
CHORD_PCS = [{(r + iv) % 12 for iv in QUALITIES[q]} for r, q in CHORD_PLAN]

# per-bar degree labels (for the report)
DEGREE_LABELS = (
    ["I", "vi", "IV", "V"] * 1
    + ["V", "IV", "vi", "I"]
    + ["V", "I", "ii", "V"]
    + ["IV", "ii", "V", "I"]
    + ["I", "IV", "ii", "V"]
    + ["IV", "V", "I", "I"]
)

# SP-115 macro knobs (8) — chorale-appropriate: straight (no swing), legato
# gate, moderate density/probability, no ratchets/octave shift, mild spread.
MACROS = {
    "density": 0.5,
    "probability": 0.7,
    "swing": 0.0,
    "accent": 0.4,
    "ratchet": 0.0,
    "octave": 0.0,
    "gate": 0.6,
    "spread": 0.3,
}

# track -> (channel, GM program) for the 3 arranger tracks
TRACK_PROGRAMS = {
    "chord":  (0, 48),   # String Ensemble 1 (matches source Alto)
    "melody": (1, 73),   # Flute (matches source Soprano)
    "bass":   (2, 43),   # Contrabass (matches source Bass)
}


# =========================================================================
# 1. Pre-flight 3-rule audit (grid sync / harmony / zero-drift)
# =========================================================================
def audit(path):
    mf = mido.MidiFile(str(path))
    grid_off = out_scale = out_chord = 0
    total_notes = 0
    track_ends = []
    pcs_seen = set()
    for tr in mf.tracks:
        chans = {m.channel for m in tr if m.type in ("note_on", "note_off")}
        if 9 in chans or not chans:
            continue
        t = 0
        n_notes = 0
        for m in tr:
            t += m.time
            if m.type == "note_on" and m.velocity > 0:
                n_notes += 1
                total_notes += 1
                if (t % GRID) != 0:
                    grid_off += 1
                pc = m.note % 12
                pcs_seen.add(pc)
                if pc not in FMAJ_PCS:
                    out_scale += 1
                bar = min(t // BAR, N_BARS - 1)
                if pc not in CHORD_PCS[bar]:
                    out_chord += 1
        if n_notes:
            track_ends.append(t)
    zero_drift = len(set(track_ends)) == 1
    return {"grid_off": grid_off, "out_scale": out_scale,
            "out_chord": out_chord, "total_notes": total_notes,
            "zero_drift": zero_drift, "track_ends": sorted(set(track_ends)),
            "pcs_seen": sorted(pcs_seen)}


print("== pre-flight audit ==")
before_h = audit(SRC_HUMANIZED)   # selector's literal pick
print("humanized (selector pick):", before_h)
before = audit(SRC_PERFECT)        # grid-locked production source
print("perfect (production source):", before)
assert before["grid_off"] == 0, "grid sync FAIL on perfect source"
assert before["out_scale"] == 0, "out-of-scale FAIL on perfect source"
assert before["out_chord"] == 0, "out-of-chord FAIL on perfect source"
assert before["zero_drift"], "zero-drift FAIL on perfect source"
print("PRE-FLIGHT PASS on perfect source "
      "(grid 0 / out-scale 0 / out-chord 0, zero-drift).")

shutil.copy2(str(SRC_PERFECT), str(MIDIDIR / "source_perfect.mid"))
shutil.copy2(str(SRC_HUMANIZED), str(MIDIDIR / "source_humanized.mid"))

# =========================================================================
# 2. Chord-driven generative arrangement (SP-115 absolute layer)
# =========================================================================
arr = ChordDrivenArranger(bpm=int(BPM), bars=N_BARS, seed=SEED)
events = arr.generate(CHORD_PLAN, macros=dict(MACROS))
print("generated events:", len(events))
by_track = {}
for ev in events:
    by_track.setdefault(ev["track"], []).append(ev)
print("per track:", {k: len(v) for k, v in sorted(by_track.items())})
for t in ("chord", "melody", "bass"):
    assert by_track.get(t), "track %s empty" % t

# =========================================================================
# 3. Serialize arrangement -> 4-track MIDI (conductor + 3 note tracks)
# =========================================================================
def write_arranger_midi(events, path, bpm, programs, total_ticks):
    mid = mido.MidiFile(ticks_per_beat=TPB)
    cond = mido.MidiTrack()
    mid.tracks.append(cond)
    cond.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(bpm), time=0))
    for tname, (ch, prog) in programs.items():
        cond.append(mido.Message("program_change", channel=ch, program=prog, time=0))

    for tname in ("chord", "melody", "bass"):
        ch, prog = programs[tname]
        tr = mido.MidiTrack()
        mid.tracks.append(tr)
        # program change lives IN the note track (not only the conductor) so
        # per-track stem renders pick up the correct GM timbre.
        tr.append(mido.Message("program_change", channel=ch, program=prog, time=0))
        entries = []
        for ev in events:
            if ev["track"] != tname:
                continue
            st = ev["start_tick"]
            if st >= total_ticks:
                continue
            end = min(ev["start_tick"] + ev["duration_ticks"], total_ticks)
            if end <= st:
                end = min(st + 1, total_ticks)
            entries.append((st, "on", ev["pitch"], int(ev["vel"]), ch))
            entries.append((end, "off", ev["pitch"], 0, ch))
        # note-offs execute before note-ons at duplicate ticks
        entries.sort(key=lambda x: (x[0], 0 if x[1] == "off" else 1))
        last = 0
        for tick, kind, note, vel, ch_ in entries:
            d = tick - last
            assert d >= 0, (tname, tick, last)
            if kind == "on":
                tr.append(mido.Message("note_on", channel=ch_, note=note,
                                       velocity=vel, time=d))
            else:
                tr.append(mido.Message("note_off", channel=ch_, note=note,
                                       velocity=0, time=d))
            last = tick
        if last < total_ticks:
            tr.append(mido.Message("note_on", channel=ch_, note=0, velocity=0,
                                   time=total_ticks - last))
    mid.save(str(path))
    return path


arr_mid = MIDIDIR / "SP115-arrangement.mid"
write_arranger_midi(events, arr_mid, BPM, TRACK_PROGRAMS, TOTAL_TICKS)
print("arrangement MIDI:", arr_mid, arr_mid.stat().st_size, "bytes")
assert arr_mid.stat().st_size > 40

# =========================================================================
# 4. FluidSynth dry render
# =========================================================================
SF = discover_soundfont()
assert SF and os.path.exists(SF), "SoundFont missing: %r" % SF
print("SoundFont:", SF)


def fluidsynth_render(midi_path, out_wav):
    r = subprocess.run([FLUID, "-ni", "-R", "0", "-C", "0", "-g", "1.2",
                        "-F", str(out_wav), SF, str(midi_path)],
                       capture_output=True, text=True, timeout=900)
    if r.returncode != 0 or not out_wav.exists() or out_wav.stat().st_size < 1000:
        raise RuntimeError("FluidSynth render failed: %s" % r.stderr[-500:])
    return out_wav


dry_wav = OUT / "dry_sp115_arrangement.wav"
fluidsynth_render(arr_mid, dry_wav)
print("dry WAV:", dry_wav.stat().st_size, "bytes")

dry_audio, _sr = read_wav(str(dry_wav))
if dry_audio.ndim == 1:
    dry_audio = np.column_stack([dry_audio, dry_audio])
dry_audio = np.asarray(dry_audio, dtype=np.float32)
assert _sr == SR, "unexpected sample rate %r" % _sr
print("dry audio shape:", dry_audio.shape,
      "peak", float(np.max(np.abs(dry_audio))))

# =========================================================================
# 5. Master
# =========================================================================
print("mastering (target %.1f LUFS, ceiling %.1f dBTP)..."
      % (TARGET_LUFS, CEILING_DB))
mastered, rep = master(dry_audio, target_lufs=TARGET_LUFS, ceiling_db=CEILING_DB,
                       sample_rate=SR)
print("master report: LUFS %.2f, true peak %.2f dBTP"
      % (float(rep.get("integrated_lufs", 0)), float(rep.get("true_peak_db", 0))))

final_wav = OUT / "SP115-chord-arranger-262-harmonic-chorale-variations.wav"
final_ogg = OUT / "SP115-chord-arranger-262-harmonic-chorale-variations.ogg"
write_wav(str(final_wav), mastered.astype(np.float32), SR, normalize=False)
r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(final_wav),
                    "-codec:a", "libopus", "-application", "voip", "-b:a", "48k",
                    str(final_ogg)], capture_output=True, text=True, timeout=180)
assert r.returncode == 0 and final_ogg.stat().st_size > 10000, \
    "ogg encode failed: %s" % r.stderr[-300:]
print("final WAV:", final_wav.stat().st_size,
      "final OGG:", final_ogg.stat().st_size)

# =========================================================================
# 6. Per-track stems
# =========================================================================
try:
    from sound.render.pipeline import RenderPipeline
    pipeline = RenderPipeline(soundfont_path=SF, fluidsynth_bin=FLUID,
                              sample_rate=SR)
    stems = pipeline.render_stems(str(arr_mid), str(STEMS), format="wav")
    print("rendered %d stems" % len(stems))
except Exception as e:
    stems = {}
    print("stem render skipped:", repr(e)[:200])

# =========================================================================
# 7. Verification
# =========================================================================
meas_lufs = float(measure_lufs(mastered, sample_rate=SR))
peak_val = float(np.max(np.abs(mastered)))
mono = 0.5 * (mastered[:, 0] + mastered[:, 1])
silence_pct = float(np.sum(np.abs(mono) < 0.001) / len(mono)) * 100.0
rms = float(np.sqrt(np.mean(mono ** 2)))
rms_map = [round(float(np.sqrt(np.mean(mono[i:i + SR] ** 2))), 4)
           for i in range(0, len(mono), SR)]
print("LUFS=%.2f peak=%.4f silence=%.2f%% rms=%.4f"
      % (meas_lufs, peak_val, silence_pct, rms))


def pitch_verify(audio_tm, pcs):
    wl = int(0.5 * SR)
    nw = len(audio_tm) // wl
    hits = valid = 0
    he_list = []
    for w in range(nw):
        seg = audio_tm[w * wl:(w + 1) * wl]
        if seg.ndim > 1:
            seg = 0.5 * (seg[:, 0] + seg[:, 1])
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


wet_hit, wet_he, wet_valid = pitch_verify(mastered, FMAJ_PCS)
dry_hit, dry_he, dry_valid = pitch_verify(dry_audio, FMAJ_PCS)
pitch_verdict = "PASS" if (wet_hit >= 0.60 and wet_he >= 0.30) else "FAIL"
print("pitch verify: wet hit=%.4f HE=%.4f | dry hit=%.4f HE=%.4f -> %s"
      % (wet_hit, wet_he, dry_hit, dry_he, pitch_verdict))

# arrangement MIDI harmony/grid audit (self-check)
arr_audit = audit(arr_mid)
print("arrangement MIDI audit:", arr_audit)

# =========================================================================
# 8. Artifacts
# =========================================================================
(ANALYSIS / "render_stats.json").write_text(json.dumps({
    "lufs": meas_lufs, "peak": peak_val, "silence_pct": silence_pct,
    "rms": rms, "rms_per_sec": rms_map,
    "wet_hit_rate": wet_hit, "wet_mean_harmonic_energy": wet_he,
    "dry_hit_rate": dry_hit, "dry_mean_harmonic_energy": dry_he,
    "valid_windows": wet_valid, "pitch_verdict": pitch_verdict,
    "arrangement_audit": arr_audit,
    "n_events": len(events),
    "n_per_track": {k: len(v) for k, v in sorted(by_track.items())},
    "target_lufs": TARGET_LUFS, "bpm": BPM,
    "n_stems": len(stems) if isinstance(stems, dict) else 0,
}, indent=2))

provenance = {
    "job": "random-style production (SP) layer-aligned",
    "date": "2026-10-31",
    "seed": SEED,
    "method": "SP-115",
    "method_module": "sound.generators.chord_arranger",
    "method_desc": "Chord-Driven 3-Track Generative Arranger "
                   "(Midicake UNA-style)",
    "layer": "ABSOLUTE - whole production layer replaced by a chord-driven "
             "3-track generative arrangement (chord pad + arp melody + bass) "
             "fed by the source's F-major harmony",
    "params": {
        "sample_rate": SR, "bpm": BPM, "ppqn": TPB,
        "meter": "4/4", "bar_ticks": BAR, "n_bars": N_BARS,
        "macros": MACROS,
        "programs": {k: v[1] for k, v in TRACK_PROGRAMS.items()},
        "channels": {k: v[0] for k, v in TRACK_PROGRAMS.items()},
        "chord_plan_degrees": DEGREE_LABELS,
        "chord_plan": [{"root": r, "quality": q} for r, q in CHORD_PLAN],
        "target_lufs": TARGET_LUFS, "ceiling_db": CEILING_DB,
    },
    "source_midi": str(SRC_PERFECT),
    "source_humanized_midi": str(SRC_HUMANIZED),
    "arrangement_midi": str(arr_mid),
    "source_bpm": BPM,
    "source_key": "F major",
    "source_pitch_classes": sorted(FMAJ_PCS),
    "output_wav": str(final_wav),
    "output_ogg": str(final_ogg),
    "dry_reference_wav": str(dry_wav),
    "lufs": meas_lufs, "peak": peak_val, "silence_pct": silence_pct, "rms": rms,
    "pitch_verdict": pitch_verdict,
    "wet_hit_rate": wet_hit, "wet_he": wet_he,
    "dry_hit_rate": dry_hit, "dry_he": dry_he,
    "preflight_humanized": before_h,
    "preflight_perfect": before,
    "arrangement_audit": arr_audit,
}
(OUT / "provenance.json").write_text(json.dumps(provenance, indent=2))

print("DONE")
