# Report — HC-033 Inuit Katajjaq Throat-Singing Duet (Breath-Game Hocket)

**Date:** 2026-09-11
**Job:** daily-human-composition-research
**Method ID:** HC-033
**Layer:** concrete (target when implemented) — human-craft knowledge; realizes material through the UnitMatrix
**Next free ID after this:** HC-034

---

## 1. Method name & tradition

**Inuit Katajjaq Throat-Singing Duet (Breath-Game Hocket).**

Inuit (Arctic North America — Nunavut, Nunavik/Québec, Greenland, Alaska), a centuries-old oral tradition practiced primarily by women as a vocal *game* (Inuktitut: ᑲᑕᔾᔭᖅ katajjaq / katajjaniq). It is distinct from Tuvan/Mongolian solo overtone throat singing (already covered as HC-027): katajjaq is a **duet** of interlocked voiced/unvoiced breath patterns with no drone and no harmonic-series melody. A documented analogous form, **rekuhkara**, existed among the Ainu of Hokkaidō, Japan, confirming the pattern's cross-cultural recurrence.

**Rotation note:** this entry adds Arctic Indigenous music to the diversity rotation (previous: Western Classical ×12, African/Afro-diasporic ×6, East/Southeast Asian ×5, Middle/Central Asian ×3, Latin American ×2, European folk ×3, Indigenous Americas previously 0). Katajjaq is women-led oral craft — a deliberate non-Western, non-harmonic, game-structured pick.

## 2. Layer classification

`layer: concrete (target when implemented)` — same tag as all HC-* rows. Katajjaq is human-craft *knowledge*: it has no algorithmic generator in `generator_registry` and is not spec'd as an ABS-* abstract method. When implemented it would realize material through the UnitMatrix as a concrete two-voice hocket + timbre-mask layer.

## 3. Craft procedure (how a human does it, step by step)

1. **Pair up, face to face.** Two singers stand close, arms linked, often rocking/shuffling foot-to-foot in time. Historically lips nearly touched — the partner's mouth cavity served as a shared resonator (acoustic coupling).
2. **Leader sets a short rhythmic motif.** One singer states a brief vowel-consonant syllable cell, repeating it with **brief silent gaps** between iterations.
3. **Responder fills the gaps.** The second singer inserts a complementary rhythmic pattern into the leader's silences — a strict **hocket**: the rest of one voice is exactly where the other speaks. The composite is a continuous stream neither voice alone produces.
4. **Use voiced + unvoiced sounds, on both breath directions.** The vocabulary is breath-syllables — voiced vowels and unvoiced consonants — produced on inhalation *and* exhalation, so the flow never stops. Pitch is largely timbral/formant-based (low chest sounds vs. high thin sounds), imitating wind, water, animal calls, and everyday sounds.
5. **Loop and ornament.** Each round holds a stable motif while surface ornamentation (vowel-colour shifts, subtle phase displacement, register inflections) varies the texture. The repertoire is passed down orally.
6. **Contest to exhaustion.** Singers push tempo and density. The first to run out of breath, break into laughter, or fail to keep the other's pace is "eliminated." A round lasts 1–3 minutes. The winner is the one who beats the largest number of people in succession.
7. **Elders coach precision.** A senior woman corrects children's sloppy intonation of contours, poorly meshed phase displacements, and vague rhythms — "exactly like a Western vocal coach" — transmitting the craft generation to generation.

## 4. Practitioner examples

- **Tanya Tagaq** — the genre's most famous solo practitioner; extends katajjaq breath techniques into contemporary art music (*Animism*, Polaris Music Prize 2014).
- **Qaunak Mikkigak**, **Kathleen Ivaluarjuk Merritt**, **Alacie Tullaugaq & Lucy Amarualik** — traditional katajjaq duettists (Nunavut/Nunavik).
- **Tudjaat**, **The Jerry Cans** (Nancy Mike), **Quantum Tangle**, **Silla + Rise** — fusion groups weaving katajjaq into pop/folk/rock.
- **Iva & Angu** (album *Katajjausiit*, Juno-nominated 2023), **Caroline & Shina Novalinga** (TikTok popularizers).
- **Ainu rekuhkara** (Hokkaidō) — analogous duet breath-hocket form.

## 5. UnitMatrix mapping (Musicom engine)

### Voices & Sections

| Voice | Role | Content | Invariance |
|---|---|---|---|
| Voice 0 | **Leader** | short motif (vowel-consonant syllable cell), repeated with silent gaps | motif identity per round (frozen while round holds) |
| Voice 1 | **Responder** | complementary pattern filling Voice 0's silences | hocket complement — never overlaps Voice 0 |
| Voice 2 (optional) | **breath/timbre layer** | voiced↔unvoiced, inhalation↔exhalation colour markers (no new pitch class) | continuous-sound invariant |

**Sections** = game rounds / motif states. Each round holds one leader-motif + its complement; a section change = new motif or tempo/density push. Macro-form = single escalating arc (1–3 minutes): entry → steady loop → ornamented variation → tempo push → collapse (one singer breaks → laugh/stop).

### Rules to encode

