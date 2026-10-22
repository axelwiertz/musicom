# -*- coding: utf-8 -*-
"""Benchmark BLOT single-note render cost (2026-10-22)."""
import time
import numpy as np
from sound.synthesis.modal_blot import (
    BLOTEngine, LumpPiece, ModalResonator, WaveguideString, DEFAULT_SR,
)


def pluck_patch(sr=DEFAULT_SR):
    engine = BLOTEngine(sample_rate=sr)
    r1 = ModalResonator(size=1.0, shape=0.15, brightness=0.7, ring_time=0.4, heat=0.03)
    engine.add_piece(LumpPiece(resonator=r1, x=0.0, y=0.0))
    r2 = ModalResonator(size=0.5, shape=0.1, brightness=0.4, ring_time=0.25, heat=0.02)
    engine.add_piece(LumpPiece(resonator=r2, x=0.3, y=0.1))
    wg = WaveguideString(sample_rate=sr)
    wg.set_pitch(220.0)
    r3 = ModalResonator(size=2.0, shape=0.2, brightness=0.5, ring_time=0.5, heat=0.0)
    engine.add_piece(LumpPiece(resonator=r3, x=0.5, y=0.3, waveguide=wg))
    engine.set_piece_ring_mod(0, 1)
    engine.breath_noise_amp = 0.004
    engine.droplet_rate = 0.0
    engine.fdn.mix = 0.12
    return engine


engine = pluck_patch()
n = int(0.3375 * DEFAULT_SR)  # 0.1875 note + 0.15 ring tail = 16200 samples
t0 = time.time()
engine.strike_all(velocity=0.6)
audio = engine.render(midi_root=57, num_samples=n, seed=7)
dt = time.time() - t0
print("samples:", n, "render sec:", round(dt, 3))
print("per-second-of-audio cost:", round(dt / (n / DEFAULT_SR), 3), "x realtime")
print("peak:", float(np.max(np.abs(audio))))
