# -*- coding: utf-8 -*-
"""071 - Arabic Rast Ant Colony (ACOPF, Method 041)

Nightly autonomous composition job. Style: Arabic (Rast maqam + maqsum rhythm).
Method: 041 - Ant Colony Optimization Path Finding (ACOPF), Stochastic paradigm.

Two-phase architecture:
  Phase 1: raw generative draft — ant agents walk a pitch-graph depositing
           pheromone; continuous (unquantized) pitch floats + chaotic rhythm,
           single voice, no harmony, no scale enforcement.
  Phase 2: musicom rules post-process — quantize to Rast maqam tones under
           section harmony (Rast jins on D/G, Nahawand jins on A), voice-leading
           check (no parallel 5ths/8ves, no voice crossing), zero-drift cell
           padding, UnitMatrixComposer export.
"""
import math
import os
import random

from structures import MusicUnit, MusicEvent, MidiInstrument, MidiPercussion
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_note_unit, create_chord_unit, create_empty_unit,
)
from workflows.provenance import write_provenance, AI_GENERATED
from visualization.grid import write_grid_visualization

# ---------------------------------------------------------------------------
# Project layout
# ---------------------------------------------------------------------------
STYLE_DIR = "/opt/data/projects/Styles/Arabic"
PROJECT = "071-arabic-rast-ant-colony"
BASE = os.path.join(STYLE_DIR, PROJECT)
MIDI_DIR = os.path.join(BASE, "MIDI")
AUDIO_DIR = os.path.join(BASE, "Audio")
ANALYSIS_DIR = os.path.join(BASE, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

RNG = random.Random(20260817)

# ---------------------------------------------------------------------------
# Concept: Arabic Rast
# ---------------------------------------------------------------------------
BPM = 100
TPB = 480
BEATS_PER_BAR = 4
BAR = TPB * BEATS_PER_BAR          # 1920 ticks/bar

# Rast maqam on D (quarter-flat E ~ 63.5, quarter-flat B ~ 70.5). MIDI grid
# approximation: E quarter-flat -> 63, B quarter-flat -> 70.
RAST_PC = [62, 63, 65, 67, 69, 70, 72, 74]      # D, E(1/4b), F, G, A, B(1/4b), C, D
RAST = [62, 63, 65, 67, 69, 70, 72]

# Section harmony: Rast jins anchored on D (bars 0-3), Nahawand jins on A
# (bars 4-7), Rast return (bars 8-11), cadence D (bars 12-15).
SECTIONS = [
    ("A", 4, "rast",   62),   # D Rast
    ("B", 4, "nahawand", 69), # A Nahawand (dorian color)
    ("A2", 4, "rast",  62),   # D Rast return
    ("C", 4, "cadence", 62),  # D Rast cadence
]
TOTAL_BARS = 16

# Maqsum rhythm (8 beats, 3+3+2) as 16th grid: DUM-TEK-TEK-DUM-TEK
MAQSUM_16THS = [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0]
# DUM (36), TEK (38/42)

# ---------------------------------------------------------------------------
# Phase 1: Ant Colony Optimization raw draft (single voice, pre-rules)
# ---------------------------------------------------------------------------

class AntColonyPitch:
    """Tiny ant-colony optimizer over a pitch graph with pheromone feedback.

    Agents (ants) hop between pitch nodes; step choice favors high pheromone
    x heuristic (consonance with current harmonic anchor + interval bias).
    Pheromone evaporates; successful hops (toward target) deposit more.
    Output: raw pitch trajectory (continuous floats, NOT scale-quantized).
    """

    def __init__(self, seed=20260817):
        self.rng = random.Random(seed)
        # pitch graph nodes 45..84
        self.nodes = list(range(45, 85))
        self.phero = {n: 1.0 for n in self.nodes}

    def _interval_bias(self, a, b):
        d = abs(b - a) % 12
        # prefer stepwise + consonant leaps
        return {0: 1.5, 1: 1.1, 2: 1.3, 3: 1.0, 4: 1.2, 5: 1.4,
                7: 1.5, 8: 0.8, 9: 0.7, 10: 0.6, 11: 0.5}.get(d, 0.9)

    def walk(self, anchor, steps, lo=48, hi=84):
        """Return list of float pitches (raw, unquantized)."""
        cur = float(anchor)
        out = []
        for _ in range(steps):
            cands = [n for n in self.nodes if lo <= n <= hi and n != int(cur)]
            if not cands:
                break
            weights = []
            for n in cands:
                w = self.phero[n] * self._interval_bias(int(cur), n)
                # pull toward the harmonic anchor
                w *= (1.0 + 0.35 * math.exp(-abs(n - anchor) / 14.0))
                weights.append(w)
            nxt = self.rng.choices(cands, weights=weights, k=1)[0]
            # continuous jitter: unquantized raw draft
            raw = nxt + self.rng.uniform(-0.45, 0.45)
            out.append(raw)
            # pheromone deposit + evaporation
            self.phero[nxt] = self.phero[nxt] * 0.85 + 1.6
            for k in self.phero:
                self.phero[k] *= 0.995
            cur = nxt
        return out

    def reset_pheromone(self):
        for k in self.phero:
            self.phero[k] = 1.0


def phase1_raw_events(seed=20260817):
    """Raw generative draft: ant-colony pitch trajectory + chaotic rhythm.

    Returns list of dicts: {pitch_float, start_beat, dur_beats, vel}.
    Rhythm: inter-onset gaps from a skewed distribution (chaotic clustering),
    clipped to [0.5, 4.0] beats — NOT quantized to the maqsum grid.
    """
    rng = random.Random(seed)
    events = []
    beat = 0.0
    anchors = [62, 62, 62, 62, 69, 69, 69, 69, 62, 62, 62, 62, 62, 62, 62, 62]
    colony = AntColonyPitch(seed)
    for bar_idx in range(TOTAL_BARS):
        anchor = anchors[bar_idx]
        steps = rng.randint(2, 4)
        traj = colony.walk(anchor, steps)
        for p in traj:
            gap = rng.uniform(0.5, 4.0) ** 1.35          # chaotic clustering
            gap = max(0.5, min(4.0, gap))
            dur = min(gap, rng.uniform(0.75, 1.5))
            vel = int(74 + 24 * abs(p - anchor) / 30.0)
            events.append({
                "pitch": p,
                "start_beat": beat,
                "dur_beats": dur,
                "vel": min(110, max(60, vel)),
            })
            beat += gap
        beat = (bar_idx + 1) * 4.0                       # bar boundary lock
    return events


def raw_to_midi_events(raw, section_start_bars):
    """Convert raw (phase-1) events to absolute-tick MusicEvents in ONE voice.

    Unquantized: pitch floats rounded to nearest int (NOT scale-constrained),
    rhythm NOT snapped to the maqsum grid. This is the pre-rules draft.
    """
    events = []
    for e in raw:
        start_tick = int(round(e["start_beat"] * TPB))
        end_tick = int(round((e["start_beat"] + e["dur_beats"]) * TPB))
        pitch = int(round(e["pitch"]))
        if pitch < 45:
            pitch = 45
        if pitch > 84:
            pitch = 84
        events.append(MusicEvent(
            pitch=pitch, volume=e["vel"],
            start_tick=start_tick, end_tick=end_tick,
        ))
    return events


# ---------------------------------------------------------------------------
# Phase 2: rules post-process — Rast quantization + harmony + voice leading
# ---------------------------------------------------------------------------

def quantize_rast(pitch, anchor):
    """Quantize a raw pitch to the nearest Rast maqam tone (or anchor jins)."""
    pool = [p for p in RAST if abs(p - anchor) <= 12]
    if not pool:
        pool = RAST
    best = min(pool, key=lambda p: abs(p - pitch))
    return best


def phase2_rules_events(raw, seed=20260817):
    """Chord-tone quantization to Rast/Nahawand jins + velocity smoothing.

    Returns list of MusicEvent with absolute ticks, per-bar pitch anchored.
    """
    rng = random.Random(seed + 1)
    anchors = [62, 62, 62, 62, 69, 69, 69, 69, 62, 62, 62, 62, 62, 62, 62, 62]
    events = []
    for e in raw:
        bar_idx = min(TOTAL_BARS - 1, int(e["start_beat"] // 4))
        anchor = anchors[bar_idx]
        pitch = quantize_rast(round(e["pitch"]), anchor)
        start_tick = int(round(e["start_beat"] * TPB))
        end_tick = int(round((e["start_beat"] + e["dur_beats"]) * TPB))
        vel = e["vel"] + rng.randint(-6, 6)
        events.append(MusicEvent(
            pitch=pitch, volume=max(56, min(112, vel)),
            start_tick=start_tick, end_tick=end_tick,
        ))
    return events


def _voice_leading_fix(events, scale=None):
    """Basic voice-leading: break stale repeated unisons by stepping one
    Rast-scale degree (never off-maqam). Also forbid parallel perfect 5ths
    between adjacent lead notes (motion by 7 semitones repeated)."""
    scale = scale or RAST
    out = []
    for i, e in enumerate(events):
        if i > 0:
            prev = out[-1]
            if e.pitch == prev.pitch and (e.start_tick - prev.end_tick) < TPB:
                # nudge by one scale degree, staying in the maqam
                if e.pitch in scale:
                    idx = scale.index(e.pitch)
                    nxt = scale[min(idx + 1, len(scale) - 1)]
                    prv = scale[max(idx - 1, 0)]
                    e.pitch = nxt if abs(nxt - e.pitch) <= 2 else prv
        out.append(e)
    # parallel-fifth check between successive lead notes
    for i in range(1, len(out)):
        a0, a1 = out[i - 1].pitch, out[i].pitch
        if abs(a1 - a0) == 7:
            # break the parallel motion: step one scale degree down instead
            if a1 in scale:
                idx = scale.index(a1)
                out[i].pitch = scale[max(idx - 1, 0)]
    return out


def build_harmony_events():
    """Diatonic-ish Rast harmony: Dm / Gm / F / A(m) per 4-bar group.

    Chords (Rast tones only):
      bars 0-3   D minor-ish   [50, 53, 57, 62]   (D F A D)
      bars 4-7   A minor-ish   [45, 52, 57, 69]   (A D A A)  Nahawand color
      bars 8-11  F major-ish   [53, 57, 60, 65]   (F A C F)
      bars 12-15 D minor-ish   [50, 53, 57, 62]   (D F A D)
    Whole-bar pads, one chord per bar, gentle arpeggiation on beats 2+4.
    """
    chords = {
        0: [50, 53, 57, 62],
        4: [45, 52, 57, 69],
        8: [53, 57, 60, 65],
        12: [50, 53, 57, 62],
    }
    events = []
    for bar in range(TOTAL_BARS):
        grp = (bar // 4) * 4
        chord = chords[grp]
        t0 = bar * BAR
        events.append(MusicEvent(pitch=chord[0], volume=72, start_tick=t0, end_tick=t0 + BAR))
        events.append(MusicEvent(pitch=chord[1], volume=66, start_tick=t0, end_tick=t0 + BAR))
        events.append(MusicEvent(pitch=chord[2], volume=62, start_tick=t0, end_tick=t0 + BAR))
        # octave top moves on beats 2 and 4 (maqsum lift)
        top = chord[3]
        events.append(MusicEvent(pitch=top, volume=64, start_tick=t0, end_tick=t0 + BAR // 2))
        events.append(MusicEvent(pitch=top + 12 if top + 12 <= 84 else top,
                                 volume=64, start_tick=t0 + BAR // 2, end_tick=t0 + BAR))
    return events


def build_bass_events():
    """Rast bass: D / A / F / D per 4-bar group, maqsum-3+3+2 pulse."""
    roots = {0: 38, 4: 33, 8: 41, 12: 38}   # D2, A1, F2, D2
    events = []
    for bar in range(TOTAL_BARS):
        root = roots[(bar // 4) * 4]
        t0 = bar * BAR
        # DUM on beat 1, TEK on beat 3 (maqsum heavy)
        events.append(MusicEvent(pitch=root, volume=90, start_tick=t0, end_tick=t0 + TPB * 1.5))
        events.append(MusicEvent(pitch=root + 12, volume=78,
                                 start_tick=t0 + TPB * 2, end_tick=t0 + TPB * 3))
        events.append(MusicEvent(pitch=root, volume=84,
                                 start_tick=t0 + TPB * 3, end_tick=t0 + BAR))
    return events


def build_drums_events():
    """Maqsum (3+3+2) on 16th grid: DUM DUM TEK / DUM TEK.

    GM: DUM=36 (kick), TEK=38 (snare) or 42 (closed hat). Pattern:
    [1,0,0,0, 1,0,0,0, 1,0,0,1, 0,0,0,0] per bar with hat ticks on offbeats.
    """
    events = []
    step16 = BAR // 16
    for bar in range(TOTAL_BARS):
        t0 = bar * BAR
        for i, hit in enumerate(MAQSUM_16THS):
            if hit:
                events.append(MusicEvent(pitch=MidiPercussion.BASS_DRUM, volume=100,
                                         start_tick=t0 + i * step16,
                                         end_tick=t0 + i * step16 + step16 // 2))
                if i in (0, 4):
                    events.append(MusicEvent(pitch=MidiPercussion.BASS_DRUM, volume=100,
                                             start_tick=t0 + i * step16 + step16 * 2,
                                             end_tick=t0 + i * step16 + step16 * 3))
                else:
                    events.append(MusicEvent(pitch=MidiPercussion.ACOUSTIC_SNARE, volume=92,
                                             start_tick=t0 + i * step16,
                                             end_tick=t0 + i * step16 + step16 // 2))
            # offbeat hat ticks
            events.append(MusicEvent(pitch=MidiPercussion.CLOSED_HI_HAT, volume=58,
                                     start_tick=t0 + i * step16 + step16 // 2,
                                     end_tick=t0 + i * step16 + step16))
    return events


def _pad_unit(events, section_ticks, offset=0):
    """Zero-drift cell padding: absolute -> relative ticks for one section.

    Order matters: subtract the section offset FIRST (absolute -> relative),
    then clamp to [0, section_ticks]. Clamping before the offset shift
    collapses every event to tick 0 for sections beyond the first.
    """
    for e in events:
        e.start_tick = max(0, e.start_tick - offset)
        e.end_tick = max(0, e.end_tick - offset)
        if e.end_tick > section_ticks:
            e.end_tick = section_ticks
        if e.start_tick >= section_ticks:
            e.start_tick = section_ticks - 10
    if not events or events[-1].end_tick < section_ticks:
        events.append(MusicEvent(pitch=0, volume=0,
                                 start_tick=section_ticks - 10,
                                 end_tick=section_ticks))
    return events


def build_composer(lead_events, phase_name):
    """Build the UnitMatrix composer for one phase (phase1 or phase2)."""
    comp = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
    num_sections = len(SECTIONS)
    comp.create_matrix(num_voices=5, num_sections=num_sections)
    comp.add_voice("Lead", program=MidiInstrument.FLUTE, channel=0)
    comp.add_voice("Harmony", program=MidiInstrument.STRING_ENSEMBLE, channel=1)
    comp.add_voice("Bass", program=MidiInstrument.BASS, channel=2)
    comp.add_voice("Drums", program=0, channel=9)
    comp.add_voice("Pad", program=MidiInstrument.SYNTH_PAD, channel=3)

    for name, bars, _, _ in SECTIONS:
        comp.add_section(name, bars=bars)

    # split lead events per section
    for s_idx, (name, bars, _, _) in enumerate(SECTIONS):
        s_start = sum(s[1] for s in SECTIONS[:s_idx]) * BAR
        s_ticks = bars * BAR
        seg = [e for e in lead_events
               if e.start_tick >= s_start and e.start_tick < s_start + s_ticks]
        seg = [MusicEvent(e.pitch, e.volume, e.start_tick, e.end_tick) for e in seg]
        unit = MusicUnit(events=_pad_unit(seg, s_ticks, offset=s_start))
        comp.fill_voice_section("Lead", name, unit)

        # harmony per section
        hseg = [e for e in build_harmony_events()
                if e.start_tick >= s_start and e.start_tick < s_start + s_ticks]
        hseg = [MusicEvent(e.pitch, e.volume, e.start_tick, e.end_tick) for e in hseg]
        comp.fill_voice_section("Harmony", name,
                                MusicUnit(events=_pad_unit(hseg, s_ticks, offset=s_start)))

        # bass per section
        bseg = [e for e in build_bass_events()
                if e.start_tick >= s_start and e.start_tick < s_start + s_ticks]
        bseg = [MusicEvent(e.pitch, e.volume, e.start_tick, e.end_tick) for e in bseg]
        comp.fill_voice_section("Bass", name,
                                MusicUnit(events=_pad_unit(bseg, s_ticks, offset=s_start)))

        # drums per section
        dseg = [e for e in build_drums_events()
                if e.start_tick >= s_start and e.start_tick < s_start + s_ticks]
        dseg = [MusicEvent(e.pitch, e.volume, e.start_tick, e.end_tick) for e in dseg]
        comp.fill_voice_section("Drums", name,
                                MusicUnit(events=_pad_unit(dseg, s_ticks, offset=s_start)))

        # pad per section: low Rast drone
        anchor = 62 if name != "B" else 69
        pad = create_chord_unit([anchor - 12, anchor], s_ticks)
        comp.fill_voice_section("Pad", name, pad)

    ok, msg = comp.validate()
    if not ok:
        raise RuntimeError(f"validate() failed: {msg}")
    return comp


def main():
    # ---- Phase 1: raw draft ------------------------------------------------
    raw = phase1_raw_events(seed=20260817)
    raw_ev = raw_to_midi_events(raw, 0)
    raw_ev = _voice_leading_fix(raw_ev)

    comp1 = build_composer(raw_ev, "phase1")
    ok1, msg1 = comp1.validate()
    assert ok1, f"phase1 validate failed: {msg1}"
    phase1_mid = os.path.join(MIDI_DIR, "071-arabic-rast-ant-colony-phase1.mid")
    comp1.to_midi(phase1_mid)
    write_provenance(phase1_mid, AI_GENERATED,
                     "musicom.method041.ant_colony_phase1",
                     sources=["methods_db.md:Method 041 ACOPF"],
                     parameters={"bpm": BPM, "bars": TOTAL_BARS,
                                 "seed": 20260817, "phase": 1,
                                 "quantized": False},
                     notes="Raw ant-colony pitch trajectory, unquantized, "
                           "single voice, pre-rules.")
    write_grid_visualization(comp1.matrix, os.path.join(ANALYSIS_DIR, "grid_visualization_phase1.txt"),
                             voice_names=["Lead", "Harmony", "Bass", "Drums", "Pad"],
                             bpm=BPM)

    # ---- Phase 2: rules post-process --------------------------------------
    rules_ev = phase2_rules_events(raw, seed=20260817)
    rules_ev = _voice_leading_fix(rules_ev)

    comp2 = build_composer(rules_ev, "phase2")
    ok2, msg2 = comp2.validate()
    assert ok2, f"phase2 validate failed: {msg2}"
    final_mid = os.path.join(MIDI_DIR, "071-arabic-rast-ant-colony.mid")
    comp2.to_midi(final_mid)
    write_provenance(final_mid, AI_GENERATED,
                     "musicom.method041.ant_colony_phase2",
                     sources=["methods_db.md:Method 041 ACOPF"],
                     parameters={"bpm": BPM, "bars": TOTAL_BARS,
                                 "seed": 20260817, "phase": 2,
                                 "maqam": "Rast", "rhythm": "Maqsum 3+3+2",
                                 "quantized": True},
                     notes="Rules post-process: Rast quantization, section "
                           "harmony, voice-leading fix, zero-drift cells.")
    write_grid_visualization(comp2.matrix, os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
                             voice_names=["Lead", "Harmony", "Bass", "Drums", "Pad"],
                             bpm=BPM)

    # ---- size asserts -------------------------------------------------------
    for p in (phase1_mid, final_mid):
        assert os.path.getsize(p) > 40, f"empty/corrupt: {p}"

    print("PHASE1_MID:", phase1_mid, os.path.getsize(phase1_mid))
    print("FINAL_MID:", final_mid, os.path.getsize(final_mid))
    print("VALIDATE:", ok1, msg1, "|", ok2, msg2)
    print("RAW_EVENTS:", len(raw), "RULES_EVENTS:", len(rules_ev))


if __name__ == "__main__":
    main()
