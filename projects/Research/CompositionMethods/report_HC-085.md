# REPORT HC-085 — Danmono (Koto Sectional Variation) Composition

**Generated:** 2026-11-05 (scheduled nightly research job)
**Method ID:** HC-085
**Layer:** `human (→concrete)` — target layer **concrete** when realized through the UnitMatrix
**Detail file:** `human_method_HC-085_danmono-koto-sectional-variation.md`
**DB:** row appended to `human_methods_db.md` (Human Composition Methods Framework table)

---

## 1. Method name & tradition

**Danmono (段物)** — Japanese koto (sōkyoku) sectional-variation composition: a piece of N movements ("dans", 段 = step), **every dan exactly the same length**, each a progressively denser variation of the first dan's theme. Fixed in the 17th century by the Yatsuhashi school; transmitted through Ikuta-ryū and Yamada-ryū; the canonical solo-koto form of the Edo period.

- **Tradition:** Japanese sōkyoku (koto chamber music); Yatsuhashi Kengyō (1614–1685), blind *kengyō*, "Father of Modern Koto" — first to bring the koto from the court to the general public; adapted the **hirajōshi** tuning and **In/insen** scale from shamisen practice; also created the kumiuta song cycle.
- **Repertoire (8 pieces):** Godan (5 dan), Rokudan (6), Shichidan (7), Hachidan (8), Kudan (9), Kumoi Kudan (9, in hon-kumoijoshi tuning), Midare (irregular danmono — 10 dan in Ikuta-ryū, 12 in Yamada-ryū), plus Mitsuzaki Kengyō's *Aki kaze no kyoku* whose introduction is in danmono form.
- **Key facts (verified online, Wikipedia + Adriaansz citations):**
  - Each dan = 52 beats (traditional count; = 13 bars of 4/4; Adriaansz counts 104 half-beats — same duration, doubled unit). Rokudan dan 1 has 4 extra beats (56) / a 4–8 beat **kandō** introduction precedes the first dan (Adriaansz 1967, p.28).
  - Tempo: each dan begins slowly, accelerates internally, slows at its end; the piece accelerates dan→dan; the very end decelerates to a slow close (Adriaansz 1970, p.27).
  - The pieces are deliberately uniform — "listeners unfamiliar with the danmono style have trouble distinguishing one piece from another"; originality was unusual for 17th-c. Japanese composers (Adriaansz 1967, p.28).
  - Authorship contested: *Rokudan* — Yatsuhashi (per Sokyoku taiisho 1779 / Buso gafu taiseishu 1812 / Kumiuta zenshu 1941) or Kitajima Kengyō (per Koto no kumiuta 1822); *Midare* — Yatsuhashi/Kurahashi; *Hachidan* — Yatsuhashi/Kurahashi; *Kudan* — unknown/Kitajima; *Shichidan* — unknown/Yasumura; *Godan* — Kitajima or Ikuta/Tomino Koto; *Kumoi Kudan* — Mitsuhashi (Adriaansz 1967 table).
  - Hirajōshi: hemitonic pentatonic, interval pattern **2-1-4-1-4** semitones; on the koto D-tuning: open strings **D–F–G–A–C** (+ octaves across 13 strings). Yatsuhashi adapted it from shamisen (Harich-Scheider 1973). Rokudan's melody is associated with the In/insen scale; the tuning's "missing" degrees are produced by left-hand **oshiide** bends.

## 2. Why this method, why now (rotation & overlap check)

- Recent IDs: HC-084 rebetiko (Greece), HC-083 mariachi (Mexico), HC-082 Jingju (China), HC-081 Gnawa (Morocco), HC-080 Notre-Dame (France), HC-079 musique concrète (France), HC-078 Tin Pan Alley (US), HC-077 Kulintang (Philippines).
- Japan in the DB: only HC-041 gagaku (court orchestral stratification) and HC-029 honkyoku (shakuhachi *ma*). **No koto/sōkyoku form existed** — danmono fills that gap.
- Overlap check: HC-066 ground-bass variation = Western ostinato chain, free-length statements; HC-074 isorhythm = pitch×rhythm cycles on tenor; HC-080 organum = chant elaboration; HC-077 kulintang = gong rhythmic modes. None shares danmono's signature invariant: **every variation section has the exact same duration**.
- Grep check over CompositionMethods dir for `danmono|koto|sōkyoku|Yatsuhashi|hirajoshi|kandō|shamisen` → 0 hits in the human DB.

## 3. The craft procedure in detail (how the human does it)

