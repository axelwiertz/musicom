# -*- coding: utf-8 -*-
"""Phase 1: Pop Ballad — framework + per-part method variation (MIDI).

Composition methods used (methods_db.md):
  Framework (Path C middle-out):
    001 Skeleton-First Refinement   — intro/verse/chorus/bridge/outro form
    012 Euclidean Groove Locking    — bass anchor groove (Bjorklund)
    018 Schillinger System          — bass accent density resultants (3/4)
    023 Tendency Masking            — lead bounded walk over chord tones
  Per-part swaps (SAME framework, SAME base patterns):
    Intro  -> 015 Ostinato Constraint (sparse loop, 1 chord per bar)
    Verse  -> 004 Prosodic Narrative Coupling (lyrical contour, 8th rests)
    Chorus -> 011 Voice-Leading Graph (nearest-chord-tone leaps, octave lift)
    Bridge -> 023 Tendency Masking (tension walk, wide intervals)
    Outro  -> 013 Inversion/Retrograde (motif retrograde, fade to root)

Engine-only: UnitMatrixComposer, zero-drift validate(), provenance sidecar.
"""
import random
from pathlib import Path

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


def _chord_tones(root, quality="maj", inv=0):
    """Triad tones above root (maj or min), optional inversion offset."""
    if quality == "min":
        tones = [0, 3, 7]
    else:
        tones = [0, 4, 7]
    tones = tones[inv:] + [t + 12 for t in tones[:inv]]
    return [root + 12 + t for t in tones]


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


def fill_pad(composer, section_roots, section_names, bars_per, qualities):
    """Sustained triad per section (ballad bed)."""
    for si, sname in enumerate(section_names):
        nbars = bars_per[si]
        section_len = nbars * BAR
        root = section_roots[si]
        tones = _chord_tones(root, qualities[si])
        evs = [MusicEvent(t, 55, 0, section_len) for t in tones]
        composer.fill_voice_section("Pad", sname, _unit(evs, section_len))


def fill_drums(composer, section_names, bars_per, dense):
    """Backbeat grid — kick 1&3, snare 2&4, hats 8ths (ballad: soft)."""
    for si, sname in enumerate(section_names):
        nbars = bars_per[si]
        section_len = nbars * BAR
        evs = []
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
                    evs.append(MusicEvent(42, hat_v, bs + h * 240, bs + h * 240 + 120))
        composer.fill_voice_section("Drums", sname, _unit(evs, section_len))


def fill_lead(composer, rng, section_roots, section_names, bars_per,
              qualities, methods):
    """Per-part lead using DIFFERENT composition methods (same framework)."""
    for si, sname in enumerate(section_names):
        nbars = bars_per[si]
        section_len = nbars * BAR
        root = section_roots[si]
        method = methods[si]
        evs = []

        if method == "001":      # Skeleton-First: sparse held tones
            tones = _chord_tones(root, qualities[si])
            for b in range(nbars):
                note = tones[b % len(tones)]
                evs.append(MusicEvent(note + 12, 80, b * BAR, b * BAR + BAR))
            notes_per_bar = 1

        elif method == "015":    # Ostinato Constraint: fixed loop
            tones = _chord_tones(root, qualities[si])
            for b in range(nbars):
                for i, t in enumerate([0, 2, 1]):
                    evs.append(MusicEvent(tones[t] + 12, 78,
                                          b * BAR + i * 640,
                                          b * BAR + i * 640 + 320))
            notes_per_bar = 3

        elif method == "004":    # Prosodic Narrative: lyrical contour, rests
            tones = _chord_tones(root, qualities[si])
            cur = tones[1] + 12
            # contour: rise-fall phrase (syllable stress mapping)
            contour = [0, 1, 2, 1, 0, -1, 0, 1, 2, 3, 2, 1, 0, -1, 0, 1]
            for b in range(nbars):
                idx = b % len(contour)
                nxt = tones[min(len(tones) - 1, max(0, idx % len(tones)))] + 12
                if b % 2 == 0:
                    evs.append(MusicEvent(nxt, 88, b * BAR, b * BAR + 480))
                else:
                    evs.append(MusicEvent(nxt, 88, b * BAR + 480, b * BAR + 960))
            notes_per_bar = 2

        elif method == "011":    # Voice-Leading Graph: nearest-chord leaps
            tones = _chord_tones(root, qualities[si])
            cur = tones[0] + 12
            for b in range(nbars):
                nxt = min(tones, key=lambda p: abs(p + 12 - cur))
                evs.append(MusicEvent(nxt + 12, 92, b * BAR, b * BAR + 480))
                if b % 2 == 1:
                    evs.append(MusicEvent(nxt + 24, 84, b * BAR + 960,
                                          b * BAR + 1440))
                cur = nxt + 12
            notes_per_bar = 2

        elif method == "023":    # Tendency Masking: bounded tension walk
            tones = _chord_tones(root, qualities[si])
            cur = tones[0] + 12
            for b in range(nbars):
                nearest = min(tones, key=lambda p: abs(p + 12 - cur))
                if rng.random() < 0.5:
                    nxt = nearest + 12
                else:
                    nxt = cur + rng.choice([-3, -2, 2, 3, 5])
                nxt = max(tones[0] + 7, min(tones[-1] + 24, nxt))
                evs.append(MusicEvent(nxt, 90, b * BAR, b * BAR + 960))
                cur = nxt
            notes_per_bar = 1

        elif method == "013":    # Inversion/Retrograde: motif backwards
            motif = [0, 4, 7, 12, 9, 5, 2, -2]   # arpeggio rise + fall
            tones = _chord_tones(root, qualities[si])
            if sname == "Outro":
                motif = motif[::-1]              # retrograde
            for b in range(nbars):
                note = tones[abs(motif[b % len(motif)]) % len(tones)] + 12
                evs.append(MusicEvent(note, 82, b * BAR, b * BAR + 720))
            notes_per_bar = 1

        else:
            notes_per_bar = 1
            tones = _chord_tones(root, qualities[si])
            evs.append(MusicEvent(tones[0] + 12, 80, 0, section_len))

        composer.fill_voice_section("Lead", sname, _unit(evs, section_len))


