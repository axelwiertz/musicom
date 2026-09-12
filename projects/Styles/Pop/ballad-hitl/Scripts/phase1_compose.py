# -*- coding: utf-8 -*-
"""Phase 1: Pop Ballad — framework + per-part method variation (MIDI).

Composition methods used (methods_db.md):
  Framework (Path C middle-out):
    001 Skeleton-First Refinement   — intro/verse/chorus/bridge/outro form
    012 Euclidean Groove Locking    — bass anchor groove (Bjorklund)
    018 Schillinger System          — bass accent density resultants (3/4)
    023 Tendency Masking            — lead bounded walk over chord tones
  Per-part swaps (SAME framework, SAME base patterns):
    Intro  -> 001 Skeleton-First     (sparse held tones)
    Verse  -> 004 Prosodic Narrative (lyrical contour, rests)
    Chorus -> 011 Voice-Leading Graph(nearest-chord-tone leaps, octave lift)
    Bridge -> 023 Tendency Masking   (tension walk, wide intervals)
    Outro  -> 013 Inversion/Retrograde (motif retrograde, resolve)

Instrumentation is a BALLAD palette, chosen per ROLE (lead / pad / bass /
texture / percussion) from style-appropriate pools — not a generic pop stack.
Every instrument is range-checked against the register each layer writes
(the old default put the arp at 50-60, below the clarinet's 52 floor).

Engine-only: UnitMatrixComposer, zero-drift validate(), provenance sidecar.
"""
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional, Tuple

from structures import MusicUnit, MusicEvent, MidiInstrument
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.paths import (
    build_framework, POP_FORM, PROGRESSIONS, KEY_OFFSET, MAJOR_DEGREES,
    progression_roots as engine_progression_roots,
)
from workflows.provenance import write_provenance, AI_ASSISTED
from visualization.grid import write_grid_visualization

BAR = 1920
PROJECT = Path("/opt/data/repos/musicom/projects/Styles/Pop/ballad-hitl")
MIDI_DIR = PROJECT / "MIDI"
MIDI_DIR.mkdir(parents=True, exist_ok=True)

KEY = "Dm"         # D minor ballad — explicit 'm' suffix drives mode inference
BPM = 72           # slow ballad
SEED = 7

FORM = [
    ("Intro", 4),
    ("Verse", 8),
    ("Chorus", 8),
    ("Bridge", 4),
    ("Outro", 4),
]
# ballad progression: i–VI–III–VII (Dm – Bb – F – C), dramatic minor aeolian
PROG = PROGRESSIONS["minor-aeolian"]  # ['i', 'VI', 'III', 'VII']

# ---------------------------------------------------------------- registers
# The register each role writes in, as (octave shift above the chord root).
# Roots live in C2-C3 (36-48); these shifts keep every layer inside its
# chosen instrument's playable range.
REGISTER = {
    "Lead": 24,      # melody: 62-79  (violin/flute/oboe/sax)
    "Pad": 12,       # bed:    50-67  (piano/organ/guitar/dulcimer)
    "Bass": 0,       # root:   38-48  (double bass/cello/tuba/bassoon)
    "Arp": 24,       # texture:62-79  (marimba/kalimba/dulcimer/clarinet/viola)
    "Drums": 0,
}

# ------------------------------------------------------- instrumentation
# Ballad-appropriate pools per role. Every entry is range-verified against
# the register above — see tests/test_ballad_palette.py.
INSTRUMENT_POOLS = {
    "Lead": ["Violin", "Flute", "Oboe", "Alto Saxophone", "Acoustic Guitar",
             "Cello"],
    "Pad": ["Piano", "Church Organ", "Acoustic Guitar", "Dulcimer"],
    "Bass": ["Double Bass", "Cello", "Tuba", "Bassoon"],
    "Arp": ["Marimba", "Kalimba", "Dulcimer", "Clarinet", "Viola"],
    "Drums": ["Drum Kit", "Timpani"],
}

