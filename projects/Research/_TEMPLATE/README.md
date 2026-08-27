# <Project Name>

Composition project using the **musicom** engine. Copy this folder, rename, fill in `compose.py`.

## Rules
- Use `musicom` engine only (see `compose.py`). No raw `mido` authoring, no `sys.path` hacks.
- Outputs → `outputs/`. Provenance sidecar per artifact. Run `preflight_check.py` before finishing.

## Run
```bash
/opt/data/micromamba/envs/musicom/bin/python compose.py
/opt/data/micromamba/envs/musicom/bin/python /opt/data/projects/Research/preflight_check.py .
```
