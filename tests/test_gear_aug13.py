"""Tests for Aug 13 2026 surveillance gear replication.

Covers:
- Batch A: ScaleQuantizer/ProbabilityEngine/ScaleModeMIDI (Synterra),
  MidiUtils/MicrotonalExporter (KHORA pitch bend), DiceVariation/ParamScope
  (Karst dice), MathModulator/StepSequencer24/MathPatch (Altitude),
  FDN reverb (Rev Ocean), Multiband (Rumble)
- Batch B: VoiceAllocator/ModulationMatrix (ECHON 6), PolyrhythmicArp
  (Memory V), HaasDelay/BinauralSynth (DMNO), Wavefolder/LowpassGate/
  WestCoastVoice (Obsidian), QuantizeModulator/ModRouter/QuantizeChain
  (Radical1), PatchLoader/PatchBuilder (Karst JSON patches)
"""

import numpy as np
import pytest

SR = 44100


# --------------------------------------------------------------------------- #
# Synterra — scale quantizer + probability engine
# --------------------------------------------------------------------------- #
class TestScaleQuantizer:
    def test_imports(self):
        from sound.synthesis import ScaleQuantizer, ProbabilityEngine, ScaleModeMIDI
        assert ScaleQuantizer is not None
        assert ProbabilityEngine is not None
        assert ScaleModeMIDI is not None

    def test_quantize_to_scale(self):
        from sound.synthesis import ScaleQuantizer
        sq = ScaleQuantizer(root=60, scale="major")
        for v in range(48, 84):
            out = sq.quantize(v)
            assert sq.is_in_scale(out)
            assert abs(out - v) <= 2

    def test_quantize_matches_known(self):
        from sound.synthesis import ScaleQuantizer
        sq = ScaleQuantizer(root=60, scale="major")
        assert sq.quantize(63) == 64  # D# -> E (nearest major member, tie->higher)
        assert sq.quantize(62) == 62  # D IS a major scale member
        assert sq.quantize(61) == 62  # C# equidistant C/D -> tie-break higher

    def test_probability_engine_scale_only(self):
        from sound.synthesis import ScaleQuantizer, ProbabilityEngine
        sq = ScaleQuantizer(root=60, scale="pentatonic")
        pe = ProbabilityEngine(scale_quantizer=sq, seed=42)
        notes = pe.generate(32)
        assert len(notes) == 32
        for n in notes:
            assert sq.is_in_scale(n)

    def test_probability_engine_deterministic_seed(self):
        from sound.synthesis import ScaleQuantizer, ProbabilityEngine
        sq = ScaleQuantizer(root=60, scale="major")
        a = ProbabilityEngine(scale_quantizer=sq, seed=7).generate(16)
        b = ProbabilityEngine(scale_quantizer=sq, seed=7).generate(16)
        assert a == b

    def test_scale_mode_midi(self):
        from sound.synthesis import ScaleModeMIDI
        sm = ScaleModeMIDI()
        sm.add_reference_pitches([60, 64, 67])
        assert sm.constrain(61) == 60
        assert sm.is_allowed(64)


# --------------------------------------------------------------------------- #
# KHORA — microtonal MIDI utils
# --------------------------------------------------------------------------- #
class TestMidiUtils:
    def test_cents_to_bend_center(self):
        from sound.utils import MidiUtils
        assert MidiUtils.cents_to_pitch_bend(0.0) == 0

    def test_cents_to_bend_positive(self):
        from sound.utils import MidiUtils
        bend = MidiUtils.cents_to_pitch_bend(50.0)  # +50 cents within ±200
        assert 0 < bend < 8191

    def test_frequency_to_pitch_bend(self):
        from sound.utils import MidiUtils
        note, bend = MidiUtils.frequency_to_pitch_bend(440.0)
        assert note == 69
        assert bend == 0  # exact 12-EDO

    def test_microtonal_exporter_writes(self, tmp_path):
        import mido
        from sound.utils import MicrotonalExporter
        exporter = MicrotonalExporter()
        notes = [
            {"pitch": 69, "start_tick": 0, "duration_ticks": 480, "bend_cents": 25.0},
            {"pitch": 72, "start_tick": 480, "duration_ticks": 480, "bend_cents": -10.0},
        ]
        path = str(tmp_path / "micro.mid")
        exporter.build_midi_with_pitch_bends(notes, path)
        mid = mido.MidiFile(path)
        # single track: tempo meta + all events
        bends = [m for m in mid.tracks[0] if m.type == "pitchwheel"]
        assert len(bends) >= 2  # bends + resets
        note_ons = [m for m in mid.tracks[0] if m.type == "note_on"]
        assert len(note_ons) == 2


