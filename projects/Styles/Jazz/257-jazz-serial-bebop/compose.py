# -*- coding: utf-8 -*-
"""257-jazz-serial-bebop — nightly composition (2026-10-22).

Method 065 — Twelve-Tone Serial Matrix Composition (TTSMC), layer concrete.
Style Jazz (bebop, ii-V-I swing), F major, 120 BPM, form intro-a-a-b-a.

Two-phase architecture:
  Phase 1 (raw): a 12-tone row + its P/R/I/RI forms drive a single-voice
    raw draft. Each section is a row-form region (Intro=P0, A1=P0, A2=R0,
    B=I0, A3=RI0). Raw pitches are the literal chromatic row pitch-classes
    (all 12 pcs, off-scale BY DESIGN = the serial fingerprint), onsets
    fractional OFF-GRID. NO harmony.
  Phase 2 (rules): onset snap to 16th grid -> row pc -> nearest F-major scale
    degree -> nearest chord tone of the bar's jazz 7th chord (ii-V-I family)
    -> full 5-voice swing texture (sax lead / trumpet guide-tones / piano
    comp / walking bass / swing drums) -> zero-drift landmark padding.
    Tiered pitch discipline: strong beats (1,3) = chord tones, weak beats
    (2,4) = in-scale (bass beat-4 uses a diatonic leading tone).

Engine-only: structures + workflows.unitmatrix_composer + workflows.humanize.
mido used READ-ONLY for audits. Instruments from the importable registry.
"""
import json
import random
import sys
from pathlib import Path

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.provenance import write_provenance
from workflows.humanize import export_dual
from visualization.grid import write_grid_visualization

# ---- instrument registry (source of truth) ---------------------------------
INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import (  # noqa: E402
    SAXOPHONE, TRUMPET, PIANO, DOUBLE_BASS, DRUM_KIT,
)

# ---- concept ---------------------------------------------------------------
GENRE = "Jazz"
NAME = "257-jazz-serial-bebop"
ROOT = Path(f"/opt/data/projects/Styles/{GENRE}/{NAME}")
for sub in ("MIDI", "Audio", "Analysis"):
    (ROOT / sub).mkdir(parents=True, exist_ok=True)

TONIC = 5                       # F
KEY_NAME = "F major"
MAJOR_OFFS = [0, 2, 4, 5, 7, 9, 11]     # ionian intervals
SCALE_DEG_PCS = [(TONIC + o) % 12 for o in MAJOR_OFFS]   # F G A Bb C D E
SCALE_PCS = set(SCALE_DEG_PCS)
BPM = 120
TPB = 480
BAR = 1920
EIGHTH = 240
SIXTEENTH = 120
BEAT = BAR // 4                 # 480
SWING_OFF = int(2 * BEAT / 3)   # 320 — swung 8th off-beat (2:1, matches ride)
SEED = 20261022
rng = random.Random(SEED)

# ---- form: intro-a-a-b-a = 36 bars (unique section names for the engine) ---
FORM_NAME = "intro-a-a-b-a"
FORM = [("Intro", 4), ("A1", 8), ("A2", 8), ("B", 8), ("A3", 8)]
N_BARS = sum(b for _, b in FORM)
SECTION_TICKS = {}
_tick = 0
for s, b in FORM:
    SECTION_TICKS[s] = (b * BAR, _tick)
    _tick += b * BAR
TOTAL_TICKS = _tick


def section_of_bar(b):
    acc = 0
    for sname, nbars in FORM:
        if acc <= b < acc + nbars:
            return sname
        acc += nbars
    return FORM[-1][0]


# ---- harmony: diatonic 7th chords in F major -------------------------------
DEG_NAMES = ["Imaj7", "ii7", "iii7", "IVmaj7", "V7", "vi7", "viio7"]
DEG_LABELS = ["Fmaj7", "Gm7", "Am7", "Bbmaj7", "C7", "Dm7", "Eo7"]


