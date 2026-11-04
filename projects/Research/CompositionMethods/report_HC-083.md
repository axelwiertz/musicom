# Report HC-083 — Mariachi Son Jalisciense Composition: Copla-Refrain Song × Sesquialtera (6/8–3/4) Armonía × Parallel-Third Violin & Trumpet Obligado Craft

**Job:** daily-human-composition-research (nightly cron, 2026-11-03)
**Method ID:** HC-083
**Detail file:** `human_method_HC-083_mariachi-son-jalisciense-craft.md`
**Next free ID:** HC-084

---

## 1. Method name & tradition

**Son jalisciense composition** — the craft of building the fast, copla-driven song form of western Mexico's mariachi tradition: a fixed **estribillo** (refrain) chained to **coplas** (verse stanzas, often improvised), set over the signature **sesquialtera** rhythm (alternating 6/8 and 3/4 bars), harmonized by a tonic–dominant **armonía** (vihuela + guitar + guitarrón), and doubled/answered by **violins in parallel thirds** plus a **trumpet obligado**.

- **Tradition / Culture:** Mexican mariachi, rooted in the *son jalisciense* of Jalisco/Nayarit (19th c.), itself part of the *son mexicano* family (Veracruz, Huasteca, Guerrero/Oaxaca, Michoacán, Jalisco) that blends Spanish, African, and Indigenous elements — all descendants of Spanish baroque guitar/violin practice brought to New Spain. The old ensemble: one vihuela, two violins, guitarrón (which by the 19th century largely replaced the harp). **Trumpets were added in the 1910s–1920s and became a fixture by the 1930s.** National prominence in the first half of the 20th c. via presidential inaugurations, radio, and the charro-cinema era (Negrete, Infante, Reyes). Modern ensemble: up to 8 violins, 2 trumpets, vihuela, guitarrón, guitars; repertoire covers sones, rancheras, corridos, huapangos, jarabes, boleros, danzones, cumbias, polkas, waltzes. **UNESCO ICH Representative List (2011).**
- **Layer:** `human (→concrete)` — target layer **concrete** when realized through the UnitMatrix (human-craft knowledge: how a mariachi sonero team — singer, violinists, trumpeter, vihuela/guitarrón strummers — composes and fixes a son by ear in rehearsal, without an authoritative score).

## 2. Why this method, why now

ID rotation: HC-082 Jingju (China), HC-081 Gnawa (Morocco), HC-080 Notre-Dame organum (France), HC-079 Musique Concrète (France), HC-078 Tin Pan Alley (US), HC-077 Kulintang (Philippines). **Latin America is present (samba 058, bossa 053, choro 034, rumba 048, montuno 018, tango 030, sikuri 042) but Mexico is completely absent from the DB** — no mariachi, no son mexicano, no ranchera, no jarabe/huapango. Overlap check: HC-018 clave montuno (Cuban guajeo under a vocal layer) is the nearest rhythmic cousin but a different tradition; HC-012 flamenco compás-falseta shares "fixed rhythmic pattern + improvised melodic block"; HC-053/058 are Brazilian; HC-034 choro shares the parallel-3rds texture but is instrumental Brazilian. Son jalisciense is unique in the DB as **a sung copla/refrain song craft whose engine is a metrical hemiola (6/8↔3/4 sesquialtera) locked by the armonía, with a parallel-third violin duet and octave/obligado trumpet** — one integrated small-ensemble human system. No duplicate: grep `mariachi|ranchera|son jalisciense|guitarrón|vihuela|sesquialtera|jarabe|huapango` → 0 hits in the human DB (only `methods_db.md`, the algorithmic DB owned by another job — untouched).

## 3. The craft procedure in detail (how the human executes it)

### Stage 0 — apprenticeship (oral/aural transmission)
1. Sones are learned **by ear** in family/ensemble, singer-to-singer; no authoritative score exists for the folk sones. Jesús Jáuregui's 20+ years of research on *El Son de la Negra* (conference, Nayarit 2010) documents that the tune "has undergone modifications and arrangements that can hardly be attributed to a single author or epoch" — collective authorship, living variants. Notation, when used, is a memory aid.
2. The apprentice learns strumming and singing/dancing together: the copla singer knows the zapateado, whose stomps accent the same hemiola the armonía plays.

