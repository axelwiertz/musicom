#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""318-sinterklaaslied — SUNG version.

Adds an MBROLA diphone vocal (Dutch, nl2) singing the classic
"Sinterklaas kapoentje" lyrics to the hand-authored melody, mixed over the
FluidSynth accompaniment (pad/bass/arp/drums), mastered to -16 LUFS.

Vocal is sung to the PERFECT (grid-locked) melody so voice + accompaniment are
sample-tight; the human voice itself is the expressive lead. The recorder
(Lead, ch0) doubles the voice — idiomatic for a Sinterklaas sing-along.

Lyrics are syllable-aligned 1:1 with the melody notes; '-' holds the previous
vowel across a note (melisma). 165 notes = 165 tokens.
"""

import json
import os
import sys

sys.path.insert(0, "/opt/data/svs")
from sing_song import sing

BASE = os.path.dirname(os.path.abspath(__file__))
MIDI = os.path.join(BASE, "MIDI", "318-sinterklaaslied-perfect.mid")
AUDIO = os.path.join(BASE, "Audio")
ANALYSIS = os.path.join(BASE, "Analysis")
os.makedirs(AUDIO, exist_ok=True)
os.makedirs(ANALYSIS, exist_ok=True)
OUT = os.path.join(AUDIO, "318-sinterklaaslied-sung")

# --- Verse (63 notes) = classic "Sinterklaas kapoentje" + 2nd stanza -------
VERSE = (
    "sin ter klaas ka poen tje - - "          # Sinterklaas kapoentje
    "gooi wat in mijn schoen tje - - "        # gooi wat in mijn schoentje
    "gooi wat in mijn laars je - - "          # gooi wat in mijn laarsje
    "dank je sin ter klaas je - "             # dank je Sinterklaasje
    "sin ter klaas je goe ie man - "          # Sinterklaasje goeie man
    "geef me wat ik wen sen kan - "           # geef me wat ik wensen kan
    "sui ker beest of mar se pein - "         # suikerbeest of marsepein
    "laat mijn schoen tje vol maar zijn - "   # laat mijn schoentje vol maar zijn
)

# --- Refrain (29 notes) = sing-along hook --------------------------------
REFRAIN = (
    "hoor de bel len "          # hoor de bellen
    "klink in de straat "       # klinken in de straat
    "sin ter klaas komt "       # Sinterklaas komt
    "aan ge reed "              # aangereden
    "hoor de bel len "
    "klink in de straat "
    "sin ter klaas kom "        # Sinterklaas kom
    "van daag "                 # vandaag
)

# --- Outro (10 notes) = closing ------------------------------------------
OUTRO = "dank je sin ter klaas je dank je wel -"

LYRICS = VERSE + REFRAIN + VERSE + OUTRO   # verse repeats as Verse2


def main():
    stats = sing(MIDI, LYRICS, OUT, voice="nl2")
    report = {
        "project": "318-sinterklaaslied",
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
