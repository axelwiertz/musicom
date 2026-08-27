# HC-017 — Sanjo Jangdan Improvisation (Korean Solo Instrumental Improvisation)

**Tradition / Culture:** Korean traditional music — sanjo (산조, "scattered melodies"), South Korea, ~1890–present. Rooted in pansori (epic vocal narrative) and sinawi (shaman ritual ensemble improvisation). UNESCO-adjacent national intangible heritage (gayageum sanjo lineages designated Important Intangible Cultural Properties).

**Primary Elements:** RHYTHM, PITCH, STRUCTURE, TEXTURE (TEXTURE as ornamental density + chuimsae audience interjection).

**Status:** ✅ Documented

---

## Description

Sanjo is a solo instrumental improvisation — a single melodic instrument (gayageum, geomungo, daegeum, haegeum, piri, ajaeng, taepyeongso) accompanied by one drummer on the janggu hourglass drum. The name literally means "scattered melodies." It is NOT fixed music: "the musician can make new music with original variations; sanjo has endless melodies in which musicians make new compositions that change with the times."

The core compositional device is the **jangdan cycle** (장단, 長短): a fixed rhythmic-metric mode, each of which carries a distinct emotional state and tempo. A sanjo performance is an **accelerating sequence of jangdan** — it opens in the slowest, most expansive cycle (jinyangjo) and progressively moves through ever-faster cycles, ending in a fast, dense climax (danmori/hwimori) that generates audience enthusiasm.

The craft is therefore **variation-within-a-fixed-rhythmic-scaffold**: the player never invents freely, but ornaments, extends, and re-orchestrates modal melodic material as the ground-tempo climbs. The janggu drummer (gosu) is not passive — they supply **chuimsae** (exclamations like "Ulssu!" / "좋다" / "eolssigu") at climactic or virtuosic moments, and the audience answers with their own chuimsae. A big chuimsae = a good performance, and the musician responds by performing better. Chuimsae is a real-time feedback loop that *shapes* the improvisation; "without chuimsae, the music is meaningless."

---

## Craft Steps (how the human does it)

1. **Internalize the jangdan system by rote.** Learn the standard cycle set and their emotional-affective registers: jinyangjo (진양조, very slow, ~6/2, most expansive/lamenting), jungmori (중모리, moderate), jungjungmori (중중모리, faster), jajinmori (자진모리, quick), hwimori (휘모리, very fast), danmori (단모리, fastest, climactic). Each cycle is a loop of accent-pattern beats the player must land on. Mastery = being able to place any phrase within any cycle without counting.

2. **Fix the jo (melodic mode) and instrument.** Three core modes on the gayageum: ujo (우조, "right/clear", G-key, dignified/bright), pyeongjo (평조, "level", C-key, calm/neutral), gyemyeonjo (계면조, "interface", B♭-key, sorrowful/plaintive — the most characteristic of sanjo). The whole piece lives in (or migrates between) these modal pitch sets; gyemyeonjo's characteristic descending, sighing figures dominate much of the repertoire.

3. **Open in jinyangjo.** The slowest cycle. Establish the mode, state the core melodic kernel (the "theme" that will be varied all night), play long ornamental phrases with wide vibrato (left-hand string pressing), and exploit the maximum expressive space per beat. This is the listener's "sinking into the melody."

4. **Advance through the accelerating jangdan sequence.** Move jinyangjo → jungmori → jungjungmori → jajinmori, restating and densifying the same modal kernel each time. Each stage = same melodic DNA, higher rhythmic subdivision, more ornament, less space.

5. **Vary, never invent.** At every stage the player performs *original variations* on the established material: left-hand nonghyeon (vibrato/bend), grace-note clusters, octave displacements, rhythmic diminution. The identity of the kernel is preserved (recognizability constraint); only its surface density changes.

6. **Play call-and-response with the gosu.** The drummer tracks the soloist, marks phrase endings, and fires chuimsae at climactic points; the soloist answers by pushing harder. This two-way conversation is the engine of intensity — it is not mere accompaniment.

7. **Answer the audience's chuimsae.** Listen for interjections from the room. A surge of chuimsae at a virtuosic run means "do it again, higher, faster" — the player extends that passage. Audience becomes co-composer of the pacing.

