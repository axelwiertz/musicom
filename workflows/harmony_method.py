# -*- coding: utf-8 -*-
"""HarmonizationMethod — harmonisation as a selectable method chain (P0).

HARMONIZATION_METHOD_PLAN.md P0. Harmonisation follows the same abstract →
concrete journey as the melody, but with its OWN selected method, and can be
sourced WITH or WITHOUT the composition method's phase-1 output.

Contract (parallel to ``CellMethod``):

    plan(ctx...) -> HarmonyPlan      # abstract: WHAT chords, per bar
    voice(plan, ...) -> [MusicEvent] # concrete: raw harmony notes

``source`` is the "include / without phase-1" switch:
  * ``"method"``   — derive the plan FROM the composition method's phase-1 raw
  * ``"template"`` — plan from a functional template / ABS walk / melody

Four concrete harmonisers fold existing assets (no re-invention):

  * ``FunctionalHarmonizer`` — I–V–vi–IV (or style progression) per bar — the
    current default path, re-encoded as a method.
  * ``SATBHarmonizer``        — ``HarmonyWriter`` voice-led SATB (melody-derived).
  * ``ChordArpHarmonizer``    — ``ChordDrivenArranger`` chord/arp/bass.
  * ``AbstractHarmonizer``    — ``rules.subset_network`` ABS-002 subset walk.

``voice()`` returns already-realized ``MusicEvent`` (grid-locked, deterministic)
for the rule-based harmonisers — the same passthrough contract as
``DefaultMethod``, so ``realize_spine`` can consume it unchanged.

Pure module; the concrete voice-leaders (harmony_writer / chord_arranger) are
imported lazily at call time.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence

from structures import MusicEvent

from rules.harmony import CHORD_SHAPES, KEY_OFFSET, PROGRESSIONS
from workflows.harmony_plan import Chord, HarmonyPlan

__all__ = [
    "HarmonizationProfile", "HarmonizationMethod",
    "FunctionalHarmonizer", "SATBHarmonizer", "ChordArpHarmonizer",
    "AbstractHarmonizer", "HARMONIZERS", "harmonizer_plan",
    "HARMONY_PROFILES", "profile_for_method", "plan_from_method",
]


@dataclass(frozen=True)
class HarmonizationProfile:
    """Per-method harmonisation descriptor (phase_semantics + source)."""
    method_id: str
    source: str              # "method" | "template"
    phase_semantics: str     # "progression"|"band"|"rhythm"|"contour"|"none"
    harmonizer: str          # "functional"|"satb"|"chordarp"|"abstract"


class HarmonizationMethod:
    """The harmonisation contract (structural, not runtime-enforced)."""

    id = "functional"
    source = "template"
    phase_semantics = "progression"

    def plan(self, key: str, section_names: Sequence[str],
             bars_per: Sequence[int], style: str = "", seed: int = 0,
             phase1=None) -> HarmonyPlan:
        """Abstract: WHAT chords, one per bar, tiled over all sections."""
        raise NotImplementedError

    def voice(self, plan: HarmonyPlan, key: str = "C", seed: int = 0,
              lead: Optional[Sequence[dict]] = None,
              ctx=None) -> List[MusicEvent]:
        """Concrete: raw harmony notes (already realized for rule-based)."""
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Functional — I–V–vi–IV (or style progression), one chord per bar
# ---------------------------------------------------------------------------

class FunctionalHarmonizer(HarmonizationMethod):
    """Template harmony: a Roman-numeral progression tiled per bar."""

    id = "functional"
    source = "template"
    phase_semantics = "progression"

    def plan(self, key, section_names, bars_per, style="", seed=0, phase1=None):
        # style -> progression flavor; fall back to pop I-V-vi-IV
        prog = None
        for flavor, degrees in PROGRESSIONS.items():
            if flavor in (style or "").lower():
                prog = degrees
                break
        if prog is None:
            prog = PROGRESSIONS["pop"]
        off = KEY_OFFSET.get(key, 0)
        chords = []
        for b in range(sum(bars_per)):
            deg = prog[b % len(prog)]
            root_iv, qual = CHORD_SHAPES.get(deg, CHORD_SHAPES["I"])
            root_midi = 48 + off + root_iv
            chords.append(Chord(root_midi=root_midi, quality=qual, degree=deg))
        return HarmonyPlan(chords=tuple(chords))

    def voice(self, plan, key="C", seed=0, lead=None, ctx=None):
        """Sustained pad block per bar (the harmony layer)."""
        evs: List[MusicEvent] = []
        bar_ticks = 1920
        for b, chord in enumerate(plan.chords):
            base = b * bar_ticks
            for t in chord.chord_tones()[:3]:
                evs.append(MusicEvent(t, 60, base, base + bar_ticks))
        return evs


# ---------------------------------------------------------------------------
# Abstract — ABS-002 subset walk, one chord per bar
# ---------------------------------------------------------------------------

class AbstractHarmonizer(HarmonizationMethod):
    """Abstract-layer harmony: a 12TET subset walk under a tension curve."""

    id = "abstract"
    source = "template"
    phase_semantics = "progression"

    def plan(self, key, section_names, bars_per, style="", seed=0, phase1=None):
        from rules.subset_network import PatternNetwork, standard_patterns
        from rules.realize import realize_tonal_cluster
        rng = __import__("random").Random(seed or 0)
        lib = PatternNetwork(standard_patterns())
        anchor_ids = ["maj0", "min9", "maj5", "min2", "dom70", "maj70"]
        net = PatternNetwork([lib.patterns[i] for i in anchor_ids])
        total = max(sum(bars_per), 2)
        curve = [1.5 * i / (total - 1) for i in range(total)]
        walk = net.walk("maj0", total, rng=rng, tension_curve=curve, home="maj0")
        chords = []
        for pid in walk:
            tones = tuple(realize_tonal_cluster(lib.patterns[pid]))
            chords.append(Chord(root_midi=tones[0], quality="maj", tones=tones))
        return HarmonyPlan(chords=tuple(chords))

    def voice(self, plan, key="C", seed=0, lead=None, ctx=None):
        # Same sustained pad as functional, but over the walked subsets.
        return FunctionalHarmonizer().voice(plan, key=key, seed=seed, lead=lead)


# ---------------------------------------------------------------------------
# SATB — HarmonyWriter voice-led four-part (melody-derived)
# ---------------------------------------------------------------------------

class SATBHarmonizer(HarmonizationMethod):
    """Melody-derived harmony: HarmonyWriter diatonic triads + voice-leading."""

    id = "satb"
    source = "template"
    phase_semantics = "contour"

    def plan(self, key, section_names, bars_per, style="", seed=0, phase1=None):
        # SATB derives chords FROM the lead, so without a lead there is no
        # independent plan — fall back to the functional template.
        return FunctionalHarmonizer().plan(key, section_names, bars_per, style, seed)

    def voice(self, plan, key="C", seed=0, lead=None, ctx=None):
        from sound.generators.harmony_writer import HarmonyWriter
        if not lead:
            return []
        hw = HarmonyWriter(key=key, style=4, seed=seed or 0)
        parts = hw.harmonize(list(lead))
        evs: List[MusicEvent] = []
        for vname, line in parts.items():
            if vname == "soprano":          # soprano doubles the melody
                continue
            for e in line:
                evs.append(MusicEvent(e["pitch"], e["volume"],
                                      e["start_tick"], e["end_tick"]))
        return evs


# ---------------------------------------------------------------------------
# ChordArp — ChordDrivenArranger chord/arp/bass (progression-derived)
# ---------------------------------------------------------------------------

class ChordArpHarmonizer(HarmonizationMethod):
    """Progression-derived harmony: UNA-style chord + arp + bass tracks."""

    id = "chordarp"
    source = "template"
    phase_semantics = "rhythm"

    def plan(self, key, section_names, bars_per, style="", seed=0, phase1=None):
        return FunctionalHarmonizer().plan(key, section_names, bars_per, style, seed)

    def voice(self, plan, key="C", seed=0, lead=None, ctx=None):
        from sound.generators.chord_arranger import ChordDrivenArranger
        chords = [(c.root_midi, c.quality) for c in plan.chords]
        arr = ChordDrivenArranger(bpm=120, bars=len(chords), seed=seed or 0)
        raw = arr.generate(chords)
        evs: List[MusicEvent] = []
        for e in raw:
            if e["track"] == "chord":       # harmony layer only (melody/bass separate)
                evs.append(MusicEvent(e["pitch"], e["vel"],
                                      e["start_tick"],
                                      e["start_tick"] + e["duration_ticks"]))
        return evs


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

HARMONIZERS = {
    "functional": FunctionalHarmonizer,
    "abstract": AbstractHarmonizer,
    "satb": SATBHarmonizer,
    "chordarp": ChordArpHarmonizer,
}


def harmonizer_plan(name: str, key: str, section_names: Sequence[str],
                    bars_per: Sequence[int], style: str = "", seed: int = 0,
                    phase1=None) -> HarmonyPlan:
    """Resolve a harmoniser by name and build its per-bar HarmonyPlan."""
    cls = HARMONIZERS.get(name)
    if cls is None:
        raise ValueError(
            f"unknown harmonizer {name!r}; use {sorted(HARMONIZERS)}")
    return cls().plan(key, section_names, bars_per, style=style, seed=seed,
                      phase1=phase1)


# Per-method harmonisation descriptors (§2 of the plan). P1 wires the
# "method" source (plan_from_method); P0 ships the table + honest stub.
HARMONY_PROFILES = {
    "001": HarmonizationProfile("001", "method", "progression", "functional"),
    "002": HarmonizationProfile("002", "method", "progression", "functional"),
    "003": HarmonizationProfile("003", "template", "contour", "satb"),
    "010": HarmonizationProfile("010", "method", "progression", "functional"),
    "012": HarmonizationProfile("012", "template", "rhythm", "chordarp"),
    "018": HarmonizationProfile("018", "template", "rhythm", "chordarp"),
    "023": HarmonizationProfile("023", "method", "band", "functional"),
    "040": HarmonizationProfile("040", "template", "contour", "satb"),
    "079": HarmonizationProfile("079", "template", "contour", "satb"),
}


def profile_for_method(method_id: str) -> Optional[HarmonizationProfile]:
    return HARMONY_PROFILES.get(method_id)


def plan_from_method(method_id: str, key: str, section_names: Sequence[str],
                     bars_per: Sequence[int], style: str = "", seed: int = 0,
                     phase1=None) -> HarmonyPlan:
    """Derive a HarmonyPlan from a composition method's phase-1 output.

    P1. For methods with a natural ``progression``/``band`` phase-1 reading
    (002/010/023/001) this re-reads ``phase1`` as a harmonic projection. For
    ``rhythm``/``contour`` methods the profile forces ``source=template`` (no
    harmonic content in phase-1). Not implemented at P0 — raise honestly.
    """
    prof = profile_for_method(method_id)
    if prof is None:
        raise KeyError(f"no harmonisation profile for method {method_id!r}")
    if prof.source != "method":
        raise NotImplementedError(
            f"method {method_id!r} is {prof.phase_semantics}-only; harmonise "
            f"from template via {prof.harmonizer!r}, not phase-1 (P1 gap)")
    raise NotImplementedError(
        f"plan_from_method for {method_id!r} ({prof.phase_semantics}) is a P1 "
        f"adapter — not built yet")