def chord_pcs(deg, seventh=True):
    idx = [deg % 7, (deg + 2) % 7, (deg + 4) % 7]
    if seventh:
        idx.append((deg + 6) % 7)
    return frozenset((TONIC + MAJOR_OFFS[i]) % 12 for i in idx)


def pc_to_pitch(pc, floor):
    for p in range(floor, floor + 12):
        if p % 12 == pc:
            return p
    return floor


def chord_tones(deg, seventh, floor, ceil):
    pcs = chord_pcs(deg, seventh)
    out = []
    for pc in sorted(pcs):
        p = pc_to_pitch(pc, floor)
        while p <= ceil:
            out.append(p)
            p += 12
    return sorted(out)


# per-bar chord specs: (degree, seventh) — jazz turnaround / ii-V-I / circle
CHORD_SPECS = []
for b in range(N_BARS):
    s = section_of_bar(b)
    bi = b - SECTION_TICKS[s][1] // BAR
    if s == "Intro":
        spec = [0, 5, 1, 4][bi]                # I vi ii V
    elif s in ("A1", "A2", "A3"):
        spec = [1, 4, 0, 5, 1, 4, 0, 0][bi]    # ii V I vi | ii V I I
    else:  # B
        spec = [2, 5, 1, 4, 2, 5, 1, 4][bi]    # iii vi ii V (circle, x2)
    CHORD_SPECS.append((spec, True))


def bar_deg(b):
    return CHORD_SPECS[b][0]


# midpoint root per section (for the report)
section_roots = {}
for sname, nbars in FORM:
    soff = SECTION_TICKS[sname][1] // BAR
    mid = soff + nbars // 2
    section_roots[sname] = CHORD_SPECS[mid][0]

# register pools per bar (chord tones realized per voice register)
LEAD_POOL = {b: chord_tones(CHORD_SPECS[b][0], True, 55, 88) for b in range(N_BARS)}
TRUMPET_POOL = {b: chord_tones(CHORD_SPECS[b][0], True, 55, 81) for b in range(N_BARS)}
PIANO_POOL = {b: chord_tones(CHORD_SPECS[b][0], True, 48, 84) for b in range(N_BARS)}
BASS_POOL = {b: chord_tones(CHORD_SPECS[b][0], True, 38, 50) for b in range(N_BARS)}


def snap16(t):
    return int(round(t / SIXTEENTH) * SIXTEENTH)


# ============================================================================
# PHASE 1 — RAW TWELVE-TONE SERIAL DRAFT (single voice, off-grid, chromatic)
# ============================================================================
# 12-tone row = deterministic permutation of the 12 pitch classes
ROW_P0 = rng.sample(range(12), 12)                 # prime
ROW_I0 = [(12 - p) % 12 for p in ROW_P0]           # inversion
ROW_R0 = ROW_P0[::-1]                              # retrograde
ROW_RI0 = [(12 - p) % 12 for p in ROW_R0]          # retrograde-inversion

# each section = a row-form region
ROW_FORM = {"Intro": ROW_P0, "A1": ROW_P0, "A2": ROW_R0, "B": ROW_I0, "A3": ROW_RI0}

raw_events = []                 # dicts: start_tick, row_pc, velocity, dur
form_counter = 0
for b in range(N_BARS):
    s = section_of_bar(b)
    if b == 0 or section_of_bar(b - 1) != s:
        form_counter = 0        # reset row index at each section boundary
    form = ROW_FORM[s]
    n_ev = rng.randint(6, 9)
    for k in range(n_ev):
        frac = (k + rng.uniform(0.0, 0.85)) / n_ev
        st = b * BAR + int(frac * BAR)
        row_pc = form[form_counter % 12]
        form_counter += 1
        dur = int(rng.uniform(0.3, 0.9) * EIGHTH)
        raw_events.append({"start_tick": st, "row_pc": row_pc,
                           "velocity": rng.randint(72, 96), "dur": dur})


