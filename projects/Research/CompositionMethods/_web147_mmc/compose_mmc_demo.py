"""MMTC engine demo: metric-modulation chain realized through the musicom UnitMatrix.

Four tempo stations (pulse = 480, 320, 360, 480 ticks = ratios 1, 3/2, 4/3, 1).
Because the engine's tick grid is fixed, the modulation is realized in *tuplet
notation mode*: each station keeps the base tempo and the pulse length changes by
the rational ratio. Section length 2880 ticks is the qlcm of the three pulse
lengths, so every voice lands on the section seam -> zero drift by construction.
"""
import os
from fractions import Fraction
from math import gcd, lcm

from structures import MusicUnit, MusicEvent, MidiInstrument
from workflows.unitmatrix_composer import UnitMatrixComposer

ROOT = os.environ.get("MUSICOM_ROOT", "/opt/data/repos/musicom")
OUT = os.path.join(ROOT, "projects/Research/outputs/mmc_147")
os.makedirs(OUT, exist_ok=True)

BPM, TPB, BPB = 120, 480, 6          # 6-beat bars -> bar = 2880 ticks
SECTION_TICKS = BPB * TPB            # 2880

# station: (name, pulse_ticks, ratio, chord, root)
STATIONS = [
    ("A", 480, Fraction(1, 1), [60, 64, 67], 36),    # C  major
    ("B", 320, Fraction(3, 2), [57, 60, 64], 33),    # A  minor
    ("C", 360, Fraction(4, 3), [53, 57, 60], 29),    # F  major
    ("D", 960, Fraction(1, 2), [60, 64, 67], 36),    # C  major (tempo cycle closes)
]


def qlcm(frs):
    return Fraction(lcm(*[f.numerator for f in frs]), gcd(*[f.denominator for f in frs]))


def pad(events, length):
    """Zero-drift padding: the row must end exactly at the section seam (pitch 0 is
    skipped by the MIDI writer)."""
    end = max(e.end_tick for e in events)
    if end < length:
        events.append(MusicEvent(pitch=0, volume=0, start_tick=end, end_tick=length))
    return MusicUnit(events=events)


composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
composer.create_matrix(num_voices=3, num_sections=len(STATIONS))
composer.add_voice("Pulse", program=MidiInstrument.PIANO, channel=0)
composer.add_voice("Chord", program=MidiInstrument.STRING_ENSEMBLE, channel=1)
composer.add_voice("Bass", program=MidiInstrument.BASS, channel=2)
for name, *_ in STATIONS:
    composer.add_section(name, bars=1)

for i, (name, pulse, ratio, chord, root) in enumerate(STATIONS):
    assert SECTION_TICKS % pulse == 0, f"{pulse} does not tile {SECTION_TICKS}"
    n = SECTION_TICKS // pulse

    # voice 1: the station's pulse itself (chord tones cycled) -- 6/9/8/6 events
    ev = [MusicEvent(pitch=chord[k % 3] + 12, volume=88, start_tick=k * pulse,
                     end_tick=(k + 1) * pulse) for k in range(n)]
    composer.fill_voice_section("Pulse", name, pad(ev, SECTION_TICKS))

    # voice 2: one sustained harmony per station (harmonic rhythm = the station)
    ev = [MusicEvent(pitch=p, volume=70, start_tick=0, end_tick=SECTION_TICKS) for p in chord]
    composer.fill_voice_section("Chord", name, pad(ev, SECTION_TICKS))

    # voice 3: bass on every second pulse (2:1 against the station pulse)
    ev = [MusicEvent(pitch=root + (12 if (k % 4) == 3 else 0), volume=96,
                     start_tick=k * 2 * pulse, end_tick=(k * 2 + 2) * pulse)
          for k in range(n // 2)]
    composer.fill_voice_section("Bass", name, pad(ev, SECTION_TICKS))

ok, msg = composer.validate()
print("validate:", ok, msg)
assert ok, msg

mid = os.path.join(OUT, "mmc_147_modulation_chain.mid")
composer.to_midi(mid)
size = os.path.getsize(mid)
print("MIDI:", mid, size, "bytes")
assert size > 40

# --- the same chain as a real tempo map (mode A): seconds per station ----------
t = Fraction(BPM)
print("\nstation  pulse  ratio   tempo  seconds  ticks  pulses")
for name, pulse, ratio, chord, root in STATIONS:
    t *= ratio
    secs = float(Fraction(SECTION_TICKS, TPB) * 60 / t)
    print(f"{name:^7}  {pulse:5d}  {str(ratio):5}  {float(t):6.1f}  {secs:6.2f}  "
          f"{SECTION_TICKS:5d}  {SECTION_TICKS // pulse:6d}")

print("\nsection length =", SECTION_TICKS, "ticks =",
      float(qlcm([Fraction(480), Fraction(320), Fraction(360)])), "= qlcm(pulses)")
print("total ticks:", composer.get_track_length_ticks())