1. **Apprentice** by ear + traditional tablature (string numbers 一…十三, finger strokes, left-hand signs — not absolute pitches; the pitch content lives in the tuning). Blind kengyō internalized the repertoire entirely by ear. Master *tsume* right-hand plucking and left-hand techniques: **kizuki** (plucks), **oshiide** (pressure bend up — the signature hirajōshi ornament), **hajiki** (snap), bass-register strokes on the lower strings.
2. **Fix the tuning** (hirajōshi D–F–G–A–C for the core; hon-kumoijoshi for *Kumoi Kudan*): the tuning IS the composition's pitch field.
3. **Compose dan 1 = the theme:** one complete 52-beat sentence (13 bars of 4/4), slow, long note values, wide registral sweep, a recognizable opening gesture, ending on the piece's **cadential formula** (fixed dan-end cadence on the field's tonic). Optional **kandō** 4–8-beat introduction before dan 1 (in Rokudan: +4 beats folded into dan 1).
4. **Compose dans 2–N as variations of EXACTLY equal length (52 beats)**, preserving the theme's structural tones at phrase/cadence points. Variation operators, applied by hand at the instrument:
   - rhythmic subdivision — the engine: quarter→8th→16th figuration, monotonically denser dan to dan;
   - ornamentation (oshiide bends, snaps);
   - register shift / figuration exchange between melody and accompaniment strings;
   - technique rotation (different stroke/bend combinations).
   Every dan closes on the same cadential formula.
5. **Set the tempo curve:** per-dan slow→fast→slow envelope; global accelerando dan→dan; final dan decelerando + slow close. Part of the composition, not performance.
6. **Optional sankyoku setting:** koto leads; shamisen doubles/supports; shakuhachi weaves heterophonic ornaments. (The solo koto version is canonical today.)
7. **Fix & transmit per school:** Ikuta-ryū / Yamada-ryū versions differ (Midare dan counts); players learn multiple school versions.

## 4. Practitioner examples

- **Yatsuhashi Kengyō** (1614–1685) — *Rokudan no Shirabe* (六段の調, six 52-beat dans, first +4), *Midare*, *Hachidan* (attributed); "Father of Modern Koto"; adapted hirajōshi + insen scales; created kumiuta.
- **Disputed composers** (Adriaansz 1967): Kitajima Kengyō (Rokudan/Kudan per some sources), Kurahashi (Midare/Hachidan), Yasumura (Shichidan), Tomino Koto (Godan), Mitsuhashi (Kumoi Kudan) — authorship communal, transmission oral.
- **Mitsuzaki Kengyō** — *Aki kaze no kyoku* (danmono-form introduction).
- **School heads:** Ikuta Kengyō (Ikuta-ryū, 1656–1688), Yamada Kengyō (Yamada-ryū, 1757–1817) — fixed the performing versions taught today.
- **Modern lineage:** Michio Miyagi (1894–1956, 300+ works, 17-string bass koto, *Haru no Umi*); Tadao Sawai, Kazue Sawai (internationalization).
- **Scholars:** Willem Adriaansz (*Research into the Chronology of Danmono*, Ethnomusicology 11/1 1967; *A Japanese Procrustean Bed*, JAMS 23 1970), William P. Malm.

## 5. UnitMatrix mapping (Musical Elements Framework)

**Elements:** STRUCTURE (fixed-length sectional variation chain), RHYTHM (progressive subdivision + tempo-curve envelope), PITCH (hirajōshi/In pentatonic field + bend ornaments), TEXTURE (solo koto melody/accompaniment; optional sankyoku heterophony). HARMONY: emergent — no functional progressions.

### Voices
- **V0 = Koto melody spine** — theme (dan 1) + all variations; carries opening gesture and dan-end cadence; identity anchor across every column.
- **V1 = Koto accompaniment layer** — left-hand/low-register bass strokes (sustained tones, cadential support) under V0.
- **V2 = Shamisen support** (sankyoku, optional) — sparser doubling/support line, same dan columns.
- **V3 = Shakuhachi ornament line** (sankyoku, optional) — heterophonic elaboration with breath-phrase shaping.
- **V4 = Metadata** — tuning tag, dan index, kandō marker, tempo-curve markers, technique tags (oshiide/hajiki).

### Sections
S0 Kandō (4–8 beats) → S1 Dan 1 (theme, 52 beats) → S2 Dan 2 → S3 Dan 3 → S4 Dan 4 → S5 Dan 5 → S6 Dan 6 (final decelerando + closing cadence). Kudan variant: 9 dan columns. **Every dan column = 52 beats × 480 ticks/beat = 24,960 ticks** — equal-length invariance is the form's hard rule, i.e. the engine's zero-drift invariant IS the danmono invariant.

