import os
from workflows.unitmatrix_composer import UnitMatrixComposer, create_note_unit

d = os.path.dirname(os.path.abspath(__file__))
c = UnitMatrixComposer(bpm=96)
c.create_matrix(num_voices=2, num_sections=3)
c.add_voice("Sax1", program=65, channel=0)
c.add_voice("Sax2", program=66, channel=1)
c.add_section("A", bars=4)
c.add_section("B", bars=4)
c.add_section("C", bars=4)
for s in ("A", "B", "C"):
    c.fill_voice_section("Sax1", s, create_note_unit(57, 4 * 1920))
    c.fill_voice_section("Sax2", s, create_note_unit(60, 4 * 1920))
ok, msg = c.validate()
print("validate:", ok, msg)
p = os.path.join(d, "sp134_sax.mid")
c.to_midi(p)
print("midi bytes:", os.path.getsize(p))
assert os.path.getsize(p) > 40
