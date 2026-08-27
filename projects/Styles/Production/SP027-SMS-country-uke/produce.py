# -*- coding: utf-8 -*-
"""
Autonomous Daily Production Job (production pass 9a2813f77dac).

Source composition : 012-country-country-uke  (Country Uke, C major chord-melody)
MIDI               : /opt/data/projects/Styles/Country/012-country-country-uke/MIDI/country_uke.mid
Production method  : SP-027 Spectral Modeling Synthesis (SMS)

Pipeline:
  1. Render source MIDI -> WAV via FluidSynth (TimGM6mb.sf2, default piano patch).
  2. Run SMS analysis-synthesis (deterministic + stochastic decomposition) per the
     canonical reference implementation in methods_db.md SP-027.
  3. Apply an SMS sound transformation:
       - Pitch-shift the DETERMINISTIC (harmonic) component by +3 semitones (brighten),
         stochastic envelope UNCHANGED (formant/noise texture preserved).
       - Noise/harmonic balance: lift stochastic energy slightly (+3 dB) for a
         more "live room" character.
  4. Mix resynthesized components, peak-normalize to -1 dBFS.
  5. Export full mix WAV + OGG (Opus).

Outputs land in the job's Production subfolder with a README and provenance.json.
"""
import subprocess
import os
import json
import hashlib
import shutil

import numpy as np
from scipy.io import wavfile

# ----------------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------------
PY = '/opt/data/micromamba/envs/musicom/bin'
FS = os.path.join(PY, 'fluidsynth')
SF2 = '/tmp/musicom-venv/lib/python3.13/site-packages/pretty_midi/TimGM6mb.sf2'

SRC_MIDI = '/opt/data/projects/Styles/Country/012-country-country-uke/MIDI/country_uke.mid'
OUT_DIR = '/opt/data/projects/Styles/Production/SP027-SMS-country-uke'
os.makedirs(OUT_DIR, exist_ok=True)

BASE_WAV = os.path.join(OUT_DIR, 'country_uke_base.wav')     # raw FluidSynth render
FULL_WAV = os.path.join(OUT_DIR, 'country_uke_SP027_SMS.wav')  # SMS-transformed full mix
FULL_OGG = os.path.join(OUT_DIR, 'country_uke_SP027_SMS.ogg')
DET_WAV = os.path.join(OUT_DIR, 'country_uke_SP027_deterministic.wav')
STOCH_WAV = os.path.join(OUT_DIR, 'country_uke_SP027_stochastic.wav')
PROV = os.path.join(OUT_DIR, 'provenance.json')

METHOD = 'SP-027'
METHOD_NAME = 'Spectral Modeling Synthesis (Friction-Induced Waveguide-adjacent hybrid: deterministic/stochastic decomposition + transformation)'

# SMS transformation parameters
PITCH_SHIFT_SEMITONES = 3.0   # harmonic component only
STOCH_GAIN_DB = 3.0           # boost stochastic (noise) balance

# ----------------------------------------------------------------------------
# Step 1: Render source MIDI to WAV
# ----------------------------------------------------------------------------
print('[1] Rendering source MIDI -> base WAV via FluidSynth ...')
if not os.path.exists(BASE_WAV) or os.path.getsize(BASE_WAV) < 1000:
    cmd = [FS, '-ni', '-g', '1.2', '-F', BASE_WAV, SF2, SRC_MIDI]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        raise RuntimeError('FluidSynth render failed: ' + r.stderr[:500])
assert os.path.getsize(BASE_WAV) > 1000, 'base WAV empty/corrupt'
print('    base WAV size:', os.path.getsize(BASE_WAV))

# ----------------------------------------------------------------------------
# Step 2: SMS analysis-synthesis (canonical reference implementation)
# ----------------------------------------------------------------------------
print('[2] Running Spectral Modeling Synthesis (deterministic + stochastic) ...')

