# -*- coding: utf-8 -*-
"""238 — Neo-Riemannian Afro Drop (Method 011: Voice-Leading Graph Search).

Nightly composition job (2026-10-12). Style = African, form =
intro-break-drop-outro (24 bars), key = G major.

Method 011 (concrete, Rules-Based): Neo-Riemannian graph traversal to find
the SHORTEST voice-leading paths between chord cells. Implementation:

  * Build a graph over the 6 diatonic major/minor triads of G major, with
    edges = the neo-Riemannian transformations P/R/L (only R and L stay
    diatonic). Edge weight = semitone distance travelled by the single
    moving voice.
  * A tonal plan of target chords (24 bars) is walked using BFS shortest
    voice-leading paths from each chord to the next. Every consecutive
    target is a single R or L step, so each bar is one minimal-voice-leading
    transformation: two common tones held, one voice moves by a step.

Two-phase architecture:
  Phase 1 (raw): single-voice random-walk draft — unquantized rhythm,
    raw octave-jittered chord tones, off-grid by design, NO harmony.
  Phase 2 (rules): grid-snap (120 ticks), per-bar chord-tone quantization,
    register enforcement, voice-led block harmony (String Ensemble),
    marimba lead, kalimba mbira ostinato, double-bass roots, ch9 African
    polyrhythm (bell timeline + shaker + kick/snare/toms).

Engines: structures.*, workflows.unitmatrix_composer, visualization.grid,
workflows.provenance, rules.voice_leading (validation), instrument registry.
"""
import collections
import itertools
import json
import math
import os
import sys

from structures import MusicUnit, MusicEvent, MidiInstrument, MidiPercussion
from workflows.unitmatrix_composer import UnitMatrixComposer
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance
from rules.voice_leading import VoiceLeadingRules

# Instrument registry is NOT pip-installed (lives in projects/Instruments) —
# canonical sys.path pattern used by every project composer (see skill).
_INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if _INSTR_DIR not in sys.path:
    sys.path.insert(0, _INSTR_DIR)
from instrument_registry import MARIMBA, STRING_ENSEMBLE, KALIMBA, DOUBLE_BASS  # noqa: E402

# ---- Concept ----------------------------------------------------------------
SEED = 238
KEY_NAME = "G major"
KEY_ROOT_PC = 7            # G
KEY_ROOT_MIDI = 55         # G3
SCALE_INTERVALS = [0, 2, 4, 5, 7, 9, 11]     # ionian from G
KEY_PCS = set((KEY_ROOT_PC + iv) % 12 for iv in SCALE_INTERVALS)
BPM = 124
TPB = 480
BPB = 4
BAR = TPB * BPB            # 1920
GRID = 120                 # 16th-note snap grid

# ---- Form: intro-break-drop-outro ------------------------------------------
SECTIONS = [("Intro", 4), ("Break", 8), ("Drop", 8), ("Outro", 4)]
TOTAL_BARS = sum(b for _, b in SECTIONS)
TOTAL_TICKS = TOTAL_BARS * BAR

# ---- Neo-Riemannian graph over G-major diatonic triads ---------------------
# node = (mode, root_pc) where mode in {'maj','min'}
# (mode, root_pc) -> roman numeral in G major
NODE_DEGREE = {
    ("maj", 7):  "I",
    ("min", 9):  "ii",
    ("min", 11): "iii",
    ("maj", 0):  "IV",
    ("maj", 2):  "V",
    ("min", 4):  "vi",
}
TRIADS = set(NODE_DEGREE.keys())


def chord_tone_pcs(mode, root):
    third = 4 if mode == "maj" else 3
    return [root % 12, (root + third) % 12, (root + 7) % 12]


def semitone_dist(a, b):
    d = abs(a - b) % 12
    return min(d, 12 - d)


def nr_neighbors(mode, root):
    """Return [(n_mode, n_root, label, move_semitones)] for diatonic R/L steps."""
    if mode == "maj":
        cands = [("min", (root + 9) % 12, "R"), ("min", (root + 4) % 12, "L")]
    else:
        cands = [("maj", (root + 3) % 12, "R"), ("maj", (root + 8) % 12, "L")]
    out = []
    for m, r, lab in cands:
        if (m, r) in TRIADS:
            a = set(chord_tone_pcs(mode, root))
            b = set(chord_tone_pcs(m, r))
            common = a & b
            move_a = list(a - common)
            move_b = list(b - common)
            dist = semitone_dist(move_a[0], move_b[0])
            out.append((m, r, lab, dist))
    return out


