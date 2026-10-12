#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SP-074 Eight-Channel Sample Drum Machine (Bullfrog Drums style) production pass.

Source : Styles/Fanfare/006-fanfare-showband-32bar/MIDI/showband32.mid
         (fanfare showband, 132 BPM, 480 tpb, 32 bars = 61440 ticks = 58.18 s:
          track1 Trumpet prog56 ch0 lead, track2 Trombone prog57 ch1 harmony,
          track3 Tuba prog58 ch2 bass, track4 GM snare ch9 note-38 only).
         Key Bb major (pcs {10,0,2,3,5,7,9}), chord plan prog_A/B/C.

Method : SP-074 -> sound.generators.drum_machine (SP_METHODS registry).
         Eight-channel sample drum machine + X0X sequencer (Bullfrog Drums style):
         7 sample drum channels + 1 CV channel (the "sequence the Bullfrog Synth"
         lane) that drives a pitched Bb-major fanfare motif.

Layer  : ABSOLUTE (generator). The drum machine re-produces the WHOLE piece:
         percussion from the 7 drum channels (fanfare rhythm DNA at 132 BPM, 32
         bars), and the key/genre context carried by the CV lane -> a Bb-major
         trumpet "Bullfrog Synth" voice rendered via FluidSynth (SP-001 carrier).
         No source MIDI notes survive; only key/tempo/form/rhythm-DNA inherited.

Chain:
  pre-flight 3-rule audit (before) -> grid-quantize rework (onsets to 16th grid)
  -> re-audit (after, all 0) -> SP-074 render (drums + CV synth) -> mix
  -> normalize_to_lufs(-14) -> Limiter(-1 dBFS) LAST
  -> SP074-...wav + .ogg (Opus 48k voip)
  -> pitch verification + drum-grid verification + silence/RMS -> provenance + REPORT
