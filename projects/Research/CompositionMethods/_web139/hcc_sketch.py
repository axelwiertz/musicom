#!/usr/bin/env python3
"""Method 138 — Huffman Coding Composition (HCC): engine prototype sketch.

Builds a Huffman tree per (voice, section) over a weighted motif vocabulary,
decodes the Kraft-tight in-order leaf schedule into per-cell MusicEvents
(pitch = anchor + codeword step-sum folded to a scale; duration = 2^(L-len)
slots; onset = leaf subtree start), fills a UnitMatrixComposer through the
sanctioned engine spine (fill_voice_section -> validate -> to_midi), and
verifies the zero-drift gate.

Run with the musicom python (ONE-ENV contract):
    $MUSICOM_PYTHON _web139/hcc_sketch.py
"""
import heapq, math, os
from structures import MusicUnit, MusicEvent, MidiInstrument
from workflows.unitmatrix_composer import UnitMatrixComposer

BAR = 1920          # ticks per bar (480 tpb x 4 beats)
L_MAX = 6           # metric-depth cap (per-section L = max codeword length)

SCALE = [0, 2, 4, 5, 7, 9, 11]      # C-major degrees (semitone offsets)
ANCHOR_DEG = {                      # per-voice anchor scale degree + octave base
    'Lead': (0, 72),                # C5
    'Viola': (2, 64),               # E4
    'Bass': (0, 48),                # C3
}

# ---------------------------------------------------------------- Huffman
class _Node:
    __slots__ = ('w', 'sym', 'left', 'right')
    def __init__(self, w, sym=None, left=None, right=None):
        self.w, self.sym, self.left, self.right = w, sym, left, right
    def __lt__(self, o):            # min-variance tie-break: leaves first
        a = (self.w, 0 if self.sym is None else 1, self.sym if self.sym is not None else '')
        b = (o.w, 0 if o.sym is None else 1, o.sym if o.sym is not None else '')
        return a < b

def huffman(weights):
    """weights: list[(sym, w)]. Returns (codes dict, root)."""
    heap = [_Node(w, s) for s, w in weights]
    heapq.heapify(heap)
    while len(heap) > 1:
        a, b = heapq.heappop(heap), heapq.heappop(heap)
        heapq.heappush(heap, _Node(a.w + b.w, None, a, b))
    codes = {}
    def walk(n, pre):
        if n.sym is not None:
            codes[n.sym] = pre
            return
        walk(n.left, pre + '0')
        walk(n.right, pre + '1')
    walk(heap[0], '')
    return codes, heap[0]

def in_order_schedule(root, L):
    """List of (sym, start_slot, span_slots). Each internal node halves its
    span (metric subdivision); leaves tile [0, 2^L) exactly, in-order."""
    out = []
    def rec(n, start, span):
        if n.sym is not None:
            out.append((n.sym, start, span))
            return
        half = span // 2
        rec(n.left, start, half)
        rec(n.right, start + half, half)
    rec(root, 0, 2 ** L)
    return out

# ---------------------------------------------------------------- musical plan
MOTIFS = [f'M{i}' for i in range(8)]
# per-section weight vectors = tonal gravity / entropy arc
SECTIONS = {
    'A':  [0.40, 0.20, 0.15, 0.10, 0.07, 0.05, 0.02, 0.01],   # peaked  -> HOME
    'B':  [0.18, 0.16, 0.15, 0.13, 0.12, 0.10, 0.09, 0.07],   # flat    -> TENSE
    "A'": [0.34, 0.22, 0.16, 0.10, 0.08, 0.06, 0.03, 0.01],   # re-peaked (development)
    'C':  [0.30, 0.18, 0.14, 0.10, 0.10, 0.08, 0.06, 0.04],   # moderate + cadence peak
}
VOICES = ['Lead', 'Viola', 'Bass']

def entropy(ws):
    tot = sum(ws)
    return -sum((w / tot) * math.log2(w / tot) for w in ws if w > 0)

def pitch_for(code, anchor_deg, base):
    """codeword bits = steps (0 down, 1 up); fold degree mod 7 into the scale."""
    steps = sum(1 if b == '1' else -1 for b in code)
    deg = (anchor_deg + steps) % 7
    octave = (anchor_deg + steps) // 7
    return base + octave * 12 + SCALE[deg]

def fill_cell(composer, voice, section, weights, L, slot):
    codes, root = huffman(list(zip(MOTIFS, weights)))
    anchor_deg, base = ANCHOR_DEG[voice]
    events = []
    for sym, start_slot, span in in_order_schedule(root, L):
        code = codes[sym]
        rank = MOTIFS.index(sym) + 1
        velocity = max(40, 104 - 8 * rank)
        events.append(MusicEvent(
            pitch=pitch_for(code, anchor_deg, base),
            volume=velocity,
            start_tick=start_slot * slot,
            end_tick=(start_slot + span) * slot,
        ))
    # events tile [0, 2^L) exactly -> cell = full section length -> zero drift
    composer.fill_voice_section(voice, section, MusicUnit(events=events))

# ---------------------------------------------------------------- engine spine
out_dir = '/opt/data/repos/musicom/projects/Research/outputs/method138_hcc'
os.makedirs(out_dir, exist_ok=True)
midi_path = os.path.join(out_dir, 'hcc_sketch.mid')

composer = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
composer.create_matrix(num_voices=len(VOICES), num_sections=len(SECTIONS))
composer.add_voice('Lead',  program=MidiInstrument.FLUTE,          channel=0)
composer.add_voice('Viola', program=MidiInstrument.STRING_ENSEMBLE, channel=1)
composer.add_voice('Bass',  program=MidiInstrument.BASS,            channel=2)
for name in SECTIONS:
    composer.add_section(name, bars=1)

print('=== Huffman Coding Composition — sketch ===\n')
for name, ws in SECTIONS.items():
    codes, root = huffman(list(zip(MOTIFS, ws)))
    L = max(len(codes[m]) for m in MOTIFS)          # metric depth = longest code
    slot = BAR // 2 ** L
    H = entropy(ws)
    Lw = sum(w * len(codes[m]) for m, w in zip(MOTIFS, ws))
    kraft = sum(2 ** (-len(codes[m])) for m in MOTIFS)
    sched = in_order_schedule(root, L)
    print(f'--- section {name}: L={L} (slots={2**L}, slot={slot} ticks), H={H:.3f} bits, L={Lw:.3f}, Kraft={kraft:.6f} ---')
    print('   motif code  onset dur  pitch-offset')
    for sym, start, span in sched:
        steps = sum(1 if b == '1' else -1 for b in codes[sym])
        print(f'   {sym:5s} {codes[sym]:>6s} {start*slot:5d} {span*slot:4d}  {steps:+d}')
    for v in VOICES:
        fill_cell(composer, v, name, ws, L, slot)
    print()

ok, msg = composer.validate()
print(f'validate() -> {ok}: {msg}')
assert ok, 'zero-drift gate FAILED'
composer.to_midi(midi_path)
size = os.path.getsize(midi_path)
print(f'midi: {midi_path} ({size} bytes)')
assert size > 40, 'empty/corrupt output'
print('SKETCH OK')
