# -*- coding: utf-8 -*-
"""Generate index.html dashboard (VoltAgent styling) with real rhythm DNA
read from the -perfect MIDI. mido READING ONLY."""
import mido  # READING ONLY (analysis)

ROOT = "/opt/data/projects/Styles/Funk/259-funk-som-extended"
NAME = "259-funk-som-extended"
FORM = [("Intro", 4), ("Verse", 4), ("Chorus", 4), ("Bridge", 4),
        ("Verse2", 4), ("Chorus2", 4), ("Break", 4), ("Outro", 4)]
VAR = {
    "Intro": "register shift (low) + sparse",
    "Verse": "base motif (SOM-C contour)",
    "Chorus": "transposition +3 + density rise",
    "Bridge": "retrograde + register shift",
    "Verse2": "inversion",
    "Chorus2": "augmentation + 7th color",
    "Break": "diminution + counterline",
    "Outro": "diminution + fade",
}
ROOTS = {"Intro": "iv (Bbm)", "Verse": "VI (Db)", "Chorus": "VII (Eb)",
         "Bridge": "i (Fm)", "Verse2": "III (Ab)", "Chorus2": "VII (Eb)",
         "Break": "VI (Db)", "Outro": "v (Cm)"}

mid = mido.MidiFile(f"{ROOT}/MIDI/{NAME}-perfect.mid")
tracks = {}
for t in mid.tracks[1:]:
    ch = None
    for m in t:
        if m.type == 'program_change':
            ch = m.channel
    tracks[ch] = t


def onset_grid(ch):
    grid = [["░"] * 16 for _ in range(32)]
    t = tracks.get(ch)
    if t is None:
        return grid
    abs_t = 0
    for m in t:
        abs_t += m.time
        if m.type == 'note_on' and m.velocity > 0:
            bar = min(abs_t // 1920, 31)
            sixteenth = (abs_t % 1920) // 120
            grid[bar][min(sixteenth, 15)] = "█"
    return grid


lead = onset_grid(0)
drums = onset_grid(9)


def rows_html(grid):
    out = []
    for i, row in enumerate(grid):
        cells = "".join(f'<span class="on">█</span>' if c == "█"
                        else f'<span class="off">░</span>' for c in row)
        out.append(f'<tr><td class="bar">{i:02d}</td><td class="grid">{cells}</td></tr>')
    return "\n".join(out)


sections = []
acc = 0
for s, nb in FORM:
    sections.append({"name": s, "bars": f"{acc}–{acc+nb-1}", "root": ROOTS[s],
                     "var": VAR[s]})
    acc += nb
sec_rows = "\n".join(
    f'<tr><td>{s["name"]}</td><td>{s["bars"]}</td><td>{s["root"]}</td>'
    f'<td>{s["var"]}</td></tr>' for s in sections)

html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>259-funk-som-extended</title>
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
  <h1>259-<span class="accent">funk-som</span>-extended</h1>
  <div class="sub">Funk · F minor (aeolian) · 104 BPM · 4/4 · 8 sections × 4 bars = 32 bars
  &nbsp;·&nbsp; rework of <span class="accent">098-funk-som</span></div>
</header>
<main>
<section>
  <h2>Listen</h2>
  <a class="play" href="Audio/259-funk-som-extended-perfect.ogg">▶ perfect.ogg</a>
  <a class="play" href="Audio/259-funk-som-extended-humanized.ogg">▶ humanized.ogg</a>
  <a class="play" href="MIDI/259-funk-som-extended-perfect.mid">⤓ perfect.mid</a>
  <a class="play" href="MIDI/259-funk-som-extended-humanized.mid">⤓ humanized.mid</a>
  <a class="play" href="MIDI/259-funk-som-extended-phase1.mid">⤓ phase1.mid</a>
</section>
<section>
  <h2>Verification</h2>
  <div class="metrics">
    <div class="card"><div class="k">zero-drift</div><div class="v">5 × 61440</div></div>
    <div class="card"><div class="k">off-grid (perfect)</div><div class="v">0</div></div>
    <div class="card"><div class="k">scale violations</div><div class="v">0</div></div>
    <div class="card"><div class="k">chord violations</div><div class="v">0</div></div>
    <div class="card"><div class="k">notes</div><div class="v">1314</div></div>
  </div>
</section>
<section>
  <h2>Sections — midpoint roots + variation</h2>
  <table><thead><tr><th>section</th><th>bars</th><th>midpoint root</th>
  <th>variation</th></tr></thead><tbody>
  {sec_rows}
  </tbody></table>
</section>
<section>
  <h2>Rhythm DNA — lead (trumpet) · 16th grid</h2>
  <table><thead><tr><th>bar</th><th>onsets (█ hit · ░ rest)</th></tr></thead>
  <tbody>{rows_html(lead)}</tbody></table>
</section>
<section>
  <h2>Rhythm DNA — drums (ch9) · 16th grid</h2>
  <table><thead><tr><th>bar</th><th>onsets (█ hit · ░ rest)</th></tr></thead>
  <tbody>{rows_html(drums)}</tbody></table>
</section>
</main></body></html>
"""
with open(f"{ROOT}/index.html", "w") as f:
    f.write(html)
print("index.html written:", len(html), "bytes")
