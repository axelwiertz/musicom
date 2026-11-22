# -*- coding: utf-8 -*-
"""319-sinterklaasavond — Sinterklaas liedje #2 through the musicom engine.

Style 'sinterklaas', G major, 100 BPM, 4/4 (gentler 'evening' character).

METHOD-DRIVEN MELODY (two-phase architecture):
  Phase 1 (composition method 023 Tendency Masking): the melody is generated
  by ``generators.tendency_masking.TendencyMaskingGenerator`` inside a singable
  register envelope (G4..F#5) — the 'tendency mask' keeps a children's tune in
  a singable corridor. Raw, stochastic-within-bounds.
  Phase 2 (musicom rules post-processing): strong beats (1 & 3) snap to the
  bar's chord tone (I-IV-V in G); every note is re-clamped to the nearest
  scale pitch within a 3rd of the previous note (conjunct/singable), keeping
  the melody diatonic + stepwise.

ACCOMPANIMENT = the style's rules layer (same as #1): tuba oom-pah bass,
celesta sustained pad, glockenspiel 8th bell arp, light march kit.

Production method (render.py): SP-032 FDN Reverb (warm hall) over the
FluidSynth render, then master to -16 LUFS.

Harmony (G major):
  Intro:   G G G G
  Verse:   G G C D | G C D G
  Verse2:  G G C D | G C D G
  Outro:   G G G G  (pedal, progressive dropout)
"""

from __future__ import annotations

import json
import os
import random

from structures import MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.cell_engine import _unit_from_events
from workflows.humanize import export_dual
from generators.tendency_masking import TendencyMaskingGenerator

# ----------------------------------------------------------------------------
# Constants (G major)
# ----------------------------------------------------------------------------
BPM = 100
TPB = 480
BPB = 4
BAR = TPB * BPB            # 1920
SEED = 319
STYLE = "sinterklaas"
KEY = "G"
FORM = "intro-verse-verse-outro"

PROG = {"Lead": 74, "Pad": 8, "Bass": 58, "Arp": 9, "Drums": 0}
CHAN = {"Lead": 0, "Pad": 0, "Bass": 0, "Arp": 0, "Drums": 9}

# bass octave roots + fifths
ROOT = {"G": 43, "C": 48, "D": 50}
PAD = {"G": (55, 59, 62), "C": (60, 64, 67), "D": (62, 66, 69)}
ARP = {"G": (55, 59, 62, 67), "C": (60, 64, 67, 72), "D": (62, 66, 69, 74)}
# melody-octave chord tones (for phase-2 strong-beat snap)
MEL_CHORD = {"G": (67, 71, 74), "C": (67, 72, 76), "D": (69, 74, 78)}

# G-major scale in the melody register (G4..F#5)
G_SCALE = [67, 69, 71, 72, 74, 76, 78]

CHORDS = {
    "Intro":  ["G"] * 4,
    "Verse":  ["G", "G", "C", "D", "G", "C", "D", "G"],
    "Verse2": ["G", "G", "C", "D", "G", "C", "D", "G"],
    "Outro":  ["G"] * 4,
}


# ----------------------------------------------------------------------------
# Voice builders (accompaniment = rules layer)
# ----------------------------------------------------------------------------
def pad_events(bars, chords):
    evs = []
    for b in range(bars):
        base = b * BAR
        for p in PAD[chords[b]]:
            evs.append(MusicEvent(p, 60, base, base + BAR))
    return evs


def bass_events(bars, chords):
    evs = []
    for b in range(bars):
        r = ROOT[chords[b]]
        base = b * BAR
        evs.append(MusicEvent(r, 88, base, base + 420))
        evs.append(MusicEvent(r + 7, 80, base + 480, base + 840))
        evs.append(MusicEvent(r, 88, base + 960, base + 1380))
        evs.append(MusicEvent(r + 7, 80, base + 1440, base + 1800))
    return evs


def arp_events(bars, chords):
    evs = []
    for b in range(bars):
        tones = ARP[chords[b]]
        base = b * BAR
        for e in range(8):
            evs.append(MusicEvent(tones[e % 4], 62, base + e * 240, base + e * 240 + 230))
    return evs


def drums_events(bars):
    evs = []
    for b in range(bars):
        base = b * BAR
        for beat in (0, 2):
            evs.append(MusicEvent(36, 82, base + beat * 480, base + beat * 480 + 100))
        for beat in (1, 3):
            evs.append(MusicEvent(38, 74, base + beat * 480, base + beat * 480 + 90))
        for e in range(8):
            evs.append(MusicEvent(42, 40, base + e * 240, base + e * 240 + 70))
    return evs


