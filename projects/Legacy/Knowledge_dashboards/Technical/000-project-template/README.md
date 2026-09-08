# 000 — Project Template
## Musicom Composition Workflow

### Pillars
1. **Theory (Theoretician role):** Tonic, mode, harmonic matrix, rules JSON
2. **DNA (Melodist role):** PitchPattern intervals + Euclidean RhythmPattern
3. **Synthesis (Arranger role):** Multi-track render → WAV/OGG via numpy+ffmpeg
4. **Dashboard:** index.html (dark, Slate-950 / Cyan / Rose) + piano roll + volume graph
5. **Publish:** Commit to musicom-agent/music-projects → GitHub Pages

### Standard Folder Structure
```
NNN-project-name/
├── index.html          ← project dashboard page
├── README.md           ← this file
├── src/                ← Python composition scripts
├── midi/               ← generated or source MIDI files
├── audio/              ← rendered .wav and .ogg files
├── analysis/           ← piano_roll.png, volume_graph.png, JSON analyses
└── dashboard/          ← optional extra assets (images, data)
```

### Audio Stack (available in Docker)
- **music21 10.1.0** — theory, score analysis, MusicXML
- **musicpy 7.12** — chord/melody generation, MIDI I/O
- **mido** — low-level MIDI read/write
- **numpy 2.4.5** — raw synthesis (sine/sawtooth/noise)
- **ffmpeg 7.1** — WAV→OGG conversion, format bridge
- *(fluidsynth/soundfonts: not installed — use numpy synthesis or ffmpeg web-sample fetch)*

### Naming Convention
`NNN-kebab-case-name` where NNN = 3-digit zero-padded ID (000 = template)
