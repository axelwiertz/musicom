# -*- coding: utf-8 -*-
"""Summary + audio provenance sidecars for 094 (READ-ONLY over the artifacts)."""
import json
import os

from structures import MusicUnit  # noqa: F401 (compliant-import marker)
from workflows.provenance import write_provenance, AI_ASSISTED
from utilities.env import soundfont_path

PROJ = ("/opt/data/repos/musicom/projects/Styles/African/"
        "094-african-hierarchical-diffusion")
A, M = os.path.join(PROJ, "Analysis"), os.path.join(PROJ, "MIDI")

concept = json.load(open(os.path.join(A, "concept.json")))
audit = json.load(open(os.path.join(A, "audit.json")))
stats = json.load(open(os.path.join(A, "render_stats.json")))
tonal = json.load(open(os.path.join(A, "tonal_check.json")))
info = json.load(open(os.path.join(A, "render_info.json")))

summary = {
    "project": "094-african-hierarchical-diffusion",
    "date": "2026-09-12",
    "style": "African (Mande / djembe drum-ensemble idiom)",
    "layer": "concrete",
    "method": {"id": "010", "name": "Hierarchical Diffusion",
               "implementation": "generators.chain.MarkovChainGenerator",
               "levels": ["L4 section (6 states)", "L3 bar (3 states)",
                          "L2 beat (3 states)", "L1 onset expansion (1/2/3-4 hits)"]},
    "key": "A dorian",
    "bpm": 112,
    "form": concept["sections"],
    "bars": 24,
    "grid": "16th (120 ticks @ 480 TPB)",
    "progression": concept["progression"],
    "voices": concept["voices"],
    "grid_audit": {"off_16th": audit["grid_phase2"]["total_off_16th"],
                   "notes": audit["grid_phase2"]["total_notes"],
                   "verdict": audit["verdict_grid"]},
    "harmony_audit": {"verdict": audit["verdict_harmony"],
                      "per_voice": [{k: r[k] for k in
                                     ("voice", "out_of_scale", "out_of_chord")}
                                    for r in audit["harmony_phase2"]]},
    "range_audit": {"verdict": audit["verdict_range"]},
    "zero_drift": {"phase1": audit["zero_drift_phase1"]["drift_ok"],
                   "phase2": audit["zero_drift_phase2"]["drift_ok"],
                   "max_end_ticks": audit["zero_drift_phase2"]["max_end"]},
    "phase1_fingerprint": {"off_16th": audit["phase1_fingerprint"]["total_off_16th"],
                           "notes": audit["phase1_fingerprint"]["total_notes"]},
    "audio": {
        "phase2": {"duration_s": stats["phase2"]["duration_s"],
                   "peak": stats["phase2"]["peak"],
                   "silence_ratio": stats["phase2"]["silence_ratio"],
                   "silent_seconds": stats["phase2"]["silent_seconds"],
                   "verdict": stats["phase2"]["verdict_silence"]},
        "phase1": {"duration_s": stats["phase1"]["duration_s"],
                   "peak": stats["phase1"]["peak"],
                   "silence_ratio": stats["phase1"]["silence_ratio"],
                   "verdict": stats["phase1"]["verdict_silence"]},
    },
    "tonal": {"phase1_fundamentals_present":
              "%d/%d" % (tonal["phase1"]["fundamental_present"],
                         tonal["phase1"]["notes_tested"]),
              "phase2_windows_pitched":
              "%d/%d" % (tonal["phase2"]["windows_pitched"],
                         tonal["phase2"]["windows"]),
              "melodic_in_key_mass": tonal["chroma"]["in_key_mass"],
              "track_pc_off_key": {r["track"]: r["off_key"]
                                   for r in tonal["track_pc_audit"]
                                   if not r["is_percussion"]}},
    "fixes_applied": [
        "UnitMatrix cell rebase: events carry ABSOLUTE ticks but each cell is a "
        "section-relative coordinate space; without the `slice_section` rebase "
        "every event in sections > 0 clamped to SECTION_TICKS-10 -> 124 off-grid "
        "onsets + collapsed note collisions. After fix: 0 off-grid, 1433 notes.",
        "Bass octave doublings rewired to real chord tones (was root+12 blindly "
        "-> 6 out-of-chord); range widened to 33-52 so the diatonic octave is "
        "the chord tone. After fix: 0 out-of-chord.",
    ],
    "artifacts": {},
}
for p in ("MIDI/094-african-hierarchical-diffusion.mid",
          "MIDI/094-african-hierarchical-diffusion-phase1.mid",
          "Audio/094-african-hierarchical-diffusion.ogg",
          "Audio/094-african-hierarchical-diffusion-phase1.ogg"):
    fp = os.path.join(PROJ, p)
    if os.path.exists(fp):
        summary["artifacts"][p] = os.path.getsize(fp)

with open(os.path.join(A, "summary.json"), "w") as f:
    json.dump(summary, f, indent=2)
print("summary.json written")

for label in ("phase2", "phase1"):
    base = ("094-african-hierarchical-diffusion" if label == "phase2"
            else "094-african-hierarchical-diffusion-phase1")
    for ext in ("ogg",):
        p = os.path.join(PROJ, "Audio", base + "." + ext)
        if os.path.exists(p):
            write_provenance(p, classification=AI_ASSISTED,
                             generator="workflows.musicom_workflow.produce (SP-001 FluidSynth)",
                             parameters={"phase": 1 if label == "phase1" else 2,
                                         "bpm": concept["bpm"],
                                         "soundfont": os.path.basename(soundfont_path()),
                                         "peak_after_norm": info[label]["peak_after_norm"],
                                         "silence_ratio": stats[label]["silence_ratio"],
                                         "format": "Opus 48k voip OGG"},
                             notes="FluidSynth CLI render of the 094 MIDI -> ffmpeg "
                                   "volume normalisation to -1 dBFS -> Opus OGG.")
            print("provenance:", os.path.basename(p))
