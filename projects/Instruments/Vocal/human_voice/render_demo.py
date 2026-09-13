# -*- coding: utf-8 -*-
"""Render a singing-voice demo phrase and write WAV + OGG for delivery.

Shows the instrument in action: a short phrase sung by each voice type,
plus a vowel-identity demonstration (same pitch, /a/ /e/ /i/ /o/ /u/).
"""
import subprocess
from pathlib import Path

import numpy as np

from sound.synthesis.singing_voice import SingingVoice
from sound.utils.io import write_wav

SR = 44100
OUT = Path("/opt/data/repos/musicom/projects/Instruments/Vocal/human_voice/audio")
OUT.mkdir(parents=True, exist_ok=True)

# A short, idiomatic vocal phrase: do-re-mi-fa-sol-fa-mi-re-do (C major),
# sung with Italian vowels. MIDI = C4..G4.
PHRASE = [
    (60, 0.45, "a"), (62, 0.45, "a"), (64, 0.45, "e"),
    (65, 0.45, "e"), (67, 0.9,  "i"), (65, 0.45, "e"),
    (64, 0.45, "e"), (62, 0.45, "o"), (60, 0.9,  "u"),
]


def _to_ogg(wav_path: Path, ogg_path: Path):
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav_path),
         "-codec:a", "libopus", "-application", "voip", "-b:a", "96k",
         str(ogg_path)], check=True)


def main():
    artifacts = {}

    # 1. one phrase per voice type (timbre contrast)
    for vt in ("bass", "tenor", "alto", "soprano"):
        voice = SingingVoice(sample_rate=SR, voice_type=vt)
        # transpose so each sits in its comfortable register
        shift = {"bass": -12, "tenor": 0, "alto": 12, "soprano": 12}[vt]
        notes = [(p + shift, d, v) for (p, d, v) in PHRASE]
        wav = voice.render_phrase(notes, aspiration=0.08)
        wav_path = OUT / f"phrase_{vt}.wav"
        ogg_path = OUT / f"phrase_{vt}.ogg"
        write_wav(str(wav_path), wav, SR)
        _to_ogg(wav_path, ogg_path)
        artifacts[vt] = str(ogg_path)
        print(f"{vt:8s} phrase -> {ogg_path.name} "
              f"({ogg_path.stat().st_size} B, rms {np.sqrt(np.mean(wav**2)):.3f})")

    # 2. vowel identity demo: same pitch (A4), five vowels
    voice = SingingVoice(sample_rate=SR, voice_type="alto")
    vowel_notes = [(69, 0.5, v) for v in ("a", "e", "i", "o", "u")]
    wav = voice.render_phrase(vowel_notes, legato=False)
    wav_path = OUT / "vowels_a_e_i_o_u.wav"
    ogg_path = OUT / "vowels_a_e_i_o_u.ogg"
    write_wav(str(wav_path), wav, SR)
    _to_ogg(wav_path, ogg_path)
    artifacts["vowels"] = str(ogg_path)
    print(f"vowels  a/e/i/o/u -> {ogg_path.name} ({ogg_path.stat().st_size} B)")

    # 3. breathy vs clean contrast
    clean = SingingVoice(sample_rate=SR, voice_type="alto")
    breathy = SingingVoice(sample_rate=SR, voice_type="alto", open_quotient=0.55)
    c = clean.render_note(69, 1.5, "a")
    b = breathy.render_note(69, 1.5, "a", aspiration=0.5)
    both = np.concatenate([c, np.zeros(SR // 4), b])
    wav_path = OUT / "clean_vs_breathy.wav"
    ogg_path = OUT / "clean_vs_breathy.ogg"
    write_wav(str(wav_path), both, SR)
    _to_ogg(wav_path, ogg_path)
    artifacts["breathy"] = str(ogg_path)
    print(f"contrast clean/breathy -> {ogg_path.name} ({ogg_path.stat().st_size} B)")

    print("\nDELIVER:")
    for k, v in artifacts.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