def fill_arp(composer, section_roots, section_names, bars_per, qualities, on):
    """16th arpeggio texture (L1 micro) — only in dense sections."""
    for si, sname in enumerate(section_names):
        nbars = bars_per[si]
        section_len = nbars * BAR
        if not on.get(sname, False):
            composer.fill_voice_section("Arp", sname, _unit([], section_len))
            continue
        root = section_roots[si]
        tones = _chord_tones(root, qualities[si])
        evs = []
        for b in range(nbars):
            for q in range(2):
                note = tones[(b + q) % len(tones)]
                evs.append(MusicEvent(note, 55, b * BAR + q * 960,
                                      b * BAR + q * 960 + 480))
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


def build_ballad(seed=None, density=None, offset=0, form=None, key=None):
    """Build the full ballad composer (framework + per-part method swaps).

    seed            : RNG seed for the tendency-masking lead (method 023)
    density/offset  : anchor (bass) variant parameters — the HITL search
                      space. density=None keeps the original 3/4 alternation.
    """
    form = form or FORM
    key = key or KEY
    section_names = [s[0] for s in form]
    bars_per = [s[1] for s in form]
    seed = SEED if seed is None else seed
    rng = random.Random(seed)

    section_roots, qualities, roots_per_bar = ballad_harmony(form, key)

    composer = build_framework(style="pop", key=key, bpm=BPM, form=form,
                               seed=seed)
    fill_drums(composer, section_names, bars_per, dense=DRUM_DENSITY)
    fill_bass(composer, roots_per_bar, section_names, bars_per,
              density=density, offset=offset)
    fill_pad(composer, section_roots, section_names, bars_per, qualities)
    fill_lead(composer, rng, section_roots, section_names, bars_per,
              qualities, [LEAD_METHODS[s] for s in section_names])
    fill_arp(composer, section_roots, section_names, bars_per, qualities,
             on=ARP_ON)
    return composer


def main():
    composer = build_ballad(seed=SEED)

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
                 "methods:001,012,018,015,004,011,023,013"],
        parameters={"seed": SEED, "form": str(FORM),
                    "lead_methods": LEAD_METHODS},
    )
    # grid viz
    write_grid_visualization(composer.matrix,
                             str(PROJECT / "Analysis" / "grid_phase1.txt"))

    print(f"OK {midi_path} ({midi_path.stat().st_size} B)")
    print(f"provenance: {prov}")
    print(f"sections: {section_names} bars: {[s[1] for s in FORM]}")
    print(f"roots: {section_roots} qualities: {qualities}")


if __name__ == "__main__":
    main()
