# -*- coding: utf-8 -*-
"""Build the VoltAgent-styled dashboard (black/emerald) for 309-celtic-sieve-set."""
import os

BASE = "/opt/data/projects/Styles/Celtic/309-celtic-sieve-set"

SIEVES = {
    "S1": {"pitch_mod": 4, "pitch_res": [0, 2], "rhythm_mod": 4, "rhythm_res": [0, 3], "pool": "{0,2,4,6,8,10} whole-tone"},
    "S2": {"pitch_mod": 3, "pitch_res": [0, 1], "rhythm_mod": 3, "rhythm_res": [0, 2], "pool": "{0,1,3,4,6,7,9,10}"},
    "S3": {"pitch_mod": 5, "pitch_res": [0, 2], "rhythm_mod": 5, "rhythm_res": [0, 2], "pool": "{0,2,5,7,10} pentatonic"},
    "S4": {"pitch_mod": 4, "pitch_res": [1, 3], "rhythm_mod": 4, "rhythm_res": [1, 2], "pool": "{1,3,5,7,9,11}"},
    "S5": {"pitch_mod": 3, "pitch_res": [0, 2], "rhythm_mod": 3, "rhythm_res": [0],    "pool": "{0,2,3,5,6,8,9,11}"},
    "S6": {"pitch_mod": 7, "pitch_res": [0, 4], "rhythm_mod": 4, "rhythm_res": [0, 3], "pool": "{0,4,7,11} quartal"},
}
PROG = {
    "S1": ["D", "D", "G", "D"],
    "S2": ["G", "D", "Am", "D"],
    "S3": ["Em", "D", "G", "Am"],
    "S4": ["Bm", "G", "D", "Am"],
    "S5": ["G", "Em", "Bm", "Am"],
    "S6": ["D", "G", "Am", "D"],
}


def rhythm_rows(name):
    sv = SIEVES[name]
    rm, rres = sv["rhythm_mod"], sv["rhythm_res"]
    rows = []
    for bar in range(4):
        cells = []
        for s in range(16):
            step = bar * 16 + s
            cells.append("█" if (step % rm) in rres else "░")
        rows.append("".join(cells))
    return rows


sections_html = []
for name in ["S1", "S2", "S3", "S4", "S5", "S6"]:
    sv = SIEVES[name]
    grid_rows = rhythm_rows(name)
    bars_html = "".join(
        f'<div class="rbar">' +
        "".join(f'<span class="{ "on" if c == "█" else "off" }">{c}</span>' for c in row) +
        "</div>" for row in grid_rows)
    sections_html.append(f"""
    <div class="section">
      <div class="sechead"><span class="sname">{name}</span>
        <span class="mono">pitch {sv['pitch_mod']}@{{{','.join(map(str, sv['pitch_res']))}}} · rhythm {sv['rhythm_mod']}@{{{','.join(map(str, sv['rhythm_res']))}}}</span>
      </div>
      <div class="pool mono">pool {sv['pool']}</div>
      <div class="grid">{bars_html}</div>
      <div class="mono prog">chords {' · '.join(PROG[name])}</div>
    </div>""")

html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>309 · Celtic Sieve Set</title>
<style>
:root {{ --bg:#050507; --acc:#00d992; --surf:#101010; --txt:#e8e8e8; --dim:#7a7a7a; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--txt);
  font-family:'JetBrains Mono', ui-monospace, monospace; }}
h1,h2,h3 {{ font-family:system-ui, -apple-system, 'Segoe UI', sans-serif; }}
h1 {{ font-size:60px; line-height:1.0; margin:0 0 8px; letter-spacing:-1px; }}
h2 {{ color:var(--acc); font-size:22px; margin:28px 0 12px; }}
.wrap {{ max-width:1080px; margin:0 auto; padding:32px 20px 64px; }}
.meta {{ color:var(--dim); font-size:13px; line-height:1.7; }}
.meta b {{ color:var(--acc); font-weight:600; }}
.section {{ background:var(--surf); border:1px solid #181818; border-radius:8px;
  padding:14px 16px; margin:12px 0; }}
.sechead {{ display:flex; justify-content:space-between; align-items:baseline; gap:12px; flex-wrap:wrap; }}
.sname {{ color:var(--acc); font-weight:700; font-size:18px; font-family:system-ui,sans-serif; }}
.mono {{ font-size:12px; color:var(--dim); }}
.pool {{ margin:6px 0 4px; }}
.grid {{ margin:4px 0 8px; }}
.rbar {{ display:flex; gap:2px; margin:1px 0; }}
.rbar span {{ width:22px; height:18px; display:inline-flex; align-items:center;
  justify-content:center; font-size:11px; border-radius:3px; }}
.rbar .on {{ background:linear-gradient(135deg,#00d992,#00b375); color:#04241a; font-weight:700; }}
.rbar .off {{ background:#1a1a1a; color:#333; }}
.prog {{ color:var(--acc); }}
a {{ color:var(--acc); text-decoration:none; }}
a:hover {{ text-decoration:underline; }}
audio {{ width:100%; margin:4px 0; }}
.playlist {{ display:flex; flex-direction:column; gap:8px; }}
.legend {{ font-size:12px; color:var(--dim); margin-bottom:8px; }}
.legend .on, .legend .off {{ display:inline-block; width:14px; height:12px; border-radius:2px;
  vertical-align:middle; margin:0 4px 0 0; }}
.legend .on {{ background:#00d992; }} .legend .off {{ background:#1a1a1a; border:1px solid #333; }}
</style></head><body><div class="wrap">

<h1>309 · Celtic Sieve Set</h1>
<div class="meta">
<b>style</b> Celtic &nbsp;·&nbsp; <b>method</b> 025 Xenakis Sieve Theory (Rules-Based, concrete)<br>
<b>key</b> D Mixolydian &nbsp;·&nbsp; <b>tempo</b> 120 BPM &nbsp;·&nbsp; <b>form</b> through-composed (6 × 4 bars = 24)<br>
<b>voices</b> Violin · Flute · Bagpipe · Harp · Double Bass &nbsp;·&nbsp; <b>hz seed</b> 69180
</div>

<h2>Listen</h2>
<div class="playlist">
<div><span class="mono">perfect</span><br>
<audio controls preload="none" src="Audio/309-celtic-sieve-set-perfect.ogg"></audio></div>
<div><span class="mono">humanized</span><br>
<audio controls preload="none" src="Audio/309-celtic-sieve-set-humanized.ogg"></audio></div>
<div><span class="mono">phase1 (raw sieve)</span><br>
<audio controls preload="none" src="Audio/309-celtic-sieve-set-phase1.ogg"></audio></div>
</div>

<h2>MIDI</h2>
<div class="meta">
<a href="MIDI/309-celtic-sieve-set-perfect.mid">-perfect.mid</a> ·
<a href="MIDI/309-celtic-sieve-set-humanized.mid">-humanized.mid</a> ·
<a href="MIDI/309-celtic-sieve-set-phase1.mid">-phase1.mid</a>
</div>

<h2>Rhythm DNA — per-section sieve (16th grid, █ onset · ░ rest)</h2>
<div class="legend"><span class="on"></span>onset&nbsp;&nbsp;<span class="off"></span>rest</div>
{''.join(sections_html)}

</div></body></html>"""

with open(os.path.join(BASE, "index.html"), "w") as f:
    f.write(html)
print("DASHBOARD_OK", os.path.join(BASE, "index.html"))
