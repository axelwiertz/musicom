"""Phase 5 tests: paradigm-compare workflow + provenance labeling."""
import json
import os
import tempfile

import pytest

from structures import MusicUnit, MusicEvent
from workflows.paradigm_compare import (
    run_comparison, PARADIGMS, compare_table, _unit_stats,
)
from workflows.provenance import (
    build_provenance, write_provenance, policy_warnings,
    HUMAN, AI_ASSISTED, AI_GENERATED,
)


# --- uint8 overflow regression (found during T5.1) --------------------------
def test_pitch_intervals_no_uint8_overflow():
    # descending jump 72 -> 60 must be -12, not a uint8-wrapped ~244
    unit = MusicUnit(events=[
        MusicEvent(72, 100, 0, 480),
        MusicEvent(60, 100, 480, 960),
    ])
    assert unit.pitch_intervals == [-12]


# --- T5.1 paradigm-compare ---------------------------------------------------
def test_all_three_paradigms_present():
    assert set(PARADIGMS) == {"stochastic", "rules", "nature"}


def test_paradigm_units_generate():
    for name, fn in PARADIGMS.items():
        unit = fn()
        assert len(unit) > 0, name
        assert all(p > 0 for p in unit.pitches), name


def test_run_comparison_writes_artifacts():
    with tempfile.TemporaryDirectory() as d:
        r = run_comparison(d, bpm=120, seed=42)
        assert set(r["paradigms"]) == {"stochastic", "rules", "nature"}
        for name, info in r["paradigms"].items():
            assert os.path.getsize(info["midi"]) > 40, name
            assert os.path.exists(info["grid"]), name
            assert os.path.exists(info["provenance"]), name
        assert os.path.exists(r["table_path"])
        assert "| paradigm |" in r["table"]


def test_rules_paradigm_is_stepwise():
    # deterministic rules walk should have small average interval
    stats = _unit_stats(PARADIGMS["rules"]())
    assert stats["avg_abs_interval"] < 3


# --- T5.2 provenance ---------------------------------------------------------
def _tmp_artifact(d):
    p = os.path.join(d, "art.mid")
    with open(p, "wb") as f:
        f.write(b"MThd" + b"\x00" * 60)
    return p


def test_build_provenance_record():
    with tempfile.TemporaryDirectory() as d:
        p = _tmp_artifact(d)
        rec = build_provenance(p, AI_GENERATED, "unit_test",
                               sources=["seed=1"], parameters={"bpm": 90})
        assert rec["classification"] == AI_GENERATED
        assert rec["generator"] == "unit_test"
        assert len(rec["sha256"]) == 64
        assert rec["bytes"] == os.path.getsize(p)


def test_write_provenance_sidecar():
    with tempfile.TemporaryDirectory() as d:
        p = _tmp_artifact(d)
        prov = write_provenance(p, AI_ASSISTED, "unit_test", sources=["human.mid"])
        assert prov.endswith(".provenance.json")
        with open(prov) as f:
            rec = json.load(f)
        assert rec["classification"] == AI_ASSISTED


def test_invalid_classification_rejected():
    with tempfile.TemporaryDirectory() as d:
        p = _tmp_artifact(d)
        with pytest.raises(ValueError):
            build_provenance(p, "totally-human", "x")


def test_policy_warnings():
    with tempfile.TemporaryDirectory() as d:
        p = _tmp_artifact(d)
        rec = build_provenance(p, AI_GENERATED, "gen", sources=[])
        assert any("monetization" in w for w in policy_warnings(rec))
        rec_ok = build_provenance(p, HUMAN, "human")
        assert policy_warnings(rec_ok) == []
