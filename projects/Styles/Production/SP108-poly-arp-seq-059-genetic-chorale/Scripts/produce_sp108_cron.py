# -*- coding: utf-8 -*-
"""SP-108 Polyphonic Arpeggiator + Step Sequencer production pass (absolute layer).

Source : Styles/Experimental/059-genetic-chorale/MIDI/059-genetic-chorale.mid
         (8-bar SATB chorale, G natural minor i-iv-v-i-iv-v-iv-i, 88 BPM,
          480 TPB, 4 voices ch0..3 prog74/prog33, 15360 ticks = 8 bars).
Method : SP-108 -> sound.generators.poly_arp_seq (Arpeggiator, Prophet Rev4
         firmware-mod style). ABSOLUTE layer: the whole piece's chordal
         texture is re-voiced as a single flowing 16th-note arpeggio line
         (per-bar chord -> arpeggiator -> new note stream), rendered through
         a FluidSynth carrier (SP-001) and mastered.

Pre-flight: 3-rule audit -> fix 1 out-of-chord note (Tenor bar1 C3=48 ->
         D3=50, the documented intent) -> re-audit all-0 -> SP-108 render.
"""
import hashlib
import json
import os
import shutil
import subprocess
import wave
from pathlib import Path

import numpy as np
import mido

from sound.render.fluidsynth import discover_soundfont
from sound.generators.poly_arp_seq import Arpeggiator
from sound.effects.mastering import master, target_for_style, measure_lufs

# ---------------------------------------------------------------------------
SRC = Path("/opt/data/repos/musicom/projects/Styles/Experimental/059-genetic-chorale/MIDI/059-genetic-chorale.mid")
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/SP108-poly-arp-seq-059-genetic-chorale")
AUD = OUT / "Audio"
STEMS = AUD / "stems"
MIDIDIR = OUT / "MIDI"
ANALYSIS = OUT / "Analysis"
SCRIPTS = OUT / "Scripts"

for d in (AUD, STEMS, MIDIDIR, ANALYSIS, SCRIPTS):
    d.mkdir(parents=True, exist_ok=True)

SR = 44100
TPB = 480
BPM = 88.0
BAR_TICKS = 1920
N_BARS = 8
TOTAL_TICKS = BAR_TICKS * N_BARS          # 15360
SEED = 2026102022
GRID = 120                                 # 16th-note
STEP = 120                                 # arp step ticks (1/16 division)

GMIN_PCS = {7, 9, 10, 0, 2, 3, 5}          # G A Bb C D Eb F
CHORD_DEGREES = [1, 4, 5, 1, 4, 5, 4, 1]

# per-bar 4-note chords AFTER rework (Tenor bar1 48 -> 50)
BAR_CHORDS = [
    [67, 55, 50, 38],   # bar1 i  Gm  (G4 G3 D3 D2)
    [67, 55, 51, 48],   # bar2 iv Cm  (G4 G3 Eb3 C3)
    [65, 57, 50, 38],   # bar3 v  Dm  (F4 A3 D3 D2)
    [67, 58, 50, 43],   # bar4 i  Gm  (G4 Bb3 D3 G2)
    [67, 60, 51, 48],   # bar5 iv Cm  (G4 C4 Eb3 C3)
    [65, 57, 50, 38],   # bar6 v  Dm  (F4 A3 D3 D2)
    [63, 55, 51, 48],   # bar7 iv Cm  (Eb4 G3 Eb3 C3)
    [67, 55, 50, 43],   # bar8 i  Gm  (G4 G3 D3 G2)
]

FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"


def chord_pcs(deg):
    gmin = [7, 9, 10, 0, 2, 3, 5]
    idx = deg - 1
    return {gmin[(idx + off) % 7] for off in (0, 2, 4)}


def read_wav(p):
    with wave.open(str(p), "rb") as wf:
        nch = wf.getnchannels()
        sr = wf.getframerate()
        data = wf.readframes(wf.getnframes())
        samples = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
        if nch == 1:
            return np.vstack([samples, samples]), sr
        return samples.reshape(-1, nch).T, sr


def write_wav(p, audio, sr=SR):
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


