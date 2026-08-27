# SP-014 — Waveguide Mesh Physical Modeling (Modern Disco)

Production pass: **SP-014 Waveguide Mesh Physical Modeling** applied to
**`modern_disco.mid`** (Modern Disco, 126 BPM, 63.5s).

| Field | Value |
|---|---|
| Method ID | SP-014 |
| Method | Waveguide Mesh Physical Modeling |
| Layer | Synthesis Engines |
| Target | Acoustic / Resonant Space Timbre |
| Source composition | `/opt/data/projects/Styles/Disco/modern/v1/modern_disco.mid` |
| Source tempo | 126.0 BPM |
| Source duration | 60.95 s (render 63.45 s with tail) |
| Source tracks | Drums (ch9, 736 notes), Bass (pgm 88, ch0, 512), Lead (pgm 74, ch1, 256), Strings (pgm 49, ch2, 768) |
| Render | `Audio/mix_mesh_gm.wav` + `Audio/mix_mesh_gm.ogg` (Opus) |
| Mastering | musicom `MasteringChain`: StereoImager(1.15) + Limiter(-1.0 dB) + LUFS(-14) |

## What was done

The pitched instruments (lead, bass, strings) were re-synthesized with a
**2D digital waveguide mesh** — the SP-014 physical model. The mesh is a grid
of delay lines connected by scattering junctions; a strike excites a
displacement wave that propagates, reflects at clamped boundaries, and is
read at a pickup point. Each note's mesh grid size scales with pitch
(higher notes -> smaller, brighter meshes; lower notes -> larger, deeper
meshes), giving a marimba / steel-pan / drumhead hybrid timbre.

The drum track (channel 9) was rendered through FluidSynth GM
(TimGM6mb.sf2) to keep the disco groove rhythmically intact, then all layers
were mixed and mastered.

### Layers

| Layer | Source | Treatment |
|---|---|---|
| Drums | ch9 | FluidSynth GM (unchanged rhythm, centered) |
| Lead | ch1 (pgm 74) | waveguide mesh, grid ~ 11, damping 0.9965, clamped edges |
| Strings | ch2 (pgm 49) | waveguide mesh, grid ~ 15, damping 0.9970, clamped edges |
| Bass | ch0 (pgm 88) | waveguide mesh, grid ~ 19, damping 0.9980 (low body) |
| MeshBed | — | bar-aligned low drone strikes on a large plate (room resonance) |

### Files

```
SP014-waveguide-mesh-disco/
├── README.md
├── produce_sp014.py          # full production script (engine + pipeline)
├── MIDI/
│   └── original.mid          # source composition (DAW artifact)
├── Audio/
│   ├── mix_mesh_gm.wav       # final stereo mix (mastered)
│   ├── mix_mesh_gm.ogg       # Opus render (Telegram playback)
│   └── stems/
│       ├── Drums_GM.wav
│       ├── LeadFlute.wav
│       ├── StringsPlate.wav
│       └── MeshBed.wav
└── Analysis/
    ├── provenance.json
    └── grid_visualization.txt
```

## Method notes (SP-014 implementation)

- Junction update (uniform 2D mesh): `v[n] = d*0.5*(N+S+E+W)[n-1] - d^2*v[n-2]`
- **Damping** `d`: 0.9965 (lead) / 0.997 (strings) / 0.998 (bass) / 0.9985 (bed)
- **Boundaries**: clamped (`r = -1`, phase-inverted reflection, like a drumhead edge)
- **Excitation**: raised-cosine displacement strike + short harmonic-rich
  impulse at the note pitch injected into the strike region (the mesh colors
  the decay; the excitation carries the pitch — verified: dominant spectral
  peak == struck note, x1.00 across the tested register)
- **Pickup**: pressure read at (0.3, 0.4) of the mesh

### Debugging note (engine fix)

The first implementation rebind-swapped the mesh state buffers
(`grid_prev, grid_curr = grid_curr, grid_next`) which **aliased** the arrays:
the next iteration overwrote the `n-1` state mid-read, and the recursion
exploded to `inf` (~2.84x/step). Verified against a dense-matrix eigenvalue
form of the same recursion (max|eig| = d <= 1 => stable). Fix: copy buffers
(`np.copy`) on every step, exactly as the spec's reference implementation
does. The full render now runs NaN/inf-free.

## Verification (real outputs)

| Check | Result |
|---|---|
| Mix peak / RMS | 0.863 / -17.1 dBFS |
| Mix duration | 63.45 s (source 60.95 s + tail) |
| Spectral balance | sub 0.9e9 / bass 7.4e9 / mids 20.0e9 / highs 1.8e9 / air 16e6 |
| Stems | Drums 0.877 / Lead 0.652 / Strings 0.277 / Bed 0.154 peak |
| OGG | 63.46 s, 408 KB (Opus 48k voip) |
| Silence checks | PASS (early, mid, tail all have signal) |
| MIDI artifact | `MIDI/original.mid` (17,213 bytes) |

## Listen for

- **Lead** = mesh "steel pan" character over the straight disco backbeat
- **Strings** = resonant plate shimmer under the lead line
- **Bass** = deep mesh body (drum-like low end, high damping for long decay)
- **MeshBed** = sub-audible room resonance struck once per bar
- The **decay tails** are pure waveguide physics — no reverb plugin was used