# Named palettes: one instrument per role. Rounds rotate through these so
# successive rounds are auditioned in a fresh instrumentation.
PALETTES = {
    "classic": {          # the canonical piano-and-strings ballad
        "Lead": "Violin", "Pad": "Piano", "Bass": "Cello",
        "Arp": "Viola", "Drums": "Drum Kit",
    },
    "noir": {             # jazz-tinged late-night ballad
        "Lead": "Alto Saxophone", "Pad": "Piano", "Bass": "Double Bass",
        "Arp": "Dulcimer", "Drums": "Drum Kit",
    },
    "chamber": {          # orchestral / art-song
        "Lead": "Oboe", "Pad": "Church Organ", "Bass": "Bassoon",
        "Arp": "Clarinet", "Drums": "Timpani",
    },
    "folk": {             # acoustic singer-songwriter
        "Lead": "Acoustic Guitar", "Pad": "Dulcimer", "Bass": "Double Bass",
        "Arp": "Kalimba", "Drums": "Drum Kit",
    },
}
PALETTE_ORDER = ["classic", "noir", "chamber", "folk"]
DEFAULT_PALETTE = "classic"


def palette_for_round(round_num: int) -> dict:
    """Palette mapping for a round (rotates so rounds don't sound alike)."""
    return dict(PALETTES[PALETTE_ORDER[round_num % len(PALETTE_ORDER)]])


# ---------------------------------------------------------------- variant
@dataclass
class VariantSpec:
    """One candidate's variation across MULTIPLE stems.

    The anchor (bass) is only one dimension: lead method, texture pattern,
    pad behaviour and drum level all vary too, so candidates within a round
    are audibly distinct rather than near-duplicates.
    """
    density: Optional[int] = None      # bass accents/bar (None = 3/4 default)
    offset: int = 0                    # bass tick offset (0 = on-beat)
    lead_method: Optional[str] = None  # override the per-section method
    arp_on: Optional[Tuple[str, ...]] = None   # sections with texture
    arp_rate: int = 2                  # texture notes per bar
    pad_style: str = "sustain"         # sustain | pulse
    drum_level: str = "default"        # default | soft | full | none
    palette: Optional[Dict[str, str]] = None

    def palette_map(self) -> Dict[str, str]:
        return self.palette or PALETTES[DEFAULT_PALETTE]


# ---------------------------------------------------------------- helpers
def _unit(events, section_len):
    """Terminal silent landmark (zero-drift)."""
    u = MusicUnit()
    for ev in events:
        u.add_event(ev)
    u.add_event(MusicEvent(0, 0, section_len, section_len))
    return u


def _progression_roots(progression, total_bars, key, harmonic_rhythm=1):
    """Per-bar root MIDI pitches — delegates to the canonical engine helper.

    Handles BOTH major (I/IV/V/vi) and minor-aeolian (i/VI/III/VII) spellings
    via rules.harmony.progression_roots (mode-aware). This used to be a local
    reimplementation of the engine's buggy `MAJOR_DEGREES.index(deg.upper())`
    lookup, which collapsed uppercase minor degrees (VI/III/VII) onto index 0.
    """
    return engine_progression_roots(progression, total_bars, key,
                                    harmonic_rhythm=harmonic_rhythm)


def _chord_tones(root, quality="maj", inv=0, octave=12):
    """Triad tones above root (maj or min), optional inversion + octave."""
    if quality == "min":
        tones = [0, 3, 7]
    else:
        tones = [0, 4, 7]
    tones = tones[inv:] + [t + 12 for t in tones[:inv]]
    return [root + octave + t for t in tones]


