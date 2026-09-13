#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""SP-073 MUSIC BOX production pass -- cron 2026-09-13.

Source composition : Styles/Blues/027-delta-blues-shack/MIDI/027_delta_blues.mid
                     (Delta Blues, 72 BPM, A minor pentatonic / blues
                      hexatonic, 52 bars, 4 voices)
Method (registry)  : SP-073 -> sound.synthesis.music_box
                     "Twin-Detuned-Comb Music Box Modal Synthesis
                      (Muro Box N40-style)"
Selection source   : workflows.musicom_workflow.SP_METHODS (implemented registry)
Layer discipline   : ABSOLUTE layer -- twin-comb tine synthesis replaces the
                     production layer for ALL voices (lead, harmony, bass and
                     the percussion track, which has no tine equivalent and is
                     re-mapped into the tine register -- documented below).

Chain (order fixed):
  dry SoundFont mix (FluidSynth, internal reverb/chorus OFF) -- reference
  + dry per-track stems (RenderPipeline.render_stems, FX OFF)
  -> per-voice TwinCombMusicBox render (own decay/detune/pan/mechanics/jitter)
  -> explicit velocity gain (render_note() peak-normalizes each note to 0.9,
     which erases dynamics -> clip((vel/90)**1.5, 0.22, 1.30) at the call site)
  -> voice bus sum -> peak-normalize 0.89
  -> normalize_to_lufs(-14) -> Limiter(-1.0 dBFS) LAST