def sha256(p):
    h = hashlib.sha256()
    with open(str(p), "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


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
                if (m.note % 12) not in GMIN_PCS:
                    out_scale += 1
                bar = min(t // BAR_TICKS, N_BARS - 1)
                if (m.note % 12) not in chord_pcs(CHORD_DEGREES[bar]):
                    out_chord += 1
        if n_notes:
            track_ends.append(t)
    zero_drift = len(set(track_ends)) == 1
    return {"grid_off": grid_off, "out_scale": out_scale, "out_chord": out_chord,
            "zero_drift": zero_drift, "track_ends": sorted(set(track_ends)),
            "total_notes": total_notes}


# ===========================================================================
# 1. Pre-flight audit (before) + copy source for reference
# ===========================================================================
shutil.copy2(str(SRC), str(MIDIDIR / "source_original.mid"))
shutil.copy2(str(SRC), str(MIDIDIR / "059-genetic-chorale-phase1.mid"))
before = audit(SRC)
print("PREFLIGHT before:", before)

# ===========================================================================
# 2. Rework: Tenor bar1 note 48 (C3, out of Gm chord) -> 50 (D3)
# ===========================================================================
mf = mido.MidiFile(str(SRC))
fixed = 0
for tr in mf.tracks:
    t = 0
    for m in tr:
        t += m.time
        if m.type == "note_on" and m.note == 48 and m.velocity > 0 and t < BAR_TICKS:
            m.note = 50
            fixed += 1
print("rework fixed notes:", fixed)
norm = MIDIDIR / "composition.mid"
mf.save(str(norm))

after = audit(norm)
print("PREFLIGHT after :", after)
assert after["grid_off"] == 0, "grid sync failing after rework"
assert after["out_scale"] == 0, "out-of-scale failing after rework"
assert after["out_chord"] == 0, "out-of-chord failing after rework"
assert after["zero_drift"], "zero-drift failing after rework"

(ANALYSIS / "rework_audit.json").write_text(json.dumps({
    "before": before, "after": after,
    "rework": "snap Tenor bar1 note 48 (C3, non-chord) to 50 (D3, chord tone of Gm); "
              "all other notes untouched; source preserved as source_original.mid",
}, indent=2))

# ===========================================================================
# 3. SP-108: arpeggiate per-bar chords -> new note stream (absolute layer)
# ===========================================================================
arp = Arpeggiator(bpm=int(BPM), division="1/16", ppqn=TPB)
arp.mode = "updown"
arp.octave_range = 2
arp.hold = False

arp_events = []   # (pitch, velocity, start_tick, end_tick)
for bar in range(N_BARS):
    arp.all_notes_off()
    arp._step_index = 0
    for n in BAR_CHORDS[bar]:
        arp.note_on(n, 100)
    b0 = bar * BAR_TICKS
    for s in range(16):
        evts = arp.tick(STEP)
        for ev in evts:
            start = b0 + s * STEP
            dur = max(1, int(STEP * ev.gate))
            arp_events.append((ev.pitch, ev.velocity, start, start + dur))

print("SP-108 arp events:", len(arp_events))
arp_pcs = sorted(set(p for p, v, s, e in arp_events for p in [p % 12]))
print("arp pitch classes:", arp_pcs)
assert arp_pcs and set(arp_pcs) <= GMIN_PCS, "arp notes drifted out of G minor scale"

# write arpeggiated MIDI
mid = mido.MidiFile(ticks_per_beat=TPB)
tr0 = mido.MidiTrack()
tr0.append(mido.MetaMessage("set_tempo", tempo=int(round(60000000 / BPM)), time=0))
tr0.append(mido.MetaMessage("time_signature", numerator=4, denominator=4, time=0))
tr0.append(mido.MetaMessage("end_of_track", time=TOTAL_TICKS))
mid.tracks.append(tr0)
tr1 = mido.MidiTrack()
tr1.append(mido.Message("program_change", program=0, channel=0, time=0))  # piano carrier
evs = []
for p, v, s, e in arp_events:
    evs.append((s, "on", p, v))
    evs.append((e, "off", p, 0))
evs.sort()
prev = 0
for t, kind, pitch, vel in evs:
    dt = t - prev
    if dt < 0:
        dt = 0
    prev += dt
    if kind == "on":
        tr1.append(mido.Message("note_on", note=pitch, velocity=vel, channel=0, time=dt))
    else:
        tr1.append(mido.Message("note_off", note=pitch, velocity=0, channel=0, time=dt))
# zero-drift: pad track to TOTAL_TICKS
if prev < TOTAL_TICKS:
    tr1.append(mido.MetaMessage("end_of_track", time=TOTAL_TICKS - prev))
else:
    tr1.append(mido.MetaMessage("end_of_track", time=0))
mid.tracks.append(tr1)
arp_midi = MIDIDIR / "SP108-arp.mid"
mid.save(str(arp_midi))
print("wrote", arp_midi, arp_midi.stat().st_size, "bytes")

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

# dry reference: reworked chorale (pre-arpeggiation)
dry_wav = OUT / "dry_full_mix_chorale_reference.wav"
render(norm, dry_wav)
print("dry reference:", dry_wav.stat().st_size, "bytes")

# SP-108 arpeggiated full mix (raw)
raw_wav = OUT / "SP108_arp_raw.wav"
render(arp_midi, raw_wav)
print("SP-108 raw:", raw_wav.stat().st_size, "bytes")

# per-track stems of reworked chorale (DAW import artifacts)
try:
    from sound.render.pipeline import RenderPipeline
    pipeline = RenderPipeline(soundfont_path=SF, fluidsynth_bin=FLUID, sample_rate=SR)
    stems = pipeline.render_stems(str(norm), str(STEMS), format="wav")
    print("rendered %d stems" % len(stems))
except Exception as e:
    stems = {}
    print("stem render skipped:", repr(e)[:200])

# ===========================================================================
# 5. Master the SP-108 render
# ===========================================================================
style = "experimental"
try:
    TARGET_LUFS = target_for_style(style)
except Exception:
    TARGET_LUFS = -14.0
CEILING_DB = -1.0

raw_audio, sr = read_wav(raw_wav)           # (2, N)
raw_tm = raw_audio.T.astype(np.float32)     # (N, 2)
print("mastering (target %s LUFS, ceiling %s dBTP)..." % (TARGET_LUFS, CEILING_DB))
mastered_tm, rep = master(raw_tm, target_lufs=TARGET_LUFS, ceiling_db=CEILING_DB,
                          sample_rate=SR)
print("master report: LUFS %.2f, true peak %.2f dBTP"
      % (float(rep.get("integrated_lufs", 0)), float(rep.get("true_peak_db", 0))))
final_master = mastered_tm.T                  # (2, N)

final_wav = OUT / "SP108-poly-arp-seq-059-genetic-chorale.wav"
final_ogg = OUT / "SP108-poly-arp-seq-059-genetic-chorale.ogg"
write_wav(final_wav, final_master, sr=SR)
r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(final_wav),
                    "-codec:a", "libopus", "-application", "voip", "-b:a", "48k",
                    str(final_ogg)], capture_output=True, text=True, timeout=180)
