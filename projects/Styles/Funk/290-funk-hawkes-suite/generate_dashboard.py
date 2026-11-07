# -*- coding: utf-8 -*-
"""Generate index.html dashboard (VoltAgent styling) + top-level provenance.json."""
import os
import json

import mido  # READING ONLY (analysis)

PROJ = "/opt/data/projects/Styles/Funk/290-funk-hawkes-suite"
PERFECT = os.path.join(PROJ, "MIDI", "290-funk-hawkes-suite-perfect.mid")

BAR = 1920
GRID16 = 120
N_BARS = 32
NAMES = ["Intro", "Verse", "Chorus", "Break", "Verse2", "Chorus2",
         "Bridge", "Outro"]

# Lead voice rhythm DNA (track 1 = lead, skip conductor track 0)
mid = mido.MidiFile(PERFECT)
lead = mid.tracks[1]
onsets = set()
tick = 0
for m in lead:
    tick += m.time
    if m.type == "note_on" and m.velocity > 0 and m.channel != 9:
        onsets.add(tick)

rows = []
for bar in range(N_BARS):
    cells = []
    for s in range(16):
        t = bar * BAR + s * GRID16
        cells.append("█" if t in onsets else "░")
    sec = NAMES[bar // 4]
    rows.append(f"{sec:8s} | {''.join(cells)} | bar {bar+1:2d}")

grid_text = "\n".join(rows)

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>290-funk-hawkes-suite — Funk HPSEC Rework</title>
<style>
  body {{ background:#050507; color:#e8e8ec; font-family:'JetBrains Mono',monospace;
         margin:0; padding:40px; line-height:1.5; }}
  h1 {{ font-family:system-ui,-apple-system,sans-serif; font-size:60px;
       line-height:1.0; margin:0 0 8px; color:#fff; }}
  .accent {{ color:#00d992; }}
  .surf {{ background:#101010; border:1px solid #1a1a1a; border-radius:8px;
          padding:20px; margin:20px 0; }}
  .grid {{ font-size:13px; letter-spacing:1px; white-space:pre; }}
  table {{ border-collapse:collapse; width:100%; }}
  td,th {{ padding:8px 12px; text-align:left; border-bottom:1px solid #1a1a1a; }}
  th {{ color:#00d992; }}
  a {{ color:#00d992; text-decoration:none; }}
  .metric {{ font-size:14px; color:#8a8a94; }}
</style>
</head>
<body>
<h1>290 <span class="accent">funk-hawkes-suite</span></h1>
<div class="metric">Funk · Method 045 Hawkes Self-Exciting (HPSEC) · F minor ·
100 BPM · 4/4 · 32 bars (8 sections)</div>

<div class="surf">
<h3 class="accent">Form</h3>
<div class="grid">{' | '.join(f"{n} ({8+i*4}-{11+i*4})" for i, n in enumerate(NAMES))}</div>
</div>

<div class="surf">
<h3 class="accent">Lead rhythm DNA (█ onset · ░ rest, 16th grid)</h3>
<pre class="grid">{grid_text}</pre>
</div>

<div class="surf">
<h3 class="accent">Variation techniques</h3>
<table>
<tr><th>Technique</th><th>Where</th><th>How</th></tr>
<tr><td>Transposition</td><td>Verse2</td><td>lead register +12 (octave up)</td></tr>
<tr><td>Retrograde</td><td>Bridge</td><td>lead = reversed Chorus2 pitch seq</td></tr>
<tr><td>Inversion</td><td>Bridge</td><td>sax = Verse sax inverted (axis 70)</td></tr>
<tr><td>Augmentation</td><td>Outro</td><td>lead durations doubled</td></tr>
<tr><td>Diminution</td><td>Chorus2</td><td>lead density 48 (16th-note)</td></tr>
<tr><td>Density rise</td><td>Chorus2</td><td>full kit + claps + crash</td></tr>
</table>
</div>

<div class="surf">
<h3 class="accent">Artifacts</h3>
<table>
<tr><th>File</th><th>Link</th></tr>
<tr><td>Perfect MIDI</td><td><a href="MIDI/290-funk-hawkes-suite-perfect.mid">290-funk-hawkes-suite-perfect.mid</a></td></tr>
<tr><td>Humanized MIDI</td><td><a href="MIDI/290-funk-hawkes-suite-humanized.mid">290-funk-hawkes-suite-humanized.mid</a></td></tr>
<tr><td>Phase-1 MIDI</td><td><a href="MIDI/290-funk-hawkes-suite-phase1.mid">290-funk-hawkes-suite-phase1.mid</a></td></tr>
<tr><td>Perfect OGG</td><td><a href="Audio/290-funk-hawkes-suite-perfect.ogg">290-funk-hawkes-suite-perfect.ogg</a></td></tr>
<tr><td>Humanized OGG</td><td><a href="Audio/290-funk-hawkes-suite-humanized.ogg">290-funk-hawkes-suite-humanized.ogg</a></td></tr>
</table>
</div>
</body>
</html>
"""
with open(os.path.join(PROJ, "index.html"), "w") as f:
    f.write(html)
print("index.html written")

# top-level provenance.json (aggregate)
prov = {
    "project": "290-funk-hawkes-suite",
    "genre": "Funk",
    "method": "045 Hawkes Process Self-Exciting Composition (HPSEC)",
    "key": "F minor",
    "bpm": 100,
    "bars": N_BARS,
    "sections": NAMES,
    "source": "/opt/data/projects/Styles/Funk/088-funk-hawkes",
    "redesign": True,
    "audit_failure": ["index.html missing", "top-level provenance.json missing"],
    "seed": 20261107,
    "variation": ["transposition", "retrograde", "inversion", "augmentation",
                  "diminution", "density-rise", "counterline"],
    "generator": "Hawkes HPSEC + musicom rules + humanize (export_dual)",
    "created_utc": "2026-11-07",
}
with open(os.path.join(PROJ, "provenance.json"), "w") as f:
    json.dump(prov, f, indent=2)
print("provenance.json written")
