
import pretty_midi
import subprocess
import os

midi_path = "/opt/data/projects/012-native-balfolk-render/midi/native_render.mid"
wav_path = "/opt/data/projects/012-native-balfolk-render/audio/native_render.wav"
ogg_path = "/opt/data/projects/012-native-balfolk-render/audio/native_render.ogg"
sf2_path = "/usr/share/sounds/sf2/FluidR3_GM.sf2"

pm = pretty_midi.PrettyMIDI(initial_tempo=118)
violin = pretty_midi.Instrument(program=40)
melody = [(62, 0.0, 0.5), (64, 0.5, 1.0), (65, 1.0, 1.5), (67, 1.5, 2.0), (69, 2.0, 2.5)]
for p, s, e in melody:
    violin.notes.append(pretty_midi.Note(100, p, s, e))
pm.instruments.append(violin)

accordion = pretty_midi.Instrument(program=21)
accordion.notes.append(pretty_midi.Note(70, 50, 0, 4))
pm.instruments.append(accordion)

pm.write(midi_path)

# USE CLI FOR HIGH QUALITY RENDER
subprocess.run(["fluidsynth", "-ni", sf2_path, midi_path, "-F", wav_path, "-r", "44100"], check=True)
subprocess.run(["ffmpeg", "-i", wav_path, "-codec:a", "libopus", "-b:a", "128k", ogg_path, "-y", "-loglevel", "error"], check=True)
