# report_HC-075 — Bel Canto Aria Construction: *La Solita Forma* (Tempo d'Attacco → Cantabile → Tempo di Mezzo → Cabaletta)

**Job:** `daily-human-composition-research` · **Date:** 2026-10-25 · **Method ID:** HC-075
**Detail file:** `human_method_HC-075_bel-canto-solita-forma-aria-construction.md`

---

## 1. Header

| Field | Value |
|---|---|
| **Method name** | Bel Canto Aria Construction — *La Solita Forma*: Tempo d'Attacco → Cantabile → Tempo di Mezzo → Cabaletta (four-movement dramatic scene architecture with composed-in ornament slots) |
| **Tradition** | Italian Romantic opera / bel canto — Rossini (1792–1868), Bellini (1801–1835), Donizetti (1797–1848) through middle Verdi (1813–1901); Milan/Naples/Paris opera industry c. 1810–1870; the convention dissolves into continuous *azione* in *Otello* (1887) and *Falstaff* (1893). Term coined by the critic **Abramo Basevi** (1859); reframed as "multipartite form" by **Philip Gossett** (1974). |
| **Layer** | `concrete (target when implemented)` — each movement is real note events: voice row with pitches + syllable grid, orchestra rows with real parts, sections with their own key/tempo/meter. Key plan, tempo plan and text-function tags are cell attributes; no abstract harmonic layer is generated. |
| **Primary elements** | STRUCTURE (movement chain), MELODY/PITCH (cantabile arc, cabaletta periodic tune), RHYTHM (tempo plan, galloping pulse), TEXTURE (voice frame vs. orchestra, obbligato, chorus), TEXT (prosody, dramatic function per movement) |
| **Why human craft, not algorithm** | The *situazione* chooses the movement subset (romanza has no cabaletta; ballata is strophic). The term is a critic's post-hoc label, not a composer's brief. Key choice is a *person* (tessitura/passaggio of a named singer). The logic is theatrical, not tonal-architectural. Late Verdi dissolves the form on purpose — no rule set knows when. |
| **Research sources (fetched 2026-10-25)** | Wikipedia: *Solita forma* (Basevi origin, Gossett's "multipartite form", five-stage pattern incl. tempo di mezzo and finale stretta); *Cabaletta* (two stanzas + embellished variations + coda; term first defined 1826 in Lichtenthal's *Dizionario*; classic examples "Non più mesta" 1817, "Vien diletto" 1835, "Di quella pira" 1853; cabaletta as joy or grief — "Spargi d'amaro pianto"). Repertoire knowledge for the remaining examples. |

**Distinct from existing HC methods:**
- **HC-038 (sonata form)** — instrumental, one continuous tonal process (exposition/development/recapitulation); HC-075 is a *chain of four separate set pieces* whose keys are local and whose logic is a character's changing emotional state.
- **HC-007 (lyric–melody prosody)** — one hook over one loop; HC-075 needs four contrasting movements plus a separate ornament-overlay pass.
- **HC-011 (orchestration)** — timbral craft as its own discipline; here orchestration is subordinated to audibility of the text (*parola scenica*).
- **HC-063 (improvisation-to-notation)** — captures a performance after the fact; HC-075 *plans* performer freedom as declared open cells (cadenza, cabaletta repeat, final high note).
- **HC-006 (jazz shout chorus)** — fast climactic tutti after a lyrical opening, but no operatic scena, no libretto, different harmonic language.
- **HC-041 / HC-046 (court/ritual stratification)** — fixed ceremonial architecture, not character-driven dramaturgy.

**Deduplication note:** the first candidate for this slot was Korean *sanjo* jangdan-cycle composition, but **HC-017 (`sanjo-jangdan-improvisation`)** already documents the Korean sanjo method (jangdan ladder, jo modes, chuimsae). That draft was discarded before publication and replaced with this method — no duplicate topic entered the DB.

---

## 2. What the method is

Italian opera houses of the 1810s–1860s commissioned full scores in weeks for a specific cast. The industry's answer was a **standardized multi-movement scene** that composer and audience both knew cold — *la solita forma* ("the usual form"), named by Basevi in 1859, later called the **multipartite form** by Gossett. A character's scene advances from a **static lyrical moment to a decisive finale** through four functional movements:

