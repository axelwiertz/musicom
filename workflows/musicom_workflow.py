# -*- coding: utf-8 -*-
"""Musicom workflow — single entry points for the design → realization loop.

This is the reorganization spine: instead of each project re-inventing a
bespoke compose.py / regen.py / produce_*.py, the workflow exposes ONE
compose() and ONE produce() that wire the knowledge (methods, styles,
instruments, sound) into the engine.

DESIGN (composition):
    from workflows.musicom_workflow import compose
    result = compose(
        style="pop",                 # style_registry key (or "flamenco", ...)
        method="001",                # composition method (methods_db) or "HC-012"
        form="verse-chorus",         # pop form template
        key="C", bpm=120,
        voices=[("Lead", "Flute"), ("Pad", "Piano"), ("Bass", "Double Bass"),
                ("Arp", "Clarinet"), ("Drums", "Drum Kit")],
    )
    result.midi_path          # validated, zero-drift MIDI
    result.provenance         # provenance.json sidecar

REALIZATION (production):
    from workflows.musicom_workflow import produce
    audio = produce(
        midi_path=result.midi_path,
        method="SP-011",             # sound production method (methods_db)
        params={"loop_gain": 0.996}, # method-specific knobs
        out_dir="Audio",
    )
    audio.wav_path / audio.ogg_path

If you only need the current best path without choices, call:
    compose(style="pop", ...)  # picks a default method per style
    produce(midi_path, "SP-001")  # SoundFont render (FluidSynth), always available

The registry functions build the tables that should live in docs/:
    method_table()  -> markdown table of composition methods
    sp_method_table() -> markdown table of sound production methods
    style_table()   -> markdown table of style templates
"""

import json
import os
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

# --- engine imports (editable install; no sys.path hacks needed) ------------
from structures import MidiInstrument, MidiPercussion
from workflows.unitmatrix_composer import UnitMatrixComposer, create_note_unit
from workflows.provenance import write_provenance
from sound.render.fluidsynth import discover_soundfont

# --- instruments (Phase 1b: real Instrument objects) ------------------------
_INSTR_DIR = "/opt/data/projects/Instruments"
if _INSTR_DIR not in sys.path:
    sys.path.insert(0, _INSTR_DIR)
try:
    from instrument_registry import ALL_INSTRUMENTS, by_name as _instr_by_name
except ImportError:
    ALL_INSTRUMENTS = {}
    def _instr_by_name(n):
        raise KeyError(n)


# --- style registry: extracted from the 53 genre dirs (Phase 1b) ------------
# Each style: typical tempo, time signature, form template, characteristic
# rhythm/motion, default voice roles.
STYLE_REGISTRY = {
    "pop": {
        "bpm": 120, "time_sig": "4/4",
        "form": "intro-verse-chorus-bridge-outro",
        "motion": "16th arp + backbeat",
        "default_voices": [("Lead", "Flute"), ("Pad", "Piano"),
                           ("Bass", "Double Bass"), ("Arp", "Clarinet"),
                           ("Drums", "Drum Kit")],
    },
    "bossa_nova": {
        "bpm": 100, "time_sig": "4/4",
        "form": "intro-A-A-B-A",
        "motion": "clave-ish guitar + soft brushes",
        "default_voices": [("Lead", "Flute"), ("Guitar", "Acoustic Guitar"),
                           ("Bass", "Double Bass"), ("Drums", "Drum Kit")],
    },
    "flamenco": {
        "bpm": 130, "time_sig": "3/4",
        "form": "intro-falseta-letra-falseta-cierre",
        "motion": "12-beat compas, Andalusian cadence",
        "default_voices": [("Lead", "Flute"), ("Guitar", "Acoustic Guitar"),
                           ("Bass", "Double Bass"), ("Drums", "Drum Kit")],
    },
    "jazz": {
        "bpm": 140, "time_sig": "4/4",
        "form": "head-solos-head",
        "motion": "swing 8ths, walking bass",
        "default_voices": [("Lead", "Trumpet"), ("Harmony", "Piano"),
                           ("Bass", "Double Bass"), ("Drums", "Drum Kit")],
    },
    "techno": {
        "bpm": 128, "time_sig": "4/4",
        "form": "intro-break-drop-outro",
        "motion": "4-on-floor kick, 16th hats",
        "default_voices": [("Bass", "Double Bass"), ("Arp", "Clarinet"),
                           ("Drums", "Drum Kit")],
    },
}

