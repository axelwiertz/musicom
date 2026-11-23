"""Import + smoke test for 2026-11-23 gear replications (SP-168..171)."""
import numpy as np

from workflows.musicom_workflow import SP_METHODS
for k in ("SP-168", "SP-169", "SP-170", "SP-171"):
    assert k in SP_METHODS, k
    print(f"registered {k}: {SP_METHODS[k][0]}")

# SP-168 virus_va
from sound.synthesis.virus_va import VirusVA, VirusOsc, VirusVoice
va = VirusVA(sample_rate=22050, max_voices=4, unison=2, seed=11)
out = va.play([60, 64, 67], dur=0.5)
assert out.shape == (11025, 2) and np.all(np.isfinite(out))
print(f"virus_va: VirusVA ok, out={out.shape}, peak={np.abs(out).max():.3f}")

# SP-169 paraphonic_voice
from sound.synthesis.paraphonic_voice import ParaphonicVoice, LadderFilter
pv = ParaphonicVoice(sample_rate=22050, mode="four", mk=2, seed=5)
o = pv.play([60, 64, 67], dur=0.5)
assert o.shape == (11025, 2) and np.all(np.isfinite(o))
print(f"paraphonic_voice: ParaphonicVoice ok, out={o.shape}, peak={np.abs(o).max():.3f}")

# SP-170 wavetable_drums
from sound.generators.wavetable_drums import WavetableDrumMachine, build_wavetable
wt = build_wavetable("metal")
assert wt.shape == (32, 256)
wd = WavetableDrumMachine(sample_rate=22050, bpm=120, seed=4)
wd.add_track("kick", {"table1": "saw", "cutoff": 800.0, "amp_decay": 16.0})
pattern = {"bpm": 120, "steps": 16, "tracks": {
    "kick": {"steps": [{"on": 1, "vel": 0.9} if s % 4 == 0 else None
                       for s in range(16)]}}}
audio, events = wd.render_pattern(pattern)
assert audio.ndim == 2 and np.all(np.isfinite(audio)) and len(events) == 4
print(f"wavetable_drums: WavetableDrumMachine ok, events={len(events)}, audio={audio.shape}")

# SP-171 drum_replacer
from sound.effects.drum_replacer import DrumReplacer, detect_hits
rng = np.random.default_rng(3)
sr = 22050
track = np.zeros(sr)
for k in range(4):
    idx = int((0.2 + 0.24 * k) * sr)
    t = np.arange(int(0.08 * sr)) / sr
    track[idx:idx + len(t)] += np.sin(2 * np.pi * 180 * t) * np.exp(-t * 40)
hits = detect_hits(track, sr, threshold=0.08, retrigger_ms=60)
assert len(hits) == 4, len(hits)
s = np.sin(2 * np.pi * 200 * t) * np.exp(-t * 30)
dr = DrumReplacer(sample_rate=sr, samples={"snare": s})
rep = dr.process(track, threshold=0.08, retrigger_ms=60, wet=1.0)
assert rep.shape == track.shape and np.all(np.isfinite(rep))
print(f"drum_replacer: DrumReplacer ok, hits={len(hits)}, replaced peak={np.abs(rep).max():.3f}")

print("SMOKE OK")
