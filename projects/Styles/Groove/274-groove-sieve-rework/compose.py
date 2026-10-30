# -*- coding: utf-8 -*-
"""274-groove-sieve-rework — rework of 080-groove-sieve (Groove / Method 025
Xenakis Sieve Theory).

Two-phase architecture, rebuilt from scratch through the canonical
UnitMatrixComposer (redesign required: source lacked index.html dashboard).

Identity preserved (from source):
  genre Groove, key G natural minor, 110 BPM 4/4 (bar 1920, 8th 240, 16th 120),
  Method 025 Xenakis Sieve (sieve C = A mod 8 {0,2,5} INTERSECT B mod 7 {0,1,4},
  period lcm(8,7)=56, offsets [0,8,18,21,29,32,42,50,53]),
  5 core voices (Lead soprano sax 65, Horns brass 61, Rhodes EP 4, Bass EB 33,
  Drums ch9) + a new Counter (strings 48) only in chorus sections.

New form (LONGER + more varied): 32 bars / 8 sections (source was 24 bars /
6 sections). Per-section harmonic regions + per-section variation technique.

Variation techniques (5 distinct):
  1. Transposition / register shift  -> VerseB +12, Chorus2 +12
  2. Inversion                       -> Bridge (sieve offsets negated)
  3. Retrograde                      -> VerseC (sieve offset sequence reversed)
  4. Augmentation                    -> Outro (onset step doubled, sparse)
  5. Density rise + counterline      -> Chorus/Chorus2 (denser raw + Counter voice)
"""
import os
import json
import hashlib

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer, create_empty_unit
from workflows.humanize import export_dual
from workflows.provenance import write_provenance, AI_ASSISTED
from visualization.grid import write_grid_visualization
from rules.progression import Scale7ChordDegree

# ------------------------------------------------------------------ paths
PROJ = "/opt/data/projects/Styles/Groove/274-groove-sieve-rework"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

PID = "274"
NAME = "groove-sieve-rework"
BASE = f"{PID}-{NAME}"
STYLE = "groove"
GENRE = "Groove"

# ------------------------------------------------------------------ identity
BPM = 110
TPB = 480
BEATS = 4
BAR = TPB * BEATS                 # 1920
SIXTEENTH = 120
EIGHTH = 240

KEY_NAME = "G natural minor"
KEY_ROOT_PC = 7                   # G
KEY_PCS = {7, 9, 10, 0, 2, 3, 5}  # G A Bb C D Eb F
SCALE_INTERVALS = [0, 2, 3, 5, 7, 8, 10]   # G aeolian semitone offsets

# degree symbol -> scale-degree index + triad quality intervals (G natural minor)
DEGREE_STEP = {'i': 0, 'ii': 1, 'III': 2, 'iv': 3, 'v': 4, 'VI': 5, 'VII': 6}
QUALITY = {'i': (0, 3, 7), 'ii': (0, 3, 6), 'III': (0, 4, 7), 'iv': (0, 3, 7),
           'v': (0, 3, 7), 'VI': (0, 4, 7), 'VII': (0, 4, 7)}

# ------------------------------------------------------------------ form
# (name, bars, progression [degree symbols], lead technique, raw density,
#  raw center0, step multiplier)
SECTIONS = [
    ("Intro",     4, ['i', 'VII', 'i', 'VII'], 'rise',   26, 67, 1.0),
    ("VerseA",    4, ['i', 'III', 'iv', 'v'], 'rise',   34, 69, 1.0),
    ("VerseB",    4, ['i', 'iv', 'v', 'VI'],  'rise',   34, 81, 1.0),  # +12
    ("Chorus",    4, ['III', 'VII', 'i', 'iv'], 'rise', 40, 71, 1.0),
    ("Bridge",    4, ['VI', 'III', 'VII', 'v'], 'invert', 34, 69, 1.0),
    ("VerseC",    4, ['i', 'III', 'iv', 'v'], 'retro',  34, 69, 1.0),
    ("Chorus2",   4, ['III', 'VII', 'i', 'iv'], 'rise', 40, 83, 1.0),  # +12
    ("Outro",     4, ['i', 'VI', 'VII', 'i'],  'rise',   20, 67, 2.0),  # augment
]
TOTAL_BARS = sum(s[1] for s in SECTIONS)          # 32
TOTAL_TICKS = TOTAL_BARS * BAR
SECTION_START = {}
_acc = 0
for name, bars, prog, tech, dens, center, smult in SECTIONS:
    SECTION_START[name] = _acc
    _acc += bars
