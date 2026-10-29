# -*- coding: utf-8 -*-
"""SP-127 drumline (Ten-Model Drum Synthesizer + Funk Humaniser) production pass.

Source : Styles/Groove/258-groove-rbn-critical
         (A natural minor funk groove, 104 BPM, 4/4, 480 TPB, 24 bars =
          46080 ticks; 5 voices: clavi 7 / rhodes 4 / bass 33 / pad 88 +
          groove drums ch9 - kick36 x72, snare38 x48, closed-hat42 x384,
          open-hat46 x8).

Method : SP-127 -> sound.generators.drumline (Drumline + DynamicFilter,
         OP-XY drumline-style). ABSOLUTE layer on the DRUM/percussion layer:
         the whole kit is re-synthesised from the 10 drumline models (kick /
         snare / rim / hat_closed / hat_open / conga_low / conga_high /
         shaker / clap / tom) with the "funk" humaniser.  drumline is a
         DRUM-only synth (no pitched models), so the A-minor harmonic/melodic
         layer (clavi / rhodes / bass / pad) is carried by the FluidSynth
         SP-001 carrier (pitched voices only, drum track stripped) - the same
         carrier convention the SP-074 drum-machine pass used for key/genre
         context.  The drum production layer is replaced ABSOLUTELY (0 of the
         source's 512 GM drum hits survive; all drums are drumline).

Pipeline: source perfect MIDI -> 3-rule pre-flight audit (grid/harmony/zero-drift)
          -> extract ch9 drum groove -> drumline 10-model synthesis (funk)
          -> pitched carrier MIDI (ch9 stripped) -> FluidSynth SP-001 render
          -> mix (drum bus + pitched bus) -> master() (groove -14 LUFS, -1 dBTP)
          -> WAV + Opus OGG -> stems (per-model drums + pitched carrier)
          -> pitch/grid/silence/RMS verification -> REPORT.md.
"""
import json
import os
import subprocess
from pathlib import Path

import numpy as np
import mido

from sound.generators.drumline import Drumline, DynamicFilter, MODELS
from sound.render.fluidsynth import discover_soundfont
from sound.effects.mastering import master, target_for_style, measure_lufs
from sound.utils.io import read_wav, write_wav

# ---- paths -------------------------------------------------------------
SRC_HUMANIZED = Path("/opt/data/repos/musicom/projects/Styles/Groove/"
                     "258-groove-rbn-critical/MIDI/258-groove-rbn-critical-humanized.mid")
SRC = Path("/opt/data/repos/musicom/projects/Styles/Groove/"
           "258-groove-rbn-critical/MIDI/258-groove-rbn-critical-perfect.mid")
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/"
           "SP127-drumline-258-groove-rbn-critical")
AUD = OUT / "Audio"
STEMS = AUD / "stems"
MIDIDIR = OUT / "MIDI"
ANALYSIS = OUT / "Analysis"
SCRIPTS = OUT / "Scripts"

for d in (AUD, STEMS, MIDIDIR, ANALYSIS, SCRIPTS):
    d.mkdir(parents=True, exist_ok=True)

# ---- constants ---------------------------------------------------------
SR = 44100
BPM = 104.0
TPB = 480
BAR = 1920                 # 4/4 bar
N_BARS = 24
TOTAL_TICKS = BAR * N_BARS  # 46080
GRID = 120                  # 16th note
BAR_SAMPLES = int(round(60.0 / BPM * 4 * SR))   # 101769
SEED = 20261029
STYLE = "Groove"
FUNK = 0.35                 # the method's "funk humaniser"

# A natural minor pitch classes: A B C D E F G
AMIN_PCS = {9, 11, 0, 2, 4, 5, 7}

# 24-bar 7th-chord plan (from source REPORT.md), chord-tone pitch classes
PROG = (["i7", "i7", "VI7", "VII7"] * 2 +
        ["III7", "VI7", "iv7", "v7"] * 2 +
        ["i7", "i7", "VI7", "VII7"] * 2)
