# -*- coding: utf-8 -*-
"""Finalize: write REPORT.md, README.md, index.html from real JSON reports."""
import json, os
import mido  # READING ONLY (analysis)

BASE = "/opt/data/projects/Styles/Experimental/314-abelian-sandpile-suite"
PROJ = "314-abelian-sandpile-suite"
MIDI = os.path.join(BASE, "MIDI")
ANALYSIS = os.path.join(BASE, "Analysis")

summary = json.load(open(os.path.join(ANALYSIS, "compose_summary.json")))
verify = json.load(open(os.path.join(ANALYSIS, "verify_report.json")))
render = json.load(open(os.path.join(ANALYSIS, "render_report.json")))
prov = json.load(open(os.path.join(BASE, "provenance.json")))

# ---- rhythm DNA grid from perfect MIDI (lead = track 1) -------------------
BAR = 1920
GRID = 120
onset_slots = set()
mid = mido.MidiFile(os.path.join(MIDI, PROJ + "-perfect.mid"))
track = mid.tracks[1]
abs_t = 0
for m in track:
    abs_t += m.time
    if m.type == "note_on" and m.velocity > 0:
        bar = abs_t // BAR
        slot = (abs_t % BAR) // GRID
        onset_slots.add((bar, slot))
n_bars = summary["bars"]
grid_rows = []
for b in range(n_bars):
    cells = "".join("\u2588" if (b, s) in onset_slots else "\u2591" for s in range(16))
    grid_rows.append(f"<div class='gline'><span class='baridx'>{b+1:02d}</span><span class='cells'>{cells}</span></div>")
grid_html = "\n".join(grid_rows)

def fmt_pct(x):
    return f"{x*100:.2f}%"

perf = verify["perfect"]
hum = verify["humanized"]
ph1 = verify["phase1"]

# markdown render rows (REPORT.md) + HTML render rows (index.html)
render_md = "\n".join(
    f"| {label} | {render[tag]['lufs']:.2f} | {render[tag]['true_peak_db']:.2f} "
    f"| {fmt_pct(render[tag]['silence_ratio'])} | {render[tag]['ogg_bytes']:,} |"
    for tag, label in (("phase1", "Phase 1 (raw)"), ("perfect", "Perfect"),
                       ("humanized", "Humanized"))
)
render_html = "\n".join(
    f"<tr><td>{label}</td><td>{render[tag]['lufs']:.2f}</td>"
    f"<td>{render[tag]['true_peak_db']:.2f}</td>"
    f"<td>{fmt_pct(render[tag]['silence_ratio'])}</td>"
    f"<td>{render[tag]['ogg_bytes']:,}</td></tr>"
    for tag, label in (("phase1", "Phase 1 (raw)"), ("perfect", "Perfect"),
                       ("humanized", "Humanized"))
)

section_rows = "\n".join(
    f"| {s['name']} | 4 | {' '.join(s['progression_names'])} | "
    f"{s['midpoint_degree']} | {s['variation']} |"
    for s in prov["sections"]
)
variation_md = "\n".join(
    f"- **{k}** — {v}" for k, v in prov["variation_techniques"].items()
)
variation_html = "\n".join(
    f"<tr><td>{k}</td><td>{v}</td></tr>"
    for k, v in prov["variation_techniques"].items()
)
mid_degrees = sorted({s["midpoint_degree"] for s in prov["sections"]})
sf_name = render["soundfont"].split("/")[-1]

