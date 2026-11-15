# -*- coding: utf-8 -*-
"""Build index.html dashboard (VoltAgent styling) with rhythm DNA grids."""
import mido
import json

PROJ = "305-minimalism-phase-variations"
BASE = "/opt/data/projects/Styles/Minimalism/" + PROJ
mid_path = f"{BASE}/MIDI/{PROJ}-perfect.mid"

SECTIONS = [("Intro", 2), ("Phase1", 4), ("Phase2", 4), ("Phase3", 4),
            ("Phase4", 4), ("Phase5", 4), ("Bridge", 4), ("Phase6", 2),
            ("Resolve", 2), ("Coda", 2)]
BAR = 1920

VOICE_LABELS = ["MarimbaA", "MarimbaB", "Pad", "Bass", "Drums"]

mid = mido.MidiFile(mid_path)
total_bars = sum(b for _, b in SECTIONS)

tracks = []
for ti in range(1, len(mid.tracks)):
    tr = mid.tracks[ti]
    activity = [False] * total_bars
    t = 0
    for m in tr:
        t += m.time
        if m.type == "note_on" and m.velocity > 0:
            bar = min(t // BAR, total_bars - 1)
            activity[bar] = True
    tracks.append(activity)


def grid_row(activity):
    out = []
    acc = 0
    for name, bars in SECTIONS:
        for b in range(bars):
            out.append("\u2588" if activity[acc] else "\u2591")
            acc += 1
        out.append("|")
    return "".join(out)


rows = [(label, grid_row(act)) for label, act in zip(VOICE_LABELS, tracks)]


def section_ticks():
    parts = []
    acc = 0
    for name, bars in SECTIONS:
        parts.append(f"{name} {acc}-{acc+bars-1}")
        acc += bars
    return ", ".join(parts)


ver = json.load(open(f"{BASE}/Analysis/verification.json"))
perf = ver["report"]["perfect"]
hum = ver["report"]["humanized"]
ph1 = ver["report"]["phase1"]

grid_html = "\n".join(
    f'<div class="gridrow"><span class="vname">{name}</span><span class="grid">{grid}</span></div>'
    for name, grid in rows
)

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{PROJ}</title>
<style>
  :root {{ --bg:#050507; --accent:#00d992; --surface:#101010; --dim:#3a3a44; }}
  * {{ box-sizing:border-box; }}
  body {{ background:var(--bg); color:#e6e6ea; margin:0;
         font-family:'JetBrains Mono',ui-monospace,Menlo,monospace; }}
  header {{ padding:3rem 2rem 2rem; border-bottom:1px solid var(--surface); }}
  h1 {{ font-family:system-ui,-apple-system,sans-serif; font-size:3.75rem;
       line-height:1.0; margin:0 0 .5rem; color:#fff; font-weight:800; }}
  h1 .accent {{ color:var(--accent); }}
  .sub {{ color:#8a8a96; font-size:1rem; }}
  main {{ max-width:1180px; margin:0 auto; padding:2rem; }}
  section {{ background:var(--surface); border:1px solid var(--dim);
            border-radius:10px; padding:1.5rem; margin:1.5rem 0; }}
  h2 {{ font-family:system-ui,-apple-system,sans-serif; color:var(--accent);
       margin:0 0 1rem; font-size:1.3rem; }}
  table {{ width:100%; border-collapse:collapse; font-size:.9rem; }}
  th,td {{ text-align:left; padding:.5rem .6rem; border-bottom:1px solid var(--dim); }}
  th {{ color:var(--accent); font-weight:600; }}
  .pill {{ display:inline-block; background:rgba(0,217,146,.12);
          color:var(--accent); border:1px solid rgba(0,217,146,.4);
          border-radius:999px; padding:.15rem .7rem; margin:.2rem .2rem 0 0;
          font-size:.78rem; }}
  .gridrow {{ display:flex; align-items:baseline; gap:.6rem; padding:.25rem 0;
              overflow-x:auto; white-space:nowrap; }}
  .vname {{ color:var(--accent); min-width:6rem; font-weight:600; }}
  .grid {{ color:#c7c9d1; letter-spacing:.05em; }}
  .legend {{ color:#8a8a96; font-size:.8rem; margin-top:.5rem; }}
  .kpi {{ display:flex; gap:1.5rem; flex-wrap:wrap; }}
  .kpi div {{ background:var(--bg); border:1px solid var(--dim);
              border-radius:8px; padding:1rem 1.2rem; }}
  .kpi b {{ display:block; color:var(--accent); font-size:1.5rem; }}
  a {{ color:var(--accent); text-decoration:none; }}
  a:hover {{ text-decoration:underline; }}
  .ok {{ color:var(--accent); }} .warn {{ color:#ffb454; }}
</style>
</head>
<body>
<header>
  <h1>minimalism <span class="accent">phase</span> variations</h1>
  <div class="sub">{PROJ} · rework of 001-minimalism-phase-study · E(5,12) Euclidean phase cell</div>
</header>
<main>

<section>
  <h2>Meta</h2>
  <table>
    <tr><th>Key</th><td>C major (C D E F G A B)</td>
        <th>BPM</th><td>120 · 4/4 · 480 TPB</td></tr>
    <tr><th>Form</th><td colspan="3">intro-phase1-6-bridge-resolve-coda · 32 bars · 10 sections</td></tr>
    <tr><th>Voices</th><td colspan="3">MarimbaA(12) · MarimbaB(12) · Pad=Strings(48) · Bass(32) · Drums(ch9)</td></tr>
  </table>
</section>

<section>
  <h2>Variation techniques (7)</h2>
  <div>
    <span class="pill">T1 phase-walk — MarimbaB +1 beat/section</span>
    <span class="pill">T2 retrograde — Phase5 MarimbaB</span>
    <span class="pill">T3 inversion — Bridge MarimbaB</span>
    <span class="pill">T4 augmentation — Coda ×2</span>
    <span class="pill">T5 register shift — Phase4 +12 / bookends −12</span>
    <span class="pill">T6 density/diminution — Phase4+6 8th cell</span>
    <span class="pill">T7 relative-minor — Bridge → vi/Am</span>
  </div>
</section>

<section>
  <h2>Form &amp; harmonic regions</h2>
  <table>
    <tr><th>Section</th><th>Bars</th><th>Chords</th><th>Technique</th></tr>
    <tr><td>Intro</td><td>0-1</td><td>C C</td><td>T5 register −12</td></tr>
    <tr><td>Phase1</td><td>2-5</td><td>C C C C</td><td>baseline unison (phase 0)</td></tr>
    <tr><td>Phase2</td><td>6-9</td><td>C F C Am</td><td>T1 phase +1</td></tr>
    <tr><td>Phase3</td><td>10-13</td><td>C G C F</td><td>T1 phase +2</td></tr>
    <tr><td>Phase4</td><td>14-17</td><td>C Dm G C</td><td>T1 +3 · T5 +12 · T6 density</td></tr>
    <tr><td>Phase5</td><td>18-21</td><td>Am G Dm Am</td><td>T1 +4 · T2 retrograde</td></tr>
    <tr><td>Bridge</td><td>22-25</td><td>Am Dm Am C</td><td>T1 +5 · T3 inversion · T7 vi region</td></tr>
    <tr><td>Phase6</td><td>26-27</td><td>G Am</td><td>T1 +6 · T6 8th cell</td></tr>
    <tr><td>Resolve</td><td>28-29</td><td>C C</td><td>phase re-lock · T5 −12</td></tr>
    <tr><td>Coda</td><td>30-31</td><td>C C</td><td>T4 augmentation fade</td></tr>
  </table>
</section>

<section>
  <h2>Rhythm DNA <span class="legend">(█ onset · ░ rest · | section boundary)</span></h2>
  {grid_html}
  <div class="legend">grid = per-bar activity, {total_bars} bars → {section_ticks()}</div>
</section>

<section>
  <h2>Verification (read-only mido)</h2>
  <div class="kpi">
    <div><b>{perf['tracks']}</b>voice tracks</div>
    <div><b>{perf['track_len']}</b>track len (ticks)</div>
    <div><b class="ok">{perf['off120']}</b>off-grid (perfect)</div>
    <div><b class="ok">{hum['off120']}</b>off-grid (humanized)</div>
    <div><b class="ok">{perf['scale_violations']}</b>scale violations</div>
    <div><b class="ok">{perf['chord_violations_blanket']}</b>chord violations (perfect)</div>
    <div><b class="ok">{hum['strong_beat_violations']}</b>strong-beat violations</div>
    <div><b>{ph1['pitched']}</b>phase-1 raw notes</div>
  </div>
</section>

<section>
  <h2>Artifacts</h2>
  <table>
    <tr><th>MIDI</th><td><a href="MIDI/{PROJ}-phase1.mid">phase1</a> ·
      <a href="MIDI/{PROJ}-perfect.mid">perfect</a> ·
      <a href="MIDI/{PROJ}-humanized.mid">humanized</a></td></tr>
    <tr><th>Audio</th><td><a href="Audio/{PROJ}-perfect.ogg">perfect.ogg</a> ·
      <a href="Audio/{PROJ}-humanized.ogg">humanized.ogg</a> ·
      <a href="Audio/{PROJ}-phase1.ogg">phase1.ogg</a></td></tr>
    <tr><th>Docs</th><td><a href="REPORT.md">REPORT</a> ·
      <a href="Analysis/grid_visualization.txt">grid visualization</a> ·
      <a href="Analysis/verification.json">verification</a></td></tr>
  </table>
</section>

</main>
</body>
</html>
"""
with open(f"{BASE}/index.html", "w") as f:
    f.write(html)
print("INDEX_OK", len(html), "bytes")
