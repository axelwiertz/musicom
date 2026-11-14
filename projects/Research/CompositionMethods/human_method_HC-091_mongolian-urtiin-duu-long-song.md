# HC-091 — Mongolian Urtiin Duu (Long Song) Composition

**Method:** Mongolian Urtiin Duu (Long Song) Composition — *Shilber* Skeleton × *Khooslol* Ornament Craft
**Tradition:** Mongolian pastoral vocal tradition (Khalkha central/east, Oirat west, Buryat & Inner Mongolian variants)
**Layer:** `human (→concrete)` — target layer **concrete** when realized through the UnitMatrix
**Primary elements (Musical Elements Framework):** PITCH, STRUCTURE, RHYTHM, TEXTURE — HARMONY emergent only (drone + parallel 4ths/5ths, no functional harmony)

---

## 1. What it is

The **urtiin duu** ("long song") is the central vocal genre of Mongolian pastoral music — "long" not because the songs are long but because **each syllable of text is stretched over a long melodic span**: a four-minute song may contain only ten words. It is a **melisma-and-skeleton craft**: the singer composes (or inherits) a fixed melodic **skeleton** (*shilber*) and elaborates it live with a rich ornamental surface (*khooslol*) whose vocabulary — tenuto-vibrato *shuranhai*, lower-modulated *nugalaa*, leaps (*usrelt*), pulsation (*tsokhilgo*), sprinkling (*tsatslaga*), free tones (*khayalga*), repeated vibration (*shigshree*) — is the actual compositional surface of the tradition. UNESCO proclaimed it a Masterpiece of the Oral and Intangible Heritage of Humanity in 2005 and inscribed it on the Representative List in 2008 (Mongolia, ID 00115; the Inner Mongolian practice inscribed separately, ID 00112).

## 2. The craft procedure (how the human does it)

1. **Learn by ear in the pastoral context.** No notation. Apprentices internalize the regional repertory by listening and by practicing alone on the steppe, often singing while riding slowly on horseback — a journey is measured in "three long songs." Masters teach stanza by stanza.
2. **Fix the poetic text.** Urtiin duu is strophic: typically 4-line stanzas. Imagery centers on horses, homeland, parents, and nature; texts may be praise (*magtaal*-flavored), philosophical, religious, romantic, or celebratory. The text is sung to the same skeleton on every stanza.
3. **Compose the *shilber* (melodic skeleton).** The skeleton is the underlying contour of each phrase: an **anhemitonic pentatonic** field, **wide ambitus** (melodies can cover up to three octaves), arch-shaped phrases, and structural tones landing on the mode's finals. The skeleton is the **identity anchor** — every stanza sings it, and the ornament surface must never obscure it.
4. **Choose the style register.** Three styles, distinguished by the *way* the skeleton is sung rather than by length:
   - **Aizam** — "major"/grand long songs: broad melody, ceremonial function, opening vocable *"Aya, zee khu"*, sung in sequence at the start of a feast or ceremony; the summit of the art that tests singer and morin khuur player.
   - **Suman** — "ordinary" long songs.
   - **Besreg** — "minor"/shortened songs: short verses, refrains, melodic courses full of leaps and bounds.
