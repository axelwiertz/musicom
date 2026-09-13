"""Hybrid render — voice-like instrument tracks + FluidSynth backing.

Voice-like instruments (sound/synthesis/voice_like.py) have **no real GM
soundfont equivalent**. A FluidSynth render of a track assigned "Kazoo" would
play the GM stand-in (program 59 = Muted Trumpet), not a kazoo — the MIDI
program number exists only so the part is identifiable on export.

So rendering a composition that uses them needs two engines on one file:

    voice tracks  ->  VoiceLikeInstrument (synthesis, per-track)
    other tracks  ->  FluidSynth (soundfont, the backing band)
    then sum, master, encode.

This module does that. It is the production counterpart to giving a
composition a "singing" track played by a voice-like instrument.

Usage
-----
    from sound.render.hybrid import render_hybrid

    # note-track order matches the composer's voice order (Lead, Pad, ...)
    render_hybrid("song.mid", ["talkbox", None, None, None, None],
                  "song-voice.wav")

`voice_instruments` is a list aligned to the MIDI's note-bearing tracks (track
0, the tempo/meta track, is always skipped — same convention as
`RenderPipeline.render_stems`). Each entry is either a voice-like instrument
key (``"kazoo"``, ``"talkbox"``, ...) or None for "render this track with the
soundfont".
"""

import os
import subprocess
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from ..synthesis.voice_like import INSTRUMENTS, VoiceLikeInstrument
from ..utils.io import read_wav, write_wav

__all__ = [
    "TrackInfo", "parse_tracks", "render_hybrid", "voice_track_indices",
    "VOICE_VOWEL_CYCLE",
]

#: Default vowel sequence for a "singing" line — cycles so a melody reads as
#: articulated syllables rather than one static vowel.
VOICE_VOWEL_CYCLE: Tuple[str, ...] = ("a", "o", "e", "a", "u", "o")


@dataclass
class TrackInfo:
    """One note-bearing MIDI track."""

    index: int                  # position among note-bearing tracks
    midi_track: int             # index in mid.tracks
    channel: int
    program: int
    name: str
    notes: List[dict] = field(default_factory=list)   # pitch/vel/start_ticks/end_ticks

    @property
    def is_drums(self) -> bool:
        return self.channel == 9

    def span_ticks(self) -> int:
        return max((n["end_ticks"] for n in self.notes), default=0)


def parse_tracks(midi_path: str) -> Tuple[List[TrackInfo], int, int]:
    """Read a MIDI file into note-bearing tracks.

    Uses mido for READING only (the engine's authoring rule forbids it for
    writing). Returns ``(tracks, ticks_per_beat, total_ticks)`` where
    ``tracks`` is in the same order as `RenderPipeline.render_stems` assigns
    stem indices: note-bearing tracks only, track 0 (tempo) skipped.
    """
    import mido

    mid = mido.MidiFile(str(midi_path))
    tpb = mid.ticks_per_beat
    tracks: List[TrackInfo] = []
    total = 0

    for ti, track in enumerate(mid.tracks):
        has_notes = any(m.type in ("note_on", "note_off") for m in track)
        if not has_notes:
            continue

        program, channel = 0, 0
        for m in track:
            if m.type == "program_change":
                program, channel = m.program, m.channel
                break
        if channel == 0 and program == 0:
            note_chans = {m.channel for m in track if m.type == "note_on"}
            if note_chans == {9}:
                channel = 9

        info = TrackInfo(index=len(tracks), midi_track=ti, channel=channel,
                         program=program, name=track.name or f"track{len(tracks):02d}")

        abstick = 0
        active: Dict[int, Tuple[int, int]] = {}
        for m in track:
            abstick += m.time
            if m.type == "note_on" and m.velocity > 0:
                active[m.note] = (abstick, m.velocity)
            elif m.type == "note_off" or (m.type == "note_on" and m.velocity == 0):
                if m.note in active:
                    st, vel = active.pop(m.note)
                    # note 0 is the engine's silent zero-drift pad — skip it
                    if m.note > 0:
                        info.notes.append({"pitch": m.note, "velocity": vel,
                                           "start_ticks": st, "end_ticks": abstick})
        total = max(total, info.span_ticks())
        tracks.append(info)

    return tracks, tpb, total