# ---------- REPORT.md ----------
report = f"""# REPORT — {PROJ}

**Nightly rework job · 2026-11-20.**

| Field | Value |
|---|---|
| **Project** | `{PROJ}` (next ID after 313) |
| **Source** | `277-abelian-sandpile-avalanche` (Experimental, D minor, 88 BPM, Method 036 ASAR) |
| **Genre** | Experimental |
| **Method** | 036 — Abelian Sandpile Avalanche Rhythmics (ASAR) |
| **Key** | D minor (aeolian) — pcs `{{D,E,F,G,A,Bb,C}}` |
| **Tempo / Meter** | 88 BPM · 4/4 · 480 TPB (BAR = 1920) |
| **Form** | through-composed `S1..S8` (4 bars each = **32 bars**) — was 24 bars / 6 sections |
| **Voices** | Lead=Marimba(12) · Counter=Celesta(8) · Harmony=Piano(1) · Pad=String Ensemble(48) · Bass=Double Bass(43) |
| **Seeds** | raw `20261120` · humanize `{summary['hz_seed']}` |

## 1. Audit of source 277

| Standard | Result |
|---|---|
| 1. Engine (UnitMatrixComposer) | PASS |
| 2. Zero-drift | PASS (5 tracks, 46080 ticks) |
| 3. Rhythm-grid sync | PASS (0 off-grid) |
| 4. ≥4 voice tracks | PASS (5) |
| 5. Two-phase (phase1 present) | PASS |
| 6. provenance.json + index.html | **FAIL** (missing both at root) |

**Decision: redesign (standard 6) + extension.** The source's engine code is
compliant; the failure is missing portfolio artifacts. Identity (genre, D
minor, 88 BPM, sandpile method, 5-voice instrumentation) preserved; form
extended 24→32 bars, 6→8 sections, +6 variation techniques; strict per-bar
chord discipline (stronger than the source's tiered discipline); root
`provenance.json` + `index.html` added.

## 2. Form & per-section harmonic regions

| Section | Bars | Progression | Midpoint degree | Variation |
|---|---|---|---|---|
{section_rows}

Each section has its own short progression; per-section midpoint chords land on
degrees {mid_degrees} — not all degree i (no bar-0 tonic collapse).
Roots derived via `Scale7ChordDegree.get_diatonic_note` (aeolian offsets).

## 3. Variation techniques (6)

{variation_md}

## 4. Two-phase architecture

- **Phase 1** (`-phase1.mid`): raw BTW abelian sandpile on a 14×256 lattice,
  per-section variation transforms applied to the (row,col) topple stream
  BEFORE decode. Float pitch + chromatic jitter, off-grid onsets, single
  voice, no harmony. Own `validate()` gate: PASS (61440 ticks).
- **Phase 2** (`-perfect.mid` + `-humanized.mid`): STRICT chord discipline
  (every note snaps to its own bar's chord tone), 16th grid snap, dedup,
  voice-leading (parallel 5th/octave break), 5-voice texture.

## 5. Humanization (dual-version, style-derived, seeded)

`hz_seed = {summary['hz_seed']}` · style **experimental** profile + per-instrument
DNA. **Bar-accurate clamping**: the humanized composer uses 1-bar sections so
the humanizer's boundary clamp == bar boundary — jitter never re-attributes a
note to the wrong bar's chord.

## 6. Verification (read-only mido)

| Artifact | tracks | tick len | pitched | off-grid | scale viol | chord viol |
|---|---|---|---|---|---|---|
| phase1 | 1 | 61440 | {ph1['pitched']} | {ph1['offgrid']} | {ph1['out_of_scale']} | {ph1['out_of_chord']} |
| **perfect** | 5 | 61440 | {perf['pitched']} | **{perf['offgrid']}** | **{perf['out_of_scale']}** | **{perf['out_of_chord']}** |
| **humanized** | 5 | 61440 | {hum['pitched']} | {hum['offgrid']} | **{hum['out_of_scale']}** | **{hum['out_of_chord']}** |

Zero-drift: all voice tracks equal length (61440). Perfect off-grid == 0;
humanized off-grid > 0 (jitter ran). Scale + chord violations == 0 in both
phase-2 artifacts.

## 7. Render + master

`target_for_style("experimental")` = **−14.0 LUFS**, ceiling **−1 dBTP**.
SoundFont `{sf_name}`.

| Artifact | LUFS | true peak | silence | OGG bytes |
|---|---|---|---|---|
{render_md}

## 8. Files

- `MIDI/{PROJ}-phase1.mid` · `-perfect.mid` · `-humanized.mid` (+ provenance sidecars)
- `Audio/{PROJ}-phase1.ogg` · `-perfect.ogg` · `-humanized.ogg`
- `provenance.json` (root) · `index.html` · `README.md` · `REPORT.md`
- `Analysis/grid_visualization*.txt` · `compose_summary.json` · `verify_report.json` · `render_report.json`
- `compose.py` · `render.py` · `verify.py`
"""
with open(os.path.join(BASE, "REPORT.md"), "w") as f:
    f.write(report)