- **Hocket interlock**: at most one voice onsets per subdivision slot (rest of V0 = note of V1, and vice versa). Composite super-pattern emerges that no single voice plays.
- **Breath-continuity**: sound never stops — every slot is filled by inhalation *or* exhalation (voiced or unvoiced); model as an always-on stream, not discrete rests.
- **Motif invariance per round**: leader cell frozen while a round holds; only surface ornament (vowel colour / micro phase offset) varies.
- **Complement generation**: responder pattern = derived from leader's gap mask (shifted / filled) — deterministic gap-fill, like kotekan interlock (HC-002) but voiced/breath-based rather than pitch-based.
- **Voiced/unvoiced + inhalation/exhalation timbre mask**: alternation drives TEXTURE without changing pitch class.
- **Game/escalation arc**: tempo and density rise monotonically toward the round's end; termination = breath-limit gate (one voice drops out → laugh/stop event).
- **Pitch minimality**: no functional harmony, no scale — pitch is timbral/contour. Contour accuracy is what the elder corrects. Melodic contour imitates nature/wind/animal vocabulary.
- **Contest closure**: section ends on the first "break" (elimination) event, not a cadence.

### Fill/flow note

Katajjaq is the *opposite* of a sparse staccato method: the hocket + breath-continuity invariant produces a **fully continuous** stream by construction. It is therefore a candidate **continuous-fill companion** to sparse rhythmic generators (011 Euclidean / 032 Isorhythmic) rather than a method needing a fill layer added to it.

### Element mapping

- **RHYTHM** — hocket interlock, tempo push, breath-cycle pulsation (primary).
- **TEXTURE** — voiced/unvoiced + inhalant/exhalant alternation, close-mic acoustic coupling (primary).
- **PITCH** — formant/timbral contour only, nature-imitative vocabulary (secondary).
- **STRUCTURE** — single escalating game-round arc (secondary).
- **HARMONY** — absent (monophonic hocket; vertical sonorities incidental).

## 6. Table row added (human_methods_db.md)

```
| HC-033 | human (→concrete) | Inuit Katajjaq Throat-Singing Duet (Breath-Game Hocket) | Inuit (Arctic North America — Nunavut/Nunavik/Greenland/Alaska), centuries-old oral tradition; women's vocal game; UNESCO-recognized; analog Ainu rekuhkara (Japan) | RHYTHM, TEXTURE, PITCH, STRUCTURE | Pair up face-to-face (lips nearly touching = shared mouth-cavity resonator) → leader sets short breath-syllable motif repeated with silent gaps → responder fills each gap with complementary pattern (hocket) → use voiced+unvoiced sounds on inhalation AND exhalation (continuous stream, imitate wind/water/animals) → loop + ornament (vowel-colour shift, micro phase offset) → push tempo/density in contest → first to run out of breath/laugh/break pace loses (round 1–3 min) → elder corrects contour intonation, phase mesh, rhythm like a vocal coach | Voice 0 = leader (motif + silent gaps, frozen per round). Voice 1 = responder (gap-fill complement, never overlaps V0). Voice 2 = breath/timbre layer (voiced↔unvoiced, inhalation↔exhalation, no new pitch class). Sections = game rounds/motif states (entry→loop→ornament→tempo push→collapse). Rules: hocket interlock (≤1 onset/subdivision, rest-of-V0 = note-of-V1), breath-continuity (no silence, every slot filled), motif invariance per round, complement = leader gap-mask fill, voiced/unvoiced timbre mask, escalation arc, breath-limit termination (laugh/stop), pitch-as-timbre (contour only, no scale/harmony), nature-imitative vocabulary | Tanya Tagaq (Animism, Polaris 2014), Qaunak Mikkigak, Kathleen Ivaluarjuk Merritt, Alacie Tullaugaq & Lucy Amarualik, Tudjaat, The Jerry Cans (Nancy Mike), Iva & Angu (Katajjausiit, Juno 2023), Caroline & Shina Novalinga (TikTok); Ainu rekuhkara (Hokkaidō) analog | ✅ Documented |
```

## 7. Verification

- `HC-033` present in detail file `human_method_HC-033_inuit-katajjaq-throat-singing-duet.md` ✓
- `HC-033` present in `human_methods_db.md` framework table ✓
- Highest ID = **HC-033**; next free ID = **HC-034** ✓
- No duplicate HC-033 in table (only the new row) ✓

## 8. Quirks / pitfalls

- **Not "music" to the practitioners** — a *game*; the competition mechanic (breath-limit, laugh-break elimination) *is* the form. Any encoding must model the round/elimination structure, not just the notes.
- **Continuous stream, zero rests** — a naive note-on/note-off model with silences will wrongly produce gaps. Must model the hocket complement + breath-continuity so the composite is unbroken.
- **Pitch is timbre** — there is no scale/harmony to quantize against; pitch mapping must be contour/formant-based, or the "melody" will read as wrong notes.
- **Distinct from HC-027** (Tuvan solo overtone — one body, harmonic-series melody over a fixed drone) — katajjaq is *two bodies, interlocked breath patterns, no drone*.
- **Unvoiced sounds** (consonant noise) have no MIDI pitch; encode as low-velocity/percussive/noise events or timbre flags rather than pitched notes.
