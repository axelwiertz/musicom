"""Validation script for Method 093 PPNC."""
import numpy as np
from structures import MusicUnit, MusicEvent, UnitMatrix, MidiInstrument
from workflows.unitmatrix_composer import UnitMatrixComposer

def simulate_percolation_grid(num_voices, num_steps, p_occ=0.5927, seed=42):
    rng = np.random.default_rng(seed)
    return rng.random((num_voices, num_steps)) < p_occ

def label_clusters_4conn(grid):
    rows, cols = grid.shape
    labels = np.zeros((rows, cols), dtype=int)
    cluster_sizes = {}
    current_label = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r, c] and labels[r, c] == 0:
                current_label += 1
                queue = [(r, c)]
                labels[r, c] = current_label
                size = 0
                while queue:
                    curr_r, curr_c = queue.pop(0)
                    size += 1
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = curr_r + dr, curr_c + dc
                        if 0 <= nr < rows and 0 <= nc < cols:
                            if grid[nr, nc] and labels[nr, nc] == 0:
                                labels[nr, nc] = current_label
                                queue.append((nr, nc))
                cluster_sizes[current_label] = size
    return labels, cluster_sizes

def check_horizontal_spanning(labels):
    cols = labels.shape[1]
    left_labels = set(labels[:, 0]) - {0}
    right_labels = set(labels[:, cols - 1]) - {0}
    return list(left_labels.intersection(right_labels))

def compose_percolation_section(p_occ=0.5927, bars=4, num_voices=4, bpm=120, seed=42):
    base_pitches = [72, 60, 48, 36]
    scale_steps = [0, 2, 4, 5, 7, 9, 11, 12, 14, 16]
    ticks_per_step = 120
    steps_per_bar = 16
    total_steps = bars * steps_per_bar
    total_ticks = bars * 1920
    
    grid = simulate_percolation_grid(num_voices, total_steps, p_occ=p_occ, seed=seed)
    labels, cluster_sizes = label_clusters_4conn(grid)
    spanning = check_horizontal_spanning(labels)
    
    composer = UnitMatrixComposer(bpm=bpm, ticks_per_beat=480, beats_per_bar=4)
    composer.create_matrix(num_voices=num_voices, num_sections=1)
    
    voice_names = ["Soprano", "Alto", "Tenor", "Bass"]
    instruments = [
        MidiInstrument.FLUTE,
        MidiInstrument.VIOLIN,
        MidiInstrument.STRING_ENSEMBLE,
        MidiInstrument.BASS
    ]
    for v in range(num_voices):
        composer.add_voice(voice_names[v], program=instruments[v], channel=v)
    composer.add_section("A", bars=bars)
    
    for v in range(num_voices):
        events = []
        step = 0
        while step < total_steps:
            if grid[v, step]:
                cid = labels[v, step]
                run_len = 1
                while (step + run_len < total_steps and 
                       grid[v, step + run_len] and 
                       labels[v, step + run_len] == cid):
                    run_len += 1
                start_tick = step * ticks_per_step
                end_tick = min((step + run_len) * ticks_per_step, total_ticks)
                scale_deg = (cid * 2 + (1 if cid in spanning else 0)) % len(scale_steps)
                pitch = base_pitches[v] + scale_steps[scale_deg]
                base_vel = 75 if cid not in spanning else 95
                vel = int(np.clip(base_vel + min(30, cluster_sizes.get(cid, 1) * 2), 40, 127))
                events.append(MusicEvent(pitch=pitch, volume=vel, start_tick=start_tick, end_tick=end_tick))
                step += run_len
            else:
                step += 1
        pad = MusicEvent(pitch=0, volume=0, start_tick=max(0, total_ticks - 1), end_tick=total_ticks)
        composer.fill_voice_section(voice_names[v], "A", MusicUnit(events=events + [pad]))
        
    ok, msg = composer.validate()
    assert ok, f"Zero-drift gate failed: {msg}"
    print(f"Validation successful! Zero-drift: {ok}. Clusters: {len(cluster_sizes)}. Spanning: {spanning}")
    return composer

if __name__ == "__main__":
    compose_percolation_section()
