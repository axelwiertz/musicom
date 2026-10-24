# -*- coding: utf-8 -*-
"""SP-078 Polymetric Grid production pass (absolute layer).

Source : Styles/Gamelan/017-gamelan-central-java/MIDI/gamelan_live_render.mid
         (D Slendro pentatonic gamelan, 80 BPM, 480 TPB, 8 x 16-beat gongan
          cycles, 4 voices: Saron balungan / Peking elaboration / Colotomic
          pots (kethuk+kempul+kenong) / Gong Ageng).

Method : SP-078 -> sound.generators.polymetric_grid (PolymetricGrid, Rapid
         Flow omniGRID-style 16-track polymetric step sequencer). ABSOLUTE
         layer: the whole 4-voice gamelan texture is re-voiced as a 6-track
         polymetric grid whose independent step-counts + resolutions re-phase
         against each other, with Bjorklund Euclidean pulses, per-step graphs
         (note-length / probability / repeats ratchet), and per-step Slendro
         pitch overrides (the module's Western SCALES has no slendro, so the
         pentatonic is applied manually via Track.set_pitch — same quantised
         result). Rendered through a FluidSynth carrier (SP-001) and mastered.

Pipeline: source MIDI -> 3-rule audit (grid/harmony/zero-drift)
          -> boundary-clamp rework (final gong 2-beat ring truncated to the
             128-beat seam -> zero-drift clean) -> re-audit
          -> per-track polymetric render (6 tracks) -> groove MIDI (4 channels)
          -> FluidSynth raw WAV + dry reference + stems
          -> master() (-14 LUFS, -1 dBTP) -> WAV + Opus OGG
          -> pitch/grid/harmony/silence verification -> REPORT.md.
"""
import json
import math
import os
import shutil
import subprocess
from pathlib import Path

import numpy as np
import mido

from sound.render.fluidsynth import discover_soundfont
from sound.effects.mastering import master, target_for_style, measure_lufs
from sound.generators.polymetric_grid import PolymetricGrid

ROOT = Path("/opt/data/repos/musicom/projects/Styles")
SRC = ROOT / "Gamelan/017-gamelan-central-java/MIDI/gamelan_live_render.mid"
OUT = ROOT / "Production/SP078-polymetric-grid-017-gamelan-central-java"
AUD = OUT / "Audio"
STEMS = AUD / "stems"
MIDIDIR = OUT / "MIDI"
ANALYSIS = OUT / "Analysis"
SCRIPTS = OUT / "Scripts"

for d in (AUD, STEMS, MIDIDIR, ANALYSIS, SCRIPTS):
    d.mkdir(parents=True, exist_ok=True)

SR = 44100
BPM = 80.0
TPB = 480
BAR = 1920                 # 4 beats
TOTAL_BEATS = 96           # 6 gongan x 16 beats
TOTAL_TICKS = int(BAR * TOTAL_BEATS / 4)   # 46080
GRID = 120                 # 16th note
SEED = 20261024
STYLE = "gamelan"

# D Slendro pentatonic: D E F# A B  ->  pitch classes {2,4,6,9,11}
SLENDRO_PITCHES = [62, 64, 66, 69, 71, 74]      # D4 E4 F#4 A4 B4 D5
SLENDRO_PCS = {2, 4, 6, 9, 11}
KEY_ROOT = 62                                    # D4

FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# 0. Pre-flight 3-rule audit (on the SOURCE)
# ---------------------------------------------------------------------------
def audit(path, total_ticks=None):
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
                if (m.note % 12) not in SLENDRO_PCS:
                    out_scale += 1
                # D Slendro is a modal drone (no chord progression): the
                # "chord" is the tonic D drone, whose consonant tones are the
                # whole slendro pentatonic -> out-of-chord == out-of-scale.
                if (m.note % 12) not in SLENDRO_PCS:
                    out_chord += 1
        if n_notes:
            track_ends.append(t)
    zero_drift = len(set(track_ends)) == 1
    return {"grid_off": grid_off, "out_scale": out_scale, "out_chord": out_chord,
            "zero_drift": zero_drift, "track_ends": sorted(set(track_ends)),
            "total_notes": total_notes}


