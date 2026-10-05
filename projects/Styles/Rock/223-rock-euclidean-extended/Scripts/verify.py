# -*- coding: utf-8 -*-
# READING ONLY (analysis) — mido used to audit, never author.
import mido, os, json

PROJ = "/opt/data/projects/Styles/Rock/223-rock-euclidean-extended"
P2 = os.path.join(PROJ, "MIDI", "223-rock-euclidean-extended.mid")
P1 = os.path.join(PROJ, "MIDI", "223-rock-euclidean-extended-phase1.mid")

KEY_ROOT = 64
AEOLIAN = [0, 2, 3, 5, 7, 8, 10]
KEY_PCS = {(KEY_ROOT + i) % 12 for i in AEOLIAN}
BAR = 1920
N_BARS = 32
PROG_DEG = ([0,0,5,6] + [0,5,2,6] + [5,2,6,0] + [5,6,0,0] +
            [3,5,2,6] + [5,6,0,0] + [0,2,6,5] + [0,0,5,0])


def degree_triad_pcs(d):
    def dn(x):
        return KEY_ROOT + (x // 7) * 12 + AEOLIAN[x % 7]
    return {dn(d) % 12, dn(d + 2) % 12, dn(d + 4) % 12}


def audit(path, check_key=True):
    print("=== AUDIT", os.path.basename(path), "===")
    sz = os.path.getsize(path)
    print("size:", sz, "bytes  (>40:", sz > 40, ")")
    mid = mido.MidiFile(path)
    print("type", mid.type, "tpb", mid.ticks_per_beat, "ntracks", len(mid.tracks))
    lengths = {}
    for i, t in enumerate(mid.tracks):
        lengths[i] = sum(m.time for m in t)
    voice_lens = [lengths[i] for i in range(1, len(mid.tracks))]
    print("track lengths:", lengths)
    print("zero-drift:", len(set(voice_lens)) == 1, "->", set(voice_lens),
          "| N voice tracks:", len(voice_lens))

    off_grid = scale_viol = chord_viol = pitched = 0
    for i, t in enumerate(mid.tracks):
        if i == 0:
            continue
        is_ch9 = any(m.type == 'program_change' and m.channel == 9 for m in t)
        abs_t = 0
        for m in t:
            abs_t += m.time
            if m.type == 'note_on' and m.velocity > 0:
                if is_ch9:
                    continue
                pitched += 1
                if not (abs_t % 120 == 0 or abs_t % 240 == 0):
                    off_grid += 1
                if check_key:
                    pc = m.note % 12
                    if pc not in KEY_PCS:
                        scale_viol += 1
                    bar = min(abs_t // BAR, N_BARS - 1)
                    if pc not in degree_triad_pcs(PROG_DEG[bar]):
                        chord_viol += 1
    print(f"pitched onsets: {pitched}")
    print(f"OFF-GRID: {off_grid}  (must be 0)")
    print(f"SCALE VIOLATIONS: {scale_viol}  (must be 0)")
    print(f"CHORD VIOLATIONS: {chord_viol}  (must be 0)")
    return dict(size=sz, nvoice=len(voice_lens), lengths=voice_lens,
                off_grid=off_grid, scale_viol=scale_viol, chord_viol=chord_viol,
                pitched=pitched)


print("===== PHASE 2 (rules) =====")
r2 = audit(P2)
print()
print("===== PHASE 1 (raw) =====")
r1 = audit(P1, check_key=False)
json.dump(dict(phase2=r2, phase1=r1),
          open(os.path.join(PROJ, "Analysis", "rework_verify.json"), "w"), indent=2)
print("\nsaved Analysis/rework_verify.json")
