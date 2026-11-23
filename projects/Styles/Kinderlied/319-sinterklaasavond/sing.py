#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""319-sinterklaasavond — SUNG version.

Adds an MBROLA diphone vocal (Dutch, nl2) singing an original Sinterklaas-
avond lyric to the method-023 (Tendency Masking) generated melody, mixed over
the FluidSynth accompaniment, mastered to -16 LUFS.

Vocal is sung to the PERFECT (grid-locked) melody for sample-tight sync.
66 notes = 66 tokens; '-' holds the previous vowel (melisma). The generated
melody's rests naturally become phrase breaks (breaths).
"""

import json
import os
import sys

sys.path.insert(0, "/opt/data/svs")
from sing_song import sing

BASE = os.path.dirname(os.path.abspath(__file__))
MIDI = os.path.join(BASE, "MIDI", "319-sinterklaasavond-perfect.mid")
AUDIO = os.path.join(BASE, "Audio")
ANALYSIS = os.path.join(BASE, "Analysis")
os.makedirs(AUDIO, exist_ok=True)
os.makedirs(ANALYSIS, exist_ok=True)
OUT = os.path.join(AUDIO, "319-sinterklaasavond-sung")

# --- Verse (28 notes, 4 phrases: 7/8/6/7) --------------------------------
VERSE = (
    "de a vond is ge ko men "                  # De avond is gekomen
    "de ster ren staan daar te stra len "      # De sterren staan daar te stralen
    "zijn paard klinkt op de stoep "           # Zijn paard klinkt op de stoep
    "sin ter klaas rijdt door de straat "      # Sinterklaas rijdt door de straat
)

# --- Verse2 (24 notes; rests -> 3/1/2/1/1/16) ----------------------------
VERSE2 = (
    "hij klopt aan "                           # Hij klopt aan
    "zacht "                                   # zacht
    "klop klop "                               # klop klop
    "hoor "                                    # hoor
    "daar "                                    # daar
    "de bel len klin ken en het paard stapt "  # de bellen klinken en het paard stapt
    "nu heel rust ig door de straat "          # nu heel rustig door de straat
)

# --- Outro (14 notes; 11 + 3) --------------------------------------------
OUTRO = (
    "ga nu maar sla pen en droom van al het zoet "  # ga nu maar slapen en droom van al het zoet
    "sin ter klaas "                                # Sinterklaas
)

LYRICS = VERSE + VERSE2 + OUTRO


def main():
    stats = sing(MIDI, LYRICS, OUT, voice="nl2")
    report = {
        "project": "319-sinterklaasavond",
        "variant": "sung",
        "source_midi": os.path.basename(MIDI),
        "voice": "nl2 (MBROLA diphone, Dutch)",
        "lyrics": LYRICS.strip(),
        "note_count": stats["notes"],
        "token_count": stats["syllables"],
        "phoneme_count": stats["phonemes"],
        "mix": {k: v for k, v in stats.items()
                if k not in ("notes", "syllables", "phonemes")},
    }
    with open(os.path.join(ANALYSIS, "sung_report.json"), "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(json.dumps(stats, indent=2))
    print("wrote", OUT + ".wav", "and", OUT + ".ogg")


if __name__ == "__main__":
    main()
