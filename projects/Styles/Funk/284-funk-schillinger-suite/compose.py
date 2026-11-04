# -*- coding: utf-8 -*-
"""284-funk-schillinger-suite -- Funk / Method 018 Schillinger (rework of 081).

Rework of 081-funk-schillinger. Source identity preserved: Funk, Bb major,
100 BPM, Schillinger rhythmic interference (Method 018), trumpet lead +
Rhodes + guitar + bass + clav + backbeat drums.

New version: 8 sections (N+2 over the source's 6), 32 bars, with >=3
variation techniques applied per section. Two-phase architecture (raw
Schillinger draft -> musicom rules post-process). Per-section harmonic
regions. Dual-version export (perfect + humanized).

Engine only: structures + workflows.unitmatrix_composer +
generators.schillinger + rules.voice_leading. No raw mido authoring.
"""
import os
import json
import math

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer, create_empty_unit
from generators.schillinger import SchillingerGenerator

# instrument registry (NOT pip-installed; sanctioned sys.path for registry only)
import sys
sys.path.insert(0, "/opt/data/projects/Instruments")
from instrument_registry import by_name  # noqa: E402

SEED = 20261104
rng = np.random.default_rng(SEED)

PROJ = "/opt/data/projects/Styles/Funk/284-funk-schillinger-suite"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

BPM = 100
TPB = 480
BEATS = 4
BAR = TPB * BEATS            # 1920
GRID = 120                    # 16th note @ 100 BPM
LEAD_LO, LEAD_HI = 58, 88

# Bb major pitch-class set + full scale notes across a wide register
SCALE_PCS = {10, 0, 2, 3, 5, 7, 9}          # Bb C D Eb F G A
SCALE_BASE = [58, 60, 62, 63, 65, 67, 69]   # Bb3..A4
SCALE_NOTES = sorted({n + 12 * o for o in range(-2, 5) for n in SCALE_BASE})

# diatonic triads in Bb major, keyed by root MIDI
CHORDS = {
    58: [58, 62, 65],   # Bb  I
    60: [60, 63, 67],   # Cm  ii
    62: [62, 65, 69],   # Dm  iii
    63: [63, 67, 70],   # Eb  IV
    65: [65, 69, 72],   # F   V
    67: [67, 70, 74],   # Gm  vi
    69: [69, 72, 75],   # Adim vii (unused)
}
CHORD_NAMES = {58: "I", 60: "ii", 62: "iii", 63: "IV", 65: "V", 67: "vi", 69: "vii"}
BASS = {58: 34, 60: 36, 62: 38, 63: 39, 65: 41, 67: 43, 69: 45}

# ---------------------------------------------------------------- form
NAMES = ["Intro", "Verse", "Chorus", "Verse2", "Chorus2", "Bridge",
         "Chorus3", "Outro"]
BARS_PER = 4
N_SECTIONS = len(NAMES)          # 8 (source had 6 -> N+2)
N_BARS = N_SECTIONS * BARS_PER   # 32 bars
SECTION_TICKS = BAR * BARS_PER   # 7680

# Per-section harmonic regions (each section its OWN 4-bar progression).
# This avoids the "bar-0 tonic" bug: section identity is read from the
# MIDPOINT chord (bar index 1), never from bar 0.
SECTION_PROGS = {
    0: [58, 63, 65, 58],   # Intro   I  IV V  I
    1: [58, 67, 60, 65],   # Verse   I  vi ii V
    2: [63, 65, 58, 67],   # Chorus  IV V  I  vi
    3: [58, 67, 60, 65],   # Verse2  I  vi ii V
    4: [63, 65, 58, 67],   # Chorus2 IV V  I  vi
    5: [67, 63, 58, 65],   # Bridge  vi IV I  V   (relative-minor region)
    6: [63, 65, 58, 67],   # Chorus3 IV V  I  vi
    7: [58, 63, 58, 65],   # Outro   I  IV I  V
}

# ---------------------------------------------------------------- variation plan
# Schillinger generator params per section (per-section method change)
SCH_PARAMS = {0: (5, 3), 1: (5, 3), 2: (5, 3), 3: (5, 3),
              4: (5, 3), 5: (7, 4), 6: (5, 3), 7: (5, 3)}
# contour mode: "norm" = sine projection, "inv" = inverted (mirror)
CONTOUR_MODE = {0: "norm", 1: "norm", 2: "norm", 3: "norm",
                4: "norm", 5: "inv", 6: "norm", 7: "norm"}
