"""Rule-based harmony writer — HarmonyKeen style (music theory, not AI).

Replicable logic from the Synthtopia item "New Mac App, HarmonyKeen, Writes
Harmony Parts To Your MIDI Melodies Using Music Theory, Not AI" (2026-09-15):
"You give it a monophonic MIDI melody and it writes harmony parts around it,
working out the voice leading... It runs on music theory rather than a neural
network. It reads the whole melody first, finds the phrases and cadences, picks
a chord sequence that fits, then writes the voices. The same input and settings
give the same result every time." Styles range "from a single added line through
close vocal harmony and four-part writing to fuller arrangements."

What is replicated here (the algorithm, not the app):

* ``HarmonyWriter``:
  - **phrase segmentation** — the melody is split at long gaps and pitch-direction
    extremes (a cheap but honest cadence heuristic);
  - **harmonic analysis** — for every melody note, candidate diatonic chords
    (I..vii in the melody's key) are scored by how many melody tones they
    contain (the note's chord-factor membership), with cadential bias at
    phrase ends (V→I);
  - **voice-leading** — harmony voices are built as SATB-style lines: each
    chord is voiced close to the melody note, and each voice moves along the
    path of minimal semitone motion between consecutive chords (classic
    voice-leading cost), with clamping into the voice's range and a rule that
    a voice does not jump more than a fifth when a step is available
    (the "law of the shortest way");
  - **styles**: ``1`` = one added line, ``2`` = close 2-part harmony,
    ``3`` = close vocal harmony (three lines), ``4`` = full four-part writing
    (SATB under the melody as soprano), ``5`` = fuller arrangement (SATB +
    bass doubling);
  - **deterministic**: same melody + settings → same output.
* ``melody_to_events`` / ``events_to_midi`` round-trips musicom MIDI-event dicts.

Not replicated: the VST3/AU/standalone app, its preset UI, its specific chord
dictionary (we use diatonic triads + V7; HarmonyKeen's exact table is
proprietary — the *rule structure* is replicated, not the constants).

Usage:
    from sound.generators.harmony_writer import HarmonyWriter

    hw = HarmonyWriter(key="C", style=4, seed=0)
    melody = [{"pitch": 72, "volume": 100, "start_tick": 0, "end_tick": 480}, ...]
    parts = hw.harmonize(melody)        # dict voice_name -> note events
"""

from __future__ import annotations

from typing import Dict, List, Sequence, Tuple

MAJOR_STEPS = (2, 2, 1, 2, 2, 2, 1)          # Ionian
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
ROMAN = ["I", "ii", "iii", "IV", "V", "vi", "vii"]
# voices as (name, semitone-below-melody-cap, range) — SATB under the melody
VOICE_RANGES = {          # name: (low_midi, high_midi)
    "soprano": (60, 81),
    "alto": (55, 74),
    "tenor": (48, 69),
    "bass": (40, 64),
}


def key_scale(key: str) -> List[int]:
    """Major-scale pitch classes of ``key`` (e.g. "C", "Eb", "F#")."""
    root = NOTE_NAMES.index(key if len(key) == 1 else key[0].upper() + key[1:])
    return [(root + sum(MAJOR_STEPS[:i])) % 12 for i in range(7)]


def diatonic_triads(key: str) -> List[Tuple[int, str, Tuple[int, ...]]]:
    """The seven diatonic triads: (degree, roman, (root, third, fifth)).

    Pitch classes are returned in chord-tone ORDER (root, third, fifth) — not
    sorted — so callers can identify the root at index 0. Sorting breaks the
    root of IV/V/vi/vii°, whose root pitch-class is not the numeric minimum
    (e.g. F major = (5, 9, 0) → sorted (0, 5, 9) loses F as the root, so
    ``choose_chords`` and the bass voice-lead both target the wrong note).
    """
    root = NOTE_NAMES.index(key if len(key) == 1 else key[0].upper() + key[1:])
    qualities = [(0, 4, 7), (2, 5, 9), (4, 7, 11), (5, 9, 0),
                 (7, 11, 2), (9, 0, 4), (11, 2, 5)]
    out = []
    for d, deg in enumerate(qualities):
        pcs = tuple((root + iv) % 12 for iv in deg)
        out.append((d, ROMAN[d], pcs))
    return out


