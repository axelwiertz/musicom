# -*- coding: utf-8 -*-
"""Method contract — the missing piece of the cell engine (Phase 4 P0).

METHOD_CONTRACT_PLAN.md (§2): the cell engine can FILL cells, but nothing yet
drives it with a METHOD. This module defines the contract the method must
satisfy so the realization spine (``workflows.realize_spine``) can turn raw
method output into a validated ``MusicUnit``.

The two-stage contract (fork 3 of VOICE_ROLE_WORKFLOW_PLAN):

    resolve_role(ctx) -> role        # the METHOD decides the voice's role FIRST
    generate(ctx, role) -> notes     # then emits raw / realized material

``RawNote`` is the genuinely-raw note (unquantized pitch_index + onset, exactly
what a phase-1 draft is made of). ``DefaultMethod`` wraps the P0 legacy fillers
(already grid-locked + in-scale + in-chord) so ``compose()`` stays byte-identical
when the spine is adopted. ``registry_method()`` resolves a method ID to a
``CellMethod`` — and is honest about the spec-only / not-yet-adapted cases.

Uses only the musicom engine. No mido authoring, no ad-hoc arrays.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Protocol, Sequence, Union

from structures import MusicEvent

from workflows.cell_engine import ROLE_FILLERS, CellContext, default_resolve_role

__all__ = [
    "RawNote", "MethodOutput", "CellMethod", "DefaultMethod", "registry_method",
]


@dataclass(frozen=True)
class RawNote:
    """A genuinely raw note — unquantized, method character preserved.

    ``pitch_index`` is a [0,1] pitch height (NOT a MIDI pitch); the realization
    spine maps it into the cell register and snaps it to scale/chord. ``onset``
    may be fractional (off-grid) — the spine grid-locks it. This is the same
    shape the two-phase architecture's phase-1 draft already produces.
    """
    pitch_index: float = 0.5
    onset: float = 0.0
    velocity: int = 100


# A method's generate() output is EITHER raw (RawNote -> the spine snaps it) OR
# already-realized (MusicEvent -> the spine passes it through). DefaultMethod
# emits the latter because the legacy fillers ARE the realization.
MethodOutput = Union[RawNote, MusicEvent]


class CellMethod(Protocol):
    """The method contract (structural — not enforced at runtime).

    Any object with ``resolve_role`` + ``generate`` is a CellMethod. Markov,
    tendency-masking, serial, FHN — interchangeable because the spine doesn't
    care how the raw material was produced.
    """

    def resolve_role(self, ctx: CellContext) -> str: ...

    def generate(self, ctx: CellContext, role: str) -> Sequence[MethodOutput]: ...


class DefaultMethod:
    """The P0 legacy fillers exposed as a CellMethod (already-realized output).

    ``generate()`` returns the legacy filler events directly as ``MusicEvent``
    (grid-locked, in-scale, in-chord) — the fillers ARE the realization, so the
    spine passes them through unchanged. This is what keeps ``compose()``
    byte-identical when the spine is adopted.
    """

    def resolve_role(self, ctx: CellContext) -> str:
        role = default_resolve_role(ctx.voice_idx, ctx.instrument_name, ctx)
        if role is None:
            raise ValueError(
                f"no role for voice {ctx.voice_idx!r} "
                f"instrument {ctx.instrument_name!r}")
        return role

    def generate(self, ctx: CellContext, role: str) -> List[MusicEvent]:
        if role not in ROLE_FILLERS:
            raise KeyError(f"unknown role {role!r}; available: {sorted(ROLE_FILLERS)}")
        return ROLE_FILLERS[role](ctx)


def registry_method(method_id: str) -> CellMethod:
    """Resolve a method ID to a CellMethod, or explain exactly why not.

    - ``"default"`` -> ``DefaultMethod`` (the legacy fillers).
    - an implemented concrete method (001/002/003/010/012/018/023/040/079) ->
      its ``CellMethod`` adapter; adapters land in P1, so for now this raises
      ``NotImplementedError`` naming the gap.
    - a spec-only method (026/048/065/...) -> no code -> raises ``KeyError`` or
      ``NotImplementedError`` (the cron's bespoke ``generate()`` is the
      realization for those).
    """
    if method_id == "default":
        return DefaultMethod()

    from generators.generator_registry import GENERATOR_REGISTRY
    if method_id not in GENERATOR_REGISTRY:
        raise KeyError(
            f"method {method_id!r} is not in generator_registry "
            f"(spec-only, no shared code). The composition cron's bespoke "
            f"generate() is the realization for these methods.")
    mod_path, class_name, _ = GENERATOR_REGISTRY[method_id]
    if mod_path is None:
        raise NotImplementedError(
            f"method {method_id!r} is spec-only (no code) — cannot adapt to a "
            f"CellMethod.")
    raise NotImplementedError(
        f"method {method_id!r} has code ({mod_path}.{class_name or ''}) but no "
        f"CellMethod adapter yet — lands in P1.")