1. **Scena / tempo d'attacco** — accompanied recitative; states the situation, free and modulating, exists to *arrive* at the lyric moment.
2. **Cantabile (adagio / cavatina / pezzo concertato)** — the lyric core; long-breathed, tonally closed, one arch climax, slow harmonic rhythm, named obbligato.
3. **Tempo di mezzo** — the interruption; a messenger, a chorus, an entrance, an offstage voice; new key and tempo; *changes the emotional state*.
4. **Cabaletta (stretta)** — the decision; two strophes + coda, periodic syllabic tune over a "galloping" pulse, ornament added on the repeat; in act finales expands to a **finale stretta** with chorus and *parlante*.

It is a **situation grammar, not a mold**: composers selected which movements a scene needed. "Una furtiva lagrima" is a two-strophe romanza; "La donna è mobile" is a ballata; a full sortita uses all four. The craft is choosing the right chain, then making each movement do its own job with its own technique — declamation, lyric arc, modulation-as-interruption, periodic tune — and leaving the singer's slots open.

---

## 3. Craft procedure in detail

### Step 0 — Read the libretto and the cast list
Establish the *situazione* (who is on stage, what they want, what blocks them, what they decide) and the voices available (tenore di grazia vs. di forza, soprano leggero/drammatico, baritono). Range, tessitura, agility and stamina decide key, ambitus, and how much ornament the cabaletta can carry.

### Step 1 — Choose the scene type (movement subset)
- **Aria di sortita / cavatina** (entrance): scena + cantabile (+ cabaletta in the 1830s–40s).
- **Aria di mezzo carattere**: mixed affect, lighter scena.
- **Aria patetica / romanza**: slow, strophic, **no cabaletta**.
- **Aria di bravura**: brilliance-forward, cabaletta dominates.
- **Preghiera**: prayer, usually with chorus.
- **Duet / pezzo concertato**: same chain with 2+ voices; the slow movement becomes a *concertato* (different texts simultaneously).
- **Act finale**: adds **finale stretta** — ensemble + chorus, often over a *parlante* (declamatory voices above a repeating orchestral figure), accelerating to the curtain.

### Step 2 — Write the scena / tempo d'attacco
Accompanied recitative: syllabic near-speech declamation, sparse orchestral punctuation on rhetorical accents, free rhythm, restless modulation. End on a text line that pivots to reflection; prepare the adagio's key with a dominant pedal and a held chord, then *attacca*.

### Step 3 — Compose the cantabile
- **Form:** two-strophe lyric, A–A′ (or A–B–A), 8–16 bars per strophe; tonally closed or half-closed with fermata.
- **Melody:** long-breathed, mostly stepwise, exactly one arch high note per strophe; appoggiaturas and delayed resolutions; decorated descent to the cadence. Bellini is the extreme (one unbroken arc, almost no internal cadence).
- **Harmonic rhythm:** slow — one chord per bar or half-bar; I–IV–V with modal mixture and a chromatic bass step for color. Complexity lives in melody and inner motion, not chord rate.
- **Accompaniment:** a frame — pulsing/arpeggiated strings plus a **named obbligato** (horn, clarinet, flute, cello) answering in the voice's rests. Verdi's *parola scenica*: orchestration must keep the words audible.
- **Cadenza slot:** end on a dominant fermata, cadenza written out (later Verdi) or left to the singer (earlier practice) — but always leave the slot.

### Step 4 — Compose the tempo di mezzo (the hinge)
20–40 bars in a new tempo and usually a new key: chorus comment, messenger, entrance, offstage voice. Modulate by chromatic third or to the dominant; use declamatory choral interjections and a rhythmic figure that "interrupts" the adagio. End on a dominant pedal and *attacca* into the cabaletta — never a full stop. Its job is to change the character's emotional state so the cabaletta's energy is motivated. This is the movement amateurs omit; without it the cabaletta is unmotivated bombast.

### Step 5 — Compose the cabaletta
- **Form:** A–A′ (periodic 8–16-bar strophes) + coda; the repeat carries the singer's ornaments.
- **Pulse/texture:** "galloping" repeated chords or pulsing eighths, brass accents, chorus joining; duple, march-like.
- **Melody:** deliberately simple and syllabic — the opposite of the cantabile's arc; one or two high notes saved for repeat and coda.
- **Harmony:** tonic–dominant frames, a pivot for strophe 2 (subdominant or relative), tonic coda with stretto feeling.
- **Ornament protocol:** strophe 1 plain, strophe 2 embellished, coda virtuosic climax.

