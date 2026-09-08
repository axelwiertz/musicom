import sys
import structures, workflows
from sound.render.pipeline import RenderPipeline
print("musicom env OK")
print("MidiInstrument exposes:", [a for a in dir(structures.MidiInstrument) if not a.startswith("_")])
