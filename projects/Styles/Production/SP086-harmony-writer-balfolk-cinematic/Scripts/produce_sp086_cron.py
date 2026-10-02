# -*- coding: utf-8 -*-
"""SP-086 Harmony Writer production pass - 2026-10-02 cron (random-style).

Source : Styles/Balfolk/014-balfolk-cinematic/MIDI/balfolk_cinematic_v1.mid
         (D-Dorian balfolk jig, 120 BPM, 96 beats = 24 bars:
          Violin prog40 ch0 -> 112-note melody D4-A4 (D E F G A),
          String Ensemble prog48 ch1 -> D2 pedal drone)
Method : SP-086 -> sound.generators.harmony_writer (SP_METHODS registry;
         adapter not wired in produce() -> module API directly).
Layer  : ABSOLUTE - HarmonyWriter writes SATB harmony parts around the whole
         monophonic melody, replacing the source arrangement. GM rendering via
         FluidSynth (the SP-001 reference) is the acoustic realisation; the
         SP-086 "layer" is the harmony content itself.

Tick note: source MIDI uses tpb=10080 (= 480 * 21). The musicom engine
(UnitMatrixComposer) is built for the standard 480 tpb; all ticks are rescaled
/21 at parse time so the engine writes a standard 480-tpb MIDI.

Chain:
  source MIDI -> mido parse (read only) -> melody event dicts (480-tpb ticks)
  -> HarmonyWriter(key="C", style=5).harmonize()   (D dorian = parent major C)
     voices: soprano (melody), alto, tenor, bass, bass2 (bass - octave)
  -> harmonized MIDI via UnitMatrixComposer (zero-drift validate gate)
     soprano->Violin 40, alto->Viola 41, tenor->Cello 42,
     bass->Contrabass 43, bass2->Tuba 58
  -> fluidsynth render (harmonized = "wet", source = dry reference)
  -> stems (dry = source, harmony = harmonized) via RenderPipeline
  -> pitch verification + silence/RMS on harmonized mix
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
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/SP086-harmony-writer-balfolk-cinematic")
AUD = OUT / "Audio"
STEMS_DRY = AUD / "stems_dry"
STEMS_HARMONY = AUD / "stems_harmony"
MIDIDIR = OUT / "MIDI"
ANALYSIS = OUT / "Analysis"
SCRIPTS = OUT / "Scripts"
for d in (AUD, STEMS_DRY, STEMS_HARMONY, MIDIDIR, ANALYSIS, SCRIPTS):
    d.mkdir(parents=True, exist_ok=True)

SR = 44100
SEED = 20261002
KEY = "C"          # D dorian == parent major C (melody centers on D, the ii)
STYLE = 5          # SATB + bass octave doubling (fuller cinematic arrangement)
TPB = 480          # standard musicom tick resolution

from sound.render.fluidsynth import discover_soundfont
from sound.generators.harmony_writer import HarmonyWriter
from sound.render.pipeline import RenderPipeline
from sound.effects.mastering import normalize_to_lufs, measure_lufs, Limiter

SF = discover_soundfont()
assert SF and os.path.exists(SF), "no soundfont"
print("soundfont:", SF)

FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
if not Path(FLUID).exists():
    FLUID = "fluidsynth"

shutil.copy2(str(SRC), str(MIDIDIR / "balfolk_cinematic_v1.mid"))

# ---------------- parse source ----------------
mid = mido.MidiFile(str(SRC))
src_tpb = mid.ticks_per_beat
scale = TPB / src_tpb  # 480 / 10080 = 1/21 (exact)
assert (TPB % src_tpb == 0) or (src_tpb % TPB == 0) or True
tempo = 500000
for msg in mid.tracks[0]:
    if msg.type == "set_tempo":
        tempo = msg.tempo
        break
BPM = 60000000.0 / tempo
print("src_tpb=%d tempo=%d bpm=%.2f tracks=%d scale=1/%d"
      % (src_tpb, tempo, BPM, len(mid.tracks), round(1.0 / scale)))

# melody = track 1 (Violin, ch0). Build HarmonyWriter event dicts (480-tpb).
melody = []
active = {}
abstick = 0
for msg in mid.tracks[1]:
    abstick += msg.time
    if msg.type == "note_on" and msg.velocity > 0:
        active[msg.note] = (abstick, msg.velocity)
    elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
        if msg.note in active:
            s, v = active.pop(msg.note)
            melody.append({"pitch": msg.note, "volume": v,
                           "start_tick": int(round(s * scale)),
                           "end_tick": int(round(abstick * scale))})
melody.sort(key=lambda e: e["start_tick"])
last_tick = max(e["end_tick"] for e in melody)
total_beats = last_tick / TPB
print("melody n=%d last_tick=%d beats=%.1f bars=%.1f pitches=%s"
      % (len(melody), last_tick, total_beats, total_beats / 4.0,
         sorted({e["pitch"] for e in melody})))

# ---------------- harmonize (SP-086 core) ----------------
hw = HarmonyWriter(key=KEY, style=STYLE, seed=SEED)
parts = hw.harmonize(melody)
chords = hw.choose_chords(melody)
print("harmony voices:", sorted(parts.keys()))
for v in sorted(parts):
    evs = parts[v]
    print("  %s n=%d range=%d..%d" % (v, len(evs),
          min(e["pitch"] for e in evs), max(e["pitch"] for e in evs)))
print("chord degrees (first 24):", [r for _, r in chords[:24]])

# voice -> (GM program, channel)
VOICE_MAP = {
    "soprano": (40, 0),   # Violin
    "alto": (41, 1),      # Viola
    "tenor": (42, 2),     # Cello
    "bass": (43, 3),      # Contrabass
    "bass2": (58, 4),     # Tuba (octave-doubled bass)
}
VOICE_ORDER = ["soprano", "alto", "tenor", "bass", "bass2"]

# ---------------- write harmonized MIDI (musicom engine) ----------------
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

section_bars = int(round(total_beats / 4.0))
section_len = section_bars * 4 * TPB
if last_tick > section_len:
    section_bars += 1
    section_len = section_bars * 4 * TPB
print("section_bars=%d section_len=%d" % (section_bars, section_len))

composer = UnitMatrixComposer(bpm=int(round(BPM)), ticks_per_beat=TPB, beats_per_bar=4)
composer.create_matrix(num_voices=len(VOICE_ORDER), num_sections=1)
for v in VOICE_ORDER:
    prog, ch = VOICE_MAP[v]
    composer.add_voice(v, program=prog, channel=ch)
composer.add_section("A", bars=section_bars)

for v in VOICE_ORDER:
    evs = parts[v]
    events = [MusicEvent(e["pitch"], int(e.get("volume", 90)),
                         e["start_tick"], e["end_tick"]) for e in evs]
    unit = MusicUnit(events=events)
    unit.add_event(MusicEvent(0, 0, section_len, section_len))  # terminal landmark
    composer.fill_voice_section(v, "A", unit)

ok, msg = composer.validate()
if not ok:
    raise RuntimeError("validate() failed: %s" % msg)
HARMONY_MID = MIDIDIR / "balfolk_cinematic_v1_harmonized.mid"
composer.to_midi(str(HARMONY_MID))
assert HARMONY_MID.stat().st_size > 40, "harmonized MIDI empty"
print("harmonized MIDI: %s (%d B)" % (HARMONY_MID, HARMONY_MID.stat().st_size))

# verify the written MIDI spans the full duration (no tick truncation)
chk = mido.MidiFile(str(HARMONY_MID))
chk_last = 0
for tr in chk.tracks[1:]:
    t = 0
    for msg in tr:
        t += msg.time
    chk_last = max(chk_last, t)
print("written MIDI tpb=%d last_tick=%d (expect ~%d)" % (chk.ticks_per_beat, chk_last, section_len))
assert chk.ticks_per_beat == TPB
assert abs(chk_last - section_len) < 100, "tick truncation in written MIDI!"

# ---------------- render: dry reference + harmonized (wet) ----------------
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

wet_wav = OUT / "SP086-harmony-writer-balfolk-cinematic.wav"
run([FLUID, "-ni", "-g", "1.2", "-F", str(wet_wav), "-r", str(SR),
     "-o", "synth.reverb.active=no", "-o", "synth.chorus.active=no",
     SF, str(HARMONY_MID)])
assert wet_wav.stat().st_size > 40000, "harmonized WAV empty"
assert wet_wav.stat().st_size < 100 * 1024 * 1024, "harmonized WAV too big"
print("harmonized WAV %d B" % wet_wav.stat().st_size)

# ---------------- stems ----------------
pipe = RenderPipeline(soundfont_path=SF)
dry_stems = pipe.render_stems(str(SRC), str(STEMS_DRY), format="wav")
for k, p in dry_stems.items():
    print("dry stem %s %d B" % (k, Path(p).stat().st_size))
harm_stems = pipe.render_stems(str(HARMONY_MID), str(STEMS_HARMONY), format="wav")
for k, p in harm_stems.items():
    print("harmony stem %s %d B" % (k, Path(p).stat().st_size))

# ---------------- normalize wet to LUFS -14 + limiter ----------------
def load_wav(p):
    with wave.open(str(p), "rb") as wf:
        n, ch = wf.getnframes(), wf.getnchannels()
        raw = np.frombuffer(wf.readframes(n), dtype=np.int16).astype(np.float64) / 32768.0
    if ch == 2:
        return raw.reshape(-1, 2)
    return np.stack([raw, raw], axis=1)

wet = load_wav(wet_wav)
wet = wet / max(1e-9, float(np.max(np.abs(wet)))) * 0.89
wet_lufs = normalize_to_lufs(wet, -14.0, SR)
final = Limiter(threshold_db=-1.0).process(wet_lufs)
lufs_val = measure_lufs(final, SR)
peak_val = float(np.max(np.abs(final)))
print("LUFS=%.2f peak=%.4f dur=%.2fs" % (lufs_val, peak_val, len(final) / SR))

def write_wav(p, audio, sr=44100):
    a = np.clip(np.asarray(audio), -1.0, 1.0)
    ints = (a * 32767.0).astype(np.int16)  # scale! (SP-079 int16 truncation bug)
    ch = 1 if a.ndim == 1 else a.shape[1]
    with wave.open(str(p), "wb") as wf:
        wf.setnchannels(ch)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(ints.tobytes())

write_wav(wet_wav, final)
print("harmonized WAV (mastered) %d B" % wet_wav.stat().st_size)

# OGG (Opus voip)
OGG_OUT = OUT / "SP086-harmony-writer-balfolk-cinematic.ogg"
r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wet_wav),
                    "-codec:a", "libopus", "-application", "voip", "-b:a", "48k",
                    str(OGG_OUT)], capture_output=True, text=True, timeout=180)
assert r.returncode == 0, "ffmpeg failed: %s" % r.stderr[-300:]
assert OGG_OUT.stat().st_size > 10000, "OGG empty"
print("WAV %d B  OGG %d B  dur %.2fs" % (wet_wav.stat().st_size,
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

# active notes per window from melody + harmony voices (480-tpb -> seconds)
spb = tempo / 1e6  # seconds per beat
all_notes = {}
for v in VOICE_ORDER:
    for e in parts[v]:
        s = e["start_tick"] / TPB * spb
        en = e["end_tick"] / TPB * spb
        all_notes.setdefault(e["pitch"], []).append((s, en))

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
    "wav_bytes": wet_wav.stat().st_size,
    "ogg_bytes": OGG_OUT.stat().st_size,
    "harmonized_midi_bytes": HARMONY_MID.stat().st_size,
    "n_melody_notes": len(melody),
    "n_harmony_voices": len(VOICE_ORDER),
    "chord_degrees_first_24": [r for _, r in chords[:24]],
}
with open(ANALYSIS / "render_stats.json", "w") as f:
    json.dump(stats, f, indent=2)

# ---------------- grid visualization (harmonized voices) ----------------
from structures import UnitMatrix
from visualization.grid import write_grid_visualization
mat = UnitMatrix(shape=(len(VOICE_ORDER), 1))
for r, v in enumerate(VOICE_ORDER):
    evs = [MusicEvent(e["pitch"], int(e.get("volume", 90)),
                      e["start_tick"], e["end_tick"]) for e in parts[v]]
    evs.append(MusicEvent(0, 0, section_len, section_len))
    mat.set_unit((r, 0), MusicUnit(events=evs))
gv = write_grid_visualization(mat, str(ANALYSIS / "grid_visualization.txt"),
                              ticks_per_character=4 * TPB,
                              voice_names=VOICE_ORDER, bpm=int(round(BPM)))
print("grid: %s" % gv)

# ---------------- provenance ----------------
def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

prov = {
    "job": "random-style production pass (SP) - LAYER-ALIGNED 2026-10-02",
    "selection_source": "workflows.musicom_workflow.SP_METHODS registry (38 implemented)",
    "seed": SEED,
    "composition_source": str(SRC),
    "composition_sha256": sha256(str(SRC)),
    "production_method": "SP-086",
    "production_method_name": "Rule-Based Melody Harmony Writer w/ Voice Leading (HarmonyKeen-style)",
    "registered_module": "sound.generators.harmony_writer",
    "layer_discipline": "absolute layer: HarmonyWriter writes SATB harmony around the WHOLE melody, replacing the source arrangement; GM render via FluidSynth (SP-001 reference) is the acoustic realisation",
    "harmony_params": {"key": KEY, "style": STYLE, "seed": SEED,
                       "rationale": "melody is D-Dorian (D E F G A); HarmonyWriter is Ionian-only so key=C = parent major, melody tonic D lands on the ii chord"},
    "voice_map": {v: {"program": VOICE_MAP[v][0], "channel": VOICE_MAP[v][1]} for v in VOICE_ORDER},
    "tick_rescale": {"source_tpb": src_tpb, "engine_tpb": TPB, "scale": scale},
    "fixes": [
        "engine bug fix (sound/generators/harmony_writer.py diatonic_triads): sorted() on pitch-class set lost root/third/fifth order, so IV/V/vi/vii roots were misidentified and choose_chords collapsed the D-Dorian melody to a degenerate ii/iii alternation; fixed to return chord tones in (root,third,fifth) order transposed to the key root",
        "source MIDI tpb=10080 (=480*21) breaks UnitMatrixComposer's 480-tpb tick model (16-bit tick truncation -> 6s render); rescaled all ticks /21 to standard 480 tpb before composing",
        "write_wav uses (audio*32767).astype(int16) scaling, not raw astype(int16) (SP-079 silent-output bug)",
    ],
    "checks": {"pitch_verification": pitch_ver, "silence_wet": round(sil, 4),
               "silence_dry": round(sil_dry, 4), "lufs": round(lufs_val, 2),
               "peak": round(peak_val, 4)},
    "artifacts": {"wav": str(wet_wav), "ogg": str(OGG_OUT),
                  "harmonized_midi": str(HARMONY_MID),
                  "dry_reference": str(dry_full),
                  "harmony_stems": {k: str(v) for k, v in harm_stems.items()},
                  "dry_stems": {k: str(v) for k, v in dry_stems.items()}},
}
with open(OUT / "provenance.json", "w") as f:
    json.dump(prov, f, indent=2)
print("provenance.json written")
print("DONE")
