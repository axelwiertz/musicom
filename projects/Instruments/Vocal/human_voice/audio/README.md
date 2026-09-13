# Human Voice — demo audio

Rendered by `render_demo.py` via `sound/synthesis/singing_voice.py`.

- `phrase_<bass|tenor|alto|soprano>.ogg` — the same C-major phrase sung by
  each voice type (transposed into its comfortable register). Listen for the
  timbre brightening from bass → soprano at the same *musical* position —
  that is the vocal-tract-length effect, not a pitch change.
- `vowels_a_e_i_o_u.ogg` — one pitch (A4), five vowels. The vowel identity
  lives entirely in the formant envelope (F1/F2), not the pitch.
- `clean_vs_breathy.ogg` — the same note clean, then breathy (aspiration +
  lower open quotient). The "air" is added turbulence noise, the same
  physical mechanism as a real whisper.

Regenerate with:

```bash
PY=/opt/data/micromamba/envs/musicom/bin/python
$PY render_demo.py
```