# --- method defaults (composition methods by ID → short description) -------
# Keys = methods_db.md method IDs. Values = (short desc, style hint).
COMPOSITION_METHODS = {
    "001": "Skeleton-First Refinement (rules, form-first)",
    "002": "Markov Probabilistic Transitions (stochastic)",
    "012": "Euclidean Groove Locking (rules, rhythm)",
    "018": "Schillinger System (rhythm interference)",
    "023": "Tendency Masking Stochastic Bounds",
    "026": "Deconstructive Phase-Shift Minimalism",
    "032": "Isorhythmic Talea-Color Mapping",
    "040": "Perlin Noise Composition (nature-led)",
    "043": "Strange Attractor Trajectory Mapping",
    "048": "Reflected Brownian Motion Pitch Diffusion",
    "059": "Echo State Network Reservoir Composition",
    "HC-012": "Flamenco Compas & Falseta (human method)",
    "HC-007": "Lyric-Melody Prosody (human method)",
}

# --- sound production methods (SP table → implementation path) -------------
# Maps SP method ID to the shared sound/ module that implements it.
SP_METHODS = {
    "SP-001": ("sound.render.fluidsynth", "Multi-timbral SoundFont (FluidSynth)"),
    "SP-011": ("sound.synthesis.karplus_strong", "Karplus-Strong String Synthesis"),
    "SP-021": ("sound.synthesis.binaural", "Binaural HRTF Spatialization"),
    "SP-024": ("sound.synthesis.bowed", "Bowed String Physical Modeling"),
    "SP-026": ("sound.effects.phase_vocoder", "Spectral Phase Vocoder Resynthesis"),
    "SP-028": ("sound.effects.lpc_synth", "Linear Predictive Coding Synthesis"),
    "SP-032": ("sound.effects.fdn_reverb", "Feedback Delay Network Reverb"),
    "SP-033": ("sound.synthesis.supersaw_swarm", "Detuned Saw Swarm + Scale/Chord Quantize + Morph Pad"),
    "SP-034": ("sound.effects.bbd_chorus", "BBD Chorus Ensemble (Clock/Compander/Per-Voice Variation)"),
    "SP-035": ("sound.effects.shimmer_reverb", "Fractional-Pitch Shimmer Reverb (SOLA Shift in Feedback)"),
    "SP-036": ("sound.synthesis.formant_voice", "Klatt-Cascade Formant Voice / Speech Synthesis (klattsch-style)"),
    "SP-037": ("sound.effects.subharmonic", "Pitch-Tracked 3-Band Sub-Harmonic Generator (Penteo 8 Synthesized LFE-style)"),
    # NOTE (2026-09-10): docs/methods.md already reserves SP-038..SP-068 for the
    # absolute-layer catalog (VOSIM, FDTD, DDSP, ...).  The LAYER DISCIPLINE
    # union (SP_METHODS ∪ methods-registry.md) therefore under-counts; the true
    # next free SP-ID is the global max across all three docs + 1 = SP-069.
    "SP-069": ("sound.effects.topology_distortion", "Switched Discrete Distortion Topology Bank (FuzzBillion-style)"),
    "SP-070": ("sound.effects.morph_filter", "Morphing Five-Character Resonant Filter (ZERO9 Fusion Filter-style)"),
    "SP-071": ("sound.effects.severance", "Gated Reverb + Dual-Engine Delay + Glitch Chain + Parallel Band Compressor (ZERO9-style)"),
    "SP-072": ("sound.synthesis.critter_pad", "Three-Partial Pad Bank with Stochastic Microtonal Critters Layer (Brackish Pads-style)"),
    "SP-073": ("sound.synthesis.music_box", "Twin-Detuned-Comb Music Box Modal Synthesis (Muro Box N40-style)"),
    "SP-074": ("sound.generators.drum_machine", "Eight-Channel Sample Drum Machine + Sequencer (Bullfrog Drums-style)"),
    "SP-075": ("sound.render.hybrid", "Voice-Like Instrument Hybrid Render (synthesized voice tracks + SoundFont backing)"),
    # 2026-09-14 scan (adopted + registered 2026-09-17)
    "SP-076": ("sound.synthesis.lfsr_voice", "Tuned LFSR Digital-Noise Voice (Noise Engineering AT Legio-style)"),
    "SP-077": ("sound.synthesis.tzfm", "Through-Zero FM + Per-Note Waveform Stepping (Korg Prologue Elixir-style)"),
    "SP-078": ("sound.generators.polymetric_grid", "16-Track Polymetric Step Sequencer w/ Per-Step Graphs (Rapid Flow omniGRID-style)"),
    "SP-079": ("sound.generators.acid_seq", "Scale-Locked Acid Sequencer + 303/202 Voice (BS-203 MacroAcidizer-style)"),
    "SP-080": ("sound.generators.cadence_variator", "Cadence Engine Rhythmic Variator w/ Flux Randomizer (Emergence Audio Envoy-style)"),
    "SP-081": ("sound.modular.random8", "8-Channel Quantized Random CV Source (Befaco/Mylar Melodies RANDOM8-style)"),
    "SP-082": ("sound.synthesis.string_scales", "Scale-Quantized String Arpeggiator Voice (Zlosynth Arplus-style)"),
    "SP-083": ("sound.modular.wandering", "Non-LFO Wandering Engine + Portal + Drift Clouds Voice (Sound Dust-style)"),
    # 2026-09-17 scan
    "SP-084": ("sound.synthesis.air_pipe", "Flue-Pipe Physical Model w/ Air-Supply Modulation (Modartt Airteq-style)"),
    "SP-085": ("sound.effects.glitch_chopper", "Transient-Snapped Segment Chopper w/ Glitch/Reverse Probability (GlitchShredder-style)"),
    "SP-086": ("sound.generators.harmony_writer", "Rule-Based Melody Harmony Writer w/ Voice Leading (HarmonyKeen-style)"),
}