### Step 6 — Plan the orchestral frame per movement
Recit: thin and punctuating. Cantabile: strings as body + one woodwind/horn obbligato; transparent inner voices in the voice's tessitura. Tempo di mezzo: choral/brass interjections, sharp articulation. Cabaletta: full band, brass fanfares, percussion, chorus. Never double the voice loudly at pitch during sustained singing.

### Step 7 — Set the text (prosody gate)
One syllable per note in declamatory/syllabic passages; melisma only at cadences or on weighted vowels. Italian prosody governs placement: open vowels sustain, double consonants force a rhythmic break, the line's final accent falls on a strong beat. Verse meter (settenario, ottonario, endecasillabo) **is** the rhythmic template of the tune.

### Step 8 — Rehearse, transpose, substitute (negotiation loop)
Fit the piece to the actual singer: transpose, rewrite the second strophe, swap in an *aria di sostituzione*, adjust cadenzas, revise after the orchestral *prova*. The printed score is one state of a mutable object; critical editions (Gossett / Ricordi–Chicago) document the variants.

### Step 9 — Know the dialects
Rossini: rhythmic incisiveness, crescendo architecture, patter, pure-élan cabalettas. Bellini: long-spun melody, minimal harmonic motion, ornament as line. Donizetti: dramatic rhythm, mad-scene extremes, obbligato color. Verdi: fuse the movements on one dramatic impulse, then progressively dissolve the set pieces; late Verdi uses the form as a ghost.

---

## 4. Practitioner examples

| Practitioner / work | Role in the craft |
|---|---|
| **Rossini** — *Il barbiere di Siviglia* (1816), "Una voce poco fa" | Textbook chain: recitative → cantabile → tempo di mezzo ("Io sono docile… ma se mi toccano") → fast stretta; the middle movement is a *character reveal*, not filler. |
| **Rossini** — *La Cenerentola* (1817), "Non più mesta" | Canonical **cabaletta**: two stanzas + embellished variation, galloping accompaniment, virtuosic coda. |
| **Bellini** — *Norma* (1831), "Casta diva" | Purest cantabile: single long arc over slow harmony with chorus and flute obbligato, then the cabaletta "Ah! bello a me ritorna" after a recitative hinge — the model "static lyric → decisive fast close". |
| **Bellini** — *I puritani* (1835), "Vien diletto, è in ciel la luna" | Cited classic cabaletta; ornament protocol at its most elaborate — the singer's added variations *are* the final movement. |
| **Donizetti** — *Lucia di Lammermoor* (1835) | "Regnava nel silenzio… Quando rapito in estasi": cantabile + tempo di mezzo + cabaletta in one scene. Mad Scene "Spargi d'amaro pianto" is a cabaletta of grief (glass harmonica in the early version) — the fast movement can carry tragedy. |
| **Donizetti** — *Linda di Chamounix* (1842), "O luce di quest'anima" | Cabaletta as overwhelming joy — the opposite emotional pole. |
| **Verdi** — *Il trovatore* (1853), "Ah sì, ben mio… Di quella pira" | Cantabile flows into the cabaletta on one dramatic impulse (Manrico rushes to save his mother) — movements fused; "Di quella pira" is a cited classic cabaletta. |
| **Verdi** — *La traviata* (1853), "Ah fors'è lui… Sempre libera" | Cantabile → tempo di mezzo ("Follie! follie!") → cabaletta, with **Alfredo's offstage voice** interrupting the cabaletta — the "third party" convention used as psychology. |
| **Verdi** — *Rigoletto* (1851), "La donna è mobile" | A **ballata**, not a four-movement aria: the convention is a menu, not a mold; the tune returns as a dramaturgical knife in the last act. |
| **Verdi** — *Otello* (1887), *Falstaff* (1893) | Dissolution: continuous *azione*, set pieces dissolved; solita forma survives as an implied skeleton ("Dio! mi potevi scagliar" gestures at a cantabile without settling into one). |
| **Abramo Basevi** (1859) / **Philip Gossett** (1974–) | Basevi coined *la solita forma* in his Verdi study; Gossett renamed and re-analyzed it as the "multipartite form" and edited the critical Verdi edition documenting transpositions, substitutions and *ossia* variants. |
| **The prima donna / primo uomo** | Co-authors of the open slots: cadenzas, cabaletta ornaments, interpolated high notes — and of which aria gets sung at all. |

