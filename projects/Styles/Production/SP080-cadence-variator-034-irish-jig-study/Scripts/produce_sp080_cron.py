# -*- coding: utf-8 -*-
"""SP-080 Cadence Engine Rhythmic Variator production pass (absolute layer).

Source : Styles/"Celtic / Irish Traditional"/034-irish-jig-study/MIDI/irish_jig.mid
         (6-bar Irish jig, G major, 120 BPM, 4/4, 480 TPB, single flute melody
         program 73, 56 onsets = 48 structural 8th notes + 8 ornament "cuts").
Method : SP-080 -> sound.generators.cadence_variator (CadenceEngine + FluxRandomizer,
         Emergence Audio "Envoy" style). ABSOLUTE layer: two CadenceLayers
         (Envoy's two-layer design) drive time-varying gain/pan/LP-filter
         modulation over the FluidSynth dry render; no new notes written.

Pre-flight: 3-rule audit -> remove 8 off-grid ornament "cut" grace notes
         (+30-tick, velocity 90) -> snap 2 out-of-scale notes (C#5=73->D5=74,
         G#4=68->A4=69, leading-tone resolutions) -> re-audit all-0.
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
from sound.render.pipeline import RenderPipeline
from sound.generators.cadence_variator import CadenceEngine, FluxRandomizer
from sound.effects.filter import StateVariableFilter
from sound.effects.reverb import AlgorithmicReverb
from sound.effects.mastering import normalize_to_lufs, measure_lufs, Limiter, target_for_style

# ---------------------------------------------------------------------------
SRC = Path("/opt/data/repos/musicom/projects/Styles/Celtic / Irish Traditional/"
           "034-irish-jig-study/MIDI/irish_jig.mid")
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/"
           "SP080-cadence-variator-034-irish-jig-study")
AUD = OUT / "Audio"
STEMS_DRY = AUD / "stems_dry"
STEMS_WET = AUD / "stems_wet"
MIDIDIR = OUT / "MIDI"
ANALYSIS = OUT / "Analysis"
SCRIPTS = OUT / "Scripts"

for d in (AUD, STEMS_DRY, STEMS_WET, MIDIDIR, ANALYSIS, SCRIPTS):
    d.mkdir(parents=True, exist_ok=True)

SR = 44100
TPB = 480
BPM = 120.0
BAR = 1920
N_BARS = 6
TOTAL_TICKS = BAR * N_BARS          # 11520
SEED = 20261102
GRID = 240                          # 8th note

GMAJ = {0, 2, 4, 6, 7, 9, 11}       # G A B C D E F#
# progression (beat-1 anchored): G | D | C | G | C | D
PROG = {0: ("G", {7, 11, 2}), 1: ("D", {2, 6, 9}), 2: ("C", {0, 4, 7}),
        3: ("G", {7, 11, 2}), 4: ("C", {0, 4, 7}), 5: ("D", {2, 6, 9})}

SF = discover_soundfont()
FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"


def parse_notes(path):
    mid = mido.MidiFile(str(path))
    tpb = mid.ticks_per_beat
    notes = []
    for tr in mid.tracks:
        t = 0
        active = {}
        for m in tr:
            t += m.time
            if m.type == "note_on" and m.velocity > 0:
                active[m.note] = (t, m.velocity)
            elif m.type == "note_off" or (m.type == "note_on" and m.velocity == 0):
                if m.note in active:
                    st, vel = active.pop(m.note)
                    if m.note > 0:
                        notes.append({"pitch": m.note, "vel": vel, "start": st, "end": t})
    return tpb, notes


def audit(notes):
    grid_off = out_scale = out_chord = 0
    for n in notes:
        p, st = n["pitch"], n["start"]
        pc = p % 12
        bar = min(st // BAR, N_BARS - 1)
        if st % GRID != 0:
            grid_off += 1
        if pc not in GMAJ:
            out_scale += 1
        # beat-1 harmonic anchor must be a chord tone of its bar
        if (st % BAR) == 0 and pc not in PROG[bar][1]:
            out_chord += 1
    return {"grid_off": grid_off, "out_scale": out_scale, "out_chord": out_chord,
            "total_notes": len(notes)}


def read_wav(p):
    with wave.open(str(p), "rb") as wf:
        nch = wf.getnchannels()
        sr = wf.getframerate()
        data = wf.readframes(wf.getnframes())
        x = np.frombuffer(data, dtype=np.int16).astype(np.float64) / 32768.0
        if nch == 1:
            return np.vstack([x, x]), sr
        return x.reshape(-1, nch).T, sr


def write_wav(p, audio, sr=SR):
    audio = np.clip(np.asarray(audio, dtype=np.float64), -1.0, 1.0)
    if audio.ndim == 1:
        nch, inter = 1, audio
    elif audio.shape[0] == 2:
        nch, inter = 2, audio.T.reshape(-1)      # channel-major (2, N)
    elif audio.ndim == 2 and audio.shape[1] == 2:
        nch, inter = 2, audio.reshape(-1)        # time-major (N, 2)
    else:
        nch, inter = audio.shape[0], audio.T.reshape(-1)
    data = (inter * 32767.0).astype(np.int16).tobytes()
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


# ===========================================================================
# 1. Pre-flight audit (before) + copy source
# ===========================================================================
shutil.copy2(str(SRC), str(MIDIDIR / "source_original.mid"))
shutil.copy2(str(SRC), str(MIDIDIR / "irish_jig-phase1.mid"))
tpb, src_notes = parse_notes(SRC)
before = audit(src_notes)
print("PREFLIGHT before:", before)

# ===========================================================================
# 2. Rework: drop ornament cuts (off-grid), snap 2 out-of-scale notes
# ===========================================================================
keep = []
for n in src_notes:
    if n["start"] % GRID != 0:
        continue                 # drop ornament "cut" (non-structural, +30 tick)
    p = n["pitch"]
    if p == 73:
        p = 74                   # C#5 -> D5 (leading-tone resolution, G major)
    elif p == 68:
        p = 69                   # G#4 -> A4 (leading-tone resolution, G major)
    keep.append({"pitch": p, "vel": n["vel"], "start": n["start"], "end": n["end"]})

norm = MIDIDIR / "composition.mid"
mid = mido.MidiFile(ticks_per_beat=TPB)
t0 = mido.MidiTrack()
t0.append(mido.MetaMessage("set_tempo", tempo=int(round(60000000 / BPM)), time=0))
t0.append(mido.MetaMessage("time_signature", numerator=4, denominator=4, time=0))
t0.append(mido.MetaMessage("end_of_track", time=TOTAL_TICKS))
mid.tracks.append(t0)
t1 = mido.MidiTrack()
t1.append(mido.Message("program_change", program=73, channel=0, time=0))
evs = []
for n in keep:
    evs.append((n["start"], "on", n["pitch"], n["vel"]))
    evs.append((n["end"], "off", n["pitch"], 0))
evs.sort(key=lambda x: (x[0], 0 if x[1] == "off" else 1))
prev = 0
for t, kind, p, v in evs:
    dt = max(0, t - prev)
    t1.append(mido.Message("note_on" if kind == "on" else "note_off",
                           note=p, velocity=v, channel=0, time=dt))
    prev = t
t1.append(mido.MetaMessage("end_of_track", time=max(0, TOTAL_TICKS - prev)))
mid.tracks.append(t1)
mid.save(str(norm))

after = audit(keep)
print("PREFLIGHT after :", after)
assert after["grid_off"] == 0, "grid sync failing after rework"
assert after["out_scale"] == 0, "out-of-scale failing after rework"
assert after["out_chord"] == 0, "out-of-chord failing after rework"
assert os.path.getsize(str(norm)) > 40, "reworked MIDI empty"

(ANALYSIS / "rework_audit.json").write_text(json.dumps({
    "before": before, "after": after,
    "rework": "dropped 8 ornament 'cut' grace notes (start%240==30, velocity 90) "
              "for grid sync; snapped C#5(73)->D5(74) and G#4(68)->A4(69) "
              "(leading-tone resolutions into G major); source preserved as "
              "source_original.mid + irish_jig-phase1.mid",
}, indent=2))

# ===========================================================================
# 3. Dry render (FluidSynth) + stems
# ===========================================================================
print("SoundFont:", SF)

def render(midi_path, out_wav):
    r = subprocess.run([FLUID, "-ni", "-R", "0", "-C", "0", "-g", "1.2",
                        "-F", str(out_wav), SF, str(midi_path)],
                       capture_output=True, text=True, timeout=900)
    if r.returncode != 0 or not out_wav.exists() or out_wav.stat().st_size < 1000:
        raise RuntimeError("FluidSynth render failed: %s" % r.stderr[-500:])
    return out_wav

dry_wav = OUT / "dry_full_mix_jig_reference.wav"
render(norm, dry_wav)
print("dry reference:", dry_wav.stat().st_size, "bytes")

pipe = RenderPipeline(soundfont_path=SF, fluidsynth_bin=FLUID, sample_rate=SR)
dry_stems_raw = pipe.render_stems(str(norm), str(STEMS_DRY), format="wav")
print("dry stems:", sorted(dry_stems_raw.keys()))

dry_audio = {}
max_len = 0
for sname, spath in sorted(dry_stems_raw.items()):
    arr, _sr = read_wav(spath)
    dry_audio[sname] = arr
    max_len = max(max_len, arr.shape[1])
for sname in dry_audio:
    if dry_audio[sname].shape[1] < max_len:
        pad = np.zeros((2, max_len - dry_audio[sname].shape[1]), dtype=np.float64)
        dry_audio[sname] = np.hstack([dry_audio[sname], pad])
print("max stem length %d samples (%.2fs)" % (max_len, max_len / SR))

# ===========================================================================
# 4. SP-080 Cadence Engine — two layers (Envoy design) over each stem
# ===========================================================================
stem_configs = {
    "jig": {"role": "Flute Melody (single voice)", "hp_base": 200.0, "lp_base": 9000.0,
            "pan_width": 0.0, "gain": 1.0},
}

wet_stems = {}
mix_bus = np.zeros((2, max_len), dtype=np.float64)

for sidx, (sname, arr) in enumerate(sorted(dry_audio.items())):
    cfg = list(stem_configs.values())[0]
    print("voice (%s): role=%s" % (sname, cfg["role"]))

    eng = CadenceEngine(bpm=BPM, master_lfo_rate=0.7, seed=SEED + sidx)
    low = eng.add_layer(name="low", block_steps=[8, 6, 8, 7], rate=2.0,
                        direction="forward", feel="straight", root=62, gain=1.05)
    high = eng.add_layer(name="high", block_steps=[7, 5, 8, 8], rate=3.0,
                         direction="pingpong", feel="swing", root=74, gain=0.95)
    low.lfo_rate, low.lfo_depth = 0.30, 0.20
    high.lfo_rate, high.lfo_depth = 0.45, 0.25

    for layer, pbase in ((low, -0.20), (high, 0.25)):
        for bidx, b in enumerate(layer.blocks):
            for st in range(b.steps):
                mod = 1.0 + 0.3 * np.sin(2.0 * np.pi * st / b.steps)
                b.set_step(
                    st,
                    velocity=100.0 + 15.0 * np.cos(np.pi * st / max(1, b.steps)),
                    pan=float(np.clip(pbase + 0.15 * (1 if st % 2 == 0 else -1), -1.0, 1.0)),
                    hp=float(cfg["hp_base"] * mod),
                    lp=float(cfg["lp_base"] * mod),
                )

    eng.flux = FluxRandomizer(depth=0.22, blocks=[0, 2], seed=SEED + sidx * 17)

    # loops must cover max_len for the fastest layer (high, rate 3)
    step_s_hi = eng.step_seconds(high)
    needed = int(np.ceil((max_len / SR) / step_s_hi))
    loops = int(np.ceil(needed / max(1, high.total_steps))) + 1
    events = eng.render_events(loops=loops, seed=SEED + sidx * 23, apply_flux=True)
    print("   %d cadence events over %d loops" % (len(events), loops))

    gain_curve = np.ones(max_len, dtype=np.float64)
    pan_curve = np.full(max_len, cfg["pan_width"], dtype=np.float64)
    lp_curve = np.full(max_len, cfg["lp_base"], dtype=np.float64)

    for ev in events:
        i_start = int(ev["start"] * SR)
        i_end = min(max_len, int((ev["start"] + ev["length"]) * SR))
        if i_start >= max_len or i_end <= i_start:
            continue
        vel_scale = ev["velocity"] / 100.0
        lfo = ev["lfo"]
        gain_curve[i_start:i_end] = 1.0 + 0.22 * (vel_scale - 1.0) + 0.15 * lfo
        pan_curve[i_start:i_end] = ev["pan"] + 0.10 * lfo
        lp_curve[i_start:i_end] = np.clip(ev["lp"] * (1.0 + 0.20 * lfo), 400.0, 11000.0)

    svf_l = StateVariableFilter(sample_rate=SR)
    svf_r = StateVariableFilter(sample_rate=SR)
    filtered = np.zeros_like(arr)
    blk = 256
    for b0 in range(0, max_len, blk):
        b1 = min(max_len, b0 + blk)
        cur_lp = float(np.mean(lp_curve[b0:b1]))
        filtered[0, b0:b1] = svf_l.process(arr[0, b0:b1], cutoff=cur_lp, mode="lp")
        filtered[1, b0:b1] = svf_r.process(arr[1, b0:b1], cutoff=cur_lp, mode="lp")

    pan_c = np.clip(pan_curve, -1.0, 1.0)
    pan_angle = (pan_c + 1.0) * (np.pi / 4.0)
    left = np.cos(pan_angle) * gain_curve * cfg["gain"]
    right = np.sin(pan_angle) * gain_curve * cfg["gain"]
    wet = np.zeros_like(arr)
    wet[0] = filtered[0] * left
    wet[1] = filtered[1] * right

    stem_pk = float(np.max(np.abs(wet)))
    if stem_pk > 1e-9:
        wet = wet * (0.89 / stem_pk)

    stem_out = STEMS_WET / ("%s_CADENCE.wav" % sname)
    write_wav(stem_out, wet)
    wet_stems[sname] = str(stem_out)
    print("   wet stem %s: %d B peak=%.3f" % (sname, stem_out.stat().st_size,
                                              float(np.max(np.abs(wet)))))
    mix_bus += wet

# ===========================================================================
# 5. Master bus
# ===========================================================================
print("master bus...")
rev = AlgorithmicReverb(sample_rate=SR, room_size=0.55, damping=0.45,
                        wet_dry=0.10, width=0.85)
mix_rev = rev.process(mix_bus.T)          # time-major (N, 2)
TARGET_LUFS = target_for_style("celtic")
mix_lufs = normalize_to_lufs(mix_rev, target_lufs=TARGET_LUFS, sample_rate=SR)
final = Limiter(threshold_db=-1.0, release_ms=80.0).process(mix_lufs)   # (N, 2)
lufs_val = float(measure_lufs(final, SR))
peak_val = float(np.max(np.abs(final)))
print("LUFS=%.2f peak=%.4f dur=%.2fs" % (lufs_val, peak_val, final.shape[0] / SR))

WET_WAV = OUT / "SP080-cadence-variator-034-irish-jig-study.wav"
write_wav(WET_WAV, final)
print("wet WAV %d B" % WET_WAV.stat().st_size)

WET_OGG = OUT / "SP080-cadence-variator-034-irish-jig-study.ogg"
r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(WET_WAV),
                    "-codec:a", "libopus", "-application", "voip", "-b:a", "48k",
                    str(WET_OGG)], capture_output=True, text=True, timeout=180)
assert r.returncode == 0 and WET_OGG.stat().st_size > 10000, "ogg encode failed"
print("OGG %d B" % WET_OGG.stat().st_size)

# ===========================================================================
# 6. Verification
# ===========================================================================
final_cm = final.T                                  # (2, N) channel-major
mono = 0.5 * (final_cm[0] + final_cm[1])
silence_pct = float(np.sum(np.abs(mono) < 0.001) / len(mono)) * 100.0
rms = float(np.sqrt(np.mean(mono ** 2)))
rms_map = [round(float(np.sqrt(np.mean(mono[i:i + SR] ** 2))), 4)
           for i in range(0, len(mono), SR)]
print("silence=%.2f%% rms=%.4f" % (silence_pct, rms))


def pitch_verify(audio_2n, pcs):
    m = 0.5 * (audio_2n[0] + audio_2n[1])
    wl = int(0.5 * SR)
    nw = len(m) // wl
    hits = valid = 0
    he_list = []
    for w in range(nw):
        seg = m[w * wl:(w + 1) * wl]
        if np.max(np.abs(seg)) < 0.01:
            continue
        valid += 1
        win = np.hanning(len(seg))
        spec = np.abs(np.fft.rfft(seg * win))
        freqs = np.fft.rfftfreq(len(seg), 1.0 / SR)
        mask = (freqs >= 50.0) & (freqs <= 1000.0)
        sub, subf = spec[mask], freqs[mask]
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


dry_audio_mix, _sr = read_wav(dry_wav)
hit_rate, he_mean, valid = pitch_verify(final_cm, GMAJ)
dry_hit, dry_he, dry_valid = pitch_verify(dry_audio_mix, GMAJ)
he_retention = (he_mean / dry_he) if dry_he > 0 else 0.0
pitch_verdict = "PASS" if (hit_rate >= 0.60 and he_mean >= 0.30) else "FAIL"
print("Pitch verify: valid=%d hit=%.4f HE=%.4f | dry hit=%.4f HE=%.4f | retention=%.3f -> %s"
      % (valid, hit_rate, he_mean, dry_hit, dry_he, he_retention, pitch_verdict))

# ===========================================================================
# 7. Provenance + stats
# ===========================================================================
(ANALYSIS / "render_stats.json").write_text(json.dumps({
    "lufs": lufs_val, "peak": peak_val, "silence_pct": silence_pct,
    "rms": rms, "rms_per_sec": rms_map,
    "hit_rate": hit_rate, "mean_harmonic_energy": he_mean, "valid_windows": valid,
    "dry_hit_rate": dry_hit, "dry_he": dry_he, "he_retention": he_retention,
    "pitch_verdict": pitch_verdict,
    "n_cadence_events": len(events), "n_stems": len(dry_stems_raw),
}, indent=2))

provenance = {
    "job": "random-style production (SP) layer-aligned",
    "date": "2026-11-02",
    "seed": SEED,
    "method": "SP-080",
    "method_module": "sound.generators.cadence_variator",
    "method_desc": "Cadence Engine Rhythmic Variator w/ Flux Randomizer (Emergence Audio Envoy-style)",
    "layer": "ABSOLUTE",
    "params": {
        "sample_rate": SR, "bpm": BPM, "ppqn": TPB,
        "master_lfo_rate": 0.7,
        "layers": [
            {"name": "low", "block_steps": [8, 6, 8, 7], "rate": 2.0,
             "direction": "forward", "feel": "straight", "root": 62, "gain": 1.05},
            {"name": "high", "block_steps": [7, 5, 8, 8], "rate": 3.0,
             "direction": "pingpong", "feel": "swing", "root": 74, "gain": 0.95},
        ],
        "flux_depth": 0.22, "flux_blocks": [0, 2],
        "carrier": "FluidSynth SP-001 (flute program 73)",
        "reverb": {"room_size": 0.55, "damping": 0.45, "wet_dry": 0.10, "width": 0.85},
        "target_lufs": TARGET_LUFS, "ceiling_db": -1.0,
    },
    "source_midi": str(SRC),
    "normalized_midi": str(norm),
    "source_bpm": BPM,
    "source_pitch_classes": sorted(GMAJ),
    "progression": ["G", "D", "C", "G", "C", "D"],
    "rework": "dropped 8 ornament cuts; 73->74, 68->69",
    "output_wav": str(WET_WAV),
    "output_ogg": str(WET_OGG),
    "lufs": lufs_val, "peak": peak_val, "silence_pct": silence_pct, "rms": rms,
    "pitch_verdict": pitch_verdict, "hit_rate": hit_rate, "he_mean": he_mean,
    "dry_he": dry_he, "he_retention": he_retention,
    "preflight_before": before, "preflight_after": after,
}
(OUT / "provenance.json").write_text(json.dumps(provenance, indent=2))

try:
    shutil.copy2(__file__, str(SCRIPTS / "produce_sp080_cron.py"))
except shutil.SameFileError:
    pass

print("Done.")