### Stage 1 — fix the harmonic cell and key
3. Pick a **major key** (sones jaliscienses are "mostly in major keys") and a **tonic–dominant cell**: the harmony alternates essentially I–V (occasional IV), no chromaticism. The whole son is composed over this repeating cell.
4. The **guitarrón** (6-string, fretless, re-entrant tuning A–D–G–C–E–A; developed from the Spanish *bajo de uña*) lays the bass: **bordones** (open-string root–fifth notes), frequently **doubled at the octave**, with short walking pickup figures leading into each downbeat.

### Stage 2 — set the sesquialtera (rhythmic engine)
5. Lock the **sesquialtera**: one bar of **6/8** (3+3) followed by one bar of **3/4** (2+2+2), alternating throughout, carried by the armonía (vihuela + guitars) and guitarrón together. Both bars hold the same six eighth-note units → a true hemiola (3:2 regrouping), not a change of bar length.
6. **Vihuela** (5-string, high-pitched) strums **rasgueados** in the high register marking the hemiola's offbeat energy; guitar(s) strum the chord rhythm; the combined pattern is the famous "son rhythm": accented dotted-quarter bars alternating with three-quarter bars.
7. Optional percussion: **zapateado** stomps on a wooden platform; sones are fast (allegro).

### Stage 3 — compose the text: estribillo + coplas
8. Write/choose the **estribillo**: 1–2 short fixed lines, repeated verbatim — the song's identity hook.
9. Compose **coplas**: short stanzas — 4-line **cuartetas** or 6-line **sextillas** (rhyme abcbdb), each line ending on a strong downbeat; **syllabic** text-setting in 6/8; high register, light ornaments; coplas may be improvised/traded in performance (sonecitos del país). Subjects: love, betrayal, regional pride, animals, humor, machismo — short, never narrative (that is the corrido's job).
10. Alternate **estribillo → copla → estribillo → copla…**: singer solo on coplas, ensemble joins the refrain.

### Stage 4 — voice the instruments around the melody
11. **Violins** (two) play the vocal melody **in parallel thirds** (the "tercia" sound), high and bright, with ornaments; first violin leads instrumental passages.
12. **Trumpet** (Miguel Martínez of Mariachi Vargas codified the style in the 1930s): **rests during vocal coplas**, plays short **obligado answers** between phrases, **octave-doubles the melody** or takes the lead in instrumental sections; bright, projecting tone above the strings.
13. All players sing — every musician doubles as chorus on the estribillo.

### Stage 5 — assemble the form & fix the arrangement
14. Chain the sections: **instrumental intro** (armonía alone states the hemiola) → **estribillo** → **copla 1** → **monte / instrumental interlude** (violin↔trumpet phrase-trading, register rises) → **estribillo** → **copla 2** → **monte II (faster, higher)** → **remate** (V–I cadential flourish, strummed rasgueo, *grito* shout "¡arriba!/¡olé!", zapateado stamp).
15. The arrangement is **fixed by ensemble tradition**: each mariachi keeps a house version; Blas Galindo's 1940 *Sones de Mariachi* suite (premiered in New York) is one concert adaptation of *El Son de la Negra*; Rubén Fuentes (violinist, artistic director of Mariachi Vargas from 1950) shaped the modern repertoire's arrangements.

## 4. Practitioner examples

- **Mariachi Vargas de Tecalitlán** (founded by Gaspar Vargas, led by Silvestre Vargas from 1928; in Mexico City from the 1930s) — the canonical ensemble: recordings, films, defining arrangements of *El Son de la Negra*; **Rubén Fuentes** (violinist/arranger) and **Miguel Martínez** (first great mariachi trumpeter) built the modern sound.
- **Blas Galindo (1910–1993)** — composer; adapted *El Son de la Negra* (1940) in *Sones de Mariachi*, carrying the folk son to the concert stage.
- **Jesús Jáuregui** — ethnomusicologist; provenance studies (2010) proving the collective, multi-author history of *El Son de la Negra* — the textbook case of oral son transmission.
- **Charro-cinema singers** — Jorge Negrete, Pedro Infante, **Lucha Reyes** (*La Tequilera*): nationalized sones and rancheras via film/radio in the 1930s–50s.
- **José Alfredo Jiménez (1926–1973)** — ranchera canon ("basis of modern regional Mexican music"): *El Rey*, *Si Nos Dejan*, *Que Bonito Amor*, *La Media Vuelta* — the sibling song craft on the same mariachi armonía language (3/4, 2/4).
- **Tomás Méndez** — *Cucurrucucú Paloma*, *Que Te Vaya Bonito* (rancheras).
- **Vicente Fernández** — *Volver Volver*, *El Rey*; kept the mariachi arrangement tradition alive to the present.
- Family members: **jarabe tapatío** (national dance; standard music by Jesús González Rubio, 19th c., arranged 1920s as a medley of son rhythms) and **huapango de mariachi** (Huasteca son for full ensemble). Scholarship: Jesús Jáuregui, Jonathan Clark (mariachi history).

## 5. UnitMatrix mapping

### Voices
- **V0 = Vocal lead** — estribillo + coplas; syllabic 6/8 declamation, high register, light ornaments; *grito* event at remate.
- **V1 = Violin duet** — vocal melody doubled in **parallel thirds**; ornaments; leads monte blocks.
- **V2 = Trumpet** — obligado answers between vocal phrases; rests during coplas; octave doubling in monte.
- **V3 = Vihuela** — rasgueado strum dictionary; hemiola offbeat/backbeat attack map, high register.
- **V4 = Guitar / armonía** — I–V chord-strum rhythm; the 6/8↔3/4 bar-pattern lock.
- **V5 = Guitarrón** — bordones (root–fifth open-string bass), octave doublings, walking pickups.
- **V6 = Zapateado (optional)** — stomp accents doubling the hemiola; stamps at remate.

### Sections
Columns = the **son form chain** — every bar is 6 eighths whether 6/8 or 3/4, so bar lengths are naturally equal (zero drift trivial):
S0 Intro (armonía alone) → S1 Estribillo → S2 Copla 1 → S3 Monte I (violin↔trumpet antiphony) → S4 Estribillo (repeat) → S5 Copla 2 → S6 Monte II (faster/higher) → S7 Remate (V–I rasgueo + grito + stomp). All voices padded to full column length; `validate()` must pass.

### Rules to encode
1. **Sesquialtera lock:** even/odd bars group 3+3 (6/8) vs 2+2+2 (3/4); armonía + guitarrón accent maps follow; equal tick length both ways.
2. **Harmony cell:** I–V alternation (occasional IV); guitarrón root–fifth bordones with octave doubling; no chromatic harmony; major keys.
3. **Parallel-thirds duet:** V1 = V0 transposed a 3rd, adjusted to the nearest I–V chord tone (the human violinist's by-ear correction).
4. **Trumpet separation:** V2 silent during vocal coplas; answers between phrases; octave-doubles V0/V1 in monte sections only.
5. **Copla prosody:** cuarteta/sextilla (abcbdb), syllabic setting, line ends on downbeats; estribillo verbatim-repeated identity anchor.
6. **Monte antiphony:** violin/trumpet alternate phrases (≥1 phrase rest); register ascent Monte I→II.
7. **Remate:** V–I cadence, strummed rasgueo, optional grito + zapateado stamp; fast tempo throughout.
8. **Vihuela strum dictionary:** per-bar attack maps (6/8: accents on eighth 1 & 4; 3/4: accents on eighths 1, 3, 5) — the hemiola made audible.
9. **Zero-drift:** equal-length bars; free vocal melisma quantized to the 6-eighth grid; `validate()` gate.
10. **Humanize:** guitarrón/vihuela strict (groove anchors), vocal rubato + portamento, violin slight layback; grito as a loud short remate event.

### Realization path
Framework row → `UnitMatrixComposer` (7 voices × 8-section chain) → `fill_voice_section` per cell → `validate()` → `to_midi` → humanize (per-role DNA) → FluidSynth render (GM: violin≈strings, trumpet≈trumpet, guitarrón≈acoustic bass, vihuela≈nylon guitar, zapateado≈woodblock) → `provenance.json` + grid visualization.

## 6. Table row added

```
| **HC-083** | human (→concrete) | Mariachi Son Jalisciense Composition — Copla-Refrain Song × Sesquialtera (6/8–3/4) Armonía × Parallel-Third Violin & Trumpet Obligado Craft | Mexican mariachi — son jalisciense (Jalisco/Nayarit, 19th c.; old ensemble = vihuela + 2 violins + guitarrón, which replaced the harp; trumpets added 1910s–20s, fixture by 1930s; charro-cinema golden age 1930s–50s; UNESCO ICH Representative List 2011) | RHYTHM, STRUCTURE, PITCH, TEXTURE, HARMONY | Learn the son by ear (oral tradition; collective authorship — Jáuregui on El Son de la Negra: no single author, living variants) → pick a major key + tonic–dominant cell (I–V alternation, occasional IV, no chromaticism) → guitarrón lays bordones (root–fifth open-string bass, octave doublings, walking pickups into downbeats) → lock the sesquialtera: armonía (vihuela + guitar) & guitarrón alternate one 6/8 bar (3+3) with one 3/4 bar (2+2+2) — same six eighths, pure hemiola → vihuela strums high rasgueados marking the hemiola offbeats → write the estribillo (fixed 1–2 line refrain, the song's identity) → compose coplas (4-line cuartetas / 6-line sextillas abcbdb, syllabic 6/8 declamation, line ends on downbeats, often improvised in performance) → violins double the vocal melody in parallel thirds (tercias) with ornaments → trumpet (Miguel Martínez style) rests during coplas, plays obligado answers between phrases, octave-doubles melody in the monte → chain the form: instrumental intro (armonía alone) → estribillo → copla → monte (violin↔trumpet antiphony, register rises) → estribillo → copla → faster/higher monte → remate (V–I rasgueo flourish + grito ¡arriba! + zapateado stamp) → fix the arrangement by ensemble tradition (each mariachi keeps a house version; Galindo's 1940 Sones de Mariachi suite is one concert adaptation) | Voice 0 = vocal lead (estribillo + coplas, syllabic 6/8 declamation, high register, grito at remate). Voice 1 = violin duet (vocal melody in parallel thirds, ornaments, monte lead). Voice 2 = trumpet (obligado answers between vocal phrases, rest during coplas, octave doubling in monte). Voice 3 = vihuela (rasgueado strum dictionary, hemiola offbeat accents). Voice 4 = guitar/armonía (I–V chord-strum rhythm, 6/8↔3/4 bar-pattern lock). Voice 5 = guitarrón (bordones root–fifth, octave doublings, walking pickups). Voice 6 = zapateado (optional stomp accents, stamps at remate). Sections = son form chain (Intro armonía → Estribillo → Copla → Monte I → Estribillo → Copla → Monte II → Remate; every bar = 6 eighths whether 6/8 or 3/4 → equal tick length, zero drift natural). Rules: sesquialtera grouping lock (3+3 vs 2+2+2 accent maps), I–V harmony cell (no chromaticism, major keys), parallel-thirds derivation with chord-tone adjustment, trumpet-rest-during-copla separation, copla prosody (cuarteta/sextilla, downbeat line ends, verbatim estribillo anchor), monte antiphony + register ascent, remate cadence (V–I + grito + stomp), vihuela per-bar attack maps, fast allegro tempo, zero-drift gate, humanize (rhythm section strict, vocals rubato + portamento) | Mariachi Vargas de Tecalitlán (Gaspar Vargas, Silvestre Vargas 1928–, Rubén Fuentes arranger 1950–, Miguel Martínez trumpet), Blas Galindo (Sones de Mariachi suite 1940, El Son de la Negra adaptation), José Alfredo Jiménez (El Rey, Si Nos Dejan), Tomás Méndez (Cucurrucucú Paloma), Jorge Negrete, Pedro Infante, Lucha Reyes (La Tequilera), Vicente Fernández (Volver Volver); scholars Jesús Jáuregui (attribution studies), Jonathan Clark | ✅ Documented |
```
(full row appended to `human_methods_db.md` line 89; verified via grep `HC-083` → 1 row in db + detail + this report.)

## 7. Quirks & pitfalls

- **Collective authorship:** sones are folk items — *El Son de la Negra* has no single composer; model the *process* (estribillo/copla/sesquialtera/remate), not a fixed score. Do not credit Blas Galindo as composer — he *adapted* it in 1940.
- **Sesquialtera ≠ meter change:** 6/8 then 3/4 is a regrouping of the same six eighth notes — keep both bars the same tick length or zero-drift breaks.
- **Parallel thirds must fit the I–V cell:** a naive 3rd above the melody can land outside the chord — adjust to nearest chord tone (what the human violinist does by ear).
- **Trumpet etiquette:** no trumpet doubling over the singer during coplas; doubling only in instrumental blocks — encode the separation or the texture muddies.
- **Ranchera vs son:** the ranchera (3/4, 2/4) is a sibling genre with the same ensemble — don't force it into the sesquialtera rule; scope the method to the son.
- **Fast + high is the idiom:** allegro sones in a bright tessitura; slowing or dropping register reads as a different genre.
- Do NOT touch `methods_db.md` (algorithmic DB, owned by another job) — only `human_methods_db.md` modified.

## 8. Verification

- `grep HC-083 human_methods_db.md` → 1 row (appended, ✅ Documented).
- `grep HC-083 human_method_HC-083_mariachi-son-jalisciense-craft.md` → header + body references.
- `grep HC-083 report_HC-083.md` → this record.
- **Next free ID: HC-084** (max existing = HC-083).