**Listening:** "Casta diva" + "Ah! bello a me ritorna"; "Una voce poco fa"; "Regnava nel silenzio… Quando rapito in estasi" and "Spargi d'amaro pianto"; "Ah sì, ben mio… Di quella pira"; "Ah fors'è lui… Sempre libera". The seams are the form.

---

## 5. UnitMatrix integration (Musicom engine)

**Layer:** concrete. Each movement is a column of real note events; key/tempo/meter are section attributes.

**Voices (rows):**
- **V0 — Voice (solo):** monophonic melody + syllable grid; voice type, tessitura band, ornament-slot markers.
- **V1 — Violins I / V2 — Violins II + Viola / V3 — Cello + Bass:** string body; frame for cantabile, motor for cabaletta.
- **V4 — Obbligato (flute/clarinet/horn/cello):** named interlocutor — unison/octave doubling or answers strictly in V0's rests; dynamic capped below V0 in V0's tessitura.
- **V5 — Brass + timpani:** cabaletta/finale energy, fanfares, phrase-joint accents.
- **V6 — Chorus (SATB):** tempo di mezzo comments, cabaletta join, *parlante* in act finales.
- **V7 — Text/prosody metadata row (non-sounding):** syllables, verse meter, stress, dramatic-function tag per section. Makes the form legible and auditable.

**Sections (columns):**

| Cell | Movement | Key / Tempo | Content |
|---|---|---|---|
| S0 | Scena / tempo d'attacco | free, modulating; recit | syllabic declamation, orchestral punctuation, ends on dominant pedal → attacca |
| S1 | Cantabile | local tonic; adagio | 2-strophe lyric arc, slow harmonic rhythm, obbligato, fermata cadenza slot |
| S2 | Tempo di mezzo | new key (chromatic 3rd / dominant); moderato–allegro | interruption: chorus/messenger/offstage voice; ends on dominant pedal → attacca |
| S3 | Cabaletta (stretta) | **S1's tonic**; allegro vivace | A–A′ + coda, galloping pulse, ornament layer on A′, high-note slot in coda |
| S3′ | Finale stretta variant | tonic; presto | ensemble + chorus, *parlante* over repeating orchestral figure, accelerando to curtain |

**Rules to encode:**
1. **Movement gate:** `solita_forma` tag ⇒ S0→S1→S2→S3 in order; `romanza`/`ballata` tag ⇒ **no** cabaletta. Tag chosen from dramatic function, never defaulted.
2. **Key plan:** `S3.key == S1.key`; S2 modulates away (chromatic third or dominant); S0 may start anywhere but must prepare S1's key with a dominant pedal in its last bars.
3. **Tempo plan:** S1 slowest, then S2, then S3; strictly stepped, no continuous ramp; S0 *senza misura* (tick-proportional to syllables).
4. **Attacca seams:** no silence at S0→S1 and S2→S3; S2's last tick = S3's first tick, dominant pedal spanning the seam — zero-drift is structural.
5. **Text-function gate:** S2 tag must be `interruption` (new agent/fact) or `changed_state`; S3 tag must be `decision`. Otherwise the form is invalid.
6. **Cantabile arch rule:** exactly one climax per strophe, approached from below and resolved by step; harmonic rhythm ≤ 1 chord/bar while singing.
7. **Obbligato rule:** V4 sounds only in V0's rests or doubled at unison/octave; dynamic capped below V0 in the tessitura band.
8. **Ornament slots = declared open cells:** S1 cadenza, S3 A′ ornament overlay, S3 coda high note are filled in a **separate performer pass** (seeded, provenance-recorded) — never pre-filled by the composer pass.
9. **Cabaletta periodicity:** 4/8-bar phrases, syllabic (≤ 1 note per syllable except cadence melisma), no phrase > 2 bars without a resting point.
10. **Prosody gate:** verse meter sets the rhythmic template; final line stress on a strong beat; double consonants force a rhythmic break (rest or rearticulation).
11. **Zero-drift:** all voices' cells end at the section terminal landmark; the voice's final event lands on the tonic at the last boundary; `validate()` must pass.

**Distinct in engine terms:** HC-038 is one continuous movement with a tonal-function map; HC-075 is four set pieces with local keys and a dramatic gate. HC-007 models one hook; HC-075 needs four movements plus an ornament overlay. HC-063 captures a performance post-hoc; HC-075 pre-plans the freedom.