assert _acc == TOTAL_BARS

BAR_DEGREE = []                                   # global bar -> degree symbol
for name, bars, prog, tech, dens, center, smult in SECTIONS:
    BAR_DEGREE.extend(prog)
assert len(BAR_DEGREE) == TOTAL_BARS

SEED = 20260828
hz_seed = int(hashlib.md5(BASE.encode()).hexdigest()[:8], 16) % 100000


def diatonic_note(degree_index, base=55):
    """Canonical diatonic note (no %7 wrapper) — G3 = 55 anchor."""
    return Scale7ChordDegree.get_diatonic_note(base, SCALE_INTERVALS, degree_index)


def chord_pcs(deg):
    root = (KEY_ROOT_PC + SCALE_INTERVALS[DEGREE_STEP[deg]]) % 12
    return {(root + q) % 12 for q in QUALITY[deg]}


def nearest_in_pcs(pitch, pcs, lo=0, hi=127):
    """Nearest note within [lo, hi] whose pitch-class is in pcs. Range-restricted
    so the result never needs a post-clamp (a post-clamp would change the
    pitch-class, silently breaking chord/scale compliance)."""
    best = None
    for n in range(max(lo, pitch - 12), min(hi, pitch + 12) + 1):
        if n % 12 in pcs:
            if best is None or abs(n - pitch) < abs(best - pitch):
                best = n
    return best


def nearest_scale(pitch, lo=0, hi=127):
    return nearest_in_pcs(pitch, KEY_PCS, lo, hi)


def nearest_chord(pitch, deg, lo=0, hi=127):
    return nearest_in_pcs(pitch, chord_pcs(deg), lo, hi)


def chord_voicing(deg, base):
    """[root, 3rd, 5th, octave] absolute notes rooted at base register."""
    d = DEGREE_STEP[deg]
    return [diatonic_note(d, base), diatonic_note(d + 2, base),
            diatonic_note(d + 4, base), diatonic_note(d + 7, base)]


# ------------------------------------------------------------------ sieve
SIEVE_A_MOD, SIEVE_A_RES = 8, (0, 2, 5)
SIEVE_B_MOD, SIEVE_B_RES = 7, (0, 1, 4)


def sieve_offsets(lo=0, hi=56):
    return [n for n in range(lo, hi)
            if (n % SIEVE_A_MOD) in SIEVE_A_RES and (n % SIEVE_B_MOD) in SIEVE_B_RES]


SIEVE_OFFSETS = sieve_offsets(0, 56)   # [0,8,18,21,29,32,42,50,53]


# ------------------------------------------------------------------ phase 1
def raw_events_for(tech, n_events, dur_ticks, center0, smult, seed):
    """Raw sieve walk (single voice): unquantized rhythm, raw chromatic wander."""
    r = np.random.default_rng(seed)
    if tech == 'invert':
        offs = [-o for o in SIEVE_OFFSETS]
    elif tech == 'retro':
        offs = list(reversed(SIEVE_OFFSETS))
    else:
        offs = list(SIEVE_OFFSETS)
    events = []
    tick = 0
    center = float(center0)
    step = dur_ticks / max(1, n_events) * smult
    i = 0
    while tick < dur_ticks - 120:
        p = center + offs[i % len(offs)] + r.normal(0.0, 1.1)
        p = int(round(max(48, min(96, p))))
        dur = int(step * (0.8 + 0.4 * r.random()))
        dur = max(120, min(dur, dur_ticks - tick))
        vel = int(np.clip(60 + 26 * abs(np.sin(i * 1.31)), 44, 104))
        if dur > 0:
            events.append(MusicEvent(pitch=p, volume=vel,
                                     start_tick=tick, end_tick=tick + dur))
        tick += dur
        center += r.normal(0.0, 0.9)
        i += 1
    return events