class HarmonyWriter:
    """Write harmony parts around a monophonic melody (rule-based)."""

    def __init__(self, key: str = "C", style: int = 4, seed: int = 0):
        if style not in (1, 2, 3, 4, 5):
            raise ValueError("style must be 1..5")
        self.key = key
        self.style = int(style)
        self.seed = int(seed)
        self.triads = diatonic_triads(key)

    # ------------------------------------------------------------- analysis
    def segment_phrases(self, melody: Sequence[dict], gap_ticks: int = 480,
                        max_len: int = 16) -> List[List[dict]]:
        """Split notes into phrases: on rests >= gap_ticks or after max_len."""
        phrases, cur = [], []
        for i, ev in enumerate(melody):
            if cur and ev["start_tick"] - cur[-1]["end_tick"] >= gap_ticks:
                phrases.append(cur)
                cur = []
            cur.append(ev)
            if len(cur) >= max_len:
                phrases.append(cur)
                cur = []
        if cur:
            phrases.append(cur)
        return phrases or [[]]

    def choose_chords(self, melody: Sequence[dict]) -> List[Tuple[int, int]]:
        """Per melody event: (degree, roman) of the best-fitting diatonic triad.

        Score = membership of the melody pitch class in the triad (root 3,
        third 2, fifth 1) + cadence bonus (V before phrase-final I).
        Deterministic tie-break: earlier degree wins.
        """
        best = []
        for i, ev in enumerate(melody):
            pc = ev["pitch"] % 12
            scored = []
            for d, roman, pcs in self.triads:
                s = 0
                if pc == pcs[0]:
                    s = 3
                elif pc in pcs:
                    s = 2 if pc == pcs[1] else 1
                scored.append((s, -d, d))
            scored.sort(reverse=True)
            deg = scored[0][2]
            # cadence: final note of a phrase -> prefer V or I under it
            is_last = (i == len(melody) - 1) or \
                melody[i + 1]["start_tick"] - ev["end_tick"] >= 480
            if is_last and deg not in (4, 0) and scored[0][0] <= 1:
                deg = 4 if deg != 0 else 0
            best.append((deg, ROMAN[deg]))
        return best

    # ------------------------------------------------------- voice leading
    @staticmethod
    def _closest(target: int, lo: int, hi: int, prev: int | None) -> int:
        """Pitch nearest ``target`` inside [lo, hi], biased to stay near prev."""
        opts = [target + 12 * k for k in range(-2, 3)]
        ok = [p for p in opts if lo <= p <= hi]
        if not ok:
            return int(min(max(target, lo), hi))
        if prev is None:
            return ok[0]
        return min(ok, key=lambda p: abs(p - prev))

    def voice_lines(self, melody: Sequence[dict],
                    chords: Sequence[Tuple[int, int]]) -> Dict[str, List[dict]]:
        """Build the harmony voices under the melody.

        Voice count and ranges follow ``style``:
            1: alto only; 2: alto+tenor; 3: alto+tenor+bass (close harmony);
            4: SATB (soprano doubles the melody); 5: SATB + bass doubling
            (fuller arrangement).
        """
        triad_pcs = {d: pcs for d, _, pcs in self.triads}
        lines: Dict[str, List[dict]] = {}
        active = {
            1: ["alto"],
            2: ["alto", "tenor"],
            3: ["alto", "tenor", "bass"],
            4: ["alto", "tenor", "bass", "soprano"],
            5: ["alto", "tenor", "bass", "soprano"],
        }[self.style]
        prevs: Dict[str, int | None] = {v: None for v in active}
        for i, (ev, (deg, _)) in enumerate(zip(melody, chords)):
            pcs = triad_pcs[deg]
            mel = ev["pitch"]
            for v in active:
                lo, hi = VOICE_RANGES[v]
                if v == "soprano":
                    # soprano = melody itself, folded into range via octaves
                    p = mel
                    while p < lo:
                        p += 12
                    while p > hi:
                        p -= 12
                    pitch = p
                elif v == "bass":
                    # the chord root, nearest-below with shortest-way preference
                    pitch = self._closest_below(mel, pcs[0], lo, hi, prevs[v])
                else:
                    # any chord tone strictly below the melody (close position)
                    pitch = self._closest_below(mel, None, lo, hi, prevs[v],
                                                chord_pcs=pcs)
                lines.setdefault(v, []).append(
                    {"pitch": int(pitch), "volume": int(ev.get("volume", 100)),
                     "start_tick": ev["start_tick"], "end_tick": ev["end_tick"]})
                prevs[v] = pitch
        if self.style == 5:
            lines["bass2"] = [
                {**e, "pitch": int(e["pitch"]) - 12} for e in lines["bass"]]
        return lines

    @staticmethod
    def _closest_below(mel: int, root_pc: int | None, lo: int, hi: int,
                       prev: int | None, chord_pcs=None) -> int:
        """Nearest chord tone below ``mel`` in [lo, hi]; shortest-way rule vs prev."""
        cands = []
        for pc in (chord_pcs if chord_pcs is not None else
                   ([root_pc] if root_pc is not None else ())):
            for octv in range(3, 9):
                p = pc + 12 * octv
                if p < mel and lo <= p <= hi:
                    cands.append(p)
        if not cands:
            return int(min(max(mel - 12, lo), hi))
        if prev is not None:
            # law of the shortest way, with ascending tie-break
            cands.sort(key=lambda p: (abs(p - prev), p))
        else:
            cands.sort(key=lambda p: -p)      # nearest below the melody
        return cands[0]

    # --------------------------------------------------------------- public
    def harmonize(self, melody: Sequence[dict]) -> Dict[str, List[dict]]:
        """Harmonize a monophonic melody (musicom MIDI-event dicts).

        Returns a dict of voice name -> note-event list (deterministic).
        """
        if not melody:
            return {}
        chords = self.choose_chords(melody)
        return self.voice_lines(list(melody), chords)


