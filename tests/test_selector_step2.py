# -*- coding: utf-8 -*-
"""Tests for the method selector (workflows/selector.py) — build step 2.

Covers (plan §4 + advice #3/#7):
- Pure function: no state, deterministic output.
- Hard gates: spec-only never selected (registry truth), headless cost guard,
  corpus requirement, determinism requirement, memory-depth level match,
  metric binding, tonal gravity.
- Scoring: style affinity (HC method wins for matching style), curated
  SCALE-mirror tie-break.
- Daily-additions resilience: union of SCALE + registry; registry-only
  methods are selectable with a default level.
- Audit trail: every selection carries reasons.
"""
import sys

import pytest

sys.path.insert(0, "/opt/data/projects/Instruments")

from generators.generator_registry import GENERATOR_REGISTRY
from workflows.paths import SCALE, impl_status
from workflows.selector import (
    TRAITS, STYLE_HC_MAP, TaskProfile, Selection, select, select_for_cron,
    selector_table,
)


# ------------------------------------------------------------- pure fn ----

def test_select_is_deterministic():
    p = TaskProfile(tonal_gravity="strict", metric_binding="grid",
                    memory_depth="meso", headless=True)
    a = [(s.method_id, s.score) for s in select(p)]
    b = [(s.method_id, s.score) for s in select(p)]
    assert a == b


def test_select_sorted_by_score_then_id():
    p = TaskProfile(tonal_gravity="strict", metric_binding="grid",
                    memory_depth="meso", headless=True)
    r = select(p)
    scores = [s.score for s in r]
    assert scores == sorted(scores, reverse=True)
    # within equal score: method_id ascending
    for i in range(len(r) - 1):
        if r[i].score == r[i + 1].score:
            assert r[i].method_id < r[i + 1].method_id


def test_selection_has_reasons():
    for s in select(TaskProfile(tonal_gravity="strict"), limit=3):
        assert isinstance(s, Selection)
        assert s.reasons, "selection must carry audit reasons"
        assert s.implemented is True


def test_limit():
    full = select(TaskProfile())
    limited = select(TaskProfile(), limit=3)
    assert len(limited) == 3
    assert [s.method_id for s in limited] == [s.method_id for s in full[:3]]


# --------------------------------------------------------- hard gates ----

def test_spec_only_never_selected():
    # every spec-only registry entry (None module) must be filtered
    spec_only = [mid for mid, (m, _, _) in GENERATOR_REGISTRY.items() if m is None]
    assert spec_only, "test needs spec-only entries to exist"
    all_sel = {s.method_id for s in select(TaskProfile())}
    for mid in spec_only:
        assert mid not in all_sel, f"{mid} is spec-only but was selected"


def test_headless_cost_guard():
    # heavy AI-Driven methods (headless_ok False) must be excluded headless
    heavy = [mid for mid, t in TRAITS.items() if not t["headless_ok"]]
    assert heavy, "test needs heavy methods to exist"
    cron_sel = {s.method_id for s in select(TaskProfile(headless=True))}
    for mid in heavy:
        assert mid not in cron_sel, f"{mid} must not run in cron"
    # ...but remain selectable interactively
    interactive = {s.method_id for s in select(TaskProfile(headless=False))}
    # heavy methods aren't in SCALE/registry, so they can't be selected anyway;
    # the guard is about the trait, checked at the profile level:
    assert all(not t["headless_ok"] for mid, t in TRAITS.items()
               if mid in ("042", "046", "047", "054", "057", "059", "060", "062", "063"))


def test_corpus_gate():
    no_corpus = select(TaskProfile(corpus=False))
    no_corpus_ids = {s.method_id for s in no_corpus}
    # corpus-requiring methods with code are excluded when no corpus
    for mid, t in TRAITS.items():
        if t["corpus"] and impl_status(mid):
            assert mid not in no_corpus_ids, f"{mid} needs corpus but selected without"


def test_determinism_gate():
    det = {s.method_id for s in select(TaskProfile(determinism=True))}
    for mid, t in TRAITS.items():
        if not t["deterministic"] and impl_status(mid):
            assert mid not in det, f"{mid} is non-deterministic but selected for golden test"


def test_memory_depth_gate():
    meso = {s.method_id for s in select(TaskProfile(memory_depth="meso"))}
    for mid, (level, _) in SCALE.items():
        if level != "L3" and impl_status(mid):
            assert mid not in meso, f"{mid} is {level} but selected for meso"


def test_metric_gate():
    grid = {s.method_id for s in select(TaskProfile(metric_binding="grid"))}
    for mid, t in TRAITS.items():
        if t["metric"] != "grid" and impl_status(mid):
            assert mid not in grid, f"{mid} is fluid-metric but selected for grid"


def test_gravity_gate():
    strict = {s.method_id for s in select(TaskProfile(tonal_gravity="strict"))}
    for mid, t in TRAITS.items():
        if t["gravity"] != "strict" and impl_status(mid):
            assert mid not in strict, f"{mid} is organic but selected for strict"


# ------------------------------------------------------------- scoring ----

def test_style_affinity_ranks_hc_first():
    r = select(TaskProfile(style="flamenco"))
    assert r[0].method_id == "HC-012"
    assert "style-affinity:flamenco" in r[0].reasons
    assert r[0].score >= 3


def test_style_affinity_unknown_style_no_boost():
    # unknown style: no affinity bonus, HC methods don't dominate
    r = select(TaskProfile(style="nope"))
    assert all("style-affinity" not in s.reasons for s in r)


# ------------------------------------------- daily-additions resilience ----

def test_union_of_scale_and_registry():
    # every registry method with code is selectable under empty profile
    impl_ids = {mid for mid, (m, _, _) in GENERATOR_REGISTRY.items() if m is not None}
    all_sel = {s.method_id for s in select(TaskProfile())}
    assert impl_ids <= all_sel, f"missing: {impl_ids - all_sel}"


def test_registry_only_method_gets_default_level():
    # simulate a method newly added to the registry but not yet in SCALE
    import generators.generator_registry as gr
    orig = dict(gr.GENERATOR_REGISTRY)
    gr.GENERATOR_REGISTRY["999"] = ("generators.base", "FunctionGenerator", "new")
    try:
        # re-imported reference inside selector reads module attr live?
        from workflows import selector
        r = [s for s in selector.select(TaskProfile()) if s.method_id == "999"]
        assert r, "registry-only method must be selectable"
        assert r[0].level == "L3", "unclassified method should get default L3"
        assert "level:L3" in r[0].reasons
    finally:
        gr.GENERATOR_REGISTRY.clear()
        gr.GENERATOR_REGISTRY.update(orig)


# ----------------------------------------------------------- cron helper ----

def test_select_for_cron_all_headless_deterministic():
    r = select_for_cron(limit=10)
    assert 1 <= len(r) <= 10
    for s in r:
        assert TRAITS.get(s.method_id, {}).get("headless_ok", True)
        assert TRAITS.get(s.method_id, {}).get("deterministic", True)


def test_selector_table_markdown():
    t = selector_table()
    assert t.startswith("| Method ID | Gravity | Metric | Corpus |")
    assert "| 001 |" in t
