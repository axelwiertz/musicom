import mido

mid = mido.MidiFile('/opt/data/repos/musicom/projects/Styles/Balfolk/005-balfolk-production/midi/native_render.mid')
print("Type:", mid.type)
print("Ticks per beat:", mid.ticks_per_beat)
print("Tracks:", len(mid.tracks))
for i, trk in enumerate(mid.tracks):
    notes = [m for m in trk if m.type == 'note_on' and m.velocity > 0]
    programs = [m.program for m in trk if m.type == 'program_change']
    print(f"Track {i}: {trk.name} | {len(trk)} msgs | {len(notes)} note-ons | programs: {programs}")
    if notes:
        pitches = [n.note for n in notes]
        print(f"   pitch range: {min(pitches)} - {max(pitches)} | first 5: {pitches[:5]}")
print("Total length (sec):", mid.length)
