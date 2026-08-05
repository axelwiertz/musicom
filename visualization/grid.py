"""High-contrast UnitMatrix grid visualizer (Missing-Link Area 2).

Renders a terminal ASCII timeline (█ sounding / ░ rest) per voice/section with
per-voice density %, and can persist the render to an Analysis file.

Pure stdlib + numpy; no sys.path hacks (package is installed editable).
"""
from typing import List, Optional
from structures.matrix import UnitMatrix
from structures.unit import MusicUnit, MusicEvent


def _column_durations(matrix: UnitMatrix) -> list:
    """Max end_tick per section column (fallback 1 bar = 1920 ticks)."""
    cols = []
    for c in range(matrix.num_cols):
        max_tick = 0
        for r in range(matrix.num_rows):
            unit = matrix.get_unit((r, c))
            if unit is not None and len(unit.data) > 0:
                for e in unit.events:
                    if e.end_tick > max_tick:
                        max_tick = e.end_tick
        cols.append(max_tick if max_tick > 0 else 480 * 4)
    return cols


def render_grid(matrix: UnitMatrix,
                ticks_per_character: int = 120,
                voice_names: Optional[List[str]] = None,
                bpm: Optional[int] = None,
                mode: Optional[str] = None) -> str:
    """Return the high-contrast grid as a string (does not print).

    - █ = sounding event, ░ = rest/silence, | = section boundary
    - Per-voice density % = sounding chars / total chars.
    """
    lines = []
    header = "=" * 70
    lines.append(header)
    title = "MUSICOM UNITMATRIX VISUALIZER (HIGH-CONTRAST TIMELINE)"
    if bpm is not None or mode is not None:
        tags = []
        if bpm is not None:
            tags.append(f"BPM: {bpm}")
        if mode is not None:
            tags.append(f"Mode: {mode}")
        title += "  [" + " | ".join(tags) + "]"
    lines.append(title)
    lines.append(f"Matrix shape: {matrix.num_rows} voices x {matrix.num_cols} sections")
    lines.append(header)

    col_durations = _column_durations(matrix)
    lines.append(f"Section durations (ticks): {col_durations}")
    lines.append("-" * 70)

    for r in range(matrix.num_rows):
        name = voice_names[r] if voice_names and r < len(voice_names) else f"Voice {r:02d}"
        row_cells = []
        sounding = 0
        total = 0
        for c in range(matrix.num_cols):
            unit = matrix.get_unit((r, c))
            cell_dur = col_durations[c]
            num_chars = max(1, int(cell_dur / ticks_per_character))
            grid_chars = ["░"] * num_chars
            if unit is not None and len(unit.data) > 0:
                for e in unit.events:
                    if e.pitch == 0:      # silent padding/rest
                        continue
                    start_char = int(e.start_tick / ticks_per_character)
                    end_char = int(e.end_tick / ticks_per_character)
                    start_char = max(0, min(start_char, num_chars - 1))
                    end_char = max(start_char + 1, min(end_char, num_chars))
                    for idx in range(start_char, end_char):
                        grid_chars[idx] = "█"
            sounding += grid_chars.count("█")
            total += num_chars
            row_cells.append("".join(grid_chars))
        density = (100 * sounding / total) if total else 0
        lines.append(f"{name:<16}: " + " |".join(row_cells) + f"  (Density: {density:.0f}%)")

    lines.append("-" * 70)
    lines.append("Legend: █ = Sounding | ░ = Rest | | = Section boundary")
    lines.append(header)
    return "\n".join(lines)


def print_high_contrast_grid(matrix: UnitMatrix, ticks_per_character: int = 120, **kwargs):
    """Print the grid to stdout (backward-compatible entry point)."""
    print(render_grid(matrix, ticks_per_character, **kwargs))


def write_grid_visualization(matrix: UnitMatrix, output_path: str,
                             ticks_per_character: int = 120, **kwargs) -> str:
    """Render the grid and write it to `output_path`. Returns the path."""
    import os
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    text = render_grid(matrix, ticks_per_character, **kwargs)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text + "\n")
    return output_path


if __name__ == "__main__":
    u11 = MusicUnit(events=[MusicEvent(60, 100, 0, 240), MusicEvent(62, 100, 240, 480)])
    u12 = MusicUnit(events=[MusicEvent(64, 100, 0, 480)])
    u21 = MusicUnit(events=[MusicEvent(48, 100, 0, 480)])
    u22 = MusicUnit(events=[])  # rest
    m = UnitMatrix(shape=(2, 2))
    m.set_unit((0, 0), u11); m.set_unit((0, 1), u12)
    m.set_unit((1, 0), u21); m.set_unit((1, 1), u22)
    print_high_contrast_grid(m, ticks_per_character=60,
                             voice_names=["Lead", "Bass"], bpm=120, mode="Ionian")