5. **Build each stanza as TWO parts** (the genre's signature macro-architecture):
   - **Opening slow section** — free rhythm, unmeasured; sustained *shuranhai* tenuto tones with deeply modulated vibrato on the vowels (*dan* single / *davkhar* double forms).
   - **Faster concluding section** — metrically pulsed, marked by *tsokhilgo* (modulated pulsation); ornament density rises.
6. **Elaborate the skeleton with *khooslol* ornaments** — the ornamental surface varies from stanza to stanza (skeleton fixed, surface free): *nugalaa* (sharp notes modulated lower in pitch), *usrelt* (upward/downward tone leaps or sudden shifts), *tsatslaga* (sprinkling), *khayalga* (bestrewing — free improvised tones), *shigshree* (sifting — repeated vocal vibration). Improvisation is **within** the skeleton, never against it.
7. **Add morin khuur heterophonic support** (eastern Khalkha). The two-string horse-head fiddle (strings traditionally a fifth apart, modern practice a fourth — B♭–F) plays the melody on the high string while the low string drones; it gives an instrumental **prelude and interludes** and shadows the voice heterophonically. Inner Mongolian practice often doubles the skeleton in **parallel 4ths/5ths** (double-stops). Western Oirats sing unaccompanied or with the *igil*.
8. **Sing full-voice in the highest register** with strict breathing discipline: the breath is physically free but the rules are strict — only the absolutely necessary breathing breaks, never interrupting a chain of ornaments. The richer the voice and the longer the hold, the more intense the effect.
9. **Follow ceremonial etiquette and scale.** Aizam songs open ceremonies in a set order; at full length a long song is a marathon (*Uvgin shuvuu khoyor*, "Old Man and the Bird," has 32 stanzas ≈ 3 hours). The socialist era truncated stage renditions to 3–5 minutes; the full-length tradition was restored in the 2010s (Dorjdagva Myagmarsuren's *Mongolian Statehood Long Song* recordings, 25–35 min each).
10. **Transmit and compose new songs.** New songs arise by fitting new texts to known skeletons (text replacement) or, for master singers, by fashioning a new skeleton within the regional formula conventions. Contemporary art composers (Jantsannorov) adapt long-song material into notated works.

## 3. Practitioner examples

- **Namjilyn Norovbanzad** (1928–2002) — the most celebrated urtiin duu singer, global icon of the genre.
- **Dorjdagva Myagmarsuren** — singer-researcher; restored and recorded full-length *aizam* long songs (*Mongolian Statehood Long Song*, 2013, 9 songs / 258 min), with morin khuur player **Battulga Batbold**.
- **Ganbaatar Khongorzul** — internationally recognized long-song singer (UNESCO-associated performances).
- **B. Sarantuya, D. Erdenechimeg** — contemporary stage masters of the State Academic theatre tradition.
- **Sambuugiin Pürevjav** — morin khuur master (Altai Khairkhan).
- **Inner Mongolia:** Alashaa (Alxa) long-song singers documented by **Ojuna W. Pilcher** (2018) — nostalgia, horse metaphors, ornamentation tied to nomadic lifeways.
- **Scholars:** Carole Pegg (*Mongolian Music, Dance & Oral Narrative*, 2001), Charlotte D'Evelyn (*The Long Song of Mongolia*, Cambridge, 2019), Sunmin Yoon (2011), David Chao (2010).

## 4. UnitMatrix integration (Musicom engine)

### Voices
- **Voice 0 = Shilber skeleton spine** — the invariant identity anchor: pentatonic contour, structural tones, phrase arch, finals. Constant across all stanzas; never altered by the ornament layer.
- **Voice 1 = Khooslol ornament layer** — the compositional surface: *shuranhai* (tenuto+vibrato — realized as long durations + pitch-bend/articulation intent), *nugalaa*, *usrelt* (leaps), *tsokhilgo* (pulsation), *tsatslaga*, *khayalga*, *shigshree*. Density gradient sparse→dense across stanzas; must never add new structural tones.
- **Voice 2 = Morin khuur heterophony** — echoes V0's contour with delay/ornament, low-string drone active; Inner Mongolian variant doubles V0 in parallel 4ths/5ths (double-stop chords).
- **Voice 3 = Drone/pedal** — invariant tonic sustain (low morin khuur string / igil).
- **Voice 4 = Metadata** — style tag (aizam/suman/besreg), stanza index, ornament log, text stanza.

### Sections
`S0 Prelude (morin khuur solo)` → per stanza: `S_n_Slow (free rhythm)` + `S_n_Fast (pulsed)` → `S_Final Coda (cadence convergence + release)`.

### Rules (encoder sketch)
- **Skeleton invariance:** V0 identical across all stanzas (zero-drift safe: same cell reused per stanza column).
- **Style gate:** aizam requires vocable opening + broad range; besreg allows short verses + leap-heavy contour.
- **Two-part rhythm rule:** slow sections are **free-rhythm** — realized as absolute-tick rubato placement (no grid quantization); fast sections pulsed with *tsokhilgo* accents.
- **Pentatonic pitch set:** anhemitonic pentatonic field; wide-ambitus filter (≤ ~3 octaves).
- **Heterophonic echo constraint:** V2 shadows V0's contour; no independent harmonic progression.
- **Drone invariance:** V3 continuous.
- **Breathing-break mask:** ornament chains never interrupted — rests only at phrase seams.
- **Melisma-per-syllable budget:** one text syllable may span many beats (long durations), enforcing the "ten words per four minutes" character.
- **Zero-drift padding:** free-rhythm cells still fill their section tick span (terminal landmark), preserving the equal-length invariant.