# --------------------------------------------------------------------------- #
# Karst — dice variation + param scopes
# --------------------------------------------------------------------------- #
class TestDiceVariation:
    def test_lock_prevents_variation(self):
        from sound.generators import DiceVariation
        dv = DiceVariation(variation_probability=1.0, seed=1)
        dv.lock("cutoff")
        out = dv.vary({"cutoff": 2000, "resonance": 0.5})
        assert out["cutoff"] == 2000  # locked

    def test_variation_changes(self):
        from sound.generators import DiceVariation
        dv = DiceVariation(variation_probability=1.0, seed=3)
        out = dv.vary({"resonance": 0.5})
        assert out["resonance"] != 0.5

    def test_unlock(self):
        from sound.generators import DiceVariation
        dv = DiceVariation(variation_probability=1.0, seed=5)
        dv.lock("x")
        dv.unlock("x")
        assert not dv.is_locked("x")

    def test_param_scope(self):
        from sound.generators import ParamScope
        ps = ParamScope()
        ps.add_scope("lead", {"cutoff": 3000})
        ps.activate("lead")
        assert ps.active() == {"cutoff": 3000}
        ps.set("lead", {"cutoff": 5000})
        assert ps.get("lead") == {"cutoff": 5000}


# --------------------------------------------------------------------------- #
# Altitude — math modulators + 24-step sequencer
# --------------------------------------------------------------------------- #
class TestMathModulator:
    def test_process_nonzero(self):
        from sound.modular import MathModulator
        m = MathModulator("sin(2*pi*2*t)", rate=2.0)
        sig = m.process(4410)
        assert len(sig) == 4410
        assert np.max(np.abs(sig)) > 0.1

    def test_invalid_expr_zeros(self):
        from sound.modular import MathModulator
        m = MathModulator("undefined_func(t)")
        sig = m.process(100)
        assert np.all(sig == 0.0)

    def test_step_sequencer(self):
        from sound.modular import StepSequencer24
        seq = StepSequencer24(steps=24)
        seq.set_pattern([1.0] + [0.0] * 23)
        assert seq.get_step(0) == 1.0
        assert seq.get_step(24) == 1.0  # wraps

    def test_math_patch(self):
        from sound.modular import MathModulator, StepSequencer24, MathPatch
        patch = MathPatch(SR)
        lfo = MathModulator("sin(2*pi*1*t)")
        seq = StepSequencer24(24)
        seq.set_pattern([0.5] * 24)
        patch.add_source("lfo", lfo)
        patch.add_source("seq", seq)
        patch.modulate("filter", "lfo", 0.5)
        patch.modulate("filter", "seq", 0.2)
        out = patch.render(0.1)
        assert "filter" in out
        assert len(out["filter"]) == int(0.1 * SR)


# --------------------------------------------------------------------------- #
# Rev Ocean — FDN reverb
# --------------------------------------------------------------------------- #
class TestFDNReverb:
    def test_imports(self):
        from sound.effects import FDN
        assert FDN is not None

    def test_changes_audio(self):
        from sound.effects import FDN
        fdn = FDN(SR)
        t = np.linspace(0, 0.2, int(0.2 * SR))
        audio = np.sin(2 * np.pi * 440 * t)
        out = fdn.process(audio)
        assert len(out) == len(audio)
        assert not np.allclose(out, audio)

    def test_freeze_extends_tail(self):
        from sound.effects import FDN
        fdn = FDN(SR)
        t = np.linspace(0, 0.1, int(0.1 * SR))
        audio = np.zeros_like(t)
        audio[0] = 1.0  # impulse
        normal = fdn.process(audio)
        fdn2 = FDN(SR)
        fdn2.set(freeze=True)
        frozen = fdn2.process(audio)
        # frozen tail energy after input should be higher
        assert np.sum(np.abs(frozen)) > np.sum(np.abs(normal))


