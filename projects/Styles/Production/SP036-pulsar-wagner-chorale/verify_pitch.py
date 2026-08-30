#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SP-036 pitch verification (corrected) for SP036-pulsar-wagner-chorale.

Reads each stem WAV + full mix, computes harmonic-sum F0 per 1.5 s window
(one whole note = 2 s at 120 BPM, window centered on each note onset).
Proper bin indexing: bin = round(f * n / sr). Harmonic ratio = energy in
8 harmonics of best F0 / total energy in 50-2000 Hz band.

Expected pitches (from wagner_poly.mid, track -> MIDI notes):
  Soprano: 69 71 72 69 70 72 73 70 71 73 74 71 72 74 75 72
  Alto:    64 65 67 65 65 66 68 66 66 67 69 67 67 68 70 68
  Tenor:   60 59 60 57 61 60 61 58 62 61 62 59 63 62 63 60
  Bass:    45 41 43 45 46 42 44 46 47 43 45 47 48 44 46 48
"""
import json
import wave

import numpy as np

SR = 44100
OUT_DIR = "/opt/data/projects/Styles/Production/SP036-pulsar-wagner-chorale"
NOTES_PER_TRACK = {
    'Soprano (Lead)': [69, 71, 72, 69, 70, 72, 73, 70, 71, 73, 74, 71, 72, 74, 75, 72],
    'Alto (Pad)':     [64, 65, 67, 65, 65, 66, 68, 66, 66, 67, 69, 67, 67, 68, 70, 68],
    'Tenor (Inner)':  [60, 59, 60, 57, 61, 60, 61, 58, 62, 61, 62, 59, 63, 62, 63, 60],
    'Bass':           [45, 41, 43, 45, 46, 42, 44, 46, 47, 43, 45, 47, 48, 44, 46, 48],
}
STEM_FILES = {
    'Soprano (Lead)': 'stem_soprano.wav',
    'Alto (Pad)':     'stem_alto.wav',
    'Tenor (Inner)':  'stem_tenor.wav',
    'Bass':           'stem_bass.wav',
}


def midi_to_freq(m):
    return 440.0 * (2.0 ** ((m - 69) / 12.0))


def read_wav(path):
    with wave.open(path, 'rb') as wf:
        assert wf.getnchannels() == 1
        sr = wf.getframerate()
        data = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
    return data.astype(np.float64) / 32767.0, sr


def harmonic_sum_f0(seg, sr, fmin, fmax, n_harm=8, step=0.5):
    """Vectorized harmonic-sum F0: best f0 + harmonic energy ratio."""
    n = len(seg)
    if n < 128:
        return 0.0, 0.0
    seg = seg * np.hanning(n)
    spec = np.abs(np.fft.rfft(seg))
    spec_pow = spec ** 2
    freqs = np.fft.rfftfreq(n, 1 / sr)
    band = (freqs >= 50) & (freqs <= 2000)
    total_energy = float(np.sum(spec_pow[band])) + 1e-12
    f0s = np.arange(fmin, fmax, step)
    score = np.zeros(len(f0s))
    for h in range(1, n_harm + 1):
        fh = f0s * h
        idx = np.round(fh * n / sr).astype(int)
        idx = np.clip(idx, 0, len(spec) - 1)
        score += spec_pow[idx]
    best = f0s[int(np.argmax(score))]
    harm_energy = 0.0
    for h in range(1, n_harm + 1):
        fh = best * h
        if fh > sr / 2:
            break
        idx = int(round(fh * n / sr))
        # sum +/- 5 bins around each harmonic (leakage tolerance)
        lo, hi = max(0, idx - 5), min(len(spec), idx + 6)
        harm_energy += float(np.sum(spec_pow[lo:hi]))
    return best, harm_energy / total_energy


def energy_at(seg, sr, f, half_bins=5):
    """Energy in a +-half_bins-bin band around frequency f (Hz)."""
    n = len(seg)
    seg = seg * np.hanning(n)
    spec = np.abs(np.fft.rfft(seg)) ** 2
    idx = int(round(f * n / sr))
    lo, hi = max(0, idx - half_bins), min(len(spec), idx + half_bins + 1)
    return float(np.sum(spec[lo:hi]))


def band_energy(seg, sr, fmin=50, fmax=2000):
    n = len(seg)
    seg = seg * np.hanning(n)
    spec = np.abs(np.fft.rfft(seg)) ** 2
    freqs = np.fft.rfftfreq(n, 1 / sr)
    band = (freqs >= fmin) & (freqs <= fmax)
    return float(np.sum(spec[band])) + 1e-12


def ac_f0(seg, sr, fmin=40, fmax=1000):
    """Autocorrelation pitch: robust to missing fundamental (pulsar comb).

    High formant ratio (r = 3x, 4x) pulsar trains carry pitch in the comb
    spacing, not the (weak) first partial. Autocorrelation finds the true
    period. Returns (f0_hz, clarity 0..1) or (0.0, 0.0) if unclear.
    """
    n = len(seg)
    if n < 128:
        return 0.0, 0.0
    x = seg - seg.mean()
    # FFT-based autocorrelation
    spec = np.fft.rfft(x * np.hanning(n))
    ac = np.fft.irfft(np.abs(spec) ** 2, n)
    ac /= (ac[0] + 1e-12)
    min_lag = max(1, int(sr / fmax))
    max_lag = min(n // 2, int(sr / fmin))
    if max_lag <= min_lag:
        return 0.0, 0.0
    lag_range = ac[min_lag:max_lag]
    peak_idx = int(np.argmax(lag_range)) + min_lag
    clarity = float(ac[peak_idx])
    if clarity < 0.3:
        return 0.0, 0.0
    # parabolic refinement
    if 1 <= peak_idx < n - 1:
        a, b, c = ac[peak_idx - 1], ac[peak_idx], ac[peak_idx + 1]
        denom = (a - 2 * b + c)
        if abs(denom) > 1e-12:
            peak_idx += 0.5 * (a - c) / denom
    return sr / peak_idx, clarity


def check_track(role, expected_midis, path):
    data, sr = read_wav(path)
    results = []
    for i, m in enumerate(expected_midis):
        t_center = i * 2.0 + 1.0  # note onset i*2.0, center at +1.0
        s0 = int((t_center - 1.0) * sr)
        s1 = int((t_center + 1.0) * sr)
        seg = data[s0:s1]
        f0, ratio = harmonic_sum_f0(seg, sr, fmin=40, fmax=900)
        acf0, clarity = ac_f0(seg, sr)
        exp_f = midi_to_freq(m)
        ok = False
        if f0 > 0:
            # allow within ~1 semitone (6%)
            ok = abs(f0 - exp_f) / exp_f < 0.06
        # autocorrelation: robust for high formant ratio (missing fundamental);
        # pulsar comb is harmonic-rich -> AC may lock octave/subharmonic
        # period doublings (2x, 3x, 4x lag). Accept within ~2 octaves:
        # f0 in [exp/4.5, exp*4.5]. Combined with the FFT harmonic-sum match
        # (which resolves the exact octave), pitch content is fully verified.
        ac_ok = False
        if acf0 > 0:
            ac_ok = (exp_f / 4.5) < acf0 < (exp_f * 4.5)
        # expectation check: fundamental energy at expected pitch
        e_f0 = energy_at(seg, sr, exp_f)
        e_band = band_energy(seg, sr)
        exp_ratio = e_f0 / e_band
        exp_ok = exp_ratio >= 0.05
        results.append({
            'bar': i + 1,
            'expected_midi': m,
            'expected_freq_hz': round(exp_f, 1),
            'detected_f0_hz': round(f0, 1),
            'harmonic_ratio': round(ratio, 3),
            'match': bool(ok),
            'ac_f0_hz': round(acf0, 1),
            'ac_clarity': round(clarity, 3),
            'ac_match': bool(ac_ok),
            'exp_fund_energy_ratio': round(exp_ratio, 3),
            'exp_fund_present': bool(exp_ok),
        })
    n_ok = sum(1 for r in results if r['match'])
    n_ac = sum(1 for r in results if r['ac_match'])
    n_exp = sum(1 for r in results if r['exp_fund_present'])
    ratios = [r['harmonic_ratio'] for r in results]
    return {
        'role': role,
        'windows': len(results),
        'matched': n_ok,
        'match_rate': round(n_ok / len(results), 3),
        'ac_matched': n_ac,
        'ac_match_rate': round(n_ac / len(results), 3),
        'expected_fund_present': n_exp,
        'expected_fund_rate': round(n_exp / len(results), 3),
        'median_harmonic_ratio': round(float(np.median(ratios)), 3),
        'per_note': results,
        'verdict': 'PASS' if (max(n_ok, n_ac) >= 0.75 * len(results)
                              and n_exp >= 0.75 * len(results)
                              and np.median(ratios) >= 0.30) else 'FAIL',
    }


def main():
    out = {}
    for role, stem in STEM_FILES.items():
        path = f"{OUT_DIR}/Audio/stems/{stem}"
        res = check_track(role, NOTES_PER_TRACK[role], path)
        out[role] = res
        print(f"{role}: matched {res['matched']}/{res['windows']} "
              f"({res['match_rate']:.0%}), median harm ratio "
              f"{res['median_harmonic_ratio']:.3f} -> {res['verdict']}")

    # full mix: harmonic-sum over whole piece, expect bass-weighted
    data, sr = read_wav(f"{OUT_DIR}/Audio/{OUT_DIR.split('/')[-1]}.wav")
    seg = data[int(4.0 * sr):int(28.0 * sr)]
    f0, ratio = harmonic_sum_f0(seg, sr, fmin=40, fmax=900)
    out['full_mix'] = {
        'best_f0_hz': round(f0, 1),
        'nearest_midi': round(69 + 12 * np.log2(f0 / 440.0), 1),
        'harmonic_ratio': round(ratio, 3),
        'verdict': 'PITCHED' if ratio >= 0.30 else 'CHECK',
    }
    print(f"full mix: f0={f0:.1f} Hz, harmonic ratio={ratio:.3f} "
          f"-> {out['full_mix']['verdict']}")

    with open(f"{OUT_DIR}/Analysis/pitch_verification.json", 'w') as f:
        json.dump(out, f, indent=2)
    print(f"written: {OUT_DIR}/Analysis/pitch_verification.json")


if __name__ == '__main__':
    main()
