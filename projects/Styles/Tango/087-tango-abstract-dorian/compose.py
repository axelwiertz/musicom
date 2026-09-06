# -*- coding: utf-8 -*-
"""087-tango-abstract-dorian — nightly autonomous composition (2026-09-05).

Style: Tango / Method: ABS-002 Subset Walker (ABSTRACT layer) + ABS-001
tension-curve steering + method-006 cadence close (rules layer).

Two-phase architecture:
  Phase 1 (raw): single alto-sax voice. Each bar's pitch stream samples the
    CURRENT WALKED SUBSET pc field; events land on fractional OFF-GRID ticks
    (raw generative fingerprint). No harmony, no bass, no drums.
  Phase 2 (musicom rules post-process): grid-snap FIRST (16th), then octave-
    aware chord-tone quantization per bar (snapped-onset bar), voice-leading
    cap, full texture (alto-sax lead, violin counterline, cello pad, piano
    marcato comp, double-bass tango roots, drum kit). Cadence close: final
    bar forced to tonic VII (C major).

Engine only: structures + workflows.unitmatrix_composer + rules.subset_network.
mido used READ-ONLY for audits. Instruments from the importable registry.
"""
import json
import os
import random
import subprocess
import sys
from pathlib import Path

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.musicom_workflow import produce

# ---- instrument registry (source of truth, NOT pip-installed) -------------
INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import (  # noqa: E402
    VIOLIN, CELLO, PIANO, DOUBLE_BASS, DRUM_KIT, MARIMBA, SAXOPHONE
)
REPO = "/opt/data/repos/musicom"
if REPO not in sys.path:
    sys.path.insert(0, REPO)
from rules.subset_network import PatternNetwork, standard_patterns  # noqa: E402
from workflows.provenance import write_provenance  # noqa: E402
from visualization.grid import write_grid_visualization  # noqa: E402

# ---------------- concept ---------------------------------------------------
GENRE = "Tango"
NAME = "087-tango-abstract-dorian"
ROOT = Path(f"/opt/data/projects/Styles/{GENRE}/{NAME}")
for sub in ("MIDI", "Audio", "Analysis"):
    (ROOT / sub).mkdir(parents=True, exist_ok=True)

# D dorian (dark tango lean: minor third + natural 6)
TONIC = 2                       # D
KEY_NAME = "D dorian"
DORIAN_OFFS = [0, 2, 3, 5, 7, 9, 10]     # rel to D=0
SCALE_PCS = set((TONIC + o) % 12 for o in DORIAN_OFFS)
BPM = 112
TPB = 480
BAR = 1920
EIGHTH = 240
SIXTEENTH = 120
BEAT = BAR // 4                 # 480 ticks per beat
FORM = [("Intro", 4), ("TangoA", 4), ("TangoB", 4), ("Lift", 4),
        ("TangoA2", 4), ("Outro", 4)]
N_BARS = sum(b for _, b in FORM)
SECTION_TICKS = {}
_tick = 0
for s, b in FORM:
    SECTION_TICKS[s] = (b * BAR, _tick)
    _tick += b * BAR
TOTAL_TICKS = _tick
SEED = 20260905
rng = random.Random(SEED)

# ---------------- abstract layer: subset walk ------------------------------
def chord_pcs(deg, seventh=False):
    idx = [deg, (deg + 2) % 7, (deg + 4) % 7]
    if seventh:
        idx.append((deg + 6) % 7)
    rels = [DORIAN_OFFS[i] for i in idx]
    return frozenset((TONIC + r) % 12 for r in rels)

def find_id(pcs):
    for p in standard_patterns():
        if p.subset == pcs:
            return p.id
    return None

DEG_NAMES = ["i", "ii", "III", "IV", "v", "vi", "VII"]
DEG_LABELS = ["Dm", "Edim", "F", "Gm", "Am", "Bdim", "C"]
ANCHOR_DEG = {}          # pid -> degree index (0..6)
anchor_ids = []
for d in range(7):
    pid = find_id(chord_pcs(d))
    if pid:
        ANCHOR_DEG[pid] = d
        anchor_ids.append(pid)
for d in (0, 1, 2, 3, 4, 6):
    pid = find_id(chord_pcs(d, seventh=True))
    if pid:
        ANCHOR_DEG[pid] = d
        anchor_ids.append(pid)