def bfs_shortest(start, target):
    """BFS shortest voice-leading path from start to target (nodes inclusive)."""
    if start == target:
        return [start]
    parent = {start: None}
    edge_meta = {}
    q = collections.deque([start])
    while q:
        cur = q.popleft()
        if cur == target:
            break
        for nm, nr, lab, dist in nr_neighbors(*cur):
            nxt = (nm, nr)
            if nxt not in parent:
                parent[nxt] = cur
                edge_meta[nxt] = (lab, dist)
                q.append(nxt)
    if target not in parent:
        raise RuntimeError(f"no path {start} -> {target}")
    path = [target]
    while parent[path[-1]] is not None:
        path.append(parent[path[-1]])
    path.reverse()
    return path


# Tonal plan: target chords per bar (24 bars), sectioned.
PLAN = [
    ("maj", 7), ("min", 4), ("maj", 0), ("min", 9),           # Intro I vi IV ii
    ("maj", 0), ("min", 4), ("maj", 7), ("min", 11),          # Break IV vi I iii
    ("maj", 2), ("min", 11), ("maj", 7), ("min", 4),          #        V iii I vi
    ("maj", 7), ("min", 11), ("maj", 2), ("min", 11),         # Drop  I iii V iii
    ("maj", 7), ("min", 4), ("maj", 0), ("min", 9),           #       I vi IV ii
    ("maj", 0), ("min", 4), ("maj", 7), ("maj", 7),           # Outro IV vi I I
]
assert len(PLAN) == TOTAL_BARS


def generate_chord_path():
    """Walk the tonal plan via BFS shortest voice-leading paths."""
    path = [PLAN[0]]
    steps = []  # per step: (label, move_semitones)
    for t in PLAN[1:]:
        if t == path[-1]:
            # hold the chord (fermata-like), zero voice movement
            steps.append(("hold", 0))
            path.append(t)
            continue
        route = bfs_shortest(path[-1], t)
        for node in route[1:]:
            meta = None
            for nm, nr, lab, dist in nr_neighbors(*path[-1]):
                if (nm, nr) == node:
                    meta = (lab, dist)
                    break
            steps.append(meta)
            path.append(node)
    return path, steps


# ---- Pitch helpers ----------------------------------------------------------
def pitch_in(pc, lo, hi, center=None):
    """Return a MIDI pitch with pitch-class pc inside [lo,hi], nearest center."""
    center = center if center is not None else (lo + hi) // 2
    best, bestd = None, None
    for k in itertools.count(0):
        n = pc + 12 * k
        if n > hi:
            break
        if lo <= n <= hi:
            d = abs(n - center)
            if bestd is None or d < bestd:
                bestd, best = d, n
    for k in itertools.count(-1, -1):
        n = pc + 12 * k
        if n < lo:
            break
        if lo <= n <= hi:
            d = abs(n - center)
            if bestd is None or d < bestd:
                bestd, best = d, n
    return best


def arpeggio_pcs(mode, root):
    third = 4 if mode == "maj" else 3
    return [root, root + third, root + 7, root + 12, root + 7, root + third]


def dedup(events):
    d, order = {}, []
    for e in events:
        key = (e.start_tick, e.pitch)
        if key not in d:
            d[key] = e
            order.append(key)
        elif (e.end_tick - e.start_tick) > (d[key].end_tick - d[key].start_tick):
            d[key] = e
    return [d[k] for k in order]


def snap(t):
    return int(round(t / GRID) * GRID)


# ---- Section bookkeeping ----------------------------------------------------
SECTION_START_BARS = []
_acc = 0
for _name, _b in SECTIONS:
    SECTION_START_BARS.append(_acc)
    _acc += _b


def bar_of(tick):
    return tick // BAR


def section_start_abs(s):
    return SECTION_START_BARS[s] * BAR


def section_ticks(s):
    return SECTIONS[s][1] * BAR