@dataclass
class ComposeResult:
    midi_path: str
    provenance_path: str
    method: str
    voices: list
    bpm: int


@dataclass
class ProduceResult:
    wav_path: str
    ogg_path: str = None
    method: str = None
    info: dict = field(default_factory=dict)


def _unit_from_events(events, section_len=None):
    """Build a MusicUnit from MusicEvent list.

    If `section_len` given, the terminal landmark lands exactly at
    section_len (the section's full length in ticks) — this guarantees
    every voice's section unit has the same length (zero-drift gate).
    """
    from structures import MusicUnit
    from structures import MusicEvent as _ME
    unit = MusicUnit()
    for ev in events:
        unit.add_event(ev)
    if section_len is None:
        section_len = max((ev.end_tick for ev in events), default=0)
    unit.add_event(_ME(0, 0, section_len, section_len))
    return unit


def _resolve_instrument(voice_name, instrument_name):
    """Return (voice_label, midi_program, channel). Drums → ch9."""
    if instrument_name.lower() in ("drum kit", "drums", "percussion"):
        return voice_name, 0, 9
    inst = _instr_by_name(instrument_name)
    return voice_name, inst.midi_program, 0


def compose(style="pop", method=None, form=None, key="C", bpm=None,
            voices=None, num_bars=32, seed=None, out_dir=None,
            sections=None):
    """Compose a piece through the musicom engine (zero-drift guaranteed).

    Uses the UnitMatrixComposer with the requested voices. If `method` is
    None, picks a default per style. Returns ComposeResult with paths.

    Note: the UnitMatrixComposer needs actual note material per section.
    This entry point sets up the framework; a composition agent fills the
    cells (via the engine API) and calls to_midi. For a ready-to-run
    example see `examples/compose_demo.py`.
    """
    bpm = bpm or STYLE_REGISTRY.get(style, {}).get("bpm", 120)
    form = form or STYLE_REGISTRY.get(style, {}).get("form", "intro-verse-chorus-bridge-outro")
    voices = voices or STYLE_REGISTRY.get(style, {}).get("default_voices",
             [("Lead", "Flute"), ("Pad", "Piano"), ("Bass", "Double Bass"),
              ("Arp", "Clarinet"), ("Drums", "Drum Kit")])
    method = method or "001"  # Skeleton-First default

    out_dir = Path(out_dir or f"/opt/data/projects/Styles/{style.title()}/workflow-demo")
    midi_dir = out_dir / "MIDI"
    midi_dir.mkdir(parents=True, exist_ok=True)
    midi_path = midi_dir / f"{style}-{method}.mid"

    composer = UnitMatrixComposer(bpm=bpm, ticks_per_beat=480, beats_per_bar=4)
    num_sections = 5
    composer.create_matrix(num_voices=len(voices), num_sections=num_sections)
    for i, (vname, inst_name) in enumerate(voices):
        label, prog, ch = _resolve_instrument(vname, inst_name)
        composer.add_voice(label, program=prog, channel=ch)

    # sections per form (default pop: intro/verse/chorus/bridge/outro)
    section_names = sections or ["Intro", "Verse", "Chorus", "Bridge", "Outro"]
    bars_per = [4, 8, 8, 4, 4] if len(section_names) == 5 else [num_bars // len(section_names)] * len(section_names)
    for sname, nbars in zip(section_names, bars_per):
        composer.add_section(sname, bars=nbars)

    # --- fill cells with a real framework (I–V–vi–IV skeleton) --------------
    # Key → scale degree pitch sets; canonical tables live in rules/harmony.py
    from rules.harmony import CHORD_SHAPES, KEY_OFFSET, QUALITY_INTERVALS
    off = KEY_OFFSET.get(key, 0)
    # chords: [I, V, vi, IV] as (root, quality) where quality is
    # "maj" (0,4,7) or "min" (0,3,7)
    PROG = [("I", 0), ("V", 1), ("vi", 2), ("IV", 3)]  # per 2-bar slot
    BAR = 1920
    # ---- abstract path: ABS-* method -> subset-network progression --------
    # LAYER_ARCHITECTURE.md: abstract layer designs the harmony as a walk
    # through 12TET subsets (z-relations, tension curve); concrete layer
    # realizes it. When method is ABS-*, run the subset walk and derive the
    # per-section chord tones from the walked patterns instead of the
    # hardcoded I–V–vi–IV.
    _is_abs = str(method).startswith("ABS")
    chord_tones_by_section = []
    if _is_abs:
        from rules.subset_network import (patterns_from_degrees,
                                          PatternNetwork, standard_patterns,
                                          interval_vector, tension)
        # The abstract->concrete bridge now lives in rules/realize.py instead
        # of being six hardcoded inline lines here. realize_tonal_cluster()
        # is byte-identical to the previous inline formula (pinned by
        # tests/test_realize_bridge.py), so this refactor is provably
        # output-neutral rather than approximately equivalent.
        from rules.realize import realize_tonal_cluster
        rng = __import__("random").Random(seed)
        net_lib = PatternNetwork(standard_patterns())
        # anchor: tonic-major plus its P/L/R-close neighbors for the walk
        anchor_ids = ["maj0", "min9", "maj5", "min2", "dom70", "maj70"]
        anchor_pats = [net_lib.patterns[i] for i in anchor_ids]
        net = PatternNetwork(anchor_pats)
        # tension curve over the 5 sections: rise into chorus, peak bridge,
        # resolve outro (values are tension deltas; walk picks by closeness)
        curve = [0.0, 0.5, 1.0, 1.5, 0.2]
        walk = net.walk("maj0", len(section_names), rng=rng,
                        tension_curve=curve, home="maj0")
        # per-section chord tones: pattern subset transposed into a register
        # (root ~48 = C3), plus the root itself for the bass
        chord_tones_by_section = []
        for pid in walk:
            pat = net_lib.patterns[pid]
            chord_tones_by_section.append(realize_tonal_cluster(pat))
        # provenance hook: the walk is embedded in the method string below
        method = f"{method}:subset_walk={','.join(walk)}"
    chord_roots = []
    for deg, _ in PROG:
        root, qual = CHORD_SHAPES[deg]
        # roots: I=C, V=G, vi=A, IV=F in C major → scale offsets
        root_midi = 48 + off + root  # bass octave
        chord_roots.append((root_midi, qual))
    # 5 sections × 4 bars each = 20 bars; repeat the 4-chord prog
    slots = []
    for s in range(5):
        for b in range(4):
            slots.append(chord_roots[(b) % 4])
    # build per-voice material
    from structures import MusicEvent
    for s, sname in enumerate(section_names):
        # find the chord for this section's first bar (framework: hold chord per section)
        if _is_abs:
            # abstract path: chord tones come from the walked subset
            chord_tones = chord_tones_by_section[s]
            root_midi = chord_tones[0]
            qual = "min" if len(chord_tones) > 0 else "maj"  # unused below on this path
        else:
            root_midi, qual = chord_roots[s % 4]
            third = 3 if qual == "min" else 4
            fifth = 7
            chord_tones = [root_midi, root_midi + third, root_midi + fifth]
        section_bars = bars_per[s]
        section_len = section_bars * BAR
        # Lead: arpeggio of chord tones (8th notes)
        lead_evs = []
        for b in range(section_bars * 2):
            step = chord_tones[b % 3] + 12  # octave up for lead
            lead_evs.append(MusicEvent(step, 90, b * 960, b * 960 + 480))
        lead_unit = _unit_from_events(lead_evs, section_len)
        composer.fill_voice_section(voices[0][0], sname, lead_unit)
        # Pad: sustained chord (whole-section)
        pad_evs = [MusicEvent(chord_tones[i], 60, 0, section_len) for i in range(3)]
        composer.fill_voice_section(voices[1][0], sname, _unit_from_events(pad_evs, section_len))
        # Bass: root on beats 1 & 3
        bass_evs = [MusicEvent(root_midi, 95, b * BAR, b * BAR + 900) for b in range(section_bars)]
        composer.fill_voice_section(voices[2][0], sname, _unit_from_events(bass_evs, section_len))
        # Arp (if present): 16th-note arpeggio
        if len(voices) > 3:
            arp_evs = []
            for b in range(section_bars * 4):
                note = chord_tones[b % 3] + 12
                arp_evs.append(MusicEvent(note, 70, b * 480, b * 480 + 240))
            composer.fill_voice_section(voices[3][0], sname, _unit_from_events(arp_evs, section_len))
        # Drums (if present): kick on 1&3, snare on 2&4, hat on 8ths
        if len(voices) > 4 and voices[4][1].lower() in ("drum kit", "drums", "percussion"):
            drum_evs = []
            for b in range(section_bars):
                bar_start = b * BAR
                drum_evs.append(MusicEvent(36, 100, bar_start, bar_start + 120))       # kick 1
                drum_evs.append(MusicEvent(38, 90, bar_start + 960, bar_start + 1080))  # snare 3
                for h in range(8):
                    drum_evs.append(MusicEvent(42, 60, bar_start + h * 240, bar_start + h * 240 + 120))  # hats
            composer.fill_voice_section(voices[4][0], sname, _unit_from_events(drum_evs, section_len))

    ok, msg = composer.validate()
    if not ok:
        raise RuntimeError(f"validate() failed: {msg}")
    composer.to_midi(str(midi_path))

    prov_path = write_provenance(
        artifact_path=str(midi_path),
        classification="ai-assisted",
        generator=f"musicom_workflow.compose(style={style}, method={method})",
        sources=[f"style_registry:{style}", f"method:{method}"],
        parameters={"bpm": bpm, "form": form, "voices": voices, "seed": seed},
    )
    return ComposeResult(
        midi_path=str(midi_path),
        provenance_path=str(prov_path) if prov_path else "",
        method=method,
        voices=voices,
        bpm=bpm,
    )


def _midi_to_notes(midi_path, sr=44100):
    """Parse a MIDI file into note dicts {pitch, start, end, velocity, role}.

    Program 33 (or drums ch9) → "bass"; melodic → "lead". Uses mido for
    READING only (analysis) — never for authoring (AGENTS.md rule).
    """
    import mido
    mid = mido.MidiFile(str(midi_path))

    def tick_to_sec(m, tick):
        # tempo map from track 0
        abs_tempos = []
        at = 0
        for msg in m.tracks[0]:
            at += msg.time
            if msg.type == "set_tempo":
                abs_tempos.append((at, msg.tempo))
        if not abs_tempos:
            abs_tempos = [(0, 500000)]
        sec = 0.0
        prev = 0
        cur = abs_tempos[0][1]
        for at, tmp in abs_tempos:
            if tick <= at:
                break
            sec += (at - prev) * cur / m.ticks_per_beat / 1_000_000
            prev = at
            cur = tmp
        sec += (tick - prev) * cur / m.ticks_per_beat / 1_000_000
        return sec

    notes = []
    for ti, track in enumerate(mid.tracks):
        program, channel = 0, 0
        for msg in track:
            if msg.type == "program_change":
                program, channel = msg.program, msg.channel
        abstick = 0
        active = {}
        for msg in track:
            abstick += msg.time
            if msg.type == "note_on" and msg.velocity > 0:
                active[msg.note] = (abstick, msg.velocity)
            elif msg.type in ("note_off",) or (msg.type == "note_on" and msg.velocity == 0):
                if msg.note in active:
                    s, vel = active.pop(msg.note)
                    if channel == 9:
                        role = "bass"  # drums → bass role (low)
                    else:
                        role = "bass" if program == 33 else "lead"
                    notes.append({
                        "pitch": msg.note, "velocity": vel,
                        "start": tick_to_sec(mid, s),
                        "end": tick_to_sec(mid, abstick),
                        "role": role, "program": program, "track": ti,
                    })
    notes.sort(key=lambda e: e["start"])
    return notes


def produce(midi_path, method="SP-001", params=None, out_dir=None,
            sr=44100):
    """Produce audio from a MIDI file using a sound production method.

    SP-001 (default): FluidSynth SoundFont render → WAV → OGG.
    Other methods use the shared sound/ modules (see SP_METHODS).
    """
    params = params or {}
    midi_path = str(midi_path)
    out_dir = Path(out_dir or Path(midi_path).parent.parent / "Audio")
    out_dir.mkdir(parents=True, exist_ok=True)
    base = Path(midi_path).stem

    if method == "SP-001":
        return _produce_fluidsynth(midi_path, out_dir, base, sr)

    if method == "SP-011":
        from sound.synthesis.karplus_strong import render_melody_wav
        notes = _midi_to_notes(midi_path)
        wav_path = out_dir / f"{base}-SP011.wav"
        audio, info = render_melody_wav(notes, wav_path, sr=sr, roles=params.get("roles"))
        ogg_path = out_dir / f"{base}-SP011.ogg"
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav_path),
             "-codec:a", "libopus", "-application", "voip", "-b:a", "48k", str(ogg_path)],
            capture_output=True, text=True)
        info.update({"wav_bytes": wav_path.stat().st_size,
                     "ogg_bytes": ogg_path.stat().st_size if ogg_path.exists() else 0})
        return ProduceResult(wav_path=str(wav_path), ogg_path=str(ogg_path),
                             method=method, info=info)

    if method == "SP-075":
        # Voice-like hybrid: synthesize the "singing" tracks with
        # VoiceLikeInstrument, render the rest with the soundfont.
        # params["voice_instruments"] is a list aligned to the MIDI's
        # note-bearing tracks (voice order); None = use the soundfont.
        from sound.render.hybrid import render_hybrid
        vi = params.get("voice_instruments")
        if vi is None:
            raise ValueError(
                "SP-075 needs params['voice_instruments'] — a list aligned to "
                "the MIDI's note-bearing tracks, e.g. ['talkbox', None, None]. "
                "Voice order is the composer's add_voice() order.")
        wav_path = out_dir / f"{base}-SP075.wav"
        info = render_hybrid(
            midi_path, vi, str(wav_path), sr=sr,
            bpm=params.get("bpm"), vowels=params.get("vowels"),
            voice_gain=params.get("voice_gain", 1.0),
            backing_gain=params.get("backing_gain", 1.0),
            seed=params.get("seed", 0))
        ogg_path = out_dir / f"{base}-SP075.ogg"
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav_path),
             "-codec:a", "libopus", "-application", "voip", "-b:a", "48k",
             str(ogg_path)],
            capture_output=True, text=True)
        info.update({"wav_bytes": wav_path.stat().st_size,
                     "ogg_bytes": ogg_path.stat().st_size if ogg_path.exists() else 0})
        return ProduceResult(wav_path=str(wav_path), ogg_path=str(ogg_path),
                             method=method, info=info)

    if method in SP_METHODS:
        mod_path, desc = SP_METHODS[method]
        mod = _import(mod_path)
        # generic path: if module has a demo/render that accepts notes
        # (see individual modules for their exact API)
        info = {"method": method, "module": mod_path, "description": desc,
                "params": params}
        raise NotImplementedError(
            f"{method} ({desc}) is implemented in {mod_path} but the workflow "
            f"adapter for it is not yet wired. Call the module directly: "
            f"from {mod_path} import ...")

    raise ValueError(f"Unknown production method {method!r}. Available: {sorted(SP_METHODS)}")


