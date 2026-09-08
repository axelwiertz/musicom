#!/usr/bin/env python3
"""Fix verify scripts: solo render + discover_soundfont (buzz fix).

Transforms the old render block in verify_*.py:
    sf2 = ".../TimGM6mb.sf2"
    fluidsynth = ".../fluidsynth"
    wav = "..."
    r = subprocess.run([fluidsynth, "-ni", "-g", "1.2", "-F", wav, sf2, midi_path], ...)
    print(...); assert ...

into:
    from _test.render_audio import render_midi, spectral_buzz_check
    sf2_legacy = ".../TimGM6mb.sf2"   # kept for phdr/stem checks
    fluidsynth = ".../fluidsynth"
    wav = "..."
    render_midi(midi_path, wav, solo=1)   # instrument SOLO (no unison doubling)
    wsize = os.path.getsize(wav); assert wsize > 40
    ok, rep = spectral_buzz_check(wav); assert ok

Run: python fix_verify_render.py [file ...]   (default: all verify_*.py except the two already fixed)
"""
import re
import sys
import glob

T6 = "/opt/data/micromamba/envs/musicom/lib/python3.11/site-packages/pretty_midi/TimGM6mb.sf2"

def fix(path):
    src = open(path).read()
    if "_test.render_audio" in src:
        print(f"  skip (already fixed): {path}")
        return False
    if T6 not in src:
        print(f"  skip (no TimGM6mb render): {path}")
        return False

    # The old block: sf2 = T6 ... fluidsynth ... wav = ... subprocess.run ...
    # We replace the subprocess run + checks with the helper call.
    old_run = re.compile(
        r"r = subprocess\.run\(\[fluidsynth, \"-ni\", \"-g\", \"1\.2\", \"-F\", wav, sf2, midi_path\],\s*\n\s*capture_output=True\)"
    )
    if not old_run.search(src):
        print(f"  WARN no subprocess pattern: {path}")
    src = old_run.sub("render_midi(midi_path, wav, solo=1)  # instrument SOLO (buzz fix)", src)

    # Rename sf2 -> sf2_legacy ONLY in the assignment + remaining uses.
    # Careful: the path string contains ".sf2" — replace the exact
    # assignment line, then only bare identifier references.
    src = src.replace(f'sf2 = "{T6}"', f'sf2_legacy = "{T6}"')
    # any remaining bare sf2 references that are NOT sf2_legacy already
    src = re.sub(r'(?<!_legacy)\bsf2\b(?!")', 'sf2_legacy', src)
    # undo any accidental corruption of the path string itself
    src = src.replace(".sf2_legacy\"", ".sf2\"")

    # Insert helper import after "import subprocess" (or at top if absent)
    if "from _test.render_audio import" not in src:
        if "import subprocess" in src:
            src = src.replace("import subprocess",
                              "import subprocess\nfrom _test.render_audio import render_midi, spectral_buzz_check",
                              1)
        else:
            src = "from _test.render_audio import render_midi, spectral_buzz_check\n" + src

    # Replace the post-render existence/print checks with spectral check.
    # Pattern: the "FluidSynth exit" print + assert + wav-size block.
    old_checks = re.compile(
        r"print\(f\"FluidSynth exit: \{r\.returncode\}\"\)\n"
        r"assert r\.returncode == 0, r\.stderr\.decode\(\)\[-500:\]\n"
        r"if os\.path\.exists\(wav\):\n"
        r"    wsize = os\.path\.getsize\(wav\)\n"
        r"    print\(f\"WAV: \{wav\} \(\{wsize\} bytes\)\"\)\n"
        r"    assert wsize > 40, \"empty/corrupt WAV\""
    )
    if old_checks.search(src):
        src = old_checks.sub(
            "wsize = os.path.getsize(wav)\n"
            "print(f\"WAV (solo): {wav} ({wsize} bytes)\")\n"
            "assert wsize > 40, \"empty/corrupt WAV\"\n"
            "ok, rep = spectral_buzz_check(wav)\n"
            "print(f\"Spectral check: {rep}\")\n"
            "assert ok, f\"buzz in solo render: {rep}\"",
            src)

    open(path, "w").write(src)
    print(f"  fixed: {path}")
    return True


if __name__ == "__main__":
    targets = sys.argv[1:]
    if not targets:
        targets = sorted(glob.glob("/opt/data/projects/Instruments/_test/verify_*.py"))
    n = 0
    for t in targets:
        if fix(t):
            n += 1
    print(f"fixed {n} scripts")