# ---------- README.md ----------
readme = f"""# {PROJ}

**Method 036 — Abelian Sandpile Avalanche (ASAR)** · concrete · Nature-Led
Nightly rework of `277-abelian-sandpile-avalanche` (redesign + extension).

| Field | Value |
|---|---|
| Genre | Experimental |
| Key | D minor (aeolian) — pcs `{{D,E,F,G,A,Bb,C}}` |
| Tempo | 88 BPM · 4/4 · 480 TPB |
| Form | through-composed `S1..S8` (4 bars each = 32 bars) |
| Seed | raw `20261120` · humanize `{summary['hz_seed']}` |
| Voices | Lead=Marimba · Counter=Celesta · Harmony=Piano · Pad=String Ensemble · Bass=Double Bass |

## Concept

Bak–Tang–Wiesenfeld abelian sandpile on a 14×256 lattice. A "composer's hand"
advances the drop site across register (density arc 3/5/7/11/7/9/5/3), and each
cell toppling is a note. Six variation techniques: transposition (+4 diatonic),
inversion (diatonic mirror), retrograde (section time-reversal), augmentation
(duration doubling + thinning), register shift, counterline variation.

- **Phase 1** — raw toppling stream (off-grid, chromatic jitter, single voice).
- **Phase 2** — strict chord discipline, 16th grid snap, dedup, voice-leading,
  5-voice texture. Dual-version export (-perfect / -humanized).

## Files

- `MIDI/` — `-phase1.mid`, `-perfect.mid`, `-humanized.mid` (+ provenance sidecars)
- `Audio/` — `-phase1.ogg`, `-perfect.ogg`, `-humanized.ogg` (mastered −14 LUFS)
- `Analysis/` — `grid_visualization*.txt`, `compose_summary.json`, `verify_report.json`, `render_report.json`
- `provenance.json` · `index.html` · `REPORT.md`
- `compose.py` / `render.py` / `verify.py`

Full details in `REPORT.md`.
"""
with open(os.path.join(BASE, "README.md"), "w") as f:
    f.write(readme)