def _import(mod_path):
    parts = mod_path.split(".")
    mod = __import__(".".join(parts[:-1]), fromlist=[parts[-1]])
    return getattr(mod, parts[-1]) if len(parts) > 1 else mod


def _produce_fluidsynth(midi_path, out_dir, base, sr):
    """FluidSynth SoundFont render → WAV → OGG (SP-001)."""
    wav_path = out_dir / f"{base}.wav"
    ogg_path = out_dir / f"{base}.ogg"
    from utilities.env import fluidsynth_bin
    sf = discover_soundfont()
    if not sf:
        raise FileNotFoundError("No SoundFont found — install FluidR3_GM.sf2 or TimGM6mb.sf2")
    r = subprocess.run(
        [fluidsynth_bin(), "-ni", "-g", "1.2", "-F", str(wav_path), sf, midi_path],
        capture_output=True, text=True)
    if r.returncode != 0 or not wav_path.exists() or wav_path.stat().st_size < 1000:
        raise RuntimeError(f"fluidsynth failed: {r.stderr[-500:]}")
    r2 = subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav_path),
         "-codec:a", "libopus", "-application", "voip", "-b:a", "48k", str(ogg_path)],
        capture_output=True, text=True)
    if r2.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {r2.stderr[-300:]}")
    return ProduceResult(wav_path=str(wav_path), ogg_path=str(ogg_path),
                         method="SP-001",
                         info={"sr": sr, "bytes_wav": wav_path.stat().st_size})


def method_table():
    """Markdown table of composition methods (for docs/)."""
    rows = ["| ID | Method |", "|---|---|"]
    rows += [f"| {k} | {v} |" for k, v in sorted(COMPOSITION_METHODS.items())]
    return "\n".join(rows)


def sp_method_table():
    """Markdown table of sound production methods (for docs/)."""
    rows = ["| ID | Module | Description |", "|---|---|---|"]
    for k, (m, d) in sorted(SP_METHODS.items()):
        rows.append(f"| {k} | `{m}` | {d} |")
    return "\n".join(rows)


def style_table():
    """Markdown table of style templates (for docs/)."""
    rows = ["| Style | BPM | Form | Motion |", "|---|---|---|---|"]
    for k, v in sorted(STYLE_REGISTRY.items()):
        rows.append(f"| {k} | {v['bpm']} | {v['form']} | {v['motion']} |")
    return "\n".join(rows)


if __name__ == "__main__":
    print("=== COMPOSITION METHODS ===")
    print(method_table())
    print()
    print("=== SOUND PRODUCTION METHODS ===")
    print(sp_method_table())
    print()
    print("=== STYLES ===")
    print(style_table())
