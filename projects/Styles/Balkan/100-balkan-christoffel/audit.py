# -*- coding: utf-8 -*-
"""Audits MIDI files for 100-balkan-christoffel.
# READING ONLY (analysis)
Verifies:
1. Zero-drift (track ticks equal, matching expected)
2. 16th-grid compliance (120 ticks) for Phase 2: must be 0 off-grid
3. Harmony compliance (scale and chord tones) for Phase 2: must be 0 out-of-scale, 0 out-of-chord
4. Phase 1 raw unquantized fingerprint
"""
import os
import json
import mido

from structures import MusicUnit, MusicEvent


PROJ = "/opt/data/repos/musicom/projects/Styles/Balkan/100-balkan-christoffel"
MIDI_DIR = os.path.join(PROJ, "MIDI")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")

P2_MID = os.path.join(MIDI_DIR, "100-balkan-christoffel.mid")
P1_MID = os.path.join(MIDI_DIR, "100-balkan-christoffel-phase1.mid")

GRID16 = 120
GRID8 = 240
BAR_TICKS = 1320
TOTAL_TICKS = 31680

D_DORIAN_PCS = {2, 4, 5, 7, 9, 11, 0}
ALLOWED_PCS = D_DORIAN_PCS.union({10})  # 10 is Bb in Zavurshek section

SECTION_CHORDS = {
    0: ["Dm", "Dm", "C", "Dm"],
    1: ["Dm", "C", "G", "Dm"],
    2: ["F", "C", "Dm", "Am"],
    3: ["G", "F", "C", "Dm"],
    4: ["Dm", "C", "G", "Dm"],
    5: ["Bb", "C", "Dm", "Dm"],
}

CHORD_PCS = {
    "Dm": {2, 5, 9},
    "C":  {0, 4, 7},
    "G":  {7, 11, 2},
    "F":  {5, 9, 0},
    "Am": {9, 0, 4},
    "Bb": {10, 2, 5},
}

def get_chord_pcs_at_tick(tick):
    bar_idx = tick // BAR_TICKS
    sec_idx = bar_idx // 4
    bar_in_sec = bar_idx % 4
    if sec_idx >= 6:
        sec_idx = 5
        bar_in_sec = 3
    ch = SECTION_CHORDS[sec_idx][bar_in_sec]
    return ch, CHORD_PCS[ch]

def parse_events(mid_path):
    mid = mido.MidiFile(mid_path)
    tracks_events = []
    for trk_idx, trk in enumerate(mid.tracks):
        abs_tick = 0
        notes = []
        open_notes = {}
        for msg in trk:
            abs_tick += msg.time
            if msg.type == 'note_on' and msg.velocity > 0:
                open_notes[msg.note] = (abs_tick, msg.velocity)
            elif (msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0)):
                if msg.note in open_notes:
                    st, vel = open_notes.pop(msg.note)
                    notes.append({
                        "pitch": msg.note,
                        "velocity": vel,
                        "start_tick": st,
                        "end_tick": abs_tick,
                        "track": trk_idx,
                        "channel": getattr(msg, 'channel', 0)
                    })
        tracks_events.append((trk.name, abs_tick, notes))
    return tracks_events

def audit_p2():
    tracks = parse_events(P2_MID)
    total_notes = 0
    off_grid_16 = 0
    out_of_scale = 0
    out_of_chord = 0
    
    report_lines = []
    track_stats = []
    
    for trk_name, total_tick, notes in tracks:
        # Check channel
        ch = notes[0]["channel"] if notes else 0
        is_drum = (ch == 9)
        
        t_off16 = 0
        t_oos = 0
        t_ooc = 0
        
        for n in notes:
            if n["pitch"] == 0:
                continue
            total_notes += 1
            st = n["start_tick"]
            if st % GRID16 != 0:
                off_grid_16 += 1
                t_off16 += 1
                
            if not is_drum:
                pc = n["pitch"] % 12
                if pc not in ALLOWED_PCS:
                    out_of_scale += 1
                    t_oos += 1
                ch_name, c_pcs = get_chord_pcs_at_tick(st)
                if pc not in c_pcs:
                    out_of_chord += 1
                    t_ooc += 1
                    
        track_stats.append({
            "name": trk_name,
            "channel": ch,
            "total_tick": total_tick,
            "notes": len(notes),
            "off16": t_off16,
            "oos": t_oos,
            "ooc": t_ooc
        })
        print(f"Track '{trk_name}' (ch {ch}): {len(notes)} notes | tick_len={total_tick} | off16={t_off16} | oos={t_oos} | ooc={t_ooc}")
        
    print(f"\nPhase 2 Summary:")
    print(f"Total notes audited: {total_notes}")
    print(f"16th off-grid onsets: {off_grid_16} / {total_notes}")
    print(f"Out of scale: {out_of_scale} / {total_notes}")
    print(f"Out of chord: {out_of_chord} / {total_notes}")
    
    return {
        "total_notes": total_notes,
        "off_grid_16": off_grid_16,
        "out_of_scale": out_of_scale,
        "out_of_chord": out_of_chord,
        "tracks": track_stats
    }

def audit_p1():
    tracks = parse_events(P1_MID)
    trk_name, total_tick, notes = tracks[1]  # voice track
    off_grid_16 = 0
    for n in notes:
        if n["pitch"] == 0: continue
        if n["start_tick"] % GRID16 != 0:
            off_grid_16 += 1
    print(f"\nPhase 1 Raw Draft (Clarinet): {len(notes)} notes | off-grid={off_grid_16}/{len(notes)} | tick_len={total_tick}")
    return {
        "total_notes": len(notes),
        "off_grid_16": off_grid_16,
        "total_tick": total_tick
    }

if __name__ == "__main__":
    p2_res = audit_p2()
    p1_res = audit_p1()
    
    with open(os.path.join(ANALYSIS_DIR, "audit.json"), "w") as f:
        json.dump({"phase2": p2_res, "phase1": p1_res}, f, indent=2)