def unit_from(events, sec_len):
    u = MusicUnit()
    for e in events:
        if e.end_tick > e.start_tick:
            u.add_event(e)
    u.add_event(MusicEvent(0, 0, sec_len, sec_len))   # zero-drift landmark
    return u


p1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=4)
p1.create_matrix(num_voices=1, num_sections=len(FORM))
p1.add_voice("RawRow", program=SAXOPHONE.midi_program, channel=0)
for sname, nbars in FORM:
    p1.add_section(sname, bars=nbars)
for sname, (slen, soff) in SECTION_TICKS.items():
    evs = []
    for e in raw_events:
        if soff <= e["start_tick"] < soff + slen:
            pitch = 60 + e["row_pc"]                       # literal row pc
            st = e["start_tick"] - soff
            end = min(st + e["dur"], slen - 1)
            evs.append(MusicEvent(pitch=pitch, volume=e["velocity"],
                                  start_tick=st, end_tick=end))
    p1.fill_voice_section("RawRow", sname, unit_from(evs, slen))
ok1, msg1 = p1.validate()
assert ok1, f"phase1 validate failed: {msg1}"
midi1 = ROOT / "MIDI" / f"{NAME}-phase1.mid"
p1.to_midi(str(midi1))
write_provenance(str(midi1), "ai-generated", f"musicom nightly {NAME}",
                 sources=["methods_db:065 Twelve-Tone Serial Matrix (P/R/I/RI)",
                          f"style:{GENRE}", "phase:1 raw draft"],
                 parameters={"phase": 1, "seed": SEED, "key": KEY_NAME,
                             "bpm": BPM, "form": FORM_NAME,
                             "row_p0": ROW_P0,
                             "notes": "12-tone row P0 -> chromatic raw draft; "
                                      "sections are row-form regions"})
print("phase1 midi:", midi1, midi1.stat().st_size, "bytes")

# ============================================================================
# PHASE 2 — RULES POST-PROCESS (grid snap + chord quant + full jazz texture)
# ============================================================================

def nearest_degree(row_pc):
    """Project a raw 12-tone pc onto the nearest F-major scale degree."""
    best, bd = 0, 13
    for d, spc in enumerate(SCALE_DEG_PCS):
        dist = min((row_pc - spc) % 12, (spc - row_pc) % 12)
        if dist < bd:
            best, bd = d, dist
    return best


def lead_events():
    notes = []
    for b in range(N_BARS):
        s = section_of_bar(b)
        pool = LEAD_POOL[b]
        raw = [e for e in raw_events if b * BAR <= e["start_tick"] < (b + 1) * BAR]
        raw.sort(key=lambda e: e["start_tick"])
        for e in raw:
            st = snap16(e["start_tick"])
            if st >= (b + 1) * BAR:
                st = (b + 1) * BAR - SIXTEENTH
            d = nearest_degree(e["row_pc"])
            dur = max(SIXTEENTH, snap16(e["dur"]))
            vel = e["velocity"]
            if s == "B":                       # density rise (16th runs)
                dur = SIXTEENTH
                vel = min(127, vel + 6)
            elif s == "A3":                    # fade toward close
                vel = max(40, vel - 22)
            elif s == "Intro":                 # sparse, longer
                dur = min(EIGHTH * 2, dur + EIGHTH)
            target = pc_to_pitch(SCALE_DEG_PCS[d], 58)
            best = min(pool, key=lambda p: abs(p - target))
            for cand in (best - 12, best + 12):
                if abs(cand - target) < abs(best - target):
                    best = cand
            pitch = max(55, min(88, best))
            notes.append(MusicEvent(pitch=pitch, volume=int(vel),
                                    start_tick=st,
                                    end_tick=min(st + dur, (b + 1) * BAR - 1)))
    return notes


