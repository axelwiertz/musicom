# HC-029 — Shakuhachi Honkyoku Breath-Phrase & Ma Craft (Ichi-On Jōbutsu)

**Layer:** human → `concrete` (target when implemented) — human-craft knowledge; realized through the UnitMatrix into playable voices/events.

**Tradition / Culture:** Japanese Zen Buddhist — the shakuhachi (end-blown bamboo flute) honkyoku ("original pieces") repertoire of the Fuke-shū *komusō* ("monks of emptiness / nothingness"), Edo period (1603–1868) to present; preserved today in the Kinko Ryū, Dokyoku, and Meian schools. The shakuhachi honkyoku is recognized within Japan's Important Intangible Cultural Properties (Kinko Ryū, Tozan Ryū). The craft is *sui-zen* — "blowing meditation" — music made as seated spiritual practice, not performance.

**Method ID:** HC-029

---

## 1. Description

How a shakuhachi player actually composes/realizes a honkyoku: not as a sequence
of notes in a meter, but as a chain of **breath-phrases** — each one a single
exhalation shaped from a controlled attack through a sustained, vibrating body to
a deliberate release — separated by **ma** (composed silence). The core doctrine
is **ichi-on jōbutsu** (一音成仏, "one sound becoming Buddha"): *a single tone,
fully shaped, is a complete musical/spiritual act* — not a means to a melody but
an end in itself. Pitch is fluid (bent by head-motion: **meri** = flatten by
lowering the head over the blowing edge, **kari** = raise), rhythm is breath-
relative (no barlines, no time signature, durations felt not metered), and silence
is a positive, composed element rather than the absence of sound.

The craft is four coupled sub-skills a human masters and recombines:
**(a)** tone-envelope shaping (each single tone: attack → body/vibrato → decay),
**(b)** meri/kari pitch-bending (microtonal shading of the 5-hole pentatonic scale),
**(c)** ma placement (where and how long each silence is, relative to the phrase
it follows), **(d)** arch-form assembly (ro → kan → ro, open and close on the
fundamental, let the breath decay into silence).

## 2. Craft Steps (how the human does it, step by step)

1. **Settle the instrument & the breath.** The shakuhachi has 5 finger holes
   (open = D–F–G–A–C, the *in*-scale; fundamental = **ro**, low D). Sit in seiza,
   empty the body, breathe from the diaphragm. The unit of music is *one full
   exhalation* — a phrase is as long as one breath, no longer.
2. **Begin from ro.** The piece opens on the fundamental ro — a long, unadorned,
   slowly-vibrating tone. This is not an anacrusis; it *is* the music. The player
   holds it, listens to its overtones, and lets it set the room's resonance.
3. **Shape each tone as a complete object.** Every tone gets a 3-phase envelope:
   **sao** (attack — a breathy or clean onset) → **oto** (sustained body, with
   *yuri* finger/head vibrato and *ne-iro* tone-colour) → **nayashi/decay** (a
   dropping release). No two tones are meant to be identical — each is a fresh
   meditation, not a reproduced pitch.
4. **Bend pitches with meri/kari.** By lowering or raising the head relative to
   the blowing edge (or half-holing), the player flattens/sharps a pitch by a
   quarter- to whole-tone — *meri* passages descend darkly, *kari* brightens.
   The same fingering yields many pitches; the pitch lives in the *embouchure*,
   not the holes.
5. **Insert ma — compose the silence.** Between phrases the player leaves *ma*:
   a silence whose length is felt in relation to the breath that just decayed
   (long after a long tone, short after a clipped one). Ma is never metronomic;
   it is the negative space that gives each phrase its weight and lets the last
   tone finish ringing in the room (and in the ear).
6. **Ornament with breath/finger techniques.** *atari* (a sharp breath-accent that
   re-articulates a held tone), *suri* (a slide between fingerings), *yuri*
   (vibrato), *muraiki* (a violent "explosive" breath for dynamic peaks),
   *tama-ne* ("round tones" = soft, perfectly centered attacks). These are
   textural events, not new pitches.
7. **Assemble the breath-arch.** The piece rises from ro through the mid register
   to **kan** (the upper octave, the emotional peak), then descends back to ro,
   closing on a final long ro that is allowed to fade to silence. The arch mirrors
   a meditation session: settle → rise → peak → return → dissolve.
8. **Never perform — practice.** Tempo, duration, and phrasing are free and change
   every time. A piece that lasts 5 minutes in one sitting may last 20 in another;
   the *form* (the breath-phrase chain and the arch) is invariant, the *clock* is
   not. The goal is the blowing itself (sui-zen), not a fixed product.

## 3. Practitioner Examples

- **Kurosawa Kinko I** (1710–1771) — founder of the Kinko Ryū school; compiled
  and systematized the 36-piece honkyoku canon used by the komusō; his notation
  (kinko notation) is breath-mark-based, with no bar lines and no absolute meter.
- **Watazumi Doso Roshi** (1911–1992) — Dokyoku school; played *hōchiku*
  (uncut, un-tempered, thick-root bamboo) to escape equal temperament entirely;
  taught **Yokoyama Katsuya**; embodied the "one sound, total commitment" ideal.
- **Yokoyama Katsuya** (1934–2010) — Dai Shihan of the Kinko school; his recording
  of **"Shika no Tōne"** (Distant Calls of Deer, mid-18th-c.) is the reference
  rendition: two-note deer-call motifs (C–A), each phrase a single breath, ma
  echoing across mountain distance.
