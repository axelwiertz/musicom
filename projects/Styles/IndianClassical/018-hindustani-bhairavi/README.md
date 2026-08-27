# 018 - Hindustani Classical: Raga Bhairavi & Teental

## Concept
Autonomous, live-expanding composition in Hindustani Classical tradition. Generative Sitar melodies inside **Raga Bhairavi** structured over a 16-beat **Teental** on Tabla, backed by a constant staggered **Tanpura** drone.

## Pattern Center

### 1. Swaras (Pitch Pattern)
*   **Scale Center**: D tonal center (Sa = D4, MIDI 62).
*   **Mode/Thaat**: Bhairavi Thaat (equivalent to Phrygian mode).
*   **Swaras (Scale Degrees)**: 1, b2, b3, 4, 5, b6, b7, 8 (Sa, Komal Re, Komal Ga, Shuddha Ma, Pa, Komal Dha, Komal Ni, Tar Sa).
*   **MIDI Set**: `{62, 63, 65, 67, 69, 70, 72, 74}` (centered on D4).
*   **Raga Gravity (Melodic Vadi/Samvadi)**: Foci on Sa, Ma, Pa.

### 2. Tala (Rhythmic Pattern)
*   **Rhythmic Cycle**: Teental (16 beats).
*   **Division**: 4 + 4 + 4 + 4.
*   **Metric Gravity Points**:
    *   **Beat 1 (Sam)**: Heavy accent on first beat (Clap / Sa).
    *   **Beat 5 (Taali)**: Secondary accent (Clap).
    *   **Beat 9 (Khali)**: Silent / open wave (Khali).
    *   **Beat 13 (Taali)**: Third accent (Clap).
*   **Tabla Bol Grid**:
    ```
    1   2   3   4   | 5   6   7   8   | 9   10  11  12  | 13  14  15  16
    Dha Dhin Dhin Dha | Dha Dhin Dhin Dha | Dha Tin  Tin  Ta  | Ta  Dhin Dhin Dha
    (X)  - Clap       | (2) - Clap       | (0) - Wave       | (3) - Clap
    ```

## Structure
*   **Drone (Tanpura)**: Continuous staggered sweeps playing Sa (D2/D3) and Pa (A2).
*   **Solo Sitar (Melody)**: Active live Taan (rapid stepwise sweeps), Alap structures, and ornaments/grace notes (meends) triggered programmatically on the fly.
*   **Tabla (Rhythm)**: Dynamic accompaniment with double-tempo offbeat filler triggers during active claps.

## Executables
*   `/src/live_composer.py`: The live infinite generation kernel.

## Output Media
*   `MIDI/bhairavi_live_render.mid`
*   `Audio/bhairavi_live_render.ogg`
