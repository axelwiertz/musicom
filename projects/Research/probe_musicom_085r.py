# -*- coding: utf-8 -*-
"""Abstract dev probe: what is a sensible bass root for each pattern id?

Patterns in F-minor-ish field with pc5 F anchor:
- min5 {0,5,8} Fm -> root F (pc5)
- maj5 {0,5,9} F? {F A C} is F major -> root F (pc5)
- maj71 {0,1,5,8} Db F Ab C -> Dbmaj7 root Db (pc1)
- dim5 {5,8,11} F Ab B -> Fdim root F (pc5)
- dom71 {1,5,8,11} Db F Ab B -> Db7 root Db (pc1)
- min0 {0,3,7} Cm root C (pc0); maj3 {3,7,10} Eb root Eb (pc3);
- min10 {1,5,10} Bbm root Bb (pc10); maj8 {0,3,8} Ab root Ab (pc8).
So the seed-41 walk: Fm F Dbmaj7 Fdim Db7 Fm?? wait seq was [min5, maj5,
maj71, dim5, dom71, min5] -> Fm / F / Dbmaj7 / Fdim / Db7 / Fm. The bass
roots: F F Db F Db F.
Names: Fm F Dbmaj7 Fdim Db7 Fm.
"""
print("walk 41 realization: Fm | F | Dbmaj7 | Fdim | Db7 | Fm")
print("bass roots: F2(41) F2(41) Db2(37) F2(41) Db2(37) F2(41)")
