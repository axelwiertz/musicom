# -*- coding: utf-8 -*-
"""SP-117 Reverse Reverb production pass (absolute layer).

Source : Styles/Electronic/089-electronic-subset-minor/MIDI/089-electronic-subset-minor.mid
         (24-bar 6-voice electronic subset-walk piece, A natural minor, 112 BPM,
          4/4, 480 TPB, 24 bars = 46080 ticks. Voices: Lead Marimba (prog 12,
          ch0, 219 notes), Clarinet (prog 71, ch1, 96), Cello (prog 42, ch2,
          72), Dulcimer (prog 15, ch3, 384), Bass (prog 43, ch4, 192), Drums
          (ch9, 300). 963 pitched notes + 300 drum hits.
Method : SP-117 -> sound.effects.reverse_reverb (ReverseReverb, Bixlab-style).
         ABSOLUTE layer: reverse -> IR convolution -> reverse-back swelling
         wash applied to the whole FluidSynth dry render; no new notes.

Pre-flight: 3-rule audit -> expected clean (compose.py was grid/harmony
         quantized, audit.py already PASSED). Re-verify here.
"""
import hashlib
import json
import shutil
import subprocess
import wave
from pathlib import Path

import numpy as np
import mido

from sound.render.fluidsynth import discover_soundfont
from sound.render.pipeline import RenderPipeline
from sound.effects.reverse_reverb import ReverseReverb
from sound.effects.mastering import normalize_to_lufs, measure_lufs, Limiter, target_for_style

SRC = Path("/opt/data/repos/musicom/projects/Styles/Electronic/"
           "089-electronic-subset-minor/MIDI/089-electronic-subset-minor.mid")
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/"
           "SP117-reverse-reverb-089-electronic-subset-minor")
AUD = OUT / "Audio"
STEMS_DRY = AUD / "stems_dry"
MIDIDIR = OUT / "MIDI"
ANALYSIS = OUT / "Analysis"
SCRIPTS = OUT / "Scripts"

for d in (AUD, STEMS_DRY, MIDIDIR, ANALYSIS, SCRIPTS):
    d.mkdir(parents=True, exist_ok=True)

SR = 44100
TPB = 480
BPM = 112.0
BAR = 1920
N_BARS = 24
TOTAL_TICKS = BAR * N_BARS          # 46080
SEED = 20261104
GRID = 120                          # 16th-note grid

# A natural minor pitch classes: A B C D E F G
AMIN = {9, 11, 0, 2, 4, 5, 7}

# per-bar chord subset (from summary.json progression / audit.py)
PROG = ['min9', 'min4', 'maj5', 'maj0', 'maj5', 'maj0', 'dom77', 'min72',
        'dom77', 'min74', 'dom77', 'maj70', 'maj7', 'min4', 'min2', 'maj5',
        'min2', 'min4', 'maj5', 'maj0', 'min2', 'maj0', 'dom77', 'min9']
CHORD_PCS = {  # from rules.subset_network standard_patterns subsets
    'min9': {0, 4, 9}, 'min4': {4, 7, 11}, 'maj5': {0, 5, 9},
    'maj0': {0, 4, 7}, 'dom77': {2, 5, 7, 11}, 'min72': {0, 2, 5, 9},
    'min74': {2, 4, 7, 11}, 'maj70': {0, 4, 7, 11}, 'maj7': {2, 7, 11},
    'min2': {2, 5, 9},
}
PITCHED_CHANNELS = {0, 1, 2, 3, 4}
VOICE_NAMES = {0: "Lead(Marimba)", 1: "Clarinet", 2: "Cello",
               3: "Dulcimer", 4: "Bass", 9: "Drums"}

SF = discover_soundfont()
FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"


def parse_notes(path):
    mid = mido.MidiFile(str(path))
    notes = []
    track_lens = []
    for tr in mid.tracks:
        t = 0
        active = {}
        for m in tr:
            t += m.time
            if m.type == "note_on" and m.velocity > 0:
                active[(m.channel, m.note)] = t
            elif m.type == "note_off" or (m.type == "note_on" and m.velocity == 0):
                key = (m.channel, m.note)
                if key in active:
                    st = active.pop(key)
                    notes.append({"ch": m.channel, "pitch": m.note, "start": st, "end": t})
        track_lens.append(t)
    return mid, notes, track_lens


