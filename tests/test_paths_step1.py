# -*- coding: utf-8 -*-
"""Tests for the composition path layer (workflows/paths.py) — build step 1.

Covers:
- SCALE registry: every method has a level, levels are the 4 valid ones,
  implementation status matches generator_registry reality (no routing to
  spec-only dead ends).
- Path C middle-out orchestrator: deterministic (same seed -> byte-identical
  MIDI), zero-drift gate passes, all 5 voices equal length, non-empty output,
  provenance sidecar written, chain metadata present.
"""
import hashlib
import os
import sys

import pytest

sys.path.insert(0, "/opt/data/projects/Instruments")

from workflows.paths import (
    SCALE, LEVELS, MIDDLE_OUT_CHAIN,
    methods_by_scale, scale_of, impl_status, scale_table,
    compose_middle_out, PathResult, POP_FORM,
)


# ---------------------------------------------------------------- SCALE ---

def test_scale_levels_valid():
    for mid, (lv, impl) in SCALE.items():
        assert lv in LEVELS, f"{mid} has invalid level {lv}"
        assert isinstance(impl, bool)


def test_scale_has_all_four_levels():
    assert methods_by_scale("L4"), "L4 empty"
    assert methods_by_scale("L3"), "L3 empty"
    assert methods_by_scale("L2"), "L2 empty"
    assert methods_by_scale("L1"), "L1 empty"


def test_scale_counts_match_plan():
    # plan §1: 13 L4, 25 L3, 20 L2, 9 L1 — L3 has 26 rows in the plan table
    # (the doc's count column says 25; the table lists 26). Step 2 added 003
    # (Genetic, L3) → L3 = 27. Registry matches the table + later additions.
    # LAYER_ARCHITECTURE.md added 5 ABS abstract-layer methods:
    # ABS-001/002 at L4 (+2 → 15), ABS-003/004/005 at L3 (+3 → 30).
    # Weekly registration (2026-09-06) added 071/072/073/074/075 at L4
    # (+5 → 20) and 076/077/078 at L3 (+3 → 33).
    # HC weekly registration added HC-020/HC-024 at L4 (+2 → 22), and
    # HC-018/019/021/022/023/025/026/027 at L3 (+8 → 41).
    # Weekly registration (2026-09-13) added 083/084/085 at L4 (+3 → 25),
    # 079/080/081/082 at L3 (+4 → 45); HC-028/029/030/031/032/033/034
    # added HC-029/030/031/032 at L4 (+4 → 29) and HC-028/033/034 at L3
    # (+3 → 48). Registry now routes 079 (tintinnabuli, first 07x with code).
    # Weekly registration (2026-09-20) added 088/089/090/091 at L4 (+4 → 33),
    # 086/087 at L3 (+2 → 50); HC-035..HC-040 added HC-036/037/038/040 at L4
    # (+4 → 37) and HC-035/039 at L3 (+2 → 52).
    # Weekly registration (2026-09-27) added 097 at L4 and HC-041/HC-046 at L4
    # (+3 → 40); 093/094/ABS-095/096 at L3 and HC-042/043/044/045/047 at L3
    # (+9 → 61). ABS-095 is the first abstract-layer numeric method (CTC),
    # routed to rules.subset_network like ABS-001..005.
    # Weekly registration (2026-10-04) added 098/ABS-099/100/101/102/103/ABS-104
    # at L4 (+7 → 47) and HC-049/051/054 at L4 (+3 → 50); HC-048/050/052/053 at L3
    # (+4 → 65). ABS-099 (SSMC) and ABS-104 (PSSC) are abstract-layer numeric
    # methods routed to rules.subset_network like ABS-001..005 and ABS-095.
    assert len(methods_by_scale("L4")) == 50
    assert len(methods_by_scale("L3")) == 65
    assert len(methods_by_scale("L2")) == 20
    assert len(methods_by_scale("L1")) == 9


def test_scale_of_known_and_unknown():
    assert scale_of("001") == "L4"
    assert scale_of("002") == "L1"
    assert scale_of("HC-012") == "L3"
    assert scale_of("nope") is None


def test_impl_status_reflects_registry():
    # implemented methods (in generator_registry with real code)
    assert impl_status("001") is True
    assert impl_status("012") is True
    assert impl_status("023") is True
    assert impl_status("002") is True
    # spec-only methods must NOT be routable
    assert impl_status("026") is False
    assert impl_status("048") is False
    assert impl_status("034") is False
    assert impl_status("HC-007") is False


def test_scale_table_is_markdown():
    t = scale_table()
    assert t.startswith("| Method ID | Level | Implemented |")
    assert "| 001 | L4 |" in t
    assert "spec-only" in t


# ----------------------------------------------------------- MIDDLE-OUT ---

@pytest.fixture(scope="module")
def middle_out():
    return compose_middle_out(style="pop", key="C", bpm=120, seed=42)


def test_result_shape(middle_out):
    assert isinstance(middle_out, PathResult)
    assert middle_out.path == "C"
    assert middle_out.seed == 42
    assert middle_out.key == "C"
    assert middle_out.bpm == 120
    assert middle_out.style == "pop"


def test_midi_exists_nonempty(middle_out):
    assert os.path.exists(middle_out.midi_path)
    assert os.path.getsize(middle_out.midi_path) > 40, "empty/corrupt MIDI"


def test_provenance_written(middle_out):
    assert middle_out.provenance_path
    assert os.path.exists(middle_out.provenance_path)


def test_chain_has_five_steps():
    assert len(MIDDLE_OUT_CHAIN) == 5
    scales = [s for s, _, _ in MIDDLE_OUT_CHAIN]
    assert scales == ["L3", "L3", "L4", "L2", "L1"]


def test_chain_methods_implemented():
    # Path C must only route to methods with working code
    for sc, mid, _ in MIDDLE_OUT_CHAIN:
        assert impl_status(mid), f"{mid} is spec-only — must not be in Path C"


def test_zero_drift_equal_tracks(middle_out):
    import mido
    m = mido.MidiFile(middle_out.midi_path)
    # track 0 = tempo; remaining must all be identical length
    voice_lens = [sum(msg.time for msg in t) for t in m.tracks[1:]]
    assert len(set(voice_lens)) == 1, f"track drift: {voice_lens}"


def test_deterministic_same_seed():
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        r1 = compose_middle_out(seed=7, out_dir=td)
        r2 = compose_middle_out(seed=7, out_dir=td)
        h1 = hashlib.sha256(open(r1.midi_path, "rb").read()).hexdigest()
        h2 = hashlib.sha256(open(r2.midi_path, "rb").read()).hexdigest()
        assert h1 == h2, "same seed must give byte-identical MIDI"


def test_different_seed_different_output():
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        r1 = compose_middle_out(seed=1, out_dir=td)
        r2 = compose_middle_out(seed=2, out_dir=td)
        h1 = hashlib.sha256(open(r1.midi_path, "rb").read()).hexdigest()
        h2 = hashlib.sha256(open(r2.midi_path, "rb").read()).hexdigest()
        assert h1 != h2, "different seeds should differ"


def test_form_default_pop():
    assert POP_FORM == [("Intro", 4), ("Verse", 8), ("Chorus", 8),
                        ("Bridge", 4), ("Outro", 4)]