# rhythm mode: "norm", "aug" (half speed), "retro" (reversed resultant)
RHYTHM_MODE = {0: "aug", 1: "norm", 2: "norm", 3: "norm",
               4: "norm", 5: "norm", 6: "norm", 7: "retro"}
REGISTER = {0: 68, 1: 72, 2: 76, 3: 74, 4: 78, 5: 72, 6: 76, 7: 66}
DENSITY = {0: 20, 1: 30, 2: 40, 3: 30, 4: 40, 5: 36, 6: 44, 7: 20}
# Verse2 lead transposed up a perfect 4th (5 semitones) pre-quantization
TRANSPOSE = {0: 0, 1: 0, 2: 0, 3: 5, 4: 0, 5: 0, 6: 0, 7: 0}

# drums (GM channel-9 note map)
KICK, SNARE, CLAP, HHAT, RIDE, CRASH = 36, 38, 39, 42, 51, 49
TOM_LOW, TOM_MID, TOM_HIGH = 45, 47, 50

# voices: name, registry instrument name, program, channel
VOICES = [
    ("Lead",   "trumpet",        56, 0),
    ("Rhodes", "rhodes",          4, 1),
    ("Guitar", "clean_electric", 27, 2),
    ("Bass",   "electric_bass",  33, 3),
    ("Clav",   "clavi",           7, 4),
    ("Drums",  "drum_kit",        0, 9),
]
N_V = len(VOICES)
vnames = [v[0] for v in VOICES]


def chord_for_bar(bar):
    s, b = divmod(bar, BARS_PER)
    return CHORDS[SECTION_PROGS[s][b]]


def root_for_bar(bar):
    s, b = divmod(bar, BARS_PER)
    return SECTION_PROGS[s][b]


def nearest_scale_tone(pitch):
    return min(SCALE_NOTES, key=lambda n: abs(n - pitch))


def nearest_chord_tone(pitch, tones):
    """Snap pitch to the nearest chord tone in ANY octave (root-relative)."""
    best = min(tones, key=lambda t: abs(t + 12 * round((pitch - t) / 12.0) - pitch))
    return int(best + 12 * round((pitch - best) / 12.0))


# ---------------------------------------------------------------- phase 1
def raw_schillinger_melody(seed, duration_ticks, n_events, center0, a, b,
                           contour_mode, rhythm_mode, transpose_semi=0):
    """Single-voice raw Schillinger walk (unquantized rhythm + raw pitches)."""
    r = np.random.default_rng(seed)
    cycle = SchillingerGenerator(generator_a=a, generator_b=b).generate_resultant()
    if rhythm_mode == "retro":
        cycle = cycle[::-1]
    aug = 2.0 if rhythm_mode == "aug" else 1.0
    total_pulses = float(sum(cycle))
    events = []
    tick = 0
    center = center0
    for i in range(n_events):
        d_pulses = cycle[i % len(cycle)]
        scale = (duration_ticks / n_events) / (total_pulses / len(cycle))
        scale *= aug
        scale *= (0.9 + 0.25 * r.random())     # raw: jittered, off-grid
        dur = int(d_pulses * scale)
        dur = max(90, min(dur, duration_ticks - tick))
        sinv = 4.0 * math.sin(i * 0.55)
        p = (center - sinv) if contour_mode == "inv" else (center + sinv)
        p += r.normal(0.0, 1.1)
        p += transpose_semi
        p = max(LEAD_LO, min(LEAD_HI, p))
        midi = int(round(p))
        vel = int(np.clip(62 + 24 * abs(math.sin(i * 1.23)), 46, 106))
        if tick + dur > duration_ticks:
            dur = duration_ticks - tick
        if dur > 0:
            events.append(MusicEvent(pitch=midi, volume=vel,
                                     start_tick=tick, end_tick=tick + dur))
        tick += dur
        center += r.normal(0.0, 0.9)
    return events


phase1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase1.create_matrix(num_voices=1, num_sections=N_SECTIONS)
phase1.add_voice("LeadRaw", program=56, channel=0)
for s, name in enumerate(NAMES):
    phase1.add_section(name, bars=BARS_PER)
    a, b = SCH_PARAMS[s]
    evs = raw_schillinger_melody(SEED + s, SECTION_TICKS, DENSITY[s],
                                 REGISTER[s], a, b, CONTOUR_MODE[s],
                                 RHYTHM_MODE[s], TRANSPOSE[s])
    # terminal landmark (zero-drift)
    evs.append(MusicEvent(pitch=0, volume=0, start_tick=SECTION_TICKS - 1,
                          end_tick=SECTION_TICKS))
    phase1.set_unit(0, s, MusicUnit(events=evs))