def split_abs_to_section(abs_events, s):
    start = section_start_abs(s)
    length = section_ticks(s)
    end = start + length
    cell = []
    for e in abs_events:
        if e.end_tick <= start or e.start_tick >= end:
            continue
        st = max(0, e.start_tick - start)
        et = min(length, e.end_tick - start)
        if et <= st:
            continue
        cell.append(MusicEvent(pitch=e.pitch, volume=e.volume,
                               start_tick=st, end_tick=et))
    if not cell or cell[-1].end_tick < length:
        last = cell[-1].end_tick if cell else 0
        cell.append(MusicEvent(pitch=0, volume=0, start_tick=last, end_tick=length))
    return MusicUnit(events=cell)


# ---- Voicing (harmony pad) --------------------------------------------------
def voice_progression(chord_path, lo=55, hi=79):
    """Voice the 24 triads with greedy min-motion (neo-Riemannian smooth)."""
    vl = VoiceLeadingRules(style="classical")
    voicings = []
    prev = None
    for (mode, root) in chord_path:
        pcs = chord_tone_pcs(mode, root)
        if prev is None:
            # canonical root-position-ish voicing, sorted
            cand = sorted(pitch_in(p, lo, hi) for p in pcs)
            # enforce distinct ascending by octave fallback
            if len(set(cand)) < 3:
                cand = sorted([pitch_in(pcs[0], lo, hi),
                               pitch_in(pcs[1], lo, hi),
                               pitch_in(pcs[2], lo, hi)])
                if len(set(cand)) < 3:
                    cand = sorted(set(cand + [c + 12 for c in cand]))
            cand = sorted(set(cand))[:3]
            while len(cand) < 3:
                cand.append(cand[-1] + 12)
            voicings.append(sorted(cand))
        else:
            best, bestd = None, None
            for perm in itertools.permutations(pcs):
                cand = []
                ok = True
                for j, pc in enumerate(perm):
                    n = pitch_in(pc, lo, hi, center=prev[j])
                    if n is None:
                        ok = False
                        break
                    cand.append(n)
                if not ok:
                    continue
                dist = sum(abs(prev[j] - cand[j]) for j in range(3))
                if bestd is None or dist < bestd:
                    bestd, best = dist, sorted(cand)
            if best is None:
                best = sorted(pitch_in(p, lo, hi) for p in pcs)
            voicings.append(best)
        prev = voicings[-1]
    # voice-leading validation
    violations = []
    for i in range(1, len(voicings)):
        violations += vl.check_parallel_motion(voicings[i - 1], voicings[i])
        violations += vl.check_hidden_fifths(voicings[i - 1], voicings[i])
    return voicings, violations


# ---- Phase-1 raw draft (single voice, unquantized, no harmony) -------------
def build_raw_events(chord_path):
    import random
    rng = random.Random(SEED)
    out = []
    for bar, (mode, root) in enumerate(chord_path):
        base = bar * BAR
        n = rng.randint(2, 4)
        tones = chord_tone_pcs(mode, root)
        for _ in range(n):
            st = base + rng.randint(0, BAR - 200)          # unquantized
            pc = rng.choice(tones)
            pitch = pitch_in(pc, 48, 84, center=rng.randint(48, 84))
            dur = rng.randint(120, 720)
            vel = rng.randint(70, 100)
            out.append(MusicEvent(pitch=pitch, volume=vel,
                                  start_tick=st,
                                  end_tick=min(base + BAR, st + dur)))
    return out


# ---- Phase-2 voices ---------------------------------------------------------
def build_lead(chord_path):
    """Marimba lead — chord-tone contours on section rhythm templates."""
    out = []
    for bar, (mode, root) in enumerate(chord_path):
        sec = 0
        for s, (_n, _b) in enumerate(SECTIONS):
            if bar >= SECTION_START_BARS[s]:
                sec = s
        sec_name = SECTIONS[sec][0]
        base = bar * BAR
        if sec_name == "Intro":
            slots = [0, 8]                      # half notes
        elif sec_name == "Break":
            slots = [0, 4, 6, 10] if bar % 2 == 0 else [8, 10, 12, 14]
        elif sec_name == "Drop":
            slots = list(range(0, 16, 2))       # 8th notes
        else:  # Outro
            slots = [0, 6, 12]
        arp = arpeggio_pcs(mode, root)
        for i, slot in enumerate(slots):
            st = base + slot * GRID
            pc = arp[i % len(arp)]
            pitch = pitch_in(pc, 60, 84)
            if sec_name == "Intro" or sec_name == "Outro":
                dur = GRID * 8 if slot in (0, 8) else GRID * 4
            elif sec_name == "Break":
                dur = GRID * 3
            else:
                dur = GRID * 2
            vel = 96 if sec_name == "Drop" else 88
            out.append(MusicEvent(pitch=pitch, volume=vel,
                                  start_tick=snap(st),
                                  end_tick=min(base + BAR, snap(st) + dur)))
    return dedup(out)


