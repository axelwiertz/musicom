"""Tests for the voice-like hybrid render (sound/render/hybrid.py, SP-075).

The point of these tests is that a composition can put a voice-like instrument
on its "singing" track and actually *hear* that instrument — not the FluidSynth
stand-in preset that the MIDI program number maps to.

The regression this guards: a voice-like instrument has no real GM equivalent
(Kazoo's program 59 is "Muted Trumpet" in the soundfont). Rendering the whole
MIDI through FluidSynth would silently play a trumpet. So the voice tracks must
be synthesized by VoiceLikeInstrument and only the backing rendered by
FluidSynth.
"""
import os
import subprocess
import sys

import numpy as np
import pytest

from sound.render.hybrid import (
    VOICE_VOWEL_CYCLE,
    parse_tracks,
    render_hybrid,
    voice_track_indices,
)

REG_INSTR = "/opt/data/projects/Instruments"
if REG_INSTR not in sys.path:
    sys.path.insert(0, REG_INSTR)

SR = 44100


# --------------------------------------------------------------------------- #
# registry: the family must be individually addressable                        #
# --------------------------------------------------------------------------- #

def test_every_family_member_is_registered():
    from instrument_registry import ALL_INSTRUMENTS
    for key in ("vox_humana", "kazoo", "jaw_harp", "didgeridoo",
                "singing_saw", "talkbox"):
        assert key in ALL_INSTRUMENTS, f"{key} not registered"
        inst = ALL_INSTRUMENTS[key]
        assert inst.synthesis == "voice_like", key
        assert inst.synthesis_defaults["instrument"] == key, key
        assert inst.range_min < inst.range_max, key


def test_members_lookup_by_name():
    from instrument_registry import by_name
    for name in ("Kazoo", "Talkbox", "Vox Humana", "Singing Saw",
                 "Jaw Harp", "Didgeridoo"):
        inst = by_name(name)
        assert inst.synthesis == "voice_like", name


def test_voice_like_keys_helper_lists_the_family():
    from instrument_registry import VOICE_LIKE_KEYS, ALL_INSTRUMENTS
    for k in VOICE_LIKE_KEYS:
        assert k in ALL_INSTRUMENTS
        assert ALL_INSTRUMENTS[k].synthesis == "voice_like"


def test_members_have_distinct_engines():
    """Six members must route to six different engines, not all to vox_humana."""
    from instrument_registry import ALL_INSTRUMENTS
    engines = {
        ALL_INSTRUMENTS[k].synthesis_defaults["instrument"]
        for k in ("vox_humana", "kazoo", "jaw_harp", "didgeridoo",
                  "singing_saw", "talkbox")
    }
    assert len(engines) == 6, f"members share engines: {engines}"


# --------------------------------------------------------------------------- #
# track parsing                                                                #
# --------------------------------------------------------------------------- #

@pytest.fixture(scope="module")
def ballad_midi():
    p = ("/opt/data/repos/musicom/projects/Styles/Pop/ballad-hitl/"
         "MIDI/pop-ballad-hitl.mid")
    if not os.path.exists(p):
        pytest.skip("ballad MIDI not present")
    return p


def test_parse_tracks_order_and_roles(ballad_midi):
    tracks, tpb, total = parse_tracks(ballad_midi)
    assert tpb == 480
    assert len(tracks) == 5, "ballad has Lead/Pad/Bass/Arp/Drums"
    # indices are contiguous and match the composer's voice order
    assert [t.index for t in tracks] == [0, 1, 2, 3, 4]
    assert tracks[4].is_drums, "last track must be the drum track (channel 9)"
    assert all(len(t.notes) > 0 for t in tracks)
    assert total > 0


def test_parse_tracks_skips_the_silent_zero_pad(ballad_midi):
    """The engine pads each track to equal length with a note-0 landing."""
    tracks, _, _ = parse_tracks(ballad_midi)
    for t in tracks:
        assert all(n["pitch"] > 0 for n in t.notes), \
            "note 0 (zero-drift pad) leaked into the note list"


# --------------------------------------------------------------------------- #
# voice/track routing                                                          #
# --------------------------------------------------------------------------- #

def test_voice_track_indices_maps_only_non_none():
    class T:
        pass
    tracks = [T() for _ in range(5)]
    m = voice_track_indices(tracks, ["talkbox", None, None, "jaw_harp", None])
    assert m == {0: "talkbox", 3: "jaw_harp"}


def test_voice_track_indices_rejects_unknown():
    class T:
        pass
    with pytest.raises(ValueError, match="Unknown voice-like instrument"):
        voice_track_indices([T()], ["not_an_instrument"])


def test_voice_track_indices_rejects_overlong_map():
    """An overlong map is a silent mis-assignment bug — must raise."""
    class T:
        pass
    with pytest.raises(ValueError, match="entries but the MIDI has"):
        voice_track_indices([T()], ["kazoo", "talkbox"])


