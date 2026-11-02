# -*- coding: utf-8 -*-
"""Smoke test for 2026-11-02 surveillance replications (run as script)."""
import sys
import numpy as np

ok = []

from sound.modular.modbox_cv import ModboxCV, ThreePhaseLFO, SampleHold
m = ModboxCV(); o = m.render(48000, 48000)
assert o["three_phase"].shape == (3, 48000)
ok.append(f"modbox_cv ok three_phase={o['three_phase'].shape}")

from sound.generators.drum_grid import DrumGridSequencer
s = DrumGridSequencer(bpm=120, steps=16)
s.fill_euclidean("kick", 4)
h = s.generate(seed=1)
assert len(h) > 0
ok.append(f"drum_grid ok {len(h)} hits")

from sound.generators.wave_melody import WaveMelodyGenerator
w = WaveMelodyGenerator(kind="saw", root=0, scale="pentatonic")
ev = w.generate(bars=2, seed=1)
assert len(ev) > 0
ok.append(f"wave_melody ok {len(ev)} events")

from sound.effects.spectral_sidechain import SpectralSidechain
sc = SpectralSidechain(sr=8000)
x = np.sin(2 * np.pi * 220 * np.arange(8000) / 8000) * 0.5
k = np.zeros(8000); k[:800] = np.sin(2 * np.pi * 55 * np.arange(800) / 800)
y = sc.process(x, k)
assert len(y) == 8000
ok.append(f"spectral_sidechain ok len={len(y)}")

from sound.synthesis.noise_resonator import NoiseResonatorVoice
v = NoiseResonatorVoice(noise_kind="white", n_resonators=2)
a = v.render_note(220.0, 0.1)
assert len(a) == 4410
ok.append(f"noise_resonator ok len={len(a)}")

from sound.synthesis.string_ensemble import CremaVoice
c = CremaVoice()
ch = c.render_chord([60, 64, 67], 0.3)
assert ch.shape == (2, 13230)
ok.append(f"string_ensemble ok {ch.shape}")

from sound.modular.patch_mutator import PatchMutator
pm = PatchMutator(seed=1)
_, r = pm.mutate({"a": 0.5, "b": 0.5}, strength=0.2, selectable={"a"})
assert len(r) >= 1
ok.append(f"patch_mutator ok {len(r)} changes")

# workflow SP_METHODS registration check
from workflows.musicom_workflow import SP_METHODS
ids = [f"SP-{i}" for i in range(135, 142)]
missing = [i for i in ids if i not in SP_METHODS]
assert not missing, f"missing registrations: {missing}"
ok.append(f"SP_METHODS ok: {len(SP_METHODS)} entries, SP-135..141 registered")

print("\n".join(ok))
print("ALL SMOKE TESTS PASSED")