def trumpet_events():
    """Guide-tone counterline: 3rd & 7th of each chord on beats 2 and 4."""
    evs = []
    for b in range(N_BARS):
        tones = TRUMPET_POOL[b]
        bar0 = b * BAR
        third = tones[1] if len(tones) > 1 else tones[0]
        seventh = tones[3] if len(tones) > 3 else tones[-1]
        evs.append(MusicEvent(pitch=third, volume=70,
                              start_tick=bar0 + BEAT, end_tick=bar0 + BEAT + EIGHTH * 2))
        evs.append(MusicEvent(pitch=seventh, volume=68,
                              start_tick=bar0 + 3 * BEAT, end_tick=bar0 + 3 * BEAT + EIGHTH * 2))
    return evs


def piano_events():
    """Comping: chord voicings on 'and of 2' and 'and of 4' (on-grid 8ths)."""
    evs = []
    for b in range(N_BARS):
        tones = PIANO_POOL[b]
        bar0 = b * BAR
        for st in (bar0 + 3 * EIGHTH, bar0 + 7 * EIGHTH):   # 720, 1680
            for p in tones[:4]:
                evs.append(MusicEvent(pitch=p, volume=60,
                                      start_tick=st, end_tick=st + EIGHTH))
    return evs


def bass_events():
    """Walking bass: root/3rd/5th (strong=chord) + diatonic leading tone (weak)."""
    evs = []
    for b in range(N_BARS):
        tones = BASS_POOL[b]
        root = tones[0]
        bar0 = b * BAR
        evs.append(MusicEvent(pitch=root, volume=92, start_tick=bar0, end_tick=bar0 + BEAT))
        evs.append(MusicEvent(pitch=tones[1] if len(tones) > 1 else root, volume=84,
                              start_tick=bar0 + BEAT, end_tick=bar0 + 2 * BEAT))
        evs.append(MusicEvent(pitch=tones[2] if len(tones) > 2 else root, volume=86,
                              start_tick=bar0 + 2 * BEAT, end_tick=bar0 + 3 * BEAT))
        # beat 4: diatonic leading tone one semitone below next bar's root
        nxt = bar_deg((b + 1) % N_BARS)
        next_root_pc = (TONIC + MAJOR_OFFS[nxt]) % 12
        lead = (next_root_pc - 1) % 12
        if lead in SCALE_PCS:
            lead_pitch = pc_to_pitch(lead, 38)
        else:
            lead_pitch = tones[3] if len(tones) > 3 else root
        lead_pitch = max(38, min(50, lead_pitch))
        evs.append(MusicEvent(pitch=lead_pitch, volume=82,
                              start_tick=bar0 + 3 * BEAT, end_tick=bar0 + 4 * BEAT))
    return evs


def drums_events():
    """Swing ride + hi-hat chick (2,4) + feather kick (1,3). Channel 9."""
    evs = []
    for b in range(N_BARS):
        s = section_of_bar(b)
        bar0 = b * BAR
        for beat in range(4):
            base = bar0 + beat * BEAT
            evs.append(MusicEvent(pitch=51, volume=64,
                                  start_tick=base, end_tick=base + SIXTEENTH * 2))
            if not (s == "A3" and beat == 3):
                sw = base + int(2 * BEAT / 3)           # swung off-beat
                evs.append(MusicEvent(pitch=51, volume=56,
                                      start_tick=sw, end_tick=sw + SIXTEENTH))
        for beat in (1, 3):                             # hi-hat chick
            st = bar0 + beat * BEAT
            evs.append(MusicEvent(pitch=42, volume=88, start_tick=st, end_tick=st + SIXTEENTH))
        for beat in (0, 2):                             # feather kick
            st = bar0 + beat * BEAT
            evs.append(MusicEvent(pitch=36, volume=72, start_tick=st, end_tick=st + SIXTEENTH))
    return evs


