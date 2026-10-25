# -*- coding: utf-8 -*-
"""Generate index.html dashboard for the rework (VoltAgent styling, real data)."""
import json
import os

import mido  # READING ONLY (analysis)

ROOT = "/opt/data/repos/musicom/projects/Styles/West African Polyrhythms/264-rbncc-west-african-polyrhythm-rework"
NAME = "264-rbncc-west-african-polyrhythm-rework"

summary = json.load(open(f"{ROOT}/Analysis/summary.json"))
verify = json.load(open(f"{ROOT}/Analysis/verify.json"))
hz = json.load(open(f"{ROOT}/MIDI/{NAME}-humanized.mid.provenance.json"))["parameters"]["humanize"]

BAR = 1920
S16 = 120
N_BARS = summary["bars"]
FORM = summary["form"]
VOICES = summary["voices"]
VARIATIONS = summary["variations"]
ROOTS = summary["section_roots_midpoint"]

# extract rhythm DNA from perfect MIDI (lead ch1 + drums ch9)
mid = mido.MidiFile(f"{ROOT}/MIDI/{NAME}-perfect.mid")
lead_rows = []       # 16-char strings per bar
drum_rows = []
for t in mid.tracks[1:]:
    ch = None
    prog = None
    for m in t:
        if m.type == "program_change":
            ch = m.channel
            prog = m.program
    is_drums = ch == 9
    is_lead = (ch == 1)
    if not (is_drums or is_lead):
        continue
    grid = [set() for _ in range(N_BARS)]
    t_abs = 0
    for m in t:
        t_abs += m.time
        if m.type == "note_on" and m.velocity > 0:
            bar = t_abs // BAR
            if bar < N_BARS:
                slot = (t_abs % BAR) // S16
                grid[bar].add(slot)
    rows = [''.join('█' if s in grid[b] else '░' for s in range(16)) for b in range(N_BARS)]
    if is_lead:
        lead_rows = rows
    else:
        drum_rows = rows


def row_html(rows):
    out = []
    for b, r in enumerate(rows):
        cells = ''.join(f'<span class="{"on" if c == "█" else "off"}">{c}</span>' for c in r)
        out.append(f'<tr><td class="bar">{b:02d}</td><td class="grid">{cells}</td></tr>')
    return ''.join(out)


def hz_table():
    rows = []
    for v in VOICES:
        if v == "Drums":
            continue
        h = hz.get(v, {})
        rows.append(f"<tr><td>{v}</td><td>{h.get('mean_abs_shift_ticks', 0):.2f}</td>"
                    f"<td>{h.get('max_abs_shift_ticks', 0)}</td>"
                    f"<td>{h.get('mean_abs_vel_delta', 0):.2f}</td></tr>")
    h = hz.get("Drums", {})
    rows.append(f"<tr><td>Drums</td><td>{h.get('mean_abs_shift_ticks', 0):.2f}</td>"
                f"<td>{h.get('max_abs_shift_ticks', 0)}</td>"
                f"<td>{h.get('mean_abs_vel_delta', 0):.2f}</td></tr>")
    return ''.join(rows)


def section_table():
    rows = []
    bar = 0
    for sname in FORM:
        nb = 4
        b0 = bar
        b1 = bar + nb - 1
        root = ROOTS[sname]
        var = VARIATIONS[sname]
        rows.append(f"<tr><td>{sname}</td><td>{b0}–{b1}</td>"
                    f"<td>{root}</td><td>{var}</td></tr>")
        bar += nb
    return ''.join(rows)


p = verify["perfect"]
hz_row = verify["humanized"]
ph1 = verify["phase1"]

html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{NAME}</title>
<style>
:root {{ --bg:#050507; --accent:#00d992; --surface:#101010; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:#e6e6e6;
  font-family:system-ui,-apple-system,Segoe UI,sans-serif; }}
