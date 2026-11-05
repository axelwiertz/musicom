# Report HC-084 — Rebetiko (Greek Urban Song) Composition: Dromos × Taximi × Zeibekiko/Hasapiko Dance-Rhythm Craft

**Date:** 2026-11-04 (nightly `daily-human-composition-research` run)
**Method ID:** HC-084
**Layer:** `human (→concrete)` — target layer **concrete** when realized through the UnitMatrix. This is human-craft knowledge (how a bouzouki player of the tekedes/tavernas actually composes), realized as concrete notes/grids via the Musicom engine.

---

## 1. Method & tradition (summary)

**Rebetiko song-craft** — Greek urban popular song (late 19th c.–1950s): an orally-composed strophic song following a **dromos** (makam-derived Greek popular mode), framed by free **taximi** improvisation, set to **dance rhythms** (zeibekiko 9/4·9/8, hasapiko 4/4, hasaposerviko 2/4, tsifteteli 4/4…), carried by the **bouzouki**, which is also the rhythm section (no drum kit in the classic Piraeus style). UNESCO Representative List 2017.

**Tradition/culture:** Greek urban song — Smyrna/Constantinople Ottoman-café lineage (Smyrneïka) fused with mainland Piraeus mangas style in the 1930s; classic phase by late 1930s; Metaxas censorship 1937; post-war Tsitsanis Westernization → laïko; revival 1960s–70s.

## 2. Why this ID / rotation

- Highest existing HC-ID before this run: **HC-083** (verified: DB table rows `| **HC-NNN** |` scan + 83 `human_method_HC-*.md` files + report files; max = 083).
- New ID: **HC-084** — no HC-084 exists in table, detail files, or reports (only referenced as "next free ID" in report_HC-083.md).
- Rotation: last seven = mariachi (083, Mexico), Jingju (082, China), Gnawa (081, Morocco), Notre-Dame (080, France), concrète (079, France), Tin Pan Alley (078, US), Kulintang (077, Philippines). **Greece/Balkans nearly absent** (only Hungary 060, Bulgaria 019) — Greek urban song never covered. Overlap-checked vs HC-003 (makam heterophony), HC-031 (radif), HC-004 (raga-tala): unique as urban orally-composed modal SONG with free prelude + string-carried dance rhythm.

## 3. Craft procedure (how the human does it)

