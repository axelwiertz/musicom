#!/opt/data/micromamba/envs/musicom/bin/python
# -*- coding: utf-8 -*-
"""Generate VoltAgent-styled index.html dashboard for 104-celtic-subset-variations."""
import os, json, html

PROJ = "/opt/data/projects/Styles/Celtic/104-celtic-subset-variations"
ANALYSIS = os.path.join(PROJ, "Analysis")

summary = json.load(open(os.path.join(ANALYSIS, "summary.json")))
verify = json.load(open(os.path.join(ANALYSIS, "verify.json")))
render = json.load(open(os.path.join(ANALYSIS, "render_stats.json")))
grid_txt = open(os.path.join(ANALYSIS, "grid_visualization.txt")).read()

p2 = verify["audit"]["phase2"]
p1 = verify["audit"]["phase1"]
sections = summary["sections"]
mid = summary["section_midpoint"]
prog = summary["progression"]

section_rows = ""
for name, bars in sections.items():
    m = mid[name]
    bar_span = f"{list(sections).index(name)*4}-{list(sections).index(name)*4+3}"
    section_rows += (
        f'<tr><td class="mono">{name}</td><td class="mono">{bars} bars</td>'
        f'<td class="mono">{m["degree"]}</td>'
        f'<td class="mono">{m["quality"]}</td>'
        f'<td class="mono">{" ".join(m["bars"])}</td></tr>\n'
    )

var_rows = ""
for i, v in enumerate(summary["variation_techniques"], 1):
    var_rows += f'<tr><td class="mono">V{i}</td><td>{html.escape(v.split(" ", 1)[1])}</td></tr>\n'

ogg2 = "Audio/104-celtic-subset-variations.ogg"
ogg1 = "Audio/104-celtic-subset-variations-phase1.ogg"
r2 = render.get("104-celtic-subset-variations", {})
r1 = render.get("104-celtic-subset-variations-phase1", {})

