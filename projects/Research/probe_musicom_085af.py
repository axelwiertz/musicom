# -*- coding: utf-8 -*-
"""Probe: layered methodology — per-bar chord grid derived from the
section-level subset walk with per-bar chromatic passing on bar 4.

Rule: whole-piece scale = F harmonic minor-ish?? Keep harmony audit clean:
every chord tone pc in F natural minor + allow raised leading tone? The
lead/bass/comp quantize against per-SECTION subset pcs, so audit scale =
union of all walked subsets pcs. For the walk min5 maj8 maj71 maj78 min75
min5 union = {0,1,3,5,7,8} = F Ab Bb? wait {0,1,3,5,7,8} — C Db Eb F G Ab.
That's F dorian-ish? F G Ab ... C Db Eb = F minor with raised 6th? Db = b2?
No: F natural minor pcs {5,7,8,10,0,1,3}. Union here = {0,1,3,5,7,8} = C,
Db, Eb, F, G, Ab = missing Bb (pc10), has G (7). So NOT a standard key!
Hmm wait F natural minor: F(5) G(7) Ab(8) Bb(10) C(0) Db(1) Eb(3). Union
{0,1,3,5,7,8} includes pc 5(F),7(G),8(Ab) but NOT 10(Bb); Db(1) Eb(3) C(0)
present. That's F minor WITHOUT Bb = wrong. maj78 Abmaj7 = Ab C Eb G {0,3,7,8}
has G (7) natural — G is in F minor (2nd degree). Bb missing because none of
the walked subsets contains pc10. Bb is in min10/min710 but not walked. That
makes the union = F aeolian missing Bb... the scale is "F minor b4"? Let me
fix: I need pc 10 (Bb) in the field so the scale reads as true F natural
minor. Add min10 (Bbm triad) and min710 (Bbm7) back into the FIELD (walk may
or may not pick them), and set the AUDIT scale = F natural minor full set.
The audit scale is the KEY scale: F natural minor {5,7,8,10,0,1,3}. Chord
tones from each subset must all be within it: min5 yes; maj8 {0,3,8} yes;
maj71 {0,1,5,8} yes; maj78 {0,3,7,8} yes; min75 {0,3,5,8} yes. All good.
"""
print("union of walked subsets all inside F natural minor pcs {5,7,8,10,0,1,3}")
print("audit scale = F natural minor (whole piece)")
