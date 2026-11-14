# Report HC-091 — Mongolian Urtiin Duu (Long Song) Composition

**Date:** 2026-11-13 (nightly human-composition-research run)
**Method ID:** HC-091 (next free ID after this: **HC-092**)
**Layer:** `human (→concrete)` — human-craft knowledge; target layer **concrete** when realized through the UnitMatrix (the shilber skeleton + khooslol ornament surface realize directly as concrete MusicUnits; free-rhythm slow sections realize as absolute-tick rubato events)

---

## 1. Method name & tradition

**Mongolian Urtiin Duu (Long Song) Composition — *Shilber* Skeleton × *Khooslol* Ornament Craft**
(*Aizam* / *Suman* / *Besreg* style registers; two-part slow→fast stanza architecture; morin khuur heterophonic support)

- **Tradition / Culture:** Mongolian pastoral vocal tradition — Khalkha (central/east Mongolia, morin khuur + limbe accompaniment), Oirat (west Mongolia: unaccompanied or *igil*), Buryat and Inner Mongolian variants. Roots at least to the 13th c. (Genghis unification; *Ertnii Saikhan* sung at weddings and imperial feasts). UNESCO: proclaimed Masterpiece of the Oral and Intangible Heritage of Humanity 2005; inscribed Representative List 2008 (Mongolia, ID 00115; Inner Mongolian practice ID 00112).
- **Primary elements (Musical Elements Framework):** PITCH (skeleton + ornament), STRUCTURE (two-part stanza, strophic chain), RHYTHM (free→metered), TEXTURE (heterophony + drone). HARMONY is NOT primary — vertical sonorities are emergent (drone + parallel 4ths/5ths), never functional.

## 2. Why this method, why now (rotation & overlap check)

- **Rotation:** recent entries — Finnic rune song (HC-090), Western Classical canon (HC-089), jazz contrafact (HC-088), Russian znamenny (HC-087), Caribbean steelband (HC-086), Japanese koto (HC-085). HC-091 adds **Central Asian / Mongolian pastoral song**, a region entirely absent from the framework so far.
- **Overlap check:** grep of the CompositionMethods tree for `Mongol|urtyn|urtiin|duu|morin|khooslol|shilber|overtone|khöömii` returns no existing HC entry (HC-027 Tuvan overtone throat singing is a Siberian *technique* tradition; HC-003 Ottoman makam heterophony is a different heterophonic system). Urtiin duu = melody-skeleton × ornament-surface craft over a pentatonic field with free-rhythm/fast two-part architecture — no duplication with any existing row.

## 3. The craft procedure in detail (how the human does it)

1. **Learn by ear in the pastoral context** — no notation. The apprentice internalizes the regional repertory by listening and by practicing **alone on the steppe, singing while riding slowly on horseback** ("a trip lasted three long songs"). Masters teach stanza by stanza; the repertory is ceremonial/social (feasts, weddings, Naadam, seasonal rites).
2. **Fix the poetic text** — strophic, typically 4-line stanzas; imagery: horses, homeland, parents, nature; praise, philosophical, romantic, or celebratory themes. Every stanza is sung to the same melodic skeleton.
3. **Compose the *shilber* (melodic skeleton)** — the underlying phrase contour: **anhemitonic pentatonic** field, **wide ambitus** (up to ~3 octaves), arch-shaped phrases, structural tones on the mode's finals. The skeleton is the piece's **identity anchor**; all stanzas sing it.
4. **Choose the style register** — the three styles differ by *performance manner*, not length:
   - **Aizam** ("major"/grand): broad melody, ceremonial, opens with the vocable *"Aya, zee khu"*, sung in a set sequence at the start of ceremonies; the summit of the art.
   - **Suman** ("ordinary"): the everyday long song.
   - **Besreg** ("minor"/shortened): short verses, refrains, leap-filled melodic courses.
5. **Build each stanza in TWO parts** — the genre's signature architecture:
   - **Slow opening section:** free rhythm/unmeasured; sustained *shuranhai* (tenuto with deeply modulated vibrato on vowels; *dan* single / *davkhar* double).
   - **Fast concluding section:** metrically pulsed, marked by *tsokhilgo* (modulated pulsation).
