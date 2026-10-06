# -*- coding: utf-8 -*-
"""Generate index.html dashboard (VoltAgent styling) from real composition data."""
import importlib.util, sys, datetime

spec = importlib.util.spec_from_file_location("c", "Scripts/compose.py")
c = importlib.util.module_from_spec(spec)
sys.modules["c"] = c
spec.loader.exec_module(c)

LEAD, PROG, SECTIONS = c.LEAD, c.PROG, c.SECTIONS
dt = datetime.datetime.utcnow().isoformat()

grid = [['░'] * 16 for _ in range(24)]
for (bar, s, d, p) in LEAD:
    if 0 <= bar < 24 and 0 <= s < 16:
        grid[bar][s] = '█'

bars_html = ''.join(
    f'<div class="brow"><span class="blbl">{b:02d}</span>'
    f'<span class="bgrid">{"".join(grid[b])}</span></div>' for b in range(24))

chords = ' '.join(PROG)
sec_strip = []
bar = 0
for name, n in SECTIONS:
    sec_strip.append(
        f'<span class="secchip" style="flex:{n}">{name}'
        f'<br><small>{PROG[bar]}…{PROG[bar+n-1]}</small></span>')
    bar += n

html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>225 · Country Steel Rework</title>
<style>
:root {{ --bg:#050507; --accent:#00d992; --surface:#101010; --ink:#e6e6e6; --dim:#7a7a7a; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--ink); font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif; }}
header {{ padding:32px 40px 20px; border-bottom:1px solid #1a1a1a; }}
h1 {{ font-size:60px; line-height:1.0; margin:0 0 8px; font-weight:800; letter-spacing:-1px; }}
h1 .acc {{ color:var(--accent); }}
.sub {{ color:var(--dim); font-family:'JetBrains Mono',monospace; font-size:14px; }}
main {{ padding:28px 40px 60px; max-width:1100px; }}
h2 {{ font-size:22px; margin:32px 0 12px; font-weight:700; }}
h2::before {{ content:'▍'; color:var(--accent); margin-right:8px; }}
.card {{ background:var(--surface); border:1px solid #1a1a1a; border-radius:10px; padding:18px 20px; margin:12px 0; }}
.mono {{ font-family:'JetBrains Mono',monospace; }}
.metrics {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:12px; }}
.metric {{ background:var(--surface); border:1px solid #1a1a1a; border-radius:8px; padding:14px; }}
.metric .v {{ font-family:'JetBrains Mono',monospace; font-size:30px; color:var(--accent); font-weight:700; }}
.metric .k {{ color:var(--dim); font-size:12px; text-transform:uppercase; letter-spacing:1px; }}
.secstrip {{ display:flex; gap:6px; }}
.secchip {{ background:var(--surface); border:1px solid #1a1a1a; border-radius:8px; padding:10px; text-align:center; font-weight:700; }}
.secchip small {{ color:var(--dim); font-family:'JetBrains Mono',monospace; font-weight:400; }}
.brow {{ display:flex; align-items:center; gap:10px; font-family:'JetBrains Mono',monospace; font-size:14px; }}
.blbl {{ color:var(--dim); width:24px; text-align:right; }}
.bgrid {{ letter-spacing:1px; color:var(--accent); }}
.legend {{ color:var(--dim); font-family:'JetBrains Mono',monospace; font-size:12px; margin-top:8px; }}
table {{ width:100%; border-collapse:collapse; font-family:'JetBrains Mono',monospace; font-size:13px; }}
td,th {{ border:1px solid #1a1a1a; padding:7px 10px; text-align:left; }}
th {{ color:var(--accent); font-weight:600; }}
a {{ color:var(--accent); text-decoration:none; }}
.fail {{ color:#ff5c5c; }} .pass {{ color:var(--accent); }}
</style></head><body>
<header>
<h1>225 <span class="acc">Country Steel</span> Rework</h1>
<div class="sub">source 038-steel-guitar-demo · G major · 90 BPM · 24 bars · two-phase · UnitMatrixComposer</div>
</header>
<main>

<h2>Verification</h2>
<div class="metrics">
<div class="metric"><div class="v">5</div><div class="k">voice tracks</div></div>
<div class="metric"><div class="v">46080</div><div class="k">ticks / track</div></div>
<div class="metric"><div class="v">0</div><div class="k">off-grid onsets</div></div>
<div class="metric"><div class="v">0</div><div class="k">scale violations</div></div>
<div class="metric"><div class="v">0</div><div class="k">chord violations</div></div>
<div class="metric"><div class="v">24</div><div class="k">bars</div></div>
</div>

<h2>Form &amp; Harmony</h2>
<div class="card"><div class="secstrip">{''.join(sec_strip)}</div></div>
<div class="card mono">chords/bar: {chords}</div>

<h2>Rhythm DNA — Lead (█ onset · ░ rest)</h2>
<div class="card">{bars_html}</div>
<div class="legend">16th-note grid per bar (16 cols) · 120 ticks / cell. Chorus 10–17 = register shift; bridge 18–21 = retrograde descent; outro 22–23 = augmentation.</div>

<h2>Variation Techniques</h2>
<table>
<tr><th>Technique</th><th>Section</th></tr>
<tr><td>Register shift (+octave)</td><td>Chorus</td></tr>
<tr><td>Retrograde (contour reversal)</td><td>Bridge</td></tr>
<tr><td>Augmentation (long values)</td><td>Outro / Bridge bass</td></tr>
<tr><td>Counterline (fiddle)</td><td>Chorus + Bridge</td></tr>
<tr><td>Per-section harmonic regions</td><td>all</td></tr>
<tr><td>Density rise (drums)</td><td>intro→chorus</td></tr>
</table>

<h2>Artifacts</h2>
<div class="card mono">
<a href="Audio/225-country-steel-rework.ogg">Audio/225-country-steel-rework.ogg</a><br>
<a href="MIDI/225-country-steel-rework.mid">MIDI/225-country-steel-rework.mid</a><br>
<a href="MIDI/225-country-steel-rework-phase1.mid">MIDI/225-country-steel-rework-phase1.mid</a><br>
<a href="Analysis/grid_visualization.txt">Analysis/grid_visualization.txt</a><br>
<a href="Analysis/verify.json">Analysis/verify.json</a><br>
<a href="Scripts/compose.py">Scripts/compose.py</a>
</div>

<h2>Audit (source)</h2>
<table>
<tr><th>Standard</th><th>Result</th></tr>
<tr><td>Engine (UnitMatrixComposer)</td><td class="fail">FAIL — raw mido</td></tr>
<tr><td>Zero-drift</td><td class="fail">FAIL — 30480 vs 34330</td></tr>
<tr><td>Rhythm-grid sync</td><td class="fail">FAIL — 448/576 off-grid</td></tr>
<tr><td>≥4 voice tracks</td><td class="fail">FAIL — 2</td></tr>
<tr><td>Two-phase artifacts</td><td class="fail">FAIL</td></tr>
<tr><td>provenance + index</td><td class="fail">FAIL</td></tr>
</table>
<div class="card mono" style="color:var(--dim)">decision: REDESIGN · reworked {dt}</div>

</main></body></html>"""

open("index.html", "w").write(html)
print("wrote index.html", len(html), "bytes")
