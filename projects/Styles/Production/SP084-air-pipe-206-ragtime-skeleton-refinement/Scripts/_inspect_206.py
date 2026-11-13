# -*- coding: utf-8 -*-
import mido

P = "projects/Styles/Ragtime/206-ragtime-skeleton-refinement/MIDI/206-ragtime-skeleton-refinement.mid"
mf = mido.MidiFile(P)
print("TPB", mf.ticks_per_beat, "length", round(mf.length, 2), "s")
tempo = None
for tr in mf.tracks:
    for m in tr:
        if m.type == "set_tempo":
            tempo = round(60000000.0 / m.tempo, 2)
print("BPM", tempo)

for i, tr in enumerate(mf.tracks):
    chans = set()
    progs = []
    notes = []
    t = 0
    for m in tr:
        t += m.time
        if m.type == "program_change":
            progs.append(m.program)
        if m.type == "note_on" and m.velocity > 0:
            chans.add(m.channel)
            notes.append((m.note, m.velocity))
    if notes or progs:
        rng = (min(n[0] for n in notes), max(n[0] for n in notes)) if notes else None
        print(f"track{i}: chans={sorted(chans)} progs={progs} nnotes={len(notes)} end_tick={t} pitch_range={rng}")