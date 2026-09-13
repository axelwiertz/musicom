#!/usr/bin/env python
"""Voice-instrument ballad demo — voice-like instruments on the "singing" track.

Builds the pop ballad with the `vocal` palette (Lead = Talkbox, Arp = Jaw Harp)
and the `drone` palette (Lead = Singing Saw, Pad = Vox Humana, Bass =
Didgeridoo), renders each with the SP-075 hybrid pipeline (voice tracks
synthesized, backing band from the soundfont), then masters to LUFS -14 /
peak -1 dB and encodes OGG.

Also renders the SAME composition twice — once with the soundfont stand-in and
once with the voice instrument — so the difference is directly audible. That
is the honest check: a voice-like instrument has no real GM equivalent, and if
the hybrid routing ever regressed you would hear a Muted Trumpet instead of a
kazoo.

Usage:
    $MUSICOM_PYTHON render_vocal_ballad.py
"""
import os
import subprocess
import sys
from pathlib import Path

import numpy as np

REPO = Path("/opt/data/repos/musicom")
SCRIPT_DIR = REPO / "projects/Styles/Pop/ballad-hitl/Scripts"
OUT = REPO / "projects/Styles/Pop/ballad-hitl/Audio"
OUT.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, "/opt/data/projects/Instruments")

from phase1_compose import (  # noqa: E402
    PALETTES, VariantSpec, build_ballad, voice_instrument_map,
)
from sound.effects.mastering import Limiter, normalize_to_lufs  # noqa: E402
from sound.render.hybrid import render_hybrid  # noqa: E402
from sound.utils.io import read_wav, write_wav  # noqa: E402
from workflows.provenance import write_provenance  # noqa: E402

SR = 44100
BPM = 72


def master_and_encode(wav_in, base, title):
    """Master to LUFS -14 / peak -1 dB, then encode OGG + MP3-free opus."""
    a, sr = read_wav(str(wav_in))
    a = np.asarray(a, dtype=np.float64)
    if a.ndim > 1:
        a = a.mean(axis=1)
    a = normalize_to_lufs(a, target_lufs=-14.0, sample_rate=sr)
    a = Limiter(threshold_db=-1.0, release_ms=100.0, sample_rate=sr).process(a)
    wav = OUT / f"{base}.wav"
    ogg = OUT / f"{base}.ogg"
    write_wav(str(wav), a, sr, normalize=False)
    assert os.path.getsize(wav) > 40, "empty master WAV"
    r = subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav),
         "-c:a", "libvorbis", "-q:a", "6", str(ogg)],
        capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {r.stderr[-300:]}")

    from sound.effects.mastering import measure_lufs
    peak = float(np.max(np.abs(a)))
    lufs = measure_lufs(a, sr)
    silent = float((np.abs(a) < 1e-4).mean() * 100)
    print(f"  {base:34s} LUFS {lufs:6.2f}  peak {peak:.3f}  "
          f"silence {silent:4.1f}%  {os.path.getsize(ogg) // 1024:5d} KB")
    write_provenance(
        artifact_path=str(ogg), classification="ai-assisted",
        generator="render_vocal_ballad.py",
        sources=["phase1_compose.build_ballad", "sound.render.hybrid.render_hybrid"],
        parameters={"title": title, "bpm": BPM, "sr": sr,
                    "master": {"lufs": lufs, "peak": peak}},
    )
    return wav, ogg, lufs, peak

def build(palette_name, seed=7):
    """Build the ballad in a given palette; return (midi_path, voice_map)."""
    pal = PALETTES[palette_name]
    composer = build_ballad(seed=seed, variant=VariantSpec(palette=pal))
    ok, msg = composer.validate()
    assert ok, f"validate failed for {palette_name}: {msg}"
    midi = OUT / f"vocalballad-{palette_name}.mid"
    composer.to_midi(str(midi))
    assert os.path.getsize(midi) > 40, "empty MIDI"
    return midi, voice_instrument_map(pal), pal