def build_harmony(chord_path, voicings):
    """String Ensemble block chords, one per bar, voice-led."""
    out = []
    for bar, (_mode, _root) in enumerate(chord_path):
        base = bar * BAR
        for p in voicings[bar]:
            out.append(MusicEvent(pitch=p, volume=72,
                                  start_tick=base, end_tick=base + BAR))
    return out


def build_kalimba(chord_path):
    """Kalimba mbira ostinato — 16th-note arpeggio of chord tones."""
    out = []
    for bar, (mode, root) in enumerate(chord_path):
        sec = 0
        for s, (_n, _b) in enumerate(SECTIONS):
            if bar >= SECTION_START_BARS[s]:
                sec = s
        sec_name = SECTIONS[sec][0]
        base = bar * BAR
        arp = arpeggio_pcs(mode, root)
        if sec_name in ("Intro", "Outro"):
            slots = list(range(0, 16, 4))       # quarter-note plucks
        else:
            slots = list(range(0, 16, 2))       # 8th-note pattern
        for i, slot in enumerate(slots):
            st = base + slot * GRID
            pc = arp[(i * 2) % len(arp)]
            pitch = pitch_in(pc, 62, 81)
            out.append(MusicEvent(pitch=pitch, volume=76,
                                  start_tick=snap(st), end_tick=snap(st) + GRID))
    return dedup(out)


def build_bass(chord_path):
    """Double bass — chord roots with an African ostinato rhythm."""
    out = []
    for bar, (mode, root) in enumerate(chord_path):
        sec = 0
        for s, (_n, _b) in enumerate(SECTIONS):
            if bar >= SECTION_START_BARS[s]:
                sec = s
        sec_name = SECTIONS[sec][0]
        base = bar * BAR
        rp = pitch_in(root, 40, 55)
        if sec_name in ("Intro", "Outro"):
            slots = [0, 8]
        elif sec_name == "Break":
            slots = [0, 6] if bar % 2 == 0 else [8, 10]
        else:  # Drop
            slots = [0, 4, 8, 12]               # four-on-floor roots
        for slot in slots:
            st = base + slot * GRID
            out.append(MusicEvent(pitch=rp, volume=94,
                                  start_tick=snap(st), end_tick=snap(st) + GRID * 2))
    return dedup(out)


def build_drums():
    """ch9 African polyrhythm: bell timeline + shaker + kick/snare/toms."""
    out = []
    BELL = [0, 3, 6, 10, 12]                    # 5-stroke cowbell timeline
    for s, (name, bars) in enumerate(SECTIONS):
        sec_start = section_start_abs(s)
        if name == "Drop" and s > 0:
            out.append(MusicEvent(pitch=MidiPercussion.CRASH_CYMBAL, volume=88,
                                  start_tick=sec_start, end_tick=sec_start + GRID))
        for b in range(bars):
            base = sec_start + b * BAR
            # shaker (maracas) 16ths — constant timeline
            for slot in range(16):
                st = base + slot * GRID
                vel = 60 if name in ("Intro", "Outro") else 66
                if name == "Intro" and slot % 4 != 0:
                    continue
                if name == "Outro" and slot % 8 != 0:
                    continue
                out.append(MusicEvent(pitch=MidiPercussion.MARACAS, volume=vel,
                                      start_tick=st, end_tick=st + GRID))
            # cowbell timeline
            for slot in BELL:
                if name in ("Intro", "Outro") and slot not in (0, 12):
                    continue
                out.append(MusicEvent(pitch=MidiPercussion.COWBELL, volume=72,
                                      start_tick=base + slot * GRID,
                                      end_tick=base + slot * GRID + GRID))
            # kick
            if name == "Drop":
                for slot in (0, 4, 8, 12):
                    out.append(MusicEvent(pitch=MidiPercussion.BASS_DRUM, volume=100,
                                          start_tick=base + slot * GRID,
                                          end_tick=base + slot * GRID + GRID))
            elif name == "Break":
                if b % 2 == 0:
                    out.append(MusicEvent(pitch=MidiPercussion.BASS_DRUM, volume=92,
                                          start_tick=base, end_tick=base + GRID))
            # snare backbeat (Drop)
            if name == "Drop":
                for slot in (4, 12):
                    out.append(MusicEvent(pitch=MidiPercussion.ACOUSTIC_SNARE, volume=90,
                                          start_tick=base + slot * GRID,
                                          end_tick=base + slot * GRID + GRID))
            # tom "response" fills (Break)
            if name == "Break" and b % 2 == 1:
                for slot, tom in ((10, MidiPercussion.LOW_TOM),
                                  (12, MidiPercussion.MID_TOM),
                                  (14, MidiPercussion.HIGH_TOM)):
                    out.append(MusicEvent(pitch=tom, volume=80,
                                          start_tick=base + slot * GRID,
                                          end_tick=base + slot * GRID + GRID))
    return dedup(out)