### Rules to encode
1. **Dan-length invariance** — every cell in every voice pads to the identical terminal landmark; `validate()` is the compositional gate, not just an engine check.
2. **Tuning pitch-set constraint** — D–F–G–A–C (+octaves; hon-kumoijoshi variant for Kumoi Kudan); intermediate pitches only as short oshiide ornaments.
3. **Theme-skeleton preservation** — dans 2–N share structural tones + dan-end cadence; variation operators (subdivision/ornament/register/technique) with figuration density monotone non-decreasing.
4. **Opening-gesture recognition** — each dan opens with a recognizable variant of the piece's opening figure.
5. **Dan-end cadential formula lock** — same cadence type, landing on the field's tonic, every dan.
6. **Tempo-curve envelope** — per-dan rubato slow→fast→slow; global accelerando; final ritardando.
7. **Sankyoku separation** (optional) — V2/V3 heterophonic, sparser, no crossing above structural register except cadence fills.
8. **Kandō gate** — S0 exists only before dan 1; V1/V4 support only.
9. **Zero-drift validate + strong rubato humanize** — danmono is rubato music; grid-locked MIDI reads as machine; keep column terminal landmarks untouched.

### Realization path
Framework row → `UnitMatrixComposer` (5 voices × 7 sections Rokudan / 10 columns Kudan) → hirajōshi pitch filter per voice → theme in S1, variation operators per dan (subdivision map 1×→2×→4×→8×) → `fill_voice_section` → `validate()` → `to_midi` → humanize (accelerando rubato profiles per dan; V1 strict, V0 loose) → FluidSynth render (GM: koto ≈ plucked-strings/koto patch or nylon guitar/pizzicato; shamisen ≈ banjo/muted pluck; shakuhachi ≈ flute w/ breath) → `provenance.json` + grid visualization. Per AGENTS.md: all artifacts under `projects/Research/outputs/<project>/`, assert file size > 40 B after render.

## 6. Table row added (human_methods_db.md, Human Composition Methods Framework)

```
| **HC-085** | human (→concrete) | Danmono (Koto Sectional Variation) Composition — Fixed-Length *Dan* Architecture & Progressive Figuration (Yatsuhashi-School Sōkyoku Craft) | Japanese sōkyoku (koto chamber music) — Yatsuhashi school (Yatsuhashi Kengyō 1614–1685, "Father of Modern Koto"), 17th-c. Edo Japan; Ikuta-ryū (1656–) & Yamada-ryū (1757–) school versions; scholars Adriaansz (1967/1970), Malm | STRUCTURE, RHYTHM, PITCH, TEXTURE | <craft procedure — see detail file> | <UnitMatrix — see detail file> | Yatsuhashi Kengyō (Rokudan no Shirabe; Midare; Hachidan), Kitajima/Kurahashi/Yasumura/Tomino Koto/Mitsuhashi (disputed authorship), Mitsuzaki Kengyō, Ikuta & Yamada Kengyō, Michio Miyagi; scholars Adriaansz, Malm | ✅ Documented |
```
(Full text written to the DB; abbreviated here for readability.)

## 7. Verification

- `grep HC-085 human_method_HC-085_danmono-koto-sectional-variation.md` → found (Method ID line).
- `grep HC-085 human_methods_db.md` → found (row present).
- Highest ID now HC-085 → **next free ID: HC-086**.

## 8. Quirks & pitfalls

- **Two beat-count conventions:** 52 beats/dan (traditional) vs 104 half-beats (Adriaansz) — pick one convention in code; they are the same duration only if the unit halves.
- **First column ≠ dan columns:** Rokudan dan 1 has +4 beats (56) or a separate kandō intro — model kandō as its own S0 column so the six dan columns stay byte-equal.
- **Tablature, not notes:** string-number notation; transcribe the tuning to concrete pitches before writing units.
- **No functional harmony:** hemitonic pentatonic mode + bends; no chord progression to encode.
- **Rubato is normative:** strict quantization + steady tempo destroys the form's identity; compose the tempo envelope into the humanize profile.
- **Originality was not the goal:** pieces sound alike by design (Adriaansz); "fixing" the formula breaks the genre. Midare is the single sanctioned irregularity.
- **Attribution contested:** cite Yatsuhashi authorship as attributed/disputed.