header {{ padding:40px 32px 20px; border-bottom:1px solid #1a1a1a; }}
h1 {{ font-size:60px; line-height:1.0; margin:0 0 8px; color:#fff; }}
.sub {{ color:#888; font-size:16px; }}
.accent {{ color:var(--accent); }}
main {{ padding:24px 32px 48px; max-width:1200px; margin:0 auto; }}
section {{ margin:28px 0; }}
h2 {{ font-size:22px; letter-spacing:.5px; color:var(--accent);
  border-bottom:1px solid #1a1a1a; padding-bottom:6px; }}
table {{ border-collapse:collapse; width:100%; }}
th,td {{ padding:6px 12px; text-align:left; border-bottom:1px solid #161616;
  font-family:"JetBrains Mono",monospace; font-size:13px; }}
th {{ color:#888; font-weight:600; }}
.metrics {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr));
  gap:12px; }}
.card {{ background:var(--surface); border:1px solid #1a1a1a;
  border-radius:8px; padding:16px; }}
.card .k {{ color:#888; font-size:12px; text-transform:uppercase;
  letter-spacing:1px; }}
.card .v {{ font-family:"JetBrains Mono",monospace; font-size:26px;
  color:var(--accent); margin-top:4px; }}
.grid {{ font-family:"JetBrains Mono",monospace; font-size:14px;
  letter-spacing:2px; }}
.on {{ color:var(--accent); }}
.off {{ color:#2a2a2a; }}
.bar {{ color:#666; }}
a.play {{ display:inline-block; margin:6px 12px 6px 0; padding:10px 18px;
  background:var(--surface); border:1px solid var(--accent); color:var(--accent);
  border-radius:6px; text-decoration:none; font-family:"JetBrains Mono",monospace; }}
</style></head>
<body>
<header>
  <h1>264-<span class="accent">rbncc-west-african-polyrhythm</span>-rework</h1>
  <div class="sub">West African Polyrhythms · G major · 112 BPM · 4/4 ·
  10 sections × 4 bars = 40 bars
  &nbsp;·&nbsp; rework of <span class="accent">210-rbncc-west-african-polyrhythm</span>
  &nbsp;·&nbsp; method 082 RBNCC (N=16 K=2 p=0.5, cycle 12 → 3:4 polyrhythm)</div>
</header>
<main>
<section>
  <h2>Listen</h2>
  <a class="play" href="Audio/{NAME}-perfect.ogg">▶ perfect.ogg</a>
  <a class="play" href="Audio/{NAME}-humanized.ogg">▶ humanized.ogg</a>
  <a class="play" href="MIDI/{NAME}-perfect.mid">⤓ perfect.mid</a>
  <a class="play" href="MIDI/{NAME}-humanized.mid">⤓ humanized.mid</a>
  <a class="play" href="MIDI/{NAME}-phase1.mid">⤓ phase1.mid</a>
</section>
<section>
  <h2>Verification</h2>
  <div class="metrics">
    <div class="card"><div class="k">zero-drift</div><div class="v">5 × {p['voice_len']}</div></div>
    <div class="card"><div class="k">off-grid (perfect)</div><div class="v">{p['offgrid']}</div></div>
    <div class="card"><div class="k">off-grid (humanized)</div><div class="v">{hz_row['offgrid']}</div></div>
    <div class="card"><div class="k">scale violations</div><div class="v">{p['scale_viol']}</div></div>
    <div class="card"><div class="k">chord violations</div><div class="v">{p['chord_viol']}</div></div>
    <div class="card"><div class="k">notes</div><div class="v">{p['total_notes']}</div></div>
    <div class="card"><div class="k">bars</div><div class="v">{N_BARS}</div></div>
  </div>
</section>
<section>
  <h2>Sections — midpoint roots + variation</h2>
  <table><thead><tr><th>section</th><th>bars</th><th>midpoint root</th>
  <th>variation</th></tr></thead><tbody>
{section_table()}
  </tbody></table>
</section>
<section>
  <h2>Humanization (per-voice, mean/max shift ticks, vel Δ)</h2>
  <table><thead><tr><th>voice</th><th>shift mean</th><th>shift max</th>
  <th>vel Δ</th></tr></thead><tbody>
{hz_table()}
  </tbody></table>
</section>
<section>
  <h2>Rhythm DNA — lead kalimba · 16th grid</h2>
  <table><thead><tr><th>bar</th><th>onsets (█ hit · ░ rest)</th></tr></thead>
  <tbody>{row_html(lead_rows)}</tbody></table>
</section>
<section>
  <h2>Rhythm DNA — drums (ch9) · 16th grid</h2>
  <table><thead><tr><th>bar</th><th>onsets (█ hit · ░ rest)</th></tr></thead>
  <tbody>{row_html(drum_rows)}</tbody></table>
</section>
</main></body></html>
"""

with open(f"{ROOT}/index.html", "w") as f:
    f.write(html)
print("index.html written:", os.path.getsize(f"{ROOT}/index.html"), "bytes")
print("lead rows:", len(lead_rows), "drum rows:", len(drum_rows))
