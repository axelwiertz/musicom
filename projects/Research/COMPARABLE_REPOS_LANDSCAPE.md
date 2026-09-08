# Musicom — Comparable Repos & Documentation (landscape scan)

Date: 2026-09-08. Sources: GitHub Search API (authenticated), PyPI, DuckDuckGo.
~25 queries, 100+ repos screened, READMEs of the closest 8 read in full.
Stars/dates are point-in-time snapshots.

## 1. Closest philosophical matches (full-control / transparent / agentic)

These share musicom's core thesis: *transparent, editable, every-step-control
music generation — not opaque prompt-to-audio*.

| Project | Stars | What it is | Overlap with musicom | Key difference |
|---|---|---|---|---|
| **[Midra](https://github.com/XIAODUOLU/Midra)** (XIAODUOLU) | 60★ | Agentic prompt-to-code MIDI framework. "Compiles NL prompts into structured, inspectable music code… unlike opaque end-to-end AI audio." | **Closest single comp.** Prompt→code→MIDI, checkpoint JSONs, editable output, agentic composition | Musicom is method-taxonomy-driven (100+ catalogued methods by layer), not prompt-driven; musicom has verification/audit gates + provenance; Midra is newer/single-author, no research corpus |
| **[houseband](https://github.com/matt-l-morgan/houseband)** | 0★ | Agentic loop: 3 composer agents write Python→MIDI, LLM judge panel critiques vs rubrics, coach persists lessons | Nightly agent composition + REPORT + critique-into-improvement loop is musicom's cron pipeline | houseband's focus is *measurable agent improvement* (falsifiable critique signal); musicom's is *layered method coverage + audited artifacts* |
| **[WeaveMuse](https://github.com/manoskary/weavemuse)** | 33★ | smolagents framework orchestrating music AI models (ChatMusician, NotaGen, Stable Audio) | Agent orchestration + multi-model generation | Weavemuse wraps big models; musicom builds symbolic control from theory/rules instead |
| **[music-gen-skill](https://github.com/sirruf/music-gen-skill)** (sirruf) | 0★ | Claude Code skill: LLM writes MIDI (mido) → fluidsynth + GM SoundFont render; "honest framing: algorithmic composition + sampled instruments" | **Nearly identical runtime architecture** (python+mido+fluidsynth+SF2, deterministic, no cloud) | One-shot skill vs musicom's full engine + registry + corpus; musicom could cite it as prior art for the "LLM emits MIDI, SoundFont renders" pattern |

## 2. Pattern / method toolboxes (the "methods" concept)

| Project | Stars | What it is | Relation |
|---|---|---|---|
| **[isobar](https://github.com/ideoforms/isobar)** | 431★ (active 2026-09) | Python pattern library: PTeams, timelines, L-systems, Markov, Euclid, warp/interpolation, MIDI output | **Closest peer engine.** Same shape (patterns→events→MIDI), no layer taxonomy, no verification gates, no research DB |
| **[total-serialism](https://github.com/tmhglnd/total-serialism)** | 185★ (JS) | Toolbox of algorithmic-composition methods (arrays in → arrays out): Euclid, cellular automata, sieve, Perlin, dice | Same "methods toolbox" idea in JS; feeds Mercury/P5/ToneJS. musicom's DB is far larger (100+ methods with layer tags) |
| **[Kulitta](https://github.com/donya/Kulitta)** | 113★ | Haskell algorithmic composition lib (Yale dissertation): harmony generation via grammar + PC sets | Academic cousin: theory-first generation, but Haskell + no production layer |
| **[foox](https://github.com/ntoll/foox)** | 131★ | Species counterpoint via genetic algorithms (Python) | Overlaps musicom's `rules/voice_leading` + HC counterpoint methods; single-technique vs musicom's catalog |
| **[ziffers](https://github.com/amiika/ziffers)** | 94★ | Numbered notation DSL for generative melodies (live-coding) | Notation-first vs musicom's data-structure-first |
| **[scamp](https://pypi.org/project/scamp/)** | 0.12.0 | "Suite for Computer-Assisted Composition": manages flow of musical time, SoundFont/MIDI playback, ensembles | Strong peer for *composition-in-Python with playback*; no generative-method registry, no audit layer |
| **[pycomposer](https://pypi.org/project/pycomposer/)** | 1.0.6 | GAN/Markov auto-composition | Model-based, no control granularity |

## 3. Symbolic music-generation research repos (model-centric)

Musicom deliberately treats these as *alternatives to full-control* (black-box
end-to-end), but they're the academic comparators:

| Project | Stars | Note |
|---|---|---|
| [NotaGen](https://github.com/ElectricAlexis/NotaGen) | 1225★ | LLM-training paradigm for symbolic music (ABC) |
| [muspy](https://github.com/salu133445/muspy) | 524★ | Toolkit for symbolic-gen research: datasets, IO, eval. Data-centric, not compositional |
| [symbolic-music-diffusion](https://github.com/magenta/symbolic-music-diffusion) | 280★ | Magenta diffusion |
| [musicaiz](https://github.com/carlosholivan/musicaiz) | 192★ | Symbolic gen + eval + analysis framework |
| [MidiNet](https://github.com/RichardYang40148/MidiNet) / [MIDI-GPT](https://github.com/Metacreation-Lab/MIDI-GPT) / [rule-guided diffusion](https://github.com/yjhuangcd/rule-guided-music) / [mgeval](https://github.com/RichardYang40148/mgeval) | 90–186★ | Model + eval research lineage |
| [Awesome-Music-Generation](https://github.com/shaopengw/Awesome-Music-Generation) (167★), [awesome-ai-music-generation](https://github.com/Curated-Awesome-Lists/awesome-ai-music-generation) (494★) | — | Landscape lists (mostly model papers) |

## 4. Foundations musicom builds on (check its docs cite them as peers, not comps)

| Project | Stars | Role vs musicom |
|---|---|---|
| [music21](https://github.com/cuthbertLab/music21) | 2576★ | Analysis/notation toolkit — musicom uses it for analysis + MusicXML. Different goal (computer-aided musicology, not generation pipeline) |
| [pretty_midi](https://github.com/craffel/pretty-midi) | 1037★ | MIDI utility — used by musicom's env |
| [abjad](https://github.com/Abjad/abjad) | 268★ | Python API over LilyPond (notation output, not generation) |
| [mingus](https://pypi.org/pypi/mingus/) | 0.6.1 | Older music-theory package |
| [librosa](https://github.com/librosa/librosa) | ~7k★ | Audio analysis (MIR), not composition |

## 5. Live-coding environments (different niche, same "control" ethos)

| Project | Stars | Note |
|---|---|---|
| [sonic-pi](https://github.com/sonic-pi-net/sonic-pi) | 12121★ | Live coding education instrument — huge, real-time, Ruby-based |
| [SuperCollider](https://github.com/supercollider/supercollider) | 6718★ | Synthesis server + language; algorithmic composition via sclang |
| [FoxDot](https://github.com/Qirky/FoxDot) / renardo | 1155★/92★ | Python live coding |
| [Mercury](https://github.com/tmhglnd/mercury) | 376★ | Minimal live-coding language (education-friendly) |
| [Strudel](https://github.com/felixroos/strudel) | — | TidalCycles port to JS |

Real-time/interactive focus vs musicom's *offline, audited, git-tracked
production pipeline* focus. Different job.

## 6. Education-focused

| Project | Stars | Note |
|---|---|---|
| [JythonMusic](https://github.com/manaris/jythonMusic) | 36★ | Open environment for music making + creative programming in classrooms (Jython) — the closest *education-first* comp, but GUI/performing-oriented, no agent pipeline, no production layer |
| wellen (dennisppaul) | 35★ | Framework for exploring/teaching generative music |
| music21 (also) | — | Widely used in pedagogy via computational-musicology courses |

## 7. Where musicom sits — synthesis

**No scanned project combines all of musicom's pillars:**

1. **Layered method taxonomy** (abstract ABS-* / concrete 001–081 / human HC-001–029 / absolute SP-*) with a living, nightly-researched DB — unique. Closest: total-serialism's method toolbox (no DB/layer tags), isobar's pattern classes.
2. **Human-composition methods as first-class DB** (HC compás, tala, partimento…) — not seen anywhere else.
3. **Verification/audit gates as a first-class layer** (zero-drift validate, grid/harmony audits, silence/RMS, pitch checks) — no comp does this systematically; houseband does critique-via-LLM (different mechanism, same "falsifiable output" instinct).
4. **Autonomous agent pipeline over a git-tracked corpus** (nightly compose/research, weekly registration, provenance sidecars) — houseband is the nearest (agentic loop), musicom adds persistence + method registry.
5. **ONE-ENV/ONE-TREE ops discipline** (env.py contract, lock files, commit-only sync) — engineering hygiene nobody else in this list even documents.

**Where comps are ahead (borrowable ideas):**
- **Midra**: prompt→checkpointed JSON plan artifacts; human-in-the-loop editing UI.
- **houseband**: explicit judge rubrics + "did the agent improve" metrics — a natural extension of musicom's REPORT/audit discipline.
- **isobar**: cleaner pattern-combinator DSL; timeline scheduling.
- **muspy**: standardized evaluation metrics + dataset IO — could strengthen musicom's analysis layer.
- **scamp**: expressive performance params (tempo curves, note articulation) in playback.
- **WeaveMuse**: Gradio UI + score rendering for immediate human listening.

## 8. Suggested positioning line (for README/pitch)

> Musicom = "a controlled, audited, layer-structured composition framework"
> — sits between Midra/houseband (agentic prompt-to-MIDI) and
> isobar/scamp (pattern & composition libs), with the methods DB + verification
> gates + autonomous research pipeline that none of them have.
