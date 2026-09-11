# Report HC-032 — Guqin Jianzipu Tablature & Dapu Reconstruction

**Date:** 2026-09-10 (nightly `daily-human-composition-research` job)
**Method ID:** HC-032
**Method Name:** Guqin Jianzipu Tablature & Dapu Reconstruction
**Tradition / Culture:** Chinese literati zither music — guqin (古琴, seven-string zither), ~3000-year unbroken tradition; UNESCO Intangible Cultural Heritage (2008, "Guqin and its music").
**Layer:** concrete (target when implemented) — human-craft knowledge; realizes material through the UnitMatrix (Voices & Sections).
**Primary Musical Elements:** PITCH, TEXTURE, STRUCTURE, RHYTHM.

---

## 1. Method Summary

The guqin (Chinese literati zither) transmits its ~3,000-piece repertoire not in
staff notation but in **jianzipu (減字譜, "reduced-character tablature")** — dense
composite ideographs, each glyph encoding (for one sounding event) the **string
number, left-hand hui stop position, right-hand pluck technique, and left-hand
follow-through technique**. Critically, jianzipu records **pitch-space and
timbre-action but no rhythm, duration, tempo, metre, or phrasing**. The craft of
turning a bare glyph stream into living music is **dapu (打譜, "beating out the
tablature")** — interpretative reconstruction. Every performance of a historical
guqin piece is therefore in part a re-composition: the reconstructor supplies the
rhythmic skeleton, tempo map, phrasing, and ornament profile from idiom, lineage
dialect, technique-density cues, and the piece's programmatic image, all within
the aesthetic ideal of *qing wei* (清微淡遠, "pure, subtle, spare, distant").

---

## 2. Layer Classification

- **Target layer: concrete.** Human-craft knowledge; when implemented it will
  realize material (a glyph stream → sounding events) through the UnitMatrix
  (Voices & Sections), filling cells with `MusicEvent`s. It is NOT an
  abstract-layer design method and NOT an absolute-layer sound-production
  method (the guqin's timbral identity is a *performance* concern, not a DSP
  concern in this index).

---

## 3. Craft Procedure (how a human does it, step by step)

1. **Fix tuning (diao 調).** Choose one of ~30 standard tunings (zhengdiao
   正調 C–D–F–G–A–c–d, ruibin, manjue, qiliang, etc.). Open strings form a
   pentatonic core; the tuning defines the pitch universe and color. Invariant
   modal spine.
2. **Read the glyph stream.** Transcribe jianzipu column-by-column (right to
   left). Each glyph → (string, hui stop, pluck technique, left-hand
   technique). No rhythm is present — only the *sequence* of sounding events
   and their timbre actions.
3. **Map stop positions to pitch.** Open string (san 散) = the string's tuned
   pitch. Hui stop N divides the string at N/13 → pitch rises by that interval
   (hui 7 = octave node, hui 5 = 12th). Fan (泛 harmonic/flageolet) = harmonic
   series of the string; an (按 stopped) = full pressed pitch.
4. **Infer the rhythm (the dapu decision).** Supply rhythm from: idiomatic
   phrase grammar (balanced 2+2 / 4-bar breath groups); the lineage's
   beat-intuition (Guangling / Yushan / Shu / Zhucheng / Meian dialects);
   technique-density cues (rapid lun 輪 / shuang 雙 alternations ⇒ short values,
   long chuo 綽 / zhu 注 slides ⇒ held durations); and the programmatic
   title-story (flowing river, parting, orchid).
5. **Shape phrasing & tempo map.** Decide rubato: where to expand (held
   harmonic, long slide), where to push (ornamental run before a cadence).
   Tempo free and breath-driven; inter-phrase silence is composed.
6. **Notate the left-hand ornament profile.** Per pluck: yin 吟 (vibrato),
   rou 揉 (slow vibrato), nao 猱 (shake), shang 上 (slide up), xia 下 (slide
   down) + microtonal shading. No pitch-class change — timbre/texture/phrasing.
7. **Fix phrase order & repeat structure.** Old tablatures may omit repeat
   marks or leave section order ambiguous; reconstructor fixes the macro-form
   (typically an arch).
8. **Stress-test by performance.** Play repeatedly; adjust until the piece
   "breathes." A dapu is never final — re-negotiated by each master.

---

## 4. Practitioner Examples

- **Zhu Quan (朱權, 1378–1448)** — Ming prince, compiled *Shenqi Mipu*
  (神奇秘譜, "Wondrous and Secret Notation", 1425), earliest surviving guqin
  tablature anthology (64 pieces); his preface explicitly notes rhythm must be
  supplied by the player because notation cannot record it.
- **Guangling San (廣陵散)** — most famous guqin piece, Wei/3rd-c. story of
  Nie Zheng's assassination and poet Ji Kang's farewell; survives only as
  tablature in Shenqi Mipu, reconstructed (dapu) repeatedly across centuries.
- **Guan Pinghu (管平湖, 1897–1967)** — Beijing master; his dapu of *Liu Shui*
  ("Flowing Water") is the recording on the Voyager Golden Record (1977) — the
  definitive example of rhythmic/phrasing reconstruction from bare tablature.
- **Wu Wenguang (吳文光)** — modern master; dapu of Tang-dynasty pieces (e.g.
  the 8th-c. *Youlan* "Solitary Orchid" lineage).
- **Zha Fuxi (查阜西)** — scholar-performer who catalogued the surviving corpus
  (3,000+ pieces, ~130 collections), the documentary basis of modern dapu.

---

## 5. UnitMatrix Mapping

### Voices & Sections
- **Voice 0 — tuning/spine anchor (invariant).** Open-string pentatonic set of
  the chosen diao; never changed. Optionally materialized as a sparse held
  open-string drone (guqin frequently returns to open-string resonance).
- **Voice 1 — the realized glyph stream (melodic line).** One cell = one glyph
  = one `MusicEvent`; pitch from (string × hui) resolution, onset/duration from
  the dapu rhythm the reconstructor supplies.
- **Voice 2 — left-hand ornament/timbre layer.** Not separate notes; per-event
  articulation metadata (yin/rou/nao vibrato, shang/xia slides) realized as
  pitch-bend/CC or microtonal offsets — the guqin's texture.
- **Voice 3 — harmonic (fan) layer.** Bell-like flageolet tones (hui 7/5/9) as
  a distinct timbre register; section openings / cadential punctuation.
- **Sections = phrase-breath macro-form (arch).** Slow opening (state material)
  → Development (density climbs) → Climax (fast lun/shuang alternations) →
  Return → Dissolve (fade to open-string resonance/silence). Composed gap (ma)
  between sections is a first-class unit.

### Rules to encode
1. **Tuning invariance** — all pitches ∈ diao open-string + stopped-pitch set.
2. **Glyph → pitch resolution** — `pitch = string_freq(string) × 13/(13 − hui)`
   (stopped) or `× k` for the hui harmonic node (fan); 12-TET round or pure
   tuning per config.
3. **Technique → duration cue** — lun/shuang ⇒ short IOIs; chuo/zhu ⇒ stretched
   duration; fan ⇒ ring-out sustain.
4. **Phrase grammar** — balanced breath groups; cadential idiom at section
   ends; ma (silence) between phrases; free/rubato (metric_binding = fluid).
5. **Ornament post-filter** — ≤1 left-hand ornament per pluck event; timbre not
   pitch class; vibrato rate ∝ register.
6. **Arch macro-form** — density monotonic to climactic fast passage, then
   decay to open-string resonance; always returns to a tonic open string.
7. **Zero-drift** — all voices padded to section length (absolute ticks),
   consistent with the engine's equal-length invariant.

### Musical Elements mapping
- **PITCH** — from glyph stop-resolution (string × hui / harmonic node); tuning-locked.
- **RHYTHM** — reconstructed (dapu), free/rubato, technique-density-cued; the core human contribution.
- **HARMONY** — non-functional; vertical sonority incidental (open-string resonance, parallel octaves/unisons idiomatic); modal pentatonic.
- **STRUCTURE** — arch macro-form from phrase grammar + programmatic image.
- **TEXTURE** — left-hand ornament layer + fan harmonic timbre register; single-line but timbrally rich.

---

## 6. Table Row Added (human_methods_db.md)

| Method ID | Layer | Method Name | Tradition / Culture | Primary Elements | Craft Process | UnitMatrix Mapping | Real Practitioner Example | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| HC-032 | human (→concrete) | Guqin Jianzipu Tablature & Dapu Reconstruction | Chinese literati zither music — guqin (古琴), ~3000-year tradition; UNESCO Intangible Cultural Heritage (2008) | PITCH, TEXTURE, STRUCTURE, RHYTHM | Fix tuning (diao, ~30 standard tunings, pentatonic open-string core) → read jianzipu glyph stream (string × hui stop × pluck technique × left-hand technique; NO rhythm recorded) → resolve glyph → pitch (open san / harmonic fan / stopped an, hui = string-length division) → infer rhythm via dapu (idiomatic phrase grammar + lineage beat-intuition + technique-density cue + programmatic image) → shape phrasing/tempo map (free, breath-driven) → notate left-hand ornament profile (yin/rou/nao vibrato, shang/xia slides, microtonal shading) → fix phrase order & repeat structure (arch macro-form) → stress-test by performance (dapu = living reading, never final) | Voice 0 = tuning/spine anchor (invariant pentatonic open-string set, sparse drone). Voice 1 = realized glyph stream (1 glyph = 1 event; pitch from string×hui, onset/duration from dapu rhythm). Voice 2 = left-hand ornament/timbre layer (vibrato/slide microtonal offsets, no new pitch class). Voice 3 = harmonic fan layer (bell-like flageolet register). Sections = phrase-breath arch (slow opening → development → climax fast lun/shuang → return → dissolve to open-string resonance). Rules: tuning invariance, glyph→pitch resolution, technique→duration cue (lun/shuang short, chuo/zhu stretched, fan sustain), phrase grammar + composed ma silence, free/rubato (fluid metric), ornament post-filter, arch form, return-to-tonic, zero-drift padding | Zhu Quan (Shenqi Mipu 1425, earliest tablature anthology), Guangling San (dapu lineage, 3rd-c. story), Guan Pinghu (Liu Shui "Flowing Water" on Voyager Golden Record 1977), Wu Wenguang (Youlan dapu), Zha Fuxi (corpus cataloguer) | ✅ Documented |

---

## 7. Quirks & Pitfalls

- **Rhythm is a gap in the source, not a bug.** Faithful implementation must
  treat jianzipu as pitch + timbre + technique only, generating rhythm from a
  dapu policy. Naively quantizing glyphs to an equal grid destroys the idiom.
- **Do not over-harmonize.** The guqin is essentially monophonic (occasional
  octave/unison doubling). Polyphonic "realization" violates qing wei.
- **Hui math is microtonal.** hui stops are exact string-length divisions
  (13/(13−N)); 12-TET rounding is lossy. Preserve just-intonation option.
- **The gap (ma) is a note.** Do not elide inter-phrase silence (parallel to
  Japanese honkyoku "ma", cf. HC-029).

---

## 8. Verification

- Detail file: `human_method_HC-032_guqin-jianzipu-dapu-reconstruction.md` ✅
- DB row appended to `human_methods_db.md` ✅
- No duplicate HC-032 in table (only one row) ✅
- **Next free ID: HC-033** (max existing = HC-032; next = max+1).

---

## 9. Rotation Note

Tradition selected to avoid recent overlap: Chinese literati zither — distinct
from the Persian (HC-031), Argentine (HC-030), Japanese (HC-029), and jazz
(HC-028) entries that immediately precede it. Next cycle should steer clear of
East-Asian free-rhythm zither/breath traditions already covered (guqin HC-032,
shakuhachi HC-029) and pick a different region/genre (e.g. Central/Eastern
European, Latin American, Oceanian, or electronic songcraft).
