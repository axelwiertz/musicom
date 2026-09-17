# -*- coding: utf-8 -*-
"""Instrument registry — musicom instruments as a real, importable package.

Loads every instrument's constants (MIDI_PROGRAM, ranges, articulations,
synthesis presets, production defaults) from the per-instrument .py files
into uniform `Instrument` objects. Exposes both module-style constants
(backwards compatible) and object-style access (VIOLIN.midi_program).

Usage:
    from instrument_registry import VIOLIN, PIANO, TRUMPET, ALL_INSTRUMENTS, by_name, by_program

    composer.add_voice("Violin", program=VIOLIN.midi_program, channel=0)
    inst = by_name("flute")            # → FLUTE
    inst = by_program(56)              # → TRUMPET (GM 56)
"""

import importlib
import importlib.util
import os
import sys

_INSTR_DIR = os.path.dirname(os.path.abspath(__file__))
if _INSTR_DIR not in sys.path:
    sys.path.insert(0, _INSTR_DIR)

# module path (relative to Instruments dir) -> registry key
_INSTRUMENT_MODULES = {
    "Strings.violin.violin": "violin",
    "Strings.harp.harp": "harp",
    "Strings.viola.viola": "viola",
    "Strings.cello.cello": "cello",
    "Strings.double_bass.double_bass": "double_bass",
    "Keys.piano.piano": "piano",
    "Keys.organ.organ": "organ",
    "Keys.dulcimer.dulcimer": "dulcimer",
    "Keys.harpsichord.harpsichord": "harpsichord",
    "Brass.trumpet.trumpet": "trumpet",
    "Brass.trombone.trombone": "trombone",
    "Brass.french_horn.french_horn": "french_horn",
    "Brass.tuba.tuba": "tuba",
    "Woodwind.flute.flute": "flute",
    "Woodwind.clarinet.clarinet": "clarinet",
    "Woodwind.oboe.oboe": "oboe",
    "Woodwind.bassoon.bassoon": "bassoon",
    "Woodwind.saxophone.saxophone": "saxophone",
    "Guitar.acoustic.acoustic_guitar": "acoustic_guitar",
    "Percussion.drum_kit.drum_kit": "drum_kit",
    "Percussion.marimba.marimba": "marimba",
    "Percussion.steel_drums.steel_drums": "steel_drums",
    "Percussion.vibraphone.vibraphone": "vibraphone",
    "World.sitar.sitar": "sitar",
    "World.koto.koto": "koto",
    "World.shamisen.shamisen": "shamisen",
    "World.kalimba.kalimba": "kalimba",
    "World.banjo.banjo": "banjo",
    "Woodwind.bagpipe.bagpipe": "bagpipe",
    "World.shenai.shenai": "shenai",
    "World.fiddle.fiddle": "fiddle",
    "Percussion.timpani.timpani": "timpani",
    "Percussion.xylophone.xylophone": "xylophone",
    "World.taiko.taiko": "taiko",
    "Vocal.human_voice.human_voice": "human_voice",
    "Vocal.voice_like.voice_like_voice": "voice_like",
}

_FIELDS = (
    "midi_program", "gm_name", "range_min", "range_max",
    "solo_range", "sweet_spot", "zones", "articulations",
    "synthesis", "modal_preset", "karplus_defaults", "fm_defaults",
    "bowed_defaults", "drum606_defaults", "synthesis_defaults",
    "motor_defaults", "xylophone_modes",
    "reverb_tail", "eq_body", "eq_presence", "eq_air", "pan",
    "stem_label",
)


class Instrument:
    """Uniform view over an instrument's constants."""

    def __init__(self, name, family, module):
        self.name = name
        self.family = family
        self.module_path = module.__name__ if hasattr(module, "__name__") else str(module)
        for f in _FIELDS:
            setattr(self, f, getattr(module, f.upper(), None))

    @property
    def program(self):
        return self.midi_program

    def in_range(self, midi_note):
        if self.range_min is None or self.range_max is None:
            return True
        return self.range_min <= midi_note <= self.range_max

    def in_sweet_spot(self, midi_note):
        if self.sweet_spot:
            return self.sweet_spot[0] <= midi_note <= self.sweet_spot[1]
        return self.in_range(midi_note)

    def __repr__(self):
        return (f"<Instrument {self.name} (family={self.family}, "
                f"program={self.midi_program}, range={self.range_min}-{self.range_max})>")


