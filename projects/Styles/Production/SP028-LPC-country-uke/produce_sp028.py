# -*- coding: utf-8 -*-
"""
SP-028 Linear Predictive Coding (LPC) Synthesis - production pass.

Applies the LPC source-filter model to the selected country uke composition.
Two SP-028 demonstrations, exactly per methods_db.md section SP-028:

  1. FORMANT-PRESERVING VOCAL RESYNTHESIS (timbre transfer / vocal color):
     - Analyze the lead-vocal region of a dry render with LPC (autocorrelation +
       Levinson-Durbin -> all-pole filter coefficients encoding formant structure).
     - Re-excite the extracted all-pole filter with a controlled glottal impulse
       train -> 'LPC country chorus' with the composition's formant color but a
       clean synthetic voice source. This is the core SP-028 vocoder trick.

  2. FORMANT-PRESERVING PITCH SHIFT:
     - Keep LPC coefficients (formants) unchanged, change excitation period
       T0' = T0 / beta -> shift pitch while formants stay fixed.

Method map: analysis (autocorrelation + Levinson-Durbin) and synthesis (all-pole
IIR driven by impulse-train excitation) implemented in numpy/scipy, exactly per
methods_db.md SP-028.

Pipeline:
  composition.mid --(FluidSynth dry render, source)---> dry.wav
  dry.wav --(LPC analysis of voiced region)---> {a_k, pitch T0, voicing, gain}
  {a_k, T0} --(re-excite w/ glottal train + shift)---> LPC resynth stems
  dry.wav + LPC stems --(blend, loudness glue)---> full_mix.wav
  full_mix.wav --(ffmpeg libopus 48k voip)---> full_mix.ogg
"""
import os
import json
import hashlib
import subprocess
import numpy as np
import scipy.signal as sig
import wave

# ----------------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------------
PROJ = "/opt/data/projects/Styles/Production/SP028-LPC-country-uke"
MIDI_SRC = "/opt/data/projects/Styles/Country/012-country-country-uke/MIDI/v2_country_unitmatrix.mid"
SOUNDFONT = "/opt/data/micromamba/envs/musicom/lib/python3.11/site-packages/pretty_midi/TimGM6mb.sf2"
FLUIDSYNTH = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"

AUDIO = os.path.join(PROJ, "Audio")
MIDI_OUT = os.path.join(PROJ, "MIDI")
ANALYSIS = os.path.join(PROJ, "Analysis")
os.makedirs(AUDIO, exist_ok=True)
os.makedirs(MIDI_OUT, exist_ok=True)
os.makedirs(ANALYSIS, exist_ok=True)

SR = 44100

def wav_read(path):
    with wave.open(path, 'rb') as wf:
        nch = wf.getnchannels()
        sw = wf.getsampwidth()
        fr = wf.getframerate()
        n = wf.getnframes()
        raw = wf.readframes(n)
    data = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    if nch > 1:
        data = data.reshape(n, nch)
    return data, nch, fr

def wav_write(path, data, sr=SR, nch=1):
    if data.ndim == 1:
        data = data[:, None]
    if nch == 1:
        data = data[:, 0]
    pcm = np.clip(data, -1.0, 1.0)
    pcm = (pcm * 32767.0).astype(np.int16)
    with wave.open(path, 'wb') as wf:
        wf.setnchannels(nch)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())

# ----------------------------------------------------------------------------
# Step 0. Copy source MIDI for reference
# ----------------------------------------------------------------------------
import shutil
midi_copy = os.path.join(MIDI_OUT, "original_v2_country_unitmatrix.mid")
shutil.copy(MIDI_SRC, midi_copy)
with open(MIDI_SRC, 'rb') as f:
    src_sha = hashlib.sha256(f.read()).hexdigest()