# --------------------------------------------------------------------------- #
# UVI Rumble — multiband
# --------------------------------------------------------------------------- #
class TestMultiband:
    def test_crossover_splits(self):
        from sound.effects import LinkwitzRiley
        sr = SR
        t = np.linspace(0, 0.5, int(0.5 * sr))
        signal = np.sin(2 * np.pi * 60 * t) + np.sin(2 * np.pi * 3000 * t)
        low, high = LinkwitzRiley.crossover(signal, sr, cutoff=500)
        f_low = np.abs(np.fft.rfft(low))
        f_high = np.abs(np.fft.rfft(high))
        freqs = np.fft.rfftfreq(len(signal), 1 / sr)
        # Low band: energy mostly below 500; high band: above
        assert np.sum(f_low[freqs > 2000]) < np.sum(f_low[freqs < 500])
        assert np.sum(f_high[freqs < 200]) < np.sum(f_high[freqs > 1000])

    def test_compressor_processes(self):
        from sound.effects import MultibandCompressor
        mbc = MultibandCompressor(SR)
        t = np.linspace(0, 0.2, int(0.2 * SR))
        audio = np.sin(2 * np.pi * 100 * t) + np.sin(2 * np.pi * 1000 * t)
        out = mbc.process(audio)
        assert len(out) == len(audio)
        assert np.max(np.abs(out)) > 0.01

    def test_multiband_synth_renders(self):
        from sound.effects import MultibandSynth
        ms = MultibandSynth(SR)
        ms.add_oscillator(0, waveform="saw", freq=60.0)
        ms.add_oscillator(1, waveform="square", freq=440.0)
        audio = ms.render(0.2)
        assert len(audio) == int(0.2 * SR)
        assert np.max(np.abs(audio)) > 0.01


# --------------------------------------------------------------------------- #
# ECHON 6 — voice allocator + mod matrix
# --------------------------------------------------------------------------- #
class TestVoiceAllocator:
    def test_allocate_release(self):
        from sound.synthesis import VoiceAllocator
        va = VoiceAllocator(num_voices=6)
        v = va.allocate()
        assert v == 0
        va.release(v)
        assert not va.is_active(v)

    def test_steals_oldest(self):
        from sound.synthesis import VoiceAllocator
        va = VoiceAllocator(num_voices=2)
        va.allocate()  # voice 0
        va.allocate()  # voice 1
        assert va.allocate() == 0  # steals oldest (voice 0)
        assert len(va.active_voices()) == 2

    def test_modulation_matrix(self):
        from sound.synthesis import ModulationMatrix
        mm = ModulationMatrix(9, 32)
        mm.set_route(0, 5, 0.5)
        assert mm.get_amount(0, 5) == 0.5
        out = mm.apply({0: 0.4}, {5: 0.1})
        assert out[5] == pytest.approx(0.1 + 0.4 * 0.5)


# --------------------------------------------------------------------------- #
# Memory V — polyrhythmic arp
# --------------------------------------------------------------------------- #
class TestPolyrhythmicArp:
    def test_parts_and_events(self):
        from sound.synthesis import PolyrhythmicArp
        arp = PolyrhythmicArp(SR)
        arp.add_part([60, 64, 67], division=4)
        arp.add_part([48, 55], division=3)
        events = arp.generate(bpm=120, total_steps=12)
        # 12 steps from each part
        assert len(events) == 24
        parts = {e["part"] for e in events}
        assert parts == {0, 1}

    def test_render(self):
        from sound.synthesis import PolyrhythmicArp
        arp = PolyrhythmicArp(SR)
        arp.add_part([60, 64, 67], division=4)
        audio = arp.render(bpm=120, total_steps=8)
        assert len(audio) > 0
        assert np.max(np.abs(audio)) > 0.01


# --------------------------------------------------------------------------- #
# DMNO — binaural / Haas
# --------------------------------------------------------------------------- #
class TestBinaural:
    def test_haas_delay(self):
        from sound.synthesis import HaasDelay
        haas = HaasDelay(SR)
        t = np.linspace(0, 0.1, int(0.1 * SR))
        mono = np.sin(2 * np.pi * 440 * t)
        stereo = haas.process(mono, delay_ms=10.0)
        assert stereo.ndim == 2
        assert stereo.shape[1] == 2
        # channels differ (decorrelated)
        assert np.corrcoef(stereo[:, 0], stereo[:, 1])[0, 1] < 0.99

    def test_binaural_synth_renders(self):
        from sound.synthesis import BinauralSynth
        bs = BinauralSynth(SR)
        stereo = bs.render_note(440.0, 0.3, mode="binaural")
        assert stereo.ndim == 2
        assert stereo.shape[1] == 2
        assert np.max(np.abs(stereo)) > 0.01


