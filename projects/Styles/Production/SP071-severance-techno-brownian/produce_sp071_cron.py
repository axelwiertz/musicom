#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""SP-071 SEVERANCE production pass -- cron 2026-09-12.

Source composition : Styles/Techno/083-techno-brownian/MIDI/083-techno-brownian.mid
                     (Techno, method 048 Reflected Brownian Motion Pitch Diffusion,
                      F natural minor, 128 BPM, 24 bars / 6 sections, 6 voices)
Method (registry)  : SP-071 -> sound.effects.severance
                     "Gated Reverb + Dual-Engine Delay + Glitch Chain +
                      Parallel Band Compressor (ZERO9-style)"
Selection source   : workflows.musicom_workflow.SP_METHODS (implemented registry)
Layer discipline   : ABSOLUTE layer -- the ZERO9 suite replaces the space /
                     echo / glue layer for the WHOLE piece (applied on the full
                     mix bus), and the same chain is applied per voice to ship
                     processed stems too.

Chain (order fixed, documented):
  dry mix (FluidSynth, internal reverb/chorus OFF so SEVERANCE is the only
           space layer)
   -> ParallelBandCompressor   (4-band up/down parallel compression = bus glue)
   -> GatedReverb              (onset-gated tail, spectral declash, movement LFO)
   -> DualEngineDelay          (continuous + granular, serial routing)
   -> RhythmicGlitchChain      (tempo-locked 4-stage, sparse patterns)
   -> 35% spectral declash blend (stacked-peak taming)
   -> normalize_to_lufs(-14)   -> Limiter(-1.0 dBFS) last