Memory discipline (this box has ~3.9 GB RAM): voices are rendered one at a
time, written to a wet-stem WAV, pitch-verified in place, then freed; every
long buffer is float32 and the dry stereo pair is dropped after its mono
summary is taken.  The first run OOM-killed (exit 137) holding four float64
voice buses plus the dry mix plus the mix copy simultaneously.
"""
import hashlib
import json
import os
import subprocess
import time
import wave
from pathlib import Path

import numpy as np
import mido

from sound.synthesis.music_box import (TwinCombMusicBox, TINE_RATIOS,
                                       midi_to_freq, DEFAULT_DETUNE_CENTS)
from sound.render.fluidsynth import discover_soundfont
from sound.render.pipeline import RenderPipeline
from sound.effects.mastering import normalize_to_lufs, measure_lufs, Limiter
from sound.effects.subharmonic import pitch_frame

SRC = Path('/opt/data/repos/musicom/projects/Styles/Blues/027-delta-blues-shack/'
           'MIDI/027_delta_blues.mid')
OUT = Path('/opt/data/repos/musicom/projects/Styles/Production/'
           'SP073-musicbox-delta-blues')
AUDIO = OUT / 'Audio'
STEMS_DRY = AUDIO / 'stems_dry'
STEMS_WET = AUDIO / 'stems_wet'
MIDIDIR = OUT / 'MIDI'
ANALYSIS = OUT / 'Analysis'
for d in (AUDIO, STEMS_DRY, STEMS_WET, MIDIDIR, ANALYSIS):
    d.mkdir(parents=True, exist_ok=True)

SR = 44100
FLUID = os.environ.get('MUSICOM_FLUIDSYNTH',
                       '/opt/data/micromamba/envs/musicom/bin/fluidsynth')
FFMPEG = '/usr/bin/ffmpeg'
SF = discover_soundfont()
assert SF and os.path.exists(SF), 'no soundfont found'
print('soundfont:', SF, flush=True)

# --------------------------------------------------------------- source parse
mid = mido.MidiFile(str(SRC))
tpb = mid.ticks_per_beat
tempo = None
tsig = None
for m in mid.tracks[0]:
    if m.type == 'set_tempo' and tempo is None:
        tempo = m.tempo
    if m.type == 'time_signature' and tsig is None:
        tsig = (m.numerator, m.denominator)
assert tempo
spt = tempo / 1e6 / tpb
BPM = 60e6 / tempo
BAR_TICKS = tpb * 4              # musical bar = 4 quarters (source tsig is 12/8;
print('source MIDI: tpb={} tempo={} ({:.3f} BPM) tsig={} tracks={}'.format(
    tpb, tempo, BPM, tsig, len(mid.tracks)), flush=True)

DRUM_CH = 9
VOICES = []          # (track_index, name, program, channel)
for i, track in enumerate(mid.tracks):
    prog, ch, n = None, None, 0
    for m in track:
        if m.type == 'program_change' and prog is None:
            prog = m.program
            ch = m.channel
        if m.type == 'note_on' and m.velocity:
            n += 1
            if ch is None:
                ch = getattr(m, 'channel', 0)
    if n >= 2:
        VOICES.append((i, 'track{:02d}'.format(i), prog, ch))
for v in VOICES:
    print('  voice track {}: prog={} ch={}'.format(v[0], v[2], v[3]),
          flush=True)
assert len(VOICES) == 4


def parse_notes(track_idx):
    """-> [(start_s, dur_s, note, velocity)] with absolute ticks -> seconds."""
    t = 0
    open_notes = {}
    out = []
    for m in mid.tracks[track_idx]:
        t += m.time
        if m.type == 'note_on' and m.velocity:
            open_notes.setdefault(m.note, []).append((t, m.velocity))
        elif m.type == 'note_off' or (m.type == 'note_on' and not m.velocity):
            if open_notes.get(m.note):
                st, vel = open_notes[m.note].pop(0)
                out.append((st * spt, (t - st) * spt, m.note, vel))
    out.sort()
    return out


PITCHED = []   # (track, name, program, notes)
DRUM_NOTES = []
for (tr, name, prog, ch) in VOICES:
    notes = parse_notes(tr)
    if ch == DRUM_CH:
        DRUM_NOTES = notes
    else:
        PITCHED.append((tr, name, prog, notes))
print('pitched note events:', sum(len(p[3]) for p in PITCHED),
      ' percussive:', len(DRUM_NOTES), flush=True)
DUR_S = max(n[0] + n[1] for n in DRUM_NOTES)
for (tr, name, prog, notes) in PITCHED:
    DUR_S = max(DUR_S, max(n[0] + n[1] for n in notes))
DUR_S = float(np.ceil(DUR_S * 1000) / 1000.0)
BAR_S = BAR_TICKS * spt
print('duration: {:.3f} s  bar {:.4f} s -> {:.2f} bars'.format(
    DUR_S, BAR_S, DUR_S / BAR_S), flush=True)

# ------------------------------------------------------------- voice profiles
# Music box tine banks have no percussion and no true bass register, so the
# absolute layer (a) renders every pitched voice as tines with its own
# decay / detune / pan and (b) re-maps the 4 percussion classes into the tine
# register by documented transposition.  Tine ring time == the module's
# `decay`; decays are matched to each voice's note density (printed below) --
# a 1251-note lead line at ~7 notes/s cannot share the harmony's long ring
# without turning the texture to mud (measured: chroma match drops from
# 0.92-0.95 at decay 0.25-0.55 while strict per-onset pitch match falls
# 51% -> 32%, so the lead uses the short end).
FADE_GUARD = 2.6      # render each segment out to exp(-2.6) ~ 7.4 %
FADE_MS = 30.0        # cosine fade on the segment tail (click guard)
VOICE_CFG = {
    25: dict(label='Resonator Guitar lead', kind='tine', decay=0.32,
             brightness=1.00, detune=DEFAULT_DETUNE_CENTS, pan=-0.22,
             mechanics=0.16, jitter=3.0, tail=1.0, gain=1.00),
    26: dict(label='Acoustic Slide harmony', kind='tine', decay=1.10,
             brightness=0.70, detune=7.0, pan=0.38,
             mechanics=0.13, jitter=3.5, tail=1.6, gain=0.80),
    32: dict(label='Thumb Bass sub', kind='tine', decay=1.00,
             brightness=0.55, detune=14.0, pan=0.00,
             mechanics=0.20, jitter=1.8, tail=1.6, gain=0.62),
}
# Percussion -> tine register.  The source kit is stomp(36)/clap(39)/
# closed-hat(42)/open-hat(46) on a 2-to-3-step grid.  Tines have no noise
# burst, so each class is realised as a SHORT tine struck at a transposed
# pitch whose ring + brightness order reproduces kick < clap < hat.
#
# DECAYS ARE SET BY MEASUREMENT, not by ear-guessing: the percussion grid at
# 72 BPM puts hits as close as 3 sixteenths (0.156 s) apart, so any tine ring
# >= 0.45 s is still at ~25 % amplitude when the next hit lands and the
# band-limited onset contrast collapses.  Onset-contrast sweep on the isolated
# stomp bus (Analysis/kick_shift.log):
#   decay 0.45 s -> 19 % of onsets clear a 2x local rise
#   decay 0.22 s -> 50 %
#   decay 0.12 s -> 97 %   <-- chosen
# Transposition sweep at 0.12 s: shift -12 (32.7 Hz) 97 %, 0 (65.4 Hz) 97 %,
# +12 (130.8 Hz) 99 % -- all usable; -12 keeps the stomp in the sub register
# where the source kick sat, so it is kept for register fidelity.
PERC_CFG = {
    36: dict(label='Stomp/kick', shift=-12, decay=0.12, brightness=0.55,
             detune=10.0, mechanics=0.30, jitter=4.0, tail=0.30, gain=0.95,
             pan=0.0),
    39: dict(label='Clap', shift=12, decay=0.14, brightness=1.15,
             detune=12.0, mechanics=0.40, jitter=6.0, tail=0.25, gain=0.55,
             pan=0.28),
    42: dict(label='Closed hat', shift=36, decay=0.12, brightness=1.35,
             detune=16.0, mechanics=0.50, jitter=7.0, tail=0.20, gain=0.42,
             pan=None),      # alternate L/R
    46: dict(label='Open hat', shift=31, decay=0.30, brightness=1.25,
             detune=14.0, mechanics=0.45, jitter=7.0, tail=0.40, gain=0.45,
             pan=-0.30),
}
for prog in [v[2] for v in VOICES if v[3] != DRUM_CH]:
    assert prog in VOICE_CFG, 'no profile for program {}'.format(prog)


def vel_gain(vel, ref=90.0, lo=0.22, hi=1.30):
    """render_note() peak-normalizes every note to 0.9 -> re-inject dynamics."""
    return float(np.clip((vel / ref) ** 1.5, lo, hi))


_FADE_W = None


def cosine_fade(seg):
    """Fade the last FADE_MS of a segment (module truncates modes at 4*tau)."""
    global _FADE_W
    k = int(FADE_MS * 0.001 * SR)
    if seg.shape[0] <= k:
        return seg
    if _FADE_W is None:
        _FADE_W = 0.5 * (1.0 + np.cos(np.linspace(0.0, np.pi, k))).astype(
            np.float32)
    seg[-k:] *= _FADE_W[:, None]
    return seg


def write_wav_stereo(path, arr):
    a = np.clip(np.asarray(arr, dtype=np.float32), -1.0, 1.0)
    with wave.open(str(path), 'wb') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes((a * 32767.0).astype(np.int16).tobytes())


def load_wav(path, dtype=np.float32):
    with wave.open(str(path), 'rb') as wf:
        n, ch, rate = wf.getnframes(), wf.getnchannels(), wf.getframerate()
        raw = np.frombuffer(wf.readframes(n), dtype=np.int16).astype(
            dtype) / 32768.0
    assert rate == SR
    if ch == 2:
        return raw.reshape(-1, 2)
    return np.column_stack([raw, raw])


def fft_dom_peak(win, lo=50.0, hi=1000.0):
    spec = np.abs(np.fft.rfft(win * np.hanning(len(win))))
    fr = np.fft.rfftfreq(len(win), 1.0 / SR)
    a = np.searchsorted(fr, lo)
    b = np.searchsorted(fr, hi)
    return float(fr[np.argmax(spec[a:b]) + a])


def harmonic_ratio(win, f0, nharm=8):
    spec = np.abs(np.fft.rfft(win * np.hanning(len(win)))) ** 2
    tot = float(np.sum(spec[1:]))
    acc = 0.0
    for k in range(1, nharm + 1):
        fk = f0 * k
        if fk >= SR / 2:
            break
        i = int(round(fk * len(win) / SR))
        lo, hi = max(1, i - 3), min(len(spec) - 1, i + 4)
        acc += float(np.sum(spec[lo:hi + 1]))
    return acc / max(tot, 1e-12)


def centroid(x):
    spec = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    fr = np.fft.rfftfreq(len(x), 1.0 / SR)
    s = float(np.sum(spec))
    return float(np.sum(fr * spec) / s) if s > 0 else 0.0


# ------------------------------------------------------- dry reference render
dry_full = OUT / 'dry_full_mix.wav'
print('rendering dry SoundFont mix (internal FX OFF) ...', flush=True)


def fluid_render(midi_path, wav_path):
    cmd = [FLUID, '-ni', '-g', '1.2',
           '-o', 'synth.reverb.active=no', '-o', 'synth.chorus.active=no',
           '-F', str(wav_path), '-r', str(SR), SF, str(midi_path)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    if r.returncode != 0 or not os.path.exists(wav_path):
        raise RuntimeError('fluidsynth failed: ' + (r.stderr or r.stdout)[-400:])
    sz = os.path.getsize(wav_path)
    assert 40000 < sz < 200 * 1024 * 1024, 'WAV size {} B'.format(sz)


fluid_render(SRC, dry_full)
dry = load_wav(dry_full)
dry_mono = dry.mean(axis=1)
dry_peak = float(np.abs(dry).max())
del dry
print('dry_full_mix: {:.2f}s peak {:.3f}'.format(len(dry_mono) / SR, dry_peak),
      flush=True)

print('rendering dry per-track stems (RenderPipeline, FX OFF) ...', flush=True)
pipe = RenderPipeline(soundfont_path=SF)
dry_stems = pipe.render_stems(str(SRC), str(STEMS_DRY), format='wav')
for k in sorted(dry_stems):
    print('   {} {} B'.format(k, os.path.getsize(dry_stems[k])), flush=True)


def silence_stats(mono):
    sil = float(np.sum(np.abs(mono) < 0.001) / len(mono))
    rms = [float(np.sqrt(np.mean(mono[i:i + SR] ** 2)))
           for i in range(0, len(mono), SR)]
    return sil, rms


sil_dry, rms_dry = silence_stats(dry_mono)

# ------------------------------------------------------------- wet synthesis
N_MIX = int(np.ceil((DUR_S + 2.2) * SR))
wet = np.zeros((N_MIX, 2), dtype=np.float32)
print('SP-073 twin-comb tine synthesis (absolute layer, all voices) ...',
      flush=True)
t_start = time.time()
wet_stems = {}
per_note = []          # (voice label, note, dom_hz, hit)  -- strict slots
voice_note_stats = {}


def mixin(buf, gain):
    global wet
    n = min(N_MIX, buf.shape[0])
    wet[:n] += buf[:n] * np.float32(gain)


def render_voice(tr, name, prog, notes):
    """Render one pitched voice; verify pitch in place; mix in; free."""
    cfg = VOICE_CFG[prog]
    vname = cfg['label']
    mb = TwinCombMusicBox(sample_rate=SR,
                          detune_cents=float(cfg['detune']),
                          decay=float(cfg['decay']),
                          pan=float(cfg['pan'] or 0.0))
    mb.comb_a.brightness = float(cfg['brightness'])
    mb.comb_b.brightness = float(cfg['brightness']) * 0.97
    mb.mechanics = float(cfg['mechanics'])
    mb.jitter_cents = float(cfg['jitter'])
    buf = np.zeros((N_MIX, 2), dtype=np.float32)
    t0 = time.time()
    onset_arr = np.array([n[0] for n in notes])
    for i, (st, dur, note, vel) in enumerate(notes):
        seg = mb.render_note(note,
                             duration=min(dur + FADE_GUARD * float(cfg['decay']),
                                          8.0),
                             seed=20260913 + i)
        seg = np.asarray(seg, dtype=np.float32)
        seg = cosine_fade(seg) * np.float32(vel_gain(vel))
        s = int(st * SR)
        e = min(N_MIX, s + seg.shape[0])
        if s >= N_MIX or e <= s:
            continue
        buf[s:e] += seg[:e - s]
    dens = len(notes) / max(DUR_S, 1e-9)
    print('   {} : {} notes ({:.2f}/s, decay {:.2f} s) in {:.1f} s  peak {:.3f}'
          .format(vname, len(notes), dens, cfg['decay'], time.time() - t0,
                  float(np.abs(buf).max())), flush=True)
    # stem (peak-normalized, independent of the bus gain)
    p = float(np.abs(buf).max())
    stem = buf * np.float32(0.89 / p) if p > 0 else buf.copy()
    sp = STEMS_WET / ('track_%s.wav' % vname.replace(' ', '_'))
    write_wav_stereo(sp, stem)
    wet_stems[vname] = {'path': str(sp), 'bytes': os.path.getsize(sp),
                        'peak': round(p, 4)}
    del stem
    # pitch verification on this voice's own isolated bus; only note slots with
    # NO other onset inside the window count (strict attribution)
    mono = buf.mean(axis=1)
    ok = amb = 0
    # gap-aware analysis window: the lead line runs at ~7 notes/s (138 ms
    # between onsets), so a fixed 150 ms window straddles the NEXT note for
    # most of the line and reports "ambiguous".  Bound the window to 80 % of
    # the gap to the next onset, floor 30 ms (>= ~7 cycles of the lowest lead
    # tine at 220 Hz).
    MIN_W, MAX_W = 0.030, 0.150
    for (st, dur, note, vel) in notes:
        nxt = onset_arr[onset_arr > st + 1e-6]
        gap = float(nxt.min() - st) if len(nxt) else 9.9
        wl = min(max(dur, MIN_W), MAX_W, max(MIN_W, 0.8 * gap))
        i0 = int(st * SR)
        win = mono[i0:i0 + int(wl * SR)]
        if len(win) < 1024 or float(np.abs(win).max()) < 0.004:
            continue
        clean = gap >= wl - 1e-9
        if not clean:
            amb += 1
            continue
        dom = fft_dom_peak(win)
        f0 = midi_to_freq(note)
        hit = any(abs(dom - f0 * h) / (f0 * h) < 0.02 for h in (1, 2, 3, 4))
        per_note.append((vname, note, round(dom, 1), bool(hit)))
        ok += int(hit)
    voice_note_stats[vname] = {'notes': len(notes), 'strict_slots': ok + 0,
                               'ambiguous_slots': amb}
    print('      strict onset-slot pitch match: {}/{} ({} ambiguous skipped)'
          .format(ok, ok + amb, amb), flush=True)
    mixin(buf, cfg['gain'])
    del buf, mono


for k, (tr, name, prog, notes) in enumerate(PITCHED):
    render_voice(tr, name, prog, notes)

# --- percussion tines ------------------------------------------------------
print('   Percussion tines : {} hits'.format(len(DRUM_NOTES)), flush=True)
t0 = time.time()
pname = 'Percussion tines'
pbuf = np.zeros((N_MIX, 2), dtype=np.float32)
mb_cache = {}
pan_flip = 0
for i, (st, dur, note, vel) in enumerate(DRUM_NOTES):
    cfg = PERC_CFG.get(note, PERC_CFG[42])
    pan = cfg['pan']
    if pan is None:
        pan = 0.34 if (pan_flip % 2 == 0) else -0.34
        pan_flip += 1
    key = (note, round(pan, 3))
    if key not in mb_cache:
        mb = TwinCombMusicBox(sample_rate=SR, detune_cents=cfg['detune'],
                              decay=cfg['decay'], pan=pan)
        mb.comb_a.brightness = cfg['brightness']
        mb.comb_b.brightness = cfg['brightness'] * 0.97
        mb.mechanics = cfg['mechanics']
        mb.jitter_cents = cfg['jitter']
        mb_cache[key] = mb
    seg = mb_cache[key].render_note(note + cfg['shift'],
                                    duration=FADE_GUARD * cfg['decay'],
                                    seed=20260913 + 7777 + i)
    seg = np.asarray(seg, dtype=np.float32)
    seg = cosine_fade(seg) * np.float32(vel_gain(vel) * cfg['gain'])
    s = int(st * SR)
    e = min(N_MIX, s + seg.shape[0])
    if s < N_MIX and e > s:
        pbuf[s:e] += seg[:e - s]
print('   Percussion tines : {} hits in {:.1f} s  peak {:.3f}'.format(
    len(DRUM_NOTES), time.time() - t0, float(np.abs(pbuf).max())), flush=True)
p = float(np.abs(pbuf).max())
sp = STEMS_WET / ('track_%s.wav' % pname.replace(' ', '_'))
write_wav_stereo(sp, pbuf * np.float32(0.89 / p) if p > 0 else pbuf)
wet_stems[pname] = {'path': str(sp), 'bytes': os.path.getsize(sp),
                    'peak': round(p, 4)}
mixin(pbuf, 1.0)
del pbuf

# percussive texture ordering, measured on ISOLATED class buses
perc_centroids = {}
for gm, cfg in PERC_CFG.items():
    sub = [n for n in DRUM_NOTES if n[2] == gm]
    if not sub:
        continue
    mb = TwinCombMusicBox(sample_rate=SR, detune_cents=cfg['detune'],
                          decay=cfg['decay'], pan=0.0)
    mb.comb_a.brightness = cfg['brightness']
    mb.comb_b.brightness = cfg['brightness'] * 0.97
    mb.mechanics = cfg['mechanics']
    mb.jitter_cents = cfg['jitter']
    n = int((sub[-1][0] + 0.6) * SR) + SR
    b = np.zeros((n, 2), dtype=np.float32)
    for i, (st, dur, note, vel) in enumerate(sub):
        seg = mb.render_note(note + cfg['shift'],
                             duration=FADE_GUARD * cfg['decay'],
                             seed=20260913 + i)
        seg = np.asarray(seg, dtype=np.float32)
        seg = cosine_fade(seg) * np.float32(vel_gain(vel) * cfg['gain'])
        s = int(st * SR)
        e = min(n, s + seg.shape[0])
        if s < n and e > s:
            b[s:e] += seg[:e - s]
    perc_centroids[gm] = round(centroid(b.mean(axis=1)), 1)
    del b
print('percussion centroids (Hz):', perc_centroids, flush=True)
texture_ok = (perc_centroids.get(36, 0) < perc_centroids.get(39, 1e9) <
              perc_centroids.get(42, 1e9))
print('synthesis total {:.1f} s'.format(time.time() - t_start), flush=True)

# ------------------------------------------------------------------ master
peak_raw = float(np.abs(wet).max())
if peak_raw > 0:
    wet *= np.float32(0.89 / peak_raw)
print('voice-bus sum: raw peak {:.4f} -> 0.89'.format(peak_raw), flush=True)
mix = normalize_to_lufs(wet, target_lufs=-14.0, sample_rate=SR)
del wet
mix = Limiter(threshold_db=-1.0, release_ms=100.0, sample_rate=SR).process(mix)
mix = np.asarray(mix, dtype=np.float32)
mix = np.nan_to_num(mix, nan=0.0, posinf=0.0, neginf=0.0)
lufs_mix = measure_lufs(mix, SR)
peak_mix = float(np.abs(mix).max())
out_wav = OUT / 'SP073-musicbox-delta-blues.wav'
write_wav_stereo(out_wav, mix)
print('mix: LUFS {:.2f} peak {:.4f} dur {:.2f}s'.format(
    lufs_mix, peak_mix, len(mix) / SR), flush=True)
assert 0.3 < peak_mix <= 1.0

mix_mono = mix.mean(axis=1)
del mix
DURATION_S = round(len(mix_mono) / SR, 3)
sil_wet, rms_wet = silence_stats(mix_mono)

# dry-vs-wet correlation: onset envelope (timing) + raw waveform (spectral).
# A tine render is a different signal from a SoundFont render, so the raw
# waveform correlation is NOT expected to be high; what must hold is that the
# rhythmic grid survives.  Both numbers are reported.
def onset_env(x, hop=256):
    k = len(x) // hop * hop
    e = np.abs(x[:k]).reshape(-1, hop).max(axis=1)
    d = np.diff(e, prepend=e[0])
    d[d < 0] = 0.0
    return d


n_cmp = min(len(mix_mono), len(dry_mono))
env_w = onset_env(mix_mono[:n_cmp])
env_d = onset_env(dry_mono[:n_cmp])
corr_env = float(np.corrcoef(env_w, env_d)[0, 1])
dot = float(np.dot(env_w, env_d))
corr_cos = dot / max(float(np.linalg.norm(env_w) * np.linalg.norm(env_d)), 1e-12)
env_ratio = float(np.sum(env_w) / max(np.sum(env_d), 1e-12))
print('onset-envelope corr {:.3f} (cosine {:.3f}, energy ratio {:.3f})'.format(
    corr_env, corr_cos, env_ratio), flush=True)
del env_w, env_d
wave_corr = float(np.corrcoef(mix_mono[:n_cmp] * 100.0,
                              dry_mono[:n_cmp] * 100.0)[0, 1])
del dry_mono

# ------------------------------------------------------- pitch verification
print('pitch verification ...', flush=True)
note_rate = (sum(1 for x in per_note if x[3]) / max(1, len(per_note)))
print('   per-note strict slots: {}/{} ({:.1%})'.format(
    sum(1 for x in per_note if x[3]), len(per_note), note_rate), flush=True)

# 0.5 s mix windows -- SP-071 style (chord-member test on dense textures)
note_events = [(st, dur, note) for (tr, name, prog, notes) in PITCHED
               for (st, dur, note, vel) in notes]
windows = []
checked = hits = 0
auto_frames = auto_unpitched = 0
t = 0.0
while t + 0.5 <= len(mix_mono) / SR:
    i0 = int(t * SR)
    win = mix_mono[i0:i0 + int(0.5 * SR)]
    if float(np.abs(win).max()) < 0.005:
        t += 0.5
        continue
    dom = fft_dom_peak(win)
    exp = sorted({ne for (st, dn, ne) in note_events
                  if st < t + 0.5 and (st + max(dn, 0.05)) > t})
    acf = pitch_frame(win, SR, lo=40.0, hi=1000.0)
    auto_frames += 1
    auto_unpitched += int(acf <= 0.0)
    hit = False
    if exp:
        checked += 1
        for ne in exp:
            if any(abs(dom - midi_to_freq(ne) * h) / (midi_to_freq(ne) * h) < 0.02
                   for h in (1, 2, 3, 4)):
                hit = True
                break
        hits += int(hit)
    hr = harmonic_ratio(win, midi_to_freq(min(exp)) if exp else 220.0)
    windows.append({'t': round(t, 2), 'dom_hz': round(dom, 1),
                    'acf_hz': round(acf, 1), 'hit': bool(hit),
                    'harm_ratio': round(hr, 3), 'expected_notes': exp})
    t += 0.5

mix_hit_rate = hits / max(1, checked)
med_harm = float(np.median([w['harm_ratio'] for w in windows])) if windows else 0.0
med_dom = float(np.median([w['dom_hz'] for w in windows])) if windows else 0.0
acf_ok = auto_unpitched < 0.5 * max(1, auto_frames)

# chroma comparison: source MIDI pitch classes vs detected dominant partials
pc_src = np.zeros(12)
for (tr, name, prog, notes) in PITCHED:
    for (st, dur, note, vel) in notes:
        pc_src[note % 12] += max(dur, 0.05)
pc_src /= pc_src.sum()
pc_out = np.zeros(12)
for j in range(0, len(mix_mono) - 4096, 4096):
    w = mix_mono[j:j + 4096]
    if float(np.abs(w).max()) < 0.004:
        continue
    f = fft_dom_peak(w)
    if f <= 0:
        continue
    m = 12 * np.log2(f / 440.0) + 69
    pc_out[int(round(m)) % 12] += 1
pc_out /= max(pc_out.sum(), 1)
chroma_corr = float(np.corrcoef(pc_src, pc_out)[0, 1])
del pc_src, pc_out

verdict = 'PASS' if (mix_hit_rate >= 0.60 and med_harm >= 0.30 and acf_ok and
                     texture_ok and chroma_corr >= 0.70 and
                     env_ratio > 0.8) else 'REVIEW'
print('mix windows={} checked={} hit_rate={:.3f} median_harm={:.3f} '
      'note_strict_rate={:.3f} chroma_corr={:.3f} acf_unpitched={}/{} '
      'texture_ok={} env_ratio={:.3f} -> {}'.format(
          len(windows), checked, mix_hit_rate, med_harm, note_rate,
          chroma_corr, auto_unpitched, auto_frames, texture_ok, env_ratio,
          verdict), flush=True)

# ------------------------------------------------------------------- OGG
ogg = OUT / 'SP073-musicbox-delta-blues.ogg'
subprocess.run([FFMPEG, '-y', '-loglevel', 'error', '-i', str(out_wav),
                '-codec:a', 'libopus', '-application', 'voip', '-b:a', '48k',
                str(ogg)], check=True)
assert os.path.getsize(ogg) > 5000
print('ogg: {} B'.format(os.path.getsize(ogg)), flush=True)

# ------------------------------------------------------------- analysis files
with open(ANALYSIS / 'pitch_verification.json', 'w') as f:
    json.dump({'verdict': verdict, 'mix_hit_rate': round(mix_hit_rate, 4),
               'median_harmonic_ratio': round(med_harm, 4),
               'median_dom_hz': med_dom,
               'note_strict_slots': len(per_note),
               'note_strict_rate': round(note_rate, 4),
               'per_voice_note_stats': voice_note_stats,
               'chroma_corr': round(chroma_corr, 4),
               'auto_frames': auto_frames,
               'auto_unpitched_frames': auto_unpitched,
               'onset_env_corr': round(corr_env, 4),
               'onset_env_cosine': round(corr_cos, 4),
               'onset_env_energy_ratio': round(env_ratio, 4),
               'wave_corr_dry_vs_wet': round(wave_corr, 4),
               'percussion_centroids_hz': perc_centroids,
               'texture_order_ok': bool(texture_ok),
               'per_note': [{'voice': v, 'note': n, 'dom_hz': d, 'hit': h}
                            for (v, n, d, h) in per_note],
               'windows': windows}, f, indent=2)

with open(ANALYSIS / 'render_stats.json', 'w') as f:
    json.dump({'duration_s': DURATION_S,
               'bpm': round(BPM, 4), 'bars': round(DUR_S / BAR_S, 2),
               'silence_ratio_dry': round(sil_dry, 4),
               'silence_ratio_wet': round(sil_wet, 4),
               'rms_per_second_wet': [round(x, 4) for x in rms_wet],
               'rms_per_second_dry': [round(x, 4) for x in rms_dry],
               'lufs_wet': round(lufs_mix, 2), 'peak_wet': round(peak_mix, 4),
               'wet_stems': wet_stems}, f, indent=2)
del mix_mono

# ------------------------------------------------------- grid visualization
from structures import MusicUnit, MusicEvent, UnitMatrix
from visualization.grid import write_grid_visualization

SECTIONS = [('Intro', 2), ('Verse 1', 12), ('Verse 2', 12),
            ('Guitar Solo', 12), ('Verse 3', 12), ('Outro', 2)]
BOUNDS = []
acc = 0
for nm, bars in SECTIONS:
    BOUNDS.append((nm, acc * BAR_TICKS, (acc + bars) * BAR_TICKS))
    acc += bars
matrix = UnitMatrix(shape=(len(VOICES), len(SECTIONS)))
for r in range(len(VOICES)):
    for s in range(len(SECTIONS)):
        matrix.set_unit((r, s), MusicUnit(events=[]))
for r, (tr, name, prog, ch) in enumerate(VOICES):
    t = 0
    open_notes = {}
    for m in mid.tracks[tr]:
        t += m.time
        if m.type == 'note_on' and m.velocity:
            open_notes.setdefault(m.note, []).append(t)
        elif m.type == 'note_off' or (m.type == 'note_on' and not m.velocity):
            if open_notes.get(m.note):
                st = open_notes[m.note].pop(0)
                for si, (nm, b0, b1) in enumerate(BOUNDS):
                    if b0 <= st < b1:
                        matrix.get_unit((r, si)).add_event(
                            MusicEvent(m.note, 90, int(st - b0), int(t - b0)))
                        break
for r in range(len(VOICES)):
    for s in range(len(SECTIONS)):
        u = matrix.get_unit((r, s))
        sec_len = BOUNDS[s][2] - BOUNDS[s][1]
        if len(u.events) == 0:
            u.add_event(MusicEvent(0, 0, sec_len - 10, sec_len))
        else:
            for e in u.events:
                if e.end_tick > sec_len:
                    e.end_tick = sec_len
            if max(e.end_tick for e in u.events) < sec_len:
                u.add_event(MusicEvent(0, 0, sec_len - 10, sec_len))
write_grid_visualization(
    matrix, str(ANALYSIS / 'grid_visualization.txt'),
    ticks_per_character=480,
    voice_names=[v[1] + (' (percussion)' if v[3] == DRUM_CH else '')
                 for v in VOICES],
    bpm=int(round(BPM)), mode='A pentatonic minor / blues hexatonic')
print('grid ->', ANALYSIS / 'grid_visualization.txt', flush=True)

# --------------------------------------------------------------- provenance
import shutil
shutil.copy2(SRC, MIDIDIR / SRC.name)


def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


prov = {
    'job': 'random-style production SP layer-aligned 2026-09-13',
    'method': 'SP-073',
    'module': 'sound.synthesis.music_box',
    'desc': 'Twin-Detuned-Comb Music Box Modal Synthesis (Muro Box N40-style)',
    'registry': 'workflows.musicom_workflow.SP_METHODS',
    'registry_size': 19,
    'eligible_pool': ['SP-021', 'SP-028', 'SP-032', 'SP-033', 'SP-034',
                      'SP-036', 'SP-069', 'SP-070', 'SP-072', 'SP-073',
                      'SP-074', 'SP-075'],
    'excluded_last_7d': ['SP-001', 'SP-011', 'SP-024', 'SP-026', 'SP-035',
                         'SP-037', 'SP-071'],
    'source_midi': str(SRC),
    'out_dir': str(OUT),
    'layer_discipline': 'absolute -- twin-comb tine synthesis replaces the '
                        'production layer for all 4 voices',
    'params': {
        'sample_rate': SR, 'bpm': round(BPM, 4), 'bar_ticks': BAR_TICKS,
        'duration_s': DURATION_S,
        'tine_ratios': list(TINE_RATIOS),
        'voice_profiles': {str(k): {kk: vv for kk, vv in v.items()}
                           for k, v in VOICE_CFG.items()},
        'percussion_map': {str(k): v for k, v in PERC_CFG.items()},
        'velocity_gain': 'clip((vel/90)**1.5, 0.22, 1.30) after render_note() '
                         'peak-normalisation to 0.9',
        'segment_fade_ms': FADE_MS, 'fade_guard': FADE_GUARD,
        'master': {'target_lufs': -14.0, 'limiter_threshold_db': -1.0},
    },
    'soundfont': SF,
    'dry_full_mix': {'path': str(dry_full), 'bytes': os.path.getsize(dry_full),
                     'peak': round(dry_peak, 4),
                     'silence_ratio': round(sil_dry, 4)},
    'dry_stems': {k: os.path.getsize(v) for k, v in dry_stems.items()},
    'wet_stems': wet_stems,
    'wet_full_mix': {'path': str(out_wav), 'bytes': os.path.getsize(out_wav),
                     'ogg': str(ogg), 'ogg_bytes': os.path.getsize(ogg),
                     'lufs': round(lufs_mix, 2), 'peak': round(peak_mix, 4),
                     'silence_ratio': round(sil_wet, 4),
                     'onset_env_corr': round(corr_env, 4),
                     'onset_env_cosine': round(corr_cos, 4),
                     'onset_env_energy_ratio': round(env_ratio, 4),
                     'wave_corr_dry_vs_wet': round(wave_corr, 4),
                     'sha256': sha256(out_wav)},
    'pitch_verification': {'verdict': verdict,
                           'mix_hit_rate': round(mix_hit_rate, 4),
                           'note_strict_rate': round(note_rate, 4),
                           'per_voice_note_stats': voice_note_stats,
                           'chroma_corr': round(chroma_corr, 4),
                           'median_harmonic_ratio': round(med_harm, 4),
                           'auto_unpitched_frames': auto_unpitched,
                           'auto_frames': auto_frames,
                           'texture_order_ok': bool(texture_ok)},
    'synthesis_seconds': round(time.time() - t_start, 1),
}
with open(OUT / 'provenance.json', 'w') as f:
    json.dump(prov, f, indent=2)
print('DONE ->', OUT, flush=True)
