# -*- coding: utf-8 -*-
"""SP-115 Chord-Driven 3-Track Generative Arranger production pass (2026-11-16).

Source : Styles/Cuban/001-cuban-trova-research — Cuban trova (Polo Montanez
         style) guitar melody, C major, 92 BPM, 4/4, 480 TPB, single nylon
         guitar (prog 24) monophonic seed, 96 notes, 27 bars = 51840 ticks
         ~ 70.4 s, 0% chromatic (pure C-major diatonic).

Method : SP-115 -> sound.generators.chord_arranger (Midicake UNA-style).
         SP-115 is a GENERATOR method: it produces note events, not a timbral
         effect. As an ABSOLUTE layer it re-composes the whole piece in the
         source's key (C major) and tempo (92 BPM) from a chord progression
         derived from the source melody's harmonic rhythm; no source MIDI
         notes survive (same convention as SP-098 / SP-100).

         ChordDrivenArranger emits 3 coordinated tracks per bar:
         chord/rhythm (block/strum/euclid/drone over chord tones), arpeggiated
         melody (up/down/updown/random + probability/trill/ratchet/octave),
         and harmony-following bass (root/fifth + Euclidean muting).

Pipeline: source MIDI -> 3-rule pre-flight audit (grid/harmony/zero-drift)
          -> derive 27-bar C-major trova progression from melody harmonic
          rhythm -> ChordDrivenArranger generation (3 voices) -> phase1 raw
          export (swing/ratchet off-grid character preserved) -> Phase-2
          grid quantize (snap onsets to 16th = 120 ticks) -> final MIDI
          (zero-drift validate()) -> FluidSynth GM dry render -> master()
          (target LUFS, -1 dBTP) -> WAV + Opus OGG -> pitch/silence/RMS
          verification -> stems -> provenance.json + REPORT.md.
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
from sound.render.pipeline import RenderPipeline
from sound.effects.mastering import master, target_for_style, measure_lufs
from sound.utils.io import read_wav, write_wav

from structures import MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.musicom_workflow import _unit_from_events

# ---- paths -------------------------------------------------------------
ROOT = Path("/opt/data/repos/musicom/projects/Styles")
OUT = ROOT / "Production" / "SP115-chord-arranger-001-cuban-trova"
SRC = ROOT / "Cuban/001-cuban-trova-research/MIDI/cuban_seed.mid"
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
SEED = 20261116
STYLE = "Cuban"            # -> target_for_style -> -14.0 fallback
TARGET_LUFS = target_for_style(STYLE)
CEILING_DB = -1.0
TOTAL_BARS = 27
TOTAL_TICKS = TOTAL_BARS * BAR   # 51840

# C major scale pcs (key of the source)
SCALE_PCS = {0, 2, 4, 5, 7, 9, 11}

FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"

# ---- source metadata ---------------------------------------------------
mf_src = mido.MidiFile(str(SRC))
bpm = 92.0
for tr in mf_src.tracks:
    for m in tr:
        if m.type == "set_tempo":
            bpm = round(60000000.0 / m.tempo, 2)
print("source BPM =", bpm, "| length_s =", round(mf_src.length, 2))

# =========================================================================
# 1. Pre-flight 3-rule audit on the SOURCE midi (informational)
# =========================================================================
def audit(path, scale_pcs, chord_tones_by_bar=None):
    mf = mido.MidiFile(str(path))
    grid_off = 0
    out_scale = 0
    out_chord = 0
    total_notes = 0
    track_ends = []
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
                pc = m.note % 12
                if pc not in scale_pcs:
                    out_scale += 1
                if chord_tones_by_bar is not None:
                    bar = min(t // BAR, len(chord_tones_by_bar) - 1)
                    if pc not in chord_tones_by_bar[bar]:
                        out_chord += 1
        if n_notes:
            track_ends.append(t)
    zero_drift = len(set(track_ends)) == 1
    return {"grid_off": grid_off, "out_scale": out_scale,
            "out_chord": out_chord, "total_notes": total_notes,
            "zero_drift": zero_drift, "track_ends": sorted(set(track_ends))}


src_audit = audit(SRC, SCALE_PCS)
print("== source pre-flight audit ==")
print(src_audit)

# =========================================================================
# 2. Derive the 27-bar trova chord progression (C major)
# =========================================================================
# One chord per bar following the seed melody's harmonic rhythm (downbeat +
# pitch content per bar). All chord tones lie in C major (trova son/trova/
# guajira: I-IV-V with vi/ii passing and V7 turnarounds).
CHORDS = [
    (60, "maj"),   #  0 C   (E downbeat)
    (60, "maj"),   #  1 C   (E downbeat)
    (55, "maj"),   #  2 G   (D melody -> G 5th)
    (53, "maj"),   #  3 F   (F downbeat)
    (55, "dom7"),  #  4 G7  (B downbeat -> G 3rd)
    (53, "maj"),   #  5 F   (F downbeat)
    (53, "maj"),   #  6 F   (F downbeat)
    (60, "maj"),   #  7 C   (E downbeat)
    (60, "maj"),   #  8 C   (E downbeat)
    (55, "dom7"),  #  9 G7  (G downbeat)
    (53, "maj"),   # 10 F   (A downbeat -> F 3rd)
    (55, "dom7"),  # 11 G7  (B melody -> G 3rd)
    (53, "maj"),   # 12 F   (F downbeat)
    (53, "maj"),   # 13 F   (A downbeat)
    (60, "maj"),   # 14 C   (C downbeat)
    (57, "min"),   # 15 Am  (A downbeat -> Am root)
    (60, "maj"),   # 16 C   (C downbeat)
    (57, "min"),   # 17 Am  (A downbeat)
    (50, "min"),   # 18 Dm  (D downbeat -> Dm root)
    (53, "maj"),   # 19 F   (F downbeat)
    (55, "dom7"),  # 20 G7  (D melody -> G 5th)
    (60, "maj"),   # 21 C   (C downbeat)
    (57, "min"),   # 22 Am  (E downbeat -> Am 5th)
    (60, "maj"),   # 23 C   (C downbeat)
    (53, "maj"),   # 24 F   (A downbeat -> F 3rd)
    (55, "dom7"),  # 25 G7  (B downbeat -> G 3rd)
    (60, "maj"),   # 26 C   (E downbeat)
]
assert len(CHORDS) == TOTAL_BARS

# chord-tone pcs per bar (for the harmony audit)
def chord_tone_pcs(root, quality):
    ivs = QUALITIES[quality]
    return {(root + iv) % 12 for iv in ivs}


CHORD_TONES = [chord_tone_pcs(r, q) for (r, q) in CHORDS]
# verify every chord tone is in C major
for bar, (r, q) in enumerate(CHORDS):
    assert CHORD_TONES[bar] <= SCALE_PCS, (bar, r, q, CHORD_TONES[bar])
print("chord progression: %d bars, all chord tones in C major" % TOTAL_BARS)

# =========================================================================
# 3. SP-115 generation (ChordDrivenArranger, ABSOLUTE layer)
# =========================================================================
MACROS = {
    "density": 0.60,      # moderate strum/pulse density
    "probability": 0.70,  # per-step chance for melody/bass
    "swing": 0.15,        # subtle Latin swing (off-grid -> phase-2 quantize)
    "accent": 0.50,       # mid accent
    "ratchet": 0.30,      # occasional 2..4 subdivisions
    "octave": 0.0,        # melody/bass stay in register
    "gate": 0.60,         # note length fraction
    "spread": 0.30,       # light chord voicing inversion
}

arr = ChordDrivenArranger(bpm=round(bpm), bars=TOTAL_BARS, seed=SEED)
raw_events = arr.generate(CHORDS, macros=MACROS)
print("raw events:", len(raw_events))
by_track = {}
for e in raw_events:
    by_track.setdefault(e["track"], []).append(e)
for t in ("chord", "melody", "bass"):
    print("  track %-6s n=%d pcs=%s" % (
        t, len(by_track[t]), sorted({e["pitch"] % 12 for e in by_track[t]})))

INSTRUMENTS = [
    ("Guitar", 24, 0),   # GM 24 Acoustic Guitar (nylon) — chord/strum
    ("Flute", 73, 1),    # GM 73 Flute — arpeggiated melody lead
    ("Bass", 32, 2),     # GM 32 Acoustic Bass — harmony-following bass
]
# instrument voice name -> arranger track label
TRACK_FOR_VOICE = {"Guitar": "chord", "Flute": "melody", "Bass": "bass"}


def ev_to_musicevent(e):
    start = int(e["start_tick"])
    dur = max(1, int(e["duration_ticks"]))
    end = min(start + dur, TOTAL_TICKS)
    return MusicEvent(pitch=int(e["pitch"]), volume=int(e["vel"]),
                      start_tick=start, end_tick=end)


def build_midi(track_events, out_path):
    """track_events: {track_name: [MusicEvent]} -> zero-drift MIDI."""
    comp = UnitMatrixComposer(bpm=round(bpm), ticks_per_beat=TPB, beats_per_bar=4)
    comp.create_matrix(num_voices=3, num_sections=1)
    for name, prog, ch in INSTRUMENTS:
        comp.add_voice(name, program=prog, channel=ch)
    comp.add_section("Piece", bars=TOTAL_BARS)
    for name, prog, ch in INSTRUMENTS:
        evs = sorted(track_events[TRACK_FOR_VOICE[name]],
                     key=lambda x: (x.start_tick, x.pitch))
        comp.fill_voice_section(name, "Piece", _unit_from_events(evs, TOTAL_TICKS))
    ok, msg = comp.validate()
    assert ok, "zero-drift FAIL: %s" % msg
    comp.to_midi(str(out_path))
    return comp


# ---- phase1: raw engine output (swing/ratchet off-grid character) ------
phase1_events = {
    "chord": [ev_to_musicevent(e) for e in by_track["chord"]],
    "melody": [ev_to_musicevent(e) for e in by_track["melody"]],
    "bass": [ev_to_musicevent(e) for e in by_track["bass"]],
}
build_midi(phase1_events, MIDIDIR / "001-cuban-trova-phase1.mid")
print("phase1 MIDI written")

# =========================================================================
# 4. Phase 2: grid quantize (snap onsets to 16th = 120 ticks)
# =========================================================================
def quantize_to_grid(events, grid=GRID, chord_tones_by_bar=None):
    out = []
    for e in events:
        start = int(round(e.start_tick / grid)) * grid
        start = max(0, min(start, TOTAL_TICKS - 1))
        dur = max(1, e.end_tick - e.start_tick)
        end = min(start + dur, TOTAL_TICKS)
        pitch = e.pitch
        if chord_tones_by_bar is not None:
            bar = min(start // BAR, TOTAL_BARS - 1)
            tones = chord_tones_by_bar[bar]
            pc = pitch % 12
            if pc not in tones:
                # pull to nearest chord tone (minimal |semitone| move, tie -> up)
                best = min(tones, key=lambda t: min((t - pc) % 12, (pc - t) % 12))
                up = (best - pc) % 12
                down = (pc - best) % 12
                delta = up if up <= down else -down
                pitch = pitch + delta
        out.append(MusicEvent(pitch=pitch, volume=e.volume,
                              start_tick=start, end_tick=end))
    return out


final_events = {t: quantize_to_grid(evs, GRID, CHORD_TONES)
                for t, evs in phase1_events.items()}
build_midi(final_events, MIDIDIR / "001-cuban-trova.mid")
print("final MIDI written")

# =========================================================================
# 5. Re-audit (3-rule gate on generated MIDI — MUST be clean)
# =========================================================================
phase1_audit = audit(MIDIDIR / "001-cuban-trova-phase1.mid", SCALE_PCS,
                     CHORD_TONES)
final_audit = audit(MIDIDIR / "001-cuban-trova.mid", SCALE_PCS, CHORD_TONES)
print("== phase1 audit ==")
print(phase1_audit)
print("== final audit ==")
print(final_audit)
assert final_audit["grid_off"] == 0, "grid sync FAIL"
assert final_audit["out_scale"] == 0, "out-of-scale FAIL"
assert final_audit["out_chord"] == 0, "out-of-chord FAIL"
assert final_audit["zero_drift"], "zero-drift FAIL"
print("RE-AUDIT PASS (grid 0 / out-of-scale 0 / out-of-chord 0 / zero-drift)")

# =========================================================================
# 6. FluidSynth dry render (SP-001 carrier)
# =========================================================================
SF = discover_soundfont()
assert SF and os.path.exists(SF), "SoundFont missing: %r" % SF
print("SoundFont:", SF)

final_midi = MIDIDIR / "001-cuban-trova.mid"
dry_wav = AUD / "dry_full_mix_sp001_reference.wav"


def fluidsynth_render(midi_path, out_wav):
    r = subprocess.run([FLUID, "-ni", "-R", "0", "-C", "0", "-g", "1.2",
                        "-F", str(out_wav), SF, str(midi_path)],
                       capture_output=True, text=True, timeout=900)
    if r.returncode != 0 or not out_wav.exists() or out_wav.stat().st_size < 1000:
        raise RuntimeError("FluidSynth render failed: %s" % r.stderr[-500:])
    return out_wav


fluidsynth_render(final_midi, dry_wav)
print("dry WAV:", dry_wav.stat().st_size, "bytes")

dry_audio, _sr = read_wav(str(dry_wav))
if dry_audio.ndim == 1:
    dry_audio = np.column_stack([dry_audio, dry_audio])
dry_audio = np.asarray(dry_audio, dtype=np.float32)
assert _sr == SR, "unexpected sample rate %r" % _sr
print("dry audio shape:", dry_audio.shape,
      "peak", float(np.max(np.abs(dry_audio))))

# =========================================================================
# 7. Master (target LUFS, ceiling -1 dBTP)
# =========================================================================
print("mastering (target %.1f LUFS, ceiling %.1f dBTP)..."
      % (TARGET_LUFS, CEILING_DB))
mastered, rep = master(dry_audio, target_lufs=TARGET_LUFS, ceiling_db=CEILING_DB,
                       sample_rate=SR)
print("master report: LUFS %.2f, true peak %.2f dBTP"
      % (float(rep.get("integrated_lufs", 0)), float(rep.get("true_peak_db", 0))))

final_wav = AUD / "SP115-chord-arranger-001-cuban-trova.wav"
final_ogg = AUD / "SP115-chord-arranger-001-cuban-trova.ogg"
write_wav(str(final_wav), mastered.astype(np.float32), SR, normalize=False)
r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(final_wav),
                    "-codec:a", "libopus", "-application", "voip", "-b:a", "48k",
                    str(final_ogg)], capture_output=True, text=True, timeout=180)
assert r.returncode == 0 and final_ogg.stat().st_size > 10000, \
    "ogg encode failed: %s" % r.stderr[-300:]
print("final WAV:", final_wav.stat().st_size,
      "final OGG:", final_ogg.stat().st_size)

# =========================================================================
# 8. Verification
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


final_hit, final_he, final_valid = pitch_verify(mastered, SCALE_PCS)
dry_hit, dry_he, dry_valid = pitch_verify(dry_audio, SCALE_PCS)
he_retention = final_he / dry_he if dry_he > 0 else 0.0
pitch_verdict = "PASS" if (final_hit >= 0.60 and final_he >= 0.30) else "FAIL"
print("pitch verify: final hit=%.4f HE=%.4f | dry hit=%.4f HE=%.4f | "
      "HE retention=%.3f -> %s"
      % (final_hit, final_he, dry_hit, dry_he, he_retention, pitch_verdict))

# =========================================================================
# 9. Stems (per-track WAV)
# =========================================================================
try:
    pipeline = RenderPipeline(soundfont_path=SF, fluidsynth_bin=FLUID,
                              sample_rate=SR)
    stems = pipeline.render_stems(str(final_midi), str(STEMS), format="wav")
    print("stems:", list(stems))
    stems_ok = True
except Exception as exc:
    print("stems FAILED:", exc)
    stems = {}
    stems_ok = False

# =========================================================================
# 10. Artifacts
# =========================================================================
(ANALYSIS / "render_stats.json").write_text(json.dumps({
    "lufs": meas_lufs, "peak": peak_val, "silence_pct": silence_pct,
    "rms": rms, "rms_per_sec": rms_map,
    "final_hit_rate": final_hit, "final_mean_harmonic_energy": final_he,
    "dry_hit_rate": dry_hit, "dry_mean_harmonic_energy": dry_he,
    "he_retention": he_retention,
    "valid_windows": final_valid, "pitch_verdict": pitch_verdict,
    "target_lufs": TARGET_LUFS, "bpm": bpm,
    "stems_ok": stems_ok, "n_stems": len(stems),
    "macros": MACROS,
}, indent=2))

provenance = {
    "job": "random-style production (SP) layer-aligned",
    "date": "2026-11-16",
    "seed": SEED,
    "method": "SP-115",
    "method_module": "sound.generators.chord_arranger",
    "method_desc": "Chord-Driven 3-Track Generative Arranger — input chords -> "
                   "chord/rhythm + arpeggiated melody + harmony-following bass "
                   "tracks; ratchets/trills/swing/probability/accents/Euclidean "
                   "muting; 8-macro + 16-step-lane modulation bus (Midicake "
                   "UNA-style)",
    "layer": "ABSOLUTE - generator re-composes the whole piece in the source's "
             "key/tempo; ChordDrivenArranger drives 3 voices from a derived "
             "27-bar C-major trova progression",
    "macros": MACROS,
    "chords": [list(c) for c in CHORDS],
    "target_lufs": TARGET_LUFS, "ceiling_db": CEILING_DB,
    "source_midi": str(SRC),
    "source_bpm": bpm,
    "source_key": "C major",
    "source_pitch_classes": sorted(SCALE_PCS),
    "source_form": "27 bars (single nylon-guitar trova melody, 96 notes)",
    "output_midi": str(final_midi),
    "phase1_midi": str(MIDIDIR / "001-cuban-trova-phase1.mid"),
    "output_wav": str(final_wav),
    "output_ogg": str(final_ogg),
    "dry_reference_wav": str(dry_wav),
    "lufs": meas_lufs, "peak": peak_val, "silence_pct": silence_pct, "rms": rms,
    "pitch_verdict": pitch_verdict,
    "final_hit_rate": final_hit, "final_he": final_he,
    "dry_hit_rate": dry_hit, "dry_he": dry_he, "he_retention": he_retention,
    "source_preflight": src_audit,
    "phase1_audit": phase1_audit,
    "final_audit": final_audit,
    "stems_ok": stems_ok, "n_stems": len(stems),
    "instruments": INSTRUMENTS,
}
(OUT / "provenance.json").write_text(json.dumps(provenance, indent=2))

shutil.copy(__file__, SCRIPTS / "produce_sp115_cron.py")

print("DONE")