anchor_ids = sorted(set(anchor_ids))
net_lib = PatternNetwork(standard_patterns())
net = PatternNetwork([net_lib.patterns[i] for i in anchor_ids])

HOME = "maj0"          # VII = C major: dorian's tonic-ish resolution chord
start_pid = HOME

T_CURVE = [2.0] * 24
for b in range(24):
    if 4 <= b < 8:    T_CURVE[b] = 2.0 + 0.3 * (b - 4)
    elif 8 <= b < 12: T_CURVE[b] = 2.6
    elif 12 <= b < 16:T_CURVE[b] = 3.0 + 0.8 * (b - 12)
    elif 16 <= b < 20:T_CURVE[b] = 3.0 - 0.4 * (b - 16)
walk = net.walk(start_pid, N_BARS, rng=rng, tension_curve=T_CURVE, home=HOME)
walk[-1] = HOME        # method-006 cadence close

bar_pid = walk
bar_deg = [ANCHOR_DEG[pid] for pid in walk]

def pc_to_pitch(pc, floor):
    for p in range(floor, floor + 15):
        if p % 12 in SCALE_PCS and p % 12 == pc:
            return p
    return floor

def subset_tones(pid, floor=48):
    pcs = sorted(net_lib.patterns[pid].subset)
    tones = sorted(pc_to_pitch(pc, floor) for pc in pcs)
    return tones

def degree_root_pitch(deg, floor):
    rel = DORIAN_OFFS[deg]
    pc = (TONIC + rel) % 12
    return pc_to_pitch(pc, floor)

# register floors (avoid collisions): bass ~38, cello ~48, piano ~60,
# violin ~67, sax ~60
CHORD_BY_BAR = [subset_tones(pid, 48) for pid in bar_pid]
CHORD_BASS_BY_BAR = [subset_tones(pid, 38) for pid in bar_pid]

# ============================================================================
# PHASE 1 — RAW GENERATIVE DRAFT (single voice, off-grid, no harmony)
# ============================================================================
def nearest_scale_pitch(pitch, floor=52, ceil=88):
    """Snap a raw midi float to nearest D-dorian scale pitch in [floor,ceil]."""
    best, bd = None, 1e9
    for p in range(floor, ceil + 1):
        if p % 12 in SCALE_PCS:
            d = abs(p - pitch)
            if d < bd:
                best, bd = p, d
    return best

phase1_events = []
tick = 0
bar_len = BAR
note_count = 0
for b in range(N_BARS):
    pid = bar_pid[b]
    pcs = sorted(net_lib.patterns[pid].subset)
    # 10-14 events per bar, fractional slots (off-grid fingerprint)
    n_ev = rng.randint(10, 14)
    for k in range(n_ev):
        # raw fractional position within the bar
        frac = (k + rng.uniform(0.0, 0.92)) / n_ev
        st = tick + int(frac * bar_len)
        pc = rng.choice(pcs)
        octv = rng.choice([0, 1, 2])
        raw_pitch = 60 + octv * 12 + ((pc - 2) % 12)   # D-space rough
        # map into D-dorian window 55..88
        pitch = nearest_scale_pitch(raw_pitch, 55, 88)
        dur = int(rng.uniform(0.3, 0.9) * EIGHTH)
        ev = MusicEvent(pitch=pitch, volume=rng.randint(70, 96),
                        start_tick=st, end_tick=min(st + dur, (b + 1) * BAR - 1))
        phase1_events.append(ev)
        note_count += 1
    tick += bar_len

def unit_from(events, sec_len):
    u = MusicUnit()
    for e in events:
        if e.end_tick > e.start_tick:
            u.add_event(e)
    # zero-drift landmark
    last = max((e.end_tick for e in u.events), default=0)
    if last < sec_len:
        u.add_event(MusicEvent(0, 0, sec_len, sec_len))
    elif last > sec_len:
        u.add_event(MusicEvent(0, 0, sec_len, sec_len))
    return u

# Phase-1 single section = whole piece (one 24-bar section) for simplicity of
# the raw draft, OR per-section units. Simpler: split events by section.
def split_by_section(events):
    out = []
    for sname, (slen, soff) in SECTION_TICKS.items():
        evs = [e for e in events if soff <= e.start_tick < soff + slen]
        # clip to section
        for e in evs:
            e.start_tick = e.start_tick - soff
            e.end_tick = max(e.start_tick + 1, e.end_tick - soff)
            if e.end_tick > slen:
                e.end_tick = slen
        out.append((sname, evs))
    return out

