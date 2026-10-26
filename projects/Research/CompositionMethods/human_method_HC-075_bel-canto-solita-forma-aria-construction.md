# HC-075 — Bel Canto Aria Construction: *La Solita Forma* (Tempo d'Attacco → Cantabile → Tempo di Mezzo → Cabaletta)

**Method ID:** HC-075
**Layer:** `concrete (target when implemented)` — every movement is realized as concrete note events: the voice row carries actual pitches with a syllable grid, the orchestra rows carry real parts, and each section is a self-contained "movement" with its own key, tempo and meter. Key plan, tempo plan and text-function tags are cell-level constraints; nothing is generated at an abstract harmonic layer.
**Tradition:** Italian *bel canto* and Romantic opera — Rossini (1792–1868), Bellini (1801–1835), Donizetti (1797–1848) through the middle-period Verdi (1813–1901); the convention persists as a residue into *Otello* (1887) and *Falstaff* (1893). Milan/Naples/Paris opera industry, c. 1810–1870. Term coined by the Florentine critic **Abramo Basevi** (1859); reframed as "multipartite form" by **Philip Gossett** (1974).
**Primary elements:** STRUCTURE (movement chain), MELODY/PITCH (cantabile arch + cabaletta periodic tune), RHYTHM (tempo plan, galloping cabaletta pulse), TEXTURE (voice vs. orchestra frame, obbligato, chorus), TEXT (prosody, dramatic function per movement).
**Related but distinct methods:** HC-038 (sonata form — *instrumental*, tonal-architectural logic: exposition/development/recapitulation; solita forma's logic is *dramatic*, a character's emotional state changing, and its movements are set pieces, not a tonal process), HC-007 (songwriting lyric–melody prosody — popular-song hook craft, no four-movement dramaturgy, no cabaletta repeat-with-ornament protocol), HC-011 (orchestration — timbral craft as an independent discipline; here orchestration is subordinate to audibility of the text), HC-063 (improvisation-to-notation workflow — captures a performer's extempore take; here the *slots* for the performer's act are pre-planned by the composer), HC-006 (jazz big-band shout chorus — a fast climactic tutti after a lyrical opening; different genre, different harmonic language, no operatic scena), HC-046/HC-041 (stratified court/ritual forms — fixed ceremonial architecture, not character-driven dramaturgy).

---

## 1. What the method is

In the Italian opera industry of the 1810s–1860s a composer had weeks, not months, to produce a full score for a specific cast. The solution was a **standardized multi-movement scene** that both composer and audience knew intimately: *la solita forma* ("the usual form"), which Basevi named in 1859 and which Gossett later called the **multipartite form**. Within it, a character's scene advances from a **static lyrical moment to a decisive finale** through four functional movements:

1. **Scena / Tempo d'attacco** — accompanied recitative: the character states the situation. Free, speech-like, harmonically restless; it exists to *arrive* at the lyric moment.
2. **Cantabile (adagio / cavatina / pezzo concertato)** — the lyric core: a long-breathed, tonally closed slow movement where the character reflects. This is the "aria" the audience came for.
3. **Tempo di mezzo** — the interruption: a messenger arrives, a chorus comments, a rival enters, or an offstage voice is heard. Short, in a new tempo/key; it *changes the emotional state* so that…
4. **Cabaletta (stretta)** — the fast decision: a periodic, rhythmic, often "galloping" tune in two strophes plus a virtuosic coda, on whose repeat the singer adds ornament. In act finales this expands to a **finale stretta** with chorus and a *parlante* passage.

Four facts make this a genuine **human composition method** rather than a template:

1. **The form is a *situation grammar*, not a mold.** Composers chose which movements a given scene needed. A *romanza* (e.g. "Una furtiva lagrima") is two strophes and no cabaletta; a *ballata* ("La donna è mobile") is a strophic song; a full *aria di sortita* may use all four. The craft is *selecting* the right scene type for the dramatic moment, then making the chosen chain feel inevitable.
2. **Every movement has a different job, and a different musical technique.** Recitative = syllabic declamation over unstable harmony. Cantabile = long arc, slow harmonic rhythm, delayed resolution, an obbligato instrument as interlocutor. Tempo di mezzo = modulation and rhythmic disruption. Cabaletta = periodic phrase structure, harmonic simplicity, a pulse you can march to. One composer, four techniques, in twenty minutes of music.
3. **The singer is a co-author of specific slots.** The cantabile's final cadenza, the cabaletta's repeat ornaments ("ossia" variants), and the final high note are *left open* on purpose. This is composed-in freedom — the opposite of a closed text.
4. **The score is a working document.** Arias were transposed for the available voice, substituted ("arie di sostituzione"), re-versified, and re-orchestrated per production. Composition here includes *negotiation*: the librettist, the impresario, the prima donna and the censors all edit the piece.

