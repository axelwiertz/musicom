# -*- coding: utf-8 -*-
"""SP-083 Wandering Engine + Portal + Drift Clouds production pass - 2026-10-03 cron.

Source : Styles/Flamenco/023-flamenco-16-bar/MIDI/flamenco_v2.mid
         (E-Phrygian flamenco 16-bar study, 120 BPM, 3/4 meter:
          track1 melody nylon-guitar E4..C5 (52 notes),
          track2 harmony/bass nylon-guitar E2..A4 (64 notes),
          track3 ch9 percussion palo accent note72 (48 hits))
Method : SP-083 -> sound.modular.wandering (SP_METHODS registry; adapter not
         wired in produce() -> module API directly).
Layer  : ABSOLUTE - a "Drift Clouds" modulation layer applied to the WHOLE
         rendered flamenco piece: Non-LFO Wandering Engine (ebb/flow/slew/
         near-halt control signal) + Portal ("happy drunk" modulation matrix
         that re-routes itself) drive a Cloud/Shadow two-band split with
         wandering filter cutoff, stereo pan and level. GM render via
         FluidSynth is the acoustic carrier; the SP-083 layer is the wonky
         wandering modulation on top of it (no new notes written).

Chain:
  source MIDI -> FluidSynth dry render (SP-001 reference)
  -> Cloud band (highpass 350 Hz) + Shadow band (lowpass 350 Hz)
  -> WanderingEngine(non-LFO CV) + Portal(surprise re-routing) modulation:
       wandering filter cutoff (cloud bright<->dark, shadow complementary),
       wandering stereo pan, wandering level (ebb/near-halt)
  -> stereo mix -> normalize_to_lufs(-14) -> Limiter(-1 dB) LAST
  -> SP083-wandering-flamenco-16-bar.wav + .ogg (Opus 48k voip)
  -> stems: dry (source tracks) + wet (cloud/shadow band split)
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

SRC = Path("/opt/data/repos/musicom/projects/Styles/Flamenco/023-flamenco-16-bar/MIDI/flamenco_v2.mid")
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/SP083-wandering-flamenco-16-bar")
AUD = OUT / "Audio"
STEMS_DRY = AUD / "stems_dry"
STEMS_WET = AUD / "stems_wet"
ANALYSIS = OUT / "Analysis"
SCRIPTS = OUT / "Scripts"
for d in (AUD, STEMS_DRY, STEMS_WET, ANALYSIS, SCRIPTS):
    d.mkdir(parents=True, exist_ok=True)

SR = 44100
SEED = 20261003
CLOUD_HZ = 350.0        # band split: Cloud = upper, Shadow = lower
MOD_WHEEL = 0.60        # Drift Clouds layer balance (Cloud is "the meat and potatoes")

from sound.render.fluidsynth import discover_soundfont
from sound.modular.wandering import WanderingEngine, Portal, DriftCloudsVoice, DEFAULT_DESTINATIONS
from sound.effects.filter import StateVariableFilter
from sound.effects.mastering import normalize_to_lufs, measure_lufs, Limiter
from sound.render.pipeline import RenderPipeline

SF = discover_soundfont()
assert SF and os.path.exists(SF), "no soundfont"
print("soundfont:", SF)

FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
if not Path(FLUID).exists():
    FLUID = "fluidsynth"

shutil.copy2(str(SRC), str(OUT / "flamenco_v2.mid"))

# ---------------- parse source (mido read-only) ----------------
mid = mido.MidiFile(str(SRC))
src_tpb = mid.ticks_per_beat
tempo = 500000
for msg in mid.tracks[0]:
    if msg.type == "set_tempo":
        tempo = msg.tempo
        break
BPM = 60000000.0 / tempo
SPB = tempo / 1e6  # seconds per beat
print("src_tpb=%d tempo=%d bpm=%.2f tracks=%d" % (src_tpb, tempo, BPM, len(mid.tracks)))

# ground-truth pitched notes (tracks 1,2 = guitar ch0; track 3 = ch9 perc -> skip)
pitched_notes = []   # (pitch, start_sec, end_sec)
track_summary = []
for ti, tr in enumerate(mid.tracks[1:], start=1):
    t = 0
    active = {}
    evs = []
    for msg in tr:
        t += msg.time
        if msg.type == "note_on" and msg.velocity > 0:
            active[msg.note] = t
        elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
            if msg.note in active:
                s = active.pop(msg.note)
                evs.append((msg.note, s, t))
    track_summary.append((ti, evs))
    is_perc = (ti == len(mid.tracks) - 1)  # last track = ch9 percussion
    if not is_perc:
        for (p, s, e) in evs:
            pitched_notes.append((p, s * SPB / src_tpb, e * SPB / src_tpb))

for ti, evs in track_summary:
    ps = sorted({p for p, _, _ in evs})
    print("track %d: n=%d pitches=%s" % (ti, len(evs), ps))

print("pitched notes (excl perc): %d  range %s" %
      (len(pitched_notes), sorted({p for p, _, _ in pitched_notes})))

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
    ints = (a * 32767.0).astype(np.int16)
    ch = 1 if a.ndim == 1 else a.shape[1]
    with wave.open(str(p), "wb") as wf:
        wf.setnchannels(ch)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(ints.tobytes())

dry = load_wav(dry_full)
mono_dry = (dry[:, 0] + dry[:, 1]) * 0.5
n = mono_dry.size
print("dry dur %.2fs" % (n / SR))

# ---------------- Cloud / Shadow band split ----------------
def band_split(x, hz):
    svf_lp = StateVariableFilter(sample_rate=SR)
    svf_hp = StateVariableFilter(sample_rate=SR)
    shadow = svf_lp.process(x, cutoff=hz, resonance=0.4, mode="lp")
    cloud = svf_hp.process(x, cutoff=hz, resonance=0.4, mode="hp")
    return cloud, shadow

cloud, shadow = band_split(mono_dry, CLOUD_HZ)
print("cloud %.2fs shadow %.2fs (band split @ %.0f Hz)" % (cloud.size / SR, shadow.size / SR, CLOUD_HZ))

# ---------------- SP-083 modulation machinery ----------------
# Non-LFO Wandering Engine: wonky ebb/flow control signal (no fixed frequency).
wander = WanderingEngine(sample_rate=SR, rate=0.35, wobble=0.5, roughness=0.03,
                         stall_probability=0.30, stall_length=0.8, slew=0.5,
                         seed=SEED)
# A second, slower wander drives pan (independent "Portal" hand).
wander_pan = WanderingEngine(sample_rate=SR, rate=0.18, wobble=0.35, roughness=0.02,
                             stall_probability=0.25, stall_length=1.0, slew=0.6,
                             seed=SEED + 7)
# "Happy drunk" modulation matrix: routes that re-point themselves.
portal = Portal(destinations=DEFAULT_DESTINATIONS, seed=SEED + 1)
portal.add_route("drift", "filter_cutoff", 0.40)
portal.add_route("drift", "pan", 0.35)
portal.add_route("drift", "volume", 0.20)
portal.add_route("portal", "eq_tilt", 0.15)
# Drift Clouds voice (records the documented two-layer balance).
voice = DriftCloudsVoice(sample_rate=SR, cloud_drift=1.0, shadow_drift=0.35,
                         mod_wheel=MOD_WHEEL, seed=SEED + 3)
cg, sg = voice.balance
print("DriftCloudsVoice balance cloud=%.3f shadow=%.3f" % (cg, sg))

# ---------------- apply wandering modulation block-by-block ----------------
BLK = 4096
svf_cloud = StateVariableFilter(sample_rate=SR)
svf_shadow = StateVariableFilter(sample_rate=SR)

# pre-build the static band gain from the Drift Clouds layer balance
cloud_b = cloud * cg
shadow_b = shadow * sg

surprise_times = [4.0, 8.0, 12.0, 16.0, 20.0]  # seconds where Portal re-routes

out_l = np.empty(n)
out_r = np.empty(n)
portal_log = []
pos = 0
while pos < n:
    end = min(n, pos + BLK)
    blk = end - pos
    t_now = pos / SR

    cv_buf = wander.process(blk)          # advance the non-LFO wander
    cv = float(np.clip(np.mean(cv_buf), 0.0, 1.0))
    cv2 = float(np.clip(np.mean(wander_pan.process(blk)), 0.0, 1.0))

    # Portal surprises at section boundaries (the "happy drunk" re-routing)
    for st in surprise_times:
        if abs(t_now - st) < (BLK / SR) and not any(lg[0] == st for lg in portal_log):
            touched = portal.surprise(amount=0.4)
            portal_log.append((st, touched, portal.table()))
            print("  portal.surprise @ %.1fs touched %d routes" % (st, touched))

    mods = portal.apply({"drift": cv, "portal": cv2})

    # wandering filter cutoff: cloud bright<->dark, shadow complementary
    cut_cloud = float(np.clip(1500.0 + 6500.0 * cv + mods.get("filter_cutoff", 0.0) * 1500.0,
                              800.0, 9000.0))
    cut_shadow = float(np.clip(180.0 + 900.0 * (1.0 - cv), 120.0, 1100.0))

    # wandering level (ebb / near-halt) + portal volume offset
    vol = float(np.clip(0.72 + 0.28 * cv + mods.get("volume", 0.0) * 0.15, 0.30, 1.0))

    # wandering stereo pan
    pan = float(np.clip(mods.get("pan", 0.0) + (cv2 - 0.5) * 0.7, -0.6, 0.6))

    c_seg = svf_cloud.process(cloud_b[pos:end], cutoff=cut_cloud, resonance=0.4, mode="lp")
    s_seg = svf_shadow.process(shadow_b[pos:end], cutoff=cut_shadow, resonance=0.4, mode="lp")

    mix = (c_seg + s_seg) * vol
    pan_l = np.sqrt(0.5 * (1.0 - pan))
    pan_r = np.sqrt(0.5 * (1.0 + pan))
    out_l[pos:end] = mix * pan_l
    out_r[pos:end] = mix * pan_r
    pos = end

wet = np.stack([out_l, out_r], axis=1)
print("wet mix dur %.2fs" % (wet.shape[0] / SR))

# record wander characteristics (non-LFO proof) over the full buffer
cv_full = WanderingEngine(sample_rate=SR, rate=0.35, wobble=0.5, roughness=0.03,
                          stall_probability=0.30, stall_length=0.8, slew=0.5,
                          seed=SEED).process(n, slew=0.5)
stall_frac = wander.stall_fraction(cv_full)
print("wander range %.3f..%.3f mean %.3f stall_fraction %.4f" %
      (cv_full.min(), cv_full.max(), cv_full.mean(), stall_frac))

# ---------------- master ----------------
wet_n = wet / max(1e-9, float(np.max(np.abs(wet)))) * 0.89
wet_lufs = normalize_to_lufs(wet_n, -14.0, SR)
final = Limiter(threshold_db=-1.0).process(wet_lufs)
lufs_val = measure_lufs(final, SR)
peak_val = float(np.max(np.abs(final)))
print("LUFS=%.2f peak=%.4f dur=%.2fs" % (lufs_val, peak_val, len(final) / SR))

WET_WAV = OUT / "SP083-wandering-flamenco-16-bar.wav"
write_wav(WET_WAV, final)
print("wet WAV %d B" % WET_WAV.stat().st_size)

OGG_OUT = OUT / "SP083-wandering-flamenco-16-bar.ogg"
r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(WET_WAV),
                    "-codec:a", "libopus", "-application", "voip", "-b:a", "48k",
                    str(OGG_OUT)], capture_output=True, text=True, timeout=180)
assert r.returncode == 0, "ffmpeg failed: %s" % r.stderr[-300:]
assert OGG_OUT.stat().st_size > 10000, "OGG empty"
print("WAV %d B  OGG %d B  dur %.2fs" % (WET_WAV.stat().st_size,
      OGG_OUT.stat().st_size, len(final) / SR))

# ---------------- stems ----------------
pipe = RenderPipeline(soundfont_path=SF)
dry_stems = pipe.render_stems(str(SRC), str(STEMS_DRY), format="wav")
for k, p in dry_stems.items():
    print("dry stem %s %d B" % (k, Path(p).stat().st_size))

# wet "stems" = the two Drift Clouds band layers (what SP-083 modulates)
write_wav(STEMS_WET / "cloud_band.wav", cloud_b)
write_wav(STEMS_WET / "shadow_band.wav", shadow_b)
print("wet stems: cloud_band.wav + shadow_band.wav")

# ---------------- silence / RMS ----------------
mono = (final[:, 0] + final[:, 1]) * 0.5
sil = float(np.sum(np.abs(mono) < 0.001) / len(mono))
sil_dry = float(np.sum(np.abs(mono_dry) < 0.001) / len(mono_dry))
rms_s = [float(np.sqrt(np.mean(mono[i:i + SR] ** 2))) for i in range(0, len(mono), SR)]
rms_dry = [float(np.sqrt(np.mean(mono_dry[i:i + SR] ** 2))) for i in range(0, len(mono_dry), SR)]
print("silence wet=%.4f dry=%.4f" % (sil, sil_dry))

# ---------------- pitch verification ----------------
def midi_to_freq(nn):
    return 440.0 * (2.0 ** ((nn - 69) / 12.0))

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
    hit = any(abs(dom - c) / c < 0.04 for f in funds for c in (f, f * 2, f * 3, f / 2))
    checked += 1
    ok += 1 if hit else 0
    if not hit:
        misses.append({"t": round(t0w, 2), "dom": round(dom, 1), "act": sorted(act)})
    f0 = midi_to_freq(min(act))
    har = sum(s_band[np.abs(f_band - f0 * k) < max(15, f0 * 0.02)].sum() for k in range(1, 8))
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

pitch_ver = {
    "windows_checked": checked,
    "dominant_peak_hit_rate": round(hit_rate, 4),
    "harmonic_energy_mean_8h": round(he_mean, 4),
    "acf_windows": acf_n,
    "acf_unpitched": unpitched,
    "lowest_midi_notes_seen": sorted(set(low_notes))[:12],
    "median_dom_hz": round(float(np.median(dom_list)), 1) if dom_list else 0.0,
    "misses": misses[:12],
    "method": "FFT dominant peak per 0.5s window, 50-2000 Hz, +/-4% vs active MIDI fund or x2/x3//2",
    "verdict": ("PASS" if (hit_rate >= 0.60 and he_mean >= 0.30 and (unpitched / max(acf_n, 1)) < 0.50) else "FAIL"),
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
    "rms_per_second_wet": [round(r, 4) for r in rms_s],
    "rms_per_second_dry": [round(r, 4) for r in rms_dry],
    "wav_bytes": WET_WAV.stat().st_size,
    "ogg_bytes": OGG_OUT.stat().st_size,
    "dry_wav_bytes": dry_full.stat().st_size,
    "n_pitched_notes": len(pitched_notes),
    "wander_stall_fraction": round(stall_frac, 4),
    "wander_range": [round(float(cv_full.min()), 4), round(float(cv_full.max()), 4)],
    "cloud_band_hz": CLOUD_HZ,
    "mod_wheel": MOD_WHEEL,
    "portal_surprise_log": [{"t": t, "touched": n} for (t, n, _) in portal_log],
}
with open(ANALYSIS / "render_stats.json", "w") as f:
    json.dump(stats, f, indent=2)

# ---------------- grid visualization (source rhythm DNA) ----------------
BAR = int(src_tpb * 4)  # 4-beat bar in source ticks (meter is 3/4 but grid shows onsets)
grid_lines = []
grid_lines.append("SP-083 source rhythm DNA - flamenco_v2.mid (E Phrygian, 120 BPM)")
grid_lines.append("rows = tracks, columns = bars (16 bars), '#'=onset '.'=rest")
bar_ticks = int(src_tpb * 3)  # 3/4 meter = 3 beats per bar
for ti, evs in track_summary:
    n_bars = 1 + max((e // bar_ticks) for _, s, e in evs)
    row = ["track %d" % ti]
    for b in range(n_bars):
        b0, b1 = b * bar_ticks, (b + 1) * bar_ticks
        has = any(s < b1 and e > b0 for _, s, e in evs)
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
    "job": "random-style production pass (SP) - LAYER-ALIGNED 2026-10-03",
    "selection_source": "workflows.musicom_workflow.SP_METHODS registry (38 implemented)",
    "seed": SEED,
    "composition_source": str(SRC),
    "composition_sha256": sha256(str(SRC)),
    "production_method": "SP-083",
    "production_method_name": "Non-LFO Wandering Engine + Portal + Drift Clouds Voice (Sound Dust-style)",
    "registered_module": "sound.modular.wandering",
    "layer_discipline": "absolute layer: SP-083 is a modulation/effect layer applied to the WHOLE flamenco render (Cloud/Shadow band split driven by non-LFO wander + surprised modulation matrix); no new notes written; FluidSynth GM render is the acoustic carrier",
    "sp083_params": {
        "seed": SEED,
        "cloud_band_hz": CLOUD_HZ,
        "mod_wheel": MOD_WHEEL,
        "wander": {"rate": 0.35, "wobble": 0.5, "roughness": 0.03,
                   "stall_probability": 0.30, "stall_length": 0.8, "slew": 0.5},
        "wander_pan": {"rate": 0.18, "wobble": 0.35, "stall_probability": 0.25,
                       "stall_length": 1.0, "slew": 0.6},
        "portal_routes": ["drift->filter_cutoff 0.40", "drift->pan 0.35",
                          "drift->volume 0.20", "portal->eq_tilt 0.15"],
        "surprise_times_s": surprise_times,
        "filter": "cloud SVF lp 1500+6500cv Hz, shadow SVF lp 180+900(1-cv) Hz",
        "level": "0.72+0.28cv (ebb/near-halt)",
        "pan": "(cv2-0.5)*0.7 + portal pan offset",
    },
    "fixes": [],
    "checks": {"pitch_verification": pitch_ver, "silence_wet": round(sil, 4),
               "silence_dry": round(sil_dry, 4), "lufs": round(lufs_val, 2),
               "peak": round(peak_val, 4)},
    "artifacts": {"wav": str(WET_WAV), "ogg": str(OGG_OUT),
                  "dry_reference": str(dry_full),
                  "wet_stems": {"cloud": str(STEMS_WET / "cloud_band.wav"),
                                "shadow": str(STEMS_WET / "shadow_band.wav")},
                  "dry_stems": {k: str(v) for k, v in dry_stems.items()}},
}
with open(OUT / "provenance.json", "w") as f:
    json.dump(prov, f, indent=2)
print("provenance.json written")
print("DONE")