def audit(notes):
    grid_off = out_scale = out_chord = 0
    for n in notes:
        ch, p, st = n["ch"], n["pitch"], n["start"]
        if ch not in PITCHED_CHANNELS:
            continue
        pc = p % 12
        bar = min(st // BAR, N_BARS - 1)
        if st % GRID != 0:
            grid_off += 1
        if pc not in AMIN:
            out_scale += 1
        if pc not in CHORD_PCS[PROG[bar]]:
            out_chord += 1
    return {"grid_off": grid_off, "out_scale": out_scale, "out_chord": out_chord,
            "total_pitched_notes": sum(1 for n in notes if n["ch"] in PITCHED_CHANNELS)}


def read_wav(p):
    with wave.open(str(p), "rb") as wf:
        nch = wf.getnchannels()
        sr = wf.getframerate()
        data = wf.readframes(wf.getnframes())
        x = np.frombuffer(data, dtype=np.int16).astype(np.float64) / 32768.0
        if nch == 1:
            return np.vstack([x, x]), sr
        return x.reshape(-1, nch).T, sr          # (2, N) channel-major


def write_wav(p, audio, sr=SR):
    audio = np.clip(np.asarray(audio, dtype=np.float64), -1.0, 1.0)
    if audio.ndim == 1:
        nch, inter = 1, audio
    elif audio.shape[0] == 2:
        nch, inter = 2, audio.T.reshape(-1)
    else:
        nch, inter = 2, audio.reshape(-1)
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
shutil.copy2(str(SRC), str(MIDIDIR / "composition.mid"))   # no rework expected
mid, src_notes, track_lens = parse_notes(SRC)
before = audit(src_notes)
print("PREFLIGHT before:", before)
print("track lengths (ticks):", track_lens)

assert before["grid_off"] == 0, "unexpected off-grid onsets"
assert before["out_scale"] == 0, "unexpected out-of-scale notes"
assert before["out_chord"] == 0, "unexpected out-of-chord notes"

note_lens = track_lens[1:]
assert len(set(note_lens)) == 1, "zero-drift violation"
print("zero-drift OK: all", len(note_lens), "note tracks len", note_lens[0])

after = dict(before)
(ANALYSIS / "rework_audit.json").write_text(json.dumps({
    "before": before, "after": after,
    "rework": "NONE — source 089-electronic-subset-minor already passes the "
              "3-rule gate (0 off-grid @16th, 0 out-of-scale, 0 out-of-chord, "
              "zero-drift 46080-tick tracks). composition.mid is a byte copy "
              "of source.",
}, indent=2))

# ===========================================================================
# 2. Dry render (FluidSynth) + stems
# ===========================================================================
print("SoundFont:", SF)


def render(midi_path, out_wav):
    r = subprocess.run([FLUID, "-ni", "-R", "0", "-C", "0", "-g", "1.2",
                        "-F", str(out_wav), SF, str(midi_path)],
                       capture_output=True, text=True, timeout=900)
    if r.returncode != 0 or not out_wav.exists() or out_wav.stat().st_size < 1000:
        raise RuntimeError("FluidSynth render failed: %s" % r.stderr[-500:])
    return out_wav


dry_wav = OUT / "dry_full_mix_reference.wav"
render(MIDIDIR / "composition.mid", dry_wav)
print("dry reference:", dry_wav.stat().st_size, "bytes")

pipe = RenderPipeline(soundfont_path=SF, fluidsynth_bin=FLUID, sample_rate=SR)
dry_stems_raw = pipe.render_stems(str(MIDIDIR / "composition.mid"), str(STEMS_DRY), format="wav")
print("dry stems:", sorted(dry_stems_raw.keys()))

# ===========================================================================
# 3. SP-117 Reverse Reverb — absolute layer over the full dry mix
# ===========================================================================
dry_audio, _sr = read_wav(dry_wav)
print("dry mix shape", dry_audio.shape, "dur %.2fs" % (dry_audio.shape[1] / SR))

# reverse-reverb wash params (Bixlab workflow: reverse -> IR conv -> reverse back)
DECAY = 2.0
WET = 0.40
PRE_DELAY_MS = 20.0
IR_DENSITY = 0.9
IR_SEED = SEED
FADE_MS = 15.0

rr = ReverseReverb(sample_rate=SR)

wet_L = rr.process(dry_audio[0], decay_sec=DECAY, wet=WET, pre_delay_ms=PRE_DELAY_MS,
                   align_to_hit=False, fade_ms=FADE_MS, ir_density=IR_DENSITY, ir_seed=IR_SEED)
wet_R = rr.process(dry_audio[1], decay_sec=DECAY, wet=WET, pre_delay_ms=PRE_DELAY_MS,
                   align_to_hit=False, fade_ms=FADE_MS, ir_density=IR_DENSITY, ir_seed=IR_SEED)
wet = np.vstack([wet_L, wet_R])                    # (2, N)
print("wet mix shape", wet.shape, "dur %.2fs" % (wet.shape[1] / SR))

wet_stem = STEMS_DRY / "full_mix_REVERSE_REVERB.wav"
write_wav(wet_stem, wet)
print("reverse-reverb wav:", wet_stem.stat().st_size, "bytes")

# ===========================================================================
# 4. Master bus
# ===========================================================================
STYLE = "electronic"
TARGET_LUFS = target_for_style(STYLE)
print("target_lufs(%s) = %.1f" % (STYLE, TARGET_LUFS))
wet_tm = wet.T                                     # time-major (N, 2)
mix_lufs = normalize_to_lufs(wet_tm, target_lufs=TARGET_LUFS, sample_rate=SR)
final = Limiter(threshold_db=-1.0, release_ms=80.0).process(mix_lufs)
lufs_val = float(measure_lufs(final, SR))
peak_val = float(np.max(np.abs(final)))
print("LUFS=%.2f peak=%.4f dur=%.2fs" % (lufs_val, peak_val, final.shape[0] / SR))

WET_WAV = OUT / "SP117-reverse-reverb-089-electronic-subset-minor.wav"
write_wav(WET_WAV, final)
print("wet WAV %d B" % WET_WAV.stat().st_size)

WET_OGG = OUT / "SP117-reverse-reverb-089-electronic-subset-minor.ogg"
r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(WET_WAV),
                    "-codec:a", "libopus", "-application", "voip", "-b:a", "48k",
                    str(WET_OGG)], capture_output=True, text=True, timeout=180)