CHORD_PCS = {
    "i7":   {9, 0, 4, 7},     # Am7  A C E G
    "VI7":  {5, 9, 0, 4},     # Fmaj7 F A C E
    "VII7": {7, 11, 2, 5},    # G7   G B D F
    "III7": {0, 4, 7, 11},    # Cmaj7 C E G B
    "iv7":  {2, 5, 9, 0},     # Dm7  D F A C
    "v7":   {4, 7, 11, 2},    # Em7  E G B D
}
assert len(PROG) == N_BARS

FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"

# note -> drumline model map (GM percussion)
NOTE_MODEL = {36: "kick", 38: "snare", 42: "hat_closed", 46: "hat_open"}

# per-model synth params (tone/decay/pitch/snap) - funk kit character
PARAMS = {
    "kick":       {"tone": 0.55, "decay": 0.45, "pitch": 0.30, "snap": 0.60},
    "snare":      {"tone": 0.50, "decay": 0.40, "pitch": 0.50, "snap": 0.70},
    "hat_closed": {"tone": 0.60, "decay": 0.30, "pitch": 0.50, "snap": 0.60},
    "hat_open":   {"tone": 0.60, "decay": 0.70, "pitch": 0.50, "snap": 0.50},
    "clap":       {"tone": 0.50, "decay": 0.40, "pitch": 0.50, "snap": 0.60},
    "shaker":     {"tone": 0.60, "decay": 0.50, "pitch": 0.50, "snap": 0.40},
    "rim":        {"tone": 0.50, "decay": 0.40, "pitch": 0.60, "snap": 0.60},
    "conga_low":  {"tone": 0.50, "decay": 0.50, "pitch": 0.40, "snap": 0.50},
    "conga_high": {"tone": 0.50, "decay": 0.50, "pitch": 0.60, "snap": 0.50},
    "tom":        {"tone": 0.50, "decay": 0.50, "pitch": 0.50, "snap": 0.50},
}


