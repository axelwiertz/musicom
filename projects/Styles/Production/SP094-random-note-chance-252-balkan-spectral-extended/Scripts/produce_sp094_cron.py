# -*- coding: utf-8 -*-
"""SP-094 Random Note Generator + Note Chance Sequencer production pass (absolute layer).

Source : Styles/Balkan/252-balkan-spectral-extended/MIDI/252-balkan-spectral-extended-perfect.mid
         (G Dorian dajcovo 7/8, 132 BPM, 480 TPB, 32 bars = 53760 ticks,
          4 voices: double bass 43 / accordion 21 / clarinet 71 / violin 40;
          grid-locked "perfect" variant = compositional truth).

Method : SP-094 -> sound.generators.random_note_gen (RandomNoteGenerator +
         NoteChanceSequencer, Maschine 3.7 Random Note Gen / Note Event
         Chance-style). ABSOLUTE layer: the whole 4-voice texture is re-voiced
         by the random-note-chance engine. Phase 1 = RandomNoteGenerator fills
         each voice's grid "from nothing" (density/odds + G-Dorian scale pool +
         register); NoteChanceSequencer assigns per-note chance, locks the
         strong 7/8 metrical positions, and re-rolls a "breathing" realisation.
         Phase 2 (musicom rules) = per-bar chord-tone quantisation (G Dorian
         triads), 16th/8th grid snap, zero-drift pad. Rendered through a
         FluidSynth carrier (SP-001) and mastered.

Pipeline: source MIDI -> 3-rule audit (grid/harmony/zero-drift)
          -> per-voice random-note-chance generation (4 voices)
          -> generated groove MIDI -> FluidSynth raw WAV + dry reference + stems
          -> master() (folk -16 LUFS, -1 dBTP) -> WAV + Opus OGG
          -> pitch/grid/harmony/silence verification -> REPORT.md.
"""
import json
import os
import random as _random
import shutil
import subprocess
from pathlib import Path

import numpy as np
import mido

from sound.generators.random_note_gen import RandomNoteGenerator, NoteChanceSequencer
from sound.render.fluidsynth import discover_soundfont
from sound.effects.mastering import master, target_for_style, measure_lufs
from sound.utils.io import read_wav, write_wav

SRC = Path("/opt/data/repos/musicom/projects/Styles/Balkan/"
           "252-balkan-spectral-extended/MIDI/252-balkan-spectral-extended-perfect.mid")
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/"
           "SP094-random-note-chance-252-balkan-spectral-extended")
AUD = OUT / "Audio"
STEMS = AUD / "stems"
MIDIDIR = OUT / "MIDI"
ANALYSIS = OUT / "Analysis"
SCRIPTS = OUT / "Scripts"

for d in (AUD, STEMS, MIDIDIR, ANALYSIS, SCRIPTS):
    d.mkdir(parents=True, exist_ok=True)

# selection metadata (from the .selection_cron.json written by the selector)
_SEL = json.loads((OUT.parent / ".selection_cron.json").read_text())
POOL_SIZE = len(_SEL.get("pool_methods", []))
RECENT_EXCLUDED = ", ".join(sorted(_SEL.get("recent_excluded", [])))


SR = 44100
BPM = 132.0
TPB = 480
BAR = 1680                         # 7/8 bar = 7 eighths * 240 = 1680 ticks
N_BARS = 32
TOTAL_TICKS = BAR * N_BARS         # 53760
GRID = 120                         # 16th-note
SEED = 20261026
STYLE = "folk"

# G Dorian pitch classes: G A Bb C D E F
GDOR_PCS = {7, 9, 10, 0, 2, 4, 5}

# G Dorian diatonic triads: degree -> (root_pc, third_pc, fifth_pc)
TRIADS = {
    "i":   (7, 10, 2),   # G  Bb D   (minor)
    "ii":  (9, 0, 4),    # A  C  E   (minor)
    "III": (10, 2, 5),   # Bb D  F   (major)
    "IV":  (0, 4, 7),    # C  E  G   (major)
    "v":   (2, 5, 9),    # D  F  A   (minor)
    "VII": (5, 9, 0),    # F  A  C   (major)
}

