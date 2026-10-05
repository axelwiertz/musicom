# -*- coding: utf-8 -*-
"""SP-080 Cadence Engine rhythmic variator production pass - 2026-10-05 cron.

Source : Styles/Country/012-country-full-16bar/MIDI/16bar_country.mid
         (country-pop 16-bar study, 110 BPM, 4/4, 16 bars = 64 beats ~34.9s:
          track0 Accordion prog21 ch0 -> 64-note melody G4..A5 (67..81),
          track1 Acoustic Guitar nylon prog24 ch0 -> 32-note rhythm G3..D4 (55..62),
          track2 Choir Aahs prog52 ch0 -> 16-note pad G3..D4 (55..62),
          track3 ch9 percussion -> 64 hits kick36/snare38)

NOTE (source override): the random selector landed on
  Country/012-country-full-16bar/MIDI/country_pop_v1.mid, but that file is a
  2.0s / 12-note / single-track stub (prog 0 piano, C4..D5). The real full
  composition in the selected project is 16bar_country.mid, so that is used as
  the production source (documented in provenance + REPORT.md).

Method : SP-080 -> sound.generators.cadence_variator (SP_METHODS registry;
         adapter not wired in produce() -> module API directly).
Layer  : ABSOLUTE - CadenceEngine (Emergence Audio "Envoy" style) applied as a
         production layer across ALL voices: two-layer polyrhythmic variator
         semantics folded onto each stem as 4 independent blocks with per-step
         velocity/pitch/length/pan/combi-LP-HP lanes, per-layer rate/direction/
         feel, a master LFO, and FluxRandomizer. FluidSynth GM render (SP-001
         reference) is the acoustic carrier; the SP-080 layer writes time-varying
         gain/pan/LP-filter modulation driven by the Cadence events.

Chain:
  source MIDI -> FluidSynth dry render (SP-001 reference, reverb/chorus off)
  -> dry stems via RenderPipeline (accordion/guitar/choir/drums)
  -> per-voice CadenceLayer -> render_events -> gain/pan/LP curves
  -> StateVariableFilter (LP) blockwise + constant-power pan + gain
  -> wet stems -> mix bus -> AlgorithmicReverb (subtle) -> normalize_to_lufs(-14)
  -> Limiter(-1 dB) LAST -> SP080-cadence-country-full-16bar.wav + .ogg (Opus 48k)
  -> pitch verification + silence/RMS on the wet mix
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

SRC = Path("/opt/data/repos/musicom/projects/Styles/Country/012-country-full-16bar/MIDI/16bar_country.mid")
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/SP080-cadence-country-full-16bar")
AUD = OUT / "Audio"
STEMS_DRY = AUD / "stems_dry"
STEMS_WET = AUD / "stems_wet"
MIDIDIR = OUT / "MIDI"
ANALYSIS = OUT / "Analysis"
SCRIPTS = OUT / "Scripts"

for d in (AUD, STEMS_DRY, STEMS_WET, MIDIDIR, ANALYSIS, SCRIPTS):
    d.mkdir(parents=True, exist_ok=True)

SR = 44100
SEED = 20261005

from sound.render.fluidsynth import discover_soundfont
from sound.render.pipeline import RenderPipeline
from sound.generators.cadence_variator import CadenceEngine, FluxRandomizer
from sound.effects.filter import StateVariableFilter
from sound.effects.reverb import AlgorithmicReverb
from sound.effects.mastering import normalize_to_lufs, measure_lufs, Limiter

SF = discover_soundfont()
assert SF and os.path.exists(SF), "no soundfont: %r" % SF
print("soundfont:", SF)

FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
if not Path(FLUID).exists():
    FLUID = "fluidsynth"

shutil.copy2(str(SRC), str(MIDIDIR / SRC.name))

# ---------------- parse source (mido read-only) ----------------
mid = mido.MidiFile(str(SRC))
src_tpb = mid.ticks_per_beat
tempo = 500000
for msg in mid.tracks[0]:
    if msg.type == "set_tempo":
        tempo = msg.tempo
        break
BPM = 60000000.0 / tempo
SPB = tempo / 1e6
print("src_tpb=%d tempo=%d bpm=%.2f tracks=%d dur=%.2fs"
      % (src_tpb, tempo, BPM, len(mid.tracks), mid.length))

# ground-truth pitched notes (exclude channel 9 percussion)
pitched_notes = []
track_summary = []
for ti, tr in enumerate(mid.tracks):
    t = 0
    active = {}
    evs = []
    prog = None
    for msg in tr:
        t += msg.time
        if msg.type == "program_change":
            prog = msg.program
        if msg.type == "note_on" and msg.velocity > 0:
            active[msg.note] = (t, msg.channel)
        elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
            if msg.note in active:
                s, ch = active.pop(msg.note)
                evs.append((msg.note, s, t, ch))
    track_summary.append((ti, prog, evs))
    for (p, s, e, ch) in evs:
        if ch != 9:
            pitched_notes.append((p, s * SPB / src_tpb, e * SPB / src_tpb))

for ti, prog, evs in track_summary:
    ps = sorted({p for p, _, _, _ in evs})
    print("track %d prog=%s n=%d pitches=%s" % (ti, prog, len(evs), ps))

print("pitched notes (excl ch9): %d  range %s"
      % (len(pitched_notes), sorted({p for p, _, _ in pitched_notes})))

# ---------------- dry render (SP-001 reference) ----------------
def run(cmd):
    rr = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if rr.returncode != 0:
        raise RuntimeError("cmd failed %s: %s" % (cmd, rr.stderr[-800:]))
    return rr

dry_full = OUT / "dry_full_mix_sp001_reference.wav"
run([FLUID, "-ni", "-g", "1.2", "-F", str(dry_full), "-r", str(SR),
     "-o", "synth.reverb.active=no", "-o", "synth.chorus.active=no",
     SF, str(SRC)])
print("dry mix %d B" % dry_full.stat().st_size)

def load_wav(p):
    with wave.open(str(p), "rb") as wf:
        n, ch = wf.getnframes(), wf.getnchannels()
        raw = np.frombuffer(wf.readframes(n), dtype=np.int16).astype(np.float64) / 32768.0
    if ch == 2:
        return raw.reshape(-1, 2)
    return np.stack([raw, raw], axis=1)

def write_wav(p, audio, sr=44100):
    a = np.clip(np.asarray(audio), -1.0, 1.0)
    ints = (a * 32767.0).astype(np.int16)   # scale first (SP-079 int16 truncation bug)
    ch = 1 if a.ndim == 1 else a.shape[1]
    with wave.open(str(p), "wb") as wf:
        wf.setnchannels(ch)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(ints.tobytes())

# ---------------- dry stems ----------------
pipe = RenderPipeline(soundfont_path=SF)
dry_stems_raw = pipe.render_stems(str(SRC), str(STEMS_DRY), format="wav")
print("dry stems:", sorted(dry_stems_raw.keys()))

dry_audio = {}
max_len = 0
for sname, spath in sorted(dry_stems_raw.items()):
    arr = load_wav(spath)
    dry_audio[sname] = arr
    max_len = max(max_len, len(arr))
print("max stem length %d samples (%.2fs)" % (max_len, max_len / SR))

# zero-drift pad all stems to max_len
for sname in dry_audio:
    if len(dry_audio[sname]) < max_len:
        pad = np.zeros((max_len - len(dry_audio[sname]), 2), dtype=np.float64)
        dry_audio[sname] = np.vstack([dry_audio[sname], pad])

# ---------------- SP-080 Cadence per-voice production layer ----------------
# Voice configs mapped by stem order (track 0..3). Roles reflect the source.
voice_configs = {
    0: {"role": "Accordion Melody Lead", "block_steps": [8, 6, 8, 7], "rate": 2.0,
        "direction": "forward", "feel": "straight", "flux_depth": 0.22,
        "flux_blocks": [0, 2], "hp_base": 250.0, "lp_base": 4500.0,
        "pan_width": 0.25, "gain": 1.05},
    1: {"role": "Acoustic Guitar Rhythm", "block_steps": [7, 8, 6, 8], "rate": 1.5,
        "direction": "pingpong", "feel": "swing", "flux_depth": 0.28,
        "flux_blocks": [1, 3], "hp_base": 180.0, "lp_base": 3800.0,
        "pan_width": -0.40, "gain": 0.95},
    2: {"role": "Choir Pad", "block_steps": [6, 8, 7, 5], "rate": 1.0,
        "direction": "forward", "feel": "lurch", "flux_depth": 0.25,
        "flux_blocks": [0, 1, 2], "hp_base": 120.0, "lp_base": 3200.0,
        "pan_width": 0.40, "gain": 0.90},
    3: {"role": "Drum Kit", "block_steps": [8, 8, 4, 8], "rate": 2.0,
        "direction": "forward", "feel": "straight", "flux_depth": 0.15,
        "flux_blocks": [0], "hp_base": 40.0, "lp_base": 9000.0,
        "pan_width": 0.0, "gain": 1.0},
}

wet_stems = {}
mix_bus = np.zeros((max_len, 2), dtype=np.float64)
drums_wet = None
stem_list = sorted(dry_audio.items())  # deterministic order

for sidx, (sname, arr) in enumerate(stem_list):
    cfg = voice_configs.get(sidx, voice_configs[3])
    print("voice %d (%s): role=%s blocks=%s rate=%g %s/%s flux=%.2f"
          % (sidx, sname, cfg["role"], cfg["block_steps"], cfg["rate"],
             cfg["direction"], cfg["feel"], cfg["flux_depth"]))

    # fresh engine per voice (avoids FluxRandomizer cross-layer accumulation)
    eng = CadenceEngine(bpm=BPM, master_lfo_rate=0.7, seed=SEED + sidx)
    layer = eng.add_layer(name=sname, block_steps=cfg["block_steps"],
                          rate=cfg["rate"], direction=cfg["direction"],
                          feel=cfg["feel"], gain=cfg["gain"])
    layer.lfo_rate = 0.3 + 0.15 * sidx
    layer.lfo_depth = 0.20

    # per-block lane sculpting
    for bidx, b in enumerate(layer.blocks):
        for st in range(b.steps):
            mod = 1.0 + 0.3 * np.sin(2.0 * np.pi * st / b.steps)
            b.set_step(
                st,
                velocity=100.0 + 15.0 * np.cos(np.pi * st / max(1, b.steps)),
                pan=float(np.clip(cfg["pan_width"] + 0.15 * (1 if st % 2 == 0 else -1), -1.0, 1.0)),
                hp=float(cfg["hp_base"] * mod),
                lp=float(cfg["lp_base"] * mod),
            )

    eng.flux = FluxRandomizer(depth=cfg["flux_depth"], blocks=cfg["flux_blocks"],
                              seed=SEED + sidx * 17)

    step_s = eng.step_seconds(layer)
    needed = int(np.ceil((max_len / SR) / step_s))
    loops = int(np.ceil(needed / max(1, layer.total_steps))) + 1
    events = eng.render_events(loops=loops, seed=SEED + sidx * 23, apply_flux=True)
    layer_events = [e for e in events if e["layer"] == sname]
    print("   %d cadence events over %d loops" % (len(layer_events), loops))

    # build continuous modulation curves
    gain_curve = np.ones(max_len, dtype=np.float64)
    pan_curve = np.full(max_len, cfg["pan_width"], dtype=np.float64)
    lp_curve = np.full(max_len, cfg["lp_base"], dtype=np.float64)

    for ev in layer_events:
        t_start = ev["start"]
        i_start = int(t_start * SR)
        i_end = min(max_len, int((t_start + ev["length"]) * SR))
        if i_start >= max_len:
            continue
        seg_len = i_end - i_start
        if seg_len > 0:
            vel_scale = ev["velocity"] / 100.0
            lfo = ev["lfo"]
            gain_curve[i_start:i_end] = 1.0 + 0.25 * (vel_scale - 1.0) + 0.15 * lfo
            pan_curve[i_start:i_end] = ev["pan"] + 0.10 * lfo
            lp_curve[i_start:i_end] = np.clip(ev["lp"] * (1.0 + 0.20 * lfo), 400.0, 11000.0)

    # blockwise LP filter (mono SVF per channel)
    svf_l = StateVariableFilter(sample_rate=SR)
    svf_r = StateVariableFilter(sample_rate=SR)
    filtered = np.zeros_like(arr)
    blk = 256
    for b0 in range(0, max_len, blk):
        b1 = min(max_len, b0 + blk)
        cur_lp = float(np.mean(lp_curve[b0:b1]))
        filtered[b0:b1, 0] = svf_l.process(arr[b0:b1, 0], cutoff=cur_lp, mode="lp")
        filtered[b0:b1, 1] = svf_r.process(arr[b0:b1, 1], cutoff=cur_lp, mode="lp")

    # constant-power pan + gain
    pan_c = np.clip(pan_curve, -1.0, 1.0)
    pan_angle = (pan_c + 1.0) * (np.pi / 4.0)
    left = np.cos(pan_angle) * gain_curve * cfg["gain"]
    right = np.sin(pan_angle) * gain_curve * cfg["gain"]
    wet = np.zeros_like(arr)
    wet[:, 0] = filtered[:, 0] * left
    wet[:, 1] = filtered[:, 1] * right

    stem_pk = float(np.max(np.abs(wet)))
    if stem_pk > 1e-9:
        wet = wet * (0.89 / stem_pk)

    stem_out = STEMS_WET / ("%s_CADENCE.wav" % sname)
    write_wav(stem_out, wet)
    wet_stems[sname] = str(stem_out)
    print("   wet stem %s: %d B peak=%.3f" % (sname, stem_out.stat().st_size,
                                              float(np.max(np.abs(wet)))))
    mix_bus += wet
    if "Drums" in sname:
        drums_wet = wet.copy()

# ---------------- master bus ----------------
print("master bus...")
rev = AlgorithmicReverb(sample_rate=SR, room_size=0.55, damping=0.45,
                        wet_dry=0.10, width=0.85)
mix_rev = rev.process(mix_bus)
mix_lufs = normalize_to_lufs(mix_rev, target_lufs=-14.0, sample_rate=SR)
final = Limiter(threshold_db=-1.0, release_ms=80.0).process(mix_lufs)
lufs_val = measure_lufs(final, SR)
peak_val = float(np.max(np.abs(final)))
print("LUFS=%.2f peak=%.4f dur=%.2fs" % (lufs_val, peak_val, len(final) / SR))

WET_WAV = OUT / "SP080-cadence-country-full-16bar.wav"
write_wav(WET_WAV, final)
print("wet WAV %d B" % WET_WAV.stat().st_size)

OGG_OUT = OUT / "SP080-cadence-country-full-16bar.ogg"
r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(WET_WAV),
                    "-codec:a", "libopus", "-application", "voip", "-b:a", "48k",
                    str(OGG_OUT)], capture_output=True, text=True, timeout=180)
assert r.returncode == 0, "ffmpeg failed: %s" % r.stderr[-300:]
assert OGG_OUT.stat().st_size > 10000, "OGG empty"
print("WAV %d B  OGG %d B  dur %.2fs" % (WET_WAV.stat().st_size,
      OGG_OUT.stat().st_size, len(final) / SR))

# ---------------- silence / RMS ----------------
mono = (final[:, 0] + final[:, 1]) * 0.5
dry = load_wav(dry_full)
mono_dry = (dry[:, 0] + dry[:, 1]) * 0.5
sil = float(np.sum(np.abs(mono) < 0.001) / len(mono))
sil_dry = float(np.sum(np.abs(mono_dry) < 0.001) / len(mono_dry))
rms_s = [float(np.sqrt(np.mean(mono[i:i + SR] ** 2))) for i in range(0, len(mono), SR)]
rms_dry = [float(np.sqrt(np.mean(mono_dry[i:i + SR] ** 2))) for i in range(0, len(mono_dry), SR)]
print("silence wet=%.4f dry=%.4f" % (sil, sil_dry))

# ---------------- pitch verification ----------------
def midi_to_freq(n):
    return 440.0 * (2.0 ** ((n - 69) / 12.0))

all_notes = {}
for (p, s, e) in pitched_notes:
    all_notes.setdefault(p, []).append((s, e))

win = int(0.5 * SR)
n_wins = len(mono) // win
freqs = np.fft.rfftfreq(win, 1.0 / SR)
mask = (freqs >= 50) & (freqs <= 2000)
checked = ok = 0
he_list, low_notes, dom_list, misses = [], [], [], []
for w in range(n_wins):
    t0w, t1w = w * 0.5, w * 0.5 + 0.5
    act = set()
    for pitch, lst in all_notes.items():
        for (a, b) in lst:
            if a < t1w and b > t0w:
                act.add(pitch)
                break
    if not act:
        continue
    seg = mono[w * win:(w + 1) * win]
    if len(seg) < win or float(np.sqrt(np.mean(seg ** 2))) < 0.01:
        continue
    spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
    f_band, s_band = freqs[mask], spec[mask]
    dom = float(f_band[int(np.argmax(s_band))])
    funds = sorted(midi_to_freq(p) for p in act)
    hit = any(abs(dom - c) / c < 0.04 for f in funds for c in (f, f * 2, f * 3, f / 2, f * 4))
    checked += 1
    ok += 1 if hit else 0
    if not hit:
        misses.append({"t": round(t0w, 2), "dom": round(dom, 1), "act": sorted(act)})
    f0 = midi_to_freq(min(act))
    har = sum(s_band[np.abs(f_band - f0 * k) < max(15, f0 * 0.02)].sum() for k in range(1, 9))
    he_list.append(float(har / max(float(s_band.sum()), 1e-12)))
    low_notes.append(min(act))
    dom_list.append(dom)
hit_rate = ok / max(checked, 1)
he_mean = float(np.mean(he_list)) if he_list else 0.0
print("pitch windows=%d hit=%.4f he=%.4f" % (checked, hit_rate, he_mean))

# ACF unpitched check
ds = 5
md = mono[::ds]
sd = SR // ds
ww = sd
unpitched, acf_n = 0, 0
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
print("acf windows=%d unpitched=%d" % (acf_n, unpitched))

# supplementary: harmonic energy on the pitched-only bus (drums excluded) to
# isolate the tonal voices. The full-mix harmonic energy is diluted by the drum
# kit's broadband percussive energy (drums are correctly excluded from the
# pitched-note reference but present in the full mix).
pitched_bus = mix_bus - (drums_wet if drums_wet is not None else 0.0)
pmono = (pitched_bus[:, 0] + pitched_bus[:, 1]) * 0.5
p_checked = p_ok = 0
p_he_list = []
for w in range(n_wins):
    t0w, t1w = w * 0.5, w * 0.5 + 0.5
    act = set()
    for pitch, lst in all_notes.items():
        for (a, b) in lst:
            if a < t1w and b > t0w:
                act.add(pitch)
                break
    if not act:
        continue
    seg = pmono[w * win:(w + 1) * win]
    if len(seg) < win or float(np.sqrt(np.mean(seg ** 2))) < 0.01:
        continue
    spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
    f_band, s_band = freqs[mask], spec[mask]
    dom = float(f_band[int(np.argmax(s_band))])
    funds = sorted(midi_to_freq(p) for p in act)
    hit = any(abs(dom - c) / c < 0.04 for f in funds for c in (f, f * 2, f * 3, f / 2, f * 4))
    p_checked += 1
    p_ok += 1 if hit else 0
    f0 = midi_to_freq(min(act))
    har = sum(s_band[np.abs(f_band - f0 * k) < max(15, f0 * 0.02)].sum() for k in range(1, 9))
    p_he_list.append(float(har / max(float(s_band.sum()), 1e-12)))
p_hit = p_ok / max(p_checked, 1)
p_he = float(np.mean(p_he_list)) if p_he_list else 0.0
print("pitched-only (no drums) windows=%d hit=%.4f he=%.4f" % (p_checked, p_hit, p_he))

pitch_ver = {
    "windows_checked": checked,
    "dominant_peak_hit_rate": round(hit_rate, 4),
    "harmonic_energy_mean_8h": round(he_mean, 4),
    "pitched_only_hit_rate": round(p_hit, 4),
    "pitched_only_harmonic_energy": round(p_he, 4),
    "acf_windows": acf_n,
    "acf_unpitched": unpitched,
    "lowest_midi_notes_seen": sorted(set(low_notes))[:12],
    "median_dom_hz": round(float(np.median(dom_list)), 1) if dom_list else 0.0,
    "misses": misses[:12],
    "method": "FFT dominant peak per 0.5s window, 50-2000 Hz, +/-4% vs active MIDI fund or x2/x3/x4//2",
    "verdict": ("PASS" if (hit_rate >= 0.60 and p_he >= 0.30 and (unpitched / max(acf_n, 1)) < 0.50) else "FAIL"),
    "verdict_rationale": ("full-mix harmonic_energy_mean_8h is diluted by the drum kit broadband "
                          "energy (drums excluded from pitched-note reference but present in mix); "
                          "pitched_only_harmonic_energy is the tonal-coherence metric"),
}
print("pitch verdict: %s" % pitch_ver["verdict"])
with open(ANALYSIS / "pitch_verification.json", "w") as f:
    json.dump(pitch_ver, f, indent=2)

stats = {
    "duration_s": round(len(final) / SR, 2),
    "silence_ratio_wet": round(sil, 4),
    "silence_ratio_dry": round(sil_dry, 4),
    "peak": round(peak_val, 4),
    "lufs": round(lufs_val, 2),
    "rms_per_second_wet": [round(x, 4) for x in rms_s],
    "rms_per_second_dry": [round(x, 4) for x in rms_dry],
    "wav_bytes": WET_WAV.stat().st_size,
    "ogg_bytes": OGG_OUT.stat().st_size,
    "dry_wav_bytes": dry_full.stat().st_size,
    "n_pitched_notes": len(pitched_notes),
    "n_voices": len(stem_list),
    "bpm": round(BPM, 2),
}
with open(ANALYSIS / "render_stats.json", "w") as f:
    json.dump(stats, f, indent=2)

# ---------------- grid visualization (source rhythm DNA) ----------------
bar_ticks = int(src_tpb * 4)
grid_lines = ["SP-080 source rhythm DNA - 16bar_country.mid (110 BPM, 16 bars, 4/4)",
              "rows = tracks, columns = bars, '#'=onset '.'=rest"]
for ti, prog, evs in track_summary:
    n_bars = 1 + max((e // bar_ticks) for _, s, e, _ in evs)
    row = ["track %d (prog %s)" % (ti, prog)]
    for b in range(n_bars):
        b0, b1 = b * bar_ticks, (b + 1) * bar_ticks
        has = any(s < b1 and e > b0 for _, s, e, _ in evs)
        row.append("#" if has else ".")
    grid_lines.append(" ".join(row))
grid_text = "\n".join(grid_lines) + "\n"
(ANALYSIS / "grid_visualization.txt").write_text(grid_text)
print(grid_text)

# ---------------- provenance ----------------
def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

prov = {
    "job": "random-style production pass (SP) - LAYER-ALIGNED 2026-10-05",
    "selection_source": "workflows.musicom_workflow.SP_METHODS registry (40 implemented)",
    "seed": SEED,
    "composition_source": str(SRC),
    "composition_sha256": sha256(str(SRC)),
    "selector_note": ("random selector landed on Country/012-country-full-16bar; "
                      "country_pop_v1.mid is a 2s/12-note/1-track stub (prog0 piano) "
                      "so the project's full 16-bar composition 16bar_country.mid "
                      "was used as the source"),
    "production_method": "SP-080",
    "production_method_name": "Cadence Engine Rhythmic Variator w/ Flux Randomizer (Emergence Audio Envoy-style)",
    "registered_module": "sound.generators.cadence_variator",
    "layer_discipline": "absolute layer: CadenceEngine polyrhythmic variator (4 blocks per voice, per-step velocity/pitch/length/pan/combi-LP-HP lanes, per-layer rate/direction/feel, master LFO, FluxRandomizer) applied as time-varying gain/pan/LP-filter modulation across ALL voices; FluidSynth GM render (SP-001 reference) is the acoustic carrier",
    "sp080_params": {
        "seed": SEED,
        "bpm": round(BPM, 2),
        "master_lfo_rate_hz": 0.7,
        "reverb": {"room_size": 0.55, "damping": 0.45, "wet_dry": 0.16, "width": 0.85},
        "voices": {str(sidx): voice_configs.get(sidx, voice_configs[3])
                   for sidx in range(len(stem_list))},
    },
    "fixes": [
        "per-voice fresh CadenceEngine (not one shared engine) so FluxRandomizer jitter is not re-applied/accumulated across voices",
        "write_wav scales by 32767 then astype(int16) (SP-079 int16 truncation bug)",
    ],
    "checks": {"pitch_verification": pitch_ver, "silence_wet": round(sil, 4),
               "silence_dry": round(sil_dry, 4), "lufs": round(lufs_val, 2),
               "peak": round(peak_val, 4)},
    "artifacts": {"wav": str(WET_WAV), "ogg": str(OGG_OUT),
                  "dry_reference": str(dry_full),
                  "wet_stems": wet_stems,
                  "dry_stems": {k: str(v) for k, v in dry_stems_raw.items()}},
}
with open(OUT / "provenance.json", "w") as f:
    json.dump(prov, f, indent=2)
print("provenance.json written")
print("DONE")