# global raw events (absolute ticks) for phase-1 export AND phase-2 lead
RAW_EVENTS = []
for s, (name, bars, prog, tech, dens, center, smult) in enumerate(SECTIONS):
    sec_ticks = bars * BAR
    s_off = SECTION_START[name] * BAR
    for e in raw_events_for(tech, dens, sec_ticks, center, smult, SEED + s):
        RAW_EVENTS.append(MusicEvent(pitch=e.pitch, volume=e.volume,
                                     start_tick=e.start_tick + s_off,
                                     end_tick=e.end_tick + s_off))


def build_phase1():
    comp = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
    comp.create_matrix(num_voices=1, num_sections=len(SECTIONS))
    comp.add_voice("LeadRaw", program=65, channel=0)
    for name, bars, prog, tech, dens, center, smult in SECTIONS:
        comp.add_section(name, bars=bars)
    for name, bars, prog, tech, dens, center, smult in SECTIONS:
        s_off = SECTION_START[name] * BAR
        sec_ticks = bars * BAR
        seg = [e for e in RAW_EVENTS if s_off <= e.start_tick < s_off + sec_ticks]
        comp.fill_voice_section("LeadRaw", name,
                                MusicUnit(events=rel_events(seg, s_off, sec_ticks)))
    ok, msg = comp.validate()
    if not ok:
        raise RuntimeError(f"phase1 validate failed: {msg}")
    return comp


# ------------------------------------------------------------------ phase 2
def rel_events(abs_events, s_start, s_len):
    out = []
    for e in abs_events:
        s = e.start_tick - s_start
        en = e.end_tick - s_start
        if en <= 0 or s >= s_len:
            continue
        s = max(0, s)
        en = min(s_len, en)
        if en <= s:
            en = min(s_len, s + SIXTEENTH)
        out.append(MusicEvent(pitch=e.pitch, volume=e.volume,
                              start_tick=s, end_tick=en))
    out.sort(key=lambda e: (e.start_tick, e.end_tick, e.pitch))
    out.append(MusicEvent(pitch=0, volume=0,
                          start_tick=max(0, s_len - 10), end_tick=s_len))
    return out


def snap(t):
    return int(round(t / float(SIXTEENTH)) * SIXTEENTH)


