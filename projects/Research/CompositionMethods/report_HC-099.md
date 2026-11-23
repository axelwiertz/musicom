# Report HC-099 — Cumbia (Colombian) Composition & Arrangement Craft

**Job:** daily-human-composition-research (nightly)
**Date:** 2026-11-22
**Method ID:** HC-099
**Next free ID:** HC-100
**Detail file:** `human_method_HC-099_cumbia-gaita-orquesta-craft.md`

---

## 1. Method name

**Cumbia (Colombian) Composition & Arrangement Craft — Gaita-Ensemble Timekeeper Architecture × Orquesta Cumbia Arrangement**
(Llamador Offbeat Spine, Guacharaca Rasp, Tambora Downbeat Grid, Root–5th Bass, Offbeat Harmony, Copla Call–Response)

## 2. Tradition / culture

- **Latin American — Colombian Caribbean coast** (epicenter: Depresión Momposina / old Indigenous "Pocabuy" country around El Banco, Guamal, Mompox, Ciénaga, Magdalena river valley).
- **Tri-ethnic synthesis** (Conquest/Colonial era): Indigenous *gaita* duct-flutes (*kuisi bunzí* = gaita hembra, *kuisi sigí* = gaita macho, Kogi/Guna) + *caña de millo*; African conical drums (*tambor alegre*, *tambor llamador*, *tambora*), *guache*, maracas and the responsorial vocal form; Spanish octosyllabic *coplas*.
- **Time span:** 19th c. (first written records; La Cumbia Soledeña founded 1877; Gosselman's 1825–26 account of the gaita ensemble) → present. **Declared Cultural Heritage of the Nation of Colombia, October 2022.** Hemispheric diffusion from the 1940s (orquesta cumbia / *música tropical*) → Mexican cumbia (sonidera, norteña, rebajada), Peruvian chicha, Argentine villera/santafesina, Central American marimba cumbia.
- Panamanian cumbia is a **separate autochthonous tradition** — not covered here.

## 3. Layer classification

**human (→concrete)** — target layer **concrete** when implemented: the method realizes material as concrete pitch/rhythm units in the UnitMatrix (fixed 2/4 sixteenth-cell grid, absolute ticks). All voices are human-authored craft layers; no algorithmic/AI generation, no DSP.

## 4. Craft procedure (how the human does it, step by step)

1. **Fix the grid:** tempo 80–100 BPM, meter 2/4 (felt as *compás partido* 2/2); one two-bar cycle = **16 sixteenth-note cells** — the zero-drift frame every part locks to.
2. **Guacharaca rasp (invariant):** never stops; per beat = long scrape + two short scrapes ("*chaaa-chi-ki*" / "chu-chucu-chu"), accents on the offbeat side of each beat.
3. **Llamador (the clock):** plays **only offbeat** (cells 3, 7, 11, 15 = "and" of each beat) and **never improvises** — the one drum to which "revuelos"/"lujos" are forbidden. Its half-beat delay against the pulse *is* the cumbia "balance"; on the beat it becomes a military march.
4. **Tambora (bombo, sticks):** marks measure starts / downbeats (live players elaborate).
5. **Bass:** fundamental + fifth on the pulse ("like footsteps"; in G: G–D) — carries the harmonic grid.
6. **Harmony (accordion / piano / brass):** offbeat chords ("a contratiempo", together with the llamador); almost always **I–IV–V**; in minor keys the V is **major** (A minor → E major, G♯ leading-tone pull home).
7. **Melody:** gaita hembra (5 holes) or caña de millo — short, repeated, neighboring-note phrases, rising and returning to the tonic; pentatonic/hexatonic modality. **Gaita macho** (2 holes) plays rhythmic *contrapunto* + shakes the *maracón* — an ancient marking/counterpoint voice.
8. **Vocal copla** (sung cumbia/cumbiamba): octosyllabic quatrains, **call-and-response** (solo verse vs. chorus/estribillo). Classic cumbia is purely instrumental by design ("aire zambo": Indigenous melody + Black drum rhythm, never sung).
9. **Orquesta arrangement (Lucho Bermúdez / Pacho Galán craft):** timekeeper trio (guacharaca/güira, llamador, tambora) + congas/timbales; bass root–5th; brass/clarinet section with offbeat punches and short mambo-derived riffs; piano offbeat comping. Form: **intro → copla → estribillo → instrumental mambo build → cierre** (return to bare skeleton, cadence on tonic).
10. **Dance check:** 80–100 BPM, sliding "arrastrado" step, the felt *retraso* of the llamador must survive.
11. **Regional re-voicing:** keep the skeleton (guacharaca long-short-short, llamador offbeat, root–5th bass); re-voice the top — Colombian (gaita/millo/accordion), sabanera (banda pelayera wind band), Mexican (sonidera synths, norteña accordion, rebajada slowed records), Peruvian chicha (electric guitars), Argentine (keyboards).

## 5. Practitioner examples

| Practitioner | Example / role |
|---|---|
| La Cumbia Soledeña (founded 1877) | Oldest named traditional cumbia group |
| Totó la Momposina | Traditional drum + caña de millo cumbia (*La Candela Viva*, 1993) |
| José Barros (1915–2007) | *La Piragua*, *Las Pilanderas*, *El Pescador*, *Navidad Negra*; founded Festival Nacional de la Cumbia (El Banco, 1971) |
| Juan Madera Castro + Wilson Choperena | *La Pollera Colorá* (music 1960, lyrics 1962) — iconic Colombian song |
| Lucho Bermúdez (1912–1994) | *Prende la Vela*, *Cumbia Colombiana*, *Danza Negra*, *Marbella*; big-band stylization ("vestir el porro de frac") |
| Pacho Galán (1906–1988) | *Ay Cosita Linda* (1954 merecumbé), *Fiesta de Cumbia*, *Cumbia Alegre* |
| Andrés Landero, Aníbal Velásquez | Accordion cumbia pioneers |
| Los Corraleros de Majagual | Calixto Ochoa, Lisandro Meza, Alfredo Gutiérrez (accordion cumbia) |
| Luis Carlos Meyer | *Cumbia Cienaguera* — first cumbia recorded abroad (Mexico 1950, with Rafael de Paz) |
| Amparito Jiménez | Popularized *La Pollera Colorá* |
| Los Mirlos, Juaneco y Su Combo | Peruvian chicha (electric-guitar cumbia) |
| Celso Piña | Mexican cumbia (Monterrey) |
| Scholars | Delia Zapata Olivella (1962), Guillermo Abadía Morales, George List (New Grove), Peter Wade (*Music, Race & Nation*, 2000) |

## 6. UnitMatrix mapping

**Voices (rows):**
- V0 Guacharaca — invariant continuous rasp (long-short-short per beat; accents cells 4/8/12/16).
- V1 Llamador — offbeat hits cells 3/7/11/15 only; ornament prohibition.
- V2 Tambora — downbeat anchor (measure starts).
- V3 Tambor alegre — improvising lead drum (open/slap fills; density ramp; optional).
- V4 Bass — root–5th on pulse (harmonic grid carrier).
- V5 Harmony (accordion/piano/brass) — offbeat chord units; I–IV–V; major V in minor.
- V6 Melody (gaita hembra/millo/clarinet) — pentatonic/hexatonic neighbor-note phrases returning to tonic.
- V7 Gaita macho — 2-hole rhythmic counterpoint + maracón (marking function).
- V8 Vocal copla + chorus — call-and-response (octosyllabic quatrains).
- V9 Brass section (orquesta) — offbeat punches/riffs, mambo-derived.

**Sections (columns):** S0_Intro_Instrumental → S1_Copla_1 → S2_Estribillo → S3_Copla_2/Mambo build → S4_Cierre.

**Rules to encode:**
1. 2/4 grid lock, 80–100 BPM, 16-cell two-bar cycle; all units end at boundaries (zero-drift).
2. Guacharaca invariance (never rests).
3. Llamador offbeat-only (cells 3/7/11/15), no revuelos/lujos.
4. Tambora downbeat anchor.
5. Bass root–5th on pulse only.
6. Offbeat harmony only (never on the beat).
7. I–IV–V vocabulary; minor tonic → major V (leading-tone pull).
8. Pentatonic/hexatonic melody, conjunct neighbor-note motion, return to tonic.
9. Call–response non-overlap mask (V8 solo vs chorus).
10. Orquesta density arc monotonic into S3, then cierre; classic cumbia density static.
11. Tempo gate 80–100 BPM.

## 7. Table row added (human_methods_db.md)

```
| **HC-099** | human (→concrete) | Cumbia (Colombian) Composition & Arrangement Craft — Gaita-Ensemble Timekeeper Architecture × Orquesta Cumbia (Llamador Offbeat Spine, Guacharaca Rasp, Tambora Downbeat Grid, Root–5th Bass, Offbeat Harmony, Copla Call–Response) | Latin American — Colombian Caribbean folk (Pocabuy/Depresión Momposina; tri-ethnic: Indigenous gaita/millo × African drums/responsorial × Spanish copla), 19th c.–present; declared national heritage Oct 2022; hemispheric diffusion 1940s– (Mexican sonidera/norteña/rebajada, Peruvian chicha, Argentine villera/santafesina) | RHYTHM, STRUCTURE, PITCH, HARMONY, TEXTURE | Fix 2/4 grid, 80–100 BPM, 16-cell two-bar cycle → lay guacharaca rasp (continuous, long-short-short "chaaa-chi-ki" per beat, invariant) → add llamador (small hand drum, offbeat cells 3/7/11/15 ONLY, never improvises — the half-beat delay IS the cumbia "balance") → tambora marks downbeats → bass plays root–5th on the pulse → harmony (accordion/piano/brass) on offbeats with I–IV–V (minor tonic → major V for the leading-tone pull) → melody (gaita hembra 5-hole / caña de millo) in short repeated neighbor-note pentatonic phrases returning to tonic; gaita macho (2-hole) plays rhythmic counterpoint + maracón → optional copla verse call-and-response (octosyllabic quartets) → orquesta arrangement (Lucho Bermúdez/Pacho Galán): intro → copla → estribillo → instrumental mambo build → cierre on the bare timekeeper skeleton | Voice 0 = guacharaca (invariant continuous rasp). Voice 1 = llamador (offbeat timekeeper, ornament prohibition). Voice 2 = tambora (downbeat anchor). Voice 3 = tambor alegre (improvising lead drum, density ramp). Voice 4 = bass (root–5th on pulse, harmonic grid). Voice 5 = harmony/accordion (offbeat chord units, I–IV–V). Voice 6 = gaita hembra/millo melody (pentatonic, neighbor-note, returns to tonic). Voice 7 = gaita macho (rhythmic counterpoint + maracón, marking function). Voice 8 = vocal copla + chorus (call–response mask). Voice 9 = brass (orquesta punches). Sections = S0_Intro_Instrumental → S1_Copla_1 → S2_Estribillo → S3_Copla_2/Mambo build → S4_Cierre. Rules: 2/4 16-cell grid lock (zero-drift), guacharaca invariance (never rests), llamador offbeat-only + no revuelos/lujos, tambora downbeat anchor, bass root–5th on pulse, offbeat-harmony-only (never on the beat), I–IV–V vocabulary + major V in minor, pentatonic neighbor-note melody returning to tonic, call–response non-overlap, monotonic orquesta density arc, 80–100 BPM tempo gate | La Cumbia Soledeña (founded 1877), Totó la Momposina, José Barros (La Piragua, Las Pilanderas), Juan Madera Castro + Wilson Choperena (La Pollera Colorá 1960/62), Lucho Bermúdez (Prende la Vela, Cumbia Colombiana, Danza Negra), Pacho Galán (Ay Cosita Linda, Fiesta de Cumbia), Andrés Landero, Aníbal Velásquez, Los Corraleros de Majagual (Calixto Ochoa, Lisandro Meza, Alfredo Gutiérrez), Luis Carlos Meyer (Cumbia Cienaguera, first abroad 1950), Amparito Jiménez, Los Mirlos & Juaneco y Su Combo (chicha), Celso Piña; scholars Zapata Olivella (1962), Abadía Morales, List (New Grove), Wade (2000) | ✅ Documented |
```

## 8. Next free ID

**HC-100** (max existing = HC-099; verified no duplicates; 99 unique HC IDs in table).

## 9. Quirks & pitfalls

- The **llamador discipline is the genre**: ornament it or put it on the beat and the cumbia "balance" dies — encode as a hard rule.
- Classic cumbia is **instrumental by design**; vocals (cumbiamba) are a later overlay — don't default to vocals.
- The gaita pair is **two-voice counterpoint** (hembra melody + macho rhythmic counterpoint), not unison/heterophony — separate voices.
- Minor cumbias need the **major V** or the cadential pull home is lost.
- Cumbia has **no clave instrument** (unlike Cuban son, HC-018): timekeeping = guacharaca + offbeat llamador on a 2/4 grid.
- Panamanian cumbia = separate tradition; Colombian diffusion is what went global.
- Regional variants re-voice the top but **never touch** the guacharaca/llamador/bass grid.

## 10. Sources

- Wikipedia: *Cumbia*, *Cumbia (Colombia)* (en + es), *Guacharaca*, *Tambor llamador* (es), *La Pollera Colorá*, *Lucho Bermúdez*, *Pacho Galán*, *José Barros*.
- El Hipnótico — "Ritmo de cumbia: cómo se hace, de la güira al bajo" (Escuela de Beats, Módulo 11): concrete pattern pedagogy — guacharaca "chaaa-chi-ki", llamador offbeat cells 3/7/11/15, tambora downbeat, root–5th bass on pulse, I–IV–V offbeat harmony, minor→major V, 80–100 BPM.
- Delia Zapata Olivella (1962), Guillermo Abadía Morales (1962/1983), George List (New Grove, *Colombia: Folk music*), Peter Wade (*Music, Race & Nation: Música Tropical in Colombia*, 2000).
