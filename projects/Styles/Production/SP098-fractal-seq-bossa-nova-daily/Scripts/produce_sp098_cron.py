#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SP-098 Fractal Sequence Generator production pass on Latin/bossa-nova-daily-2026-06-15.

Source : Styles/Latin/bossa-nova-daily-2026-06-15/composition.mid
         (bossa nova, 84 BPM, 480 tpb, 2-bar Am7 loop ~5.71s:
          track1 acoustic bass A1 ch0 (8 notes),
          track2 comp Am7 ch1 (36 notes A3/C4/E4/G4),
          track3 bossa drums ch9 (25 hits))

Method : SP-098 -> sound.generators.fractal_seq (SP_METHODS registry;
         adapter not wired in produce() -> module API directly).
         Fractal Sequence Generator — Thue-Morse / Fibonacci / Sierpinski /
         Logistic Map (Kaona B.A.C.H. FRACTAL-style).

Layer  : ABSOLUTE. The fractal engine REPLACES the melodic/harmonic production
         layer for the WHOLE piece: four fractal subsystems generate four voices
         (lead / bass / comp / counter) in the source's key (A natural minor)
         and tempo (84 BPM), expanded from the 2-bar loop to a full 8-bar
         re-composition. FluidSynth GM (SP-001) is the acoustic carrier.

Two-phase architecture (mandatory for generative methods):
  Phase 1: fractal subsystems -> raw note events (unquantized contour / chaos).
  Phase 2: musicom rules -> snap every pitch to A natural minor (diatonic),
           clean monotonic re-timing, voice-range clamp, UnitMatrixComposer
           zero-drift export. Thue-Morse contour is re-mapped from raw +/-1
           SEMITONE steps (module default, collapses to 2 tones when snapped)
           to +/-1 SCALE-DEGREE steps so the binary contour walks the diatonic
           scale. Logistic-map chaotic durations are re-timed monotonically to
           guarantee a valid MIDI timeline.

Chain:
  fractal events (Phase 1) -> scale-snap + re-time (Phase 2)
  -> UnitMatrixComposer (4 voices x 1 section of 8 bars) -> validate() -> to_midi
  -> FluidSynth GM render (FluidR3_GM.sf2) -> per-track stems (RenderPipeline)
  -> normalize_to_lufs(-14) -> Limiter(-1 dBFS) LAST
  -> SP098-fractal-seq-bossa-nova-daily.wav + .ogg (Opus 48k voip)
  -> pitch verification + silence/RMS -> provenance + REPORT.md