def process_lead(raw):
    """Grid snap -> scale quantize -> chord-tone quantize (own bar) ->
    range enforce -> dedup -> voice-leading. Grid-locked perfect layer.
    Quantization is range-restricted (lead 48..84) so no post-clamp ever
    mutates a pitch-class."""
    LO, HI = 48, 84
    events = []
    for e in raw:
        st = snap(e.start_tick)
        st = max(0, min(TOTAL_TICKS - SIXTEENTH, st))
        bar = min(TOTAL_BARS - 1, st // BAR)
        deg = BAR_DEGREE[bar]
        sc = nearest_scale(e.pitch, LO, HI)
        ct = nearest_chord(sc, deg, LO, HI)
        events.append(MusicEvent(pitch=ct, volume=e.volume,
                                 start_tick=st, end_tick=st + EIGHTH))
    # dedup collided (start_tick, pitch) keep longest
    best = {}
    for e in events:
        k = (e.start_tick, e.pitch)
        if k not in best or e.end_tick > best[k].end_tick:
            best[k] = e
    events = sorted(best.values(), key=lambda e: (e.start_tick, e.pitch))
    # voice-leading: cap adjacent leap <= 9 semitones (range-restricted)
    fixed = []
    for e in events:
        if fixed:
            prev = fixed[-1]
            if abs(e.pitch - prev.pitch) > 9:
                bar = min(TOTAL_BARS - 1, e.start_tick // BAR)
                pcs = chord_pcs(BAR_DEGREE[bar])
                cand = nearest_in_pcs((prev.pitch + e.pitch) // 2, pcs, LO, HI)
                if cand is not None:
                    e.pitch = cand
        fixed.append(e)
    return fixed


def build_horns():
    evs = []
    for bar in range(TOTAL_BARS):
        s = bar // 4
        b = bar % 4
        deg = BAR_DEGREE[bar]
        voicing = chord_voicing(deg, base=67)
        t0 = b * BAR + SECTION_START[SECTIONS[s][0]] * BAR
        stab = [0, 720, 1200]
        if SECTIONS[s][0] in ('Chorus', 'Chorus2'):
            stab = [0, 720, 1200, 1680]
        for k, off in enumerate(stab):
            p = voicing[(k * 2) % 3] + 12
            evs.append(MusicEvent(pitch=p, volume=78,
                                  start_tick=t0 + off, end_tick=t0 + off + SIXTEENTH))
    return evs


def build_rhodes():
    evs = []
    for bar in range(TOTAL_BARS):
        s = bar // 4
        b = bar % 4
        deg = BAR_DEGREE[bar]
        voicing = chord_voicing(deg, base=55)
        t0 = b * BAR + SECTION_START[SECTIONS[s][0]] * BAR
        third, fifth = voicing[1] + 12, voicing[2] + 12
        for k in range(0, BAR, 480):
            if k % 960 == 0:
                evs.append(MusicEvent(pitch=third, volume=58,
                                      start_tick=t0 + k, end_tick=t0 + k + 420))
            else:
                evs.append(MusicEvent(pitch=fifth, volume=52,
                                      start_tick=t0 + k, end_tick=t0 + k + 380))
    return evs


def build_bass():
    evs = []
    for bar in range(TOTAL_BARS):
        s = bar // 4
        b = bar % 4
        deg = BAR_DEGREE[bar]
        root = diatonic_note(DEGREE_STEP[deg], base=43)      # G2 region
        fifth = root + 7
        t0 = b * BAR + SECTION_START[SECTIONS[s][0]] * BAR
        evs += [
            MusicEvent(pitch=root, volume=102, start_tick=t0, end_tick=t0 + 360),
            MusicEvent(pitch=fifth, volume=88, start_tick=t0 + 480, end_tick=t0 + 840),
            MusicEvent(pitch=root, volume=102, start_tick=t0 + 960, end_tick=t0 + 1320),
            MusicEvent(pitch=fifth, volume=88, start_tick=t0 + 1440, end_tick=t0 + 1800),
        ]
        if SECTIONS[s][0] in ('Chorus', 'Chorus2'):
            evs.append(MusicEvent(pitch=root, volume=92, start_tick=t0 + 1800,
                                  end_tick=t0 + BAR - 10))
    return evs


def build_counter():
    """String-ensemble counterline, only in Chorus/Chorus2 (density rise)."""
    evs = []
    for bar in range(TOTAL_BARS):
        s = bar // 4
        if SECTIONS[s][0] not in ('Chorus', 'Chorus2'):
            continue
        b = bar % 4
        deg = BAR_DEGREE[bar]
        voicing = chord_voicing(deg, base=79)      # high register
        line = [voicing[1], voicing[2], voicing[3], voicing[1]]
        t0 = b * BAR + SECTION_START[SECTIONS[s][0]] * BAR
        for pos, p in zip([0, 4, 8, 12], line):
            evs.append(MusicEvent(pitch=p, volume=74,
                                  start_tick=t0 + pos * SIXTEENTH,
                                  end_tick=t0 + pos * SIXTEENTH + 3 * SIXTEENTH))
    return evs


def build_drums():
    evs = []
    for bar in range(TOTAL_BARS):
        s = bar // 4
        b = bar % 4
        t0 = b * BAR + SECTION_START[SECTIONS[s][0]] * BAR
        name = SECTIONS[s][0]
        kick, snare, hh, ohh, crash, clap = 36, 38, 42, 46, 49, 39
        for k in range(0, BAR, 240):                       # 8th hats
            evs.append(MusicEvent(pitch=hh, volume=44,
                                  start_tick=t0 + k, end_tick=t0 + k + 90))
        evs.append(MusicEvent(pitch=kick, volume=100, start_tick=t0, end_tick=t0 + 160))
        evs.append(MusicEvent(pitch=kick, volume=98, start_tick=t0 + 960, end_tick=t0 + 1120))
        if name in ('Chorus', 'Chorus2'):
            for p in (480, 1440):
                evs.append(MusicEvent(pitch=snare, volume=100, start_tick=t0 + p, end_tick=t0 + p + 140))
                evs.append(MusicEvent(pitch=clap, volume=86, start_tick=t0 + p, end_tick=t0 + p + 120))
            evs.append(MusicEvent(pitch=crash, volume=90, start_tick=t0, end_tick=t0 + 240))
            evs.append(MusicEvent(pitch=ohh, volume=70, start_tick=t0 + 1680, end_tick=t0 + 1800))
        elif name in ('Intro', 'Outro'):
            evs.append(MusicEvent(pitch=snare, volume=80, start_tick=t0 + 480, end_tick=t0 + 620))
            evs.append(MusicEvent(pitch=snare, volume=82, start_tick=t0 + 1440, end_tick=t0 + 1580))
        else:
            for p in (480, 1440):
                evs.append(MusicEvent(pitch=snare, volume=88, start_tick=t0 + p, end_tick=t0 + p + 140))
    return evs


VOICES = [
    ("Lead",    65, 0),
    ("Horns",   61, 1),
    ("Rhodes",  4,  2),
    ("Bass",    33, 3),
    ("Counter", 48, 4),
    ("Drums",   0,  9),
]


def build_phase2(lead_ev, horns_ev, rhodes_ev, bass_ev, counter_ev, drums_ev):
    comp = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
    comp.create_matrix(num_voices=len(VOICES), num_sections=len(SECTIONS))
    for name, prog, ch in VOICES:
        comp.add_voice(name, program=prog, channel=ch)
    for name, bars, prog, tech, dens, center, smult in SECTIONS:
        comp.add_section(name, bars=bars)
    vmap = {"Lead": lead_ev, "Horns": horns_ev, "Rhodes": rhodes_ev,
            "Bass": bass_ev, "Counter": counter_ev, "Drums": drums_ev}
    for name, bars, prog, tech, dens, center, smult in SECTIONS:
        s_off = SECTION_START[name] * BAR
        sec_ticks = bars * BAR
        for vname, all_ev in vmap.items():
            seg = [e for e in all_ev if s_off <= e.start_tick < s_off + sec_ticks]
            unit = MusicUnit(events=rel_events(seg, s_off, sec_ticks))
            comp.fill_voice_section(vname, name, unit)
    ok, msg = comp.validate()
    if not ok:
        raise RuntimeError(f"phase2 validate failed: {msg}")
    return comp


def main():
    # ---- phase 1 ----
    phase1 = build_phase1()
    phase1_mid = os.path.join(MIDI_DIR, BASE + "-phase1.mid")
    phase1.to_midi(phase1_mid)
    write_provenance(
        phase1_mid, AI_ASSISTED,
        "musicom two-phase rework (phase=1 raw Xenakis sieve walk, Method 025)",
        sources=["/opt/data/projects/Styles/Groove/080-groove-sieve/MIDI/080-groove-sieve-phase1.mid"],
        parameters={"bpm": BPM, "key": KEY_NAME, "phase": 1, "quantized": False,
                    "bars": TOTAL_BARS, "style": STYLE, "genre": GENRE,
                    "seed": SEED, "sieve_offsets": SIEVE_OFFSETS,
                    "sieve_A": {"mod": SIEVE_A_MOD, "res": list(SIEVE_A_RES)},
                    "sieve_B": {"mod": SIEVE_B_MOD, "res": list(SIEVE_B_RES)}},
        notes="Raw sieve walk, single voice, off-grid onsets, no harmony, pre-rules.")
    write_grid_visualization(phase1.matrix,
                             os.path.join(ANALYSIS_DIR, "grid_visualization_phase1.txt"),
                             ticks_per_character=120, voice_names=["LeadRaw"], bpm=BPM)

    # ---- phase 2 rules ----
    lead_ev = process_lead(RAW_EVENTS)
    horns_ev = build_horns()
    rhodes_ev = build_rhodes()
    bass_ev = build_bass()
    counter_ev = build_counter()
    drums_ev = build_drums()
    phase2 = build_phase2(lead_ev, horns_ev, rhodes_ev, bass_ev, counter_ev, drums_ev)

    # ---- dual-version export (perfect + humanized) ----
    inst_map = {"Lead": "soprano_sax", "Horns": "brass_section",
                "Rhodes": "rhodes", "Bass": "electric_bass",
                "Counter": "string_ensemble"}
    import sys
    sys.path.insert(0, "/opt/data/repos/musicom/projects/Instruments")
    from instrument_registry import by_name
    hz_instruments = {v: by_name(inst_map[v]).humanize_dna for v in inst_map}
    hz_instruments["Drums"] = (2.0, 4.0, 0.0, 0.008)

    perfect_path = os.path.join(MIDI_DIR, BASE + "-perfect.mid")
    humanized_path = os.path.join(MIDI_DIR, BASE + "-humanized.mid")
    hz = export_dual(phase2, perfect_path, humanized_path,
                     style=STYLE, seed=hz_seed, bpm=BPM,
                     instruments=hz_instruments)

    # ---- provenance sidecars ----
    provenance_params = {
        "bpm": BPM, "key": KEY_NAME, "mode": "aeolian", "style": STYLE,
        "genre": GENRE, "form": "32 bars / 8 sections", "bars": TOTAL_BARS,
        "sections": [{"name": s[0], "bars": s[1], "prog": s[2],
                      "technique": s[3]} for s in SECTIONS],
        "method": "025 Xenakis Sieve Theory", "rework_source": "080-groove-sieve",
        "seed": SEED, "humanize_seed": hz_seed,
        "voices": [[v[0], v[1], v[2]] for v in VOICES],
        "humanize_profiles": {k: v.get("profile") for k, v in hz.items()},
    }
    write_provenance(
        perfect_path, AI_ASSISTED,
        "musicom two-phase rework (phase=2 rules: grid snap + scale/chord-tone "
        "quantize + voice-leading + range) (Method 025 Xenakis Sieve)",
        sources=[phase1_mid],
        parameters=dict(provenance_params, phase=2, version="perfect", off_grid=0),
        notes="Grid-locked perfect layer (32 bars / 8 sections).")
    write_provenance(
        humanized_path, AI_ASSISTED,
        "musicom two-phase rework (phase=2 + humanization) (Method 025 Xenakis Sieve)",
        sources=[perfect_path],
        parameters=dict(provenance_params, phase=2, version="humanized",
                        humanize_seed=hz_seed,
                        humanize_stats={k: {kk: (float(vv) if isinstance(vv, float) else vv)
                                            for kk, vv in v.items() if kk != "profile"}
                                        for k, v in hz.items()}),
        notes="Humanized layer (style groove + per-instrument DNA).")

    # ---- grid visualization ----
    write_grid_visualization(phase2.matrix,
                             os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
                             ticks_per_character=120,
                             voice_names=[v[0] for v in VOICES], bpm=BPM)

    # ---- size asserts ----
    for p in (phase1_mid, perfect_path, humanized_path):
        assert os.path.getsize(p) > 40, f"empty/corrupt: {p}"

    # ---- summary ----
    summary = {
        "project": BASE, "pid": PID, "genre": GENRE, "style": STYLE,
        "key": KEY_NAME, "key_pcs": sorted(KEY_PCS), "bpm": BPM,
        "bars": TOTAL_BARS,
        "sections": [{"name": s[0], "bars": s[1], "prog": s[2], "technique": s[3]}
                     for s in SECTIONS],
        "phase1_path": phase1_mid, "perfect_path": perfect_path,
        "humanized_path": humanized_path, "hz_seed": hz_seed,
        "hz": {k: {kk: vv for kk, vv in v.items() if kk != "profile"}
               for k, v in hz.items()},
        "raw_event_count": len(RAW_EVENTS),
        "lead_event_count": len(lead_ev),
    }
    with open(os.path.join(PROJ, "composition_meta.json"), "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print("COMPOSE_OK")
    print(json.dumps(summary, indent=2, default=str))
    print("EVENTS:", len(lead_ev), len(horns_ev), len(rhodes_ev), len(bass_ev),
          len(counter_ev), len(drums_ev))
    return summary


if __name__ == "__main__":
    main()