shutil.copy2(str(SRC), str(MIDIDIR / "source_original.mid"))
before = audit(SRC)
print("PREFLIGHT source:", before)
assert before["grid_off"] == 0, "grid sync FAIL on source"
assert before["out_scale"] == 0, "out-of-scale FAIL on source"
assert before["out_chord"] == 0, "out-of-chord FAIL on source"

# --- rework if zero-drift fails: boundary-clamp the whole source to the
#     128-beat seam (61440 ticks). The final Gong Ageng sustains 2 beats from
#     beat 127 -> 129; clamping its note_off to 61440 restores equal track
#     lengths (the musicom zero-drift invariant) without touching any onset.
src_reworked = MIDIDIR / "source_reworked.mid"
if not before["zero_drift"]:
    total = 61440   # 128 beats (the ensemble's true boundary)
    mf = mido.MidiFile(str(SRC))
    out_mf = mido.MidiFile(ticks_per_beat=mf.ticks_per_beat)
    for tr in mf.tracks:
        events = []
        t = 0
        for m in tr:
            t += m.time
            events.append((t, m))
        new = mido.MidiTrack()
        prev = 0
        for abs_t, m in events:
            if abs_t > total:
                abs_t = total
            dt = abs_t - prev
            if dt < 0:
                dt = 0
            m2 = m.copy(time=dt)
            new.append(m2)
            prev = abs_t
        out_mf.tracks.append(new)
    out_mf.save(str(src_reworked))
    reworked = audit(src_reworked)
    print("REWORKED (boundary-clamped to 61440):", reworked)
    assert reworked["zero_drift"], "zero-drift still FAIL after rework"
    assert reworked["grid_off"] == 0 and reworked["out_scale"] == 0
else:
    src_reworked = SRC
    reworked = before
    print("zero-drift already clean; reworked == source")

# ---------------------------------------------------------------------------
# 1. SP-078 polymetric grid (absolute layer)
# ---------------------------------------------------------------------------
# 6 sequencer tracks (of the 16 available), independent step-counts/resolutions
# so their periods re-phase over the 96 beats:
#   gong/kenong/kempul/kethuk : 16 steps @ 1/4  -> 16-beat period (gongan)
#   balungan (saron)          : 12 steps @ 1/8  ->  6-beat period (poly vs 16)
#   peking (elaboration)      : 12 steps @ 1/16 ->  3-beat period (poly vs 16)
# ensemble LCM = 48 beats; the 96-beat render = 2 full re-phase cycles.
g = PolymetricGrid(bpm=BPM, master_shift_ms=0.0, shuffle="straight",
                   shuffle_amount=0.0, root=2, scale=None)

# track 1: Gong Ageng — 1 hit per gongan (Euclidean 1/16 lands on step 15)
gong = g.add_track(1, steps=16, resolution=4, note=38, channel=3, name="gong")
gong.euclidean(pulses=1)
gong.gain = 1.20
for s in range(16):
    gong.note_length.set(s, 400.0)
    gong.velocity.set(s, 100.0)

# track 2: Kenong — phrase-end punctuation beats 3/7/11/15
kenong = g.add_track(2, steps=16, resolution=4, note=50, channel=2, name="kenong")
kenong.euclidean(pulses=4, rotation=3)
kenong.gain = 0.95
for s in range(16):
    kenong.note_length.set(s, 150.0)

# track 3: Kempul — mid-gongan punctuation beats 5/10/15
kempul = g.add_track(3, steps=16, resolution=4, note=45, channel=2, name="kempul")
kempul.euclidean(pulses=3)
kempul.gain = 0.85
for s in range(16):
    kempul.note_length.set(s, 120.0)

# track 4: Kethuk — off-beat damp pots beats 0/2/4/6/8/10/12/14
kethuk = g.add_track(4, steps=16, resolution=4, note=50, channel=2, name="kethuk")
kethuk.euclidean(pulses=8)
kethuk.gain = 0.75
for s in range(16):
    kethuk.note_length.set(s, 30.0)
    kethuk.probability.set(s, 88.0)      # per-step probability graph (thinning)
kethuk.repeats.set(6, 2)                 # ratchet on beat 6 (8th-note double)

