# -*- coding: utf-8 -*-
"""Verify 205-amapiano-study MIDI: zero-drift, grid, chord-tone, density.

Chord-tone rule is two-tier:
  - harmonic voices (Rhodes/LogDrum/Sub): strict 7th-chord tones.
  - melodic voices (Lead/Guitar): extended chord tones (7th + 9th/b9 color).
Scale = A harmonic minor (A B C D E F G G#) for ALL voices.
"""
import json
import os
import mido
from collections import defaultdict

PROJ = "/opt/data/repos/musicom/projects/Styles/African/205-amapiano-study"
MID = os.path.join(PROJ, "MIDI", "205-amapiano-study.mid")

TPB = 480
BAR = 1920
SIXTEENTH = 120
CHORDS = ["Am7", "Fmaj7", "Dm7", "E7"]
SCALE_PCS = {9, 11, 0, 2, 4, 5, 7, 8}     # A harmonic minor
# 7th-chord tones (harmonic voices)
CHORD_PCS = {
    "Am7":   {9, 0, 4, 7},     # A C E G
    "Fmaj7": {5, 9, 0, 4},     # F A C E
    "Dm7":   {2, 5, 9, 0},     # D F A C
    "E7":    {4, 8, 11, 2},    # E G# B D
}
# extended (7th + 9th/b9) chord tones (melodic voices)
EXT_PCS = {
    "Am7":   {9, 0, 4, 7, 11},     # + B (9)
    "Fmaj7": {5, 9, 0, 4, 7},      # + G (9)
    "Dm7":   {2, 5, 9, 0, 4},      # + E (9)
    "E7":    {4, 8, 11, 2, 5},     # + F (b9)
}
# program -> voice class
MELODIC_PROGS = {108, 27}           # Kalimba, Guitar

mid = mido.MidiFile(MID)
tracks = [t for t in mid.tracks if any(m.type == "program_change" for m in t)]
print("voice tracks:", len(tracks))

def track_len(tr):
    t = 0
    mx = 0
    for m in tr:
        t += m.time
        if m.type in ("note_on", "note_off"):
            mx = max(mx, t)
    return mx

lengths = [track_len(t) for t in tracks]
print("track end ticks:", lengths, "zero_drift:", len(set(lengths)) == 1)

offgrid = 0
scale_viol = 0
chord_viol = 0
total_pitched = 0
per_voice = defaultdict(int)
for i, tr in enumerate(tracks):
    prog = [m for m in tr if m.type == "program_change"][0]
    t = 0
    for m in tr:
        t += m.time
        if m.type != "note_on" or m.velocity == 0:
            continue
        per_voice[prog.program] += 1
        if prog.channel == 9:
            continue
        total_pitched += 1
        note = m.note
        if t % SIXTEENTH != 0:
            offgrid += 1
        if note % 12 not in SCALE_PCS:
            scale_viol += 1
        chord = CHORDS[(t // BAR) % 4]
        allowed = EXT_PCS if prog.program in MELODIC_PROGS else CHORD_PCS
        if note % 12 not in allowed[chord]:
            chord_viol += 1

print("total pitched notes:", total_pitched)
print("offgrid onsets:", offgrid)
print("scale violations (A harmonic minor):", scale_viol)
print("chord-tone violations:", chord_viol)
print("notes per program (0=drums ch9):", dict(per_voice))

result = {
    "zero_drift": len(set(lengths)) == 1,
    "track_lengths": lengths,
    "n_voice_tracks": len(tracks),
    "total_pitched": total_pitched,
    "offgrid": offgrid,
    "scale_violations": scale_viol,
    "chord_tone_violations": chord_viol,
    "notes_per_program": dict(per_voice),
}
with open(os.path.join(PROJ, "Analysis", "verify.json"), "w") as f:
    json.dump(result, f, indent=2)
print("wrote Analysis/verify.json")
