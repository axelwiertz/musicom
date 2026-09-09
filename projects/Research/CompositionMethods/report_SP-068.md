# Report — SP-068 Bytebeat Synthesis (Integer-Expression Algorithmic Synthesis)

- **Method name:** Bytebeat Synthesis (Integer-Expression Algorithmic Synthesis)
- **ID:** SP-068
- **Layer:** absolute
- **One-line description:** Evaluate an integer expression $f(t)$ of a monotonic sample counter $t$ once per sample, take the low byte as the waveform ($y = f(t)\ \&\ 255$), using only integer arithmetic and bitwise ops (shift/AND/XOR) to synthesize deterministic, inherently-looping chip/glitch timbres — no oscillators, wavetables, or filters.
- **Next free SP ID:** SP-069

## Summary-table row (added)

`| **SP-068** | Bytebeat Synthesis (Integer-Expression Algorithmic Synthesis) | **Synthesis Engines** | Deterministic Chip / Glitch / Looping Timbre | Evaluates an integer expression $f(t)$ of a monotonic sample counter $t$ once per sample and takes the low byte as the waveform ($y=f(t) \& 255$), using only integer arithmetic and bitwise ops (shift/AND/XOR). Pitch = multiplier $K \to f = f_s\cdot\gcd(K,256)/256$ (or a phase accumulator for exact pitch); octave = `t>>s`; rhythm = `(t>>s)&mask` gates; harmony = additive/AND-XOR term stacks; macro-form = high-bit term `t>>P`. $\mathcal{O}(1)$ per sample, zero state, inherently looping (counter wraps mod $2^N$). The pure-integer, expression-driven counterpart to SP-035 GENDYN / SP-057 Chua; canonical continuous-fill layer for the Method Hybridization rule. |`

## Line-count delta

- Before: 16781
- After (summary row + detail section): 16864
- Delta: +83

## Files

- Standalone write-up: `/opt/data/projects/Research/CompositionMethods/sound_method_SP-068_bytebeat.md`
- Report: `/opt/data/projects/Research/CompositionMethods/report_SP-068.md`
- DB: `/opt/data/projects/Research/CompositionMethods/methods_db.md` (summary row line 167, detail section line 16783)

## Candidate code path

`sound/synthesis/bytebeat.py` (sibling to `equation_synth.py`, `west_coast.py`, `dx7_voice.py`, `granular.py`).

## Technical mechanics summary

1. Per-sample eval $y[n]=f(t)\ \&\ 255$, centered $x=(y-128)/128$.
2. Ramp/saw pitch: period $T=256/\gcd(K,256)$ samples → $f=f_s\cdot\gcd(K,256)/256$ (integer pitch lattice).
3. Octave = right-shift `t>>s`.
4. Free pitch via phase accumulator $\mathrm{inc}=\mathrm{round}(256\,f/f_s)$.
5. Harmony = additive term stacks (interval) or AND/XOR products (ring-mod sidebands).
6. Rhythm/texture = `(t>>s)&mask` square gates; `t^(t>>s)` glitch noise.
7. Macro-form = high-bit term `t>>P` (section selector every $2^P$ samples).
8. Band-limit via oversample ×4–8 + windowed-sinc decimate, or inline one-pole LP.

## Quirks / pitfalls hit during this run

1. **Web search blocked** — `curl` + `python -c` hit the terminal "script execution via -c flag" approval gate (pending_approval). Proceeded from established domain knowledge (bytebeat is canonical, well-documented since 2011). No fabricated references; all citations are real, standard works.
2. **Escaped-space artifacts** — the summary-table row initially rendered `\ \&\ ` (double-escaped space + amp). Fixed to `\&` (verified: backslash count 5 = `\& \mathcal \gcd \cdot \to`). Matches the known "LaTeX backslash double-escape" pitfall class.
3. **`||` prefix check** — verified NO leading double-pipe; row starts with single `| *`.
4. **CWD symlink** — write_file resolved paths to `/opt/data/repos/musicom/projects/...` (symlink target); both `/opt/data/projects/Research/...` and `/opt/data/repos/musicom/projects/...` resolve identically (ONE-TREE contract).

## Appendix — complete section text appended

See `methods_db.md` lines 16783–16864 (header `# Bytebeat Synthesis (Integer-Expression Algorithmic Synthesis) (Method SP-068)` through References). Standalone expanded version in `sound_method_SP-068_bytebeat.md`.