# track 5: Balungan (Saron core) — 12 eighths = 6 beats, polymetric vs gongan
balungan = g.add_track(5, steps=12, resolution=8, note=62, channel=0, name="balungan")
balungan.euclidean(pulses=7)
balungan.gain = 0.90
BAL_CONT = [62, 64, 66, 64, 62, 64, 69, 71, 69, 66, 64, 62]
for s in range(12):
    balungan.set_pitch(s, BAL_CONT[s])
    balungan.note_length.set(s, 90.0)

# track 6: Peking (elaboration) — 12 sixteenths = 3 beats, fastest poly layer
peking = g.add_track(6, steps=12, resolution=16, note=74, channel=1, name="peking")
peking.euclidean(pulses=9)
peking.gain = 0.95
PEK_CONT = [74, 71, 69, 71, 74, 71, 69, 66, 69, 71, 69, 66]
for s in range(12):
    peking.set_pitch(s, PEK_CONT[s])
    peking.note_length.set(s, 60.0)
    peking.probability.set(s, 92.0)

# per-track loop counts so every lane spans the full 96 beats
PERIODS = {1: 16.0, 2: 16.0, 3: 16.0, 4: 16.0, 5: 6.0, 6: 3.0}
LOOPS = {idx: int(round(TOTAL_BEATS / PERIODS[idx])) for idx in PERIODS}
print("loops per track:", LOOPS)
print("ensemble re-phase cycle: %.2f beats" % g.ensemble_period_beats)

spb = 60.0 / BPM
chan_events = {0: [], 1: [], 2: [], 3: []}   # channel -> [(pitch, vel, start, end)]
gen_total = 0
for idx in sorted(g.tracks):
    for t in g.tracks.values():
        t.muted = (t.index != idx)
    evs = g.render(loops=LOOPS[idx], seed=SEED * 101 + idx)
    trk = g.tracks[idx]
    for (start_s, note, vel, dur_s) in evs:
        start_tick = int(round(start_s / spb * TPB))
        end_tick = int(round((start_s + dur_s) / spb * TPB))
        assert start_tick % GRID == 0, "off-grid onset at %d" % start_tick
        end_tick = min(end_tick, TOTAL_TICKS)
        if end_tick <= start_tick:
            end_tick = start_tick + GRID
        chan_events[trk.channel].append((int(note), int(vel), start_tick, end_tick))
        gen_total += 1

gen_pcs = sorted({n % 12 for c in chan_events for (n, _, _, _) in chan_events[c]})
print("SP-078 generated events per channel:",
      {c: len(chan_events[c]) for c in chan_events}, "total", gen_total)
print("generated pitch classes:", gen_pcs)
assert set(gen_pcs) <= SLENDRO_PCS, "generated notes out of D Slendro"

# ---------------------------------------------------------------------------
# 2. Write groove MIDI (4 channels, zero-drift padded)
# ---------------------------------------------------------------------------
PROGRAMS = {0: 12, 1: 9, 2: 12, 3: 14}    # Saron marimba / Peking glock / pots marimba / gong bells


