# -*- coding: utf-8 -*-
"""Generate index.html dashboard (VoltAgent styling) for 303-funk-som-suite."""
import os
import re

PROJ = "/opt/data/projects/Styles/Funk/303-funk-som-suite"
GV = os.path.join(PROJ, "Analysis", "grid_visualization.txt")

# parse voice DNA rows from grid_visualization.txt
rows = {}
with open(GV) as f:
    for line in f:
        m = re.match(r"^(\w+)\s+:\s+(.+)\s+\(Density: [\d.]+%\)\s*$", line)
        if m:
            name, dna = m.group(1), m.group(2).strip()
            rows[name] = dna

VOICES = ["Lead", "Sax", "Piano", "Bass", "Drums"]


def wrap(dna):
    # dna like "██░░██ ░ | ██..." -> split sections on ' | '
    sections = [s.strip() for s in dna.split("|")]
    out = []
    for i, sec in enumerate(sections):
        html = "".join('<span class="on">█</span>' if c == "█"
                       else '<span class="rest">░</span>' if c == "░"
                       else '<span class="sep"> </span>'
                       for c in sec)
        out.append(html)
        if i < len(sections) - 1:
            out.append('<span class="sep">|</span>')
    return "".join(out)


dna_blocks = []
for v in VOICES:
    dna_blocks.append('    <div class="dnaline"><span class="dlab">%-6s</span>%s</div>'
                      % (v, wrap(rows[v])))
