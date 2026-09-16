# -*- coding: utf-8 -*-
"""SP-072 Critter Pad production pass - 2026-09-16 cron (random-style).

Source : Styles/Balfolk/014-balfolk-cinematic/MIDI/balfolk_cinematic_v1.mid
         (Balfolk jig -> cinematic, 120 BPM, 48 s, 2 voices:
          Violin prog 40 ch0 112 notes D4-A4, String Ensemble prog 48 ch1
          112 notes D2 pedal)
Method : SP-072 -> sound.synthesis.critter_pad (SP_METHODS registry;
         adapter not wired in produce() -> module API directly)
Layer  : ABSOLUTE - PadPartialBank replaces timbre for ALL voices.
         No drums in source; nothing rides GM except the SP-001 reference.

Chain:
  MIDI -> mido parse (reading only) -> per-note PadPartialBank.render_note
    (per-voice bank profiles + velocity gain at call site, render_note
     peak-normalizes every note so dynamics must be reapplied after)
    -> outer half-cosine note envelope (click safety) + tail
    -> constant-power pan -> stereo voice bus
  -> voice sum -> cassette (0.35) + splosh (0.22) bus character
  -> peak 0.89 -> normalize_to_lufs(-14) -> Limiter(-1 dB) LAST
  -> WAV + OGG (Opus 48k voip)
  + dry stems (RenderPipeline, FX off) + wet stems (same pad synth)
  + SP-001 FluidSynth dry reference mix
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

SRC = Path("/opt/data/repos/musicom/projects/Styles/Balfolk/014-balfolk-cinematic/MIDI/balfolk_cinematic_v1.mid")
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/SP072-critter-balfolk-cinematic")
AUD = OUT / "Audio"
STEMS_DRY = AUD / "stems_dry"
STEMS_WET = AUD / "stems_wet"
MIDIDIR = OUT / "MIDI"
ANALYSIS = OUT / "Analysis"
SCRIPTS = OUT / "Scripts"
for d in (AUD, STEMS_DRY, STEMS_WET, MIDIDIR, ANALYSIS, SCRIPTS):
    d.mkdir(parents=True, exist_ok=True)

SR = 44100
SEED = 20260916
TAIL_S = 0.40  # extra ring rendered past each note end

from sound.render.fluidsynth import discover_soundfont
from sound.synthesis.critter_pad import PadPartialBank
from sound.effects.mastering import normalize_to_lufs, measure_lufs, Limiter

SF = discover_soundfont()
assert SF and os.path.exists(SF), "no soundfont"
print("soundfont: %s" % SF)

FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
if not Path(FLUID).exists():
    FLUID = "fluidsynth"

shutil.copy2(str(SRC), str(MIDIDIR / "balfolk_cinematic_v1.mid"))

# ---------------- parse ----------------
mid = mido.MidiFile(str(SRC))
tpb = mid.ticks_per_beat
tempo = 500000
for msg in mid.tracks[0]:
    if msg.type == "set_tempo":
        tempo = msg.tempo
        break
BPM = 60000000.0 / tempo
sec_per_tick = tempo / 1e6 / tpb
print("tpb=%d tempo=%d bpm=%.2f sec_per_tick=%.6f tracks=%d" % (tpb, tempo, BPM, sec_per_tick, len(mid.tracks)))

voices = []  # dicts: track_idx, name, program, channel, notes[(tick_s,tick_e,pitch,vel)]
last_tick = 0
for ti, track in enumerate(mid.tracks):
    if ti == 0:
        continue
    abstick = 0
    prog, ch, nm = 0, 0, getattr(track, "name", "")
    active = {}
    notes = []
    for msg in track:
        abstick += msg.time
        if msg.type == "program_change":
            prog, ch = msg.program, msg.channel
        if msg.type == "note_on" and msg.velocity > 0:
            active[msg.note] = (abstick, msg.velocity)
        elif (msg.type == "note_off") or (msg.type == "note_on" and msg.velocity == 0):
            if msg.note in active:
                s, vel = active.pop(msg.note)
                notes.append((s, abstick, msg.note, vel))
    for note, (s, vel) in active.items():
        notes.append((s, abstick, note, vel))
    notes.sort()
    if notes:
        last_tick = max(last_tick, max(e for _, e, _, _ in notes))
    # track display name
    tname = nm if nm else ("track%d" % ti)
    voices.append({"track": ti, "name": str(tname), "program": prog,
                   "channel": ch, "notes": notes})
    print("voice %s prog=%d ch=%d n=%d" % (tname, prog, ch, len(notes)))

total_sec = last_tick * sec_per_tick
n_total = int((total_sec + TAIL_S + 1.0) * SR)
print("music=%.2fs bus=%.2fs last_tick=%d" % (total_sec, n_total / SR, last_tick))

GM = ["Acoustic_Grand_Piano", "Bright_Acoustic_Piano", "Electric_Grand_Piano",
      "Honky-tonk_Piano", "Electric_Piano_1", "Electric_Piano_2", "Harpsichord",
      "Clavi", "Celesta", "Glockenspiel", "Music_Box", "Vibraphone", "Marimba",
      "Xylophone", "Tubular_Bells", "Dulcimer", "Drawbar_Organ", "Percussive_Organ",
      "Rock_Organ", "Church_Organ", "Reed_Organ", "Accordion", "Harmonica",
      "Tango_Accordion", "Acoustic_Guitar_nylon", "Acoustic_Guitar_steel",
      "Electric_Guitar_jazz", "Electric_Guitar_clean", "Electric_Guitar_muted",
      "Overdriven_Guitar", "Distortion_Guitar", "Guitar_harmonics",
      "Acoustic_Bass", "Electric_Bass_finger", "Electric_Bass_pick",
      "Fretless_Bass", "Slap_Bass_1", "Slap_Bass_2", "Synth_Bass_1", "Synth_Bass_2",
      "Violin", "Viola", "Cello", "Contrabass", "Tremolo_Strings",
      "Pizzicato_Strings", "Orchestral_Harp", "Timpani", "String_Ensemble_1"]

# ---------------- per-voice pad profiles ----------------
# Lead violin: fast-ish partial envelopes so 0.25 s motif notes articulate;
# critters ON and audible (quarter-tone, density 2.5) = Brackish identity.
# String pedal D2: slow swell, subtle critters (eighth-tone, density 1.2).
PROFILES = {
    1: {"attack_b": 0.08, "release_b": 0.30, "attack_c": 0.12, "release_c": 0.40,
        "wob_b": 5.0, "wob_c": 12.0, "density": 2.5, "mset": "quarter-tone",
        "drift": 25.0, "bal": (0.70, 0.50, 0.50), "gain": 1.00, "pan": -0.20},
    2: {"attack_b": 0.25, "release_b": 0.70, "attack_c": 0.40, "release_c": 1.00,
        "wob_b": 4.0, "wob_c": 9.0, "density": 1.2, "mset": "eighth-tone",
        "drift": 18.0, "bal": (0.75, 0.45, 0.35), "gain": 0.85, "pan": 0.20},
}


def make_bank(prof):
    from sound.synthesis.critter_pad import Partial, Critters
    b = PadPartialBank(sample_rate=SR)
    b.basic.attack, b.basic.release = prof["attack_b"], prof["release_b"]
    b.basic.wobble_cents = prof["wob_b"]
    b.complex.attack, b.complex.release = prof["attack_c"], prof["release_c"]
    b.complex.wobble_cents = prof["wob_c"]
    b.critters = Critters(sample_rate=SR, density=prof["density"],
                          microtonal_set=prof["mset"], drift_cents=prof["drift"])
    b.balance = {"basic": prof["bal"][0], "complex": prof["bal"][1],
                 "critters": prof["bal"][2]}
    return b


def midi_to_freq(n):
    return 440.0 * (2.0 ** ((n - 69) / 12.0))


def note_envelope(n, sr, attack=0.03, release=0.40):
    a = min(int(attack * sr), max(1, n // 8))
    r = min(int(release * sr), max(1, n // 2))
    env = np.ones(n)
    env[:a] = 0.5 - 0.5 * np.cos(np.pi * np.arange(a) / a)
    env[-r:] *= 0.5 + 0.5 * np.cos(np.pi * np.arange(r) / r)
    return env


def const_power_pan(mono, pan):
    th = (pan + 1.0) * np.pi / 4.0
    return np.stack([mono * np.cos(th), mono * np.sin(th)], axis=1)


# ---------------- render ----------------
banks = {v["track"]: make_bank(PROFILES.get(v["track"], PROFILES[1])) for v in voices}
buses = {v["track"]: np.zeros((n_total, 2)) for v in voices}
bus = np.zeros((n_total, 2))
rendered = 0
for v in voices:
    tr = v["track"]
    prof = PROFILES.get(tr, PROFILES[1])
    bank = banks[tr]
    for ni, (s_tick, e_tick, pitch, vel) in enumerate(v["notes"]):
        dur = max(0.05, (e_tick - s_tick) * sec_per_tick)
        rlen = dur + TAIL_S
        mono = bank.render_note(freq=midi_to_freq(pitch), duration=rlen,
                                seed=SEED + tr * 100003 + ni * 7919)
        # render_note peak-normalizes every note to 0.8 -> dynamics lost;
        # reapply velocity gain at call site (SP-073 lesson)
        vg = float(np.clip((vel / 90.0) ** 1.5, 0.22, 1.30))
        mono = mono * vg
        mono = mono * note_envelope(len(mono), SR)
        st = const_power_pan(mono, prof["pan"]) * prof["gain"]
        i0 = int(s_tick * sec_per_tick * SR)
        i1 = min(n_total, i0 + len(st))
        if i1 <= i0:
            continue
        seg = st[:i1 - i0]
        buses[tr][i0:i1] += seg
        bus[i0:i1] += seg
        rendered += 1
print("rendered notes: %d" % rendered)

# trim bus to last sounding sample + 0.5 s
peak_env = np.abs(bus).max(axis=1)
nz = np.nonzero(peak_env > 0.0005)[0]
cut = min(n_total, (nz[-1] if len(nz) else n_total) + int(0.5 * SR))
bus = bus[:cut]
for tr in buses:
    buses[tr] = buses[tr][:cut]
print("trimmed len=%.2fs" % (len(bus) / SR))

# ---------------- bus character: cassette + splosh ----------------
from sound.synthesis.critter_pad import cassette, splosh
mix_m = (bus[:, 0] + bus[:, 1]) * 0.5
cass = cassette(mix_m, SR, amount=0.35)
# splosh expects mono, returns stereo-ish mix; apply per channel for width
left = splosh(bus[:, 0], SR, mix=0.22)
right = splosh(bus[:, 1], SR, mix=0.22)
wet = np.stack([left, right], axis=1)
# blend cassette wear at 0.35 (cassette returns full degraded signal;
# blend keeps transients readable)
wet = 0.65 * wet + 0.35 * np.stack([cass, cass], axis=1)
wet = wet / max(1e-9, np.max(np.abs(wet))) * 0.89

# ---------------- master: LUFS -14 + limiter LAST ----------------
wet_lufs = normalize_to_lufs(wet, -14.0, SR)
final = Limiter(threshold_db=-1.0).process(wet_lufs)
lufs_val = measure_lufs(final, SR)
peak_val = float(np.max(np.abs(final)))
print("LUFS=%.2f peak=%.4f" % (lufs_val, peak_val))


def write_wav(p, audio, sr=44100):
    a = np.clip(np.asarray(audio), -1.0, 1.0)
    ints = (a * 32767).astype(np.int16)
    ch = 1 if a.ndim == 1 else a.shape[1]
    with wave.open(str(p), "wb") as wf:
        wf.setnchannels(ch)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(ints.tobytes())


WAV_OUT = OUT / "SP072-critter-balfolk-cinematic.wav"
write_wav(WAV_OUT, final)
assert WAV_OUT.stat().st_size < 100 * 1024 * 1024, "WAV too big"
assert WAV_OUT.stat().st_size > 40000, "WAV empty"
OGG_OUT = OUT / "SP072-critter-balfolk-cinematic.ogg"
r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(WAV_OUT),
                    "-codec:a", "libopus", "-application", "voip", "-b:a", "48k",
                    str(OGG_OUT)], capture_output=True, text=True, timeout=180)
assert r.returncode == 0, "ffmpeg failed: %s" % r.stderr[-300:]
assert OGG_OUT.stat().st_size > 10000, "OGG empty"
print("WAV %d B  OGG %d B  dur %.2fs" % (WAV_OUT.stat().st_size, OGG_OUT.stat().st_size, len(final) / SR))

# ---------------- wet stems ----------------
stem_paths = {}
for v in voices:
    tr = v["track"]
    a = buses[tr].copy()
    pk = float(np.max(np.abs(a)))
    if pk > 1e-9:
        a = a / pk * 0.89
    gmname = GM[v["program"]] if v["program"] < len(GM) else ("Program_%d" % v["program"])
    sname = "track%02d_%s_CRITTER" % (tr - 1, gmname)
    p = STEMS_WET / (sname + ".wav")
    write_wav(p, a)
    stem_paths[sname] = str(p)
    print("wet stem %s %d B" % (sname, p.stat().st_size))

# ---------------- dry reference + dry stems ----------------
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
from sound.render.pipeline import RenderPipeline
pipe = RenderPipeline(soundfont_path=SF)
dry_stems = pipe.render_stems(str(SRC), str(STEMS_DRY), format="wav")
for k, p in dry_stems.items():
    print("dry stem %s %d B" % (k, Path(p).stat().st_size))


def load_wav(p):
    with wave.open(str(p), "rb") as wf:
        n, ch = wf.getnframes(), wf.getnchannels()
        raw = np.frombuffer(wf.readframes(n), dtype=np.int16).astype(np.float64) / 32768.0
    if ch == 2:
        return raw.reshape(-1, 2)
    return np.stack([raw, raw], axis=1)


mono = (final[:, 0] + final[:, 1]) * 0.5
dry = load_wav(dry_full)
mono_dry = (dry[:, 0] + dry[:, 1]) * 0.5
sil = float(np.sum(np.abs(mono) < 0.001) / len(mono))
sil_dry = float(np.sum(np.abs(mono_dry) < 0.001) / len(mono_dry))
rms_s = [float(np.sqrt(np.mean(mono[i:i + SR] ** 2))) for i in range(0, len(mono), SR)]
rms_dry = [float(np.sqrt(np.mean(mono_dry[i:i + SR] ** 2))) for i in range(0, len(mono_dry), SR)]
print("silence wet=%.4f dry=%.4f" % (sil, sil_dry))

# ---------------- pitch verification (mix windows, SP-071/SP-073 style) ----------------
intervals = {}
for v in voices:
    for (s_tick, e_tick, pitch, vel) in v["notes"]:
        intervals.setdefault(pitch, []).append((s_tick * sec_per_tick, e_tick * sec_per_tick))
win = int(0.5 * SR)
n_wins = len(mono) // win
freqs = np.fft.rfftfreq(win, 1.0 / SR)
mask = (freqs >= 50) & (freqs <= 2000)
checked = ok = 0
he_list, low_notes, dom_list, misses = [], [], [], []
for w in range(n_wins):
    t0w, t1w = w * 0.5, w * 0.5 + 0.5
    act = set()
    for pitch, lst in intervals.items():
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
    har = sum(s_band[np.abs(f_band - f0 * k) < max(15, f0 * 0.02)].sum() for k in range(1, 9))
    he_list.append(float(har / max(float(s_band.sum()), 1e-12)))
    low_notes.append(min(act))
    dom_list.append(dom)
hit_rate = ok / max(checked, 1)
he_mean = float(np.mean(he_list)) if he_list else 0.0
print("pitch windows=%d hit=%.4f he=%.4f" % (checked, hit_rate, he_mean))

# ACF unpitched check on every 2nd 1 s window at 8.82 kHz
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
    "lowest_midi_notes_seen": sorted(set(low_notes))[:10],
    "median_dom_hz": round(float(np.median(dom_list)), 1) if dom_list else 0.0,
    "misses": misses[:12],
    "method": "FFT dominant peak per 0.5 s window, 50-2000 Hz, +/-4% vs active MIDI fund or x2/x3//2",
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
    "wav_bytes": WAV_OUT.stat().st_size,
    "ogg_bytes": OGG_OUT.stat().st_size,
}
with open(ANALYSIS / "render_stats.json", "w") as f:
    json.dump(stats, f, indent=2)

# ---------------- grid visualization (sanctioned visualizer) ----------------
from structures import MusicUnit, MusicEvent, UnitMatrix
from visualization.grid import write_grid_visualization
mat = UnitMatrix(shape=(len(voices), 1))
for r, v in enumerate(voices):
    evs = [MusicEvent(p, vel, s, e) for (s, e, p, vel) in v["notes"]]
    evs.append(MusicEvent(0, 0, last_tick, last_tick))
    mat.set_unit((r, 0), MusicUnit(events=evs))
gv = write_grid_visualization(mat, str(ANALYSIS / "grid_visualization.txt"),
                              ticks_per_character=5040,
                              voice_names=[v["name"] for v in voices], bpm=int(BPM))
print("grid: %s" % gv)


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


prov = {
    "job": "random-style production pass (SP) - LAYER-ALIGNED 2026-09-16",
    "selection_source": "workflows.musicom_workflow.SP_METHODS registry (19 implemented)",
    "selection_file": "/opt/data/sel_20260916.json",
    "seed": SEED,
    "composition_source": str(SRC),
    "composition_sha256": sha256(str(SRC)),
    "production_method": "SP-072",
    "production_method_name": "Three-Partial Pad Bank with Stochastic Microtonal Critters Layer (Brackish Pads-style)",
    "registered_module": "sound.synthesis.critter_pad",
    "layer_discipline": "absolute layer: PadPartialBank replaces timbre for ALL voices; no drums in source; GM kit only in SP-001 reference",
    "voice_profiles": PROFILES,
    "bus_chain": "voice sum -> cassette(0.35 blend) + splosh(0.22) -> peak 0.89 -> normalize_to_lufs(-14) -> Limiter(-1 dB) LAST",
    "fixes": ["render_note peak-normalizes every note to 0.8: velocity gain clip((vel/90)**1.5,0.22,1.30) reapplied at call site",
              "outer half-cosine note envelope + 0.40 s tail per note: click safety for legato zero-gap motif"],
    "checks": {"pitch_verification": pitch_ver, "silence_wet": round(sil, 4),
               "silence_dry": round(sil_dry, 4), "lufs": round(lufs_val, 2), "peak": round(peak_val, 4)},
    "artifacts": {"wav": str(WAV_OUT), "ogg": str(OGG_OUT),
                  "wet_stems": stem_paths, "dry_stems": dry_stems,
                  "dry_reference": str(dry_full)},
}
with open(OUT / "provenance.json", "w") as f:
    json.dump(prov, f, indent=2)
print("provenance.json written")
print("DONE")