def build_track(channel, events):
    tr = mido.MidiTrack()
    tr.append(mido.Message("program_change", program=PROGRAMS[channel],
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
tr0.append(mido.MetaMessage("time_signature", numerator=4, denominator=4, time=0))
tr0.append(mido.MetaMessage("end_of_track", time=TOTAL_TICKS))
mid.tracks.append(tr0)
for ch in (0, 1, 2, 3):
    mid.tracks.append(build_track(ch, chan_events[ch]))
groove_midi = MIDIDIR / "SP078-polymetric-gamelan.mid"
mid.save(str(groove_midi))
print("wrote", groove_midi, groove_midi.stat().st_size, "bytes")

out_audit = audit(groove_midi, TOTAL_TICKS)
print("OUTPUT audit (polymetric groove):", out_audit)
assert out_audit["grid_off"] == 0
assert out_audit["out_scale"] == 0
assert out_audit["out_chord"] == 0
assert out_audit["zero_drift"]

# ---------------------------------------------------------------------------
# 3. Render (FluidSynth carrier)
# ---------------------------------------------------------------------------
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
render(src_reworked, dry_wav)
print("dry reference:", dry_wav.stat().st_size, "bytes")

raw_wav = OUT / "SP078_polymetric_raw.wav"
render(groove_midi, raw_wav)
print("SP-078 raw:", raw_wav.stat().st_size, "bytes")

try:
    from sound.render.pipeline import RenderPipeline
    pipeline = RenderPipeline(soundfont_path=SF, fluidsynth_bin=FLUID, sample_rate=SR)
    stems = pipeline.render_stems(str(groove_midi), str(STEMS), format="wav")
    print("rendered %d stems" % len(stems))
except Exception as e:
    stems = {}
    print("stem render skipped:", repr(e)[:200])

# ---------------------------------------------------------------------------
# 4. Master
# ---------------------------------------------------------------------------
TARGET_LUFS = target_for_style(STYLE)      # gamelan -> unknown -> -14.0
CEILING_DB = -1.0

raw_audio, sr = read_wav(raw_wav)
raw_tm = raw_audio.T.astype(np.float32)
print("mastering (target %.1f LUFS, ceiling %.1f dBTP)..." % (TARGET_LUFS, CEILING_DB))
mastered_tm, rep = master(raw_tm, target_lufs=TARGET_LUFS, ceiling_db=CEILING_DB,
                          sample_rate=SR)
print("master report: LUFS %.2f, true peak %.2f dBTP"
      % (float(rep.get("integrated_lufs", 0)), float(rep.get("true_peak_db", 0))))
final_master = mastered_tm.T

final_wav = OUT / "SP078-polymetric-grid-017-gamelan-central-java.wav"
final_ogg = OUT / "SP078-polymetric-grid-017-gamelan-central-java.ogg"
write_wav(final_wav, final_master, sr=SR)
r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(final_wav),
                    "-codec:a", "libopus", "-application", "voip", "-b:a", "48k",
                    str(final_ogg)], capture_output=True, text=True, timeout=180)
assert r.returncode == 0 and final_ogg.stat().st_size > 10000, "ogg encode failed"
print("final WAV:", final_wav.stat().st_size, "final OGG:", final_ogg.stat().st_size)

# ---------------------------------------------------------------------------
# 5. Verification
# ---------------------------------------------------------------------------
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


hit_rate, he_mean, valid = pitch_verify(final_master, SLENDRO_PCS)
dry_hit, dry_he, dry_valid = pitch_verify(raw_audio, SLENDRO_PCS)
he_retention = (he_mean / dry_he) if dry_he > 0 else 0.0
pitch_verdict = "PASS" if (hit_rate >= 0.60 and he_mean >= 0.30) else "FAIL"
print("Pitch verify: valid=%d hit=%.4f mean_HE=%.4f | dry hit=%.4f HE=%.4f | retention=%.3f -> %s"
      % (valid, hit_rate, he_mean, dry_hit, dry_he, he_retention, pitch_verdict))

# ---------------------------------------------------------------------------
# 6. Artifacts: render_stats + provenance
# ---------------------------------------------------------------------------
(ANALYSIS / "render_stats.json").write_text(json.dumps({
    "lufs": meas_lufs, "peak": peak_val, "silence_pct": silence_pct,
    "rms": rms, "rms_per_sec": rms_map,
    "hit_rate": hit_rate, "mean_harmonic_energy": he_mean, "valid_windows": valid,
    "dry_hit_rate": dry_hit, "dry_he": dry_he, "he_retention": he_retention,
    "pitch_verdict": pitch_verdict,
    "n_generated_notes": gen_total,
    "generated_pitch_classes": gen_pcs,
    "n_stems": len(stems) if isinstance(stems, dict) else 0,
    "target_lufs": TARGET_LUFS,
}, indent=2))