def finalize_pitched(events, pool_by_bar):
    """Grid-snap + chord-tone snap + (start,pitch) dedupe for pitched voices."""
    out = []
    for e in events:
        if e.pitch == 0:
            out.append(e)
            continue
        st = snap16(e.start_tick)
        if st < 0:
            st = 0
        bar = min(st // BAR, N_BARS - 1)
        pool = pool_by_bar[bar]
        best = min(pool, key=lambda p: abs(p - e.pitch))
        for cand in (best - 12, best + 12):
            if abs(cand - e.pitch) < abs(best - e.pitch):
                best = cand
        out.append(MusicEvent(pitch=best, volume=int(e.volume),
                              start_tick=st, end_tick=max(st + 1, e.end_tick)))
    seen = {}
    res = []
    for e in out:
        if e.pitch == 0:
            res.append(e)
            continue
        key = (e.start_tick, e.pitch)
        if key in seen:
            seen[key].end_tick = max(seen[key].end_tick, e.end_tick)
        else:
            seen[key] = e
            res.append(e)
    res.sort(key=lambda e: (e.start_tick, e.pitch))
    return res


def finalize_bass(events):
    """Grid-snap only (keep the diatonic leading tone) + register clamp + dedupe."""
    out = []
    for e in events:
        if e.pitch == 0:
            out.append(e)
            continue
        st = snap16(e.start_tick)
        pitch = max(38, min(50, e.pitch))
        if pitch % 12 not in SCALE_PCS:     # safety: force in-scale
            pitch = min(BASS_POOL[min(st // BAR, N_BARS - 1)],
                        key=lambda p: abs(p - e.pitch))
        out.append(MusicEvent(pitch=pitch, volume=int(e.volume),
                              start_tick=st, end_tick=max(st + 1, e.end_tick)))
    seen = {}
    res = []
    for e in out:
        if e.pitch == 0:
            res.append(e)
            continue
        key = (e.start_tick, e.pitch)
        if key in seen:
            seen[key].end_tick = max(seen[key].end_tick, e.end_tick)
        else:
            seen[key] = e
            res.append(e)
    res.sort(key=lambda e: (e.start_tick, e.pitch))
    return res


def cap_leaps(events, pool_by_bar, max_leap=11):
    evs = sorted([e for e in events if e.pitch], key=lambda e: e.start_tick)
    for i in range(1, len(evs)):
        prev, cur = evs[i - 1], evs[i]
        if cur.start_tick - prev.start_tick <= BAR and abs(cur.pitch - prev.pitch) > max_leap:
            bar = min(cur.start_tick // BAR, N_BARS - 1)
            pool = pool_by_bar[bar]
            target = prev.pitch + max_leap if cur.pitch > prev.pitch else prev.pitch - max_leap
            best = min(pool, key=lambda p: (abs(p - target), abs(p - cur.pitch)))
            cur.pitch = best
    return evs


def swing8(events):
    """Swing straight 8th-note off-beats (pos 240) to the 2:1 swing position
    (320), matching the ride's swing. 16th subdivisions (120/360) stay
    straight — bebop convention: straight 16ths over swing 8ths. Re-dedupe
    after the shift since two straight notes may land on the same swing slot."""
    out = []
    seen = {}
    for e in events:
        beat = e.start_tick // BEAT
        pos = e.start_tick % BEAT
        if pos == EIGHTH:
            e.start_tick = beat * BEAT + SWING_OFF
        key = (e.start_tick, e.pitch)
        if key in seen:
            seen[key].end_tick = max(seen[key].end_tick, e.end_tick)
        else:
            seen[key] = e
            out.append(e)
    out.sort(key=lambda e: (e.start_tick, e.pitch))
    return out


lead_q = swing8(cap_leaps(finalize_pitched(lead_events(), LEAD_POOL), LEAD_POOL))
trumpet_q = finalize_pitched(trumpet_events(), TRUMPET_POOL)
piano_q = swing8(finalize_pitched(piano_events(), PIANO_POOL))
bass_q = finalize_bass(bass_events())
drums_q = drums_events()

VOICES = [
    ("LeadSax", SAXOPHONE.midi_program, 0),
    ("Trumpet", TRUMPET.midi_program, 1),
    ("Piano", PIANO.midi_program, 2),
    ("Bass", DOUBLE_BASS.midi_program, 3),
    ("Drums", 0, 9),
]
events_by_voice = {
    "LeadSax": lead_q, "Trumpet": trumpet_q, "Piano": piano_q,
    "Bass": bass_q, "Drums": drums_q,
}

composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=4)
composer.create_matrix(num_voices=len(VOICES), num_sections=len(FORM))
for vname, prog, ch in VOICES:
    composer.add_voice(vname, program=prog, channel=ch)
for sname, nbars in FORM:
    composer.add_section(sname, bars=nbars)

for vname, prog, ch in VOICES:
    evs = events_by_voice[vname]
    for sname, (slen, soff) in SECTION_TICKS.items():
        seg = sorted([e for e in evs if soff <= e.start_tick < soff + slen],
                     key=lambda e: (e.start_tick, e.pitch))
        for e in seg:
            e.start_tick -= soff
            e.end_tick -= soff
            if e.end_tick > slen:
                e.end_tick = slen
            if e.end_tick <= e.start_tick:
                e.end_tick = e.start_tick + 1
        composer.fill_voice_section(vname, sname, unit_from(seg, slen))

# ---- dual-version export (perfect then humanized) --------------------------
hz_seed = SEED + 1
hz_instruments = {
    "LeadSax": SAXOPHONE.humanize_dna,
    "Trumpet": TRUMPET.humanize_dna,
    "Piano": PIANO.humanize_dna,
    "Bass": DOUBLE_BASS.humanize_dna,
    "Drums": DRUM_KIT.humanize_dna,
}
perfect_path = ROOT / "MIDI" / f"{NAME}-perfect.mid"
humanized_path = ROOT / "MIDI" / f"{NAME}-humanized.mid"
hz = export_dual(composer, str(perfect_path), str(humanized_path),
                 style=GENRE, seed=hz_seed, bpm=BPM, instruments=hz_instruments)

for path, phase, note in ((perfect_path, "2-perfect", "grid-locked, no jitter"),
                          (humanized_path, "2-humanized", "style+instrument humanized")):
    write_provenance(str(path), "ai-generated", f"musicom nightly {NAME}",
                     sources=["methods_db:065 Twelve-Tone Serial Matrix", f"style:{GENRE}",
                              "phase:2 rules", f"humanize_seed:{hz_seed}"],
                     parameters={"phase": phase, "seed": SEED, "key": KEY_NAME,
                                 "bpm": BPM, "form": FORM_NAME,
                                 "humanize": hz, "note": note})
print("perfect midi:", perfect_path, perfect_path.stat().st_size, "bytes")
print("humanized midi:", humanized_path, humanized_path.stat().st_size, "bytes")

# ---- grid visualization + summary ------------------------------------------
try:
    write_grid_visualization(composer.matrix,
                             str(ROOT / "Analysis" / "grid_visualization.txt"))
except Exception as exc:
    print("grid viz skipped:", exc)

summary = {
    "project": NAME, "genre": GENRE, "method": "065 Twelve-Tone Serial Matrix",
    "layer": "concrete", "key": KEY_NAME, "bpm": BPM, "form": FORM_NAME,
    "form_sections": [s for s, _ in FORM], "bars": N_BARS,
    "total_ticks": TOTAL_TICKS, "tonic": TONIC,
    "row_p0": ROW_P0, "row_i0": ROW_I0, "row_r0": ROW_R0, "row_ri0": ROW_RI0,
    "row_form_by_section": {s: "P0" if ROW_FORM[s] is ROW_P0
                            else "R0" if ROW_FORM[s] is ROW_R0
                            else "I0" if ROW_FORM[s] is ROW_I0 else "RI0"
                            for s, _ in FORM},
    "section_roots_midpoint": {s: DEG_LABELS[section_roots[s]] for s, _ in FORM},
    "voices": [v for v, _, _ in VOICES],
    "humanize_seed": hz_seed,
}
with open(ROOT / "Analysis" / "summary.json", "w") as f:
    json.dump(summary, f, indent=2)
print("DONE compose")
