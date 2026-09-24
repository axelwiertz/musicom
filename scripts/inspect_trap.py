import mido

mid = mido.MidiFile('/opt/data/repos/musicom/projects/Styles/Trap/001-trap-half-time/MIDI/trap-half-time.mid')
print("Type:", mid.type)
print("Ticks per beat:", mid.ticks_per_beat)
print("Tracks:", len(mid.tracks))
for i, trk in enumerate(mid.tracks):
    notes = [m for m in trk if m.type == 'note_on' and m.velocity > 0]
    programs = [m.program for m in trk if m.type == 'program_change']
    print(f"Track {i}: {trk.name} | {len(trk)} msgs | {len(notes)} note-ons | programs: {programs}")
    if notes:
        pitches = [n.note for n in notes]
        print(f"   pitch range: {min(pitches)} - {max(pitches)} | count: {len(notes)}")
print("Total length (sec):", mid.length)
