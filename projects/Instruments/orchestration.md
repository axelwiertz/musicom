# Orchestration — musicom workflow bridge

Orchestration = **how to combine instruments** (role assignment, register allocation,
doubling, timbre blending, section-by-section dynamics). Complements the per-instrument
facts in `Strings/`, `Keys/`, etc.

## Two-phase composition with orchestration

```
Phase 1: COMPOSITION (what to play)
  → skeleton, form, harmony, melody, rhythm

Phase 2: ORCHESTRATION (who plays what)
  → role assignment, register allocation, doubling, dynamics

Phase 3: PRODUCTION (how it sounds)
  → synthesis, effects, mastering
```

Orchestration sits between composition and production. It translates abstract musical
ideas into concrete instrument assignments.

## Orchestration workflow

### Step 1: Define roles

Every voice in the arrangement needs a role:

| Role | Function | Typical instruments |
|---|---|---|
| **Melody** | main theme, lead line | Violin, Flute, Trumpet, Piano (high) |
| **Counter** | secondary melody, call-response | Violin 2, Clarinet, Trombone |
| **Harmony** | chordal support, comping | Piano, Guitar, Strings (section) |
| **Bass** | low foundation, root movement | Double Bass, Bass Guitar, Tuba, Piano (low) |
| **Rhythm** | groove, pulse | Drum Kit, Percussion, Guitar (strum) |
| **Pad** | sustained background, texture | Strings (sustained), Synth Pad, Organ |
| **Accent** | hits, stabs, fanfare | Brass, Crash, Timpani |

### Step 2: Assign instruments to roles

Use the Instruments registry to pick instruments. Each role has a **primary** and
**secondary** family:

```python
from projects.Instruments.orchestration import ROLE_PROFILES

# Example: pop arrangement
roles = {
    "melody":  ROLE_PROFILES["melody"]["primary"],   # Violin
    "harmony": ROLE_PROFILES["harmony"]["primary"],  # Piano
    "bass":    ROLE_PROFILES["bass"]["primary"],     # Double Bass
    "rhythm":  ROLE_PROFILES["rhythm"]["primary"],   # Drum Kit
    "pad":     ROLE_PROFILES["pad"]["primary"],      # Strings (section)
}
```

### Step 3: Allocate registers

Avoid register crossing. Keep each instrument in its sweet spot:

```python
from projects.Instruments.orchestration import allocate_registers

# Given roles + instruments, return MIDI range per voice
ranges = allocate_registers(roles)
# → {"melody": (67, 96), "harmony": (48, 71), "bass": (36, 55), ...}
```

Rules:
- **Melody** sits above harmony (no crossing)
- **Bass** stays below 60 (C4) to avoid mud
- **Harmony** fills the middle (48–71)
- **Pad** can overlap harmony but at lower velocity

### Step 4: Doubling (optional)

Double important lines for emphasis or blend:

| Doubling type | Effect | Example |
|---|---|---|
| **Octave** | power, fullness | Violin + Cello (8va) |
| **Unison** | thickness, blend | Violin 1 + Violin 2 (same line) |
| **Cross-family** | color, blend | Flute + Violin (melody) |
| **Brass + Strings** | epic, cinematic | Trumpet + Violins (fanfare) |

```python
from projects.Instruments.orchestration import DOUBLE_RULES

# Double melody: Violin + Flute (unison)
doubled_melody = [VIOLIN, FLUTE]
```

### Step 5: Section dynamics

Vary instrumentation across sections for contrast:

| Section | Density | Instrumentation |
|---|---|---|
| **Intro** | sparse (2–3 voices) | Melody + Pad (or Rhythm) |
| **Verse** | medium (3–4 voices) | Melody + Harmony + Bass + Rhythm |
| **Chorus** | full (5–6 voices) | All roles, doubled melody |
| **Bridge** | contrast (drop or add) | Drop Rhythm, add Counter |
| **Outro** | dropout (progressive) | Remove voices one by one |

```python
from projects.Instruments.orchestration import SECTION_DYNAMICS

# Pop arrangement
dynamics = SECTION_DYNAMICS["pop"]
# → {"intro": ["melody", "pad"], "verse": [...], "chorus": [...], ...}
```

### Step 6: Balance (velocity scaling)

Melody loudest, bass solid, harmony softer, pad background:

```python
from projects.Instruments.orchestration import BALANCE_PROFILE

# Pop mix balance (relative velocity multipliers)
balance = BALANCE_PROFILE["pop"]
# → {"melody": 1.0, "harmony": 0.7, "bass": 0.9, "rhythm": 0.8, "pad": 0.5}
```

Apply to composition:
```python
melody_vel = 85 * balance["melody"]   # 85
harmony_vel = 85 * balance["harmony"] # 60
```

## Integration with UnitMatrixComposer

```python
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from projects.Instruments.orchestration import (
    ROLE_PROFILES, allocate_registers, SECTION_DYNAMICS, BALANCE_PROFILE,
)

# 1. Define roles
roles = ["melody", "harmony", "bass", "rhythm", "pad"]

# 2. Allocate registers
ranges = allocate_registers(roles)

# 3. Build composer
composer = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
composer.create_matrix(num_voices=len(roles), num_sections=5)

# 4. Add voices (from ROLE_PROFILES)
for i, role in enumerate(roles):
    inst = ROLE_PROFILES[role]["primary"]
    composer.add_voice(role.capitalize(), program=inst.MIDI_PROGRAM, channel=i)

# 5. Add sections
for section in ["Intro", "Verse", "Chorus", "Bridge", "Outro"]:
    composer.add_section(section, bars=4)

# 6. Fill cells (with register + balance constraints)
for s, section in enumerate(["Intro", "Verse", "Chorus", "Bridge", "Outro"]):
    active_roles = SECTION_DYNAMICS["pop"][section]
    for r, role in enumerate(roles):
        if role in active_roles:
            unit = build_unit_for_role(role, ranges[role], section)
            composer.set_unit(r, s, unit)

# 7. Validate + export
ok, msg = composer.validate()
composer.to_midi("arrangement.mid")
```

## Orchestration presets

Pre-defined arrangements for common genres:

```python
from projects.Instruments.orchestration import ORCHESTRATION_PRESETS

# Pop preset
pop = ORCHESTRATION_PRESETS["pop"]
# → roles, dynamics, balance, doubling rules

# Classical preset
classical = ORCHESTRATION_PRESETS["classical"]
# → strings + woodwind + brass + timpani, full orchestration

# Jazz preset
jazz = ORCHESTRATION_PRESETS["jazz"]
# → trumpet + sax + piano + bass + drums
```

## Verification

See `_test/verify_orchestration.py` for a working example:
- Pop arrangement (5 roles, 5 sections)
- Register allocation (no crossing)
- Balance applied (melody loudest, pad softest)
- Zero-drift validated
- MIDI + WAV exported

## Pitfalls

- **Register crossing**: melody below harmony → muddy mix. Check `ranges` before filling cells.
- **Too many voices**: >6 voices in pop = clutter. Stick to 4–5 for clarity.
- **Uniform dynamics**: same velocity across all roles = flat mix. Apply `BALANCE_PROFILE`.
- **Sparse intro**: 1 voice = boring. Add Pad or Rhythm for texture.
- **Chorus dropout**: don't drop Melody or Bass (core roles). Drop Pad or Counter.

## References

- HC-011 Orchestration (Western Classical tradition)
- Instruments registry: `/opt/data/projects/Instruments/registry.md`
- musicom-composer skill: composition workflow (Phase 1)
- genre-composition-patterns: density targets per genre
