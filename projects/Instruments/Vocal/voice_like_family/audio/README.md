# Voice-like family — audio demos

Rendered from `sound/synthesis/voice_like.py`. The `.wav` files are the raw
mono renders (gitignored, regenerate with `analyze_and_render.py`); the `.ogg`
files are the tracked deliverables.

All clips play the same phrase in D minor so the six instruments are directly
comparable:

```
D5(0.55,o) F#5(0.35,a) C5(0.55,e) D5(0.75,a) G4(0.40,o) D5(0.90,a) A4(0.55,u) D5(0.55,e) C5(1.10,a)
```

| file | what it is |
|---|---|
| `vox_humana.ogg` | free reed + short resonator — the organ stop named for the voice |
| `kazoo.ogg` | mirliton membrane buzz — bright, nasal honk |
| `jaw_harp.ogg` | plucked lamella — twangy drone, sharp attack |
| `didgeridoo.ogg` | lip reed in a long bore — deep vocal drone |
| `singing_saw.ogg` | bowed steel friction — ethereal, wide vocal vibrato |
| `talkbox.ogg` | amplified saw through the mouth — "talking" lead |
| `vowels_vox_humana.ogg` | vowel tour `a e i o u` on the vox humana |
| `talkbox_morph.ogg` | single note with a formant glide `/a/ -> /o/` |

Regenerate everything (and print the verification tables):

```bash
$MUSICOM_PYTHON ../voice_like_family/analyze_and_render.py
```