def _load_module(mod_path):
    """Import a dotted module path relative to Instruments dir."""
    try:
        return importlib.import_module(mod_path)
    except ImportError:
        full = os.path.join(_INSTR_DIR, mod_path.replace(".", os.sep) + ".py")
        spec = importlib.util.spec_from_file_location(mod_path, full)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load instrument module {mod_path} from {full}")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod


def _member_module(base_mod, spec):
    """Build a module-like namespace for one voice-like family member.

    The Instrument class reads uppercase constants off a module object; a
    family member shares the base module's defaults (zones, articulations,
    synthesis engine, production EQ) but overrides its own program / name /
    stem / range / sweet spot, and sets SYNTHESIS_DEFAULTS["instrument"] to
    its engine key so rendering routes to the right VoiceLikeInstrument.
    """
    import types

    m = types.SimpleNamespace()
    m.MIDI_PROGRAM = spec["midi_program"]
    m.GM_NAME = spec["label"]
    m.STEM_LABEL = spec["stem_label"]
    m.RANGE_MIN = spec["range_min"]
    m.RANGE_MAX = spec["range_max"]
    m.SOLO_RANGE = spec["sweet_spot"]
    m.SWEET_SPOT = spec["sweet_spot"]
    m.ZONES = getattr(base_mod, "ZONES", None)
    m.ARTICULATIONS = getattr(base_mod, "ARTICULATIONS", None)
    m.SYNTHESIS = getattr(base_mod, "SYNTHESIS", None)
    defaults = dict(getattr(base_mod, "SYNTHESIS_DEFAULTS", {}) or {})
    defaults["instrument"] = spec["engine"]
    m.SYNTHESIS_DEFAULTS = defaults
    m.MODAL_PRESET = getattr(base_mod, "MODAL_PRESET", None)
    m.KARPLUS_DEFAULTS = getattr(base_mod, "KARPLUS_DEFAULTS", None)
    m.FM_DEFAULTS = getattr(base_mod, "FM_DEFAULTS", None)
    m.BOWED_DEFAULTS = getattr(base_mod, "BOWED_DEFAULTS", None)
    m.DRUM606_DEFAULTS = getattr(base_mod, "DRUM606_DEFAULTS", None)
    m.MOTOR_DEFAULTS = getattr(base_mod, "MOTOR_DEFAULTS", None)
    m.REVERB_TAIL = getattr(base_mod, "REVERB_TAIL", None)
    m.EQ_BODY = getattr(base_mod, "EQ_BODY", None)
    m.EQ_PRESENCE = getattr(base_mod, "EQ_PRESENCE", None)
    m.EQ_AIR = getattr(base_mod, "EQ_AIR", None)
    m.PAN = getattr(base_mod, "PAN", None)
    return m


def _load_all():
    instruments = {}
    for mod_path, key in _INSTRUMENT_MODULES.items():
        family = mod_path.split(".")[0]
        mod = _load_module(mod_path)
        human = getattr(mod, "GM_NAME", None)
        if family == "Percussion" and key == "drum_kit":
            human = "Drum Kit"
        if not human:
            human = key.replace("_", " ").title()
        instruments[key] = Instrument(human, family, mod)

        # Voice-like family: register each member individually (kazoo,
        # jaw_harp, singing_saw, ...) in addition to the `voice_like` umbrella.
        fam = getattr(mod, "FAMILY", None)
        if isinstance(fam, dict):
            for member_key, spec in fam.items():
                if member_key == key:
                    continue
                instruments[member_key] = Instrument(
                    spec["label"], family, _member_module(mod, spec))
    return instruments


ALL_INSTRUMENTS = _load_all()

