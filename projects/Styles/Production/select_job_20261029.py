# -*- coding: utf-8 -*-
"""Layer-aligned production job selection (2026-10-27).

Same procedure as 2026-10-26: structural well-formedness gate + "musically
meaningful" gate (>=3 distinct pitch classes), then exclude recent-7-day
methods + methods already applied to the source + baseline SP-001.
"""
import json
import random
import re
import time
from pathlib import Path

import mido

SEED = 20261029
DATE = "2026-10-29"
random.seed(SEED)

ROOT = Path("/opt/data/repos/musicom/projects/Styles")
prod = ROOT / "Production"

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


def pitch_class_diversity(p: Path):
    try:
        mf = mido.MidiFile(str(p))
    except Exception:
        return 0
    pcs = set()
    for tr in mf.tracks:
        for m in tr:
            if m.type == "note_on" and m.velocity > 0:
                pcs.add(m.note % 12)
    return len(pcs)


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
meaningful = [p for p in wf if pitch_class_diversity(p) >= 3]
print("well-formed: %d / %d candidates" % (len(wf), len(candidates)))
print("meaningful (>=3 pitch classes): %d" % len(meaningful))

random.shuffle(meaningful)
selected = meaningful[0]

from workflows.musicom_workflow import SP_METHODS  # noqa: E402

all_methods = sorted(SP_METHODS.keys())

recent = set()
now = time.time()
for d in prod.iterdir():
    if not d.is_dir():
        continue
    m = re.match(r"SP-?(\d+)", d.name)
    if not m:
        continue
    if (now - d.stat().st_mtime) / 86400.0 <= 7.0:
        recent.add("SP-" + m.group(1))

src_name = selected.name
already_on_source = set()
for d in prod.iterdir():
    rp = d / "REPORT.md"
    if not rp.exists():
        continue
    try:
        body = rp.read_text(errors="ignore")
        if src_name in body:
            m = re.match(r"SP-?(\d+)", d.name)
            if m:
                already_on_source.add("SP-" + m.group(1))
    except Exception:
        pass

baseline_excluded = {"SP-001"}
excluded = recent | baseline_excluded | already_on_source
pool_methods = [m for m in all_methods if m not in excluded]
if len(pool_methods) < 4:
    pool_methods = [m for m in all_methods if m not in (baseline_excluded | already_on_source)]
if not pool_methods:
    pool_methods = [m for m in all_methods if m not in baseline_excluded]

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
    "already_on_source": sorted(already_on_source),
    "baseline_excluded": sorted(baseline_excluded),
    "pool_methods": pool_methods,
    "n_candidates": len(candidates),
    "n_well_formed": len(wf),
    "n_meaningful": len(meaningful),
    "rejected_degenerate": [],
}

sel_file = prod / ".selection_cron.json"
sel_file.write_text(json.dumps(out, indent=2))

print("SELECTED_MIDI=" + str(selected))
print("SELECTED_PROJECT=" + str(selected.relative_to(ROOT)))
print("SELECTED_METHOD=" + method)
print("METHOD_MODULE=" + method_module)
print("METHOD_DESC=" + method_desc)
print("RECENT_EXCLUDED=" + ",".join(sorted(recent)))
print("ALREADY_ON_SOURCE=" + ",".join(sorted(already_on_source)))
print("POOL_SIZE=" + str(len(pool_methods)))
print("N_WELL_FORMED=" + str(len(wf)))
print("N_MEANINGFUL=" + str(len(meaningful)))
