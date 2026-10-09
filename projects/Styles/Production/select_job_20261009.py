#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Layer-aligned production job selection (2026-10-09) with well-formed filter."""
import json
import random
import re
import time
from pathlib import Path

import mido

SEED = 20261009
DATE = "2026-10-09"
random.seed(SEED)

ROOT = Path("/opt/data/repos/musicom/projects/Styles")

NORMAL_TPB = {24, 48, 96, 120, 192, 240, 384, 480, 960}


def is_well_formed(p: Path):
    try:
        mf = mido.MidiFile(str(p))
    except Exception:
        return False
    tpb = mf.ticks_per_beat
    if tpb not in NORMAL_TPB:
        return False
    progs = 0
    note_tracks = 0
    max_dur_ticks = 0
    for tr in mf.tracks:
        has_pc = any(m.type == "program_change" for m in tr)
        if has_pc:
            progs += 1
        notes = [m for m in tr if m.type == "note_on" and m.velocity > 0]
        if notes:
            note_tracks += 1
    for tr in mf.tracks:
        t = 0
        pending = {}
        worst = 0
        for m in tr:
            t += m.time
            if m.type == "note_on" and m.velocity > 0:
                pending[m.note] = t
            elif m.type == "note_off" and m.note in pending:
                dur = t - pending.pop(m.note)
                worst = max(worst, dur)
            elif m.type == "note_on" and m.velocity == 0 and m.note in pending:
                dur = t - pending.pop(m.note)
                worst = max(worst, dur)
        max_dur_ticks = max(max_dur_ticks, worst)
    if max_dur_ticks > 16 * tpb:
        return False
    dur = mf.length
    if not (2.0 <= dur <= 600.0):
        return False
    if progs == 0 and note_tracks < 2:
        return False
    return True


candidates = []
for p in ROOT.rglob("*.mid"):
    s = str(p)
    if "/Production/" in s:
        continue
    if "phase1" in p.name:
        continue
    candidates.append(p)

assert candidates, "no candidate midi files"

wf = sorted([p for p in candidates if is_well_formed(p)])
print(f"well-formed: {len(wf)} / {len(candidates)} candidates")

if len(wf) >= 5:
    random.shuffle(wf)
    selected = wf[0]
else:
    pool = sorted(candidates)
    random.shuffle(pool)
    selected = pool[0]

from workflows.musicom_workflow import SP_METHODS  # noqa: E402

all_methods = sorted(SP_METHODS.keys())

prod = ROOT / "Production"
recent = set()
if prod.exists():
    now = time.time()
    for d in prod.iterdir():
        if not d.is_dir():
            continue
        m = re.match(r"SP-?(\d+)", d.name)
        if not m:
            continue
        age_days = (now - d.stat().st_mtime) / 86400.0
        if age_days <= 7.0:
            recent.add("SP-" + m.group(1))

baseline_excluded = {"SP-001"}
pool_methods = [m for m in all_methods if m not in recent and m not in baseline_excluded]
if len(pool_methods) < 4:
    pool_methods = [m for m in all_methods if m not in baseline_excluded]
if not pool_methods:
    pool_methods = ["SP-001"]

method = random.choice(pool_methods)
method_module, method_desc = SP_METHODS[method]

out = {
    "job": "random-style production (SP) layer-aligned",
    "date": DATE,
    "seed": SEED,
    "method": method,
    "method_module": method_module,
    "method_desc": method_desc,
    "source_midi": str(selected),
    "source_project": str(selected.relative_to(ROOT)),
    "registry_size": len(all_methods),
    "recent_excluded": sorted(recent),
    "baseline_excluded": sorted(baseline_excluded),
    "pool_methods": pool_methods,
    "n_candidates": len(candidates),
    "n_well_formed": len(wf),
}

sel_file = prod / ".selection_cron.json"
sel_file.write_text(json.dumps(out, indent=2))

print("SELECTED_MIDI=" + str(selected))
print("SELECTED_PROJECT=" + str(selected.relative_to(ROOT)))
print("SELECTED_METHOD=" + method)
print("METHOD_MODULE=" + method_module)
print("METHOD_DESC=" + method_desc)
print("REGISTRY_SIZE=" + str(len(all_methods)))
print("RECENT_EXCLUDED=" + ",".join(sorted(recent)))
print("POOL_SIZE=" + str(len(pool_methods)))
print("N_CANDIDATES=" + str(len(candidates)))
print("N_WELL_FORMED=" + str(len(wf)))