assert r.returncode == 0 and final_ogg.stat().st_size > 10000, "ogg encode failed"
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
print("LUFS=%.2f peak=%.4f silence=%.2f%% rms=%.4f" % (meas_lufs, peak_val, silence_pct, rms))


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


hit_rate, he_mean, valid = pitch_verify(final_master, GMIN_PCS)
dry_hit, dry_he, dry_valid = pitch_verify(raw_audio, GMIN_PCS)
he_retention = (he_mean / dry_he) if dry_he > 0 else 0.0
pitch_verdict = "PASS" if (hit_rate >= 0.60 and he_mean >= 0.30) else "FAIL"
print("Pitch verify: valid=%d hit=%.4f mean_HE=%.4f | dry hit=%.4f HE=%.4f | retention=%.3f -> %s"
      % (valid, hit_rate, he_mean, dry_hit, dry_he, he_retention, pitch_verdict))

# ===========================================================================
# 7. Provenance + analysis
# ===========================================================================
(ANALYSIS / "render_stats.json").write_text(json.dumps({
    "lufs": meas_lufs, "peak": peak_val, "silence_pct": silence_pct,
    "rms": rms, "rms_per_sec": rms_map,
    "hit_rate": hit_rate, "mean_harmonic_energy": he_mean, "valid_windows": valid,
    "dry_hit_rate": dry_hit, "dry_he": dry_he, "he_retention": he_retention,
    "pitch_verdict": pitch_verdict,
    "n_arp_events": len(arp_events), "arp_pitch_classes": arp_pcs,
    "n_stems": len(stems) if isinstance(stems, dict) else 0,
}, indent=2))

provenance = {
    "job": "random-style production (SP) layer-aligned",
    "date": "2026-10-20",
    "seed": SEED,
    "method": "SP-108",
    "method_module": "sound.generators.poly_arp_seq",
    "method_desc": "Polyphonic Arpeggiator + Step Sequencer (Prophet Rev4 firmware-mod-style)",
    "layer": "ABSOLUTE",
    "params": {
        "sample_rate": SR, "bpm": BPM, "ppqn": TPB,
        "arp_mode": arp.mode, "octave_range": arp.octave_range,
        "division": "1/16", "step_ticks": STEP, "gate": 0.8,
        "carrier_program": 0, "carrier": "FluidSynth SP-001",
        "target_lufs": TARGET_LUFS, "ceiling_db": CEILING_DB,
    },
    "source_midi": str(SRC),
    "normalized_midi": str(norm),
    "arp_midi": str(arp_midi),
    "source_bpm": BPM,
    "source_pitch_classes": sorted(GMIN_PCS),
    "rework": "Tenor bar1 48->50",
    "output_wav": str(final_wav),
    "output_ogg": str(final_ogg),
    "lufs": meas_lufs, "peak": peak_val, "silence_pct": silence_pct,
    "rms": rms,
    "pitch_verdict": pitch_verdict, "hit_rate": hit_rate, "he_mean": he_mean,
    "dry_he": dry_he, "he_retention": he_retention,
    "preflight_before": before, "preflight_after": after,
}
(OUT / "provenance.json").write_text(json.dumps(provenance, indent=2))

for s in ("audit_source_20261020_rerun.py", "select_job_20261020_rerun.py"):
    srcp = OUT.parent / s
    if srcp.exists():
        try:
            shutil.copy2(str(srcp), str(SCRIPTS / s))
        except shutil.SameFileError:
            pass
try:
    shutil.copy2(__file__, str(SCRIPTS / "produce_sp108_cron.py"))
except shutil.SameFileError:
    pass

print("Done.")
