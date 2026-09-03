# -*- coding: utf-8 -*-
"""Abstract dev probe: seed 85/90 walks — chord identity + bass roots.

seed 90: ['min5','maj8','maj71','maj78','min75','min5'] T [2,2,5.5,5.5,5,2]
  section 0 = Fm i (4 bars), 1 = Ab III, 2 = Dbmaj7 bVI7? maj71 root pc1
  Db -> Db F Ab C = Dbmaj7 (bVI maj7), 3 = Abmaj7 (III maj7 peak), 4 = Fm7
  (i7), 5 = Fm (resolve home). Nice: i III bVImaj7 IIImaj7 i7 i.
  Hmm iii section maj78 Abmaj7 + section 4 Fm7 - good.

seed 85: ['min5','maj8','maj71','min75','min710','min5']
  Fm Ab Dbmaj7 Fm7 Bbm7 Fm.

seed 90 has chorus peak at section 3 = Abmaj7. For a soul/groove piece:
Intro Fm (2.0), Verse Ab (2.0), Chorus Dbmaj7 (5.5), Verse2 Abmaj7 (5.5),
Chorus2 Fm7 (5.0), Outro Fm (2.0). Good shape. Verify bass root per subset.
"""
from rules.subset_network import standard_patterns
lib = {p.id: p for p in standard_patterns()}
for pid in ("min5","maj8","maj71","maj78","min75","min710"):
    p = lib[pid]
    print(pid, sorted(p.subset), "T=", p.tension)
