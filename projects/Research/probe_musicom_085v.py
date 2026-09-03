# -*- coding: utf-8 -*-
"""Abstract dev probe: choose clean field so walked subsets are in-scale.

Goal: keep all realized chord tones inside a F-minor-ish pool for the
harmony audit, i.e. use only subsets fully within F natural minor pcs
{5,7,8,10,0,1,3} + allow F harmonic-minor colors on V (pc 3 root Eb -> Eb
maj with G pc7? Eb G Bb = {3,7,10} all in natural minor — ok) + dom7 on
root 3 with D? no.

In-scale candidates on F natural minor:
- triads: min5 Fm {0,5,8} dim7 Gdim {1,7,10} maj8 Ab {0,3,8}
  min10 Bbm {1,5,10} min0 Cm {0,3,7} maj1 Db {1,5,8} maj3 Eb {3,7,10}
- 7ths inside natural minor (built from scale tones):
  min75 Fm7 {0,3,5,8} min710 Bbm7 {1,3,5,10} min77? Gm7 {1,7,10,2}?
  wait Gm7 = G Bb D F = {2,7,10,1} = min77 subset {1,2,7,10} in scale yes.
  maj78 Abmaj7 {0,3,7,8}? Ab C Eb G = {0,3,7,8} in scale yes.
  dom7 out-of-scale ones contain pc11/pc6 etc — exclude or accept.
  min0 Cm7 = C Eb G Bb = {0,3,7,10} = min70 in scale yes.
  maj71 Dbmaj7 = Db F Ab C = {1,5,8,0} = {0,1,5,8} in scale yes!
  dom71 Db7 has B(pc11) — out.
  dom710 Bb7 = {10,2,5,8} pc2 = D natural — in F minor? D natural pc2 NOT
  in natural minor (D is pc 2; F minor has Db pc 1). Bb7 has D natural —
  out of scale. But Bb7 = V7 of Eb; in F minor Bb is the subdominant minor
  (iv=Bbm). Using Bb major 7? Bbmaj7 = Bb D F A = {10,2,5,9} pc2, pc9 A
  natural both out. Hmm.
- dim7 Gdim {1,7,10} fully in scale = vii dim of F minor! Real triad on pc
  7 root G: {7,10,1} = dim7 id? id "dim7" with root digit 7 -> dim7. in.
  Earlier I used 'dim7' meaning the Gdim triad. tension 4.0.
- Fdim dim5 = {5,8,11} pc11 out.

So to keep audit clean: choose field = {min5 Fm, dim7 Gdim, maj8 Ab,
min10 Bbm, min0 Cm, maj1 Db, maj3 Eb, min75 Fm7, min710 Bbm7, min77 Gm7,
maj78 Abmaj7, min70 Cm7, maj71 Dbmaj7} all strictly in F natural minor
pcs. Tension curve: peak wants a 7th chord (max T = 5.5 maj78). Curve
[2.2,3.5,5.5,4.0,5.5,2.0].
"""
from rules.subset_network import PatternNetwork, standard_patterns
import random

lib = {p.id: p for p in standard_patterns()}
field = ["min5","dim7","maj8","min10","min0","maj1","maj3",
         "min75","min710","min77","maj78","min70","maj71"]
field = [f for f in field if f in lib]
print("field:", [(f, sorted(lib[f].subset), round(lib[f].tension,1)) for f in field])
net = PatternNetwork([lib[f] for f in field])
curve = [2.2, 3.5, 5.5, 4.0, 5.5, 2.0]
seen = set()
for seed in range(80, 110):
    rng = random.Random(seed)
    w = net.walk("min5", 6, rng=rng, tension_curve=curve, home="min5")
    k = tuple(w)
    if k not in seen:
        seen.add(k)
        ok = all(set(lib[x].subset) <= {5,7,8,10,0,1,3} for x in w)
        print(f"seed {seed}:", w, "in-scale:", ok,
              "T:", [round(lib[x].tension,1) for x in w])
print("unique:", len(seen))