def voice_track_indices(tracks: Sequence[TrackInfo],
                        voice_instruments: Sequence[Optional[str]]) -> Dict[int, str]:
    """Map track index → instrument key for the entries that are voice-like.

    Raises if the mapping is longer than the track list (a silent mismatch
    would otherwise render the wrong track with the wrong engine).
    """
    if len(voice_instruments) > len(tracks):
        raise ValueError(
            f"voice_instruments has {len(voice_instruments)} entries but the "
            f"MIDI has {len(tracks)} note tracks")
    out: Dict[int, str] = {}
    for idx, key in enumerate(voice_instruments):
        if key is None:
            continue
        if key not in INSTRUMENTS:
            raise ValueError(
                f"Unknown voice-like instrument {key!r}. "
                f"Available: {sorted(INSTRUMENTS)}")
        out[idx] = key
    return out


def _render_voice_track(track: TrackInfo, instrument: str, tpb: int, bpm: float,
                        sr: int, vowels: Optional[Sequence[str]] = None,
                        seed: int = 0) -> np.ndarray:
    """Synthesize one MIDI track with a voice-like instrument.

    Notes are placed on an **absolute timeline** (not concatenated), so rests
    and the groove survive. Vowels cycle through `vowels` per note so the line
    reads as articulated syllables.
    """
    sec_per_tick = 60.0 / (bpm * tpb)
    total = track.span_ticks()
    n_total = max(1, int(total * sec_per_tick * sr) + int(0.6 * sr))
    buf = np.zeros(n_total, dtype=np.float64)

    vs = tuple(vowels) if vowels else VOICE_VOWEL_CYCLE
    vi = VoiceLikeInstrument(instrument, sample_rate=sr, seed=seed)

    for i, note in enumerate(sorted(track.notes, key=lambda x: x["start_ticks"])):
        dur = (note["end_ticks"] - note["start_ticks"]) * sec_per_tick
        if dur <= 0:
            continue
        f0 = 440.0 * 2.0 ** ((note["pitch"] - 69) / 12.0)
        # slight gap so repeated notes re-articulate instead of merging
        seg = vi.render_note(f0, max(dur, 0.02), vowel=vs[i % len(vs)])
        start = int(note["start_ticks"] * sec_per_tick * sr)
        end = min(start + len(seg), n_total)
        if end <= start:
            continue
        vel = note["velocity"] / 127.0
        buf[start:end] += seg[: end - start] * (0.35 + 0.65 * vel)

    return buf


def _render_backing_fluidsynth(midi_path: str, mute_tracks: Sequence[int],
                               out_wav: str, tpb: int, sr: int) -> Optional[str]:
    """FluidSynth-render the MIDI with `mute_tracks` removed.

    Returns the WAV path, or None when there is nothing left to render (a
    composition made entirely of voice-like instruments).
    """
    import mido

    mid = mido.MidiFile(str(midi_path))
    keep = mido.MidiFile(ticks_per_beat=mid.ticks_per_beat)
    kept = 0
    for i, track in enumerate(mid.tracks):
        if i in set(mute_tracks):
            continue
        has_notes = any(m.type in ("note_on", "note_off") for m in track)
        is_tempo = any(m.type == "set_tempo" for m in track)
        if not has_notes and not is_tempo:
            continue
        new = mido.MidiTrack()
        for m in track:
            new.append(m)
        keep.tracks.append(new)
        if has_notes:
            kept += 1

    if kept == 0:
        return None

    tmp = os.path.join(os.path.dirname(out_wav) or ".", "_hybrid_backing.mid")
    keep.save(tmp)

    from .fluidsynth import discover_soundfont
    from utilities.env import fluidsynth_bin
    sf = discover_soundfont()
    if not sf:
        raise FileNotFoundError("No SoundFont found for the backing render")
    r = subprocess.run(
        [fluidsynth_bin(), "-ni", "-g", "1.2", "-F", str(out_wav), sf, tmp],
        capture_output=True, text=True)
    os.unlink(tmp)
    if r.returncode != 0 or not os.path.exists(out_wav) \
            or os.path.getsize(out_wav) < 1000:
        raise RuntimeError(f"fluidsynth backing render failed: {r.stderr[-400:]}")
    return out_wav


