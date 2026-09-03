# -*- coding: utf-8 -*-
"""Abstract dev probe: pick one walk and map pcs -> F-minor-ish diatonic bass roots.

Decide F-minor harmonic realization per section-subset:
- min5 {0,5,8} = Fm (root pc 5). Bass root F2 = 41.
- maj5 {0,5,9} = F-major (picardy / V-of-iv color, root pc 5). Bass F = 41.
- maj71 {1,4,8,11}... root pc 1 = Db maj7. Wait earlier I printed maj71 =
  {0,1,5,8}?? both can't be. Probe printed maj71 [0,1,5,8]. Root pc 1, maj
  triad 1,4,8 + maj7 11: {1,4,8,11}. [0,1,5,8] = 4-note but sorted subset
  {0,1,5,8} — that's Dbmin/maj? No: {1,4,8,11} mod sorted = {1,4,8,11}; the
  printed subset {0,1,5,8} is a DIFFERENT pc set. Something off: maj71 =
  prefix maj7 + root digit 1 => tetrad (0,4,7,11)+1 = {1,5,8,0} = {0,1,5,8}
  = Dbmaj7 (Db F Ab C) yes! sorted {0,1,5,8} correct. I mis-added before.
  Root pc 1 = Db. Bass Db2 = 37.
- dim5 = root pc 5 dim triad {5,8,11} = Fdim? F Ab B? = F diminished? F Ab B
  -> {5,8,11} yes Fdim. Bass F 41.
- dom71 = {1,5,8,11} = Db7? Db F Ab B = Db7 -> root pc 1 = Db. Bass Db 37.
Chord tones for realization (lead/comp in octave 4, bass octave 2/3):
"""
pc_to_name = {0:"C",1:"Db",2:"D",3:"Eb",4:"E",5:"F",6:"Gb",7:"G",8:"Ab",9:"A",10:"Bb",11:"B"}
def name_set(pcs): return " ".join(pc_to_name[p] for p in sorted(pcs))
for pid, pcs in [("min5",{0,5,8}),("maj5",{0,5,9}),("maj71",{0,1,5,8}),
                 ("dim5",{5,8,11}),("dom71",{1,5,8,11})]:
    print(pid, name_set(pcs), "bass root pc", sorted(pcs)[0] if False else None)