p1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=4)
p1.create_matrix(num_voices=1, num_sections=len(FORM))
p1.add_voice("RawDraft", program=SAXOPHONE.midi_program, channel=0)
for sname, (slen, soff) in SECTION_TICKS.items():
    p1.add_section(sname, bars=dict(FORM)[sname])
sections_by_bar = []
b_idx = 0
for sname, nbars in FORM:
    slen = nbars * BAR
    evs = []
    for b in range(b_idx, b_idx + nbars):
        evs += [e for e in phase1_events
                if b * BAR <= e.start_tick < (b + 1) * BAR]
    b_idx += nbars
    # make section-relative
    off = SECTION_TICKS[sname][1]
    for e in evs:
        e.start_tick -= off
        e.end_tick -= off
    p1.fill_voice_section("RawDraft", sname, unit_from(evs, slen))
ok1, msg1 = p1.validate()
assert ok1, f"phase1 validate failed: {msg1}"
midi1 = ROOT / "MIDI" / f"{NAME}-phase1.mid"
p1.to_midi(str(midi1))
write_provenance(str(midi1), "ai-generated",
                 f"musicom nightly {NAME}",
                 sources=["methods_db:ABS-002 subset walk", f"style:{GENRE}",
                          "phase:1 raw draft"],
                 parameters={"phase": 1, "seed": SEED, "key": KEY_NAME,
                             "bpm": BPM, "form": FORM,
                             "walk": ",".join(bar_pid)})
print("phase1 midi:", midi1, midi1.stat().st_size, "bytes,", note_count, "notes")

# ============================================================================
# PHASE 2 — RULES POST-PROCESS (grid lock + chord quant + texture)
# ============================================================================
def snap16(t):
    return int(round(t / SIXTEENTH) * SIXTEENTH)

# per-voice event builders ------------------------------------------------
def sax_lead_events():
    evs = []
    for b in range(N_BARS):
        pid = bar_pid[b]
        tones = CHORD_BY_BAR[b]            # subset realized ~48-72
        lead_pool = [t + 12 for t in tones if t + 12 <= 88]  # ~60-84 window
        if not lead_pool:
            lead_pool = [t for t in tones if t <= 84]
        n = rng.choice([6, 8])             # tango melodic density: 8ths/16ths
        # rhythm: start on a 16th slot in bar, march by 8th mostly, some 16ths
        pos = b * BAR + SIXTEENTH * rng.choice([0, 2, 4])
        while pos < (b + 1) * BAR:
            pc = rng.choice(pcs_of(pid))
            # choose a lead-pool tone with that pc
            cands = [p for p in lead_pool if p % 12 == pc]
            pitch = rng.choice(cands) if cands else rng.choice(lead_pool)
            step = EIGHTH if rng.random() < 0.7 else SIXTEENTH
            dur = int(step * rng.uniform(0.7, 0.95))
            evs.append(MusicEvent(pitch=pitch, volume=rng.randint(78, 96),
                                  start_tick=pos,
                                  end_tick=min(pos + dur, (b + 1) * BAR)))
            pos += step
    return evs

def pcs_of(pid):
    return sorted(net_lib.patterns[pid].subset)

def violin_counter_events():
    evs = []
    for b in range(N_BARS):
        tones = CHORD_BY_BAR[b]
        pool = [t + 12 for t in tones if t + 24 <= 96] or [t + 12 for t in tones]
        # answering 8ths on beats 2 & 4 + upbeat pickups, register +12
        bar0 = b * BAR
        for beat in (1, 3):
            st = bar0 + beat * BEAT
            pc = rng.choice(pcs_of(bar_pid[b]))
            cands = [p for p in pool if p % 12 == pc] or pool
            pitch = rng.choice(cands)
            evs.append(MusicEvent(pitch=pitch, volume=72,
                                  start_tick=st, end_tick=st + EIGHTH * 1))
            # second 8th of the beat (syncopation answer)
            st2 = st + EIGHTH
            if st2 < (b + 1) * BAR:
                pc2 = rng.choice(pcs_of(bar_pid[b]))
                cands2 = [p for p in pool if p % 12 == pc2] or pool
                evs.append(MusicEvent(pitch=rng.choice(cands2), volume=66,
                                      start_tick=st2,
                                      end_tick=st2 + EIGHTH * 1))
    return evs

