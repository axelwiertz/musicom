# Report HC-053: Bossa Nova Guitar Beat & Vocal Fraseado Craft (Batida + Tempo Rubato)

**Layer:** human (→concrete)  
**Next Free HC-ID:** HC-054  
**Documentation:** `human_method_HC-053_bossa-nova-batida-fraseado.md`

---

## Method Overview

- **Method Name:** Bossa Nova Guitar Beat & Vocal Fraseado Craft (Batida + Tempo Rubato)
- **Tradition/Culture:** Brazilian Bossa Nova — Rio de Janeiro (Zona Sul), 1958–present. Pioneered by João Gilberto (guitar voice), Antônio Carlos "Tom" Jobim (composer/pianist), Vinicius de Moraes (lyricist).
- **Primary Elements (Musical Framework):** RHYTHM, HARMONY, PITCH, TEXTURE, STRUCTURE
- **Layer:** concrete (implementable via UnitMatrix)

---

## The Human Craft Procedure

Bossa Nova is not improvised in the jazz sense. It is a **composition and interpretation** method with strict self-imposed constraints that the human artist uses to create a seductive, quiet, anti-samba intimacy. The method decomposes into 6 phases:

### Phase 1: Fix the Batida (Right-Hand Guitar Foundation)

1. **Thumb = surdo**: Right-hand thumb plays a bass note on **every quarter-note beat**. Never misses a pulse, never rests, never plays upbeats. This is the invariant heartbeat.
2. **Three fingers = partido alto clave**: Index, middle, and ring fingers (classical guitar position, little finger unused) pluck a 4-note block chord on syncopated offbeats. The pattern is derived from the samba tamborim clave (partido alto), with two halves: syncopated (beats 1 and 4 feel) and unsyncopated (beats 2 and 3 feel).
3. **Never strum**: All chord notes are plucked simultaneously (block chord). No arpeggiation, no strumming.
4. **Channel chamada**: Optionally begin a song by repeating the opening chord as even quavers — a "waiting for the singer" holding pattern — before sliding into the rhythmic pattern.
5. **Variation pool**: The three-finger pattern flows between several canonical variants selected instinctively. At slow tempos: straight crotchet chords or quaver-triplet breaks. At chord-change-every-beat passages: simultaneous bass+chord.

### Phase 2: Set the Harmonic Language

