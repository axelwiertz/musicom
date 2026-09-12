# HC-033 — Inuit Katajjaq Throat-Singing Duet (Breath-Game Hocket)

**Method ID:** HC-033
**Layer:** concrete (target when implemented) — human-craft knowledge; realizes material through the UnitMatrix
**Tradition / Culture:** Inuit (Arctic North America — Nunavut, Nunavik/Québec, Greenland, Alaska) — katajjaq / katajjaniq, an Indigenous vocal *game* practiced by women, centuries-old oral tradition. UNESCO-recognized; distinct from Tuvan/Mongolian solo overtone singing (HC-027): katajjaq is a **duet** of interlocked voiced/unvoiced breath patterns, not a one-body harmonic-series melody.
**Primary Elements:** RHYTHM, TEXTURE, PITCH, STRUCTURE
**Status:** ✅ Documented

---

## What it is

Katajjaq (Inuktitut: ᑲᑕᔾᔭᖅ) is a two-person vocal contest in which women face each other at close range — historically lips nearly touching so one singer's mouth cavity serves as the other's resonator — and trade interlocked rhythmic patterns. It is understood in Inuit culture as a *breathing game* (entertainment while men were away hunting), not "music" in the Western sense. The sound is a panting, rhythmic, harmonically-stable stream built from voiced AND unvoiced sounds produced on both **inhalation and exhalation**. One singer leads a short motif repeated with silent gaps; the other fills each gap with a complementary pattern. The game ends when one singer runs out of breath, laughs, or loses the pace — the winner is whoever can outlast the most opponents.

## Craft procedure (how a human does it, step by step)

1. **Pair up, face to face.** Two singers stand close, arms linked, often rocking/shuffling foot-to-foot in time. Historically lips nearly touched — the partner's mouth cavity became a shared resonator (acoustic coupling).
2. **Leader sets a short rhythmic motif.** One singer states a brief pattern (a repeated vowel-consonant syllable cell), repeating it with **brief silent gaps** between iterations.
3. **Responder fills the gaps.** The second singer inserts a complementary rhythmic pattern into the leader's silences — a strict **hocket**: the rest of one voice is exactly where the other speaks. The composite is a continuous, unbroken stream that neither voice alone produces.
4. **Use voiced + unvoiced sounds, on both breath directions.** The vocabulary is breath-syllables: voiced vowels and unvoiced consonants, produced on inhalation *and* exhalation, so the flow never stops and pitch is largely timbral/formant-based (low chest sounds vs. high thin sounds), imitating wind, water, animal calls, and everyday sounds.
5. **Loop and ornament.** Each round holds a stable motif while surface ornamentation (vowel-colour shifts, subtle phase displacement, register inflections) varies the texture. Motifs imitate nature; the repertoire is passed down orally.
6. **Contest to exhaustion.** The singers push tempo and density. The first to run out of breath, break into laughter, or fail to keep the other's pace is "eliminated." A full round lasts 1–3 minutes. The winner is the one who beats the largest number of people in succession.
7. **Elders coach precision.** A senior woman corrects children's sloppy intonation of contours, poorly meshed phase displacements, and vague rhythms — exactly like a Western vocal coach — transmitting the craft generation to generation.

## Real practitioner examples

- **Tanya Tagaq** — the genre's most famous solo practitioner; extends katajjaq breath techniques into contemporary art music (*Animism*, Polaris Music Prize 2014); blends with rock/electronica.
- **Qaunak Mikkigak**, **Kathleen Ivaluarjuk Merritt**, **Alacie Tullaugaq & Lucy Amarualik** — traditional katajjaq duettists (Nunavut/Nunavik).
- **Tudjaat**, **The Jerry Cans** (Nancy Mike), **Quantum Tangle**, **Silla + Rise** — fusion groups weaving katajjaq into pop/folk/rock.
- **Iva & Angu** (album *Katajjausiit*, Juno-nominated 2023), **Caroline & Shina Novalinga** (TikTok popularizers).
- **Ainu rekuhkara** (Hokkaidō, Japan) — a documented analogous duet breath-hocket form, confirming the pattern's cross-cultural recurrence.

## UnitMatrix integration (Musicom engine)

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
- **Complement generation**: responder pattern = derived from leader's gap mask (shifted / filled) — a deterministic gap-fill, like kotekan interlock (HC-002) but voiced/breath-based rather than pitch-based.
- **Voiced/unvoiced + inhalation/exhalation timbre mask**: alternation drives TEXTURE without changing pitch class (pitch is formant-relative, low↔high register).
- **Game/escalation arc**: tempo and density rise monotonically toward the round's end; termination = breath-limit gate (one voice drops out → laugh/stop event).
- **Pitch minimality**: no functional harmony, no scale — pitch is timbral/contour (contour accuracy is what the elder corrects). Melodic contour imitates nature/wind/animal vocabulary.
- **Contest closure**: section ends on first "break" (elimination) event, not a cadence.

### Fill/flow note (per the sparse-vs-flow rule)

Katajjaq is the opposite of a sparse staccato method: the hocket + breath-continuity invariant produces a **fully continuous** stream by construction. It is therefore a candidate *continuous-fill* companion to sparse rhythmic generators (011 Euclidean / 032 Isorhythmic) rather than a method needing a fill layer added to it.

### Element mapping

- **RHYTHM** — hocket interlock, tempo push, breath-cycle pulsation (primary).
- **TEXTURE** — voiced/unvoiced + inhalant/exhalant alternation, close-mic acoustic coupling (primary).
- **PITCH** — formant/timbral contour only, nature-imitative vocabulary (secondary).
- **STRUCTURE** — single escalating game-round arc (secondary).
- **HARMONY** — absent (monophonic hocket; vertical sonorities incidental).

## Quirks / pitfalls

- **Not "music" to the practitioners** — a *game*; the competition mechanic (breath-limit, laugh-break elimination) is the form, not decoration. Any encoding must model the round/elimination structure, not just the notes.
- **Continuous stream, zero rests** — a naive event model (note-on/note-off with silences) will wrongly produce gaps. Must model the hocket complement + breath-continuity so the composite is unbroken.
- **Pitch is timbre** — there is no scale/harmony to quantize against; pitch mapping must be contour/formant-based, or the "melody" will read as wrong notes.
- **Distinct from HC-027** (Tuvan solo overtone — one body, harmonic-series melody over a fixed drone) — do not conflate: katajjaq is *two bodies, interlocked breath patterns, no drone*.
- **Unvoiced sounds** (consonant noise) have no MIDI pitch; encode as low-velocity/percussive/noise events or timbre flags rather than pitched notes.