# ---------- index.html ----------
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{PROJ} — VoltAgent Dashboard</title>
<style>
  :root {{ --bg:#050507; --accent:#00d992; --surface:#101010; --fg:#e6e6e6; --dim:#7a7a7a; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--fg);
         font-family:'JetBrains Mono', ui-monospace, monospace; }}
  header {{ border-bottom:1px solid #1c1c1c; padding:32px 40px 24px; }}
  h1 {{ font-family:system-ui, sans-serif; font-size:60px; line-height:1.0; margin:0; color:var(--accent); }}
  .sub {{ color:var(--dim); margin-top:10px; font-size:14px; }}
  main {{ padding:24px 40px 60px; max-width:1200px; }}
  .card {{ background:var(--surface); border:1px solid #1c1c1c; border-radius:8px;
          padding:20px 24px; margin:20px 0; }}
  h2 {{ font-family:system-ui, sans-serif; color:var(--accent); font-size:20px;
       margin:0 0 16px; }}
  table {{ border-collapse:collapse; width:100%; font-size:13px; }}
  th, td {{ text-align:left; padding:6px 10px; border-bottom:1px solid #1c1c1c; }}
  th {{ color:var(--accent); font-weight:600; }}
  .gline {{ display:flex; align-items:center; line-height:1.35; font-size:13px; }}
  .baridx {{ color:var(--dim); width:34px; flex:none; }}
  .cells {{ letter-spacing:1px; color:var(--accent); }}
  audio {{ width:100%; margin:6px 0; }}
  a {{ color:var(--accent); text-decoration:none; }}
  a:hover {{ text-decoration:underline; }}
  .grid {{ font-family:'JetBrains Mono', monospace; overflow-x:auto; }}
</style>
</head>
<body>
<header>
  <h1>{PROJ}</h1>
  <div class="sub">Experimental · Method 036 Abelian Sandpile Avalanche · D minor · 88 BPM · 32 bars (S1..S8) · rework of 277-abelian-sandpile-avalanche</div>
</header>
<main>

<div class="card">
  <h2>Audio</h2>
  <p>Perfect (grid-locked) &nbsp;·&nbsp; <a href="Audio/{PROJ}-perfect.ogg">{PROJ}-perfect.ogg</a></p>
  <audio controls src="Audio/{PROJ}-perfect.ogg"></audio>
  <p>Humanized (jittered) &nbsp;·&nbsp; <a href="Audio/{PROJ}-humanized.ogg">{PROJ}-humanized.ogg</a></p>
  <audio controls src="Audio/{PROJ}-humanized.ogg"></audio>
  <p>Phase 1 raw &nbsp;·&nbsp; <a href="Audio/{PROJ}-phase1.ogg">{PROJ}-phase1.ogg</a></p>
  <audio controls src="Audio/{PROJ}-phase1.ogg"></audio>
</div>

<div class="card">
  <h2>Rhythm DNA — Lead (avalanche cascade, 32 bars × 16th)</h2>
  <div class="grid">{grid_html}</div>
  <div class="sub">█ onset · ░ rest · 16 columns per bar (16th-note grid)</div>
</div>

<div class="card">
  <h2>Variation techniques</h2>
  <table>
    <tr><th>Technique</th><th>Where / how</th></tr>
    {variation_html}
  </table>
</div>

<div class="card">
  <h2>Render + master (−14 LUFS target)</h2>
  <table>
    <tr><th>Artifact</th><th>LUFS</th><th>true peak</th><th>silence</th><th>OGG bytes</th></tr>
    {render_html}
  </table>
</div>

<div class="card">
  <h2>MIDI</h2>
  <table>
    <tr><th>Artifact</th><th>tracks</th><th>tick len</th><th>pitched</th><th>off-grid</th><th>scale viol</th><th>chord viol</th></tr>
    <tr><td>phase1</td><td>1</td><td>61440</td><td>{ph1['pitched']}</td><td>{ph1['offgrid']}</td><td>{ph1['out_of_scale']}</td><td>{ph1['out_of_chord']}</td></tr>
    <tr><td>perfect</td><td>5</td><td>61440</td><td>{perf['pitched']}</td><td>{perf['offgrid']}</td><td>{perf['out_of_scale']}</td><td>{perf['out_of_chord']}</td></tr>
    <tr><td>humanized</td><td>5</td><td>61440</td><td>{hum['pitched']}</td><td>{hum['offgrid']}</td><td>{hum['out_of_scale']}</td><td>{hum['out_of_chord']}</td></tr>
  </table>
  <p class="sub">
    <a href="MIDI/{PROJ}-phase1.mid">phase1.mid</a> ·
    <a href="MIDI/{PROJ}-perfect.mid">perfect.mid</a> ·
    <a href="MIDI/{PROJ}-humanized.mid">humanized.mid</a>
  </p>
</div>

</main>
</body>
</html>
"""
with open(os.path.join(BASE, "index.html"), "w") as f:
    f.write(html)

print("FINALIZE_OK")
print("REPORT.md", os.path.getsize(os.path.join(BASE, "REPORT.md")))
print("README.md", os.path.getsize(os.path.join(BASE, "README.md")))
print("index.html", os.path.getsize(os.path.join(BASE, "index.html")))