1. **Apprentice by ear** ("pézo me to aftí" — play by ear; no scores, no written theory); absorb meraki/kefi/kaimos aesthetic (Hatzidakis). Early teké practice: circle of singers, each adding a verse, no refrain, songs lasting hours (Petropoulos).
2. **Choose the dromos** (δρόμος, "road") — modal pathway named from Turkish makams: ousák (uşşâk), hitzáz (hicâz/phrygian dominant), rast, saba(h), kiourdi (kürdî), nahawand, plus matzóre (major) / minóre (minor). The makam system is the melodic core.
3. **Fix the mode's grammar** (not just a scale): idioms (*idhiomatismí* — e.g., ousák's unstable 2nd: flat ascending, natural descending; 6th gravitating to 7th), dominant notes/*élxis* (gravitational pull of the mode's central tone), cadences (*katalíxis* — interim vs final), and the rast-pentachord-below-tonic gesture idiom of ousák/hitzáz.
4. **Improvise the taximi** — free, unmeasured prelude in the dromos (beginning or middle of the song; also inside the song over the ad-lib rhythm), over the **íso** drone; establishes tonality/dromos, displays skill, closes on a cadence launching the metered song.
5. **Set the dance rhythm** — zeibekiko 9/4·9/8 (grouping 2+2+2+3, solo "eagle" dance), hasapiko 4/4 (hasapikos varys), hasaposerviko 2/4 (fast), tsifteteli 4/4, karsilamas 9/8, aptalikos 9/4/9/16, bolero 3/4, kalamatianos 7/8. **The bouzouki strum patterns are the drums** (no kit); komboloi-on-glass clicks add time; toubeleki in Smyrna style.
6. **Compose the song** — strophic verses (8- or 15-syllable lines), syllabic setting, phrase-end melisma, verbatim refrain; themes of the urban underworld + universal (love, loss, exile, mother, death). *Amanedes* variant: improvised unmeasured lament with "aman" exclamations.
7. **Voice the ensemble** — bouzouki (lead + taximi + strum), baglamas (octave doubling, light ornaments), guitar (harmonic-rhythmic bed), later double bass; Smyrna: violin, oud, kanonaki, santouri, politiki lyra, cimbalom. **Harmony is mode-derived, not functional** — chords are stacks of the mode's tones, cadence chords per katalíxis.
8. **Direct the band by ear** — the bouzouki player calls "D minóre zeimbékiko" (tonality + first chord + rhythm); the band follows by recognition/modal structure.
9. **Chain the form** — taximi → verse → refrain → interlude (taximi/orchestra break) → verse → refrain → closing taximi + ritardando cadence. Dancing sets: the **hasapiko service** — chained hasapiko songs, accelerating slow 4/4 → fast 2/4 hasaposerviko.

## 4. Practitioner examples

- **Markos Vamvakaris** (1905–1972) — "patriarch of the bouzouki"; first Greek bouzouki recordings Oct 1932; Piraeus zeibekika/hasapika/hasiklidika (*Frangosyriani*, *Vre ti manna sou*).
- **Piraeus Quartet** — Vamvakaris, Yiorgos Batis, Anestis Delias, Stratos Pagioumtzis (1930s shellac classics).
- **Smyrna style** — Roza Eskenazi (Smyrna Trio: Semsis violin, Tomboulis oud), Rita Abatzi, Marika Papagika, Smyrneiki Estudiantina; A&R directors Panagiotis Toundas, Spyros Peristeris.
- **Vassilis Tsitsanis** (1915–1984) — hundreds of songs, bridge to laïko; *Synnefiasmeni Kyriaki* ("Cloudy Sunday"); singers Sotiria Bellou, Marika Ninou, Stella Haskil, Ioanna Georgakopoulou.
- **Manolis Chiotis** — 4-course bouzouki (1953/56), Latin influences, electrification.
- **Manos Hatzidakis** — 1948 legitimizing lecture; *Six Folk Paintings* (1951).
- Revival: Grigoris Bithikotsis, Stelios Kazantzidis, Giorgos Zambetas; scholars Holst-Warhaft, Petropoulos, Gauntlett, Pennanen, Ordoulidis. UNESCO ICH Representative List 2017.

## 5. UnitMatrix mapping (Musical Elements Framework: PITCH, STRUCTURE, RHYTHM, TEXTURE, HARMONY)

### Voices (7 active + metadata)
| Voice | Role | UnitMatrix cell content |
|---|---|---|
| V0 | Bouzouki lead spine | dromos carrier: taximi melody + song melody; strum rhythm in low register |
| V1 | 2nd bouzouki/guitar | per-rhythm strum dictionary; dromos-derived chord skeleton |
| V2 | Vocal lead | strophic verses + verbatim refrain; syllabic 8/15-syllable setting |
| V3 | Baglamas/tzouras | high octave (+12/+24) doubling, sparse ornaments |
| V4 | Íso drone | sustained tonic pedal under taximi (and optional under verses) |
| V5 | Bass (double bass) | root movement/walk (later-period texture) |
| V6 | Komboloi/toubeleki | glass-click / hand-drum pattern per rhythm (strict, sparse) |
| V7 | Metadata | dromos tag, idiom tags, rhythm tag, taximi markers, band-call string |

### Sections
S0 Taximi (free, unmeasured; V0 over V4 drone; opens/closes on dromos cadence) → S1 Verse 1 → S2 Refrain (byte-identical repeat) → S3 Interlude (instrumental; V2 silent) → S4 Verse 2 → S5 Refrain → S6 Closing Taximi/Cadence (ritardando). Hasapiko service: S7–S11 = chained second/third song blocks with 4/4 → 2/4 acceleration.

### Rules to encode
1. Dromos pitch-set constraint per voice (hitzáz 1–♭2–3–♯4–5–♭6–♭7; ousák with unstable ♭2; rast/matzóre major; minóre nahawand; saba/kiourdi variants).
2. Idiom filters: unstable-2nd behavior; rast-pentachord-below-tonic gesture (ousák/hitzáz only); élxis dominant gravitation; interim/final katalíxis cadence formulas.
3. Taximi cells: free-rhythm units over V4 drone, quantized for the engine (long-note skeleton + rubato humanize), start/end dromos-legal.
4. Rhythm-grid lock: 9/8·9/4 zeibekiko with 2+2+2+3 accent map; 4/4 hasapiko; 2/4 hasaposerviko; 4/4 tsifteteli; 9/8 karsilamas — constant per song.
5. Strophic + verbatim refrain; verse line = 8/15 syllables, one note per syllable except cadence melisma.
6. Dromos-derived harmony (no functional ii–V–I); cadence chords per katalíxis; tonic quality fixed by dromos.
7. Baglamas doubling: +12/+24, sparser, never below V0.
8. Interlude separation: V2 rests in S3/S6; V0 leads; call-and-answer at phrase gaps.
9. Hasapiko-service acceleration + final ritardando only in cadence column.
10. Zero-drift validate gate + humanize (rhythm section strict; vocal/bouzouki solo loose).

### Realization path
Framework row → `UnitMatrixComposer` (7 voices × 7 or 11 sections) → dromos pitch filter per voice → `fill_voice_section` → `validate()` → `to_midi` → humanize (per-role DNA) → FluidSynth render (GM: bouzouki ≈ nylon guitar/mandolin, baglamas ≈ mandolin +12, vocal lead patch, acoustic bass, woodblock clicks) → `provenance.json` + grid visualization.

## 6. Table row added to human_methods_db.md

```
| **HC-084** | human (→concrete) | Rebetiko (Greek Urban Song) Composition — Dromos Modal Song-Craft × Taximi Free Prelude × Zeibekiko/Hasapiko Dance-Rhythm Architecture (Bouzouki-Carried Strophic Form) | Greek urban song — rebetiko/rembetika: Smyrna & Constantinople Ottoman-café lineage → Piraeus/Athens/Thessaloniki 1920s–1950s; classic phase 1930s; revival 1960s–70s; UNESCO Representative List 2017 | PITCH (dromos), STRUCTURE, RHYTHM, TEXTURE, HARMONY (dromos-derived) | Apprentice by ear (pézo me to aftí — play by ear, no scores) → choose the dromos (modal "road" from makam names: ousák, hitzáz, rast, saba, kiourdi, nahawand, matzóre/minóre) → fix the mode's grammar (idioms: ousák unstable 2nd flat-ascent/natural-descent, 6th→7th gravitation; élxis dominant pull; interim/final katalíxis cadences; rast-pentachord idiom in ousák/hitzáz) → improvise the taximi (free unmeasured prelude in the dromos over íso drone; opening/middle/closing) → set the dance rhythm (zeibekiko 9/4·9/8 2+2+2+3, hasapiko 4/4, hasaposerviko 2/4, tsifteteli 4/4 — the bouzouki strum patterns ARE the drums, no kit) → compose strophic song (8-/15-syllable lines, syllabic setting, phrase-end melisma, verbatim refrain; amanedes = free lament variant) → voice the ensemble (bouzouki lead, baglamas octave doubling, guitar bed, later double bass; harmony = mode-tone chords, NOT functional) → direct band by ear ("D minóre zeimbékiko" = key + first chord + rhythm) → chain form (taximi→verse→refrain→interlude→verse→refrain→closing taximi + ritardando; hasapiko service = chained accelerating dance set) | Voice 0 = bouzouki lead spine (taximi + melody, dromos carrier). Voice 1 = 2nd bouzouki/guitar (per-rhythm strum dictionary, dromos chord skeleton). Voice 2 = vocal lead (strophic verses, syllabic, melisma at phrase ends). Voice 3 = baglamas/tzouras (octave doubling + light ornaments). Voice 4 = íso drone (sustained tonic under taximi). Voice 5 = double bass (root/walk, later texture). Voice 6 = komboloi/toubeleki percussion (glass-click/hand-drum per rhythm). Voice 7 = metadata (dromos, idiom, rhythm, section, taximi tags). Sections = S0 Taximi → S1 Verse 1 → S2 Refrain → S3 Interlude → S4 Verse 2 → S5 Refrain → S6 Closing Taximi/Cadence; hasapiko service = chained S7–S11 with 4/4→2/4 acceleration. Rules: dromos pitch-set + idiom filters, élxis gravitation, katalíxis cadence formulas, rhythm-grid lock (2+2+2+3 zeibekiko etc.), strophic + verbatim-refrain, mode-derived harmony (no functional progressions), baglamas doubling, interlude vocal-rest separation, ritardando close, zero-drift validate | Markos Vamvakaris (Frangosyriani; first bouzouki discs 1932), Piraeus Quartet (Batis, Delias, Pagioumtzis), Smyrna style — Roza Eskenazi, Rita Abatzi, Marika Papagika, Smyrneiki Estudiantina; Vassilis Tsitsanis (Synnefiasmeni Kyriaki, bridge to laïko), Sotiria Bellou, Manolis Chiotis (4-course bouzouki), Manos Hatzidakis (1948 lecture, Six Folk Paintings); scholars Holst-Warhaft, Petropoulos, Pennanen, Ordoulidis | ✅ Documented |
```

Appended as line 90 (after the HC-083 row, line 89).

## 7. Verification

- Grep `HC-084` in `human_method_HC-084_rebetiko-dromos-taximi-craft.md` → present (header + body).
- Grep `HC-084` in `human_methods_db.md` → present (new table row, line 90).
- Grep `HC-084` in `report_HC-084.md` → present (this file).
- Highest existing ID after append: **HC-084** → **next free ID: HC-085**.

## 8. Quirks & pitfalls

- **Dromos ≠ scale** — a behavioral road (idioms/élxis/cadences); pitch-set filter alone yields un-rebetiko melody. Encode phrase-level idiom rules.
- **No functional harmony** — mode-tone chords; forcing ii–V–I under hitzáz breaks the genre. Ottoman microtones ≈ 12-TET on the bouzouki (Pennanen) — quantize to equal temperament, don't fake microtones.
- **Rhythm lives in the strings** — classic Piraeus has no drum kit; adding one reads as laïko/archontorebetiko.
- **Oral tradition** — scores are memory aids; model grammar, vary ornament per performance.
- **Censorship** (1937–46) — text-level concern, music never censored.
- **Trichordo vs tetrachordo** — scope the method to the classic 3-course texture; post-1953 Chiotis tetrachordo changes chord vocabulary.
- **Zeibekiko vs hasapiko accent grammars** must not be mixed.
- Only `human_methods_db.md` modified; `methods_db.md` (algorithmic) untouched.