# --------------------------------------------------------------------------- #
# Obsidian — West Coast
# --------------------------------------------------------------------------- #
class TestWestCoast:
    def test_wavefolder_bounded(self):
        from sound.synthesis import Wavefolder
        wf = Wavefolder(amount=2.0)
        t = np.linspace(0, 0.1, int(0.1 * SR))
        saw = 2.0 * (440 * t % 1.0) - 1.0
        folded = wf.process(saw)
        assert np.max(np.abs(folded)) <= 1.0 + 1e-9
        assert not np.allclose(folded, saw)

    def test_lowpass_gate(self):
        from sound.synthesis import LowpassGate
        lpg = LowpassGate(SR)
        t = np.linspace(0, 0.1, int(0.1 * SR))
        audio = np.sin(2 * np.pi * 2000 * t)
        out = lpg.process(audio, cutoff=2000.0, decay=0.9)
        # High-frequency content attenuated
        assert np.sqrt(np.mean(out ** 2)) < np.sqrt(np.mean(audio ** 2)) + 1e-6

    def test_west_coast_voice(self):
        from sound.synthesis import WestCoastVoice
        vc = WestCoastVoice(SR)
        audio = vc.render_note(220.0, 0.3)
        assert len(audio) == int(0.3 * SR)
        assert np.max(np.abs(audio)) > 0.01


# --------------------------------------------------------------------------- #
# Radical1 — quantize modulators
# --------------------------------------------------------------------------- #
class TestQuantizeMod:
    def test_snaps(self):
        from sound.effects import QuantizeModulator
        qm = QuantizeModulator(steps=4)
        assert qm.process(0.37) == pytest.approx(1 / 3)
        assert qm.process(0.0) == 0.0
        assert qm.process(1.0) == 1.0

    def test_router(self):
        from sound.effects import ModRouter
        mr = ModRouter()
        mr.set_route("lfo1", "filter")
        out = mr.process({"lfo1": 0.5}, {"filter": 0.1})
        assert out["filter"] == pytest.approx(0.6)

    def test_chain(self):
        from sound.effects import QuantizeChain
        qc = QuantizeChain(SR)
        qc.add_quantizer("lfo", steps=4)
        qc.router.set_route("lfo", "gain")
        t = np.linspace(0, 0.1, int(0.1 * SR))
        audio = np.sin(2 * np.pi * 440 * t)
        out = qc.process(audio, {"lfo": 0.5}, {"gain": 0.0})
        assert len(out) == len(audio)
        assert not np.allclose(out, audio)


# --------------------------------------------------------------------------- #
# Karst — patch loader / builder
# --------------------------------------------------------------------------- #
class TestPatchLoader:
    def test_roundtrip(self, tmp_path):
        from sound.modular import PatchLoader
        patch = {"nodes": [{"type": "osc", "name": "o", "params": {"freq": 440}}],
                 "edges": []}
        path = str(tmp_path / "patch.json")
        PatchLoader.save(patch, path)
        loaded = PatchLoader.load(path)
        assert loaded == patch

    def test_builder_renders(self):
        from sound.modular import PatchBuilder
        patch = {
            "nodes": [
                {"type": "osc", "name": "osc1", "params": {"freq": 440.0, "waveform": "sine"}},
                {"type": "gain", "name": "g1", "params": {"gain": 0.5}},
                {"type": "out", "name": "out1", "params": {}},
            ],
            "edges": [
                {"src": "osc1", "out": "out", "dst": "g1", "in": "in"},
                {"src": "g1", "out": "out", "dst": "out1", "in": "in"},
            ],
        }
        builder = PatchBuilder(SR)
        graph = builder.build(patch)
        audio = graph.render(0.1)
        assert len(audio) == int(0.1 * SR)
        assert np.max(np.abs(audio)) > 0.1