def cello_pad_events():
    evs = []
    for b in range(N_BARS):
        tones = CHORD_BY_BAR[b]            # root position ~48
        # pick root + fifth (or 3rd) sustained whole-bar; marcato re-attack
        root = tones[0]
        fifth_or_third = tones[2] if len(tones) > 2 else tones[1]
        st = b * BAR
        evs.append(MusicEvent(pitch=root, volume=58,
                              start_tick=st, end_tick=st + BAR))
        evs.append(MusicEvent(pitch=fifth_or_third, volume=52,
                              start_tick=st, end_tick=st + BAR))
    return evs

def piano_comp_events():
    evs = []
    for b in range(N_BARS):
        tones = CHORD_BY_BAR[b]
        pool = [t + 12 for t in tones if t + 12 <= 84] or [t for t in tones]
        bar0 = b * BAR
        # tango marcato: strong 8th-note hits on beat 1 & 3 (staccato)
        for beat in (0, 2):
            st = bar0 + beat * BEAT
            for p in pool[:3]:
                evs.append(MusicEvent(pitch=p, volume=64,
                                      start_tick=st,
                                      end_tick=st + SIXTEENTH * 1))
    return evs

def bass_events():
    evs = []
    for b in range(N_BARS):
        pid = bar_pid[b]
        deg = bar_deg[b]
        root = CHORD_BASS_BY_BAR[b][0]
        bar0 = b * BAR
        sname = section_of_bar(b)
        # tango bass: root on 1, fifth 8th push on beat 4 into next bar
        evs.append(MusicEvent(pitch=root, volume=92,
                              start_tick=bar0, end_tick=bar0 + 900))
        # pickup on beat 4 (offbeat 8th) if not outro quiet
        if not (sname == "Outro"):
            st = bar0 + 3 * BEAT + EIGHTH
            if st < bar0 + BAR - 1:
                evs.append(MusicEvent(pitch=root, volume=84,
                                      start_tick=st,
                                      end_tick=min(st + EIGHTH * 2,
                                                   (b + 1) * BAR)))
    return evs

def section_of_bar(b):
    acc = 0
    for sname, nbars in FORM:
        if acc <= b < acc + nbars:
            return sname
        acc += nbars
    return FORM[-1][0]

