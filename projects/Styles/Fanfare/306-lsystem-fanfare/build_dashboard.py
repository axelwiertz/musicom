# -*- coding: utf-8 -*-
"""Build index.html dashboard (VoltAgent black/emerald styling)."""
import json
import os

PROJ = "306-lsystem-fanfare"
BASE = "/opt/data/projects/Styles/Fanfare/" + PROJ
AN = os.path.join(BASE, "Analysis")


def load(name, default=None):
    p = os.path.join(AN, name)
    if os.path.exists(p):
        with open(p) as f:
            return json.load(f)
    return default


s = load("compose_summary.json") or {}
v = load("verification.json") or {}
r = load("render_report.json") or {}

perf = (v.get("report") or {}).get("perfect", {})
hum = (v.get("report") or {}).get("humanized", {})

# rhythm DNA grid: per-section onset heat for the lead (Trumpet) — simplified
# to a text block from grid_visualization.txt
grid_txt = ""
gp = os.path.join(AN, "grid_visualization.txt")
if os.path.exists(gp):
    with open(gp) as f:
        grid_txt = f.read()

rows = ""
for sec, chords in (s.get("progression") or {}).items():
    bars = s.get("section_bars", [])[list((s.get("progression") or {}).keys()).index(sec)] \
        if sec in (s.get("progression") or {}) else 0
    rows += (f'<tr><td class="mono">{sec}</td><td class="mono">{bars}</td>'
             f'<td class="mono">{" · ".join(chords)}</td></tr>\n')

render_rows = ""
if r:
    for ver in ("phase1", "perfect", "humanized"):
        d = r.get(ver, {})
        if not d:
            continue
        render_rows += (f'<tr><td class="mono">{ver}</td>'
                        f'<td class="mono">{d.get("lufs")} LUFS</td>'
                        f'<td class="mono">{d.get("true_peak_db")} dBTP</td>'
                        f'<td class="mono">{d.get("silence_ratio")}</td>'
                        f'<td class="mono">{d.get("ogg_bytes", 0) // 1024} KB</td></tr>\n')

off_p = perf.get("off120", "?")
off_h = hum.get("off120", "?")

html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>{PROJ} — Fanfare L-System</title>
<style>
:root {{ --bg:#050507; --accent:#00d992; --surface:#101010; }}
body {{ background:var(--bg); color:#e8e8e8; font-family:'JetBrains Mono',monospace;
       margin:0; padding:2rem 3rem; }}
h1 {{ font-family:system-ui; font-size:60px; line-height:1.0; margin:0 0 .2rem; }}
h1 .accent {{ color:var(--accent); }}
h2 {{ font-family:system-ui; color:var(--accent); margin-top:2rem; }}
table {{ border-collapse:collapse; margin:1rem 0; }}
td,th {{ border:1px solid #222; padding:.4rem .9rem; text-align:left; }}
th {{ color:var(--accent); font-family:system-ui; }}
.mono {{ font-family:'JetBrains Mono',monospace; }}
.tag {{ color:var(--accent); }}
pre {{ background:var(--surface); padding:1rem; overflow:auto; font-size:11px; line-height:1.2; }}
audio {{ margin:.4rem 0; width:100%; }}
</style></head><body>
<h1>306 <span class="accent">L-System Fanfare</span></h1>
<p class="mono">Method 019 · L-System Algorithmic Composition (concrete) ·
   Bb major · 120 BPM · cinematic-build · 32 bars</p>

<h2>Listen</h2>
<p class="mono"><b>perfect</b> (grid-locked)</p>
<audio controls src="Audio/{PROJ}-perfect.ogg"></audio>
<p class="mono"><b>humanized</b> (style + brass DNA)</p>
<audio controls src="Audio/{PROJ}-humanized.ogg"></audio>
<p class="mono"><b>phase1</b> (raw L-system draft)</p>
<audio controls src="Audio/{PROJ}-phase1.ogg"></audio>

<h2>L-System (method 019)</h2>
<pre>axiom = "{s.get('lsystem',{}).get('axiom','C')}"
rules = {json.dumps(s.get('lsystem',{}).get('rules',{}))}
interpretation: A=+1 degree, B=-1 degree, C=+2 degrees, R=rest
symbols = {s.get('lsystem',{}).get('symbols','?')} (A{s.get('lsystem',{}).get('symbol_counts',{}).get('A','?')} B{s.get('lsystem',{}).get('symbol_counts',{}).get('B','?')} C{s.get('lsystem',{}).get('symbol_counts',{}).get('C','?')} R{s.get('lsystem',{}).get('symbol_counts',{}).get('R','?')})</pre>

<h2>Form & Progression (Bb major)</h2>
<table><tr><th>Section</th><th>Bars</th><th>Chords</th></tr>{rows}</table>

<h2>Verification</h2>
<table><tr><th>Version</th><th>Tracks</th><th>Zero-drift</th><th>Off-grid (16th)</th>
<th>Untagged out-of-scale</th><th>Strong violations</th></tr>
<tr><td class="mono">phase1</td><td class="mono">{(v.get('report') or {}).get('phase1',{}).get('tracks','?')}</td>
<td class="mono">raw</td><td class="mono">{(v.get('report') or {}).get('phase1',{}).get('off120','?')}</td>
<td class="mono">{(v.get('report') or {}).get('phase1',{}).get('scale_violations','?')} (raw)</td>
<td class="mono">—</td></tr>
<tr><td class="mono">perfect</td><td class="mono">{perf.get('tracks','?')}</td><td class="mono">{perf.get('zero_drift')}</td>
<td class="mono">{off_p}</td><td class="mono">{perf.get('scale_violations')}</td>
<td class="mono">{perf.get('strong_violations')}</td></tr>
<tr><td class="mono">humanized</td><td class="mono">{hum.get('tracks','?')}</td><td class="mono">{hum.get('zero_drift')}</td>
<td class="mono">{off_h}</td><td class="mono">{hum.get('scale_violations')}</td>
<td class="mono">{hum.get('strong_violations')}</td></tr></table>

<h2>Render (mastered, target {r.get('target_lufs')} LUFS)</h2>
<table><tr><th>Version</th><th>LUFS</th><th>True-peak</th><th>Silence</th><th>OGG</th></tr>{render_rows}</table>

<h2>Humanization (seed {s.get('hz_seed')})</h2>
<pre>{json.dumps(s.get('hz', {}), indent=2)}</pre>

<h2>Rhythm DNA (grid)</h2>
<pre>{grid_txt}</pre>
</body></html>
"""
out = os.path.join(BASE, "index.html")
with open(out, "w") as f:
    f.write(html)
print("DASHBOARD_OK", out, os.path.getsize(out), "bytes")