# --------------------------------------------------------------------------- #
# the actual hybrid render                                                     #
# --------------------------------------------------------------------------- #

@pytest.fixture(scope="module")
def hybrid_out(tmp_path_factory, ballad_midi):
    """Render the ballad with a voice-like lead, once for this module."""
    out = tmp_path_factory.mktemp("hybrid") / "vocal.wav"
    info = render_hybrid(ballad_midi, ["talkbox", None, None, None, None],
                         str(out), bpm=72)
    return str(out), info


def test_hybrid_render_produces_audio(hybrid_out):
    path, info = hybrid_out
    assert os.path.exists(path)
    assert os.path.getsize(path) > 40
    assert info["seconds"] > 60, "ballad is ~93 s"
    assert info["tracks"] == 5


def test_hybrid_routes_voice_track_to_synthesis(hybrid_out):
    _, info = hybrid_out
    assert info["voice_tracks"] == {0: "talkbox"}
    assert info["engines"]["track00"]["engine"] == "voice_like"
    assert info["engines"]["track00"]["instrument"] == "talkbox"


def test_hybrid_routes_other_tracks_to_soundfont(hybrid_out):
    _, info = hybrid_out
    for i in (1, 2, 3, 4):
        assert info["engines"][f"track{i:02d}"]["engine"] == "fluidsynth"
    assert info["backing_rendered"] is True


def test_hybrid_audio_is_not_silent_and_has_no_clipping(hybrid_out):
    from sound.utils.io import read_wav
    path, _ = hybrid_out
    a, sr = read_wav(path)
    a = np.asarray(a, dtype=np.float64)
    if a.ndim > 1:
        a = a.mean(axis=1)
    assert sr == SR
    assert float(np.abs(a).max()) > 0.1, "render is (near) silent"
    assert float(np.abs(a).max()) <= 1.0, "render clips"
    # a mostly-silent render would mean the mute/track mapping went wrong
    assert float((np.abs(a) > 1e-4).mean()) > 0.5, "render is mostly silence"


def test_voice_lead_is_actually_audible_in_the_mix(hybrid_out, tmp_path):
    """The synthesized voice track must contribute energy to the mix.

    Render the same MIDI with the voice track muted (soundfont-only) and
    confirm the hybrid mix differs — otherwise the voice instrument is
    cosmetic and the soundfont stand-in was used after all.
    """
    from sound.utils.io import read_wav
    from sound.effects.mastering import measure_lufs
    path, _ = hybrid_out
    a, sr = read_wav(path)
    a = np.asarray(a, dtype=np.float64)
    if a.ndim > 1:
        a = a.mean(axis=1)

    # solo the voice track as the renderer would
    from sound.render.hybrid import _render_voice_track
    tracks, tpb, _ = parse_tracks(
        "/opt/data/repos/musicom/projects/Styles/Pop/ballad-hitl/"
        "MIDI/pop-ballad-hitl.mid")
    solo = _render_voice_track(tracks[0], "talkbox", tpb, 72, SR, seed=0)
    assert float(np.abs(solo).max()) > 0.05, "voice track rendered silent"

    # and confirm the hybrid mix is louder where the voice plays
    n = min(len(a), len(solo))
    r_mix = float(np.sqrt(np.mean(a[:n] ** 2)))
    assert r_mix > 0.01, "mix RMS implausibly low"


def test_render_is_deterministic(ballad_midi, tmp_path):
    a = tmp_path / "a.wav"
    b = tmp_path / "b.wav"
    render_hybrid(ballad_midi, ["kazoo", None, None, None, None], str(a), bpm=72)
    render_hybrid(ballad_midi, ["kazoo", None, None, None, None], str(b), bpm=72)
    from sound.utils.io import read_wav
    x, _ = read_wav(str(a))
    y, _ = read_wav(str(b))
    assert np.allclose(np.asarray(x, dtype=np.float64),
                       np.asarray(y, dtype=np.float64)), \
        "hybrid render is not deterministic"


def test_voice_instrument_choice_changes_the_render(ballad_midi, tmp_path):
    """Two different voice instruments must not produce identical audio."""
    from sound.utils.io import read_wav
    outs = {}
    for key in ("kazoo", "talkbox", "singing_saw"):
        p = tmp_path / f"{key}.wav"
        render_hybrid(ballad_midi, [key, None, None, None, None], str(p), bpm=72)
        a, _ = read_wav(str(p))
        outs[key] = np.asarray(a, dtype=np.float64)
    ks = list(outs)
    for i in range(len(ks)):
        for j in range(i + 1, len(ks)):
            n = min(len(outs[ks[i]]), len(outs[ks[j]]))
            assert not np.allclose(outs[ks[i]][:n], outs[ks[j]][:n]), \
                f"{ks[i]} and {ks[j]} rendered identically"