1. **Four-note chords only**: Never a perfect major or minor triad. Every chord includes a 6th or 7th. Never play a triad with an added 2nd.
2. **Invert for stepwise bass**: Chords are in inversion (3rd, 5th, or 7th in the bass) so the bass moves stepwise rather than by leap. Roots are implied, not always present. Example: Dm7→G7→Cmaj7 becomes Fmaj7/A→Fdim7/Ab→Em7/G (stepwise A→Ab→G).
3. **Functional jazz harmony**: Extended chords (maj7, m7, m9, 6/9, G13, F#m7b5, altered dominants). Tritone substitution (Dm7–Db7–Cmaj7). Chromatic mediant movement. Center on tonic major/minor with Dorian/Aeolian inflections.
4. **Canonical progressions**: ii–V–I (Dm7–G7–Cmaj7), ii–V–I with tritone sub, parallel descending chord forms.

### Phase 3: Compose or Arrange the Melody

1. **Melody is sacred**: Never change the composed melody pitches. João Gilberto never altered a melody note.
2. **Set song form**: Standard 32-bar AABA (Tin Pan Alley) or 16-bar AB.
3. **Set harmonic rhythm independently**: May double or halve the chord-change speed relative to the original. May momentarily add a beat (2/4→3/4) to accommodate a phrase.
4. **Set key**: Typically major (bright/nostalgic) or minor (melancholic).

### Phase 4: Execute Vocal Fraseado — The Core Artistic Method

This is the unique craft contribution. The vocal part uses **tempo rubato in the older Mozart/Chopin sense**: free melody floating over a **steady** accompaniment, deliberately out of sync.

1. **Strip all ornamentation**: No vibrato, portamento (slides), melismata, dynamic swells, register changes. Voice is spoken-quality, soft, intimate.
2. **Float over the beat**: The singer places melodic phrases ahead of or behind the guitar's steady beat by variable amounts — sometimes early, sometimes late, sometimes dramatically displaced by a half-beat or whole beat.
3. **Create phrase displacement**: Move entire melodic phrases backward or forward relative to their natural barline position. Example: a phrase that would naturally start on beat 1 is shifted to start on beat 4.
4. **Vary on each repeat**: Each A-section repeat is phrased uniquely. "Fazendo sempre a mesma coisa que nunca é a mesma" — always doing the same thing that is never the same (Caetano Veloso).
5. **Alternate in/out**: Some phrases sit in the rhythmic pocket; others float freely. Often a whole verse is "out" (tense) and the chorus lands "on the money" (release).
6. **Speech-rhythm inflection**: The melody follows Brazilian Portuguese natural syncopation. Pronunciation is eccentric, treated as micro-sound design (nasal vowels, fuzzy consonants, elision).

### Phase 5: Percussion (Minimalist)

1. **Pure method**: Voice + guitar only (solo concerts).
2. **Optional addition**: Hi-hat only (as Sonny Carr on the 1973 "white album" — no bass drum, no snare, no cymbals except hi-hat on offbeats).
3. **Low dynamic always**: Everything quiet.

### Phase 6: Shape the Macro-Form

1. **Play AABA (32-bar) or AB (16-bar) with repeats**.
2. **Tempo choice**: Speed up slow songs, slow down fast ones. Never extreme tempos.
3. **Repeat as needed**: A song may last 6+ minutes with multiple unique phrasing rounds.
4. **Close**: Final chord held with optional 4-note extension.

---

## Practitioner Examples

| Practitioner | Role | Key Works |
|---|---|---|
| **João Gilberto** | Inventor of the method (guitar + voice) | *Chega de Saudade* (1958 debut single, the birth document), *O Amor, O Sorriso e a Flor* (1960), *João Voz e Violão* (2000 — quintessential solo demonstration), *Live in Montreux*, *In Tokyo* (2003) |
| **Antônio Carlos Jobim** | Composer (repertoire for the method) | *Garota de Ipanema* (The Girl from Ipanema), *Desafinado*, *Wave*, *Dindi*, *Samba de Uma Nota Só*, *Águas de Março* (Waters of March), *Chega de Saudade* |
| **Vinicius de Moraes** | Lyricist (all canonical bossa lyrics) | *Chega de Saudade*, *Garota de Ipanema*, all Jobim collaborations |
| **Stan Getz** | Saxophonist (most famous collaborator) | *Getz/Gilberto* (1963 Verve — one of best-selling jazz records) |
| **Astrud Gilberto** | Vocalist (applied the fraseado internationally) | "The Girl from Ipanema" on *Getz/Gilberto* |
| **Sonny Carr** | Drummer (hi-hat only on 1973 "white album") | *João Gilberto* (1973 Polydor) |

---

## UnitMatrix Mapping (Musicom Engine)

### Voices

| Voice | Name | Role | Invariant Rule |
|---|---|---|---|
| V0 | **Surdo Thumb Bass** | Steady crotchet bass-note pulse; invariant foundation, never rests | **Beat-invariance**: fires an event on every beat |
| V1 | **Partido Alto Chord Clave** | Syncopated 4-note block chord clave on offbeats; fixed pattern set per song | **Hand-partition interlock**: no simultaneous onset with V0 |
| V2 | **Vocal Fraseado Melody** | Composed melody with free tempo-rubato onset displacement; pitches frozen | **Phrase-displacement freedom**: onsets variable ±1–2 subdivisions from grid; **pitch-invariant**: never changes melody |
| V3 | **Optional Hi-Hat** | Minimal open hi-hat offbeat pulse | Optional, invariant if present |
| V4 | **Harmonic Grid** | Underlying chord progression (4-note extended chords) | Frozen per composition; voices via inversion |

### Sections (AABA 32-bar standard)

| Section | Bars | Key/Harmony | Function |
|---|---|---|---|
| S0 Intro (chamada) | 0–2 bars (optional) | Tonic, repeated quaver chord | Establishing pulse |
| S1 A1 | 8 bars | Tonic | Main melody statement (first fraseado) |
| S2 A2 | 8 bars | Tonic | A repeat (new fraseado) |
| S3 B (Bridge) | 8 bars | Subdominant or relative minor | Contrast |
| S4 A3 | 8 bars | Tonic | Return (final fraseado) |
| S5 Coda (optional) | 2–8 bars | Tonic held chord | Closure |

### Rule Set for UnitMatrix Encoding

1. **Beat-invariance** (V0): V0 must fire a bass event on every crotchet beat. Zero rests allowed. This is the core spine.
2. **Hand-partition interlock** (V0+V1): V0 (bass) and V1 (chord block) must never have simultaneous onsets. Bass occupies the beat tick; chord block occupies the offbeat tick(s). They interlock.
3. **4-note chord rule** (V1): Each V1 event must contain exactly 4 pitch classes. No perfect triads allowed. Every chord must include a 6th or 7th. No added 2nd. The pitches are drawn from extended jazz harmony vocabulary (maj7, m7, 6/9, m9, altered dominant, etc.).
4. **Inversion filter** (V0 pitch content): The bass note (V0 pitch) should move stepwise (M2, m2, or same). Root-position jumps > P5 are rejected unless required by key change. Roots are implied, not mandatory.
5. **Phrase-displacement freedom** (V2): V2's onset ticks may be shifted by ±1–2 sixteenth-note subdivisions from the strict grid position. This is the core artistic freedom. Pitches remain identical to the composed melody at all times.
6. **Anti-ornament constraint** (V2): V2 must contain exactly the melody note sequence. No grace notes, vibrato simulation, slides between pitches, or melismata.
7. **Melody-invariant** (V2): V2 pitch sequence never changes across sections or repeats. All variation is in timing only.
8. **Volume invariance** (all voices): All voices maintain consistent velocity (pp–mp range, no >5 dynamic steps variation).
9. **Form lock**: Sections follow A→A→B→A order with no section permutation.
10. **Zero-drift padding**: V0 and V1 always terminate simultaneously at section boundaries. V2 may end slightly early/late but must have a rest event before the next section's first V0 beat.

---

## Table Row Added to DB

```
| HC-053 | human (→concrete) | Bossa Nova Guitar Beat & Vocal Fraseado Craft (Batida + Tempo Rubato) | Brazilian Bossa Nova — Rio de Janeiro (Zona Sul), 1958–present; João Gilberto, Tom Jobim, Vinicius de Moraes | RHYTHM, HARMONY, PITCH, TEXTURE, STRUCTURE | Fix batida: right-hand thumb plays steady crotchet bass pulse (surdo, invariant, never rests) + three fingers pluck 4-note block chords in partido-alto clave syncopation → set 4-note-only harmony (always 6th/7th coloration, never plain triads, never added 2nds) → invert chords for stepwise bass voice-leading (roots implied, not always present) → fix composed melody (never alter pitches) → execute vocal fraseado: tempo rubato (free melody floating over steady beat, phrase displacement ahead/behind by up to a whole beat) → vary phrasing uniquely on each repeat → preserve no-ornament rule (no vibrato, portamento, melismata, dynamic swells) → keep low volume, voice and guitar in proportional balance → add minimal percussion (hi-hat only, optional) → shape AABA/AB song form | Voice 0 = surdo thumb bass (invariant crotchet pulse on every beat, never rests). Voice 1 = partido alto chord clave (syncopated 4-note block chords on offbeats, clave-driven pattern set). Voice 2 = vocal fraseado melody (composed pitches invariant; onsets free-variable via tempo rubato displacement). Voice 3 = optional hi-hat offbeat (minimal pulse layer, 1973 album style). Sections = S0 Intro Chamada (optional, 0–2 bars) → S1 A (8 bars, tonic, main melody statement) → S2 A (8 bars, repeat with new fraseado) → S3 B (8 bars, bridge, subdominant/relative-minor contrast) → S4 A (8 bars, return to tonic) → S5 Coda (2–8 bars, optional). Rules: beat-invariance (V0 fires on every beat, never rests), hand-partition interlock (V0/V1 no simultaneous onset; bass on beat, chord on offbeat space), 4-note chord rule (no triads, no added 2nd, always 6th/7th), inversion filter (stepwise bass movement preferred, root leaps >P5 rejected), phrase-displacement freedom (V2 onsets may shift ±1–2 subdivisions while V0 locked), anti-ornament constraint (V2: no grace notes, vibrato, slides, melismata), melody-invariant (V2 pitches never change), volume invariance (consistent piano dynamic), form lock (AABA 32-bar or AB 16-bar). | João Gilberto (inventor: *Chega de Saudade* 1958, *João Voz e Violão* 2000 solo album), Antônio Carlos Jobim (composer: *Garota de Ipanema*, *Desafinado*, *Wave*, *Dindi*, *Samba de Uma Nota Só*), Vinicius de Moraes (lyricist), Stan Getz/Astrud Gilberto (*Getz/Gilberto* 1963, international breakthrough), Sonny Carr (hi-hat 1973 "white album") | ✅ Documented |
```

---

## Next Free ID

**HC-054** — determined by scanning all `human_method_HC-*.md` and report files, cross-checking the DB table. HC-053 is the current maximum.

---

## Quirks & Pitfalls

1. **Extreme difficulty of quantization**: The batida's clave syncopation is micro-timed at the 16th-note level with a swung/laid-back feel that is not triplet-based. Machine-quantization tends to produce a stiff, incorrect feel. The clave must swing.
2. **V0 can never rest**: If the thumb bass stops for even one beat, the entire groove collapses. The invariant crotchet pulse is the single most important structural rule.
3. **Inversion ambiguity**: The inversion rule means V0's pitch may not match the chord root. The voice-leading contour matters more than chord-label accuracy. In UnitMatrix terms, V0 pitch should be read as a bass-tone, not a root.
4. **Notating fraseado impossible in ticks**: Vocal timing offsets are not fixed — they are artist's choice. In practice, V2 onsets should be given **relative slots** (early/nominal/late) rather than absolute tick positions. The validation gate must allow a range, not an exact value.
5. **4-note ceiling is also a floor**: Fewer than 4 notes is a plain triad (forbidden). More than 4 notes exceeds the three-finger pluck limit on a classical guitar (only index+middle+ring available).
6. **Percussion is impure**: The pure solo method uses no percussion. The hi-hat exception on the 1973 album is specifically Sonny Carr's innovation. Adding full drum kit (bass drum, snare, ride cymbal) collapses the method into conventional samba/jazz.
7. **One human, two jobs**: In João's performances, the same person executes V0+V1 (right hand) AND V2 (voice). In a separated UnitMatrix realization, the interlocking between thumb and fingers is no longer felt by a single nervous system. The groove may need explicit timing rules to compensate.

---

## Verification

- Detail file written: `human_method_HC-053_bossa-nova-batida-fraseado.md` — 12,877 bytes, verified
- DB updated: `human_methods_db.md` — HC-053 row appended, verified by re-read
- No HC-053 files existed prior; no HC-054 files exist
- Tradition: **Brazilian Bossa Nova** (Rio de Janeiro, 1958–present) — fills a Brazilian gap (only Choro HC-034 existed for Brazil)
- Method layer: **concrete** — fully implementable via the UnitMatrix voice/section/rule system described above