def drums_events():
    evs = []
    for b in range(N_BARS):
        sname = section_of_bar(b)
        bar0 = b * BAR
        dense = sname in ("TangoA", "TangoB", "Lift", "TangoA2")
        # kick beats 1 & 3 (+ lift: every beat)
        k_ons = [0, 2] if not dense else ([0, 1, 2, 3] if sname == "Lift" else [0, 2])
        for beat in k_ons:
            st = bar0 + beat * BEAT
            evs.append(MusicEvent(pitch=36, volume=100,
                                  start_tick=st, end_tick=st + SIXTEENTH * 2))
        # snare: backbeat 2 & 4 (tango habanera-ish)
        for beat in (1, 3):
            st = bar0 + beat * BEAT
            evs.append(MusicEvent(pitch=38, volume=92 if dense else 70,
                                  start_tick=st, end_tick=st + SIXTEENTH * 2))
        # closed hat 8ths + 16ths in dense
        sub = SIXTEENTH if sname in ("Lift", "TangoB") else EIGHTH
        st = bar0
        while st < (b + 1) * BAR - sub:
            evs.append(MusicEvent(pitch=42, volume=56,
                                  start_tick=st, end_tick=st + sub // 2))
            st += sub
        if dense and sname != "Lift":
            # accent on the "and" of 4 (habanera pulse)
            st = bar0 + 3 * BEAT + EIGHTH
            evs.append(MusicEvent(pitch=42, volume=80,
                                  start_tick=st, end_tick=st + SIXTEENTH))
    return evs

# --- build phase-2 voices (grid + chord quantize baked in at construction) --
voice_events = {
    "LeadSax": sax_lead_events(),
    "Violin": violin_counter_events(),
    "Cello": cello_pad_events(),
    "Piano": piano_comp_events(),
    "Bass": bass_events(),
    "Drums": drums_events(),
}

# chord-quantize & grid-snap every pitched event (grid rule: 16th)
def grid_quantize_pitched(events, get_chord_tones):
    out = []
    for e in events:
        if e.pitch == 0:
            out.append(e)
            continue
        st = snap16(e.start_tick)
        if st < 0:
            st = 0
        # chord tones of the bar the SNAPPED onset lands in
        bar = min(st // BAR, N_BARS - 1)
        pool = get_chord_tones(bar)
        best = min(pool, key=lambda p: abs(p - e.pitch))
        # octave variants: nearest across +-12
        for cand in (best - 12, best, best + 12):
            if abs(cand - e.pitch) < abs(best - e.pitch):
                best = cand
        end = max(st + 1, e.end_tick)
        out.append(MusicEvent(pitch=best, volume=e.volume,
                              start_tick=st, end_tick=end))
    return out

lead_pool_by_bar = {b: ([t + 12 for t in CHORD_BY_BAR[b] if t + 12 <= 88]
                        or [t for t in CHORD_BY_BAR[b] if t <= 84])
                    for b in range(N_BARS)}
violin_pool_by_bar = {b: ([t + 12 for t in CHORD_BY_BAR[b] if t + 24 <= 96]
                          or [t + 12 for t in CHORD_BY_BAR[b]])
                      for b in range(N_BARS)}
viola_pool_by_bar = {b: [t for t in CHORD_BY_BAR[b]] for b in range(N_BARS)}
piano_pool_by_bar = {b: ([t + 12 for t in CHORD_BY_BAR[b] if t + 12 <= 84]
                         or [t for t in CHORD_BY_BAR[b]]) for b in range(N_BARS)}
bass_pool_by_bar = {b: CHORD_BASS_BY_BAR[b] for b in range(N_BARS)}

lead_q = grid_quantize_pitched(sax_lead_events(),
                               lambda b: lead_pool_by_bar[b])
violin_q = grid_quantize_pitched(violin_counter_events(),
                                 lambda b: violin_pool_by_bar[b])
cello_q = grid_quantize_pitched(cello_pad_events(),
                                lambda b: viola_pool_by_bar[b])
piano_q = grid_quantize_pitched(piano_comp_events(),
                                lambda b: piano_pool_by_bar[b])
bass_q = grid_quantize_pitched(bass_events(),
                               lambda b: bass_pool_by_bar[b])

# voice-leading: cap leaps on the lead (<= 10 semitones between onsets
# <= 1 bar apart) toward nearest chord tone of the destination bar
def cap_leaps(events, max_leap=10):
    evs = sorted([e for e in events if e.pitch], key=lambda e: e.start_tick)
    for i in range(1, len(evs)):
        prev = evs[i - 1]
        cur = evs[i]
        if cur.start_tick - prev.start_tick <= BAR and abs(cur.pitch - prev.pitch) > max_leap:
            bar = min(cur.start_tick // BAR, N_BARS - 1)
            pool = lead_pool_by_bar[bar]
            # step toward prev pitch within cap
            target = prev.pitch + max_leap if cur.pitch > prev.pitch else prev.pitch - max_leap
            best = min(pool, key=lambda p: (abs(p - target), abs(p - cur.pitch)))
            cur.pitch = best
    return evs

lead_q = cap_leaps(lead_q)
violin_q = cap_leaps(violin_q)

# dedupe identical (start, pitch) overlaps per voice (collision from snap)
def dedupe(events):
    seen = {}
    out = []
    for e in events:
        if e.pitch == 0:
            out.append(e)
            continue
        key = (e.start_tick, e.pitch)
        if key in seen:
            # merge: extend duration
            seen[key].end_tick = max(seen[key].end_tick, e.end_tick)
        else:
            seen[key] = e
            out.append(e)
    out.sort(key=lambda e: (e.start_tick, e.pitch))
    return out

lead_q = dedupe(lead_q)
violin_q = dedupe(violin_q)
cello_q = dedupe(cello_q)
piano_q = dedupe(piano_q)
bass_q = dedupe(bass_q)

# --- assemble phase 2 -------------------------------------------------------
VOICES = [
    ("LeadSax", SAXOPHONE.midi_program, 0),
    ("Violin", VIOLIN.midi_program, 1),
    ("Cello", CELLO.midi_program, 2),
    ("Piano", PIANO.midi_program, 3),
    ("Bass", DOUBLE_BASS.midi_program, 4),
    ("Drums", 0, 9),
]
events_by_voice = {
    "LeadSax": lead_q, "Violin": violin_q, "Cello": cello_q,
    "Piano": piano_q, "Bass": bass_q, "Drums": drums_events(),
}
# drums built directly on grid (audit will confirm)
drums_q = drums_events()

p2 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=4)
p2.create_matrix(num_voices=len(VOICES), num_sections=len(FORM))
for vname, prog, ch in VOICES:
    p2.add_voice(vname, program=prog, channel=ch)
for sname, nbars in FORM:
    p2.add_section(sname, bars=nbars)

for vname, prog, ch in VOICES:
    evs = events_by_voice[vname]
    for sname, (slen, soff) in SECTION_TICKS.items():
        seg = [e for e in evs if soff <= e.start_tick < soff + slen]
        for e in seg:
            e.start_tick -= soff
            e.end_tick -= soff
            if e.end_tick > slen:
                e.end_tick = slen
        p2.fill_voice_section(vname, sname, unit_from(seg, slen))

ok2, msg2 = p2.validate()
assert ok2, f"phase2 validate failed: {msg2}"
midi2 = ROOT / "MIDI" / f"{NAME}.mid"
p2.to_midi(str(midi2))
write_provenance(str(midi2), "ai-generated",
                 f"musicom nightly {NAME}",
                 sources=["methods_db:ABS-002 subset walk", f"style:{GENRE}",
                          "phase:2 rules"],
                 parameters={"phase": 2, "seed": SEED, "key": KEY_NAME,
                             "bpm": BPM, "form": FORM,
                             "walk": ",".join(bar_pid),
                             "texture": [v for v, _, _ in VOICES]})
print("phase2 midi:", midi2, midi2.stat().st_size, "bytes")

# ============================================================================
# RENDER — SP-001 via workflow adapter, then silence/RMS stats
# ============================================================================
for phase_midi, tag in ((midi1, "phase1"), (midi2, "phase2")):
    r = produce(str(phase_midi), method="SP-001")
    for p in (r.wav_path, r.ogg_path):
        write_provenance(p, "ai-generated", f"musicom nightly {NAME} produce SP-001",
                         sources=["SP-001 fluidsynth", f"087 {tag} midi"],
                         parameters={"render": "SP-001", "phase": tag})
    print(f"{tag} wav:", r.wav_path, os.path.getsize(r.wav_path),
          "ogg:", os.path.getsize(r.ogg_path))
    import wave
    import numpy as np
    wf = wave.open(r.wav_path, "rb")
    sr = wf.getframerate()
    ch = wf.getnchannels()
    raw = np.frombuffer(wf.readframes(wf.getnframes()),
                        dtype=np.int16).astype(np.float32) / 32768.0
    wf.close()
    if ch > 1:
        mono = raw.reshape(-1, ch).mean(axis=1)
    else:
        mono = raw
    dur = len(mono) / sr
    sil = float(np.sum(np.abs(mono) < 0.001) / len(mono))
    secs = [float(np.sqrt(np.mean(mono[int(s * sr):int((s + 1) * sr)] ** 2)))
            for s in range(int(dur))]
    silent = sum(1 for v in secs if v < 0.001)
    stat = {"duration_s": round(dur, 2), "silence_ratio": round(sil, 4),
            "silent_secs": silent, "total_secs": len(secs),
            "peak": round(float(np.max(np.abs(mono))), 4),
            "rms_mean": round(float(np.sqrt(np.mean(mono ** 2))), 5)}
    print(f"{tag} stats:", json.dumps(stat))

# grid visualization + analysis JSON
try:
    write_grid_visualization(p2.matrix, str(ROOT / "Analysis" / "grid_visualization.txt"))
except Exception as exc:
    print("grid viz skipped:", exc)

summary = {
    "project": NAME, "genre": GENRE, "key": KEY_NAME, "bpm": BPM,
    "form": [s for s, _ in FORM], "bars": N_BARS,
    "method": "ABS-002 subset walk (+ABS-001 tension, +006 cadence close)",
    "layer": "abstract",
    "seed": SEED,
    "walk_pids": bar_pid,
    "walk_degrees": [DEG_NAMES[d] for d in bar_deg],
    "voices": [v for v, _, _ in VOICES],
    "phase1_notes": note_count,
}
with open(ROOT / "Analysis" / "summary.json", "w") as f:
    json.dump(summary, f, indent=2)
print("DONE")