# ---- Compose ----------------------------------------------------------------
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
MIDI_DIR = os.path.join(PROJECT_DIR, "MIDI")
ANALYSIS_DIR = os.path.join(PROJECT_DIR, "Analysis")
AUDIO_DIR = os.path.join(PROJECT_DIR, "Audio")
for d in (MIDI_DIR, ANALYSIS_DIR, AUDIO_DIR):
    os.makedirs(d, exist_ok=True)

BASE = "238-neoriemannian-afro-drop"
MIDI_PATH = os.path.join(MIDI_DIR, BASE + ".mid")
PHASE1_PATH = os.path.join(MIDI_DIR, BASE + "-phase1.mid")

VOICES = ["Lead", "Harmony", "Kalimba", "Bass", "Drums"]
VOICE_PROGRAMS = [MARIMBA.midi_program, STRING_ENSEMBLE.midi_program,
                  KALIMBA.midi_program, DOUBLE_BASS.midi_program, 0]
VOICE_CHANNELS = [0, 1, 2, 3, 9]


def compose():
    chord_path, steps = generate_chord_path()
    assert len(chord_path) == TOTAL_BARS, \
        f"chord path length {len(chord_path)} != {TOTAL_BARS} bars"
    voicings, vl_violations = voice_progression(chord_path)

    # ---- Phase 1: raw single-voice draft -----------------------------------
    raw = build_raw_events(chord_path)
    p1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    p1.create_matrix(num_voices=1, num_sections=len(SECTIONS))
    p1.add_voice("RawDraft", program=MARIMBA.midi_program, channel=0)
    for name, bars in SECTIONS:
        p1.add_section(name, bars=bars)
    for s, (name, _bars) in enumerate(SECTIONS):
        p1.fill_voice_section("RawDraft", name, split_abs_to_section(raw, s))
    ok1, msg1 = p1.validate()
    if not ok1:
        raise RuntimeError(f"Phase 1 zero-drift FAILED: {msg1}")
    p1.to_midi(PHASE1_PATH)

    # ---- Phase 2: rules post-process ----------------------------------------
    lead = build_lead(chord_path)
    harm = build_harmony(chord_path, voicings)
    kal = build_kalimba(chord_path)
    bass = build_bass(chord_path)
    drums = build_drums()

    voice_events = {"Lead": lead, "Harmony": harm, "Kalimba": kal,
                    "Bass": bass, "Drums": drums}

    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    composer.create_matrix(num_voices=len(VOICES), num_sections=len(SECTIONS))
    for name, prog, ch in zip(VOICES, VOICE_PROGRAMS, VOICE_CHANNELS):
        composer.add_voice(name, program=prog, channel=ch)
    for name, bars in SECTIONS:
        composer.add_section(name, bars=bars)
    for s, (name, _bars) in enumerate(SECTIONS):
        for vname in VOICES:
            composer.fill_voice_section(vname, name,
                                        split_abs_to_section(voice_events[vname], s))

    ok2, msg2 = composer.validate()
    if not ok2:
        raise RuntimeError(f"Phase 2 zero-drift FAILED: {msg2}")
    composer.to_midi(MIDI_PATH)

    grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
    write_grid_visualization(composer.matrix, grid_path, ticks_per_character=120,
                             voice_names=VOICES, bpm=BPM, mode="Major (G)")

    # save chord path + step metadata for the audit + report
    summary = {
        "key": KEY_NAME, "root_pc": KEY_ROOT_PC, "scale_intervals": SCALE_INTERVALS,
        "bpm": BPM, "ticks_per_beat": TPB, "beats_per_bar": BPB, "bar_ticks": BAR,
        "grid": GRID, "form": "intro-break-drop-outro",
        "sections": [{"name": n, "bars": b} for n, b in SECTIONS],
        "total_bars": TOTAL_BARS, "total_ticks": TOTAL_TICKS,
        "voices": [{"name": n, "program": p, "channel": c}
                   for n, p, c in zip(VOICES, VOICE_PROGRAMS, VOICE_CHANNELS)],
        "chord_path": [
            {"bar": i, "mode": m, "root_pc": r, "degree": NODE_DEGREE[(m, r)],
             "chord_tone_pcs": chord_tone_pcs(m, r)}
            for i, (m, r) in enumerate(chord_path)],
        "voice_leading_steps": [
            {"from_bar": i, "to_bar": i + 1, "label": st[0],
             "move_semitones": st[1]}
            for i, st in enumerate(steps)],
        "vl_violations": vl_violations,
    }
    with open(os.path.join(ANALYSIS_DIR, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    return composer, ok1, chord_path, steps, voicings, vl_violations, len(raw)


if __name__ == "__main__":
    composer, ok1, chord_path, steps, voicings, vl_violations, n_raw = compose()

    size2 = os.path.getsize(MIDI_PATH)
    size1 = os.path.getsize(PHASE1_PATH)
    assert size2 > 40, f"Phase 2 MIDI too small ({size2})"
    assert size1 > 40, f"Phase 1 MIDI too small ({size1})"

    print(f"[OK] Phase 1 MIDI: {PHASE1_PATH} ({size1} bytes)")
    print(f"[OK] Phase 2 MIDI: {MIDI_PATH} ({size2} bytes)")
    print(f"[OK] Phase 1 zero-drift: {ok1}")
    print(f"[OK] Phase 2 zero-drift: True")
    print(f"[OK] Bars: {TOTAL_BARS}, sections: {len(SECTIONS)}")
    print(f"[OK] Raw draft events: {n_raw}")
    print(f"[OK] Voice-leading violations (classical): {len(vl_violations)}")
    print(f"[OK] Chord path (degree per bar):")
    degs = [NODE_DEGREE[(m, r)] for m, r in chord_path]
    print("     " + " ".join(f"{d:>3}" for d in degs[:12]))
    print("     " + " ".join(f"{d:>3}" for d in degs[12:]))

    write_provenance(
        PHASE1_PATH,
        classification="ai-generated",
        generator="Method 011 Voice-Leading Graph Search (Neo-Riemannian) - PRE-RULES raw draft",
        sources=["Research/CompositionMethods/methods_db.md:Method 011",
                 "workflows/unitmatrix_composer.py"],
        parameters={"method": 11, "phase": 1, "key": KEY_NAME, "bpm": BPM,
                    "sections": len(SECTIONS), "total_bars": TOTAL_BARS,
                    "seed": SEED, "style": "African", "form": "intro-break-drop-outro"},
        notes="Phase 1: single-voice random-walk draft over the neo-Riemannian "
              "graph, unquantized rhythm, raw octave-jittered chord tones, "
              "off-grid by design, no harmony.",
    )
    write_provenance(
        MIDI_PATH,
        classification="ai-generated",
        generator="Method 011 Voice-Leading Graph Search (Neo-Riemannian) + musicom rules",
        sources=["Research/CompositionMethods/methods_db.md:Method 011",
                 "rules/voice_leading.py", "workflows/unitmatrix_composer.py",
                 "projects/Instruments/instrument_registry.py"],
        parameters={"method": 11, "phase": 2, "key": KEY_NAME, "bpm": BPM,
                    "sections": len(SECTIONS), "total_bars": TOTAL_BARS,
                    "seed": SEED, "style": "African", "form": "intro-break-drop-outro",
                    "voices": VOICES},
        notes="Phase 2: BFS shortest voice-leading path (2 common tones held, 1 "
              "voice moves by step), grid-snap 120 ticks, per-bar chord-tone "
              "quantization, voice-led string pad, marimba lead, kalimba mbira "
              "ostinato, double-bass roots, ch9 African polyrhythm.",
    )
    print("[OK] Provenance sidecars written (phase 1 + phase 2).")