# 32-bar G Dorian progression (from source rework REPORT.md), 8 sections x 4 bars
PROG_DEG = ["i", "i", "VII", "VII", "i", "VII", "IV", "i",
            "IV", "ii", "VII", "v", "III", "VII", "IV", "i",
            "v", "IV", "ii", "VII", "VII", "IV", "ii", "v",
            "IV", "VII", "i", "IV", "i", "VII", "IV", "i"]
assert len(PROG_DEG) == N_BARS

# 4 voices mirroring the source's instrumentation; chord = triad indices used
# (0=root,1=third,2=fifth).  scale="minor" root=50 == D natural minor == the
# G Dorian pitch-class set {7,9,10,0,2,4,5} (both are modes of F major), so the
# generator's built-in scale quantisation stays in-key for G Dorian.
VOICES = {
    "Bass":      dict(density=0.80, step=240, chance=0.92, register=(43, 55),
                      program=43, channel=1, chord=(0, 2), dur=320,
                      sequential=False, vel=(80, 112)),
    "Accordion": dict(density=0.45, step=120, chance=0.80, register=(55, 67),
                      program=21, channel=2, chord=(0, 1, 2), dur=200,
                      sequential=False, vel=(72, 104)),
    "Clarinet":  dict(density=0.38, step=120, chance=0.72, register=(67, 86),
                      program=71, channel=3, chord=(0, 1, 2), dur=180,
                      sequential=True, vel=(88, 118)),
    "Violin":    dict(density=0.28, step=120, chance=0.62, register=(79, 91),
                      program=40, channel=4, chord=(0, 1, 2), dur=120,
                      sequential=True, vel=(64, 96)),
}

FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"


def nearest_pc(pitch, pc):
    n = pitch - (pitch % 12) + pc
    return min((n - 12, n, n + 12), key=lambda c: abs(c - pitch))


def nearest_chord_tone(pitch, pcs):
    return min((nearest_pc(pitch, pc) for pc in pcs), key=lambda c: abs(c - pitch))