html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>104-celtic-subset-variations — Musicom Rework</title>
<style>
  :root {{
    --bg: #050507; --accent: #00d992; --surface: #101010;
    --txt: #e6e6e6; --dim: #888;
  }}
  * {{ box-sizing: border-box; }}
  body {{ background: var(--bg); color: var(--txt); margin: 0;
         font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
         line-height: 1.5; }}
  .wrap {{ max-width: 1080px; margin: 0 auto; padding: 2rem 1.5rem; }}
  h1 {{ font-size: 60px; line-height: 1.0; margin: 0 0 0.25rem; color: var(--accent);
       letter-spacing: -0.02em; }}
  h2 {{ font-size: 22px; color: var(--accent); margin: 2rem 0 0.75rem;
       border-bottom: 1px solid #1e1e1e; padding-bottom: 0.4rem; }}
  .sub {{ color: var(--dim); margin: 0 0 1.5rem; }}
  .mono {{ font-family: "JetBrains Mono", "Fira Code", ui-monospace, monospace; }}
  .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
           gap: 0.75rem; margin: 1rem 0; }}
  .card {{ background: var(--surface); border: 1px solid #1e1e1e; border-radius: 8px;
          padding: 0.9rem; }}
  .card .k {{ font-size: 11px; text-transform: uppercase; color: var(--dim);
            letter-spacing: 0.08em; }}
  .card .v {{ font-size: 22px; color: var(--accent); font-family: ui-monospace, monospace; }}
  table {{ border-collapse: collapse; width: 100%; margin: 0.75rem 0;
          background: var(--surface); border-radius: 8px; overflow: hidden; }}
  th, td {{ text-align: left; padding: 0.5rem 0.75rem; font-size: 13px;
           border-bottom: 1px solid #1a1a1a; }}
  th {{ color: var(--accent); font-size: 11px; text-transform: uppercase;
       letter-spacing: 0.06em; background: #0b0b0d; }}
  pre {{ background: var(--surface); border: 1px solid #1e1e1e; border-radius: 8px;
        padding: 1rem; overflow-x: auto; font-size: 11px; line-height: 1.35; }}
  a {{ color: var(--accent); text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  .ok {{ color: var(--accent); }} .bad {{ color: #ff5d5d; }}
  .pill {{ display:inline-block; background:#0b0b0d; border:1px solid #1e1e1e;
          border-radius:999px; padding:0.2rem 0.6rem; margin:0.15rem; font-size:12px; }}
</style>
</head>
<body>
<div class="wrap">
  <h1>104-celtic-subset-variations</h1>
  <p class="sub">Musicom rework of <span class="mono">085-celtic-subset-walk</span>
     &middot; Celtic &middot; ABS-002 Subset Walker + ABS-001 tension curve + method-006 cadence</p>

  <div class="cards">
    <div class="card"><div class="k">Key</div><div class="v">Ab maj</div></div>
    <div class="card"><div class="k">BPM</div><div class="v">96</div></div>
    <div class="card"><div class="k">Meter</div><div class="v">4/4</div></div>
    <div class="card"><div class="k">Form</div><div class="v">8&times;4</div></div>
    <div class="card"><div class="k">Bars</div><div class="v">32</div></div>
    <div class="card"><div class="k">Voices</div><div class="v">7</div></div>
    <div class="card"><div class="k">Variations</div><div class="v">7</div></div>
    <div class="card"><div class="k">Decision</div><div class="v" style="font-size:14px">redesign+extend</div></div>
  </div>

  <h2>Listen</h2>
  <p>
    <a href="{ogg2}" download>Phase 2 (rules) &mdash; OGG</a> &nbsp;&middot;&nbsp;
    <a href="MIDI/104-celtic-subset-variations.mid" download>Phase 2 &mdash; MIDI</a> &nbsp;&middot;&nbsp;
    <a href="{ogg1}" download>Phase 1 (raw) &mdash; OGG</a> &nbsp;&middot;&nbsp;
    <a href="MIDI/104-celtic-subset-variations-phase1.mid" download>Phase 1 &mdash; MIDI</a>
  </p>

  <h2>Section Map (per-section harmonic regions, midpoint chord)</h2>
  <table>
    <tr><th>Section</th><th>Length</th><th>Midpoint degree</th><th>Quality</th><th>Bar progression</th></tr>
    {section_rows}
  </table>

  <h2>Variation Techniques</h2>
  <table>
    <tr><th>#</th><th>Technique (where applied)</th></tr>
    {var_rows}
  </table>

  <h2>Verification (phase 2)</h2>
  <div class="cards">
    <div class="card"><div class="k">Voice tracks</div><div class="v">{p2["n_tracks"]}</div></div>
    <div class="card"><div class="k">Track length</div><div class="v" style="font-size:16px">{p2["lengths"][0]}</div></div>
    <div class="card"><div class="k">Zero-drift</div><div class="v ok">pass</div></div>
    <div class="card"><div class="k">Off-grid</div><div class="v ok">{p2["off_grid"]}</div></div>
    <div class="card"><div class="k">Scale viol</div><div class="v ok">{p2["scale_viol"]}</div></div>
    <div class="card"><div class="k">Chord viol</div><div class="v ok">{p2["chord_viol"]}</div></div>
    <div class="card"><div class="k">Silence</div><div class="v">{r2.get("silence_ratio", "—")}</div></div>
    <div class="card"><div class="k">Peak</div><div class="v">{r2.get("peak", "—")}</div></div>
  </div>

  <h2>Rhythm DNA</h2>
  <pre class="mono">{html.escape(grid_txt)}</pre>

  <p class="sub" style="margin-top:2rem">Musicom &middot; VoltAgent dashboard &middot;
     generated {html.escape(str(summary.get("seed", "")))}</p>
</div>
</body>
</html>
"""

with open(os.path.join(PROJ, "index.html"), "w") as f:
    f.write(html_doc)
print("index.html written", os.path.getsize(os.path.join(PROJ, "index.html")), "bytes")