# =========================================================================
# 1. Pre-flight 3-rule audit (grid sync / harmony / zero-drift)
# =========================================================================
def audit(path, chord_plan):
    """3-rule audit under the source's tiered harmony discipline:
    grid sync (16th=120) + in-scale + strong-beat(1&3) in-chord.
    Weak-beat in-scale notes are passing tones (allowed), not violations."""
    mf = mido.MidiFile(str(path))
    grid_off = out_scale = strong_out_chord = weak_scale_only = 0
    strong_total = weak_total = 0
    track_ends = []
    total_notes = 0
    strong_pos = {0, 960}   # beats 1 & 3 (4/4 @ 16th grid)
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
                if pc not in AMIN_PCS:
                    out_scale += 1
                bar = min(t // BAR, N_BARS - 1)
                in_chord = pc in CHORD_PCS[chord_plan[bar]]
                if (t % BAR) in strong_pos:
                    strong_total += 1
                    if not in_chord:
                        strong_out_chord += 1
                else:
                    weak_total += 1
                    if not in_chord:
                        weak_scale_only += 1   # in-scale passing tone
        if n_notes:
            track_ends.append(t)
    zero_drift = len(set(track_ends)) == 1
    return {"grid_off": grid_off, "out_scale": out_scale,
            "strong_out_chord": strong_out_chord,
            "weak_scale_only": weak_scale_only,
            "strong_total": strong_total, "weak_total": weak_total,
            "zero_drift": zero_drift, "track_ends": sorted(set(track_ends)),
            "total_notes": total_notes}


print("== pre-flight audit ==")
before = audit(SRC_HUMANIZED, PROG)   # selector's literal pick (humanized)
print("humanized (selector pick):", before)
after = audit(SRC, PROG)              # grid-locked twin = compositional truth
print("perfect (production source):", after)
assert after["grid_off"] == 0, "grid sync FAIL on perfect source"
assert after["out_scale"] == 0, "out-of-scale FAIL on perfect source"
assert after["strong_out_chord"] == 0, "strong-beat out-of-chord FAIL on perfect source"
assert after["zero_drift"], "zero-drift FAIL on perfect source"
print("PRE-FLIGHT PASS on perfect source (grid 0 / out-scale 0 / strong-out-chord 0, zero-drift).")

import shutil
shutil.copy2(str(SRC), str(MIDIDIR / "source_perfect.mid"))
shutil.copy2(str(SRC_HUMANIZED), str(MIDIDIR / "source_humanized.mid"))

# =========================================================================
# 2. Extract the source drum groove (ch9) -> per-model 16th patterns
# =========================================================================
def extract_drum_patterns(path):
    mf = mido.MidiFile(str(path))
    pats = {m: np.zeros((N_BARS, 16), dtype=np.float32) for m in NOTE_MODEL.values()}
    for tr in mf.tracks:
        chans = {m.channel for m in tr if m.type in ("note_on", "note_off")}
        if 9 not in chans:
            continue
        t = 0
        for m in tr:
            t += m.time
            if m.type == "note_on" and m.velocity > 0:
                model = NOTE_MODEL.get(m.note)
                if model is None:
                    continue
                bar = min(t // BAR, N_BARS - 1)
                step = min((t % BAR) // GRID, 15)
                v = m.velocity / 127.0
                if v > pats[model][bar, step]:
                    pats[model][bar, step] = v
    return pats


pats = extract_drum_patterns(SRC)
print("source drum hits per model:",
      {m: int(np.count_nonzero(p)) for m, p in pats.items()})

# ---- funk color models (idiomatic, documented; source carries the core 4) ----
clap_pat = (pats["snare"] * 0.55).astype(np.float32)   # clap layered on 2&4
shaker_pat = np.zeros((N_BARS, 16), dtype=np.float32)
shaker_pat[:, [0, 2, 4, 6, 8, 10, 12, 14]] = 0.35      # 8th-note shaker
conga_low_pat = np.zeros((N_BARS, 16), dtype=np.float32)
conga_low_pat[:, 6] = 0.50                              # "and of 2"
conga_high_pat = np.zeros((N_BARS, 16), dtype=np.float32)
conga_high_pat[:, 10] = 0.50                            # "and of 3"
rim_pat = np.zeros((N_BARS, 16), dtype=np.float32)
rim_pat[:, 14] = 0.45                                   # "and of 4" ghost pickup
tom_pat = np.zeros((N_BARS, 16), dtype=np.float32)
for b in (7, 15, 23):                                   # section-boundary fills
    tom_pat[b, [12, 13, 14, 15]] = [0.40, 0.50, 0.65, 0.85]

COLOR = {"clap": clap_pat, "shaker": shaker_pat,
         "conga_low": conga_low_pat, "conga_high": conga_high_pat,
         "rim": rim_pat, "tom": tom_pat}

ALL_PATTERNS = dict(pats)
ALL_PATTERNS.update(COLOR)
assert set(ALL_PATTERNS) == set(MODELS), \
    "missing models: %s" % (set(MODELS) - set(ALL_PATTERNS))

# =========================================================================
# 3. drumline synthesis (absolute drum layer, per bar -> concat, funk)
# =========================================================================
def render_model(dl, model, pattern, seed):
    chunks = []
    for bar in range(N_BARS):
        steps = [float(v) for v in pattern[bar]]
        a = dl.render(model, steps, bpm=BPM, params=PARAMS[model],
                      funk=FUNK, seed=seed * 1000 + bar)
        a = a[:BAR_SAMPLES]
        if len(a) < BAR_SAMPLES:
            a = np.pad(a, (0, BAR_SAMPLES - len(a)))
        chunks.append(a)
    return np.concatenate(chunks).astype(np.float32)


dl = Drumline(sample_rate=SR, seed=SEED)
drum_bus = np.zeros(N_BARS * BAR_SAMPLES, dtype=np.float32)
stem_paths = {}
for i, model in enumerate(MODELS):
    a = render_model(dl, model, ALL_PATTERNS[model], seed=SEED * 101 + i)
    # per-model stem (mono WAV)
    stem_wav = STEMS / ("drum_%s.wav" % model)
    write_wav(str(stem_wav), np.column_stack([a, a]).astype(np.float32),
              SR, normalize=True)
    stem_paths[model] = str(stem_wav)
    drum_bus += a

# glue: dynamic filter (HPF+LPF+comp+drive) over the summed drum bus
df = DynamicFilter(SR)
drum_bus = df.process(drum_bus, hp=25.0, lp=14000.0, drive=0.12, comp=0.45)
peak = np.max(np.abs(drum_bus))
if peak > 1e-9:
    drum_bus = (drum_bus / peak * 0.9).astype(np.float32)
print("drum bus:", len(drum_bus), "samples =",
      round(len(drum_bus) / SR, 2), "s, peak", float(np.max(np.abs(drum_bus))))

# =========================================================================
# 4. pitched carrier (ch9 stripped) -> FluidSynth SP-001 render
# =========================================================================
mf = mido.MidiFile(str(SRC))
pitched_mid = mido.MidiFile(ticks_per_beat=TPB)
kept = 0
for tr in mf.tracks:
    chans = {m.channel for m in tr if m.type in ("note_on", "note_off")}
    if 9 in chans:
        continue
    pitched_mid.tracks.append(tr)
    kept += 1
carrier_mid = MIDIDIR / "pitched_carrier.mid"
pitched_mid.save(str(carrier_mid))
print("pitched carrier MIDI:", carrier_mid, carrier_mid.stat().st_size,
      "bytes,", kept, "tracks kept")

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


carrier_wav = OUT / "pitched_carrier_sp001.wav"
fluidsynth_render(carrier_mid, carrier_wav)
print("pitched carrier WAV:", carrier_wav.stat().st_size, "bytes")

dry_wav = OUT / "dry_full_mix_sp001_reference.wav"
fluidsynth_render(SRC, dry_wav)
print("dry full-mix reference:", dry_wav.stat().st_size, "bytes")

carrier_audio, _sr = read_wav(str(carrier_wav))
if carrier_audio.ndim == 1:
    carrier_audio = np.column_stack([carrier_audio, carrier_audio])
carrier_audio = np.asarray(carrier_audio, dtype=np.float32)

# ---- per-voice stems of the pitched carrier (RenderPipeline) ------------
try:
    from sound.render.pipeline import RenderPipeline
    pipeline = RenderPipeline(soundfont_path=SF, fluidsynth_bin=FLUID,
                              sample_rate=SR)
    pitched_stems = pipeline.render_stems(str(carrier_mid), str(STEMS),
                                          format="wav")
    print("rendered %d pitched stems" % len(pitched_stems))
except Exception as e:
    pitched_stems = {}
    print("pitched stem render skipped:", repr(e)[:200])

# =========================================================================
# 5. Mix + master
# =========================================================================
n_total = min(len(drum_bus), len(carrier_audio))
drum_bus = drum_bus[:n_total]
carrier_audio = carrier_audio[:n_total]
drum_stereo = np.column_stack([drum_bus, drum_bus]).astype(np.float32)
mix = (carrier_audio * 1.0 + drum_stereo * 0.85).astype(np.float32)

TARGET_LUFS = target_for_style(STYLE)   # Groove -> -14.0
CEILING_DB = -1.0
print("mastering (target %.1f LUFS, ceiling %.1f dBTP)..." %
      (TARGET_LUFS, CEILING_DB))
mastered, rep = master(mix, target_lufs=TARGET_LUFS, ceiling_db=CEILING_DB,
                       sample_rate=SR)
print("master report: LUFS %.2f, true peak %.2f dBTP"
      % (float(rep.get("integrated_lufs", 0)), float(rep.get("true_peak_db", 0))))

final_wav = OUT / "SP127-drumline-258-groove-rbn-critical.wav"
final_ogg = OUT / "SP127-drumline-258-groove-rbn-critical.ogg"
write_wav(str(final_wav), mastered.astype(np.float32), SR, normalize=False)
r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(final_wav),
                    "-codec:a", "libopus", "-application", "voip", "-b:a", "48k",
                    str(final_ogg)], capture_output=True, text=True, timeout=180)
assert r.returncode == 0 and final_ogg.stat().st_size > 10000, \
    "ogg encode failed: %s" % r.stderr[-300:]
print("final WAV:", final_wav.stat().st_size,
      "final OGG:", final_ogg.stat().st_size)

# =========================================================================
# 6. Verification
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


# pitched carrier pitch verify (A natural minor)
hit_rate, he_mean, valid = pitch_verify(carrier_audio, AMIN_PCS)
pitch_verdict = "PASS" if (hit_rate >= 0.60 and he_mean >= 0.30) else "FAIL"
print("Pitched-carrier pitch verify: valid=%d hit=%.4f mean_HE=%.4f -> %s"
      % (valid, hit_rate, he_mean, pitch_verdict))

# drum bus rhythm grid check: envelope autocorrelation -> 16th period
drum_env = np.abs(drum_bus)
# decimate envelope to 1 kHz for speed
step = SR // 1000
env = drum_env[::step]
ac = np.correlate(env - env.mean(), env - env.mean(), mode="full")
ac = ac[len(ac) // 2:]
ac /= (ac[0] + 1e-12)
# search lag 30ms..600ms for the strongest peak
lo = int(0.030 * 1000)
hi = int(0.600 * 1000)
if len(ac) > hi:
    seg = ac[lo:hi]
    lag_ms = float((lo + int(np.argmax(seg))) / 1.0)
    strength = float(seg[int(np.argmax(seg))])
else:
    lag_ms = 0.0
    strength = 0.0
sixteenth_ms = 60000.0 / BPM / 4.0   # 144.23 ms
grid_ok = abs(lag_ms - sixteenth_ms) < 15.0
print("drum envelope grid: dominant period %.1f ms (16th=%.1f ms) -> %s"
      % (lag_ms, sixteenth_ms, "PASS" if grid_ok else "NOTE"))

# =========================================================================
# 7. Artifacts
# =========================================================================
(ANALYSIS / "render_stats.json").write_text(json.dumps({
    "lufs": meas_lufs, "peak": peak_val, "silence_pct": silence_pct,
    "rms": rms, "rms_per_sec": rms_map,
    "pitched_hit_rate": hit_rate, "pitched_mean_harmonic_energy": he_mean,
    "pitched_valid_windows": valid, "pitch_verdict": pitch_verdict,
    "drum_env_period_ms": lag_ms, "drum_env_16th_ms": sixteenth_ms,
    "drum_grid_ok": grid_ok,
    "n_drum_models": len(MODELS), "funk": FUNK,
    "n_source_drum_hits": {m: int(np.count_nonzero(p)) for m, p in pats.items()},
    "n_pitched_stems": len(pitched_stems) if isinstance(pitched_stems, dict) else 0,
    "n_drum_stems": len(stem_paths),
    "target_lufs": TARGET_LUFS,
}, indent=2))

provenance = {
    "job": "random-style production (SP) layer-aligned",
    "date": "2026-10-29",
    "seed": SEED,
    "method": "SP-127",
    "method_module": "sound.generators.drumline",
    "method_desc": "Ten-Model Drum Synthesizer + Funk Humaniser (OP-XY drumline-style)",
    "layer": "ABSOLUTE (drum/percussion layer re-synthesised by drumline; "
             "pitched A-minor layer carried by FluidSynth SP-001)",
    "params": {
        "sample_rate": SR, "bpm": BPM, "ppqn": TPB,
        "meter": "4/4", "bar_ticks": BAR, "n_bars": N_BARS,
        "funk": FUNK, "drum_models": list(MODELS),
        "per_model_params": PARAMS,
        "color_models": {k: "idiomatic funk layer" for k in COLOR},
        "dynamic_filter": {"hp": 25.0, "lp": 14000.0, "drive": 0.12, "comp": 0.45},
        "carrier": "FluidSynth SP-001 (FluidR3_GM, dry -R 0 -C 0 -g 1.2), ch9 stripped",
        "target_lufs": TARGET_LUFS, "ceiling_db": CEILING_DB,
    },
    "source_midi": str(SRC),
    "source_humanized_midi": str(SRC_HUMANIZED),
    "carrier_midi": str(carrier_mid),
    "source_bpm": BPM,
    "source_key": "A natural minor",
    "source_pitch_classes": sorted(AMIN_PCS),
    "bar_degrees": PROG,
    "output_wav": str(final_wav),
    "output_ogg": str(final_ogg),
    "carrier_wav": str(carrier_wav),
    "dry_reference_wav": str(dry_wav),
    "lufs": meas_lufs, "peak": peak_val, "silence_pct": silence_pct, "rms": rms,
    "pitch_verdict": pitch_verdict, "pitched_hit_rate": hit_rate,
    "pitched_he": he_mean,
    "drum_env_period_ms": lag_ms, "drum_grid_ok": grid_ok,
    "preflight_humanized": before,
    "preflight_perfect": after,
}
(OUT / "provenance.json").write_text(json.dumps(provenance, indent=2))

print("DONE")