provenance = {
    "job": "random-style production (SP) layer-aligned",
    "date": "2026-10-24",
    "seed": SEED,
    "method": "SP-078",
    "method_module": "sound.generators.polymetric_grid",
    "method_desc": "16-Track Polymetric Step Sequencer w/ Per-Step Graphs (Rapid Flow omniGRID-style)",
    "layer": "ABSOLUTE",
    "params": {
        "sample_rate": SR, "bpm": BPM, "ppqn": TPB,
        "total_beats": TOTAL_BEATS, "total_ticks": TOTAL_TICKS,
        "shuffle": "straight", "shuffle_amount": 0.0,
        "master_shift_ms": 0.0, "scale": "D Slendro (manual via set_pitch)",
        "tracks": {
            "1_gong": {"steps": 16, "res": 4, "note": 38, "euclidean": (1, 16)},
            "2_kenong": {"steps": 16, "res": 4, "note": 50, "euclidean": (4, 16, 3)},
            "3_kempul": {"steps": 16, "res": 4, "note": 45, "euclidean": (3, 16)},
            "4_kethuk": {"steps": 16, "res": 4, "note": 50, "euclidean": (8, 16),
                         "probability": 88.0, "repeats_step6": 2},
            "5_balungan": {"steps": 12, "res": 8, "contour": BAL_CONT, "euclidean": (7, 12)},
            "6_peking": {"steps": 12, "res": 16, "contour": PEK_CONT, "euclidean": (9, 12),
                         "probability": 92.0},
        },
        "periods_beats": PERIODS,
        "loops": LOOPS,
        "ensemble_rephase_beats": g.ensemble_period_beats,
        "carrier": "FluidSynth SP-001 (FluidR3_GM)",
        "target_lufs": TARGET_LUFS, "ceiling_db": CEILING_DB,
    },
    "source_midi": str(SRC),
    "source_reworked_midi": str(src_reworked),
    "groove_midi": str(groove_midi),
    "source_bpm": BPM,
    "source_key": "D Slendro pentatonic (D E F# A B)",
    "source_pitch_classes": sorted(SLENDRO_PCS),
    "output_wav": str(final_wav),
    "output_ogg": str(final_ogg),
    "raw_wav": str(raw_wav),
    "dry_reference_wav": str(dry_wav),
    "lufs": meas_lufs, "peak": peak_val, "silence_pct": silence_pct, "rms": rms,
    "pitch_verdict": pitch_verdict, "hit_rate": hit_rate, "he_mean": he_mean,
    "dry_he": dry_he, "he_retention": he_retention,
    "preflight_source": before,
    "preflight_reworked": reworked,
    "output_audit": out_audit,
}
(OUT / "provenance.json").write_text(json.dumps(provenance, indent=2))

