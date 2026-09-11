# HC-032 — Guqin Jianzipu Tablature & Dapu Reconstruction

**Method ID:** HC-032
**Layer:** concrete (target when implemented) — human-craft knowledge; realizes material through the UnitMatrix (Voices & Sections).
**Tradition / Culture:** Chinese literati zither music — guqin (古琴, seven-string zither), ~3000-year unbroken tradition; UNESCO Intangible Cultural Heritage (2008, "Guqin and its music").
**Primary Elements:** PITCH, TEXTURE, STRUCTURE, RHYTHM.

---

## 1. Description

The guqin is the scholar's instrument of classical China, one of the "four arts"
(qin 琴, qi 棋 chess, shu 書 calligraphy, hua 畫 painting). Its repertoire is
transmitted not as staff notation but as **jianzipu (減字譜, "reduced-character
tablature")** — composite ideographs that stack radical fragments of Chinese
characters into a single glyph encoding, for one sounding event:

- **string number** (1–7, top/middle cluster),
- **left-hand stop position** (a hui 徽 harmonic node number, 1–13, or "open
  string" san 散),
- **right-hand plucking technique** (bottom/middle cluster — the finger and
  direction of the pluck), and
- **left-hand technique** applied after the pluck (vibrato, slide, portamento,
  shake).

Crucially, jianzipu records **pitch-space and timbre-action but NOT rhythm,
duration, tempo, metre, or phrasing**. There is no note value. A single glyph
tells the player *where to put the fingers and how to strike*, and the player
must supply *when and how long*.

The human craft of turning a bare glyph stream into living music is **dapu
(打譜, literally "striking/beating out the tablature")** — the interpretative
reconstruction of an old piece from tablature. This is the compositional heart
of the tradition: every performance of a historical guqin piece is, in part, a
re-composition. The reconstructor must infer a rhythmic skeleton, tempo map,
phrasing, and ornament profile that is consistent with the technique encoded in
the glyphs, with the idiom of the school/lineage, and with the aesthetic ideal
of *qing wei* (清微淡遠 — "pure, subtle, spare, distant").

---

## 2. Craft Procedure (how the human actually does it)

1. **Fix tuning (diao).** Choose one of ~30 standard tunings (e.g. zhengdiao
   正調 C–D–F–G–A–c–d, or a lowered/slack tunings like ruibin, manjue, qiliang).
   Open strings form a pentatonic core; the tuning defines the pitch universe
   and the color of the piece. This is the invariant modal spine.

2. **Read the glyph stream.** Transcribe the jianzipu column-by-column (right to
   left). For each glyph, extract (string, hui stop, pluck technique, left-hand
   technique). No rhythm is present — the player reads only the *sequence of
   sounding events and their timbre actions*.

3. **Map stop positions to pitches.** Open string (san) = the string's tuned
   pitch. A hui stop N on a string divides it at N/13 of length → pitch rises
   by the corresponding interval (hui 7 = octave harmonic node; hui 5 = 12th,
   etc.). Fan (泛, harmonic/flageolet) touches yield the harmonic series of the
   string — bright bell-like pitches; an (按, stopped) yields a full pressed
   pitch. This is the pitch-realization step: glyph → pitch class.

4. **Infer the rhythmic skeleton (the dapu decision).** The reconstructor
   supplies rhythm from several sources:
   - **idiomatic phrase grammar** — the guqin phrase tends toward balanced
     2+2 / 4-bar breath groups; cadential idioms and the ending gesture of a
     section mark phrase boundaries;
   - **the "da" (beat) intuition of the lineage** — each school (Guangling,
     Yushan, Shu, Zhucheng, Meian) carries a house rhythmic dialect;
   - **the technique density cue** — rapid alternations (lun 輪, shuang 雙)
     imply shorter note values; long slides (chuo 綽 / zhu 注) imply held,
     stretched durations;
   - **lyric association where the piece has a title-story** — the programmatic
     image (a flowing river, a parting at Yangguan, an orchid) shapes tempo.

5. **Shape phrasing and tempo map.** Decide rubato structure: where to expand
   (a held harmonic, a long slide), where to push (an ornamental run before a
   cadence). Guqin tempo is free and breath-driven; the *ma* (間, gap/silence)
   between phrases is composed, not incidental.

6. **Notate the left-hand ornament profile.** After each pluck, decide the
   ornament: yin 吟 (vibrato) vs. rou 揉 (slow vibrato) vs. nao 猱 (shaking),
   shang 上 (slide up) vs. xia 下 (slide down), and their microtonal shading.
   These do not change pitch class but define timbre/texture and phrasing.

7. **Reconstruct phrase order and repeat structure.** Old tablatures (e.g.
   Shenqi Mipu) sometimes omit repeat marks or leave a section's internal order
   ambiguous; the reconstructor fixes the macro-form (often an arch: slow
   opening → development → climactic fast passage → return → dissolve).

8. **Stress-test by performance.** Play the reconstruction repeatedly; adjust
   until the piece "breathes." A dapu is never final — it is a living reading,
   re-negotiated by each master. Guan Pinghu's famous reading of *Liu Shui*
   ("Flowing Water") differs from other masters' precisely at the level of
   rhythm and ornament he supplied.

---

## 3. Practitioner Examples

- **Zhu Quan (朱權, 1378–1448)** — Ming prince who compiled *Shenqi Mipu*
  (神奇秘譜, "Wondrous and Secret Notation", 1425), the earliest surviving
  guqin tablature anthology (64 pieces); his preface explicitly notes that
  rhythm must be supplied by the player because the notation cannot record it.
- **Guangling San (廣陵散)** — the most famous guqin piece, traced to the
  Wei/3rd-century tale of Nie Zheng's assassination and the poet Ji Kang's
  farewell performance; survives in Shenqi Mipu only as tablature and has been
  reconstructed (dapu) repeatedly across centuries.
- **Guan Pinghu (管平湖, 1897–1967)** — Beijing guqin master; his dapu of
  *Liu Shui* ("Flowing Water") is the recording carried aboard the Voyager
  Golden Record (1977), the definitive example of rhythmic/phrasing
  reconstruction from bare tablature.
- **Wu Wenguang (吳文光)** — modern master whose dapu of Tang-dynasty pieces
  (e.g. from the 8th-c. *Youlan* "Solitary Orchid" lineage) illustrates
  reconstruction of ancient tablature into performable form.
- **Zha Fuxi (查阜西)** — scholar-performer who catalogued and systematized
  the surviving guqin tablature corpus (3,000+ pieces across ~130 collections),
  laying the documentary basis for modern dapu practice.

---

## 4. UnitMatrix Integration

### Voices & Sections
- **Voice 0 — tuning/spine anchor (invariant).** The open-string pitch set of
  the chosen diao (pentatonic core) is the invariant harmonic reference; it is
  never changed within a piece. Optionally materialized as a sparse drone/held
  open string (the guqin frequently returns to open-string resonance).
- **Voice 1 — the melodic line (the realized glyph stream).** Each UnitMatrix
  cell = one glyph → one sounding event: a `MusicEvent` whose pitch comes from
  (string × hui stop) resolution and whose onset/duration come from the dapu
  rhythm the reconstructor supplies.
- **Voice 2 — left-hand ornament/timbre layer.** Not separate notes, but
  per-event articulation metadata (vibrato yin/rou/nao, slides shang/xia,
  portamento) realized as pitch-bend/CC or microtonal pitch offsets — the
  "texture" of the guqin.
- **Voice 3 — harmonic (fan) layer.** Bell-like flageolet tones (hui 7/5/9)
  as a distinct timbre register; often used for section openings and cadential
  punctuation.
- **Sections = the phrase/dapu macro-form**, typically an arch:
  Slow opening (state material) → Development (density climbs) → Climax
  (fast lun/shuang alternations) → Return → Dissolve (fade to open-string
  resonance / silence). One phrase-breath = one section; the composed gap (ma)
  between sections is a first-class unit.

### Rules to encode
1. **Tuning invariance** — all pitches ∈ the diao's open-string + stopped-pitch
   set (pentatonic core + hui-division pitches). No pitch outside the set.
2. **Glyph → pitch resolution** — `pitch = string_freq(string) × 13/(13 − hui)`
   (stopped) or `× k` for the hui harmonic node (fan). 12-TET round or
   just/pure tuning per config.
3. **Technique → duration cue** — lun/shuang (alternation) ⇒ short IOIs;
   chuo/zhu (slides) ⇒ stretched duration; fan (harmonic) ⇒ ring-out sustain.
   The reconstructor's rhythm must respect these density cues.
4. **Phrase grammar** — balanced breath groups (2+2, 4 bars), cadential idiom
   at section ends, ma (silence) required between phrases, free/rubato tempo
   (no fixed grid binding — metric_binding = fluid).
5. **Ornament post-filter** — each pluck event may carry one left-hand ornament
   (yin/rou/nao/shang/xia); ornaments add timbre not pitch class; vibrato rate
   ∝ register (higher = faster).
6. **Arch macro-form** — density monotonic to a climactic fast passage, then
   decay to open-string resonance; piece always returns to a tonic open string.
7. **Zero-drift** — every voice's units padded to section length (absolute
   ticks), consistent with the engine's equal-length invariant.

### Musical Elements mapping
- **PITCH** — from glyph stop-resolution (string × hui / harmonic node); tuning-locked.
- **RHYTHM** — reconstructed (dapu), free/rubato, technique-density-cued; the core human contribution.
- **HARMONY** — non-functional; vertical sonority incidental (open-string resonance, parallel octaves/unisons idiomatic); modal pentatonic.
- **STRUCTURE** — arch macro-form from phrase grammar + programmatic image.
- **TEXTURE** — the left-hand ornament layer + fan harmonic timbre register; single-line but timbrally rich.

---

## 5. Quirks & Pitfalls

- **Rhythm is a gap in the source, not a bug.** Any faithful engine
  implementation must treat jianzipu as *pitch + timbre + technique* only, and
  generate rhythm from a dapu policy. Naively quantizing glyphs to an equal
  grid destroys the idiom (the whole point of the craft is the free,
  breath-driven rhythm).
- **Do not over-harmonize.** The guqin is essentially monophonic (occasional
  octave/unison doublings). Polyphonic "realization" violates the aesthetic of
  qing wei. Keep one melodic voice + resonance/ornament layers.
- **Hui math is microtonal.** hui stops are exact string-length divisions
  (13/(13−N)); a 12-TET rounding is a lossy convenience. Preserve the option of
  just-intonation/pure tuning.
- **The gap (ma) is a note.** Do not elide inter-phrase silence; guqin
  aesthetics treat silence as composed material (parallel to the Japanese
  honkyoku "ma", cf. HC-029).