# ----------------------------------------------------------------------------
# METHOD 023 — Tendency Masking melody (two-phase)
# ----------------------------------------------------------------------------
def melody_events_023(section, seed):
    """Phase 1: Tendency Masking inside a singable corridor (G4..F#5).
    Phase 2: strong beats -> chord tones; conjunct clamp (<= a 3rd step)."""
    chords = CHORDS[section]
    bars = len(chords)
    section_len = bars * BAR

    random.seed(seed)
    gen = TendencyMaskingGenerator(key_pitches=G_SCALE)
    raw = gen.generate_voice_section(
        section_ticks=section_len, step_ticks=480,
        bounds_start=(67, 76), bounds_end=(67, 76),
        density=0.85, volume=88,
    )

    out = []
    prev = None
    for ev in raw.events:
        if ev.pitch == 0:            # terminal landmark — pass through
            out.append(ev)
            continue
        p = ev.pitch
        bar = min(ev.start_tick // BAR, bars - 1)
        # phase 2a: strong beat (1 or 3) -> nearest chord tone
        if ev.start_tick % BAR in (0, 960):
            p = min(MEL_CHORD[chords[bar]], key=lambda t: abs(t - p))
        # phase 2b: conjunct clamp (nearest scale pitch within a 3rd of prev)
        if prev is not None and abs(p - prev) > 4:
            cands = [s for s in G_SCALE if abs(s - prev) <= 4]
            p = min(cands, key=lambda s: abs(s - p))
        out.append(MusicEvent(p, ev.volume, ev.start_tick, ev.end_tick))
        prev = p
    return out


# ----------------------------------------------------------------------------
# Fill one section
# ----------------------------------------------------------------------------
def fill_section(composer, section, mode):
    chords = CHORDS[section]
    bars = len(chords)
    section_len = bars * BAR

    lead = melody_events_023(section, seed=SEED + {"Intro": 0, "Verse": 1,
                                                   "Verse2": 2, "Outro": 3}[section])
    pad = pad_events(bars, chords)

    if mode == "intro":
        # instrumental bell intro — no melody, no bass, no drums
        lead, bass, arp, drums = [], [], arp_events(bars, chords), []
    elif mode == "outro":
        bass = bass_events(1, chords[:1])
        drums = drums_events(1)
        arp = arp_events(2, chords[:2])
    else:
        bass = bass_events(bars, chords)
        arp = arp_events(bars, chords)
        drums = drums_events(bars)

    cells = {"Lead": lead, "Pad": pad, "Bass": bass, "Arp": arp, "Drums": drums}
    for vname, evs in cells.items():
        composer.fill_voice_section(vname, section, _unit_from_events(evs, section_len))


# ----------------------------------------------------------------------------
# Compose + export (dual)
# ----------------------------------------------------------------------------
def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    midi_dir = os.path.join(out_dir, "MIDI")
    os.makedirs(midi_dir, exist_ok=True)
    base = os.path.join(midi_dir, "319-sinterklaasavond")

    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    composer.create_matrix(num_voices=5, num_sections=4)

    for vname in ("Lead", "Pad", "Bass", "Arp", "Drums"):
        composer.add_voice(vname, program=PROG[vname], channel=CHAN[vname])

    for sname, bars in [("Intro", 4), ("Verse", 8), ("Verse2", 8), ("Outro", 4)]:
        composer.add_section(sname, bars=bars)

    fill_section(composer, "Intro", "intro")
    fill_section(composer, "Verse", "full")
    fill_section(composer, "Verse2", "full")
    fill_section(composer, "Outro", "outro")

    instruments = {"Drums": (2.0, 4.0, 0.0, 0.01)}
    hz = export_dual(composer, base + "-perfect.mid", base + "-humanized.mid",
                     style=STYLE, seed=SEED, bpm=BPM, instruments=instruments)

    prov = {
        "project": "319-sinterklaasavond",
        "style": STYLE, "key": KEY, "bpm": BPM, "time_sig": "4/4",
        "form": FORM, "seed": SEED,
        "composition_method": "023 Tendency Masking (melody, two-phase)",
        "phase1": "TendencyMaskingGenerator, corridor G4..F#5, 8th step, density 0.85",
        "phase2": "strong beats -> I-IV-V chord tones; conjunct clamp <= 3rd; diatonic",
        "production_method": "SP-032 FDN Reverb (warm hall) + master -16 LUFS",
        "voices": [{"name": v, "program": PROG[v], "channel": CHAN[v]}
                   for v in ("Lead", "Pad", "Bass", "Arp", "Drums")],
        "sections": {s: CHORDS[s] for s in CHORDS},
        "humanize": hz,
    }
    with open(os.path.join(midi_dir, "319-sinterklaasavond.provenance.json"), "w") as f:
        json.dump(prov, f, indent=2)

    print("wrote", base + "-perfect.mid")
    print("wrote", base + "-humanized.mid")
    print("humanize summary:", json.dumps(hz, indent=2))


if __name__ == "__main__":
    main()