"""
import hashlib
import json
import math
import shutil
import subprocess
import wave
from pathlib import Path

import numpy as np

from structures import MusicUnit, MusicEvent, MidiInstrument
from workflows.unitmatrix_composer import UnitMatrixComposer
from sound.render.fluidsynth import discover_soundfont
from sound.render.pipeline import RenderPipeline
from sound.generators.fractal_seq import (
    thue_morse_seq, FibonacciRhythm, SierpinskiAccent, LogisticMapMelody,
)
from sound.effects.mastering import normalize_to_lufs, measure_lufs, Limiter

SRC = Path("/opt/data/repos/musicom/projects/Styles/Latin/bossa-nova-daily-2026-06-15/composition.mid")
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/SP098-fractal-seq-bossa-nova-daily")
AUD = OUT / "Audio"
STEMS_DRY = AUD / "stems_dry"
MIDIDIR = OUT / "MIDI"
ANALYSIS = OUT / "Analysis"
SCRIPTS = OUT / "Scripts"

for d in (AUD, STEMS_DRY, MIDIDIR, ANALYSIS, SCRIPTS):
    d.mkdir(parents=True, exist_ok=True)

SR = 44100
BPM = 84.0
TPB = 480
BAR_TICKS = TPB * 4          # 1920
N_BARS = 8
TOTAL_TICKS = BAR_TICKS * N_BARS   # 15360
SEED = 20261010
TAIL = 1.5                    # seconds of release tail after last note

# ---- key / scale: A natural minor (A B C D E F G) ------------------------
AMIN_PC = {9, 11, 0, 2, 4, 5, 7}
A_OFFSETS = [0, 2, 3, 5, 7, 8, 10]   # semitone offset of each degree from A

_SCALE_NOTES = [n for n in range(21, 109) if (n % 12) in AMIN_PC]


def snap_to_scale(p: int) -> int:
    """Snap a raw MIDI pitch to the nearest A-natural-minor scale tone."""
    p = int(p)
    if p <= _SCALE_NOTES[0]:
        return _SCALE_NOTES[0]
    if p >= _SCALE_NOTES[-1]:
        return _SCALE_NOTES[-1]
    lo, hi = 0, len(_SCALE_NOTES) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if _SCALE_NOTES[mid] < p:
            lo = mid + 1
        else:
            hi = mid
    a, b = _SCALE_NOTES[lo - 1], _SCALE_NOTES[lo]
    return a if (p - a) <= (b - p) else b


def pad(events, total=TOTAL_TICKS):
    """Append a silent terminal landmark so MusicUnit.len_ticks() == total."""
    events.append(MusicEvent(pitch=0, volume=0, start_tick=total, end_tick=total))
    return events


# ===========================================================================
# Phase 1 + 2: generate four fractal voices, quantized to A natural minor
# ===========================================================================

# --- Voice 1: Lead (Thue-Morse binary contour -> diatonic degree walk) ----
lead_events = []
bits = thue_morse_seq(64)              # 64 eighth-notes = 8 bars
degree = 0
for i, b in enumerate(bits):
    degree += 1 if b else -1
    degree = max(-7, min(7, degree))    # clamp to A3..A5 register
    octave, deg = divmod(degree, 7)
    note = 69 + 12 * octave + A_OFFSETS[deg]
    start = i * 240
    lead_events.append(MusicEvent(pitch=note, volume=95,
                                  start_tick=start, end_tick=start + 200))

# --- Voice 2: Bass (Fibonacci metric grouping) ----------------------------
fb = FibonacciRhythm(fib_indices=[2, 3, 5], base_ticks=480, root_pitch=33,
                     repeats=4)
bass_events = []
for e in fb.generate():
    if e.start_tick >= TOTAL_TICKS:
        continue
    end = min(e.start_tick + e.duration_ticks, TOTAL_TICKS)
    if end <= e.start_tick:
        end = e.start_tick + 60
    bass_events.append(MusicEvent(pitch=snap_to_scale(e.pitch), volume=e.velocity,
                                  start_tick=e.start_tick, end_tick=end))

# --- Voice 3: Comp (Sierpinski triangle accent density -> Am chord tones) --
sa = SierpinskiAccent(rows=8, beats_per_bar=16, pitches=(69, 64, 57))
comp_events = []
for e in sa.generate():
    if e.start_tick >= TOTAL_TICKS:
        continue
    end = min(e.start_tick + e.duration_ticks, TOTAL_TICKS)
    comp_events.append(MusicEvent(pitch=snap_to_scale(e.pitch), volume=e.velocity,
                                  start_tick=e.start_tick, end_tick=end))

# --- Voice 4: Counter (Logistic map chaos, monotonic re-time) -------------
lm = LogisticMapMelody(r=3.9, x0=0.5, length=64, pitch_range=(40, 88),
                       ticks_per_beat=480)
counter_events = []
tick = 0
for e in lm.generate():
    dur = max(120, min(960, e.duration_ticks))
    if tick + dur > TOTAL_TICKS:
        break
    note = snap_to_scale(e.pitch)
    vel = max(40, min(110, e.velocity))
    counter_events.append(MusicEvent(pitch=note, volume=vel,
                                     start_tick=tick,
                                     end_tick=tick + max(60, dur - 60)))
    tick += dur

voices = [
    ("Lead", 74, 0, lead_events),      # Flute
    ("Bass", 33, 1, bass_events),      # Acoustic Bass
    ("Comp", 25, 2, comp_events),      # Nylon Guitar
    ("Counter", 12, 3, counter_events),  # Marimba (GM program 12)
]

for name, _, _, evs in voices:
    print("voice %-8s n=%d  last_end=%d" % (name, len(evs),
                                             max((e.end_tick for e in evs), default=0)))

# ===========================================================================
# Build UnitMatrixComposer (musicom engine — zero-drift, no hand-rolled MIDI)
# ===========================================================================
composer = UnitMatrixComposer(bpm=int(BPM), ticks_per_beat=TPB, beats_per_bar=4)
composer.create_matrix(num_voices=len(voices), num_sections=1)
for name, prog, ch, _ in voices:
    composer.add_voice(name, program=prog, channel=ch)
composer.add_section("Fractal", bars=N_BARS)

for name, _, _, evs in voices:
    unit = MusicUnit(events=pad([MusicEvent(pitch=e.pitch, volume=e.volume,
                                            start_tick=e.start_tick,
                                            end_tick=e.end_tick) for e in evs]))
    composer.fill_voice_section(name, "Fractal", unit)

ok, msg = composer.validate()
print("validate:", ok, msg)
assert ok, "zero-drift gate FAILED: " + msg

midi_path = MIDIDIR / "SP098-fractal-seq-bossa-nova-daily.mid"
composer.to_midi(str(midi_path))
assert midi_path.stat().st_size > 40, "MIDI empty/corrupt"
print("MIDI:", midi_path, midi_path.stat().st_size, "bytes")

# copy source MIDI alongside for provenance
shutil.copy2(str(SRC), str(MIDIDIR / SRC.name))

# ===========================================================================
# Ground-truth note list (seconds) for pitch verification
# ===========================================================================
SPB = 60.0 / BPM
all_notes = []      # (pitch, start_s, end_s)
for name, _, _, evs in voices:
    for e in evs:
        if e.pitch == 0:
            continue
        all_notes.append((int(e.pitch), e.start_tick * SPB / TPB,
                          e.end_tick * SPB / TPB))
print("total notes:", len(all_notes),
      "pitch range:", min(p for p, _, _ in all_notes), "-", max(p for p, _, _ in all_notes))

# ===========================================================================
# Render: FluidSynth full mix + stems
# ===========================================================================
SF = discover_soundfont()
assert SF and Path(SF).exists(), "SoundFont missing: %r" % SF
FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        raise RuntimeError("cmd failed %s: %s" % (cmd, r.stderr[-800:]))
    return r

dry_full = OUT / "dry_full_mix_sp001_reference.wav"
print("Rendering full mix (FluidSynth, FluidR3_GM.sf2)...")
run([FLUID, "-ni", "-g", "1.2", "-F", str(dry_full), "-r", str(SR),
     SF, str(midi_path)])
print("dry full mix:", dry_full.stat().st_size, "bytes")

print("Rendering dry stems (RenderPipeline)...")
pipe = RenderPipeline(soundfont_path=SF, fluidsynth_bin=FLUID, sample_rate=SR)
stems = pipe.render_stems(str(midi_path), str(STEMS_DRY), format="wav")
print("stems:", sorted(stems.keys()))


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
        nch, data = 1, (a * 32767.0).astype(np.int16).tobytes()
    else:
        nch = 2
        data = (a * 32767.0).astype(np.int16).reshape(-1).tobytes()
    with wave.open(str(p), "wb") as wf:
        wf.setnchannels(nch)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(data)


# ===========================================================================
# Master: normalize_to_lufs(-14) -> Limiter(-1 dBFS) LAST
# ===========================================================================
mix, _sr = read_wav(dry_full)
print("mix shape:", mix.shape, "sr", _sr)
mix_norm = normalize_to_lufs(mix, target_lufs=-14.0, sample_rate=SR)
limiter = Limiter(threshold_db=-1.0, sample_rate=SR)
final = limiter.process(mix_norm)          # (N, 2)

final_wav = OUT / "SP098-fractal-seq-bossa-nova-daily.wav"
final_ogg = OUT / "SP098-fractal-seq-bossa-nova-daily.ogg"
write_wav(final_wav, final)
print("final WAV:", final_wav.stat().st_size, "bytes")

r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(final_wav),
                    "-codec:a", "libopus", "-application", "voip", "-b:a", "48k",
                    str(final_ogg)], capture_output=True, text=True, timeout=180)
assert r.returncode == 0, "ffmpeg failed: %s" % r.stderr[-300:]
assert final_ogg.stat().st_size > 10000, "OGG empty"
print("final OGG:", final_ogg.stat().st_size, "bytes")

# ===========================================================================
# Verification: silence / RMS / LUFS / pitch fidelity / harmonic energy / ACF
# ===========================================================================
meas_lufs = measure_lufs(final, sample_rate=SR)
peak_val = float(np.max(np.abs(final)))
mono = 0.5 * (final[:, 0] + final[:, 1])
silence_pct = float(np.sum(np.abs(mono) < 0.001) / len(mono)) * 100.0
rms = float(np.sqrt(np.mean(mono ** 2)))
rms_map = [round(float(np.sqrt(np.mean(mono[i:i + SR] ** 2))), 4)
           for i in range(0, len(mono), SR)]
print("LUFS=%.2f peak=%.4f silence=%.2f%% rms=%.4f" % (meas_lufs, peak_val, silence_pct, rms))


def midi_to_freq(n):
    return 440.0 * (2.0 ** ((n - 69) / 12.0))


win = int(0.5 * SR)
n_wins = len(mono) // win
freqs = np.fft.rfftfreq(win, 1.0 / SR)
mask = (freqs >= 50.0) & (freqs <= 2000.0)

checked = hits = 0
he_list, dom_list, misses = [], [], []
for w in range(n_wins):
    t0, t1 = w * 0.5, w * 0.5 + 0.5
    act = set()
    for (p, a, b) in all_notes:
        if a < t1 and b > t0:
            act.add(p)
    if not act:
        continue
    seg = mono[w * win:(w + 1) * win]
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
    # harmonic energy around the dominant frequency (SP-085/SP-092 style)
    tot = np.sum(s_band ** 2) + 1e-12
    he = 0.0
    for k in range(1, 9):
        tf = dom * k
        he += np.sum(s_band[(f_band >= tf - 15.0) & (f_band <= tf + 15.0)] ** 2)
    he_list.append(float(he / tot))

hit_rate = hits / max(checked, 1)
he_mean = float(np.mean(he_list)) if he_list else 0.0

# ACF unpitched check (SP-035 failure signature: 0 Hz / broadband noise)
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

pitch_verdict = "PASS" if (hit_rate >= 0.60 and he_mean >= 0.25
                           and (unpitched / max(acf_n, 1)) < 0.50) else "FAIL"
print("pitch windows=%d hit=%.4f he=%.4f acf_unpitched=%d/%d -> %s"
      % (checked, hit_rate, he_mean, unpitched, acf_n, pitch_verdict))

# ===========================================================================
# Grid visualization (fractal onset DNA)
# ===========================================================================
grid_lines = [
    "SP-098 Fractal Sequence Generator — onset DNA (A natural minor, 84 BPM, 8 bars)",
    "rows = fractal voices, columns = 16th-note slots per bar, '#'=onset '.'=rest",
    "",
]
slot_ticks = TPB // 4   # 120 (16th note)
for name, _, _, evs in voices:
    row = []
    for b in range(N_BARS):
        for s in range(16):
            b0 = b * BAR_TICKS + s * slot_ticks
            b1 = b0 + slot_ticks
            has = any(e.pitch != 0 and e.start_tick < b1 and e.start_tick >= b0 for e in evs)
            row.append("#" if has else ".")
    grid_lines.append("%-8s %s" % (name, "".join(row)))
grid_lines.append("")
grid_lines.append("voice legend: Lead=Thue-Morse degree walk | Bass=Fibonacci groups (2,3,5 beats) | "
                  "Comp=Sierpinski rule-90 accent | Counter=Logistic map (r=3.9) chaos")
(ANALYSIS / "grid_visualization.txt").write_text("\n".join(grid_lines) + "\n")
print("\n".join(grid_lines))

# ===========================================================================
# Provenance + analysis JSON
# ===========================================================================
def sha256(p):
    h = hashlib.sha256()
    with open(str(p), "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

(ANALYSIS / "render_stats.json").write_text(json.dumps({
    "method": "SP-098", "method_module": "sound.generators.fractal_seq",
    "layer": "absolute", "seed": SEED,
    "key": "A natural minor", "bpm": BPM, "bars": N_BARS, "ticks_per_beat": TPB,
    "voices": [{"name": n, "program": p, "channel": c, "n_notes": sum(1 for e in evs if e.pitch != 0)}
               for n, p, c, evs in voices],
    "n_notes_total": len(all_notes),
    "pitch_range": [min(p for p, _, _ in all_notes), max(p for p, _, _ in all_notes)],
    "duration_sec": round(len(mono) / SR, 2),
    "lufs": round(meas_lufs, 2), "peak": round(peak_val, 4),
    "silence_pct": round(silence_pct, 2), "rms": round(rms, 4),
    "rms_per_second": rms_map,
    "windows_checked": checked, "hit_rate": round(hit_rate, 4),
    "harmonic_energy_mean": round(he_mean, 4),
    "acf_windows": acf_n, "acf_unpitched": unpitched,
    "pitch_verdict": pitch_verdict,
    "median_dom_hz": round(float(np.median(dom_list)), 1) if dom_list else 0.0,
}, indent=2))

(ANALYSIS / "pitch_verification.json").write_text(json.dumps({
    "method": "SP-098", "project": "Latin/bossa-nova-daily-2026-06-15",
    "key": "A natural minor", "status": pitch_verdict,
    "hit_rate": round(hit_rate, 4), "harmonic_energy_mean": round(he_mean, 4),
    "acf_unpitched": unpitched, "acf_windows": acf_n,
    "windows_analyzed": checked,
    "median_dom_hz": round(float(np.median(dom_list)), 1) if dom_list else 0.0,
    "misses": misses[:12],
}, indent=2))

provenance = {
    "job": "random-style production (SP) layer-aligned",
    "date": "2026-10-10",
    "seed": SEED,
    "method": "SP-098",
    "method_module": "sound.generators.fractal_seq",
    "method_desc": "Fractal Sequence Generator — Thue-Morse/Fibonacci/Sierpinski/Logistic Map (Kaona B.A.C.H. FRACTAL-style)",
    "layer": "absolute (fractal engine replaces melodic/harmonic production for ALL voices)",
    "selection_source": "workflows.musicom_workflow.SP_METHODS registry (42 implemented)",
    "source_midi": str(SRC),
    "source_sha256": sha256(SRC),
    "output_midi": str(midi_path),
    "output_wav": str(final_wav),
    "output_ogg": str(final_ogg),
    "params": {
        "key": "A natural minor", "bpm": BPM, "bars": N_BARS,
        "thue_morse": {"length": 64, "ticks_per_note": 240, "contour": "+/-1 scale degree"},
        "fibonacci": {"fib_indices": [2, 3, 5], "base_ticks": 480, "root_pitch": 33, "repeats": 4},
        "sierpinski": {"rows": 8, "beats_per_bar": 16, "pitches": [69, 64, 57]},
        "logistic": {"r": 3.9, "x0": 0.5, "length": 64, "pitch_range": [40, 88]},
    },
    "lufs": round(meas_lufs, 2), "peak": round(peak_val, 4),
    "silence_pct": round(silence_pct, 2), "rms": round(rms, 4),
    "pitch_verdict": pitch_verdict, "hit_rate": round(hit_rate, 4),
    "he_mean": round(he_mean, 4),
    "phase2_notes": (
        "Thue-Morse module default emits +/-1 SEMITONE steps from root (collapses to a "
        "2-note G/A oscillation once snapped to A natural minor); Phase-2 re-maps the binary "
        "contour to +/-1 SCALE-DEGREE steps so it walks the full diatonic scale. Logistic-map "
        "chaotic durations re-timed monotonically (clamped 120-960 ticks) to guarantee a valid "
        "zero-drift MIDI timeline. All pitches snapped to A natural minor via snap_to_scale()."
    ),
}
(OUT / "provenance.json").write_text(json.dumps(provenance, indent=2))
(Path("/opt/data/repos/musicom/projects/Styles/Production/.selection_cron.json")).write_text(json.dumps(provenance, indent=2))

(ANALYSIS / "select_20261010.json").write_text(json.dumps({
    "date": "2026-10-10", "method": "SP-098",
    "method_module": "sound.generators.fractal_seq",
    "source_midi": str(SRC),
    "recent_excluded": sorted(["SP-021", "SP-069", "SP-080", "SP-083", "SP-085", "SP-091", "SP-092"]),
    "registry_total": 42, "n_well_formed": 223, "n_candidates": 332,
}, indent=2))

if str(__file__) != str(SCRIPTS / "produce_sp098_cron.py"):
    shutil.copy2(__file__, str(SCRIPTS / "produce_sp098_cron.py"))
print("Done. pitch_verdict=", pitch_verdict)