---

## 6. Table row added to `human_methods_db.md`

```markdown
| HC-075 | human (→concrete) | Bel Canto Aria Construction — *La Solita Forma*: Tempo d'Attacco → Cantabile → Tempo di Mezzo → Cabaletta (Four-Movement Dramatic Scene Architecture with Composed-in Ornament Slots) | Italian Romantic opera / bel canto — Rossini (1792–1868), Bellini (1801–1835), Donizetti (1797–1848) through middle Verdi (1813–1901); Milan/Naples/Paris opera industry c. 1810–1870; term coined by Abramo Basevi (1859), reframed as "multipartite form" by Philip Gossett (1974); dissolves into continuous *azione* in *Otello*/*Falstaff* | STRUCTURE, MELODY, RHYTHM, TEXTURE, TEXT (prosody) | Read libretto + cast list (situazione, voice types, tessitura) → choose scene type (aria di sortita / mezzo carattere / patetica-romanza / bravura / preghiera / duet-pezzo concertato / act finale = which movement subset) → write SCENA / TEMPO D'ATTACCO (accompanied recitative: syllabic declamation, orchestral punctuation, restless modulation, ends on dominant pedal *attacca*) → compose CANTABILE (adagio: 2-strophe A–A′ lyric arc, one arch climax approached by step, slow harmonic rhythm ≤1 chord/bar, strings + named obbligato answering in rests, fermata cadenza slot) → compose TEMPO DI MEZZO (the hinge, 20–40 bars: messenger/chorus/offstage voice interrupts, new key by chromatic 3rd or dominant, declamatory interjections, dominant pedal → *attacca*; must change the character's emotional state) → compose CABALETTA (two strophes + coda, "galloping" repeated-chord pulse, brass + chorus, periodic 4/8-bar syllabic tune, ornament layer on the A′ repeat, high-note slot in coda; for act finales expand to finale stretta with *parlante* over a repeating orchestral figure) → plan orchestral frame per movement (thin recit; string body + obbligato cantabile; brass/chorus cabaletta; never cover the voice in its tessitura — Verdi's *parola scenica*) → set text (one syllable per note except cadence melisma; verse meter settenario/ottonario/endecasillabo = rhythmic template; double consonants force a break) → rehearse/transpose/substitute (arie di sostituzione, ossia variants, singer cadenzas — the score is a mutable working document) → know the dialects (Rossini rhythmic élan, Bellini long-spun line, Donizetti dramatic rhythm/obbligato color, Verdi fusing movements then dissolving them) | V0 = Voice (monophonic melody + syllable grid; voice type, tessitura band, ornament-slot markers). V1–V3 = string body (Vln I / Vln II+Vla / Vc+Cb) as frame and motor. V4 = named obbligato (flute/clarinet/horn/cello) sounding only in V0's rests or doubled at unison/8ve, capped below V0 dynamic. V5 = brass + timpani (cabaletta/finale accents). V6 = chorus (tempo di mezzo comments, joins cabaletta, carries *parlante*). V7 = text/prosody metadata row (syllables, verse meter, stress, dramatic-function tag). Sections = S0 Scena/tempo d'attacco (free, modulating, ends on dom pedal) → S1 Cantabile (adagio, local tonic, fermata cadenza slot) → S2 Tempo di mezzo (new key by chromatic 3rd/dominant, moderato–allegro, interruption text tag, dom pedal into seam) → S3 Cabaletta (allegro vivace, S1's tonic, A–A′+coda, ornament overlay on A′, high-note slot); S3′ finale stretta variant. Rules: movement gate (solita_forma must have S0→S3 in order; romanza/ballata must have NO cabaletta — tag chosen from dramatic function, never defaulted), key plan (S3.key == S1.key; S2 modulates away; S0 prepares S1 by dominant pedal), tempo plan (S1 slowest, then S2, then S3, stepped not ramped; S0 senza misura), attacca seams (no silence at S0→S1, S2→S3; S2 last tick = S3 first tick — zero-drift structural), text-function gate (S2 = interruption/changed_state else cabaletta unmotivated; S3 = decision), cantabile arch rule (exactly one climax per strophe, stepwise resolution, harmonic rhythm ≤1 chord/bar while singing), obbligato rule, ornament slots = declared open cells filled in a separate performer pass (never pre-filled by the composer pass), cabaletta periodicity (4/8-bar phrases, syllabic, no phrase >2 bars without a resting point), prosody gate, zero-drift (all cells end at section terminal landmark; final voice event on tonic at last boundary; validate() must pass) | Rossini (*Il barbiere di Siviglia* 1816 "Una voce poco fa" — recit→cantabile→tempo di mezzo "Io sono docile… ma se mi toccano"→stretta; *La Cenerentola* 1817 "Non più mesta" — canonical cabaletta, 2 stanzas + embellished variation + virtuosic coda), Bellini (*Norma* 1831 "Casta diva" — purest cantabile arc w/ chorus + flute obbligato, then cabaletta "Ah! bello a me ritorna"; *I puritani* 1835 "Vien diletto, è in ciel la luna" — elaborate ornament protocol), Donizetti (*Lucia di Lammermoor* 1835 "Regnava nel silenzio… Quando rapito in estasi"; Mad Scene "Spargi d'amaro pianto" = cabaletta of grief w/ glass harmonica in early version; *Linda di Chamounix* 1842 "O luce di quest'anima" = cabaletta of joy), Verdi (*Il trovatore* 1853 "Ah sì, ben mio… Di quella pira" — movements fused on one dramatic impulse; *La traviata* 1853 "Ah fors'è lui… Sempre libera" — Alfredo's offstage voice interrupts the cabaletta; *Rigoletto* 1851 "La donna è mobile" = ballata, proving the form is a menu not a mold; *Otello* 1887 / *Falstaff* 1893 — form dissolved into continuous *azione*), theorists Abramo Basevi (1859, coined *la solita forma*) and Philip Gossett (1974, "multipartite form"; critical Verdi edition documenting transpositions, substitutions, ossia variants) | ✅ Documented |
```

