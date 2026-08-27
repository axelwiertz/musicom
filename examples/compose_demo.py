# -*- coding: utf-8 -*-
"""Compose + produce demo — the musicom workflow in one file.

Shows the design → realization loop:
    compose(style="pop") -> validated MIDI + provenance
    produce(midi, "SP-001") -> SoundFont WAV + OGG
    produce(midi, "SP-011") -> Karplus-Strong WAV + OGG

Run:
    /opt/data/micromamba/envs/musicom/bin/python examples/compose_demo.py
"""

from workflows.musicom_workflow import compose, produce, method_table, sp_method_table

if __name__ == "__main__":
    print("=== musicom workflow demo ===")

    # 1. DESIGN: compose a pop framework (I-V-vi-IV, 5 voices, 5 sections)
    r = compose(style="pop", key="C", bpm=120)
    print(f"\n[compose] midi:      {r.midi_path}")
    print(f"[compose] provenance: {r.provenance_path}")
    print(f"[compose] method:    {r.method} (Skeleton-First)")

    # 2. REALIZATION: two production methods on the same MIDI
    p1 = produce(r.midi_path, method="SP-001")
    print(f"\n[produce SP-001] wav: {p1.wav_path}")
    print(f"[produce SP-001] ogg: {p1.ogg_path}")

    p2 = produce(r.midi_path, method="SP-011")
    print(f"\n[produce SP-011] wav: {p2.wav_path}  ({p2.info['note_count']} notes, {p2.info['output_seconds']}s)")
    print(f"[produce SP-011] ogg: {p2.ogg_path}")

    # 3. the auto-generated tables (these should land in docs/)
    print("\n=== methods available ===")
    print(method_table())
    print("\n=== production methods available ===")
    print(sp_method_table())
    print("\nDONE")
