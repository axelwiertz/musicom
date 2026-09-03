# -*- coding: utf-8 -*-
"""Abstract dev probe: deterministic walk selection for compose_085.

Seed 55 walk: Fm Fdim Db7 Fdim Bb7 Fm (dim chord color = passing; dom7
peak on section 4; 24 bars -> 4 bars per section; each section-subset is
the chord pool; bar-level chords derive from the subset's pcs).

Whole-piece scale = F natural minor pcs {5,7,8,10,0,1,3}. All walked
subsets must be subsets of that scale to keep harmony audit clean? Check:
- min5 {0,5,8} in scale? pc 0(C) 5(F) 8(Ab) yes all in.
- dim5 {5,8,11} -> pc 11 = B NOT in F natural minor (B natural = raised 4th
  of F). B is in F harmonic minor? harmonic minor F: F G Ab Bb C Db E -> pc
  11 E present, pc 5,8,11 dim5 = F Ab B?? no B natural pc 11 => E? Wait pc
  11 = B in C-major naming. dim5 {F Ab B}: B natural pc 11.
  F harmonic minor scale pcs = {5,7,8,10,0,1,3}? harmonic minor raises 7th:
  F G Ab Bb C Db E -> {5,7,8,10,0,1,3}. pc 11 (B) not there either — that
  would be E#? Confused. pc11 = B natural. dim5 {5,8,11} = F Ab B = Fdim
  with B natural. F harmonic minor's dim triad on G = Gdim {7,10,1} (G Bb
  Db) = dim7 id. So Fdim with B natural is NOT in F minor family, it is F
  dim = vii of Gb. Chromatic neighbor color.
  dom71 Db7 {Db F Ab B}: B natural again (Db7 = Db F Ab Cb; Cb = B natural
  enharmonic) = the leading tone of Db. Db is bII (Neapolitan) of C minor;
  in F minor Db7 = subV/... Db is the bVII? F minor: Db major = bVI? F G Ab
  Bb C Db Eb => Db is bVI. Db7 has Cb=pc11 (B natural) — out of scale.
  dim5 and dom71 contain pc 11. My harmony audit scale = F minor pcs will
  flag pc 11 as out-of-scale unless I use a chromatic-tolerant audit or
  F-minor + pc11? Hmm.
"""
print("F natural minor pcs: {5,7,8,10,0,1,3}")
print("seed55 subsets: Fm {0,5,8} Fdim {5,8,11} Db7 {1,5,8,11} Bb7 {2,5,8,10}")
print("pc11 present in dim5 + dom71 -> chromatic color notes")
