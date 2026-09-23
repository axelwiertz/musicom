"""
Verification test for Method 094 (ACPC).
"""
import os
import numpy as np
from structures import MusicUnit, MusicEvent, UnitMatrix, MidiInstrument
from workflows.unitmatrix_composer import UnitMatrixComposer

def generate_apollonian_quadruples(root=(-1, 2, 2, 3), max_depth=3):
    visited = set()
    visited.add(tuple(sorted(root)))
    queue = [(np.array(root, dtype=int), 0, -1)]
    quads_ordered = []
    
    while queue:
        quad, depth, last_axis = queue.pop(0)
        quads_ordered.append((quad, depth))
        if depth < max_depth:
            sum_k = np.sum(quad)
            for i in range(4):
                if i == last_axis:
                    continue
                new_k = 2 * (sum_k - quad[i]) - quad[i]
                new_quad = np.array(quad)
                new_quad[i] = new_k
                sorted_key = tuple(sorted(new_quad))
                if sorted_key not in visited:
                    visited.add(sorted_key)
                    queue.append((new_quad, depth + 1, i))
    return quads_ordered

def realize_apollonian_composition(root=(-1, 2, 2, 3), max_depth=3, bars=4, bpm=120):
    scale_pitches = [38, 41, 43, 45, 48, 50, 53, 55, 57, 60, 62, 65, 67, 69, 72, 74, 77]
    ticks_per_bar = 1920
    total_ticks = bars * ticks_per_bar
    voice_names = ["Bass", "Tenor", "Alto", "Soprano"]
    programs = [
        MidiInstrument.BASS,
        MidiInstrument.STRING_ENSEMBLE,
        MidiInstrument.VIOLIN,
        MidiInstrument.FLUTE
    ]
    composer = UnitMatrixComposer(bpm=bpm, ticks_per_beat=480, beats_per_bar=4)
    composer.create_matrix(num_voices=4, num_sections=1)
    for v_idx, name in enumerate(voice_names):
        composer.add_voice(name, program=programs[v_idx], channel=v_idx)
    composer.add_section("A", bars=bars)
    
    quads = generate_apollonian_quadruples(root=root, max_depth=max_depth)
    num_quads = len(quads)
    step_ticks = total_ticks // max(1, num_quads)
    voice_events = {v: [] for v in range(4)}
    
    for idx, (quad, depth) in enumerate(quads):
        t_start = idx * step_ticks
        t_end = min(total_ticks, (idx + 1) * step_ticks)
        if t_start >= total_ticks:
            break
        for v_idx in range(4):
            k = int(quad[v_idx])
            if k <= 0:
                pitch = scale_pitches[0]
                vel = 55
                dur = step_ticks
            else:
                pitch = scale_pitches[k % len(scale_pitches)]
                dur_factor = 1.0 / (1.0 + np.log(max(1, k)))
                dur = max(120, int(step_ticks * dur_factor))
                vel = max(40, min(115, 60 + int(15 * np.log2(max(1, k)))) - depth * 6)
            ev_end = min(t_end, t_start + dur)
            voice_events[v_idx].append(MusicEvent(pitch=pitch, volume=vel, start_tick=t_start, end_tick=ev_end))
            
    for v_idx in range(4):
        pad = MusicEvent(pitch=0, volume=0, start_tick=max(0, total_ticks - 1), end_tick=total_ticks)
        composer.fill_voice_section(voice_names[v_idx], "A", MusicUnit(events=voice_events[v_idx] + [pad]))
        
    ok, msg = composer.validate()
    assert ok, f"Zero-drift gate failed: {msg}"
    return composer

if __name__ == "__main__":
    composer = realize_apollonian_composition(bars=4)
    out_dir = "/opt/data/projects/Research/outputs/test_094"
    os.makedirs(out_dir, exist_ok=True)
    out_midi = os.path.join(out_dir, "test_094_acpc.mid")
    composer.to_midi(out_midi)
    size = os.path.getsize(out_midi)
    print(f"Exported MIDI: {out_midi}, size={size} bytes")
    assert size > 40, "MIDI too small!"
    print("VERIFICATION PASS")