8. **Climax in danmori/hwimori.** The fastest cycle: rapid-fire repeated notes (the gayageum's ssangtwinggim "double bounce" flick technique), maximal ornament density, register climbs — generating audience enthusiasm and closing the arc.

9. **Close.** Descend from the climactic register, restate the opening kernel in its plain form, and resolve on the modal tonic.

---

## Practitioner Examples

- **Kim Chang-jo (김창조, 1865–1920):** the founding figure, developed gayageum sanjo around 1890 out of pansori and sinawi practice. Established the core accelerating jangdan architecture still taught today.
- **Kim Juk-pa (김죽파) & Seong Geum-ryeon (성금연):** two canonical gayageum sanjo lineages (Gyeonggi/Jeolla schools), each codifying a full suite of jangdan-by-jangdan variations as teachable repertoire.
- **Hwang Byung-ki (황병기, 1936–2018):** brought sanjo's ornamental improvisational vocabulary into contemporary gayageum composition.
- **Yi Saenggang (이생강):** leading daegeum (transverse flute) sanjo master, whose 1920s-derived school is the most widespread flute sanjo.
- **Kim Yeong-jae (김영재) & Ji Aeri:** geomungo (six-string zither) sanjo, notable for the instrument's harsher attack and percussive left-hand technique.
- **Sinawi tradition (shaman ritual):** the improvisational ancestor — an ensemble of two flutes, haegeum, daegeum, janggu, buk improvising collectively on a shared modal/rhythmic ground, which sanjo distilled into solo form.

---

## UnitMatrix Integration (Musicom)

**Voices:**
- **Voice 0 = Janggu (gosu) — jangdan cycle spine.** The invariant rhythmic scaffold. Each section is a different jangdan cycle; within a section the cycle loops with its accent pattern fixed. In Musicom terms this is the "bell" / "timeline" voice: a percussion track whose accent grid is the constraint everything else aligns to. The gosu also fires sparse chuimsae accent events at climactic onsets.
- **Voice 1 = Lead instrument (gayageum/geomungo/daegeum) — modal solo.** Melodic line generated by *varying* a fixed kernel: same pitch-class skeleton, ornamented and rhythmically densified per section. Onsets target the jangdan accent grid; ornamental notes (nonghyeon/grace clusters) fill weak positions.
- **Voice 2 = Optional heterophonic echo / second melodic layer.** In some schools a supporting string/flute shadows Voice 1 in loose unison with idiomatic ornament — like the makam/kotekan doubling roles. (Optional; core sanjo is solo.)
- **Voice 3 = Chuimsae / audience response (texture layer).** Sparse, loud, unpitched interjection events ("Ulssu!"/"eolssigu") placed at section transitions and virtuosic peaks. Encodes the *feedback loop*: chuimsae density at a phrase = intensity score that gates whether the next phrase repeats/extends.

**Sections:** Sections = jangdan stages, each a fixed cycle + tempo band:
`Jinyangjo (slowest) → Jungmori → Jungjungmori → Jajinmori → Hwimori/Danmori (fastest, climax) → return/close`.
Each section restates the same modal kernel at higher subdivision density. Macro-form is a **monotonic tempo/density ramp** (the "accelerando suite").

**Rules (encode as constraints):**
1. **Jangdan invariance:** within a section, Voice 0 loops its cycle unchanged; solo onsets target cycle accents.
2. **Monotonic tempo acceleration:** `tempo(S_{n+1}) > tempo(S_n)` — each successive section is faster (no back-stepping).
3. **Jo (mode) pitch-set constraint:** all pitches drawn from ujo / pyeongjo / gyemyeonjo set; gyemyeonjo adds descending-tendency weighting (sighing figures).
4. **Variation-not-invention:** each section's melody is an ornamented transformation of one fixed kernel; recognizability constraint (kernel pitch-class skeleton preserved, density/ornament varies).
5. **Density progression:** subdivision density and ornament count increase monotonically across sections (sparse→dense).
6. **Chuimsae feedback:** intensity spikes at climactic onsets trigger Voice 3 interjections + phrase extension (repeat/extend on high chuimsae).
7. **Call-and-response:** gosu marks phrase ends; soloist answers (antecedent→consequent pairing at cycle boundaries).
8. **Climax placement:** peak register + ornament density at ~75–85% of total duration (danmori/hwimori), then descending close to tonic.

**Musicom method mapping:** This is a **rules-based (deterministic) scaffold + stochastic variation fill** method in the Musicom taxonomy. The jangdan cycle is a deterministic rhythmic skeleton (closest to **011 Euclidean Groove** — pulse + accent grid); the jo mode is a pitch-set corridor (closest to **023 Tendency Masking** — L(t)/U(t) bounds, with gyemyeonjo imposing a descending tendency); the ornamented variation is Markovian/constrained fill (closest to **002 Markov** operating within the skeleton). It pairs naturally with **001 Skeleton-First** (kernel + jangdan = skeleton) and **022 MCWS** (quantize ornamental runs to the jo pitch set without breaking accent alignment). The chuimsae feedback loop is a novel *interactive intensity gate* Musicom currently lacks.

---

## Why it matters for Musicom

Sanjo gives Musicom a clean, culture-diverse model of **monotonic-tempo macro-form driven by a fixed rhythmic cycle**: a single melodic kernel restated across an accelerating sequence of jangdan sections, densified by ornament rather than rewritten. This maps directly onto UnitMatrix's Voices × Sections grid — the janggu is the invariant timeline (like the Ewe bell or partimento bass), the lead instrument is a variation engine, and sections are pre-ordered by tempo. The chuimsae/feedback rule adds a genuinely interactive, audience-shaped intensity controller — a first for the engine's rule set. It also extends the sparse-vs-continuous hybridization pattern: sanjo's fast danmori sections are dense continuous fill, while its slow jinyangjo opening is sparse — the *same* kernel renders both, demonstrating how one method spans the sparse/continuous spectrum.