def _euclid(onsets, steps):
    """Bjorklund euclidean positions (method 012)."""
    positions = []
    buckets = [0] * steps
    for i in range(onsets):
        buckets[i * steps // onsets] = 1
    return [i for i, b in enumerate(buckets) if b]


# ---------------------------------------------------------------- fills
def _bar_onsets(density, steps=4, bar=0):
    """Euclidean onset positions for one bar at a given density.

    density 3 -> 3 accents on the quarter grid (walking)
    density 4 -> all four quarters (pulse)
    density 5 -> 5 accents on the eighth grid (syncopated drive)

    Density is clamped so every variant stays playable — a density above
    the grid size yields an empty Euclidean result (silent bar), which the
    historical engine silently dropped.
    """
    if density <= steps:
        return _euclid(max(1, density), steps), 480
    # denser than the quarter grid: move to the eighth-note grid
    return _euclid(min(density, 8), 8), 240


def fill_bass(composer, roots_per_bar, section_names, bars_per,
              density=None, offset=0):
    """Method 012 + 018: Euclidean groove-locked bass, Schillinger density.

    density (int or None): accents per bar. None keeps the original
    Schillinger 3/4 resultant alternation (byte-exact default); an int
    selects a fixed evolvable density. offset: start offset in ticks
    (0 = on-beat, 240 = off-beat).
    """
    bar = 0
    for si, sname in enumerate(section_names):
        nbars = bars_per[si]
        section_len = nbars * BAR
        evs = []
        for b in range(nbars):
            root = roots_per_bar[bar]
            d = (3 + (b % 2)) if density is None else density
            positions, step_ticks = _bar_onsets(d, bar=b)
            for p in positions:
                start = b * BAR + offset + p * step_ticks
                end = min(start + step_ticks, section_len)
                if end > start:
                    evs.append(MusicEvent(root, 95, start, end))
            bar += 1
        composer.fill_voice_section("Bass", sname, _unit(evs, section_len))


def fill_pad(composer, section_roots, section_names, bars_per, qualities,
             style="sustain"):
    """Ballad bed: sustained triad, or a pulsing half-note chord (variety).

    sustain: one held triad per section (the classic pad)
    pulse:   the triad re-attacked on each half note — a ballad pianist's
             broken-chord feel, which also gives the mix movement.
    """
    for si, sname in enumerate(section_names):
        nbars = bars_per[si]
        section_len = nbars * BAR
        root = section_roots[si]
        tones = _chord_tones(root, qualities[si], octave=REGISTER["Pad"])
        evs = []
        if style == "pulse":
            for b in range(nbars):
                for half in range(2):
                    start = b * BAR + half * 960
                    for t in tones:
                        evs.append(MusicEvent(t, 48, start, start + 900))
        else:
            evs = [MusicEvent(t, 55, 0, section_len) for t in tones]
        composer.fill_voice_section("Pad", sname, _unit(evs, section_len))


def fill_drums(composer, section_names, bars_per, dense, kit="Drum Kit",
               roots_per_bar=None):
    """Backbeat grid — kick 1&3, snare 2&4, hats 8ths (ballad: soft).

    kit="Drum Kit" writes GM percussion on channel 9. kit="Timpani" is a
    PITCHED orchestral option: it plays the bar's chord root on the downbeat
    and the fifth on beat 3 (channel 0, program 47).
    """
    for si, sname in enumerate(section_names):
        nbars = bars_per[si]
        section_len = nbars * BAR
        evs = []
        if kit.lower() == "timpani":
            for b in range(nbars):
                bs = b * BAR
                root = (roots_per_bar or [38])[
                    min(si * nbars + b, len(roots_per_bar or [38]) - 1)]
                if dense[si] > 0:
                    evs.append(MusicEvent(root, 88, bs, bs + 480))
                    evs.append(MusicEvent(root + 7, 78, bs + 960, bs + 1440))
            composer.fill_voice_section("Drums", sname, _unit(evs, section_len))
            continue

        kick_v, snare_v, hat_v = 90, 80, 45
        if dense[si] == 0:
            kick_v, snare_v, hat_v = 0, 0, 0
        elif dense[si] < 50:
            kick_v, snare_v, hat_v = 70, 60, 35
        for b in range(nbars):
            bs = b * BAR
            if kick_v:
                evs.append(MusicEvent(36, kick_v, bs, bs + 120))
                evs.append(MusicEvent(38, snare_v, bs + 960, bs + 1080))
            if hat_v:
                for h in range(8):
                    evs.append(MusicEvent(42, hat_v, bs + h * 240,
                                          bs + h * 240 + 120))
        composer.fill_voice_section("Drums", sname, _unit(evs, section_len))


def _lead_section(root, quality, nbars, section_len, method, rng, sname,
                  octave):
    """One section's lead line for a given composition method."""
    evs = []
    tones = _chord_tones(root, quality, octave=octave)

    if method == "001":      # Skeleton-First: sparse held tones
        for b in range(nbars):
            note = tones[b % len(tones)]
            evs.append(MusicEvent(note, 80, b * BAR, b * BAR + BAR))

    elif method == "015":    # Ostinato Constraint: fixed loop
        for b in range(nbars):
            for i, t in enumerate([0, 2, 1]):
                evs.append(MusicEvent(tones[t], 78, b * BAR + i * 640,
                                      b * BAR + i * 640 + 320))

    elif method == "004":    # Prosodic Narrative: lyrical contour, rests
        for b in range(nbars):
            idx = b % 16
            # rise-fall phrase (syllable stress mapping)
            shape = [0, 1, 2, 1, 0, 2, 1, 0, 1, 2, 1, 2, 1, 0, 1, 0]
            nxt = tones[min(len(tones) - 1, shape[idx] % len(tones))]
            off = 0 if b % 2 == 0 else 480
            evs.append(MusicEvent(nxt, 88, b * BAR + off,
                                  b * BAR + off + 480))

    elif method == "011":    # Voice-Leading Graph: nearest-chord leaps
        cur = tones[0]
        for b in range(nbars):
            nxt = min(tones, key=lambda p: abs(p - cur))
            evs.append(MusicEvent(nxt, 92, b * BAR, b * BAR + 480))
            if b % 2 == 1:
                evs.append(MusicEvent(nxt + 12, 84, b * BAR + 960,
                                      b * BAR + 1440))
            cur = nxt

    elif method == "023":    # Tendency Masking: bounded tension walk
        cur = tones[0]
        for b in range(nbars):
            nearest = min(tones, key=lambda p: abs(p - cur))
            if rng.random() < 0.5:
                nxt = nearest
            else:
                nxt = cur + rng.choice([-3, -2, 2, 3, 5])
            nxt = max(tones[0] - 5, min(tones[-1] + 12, nxt))
            evs.append(MusicEvent(nxt, 90, b * BAR, b * BAR + 960))
            cur = nxt

    elif method == "013":    # Inversion/Retrograde: motif backwards
        motif = [0, 4, 7, 12, 9, 5, 2, -2]
        if sname == "Outro":
            motif = motif[::-1]              # retrograde
        for b in range(nbars):
            note = tones[abs(motif[b % len(motif)]) % len(tones)]
            evs.append(MusicEvent(note, 82, b * BAR, b * BAR + 720))

    else:                    # fallback: hold the root
        evs.append(MusicEvent(tones[0], 80, 0, section_len))

    return evs


def fill_lead(composer, rng, section_roots, section_names, bars_per,
              qualities, methods, octave=24):
    """Per-part lead using DIFFERENT composition methods (same framework)."""
    for si, sname in enumerate(section_names):
        nbars = bars_per[si]
        section_len = nbars * BAR
        evs = _lead_section(section_roots[si], qualities[si], nbars,
                            section_len, methods[si], rng, sname, octave)
        composer.fill_voice_section("Lead", sname, _unit(evs, section_len))


def fill_arp(composer, section_roots, section_names, bars_per, qualities, on,
             rate=2, octave=24):
    """Texture arpeggio (L1 micro) — only in the chosen sections.

    rate = notes per bar (2 = half notes, 4 = quarters). The register sits
    an octave above the chord root so it clears every texture instrument's
    floor (the historical default wrote 50-60, below the clarinet's 52).
    """
    for si, sname in enumerate(section_names):
        nbars = bars_per[si]
        section_len = nbars * BAR
        if not on.get(sname, False):
            composer.fill_voice_section("Arp", sname, _unit([], section_len))
            continue
        root = section_roots[si]
        tones = _chord_tones(root, qualities[si], octave=octave)
        evs = []
        step = BAR // max(1, rate)
        for b in range(nbars):
            for q in range(rate):
                note = tones[(b * rate + q) % len(tones)]
                start = b * BAR + q * step
                evs.append(MusicEvent(note, 55, start, start + step // 2))
        composer.fill_voice_section("Arp", sname, _unit(evs, section_len))


# ---------------------------------------------------------------- main

# Per-section harmonic REGIONS (ballad arc) — not one global loop.
# Intro frames i-VI, Verse walks the full aeolian cycle low, Chorus lifts
# on III-VII, Bridge peaks on VII-VI, Outro resolves home. Each section
# gets its own 2-bar harmonic rhythm.
SECTION_PROGS = [
    ["i", "VI"],                    # Intro
    ["i", "VI", "III", "VII"],      # Verse
    ["III", "VII", "i", "VI", "III", "VII"],  # Chorus
    ["VII", "VI", "III", "VII"],    # Bridge
    ["i", "VI", "i", "i"],          # Outro
]

# Per-part lead method swaps (same framework, same base patterns).
LEAD_METHODS = {
    "Intro": "001",     # skeleton sparse
    "Verse": "004",     # prosodic lyrical
    "Chorus": "011",    # voice-leading leaps
    "Bridge": "023",    # tendency tension
    "Outro": "013",     # retrograde motif
}

ARP_ON = {"Intro": False, "Verse": True, "Chorus": True,
          "Bridge": False, "Outro": False}
DRUM_DENSITY = [0, 45, 70, 30, 0]      # intro/outro silent
DRUM_LEVELS = {
    "none": [0, 0, 0, 0, 0],
    "soft": [0, 35, 50, 25, 0],
    "default": DRUM_DENSITY,
    "full": [0, 60, 85, 45, 0],
}


def ballad_harmony(form=None, key=None):
    """(section_roots, qualities, roots_per_bar) for the ballad form.

    Derived entirely from SECTION_PROGS via the canonical mode-aware
    engine helper — no hardcoded root lists.
    """
    form = form or FORM
    key = key or KEY
    roots_per_bar, section_roots = [], []
    cursor = 0
    for si, (sname, nbars) in enumerate(form):
        prog = SECTION_PROGS[si % len(SECTION_PROGS)]
        roots_per_bar.extend(_progression_roots(prog, nbars, key,
                                                harmonic_rhythm=2))
        section_roots.append(roots_per_bar[cursor + nbars // 2])
        cursor += nbars
    mid_deg = [SECTION_PROGS[si % len(SECTION_PROGS)][(nbars // 2 // 2)
               % len(SECTION_PROGS[si % len(SECTION_PROGS)])]
               for si, (sname, nbars) in enumerate(form)]
    qualities = ["min" if d in ("i", "iv", "v") else "maj" for d in mid_deg]
    return section_roots, qualities, roots_per_bar


def build_ballad(seed=None, variant=None, density=None, offset=0, form=None,
                 key=None):
    """Build the full ballad composer (framework + per-part method swaps).

    seed    : RNG seed for the tendency-masking lead (method 023)
    variant : a VariantSpec controlling ALL evolvable stems (anchor, lead
              method, texture, pad style, drums, palette). Individual
              density/offset kwargs still work for convenience and override
              the spec.
    """
    form = form or FORM
    key = key or KEY
    section_names = [s[0] for s in form]
    bars_per = [s[1] for s in form]
    seed = SEED if seed is None else seed
    rng = random.Random(seed)
    spec = variant or VariantSpec()
    if density is not None:
        spec.density = density
    spec.offset = offset

    palette = spec.palette_map()
    section_roots, qualities, roots_per_bar = ballad_harmony(form, key)

    voices = [(role, palette[role]) for role in
              ("Lead", "Pad", "Bass", "Arp", "Drums")]
    composer = build_framework(style="pop", key=key, bpm=BPM, form=form,
                               seed=seed, voices=voices)

    # --- percussion ---
    kit = palette["Drums"]
    dense = DRUM_LEVELS.get(spec.drum_level, DRUM_DENSITY)
    fill_drums(composer, section_names, bars_per, dense, kit=kit,
               roots_per_bar=roots_per_bar)

    # --- anchor (bass) ---
    fill_bass(composer, roots_per_bar, section_names, bars_per,
              density=spec.density, offset=spec.offset)

    # --- bed ---
    fill_pad(composer, section_roots, section_names, bars_per, qualities,
             style=spec.pad_style)

    # --- lead (per-section method swaps, optionally overridden) ---
    if spec.lead_method:
        methods = [spec.lead_method] * len(section_names)
    else:
        methods = [LEAD_METHODS[s] for s in section_names]
    fill_lead(composer, rng, section_roots, section_names, bars_per,
              qualities, methods, octave=REGISTER["Lead"])

    # --- texture ---
    if spec.arp_on is None:
        arp_on = dict(ARP_ON)
    else:
        arp_on = {s: (s in spec.arp_on) for s in section_names}
    fill_arp(composer, section_roots, section_names, bars_per, qualities,
             on=arp_on, rate=spec.arp_rate, octave=REGISTER["Arp"])

    composer.ballad_spec = spec          # type: ignore[attr-defined]
    composer.ballad_palette = palette    # type: ignore[attr-defined]
    return composer


def main():
    spec = VariantSpec(palette=PALETTES[DEFAULT_PALETTE])
    composer = build_ballad(seed=SEED, variant=spec)

    # ---- zero-drift gate ----
    ok, msg = composer.validate()
    assert ok, f"validate failed: {msg}"

    midi_path = MIDI_DIR / "pop-ballad-hitl.mid"
    composer.to_midi(str(midi_path))
    assert midi_path.stat().st_size > 40

    section_names = [s[0] for s in FORM]
    section_roots, qualities, _ = ballad_harmony()

    # provenance
    prov = write_provenance(
        artifact_path=str(midi_path),
        classification=AI_ASSISTED,
        generator="pop-ballad-hitl phase1 (paths.build_framework + per-part methods)",
        sources=[f"style:pop-ballad", f"key:{KEY}", f"bpm:{BPM}",
                 f"progression:{','.join(PROG)}", "path:C middle-out",
                 "methods:001,012,018,015,004,011,023,013",
                 "palette:" + ",".join(f"{k}={v}" for k, v in
                                       composer.ballad_palette.items())],
        parameters={"seed": SEED, "form": str(FORM),
                    "lead_methods": LEAD_METHODS,
                    "palette": composer.ballad_palette},
    )
    # grid viz
    write_grid_visualization(composer.matrix,
                             str(PROJECT / "Analysis" / "grid_phase1.txt"))

    print(f"OK {midi_path} ({midi_path.stat().st_size} B)")
    print(f"provenance: {prov}")
    print(f"sections: {section_names} bars: {[s[1] for s in FORM]}")
    print(f"roots: {section_roots} qualities: {qualities}")
    print(f"palette: {composer.ballad_palette}")


if __name__ == "__main__":
    main()