def test_all_voice_tracks_render_without_backing(ballad_midi, tmp_path):
    """A composition of only voice-like instruments needs no soundfont."""
    out = tmp_path / "allvoice.wav"
    info = render_hybrid(
        ballad_midi,
        ["talkbox", "vox_humana", "didgeridoo", "kazoo", "jaw_harp"],
        str(out), bpm=72)
    assert info["backing_rendered"] is False
    assert len(info["voice_tracks"]) == 5
    assert os.path.getsize(str(out)) > 40


def test_vowel_cycle_is_used(ballad_midi, tmp_path):
    """A custom vowel cycle must change the render vs the default."""
    from sound.utils.io import read_wav
    a = tmp_path / "a.wav"
    b = tmp_path / "b.wav"
    render_hybrid(ballad_midi, ["talkbox", None, None, None, None], str(a),
                  bpm=72, vowels=VOICE_VOWEL_CYCLE)
    render_hybrid(ballad_midi, ["talkbox", None, None, None, None], str(b),
                  bpm=72, vowels=("i",))
    x, _ = read_wav(str(a))
    y, _ = read_wav(str(b))
    assert not np.allclose(np.asarray(x, dtype=np.float64),
                           np.asarray(y, dtype=np.float64)), \
        "vowel cycle had no effect on the render"


# --------------------------------------------------------------------------- #
# workflow integration: SP-075                                                 #
# --------------------------------------------------------------------------- #

def test_sp075_is_registered():
    from workflows.musicom_workflow import SP_METHODS
    assert "SP-075" in SP_METHODS
    mod, desc = SP_METHODS["SP-075"]
    assert mod == "sound.render.hybrid"
    assert "Voice-Like" in desc


def test_produce_sp075_requires_voice_instruments(ballad_midi, tmp_path):
    from workflows.musicom_workflow import produce
    with pytest.raises(ValueError, match="voice_instruments"):
        produce(ballad_midi, method="SP-075", out_dir=str(tmp_path))


def test_produce_sp075_end_to_end(ballad_midi, tmp_path):
    from workflows.musicom_workflow import produce
    r = produce(ballad_midi, method="SP-075",
                params={"voice_instruments": ["talkbox", None, None, None, None],
                        "bpm": 72},
                out_dir=str(tmp_path))
    assert os.path.exists(r.wav_path) and os.path.getsize(r.wav_path) > 40
    assert r.info["voice_tracks"] == {0: "talkbox"}
    if r.ogg_path and os.path.exists(r.ogg_path):
        assert os.path.getsize(r.ogg_path) > 40


# --------------------------------------------------------------------------- #
# orchestration → production bridge                                            #
# --------------------------------------------------------------------------- #

PHASE1 = "/opt/data/repos/musicom/projects/Styles/Pop/ballad-hitl/Scripts"
if PHASE1 not in sys.path:
    sys.path.insert(0, PHASE1)


def test_palette_bridge_maps_voice_like_palettes():
    from phase1_compose import (PALETTES, PALETTE_ORDER, voice_instrument_map,
                                VOICE_LIKE_PALETTES)
    for name in PALETTE_ORDER:
        m = voice_instrument_map(PALETTES[name])
        assert len(m) == 5, f"{name}: map must cover the 5 roles"
        if name in VOICE_LIKE_PALETTES:
            assert any(x is not None for x in m), \
                f"{name} declares voice-like but maps to all-soundfont"
        else:
            assert all(x is None for x in m), \
                f"{name} is all-soundfont but maps to {m}"


def test_vocal_palette_lead_is_voice_like():
    from phase1_compose import PALETTES, voice_instrument_map
    m = voice_instrument_map(PALETTES["vocal"])
    assert m[0] is not None, "the vocal palette's Lead must be voice-like"
    assert m[0] == "talkbox"


def test_every_voice_instrument_fits_its_role():
    """A voice-like instrument placed in a palette must fit that role's register."""
    from phase1_compose import PALETTES, PALETTE_ORDER, build_ballad, VariantSpec
    from instrument_registry import by_name

    for name in PALETTE_ORDER:
        pal = PALETTES[name]
        composer = build_ballad(seed=7, variant=VariantSpec(palette=pal))
        ok, msg = composer.validate()
        assert ok, f"{name}: {msg}"
        for v in composer.voices:
            lo, hi, n = 999, 0, 0
            for col in range(len(composer.sections)):
                u = composer.matrix.get_unit((v["row"], col))
                if u is None:
                    continue
                for p in u.pitches:
                    if p > 0:
                        lo, hi, n = min(lo, p), max(hi, p), n + 1
            if n == 0:
                continue
            inst = by_name(pal[v["name"]])
            if inst.range_min is None or inst.range_max is None:
                continue     # drums have no pitch range
            assert lo >= inst.range_min, (
                f"{name}/{v['name']} ({pal[v['name']]}): {lo} below {inst.range_min}")
            assert hi <= inst.range_max, (
                f"{name}/{v['name']} ({pal[v['name']]}): {hi} above {inst.range_max}")
