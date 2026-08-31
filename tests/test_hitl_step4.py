# -*- coding: utf-8 -*-
"""Tests for the HITL evolution layer (workflows/hitl.py) — build step 4.

Covers (plan §3.2b):
- K <= 4 cognitive-load cap enforced.
- Candidates rendered to playable OGG excerpts (<= 30 s, non-empty).
- record_pick: persists human pick to evolution.json audit trail,
  writes provenance on the winner, returns winner metadata.
- Mutation around parent: round 2 variants cluster near the parent.
- Epsilon-wildcard: always differs from the other candidates.
- Multi-round accumulation in evolution.json.
"""
import json
import os
import sys

import pytest

sys.path.insert(0, "/opt/data/projects/Instruments")

from workflows.hitl import (
    MAX_CANDIDATES, EXCERPT_SECONDS,
    run_hitl_round, record_pick, next_round_parents, hitl_summary,
    generate_hitl_candidates, HITLRound, HITLCandidate,
)


@pytest.fixture(scope="module")
def round0():
    return run_hitl_round(style="pop", key="C", bpm=120, seed=42,
                          out_dir="/tmp/hitl_test")


def test_cap_enforced():
    with pytest.raises(ValueError):
        generate_hitl_candidates(n_candidates=5)


def test_round_shape(round0):
    assert isinstance(round0, HITLRound)
    assert 1 <= len(round0.candidates) <= MAX_CANDIDATES
    assert round0.style == "pop"
    assert round0.seed == 42


def test_candidates_render_to_ogg(round0):
    for c in round0.candidates:
        assert isinstance(c, HITLCandidate)
        assert os.path.exists(c.ogg_path)
        assert os.path.getsize(c.ogg_path) > 1000, "excerpt empty"
        assert os.path.exists(c.midi_path)
        assert os.path.getsize(c.midi_path) > 40


def test_candidate_fields(round0):
    for c in round0.candidates:
        assert 3 <= c.density <= 5
        assert c.offset in (0, 240)
        assert 0.0 <= c.fitness["total"] <= 1.0
        assert "terms" in c.fitness


def test_wildcard_differs(round0):
    others = [(c.density, c.offset) for c in round0.candidates[:-1]]
    if round0.candidates[-1].is_wildcard:
        assert (round0.candidates[-1].density,
                round0.candidates[-1].offset) not in others


def test_hitl_summary_text(round0):
    s = hitl_summary(round0)
    assert "HITL round" in s
    assert "density=" in s and "fitness=" in s
    assert len(s.splitlines()) == len(round0.candidates) + 1


def test_record_pick_writes_evolution(round0):
    import tempfile, os as _os
    evo_path = _os.path.join(tempfile.mkdtemp(), "evolution.json")
    res = record_pick(round0, 0, evolution_path=evo_path)
    assert res["winner"].variant == round0.candidates[0].variant
    assert _os.path.exists(evo_path)
    data = json.loads(open(evo_path).read())
    assert data["latest"]["judge"] == "human"
    assert data["latest"]["round"] == 0
    assert data["latest"]["pick_index"] == 0
    assert "rounds" in data and len(data["rounds"]) == 1
    assert data["latest"]["winner"]["midi"].endswith(".mid")


def test_record_pick_out_of_range(round0):
    with pytest.raises(IndexError):
        record_pick(round0, 99)


def test_next_round_parents(round0):
    d, o = next_round_parents(round0, 1)
    c = round0.candidates[1]
    assert d == c.density and o == c.offset


def test_mutation_around_parent():
    r1 = run_hitl_round(seed=42)
    d, o = next_round_parents(r1, 0)
    r2 = run_hitl_round(seed=99, parent_density=d, parent_offset=o, round_num=1)
    for c in r2.candidates:
        if not c.is_wildcard:
            # mutated candidates cluster within +/-1 of the parent density
            assert abs(c.density - d) <= 1
            # offset either preserved or flipped
            assert c.offset in (o, 240 - o)


def test_multi_round_accumulation(round0):
    import tempfile, shutil
    td = tempfile.mkdtemp()
    try:
        r1 = run_hitl_round(seed=1, out_dir=td)
        record_pick(r1, 0, evolution_path=os.path.join(td, "evolution.json"))
        r2 = run_hitl_round(seed=2, out_dir=td)
        record_pick(r2, 1, evolution_path=os.path.join(td, "evolution.json"))
        data = json.loads(open(os.path.join(td, "evolution.json")).read())
        assert len(data["rounds"]) == 2
        assert data["rounds"][0]["pick_index"] == 0
        assert data["rounds"][1]["pick_index"] == 1
        assert data["latest"]["pick_index"] == 1
    finally:
        shutil.rmtree(td)


def test_winner_provenance_sidecar(round0):
    import tempfile, os as _os
    td = tempfile.mkdtemp()
    evo_path = _os.path.join(td, "evolution.json")
    res = record_pick(round0, 0, evolution_path=evo_path)
    prov = res["winner"].midi_path + ".provenance.json"
    assert _os.path.exists(prov)
    rec = json.loads(open(prov).read())
    assert rec["classification"] == "ai-assisted"
    assert rec["generator"].startswith("workflows.hitl")
    assert "judge:human" in rec["sources"]
