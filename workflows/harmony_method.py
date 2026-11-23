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

from rules.harmony import CHORD_SHAPES, KEY_OFFSET, MAJOR_DEGREES, PROGRESSIONS
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


# ---------------------------------------------------------------------------
# Module-level helpers: degree-space plan builders (P1 method adapters)
# ---------------------------------------------------------------------------

# 002/010 Markov: transition weights over the seven diatonic degrees. The same
# "state weights -> probabilistic path" character as the melodic Markov adapter,
# applied to CHORD space instead of pitch_index.
_MARKOV_TRANSITIONS = {
    "I":  [("V", 3), ("vi", 2), ("IV", 2), ("ii", 1), ("iii", 1)],
    "ii": [("V", 4), ("IV", 2), ("vii", 1), ("I", 1)],
    "iii": [("vi", 3), ("IV", 2), ("ii", 2), ("I", 1)],
    "IV": [("V", 3), ("I", 2), ("ii", 2), ("vii", 1)],
    "V":  [("I", 4), ("vi", 2), ("iii", 1)],
    "vi": [("IV", 3), ("ii", 2), ("V", 2), ("I", 1)],
    "vii": [("I", 4), ("iii", 2), ("vi", 1)],
}


def _degrees_to_plan(degrees, key: str) -> HarmonyPlan:
    """Roman-numeral degree list -> per-bar Chord plan (root in bass octave)."""
    off = KEY_OFFSET.get(key, 0)
    chords = []
    for deg in degrees:
        root_iv, qual = CHORD_SHAPES.get(deg, CHORD_SHAPES["I"])
        chords.append(Chord(root_midi=48 + off + root_iv, quality=qual,
                            degree=deg))
    return HarmonyPlan(chords=tuple(chords))


def _force_cadence(degrees) -> list:
    """Close the progression V -> I (last two bars)."""
    out = list(degrees)
    if len(out) >= 2:
        out[-2], out[-1] = "V", "I"
    return out


def _plan_markov(total: int, seed: int) -> list:
    """002/010: weighted Markov walk over the seven diatonic degrees."""
    rng = __import__("random").Random(seed)
    cur = "I"
    out = [cur]
    for _ in range(total - 1):
        nxt, weights = zip(*_MARKOV_TRANSITIONS[cur])
        cur = rng.choices(nxt, weights=weights)[0]
        out.append(cur)
    return _force_cadence(out)


def _plan_tendency(total: int, seed: int) -> list:
    """023: harmonic band — corridor widens mid-piece (distant degrees)."""
    rng = __import__("random").Random(seed)
    degrees = []
    for b in range(total):
        p = b / max(total - 1, 1)                  # 0..1 across the piece
        width = 0.15 + 0.7 * (1 - abs(2 * p - 1))  # narrow ends, wide middle
        band = rng.uniform(-width, width)          # position inside the corridor
        idx = int(round(3 + band * 3))             # 0..6 -> degree index
        degrees.append(MAJOR_DEGREES[max(0, min(6, idx))])
    return _force_cadence(degrees)


def _plan_skeleton(total: int, seed: int) -> list:
    """001: strong bars = I, weak bars = passing chord (IV/vi)."""
    rng = __import__("random").Random(seed)
    degrees = []
    for b in range(total):
        if b % 4 in (0, 2):                        # strong bars -> tonic
            degrees.append("I")
        else:                                      # weak bars -> passing
            degrees.append(rng.choice(["IV", "vi"]))
    return _force_cadence(degrees)


_METHOD_PLAN_BUILDERS = {
    "001": _plan_skeleton,
    "002": _plan_markov,
    "010": _plan_markov,     # Hierarchical Diffusion — Markov base
    "023": _plan_tendency,
}


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
        total = sum(bars_per)
        degrees = [prog[b % len(prog)] for b in range(total)]
        return _degrees_to_plan(degrees, key)

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
    """Derive a HarmonyPlan from a composition method (P1).

    For ``source="method"`` methods (001/002/010/023) this re-runs the method's
    characteristic process over CHORD space — Markov transition weights -> degree
    walk, tendency corridor -> harmonic band, skeleton strong/weak -> I vs
    passing — then forces a V->I cadence. The phase-1 RawNote cloud encodes
    MELODY (a pitch_index walk, not a progression), so the builders re-apply the
    method's process to degree space rather than reverse-engineer a progression
    from a melodic walk (that reverse-engineering is lossy + register-dependent).

    For ``source="template"`` methods (rhythm/contour: 012/018/040/079/003) the
    phase-1 has no harmonic content, so this falls back to the profile's
    template harmoniser — the "without phase-1" path.
    """
    prof = profile_for_method(method_id)
    if prof is None:
        raise KeyError(f"no harmonisation profile for method {method_id!r}")
    if prof.source != "method":
        return HARMONIZERS[prof.harmonizer]().plan(
            key, section_names, bars_per, style, seed)
    builder = _METHOD_PLAN_BUILDERS.get(method_id)
    if builder is None:
        raise NotImplementedError(
            f"plan_from_method for {method_id!r} ({prof.phase_semantics}) not built")
    degrees = builder(sum(bars_per), seed or 0)
    return _degrees_to_plan(degrees, key)