# Convenience: uppercase short names
VIOLIN = ALL_INSTRUMENTS["violin"]
HARP = ALL_INSTRUMENTS["harp"]
VIOLA = ALL_INSTRUMENTS["viola"]
CELLO = ALL_INSTRUMENTS["cello"]
DOUBLE_BASS = ALL_INSTRUMENTS["double_bass"]
PIANO = ALL_INSTRUMENTS["piano"]
ORGAN = ALL_INSTRUMENTS["organ"]
DULCIMER = ALL_INSTRUMENTS["dulcimer"]
HARPSICHORD = ALL_INSTRUMENTS["harpsichord"]
TRUMPET = ALL_INSTRUMENTS["trumpet"]
TROMBONE = ALL_INSTRUMENTS["trombone"]
FRENCH_HORN = ALL_INSTRUMENTS["french_horn"]
TUBA = ALL_INSTRUMENTS["tuba"]
FLUTE = ALL_INSTRUMENTS["flute"]
CLARINET = ALL_INSTRUMENTS["clarinet"]
OBOE = ALL_INSTRUMENTS["oboe"]
BASSOON = ALL_INSTRUMENTS["bassoon"]
SAXOPHONE = ALL_INSTRUMENTS["saxophone"]
ACOUSTIC_GUITAR = ALL_INSTRUMENTS["acoustic_guitar"]
DRUM_KIT = ALL_INSTRUMENTS["drum_kit"]
MARIMBA = ALL_INSTRUMENTS["marimba"]
STEEL_DRUMS = ALL_INSTRUMENTS["steel_drums"]
VIBRAPHONE = ALL_INSTRUMENTS["vibraphone"]
SITAR = ALL_INSTRUMENTS["sitar"]
KOTO = ALL_INSTRUMENTS["koto"]
SHAMISEN = ALL_INSTRUMENTS["shamisen"]
KALIMBA = ALL_INSTRUMENTS["kalimba"]
BANJO = ALL_INSTRUMENTS["banjo"]
BAGPIPE = ALL_INSTRUMENTS["bagpipe"]
SHENAI = ALL_INSTRUMENTS["shenai"]
FIDDLE = ALL_INSTRUMENTS["fiddle"]
TIMPANI = ALL_INSTRUMENTS["timpani"]
XYLOPHONE = ALL_INSTRUMENTS["xylophone"]
TAIKO = ALL_INSTRUMENTS["taiko"]
HUMAN_VOICE = ALL_INSTRUMENTS["human_voice"]
# Voice-like family — one instrument per non-vocal source. The `voice_like`
# key is the umbrella (vox humana); each member is also addressable directly.
VOICE_LIKE = ALL_INSTRUMENTS["voice_like"]
VOX_HUMANA = ALL_INSTRUMENTS["vox_humana"]
KAZOO = ALL_INSTRUMENTS["kazoo"]
JAW_HARP = ALL_INSTRUMENTS["jaw_harp"]
DIDGERIDOO = ALL_INSTRUMENTS["didgeridoo"]
SINGING_SAW = ALL_INSTRUMENTS["singing_saw"]
TALKBOX = ALL_INSTRUMENTS["talkbox"]

#: Registry keys whose audio must come from VoiceLikeInstrument, not FluidSynth.
VOICE_LIKE_KEYS = (
    "voice_like", "vox_humana", "kazoo", "jaw_harp",
    "didgeridoo", "singing_saw", "talkbox",
)


def by_name(name):
    """Look up an instrument by case-insensitive name."""
    key = name.strip().lower().replace(" ", "_").replace("-", "_")
    if key in ALL_INSTRUMENTS:
        return ALL_INSTRUMENTS[key]
    for inst in ALL_INSTRUMENTS.values():
        if inst.gm_name and inst.gm_name.lower() == name.strip().lower():
            return inst
        if inst.name.lower() == name.strip().lower():
            return inst
    raise KeyError(f"No instrument named {name!r}. Available: {sorted(ALL_INSTRUMENTS)}")


def by_program(program):
    """Look up an instrument by GM program number."""
    for inst in ALL_INSTRUMENTS.values():
        if inst.midi_program == program:
            return inst
    raise KeyError(f"No instrument with program {program}. Available programs: "
                   f"{sorted(i.midi_program for i in ALL_INSTRUMENTS.values())}")