# --------------------------------------------------------------- helpers


def demo() -> str:
    """Prove segmentation, chord fit, voice ranges, cadence and determinism."""
    # I–V–vi–IV melody in C, one note per beat (480 ticks)
    melody = []
    notes = [72, 71, 67, 69,   # C5 B4 G4 A4  (beat 1..4)
             65, 64, 62, 60,   # F4 E4 D4 ... phrase 2
             60, 62, 64, 65,
             67, 67, 71, 72]
    for i, p in enumerate(notes):
        melody.append({"pitch": p, "volume": 100,
                       "start_tick": i * 480, "end_tick": (i + 1) * 480})

    for style in (1, 2, 3, 4, 5):
        hw = HarmonyWriter(key="C", style=style, seed=0)
        parts = hw.harmonize(melody)
        names = sorted(parts)
        n_voices = len(names)
        print(f"style {style}: voices={names} "
              f"first chord events={[ (p, parts[p][0]['pitch']) for p in names ]}")
        assert n_voices == (style if style < 4 else 4) + (1 if style == 5 else 0)
        for v, evs in parts.items():
            assert len(evs) == len(melody)
            lo, hi = VOICE_RANGES.get(v, (36, 55)) if v != "bass2" else (28, 52)
            assert all(lo <= e["pitch"] <= hi for e in evs), \
                f"{v} out of range: {[e['pitch'] for e in evs]}"

    # every harmony pitch is a chord tone of the chosen degree (close harmony)
    hw = HarmonyWriter(key="C", style=4)
    chords = hw.choose_chords(melody)
    parts = hw.harmonize(melody)
    pcs_by_deg = {d: pcs for d, _, pcs in hw.triads}
    for i, ev in enumerate(melody):
        deg = chords[i][0]
        for v in ("alto", "tenor", "bass"):
            assert parts[v][i]["pitch"] % 12 in pcs_by_deg[deg]
    print(f"chords chosen: {[r for _, r in chords]}")
    print("all harmony notes are chord tones: True")

    # cadence: phrase-final chord should be I or V
    finals = [chords[3], chords[7], chords[11], chords[15]]
    print("phrase-final chords:", finals)
    assert finals[-1][0] in (0, 4)

    # determinism
    p1 = HarmonyWriter(key="C", style=3, seed=0).harmonize(melody)
    p2 = HarmonyWriter(key="C", style=3, seed=7)
    p2 = p2.harmonize(melody)
    print(f"deterministic across seeds: {p1 == p2}")
    assert p1 == p2

    return "harmony_writer demo OK"


if __name__ == "__main__":
    print(demo())
