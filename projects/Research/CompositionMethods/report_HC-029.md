# Report — HC-029 Shakuhachi Honkyoku Breath-Phrase & Ma Craft (Ichi-On Jōbutsu)

**Job:** daily-human-composition-research
**Date:** 2026-09-07
**Method ID:** HC-029
**Layer:** human → `concrete` (target when implemented)
**Tradition / Culture:** Japanese Zen Buddhist — shakuhachi honkyoku ("original pieces") of the Fuke-shū *komusō* monks (Edo period 1603–1868 → present; Kinko Ryū / Dokyoku / Meian schools); *sui-zen* ("blowing meditation").

---

## 1. Method Name

Shakuhachi Honkyoku Breath-Phrase & Ma Craft (Ichi-On Jōbutsu — "one sound becomes Buddha").

## 2. Tradition

Japanese Zen Buddhist — the shakuhachi (end-blown bamboo flute) honkyoku
repertoire. Originated with the Fuke-shū sect of mendicant *komusō* ("monks of
emptiness") who used the flute as a meditation instrument during the Edo period;
the pieces were transmitted orally/breath-marks in the Kinko Ryū (Kurosawa Kinko
I, 36-piece canon), Dokyoku (Watazumi Doso Roshi), and Meian schools. The craft is
sui-zen — music as seated spiritual practice, not performance. Honkyoku is
designated Important Intangible Cultural Property (Kinko Ryū / Tozan Ryū).

## 3. Layer

`concrete` (target). Human-craft knowledge — realizes material through the
UnitMatrix into playable voices/events. Not a generator; not routed by the SCALE
selector. Target layer stated per job contract.

## 4. Craft Procedure (how the human does it, step by step)

1. **Settle instrument & breath.** 5 finger holes (open = D–F–G–A–C, the *in*
   scale; fundamental = **ro**, low D). Sit in seiza, breathe from diaphragm. The
   unit of music is *one full exhalation* — a phrase is as long as one breath.
2. **Begin from ro.** Open on the fundamental ro, a long unadorned vibrating tone.
   Not an anacrusis — it *is* the music; the player holds it and listens to its
   overtones.
3. **Shape each tone as a complete object.** 3-phase envelope: **sao** (attack)
   → **oto** (sustained body + *yuri* vibrato + *ne-iro* tone-colour) →
   **nayashi/decay** (dropping release). No two tones identical — each is a fresh
   meditation, not a reproduced pitch.
4. **Bend pitches meri/kari.** Lower/raise the head over the blowing edge (or
   half-hole) to flatten/sharpen by a quarter- to whole-tone. Same fingering =
   many pitches; pitch lives in the embouchure, not the holes.
5. **Insert ma — compose the silence.** Between phrases, leave *ma*: felt length
   relative to the breath that just decayed (long-after-long, short-after-short).
   Never metronomic; the negative space gives each phrase weight.
6. **Ornament with breath/finger techniques.** *atari* (breath-accent
   re-articulation), *suri* (slide), *yuri* (vibrato), *muraiki* (explosive
   dynamic peak), *tama-ne* ("round tones" = soft centered attacks). Textural
   events, not new pitches.
7. **Assemble the breath-arch.** Rise from ro through the mid register to **kan**
   (upper octave, emotional peak), then descend back to ro, closing on a final
   long ro that fades to silence. Mirrors a meditation session: settle → rise →
   peak → return → dissolve.
8. **Practice, never perform.** Tempo/duration free and variable every sitting;
   the *form* (phrase chain + arch) is invariant, the *clock* is not.

## 5. Practitioner Examples

- **Kurosawa Kinko I** (1710–1771) — Kinko Ryū founder; compiled the 36-piece
  komusō canon; breath-mark notation, no barlines, no absolute meter.
- **Watazumi Doso Roshi** (1911–1992) — Dokyoku school; played *hōchiku* (uncut,
  un-tempered root bamboo) to escape equal temperament; taught Yokoyama Katsuya.
- **Yokoyama Katsuya** (1934–2010) — Kinko Dai Shihan; reference recording of
  **"Shika no Tōne"** (Distant Calls of Deer): two-note deer-call motifs (C–A),
  each phrase one breath, ma echoing across mountain distance.
- **Aoki Reibo II** — Kinko Ryū, Living National Treasure (Ningen Kokuhō).
- **Riley Lee** — first non-Japanese Grand Master (dai shihan) of shakuhachi.
- **Ronnie Nyogetsu Seldin** — Ki-Sui-An line; stressed ma as the
  "negative-space" discipline.
- **Canonical pieces (Koden Sankyoku):** "Kyorei" (Empty Bell), "Mukaiji" (Misty
  Sea), "Koku" (Empty Sky); plus "Reibo", "Shika no Tōne", "Sōkkan".

## 6. UnitMatrix Mapping (Voices & Sections)

### Voices
- **Voice 0 = ro spine** — fundamental/drone reference (low D). Opens and closes
  the piece; invariant reference tone. `PITCH` anchor = in-scale pentatonic
  {D,F,G,A,C} + meri/kari bends.
- **Voice 1 = breath-phrase melodic line** — shaped tones; each event a full
  tone-envelope (attack/sustain/vibrato/decay) on the pentatonic set, bent
  meri/kari (±quarter to ±whole tone).
- **Voice 2 = ma / silence layer** — composed gaps; rest *events* (not empty
  space) with felt duration ∝ preceding phrase; carries the structure.
- **Voice 3 = ornament / ne-iro layer** — atari, suri, yuri, muraiki, tama-ne;
  textural events, no new pitch classes.

### Sections
- **Breath-phrase = one section.** Section grid repurposed: a "section" is one
  exhalation's phrase, not a bar/loop block. Macro-form = **breath-arch**:
  Ro (settle) → mid (rise) → Kan (peak) → mid (return) → Ro (final, fading).

### Rules (what would encode it)
- **Breath-phrase segmentation**: phrase length ≤ one exhalation (duration
  envelope, not fixed bar count).
- **Ma-is-composed**: rests are events, felt duration ∝ preceding phrase; never
  metronomic, never leftover time.
- **Meri/kari pitch set**: pitch ∈ {D,F,G,A,C} + microtonal bend offset on
  selected tones (descending meri, brightening kari); bend is *part of* the pitch.
- **Tone-envelope rule**: every Voice-1 event carries sao → oto(+yuri) → nayashi;
  no flat note-on/off.
- **Ro-anchoring**: open/close on ro; final ro fades to silence (decay → ma →
  end), never a hard cut.
- **Arch form**: register/density rise monotonically to kan peak, then fall to ro.
- **Free tempo**: no metronome grid — relative durations; form invariant, clock
  variable.
- **Ichi-on-jōbutsu**: every tone complete/meditative in itself; no
  "wrong-note" logic — a tone's envelope/shading is the composition.

## 7. Table Row Added

Appended to the 'Human Composition Methods Framework' table in
`human_methods_db.md` (kept aligned with the 9-column schema):

| HC-029 | human (→concrete) | Shakuhachi Honkyoku Breath-Phrase & Ma Craft (Ichi-On Jōbutsu) | Japanese Zen Buddhist — shakuhachi honkyoku ("original pieces") of the Fuke-shū komusō monks (Edo period → present; Kinko Ryū / Dokyoku / Meian schools); sui-zen "blowing meditation" | STRUCTURE, TEXTURE, RHYTHM, PITCH | ... | Voice 0 = ro spine ... Voice 1 = breath-phrase ... Voice 2 = ma/silence ... Voice 3 = ornament/ne-iro ... | Kurosawa Kinko I ... Yokoyama Katsuya ... | ✅ Documented |

(Full aligned row in the DB; full text in the detail file.)

## 8. Next Free ID

**HC-030** (highest existing = HC-029, this job's new ID; next = max+1).

## 9. Quirks / Pitfalls (engine-fit notes for the implementer)

1. **Free-tempo vs fixed grid.** UnitMatrix assumes `beats_per_bar` +
   `ticks_per_beat` (a metrical clock). Honkyoku has no meter/bars — needs a
   "free-rhythm section" type (relative tick durations, breath-length envelopes
   instead of bar counts) or a very-high-res unaccented grid. `create_section(...,
   bars=N)` maps awkwardly to unequal breath-phrases.
2. **Microtonality vs 12-TET MIDI.** Meri/kari bends are the soul of the sound;
   plain MIDI note numbers quantize them away. Needs pitch-bend events (or the
   engine's microtonal table) attached to Voice-1 events, bend *inside* the tone
   envelope (not a gliss between notes).
3. **Silence-as-event.** Rests must be first-class events (like HC-020's "break
   silence gate"), not empty padding — ma is the structural spine; zero-drift
   track-length padding must NOT fill ma with audible content.
4. **No "wrong note" semantics.** Most concrete methods validate against a scale;
   ichi-on-jōbutsu means validation is envelope/breath-based (each tone has
   attack/sustain/decay, opens/closes on ro), not note-legality based.

## 10. Files

- Detail: `/opt/data/projects/Research/CompositionMethods/human_method_HC-029_honkyoku-breath-phrase-ma.md`
- DB: `/opt/data/projects/Research/CompositionMethods/human_methods_db.md`
- Report (this file): `/opt/data/projects/Research/CompositionMethods/report_HC-029.md`