def render_hybrid(
    midi_path: str,
    voice_instruments: Sequence[Optional[str]],
    out_wav: str,
    sr: int = 44100,
    bpm: Optional[float] = None,
    vowels: Optional[Sequence[str]] = None,
    voice_gain: float = 1.0,
    backing_gain: float = 1.0,
    seed: int = 0,
    voice_indices: Optional[Sequence[int]] = None,
) -> dict:
    """Render a composition with voice-like instruments on selected tracks.

    Parameters
    ----------
    midi_path : str
        Composed MIDI (from the musicom engine).
    voice_instruments : list
        Aligned to the MIDI's note-bearing tracks (track 0 skipped). Each
        entry is a voice-like instrument key, or None for "use the soundfont".
    out_wav : str
        Output WAV path.
    bpm : float, optional
        Tempo. Read from the MIDI's tempo map when omitted.
    vowels : sequence, optional
        Vowel cycle for the singing line (default VOICE_VOWEL_CYCLE).
    voice_gain, backing_gain : float
        Relative levels. Voice defaults to 1.0, backing to 1.0.
    voice_indices : sequence, optional
        Override which track indices are voice-like (defaults to the non-None
        entries of `voice_instruments`).

    Returns
    -------
    dict
        Render metadata (tracks, engines, level, duration).
    """
    tracks, tpb, total_ticks = parse_tracks(midi_path)
    if not tracks:
        raise ValueError(f"No note-bearing tracks in {midi_path}")

    vmap = voice_track_indices(tracks, voice_instruments)
    if voice_indices is not None:
        vmap = {i: voice_instruments[i] for i in voice_indices
                if voice_instruments[i] is not None}
    vmap = {i: str(k) for i, k in vmap.items()}

    if bpm is None:
        bpm = _tempo_from_midi(midi_path, default=120.0)
    sec_per_tick = 60.0 / (bpm * tpb)
    n_total = max(1, int(total_ticks * sec_per_tick * sr) + int(0.8 * sr))

    # ---- voice-like tracks: synthesize ----
    mix = np.zeros(n_total, dtype=np.float64)
    engines = {}
    for idx, key in sorted(vmap.items()):
        t = tracks[idx]
        # a per-track seed keeps tracks independent but renders reproducible
        seg = _render_voice_track(t, key, tpb, bpm, sr, vowels=vowels,
                                 seed=seed + idx * 7919)
        if len(seg) >= n_total:
            mix += seg[:n_total] * voice_gain
        else:
            mix[: len(seg)] += seg * voice_gain
        engines[f"track{idx:02d}"] = {"engine": "voice_like",
                                      "instrument": key,
                                      "notes": len(t.notes)}

    # ---- everything else: soundfont ----
    # NOTE: must mute by index in `mid.tracks`, not by index among note-bearing
    # tracks — those differ whenever a track without notes sits between them.
    mute = [tracks[i].midi_track for i in vmap]
    backing_wav = os.path.join(os.path.dirname(out_wav) or ".", "_hybrid_backing.wav")
    got = _render_backing_fluidsynth(midi_path, mute, backing_wav, tpb, sr)
    if got:
        b, bsr = read_wav(got)
        if b.ndim > 1:
            b = b.mean(axis=1)
        b = b.astype(np.float64)
        if bsr != sr:
            raise ValueError(f"backing rendered at {bsr} Hz, expected {sr}")
        if len(b) >= n_total:
            mix[:n_total] += b[:n_total] * backing_gain
        else:
            mix[: len(b)] += b * backing_gain
        for i, t in enumerate(tracks):
            if i not in vmap:
                engines[f"track{i:02d}"] = {"engine": "fluidsynth",
                                            "program": t.program}
        os.unlink(got)
        backing_rendered = True
    else:
        backing_rendered = False

    peak = float(np.max(np.abs(mix)))
    if peak <= 0:
        raise RuntimeError("hybrid render produced silence")
    mix = mix / peak * 0.92
    write_wav(out_wav, mix, sr, normalize=False)
    assert os.path.getsize(out_wav) > 40, "empty hybrid WAV"

    return {
        "midi": str(midi_path), "wav": str(out_wav), "sr": sr, "bpm": bpm,
        "seconds": len(mix) / sr, "tracks": len(tracks),
        "voice_tracks": {tracks[i].index: k for i, k in vmap.items()},
        "engines": engines, "backing_rendered": backing_rendered,
        "voice_gain": voice_gain, "backing_gain": backing_gain,
        "peak": peak,
    }


def _tempo_from_midi(midi_path: str, default: float = 120.0) -> float:
    """First tempo in the MIDI's tempo track, as BPM."""
    import mido
    mid = mido.MidiFile(str(midi_path))
    for track in mid.tracks:
        for m in track:
            if m.type == "set_tempo":
                return 60_000_000.0 / m.tempo
    return default