assert r.returncode == 0 and WET_OGG.stat().st_size > 10000, "ogg encode failed"
print("OGG %d B" % WET_OGG.stat().st_size)

# ===========================================================================
# 5. Verification
# ===========================================================================
final_cm = final.T                                  # (2, N)
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


dry_audio_mix, _sr2 = read_wav(dry_wav)
hit_rate, he_mean, valid = pitch_verify(final_cm, AMIN)
dry_hit, dry_he, dry_valid = pitch_verify(dry_audio_mix, AMIN)
he_retention = (he_mean / dry_he) if dry_he > 0 else 0.0
pitch_verdict = "PASS" if (hit_rate >= 0.60 and he_mean >= 0.30) else "FAIL"
print("Pitch verify: valid=%d hit=%.4f HE=%.4f | dry hit=%.4f HE=%.4f | retention=%.3f -> %s"
      % (valid, hit_rate, he_mean, dry_hit, dry_he, he_retention, pitch_verdict))

# ===========================================================================
# 6. Provenance + stats
# ===========================================================================
(ANALYSIS / "render_stats.json").write_text(json.dumps({
    "lufs": lufs_val, "peak": peak_val, "silence_pct": silence_pct,
    "rms": rms, "rms_per_sec": rms_map,
    "hit_rate": hit_rate, "mean_harmonic_energy": he_mean, "valid_windows": valid,
    "dry_hit_rate": dry_hit, "dry_he": dry_he, "he_retention": he_retention,
    "pitch_verdict": pitch_verdict,
    "decay_sec": DECAY, "wet": WET, "pre_delay_ms": PRE_DELAY_MS,
    "ir_density": IR_DENSITY, "ir_seed": IR_SEED, "fade_ms": FADE_MS,
    "n_stems": len(dry_stems_raw),
}, indent=2))

provenance = {
    "job": "random-style production (SP) layer-aligned",
    "date": "2026-11-04",
    "seed": SEED,
    "method": "SP-117",
    "method_module": "sound.effects.reverse_reverb",
    "method_desc": "Reverse Reverb — reverse -> IR convolution (decaying-noise reverb, pre-delay) -> reverse back -> wet/dry mix, align-to-hit trimming + boundary fades (Bixlab Reverse Reverb-style)",
    "layer": "ABSOLUTE",
    "params": {
        "sample_rate": SR, "bpm": BPM, "ppqn": TPB,
        "decay_sec": DECAY, "wet": WET, "pre_delay_ms": PRE_DELAY_MS,
        "ir_density": IR_DENSITY, "ir_seed": IR_SEED, "fade_ms": FADE_MS,
        "align_to_hit": False,
        "carrier": "FluidSynth SP-001 (Marimba 12 + Clarinet 71 + Cello 42 + Dulcimer 15 + Bass 43 + Drums ch9)",
        "target_lufs": TARGET_LUFS, "ceiling_db": -1.0,
    },
    "source_midi": str(SRC),
    "normalized_midi": str(MIDIDIR / "composition.mid"),
    "source_bpm": BPM,
    "source_style": STYLE,
    "source_pitch_classes": sorted(AMIN),
    "progression": PROG,
    "rework": "NONE (source already clean)",
    "output_wav": str(WET_WAV),
    "output_ogg": str(WET_OGG),
    "lufs": lufs_val, "peak": peak_val, "silence_pct": silence_pct, "rms": rms,
    "pitch_verdict": pitch_verdict, "hit_rate": hit_rate, "he_mean": he_mean,
    "dry_he": dry_he, "he_retention": he_retention,
    "preflight_before": before, "preflight_after": after,
    "source_sha256": sha256(SRC),
    "composition_sha256": sha256(MIDIDIR / "composition.mid"),
}
(OUT / "provenance.json").write_text(json.dumps(provenance, indent=2))

try:
    shutil.copy2(__file__, str(SCRIPTS / "produce_sp117_cron.py"))
except shutil.SameFileError:
    pass

print("Done. pitch_verdict=%s" % pitch_verdict)