def registry_table():
    """Markdown registry table, auto-generated from loaded instruments."""
    lines = [
        "| Family | Instrument | Program | Range | Role |",
        "|---|---|---|---|---|",
    ]
    for inst in sorted(ALL_INSTRUMENTS.values(), key=lambda i: (i.family, i.name)):
        low = inst.name.lower()
        if low in ("double bass", "tuba", "trombone", "cello"):
            role = "bass, counter, accent, harmony"
        elif low == "violin":
            role = "lead, counter, accent"
        elif low == "orchestral harp":
            role = "harmony, arpeggio, glissando, melody, countermelody, accent"
        elif low == "piano":
            role = "harmony, melody, bass, rhythm"
        elif low == "church organ":
            role = "harmony, pad, bass, rhythm, accent"
        elif low == "dulcimer":
            role = "lead, melody, ornament, rhythm, harmony"
        elif low == "harpsichord":
            role = "harmony, continuo, melody, ornament, countermelody, accent"
        elif low == "drum kit":
            role = "rhythm, groove, accent"
        elif low == "marimba":
            role = "lead, melody, accent, countermelody, harmony"
        elif low == "steel drums":
            role = "lead, melody, accent, countermelody, harmony, rhythm"
        elif low == "vibraphone":
            role = "lead, melody, harmony, countermelody, accent"
        elif low == "sitar":
            role = "lead, melody, ornament, drone"
        elif low == "koto":
            role = "lead, melody, ornament, drone, harmony"
        elif low == "shamisen":
            role = "lead, melody, ornament, drone, countermelody"
        elif low == "kalimba":
            role = "lead, melody, ornament, drone, harmony"
        elif low == "banjo":
            role = "lead, melody, ornament, rhythm, accent"
        elif low == "bagpipe":
            role = "lead, melody, ornament, drone, accent"
        elif low == "shenai":
            role = "lead, melody, ornament, drone, accent"
        elif low == "fiddle":
            role = "lead, melody, ornament, countermelody, accent"
        elif low == "timpani":
            role = "accent, rhythm, bass, drone"
        elif low == "xylophone":
            role = "lead, melody, ornament, accent, countermelody"
        elif low == "taiko drum":
            role = "accent, rhythm, drone, ornament"
        elif low == "human voice":
            role = "lead, melody, countermelody"
        else:
            role = "lead, harmony, accent"
        rng = f"{inst.range_min}–{inst.range_max}" if inst.range_min else "-"
        lines.append(f"| {inst.family} | {inst.name} | {inst.midi_program} | {rng} | {role} |")
    return "\n".join(lines)


