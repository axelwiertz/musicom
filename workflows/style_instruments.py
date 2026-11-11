# -*- coding: utf-8 -*-
"""Style-aware instrumentation (P1 of PLAN_vary-instrumentation-rhythm.md).

Every genre maps to a role->instrument palette. ``instrument_palette(style)``
resolves a style name to a ``[(voice_name, instrument_name), ...]`` list the
way ``STYLE_REGISTRY.default_voices`` does — so ``compose()`` and
``build_framework()`` can swap a whole line-up by style without forking.

Rules:
- Instrument names are the ``instrument_registry.ALL_INSTRUMENTS`` keys
  (underscore form) EXCEPT drums, which MUST be ``"Drum Kit"`` so
  ``musicom_workflow._resolve_instrument`` routes it to channel 9.
- ``instrument_palette("pop")`` returns the legacy stack verbatim — the
  golden-hash gates pin it, so do NOT edit the pop entry.
- Unknown styles fall back to ``"pop"``.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

__all__ = ["INSTRUMENTATION_BY_STYLE", "INSTRUMENT_ALIASES", "instrument_palette"]

# voice stack = [(voice_name, instrument_name), ...]. Voice NAME is a label;
# the ROLE is resolved by POSITION (cell_engine.default_resolve_role), so order
# is load-bearing: idx0=lead, idx1=pad, idx2=bass, idx3=arp, idx4=drums.
INSTRUMENTATION_BY_STYLE: Dict[str, List[Tuple[str, str]]] = {
    "pop":        [("Lead", "flute"), ("Pad", "piano"), ("Bass", "double_bass"),
                   ("Arp", "clarinet"), ("Drums", "Drum Kit")],   # byte-pinned
    "rock":       [("Lead", "distortion_guitar"), ("Pad", "piano"),
                   ("Bass", "electric_bass"), ("Arp", "clean_electric"),
                   ("Drums", "Drum Kit")],
    "soul":       [("Lead", "tenor_sax"), ("Pad", "rhodes"), ("Bass", "electric_bass"),
                   ("Arp", "clean_electric"), ("Drums", "Drum Kit")],
    "techno":     [("Lead", "synth_voice"), ("Pad", "synth_pad"),
                   ("Bass", "synth_bass_1"), ("Arp", "clavi"), ("Drums", "Drum Kit")],
    "house":      [("Lead", "synth_brass_1"), ("Pad", "synth_pad"),
                   ("Bass", "synth_bass_1"), ("Arp", "rhodes"), ("Drums", "Drum Kit")],
    "trap":       [("Lead", "synth_voice"), ("Pad", "synth_pad"),
                   ("Bass", "synth_bass_2"), ("Arp", "celesta"), ("Drums", "Drum Kit")],
    "hiphop":     [("Lead", "synth_voice"), ("Pad", "rhodes"), ("Bass", "synth_bass_2"),
                   ("Arp", "electric_piano_2"), ("Drums", "Drum Kit")],
    "jazz":       [("Lead", "trumpet"), ("Harmony", "piano"), ("Bass", "double_bass"),
                   ("Arp", "jazz_guitar"), ("Drums", "Drum Kit")],
    "blues":      [("Lead", "harmonica"), ("Pad", "piano"), ("Bass", "double_bass"),
                   ("Arp", "clean_electric"), ("Drums", "Drum Kit")],
    "ragtime":    [("Lead", "honky_tonk"), ("Pad", "piano"), ("Bass", "acoustic_bass"),
                   ("Arp", "banjo"), ("Drums", "Drum Kit")],
    "funk":       [("Lead", "clavi"), ("Pad", "rhodes"), ("Bass", "slap_bass"),
                   ("Arp", "clean_electric"), ("Drums", "Drum Kit")],
    "disco":      [("Lead", "brass_section"), ("Pad", "string_ensemble"),
                   ("Bass", "electric_bass"), ("Arp", "rhodes"), ("Drums", "Drum Kit")],
    "flamenco":   [("Lead", "acoustic_guitar"), ("Pad", "string_ensemble"),
                   ("Bass", "double_bass"), ("Arp", "acoustic_guitar"),
                   ("Drums", "Drum Kit")],
    "latin":      [("Lead", "acoustic_guitar"), ("Pad", "piano"), ("Bass", "double_bass"),
                   ("Arp", "vibraphone"), ("Drums", "Drum Kit")],
    "tango":      [("Lead", "tango_accordion"), ("Pad", "string_ensemble"),
                   ("Bass", "double_bass"), ("Arp", "acoustic_guitar"),
                   ("Drums", "Drum Kit")],
    "reggae":     [("Lead", "acoustic_guitar"), ("Pad", "rhodes"), ("Bass", "electric_bass"),
                   ("Arp", "steel_drums"), ("Drums", "Drum Kit")],
    "ambient":    [("Lead", "flute"), ("Pad", "warm_pad"), ("Bass", "fretless_bass"),
                   ("Arp", "celesta"), ("Drums", "Drum Kit")],
    "minimal":    [("Lead", "marimba"), ("Pad", "string_ensemble"), ("Bass", "cello"),
                   ("Arp", "vibraphone"), ("Drums", "Drum Kit")],
    "cinematic":  [("Lead", "french_horn"), ("Pad", "string_ensemble"),
                   ("Bass", "double_bass"), ("Arp", "harp"), ("Drums", "Drum Kit")],
    "chanson":    [("Lead", "trumpet"), ("Pad", "accordion"), ("Bass", "double_bass"),
                   ("Arp", "acoustic_guitar"), ("Drums", "Drum Kit")],
    "country":    [("Lead", "steel_acoustic"), ("Pad", "piano"), ("Bass", "double_bass"),
                   ("Arp", "acoustic_guitar"), ("Drums", "Drum Kit")],
    "folk":       [("Lead", "fiddle"), ("Pad", "string_ensemble"), ("Bass", "double_bass"),
                   ("Arp", "dulcimer"), ("Drums", "Drum Kit")],
    "bluegrass":  [("Lead", "banjo"), ("Pad", "acoustic_guitar"), ("Bass", "double_bass"),
                   ("Arp", "fiddle"), ("Drums", "Drum Kit")],
    "klezmer":    [("Lead", "clarinet"), ("Pad", "accordion"), ("Bass", "double_bass"),
                   ("Arp", "acoustic_guitar"), ("Drums", "Drum Kit")],
    "balkan":     [("Lead", "clarinet"), ("Pad", "accordion"), ("Bass", "double_bass"),
                   ("Arp", "acoustic_guitar"), ("Drums", "Drum Kit")],
    "metal":      [("Lead", "distortion_guitar"), ("Pad", "synth_pad"),
                   ("Bass", "electric_bass"), ("Arp", "overdriven"), ("Drums", "Drum Kit")],
    "classical":  [("Lead", "violin"), ("Pad", "string_ensemble"), ("Bass", "cello"),
                   ("Arp", "harp"), ("Drums", "Drum Kit")],
    "baroque":    [("Lead", "violin"), ("Pad", "string_ensemble"), ("Bass", "cello"),
                   ("Arp", "harpsichord"), ("Drums", "Drum Kit")],
    "fanfare":    [("Lead", "trumpet"), ("Pad", "brass_section"), ("Bass", "tuba"),
                   ("Arp", "string_ensemble"), ("Drums", "Drum Kit")],
    "african":    [("Lead", "kalimba"), ("Pad", "marimba"), ("Bass", "didgeridoo"),
                   ("Arp", "marimba"), ("Drums", "Drum Kit")],
    "gamelan":    [("Lead", "shenai"), ("Pad", "vibraphone"), ("Bass", "double_bass"),
                   ("Arp", "steel_drums"), ("Drums", "Drum Kit")],
    "japanese":   [("Lead", "shakuhachi"), ("Pad", "koto"), ("Bass", "double_bass"),
                   ("Arp", "koto"), ("Drums", "Drum Kit")],
    "indian":     [("Lead", "sitar"), ("Pad", "string_ensemble"), ("Bass", "fretless_bass"),
                   ("Arp", "sitar"), ("Drums", "Drum Kit")],
    "arabic":     [("Lead", "oboe"), ("Pad", "string_ensemble"), ("Bass", "fretless_bass"),
                   ("Arp", "dulcimer"), ("Drums", "Drum Kit")],
    "percussion": [("Lead", "marimba"), ("Pad", "marimba"), ("Bass", "double_bass"),
                   ("Arp", "xylophone"), ("Drums", "Drum Kit")],
    "world":      [("Lead", "oboe"), ("Pad", "string_ensemble"), ("Bass", "cello"),
                   ("Arp", "harp"), ("Drums", "Drum Kit")],
}

# genre-name -> family key (normalized lowercase, spaces/hyphens/underscores -> space).
INSTRUMENT_ALIASES: Dict[str, str] = {
    "pop": "pop", "rock": "rock", "soul": "soul", "ballad": "pop", "r&b": "pop",
    "rnb": "pop",
    "techno": "techno", "electronic": "techno", "edm": "techno", "trance": "techno",
    "house": "house", "dance": "house",
    "trap": "trap", "drill": "trap", "phonk": "trap",
    "hiphop": "hiphop", "hip hop": "hiphop", "rap": "hiphop", "boom bap": "hiphop",
    "jazz": "jazz", "swing": "jazz", "bebop": "jazz", "big band": "jazz",
    "blues": "blues",
    "ragtime": "ragtime",
    "funk": "funk", "groove": "funk", "afrobeat": "funk",
    "disco": "disco",
    "flamenco": "flamenco",
    "latin": "latin", "bossa": "latin", "bossa nova": "latin", "bossanova": "latin",
    "samba": "latin", "cuban": "latin", "kizomba": "latin",
    "tango": "tango",
    "reggae": "reggae", "ska": "reggae", "dub": "reggae",
    "ambient": "ambient", "drone": "ambient",
    "minimal": "minimal", "minimalism": "minimal", "modal": "minimal",
    "cinematic": "cinematic", "film": "cinematic",
    "chanson": "chanson", "french": "chanson",
    "country": "country",
    "folk": "folk", "celtic": "folk", "balfolk": "folk",
    "bluegrass": "bluegrass",
    "klezmer": "klezmer",
    "balkan": "balkan",
    "metal": "metal", "hard rock": "metal", "punk": "metal",
    "classical": "classical", "classic": "classical", "romantic": "classical",
    "chamber": "classical", "opera": "classical",
    "baroque": "baroque",
    "fanfare": "fanfare", "brass": "fanfare",
    "african": "african", "west african": "african", "west african polyrhythms": "african",
    "gamelan": "gamelan",
    "japanese": "japanese",
    "indian": "indian", "indianclassical": "indian", "indian classical": "indian",
    "arabic": "arabic", "middle east": "arabic",
    "percussion": "percussion",
    "world": "world", "experimental": "world", "hybrid": "world", "other": "world",
    "poetry": "world",
}


def _norm(style: str) -> str:
    if not style:
        return "pop"
    key = style.lower().strip().replace("_", " ").replace("-", " ").replace("  ", " ")
    if key in INSTRUMENT_ALIASES:
        return INSTRUMENT_ALIASES[key]
    for alias, fam in INSTRUMENT_ALIASES.items():
        if alias in key:
            return fam
    return "pop"


def instrument_palette(style: str) -> List[Tuple[str, str]]:
    """Resolve a style name to a role->instrument voice stack (pop default)."""
    fam = _norm(style)
    return list(INSTRUMENTATION_BY_STYLE.get(fam, INSTRUMENTATION_BY_STYLE["pop"]))


if __name__ == "__main__":
    import sys
    sys.path.insert(0, "/opt/data/repos/musicom/projects/Instruments")
    from instrument_registry import by_name

    bad = []
    for style in INSTRUMENT_ALIASES:
        fam = _norm(style)
        for vname, inst in INSTRUMENTATION_BY_STYLE[fam]:
            if inst == "Drum Kit":
                continue
            try:
                by_name(inst)
            except KeyError:
                bad.append((style, fam, inst))
    print("palettes:", len(INSTRUMENTATION_BY_STYLE),
          "aliases:", len(INSTRUMENT_ALIASES))
    print("unresolvable instruments:", bad or "NONE")