def main():
    print("=" * 78)
    print("VOICE-INSTRUMENT BALLAD — voice-like instruments on the singing track")
    print("=" * 78)
    print(f"Ballad: D minor, {BPM} BPM, intro/verse/chorus/bridge/outro.")
    print("Voice-like instruments have no real GM equivalent, so their tracks are")
    print("synthesized (VoiceLikeInstrument) and the band is soundfont-rendered.\n")

    results = []

    # --- 1. the `vocal` palette: Talkbox lead + Jaw Harp texture ---
    print("1. palette 'vocal'  (Lead=Talkbox, Arp=Jaw Harp)")
    midi, vmap, pal = build("vocal")
    print(f"   voice routing: {vmap}")
    wav = OUT / "vocalballad-vocal-hybrid.wav"
    info = render_hybrid(str(midi), vmap, str(wav), sr=SR, bpm=BPM)
    assert info["backing_rendered"], "expected a soundfont backing"
    results.append(master_and_encode(
        wav, "vocalballad-vocal-talkbox-jawharp",
        "pop ballad, vocal palette (Talkbox lead, Jaw Harp arp)"))

    # --- 2. the `drone` palette: Singing Saw + Vox Humana + Didgeridoo ---
    print("\n2. palette 'drone'  (Lead=Singing Saw, Pad=Vox Humana, Bass=Didgeridoo)")
    midi, vmap, pal = build("drone")
    print(f"   voice routing: {vmap}")
    wav = OUT / "vocalballad-drone-hybrid.wav"
    info = render_hybrid(str(midi), vmap, str(wav), sr=SR, bpm=BPM)
    results.append(master_and_encode(
        wav, "vocalballad-drone-singingsaw-didge",
        "pop ballad, drone palette (Singing Saw, Vox Humana, Didgeridoo)"))

    # --- 3. the honest A/B: same notes, soundfont vs voice instrument ---
    print("\n3. A/B — SAME Lead line, soundfont stand-in vs voice instrument")
    print("   (Lead program 80 = 'Lead 1 (square)' in the soundfont,")
    print("    i.e. a square lead — NOT a talkbox. This is what the")
    print("    hybrid routing is preventing.)")
    midi, vmap, pal = build("vocal")
    # (a) everything through the soundfont — the "wrong" render
    from sound.render.pipeline import RenderPipeline
    from sound.render.fluidsynth import discover_soundfont
    sf = discover_soundfont()
    if not sf:
        raise FileNotFoundError("No SoundFont found for the A/B reference render")
    pipe = RenderPipeline(sample_rate=SR, soundfont_path=sf)
    sf_wav = OUT / "vocalballad-AB-soundfont.wav"
    pipe.render_to_wav(str(midi), str(sf_wav), soundfont=sf)
    assert os.path.getsize(sf_wav) > 40
    results.append(master_and_encode(
        sf_wav, "vocalballad-AB-a-soundfont-square",
        "A/B A: Lead via soundfont stand-in (square lead)"))
    # (b) the hybrid render — the voice instrument
    hy_wav = OUT / "vocalballad-AB-hybrid.wav"
    render_hybrid(str(midi), vmap, str(hy_wav), sr=SR, bpm=BPM)
    results.append(master_and_encode(
        hy_wav, "vocalballad-AB-b-talkbox",
        "A/B B: Lead synthesized as a Talkbox (voice-like)"))

    print("\n" + "=" * 78)
    print("SUMMARY")
    print("=" * 78)
    print(f"{'artifact':42s} {'LUFS':>8s} {'peak':>6s}")
    print("-" * 78)
    for _wav, ogg, lufs, peak in results:
        print(f"  {ogg.stem:42s} {lufs:8.2f} {peak:6.3f}")
    print(f"\nOutputs in {OUT}")
    print("DONE")


if __name__ == "__main__":
    main()