# ----------------------------------------------------------------------------
# Step 1. Dry render of the full arrangement (FluidSynth CLI, Stereo)
# ----------------------------------------------------------------------------
dry_wav = os.path.join(AUDIO, "dry_render_full.wav")
if not os.path.exists(dry_wav):
    cmd = [
        FLUIDSYNTH, "-a", "file", "-ni", "-g", "1.0",
        "-r", str(SR), "-F", dry_wav,
        SOUNDFONT, MIDI_SRC,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    print("fluidsynth rc:", r.returncode)
    if r.returncode != 0 or not os.path.exists(dry_wav):
        print(r.stderr[-2000:])
        raise SystemExit("FluidSynth dry render failed")
print("dry render size:", os.path.getsize(dry_wav))

dry_st, nch, fr = wav_read(dry_wav)
print("dry: nch", nch, "fr", fr, "samples", dry_st.shape[0],
      "dur", dry_st.shape[0] / fr)
dry_mono = dry_st.mean(axis=1) if dry_st.ndim > 1 and dry_st.shape[1] > 1 else dry_st
peak = np.max(np.abs(dry_mono))
print("dry peak:", peak)

# ----------------------------------------------------------------------------
# Step 2. LPC analysis (autocorrelation + Levinson-Durbin), methods_db SP-028
# ----------------------------------------------------------------------------
def levinson_durbin(r, order):
    """Solve Yule-Walker via Levinson-Durbin recursion. Returns a[1..p], E."""
    a = np.zeros(order + 1)
    a[0] = 1.0
    a_prev = np.zeros(order + 1)
    a_prev[0] = 1.0
    E = r[0]
    k = np.zeros(order)
    for i in range(1, order + 1):
        acc = r[i]
        for j in range(1, i):
            acc += a_prev[j] * r[i - j]
        ki = -acc / (E + 1e-20)
        k[i - 1] = ki
        a[i] = ki
        for j in range(1, i):
            a[j] = a_prev[j] + ki * a_prev[i - j]
        E = (1.0 - ki * ki) * E
        a_prev[:i + 1] = a[:i + 1].copy()
    return a, k, E

def lpc_analyze(x, fs, frame_ms=30, hop_ms=10, order=14, alpha=0.97,
                pitch_scale=1.0):
    """Per-frame LPC: a-coeffs, gain, pitch period, voicing.
    pitch_scale multiplies the detected pitch period (for downmixed demo 1)."""
    L = int(frame_ms * fs / 1000)
    H = int(hop_ms * fs / 1000)
    n_frames = (len(x) - L) // H + 1
    win = np.hamming(L)
    frames = []
    for m in range(n_frames):
        start = m * H
        frame = x[start:start + L].astype(np.float64)
        pre = np.zeros(L)
        pre[0] = frame[0]
        pre[1:] = frame[1:] - alpha * frame[:-1]
        xw = pre * win
        r = np.zeros(order + 1)
        for kl in range(order + 1):
            r[kl] = np.dot(xw[:L - kl], xw[kl:])
        a, kk, E = levinson_durbin(r, order)
        # residual for pitch detection
        residual = np.zeros(L)
        for n in range(L):
            residual[n] = xw[n]
            for j in range(1, order + 1):
                if n - j >= 0:
                    residual[n] += a[j] * xw[n - j]
        T_min = int(fs / 500.0)
        T_max = int(fs / 60.0)
        T_max = min(T_max, L - 1)
        voiced = False
        pitch = 0
        if T_max > T_min:
            Rr = np.correlate(residual, residual, mode='full')[L - 1:]
            if T_max < len(Rr):
                seg = Rr[T_min:T_max + 1]
                bl = T_min + int(np.argmax(seg))
                vs = Rr[bl] / (Rr[0] + 1e-20)
                voiced = vs > 0.5
                pitch = bl if voiced else 0
        frames.append({
            'a': a, 'gain': np.sqrt(max(E, 1e-20)),
            'pitch': int(pitch * pitch_scale), 'voiced': voiced,
            'time': (start + L / 2) / fs,
        })
    return frames

def lpc_synth_frame(a, excitation):
    """All-pole IIR: y[n] = e[n] - sum(a_k y[n-k])."""
    order = len(a) - 1
    y = np.zeros(len(excitation))
    for n in range(len(excitation)):
        y[n] = excitation[n]
        for j in range(1, order + 1):
            if n - j >= 0:
                y[n] -= a[j] * y[n - j]
    return y

def lpc_synthesize(frames, fs, frame_ms=30, hop_ms=10, pitch_shift=1.0,
                   voiced_gain=1.0, unvoiced_gain=1.0, t0_boost=1.0):
    """Reconstruct audio from LPC frames. Formants preserved; pitch shifted."""
    L = int(frame_ms * fs / 1000)
    H = int(hop_ms * fs / 1000)
    order = len(frames[0]['a']) - 1
    total = (len(frames) - 1) * H + L
    y = np.zeros(total)
    ws = np.zeros(total)
    win = np.hamming(L)
    rng = np.random.default_rng(42)
    for m, fr in enumerate(frames):
        a = fr['a']
        ex = np.zeros(L)
        if fr['voiced'] and fr['pitch'] > 0:
            T0 = max(1, int(fr['pitch'] / pitch_shift * t0_boost))
            amp = fr['gain'] * voiced_gain
            for n in range(L):
                if n % T0 == 0:
                    ex[n] = amp
        else:
            ex = fr['gain'] * unvoiced_gain * rng.standard_normal(L)
        fout = lpc_synth_frame(a, ex)
        fout *= win
        start = m * H
        y[start:start + L] += fout
        ws[start:start + L] += win ** 2
    nz = ws > 1e-8
    y[nz] /= ws[nz]
    pk = np.max(np.abs(y))
    if pk > 0:
        y = y / pk * 0.98
    return y

# ----------------------------------------------------------------------------
# Step 3. Pick the LEAD VOCAL region for LPC analysis (source of formants).
# We analyze the full dry mono (melody+harmony dominance in mid register) but
# choose a region where vocal energy dominates (~ the first 30 s).
# ----------------------------------------------------------------------------
n_need = int(30.0 * SR)
region = dry_mono[:n_need] if len(dry_mono) > n_need else dry_mono
assert region.size > SR, "dry render region too short"
region = region / (np.max(np.abs(region)) + 1e-9)

ORDER = 16  # moderate order: captures formant structure w/o overfitting
print("analyzing LPC region...", region.shape, "order", ORDER)
frames = lpc_analyze(region, SR, frame_ms=30, hop_ms=10, order=ORDER,
                     alpha=0.97, pitch_scale=1.0)
voiced_frac = np.mean([f['voiced'] for f in frames])
pitches_hz = [SR / f['pitch'] for f in frames if f['voiced'] and f['pitch'] > 0]
print("LPC frames:", len(frames), "voiced frac:", round(voiced_frac, 3))
if pitches_hz:
    print("voiced pitch range Hz:", round(min(pitches_hz), 1), "-",
          round(max(pitches_hz), 1), "mean", round(float(np.mean(pitches_hz)), 1))

# ----------------------------------------------------------------------------
# Step 4. SP-028 Demo 1: formant-preserving vocal resynthesis (vocoder color)
#         Re-excite the extracted all-pole filter with a clean glottal impulse
#         train -> 'LPC country chorus' (source pitch from analysis, formants
#         from the country arrangement).
# ----------------------------------------------------------------------------
lpc_vocal = lpc_synthesize(frames, SR, frame_ms=30, hop_ms=10,
                           pitch_shift=1.0, voiced_gain=1.0,
                           unvoiced_gain=0.15, t0_boost=1.0)
print("LPC vocal resynth dur:", round(lpc_vocal.shape[0] / SR, 2), "s")

# Extend LPC vocal to the full dry length for blending (loop the analyzed region
# if dry is longer than 30 s).
def repeat_to_len(sig_in, target_len):
    if len(sig_in) >= target_len:
        return sig_in[:target_len]
    reps = int(np.ceil(target_len / len(sig_in)))
    return np.tile(sig_in, reps)[:target_len]

lpc_vocal_full = repeat_to_len(lpc_vocal, dry_mono.shape[0])
wav_write(os.path.join(AUDIO, "stem_lpc_vocal_resynth.wav"), lpc_vocal_full, SR, 1)

# Melody pitch contour for the grid viz
melody_pitch = []
for f in frames:
    if f['voiced'] and f['pitch'] > 0:
        melody_pitch.append(SR / f['pitch'])
    else:
        melody_pitch.append(0.0)

# ----------------------------------------------------------------------------
# Step 5. SP-028 Demo 2: formant-preserving pitch shift (T0' = T0 / beta)
#         beta = 1.12 -> slightly lifted, formants locked.
# ----------------------------------------------------------------------------
beta = 1.12
lpc_shift = lpc_synthesize(frames, SR, frame_ms=30, hop_ms=10,
                           pitch_shift=beta, voiced_gain=1.0,
                           unvoiced_gain=0.15, t0_boost=1.0)
lpc_shift_full = repeat_to_len(lpc_shift, dry_mono.shape[0])
wav_write(os.path.join(AUDIO, "stem_lpc_pitchshift_beta112.wav"),
          lpc_shift_full, SR, 1)
print("LPC pitch-shift (beta=%.2f) dur: %.2f s" % (beta, lpc_shift_full.shape[0] / SR))

# ----------------------------------------------------------------------------
# Step 6. Full mix: dry stereo source + LPC resynth color, loudness-gained
# ----------------------------------------------------------------------------
def to_stereo(mono):
    # tiny width via delayed copy
    d = np.zeros_like(mono)
    delay = int(0.0008 * SR)
    d[delay:] = mono[:-delay]
    return np.stack([mono, d], axis=1)

# Normalize LPC vocal to sit as a color layer under/over the dry
lv = lpc_vocal_full / (np.max(np.abs(lpc_vocal_full)) + 1e-9)
ls2 = to_stereo(lv)

dry_st2 = dry_st.copy()
target_len = max(dry_st2.shape[0], ls2.shape[0])
def pad_st(image, ln):
    if image.shape[0] < ln:
        pad = np.zeros((ln - image.shape[0], image.shape[1]))
        return np.concatenate([image, pad], axis=0)
    return image[:ln]
dry2 = pad_st(dry_st2, target_len)
ls2 = pad_st(ls2, target_len)

# Blend: dry full arrangement (0.9) + LPC vocal color (0.35)
mix = 0.9 * dry2 + 0.35 * ls2
mix_peak = np.max(np.abs(mix))
if mix_peak > 0:
    mix = mix / mix_peak * 0.89
wav_write(os.path.join(AUDIO, "SP028-LPC-country-uke-fullmix.wav"), mix, SR, 2)
print("full mix dur:", round(mix.shape[0] / SR, 2), "s peak:", round(mix_peak, 3))

# ----------------------------------------------------------------------------
# Step 7. Silence / spectral sanity checks
# ----------------------------------------------------------------------------
mono_chk = mix.mean(axis=1)
silent = np.sum(np.abs(mono_chk) < 0.001) / len(mono_chk)
print("full mix silence fraction:", round(silent, 3))
# per-second RMS
secs = int(mix.shape[0] / SR)
rms_per_sec = []
for s in range(secs):
    seg = mono_chk[s * SR:(s + 1) * SR]
    rms_per_sec.append(float(np.sqrt(np.mean(seg ** 2))))
print("RMS per second (first 8):", [round(r, 4) for r in rms_per_sec[:8]])
assert len(mono_chk) > 0 and silent < 0.85

# ----------------------------------------------------------------------------
# Step 8. OGG conversion (Opus, voip, 48k) for Telegram playback
# ----------------------------------------------------------------------------
ogg = os.path.join(AUDIO, "SP028-LPC-country-uke-fullmix.ogg")
subprocess.run([
    "/usr/bin/ffmpeg", "-y", "-i",
    os.path.join(AUDIO, "SP028-LPC-country-uke-fullmix.wav"),
    "-codec:a", "libopus", "-application", "voip", "-b:a", "48k", ogg,
], capture_output=True)
print("ogg size:", os.path.getsize(ogg))

# ----------------------------------------------------------------------------
# Step 9. Provenance + notes
# ----------------------------------------------------------------------------
prov = {
    "job": "nightly SP production",
    "composition_source": {
        "path": MIDI_SRC,
        "sha256": src_sha,
        "tracks": ["Lead Vocal", "Harmony Vox", "Acoustic Guitar",
                   "Electric Guitar", "Bass", "Drums", "Fiddle", "Pedal Steel"],
        "tempo_bpm": 96.0,
        "time_signature": "4/4",
        "total_notes": 1960,
    },
    "production_method": {
        "id": "SP-028",
        "name": "Linear Predictive Coding (LPC) Synthesis",
        "layer": "Synthesis Engines",
        "description": ("Source-filter all-pole model. Autocorrelation + "
                        "Levinson-Durbin extracts spectral envelope (formants); "
                        "re-excitation with glottal impulse train / noise "
                        "resynthesizes with formant-preserving pitch shift and "
                        "vocoder-style timbre transfer."),
    },
    "params": {
        "order_p": 16,
        "frame_ms": 30, "hop_ms": 10,
        "pre_emphasis_alpha": 0.97,
        "voicing_threshold": 0.5,
        "pitch_shift_beta": beta,
        "blend_dry": 0.9, "blend_lpc": 0.35,
        "sample_rate": SR,
    },
    "outputs": {
        "full_mix_wav": "Audio/SP028-LPC-country-uke-fullmix.wav",
        "full_mix_ogg": "Audio/SP028-LPC-country-uke-fullmix.ogg",
        "stem_lpc_vocal": "Audio/stem_lpc_vocal_resynth.wav",
        "stem_lpc_pitchshift": "Audio/stem_lpc_pitchshift_beta112.wav",
        "original_midi": "MIDI/original_v2_country_unitmatrix.mid",
    },
    "analysis": {
        "lpc_frames": len(frames),
        "voiced_fraction": round(float(voiced_frac), 3),
        "voiced_pitch_hz_mean": round(float(np.mean(pitches_hz)), 1) if pitches_hz else None,
        "fullmix_peak": round(float(mix_peak), 4),
        "fullmix_silence_fraction": round(float(silent), 4),
        "fullmix_dur_s": round(float(mix.shape[0] / SR), 2),
    },
}
with open(os.path.join(PROJ, "provenance.json"), "w") as f:
    json.dump(prov, f, indent=2)
print("provenance written")

# LPC formant grid viz (ASCII): first 20 s of voicing/energy
with open(os.path.join(ANALYSIS, "lpc_formant_grid.txt"), "w") as f:
    f.write("SP-028 LPC analysis grid (region 0-30s, hop 10ms)\n")
    f.write("voiced frames (V=voiced, .=unvoiced), 400 frames shown\n")
    row = []
    for i, fr in enumerate(frames[:400]):
        row.append('V' if fr['voiced'] else '.')
    for i in range(0, len(row), 80):
        f.write("".join(row[i:i + 80]) + "\n")
    f.write("\nVoiced pitch contour (Hz), downsample x16:\n")
    pts = melody_pitch[::16]
    mmin = min([p for p in pts if p > 0], default=60)
    mmax = max([p for p in pts if p > 0], default=400)
    rng_p = mmax - mmin
    for p in pts:
        if p <= 0:
            f.write("-\n")
        else:
            nbar = int(30 * (p - mmin) / (rng_p + 1e-9))
            f.write("#" * nbar + "\n")
print("grid viz written")
print("ALL DONE")