# ===========================================================================
# 1. Pre-flight 3-rule audit on the SOURCE (perfect MIDI)
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
                if pc not in GDOR_PCS:
                    out_scale += 1
                bar = min(t // BAR, N_BARS - 1)
                r, rd, f = TRIADS[PROG_DEG[bar]]
                if pc not in {r, rd, f}:
                    out_chord += 1
        if n_notes:
            track_ends.append(t)
    zero_drift = len(set(track_ends)) == 1
    return {"grid_off": grid_off, "off8": off8, "out_scale": out_scale,
            "out_chord": out_chord, "zero_drift": zero_drift,
            "track_ends": sorted(set(track_ends)), "total_notes": total_notes}


shutil.copy2(str(SRC), str(MIDIDIR / "source_original.mid"))
before = audit(SRC)
print("PREFLIGHT source (perfect):", before)
assert before["grid_off"] == 0, "grid sync FAIL on source"
assert before["out_scale"] == 0, "out-of-scale FAIL on source"
assert before["out_chord"] == 0, "out-of-chord FAIL on source"
assert before["zero_drift"], "zero-drift FAIL on source"
print("PREFLIGHT PASS: all three rules clean on source.")

# ===========================================================================
# 2. SP-094 random-note-chance generative pass (absolute layer)
# ===========================================================================
groove_events = {v: [] for v in VOICES}   # voice -> list[(pitch, vel, start, end)]
n_dropped = {}

for vname, cfg in VOICES.items():
    step = cfg["step"]
    nsteps = TOTAL_TICKS // step
    rng = RandomNoteGenerator(
        density=cfg["density"], pitch_range=cfg["register"],
        scale="minor", root=50, velocity_range=cfg["vel"],
        max_octave_jump=2,
        seed=SEED * 101 + list(VOICES).index(vname),
    )
    raw = rng.generate(num_steps=nsteps, time_per_step=step,
                       sequential=cfg["sequential"])
    n_raw = len(raw)

    # Phase 2: per-bar chord-tone quantisation (musicom rules)
    for ev in raw:
        bar = min(ev["start"] // BAR, N_BARS - 1)
        r, rd, f = TRIADS[PROG_DEG[bar]]
        pcs = [(r, rd, f)[i] for i in cfg["chord"]]
        ev["pitch"] = nearest_chord_tone(ev["pitch"], pcs)
        ev["duration"] = cfg["dur"]

    # NoteChanceSequencer: per-note chance + lock strong 7/8 positions + re-roll
    ncs = NoteChanceSequencer(events=raw, default_chance=cfg["chance"])
    ncs._rng = _random.Random(SEED * 31 + list(VOICES).index(vname))
    for idx, ev in enumerate(raw):
        pos = ev["start"] % BAR
        strong = (pos == 0)                     # bar downbeat
        if vname == "Bass":
            strong = pos in (0, 480, 960)       # dajcovo 2+2+3 accents
        if strong:
            ncs.lock_note(idx)

    active = ncs.reroll()
    n_dropped[vname] = n_raw - len(active)

    for ev in active:
        start = ev["start"]
        bar = min(start // BAR, N_BARS - 1)
        end = min((bar + 1) * BAR, start + ev["duration"])
        groove_events[vname].append((ev["pitch"], int(ev["velocity"]), start, end))

total_gen = sum(len(v) for v in groove_events.values())
print("SP-094 generated events:", {v: len(groove_events[v]) for v in groove_events})
print("dropped by chance re-roll:", n_dropped)
gen_pcs = sorted({p % 12 for v in groove_events.values() for (p, _, _, _) in v})
print("generated pitch classes:", gen_pcs)
assert set(gen_pcs) <= GDOR_PCS, "generated notes out of G Dorian"

# ===========================================================================
# 3. Write random-note-chance groove MIDI (mido) — zero-drift padded
# ===========================================================================
def build_track(pc_program, channel, events):
    tr = mido.MidiTrack()
    tr.append(mido.Message("program_change", program=pc_program,
                           channel=channel, time=0))
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
            tr.append(mido.Message("note_on", note=pitch, velocity=vel,
                                   channel=channel, time=dt))
        else:
            tr.append(mido.Message("note_off", note=pitch, velocity=0,
                                   channel=channel, time=dt))
    if prev < TOTAL_TICKS:
        tr.append(mido.MetaMessage("end_of_track", time=TOTAL_TICKS - prev))
    else:
        tr.append(mido.MetaMessage("end_of_track", time=0))
    return tr


mid = mido.MidiFile(ticks_per_beat=TPB)
tr0 = mido.MidiTrack()
tr0.append(mido.MetaMessage("set_tempo", tempo=int(round(60000000 / BPM)), time=0))
tr0.append(mido.MetaMessage("time_signature", numerator=7, denominator=8, time=0))
tr0.append(mido.MetaMessage("end_of_track", time=TOTAL_TICKS))
mid.tracks.append(tr0)
for vname, cfg in VOICES.items():
    mid.tracks.append(build_track(cfg["program"], cfg["channel"],
                                  groove_events[vname]))
groove_midi = MIDIDIR / "SP094-random-note-chance.mid"
mid.save(str(groove_midi))
print("wrote", groove_midi, groove_midi.stat().st_size, "bytes")

out_audit = audit(groove_midi)
print("OUTPUT audit (random-note-chance groove):", out_audit)
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

raw_wav = OUT / "SP094_random_note_chance_raw.wav"
render(groove_midi, raw_wav)
print("SP-094 raw:", raw_wav.stat().st_size, "bytes")

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
TARGET_LUFS = target_for_style(STYLE)      # folk -> -16.0
CEILING_DB = -1.0

raw_tm, sr = read_wav(str(raw_wav))        # (N, 2) time-major float32
if raw_tm.ndim == 1:
    raw_tm = np.column_stack([raw_tm, raw_tm])
raw_tm = np.asarray(raw_tm, dtype=np.float32)
print("mastering (target %.1f LUFS, ceiling %.1f dBTP)..." % (TARGET_LUFS, CEILING_DB))
mastered_tm, rep = master(raw_tm, target_lufs=TARGET_LUFS, ceiling_db=CEILING_DB,
                          sample_rate=SR)
print("master report: LUFS %.2f, true peak %.2f dBTP"
      % (float(rep.get("integrated_lufs", 0)), float(rep.get("true_peak_db", 0))))

final_wav = OUT / "SP094-random-note-chance-252-balkan-spectral-extended.wav"
final_ogg = OUT / "SP094-random-note-chance-252-balkan-spectral-extended.ogg"
write_wav(str(final_wav), mastered_tm.astype(np.float32), SR, normalize=False)
r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(final_wav),
                    "-codec:a", "libopus", "-application", "voip", "-b:a", "48k",
                    str(final_ogg)], capture_output=True, text=True, timeout=180)
assert r.returncode == 0 and final_ogg.stat().st_size > 10000, "ogg encode failed: %s" % r.stderr[-300:]
print("final WAV:", final_wav.stat().st_size, "final OGG:", final_ogg.stat().st_size)

# ===========================================================================
# 6. Verification
# ===========================================================================
meas_lufs = float(measure_lufs(mastered_tm, sample_rate=SR))
peak_val = float(np.max(np.abs(mastered_tm)))
mono = 0.5 * (mastered_tm[:, 0] + mastered_tm[:, 1])
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
        seg = audio_tm[w * wl:(w + 1) * wl, 0]
        if audio_tm.shape[1] > 1:
            seg = 0.5 * (seg + audio_tm[w * wl:(w + 1) * wl, 1])
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


hit_rate, he_mean, valid = pitch_verify(mastered_tm, GDOR_PCS)
dry_tm, _ = read_wav(str(dry_wav))
if dry_tm.ndim == 1:
    dry_tm = np.column_stack([dry_tm, dry_tm])
dry_tm = np.asarray(dry_tm, dtype=np.float32)
dry_hit, dry_he, dry_valid = pitch_verify(dry_tm, GDOR_PCS)
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
    "n_dropped_by_chance": n_dropped,
    "generated_pitch_classes": gen_pcs,
    "n_stems": len(stems) if isinstance(stems, dict) else 0,
    "target_lufs": TARGET_LUFS,
}, indent=2))