The sound of the method: an unaccompanied or lightly accompanied recitative, then a melody that seems to float over a murmuring string accompaniment, a sudden modulation and bustle, then a tune that repeats louder with the singer climbing to a high note as the chorus and brass pile in — and the act is over.

---

## 2. Why this is not an algorithm

- **The situation chooses the form.** Whether this scene is a cantabile-cabaletta pair or a single romanza depends on what the character needs to *do* — decide, mourn, boast, pray. No rule set produces that judgement; a composer reads the libretto and the cast.
- **The term is a critic's, not a composer's.** Basevi described the practice after the fact; composers spoke of *situazioni*, *pezzi*, *cavatine*. Treating "solita forma" as a checklist misreads how they worked (Gossett's point).
- **Tessitura is a human constraint.** The key is chosen for a named singer's passaggio and range; the same aria exists in several transpositions. The "right key" is a person, not a pitch-class decision.
- **The dynamic is theatrical, not architectural.** Sonata form resolves tonal tension; solita forma resolves *emotional* tension. Its modulations serve the entrance of a third party, not a recapitulation.
- **Late Verdi breaks it deliberately.** In *Otello* and *Falstaff* the movements dissolve into continuous *azione* — the convention survives only as a shadow. A generative "form filler" cannot know when to dissolve a form.

---

## 3. The craft procedure, step by step

### Step 0 — Read the libretto and the cast list
Establish the *situazione*: who is on stage, what they want, what stops them, what they decide. Know the voices you are writing for (tenore di grazia vs. di forza, soprano leggero/drammatico, baritono) — range, tessitura, agility, stamina. This determines key, melodic ambitus, and how much ornament the cabaletta can carry.

### Step 1 — Choose the scene type (the movement subset)
- **Aria di sortita / cavatina** (entrance): scena + cantabile (+ cabaletta in the 1830s–40s).
- **Aria di mezzo carattere**: mixed affect, often cantabile + cabaletta with a lighter scena.
- **Aria patetica / romanza**: slow, strophic, *no* cabaletta ("Una furtiva lagrima"; "La donna è mobile" is a ballata).
- **Aria di bravura**: brilliance-forward; the cabaletta dominates.
- **Preghiera**: prayer, often with chorus.
- **Duet / pezzo concertato**: the same chain with two or more voices; the cantabile becomes a *concertato* in which characters sing different texts simultaneously.
- **Act finale**: adds a *finale stretta* — ensemble + chorus, often over a *parlante* (declamatory voices over a repeating orchestral figure), accelerating to the curtain.

### Step 2 — Write the scena / tempo d'attacco
Accompanied recitative ("recitativo accompagnato"): syllabic, near-speech declamation, sparse orchestral punctuation (a chord on the rhetorical accents), free rhythm, restless harmony that keeps modulating. End on a text line that *pivots* to lyric reflection — the classic cue is a generalizing statement ("Oh, how the memory..."). Prepare the cantabile's key with a dominant pedal and a held chord so the adagio can begin *attacca*.

### Step 3 — Compose the cantabile (the lyric core)
- **Form:** a two-strophe lyric, usually A–A′ (or A–B–A), each strophe 8–16 bars; the second strophe may be varied. Tonally closed (or half-closed with a fermata).
- **Melody:** long-breathed, mostly stepwise, with one clear *arch* high note per strophe; appoggiaturas and delayed resolutions carry the pathos; cadences are approached by a decorated descent. Bellini's style is the extreme case: a single unbroken arc with almost no internal cadence.
- **Harmonic rhythm:** slow — one chord per bar or half-bar; simple I–IV–V with modal mixture and a chromatic bass step for color. Complexity lives in the melody and the accompaniment's inner motion, not in chord rate.
- **Accompaniment:** a *frame*, not a competitor — arpeggiated or pulsing strings, often with a **named obbligato** (horn, clarinet, flute, cello) that answers the voice in its rests. Verdi's ideal of the *parola scenica*: the orchestration exists so the words are audible.
- **Cadenza slot:** end with a fermata, harmony on the dominant, so the singer inserts a cadenza. Write it out (later Verdi) or leave it (earlier practice) — but leave the *slot*.

### Step 4 — Compose the tempo di mezzo (the hinge)
Short (≈20–40 bars), in a new tempo and usually a new key; a chorus comment, a messenger, an entrance, an offstage voice. Its job is to *change the character's emotional state* so the cabaletta's energy is motivated. Technique: modulation by chromatic third or to the dominant, declamatory choral interjections, a rhythmic figure that "interrupts" the adagio's flow. End on a dominant pedal, then *attacca* into the cabaletta — never a full stop.

### Step 5 — Compose the cabaletta (the decision)
- **Form:** two strophes (A–A′), each a periodic 8–16-bar tune, then a **coda**; the repeat is where the singer adds ornaments.
- **Texture/pulse:** the "galloping" accompaniment (repeated chords or pulsing eighths), brass accents, often chorus joining; duple, march-like.
- **Melody:** deliberately simple, syllabic, memorable — the opposite of the cantabile's arc; one or two high notes saved for the repeat and coda.
- **Harmony:** tonic–dominant frames, a pivot for the second strophe (subdominant or relative), then a tonic coda with a *stretto* feeling.
- **Ornament protocol:** strophe 1 plain, strophe 2 embellished (scale runs, interpolated high notes, cadenzas), coda = virtuosic climax. This is composed-in performer freedom again.

### Step 6 — Plan the orchestral frame per movement
Recitative: thin, punctuating. Cantabile: strings as body plus one woodwind/horn obbligato; keep the inner voices transparent in the voice's tessitura. Tempo di mezzo: choral and brass interjections, sharper articulation. Cabaletta: full band, brass fanfares, percussion, chorus. Never double the voice at pitch with a loud instrument during sustained singing.

### Step 7 — Set the text (prosody gate)
One syllable per note in declamatory and syllabic passages; melisma only at cadences or on emotionally weighted vowels. Italian prosody governs placement: open vowels sustain, double consonants force a rhythmic break, and the final accent of a line must fall on a strong beat. Stress pattern of the verse (settenario, ottonario, endecasillabo) *is* the rhythmic template of the tune.

### Step 8 — Rehearse, transpose, substitute (the negotiation loop)
Fit the piece to the actual singer: transpose, rewrite the cabaletta's second strophe, replace the aria with an "aria di sostituzione" from your portfolio, adjust cadenzas. Revise after orchestral rehearsal (the *prova*). The printed score is one state of a mutable object.

### Step 9 — Know the stylistic dialects
Rossini: rhythmic incisiveness, crescendo architecture, comic patter, cabalettas of pure élan. Bellini: long-spun melody, minimal harmonic motion, ornament as line. Donizetti: dramatic rhythm, mad-scene extremes, obbligato color. Verdi: fuse the movements with one continuing dramatic impulse ("Ah sì, ben mio" → "Di quella pira"), then progressively dissolve the set pieces. Late Verdi: the form as remembered ghost.

---

## 4. Practitioner examples

| Practitioner / work | Role in the craft |
|---|---|
| **Gioachino Rossini** — *Il barbiere di Siviglia* (1816), "Una voce poco fa" | Textbook cavatina chain: recitative → cantabile ("Una voce poco fa") → tempo di mezzo ("Io sono docile… ma se mi toccano") → fast stretta. Shows the middle movement as a *character reveal*, not filler. |
| **Rossini** — *La Cenerentola* (1817), "Non più mesta" | Canonical **cabaletta** (cited as a classic example): two strophes + embellished variation, galloping accompaniment, virtuosic coda, rondo-like return of the tune. |
| **Vincenzo Bellini** — *Norma* (1831), "Casta diva" | The purest cantabile: a single long arc over a slow harmonic frame with chorus and flute obbligato, then the **cabaletta "Ah! bello a me ritorna"** after a recitative tempo di mezzo — the model of "static lyric → decisive fast close". |
| **Bellini** — *I puritani* (1835), "Vien diletto, è in ciel la luna" | Cited classic cabaletta: ornament protocol at its most elaborate (the bel canto singer's added variations *are* the composition's last movement). |
| **Gaetano Donizetti** — *Lucia di Lammermoor* (1835) | "Regnava nel silenzio… Quando rapito in estasi": cantabile + tempo di mezzo + cabaletta in one scene. The Mad Scene's "Spargi d'amaro pianto" is a cabaletta of grief (with glass harmonica in the early version) — proving the fast movement can carry tragedy, not just triumph. |
| **Donizetti** — *Linda di Chamounix* (1842), "O luce di quest'anima" | Cabaletta as overwhelming joy — the emotional pole opposite Lucia's. |
| **Giuseppe Verdi** — *Il trovatore* (1853), "Ah sì, ben mio… Di quella pira" | Cantabile flows into the cabaletta over one dramatic impulse (Manrico rushes to save his mother) — the movements fused; "Di quella pira" is cited as a classic cabaletta. |
| **Verdi** — *La traviata* (1853), "Ah fors'è lui… Sempre libera" | Violetta's scene: cantabile ("Ah fors'è lui") → tempo di mezzo ("Follie! follie!") → cabaletta ("Sempre libera"), with **Alfredo's offstage voice** interrupting the cabaletta — the "third party" convention used as psychology. |
| **Verdi** — *Rigoletto* (1851), "La donna è mobile" | A *ballata*, not a four-movement aria: proof that the convention is a menu, not a mold. The Duke's tune returns as a dramaturgical knife in the last act. |
| **Verdi** — *Otello* (1887), *Falstaff* (1893) | The dissolution: continuous *azione*, set pieces dissolved; the solita forma survives as an implied skeleton (Otello's "Dio! mi potevi scagliar" gestures at a cantabile without ever settling into one). |
| **Abramo Basevi** (1859), **Philip Gossett** (1974–) | Basevi coined *la solita forma* in his Verdi study; Gossett renamed and re-analyzed it as the "multipartite form" and edited the critical Verdi edition documenting transpositions, substitutions and *ossia* variants. |
| **The prima donna / primo uomo** | Co-authors of the open slots: cadenzas, cabaletta ornaments, interpolated high notes, and the choice of which aria to sing at all. |

**Canonical listening:** "Casta diva" + "Ah! bello a me ritorna" (Norma); "Una voce poco fa" (Barbiere); "Regnava nel silenzio… Quando rapito in estasi" and "Spargi d'amaro pianto" (Lucia); "Ah sì, ben mio… Di quella pira" (Trovatore); "Ah fors'è lui… Sempre libera" (Traviata). Listen for the *seams*: they are the form.

---

## 5. UnitMatrix integration (Musicom engine)

**Layer:** concrete. Each movement is a column of real note events; the "key plan" and "tempo plan" are section attributes, not generated harmony.

**Voices (rows):**
- **V0 — Voice (solo).** Monophonic melody + syllable grid. Attributes: voice type, tessitura band, ornament-slot markers (cadenza, cabaletta repeat, final high note).
- **V1 — Violins I / V2 — Violins II+Viola / V3 — Cello+Bass.** The string body; the frame for the cantabile and the motor for the cabaletta.
- **V4 — Obbligato (flute/clarinet/horn/cello solo).** A *named* interlocutor: doubles at unison/octave, or answers strictly in the voice's rests. Never competes in the tessitura.
- **V5 — Brass + timpani.** Cabaletta/finale energy, fanfare figures, accents at phrase joints.
- **V6 — Chorus (SATB).** Comments in the tempo di mezzo, joins the cabaletta, carries the *parlante* in act finales.
- **V7 — Text/prosody track (metadata, not sounding).** Syllable grid, verse meter, stress marks, dramatic-function tag per section. This is the row that makes the form legible to the engine and auditable by a human.

**Sections (columns)** — one per movement, each with `key`, `tempo`, `meter`, `text_function`:

| Cell | Movement | Key / Tempo | Content |
|---|---|---|---|
| S0 | Scena / tempo d'attacco | free, modulating; recit | syllabic declamation, orchestral punctuation, ends on dominant pedal → attacca |
| S1 | Cantabile | local tonic; adagio | 2-strophe lyric arc, slow harmonic rhythm, obbligato, fermata cadenza slot |
| S2 | Tempo di mezzo | new key (chromatic third / dominant); moderato–allegro | interruption: chorus/messenger/offstage voice; ends on dominant pedal → attacca |
| S3 | Cabaletta (stretta) | **S1's tonic**; allegro vivace | A–A′ + coda, galloping pulse, ornament layer on A′, high-note slot in coda |
| (S3′) | Finale stretta variant | tonic; presto | ensemble + chorus, *parlante* over repeating orchestral figure, accelerando to curtain |

**Rules to encode:**
1. **Movement gate:** an aria tagged `solita_forma` must contain S0→S1→S2→S3 in order; a `romanza`/`ballata` must contain *no* cabaletta. The tag is chosen from the dramatic function, never defaulted.
2. **Key plan:** `S3.key == S1.key` (tonal return); S2 modulates away (chromatic third or dominant); S0 may start anywhere and must prepare S1's key by a dominant pedal in its last bars.
3. **Tempo plan:** S1 is the slowest sounding movement; S2 faster than S1; S3 faster than S2; S0 is *senza misura* (free, tick-proportional to syllables). Strictly stepped, no continuous ramp.
4. **Attacca seams:** S0→S1 and S2→S3 have no silence gap; S2's last tick = S3's first tick, with the dominant pedal spanning the seam. Zero-drift is structural.
5. **Text-function gate:** S2's text tag must be `interruption` (new agent/fact) or `changed_state`; if absent, the cabaletta is unmotivated and the form invalid. S3's tag must be `decision`.
6. **Cantabile arch rule:** exactly one melodic climax per strophe, approached from below, resolved by step; harmonic rhythm ≤ 1 chord/bar during singing.
7. **Obbligato rule:** V4 sounds only in V0's rests or doubled at unison/octave; its dynamic is capped below V0 in V0's tessitura band.
8. **Ornament slots (composed-in freedom):** S1 cadenza, S3 A′ ornament layer, S3 coda high note are declared *open cells* — an optional overlay row filled at performance (or by a seeded performer model). Do not pre-fill them in the "composer" pass; keep the two passes separate and both provenance-recorded.
9. **Cabaletta periodicity:** S3 phrases must be 4/8-bar periodic and syllabic (≤ 1 note per syllable except cadence melisma); no phrase may exceed 2 bars without a resting point.
10. **Prosody gate:** verse meter (settenario/ottonario/endecasillabo) sets the rhythmic template; final line stress on a strong beat; double consonants force a rhythmic break (a rest or rearticulation).
11. **Zero-drift:** every voice's cell ends at the section terminal landmark; the voice's last event of the piece lands on the tonic at the final section boundary; `validate()` must pass.

**Distinct from adjacent HC methods in engine terms:** HC-038 (sonata form) is a *tonal process* realized by one continuous movement with an exposition/development/recapitulation function map; HC-075 is a *chain of four separate set pieces* whose logic is dramatic and whose keys are local. HC-007 (songwriting prosody) models one hook over one loop; HC-075 models four contrasting movements plus an ornament-overlay pass. HC-063 (improvisation-to-notation) captures a performance after the fact; HC-075 *plans* the performance's freedom as declared open cells.

---

## 6. Quirks & pitfalls

- **"La solita forma" is an analyst's phrase** (Basevi 1859), not a composer's brief, and Gossett's "multipartite form" is a modern reframing. Present it as a flexible convention, not a fill-in-the-blank template — composers thought in *situazioni*.
- **Not every aria has four movements.** *Romanza* ("Una furtiva lagrima"), *ballata* ("La donna è mobile"), *preghiera*, and many early cavatinas skip the cabaletta. Forcing four movements misrepresents the repertoire.
- **The cantabile's partner can be an ensemble.** In duets and finales the "slow movement" is a *pezzo concertato* where several characters sing different texts at once — not a solo aria with accompaniment.
- **The tempo di mezzo is the movement amateurs drop.** Without it the cabaletta is unmotivated bombast. It is also the movement that carries the plot — skipping it breaks the dramaturgy, not just the form.
- **The score is unstable.** Transpositions for specific singers, *arie di sostituzione*, *ossia* variants, changed cabaletta verses and singer-supplied cadenzas are normal. Cite a critical edition (Gossett/Ricordi–Chicago) and name which version you mean.
- **Ornaments on the repeat are a performer's act, sanctioned by the style** — an engine must leave the slot open, not pre-fill it as "the tune".
- **Prosody is Italian-specific.** Open vowels sustain, double consonants break, verse meter drives the rhythm. Do not reuse English-language pop prosody rules (HC-007) unmodified.
- **Voice type sets the key.** Tessitura and passaggio, not pitch-class convenience, decide transposition; the same aria exists in several keys.
- **Don't confuse keys with sonata logic.** Solita forma's modulations serve an entrance or a change of mind; there is no recapitulation to resolve. HC-038's rules will produce the wrong shapes here.
- **Late Verdi dissolves the form on purpose.** A "solita forma detector" that only knows the 1830s template will misread *Otello* and *Falstaff* as broken rather than evolved.
- **The cabaletta is not always joyful.** "Spargi d'amaro pianto" is a cabaletta of grief; the fast movement carries whatever decision the character makes, including despair.