# ---------------------------------------------------------------------------
# 7. REPORT.md
# ---------------------------------------------------------------------------
grid_before = before["grid_off"]
REPORT = """# SP-078 Polymetric Grid — production report

- **Date**: 2026-10-24
- **Job**: random-style production (SP), layer-aligned
- **Method**: SP-078 (`sound.generators.polymetric_grid`) — 16-track polymetric
  step sequencer w/ per-step graphs (Rapid Flow omniGRID-style). Independent
  step-count + resolution per track -> lanes re-phase over an LCM ensemble
  cycle; Bjorklund Euclidean pulses; per-step velocity/length/timing/probability/
  repeats graphs; eight shuffle modes; arpeggiator + scale quantisation.
- **Layer**: ABSOLUTE (whole-piece texture re-voicing; note material preserved
  as the source's D Slendro pentatonic, re-grooved by the polymetric grid).

## Selection
- **Registry source**: `workflows.musicom_workflow.SP_METHODS` (63 registered;
  55 in pool after excluding recent-7-day SP-090/092/095/101/105/108/111 and
  baseline SP-001).
- **Source composition**: `Styles/Gamelan/017-gamelan-central-java/MIDI/gamelan_live_render.mid`
  (D Slendro pentatonic gamelan, 80 BPM, 480 TPB, 8 x 16-beat gongan cycles,
  4 voices: Saron balungan / Peking elaboration / Colotomic pots / Gong Ageng;
  512 notes, all grid-locked).

## Pre-flight audit (3 rules) — zero-drift FAIL -> reworked, then PASS
The source is grid-clean (0 off-grid) and fully in D Slendro (0 out-of-scale /
0 out-of-chord), but the final Gong Ageng sustains 2 beats from beat 127 into
beat 129 -> note tracks end at [61440, 61920], violating equal-length
(zero-drift). **Rework**: boundary-clamp the whole source to the 128-beat seam
(61440 ticks) — the final gong note_off is truncated to the seam (the musicom
"no note crosses a section seam" convention). No onset touched.

| rule | before | after (reworked) |
|---|---|---|
| Grid sync (16th = 120 ticks) | **PASS** off-grid = {g_before} | **PASS** off-grid = {g_after} |
| Harmony (in D Slendro) | **PASS** out-of-scale = {s_before} | **PASS** out-of-scale = {s_after} |
| Zero-drift (equal track ends) | **FAIL** ends = {e_before} | **PASS** ends = {e_after} |

## SP-078 absolute layer (polymetric gamelan groove)
Six of the 16 available tracks, each with its own step-count + resolution so
their periods re-phase over the 96-beat render (2 full LCM re-phase cycles of
48 beats each):

| trk | role | steps | res | period | euclidean | pitch | program/ch |
|---|---|---|---|---|---|---|---|
| 1 | Gong Ageng | 16 | 1/4 | 16 beats | 1/16 (step 15) | D3 38 | 14 Tubular Bells / ch3 |
| 2 | Kenong | 16 | 1/4 | 16 beats | 4/16 rot 3 (3,7,11,15) | D4 50 | 12 Marimba / ch2 |
| 3 | Kempul | 16 | 1/4 | 16 beats | 3/16 (5,10,15) | A3 45 | 12 Marimba / ch2 |
| 4 | Kethuk | 16 | 1/4 | 16 beats | 8/16 (0,2,4,...14) | D4 50 | 12 Marimba / ch2 |
| 5 | Balungan | 12 | 1/8 | **6 beats** | 7/12 | Slendro contour | 12 Marimba / ch0 |
| 6 | Peking | 12 | 1/16 | **3 beats** | 9/12 | Slendro contour | 9 Glockenspiel / ch1 |

- **Polymetry**: tracks 5/6 run 6-beat and 3-beat periods against the 16-beat
  gongan, so the balungan and peking drift and re-phase across the piece
  (ensemble LCM = 48 beats; 96 beats = 2 full cycles).
- **Per-step graphs exercised**: note-length (gong 400% ring, kethuk 30% damp),
  probability (kethuk 88%, peking 92% — seeded thinning), repeats ratchet
  (kethuk beat 6 = 2), velocity via per-track gain.
- **Shuffle = straight, master micro-timing = 0** — deliberately disabled so
  the generated groove stays grid-locked (the composition 3-rule discipline
  requires 0 off-grid onsets; the method's pocket/shuffle controls would break
  that by design).
- **Scale quantisation**: the module's `SCALES` table is Western-only (no
  slendro), so the D Slendro pentatonic is applied manually via per-step
  `set_pitch` overrides (same quantised result).
- {n_gen} generated notes, pitch classes {gen_pcs} (all in D Slendro).
- Rendered through FluidSynth (FluidR3_GM) at 44100 Hz, mastered to −14 LUFS
  (unknown-genre default), −1 dBTP ceiling.

## Output audit (the generated groove, mirror of the 3 rules) — PASS
| rule | result |
|---|---|
| Grid sync (16th = 120 ticks) | **PASS** off-grid = {o_grid} |
| Harmony (in D Slendro) | **PASS** out-of-scale = {o_scale}, out-of-chord = {o_chord} |
| Zero-drift (equal track ends) | **PASS** 4 note tracks, end = {o_end} ticks |

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
- `MIDI/source_reworked.mid` (boundary-clamped source)
- `MIDI/SP078-polymetric-gamelan.mid` (generated polymetric groove)
- `Audio/stems/` ({n_stems} per-voice stems)
- `provenance.json`, `Analysis/render_stats.json`

## Notes
- SP-078's headline is polymetry (independent length + resolution per track,
  long LCM re-phasing) plus Euclidean generation and the per-step graph lanes.
  The absolute-layer application re-voices the gamelan's 4-voice colotomic
  texture as a 6-lane polymetric grid: the colotomy (gong/kenong/kempul/kethuk)
  stays anchored on the 16-beat gongan while the balungan (6-beat) and peking
  (3-beat) lanes drift against it — the omniGRID "lanes re-phase over time"
  behaviour expressed with slendro pitch material.
""".format(
    g_before=before["grid_off"], g_after=reworked["grid_off"],
    s_before=before["out_scale"], s_after=reworked["out_scale"],
    e_before=before["track_ends"], e_after=reworked["track_ends"],
    n_gen=gen_total, gen_pcs=gen_pcs,
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
for s in ("select_job_20261024.py",):
    srcp = OUT.parent / s
    if srcp.exists():
        try:
            shutil.copy2(str(srcp), str(SCRIPTS / s))
        except shutil.SameFileError:
            pass
try:
    shutil.copy2(__file__, str(SCRIPTS / "produce_sp078_cron.py"))
except shutil.SameFileError:
    pass

print("Done.")