provenance = {
    "job": "random-style production (SP) layer-aligned",
    "date": "2026-10-26",
    "seed": SEED,
    "method": "SP-094",
    "method_module": "sound.generators.random_note_gen",
    "method_desc": "Random Note Generator + Note Chance Sequencer (Maschine 3.7 Random Note Gen / Note Event Chance-style)",
    "layer": "ABSOLUTE",
    "params": {
        "sample_rate": SR, "bpm": BPM, "ppqn": TPB,
        "meter": "7/8", "bar_ticks": BAR, "n_bars": N_BARS,
        "voices": VOICES,
        "generator_scale_pool": "minor@D3 == G Dorian pitch-class set",
        "carrier": "FluidSynth SP-001 (FluidR3_GM, dry -R 0 -C 0 -g 1.2)",
        "target_lufs": TARGET_LUFS, "ceiling_db": CEILING_DB,
    },
    "source_midi": str(SRC),
    "groove_midi": str(groove_midi),
    "source_bpm": BPM,
    "source_key": "G Dorian",
    "source_pitch_classes": sorted(GDOR_PCS),
    "bar_degrees": PROG_DEG,
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
REPORT = """# SP-094 Random Note Generator + Note Chance Sequencer — production report

- **Date**: 2026-10-26
- **Job**: random-style production (SP), layer-aligned
- **Method**: SP-094 (`sound.generators.random_note_gen`) — Random Note Generator
  + Note Chance Sequencer (Maschine 3.7 Random Note Gen / Note Event
  Chance-style). Phase 1: `RandomNoteGenerator` fills each voice's grid "from
  nothing" from configurable odds (density), a scale-quantised pitch pool, and
  a velocity range. `NoteChanceSequencer` wraps that note stream, assigns a
  per-note chance, locks the strong metrical positions, and re-rolls a
  "breathing" realisation each loop. Phase 2 (musicom rules): per-bar G Dorian
  chord-tone quantisation, grid snap, zero-drift pad.
- **Layer**: ABSOLUTE (whole-piece texture re-voicing; note material re-generated
  as per-bar chord-tone random-note-chance texture).

## Selection
- **Registry source**: `workflows.musicom_workflow.SP_METHODS` (63 registered;
  {pool_size} in pool after excluding recent-7-day {recent_excluded} and
  baseline SP-001).
- **Source composition**: `Styles/Balkan/252-balkan-spectral-extended/MIDI/252-balkan-spectral-extended-perfect.mid`
  (G Dorian dajcovo 7/8, 132 BPM, 480 TPB, 32 bars = 53760 ticks, 4 voices —
  double bass 43 / accordion 21 / clarinet 71 / violin 40; grid-locked
  "perfect" variant used as the compositional truth).

## Pre-flight audit (3 rules) — PASS on source (no rework needed)
| rule | result |
|---|---|
| Grid sync (16th = 120 ticks) | **PASS** — off-grid = {grid_off} |
| Harmony (G Dorian scale + chord tones) | **PASS** — out-of-scale = {out_scale}, out-of-chord = {out_chord} |
| Zero-drift (equal track ends) | **PASS** — 4 note tracks, end = {track_end} ticks |

The source is grid-locked (0 off-grid; the 24 off-8th onsets are idiomatic
16th-note diminutions in the Dance section, still 16th-grid-locked), fully in
G Dorian and chord-tone clean against the 32-bar progression, and all 4 tracks
end at 53760 ticks — no rework, straight to the SP method.

## SP-094 absolute layer (random-note-chance texture)
Per-bar G Dorian triad (from the source `PROG_DEG` 32-bar progression) is
re-voiced as four random-note-chance voices, one per source instrument:

| Voice | program | register | density | step | chance | chord tones | lock |
|---|---|---|---|---|---|---|---|
| Bass | 43 Double Bass | 43-55 | 0.80 | 8th | 0.92 | root + fifth | dajcovo 2+2+3 accents |
| Accordion | 21 Accordion | 55-67 | 0.45 | 16th | 0.80 | root/3rd/5th | bar downbeat |
| Clarinet | 71 Clarinet | 67-86 | 0.38 | 16th | 0.72 | root/3rd/5th (sequential) | bar downbeat |
| Violin | 40 Violin | 79-91 | 0.28 | 16th | 0.62 | root/3rd/5th (sequential) | bar downbeat |

- **RandomNoteGenerator** scale pool: `scale="minor"` at root D3 == the
  D natural-minor pitch set `{{2,4,5,7,9,10,0}}` == the **G Dorian** pitch-class
  set (both are modes of F major), so the generator's built-in scale quantisation
  stays in-key for G Dorian. Every generated pitch is then snapped to the bar's
  chord tones (Phase 2).
- **NoteChanceSequencer**: default chance per voice above; the bass also locks
  the dajcovo 2+2+3 accents (8th positions 0/2/4 = ticks 0/480/960) so the 7/8
  lilt stays anchored while interior notes "breathe".
- **Chance re-roll dropped** {dropped} notes total (per-voice {dropped_map}).
- {n_gen} generated notes, pitch classes {gen_pcs} (all in G Dorian).
- Rendered through FluidSynth (FluidR3_GM) carrier at 44100 Hz, mastered to
  folk −16 LUFS target, −1 dBTP ceiling.

## Output audit (the generated groove, mirror of the 3 rules) — PASS
| rule | result |
|---|---|
| Grid sync (16th = 120 ticks) | **PASS** — off-grid = {o_grid} |
| Harmony (G Dorian) | **PASS** — out-of-scale = {o_scale}, out-of-chord = {o_chord} |
| Zero-drift (equal track ends) | **PASS** — 4 note tracks, end = {o_end} ticks |

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
- `MIDI/SP094-random-note-chance.mid` (generated random-note-chance groove)
- `Audio/stems/` ({n_stems} per-voice stems)
- `provenance.json`, `Analysis/render_stats.json`

## Notes
- SP-094's two headline tools are both exercised: (1) RandomNoteGenerator fills
  the grid "from nothing" from odds + scale + register (its `density`,
  `scale`, `pitch_range`, `velocity_range` params), and (2) NoteChanceSequencer
  applies per-note chance with lockable strong positions and a re-rolled
  "breathing" realisation. The absolute-layer application re-voices the Balkan
  source's 4-instrument texture with the same programs but note material
  regenerated through the chance engine, with Phase-2 chord-tone quantisation
  keeping the harmony exactly on the source's G Dorian progression.
""".format(
    pool_size=POOL_SIZE, recent_excluded=RECENT_EXCLUDED,
    grid_off=before["grid_off"], out_scale=before["out_scale"],
    out_chord=before["out_chord"], track_end=before["track_ends"][0],
    dropped=sum(n_dropped.values()),
    dropped_map={k: n_dropped[k] for k in n_dropped},
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
for s in ("select_job_20261026.py",):
    srcp = OUT.parent / s
    if srcp.exists():
        try:
            shutil.copy2(str(srcp), str(SCRIPTS / s))
        except shutil.SameFileError:
            pass
try:
    shutil.copy2(__file__, str(SCRIPTS / "produce_sp094_cron.py"))
except shutil.SameFileError:
    pass

print("Done.")
