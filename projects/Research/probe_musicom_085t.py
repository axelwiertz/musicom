# -*- coding: utf-8 -*-
"""Abstract dev probe: seed-55 walk tone sets.

seed 55: ['min5', 'dim5', 'dom71', 'dim5', 'dom710', 'min5']
=> Fm, Fdim, Db7, Fdim, Db7?? dom710 = {0? dom710 root pc 10 = Bb7 {10,2,5,8}},
   Fm. Check subsets.
"""
from rules.subset_network import standard_patterns
lib = {p.id: p for p in standard_patterns()}
for pid in ("min5","dim5","dom71","dom710"):
    print(pid, sorted(lib[pid].subset), "T=", round(lib[pid].tension,1))
