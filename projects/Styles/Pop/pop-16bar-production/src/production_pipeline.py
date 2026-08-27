"""
Sound Production Pipeline — Test each DSP method one-by-one.
Loads raw WAV, applies effects sequentially, measures LUFS at each stage.
"""

import os
import numpy as np
from sound.utils.io import read_wav, write_wav
from sound.effects import (
    AlgorithmicReverb, StateVariableFilter, BiquadFilter,
    DynamicEQ, StereoImager, Limiter, LUFSMeter, normalize_to_lufs
)

# Paths
BASE = '/opt/data/projects/Styles/Pop/pop-16bar-production'
RAW_WAV = os.path.join(BASE, 'Audio', 'pop_16bar_raw.wav')
OUTPUT_DIR = os.path.join(BASE, 'Audio', 'production_stages')
os.makedirs(OUTPUT_DIR, exist_ok=True)

def measure_lufs(audio, sr=44100):
    """Measure integrated LUFS."""
    meter = LUFSMeter(sr)
    return meter.measure(audio).integrated_lufs

def print_stats(name, audio, sr=44100):
    """Print audio stats + LUFS."""
    peak = np.max(np.abs(audio))
    rms = np.sqrt(np.mean(audio ** 2))
    lufs = measure_lufs(audio, sr)
    print(f"{name:20s} | peak={peak:.3f} | RMS={rms:.3f} | LUFS={lufs:.1f}")
    return lufs

def main():
    print("=== Sound Production Pipeline ===")
    print(f"Input: {RAW_WAV}\n")
    
    # Load raw audio
    audio, sr = read_wav(RAW_WAV)
    print(f"Loaded: {len(audio)/sr:.2f}s @ {sr}Hz")
    print(f"Shape: {audio.shape}\n")
    
    # Stage 0: Raw
    print("Stage 0: RAW (no processing)")
    lufs_raw = print_stats("Raw", audio, sr)
    write_wav(os.path.join(OUTPUT_DIR, '00_raw.wav'), audio, sr, normalize=False)
    print()
    
    # Stage 1: Reverb
    print("Stage 1: REVERB (Schroeder algorithmic)")
    reverb = AlgorithmicReverb(
        sample_rate=sr,
        room_size=0.6,
        damping=0.4,
        wet_dry=0.25,
        width=0.8
    )
    audio_reverb = reverb.process(audio)
    lufs_reverb = print_stats("Reverb", audio_reverb, sr)
    write_wav(os.path.join(OUTPUT_DIR, '01_reverb.wav'), audio_reverb, sr, normalize=False)
    print(f"  → room_size=0.6, damping=0.4, wet_dry=0.25\n")
    
    # Stage 2: SVF Lowpass (warmth)
    print("Stage 2: SVF LOWPASS (warmth, tame highs)")
    svf = StateVariableFilter(sr)
    audio_svf = svf.process(audio_reverb, cutoff=8000.0, resonance=0.2, mode='lp')
    lufs_svf = print_stats("SVF LP 8kHz", audio_svf, sr)
    write_wav(os.path.join(OUTPUT_DIR, '02_svf_lowpass.wav'), audio_svf, sr, normalize=False)
    print(f"  → cutoff=8kHz, resonance=0.2, mode=lp\n")
    
    # Stage 3: Biquad Peaking EQ (presence boost)
    print("Stage 3: BIQUAD PEAKING EQ (presence boost at 3kHz)")
    biquad = BiquadFilter(sr)
    biquad.design('peaking', freq=3000.0, Q=1.5, gain_db=3.0)
    audio_biquad = biquad.process(audio_svf)
    lufs_biquad = print_stats("Biquad Peak 3k", audio_biquad, sr)
    write_wav(os.path.join(OUTPUT_DIR, '03_biquad_peaking.wav'), audio_biquad, sr, normalize=False)
    print(f"  → freq=3kHz, Q=1.5, gain=+3dB\n")
    
    # Stage 4: Dynamic EQ (tame harshness)
    print("Stage 4: DYNAMIC EQ (tame 2-4kHz harshness)")
    deq = DynamicEQ(sr)
    deq.add_band(3000.0, q=2.0, threshold_db=-10.0, ratio=2.5)
    audio_deq = deq.process(audio_biquad)
    lufs_deq = print_stats("Dynamic EQ", audio_deq, sr)
    write_wav(os.path.join(OUTPUT_DIR, '04_dynamic_eq.wav'), audio_deq, sr, normalize=False)
    print(f"  → band: 3kHz, Q=2.0, threshold=-10dB, ratio=2.5:1\n")
    
    # Stage 5: Stereo Imager (mono bass, wide highs)
    print("Stage 5: STEREO IMAGER (mono <100Hz, wide >2kHz)")
    imager = StereoImager(sr)
    imager.set_width(0.0, below_hz=100)   # Mono sub-bass
    imager.set_width(1.3, above_hz=2000)  # Widen highs
    audio_stereo = imager.process(audio_deq)
    lufs_stereo = print_stats("Stereo Image", audio_stereo, sr)
    write_wav(os.path.join(OUTPUT_DIR, '05_stereo_imager.wav'), audio_stereo, sr, normalize=False)
    print(f"  → width=0.0 below 100Hz, width=1.3 above 2kHz\n")
    
    # Stage 6: Limiter (peak control)
    print("Stage 6: LIMITER (peak control, ceiling -1dB)")
    limiter = Limiter(threshold_db=-1.0, release_ms=100.0, sample_rate=sr)
    audio_limited = limiter.process(audio_stereo)
    lufs_limited = print_stats("Limiter", audio_limited, sr)
    write_wav(os.path.join(OUTPUT_DIR, '06_limiter.wav'), audio_limited, sr, normalize=False)
    print(f"  → threshold=-1.0dB, release=100ms\n")
    
    # Stage 7: LUFS Normalization (Spotify target)
    print("Stage 7: LUFS NORMALIZATION (Spotify -14 LUFS)")
    audio_final = normalize_to_lufs(audio_limited, target_lufs=-14.0, sample_rate=sr)
    lufs_final = print_stats("LUFS -14", audio_final, sr)
    write_wav(os.path.join(OUTPUT_DIR, '07_final_lufs14.wav'), audio_final, sr, normalize=False)
    print(f"  → target=-14.0 LUFS (Spotify standard)\n")
    
    # Summary
    print("=" * 70)
    print("PRODUCTION PIPELINE SUMMARY")
    print("=" * 70)
    print(f"{'Stage':<25} {'LUFS':>8} {'Δ LUFS':>8}")
    print("-" * 70)
    stages = [
        ("Raw", lufs_raw, 0),
        ("Reverb", lufs_reverb, lufs_reverb - lufs_raw),
        ("SVF Lowpass", lufs_svf, lufs_svf - lufs_reverb),
        ("Biquad Peaking", lufs_biquad, lufs_biquad - lufs_svf),
        ("Dynamic EQ", lufs_deq, lufs_deq - lufs_biquad),
        ("Stereo Imager", lufs_stereo, lufs_stereo - lufs_deq),
        ("Limiter", lufs_limited, lufs_limited - lufs_stereo),
        ("LUFS Normalized", lufs_final, lufs_final - lufs_limited),
    ]
    for name, lufs, delta in stages:
        print(f"{name:<25} {lufs:>7.1f} {delta:>+7.1f}")
    print("=" * 70)
    print(f"\n✓ All stages exported to: {OUTPUT_DIR}")
    print(f"✓ Final mastered audio: {OUTPUT_DIR}/07_final_lufs14.wav")
    
    return audio_final

if __name__ == '__main__':
    main()