DNA_HTML = "\n".join(dna_blocks)

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>303-funk-som-suite — Musicom</title>
<style>
  :root {
    --bg: #050507; --accent: #00d992; --surface: #101010; --ink: #e6e6e6;
    --muted: #7a7a82; --mono: "JetBrains Mono", "SFMono-Regular", Menlo, Consolas, monospace;
    --ui: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  }
  * { box-sizing: border-box; }
  body { margin: 0; background: var(--bg); color: var(--ink); font-family: var(--ui); line-height: 1.5; }
  header { padding: 3rem 2rem 1.5rem; border-bottom: 1px solid #1c1c22; }
  h1 { font-size: 60px; line-height: 1.0; margin: 0 0 .5rem; font-weight: 700; letter-spacing: -0.02em; }
  h1 .accent { color: var(--accent); }
  .sub { color: var(--muted); font-family: var(--mono); font-size: 14px; }
  main { padding: 2rem; max-width: 1080px; margin: 0 auto; }
  .grid2 { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem; }
  .card { background: var(--surface); border: 1px solid #1c1c22; border-radius: 10px; padding: 1.25rem 1.5rem; margin-bottom: 1rem; }
  .card h2 { font-size: 18px; margin: 0 0 .75rem; color: var(--accent); font-weight: 600; }
  .metric { font-family: var(--mono); font-size: 13px; }
  .metric b { color: var(--accent); font-weight: 600; }
  table { width: 100%; border-collapse: collapse; font-family: var(--mono); font-size: 13px; }
  th, td { text-align: left; padding: 6px 10px; border-bottom: 1px solid #1c1c22; }
  th { color: var(--muted); font-weight: 500; text-transform: uppercase; font-size: 11px; letter-spacing: .05em; }
  td.num { text-align: right; }
  .dna { font-family: var(--mono); font-size: 11px; line-height: 1.5; white-space: pre; overflow-x: auto; color: #b8b8c0; }
  .dna .on { color: var(--accent); }
  .dna .rest { color: #3a3a44; }
  .dna .sep { color: #555560; }
  .dnaline { white-space: nowrap; }
  .dlab { color: var(--muted); font-weight: 600; }
  .tags span { display: inline-block; background: #12251d; color: var(--accent); border: 1px solid #1e4232; border-radius: 20px; padding: 3px 12px; font-size: 12px; margin: 3px 4px 3px 0; font-family: var(--mono); }
  a { color: var(--accent); text-decoration: none; }
  a:hover { text-decoration: underline; }
  .ok { color: var(--accent); }
  .bar { height: 8px; background: #1c1c22; border-radius: 4px; overflow: hidden; margin: 6px 0; }
  .bar > i { display: block; height: 100%; background: linear-gradient(90deg, #818cf8, #00d992); }
  footer { color: var(--muted); font-family: var(--mono); font-size: 12px; padding: 2rem; text-align: center; }
</style>
</head>
<body>
<header>
  <h1>303 <span class="accent">funk-som-suite</span></h1>
  <div class="sub">Funk · F minor · 104 BPM · 4/4 · Method 075 SOM-C · 32 bars / 8 sections · source 098-funk-som</div>
</header>
<main>

  <div class="grid2">
    <div class="card">
      <h2>Identity</h2>
      <div class="metric">
        source: <b>098-funk-som</b> (standard 6 failed: index.html + root provenance.json missing)<br>
        key: <b>F minor</b> {F G Ab Bb C Db Eb}<br>
        method: <b>075 Self-Organizing Map</b> (4×4 toroidal lattice)<br>
        motif: <b>SOM trajectory walk</b> → quantized trumpet lead<br>
        voices: Lead Trumpet · Tenor Sax · Piano · Double Bass · Drums
      </div>
    </div>
    <div class="card">
      <h2>Form (8 sections)</h2>
      <div class="metric">
        Intro → Verse → Chorus → Bridge → Verse2 → Chorus2 → Breakdown → Outro<br>
        <div class="bar"><i style="width:100%"></i></div>
        <span>32 bars — N+2 sections, +33% longer than source</span>
      </div>
    </div>
  </div>

  <div class="card">
    <h2>Variation techniques (6)</h2>
    <div class="tags">
      <span>transposition +4th (Verse2)</span>
      <span>register shift +1 oct (Chorus2)</span>
      <span>retrograde contour (Bridge)</span>
      <span>augmentation ×2 (Breakdown)</span>
      <span>density contrast (Breakdown sparse)</span>
      <span>sax offbeat counterline</span>
    </div>
  </div>

  <div class="card">
    <h2>Rhythm DNA (16th grid — █ onset / ░ rest)</h2>
    <div class="dna">
""" + DNA_HTML + """
    </div>
  </div>

  <div class="grid2">
    <div class="card">
      <h2>Verification</h2>
      <table>
        <tr><th>metric</th><th>perfect</th><th>humanized</th></tr>
        <tr><td>voice tracks</td><td class="num">5</td><td class="num">5</td></tr>
        <tr><td>zero-drift (61440 t)</td><td class="num ok">true</td><td class="num ok">true</td></tr>
        <tr><td>off-grid (≠ mult 120)</td><td class="num ok">0</td><td class="num">634</td></tr>
        <tr><td>scale violations</td><td class="num ok">0</td><td class="num ok">0</td></tr>
        <tr><td>chord violations</td><td class="num ok">0</td><td class="num">9*</td></tr>
        <tr><td>strong-beat violations</td><td class="num ok">0</td><td class="num ok">0</td></tr>
      </table>
      <div class="metric" style="margin-top:.5rem;color:var(--muted)">* humanized chord violations = bar-seam jitter only; strong beats clean.</div>
    </div>
    <div class="card">
      <h2>Files</h2>
      <div class="metric">
        <a href="Audio/303-funk-som-suite-perfect.ogg">perfect.ogg</a> · <a href="Audio/303-funk-som-suite-humanized.ogg">humanized.ogg</a><br>
        <a href="MIDI/303-funk-som-suite-perfect.mid">perfect.mid</a> · <a href="MIDI/303-funk-som-suite-humanized.mid">humanized.mid</a> · <a href="MIDI/303-funk-som-suite-phase1.mid">phase1.mid</a><br>
        <a href="Analysis/grid_visualization.txt">grid_visualization.txt</a> · <a href="Analysis/verification.json">verification.json</a><br>
        <a href="provenance.json">provenance.json</a> · <a href="REPORT.md">REPORT.md</a>
      </div>
    </div>
  </div>

</main>
<footer>musicom-composer · nightly rework job · 2026-11-14 · engine: UnitMatrixComposer (two-phase) · Method 075 SOM-C extended</footer>
</body>
</html>
"""

with open(os.path.join(PROJ, "index.html"), "w") as f:
    f.write(HTML)
print("index.html written:", len(HTML), "bytes")