"""
import hashlib
import json
import shutil
import subprocess
import wave
from pathlib import Path

import numpy as np
import mido

from sound.generators.drum_machine import BullfrogDrums, Kit
from sound.render.fluidsynth import discover_soundfont
from sound.effects.mastering import normalize_to_lufs, measure_lufs, Limiter
from rules.progression import Scale7ChordDegree

# ---------------------------------------------------------------------------
SRC = Path("/opt/data/repos/musicom/projects/Styles/Fanfare/006-fanfare-showband-32bar/MIDI/showband32.mid")
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/SP074-drum-machine-006-fanfare-showband-32bar")
AUD = OUT / "Audio"
STEMS = AUD / "stems"
MIDIDIR = OUT / "MIDI"
ANALYSIS = OUT / "Analysis"
SCRIPTS = OUT / "Scripts"

for d in (AUD, STEMS, MIDIDIR, ANALYSIS, SCRIPTS):
    d.mkdir(parents=True, exist_ok=True)

SR = 44100
TPB = 480
BPM = 132.0
SPB = 60.0 / BPM            # 0.454545 s/beat
BAR_TICKS = TPB * 4         # 1920
N_BARS = 32
TOTAL_TICKS = BAR_TICKS * N_BARS   # 61440
SEED = 20261012
GRID = 120                  # 16th-note grid

FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"

KEY_ROOT = 58               # Bb3
SCALE = [0, 2, 4, 5, 7, 9, 11]   # Bb major intervals
SCALE_PCS = {10, 0, 2, 3, 5, 7, 9}   # Bb C D Eb F G A
PROG_A = [1, 4, 7, 3, 6, 2, 5, 1]
PROG_B = [6, 2, 5, 1, 4, 2, 5, 5]
PROG_C = [1, 5, 4, 5, 1, 4, 5, 1]


def run(cmd, timeout=900):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError("cmd failed %s: %s" % (cmd, r.stderr[-800:]))
    return r


def degree_for_bar(col):
    if col < 8:
        return PROG_A[col]
    elif col < 16:
        return PROG_B[col - 8]
    elif col < 24:
        return PROG_A[col - 16]
    return PROG_C[col - 24]


def section_for_bar(col):
    if col < 8:
        return "A"
    elif col < 16:
        return "B"
    elif col < 24:
        return "A_var"
    return "C"


def chord_pcs(degree):
    idx = degree - 1
    bb = [10, 0, 2, 3, 5, 7, 9]   # Bb major ascending from tonic (Bb C D Eb F G A)
    return {bb[(idx + off) % 7] for off in (0, 2, 4)}


def audit(mf):
    """Return dict with the three-rule audit numbers for a loaded MidiFile."""
    grid_off = 0
    out_scale = 0
    out_chord = 0
    track_ends = []
    for tr in mf.tracks:
        chans = {m.channel for m in tr if m.type in ("note_on", "note_off")}
        is_drum = 9 in chans
        t = 0
        for m in tr:
            t += m.time
            if m.type == "note_on" and m.velocity > 0:
                if is_drum:
                    continue
                if (t % GRID) != 0:
                    grid_off += 1
                if (m.note % 12) not in SCALE_PCS:
                    out_scale += 1
                bar = min(t // BAR_TICKS, N_BARS - 1)
                if (m.note % 12) not in chord_pcs(degree_for_bar(bar)):
                    out_chord += 1
        if t > 0:
            track_ends.append(t)
    zero_drift = len(set(track_ends)) == 1
    return {"grid_off": grid_off, "out_scale": out_scale, "out_chord": out_chord,
            "zero_drift": zero_drift, "track_ends": sorted(set(track_ends))}


def quantize_midi(src, dst, grid=GRID):
    """Snap pitched note_on/note_off to the nearest grid multiple (16th = 120).
    Drums (channel 9) are untouched (rule 1 audits pitched voices only).
    note_off is snapped against its own note_on (min duration 1 grid step) so the
    track stays monotonic and grid-aligned."""
    mf = mido.MidiFile(str(src))
    for tr in mf.tracks:
        chans = {m.channel for m in tr if m.type in ("note_on", "note_off")}
        is_drum = 9 in chans
        if is_drum:
            continue
        msgs = []
        t = 0
        for m in tr:
            t += m.time
            msgs.append([m, t])
        open_notes = {}
        for i, (m, at) in enumerate(msgs):
            if m.type == "note_on" and m.velocity > 0:
                msgs[i][1] = round(at / grid) * grid
                open_notes[m.note] = i
            elif m.type == "note_off" and m.note in open_notes:
                on_i = open_notes.pop(m.note)
                on_s = msgs[on_i][1]
                off_s = round(at / grid) * grid
                if off_s < on_s + grid:
                    off_s = on_s + grid
                msgs[i][1] = off_s
        prev = 0
        for m, at in msgs:
            dt = at - prev
            if dt < 0:
                dt = 0
            m.time = dt
            prev += dt
    mf.save(str(dst))
    return mf


def sha256(p):
    h = hashlib.sha256()
    with open(str(p), "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def read_wav(p):
    with wave.open(str(p), "rb") as wf:
        nch = wf.getnchannels()
        sr = wf.getframerate()
        n = wf.getnframes()
        raw = np.frombuffer(wf.readframes(n), dtype=np.int16).astype(np.float64) / 32768.0
    if nch == 2:
        return raw.reshape(-1, 2), sr
    return np.column_stack([raw, raw]), sr


def write_wav(p, audio, sr=SR):
    a = np.clip(np.asarray(audio), -1.0, 1.0)
    if a.ndim == 1:
        data = (a * 32767.0).astype(np.int16).tobytes()
        nch = 1
    else:
        data = (a * 32767.0).astype(np.int16).reshape(-1).tobytes()
        nch = a.shape[1]
    with wave.open(str(p), "wb") as wf:
        wf.setnchannels(nch)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(data)


# ===========================================================================
# 1. Pre-flight audit (before)
# ===========================================================================
mf_before = mido.MidiFile(str(SRC))
before = audit(mf_before)
print("PREFLIGHT before:", before)

# ===========================================================================
# 2. Rework: grid-quantize pitched onsets (keep humanized original as phase1)
# ===========================================================================
phase1 = MIDIDIR / "showband32-phase1.mid"
reworked = MIDIDIR / "showband32.mid"
shutil.copy2(str(SRC), str(phase1))
mf_after = quantize_midi(SRC, reworked)
after = audit(mf_after)
print("PREFLIGHT after :", after)
assert after["grid_off"] == 0, "grid sync still failing after rework"
assert after["out_scale"] == 0 and after["out_chord"] == 0, "harmony failing after rework"
assert after["zero_drift"], "zero-drift failing after rework"

(ANALYSIS / "rework_audit.json").write_text(json.dumps({
    "before": before, "after": after,
    "rework": "snap pitched note_on onsets to nearest 16th grid (120 ticks); "
              "drums (ch9) untouched; humanized original preserved as phase1 sidecar",
}, indent=2))

# ===========================================================================
# 3. Dry reference (FluidSynth SP-001 baseline on the reworked MIDI)
# ===========================================================================
SF = discover_soundfont()
assert SF and Path(SF).exists(), "SoundFont missing: %r" % SF
print("SoundFont:", SF)

dry_full = OUT / "dry_full_mix_sp001_reference.wav"
run([FLUID, "-ni", "-R", "0", "-C", "0", "-g", "1.2", "-F", str(dry_full),
     "-r", str(SR), SF, str(reworked)])
print("dry full mix:", dry_full.stat().st_size, "bytes")

# ===========================================================================
# 4. SP-074 drum machine (absolute layer: 7 sample channels)
# ===========================================================================
bf = BullfrogDrums(sample_rate=SR)
bf.load_kit(Kit.demo_kit(SR))
# per-channel musical shaping (Bullfrog param set)
bf.channels[1].decay = 1.0        # kick full
bf.channels[2].decay = 0.85       # snare
bf.channels[3].decay = 0.6        # hat
bf.channels[4].pitch = 0.9        # tom slightly lower
bf.channels[5].pan = -0.25        # clap left
bf.channels[6].pan = 0.25         # rim right
bf.channels[7].decay = 1.2        # cymbal long

grid = {ch: {} for ch in range(1, 8)}
flams = {}
for bar in range(N_BARS):
    sect = section_for_bar(bar)
    base = bar * 16
    # kick: marching pulse (beats 1 & 3)
    grid[1][base + 0] = 1.0
    grid[1][base + 8] = 0.9
    if sect == "C":
        grid[1][base + 4] = 0.7
        grid[1][base + 12] = 0.7
    # snare: roll/backbeat by section
    if sect == "B":
        for s in range(0, 16, 2):      # paradiddle eighths
            grid[2][base + s] = 0.8 if s in (0, 8) else 0.5
    elif sect == "C":
        for s in range(16):            # 16th crescendo roll
            grid[2][base + s] = min(1.0, 0.55 + s * 0.03)
        flams[(2, base + 4)] = 1
        flams[(2, base + 12)] = 1
    else:                              # A / A_var marching roll
        grid[2][base + 4] = 0.9
        grid[2][base + 12] = 0.9
        for s in (2, 6, 10, 14):
            grid[2][base + s] = 0.45
    # hat
    if sect == "C":
        for s in range(16):
            grid[3][base + s] = 0.4
    else:
        for s in range(0, 16, 2):
            grid[3][base + s] = 0.5
    # tom fills at section ends (bars 7, 15, 23)
    if bar in (7, 15, 23):
        for s in (12, 14, 15):
            grid[4][base + s] = 0.8
    # clap every 4th bar
    if bar % 4 == 3:
        grid[5][base + 4] = 0.7
    # rim accent cadence (bars 3,7,11,...)
    if bar in (3, 7, 11, 15, 19, 23, 27, 31):
        grid[6][base + 15] = 0.9
    # cymbal crash at section starts
    if bar in (0, 8, 16, 24):
        grid[7][base + 0] = 0.9

drum_audio = bf.render(grid, bpm=BPM, steps=16, bars=N_BARS, swing=0.12, flams=flams)
print("drum audio shape:", drum_audio.shape, "dur_s", round(len(drum_audio) / SR, 2))

# ===========================================================================
# 5. CV channel -> Bb-major fanfare motif -> FluidSynth trumpet "synth"
#    The Bullfrog CV lane is a 64-step X0X pattern (4 bars at 16 steps/bar).
#    We program a 4-bar Bb-major harmonic cell (chords I-IV-vii°-iii roots+fifths)
#    and loop it 8x over the 32 bars. The synth voice plays exactly what the CV
#    lane sequences (scale degrees read back from the CV channel).
# ===========================================================================
CV_CELL = [1, 4, 7, 3]      # 4-bar Bb-major cell (I IV vii° iii)
for k, d in enumerate(CV_CELL):
    bf.cv.set(k * 16 + 0, ((d - 1) % 7) / 6.0)
    bf.cv.set(k * 16 + 8, ((d + 3) % 7) / 6.0)

cv_seq = bf.to_cv_sequence(64)      # [(step, volts)] over the 64-step pattern
cell_notes = {}
cv_entries = []
for step, volts in cv_seq:
    deg = int(round(volts / 5.0 * 6.0)) % 7
    note = int(Scale7ChordDegree.get_diatonic_note(KEY_ROOT, SCALE, deg) + 12)
    cell_notes[step] = note
    cv_entries.append({"step": step, "volts": round(volts, 4),
                       "scale_degree": deg, "midi_note": note})
print("CV sequence entries:", len(cv_seq), "e.g.", cv_seq[:4])

synth_notes = []        # (pitch, start_tick, end_tick, velocity) — looped 8x
for bar in range(N_BARS):
    rb = bar % 4
    root = cell_notes[rb * 16 + 0]
    fifth = cell_notes[rb * 16 + 8]
    b0 = bar * BAR_TICKS
    synth_notes.append((root, b0, b0 + 960, 100))
    synth_notes.append((fifth, b0 + 960, b0 + BAR_TICKS, 95))

# synth MIDI (CV-driven "Bullfrog Synth" = FluidSynth trumpet)
synth_midi = MIDIDIR / "showband32-cv-synth.mid"
mid = mido.MidiFile(ticks_per_beat=TPB)
tr0 = mido.MidiTrack()
tr0.append(mido.MetaMessage("set_tempo", tempo=int(round(60000000 / BPM)), time=0))
tr0.append(mido.MetaMessage("time_signature", numerator=4, denominator=4, time=0))
tr0.append(mido.MetaMessage("end_of_track", time=TOTAL_TICKS))
mid.tracks.append(tr0)
tr1 = mido.MidiTrack()
tr1.append(mido.Message("program_change", program=56, channel=0, time=0))
evs = []
for p, st, en, vel in synth_notes:
    evs.append((st, "on", p, vel))
    evs.append((en, "off", p, 0))
evs.sort()
prev = 0
for t, kind, pitch, vel in evs:
    dt = t - prev
    prev = t
    if kind == "on":
        tr1.append(mido.Message("note_on", note=pitch, velocity=vel, channel=0, time=dt))
    else:
        tr1.append(mido.Message("note_off", note=pitch, velocity=0, channel=0, time=dt))
tr1.append(mido.MetaMessage("end_of_track", time=0))
mid.tracks.append(tr1)
mid.save(str(synth_midi))

synth_bus_wav = STEMS / "cv_synth_trumpet.wav"
run([FLUID, "-ni", "-R", "0", "-C", "0", "-g", "1.2", "-F", str(synth_bus_wav),
     "-r", str(SR), SF, str(synth_midi)])
print("synth bus:", synth_bus_wav.stat().st_size, "bytes")

synth_audio, _ = read_wav(synth_bus_wav)

# drum bus -> wav stem
drum_bus_wav = STEMS / "drum_machine_7ch.wav"
write_wav(drum_bus_wav, drum_audio)

# ===========================================================================
# 6. Mix + master
# ===========================================================================
n = min(len(drum_audio), len(synth_audio))
drum = drum_audio[:n]
syn = synth_audio[:n]
drum_pk = np.max(np.abs(drum)) or 1.0
syn_pk = np.max(np.abs(syn)) or 1.0
mix = drum * (0.55 / drum_pk) + syn * (0.85 / syn_pk)

mix_norm = normalize_to_lufs(mix, target_lufs=-14.0, sample_rate=SR)
limiter = Limiter(threshold_db=-1.0, sample_rate=SR)
final = limiter.process(mix_norm)

final_wav = OUT / "SP074-drum-machine-006-fanfare-showband-32bar.wav"
final_ogg = OUT / "SP074-drum-machine-006-fanfare-showband-32bar.ogg"
write_wav(final_wav, final)
r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(final_wav),
                    "-codec:a", "libopus", "-application", "voip", "-b:a", "48k",
                    str(final_ogg)], capture_output=True, text=True, timeout=180)
assert r.returncode == 0, "ffmpeg failed: %s" % r.stderr[-300:]
assert final_ogg.stat().st_size > 10000, "OGG empty"
print("final WAV:", final_wav.stat().st_size, "final OGG:", final_ogg.stat().st_size)

# ===========================================================================
# 7. Verification
# ===========================================================================
meas_lufs = measure_lufs(final, sample_rate=SR)
peak_val = float(np.max(np.abs(final)))
mono = 0.5 * (final[:, 0] + final[:, 1])
silence_pct = float(np.sum(np.abs(mono) < 0.001) / len(mono)) * 100.0
rms = float(np.sqrt(np.mean(mono ** 2)))
rms_map = [round(float(np.sqrt(np.mean(mono[i:i + SR] ** 2))), 4)
           for i in range(0, len(mono), SR)]
print("LUFS=%.2f peak=%.4f silence=%.2f%% rms=%.4f" % (meas_lufs, peak_val, silence_pct, rms))


def midi_to_freq(nn):
    return 440.0 * (2.0 ** ((nn - 69) / 12.0))


def fft_hit_check(audio, notes, sr=SR):
    """Pitch fidelity: dominant FFT peak per 0.5 s window vs active note freqs."""
    win = int(0.5 * sr)
    n_wins = len(audio) // win
    freqs = np.fft.rfftfreq(win, 1.0 / sr)
    mask = (freqs >= 50.0) & (freqs <= 3000.0)
    checked = hits = 0
    he_list, dom_list, misses = [], [], []
    for w in range(n_wins):
        t0, t1 = w * 0.5, w * 0.5 + 0.5
        act = set()
        for (p, st, en, _v) in notes:
            a, b = st * SPB / TPB, en * SPB / TPB
            if a < t1 and b > t0:
                act.add(p)
        if not act:
            continue
        seg = audio[w * win:(w + 1) * win]
        if len(seg) < win or float(np.sqrt(np.mean(seg ** 2))) < 0.01:
            continue
        spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
        f_band, s_band = freqs[mask], spec[mask]
        dom = float(f_band[int(np.argmax(s_band))])
        dom_list.append(dom)
        funds = sorted(midi_to_freq(p) for p in act)
        hit = any(abs(dom - c) / c < 0.04 for f in funds for c in (f, f * 2, f * 3, f * 4, f / 2, f / 3))
        checked += 1
        hits += 1 if hit else 0
        if not hit:
            misses.append({"t": round(t0, 2), "dom": round(dom, 1), "act": sorted(act)})
        tot = np.sum(s_band ** 2) + 1e-12
        he = 0.0
        for k in range(1, 9):
            tf = dom * k
            he += np.sum(s_band[(f_band >= tf - 15.0) & (f_band <= tf + 15.0)] ** 2)
        he_list.append(float(he / tot))
    hit_rate = hits / max(checked, 1)
    he_mean = float(np.mean(he_list)) if he_list else 0.0
    return hit_rate, he_mean, checked, dom_list, misses


# synth-bus pitch check (the pitched CV voice)
syn_mono = 0.5 * (synth_audio[:, 0] + synth_audio[:, 1])
syn_hit, syn_he, syn_checked, syn_dom, syn_miss = fft_hit_check(syn_mono, synth_notes)

# full-mix pitch check (drums are unpitched by design -> reported as context)
mix_hit, mix_he, mix_checked, mix_dom, mix_miss = fft_hit_check(mono, synth_notes)

# drum-grid check: envelope spectrum should peak at the 16th-note rate 8.8 Hz
step_dur = 60.0 / BPM / 4.0
drum_mono = 0.5 * (drum_audio[:, 0] + drum_audio[:, 1])
env = np.abs(drum_mono)
k = int(0.005 * SR)
env = np.convolve(env, np.ones(k) / k, mode="same")
env_fft = np.abs(np.fft.rfft(env))
env_freq = np.fft.rfftfreq(len(env), 1.0 / SR)
band = (env_freq >= 1.0) & (env_freq <= 40.0)
grid_peak = float(env_freq[band][int(np.argmax(env_fft[band]))])
expected = 1.0 / step_dur
grid_ok = abs(grid_peak - expected) / expected < 0.05
print("drum envelope grid peak %.2f Hz (expected %.2f Hz) -> %s"
      % (grid_peak, expected, "OK" if grid_ok else "OFF"))

# ACF unpitched (full mix)
ds = 5
md = mono[::ds]
sd = SR // ds
ww = sd
unpitched = acf_n = 0
for w in range(0, len(md) // ww, 2):
    seg = md[w * ww:(w + 1) * ww]
    if len(seg) < ww or float(np.sqrt(np.mean(seg ** 2))) < 0.01:
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

syn_verdict = "PASS" if (syn_hit >= 0.60 and syn_he >= 0.25) else "FAIL"
print("SYNTH pitch windows=%d hit=%.4f he=%.4f -> %s" % (syn_checked, syn_hit, syn_he, syn_verdict))
print("MIX   pitch windows=%d hit=%.4f he=%.4f (drums unpitched by design)"
      % (mix_checked, mix_hit, mix_he))
print("MIX   acf_unpitched=%d/%d" % (unpitched, acf_n))

# ===========================================================================
# 8. Grid visualization (SP-074 production DNA)
# ===========================================================================
repr_bars = {0: "A", 8: "B", 16: "A_var", 24: "C"}
chan_names = {1: "kick", 2: "snare", 3: "hat", 4: "tom", 5: "clap", 6: "rim", 7: "cymbal"}
lines = [
    "SP-074 Bullfrog Drums — production DNA (Bb major, 132 BPM, 32 bars)",
    "rows = 7 drum channels + CV synth; cols = 16th slots for 4 representative bars (A/B/A_var/C section starts)",
    "# = hit, . = rest  (tom/clap/rim fire at cadence bars 3,7,11,... and section-end fills, so they read empty at section starts)",
    "",
]
for ch in range(1, 8):
    row = []
    for bar, label in sorted(repr_bars.items()):
        for s in range(16):
            row.append("#" if (bar * 16 + s) in grid[ch] else ".")
    lines.append("%-7s %s" % (chan_names[ch], "".join(row)))
row = []
for bar, label in sorted(repr_bars.items()):
    for s in range(16):
        cv_on = any(_s == (bar % 4) * 16 + s for (_s, _v) in cv_seq)
        row.append("^" if cv_on else ".")
lines.append("%-7s %s   (^ = CV lane drives Bb-major trumpet fanfare note)" % ("CV/synth", "".join(row)))
(ANALYSIS / "grid_visualization.txt").write_text("\n".join(lines) + "\n")
print("\n".join(lines))

# ===========================================================================
# 9. JSONs + provenance
# ===========================================================================
(ANALYSIS / "render_stats.json").write_text(json.dumps({
    "method": "SP-074", "method_module": "sound.generators.drum_machine",
    "layer": "absolute (generator)", "seed": SEED,
    "key": "Bb major", "bpm": BPM, "bars": N_BARS, "ticks_per_beat": TPB,
    "source_duration_s": round(TOTAL_TICKS * SPB / TPB, 2),
    "drum_channels": 7, "cv_channel": True,
    "preflight_before": before, "preflight_after": after,
    "lufs": round(meas_lufs, 2), "peak": round(peak_val, 4),
    "silence_pct": round(silence_pct, 2), "rms": round(rms, 4),
    "rms_per_second": rms_map,
    "synth_pitch": {"windows": syn_checked, "hit_rate": round(syn_hit, 4),
                     "harmonic_energy": round(syn_he, 4), "verdict": syn_verdict},
    "mix_pitch_context": {"windows": mix_checked, "hit_rate": round(mix_hit, 4),
                          "harmonic_energy": round(mix_he, 4)},
    "drum_grid": {"envelope_peak_hz": round(grid_peak, 2),
                  "expected_16th_hz": round(expected, 2), "on_grid": bool(grid_ok)},
    "acf_windows": acf_n, "acf_unpitched": unpitched,
    "synth_median_dom_hz": round(float(np.median(syn_dom)), 1) if syn_dom else 0.0,
}, indent=2))

(ANALYSIS / "pitch_verification.json").write_text(json.dumps({
    "method": "SP-074", "project": "Fanfare/006-fanfare-showband-32bar",
    "key": "Bb major", "synth_verdict": syn_verdict,
    "synth_hit_rate": round(syn_hit, 4), "synth_harmonic_energy": round(syn_he, 4),
    "synth_windows": syn_checked, "synth_misses": syn_miss[:12],
    "drum_envelope_grid_peak_hz": round(grid_peak, 2),
    "drum_expected_16th_hz": round(expected, 2), "drum_on_grid": bool(grid_ok),
    "mix_hit_rate": round(mix_hit, 4), "mix_harmonic_energy": round(mix_he, 4),
    "acf_unpitched": unpitched, "acf_windows": acf_n,
}, indent=2))

(ANALYSIS / "cv_sequence.json").write_text(json.dumps({
    "description": "Bullfrog Drums CV lane (channel 8): 64-step X0X pattern (4-bar Bb-major "
                   "harmonic cell I-IV-vii*-iii), looped 8x over 32 bars. (step, volts) -> "
                   "scale degree -> Bb-major trumpet note (FluidSynth prog 56).",
    "max_volts": 5.0, "cell_bars": 4, "cell_chords": CV_CELL,
    "mapped": cv_entries, "raw": cv_seq,
}, indent=2))

provenance = {
    "job": "random-style production (SP) layer-aligned",
    "date": "2026-10-12", "seed": SEED,
    "method": "SP-074",
    "method_module": "sound.generators.drum_machine",
    "method_desc": "Eight-Channel Sample Drum Machine + Sequencer (Bullfrog Drums-style)",
    "layer": "absolute (generator): 7 drum channels replace percussion; CV lane drives Bb-major trumpet synth",
    "selection_source": "workflows.musicom_workflow.SP_METHODS registry (45 implemented)",
    "source_midi": str(SRC), "source_sha256": sha256(SRC),
    "phase1_midi": str(phase1), "reworked_midi": str(reworked),
    "synth_midi": str(synth_midi),
    "output_wav": str(final_wav), "output_ogg": str(final_ogg),
    "soundfont": SF,
    "params": {
        "key": "Bb major", "bpm": BPM, "bars": N_BARS, "swing": 0.12,
        "drum_channels": 7, "kit": "demo_kit (kick/snare/hat/tom/clap/rim/cymbal)",
        "cv_base": "Bb major scale degrees -> FluidSynth trumpet (prog 56)",
    },
    "preflight": {"before": before, "after": after},
    "rework": "pitched note_on onsets snapped to 16th grid (120 ticks); drums untouched; "
              "humanized original preserved as showband32-phase1.mid",
    "lufs": round(meas_lufs, 2), "peak": round(peak_val, 4),
    "silence_pct": round(silence_pct, 2), "rms": round(rms, 4),
    "pitch_verdict": syn_verdict, "synth_hit_rate": round(syn_hit, 4),
    "synth_he": round(syn_he, 4), "drum_grid_ok": bool(grid_ok),
}
(OUT / "provenance.json").write_text(json.dumps(provenance, indent=2))

(ANALYSIS / "select_20261012.json").write_text(json.dumps({
    "date": "2026-10-12", "method": "SP-074",
    "method_module": "sound.generators.drum_machine",
    "source_midi": str(SRC),
    "recent_excluded": ["SP-026", "SP-069", "SP-080", "SP-085", "SP-091", "SP-092", "SP-098"],
    "registry_total": 45, "n_well_formed": 227, "n_candidates": 336,
}, indent=2))

if str(Path(__file__).resolve()) != str((SCRIPTS / "produce_sp074_cron.py").resolve()):
    shutil.copy2(__file__, str(SCRIPTS / "produce_sp074_cron.py"))

print("Done. synth_verdict=", syn_verdict, "grid_off", before["grid_off"], "->", after["grid_off"])
