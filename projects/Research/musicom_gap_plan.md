# Musicom Architecture Implementation Plan: Filling the Gaps

## 1. Environment & Dependencies (DawDreamer Setup)
*   **Status:** DawDreamer successfully installed under separate Python 3.11 virtual environment.
*   **Path:** `/opt/data/repos/musicom/.venv311/bin/python`
*   **Command Bridge Strategy:** Python 3.13 main engine compiles `UnitMatrix` and writes symbolic JSON/MIDI to a shared transfer folder. A dedicated Python 3.11 subprocess script loads `dawdreamer` to host VST3 plug-ins, apply automation curves, and render high-fidelity master WAV/OGG files.

---

## 2. Step-by-Step Gap Solution Plan

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          IMPLEMENTATION ROADMAP                         │
├─────────────────────────────────────────────────────────────────────────┤
│ PHASE 1: Macro-Form Controller (Theory & Structure)                     │
│ ░ [ ] Define FormPlan config (key-changes, intensity curves, density)    │
│ ░ [ ] Map global tension profile to UnitMatrix column generators        │
├─────────────────────────────────────────────────────────────────────────┤
│ PHASE 2: Python 3.11 DawDreamer Rendering Bridge (Tools & DSP)          │
│ ░ [ ] Write rendering subprocess bridge (musicom_render_bridge.py)      │
│ ░ [ ] Support MIDI-to-audio rendering with automated VST parameter sweeps│
├─────────────────────────────────────────────────────────────────────────┤
│ PHASE 3: Multi-Agent Orchestra Engine (Skills & Subagents)              │
│ ░ [ ] Configure role parameters (Theoretician, Melodist, Arranger)      │
│ ░ [ ] Implement rule validation checkpoints (Voice Leading & Range)     │
├─────────────────────────────────────────────────────────────────────────┤
│ PHASE 4: Human-in-the-Loop Feedback (Dashboard & Steering)             │
│ ░ [ ] Build index.html UI dashboard visualizing matrix grid             │
│ ░ [ ] Enable manual seeding and interactive mutation slider weights     │
└─────────────────────────────────────────────────────────────────────────┘
```

### Gap 1: Macro-Structural Form Logic (Theory)
*   **Action:** Create a `FormController` class.
*   **Input:** Section definitions (`Intro`, `Verse`, `Chorus`, `Outro`), target bar lengths, key center changes, and an absolute tension line (0.0 to 1.0).
*   **Logic:** Translate tension indices to generator properties at column margins (e.g. higher tension scales up rhythm division speeds, note density, register constraints, and chord density).

### Gap 2: DawDreamer DSP Engine Integration (Tools)
*   **Action:** Standardize VST loading and automation.
*   **Subprocess Execution:**
    ```python
    import dawdreamer as daw
    engine = daw.RenderEngine(44100, 512)
    # Load VST instrument or sampler
    synth = engine.make_plugin_processor("synth", "/path/to/instrument.vst3")
    synth.load_midi("track.mid")
    # Apply LFO/automation curve to parameter 0 (e.g., cutoff)
    synth.set_parameter(0, 0.5)
    # Render audio output
    engine.render(duration_seconds)
    audio = engine.get_audio()
    ```

### Gap 3: Role-Based Agent Coordination (Skills)
*   **Action:** Build modular step execution pipeline in `musicom.workflows.UnitMatrixComposer`.
*   **Verification:** Reject invalid progressions or parallel fifths automatically before writing to MIDI.

### Gap 4: Piano-Roll Dashboard Dashboard (Human-in-the-Loop)
*   **Action:** Construct a lightweight static HTML canvas engine showing note-blocks across the matrix grid. Add interactive sliders to adjust scale settings and re-render loops directly.
