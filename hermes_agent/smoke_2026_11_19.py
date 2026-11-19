"""Import + smoke test for the 2026-11-19 surveillance modules (SP-161..167)."""
import numpy as np

from sound.effects.multiband_freq_shifter import MultibandFreqShifter
from sound.generators.fm_groovebox import FMGroovebox, FMPatch
from sound.synthesis.tb303_circuit import TB303Circuit
from sound.generators.multi_playhead_seq import MultiPlayheadSequencer
from sound.effects.upward_dynamics import UpwardDynamics
from sound.effects.structural_split_eq import StructuralSplitEQ
from sound.generators.formula_drumkit import FormulaDrumKit
from workflows.musicom_workflow import SP_METHODS

sr = 22050
x = 0.3 * np.sin(2 * np.pi * 220 * np.arange(sr) / sr)

# SP-161
sh = MultibandFreqShifter(sr, shifts_hz=(0.0, 40.0, -70.0),
                          sideband=("up", "both", "down"))
sh.set_anchor(57)
y161 = sh.process(x)
print(f"SP-161 multiband_freq_shifter  out={y161.shape} rms={np.sqrt(np.mean(y161**2)):.4f} "
      f"shift={sh.musical_shift(4,'major'):+.1f}Hz")

# SP-162
gb = FMGroovebox(bpm=120, sample_rate=sr)
tr = gb.add_track("b", FMPatch(algorithm=2, ratios=(1, 2, 3, 1), index=3.5))
for i, m in enumerate([36, 43, 41, 48]):
    tr.set(i * 4, midi=m, vel=100, ratchet=2 if i == 2 else 1)
ev = gb.generate(bars=1, seed=1)
a162 = gb.render(ev)
print(f"SP-162 fm_groovebox          events={len(ev)} audio={a162.size} rms={np.sqrt(np.mean(a162**2)):.4f}")

# SP-163
tb = TB303Circuit(sr, quality="economy", cutoff=300, resonance=0.8)
a163 = tb.render_pattern([{"midi": 36}, {"midi": 43, "accent": True},
                          {"midi": None}, {"midi": 46, "slide": True}], bpm=130)
print(f"SP-163 tb303_circuit         audio={a163.size} peak={np.max(np.abs(a163)):.3f}")

# SP-164
seq = MultiPlayheadSequencer(bpm=120)
tk = seq.add_track("pool", steps=8)
for i in range(8):
    tk.set_step(i, midi=48 + i * 2)
tk.add_head(length=8, division=4, output="a")
tk.add_head(length=5, direction="bwd", division=3, output="b", seq_type="EUCLID")
ev164 = seq.generate(bars=2)
print(f"SP-164 multi_playhead_seq    events={len(ev164)} smf={len(seq.to_midi_bytes(ev164))}B")

# SP-165
ud = UpwardDynamics(sr, crossover_hz=800)
y165 = ud.process(0.03 * x)
print(f"SP-165 upward_dynamics       out={y165.shape} rms={np.sqrt(np.mean(y165**2)):.5f}")

# SP-166
sq = StructuralSplitEQ(sr)
sq.tonal_gains = np.array([-2, 0, 1, 0, 0, 2, 0, 0])
tr166, to166 = sq.splitter.split(x)
y166 = sq.process(x)
print(f"SP-166 structural_split_eq   split_err={np.max(np.abs(tr166+to166-x)):.2e} out={y166.shape}")

# SP-167
kit = FormulaDrumKit.from_kit("OM", sample_rate=sr, seed=2)
y167 = kit.hit("kick", 0.9)
print(f"SP-167 formula_drumkit       kick={y167.size} peak={np.max(np.abs(y167)):.3f}")

missing = [k for k in ("SP-161", "SP-162", "SP-163", "SP-164", "SP-165",
                       "SP-166", "SP-167") if k not in SP_METHODS]
print("registry entries present:", not missing, "| total SP methods:", len(SP_METHODS))
import importlib
for k in ("SP-161", "SP-162", "SP-163", "SP-164", "SP-165", "SP-166", "SP-167"):
    importlib.import_module(SP_METHODS[k][0])
print("all 7 module paths importable via SP_METHODS: True")
