# -*- coding: utf-8 -*-
"""Abstract dev probe: walk seed-90 with home-biased resolution; bass/lead maps.

Seed 90 walk: min5 maj8 maj71 maj78 min75 min5.
Bass roots (pc -> low MIDI ~octave 1/2): F=41 or 29, Ab=32/44, Db=37,
Ab=32, F=41, F=41. For the 4-bar sections, per-bar chords can alternate
between two subsets for variety — the walk gives 1 pattern per SECTION;
bar-level = repeat + small variation (root motion within subset?). Simpler:
section pattern = chord pool; chord tones of bar = the subset's tones
transposed to register. Per-bar voicing picks root/3rd/5th/7th.
Bass per section: repeat root with rhythm. Use F2=41 Db2=37 Ab1=32/Ab2=44.
Let's finalize per-section chord tones in octave 4 for lead quantization:
min5 {0,5,8} -> F4=53 Ab4=56 C5=60 (root 53)
maj8 {0,3,8} -> Ab3? octave4: Ab=44+12? pc8 Ab = 44 (Ab3) or 56 (Ab4);
  tones on root 44: 44 Ab3, 48 C4, 56 Ab4? subset {0,3,8} with root 8(Ab):
  8->44, 0(C)->48, 3(Eb)->51? wait {0,3,8}: pc 0=C,3=Eb,8=Ab -> C Eb Ab =
  Ab major (root pc 8 = Ab: Ab C Eb = {8,0,3}). tones around octave 3/4:
  44(Ab3) 48(C4) 51(Eb4) and 56(Ab4).
maj71 {0,1,5,8} root pc 1 Db: Db F Ab C = Dbmaj7; around octave 3: 37(Db3)
  41(F3) 44(Ab3) 48(C4); octave4: 49(Db4) 53(F4) 56(Ab4) 60(C5)
maj78 {0,3,7,8} root pc 8 Ab: Abmaj7 = Ab C Eb G: 44 48 51 55? G4=55 pc7
  yes: {0,3,7,8} -> 44(Ab3) 48(C4) 51(Eb4) 55(G4) plus 56(Ab4).
min75 {0,3,5,8} root pc 5 F: Fm7 = F Ab C Eb: 41(F3) 44(Ab3) 48(C4) 51(Eb4)
Lead register: use octave 4-5. Quantize pitch classes to subset pc of the
SECTION (not bar) — sections 4 bars of same subset.
"""
print("done")
