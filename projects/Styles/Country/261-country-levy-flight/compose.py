# -*- coding: utf-8 -*-
"""261-country-levy-flight — Country Levy Flight Composition (Method 053 LFC).

Two-phase architecture (mandatory):
  Phase 1 = raw generative draft: a heavy-tailed Levy-flight random walk in
            pitch space, single voice, unquantized chromatic pitches, off-grid
            onsets, NO harmony. Exported as <project>-phase1.mid.
  Phase 2 = musicom rules post-processing: tiered pitch discipline
            (strong -> scale THEN chord, weak -> scale only), 16th-grid onset
            snap, tagged chromatic approach ornaments on the lead (rules.ornament),
            full texture (fiddle lead + steel-guitar strum + double-bass +
            train-beat drums). Dual-version export (perfect + humanized).

Method 053 LFC (concrete, Stochastic, Nature-Led): clusters of short steps =
motifs; rare long jumps = dramatic leaps / section pivots.
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
from sound.synthesis.scale_quantizer import ScaleQuantizer, classify_weight, STRONG_GRID
from rules.ornament import approach_note
from workflows.pitch_audit import audit_voice

INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import FIDDLE, STEEL_ACOUSTIC, DOUBLE_BASS, DRUM_KIT  # noqa: E402

# ---------------- selection / concept ---------------------------------------
GENRE = "Country"
NAME = "261-country-levy-flight"
METHOD = "053 Levy Flight Composition (LFC)"
LAYER = "concrete"
PARADIGM = "Stochastic"
FORM_NAME = "aabb"
FORM = [("A1", 4), ("A2", 4), ("B1", 4), ("B2", 4)]
N_BARS = sum(b for _, b in FORM)

TONIC = 7                       # G
KEY_NAME = "G major"
SCALE_PCS = [7, 9, 11, 0, 2, 4, 6]
SCALE_SET = set(SCALE_PCS)
BPM = 112
TPB = 480
BAR = 1920
BEAT = 480
EIGHTH = 240
SIXTEENTH = 120
SEED = 20261023
HZ_SEED = SEED + 1

ROOT = Path(f"/opt/data/projects/Styles/{GENRE}/{NAME}")
for sub in ("MIDI", "Audio", "Analysis"):
    (ROOT / sub).mkdir(parents=True, exist_ok=True)

# chord progression per bar (G major, aabb: A = I-IV-I, B = V-IV-I-V turn)
CHORD_PCS = {"G": [7, 11, 2], "C": [0, 4, 7], "D": [2, 6, 9]}
CHORD_SEQ = ["G", "G", "C", "G", "G", "G", "C", "D",
             "D", "C", "G", "G", "D", "C", "D", "G"]
CHORD_BY_BAR = [CHORD_PCS[c] for c in CHORD_SEQ]
ROOT_PC = {"G": 7, "C": 0, "D": 2}

SECTION_TICKS = {}
_t = 0
for s, b in FORM:
    SECTION_TICKS[s] = (b * BAR, _t)
    _t += b * BAR
TOTAL_TICKS = _t


def section_of_bar(bar):
    acc = 0
    for s, n in FORM:
        if acc <= bar < acc + n:
            return s
        acc += n
    return FORM[-1][0]


def chord_tones(pcs, floor, ceil):
    out = []
    for pc in sorted(set(pcs)):
        p = floor + ((pc - floor) % 12)
        while p <= ceil:
            out.append(p)
            p += 12
    return sorted(out)


def pc_to_pitch(pc, floor):
    for p in range(floor, floor + 12):
        if p % 12 == pc:
            return p
    return floor


def unit_from(events, sec_len):
    u = MusicUnit()
    for e in events:
        if e.end_tick > e.start_tick:
            u.add_event(e)
    u.add_event(MusicEvent(0, 0, sec_len, sec_len))   # zero-drift landmark
    return u


# ---------------- Phase 1: raw Levy-flight draft ----------------------------
def levy_step(rng):
    """Heavy-tailed step in semitones: ~85% small (motif), ~15% large (leap)."""
    if rng.random() < 0.85:
        s = rng.randint(-3, 3)
        if s == 0:
            s = rng.choice([-1, 1])
        return s
    mag = int(round(4 + 10 * (rng.random() ** 2)))   # bias toward 4..7
    return mag * rng.choice([-1, 1])


def raw_levy_lead(rng):
    """Continuous Levy flight: float pitch, off-grid float onsets."""
    raw = []
    pitch = 67.0                       # G4 (fiddle core)
    tick = 0.0
    while tick < TOTAL_TICKS:
        pitch += levy_step(rng)
        pitch = max(57.0, min(88.0, pitch))          # clamp to fiddle register
        dur = rng.choice([240.0, 120.0, 480.0, 180.0, 300.0, 360.0])
        raw.append({"pitch": pitch, "start_tick": tick, "end_tick": tick + dur})
        tick += dur
    return raw


# ---------------- Phase 2: rules post-processing ----------------------------
def quantized_lead(raw):
    """Snap onsets to 16th grid, tiered-quantize pitch, tag ornaments."""
    sq = ScaleQuantizer(root=TONIC, scale="major")
    strong_grid = STRONG_GRID["4/4"]
    notes = []              # (start_tick, pitch, weight, end_tick)
    used_onsets = set()
    for r in raw:
        st = int(round(r["start_tick"] / SIXTEENTH)) * SIXTEENTH
        if st < 0 or st >= TOTAL_TICKS:
            continue
        if st in used_onsets:
            continue
        bar = min(st // BAR, N_BARS - 1)
        ct = chord_tones(CHORD_BY_BAR[bar], 62, 88)
        w = classify_weight(st, strong_grid, BAR)
        p = sq.tiered_quantize(r["pitch"], weight=w, chord_tones=ct)
        p = int(min(88, max(57, p)))
        dur = int(round((r["end_tick"] - r["start_tick"]) / SIXTEENTH)) * SIXTEENTH
        dur = min(max(dur, SIXTEENTH), BEAT * 2)
        end = min(st + dur, TOTAL_TICKS)
        if end <= st:
            end = st + SIXTEENTH
        notes.append({"pitch": p, "weight": w, "start_tick": st,
                      "end_tick": end, "volume": 78})
        used_onsets.add(st)

    notes.sort(key=lambda n: n["start_tick"])
    # tagged chromatic approach ornaments before a few strong beat-3 notes
    ornaments = []
    placed = 0
    for n in notes:
        if placed >= 6:
            break
        if n["weight"] != "strong":
            continue
        if n["start_tick"] % BAR != 2 * BEAT:      # beat 3 (960) only, safe slot
            continue
        ap = n["start_tick"] - SIXTEENTH
        if ap in used_onsets or ap < 0:
            continue
        orn = approach_note(n["pitch"], ap, n["start_tick"], volume=66)
        ornaments.append(orn)
        used_onsets.add(ap)
        placed += 1
    return notes + ornaments


def lead_events(notes):
    evs = []
    for n in notes:
        evs.append(MusicEvent(pitch=n["pitch"], volume=n.get("volume", 78),
                              start_tick=n["start_tick"], end_tick=n["end_tick"]))
    return sorted(evs, key=lambda e: (e.start_tick, e.pitch))


def guitar_events():
    """Steel-acoustic 'boom-chick': root on 1&3, full chord strum on 2&4."""
    evs = []
    for bar in range(N_BARS):
        pcs = CHORD_BY_BAR[bar]
        ct = chord_tones(pcs, 50, 72)
        root = pc_to_pitch(pcs[0], 50)
        fifth = ct[len(ct) // 2] if len(ct) > 1 else root + 7
        base = bar * BAR
        for beat in range(4):
            st = base + beat * BEAT
            if beat % 2 == 0:                      # boom (single root)
                evs.append(MusicEvent(pitch=root, volume=70, start_tick=st,
                                      end_tick=st + EIGHTH))
            else:                                   # chick (chord strum)
                for p in ct[:3]:
                    evs.append(MusicEvent(pitch=p, volume=64, start_tick=st,
                                          end_tick=st + EIGHTH))
    return evs


def bass_events():
    """Double-bass root-fifth alternation (root 1&3, fifth 2&4)."""
    evs = []
    for bar in range(N_BARS):
        pcs = CHORD_BY_BAR[bar]
        root = pc_to_pitch(pcs[0], 36)
        fifth = root + 7
        base = bar * BAR
        for beat in range(4):
            st = base + beat * BEAT
            p = root if beat % 2 == 0 else fifth
            evs.append(MusicEvent(pitch=p, volume=82, start_tick=st,
                                  end_tick=st + BEAT - SIXTEENTH))
    return evs


def drum_events():
    """Country train beat: kick 1&3, snare 2&4, closed hat 8ths (ch 9)."""
    evs = []
    KICK, SNARE, HAT = 35, 38, 42
    for bar in range(N_BARS):
        base = bar * BAR
        for beat in range(4):
            st = base + beat * BEAT
            if beat % 2 == 0:
                evs.append(MusicEvent(pitch=KICK, volume=90, start_tick=st,
                                      end_tick=st + SIXTEENTH))
            else:
                evs.append(MusicEvent(pitch=SNARE, volume=85, start_tick=st,
                                      end_tick=st + SIXTEENTH))
        for k in range(8):
            st = base + k * EIGHTH
            evs.append(MusicEvent(pitch=HAT, volume=60, start_tick=st,
                                  end_tick=st + SIXTEENTH))
    return evs


# ---------------- build + export -------------------------------------------
rng = random.Random(SEED)
raw = raw_levy_lead(rng)
lead_notes = quantized_lead(raw)

VOICES = [
    ("Lead", FIDDLE.midi_program, 0),
    ("Guitar", STEEL_ACOUSTIC.midi_program, 1),
    ("Bass", DOUBLE_BASS.midi_program, 2),
    ("Drums", DRUM_KIT.midi_program, 9),
]
EVENTS = {
    "Lead": lead_events(lead_notes),
    "Guitar": guitar_events(),
    "Bass": bass_events(),
    "Drums": drum_events(),
}


def fill(composer, evs_by_voice, voices=None):
    voices = voices or VOICES
    for vname, _, _ in voices:
        evs = evs_by_voice[vname]
        for sname, (slen, soff) in SECTION_TICKS.items():
            seg = []
            for e in evs:
                if soff <= e.start_tick < soff + slen:
                    st = e.start_tick - soff
                    en = e.end_tick - soff
                    if en > slen:
                        en = slen
                    if en <= st:
                        en = st + 1
                    # non-mutating copy so the absolute-tick source stays intact
                    seg.append(MusicEvent(pitch=e.pitch, volume=e.volume,
                                          start_tick=st, end_tick=en))
            seg.sort(key=lambda e: (e.start_tick, e.pitch))
            composer.fill_voice_section(vname, sname, unit_from(seg, slen))


# Phase 1: single-voice raw draft
phase1_composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=4)
phase1_composer.create_matrix(num_voices=1, num_sections=len(FORM))
phase1_composer.add_voice("Lead", program=FIDDLE.midi_program, channel=0)
for sname, nbars in FORM:
    phase1_composer.add_section(sname, bars=nbars)
raw_evs = [MusicEvent(pitch=int(round(r["pitch"])), volume=78,
                      start_tick=int(round(r["start_tick"])),
                      end_tick=int(round(r["end_tick"]))) for r in raw]
phase1_composer_events = {"Lead": raw_evs}
fill(phase1_composer, phase1_composer_events, voices=[("Lead", FIDDLE.midi_program, 0)])
ok, msg = phase1_composer.validate()
assert ok, f"phase1 validate failed: {msg}"
phase1_path = ROOT / "MIDI" / f"{NAME}-phase1.mid"
phase1_composer.to_midi(str(phase1_path))
write_provenance(str(phase1_path), "ai-generated", f"musicom {NAME}",
                 sources=["methods_db:053 Levy Flight Composition (LFC)",
                          f"style:{GENRE}", "phase:1-raw"],
                 parameters={"phase": "1", "seed": SEED, "key": KEY_NAME,
                             "bpm": BPM, "form": FORM_NAME,
                             "note": "raw generative draft: unquantized chromatic "
                                     "pitches, off-grid onsets, single voice, no harmony"})
print("phase1 midi:", phase1_path, phase1_path.stat().st_size, "bytes")

# Phase 2: full texture, dual-version export
composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=4)
composer.create_matrix(num_voices=len(VOICES), num_sections=len(FORM))
for vname, prog, ch in VOICES:
    composer.add_voice(vname, program=prog, channel=ch)
for sname, nbars in FORM:
    composer.add_section(sname, bars=nbars)
fill(composer, EVENTS)

hz_instruments = {
    "Lead": FIDDLE.humanize_dna,
    "Guitar": STEEL_ACOUSTIC.humanize_dna,
    "Bass": DOUBLE_BASS.humanize_dna,
    "Drums": DRUM_KIT.humanize_dna,
}
perfect_path = ROOT / "MIDI" / f"{NAME}-perfect.mid"
humanized_path = ROOT / "MIDI" / f"{NAME}-humanized.mid"
hz = export_dual(composer, str(perfect_path), str(humanized_path),
                 style=GENRE, seed=HZ_SEED, bpm=BPM, instruments=hz_instruments)

for path, phase, note in ((perfect_path, "perfect", "grid-locked, no jitter"),
                          (humanized_path, "humanized", "style+instrument humanized")):
    write_provenance(str(path), "ai-generated", f"musicom {NAME}",
                     sources=["methods_db:053 Levy Flight Composition (LFC)",
                              f"style:{GENRE}", "phase:2-rules",
                              f"humanize_seed:{HZ_SEED}"],
                     parameters={"phase": phase, "seed": SEED, "key": KEY_NAME,
                                 "bpm": BPM, "form": FORM_NAME,
                                 "humanize": hz, "note": note,
                                 "method": METHOD, "layer": LAYER,
                                 "paradigm": PARADIGM})
print("perfect midi:", perfect_path, perfect_path.stat().st_size, "bytes")
print("humanized midi:", humanized_path, humanized_path.stat().st_size, "bytes")

# ---------------- pitch audit (tiered discipline) ---------------------------
chord_by_bar = {b: CHORD_BY_BAR[b] for b in range(N_BARS)}
lead_tagged = [{"pitch": n["pitch"], "volume": n.get("volume", 78),
                "start_tick": n["start_tick"], "end_tick": n["end_tick"],
                "weight": n.get("weight"), "ornament": n.get("ornament"),
                "resolve_pitch": n.get("resolve_pitch")} for n in lead_notes]
lead_audit = audit_voice(lead_tagged, SCALE_PCS, chord_pcs_by_bar=chord_by_bar,
                         strong_grid=STRONG_GRID["4/4"], bar_ticks=BAR, grid=240)
print("lead pitch audit:", lead_audit.summary())

# audit the accompaniment voices (in-scale/in-chord by construction)
accomp_audits = {}
for vname in ("Guitar", "Bass"):
    evs = EVENTS[vname]
    notes = [{"pitch": e.pitch, "volume": e.volume, "start_tick": e.start_tick,
              "end_tick": e.end_tick} for e in evs]
    accomp_audits[vname] = audit_voice(notes, SCALE_PCS,
                                       chord_pcs_by_bar=chord_by_bar,
                                       strong_grid=STRONG_GRID["4/4"],
                                       bar_ticks=BAR, grid=240)
    print(f"{vname} pitch audit:", accomp_audits[vname].summary())

assert lead_audit.passes, "lead pitch discipline failed"
assert accomp_audits["Guitar"].passes, "guitar pitch discipline failed"
assert accomp_audits["Bass"].passes, "bass pitch discipline failed"

# ---------------- grid viz + summary ----------------------------------------
try:
    write_grid_visualization(composer.matrix,
                             str(ROOT / "Analysis" / "grid_visualization.txt"))
except Exception as exc:
    print("grid viz skipped:", exc)

pitch_audit_report = {
    "Lead": {k: getattr(lead_audit, k) for k in
             ("total", "audible", "strong_ok", "weak_in_scale",
              "tagged_ornaments", "tagged_resolving", "tagged_non_resolving",
              "untagged_out_of_scale", "strong_violations", "collisions")},
}
for vname, ar in accomp_audits.items():
    pitch_audit_report[vname] = {k: getattr(ar, k) for k in
                                 ("total", "audible", "strong_ok", "weak_in_scale",
                                  "tagged_ornaments", "tagged_resolving",
                                  "tagged_non_resolving", "untagged_out_of_scale",
                                  "strong_violations", "collisions")}
pitch_audit_report["Lead"]["passes"] = lead_audit.passes
pitch_audit_report["Guitar"]["passes"] = accomp_audits["Guitar"].passes
pitch_audit_report["Bass"]["passes"] = accomp_audits["Bass"].passes

summary = {
    "project": NAME, "genre": GENRE, "method": METHOD, "layer": LAYER,
    "paradigm": PARADIGM, "key": KEY_NAME, "bpm": BPM, "form": FORM_NAME,
    "bars": N_BARS, "total_ticks": TOTAL_TICKS, "tonic": TONIC,
    "scale_pcs": SCALE_PCS, "chord_sequence": CHORD_SEQ,
    "chords": CHORD_PCS, "voices": [v for v, _, _ in VOICES],
    "humanize_seed": HZ_SEED, "composition_seed": SEED,
    "humanize_profiles": hz,
}
with open(ROOT / "Analysis" / "summary.json", "w") as f:
    json.dump(summary, f, indent=2)
with open(ROOT / "Analysis" / "pitch_audit.json", "w") as f:
    json.dump(pitch_audit_report, f, indent=2)

print("DONE compose")
print("lead notes:", len(lead_notes), "| raw events:", len(raw))
print("lead ornaments:", lead_audit.tagged_ornaments,
      "resolving:", lead_audit.tagged_resolving)