6. **Elaborate the skeleton with *khooslol* ornaments** — the ornamental vocabulary IS the compositional surface: *nugalaa* (sharp notes modulated lower), *usrelt* (upward/downward tone leaps), *tsatslaga* (sprinkling), *khayalga* (bestrewing — free improvised tones), *shigshree* (sifting — repeated vibration). **Skeleton fixed, surface free** — ornamentation varies per stanza; improvisation happens within the skeleton, never against it.
7. **Add morin khuur heterophonic support** (eastern Khalkha) — two-string horse-head fiddle (traditionally tuned a 5th apart, modern practice a 4th, B♭–F): melody on the high string + low-string drone; instrumental **prelude and interludes**; heterophonic shadow of the voice. Inner Mongolian practice often doubles the skeleton in **parallel 4ths/5ths** (double-stops). Western Oirats: unaccompanied or *igil*.
8. **Sing full-voice in the highest register** with strict breathing discipline — only necessary breaks, **never interrupting an ornament chain**; longer holds = more intense effect.
9. **Ceremonial etiquette & scale** — aizam songs open the feast in order; full-length renditions are marathon events (*Uvgin shuvuu khoyor*, 32 stanzas ≈ 3 hours). Socialist-era stage practice truncated songs to 3–5 min; the full-length tradition was restored in the 2010s (Dorjdagva Myagmarsuren's *Mongolian Statehood Long Song*, 9 songs / 258 min, 25–35 min each).
10. **Transmission & new composition** — new songs arise by fitting new texts to known skeletons (text replacement) or by master singers fashioning new skeletons within regional formula conventions; contemporary art composers (Jantsannorov Natsag) adapt long-song material to notation.

## 4. Practitioner examples

- **Namjilyn Norovbanzad** (1928–2002) — the iconic urtiin duu singer; brought the genre to world stages.
- **Dorjdagva Myagmarsuren** — singer-researcher; restored and recorded full-length *aizam* songs (2013 album), with morin khuur player **Battulga Batbold**.
- **Ganbaatar Khongorzul** — internationally renowned long-song singer.
- **B. Sarantuya, D. Erdenechimeg** — State Academic theatre stage masters.
- **Sambuugiin Pürevjav** — morin khuur master (Altai Khairkhan).
- **Inner Mongolia:** Alashaa (Alxa) long-song singers documented by **Ojuna W. Pilcher** (2018) — horse/nature metaphor, ornamentation tied to nomadic lifeways and nostalgia.
- **Scholars:** Carole Pegg (2001), Charlotte D'Evelyn (2019, Cambridge), Sunmin Yoon (2011), David Chao (2010).

## 5. UnitMatrix mapping (Musicom engine)

### Voices
- **Voice 0 = Shilber skeleton spine** — invariant pentatonic contour, structural tones, phrase arch, finals; identical cell reused across every stanza column (zero-drift safe).
- **Voice 1 = Khooslol ornament layer** — surface elaboration (shuranhai/nugalaa/usrelt/tsokhilgo/tsatslaga/khayalga/shigshree); density gradient sparse→dense per stanza; never adds new structural tones.
- **Voice 2 = Morin khuur heterophony** — echoes V0's contour with delay/ornament + low-string drone; parallel 4th/5th double-stop variant (Inner Mongolian mode).
- **Voice 3 = Drone/pedal** — invariant tonic sustain (low morin khuur string / igil).
- **Voice 4 = Metadata** — style tag (aizam/suman/besreg), stanza index, text stanza, ornament log.

### Sections
`S0 Prelude (morin khuur solo)` → per stanza `S_n_Slow (free rhythm)` + `S_n_Fast (pulsed)` → `S_Final Coda (cadence convergence + release)`.

### Rules (encoder sketch)
- **Skeleton invariance** — V0 constant across stanzas.
- **Style gate** — aizam: vocable opening + broad range; besreg: short verses + leap-heavy contour.
- **Two-part rhythm rule** — slow section unmeasured: absolute-tick rubato placement, NO grid quantization; fast section pulsed with tsokhilgo accents.
- **Pentatonic pitch set** + **wide-ambitus filter** (≤ ~3 octaves).
- **Heterophonic echo constraint** — V2 shadows V0 contour; no independent harmony.
- **Drone invariance** — V3 continuous.
- **Breathing-break mask** — rests only at phrase seams; ornament chains never interrupted.
- **Melisma-per-syllable budget** — one syllable may span many beats (the "ten words per four minutes" character).
- **Zero-drift padding** — free-rhythm cells still fill their section tick span (terminal landmark), preserving the equal-length invariant.

## 6. Table row added (human_methods_db.md)

```
| **HC-091** | human (→concrete) | Mongolian Urtiin Duu (Long Song) Composition — Shilber Skeleton × Khooslol Ornament Craft (Aizam/Suman/Besreg Styles; Two-Part Slow→Fast Architecture; Morin Khuur Heterophonic Support) | Mongolian pastoral vocal tradition — Khalkha (central/east Mongolia), Oirat (west: unaccompanied or igil), Buryat & Inner Mongolian variants; 13th c. roots (Genghis unification; Ertnii Saikhan at weddings/imperial feasts) → present; UNESCO Masterpiece 2005 → Representative List 2008 (Mongolia ID 00115; Inner Mongolian practice ID 00112); scholarship Pegg (2001), Chao (2010), Yoon (2011), Pilcher (2018), D'Evelyn (2019) | PITCH, STRUCTURE, RHYTHM, TEXTURE (HARMONY emergent) | Learn by ear in pastoral context (no notation; practice singing alone on horseback — a journey is measured in "three long songs") → fix the poetic text (strophic 4-line stanzas; horse/homeland/nature/praise imagery) → compose the shilber melodic skeleton (anhemitonic pentatonic contour, wide ambitus up to ~3 octaves, arch-shaped phrases, structural finals; the skeleton is the identity anchor sung by every stanza) → choose style register (aizam = grand ceremonial, broad melody, vocable opening "Aya zee khu", opens the feast; suman = ordinary; besreg = shortened, shorter verses, full of leaps) → build each stanza as TWO parts: opening slow free-rhythm section (unmeasured, sustained shuranhai tenuto tones with deep modulated vibrato — dan single / davkhar double) → faster metered section with tsokhilgo modulated pulsation → elaborate the skeleton with khooslol ornaments (nugalaa sharp notes modulated lower, usrelt upward/downward tone leaps, tsatslaga sprinkling, khayalga bestrewing/free improvised tone, shigshree sifting/repeated vibration) varying the surface per stanza while the skeleton stays fixed → add morin khuur heterophonic support (two strings traditionally a 5th apart, modern 4th Bb–F; melody on high string + low-string drone; prelude & interludes; Inner Mongolian practice doubles the skeleton in parallel 4ths/5ths; Oirats unaccompanied or with igil) → sing full-voice in the highest register with strict breathing discipline (only necessary breaks, never interrupting an ornament chain) → follow ceremonial etiquette (aizam sequence opens ceremonies; full-length rendition vs socialist-era 3–5 min stage truncation — Uvgin shuvuu khoyor has 32 stanzas ≈ 3 hours) | Voice 0 = shilber skeleton spine (invariant pentatonic contour, structural tones, arch & finals — constant across all stanzas). Voice 1 = khooslol ornament layer (surface elaboration: shuranhai/nugalaa/usrelt/tsokhilgo/tsatslaga/khayalga/shigshree; density gradient sparse→dense; no new structural tones). Voice 2 = morin khuur heterophony (echo of V0 contour + low-string drone; parallel 4th/5th double-stop variant). Voice 3 = drone/pedal (invariant low-string/tonic sustain). Voice 4 = metadata (style tag aizam/suman/besreg, stanza index, ornament log). Sections = S0 Prelude (morin khuur solo) → per stanza S_n_Slow (free rhythm) + S_n_Fast (pulsed) → S_Final Coda (cadence convergence + release). Rules: skeleton invariance (V0 constant), style gate (aizam vocable opening + broad range), two-part rhythm rule (slow section unmeasured absolute-tick rubato, NO grid quantization; fast section pulsed), pentatonic pitch set, wide-ambitus filter (≤ ~3 octaves), heterophonic echo constraint (V2 shadows V0, no independent harmony), drone invariance, breathing-break mask (ornament chains never interrupted), melisma-per-syllable budget (one word can span many beats), zero-drift padding on free-rhythm sections (cells still fill their tick span). | Namjilyn Norovbanzad (1928–2002, urtiin duu icon), Dorjdagva Myagmarsuren (full-length Statehood Long Song recordings, 25–35 min each), Ganbaatar Khongorzul, B. Sarantuya, Sambuugiin Pürevjav & Battulga Batbold (morin khuur), Jantsannorov Natsag (art-song adaptation); scholars Pegg (2001), D'Evelyn (2019), Pilcher (2018), Yoon (2011) | ✅ Documented |
```

## 7. Next free ID

**HC-092** (highest existing = HC-090; HC-091 added by this run; files cross-checked: 90 `human_method_HC-*.md` and 90 `report_HC-*.md` before this run).

## 8. Quirks & pitfalls

- **Free rhythm vs the grid engine:** the defining feature of urtiin duu is *no fixed rhythm* in the slow section. Realization must use absolute-tick rubato placement, not grid quantization — the fast section is the only place pulse rules apply. Do NOT force a meter on the slow section (that would destroy the genre).
- **Ornament fidelity ceiling:** khooslol ornaments are vocal-gestural (vibrato depth, glottal modulations, microtonal inflections). The concrete layer can only approximate — encode as duration + pitch-bend/articulation intent; flag in provenance as approximation.
- **Register realism:** the genre lives in the highest register with a falsetto mix — realization voices must respect the tessitura or the effect is lost.
- **No harmony trap:** this is NOT a harmony tradition. Vertical sonorities are emergent (drone, parallel 4ths/5ths). Do not add functional progressions — the heterophonic echo constraint exists precisely to prevent that.
- **Stanza identity:** skeleton invariance is the whole game — "variations never obscure the skeleton" (cf. the Tramote Rule 6 analogue in Thai piphat). Ornament density may climb, the skeleton must stay recognizable.
- **Text first:** text (and its stanza count) is a first-class constraint; melisma-per-syllable budget drives the piece's duration character.
- **Source verification:** UNESCO element pages are bot-walled (TSPD) — inscription facts verified via the Wikipedia element infobox (ID 00115, 2008, Mongolia) and article body (2005 Masterpiece proclamation).