"""
import hashlib
import json
import os
import subprocess
import sys
import time
import wave
from pathlib import Path

import numpy as np
import mido

from sound.render.fluidsynth import discover_soundfont
from sound.effects.severance import (
    GatedReverb, DualEngineDelay, RhythmicGlitchChain,
    ParallelBandCompressor, spectral_declash,
)
from sound.effects.mastering import normalize_to_lufs, measure_lufs, Limiter
from sound.effects.subharmonic import pitch_frame

SRC = Path('/opt/data/repos/musicom/projects/Styles/Techno/083-techno-brownian/MIDI/'
           '083-techno-brownian.mid')
OUT = Path('/opt/data/repos/musicom/projects/Styles/Production/SP071-severance-techno-brownian')
AUDIO = OUT / 'Audio'
STEMS_DRY = AUDIO / 'stems_dry'
STEMS_PROC = AUDIO / 'stems_processed'
MIDIDIR = OUT / 'MIDI'
ANALYSIS = OUT / 'Analysis'
for d in (AUDIO, STEMS_DRY, STEMS_PROC, MIDIDIR, ANALYSIS):
    d.mkdir(parents=True, exist_ok=True)

SR = 44100
BPM = 128.0
BEAT = 60.0 / BPM                 # 0.46875 s
SIXTEENTH = BEAT / 4.0            # 0.1171875 s
DOTTED_8TH = 3 * SIXTEENTH        # 0.3515625 s
DOTTED_QTR = 6 * SIXTEENTH        # 0.703125 s
GATE_LEN = BEAT / 2.0             # 0.234375 s = one 8th-note gate

FLUID = os.environ.get('MUSICOM_FLUIDSYNTH', '/opt/data/micromamba/envs/musicom/bin/fluidsynth')
FFMPEG = '/usr/bin/ffmpeg'
SF = discover_soundfont()
assert SF and os.path.exists(SF), 'no soundfont found'
print('soundfont:', SF)

FLUID_BASE = [FLUID, '-ni', '-g', '1.2',
              '-o', 'synth.reverb.active=no',
              '-o', 'synth.chorus.active=no',
              '-F']

# sparse tempo-locked glitch patterns (16 steps = 1 bar of 16ths)
PATTERNS = (
    [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],   # stutter: step 1 + 9
    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],   # reverse: step 8
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],   # bitcrush: step 13
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],   # decimate: OFF
)


def fluid_render(midi_path, wav_path):
    cmd = FLUID_BASE + [str(wav_path), '-r', str(SR), SF, str(midi_path)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    if r.returncode != 0 or not os.path.exists(wav_path):
        raise RuntimeError('fluidsynth failed: ' + (r.stderr or r.stdout)[-500:])
    sz = os.path.getsize(wav_path)
    assert sz > 40000, 'WAV empty ({} B)'.format(sz)
    assert sz < 200 * 1024 * 1024, 'WAV too big ({} B)'.format(sz)


def load_wav(path):
    with wave.open(str(path), 'rb') as wf:
        n = wf.getnframes()
        ch = wf.getnchannels()
        rate = wf.getframerate()
        raw = np.frombuffer(wf.readframes(n), dtype=np.int16).astype(np.float64) / 32768.0
    assert rate == SR, 'rate {} != {}'.format(rate, SR)
    if ch == 2:
        return raw.reshape(-1, 2)
    return np.column_stack([raw, raw])


def write_wav_stereo(path, arr):
    a = np.clip(arr, -1.0, 1.0)
    ints = (a * 32767.0).astype(np.int16)
    with wave.open(str(path), 'wb') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(ints.tobytes())


def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def severance_chain(x, triggers, gate_len=GATE_LEN, tag='', delay_mix=0.45):
    """Absolute-layer ZERO9 suite on one MONO channel.

    NOTE (module semantics): ``DualEngineDelay.process()`` returns the delay
    ENGINE OUTPUT ONLY (cont + gran), i.e. a fully wet, time-shifted copy of
    the input -- it does not add the dry back.  A 100% wet dotted-8th delay on
    a 4-on-floor techno mix moves every transient 3/16 late and comb-filters
    the whole bus (measured dry-vs-wet waveform correlation 0.06).  So the
    delay stage is applied with an explicit MIX control here: dry is kept at
    (1 - delay_mix) and the echo engine is blended in at ``delay_mix``.
    """
    t0 = time.time()
    pc = ParallelBandCompressor(sample_rate=SR)
    y = pc.process(x, down_threshold_db=-16.0, down_ratio=3.0,
                   up_threshold_db=-44.0, up_amount=0.30, parallel_mix=0.45)
    t1 = time.time()
    gr = GatedReverb(sample_rate=SR)
    gr.tail_gain = 0.55
    gr.declash = 0.5
    gr.movement = 0.5
    y = gr.process(y, triggers=triggers, gate_len=gate_len, decay=0.62)
    t2 = time.time()
    dd = DualEngineDelay(sample_rate=SR)
    y_echo = dd.process(y, time_cont=DOTTED_8TH, time_gran=DOTTED_QTR,
                        pitch_cont=1.0, pitch_gran=1.0, splice=4, feedback=0.42,
                        routing='serial', grain_len=512)
    y = (1.0 - delay_mix) * y + delay_mix * y_echo
    t3 = time.time()
    gc = RhythmicGlitchChain(sample_rate=SR)
    y = gc.process(y, bpm=BPM, patterns=PATTERNS, steps=16)
    t4 = time.time()
    y = 0.65 * y + 0.35 * spectral_declash(y, SR)
    t5 = time.time()
    assert np.all(np.isfinite(y)), 'non-finite samples in chain'
    print('   chain{}: comp {:.1f}s gate {:.1f}s delay(+{:.0%} mix) {:.1f}s '
          'glitch {:.2f}s declash {:.1f}s'.format(
              tag, t1 - t0, t2 - t1, delay_mix, t3 - t2, t4 - t3, t5 - t4))
    return y


def severance_stereo(st, triggers, tag=''):
    """Apply the chain per channel (keeps L/R independence)."""
    l = severance_chain(st[:, 0], triggers, tag=tag + 'L')
    r = severance_chain(st[:, 1], triggers, tag=tag + 'R')
    return np.column_stack([l, r])


# ------------------------------------------------------------------ MIDI parse
mid = mido.MidiFile(str(SRC))
tpb = mid.ticks_per_beat
tempo = None
for m in mid.tracks[0]:
    if m.type == 'set_tempo':
        tempo = m.tempo
        break
assert tempo is not None
sec_per_tick = tempo / 1e6 / tpb
print('source MIDI: tpb={} tempo={} ({} BPM) tracks={}'.format(tpb, tempo, 60e6 / tempo, len(mid.tracks)))

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
        print('  voice track {}: prog={} ch={} notes={}'.format(i, prog, ch, n))
assert len(VOICES) >= 2, 'need >= 2 voice tracks'

# ------------------------------------------------------- velocity-free triggers
# all percussion onsets (channel 9) = the gate trigger grid
drum_ch = 9
triggers = []
for i, track in enumerate(mid.tracks):
    if not any(getattr(m, 'channel', None) == drum_ch and m.type == 'note_on' and m.velocity
               for m in track):
        continue
    t = 0
    for m in track:
        t += m.time
        if m.type == 'note_on' and m.velocity and getattr(m, 'channel', None) == drum_ch:
            triggers.append(t * sec_per_tick)
triggers = sorted(triggers)
print('gate triggers (drum onsets): {}  first={:.3f}s last={:.3f}s'.format(
    len(triggers), triggers[0], triggers[-1]))
assert len(triggers) > 8, 'too few drum onsets for the gate'

# ------------------------------------------- expected pitched note frequencies
note_events = []      # (t_sec, dur_sec, midi_note)
for (tr, name, prog, ch) in VOICES:
    if ch == drum_ch:
        continue
    t = 0
    open_note = {}
    for m in mid.tracks[tr]:
        t += m.time
        if m.type == 'note_on' and m.velocity:
            open_note[m.note] = t
        elif m.type in ('note_off',) or (m.type == 'note_on' and not m.velocity):
            st_t = open_note.pop(m.note, None)
            if st_t is not None:
                note_events.append((st_t * sec_per_tick,
                                    (t - st_t) * sec_per_tick, m.note))
print('pitched note events:', len(note_events))


def midi_freq(n):
    return 440.0 * (2.0 ** ((n - 69) / 12.0))


# ------------------------------------------------------------------ dry render
dry_full = OUT / 'dry_full_mix.wav'
print('rendering dry full mix (internal FX OFF) ...')
fluid_render(SRC, dry_full)
dry = load_wav(dry_full)
dur = len(dry) / SR
print('dry_full_mix: {:.2f}s peak={:.3f}'.format(dur, np.abs(dry).max()))
assert np.abs(dry).max() > 0.05, 'dry render near-silent'


def silence_stats(mono):
    sil = float(np.sum(np.abs(mono) < 0.001) / len(mono))
    rms_map = [float(np.sqrt(np.mean(mono[i:i + SR] ** 2)))
               for i in range(0, len(mono), SR)]
    return sil, rms_map


dry_mono = dry.mean(axis=1)
sil_dry, rms_dry = silence_stats(dry_mono)

# --------------------------------------------------------------- dry stems
print('rendering per-voice dry stems (FX OFF) ...')
stem_meta = {}
for (tr, name, prog, ch) in VOICES:
    st = mido.MidiFile(ticks_per_beat=tpb)
    meta = mido.MidiTrack()
    meta.append(mido.MetaMessage('set_tempo', tempo=tempo, time=0))
    st.tracks.append(meta)
    vt = mido.MidiTrack()
    for m in mid.tracks[tr]:
        vt.append(m)
    st.tracks.append(vt)
    tmp_mid = STEMS_DRY / (name + '.mid')
    st.save(str(tmp_mid))
    wav = STEMS_DRY / (name + '.wav')
    fluid_render(tmp_mid, wav)
    os.unlink(tmp_mid)
    stem_meta[name] = {'track': tr, 'program': prog, 'channel': ch,
                       'wav': str(wav), 'bytes': os.path.getsize(wav)}
    print('   {}: prog={} ch={} {} B'.format(name, prog, ch, stem_meta[name]['bytes']))

# sum-vs-mix alignment check
s = np.zeros_like(dry)
for name, md in stem_meta.items():
    a = load_wav(md['wav'])
    n = min(len(a), len(s))
    s[:n] += a[:n]
n = min(len(s), len(dry))
err = float(np.max(np.abs(s[:n] - dry[:n])))
den = float(np.max(np.abs(dry[:n])))
print('stem-sum vs full mix: max abs diff {:.4f} (mix peak {:.4f}) -> {:.4%}'.format(
    err, den, err / max(den, 1e-9)))

# ------------------------------------------------------------- full mix chain
print('applying SP-071 SEVERANCE chain to FULL MIX (absolute layer) ...')
wet_st = severance_stereo(dry, triggers, tag='[full]')
wet_st = np.nan_to_num(wet_st, nan=0.0, posinf=0.0, neginf=0.0)
wet_st = normalize_to_lufs(wet_st, target_lufs=-14.0, sample_rate=SR)
wet_st = Limiter(threshold_db=-1.0, release_ms=100.0, sample_rate=SR).process(wet_st)
lufs_mix = measure_lufs(wet_st, SR)
peak_mix = float(np.abs(wet_st).max())
out_wav = OUT / 'SP071-severance-techno-brownian.wav'
write_wav_stereo(out_wav, wet_st)
print('mix: LUFS {:.2f} peak {:.4f}'.format(lufs_mix, peak_mix))
assert peak_mix <= 1.0 and peak_mix > 0.3, 'bad mix peak {}'.format(peak_mix)

wet_mono = wet_st.mean(axis=1)
sil_wet, rms_wet = silence_stats(wet_mono)

# ---------------------------------------------------------- processed stems
print('applying chain per voice (processed stems) ...')
for name, md in stem_meta.items():
    a = load_wav(md['wav'])
    y = severance_stereo(a, triggers, tag='[' + name + ']')
    y = np.nan_to_num(y, nan=0.0, posinf=0.0, neginf=0.0)
    p = float(np.abs(y).max())
    if p > 0:
        y = y * (0.891 / p)
    outp = STEMS_PROC / (name + '_serverance.wav')
    write_wav_stereo(outp, y)
    md['processed'] = str(outp)
    md['processed_bytes'] = os.path.getsize(outp)
    print('   {} processed -> {} ({:.2f}s peak {:.3f})'.format(
        name, outp.name, len(y) / SR, float(np.abs(y).max())))

# ------------------------------------------------------- pitch verification
print('pitch verification ...')

# dry-vs-wet waveform correlation (transient-preservation sanity check)
_cn = min(len(dry_mono), len(wet_mono))
_corr_dw = float(np.corrcoef(dry_mono[:_cn], wet_mono[:_cn])[0, 1])
print('dry-vs-wet waveform correlation: {:.3f}'.format(_corr_dw))
assert _corr_dw > 0.25, ('wet chain destroyed the source waveform '
                         '(corr {:.3f}) -> delay wet/dry mix wrong'.format(_corr_dw))


def fft_dom_peak_50_1000(win):
    n = len(win)
    spec = np.abs(np.fft.rfft(win * np.hanning(n)))
    freqs = np.fft.rfftfreq(n, 1.0 / SR)
    lo = np.searchsorted(freqs, 50.0)
    hi = np.searchsorted(freqs, 1000.0)
    idx = np.argmax(spec[lo:hi]) + lo
    return float(freqs[idx])


def harmonic_energy_ratio(win, f0, nharm=8):
    spec = np.abs(np.fft.rfft(win * np.hanning(len(win)))) ** 2
    total = float(np.sum(spec[1:]))
    acc = 0.0
    for k in range(1, nharm + 1):
        fk = f0 * k
        if fk >= SR / 2:
            break
        i = int(round(fk * len(win) / SR))
        lo, hi = max(1, i - 3), min(len(spec) - 1, i + 4)
        acc += float(np.sum(spec[lo:hi + 1]))
    return acc / max(total, 1e-12)


verif = {'windows': [], 'hit': 0, 'checked': 0}
step = 0.5
wlen = int(0.5 * SR)
t = 0.0
auto_frames = 0
auto_unpitched = 0
while t + 0.5 <= dur:
    i0 = int(t * SR)
    win = wet_mono[i0:i0 + wlen]
    if np.abs(win).max() < 0.005:
        t += step
        continue
    dom = fft_dom_peak_50_1000(win)
    # expected pitches sounding inside this window
    exp = sorted({ne for (st_, dn, ne) in note_events
                  if st_ < t + step and (st_ + max(dn, 0.05)) > t})
    # autocorrelation pitch (40..1000 Hz)
    acf = pitch_frame(win, SR, lo=40.0, hi=1000.0)
    auto_frames += 1
    if acf <= 0.0:
        auto_unpitched += 1
    hit = False
    if exp:
        verif['checked'] += 1
        for ne in exp:
            for harm in (1, 2, 3, 4):
                f = midi_freq(ne) * harm
                if abs(dom - f) / f < 0.02:
                    hit = True
                    break
            if hit:
                break
        if hit:
            verif['hit'] += 1
    h_ratio = harmonic_energy_ratio(win, midi_freq(min(exp)) if exp else 220.0)
    verif['windows'].append({'t': round(t, 2), 'dom_hz': round(dom, 1),
                            'acf_hz': round(acf, 1), 'hit': bool(hit),
                            'harm_ratio': round(h_ratio, 3),
                            'expected_notes': exp})
    t += step

hit_rate = verif['hit'] / max(1, verif['checked'])
med_harm = float(np.median([w['harm_ratio'] for w in verif['windows']])) if verif['windows'] else 0.0
med_dom = float(np.median([w['dom_hz'] for w in verif['windows']])) if verif['windows'] else 0.0
verdict = 'PASS' if (hit_rate >= 0.6 and med_harm >= 0.30 and
                     auto_unpitched < 0.5 * max(1, auto_frames)) else 'REVIEW'
print('pitch windows={} checked={} hit_rate={:.3f} median_harm={:.3f} '
      'auto_frames={} unpitched={} median_dom={:.1f}Hz -> {}'.format(
          len(verif['windows']), verif['checked'], hit_rate, med_harm,
          auto_frames, auto_unpitched, med_dom, verdict))

# -------------------------------------------------------------------- OGG
ogg = OUT / 'SP071-severance-techno-brownian.ogg'
subprocess.run([FFMPEG, '-y', '-loglevel', 'error', '-i', str(out_wav),
                '-codec:a', 'libopus', '-application', 'voip', '-b:a', '48k',
                str(ogg)], check=True)
assert os.path.getsize(ogg) > 5000
print('ogg: {} B'.format(os.path.getsize(ogg)))

# ------------------------------------------------------------------- analysis
with open(ANALYSIS / 'pitch_verification.json', 'w') as f:
    json.dump({'verdict': verdict, 'hit_rate': round(hit_rate, 4),
               'median_harmonic_ratio': round(med_harm, 4),
               'median_dom_hz': med_dom, 'auto_frames': auto_frames,
               'auto_unpitched_frames': auto_unpitched,
               'windows': verif['windows']}, f, indent=2)

with open(ANALYSIS / 'render_stats.json', 'w') as f:
    json.dump({'duration_s': round(dur, 3), 'bpm': BPM,
               'silence_ratio_dry': round(sil_dry, 4),
               'silence_ratio_wet': round(sil_wet, 4),
               'rms_per_second_dry': [round(x, 4) for x in rms_dry],
               'rms_per_second_wet': [round(x, 4) for x in rms_wet],
               'lufs_wet': round(lufs_mix, 2), 'peak_wet': round(peak_mix, 4),
               'gate_triggers': len(triggers)}, f, indent=2)

# grid visualization from the source MIDI (read-only parse -> UnitMatrix)
from structures import MusicUnit, MusicEvent, UnitMatrix
from visualization.grid import write_grid_visualization

BARS_PER = 4
N_SECTIONS = 6
BAR = int(tpb * 4)
matrix = UnitMatrix(shape=(len(VOICES), N_SECTIONS))
for r, (tr, name, prog, ch) in enumerate(VOICES):
    t = 0
    cur = None
    open_notes = {}
    for s in range(N_SECTIONS):
        matrix.set_unit((r, s), MusicUnit(events=[]))
    for m in mid.tracks[tr]:
        t += m.time
        if m.type == 'note_on' and m.velocity:
            open_notes[m.note] = t
        elif (m.type == 'note_off') or (m.type == 'note_on' and not m.velocity):
            st_t = open_notes.pop(m.note, t)
            sec = min(N_SECTIONS - 1, st_t // (BAR * BARS_PER))
            off = int(sec * BAR * BARS_PER)
            unit = matrix.get_unit((r, int(sec)))
            unit.add_event(MusicEvent(m.note, 90,
                                      int(st_t - off), int(t - off)))
    for s in range(N_SECTIONS):
        u = matrix.get_unit((r, s))
        sec_len = BAR * BARS_PER
        if len(u.events) == 0 or max(e.end_tick for e in u.events) < sec_len:
            last = int(u.events[-1].end_tick) if len(u.events) else sec_len - 10
            u.add_event(MusicEvent(0, 0, min(last, sec_len - 10), sec_len))
        else:
            for e in u.events:
                if e.end_tick > sec_len:
                    e.end_tick = sec_len

write_grid_visualization(matrix, str(ANALYSIS / 'grid_visualization.txt'),
                         ticks_per_character=240,
                         voice_names=[v[1] + ('' if v[3] != drum_ch else ' (drums)')
                                      for v in VOICES],
                         bpm=int(BPM), mode='F natural minor')
print('grid visualization ->', ANALYSIS / 'grid_visualization.txt')

# ------------------------------------------------------------------ provenance
import shutil
shutil.copy2(SRC, MIDIDIR / SRC.name)

prov = {
    'job': 'random-style production SP layer-aligned 2026-09-12',
    'method': 'SP-071',
    'module': 'sound.effects.severance',
    'desc': 'Gated Reverb + Dual-Engine Delay + Glitch Chain + Parallel Band Compressor (ZERO9-style)',
    'registry': 'workflows.musicom_workflow.SP_METHODS',
    'source_midi': str(SRC),
    'out_dir': str(OUT),
    'params': {
        'bpm': BPM,
        'gate_len_s': GATE_LEN,
        'gate_triggers_n': len(triggers),
        'gated_reverb': {'tail_gain': 0.55, 'declash': 0.5, 'movement': 0.5,
                         'decay': 0.62},
        'dual_engine_delay': {'time_cont_s': round(DOTTED_8TH, 5),
                              'time_gran_s': round(DOTTED_QTR, 5),
                              'feedback': 0.42, 'routing': 'serial',
                              'splice': 4, 'grain_len': 512},
        'glitch_chain': {'patterns': PATTERNS, 'steps': 16},
        'parallel_band_comp': {'down_threshold_db': -16.0, 'down_ratio': 3.0,
                               'up_threshold_db': -44.0, 'up_amount': 0.30,
                               'parallel_mix': 0.45},
        'declash_blend': 0.35,
        'master': {'target_lufs': -14.0, 'limiter_threshold_db': -1.0},
    },
    'soundfont': SF,
    'dry_full_mix': {'path': str(dry_full), 'bytes': os.path.getsize(dry_full),
                     'silence_ratio': round(sil_dry, 4)},
    'wet_full_mix': {'path': str(out_wav), 'bytes': os.path.getsize(out_wav),
                     'ogg': str(ogg), 'ogg_bytes': os.path.getsize(ogg),
                     'lufs': round(lufs_mix, 2), 'peak': round(peak_mix, 4),
                     'silence_ratio': round(sil_wet, 4),
                     'sha256': sha256(out_wav)},
    'stems': stem_meta,
    'stem_sum_vs_mix_maxdiff': round(err, 5),
    'pitch_verification': {'verdict': verdict, 'hit_rate': round(hit_rate, 4),
                           'median_harmonic_ratio': round(med_harm, 4),
                           'auto_unpitched_frames': auto_unpitched,
                           'auto_frames': auto_frames},
}
with open(OUT / 'provenance.json', 'w') as f:
    json.dump(prov, f, indent=2)

with open(OUT / 'run.log', 'w') as f:
    f.write(json.dumps(prov, indent=2) + '\n')

print('DONE ->', OUT)
