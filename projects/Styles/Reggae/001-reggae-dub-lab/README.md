# Reggae Style (001-reggae-dub-lab)

## 1. Overview
The Reggae style project explores classic Jamaican roots and dub architecture. It is built around three core stylistic pillars:
*   **The One-Drop**: Emphasizes Beat 3 of a standard 4/4 meter. Beat 1 is left entirely silent (or carried by a pickup bass note).
*   **The Skank (Chop)**: Staccato offbeat keyboard/guitar chords sounding precisely on the "and" of each beat (Beats 1+, 2+, 3+, 4+).
*   **The Bubble**: Dynamic keyboard shuffle subdivision rolling between the offbeats.

---

## 2. Musical Elements Framework Analysis

### PITCH
- **Concept**: Bass utilizes deep, minor-modal pentatonic scales with frequent slides or syncopated octave jumps. The lead brass tracks catchy, repetitive modal lines.
- **Register Boundaries**:
  - *Lead (Trumpet/Melody)*: $C_5$ to $G_6$ (Midi 72 to 103).
  - *Skank/Chops (Guitar/Keys)*: $C_4$ to $C_5$ (Midi 60 to 72).
  - *Bass (Tuba/Electric)*: $C_1$ to $C_3$ (Midi 24 to 48).

### RHYTHM
- **Concept**: Absolute focus on syncopation and spaces (the "space is the place" dub ethos).
- **Subdivision**: 16th-note swing / shuffle.
- **Anchor Positions**: 
  - Snare/Rimshot triggers strictly on Beat 3 ("One-Drop").
  - Guitar/Keys skank triggers on offbeats (the "and" offsets).

### HARMONY
- **Concept**: Minimalist chord progressions, often looping between two simple modal steps (e.g., $i \leftrightarrow bVII$ in Minor/Dorian or $I \leftrightarrow ii$ in Major).
- **Functional States**:
  - **HOME (Tonic)**: Steady root chord (e.g., A Minor).
  - **LIFT (Departure)**: Secondary step (e.g., G Major).
  - **TENSE (Climax)**: Embellished suspensions or dynamic horn stabs.
  - **TURN (Pivot/Resolution)**: Descending bass walk returning to tonic.

### STRUCTURE
- **Concept**: Multi-section form consisting of intro/outro blocks flanking standard Verse/Chorus loops, designed for seamless real-time looping.

### TEXTURE
- **Concept**: Highly spatialized. Intermittent drop-outs of vocals, keys, or drums to expose the bass and echo-laden effects (Dub-cuts).

---

## 3. UnitMatrix Mapping & Realization

The **UnitMatrix** maps the 4-voice Jamaican instrumentation across 4 distinct sections.

### Voice & Section Population:
- **Rows (Voices)**:
  - **Voice 0 (Lead Brass/Trumpet)**: Delivers sparse melodic hooks.
  - **Voice 1 (Skank Chops/Organ)**: Delivers staccato offbeat accompaniment.
  - **Voice 2 (Reggae Bass)**: Heavy syncopated low-end walk.
  - **Voice 3 (One-Drop Drums)**: Rhythmic engine emphasizing Beat 3.
- **Columns (Sections)**:
  - **Section 0 (Intro)**: Bass and drums only (establishing the groove).
  - **Section 1 (Verse)**: Full band, introducing the skank and subtle horn lines.
  - **Section 2 (Chorus)**: Peak density, full thematic brass melody.
  - **Section 3 (Outro - Dub Out)**: Instruments decay into space, leaving only bass and scattered rimshots.

---

## 4. Evaluation Scorecard (Composition Exercises)

We evaluated two generative methods inside this Reggae context: **Schillinger Design (M-018)** and **Negative Harmony Mapping (M-014)**.

| Metric | Schillinger Resultant (M-018) | Negative Harmony Axis Mirror (M-014) |
| :--- | :--- | :--- |
| **Stylistic Accuracy** | **8/10** (Creates authentic syncopated cross-rhythms) | **9/10** (Mirrors loops into highly authentic dark minor grooves) |
| **UnitMatrix Compliance**| **10/10** (Zero-drift alignment, identical track sizes) | **10/10** (Perfect track size, identical boundaries) |
| **Creative Novelty** | **9/10** (Generates fresh offbeat patterns) | **8/10** (Instantly flips happy chords to dub-minor) |
| **Acoustic Coherence** | **8/10** (Highly structured, clean phrasing) | **9/10** (Excellent physical bass range conservation) |

### Performance Evaluation Notes:
*   **Schillinger Resultants ($3 \div 2$ and $4 \div 3$)**: When mapped to offbeat skank and bass weights, the interference patterns generated highly authentic Jamaican cross-rhythms without manual note-placement. It naturally produced syncopated structures because the math naturally lands on offbeats.
*   **Negative Harmony Reflection**: Taking a standard, happy major loop and mirroring it across the dominant-tonic axis instantly generated an incredibly deep, melancholic minor-Dorian progression ideal for a "Roots Reggae" aesthetic.