- **Aoki Reibo II** — Kinko Ryū, designated Living National Treasure (Ningen
  Kokuhō); canonical Edo-era honkyoku.
- **Riley Lee** — first non-Japanese Grand Master (dai shihan) of shakuhachi;
  taught honkyoku breath-phrase craft internationally.
- **Ronnie Nyogetsu Seldin** — Ki-Sui-An line; brought Kinko Ryū honkyoku to the
  West, stressing ma as the "negative space" discipline.
- **Canonical pieces (Koden Sankyoku, the three classical pieces):**
  **"Kyorei"** (Empty Bell), **"Mukaiji"** (Misty Sea), **"Koku"** (Empty Sky) —
  plus **"Reibo"** (Yearning for the Bell), **"Shika no Tōne"**, **"Sōkkan"**
  (Hi-Fu-Mi Hachi-Gaeshi). Titles themselves name the aesthetic: emptiness, mist,
  bell, sky — sound dissolving into silence.

## 4. UnitMatrix Integration

### Voices
- **Voice 0 = ro spine** (fundamental / drone reference). The piece anchors on ro
  (low D), opens and closes on it; a breath-gated invariant reference tone.
  `PITCH` anchor = the *in*-scale pentatonic {D, F, G, A, C} + meri/kari bends.
- **Voice 1 = breath-phrase melodic line** (the shaped tones). Each event is a
  full tone-envelope (attack/sustain/vibrato/decay), pitched on the pentatonic set
  and bent by meri/kari (±quarter to ±whole tone around the fingered pitch).
- **Voice 2 = ma / silence layer** (the composed gaps). Rest *events* (not empty
  space) whose durations are felt relative to the preceding phrase; carries the
  structure.
- **Voice 3 = ornament / ne-iro layer** (atari, suri, yuri, muraiki, tama-ne).
  Textural breath/finger events — re-articulations, slides, vibrato, accents — no
  new pitch classes, only envelope and dynamic.

### Sections
- **Breath-phrase = one section.** The UnitMatrix section grid is repurposed: a
  "section" is a single exhalation's phrase, not a bar/loop block. Macro-form is
  the **breath-arch**: Ro (settle) → mid register (rise) → Kan upper-octave
  (peak) → mid (return) → Ro (final, fading to silence).

### Rules (what would encode it)
- **Breath-phrase segmentation**: phrase length bounded by breath capacity
  (a duration envelope, not a fixed bar count); no phrase exceeds one exhalation.
- **Ma-is-composed**: rests are events with felt duration ∝ preceding phrase
  (long-after-long, short-after-short); never metronomic, never "leftover time".
- **Meri/kari pitch set**: pitch ∈ pentatonic {D,F,G,A,C} with microtonal bend
  offset on selected tones (descending meri flatten, kari brighten); the bend is
  *part of* the pitch, not decoration.
- **Tone-envelope rule**: every Voice-1 event carries attack (sao) → sustain
  (oto + yuri vibrato) → decay (nayashi); no "flat" MIDI note-on/off.
- **Ro-anchoring**: open and close on ro (fundamental); final ro fades to silence
  (decay → ma → end, never a hard cut).
- **Arch form**: register/density rise monotonically to kan peak then fall back
  to ro (settle→rise→peak→return→dissolve).
- **Free tempo**: no metronome grid — relative durations, tempo variable across
  sittings; the form (phrase chain + arch) is invariant, the clock is not.
- **Ichi-on-jōbutsu**: every tone is complete/meditative in itself; no
  "wrong note" or error-correction logic — a tone's quality (envelope/shading) is
  the composition, not its position in a scale run.

### Provenance
- Layer: `concrete` (target). Human-craft knowledge → realizes material via UnitMatrix.
- Primary elements: STRUCTURE, TEXTURE, RHYTHM, PITCH.
- Not algorithmic generation — NOT routed by SCALE selector as a generator; this is
  the *knowledge* of how a shakuhachi player assembles material through breath and
  silence, available as rules for a future concrete-layer method.

### Engine-fit quirks / pitfalls (recorded for the implementer)
1. **Free-tempo vs fixed grid.** The UnitMatrix assumes `beats_per_bar` and
   `ticks_per_beat` (a metrical clock). Honkyoku has *no* meter and no bars — a
   concrete implementation needs either a "free-rhythm section" type (relative
   tick durations, breath-length envelopes instead of bar counts) or a very high
   resolution grid treated as unaccented. The `create_section(... bars=N)` model
   maps awkwardly to breath-phrases of unequal length.
2. **Microtonality vs 12-TET MIDI.** Meri/kari bends (±quarter to ±whole tone)
   are the soul of the sound; plain MIDI note numbers quantize them away. Needs
   pitch-bend events (or the engine's microtonal table if present) attached to
   Voice-1 events, with the bend *inside* the tone envelope (not a gliss between
   notes).
3. **Silence-as-event.** The engine must treat rests as first-class events (like
   the HC-020 "break silence gate") rather than empty padding — ma is the
   structural spine, and zero-drift track-length padding must NOT fill ma with
   audible content.
4. **No "wrong note" semantics.** Most concrete methods validate against a scale;
   honkyoku's ichi-on-jōbutsu principle means validation is *envelope/breath*
   based (each tone has attack/sustain/decay, opens/closes on ro), not
   note-legality based.
