#!/usr/bin/env python3
"""
compose_hhfc_demo.py — Method 146 HHFC (Hindemith Harmonic Fluctuation
Composition) engine demo.

Abstract layer: a chord-group / root-progression plan with its harmonic-
fluctuation curve (cumulative sum of progression values):
    Section A: C major (Group I-1, root=bass)      curve 0
    Section B: F/A    (Group I-2, root above bass) curve +2  (C->F, P4)
    Section C: G7     (Group II-a, tritone chord)  curve -1  (F->G, M2)
    Section D: C major (Group I-1, cadence TURN)   curve +2  (G->C, P4)
  fluctuation = [0, 2, 1, 3] — the canonical I-IV-V-I tension profile with
  the tritone chord (Group II) as the TENSE peak-approach.

Concrete layer: UnitMatrix (3 voices x 4 sections) realized with the musicom
engine.  Bass = Hindemith root/bass placement (root in bass for I-1 chords,
root ABOVE bass for the I-2 chord), Chord = 3-4 note realization, Lead =
16-eighth arpeggio of chord tones.  Zero-drift validated, MIDI exported.
"""
import os, json
from structures import MidiInstrument
from workflows.unitmatrix_composer import UnitMatrixComposer, create_note_unit, create_chord_unit

OUT_DIR = "/opt/data/projects/Research/outputs/hhfc146"
os.makedirs(OUT_DIR, exist_ok=True)

# ---- abstract plan ---------------------------------------------------------
# (section, root_pc, group, root_in_bass, chord tones as semitones above C2)
PLAN = [
    ("A", 0,  "I-1",  True,  [0, 4, 7]),        # C  major
    ("B", 5,  "I-2",  False, [9, 0, 5]),        # F/A (root F above bass A)
    ("C", 7,  "II-a", True,  [7, 11, 2, 5]),    # G7 (tritone B-F)
    ("D", 0,  "I-1",  True,  [0, 4, 7]),        # C  major (cadence TURN)
]
PROG_VAL = {0: 0, 1: -2, 2: -1, 3: 1, 4: 1, 5: 2, 6: -3, 7: 2, 8: 1, 9: 1,
            10: -1, 11: -2}                     # canonical progression values

def fluctuation(roots):
    c, out = 0, [0]
    for a, b in zip(roots, roots[1:]):
        c += PROG_VAL[(b - a) % 12]
        out.append(c)
    return out

roots = [p[1] for p in PLAN]
curve = fluctuation(roots)
print("root progression:", [p[0] for p in PLAN], roots)
print("harmonic fluctuation curve:", curve)
assert curve == [0, 2, 1, 3], "unexpected fluctuation curve"

# ---- concrete: UnitMatrix --------------------------------------------------
composer = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
composer.create_matrix(num_voices=3, num_sections=4)
composer.add_voice("Bass",  program=MidiInstrument.BASS,            channel=0)
composer.add_voice("Chord", program=MidiInstrument.STRING_ENSEMBLE, channel=1)
composer.add_voice("Lead",  program=MidiInstrument.FLUTE,           channel=2)
for name, _bars in [("A", 2), ("B", 2), ("C", 2), ("D", 2)]:
    composer.add_section(name, bars=2)

C2 = 36  # MIDI C2
BAR = 1920
SECTION = 2 * BAR          # 3840 ticks per section
EIGHTH = SECTION // 16     # 240 ticks

for i, (name, root, grp, root_in_bass, tones) in enumerate(PLAN):
    # Bass: root (or chord 3rd when root is above the bass, Group I-2)
    if root_in_bass:
        bass_pitch = C2 + 12 + root           # root in bass (C3 region)
    else:
        bass_pitch = C2 + 12 + tones[1]       # chord 3rd in bass, root above
    composer.fill_voice_section("Bass", name,
        create_note_unit(bass_pitch, SECTION))
    # Chord: the full realization (Group II-a gets its 7th = tritone tone)
    chord = [C2 + 24 + t for t in tones]      # C4 region
    composer.fill_voice_section("Chord", name,
        create_chord_unit(chord, SECTION))
    # Lead: 16-eighth arpeggio of the chord tones (motivic cycle)
    events, arp = [], [C2 + 24 + t for t in tones]
    for k in range(16):
        p = arp[k % len(arp)]
        events.append((p, k * EIGHTH))
    unit = create_note_unit(events[0][0], EIGHTH, 0)
    # build a MusicUnit with the full arpeggio
    from structures import MusicUnit, MusicEvent
    mevs = [MusicEvent(pitch=p, volume=92, start_tick=s,
                       end_tick=min(s + EIGHTH, SECTION)) for p, s in events]
    composer.fill_voice_section("Lead", name, MusicUnit(events=mevs))

ok, msg = composer.validate()
print("validate():", ok, msg)
assert ok, "zero-drift gate failed"

midi_path = os.path.join(OUT_DIR, "hhfc_146_demo.mid")
composer.to_midi(midi_path)
size = os.path.getsize(midi_path)
print("MIDI:", midi_path, size, "bytes")
assert size > 40, "empty/corrupt output"

# ---- provenance ------------------------------------------------------------
from workflows.provenance import write_provenance
write_provenance(
    midi_path,
    classification="ai-generated",
    generator="hhfc_146_demo.py (Method 146 Hindemith Harmonic Fluctuation Composition)",
    sources=["Wikipedia DE: Unterweisung im Tonsatz (classification table)",
             "Hindemith, Craft of Musical Composition I (Schott 1937/1942)",
             "Wikipedia EN: Paul Hindemith / Ludus Tonalis"],
    parameters={"plan": PLAN, "fluctuation_curve": curve,
                "progression_values": PROG_VAL,
                "bpm": 120, "ticks_per_beat": 480, "bars_per_section": 2},
    notes="Abstract->concrete demo: group/root plan realized as UnitMatrix; validate OK.",
)
print("provenance written")

print("DEMO OK — curve", curve, "| MIDI", size, "B")