if __name__ == "__main__":
    print(registry_table())
    print()
    print("Verification:")
    print("  VIOLIN.midi_program =", VIOLIN.midi_program)
    print("  ORGAN.midi_program =", ORGAN.midi_program, "(Church Organ, GM19)")
    print("  DULCIMER.midi_program =", DULCIMER.midi_program, "(should be 15)")
    print("  by_name('dulcimer') =", by_name("dulcimer"))
    print("  by_program(15) =", by_program(15))
    print("  DULCIMER.in_sweet_spot(69) =", DULCIMER.in_sweet_spot(69))
    print("  TRUMPET.midi_program =", TRUMPET.midi_program, "(should be 56)")
    print("  by_name('double bass') =", by_name("double bass"))
    print("  by_program(56) =", by_program(56))
    print("  FLUTE.in_sweet_spot(72) =", FLUTE.in_sweet_spot(72))
    print("  SITAR.midi_program =", SITAR.midi_program, "(should be 104)")
    print("  by_name('sitar') =", by_name("sitar"))
    print("  by_program(104) =", by_program(104))
    print("  SITAR.in_sweet_spot(69) =", SITAR.in_sweet_spot(69))
    print("  KOTO.midi_program =", KOTO.midi_program, "(should be 107)")
    print("  by_name('koto') =", by_name("koto"))
    print("  by_program(107) =", by_program(107))
    print("  KOTO.in_sweet_spot(69) =", KOTO.in_sweet_spot(69))
    print("  SHAMISEN.midi_program =", SHAMISEN.midi_program, "(should be 106)")
    print("  by_name('shamisen') =", by_name("shamisen"))
    print("  by_program(106) =", by_program(106))
    print("  SHAMISEN.in_sweet_spot(69) =", SHAMISEN.in_sweet_spot(69))
    print("  KALIMBA.midi_program =", KALIMBA.midi_program, "(should be 108)")
    print("  by_name('kalimba') =", by_name("kalimba"))
    print("  by_program(108) =", by_program(108))
    print("  KALIMBA.in_sweet_spot(69) =", KALIMBA.in_sweet_spot(69))
    print("  BANJO.midi_program =", BANJO.midi_program, "(should be 105)")
    print("  by_name('banjo') =", by_name("banjo"))
    print("  by_program(105) =", by_program(105))
    print("  BANJO.in_sweet_spot(69) =", BANJO.in_sweet_spot(69))
    print("  BAGPIPE.midi_program =", BAGPIPE.midi_program, "(should be 109)")
    print("  by_name('bagpipe') =", by_name("bagpipe"))
    print("  by_program(109) =", by_program(109))
    print("  BAGPIPE.in_sweet_spot(62) =", BAGPIPE.in_sweet_spot(62))
    print("  STEEL_DRUMS.midi_program =", STEEL_DRUMS.midi_program, "(should be 114)")
    print("  by_name('steel drums') =", by_name("steel drums"))
    print("  by_program(114) =", by_program(114))
    print("  STEEL_DRUMS.in_sweet_spot(69) =", STEEL_DRUMS.in_sweet_spot(69))
    print("  FIDDLE.midi_program =", FIDDLE.midi_program, "(should be 110)")
    print("  by_name('fiddle') =", by_name("fiddle"))
    print("  by_program(110) =", by_program(110))
    print("  FIDDLE.in_sweet_spot(69) =", FIDDLE.in_sweet_spot(69))
    print("  TIMPANI.midi_program =", TIMPANI.midi_program, "(should be 47)")
    print("  by_name('timpani') =", by_name("timpani"))
    print("  by_program(47) =", by_program(47))
    print("  TIMPANI.in_sweet_spot(45) =", TIMPANI.in_sweet_spot(45))
    print("  VIBRAPHONE.midi_program =", VIBRAPHONE.midi_program, "(should be 11)")
    print("  by_name('vibraphone') =", by_name("vibraphone"))
    print("  by_program(11) =", by_program(11))
    print("  VIBRAPHONE.in_sweet_spot(69) =", VIBRAPHONE.in_sweet_spot(69))
    print("  HARP.midi_program =", HARP.midi_program, "(should be 46)")
    print("  by_name('harp') =", by_name("harp"))
    print("  by_name('orchestral harp') =", by_name("orchestral harp"))
    print("  by_program(46) =", by_program(46))
    print("  HARP.in_sweet_spot(69) =", HARP.in_sweet_spot(69))
    print("  XYLOPHONE.midi_program =", XYLOPHONE.midi_program, "(should be 13)")
    print("  by_name('xylophone') =", by_name("xylophone"))
    print("  by_program(13) =", by_program(13))
    print("  XYLOPHONE.in_sweet_spot(72) =", XYLOPHONE.in_sweet_spot(72))
    print("  TAIKO.midi_program =", TAIKO.midi_program, "(should be 116)")
    print("  by_name('taiko') =", by_name("taiko"))
    print("  by_name('taiko drum') =", by_name("taiko drum"))
    print("  by_program(116) =", by_program(116))
    print("  TAIKO.in_sweet_spot(50) =", TAIKO.in_sweet_spot(50))
    print("  HARPSICHORD.midi_program =", HARPSICHORD.midi_program, "(should be 6)")
    print("  by_name('harpsichord') =", by_name("harpsichord"))
    print("  by_program(6) =", by_program(6))
    print("  HARPSICHORD.in_sweet_spot(69) =", HARPSICHORD.in_sweet_spot(69))