ok1, msg1 = phase1.validate()
print("PHASE1 validate:", msg1)
P1_MIDI = os.path.join(MIDI_DIR, "284-funk-schillinger-suite-phase1.mid")
phase1.to_midi(P1_MIDI)
print("phase1 written", P1_MIDI)

# ---------------------------------------------------------------- phase 2
def process_lead(raw_events, s):
    """Rules post-process: grid lock -> scale -> chord-tone -> voice-leading."""
    pitched = [e for e in raw_events if e.pitch != 0]
    # (1) rhythm-grid lock to the 16th grid
    g = []
    for e in pitched:
        st = int(round(e.start_tick / GRID) * GRID)
        st = min(st, SECTION_TICKS - GRID)
        g.append(MusicEvent(pitch=e.pitch, volume=e.volume, start_tick=st,
                            end_tick=max(st + GRID, e.end_tick)))
    # (2) scale degree, then (3) chord-tone quantization per bar
    q = []
    for e in g:
        p = e.pitch
        p = nearest_scale_tone(p)
        bar = s * BARS_PER + min(e.start_tick // BAR, BARS_PER - 1)
        p = nearest_chord_tone(p, chord_for_bar(bar))
        q.append(MusicEvent(pitch=p, volume=e.volume, start_tick=e.start_tick,
                            end_tick=e.end_tick))
    # (4) voice leading: cap leaps to <= 9 semitones
    for i in range(1, len(q)):
        if abs(q[i].pitch - q[i - 1].pitch) > 9:
            bar = s * BARS_PER + min(q[i].start_tick // BAR, BARS_PER - 1)
            q[i].pitch = nearest_chord_tone(q[i - 1].pitch, chord_for_bar(bar))
    # (5) dedup collided (start_tick, pitch) keeping longest duration
    best = {}
    for e in q:
        key = (e.start_tick, e.pitch)
        if key not in best or e.end_tick > best[key].end_tick:
            best[key] = e
    return sorted(best.values(), key=lambda e: (e.start_tick, e.pitch))


phase2 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase2.create_matrix(num_voices=N_V, num_sections=N_SECTIONS)
for name, _, prog, ch in VOICES:
    phase2.add_voice(name, program=prog, channel=ch)
for n in NAMES:
    phase2.add_section(n, bars=BARS_PER)

# --- lead (row 0): quantize phase-1 raw draft per section
lead_chunks = {}
for s in range(N_SECTIONS):
    raw_events = list(phase1.matrix.get_unit((0, s)).events)
    lead_events = process_lead(raw_events, s)
    lead_chunks[s] = lead_events
    phase2.set_unit(0, s, MusicUnit(events=lead_events))

# accompaniment accumulation (cells start as None -> collect then set once)
acc = {(r, s): [] for r in range(1, 5) for s in range(N_SECTIONS)}

# --- rhodes (row 1): 8th-note comp on 3rd/5th above the chord
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    tones = chord_for_bar(bar)
    t0 = b * BAR
    third, fifth = tones[1] + 12, tones[2] + 12
    for k in range(0, BAR, 480):
        even = (k // 480) % 2 == 0
        acc[(1, s)].append(MusicEvent(
            pitch=third if even else fifth, volume=56 if even else 50,
            start_tick=t0 + k, end_tick=t0 + k + 420))

# --- guitar (row 2): offbeat wah stabs, chorus push
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    tones = chord_for_bar(bar)
    t0 = b * BAR
    for off in (720, 1200, 1680):
        p = tones[(off // 240) % len(tones)] + 12
        acc[(2, s)].append(MusicEvent(
            pitch=p, volume=62, start_tick=t0 + off, end_tick=t0 + off + 100))
    if s in (2, 4, 6):
        acc[(2, s)].append(MusicEvent(
            pitch=tones[0] + 12, volume=66, start_tick=t0 + 120,
            end_tick=t0 + 200))

# --- bass (row 3): octave pulse root/fifth, chorus 16th push, bridge sustained
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    root = BASS[root_for_bar(bar)]
    fifth = root + 7
    t0 = b * BAR
    e = [
        MusicEvent(pitch=root, volume=104, start_tick=t0, end_tick=t0 + 340),
        MusicEvent(pitch=fifth, volume=88, start_tick=t0 + 480, end_tick=t0 + 820),
        MusicEvent(pitch=root, volume=104, start_tick=t0 + 960, end_tick=t0 + 1300),
        MusicEvent(pitch=fifth, volume=88, start_tick=t0 + 1440, end_tick=t0 + 1780),
    ]
    if s in (2, 4, 6):
        e.append(MusicEvent(pitch=root, volume=94, start_tick=t0 + 1800,
                            end_tick=t0 + 1910))
    if s == 5:  # bridge: sustained roots (sparse harmonic anchor)
        e = [MusicEvent(pitch=root, volume=100, start_tick=t0, end_tick=t0 + 1700)]
    acc[(3, s)].extend(e)

# --- clav (row 4): horn stabs in chorus/chorus2, counterline in chorus3
for bar in range(N_BARS):
    s, b = divmod(bar, BARS_PER)
    if s not in (2, 4, 6):
        continue
    tones = chord_for_bar(bar)
    t0 = b * BAR
    if s == 6:
        # counterline: diatonic-third harmony of the lead (snapped to chord)
        for le in lead_chunks[s]:
            if b * BAR <= le.start_tick < (b + 1) * BAR:
                cp = nearest_chord_tone(le.pitch + 4, tones)
                acc[(4, s)].append(MusicEvent(
                    pitch=cp, volume=max(40, le.volume - 8),
                    start_tick=le.start_tick, end_tick=le.end_tick))
    else:
        for off in (0, 720, 1200, 1680):
            p = tones[(off // 240) % len(tones)] + 24
            acc[(4, s)].append(MusicEvent(
                pitch=p, volume=70, start_tick=t0 + off, end_tick=t0 + off + 110))

# set accompaniment units
for (r, s), evs in acc.items():
    phase2.set_unit(r, s, MusicUnit(events=evs))

# --- drums (row 5): funk backbeat, per-section density + bridge tom fill
DRUM_DENS = {0: 0.5, 1: 0.8, 2: 1.0, 3: 0.8, 4: 1.0, 5: 0.7, 6: 1.0, 7: 0.4}
for s in range(N_SECTIONS):
    dens = DRUM_DENS[s]
    evs = []
    for bar in range(BARS_PER):
        t0 = bar * BAR
        for k in range(0, BAR, 240):
            evs.append(MusicEvent(pitch=HHAT, volume=58,
                                  start_tick=t0 + k, end_tick=t0 + k + 90))
        evs.append(MusicEvent(pitch=KICK, volume=104, start_tick=t0,
                              end_tick=t0 + 160))
        evs.append(MusicEvent(pitch=KICK, volume=100, start_tick=t0 + 960,
                              end_tick=t0 + 1120))
        if dens >= 0.7:
            evs.append(MusicEvent(pitch=SNARE, volume=104, start_tick=t0 + 480,
                                  end_tick=t0 + 620))
            evs.append(MusicEvent(pitch=SNARE, volume=110, start_tick=t0 + 1440,
                                  end_tick=t0 + 1580))
        if dens >= 1.0:
            evs.append(MusicEvent(pitch=CLAP, volume=90, start_tick=t0 + 480,
                                  end_tick=t0 + 600))
            evs.append(MusicEvent(pitch=CLAP, volume=95, start_tick=t0 + 1440,
                                  end_tick=t0 + 1560))
            evs.append(MusicEvent(pitch=RIDE, volume=72, start_tick=t0,
                                  end_tick=t0 + 600))
        if s == 5 and bar == BARS_PER - 1:  # bridge tom fill (last bar)
            for j, tom in enumerate((TOM_LOW, TOM_MID, TOM_HIGH)):
                evs.append(MusicEvent(pitch=tom, volume=88,
                                      start_tick=t0 + 1440 + j * 120,
                                      end_tick=t0 + 1440 + j * 120 + 100))
    phase2.set_unit(5, s, MusicUnit(events=evs))

# --- voice-leading check (rules.voice_leading) between bass + lead
from rules.voice_leading import VoiceLeadingRules  # noqa: E402

vlc = VoiceLeadingRules(style="classical")
vl_flags = []
for bar in range(N_BARS - 1):
    s, b = divmod(bar, BARS_PER)
    bass_a = BASS[root_for_bar(bar)]
    bass_b = BASS[root_for_bar(bar + 1)]
    la = [e for e in lead_chunks[s] if e.pitch > 0 and b * BAR <= e.start_tick < (b + 1) * BAR]
    lb = [e for e in lead_chunks[s] if e.pitch > 0 and (b + 1) * BAR <= e.start_tick < (b + 2) * BAR]
    if la and lb:
        viol = vlc.check_parallel_motion([bass_a, la[0].pitch], [bass_b, lb[0].pitch])
        if viol:
            vl_flags.append((bar, viol))
        hid = vlc.check_hidden_fifths([bass_a, la[0].pitch], [bass_b, lb[0].pitch])
        if hid:
            vl_flags.append((bar, hid))
print("VOICE-LEADING flags (bass+lead):", vl_flags[:8], "total", len(vl_flags))

# --- normalize every cell to exact section boundary (zero-drift invariant)
def normalize_cell(unit, total_ticks):
    evs = list(unit.events)
    for e in evs:
        if e.end_tick > total_ticks:
            e.end_tick = total_ticks
    if not any(e.pitch == 0 and e.end_tick == total_ticks for e in evs):
        evs.append(MusicEvent(pitch=0, volume=0, start_tick=total_ticks - 1,
                              end_tick=total_ticks))
    evs.sort(key=lambda e: (e.start_tick, e.pitch))
    return MusicUnit(events=evs)

for v in range(N_V):
    for s in range(N_SECTIONS):
        u = phase2.matrix.get_unit((v, s))
        if u is None or len(u.events) == 0:
            phase2.set_unit(v, s, create_empty_unit(SECTION_TICKS))
        else:
            phase2.set_unit(v, s, normalize_cell(u, SECTION_TICKS))

ok2, msg2 = phase2.validate()
print("PHASE2 validate:", msg2)
assert ok1 and ok2, (msg1, msg2)

# --- dual-version export (perfect grid-locked + humanized)
from workflows.humanize import export_dual  # noqa: E402

hz_instruments = {v[0]: by_name(v[1]).humanize_dna for v in VOICES}
hz_seed = SEED
PERF_MIDI = os.path.join(MIDI_DIR, "284-funk-schillinger-suite-perfect.mid")
HUM_MIDI = os.path.join(MIDI_DIR, "284-funk-schillinger-suite-humanized.mid")
hz = export_dual(phase2, PERF_MIDI, HUM_MIDI, style="funk", seed=hz_seed,
                 bpm=BPM, instruments=hz_instruments)
print("dual-version exported")

# ---------------------------------------------------------------- analysis
from visualization.grid import write_grid_visualization  # noqa: E402

grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
write_grid_visualization(phase2.matrix, grid_path, ticks_per_character=120,
                         voice_names=vnames, bpm=BPM,
                         mode="Bb major / Method 018 Schillinger + funk (rework of 081)")

# provenance
from workflows.provenance import write_provenance, AI_ASSISTED  # noqa: E402

section_roots = [SECTION_PROGS[s][1] for s in range(N_SECTIONS)]  # midpoint
assert len(set(section_roots)) > 1, "section roots all equal -> bar-0 tonic bug"

provenance_meta = {
    "bpm": BPM, "key": "Bb major", "sections": N_SECTIONS, "bars": N_BARS,
    "rework_of": "081-funk-schillinger", "rework_kind": "redesign (missing index.html/provenance; full rebuild preserving identity)",
    "per_section_progs": {NAMES[s]: [CHORD_NAMES[r] for r in SECTION_PROGS[s]] for s in range(N_SECTIONS)},
    "section_roots_midpoint": [CHORD_NAMES[r] for r in section_roots],
    "variation_techniques": [
        "augmentation (Intro: resultant durations x2)",
        "register shift (lead center 66->78->66)",
        "transposition (Verse2: lead up perfect 4th)",
        "per-section method change (Bridge: Schillinger a=7,b=4)",
        "inversion (Bridge: contour mirrored)",
        "mode shift (Bridge: relative-minor Gm region)",
        "retrograde (Outro: reversed resultant)",
        "counterline (Chorus3: diatonic-third harmony in Clav)",
    ],
    "seed": SEED, "humanize_seed": hz_seed,
}
write_provenance(P1_MIDI, AI_ASSISTED,
                 "Schillinger System of Musical Design (Method 018) + musicom rules",
                 parameters=dict(provenance_meta, phase="1"),
                 notes="raw single-voice Schillinger draft, fractional off-grid durations, "
                       "sine/inverted contour + register drift, no harmony")
write_provenance(PERF_MIDI, AI_ASSISTED,
                 "Schillinger System of Musical Design (Method 018) + musicom rules",
                 parameters=dict(provenance_meta, phase="2-perfect", humanize=None),
                 notes="grid-locked perfect layer: 16th grid, chord-tone quantized, "
                       "voice-leading checked, zero humanization")
write_provenance(HUM_MIDI, AI_ASSISTED,
                 "Schillinger System of Musical Design (Method 018) + musicom rules",
                 parameters=dict(provenance_meta, phase="2-humanized",
                                 humanize_seed=hz_seed, humanize_profiles=hz),
                 notes="humanized layer: style profile (funk) + per-instrument DNA")

# summary.json
with open(os.path.join(ANALYSIS_DIR, "summary.json"), "w") as f:
    json.dump(provenance_meta, f, indent=2)

print("PROGRESSION (per section):")
for s in range(N_SECTIONS):
    print("  ", NAMES[s], [CHORD_NAMES[r] for r in SECTION_PROGS[s]],
          "midpoint root:", CHORD_NAMES[SECTION_PROGS[s][1]])
print("SECTION ROOTS (midpoint):", [CHORD_NAMES[r] for r in section_roots])

# ---------------------------------------------------------------- verification
# READING ONLY (analysis) -- mido readback audits
import mido  # noqa: E402


def audit_midi(path, drums_channel=9):
    mid = mido.MidiFile(path)
    def total(tr):
        t = 0
        for m in tr:
            if not m.is_meta:
                t += m.time
        return t
    tots = [total(t) for t in mid.tracks]
    voice_tots = tots[1:]
    zero_drift = len(set(voice_tots)) == 1
    offgrid = 0
    scale_viol = 0
    chord_viol = 0
    pitched = 0
    for i, tr in enumerate(mid.tracks):
        if i == 0:
            continue
        is_drums = any(getattr(m, "channel", None) == drums_channel for m in tr)
        t = 0
        for m in tr:
            if not m.is_meta:
                t += m.time
            if m.type == "note_on" and m.velocity > 0:
                if is_drums:
                    continue
                pitched += 1
                if not (t % 120 == 0 or t % 240 == 0):
                    offgrid += 1
                if (m.note % 12) not in SCALE_PCS:
                    scale_viol += 1
                bar = t // BAR
                if bar >= N_BARS:
                    bar = N_BARS - 1
                chord_pcs = {c % 12 for c in chord_for_bar(bar)}
                if (m.note % 12) not in chord_pcs:
                    chord_viol += 1
    return {
        "path": path, "size": os.path.getsize(path),
        "voice_tracks": len(mid.tracks) - 1, "track_lens": voice_tots,
        "zero_drift": zero_drift, "pitched": pitched, "offgrid": offgrid,
        "scale_viol": scale_viol, "chord_viol": chord_viol,
    }

results = {
    "phase1": audit_midi(P1_MIDI),
    "perfect": audit_midi(PERF_MIDI),
    "humanized": audit_midi(HUM_MIDI),
}
for k, v in results.items():
    print(f"[{k}] size={v['size']} voices={v['voice_tracks']} lens={v['track_lens']} "
          f"drift_ok={v['zero_drift']} pitched={v['pitched']} offgrid={v['offgrid']} "
          f"scale_viol={v['scale_viol']} chord_viol={v['chord_viol']}")
    assert v["size"] > 40, "empty MIDI: %s" % k

assert results["perfect"]["offgrid"] == 0, "perfect off-grid != 0"
assert results["humanized"]["offgrid"] > 0, "humanized off-grid == 0 (jitter did not run)"
assert results["perfect"]["scale_viol"] == 0, "scale violations in perfect"
assert results["perfect"]["chord_viol"] == 0, "chord violations in perfect"
assert results["perfect"]["zero_drift"], "zero-drift failed on perfect"
assert results["humanized"]["zero_drift"], "zero-drift failed on humanized"

with open(os.path.join(ANALYSIS_DIR, "rework_audit.json"), "w") as f:
    json.dump({
        "chosen": "081-funk-schillinger",
        "genre": "Funk",
        "standard_failures": ["missing index.html + root provenance.json"],
        "redesign_required": True,
        "source_identity": {
            "key": "Bb major", "tempo": 100, "method": "018 Schillinger",
            "voices": ["trumpet", "rhodes", "guitar", "bass", "clav", "drums"],
        },
        "new_project": "284-funk-schillinger-suite",
        "verification": {k: v for k, v in results.items()},
    }, f, indent=2)

print("ALL MIDI VERIFICATION PASSED")
print("OFF-GRID perfect=0 humanized=%d | scale_viol=0 chord_viol=0"
      % results["humanized"]["offgrid"])