---

## 7. Verification & next free ID

- Detail file: `human_method_HC-075_bel-canto-solita-forma-aria-construction.md` — contains `HC-075` ✓
- DB table: `human_methods_db.md` — row `| HC-075 |` appended as line 81 ✓ (80 → 81 lines, 9 columns matching HC-074's shape)
- Report: this file, `report_HC-075.md` ✓
- DB row count of `HC-075` = 1 (no duplicate row) ✓
- Max existing ID = **HC-075** → **Next free ID: HC-076**

```bash
grep -c "HC-075" human_method_HC-075_bel-canto-solita-forma-aria-construction.md   # ≥1 ✓
grep -c '^| HC-075 ' human_methods_db.md                                          # 1 ✓
awk 'NR==81' human_methods_db.md | tr '|' '\n' | wc -l                            # 11 (9 cells) ✓
```

---

## 8. Quirks & pitfalls

- **The term is a critic's** (Basevi 1859) and a modern reframing (Gossett's "multipartite form") — a flexible convention, not a composer's checklist. Composers thought in *situazioni*.
- **Not every aria has four movements:** romanza ("Una furtiva lagrima"), ballata ("La donna è mobile"), preghiera, many early cavatinas. Forcing four misrepresents the repertoire.
- **The slow movement can be an ensemble:** in duets/finales the cantabile becomes a *pezzo concertato* with simultaneous different texts.
- **The tempo di mezzo is the dropped movement** — and it carries the plot. Skipping it breaks dramaturgy, not just form.
- **The score is unstable:** transpositions, *arie di sostituzione*, *ossia* variants, rewritten cabaletta verses, singer-supplied cadenzas. Cite a critical edition and name the version.
- **Ornaments on the cabaletta repeat are a performer's act** sanctioned by the style — keep the slot open.
- **Prosody is Italian-specific:** open vowels sustain, double consonants break, verse meter drives the rhythm; don't reuse English pop prosody rules.
- **Voice type sets the key** (tessitura/passaggio), not pitch-class convenience.
- **Don't reuse sonata-form rules:** solita forma's modulations serve an entrance or a change of mind; there is no recapitulation to resolve.
- **Late Verdi dissolves the form deliberately** — a template-only detector misreads *Otello*/*Falstaff* as broken rather than evolved.
- **The cabaletta isn't only joyful** — "Spargi d'amaro pianto" is a cabaletta of grief.
- **Dedup lesson:** check slugs for synonyms before researching — "sanjo-jangdan-improvisation" (HC-017) already covered the Korean candidate, which was dropped pre-publication.
