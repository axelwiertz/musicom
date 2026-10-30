"""ABGC demo — Artin braid group composition, method 129.

4 strands = 4 voices. Vertical position -> pitch on a fixed scale ladder
(voice-exchange Stimmtausch); strand identity -> UnitMatrix row.
Sections = Garside-influenced braid words (plain walk, Delta half-twist, ...).
Engine-only MIDI authoring (musicom UnitMatrixComposer).
"""
import os
import random
import sys

from structures import MusicEvent, MidiInstrument
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.musicom_workflow import _unit_from_events

OUT = "/opt/data/projects/Research/outputs/abgc_129"
os.makedirs(OUT, exist_ok=True)

N = 4                       # strands / voices
TPB, BPB = 480, 4
SYL = TPB                   # one braid syllable = one beat
BARS_PER_SEC = 4
SEC_LEN = BARS_PER_SEC * BPB * TPB   # 7680 ticks
SYLS_PER_SEC = SEC_LEN // SYL        # 16

# vertical position -> pitch (C maj ladder, wide spacing so crossings are audible)
LADDER = [55, 60, 64, 67]   # G3 C4 E4 G4
# per-strand tessitura offset, in semitones on the ladder's pc content
DELTA = [0, 0, 0, 0]


def delta_word(n):
    """Half-twist Delta_n = (s1..s_{n-1})(s1..s_{n-2})...(s1), length n(n-1)/2."""
    return [(i, +1) for k in range(n - 1, 0, -1) for i in range(1, k + 1)]


def walk(n, length, seed, positive_bias=0.0):
    """Adjacent-transposition walk = braid word."""
    rng = random.Random(seed)
    w = []
    for _ in range(length):
        i = rng.randrange(1, n)
        e = +1 if rng.random() < 0.5 + positive_bias / 2 else -1
        w.append((i, e))
    return w


def section_words(n):
    return {
        "A": walk(n, SYLS_PER_SEC, 101, positive_bias=0.6),          # rising writhe
        "B": walk(n, SYLS_PER_SEC, 202, positive_bias=0.0),          # balanced
        "C": delta_word(n) + walk(n, SYLS_PER_SEC - len(delta_word(n)), 303),
        "D": walk(n, SYLS_PER_SEC, 404, positive_bias=-0.6),         # falling writhe
    }


def strand_events(word, n, t0):
    """Emit one note per strand per syllable; pitch follows the *position*, not the strand."""
    perm = list(range(n))          # perm[k] = strand sitting at vertical position k
    events = [[] for _ in range(n)]
    for t, (i, e) in enumerate(word):
        start = t0 + t * SYL
        # accent: the two crossed strands, positive (over-crossing) louder
        cross = {perm[i - 1], perm[i]}
        perm[i - 1], perm[i] = perm[i], perm[i - 1]
        for pos, strand in enumerate(perm):
            # after the swap, both crossed strands occupy new positions
            vel = 96 if (strand in cross and e > 0) else (82 if strand in cross else 70)
            pitch = LADDER[pos] + DELTA[strand]
            events[strand].append(
                MusicEvent(pitch=pitch, volume=vel, start_tick=start,
                           end_tick=start + SYL))
    return events


def main():
    composer = UnitMatrixComposer(bpm=96, ticks_per_beat=TPB, beats_per_bar=BPB)
    words = section_words(N)
    names = list(words)
    composer.create_matrix(num_voices=N, num_sections=len(names))
    for v in range(N):
        composer.add_voice(f"Strand{v}", program=MidiInstrument.STRING_ENSEMBLE, channel=v)
    for s in names:
        composer.add_section(s, bars=BARS_PER_SEC)

    for si, sname in enumerate(names):
        evs = strand_events(words[sname], N, si * SEC_LEN)
        for v in range(N):
            composer.fill_voice_section(f"Strand{v}", sname,
                                        _unit_from_events(evs[v], SEC_LEN))

    ok, msg = composer.validate()
    print("validate:", ok, msg)
    assert ok, msg
    path = os.path.join(OUT, "abgc_129.mid")
    composer.to_midi(path)
    size = os.path.getsize(path)
    print("midi:", path, size, "bytes")
    assert size > 40

    # report braid invariants for provenance
    for sname, w in words.items():
        perm = list(range(N))
        for i, _ in w:
            perm[i - 1], perm[i] = perm[i], perm[i - 1]
        seen, comps = [False] * N, 0
        for s in range(N):
            if not seen[s]:
                comps += 1
                x = s
                while not seen[x]:
                    seen[x] = True
                    x = perm[x]
        print(f"section {sname}: |w|={len(w)} writhe={sum(e for _, e in w)} "
              f"closure-components={comps}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
