"""GTBRC demo through the musicom engine: 4 voices x 4 sections.

Each section is one *round* of the game (its own payoff table, driven by the
section's chord).  Best-response dynamics resolves each round to a pure Nash
equilibrium; the equilibrium profile is realized as events into UnitMatrix
cells.  Zero-drift is guaranteed by _unit_from_events(events, section_len).
"""
import random

from structures import MusicEvent, MidiInstrument
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.musicom_workflow import _unit_from_events

BPM = 96
TPB = 480
EIGHTH = TPB // 2          # 240 ticks
BARS_PER_SECTION = 2
SECTION_LEN = BARS_PER_SECTION * 4 * TPB   # 3840
SLOTS = 16                 # eighth-note slots per section
BANDS = 4
W1, W2 = 1.0, 1.5
VOICE_NAMES = ["Bass", "Tenor", "Alto", "Soprano"]
PROGRAMS = [MidiInstrument.BASS, MidiInstrument.TRUMPET,
            MidiInstrument.STRING_ENSEMBLE, MidiInstrument.FLUTE]
BASES = [36, 48, 60, 72]
SECTION_CHORDS = [[0, 4, 7, 11], [5, 9, 0, 4], [3, 7, 10, 2], [7, 11, 2, 5]]

RES = [(b, t) for b in range(BANDS) for t in range(SLOTS)]
RIDX = {r: i for i, r in enumerate(RES)}
NRES = len(RES)


def strategies(seed, chord, home):
    rng = random.Random(seed)
    pool = []
    for _ in range(12):
        band = max(0, min(BANDS - 1, home + rng.choice([-1, 0, 0, 1])))
        n = rng.choice([2, 3, 4, 4, 5])
        slots = sorted(rng.sample(range(SLOTS), n))
        pcs = [rng.choice(chord) if rng.random() > 0.15
               else (rng.choice(chord) + rng.choice([1, 2])) % 12 for _ in slots]
        res = frozenset(RIDX[(band, t)] for t in slots)
        nonchord = sum(1 for pc in pcs if pc not in chord)
        priv = 2.0 * abs(band - home) + 1.0 * abs(n - 4) + 2.0 * nonchord
        pool.append((res, tuple(pcs), band, slots, priv))
    return pool


def loads(profile):
    L = [0] * NRES
    for st in profile:
        for r in st[0]:
            L[r] += 1
    return L


def cost(i, profile, strat):
    L = loads([p for j, p in enumerate(profile) if j != i])
    return strat[4] + sum(W1 * (L[r] + 1) + W2 * (L[r] + 1) ** 2 for r in strat[0])


def potential(profile):
    L = loads(profile)
    phi = sum(st[4] for st in profile)
    for k in L:
        for j in range(1, k + 1):
            phi += W1 * j + W2 * j * j
    return phi


def best_response(S, rng):
    prof = [rng.choice(S[i]) for i in range(len(S))]
    phis = [potential(prof)]
    for sweep in range(1, 500):
        moved = False
        order = list(range(len(S)))
        rng.shuffle(order)
        for i in order:
            cur, bc = prof[i], cost(i, prof, prof[i])
            best = cur
            for s in S[i]:
                if s is cur:
                    continue
                c = cost(i, prof, s)
                if c < bc - 1e-12:
                    best, bc = s, c
            if best is not cur:
                prof[i] = best
                moved = True
                phis.append(potential(prof))
        if not moved:
            return prof, phis, sweep
    return prof, phis, 500


rng = random.Random(2026)
composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=4)
composer.create_matrix(num_voices=4, num_sections=4)
for name, prog in zip(VOICE_NAMES, PROGRAMS):
    composer.add_voice(name, program=prog, channel=PROGRAMS.index(prog) % 4)
for si in range(4):
    composer.add_section(chr(ord("A") + si), bars=BARS_PER_SECTION)

total_notes = 0
section_phi = []
section_ne_phi = []
for si in range(4):
    chord = SECTION_CHORDS[si]
    S = [strategies(1000 + si * 17 + v, chord, v) for v in range(4)]
    prof, phis, sweeps = best_response(S, rng)
    section_phi.append(phis)
    section_ne_phi.append(phis[-1])
    for v, name in enumerate(VOICE_NAMES):
        res, pcs, band, slots, _ = prof[v]
        events = []
        for k, t in enumerate(slots):
            start = t * EIGHTH
            nxt = slots[k + 1] * EIGHTH if k + 1 < len(slots) else SECTION_LEN
            dur = min(nxt - start, 4 * EIGHTH)
            pitch = BASES[band] + pcs[k]
            events.append(MusicEvent(pitch=pitch, volume=88 if v == 3 else 80,
                                     start_tick=start, end_tick=start + dur))
            total_notes += 1
        composer.fill_voice_section(
            name, chr(ord("A") + si), _unit_from_events(events, SECTION_LEN))
    print(f"section {chr(ord('A') + si)}: sweeps={sweeps} "
          f"Phi start={phis[0]:.1f} -> NE={phis[-1]:.1f} "
          f"descent steps={len(phis) - 1}")

ok, msg = composer.validate()
print("validate:", ok, msg)
assert ok, msg
out = "gtbrc_demo.mid"
composer.to_midi(out)
import os
size = os.path.getsize(out)
print(f"midi={out} bytes={size} notes={total_notes} "
      f"duration={SECTION_LEN * 4 / TPB / (BPM / 60):.1f}s")
assert size > 40, "empty/corrupt"
print("section NE potential:", [round(p, 1) for p in section_ne_phi])
print("tension curve (Phi per section, start->NE):")
for si, ph in enumerate(section_phi):
    print(" ", chr(ord("A") + si), [round(x, 1) for x in ph])