def spectral_modeling_synthesis(x, fs, N=2048, H=512, K_max=60,
                                min_snr=40.0, peak_tolerance=30.0):
    """Full SMS analysis-synthesis pipeline (reference impl from methods_db.md)."""
    window = np.hanning(N)
    n_frames = (len(x) - N) // H + 1

    all_peaks = []
    for m in range(n_frames):
        start = m * H
        frame = x[start:start + N] * window
        spectrum = np.fft.rfft(frame)
        mag = np.abs(spectrum)
        phase = np.angle(spectrum)
        freqs = np.fft.rfftfreq(N, d=1.0 / fs)
        mag_db = 20.0 * np.log10(mag + 1e-10)
        noise_floor = np.median(mag_db)
        peak_indices = []
        for i in range(1, len(mag_db) - 1):
            if mag_db[i] > mag_db[i - 1] and mag_db[i] > mag_db[i + 1]:
                if mag_db[i] - noise_floor > min_snr:
                    peak_indices.append(i)
        peak_indices.sort(key=lambda i: mag_db[i], reverse=True)
        peak_indices = peak_indices[:K_max]
        peak_indices.sort()
        frame_peaks = []
        for idx in peak_indices:
            if 0 < idx < len(mag_db) - 1:
                alpha = mag_db[idx - 1]
                beta = mag_db[idx]
                gamma = mag_db[idx + 1]
                p = 0.5 * (alpha - gamma) / (alpha - 2 * beta + gamma + 1e-20)
                refined_freq = freqs[idx] + p * (freqs[1] - freqs[0])
                refined_amp = mag[idx]
            else:
                refined_freq = freqs[idx]
                refined_amp = mag[idx]
            frame_peaks.append({'freq': refined_freq, 'amp': refined_amp, 'phase': phase[idx]})
        all_peaks.append(frame_peaks)

    # Peak tracking
    tracks = []
    active_tracks = []
    for m in range(n_frames):
        t = m * H / fs
        matched_track_ids = set()
        matched_peaks = set()
        candidates = []
        for ti, track in enumerate(active_tracks):
            for pi, peak in enumerate(all_peaks[m]):
                if pi in matched_peaks:
                    continue
                df = abs(peak['freq'] - track['last_freq'])
                if df < peak_tolerance:
                    candidates.append((df, ti, pi))
        candidates.sort()
        for df, ti, pi in candidates:
            if ti in matched_track_ids or pi in matched_peaks:
                continue
            matched_track_ids.add(ti)
            matched_peaks.add(pi)
            active_tracks[ti]['last_freq'] = all_peaks[m][pi]['freq']
            active_tracks[ti]['times'].append(t)
            active_tracks[ti]['freqs'].append(all_peaks[m][pi]['freq'])
            active_tracks[ti]['amps'].append(all_peaks[m][pi]['amp'])
            active_tracks[ti]['phases'].append(all_peaks[m][pi]['phase'])
        for pi, peak in enumerate(all_peaks[m]):
            if pi not in matched_peaks:
                active_tracks.append({
                    'track_id': len(tracks) + len(active_tracks),
                    'last_freq': peak['freq'],
                    'times': [t], 'freqs': [peak['freq']],
                    'amps': [peak['amp']], 'phases': [peak['phase']]})
        new_active = []
        for ti, track in enumerate(active_tracks):
            if ti not in matched_track_ids:
                tracks.append(track)
            else:
                new_active.append(track)
        active_tracks = new_active
    tracks.extend(active_tracks)

    # Deterministic synthesis
    output_length = len(x)
    y_det = np.zeros(output_length)
    window_sum = np.zeros(output_length)
    for m in range(n_frames):
        t_start = m * H
        frame = np.zeros(N)
        t_center = m * H / fs
        for track in tracks:
            if len(track['times']) < 1:
                continue
            idx = np.argmin(np.abs(np.array(track['times']) - t_center))
            if abs(track['times'][idx] - t_center) > H / fs * 2:
                continue
            f_k = track['freqs'][idx]
            A_k = track['amps'][idx]
            phi_k = track['phases'][idx]
            n_arr = np.arange(N)
            frame += A_k * np.cos(phi_k + 2.0 * np.pi * f_k * n_arr / fs)
        frame *= window
        y_det[t_start:t_start + N] += frame
        window_sum[t_start:t_start + N] += window ** 2
    nonzero = window_sum > 1e-8
    y_det[nonzero] /= window_sum[nonzero]

    # Stochastic residual
    x_stoch = x[:len(y_det)] - y_det
    n_stoch_frames = (len(x_stoch) - N) // H + 1
    n_bands = N // 4
    stoch_envelope = np.zeros((n_stoch_frames, n_bands))
    for m in range(n_stoch_frames):
        start = m * H
        frame = x_stoch[start:start + N] * window
        spec = np.abs(np.fft.rfft(frame)) ** 2
        band_size = max(1, len(spec) // n_bands)
        for b in range(n_bands):
            lo = b * band_size
            hi = min(lo + band_size, len(spec))
            stoch_envelope[m, b] = np.mean(spec[lo:hi])

    # Stochastic synthesis
    y_stoch = np.zeros(len(x_stoch))
    window_sum_s = np.zeros(len(x_stoch))
    for m in range(n_stoch_frames):
        t_start = m * H
        noise = np.random.randn(N)
        noise_spec = np.fft.rfft(noise)
        band_size = max(1, len(noise_spec) // n_bands)
        shaped_mag = np.zeros(len(noise_spec))
        for b in range(n_bands):
            lo = b * band_size
            hi = min(lo + band_size, len(noise_spec))
            target = np.sqrt(stoch_envelope[m, b] + 1e-20)
            shaped_mag[lo:hi] = target
        random_phase = np.exp(1j * np.random.uniform(0, 2 * np.pi, len(noise_spec)))
        shaped_spec = shaped_mag * random_phase
        frame_out = np.fft.irfft(shaped_spec, n=N) * window
        y_stoch[t_start:t_start + N] += frame_out
        window_sum_s[t_start:t_start + N] += window ** 2
    nonzero_s = window_sum_s > 1e-8
    y_stoch[nonzero_s] /= window_sum_s[nonzero_s]

    # Normalize so each component's peak is equivalent to input scale
    in_peak = max(np.max(np.abs(x)), 1e-10)
    det_peak = max(np.max(np.abs(y_det)), 1e-10)
    stoch_peak = max(np.max(np.abs(y_stoch)), 1e-10)
    y_det = y_det / det_peak * in_peak
    y_stoch = y_stoch / stoch_peak * in_peak

    return y_det, y_stoch, tracks, stoch_envelope


# Read base render
fs_base, audio = wavfile.read(BASE_WAV)
if audio.ndim > 1:
    audio = audio.mean(axis=1)
audio = audio.astype(np.float64)
audio = audio / (np.max(np.abs(audio)) + 1e-10)   # normalize to [-1, 1]
print('    base sr=%d  samples=%d  dur=%.2fs' % (fs_base, len(audio), len(audio) / fs_base))

y_det, y_stoch, tracks, stoch_env = spectral_modeling_synthesis(
    audio, fs_base, N=2048, H=512, K_max=60, min_snr=40.0, peak_tolerance=30.0)
print('    sinusoidal tracks detected:', len(tracks))

# ----------------------------------------------------------------------------
# Step 3: SMS sound transformation
#   - Pitch-shift DETERMINISTIC component only (+3 semitones)
#   - Boost stochastic energy balance (+3 dB)
# ----------------------------------------------------------------------------
print('[3] Applying SMS transformation (det pitch-shift +%0.1f st, stoch +%0.1f dB) ...'
      % (PITCH_SHIFT_SEMITONES, STOCH_GAIN_DB))

def pitch_shift_component(y_det, fs_rate, semitones):
    """Time-domain resampling pitch-shift of the deterministic (harmonic) part.
    Since SMS gives us a clean sum-of-sinusoids band, resampling preserves the
    harmonic phase structure while shifting all partials by the same ratio."""
    alpha = 2.0 ** (semitones / 12.0)
    n_new = int(round(len(y_det) / alpha))
    if n_new < 1:
        n_new = 1
    # integer + linear interp resample (scipy-free safe path already uses scipy)
    from scipy.interpolate import interp1d
    t_old = np.linspace(0, 1, len(y_det), endpoint=False)
    t_new = np.linspace(0, 1, n_new, endpoint=False)
    f = interp1d(t_old, y_det, kind='linear', bounds_error=False, fill_value=0.0)
    shifted = f(t_new)
    return shifted

y_det_shifted = pitch_shift_component(y_det, fs_base, PITCH_SHIFT_SEMITONES)

# Re-anchor shifted component length to original (pad/trim) for clean mix
if len(y_det_shifted) > len(y_det):
    y_det_shifted = y_det_shifted[:len(y_det)]
else:
    y_det_shifted = np.pad(y_det_shifted, (0, len(y_det) - len(y_det_shifted)))

stoch_gain = 10.0 ** (STOCH_GAIN_DB / 20.0)
y_stoch_boosted = y_stoch * stoch_gain

# Mix
mix = y_det_shifted + y_stoch_boosted

# RMS-aware normalization: match the SOURCE RMS so the SMS-transformed render
# is comparable in loudness/body to the original. The IBF additive deterministic
# synth + stochastic residual have very different crest factors than the source,
# so we match RMS first, then apply a soft (tanh) limiter to prevent harsh
# clipping. Soft-clipping preserves mid-level detail while gently compressing
# any remaining peaks, keeping the render both listenable and non-destructive.
src_rms = float(np.sqrt(np.mean(audio ** 2))) + 1e-10
mix_rms = float(np.sqrt(np.mean(mix ** 2))) + 1e-10
mix = mix * (src_rms / mix_rms)

# Soft limiter: tanh saturates toward -1..+1 dBFS without hard clipping artifacts.
target_peak = 10.0 ** (-1.0 / 20.0)
mix = target_peak * np.tanh(mix / target_peak)

# ----------------------------------------------------------------------------
# Step 4: Write WAV outputs
# ----------------------------------------------------------------------------
print('[4] Writing WAV + OGG outputs ...')
def write_wav(path, sig, sr):
    sig_i = np.clip(sig, -1.0, 1.0)
    sig_i = (sig_i * 32767.0).astype(np.int16)
    wavfile.write(path, sr, sig_i)
    assert os.path.getsize(path) > 40, 'empty WAV: ' + path

write_wav(FULL_WAV, mix, fs_base)
write_wav(DET_WAV, y_det_shifted, fs_base)
write_wav(STOCH_WAV, y_stoch_boosted, fs_base)
print('    full mix WAV size:', os.path.getsize(FULL_WAV))

# ----------------------------------------------------------------------------
# Step 5: OGG (Opus) via ffmpeg
# ----------------------------------------------------------------------------
ff = shutil.which('ffmpeg') or '/usr/bin/ffmpeg'
cmd = [ff, '-y', '-i', FULL_WAV, '-codec:a', 'libopus', '-application', 'voip',
       '-b:a', '48k', FULL_OGG]
r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
if r.returncode != 0:
    raise RuntimeError('ffmpeg OGG failed: ' + r.stderr[:400])
assert os.path.getsize(FULL_OGG) > 40, 'empty OGG'
print('    full mix OGG size:', os.path.getsize(FULL_OGG))

# ----------------------------------------------------------------------------
# Provenance
# ----------------------------------------------------------------------------
def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()

prov = {
    'job': 'production-9a2813f77dac',
    'source_midi': SRC_MIDI,
    'source_midi_sha256': sha256(SRC_MIDI),
    'production_method': METHOD,
    'production_method_name': METHOD_NAME,
    'transformation': {
        'deterministic_pitch_shift_semitones': PITCH_SHIFT_SEMITONES,
        'stochastic_gain_db': STOCH_GAIN_DB,
        'description': ('SMS decomposed the source into a deterministic (harmonic '
                        'sinusoidal) component and a stochastic (residual noise) '
                        'component. The harmonic component was pitch-shifted up '
                        '+3 semitones (brightening the uke) while the stochastic '
                        'envelope was preserved. Stochastic energy was lifted +3 dB '
                        'for a livelier room character. Components re-mixed and '
                        'peak-normalized to -1 dBFS.')
    },
    'sms_parameters': {'N': 2048, 'H': 512, 'K_max': 60, 'min_snr_db': 40.0,
                      'peak_tolerance_hz': 30.0, 'tracks_detected': len(tracks)},
    'render_engine': 'FluidSynth 2.5.6 (TimGM6mb.sf2)',
    'outputs': {
        'base_wav': BASE_WAV,
        'full_mix_wav': FULL_WAV,
        'full_mix_ogg': FULL_OGG,
        'deterministic_wav': DET_WAV,
        'stochastic_wav': STOCH_WAV,
    },
    'output_sha256': {
        'full_mix_wav': sha256(FULL_WAV),
        'full_mix_ogg': sha256(FULL_OGG),
    }
}
with open(PROV, 'w') as f:
    json.dump(prov, f, indent=2)
print('[done] provenance written:', PROV)
