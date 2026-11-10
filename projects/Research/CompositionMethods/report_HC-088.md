# Report HC-088 — Bebop Contrafact Head Composition

**Job:** `daily-human-composition-research` · **Date:** 2026-11-09
**Method ID:** HC-088
**Layer:** `human (→concrete)` — human-craft knowledge; target layer **concrete** when realized through the UnitMatrix
**Detail file:** `human_method_HC-088_bebop-contrafact-head-composition.md`

---

## 1. Method name, tradition, layer

**Bebop contrafact composition**: writing a *new melody* (the "head") over an *existing harmonic
progression* (the "vehicle") — the dominant jazz composition method of the 1940s bop era and still the
canonical jazz composition exercise in pedagogy. The term comes from the medieval *contrafactum* (new text
over an existing melody); musicology applied it to bop's new-melody-over-borrowed-changes procedure.

- **Tradition:** African-American jazz, bebop, USA — Minton's Playhouse & Monroe's Uptown House (Harlem),
  52nd Street (NYC), 1940s; continued in hard bop, post-bop, and jazz education to the present.
- **Layer:** concrete (target when implemented) — like all HC methods, this is human-craft knowledge that
  the Musicom engine realizes as concrete note/chord material in the UnitMatrix.

**Why it matters:** chord progressions are not copyrightable, melodies are. The contrafact gave bop
musicians new publishable originals they could improvise on immediately (familiar changes), without
permission or publisher fees — a legal/practical engine that generated hundreds of jazz standards in a few
years. *I Got Rhythm*'s "rhythm changes" became the second most-used harmonic skeleton in jazz after the
12-bar blues.

## 2. The craft procedure in detail (how the human actually does it)

1. **Choose the vehicle** — a progression known by heart: rhythm changes (*I Got Rhythm*), a 32-bar
   AABA/ABAC standard (Cherokee, Honeysuckle Rose, How High the Moon, Indiana, What Is This Thing Called
   Love, Sweet Georgia Brown, All of Me), a 12-bar blues, or a jazz original (Dameron's *Lady Bird*).
2. **Internalize the changes** — play them until automatic: guide tones (3rd & 7th) of each chord,
   II–V–I locations, bridge modulation, turnarounds. Hear the progression, don't read it.
3. **Compose the head** with bop melodic grammar:
   - chord tones on strong beats; chromatic approach tones on offbeats;
   - approach-note vocabulary: half-step approach from above/below, enclosures (above–below / below–above
     around the target), bebop scale (diatonic + added chromatic passing tone) for eighth-note runs;
   - "running the changes": arpeggiate each chord's extended harmony (descending dom7 arpeggios over the
     rhythm-changes bridge);
   - anticipation/back-phrasing: attack on the "&" of 4, resolve across the barline; rest on beat 1 as
     often as hitting it;
   - wide leaps, octave displacement, long-note-then-burst gestures; blue inflections (♭3/♭5) in reserve.
4. **Recompose the changes when useful** (contrafact ≠ mere new tune on old chords): II–V insertion,
   tritone substitution, back-cycling; **compress** the form (*Ko-Ko*: Cherokee 64→32 bars); **splice**
   vehicles (*Scrapple from the Apple*: Honeysuckle Rose A-section + I Got Rhythm bridge); replace the
   bridge. Bar count and section length are the surviving invariants.
5. **Test with the rhythm section** — must swing, lie well on the horn, be hummable. "If you can't hum
   it, it isn't a head."
6. **Improvise on it immediately** — familiar changes = instant improvisability; Parker's solos quote and
   develop head motives, so the head seeds the solo.
7. **Publish/record as an original** — new melody = new copyright; valuable during the AFM recording ban
   (1942–44).
8. **Teach it** — the standard composition exercise in jazz education (write a head over rhythm changes /
   blues / Lady Bird); analysis runs the reverse direction (find any bop tune's source changes).

## 3. Practitioner examples

- **Charlie Parker** — *Ornithology* (How High the Moon, 1946, with Benny Harris), *Ko-Ko* (Cherokee,
  compressed, 1945), *Steeplechase* / *Dexterity* / *Moose the Mooche* / *Anthropology* (rhythm changes),
  *Donna Lee* (Indiana; Davis credited, authorship debated), *Scrapple from the Apple* (1947,
  Honeysuckle Rose + rhythm bridge), *Bird of Paradise* (All of Me), *Blues for Alice* (blues + "Bird
  blues" II–V cycle).
- **Dizzy Gillespie** — *Salt Peanuts* (rhythm variant), *Woody 'n' You*; premiered Dameron's *Hot House*.
- **Tadd Dameron** — *Hot House* (What Is This Thing Called Love, 1945); *Lady Bird* (1939, original
  changes that became the vehicle of Miles Davis' *Half Nelson*).
- **Thelonious Monk** — *In Walked Bud* (Blue Skies, 1947), *Evidence* (Just You, Just Me),
  *Bright Mississippi* (Sweet Georgia Brown, 1961), *Rhythm-a-Ning* (rhythm changes, 1957),
  *Hackensack* (Oh, Lady Be Good).
- **Miles Davis** — *Half Nelson* (Lady Bird, 1947), *Donna Lee*, *Four*.
- **Sonny Rollins** — *Oleo* (rhythm changes, 1954, on *Saxophone Colossus*).
- **Duke Ellington** — *Cottontail* (rhythm changes, 1940), *In a Mellow Tone* (Rose Room, 1939).
- **James Moody** — *Moody's Mood for Love* (I'm in the Mood for Love).
- **John Coltrane** — *Impressions* (So What changes, 1961).
- **Precedent** — medieval *contrafactum*; Gounod's *Ave Maria* over Bach's Prelude BWV 846 (1853);
  classical contrafacts (Berio quoting Mahler; Crumb quoting Chopin).

All vehicle attributions verified against Wikipedia's *Contrafact* and *List of jazz contrafacts*
(retrieved live during this run).

## 4. UnitMatrix mapping

**Voices:**
- **V0 — Lead horn** (alto/trumpet/tenor): the *new composed head* in head sections; improvised line in
  solo sections. This row IS the composition.
- **V1 — Piano/guitar comping:** one chord per bar from the borrowed skeleton; shell/4-note voicings;
  off-beat stabs; silent under exposed head phrases.
- **V2 — Bass:** walking quarter-notes — roots on strong beats, chromatic approach on weak beats, II–V
  patterns.
- **V3 — Drums (ch.9):** ride swing + hi-hat 2&4; time-feel anchor; continuous through rests.
- **V4 — Optional 2nd horn:** bop harmony in 3rds/6ths below the lead, unison doubling, or 4-horn
  block-chord soli.

**Sections (AABA vehicle, 8 bars each = 15,360 ticks at 480 tpb):**
S0 Head A1 → S1 Head A2 → S2 Bridge B (contrast: register/contour change, dom7 arpeggio cycle) →
S3 Head A3 (cadence) → S4 Solo chorus 1 (lead, same skeleton) → S5 Solo chorus 2 (piano) →
S6 Head out (final head, ensemble punctuation). Blues vehicle = 12-bar sections. Tempo quarter ≈ 180–220.

**Rules to encode:**
- **Changes-lock:** harmony skeleton fixed from the source vehicle (roman-numeral table per section);
  recomposition operators (II–V insertion, tritone sub, back-cycle, compression/splice) must be logged
  and must preserve section bar counts — zero-drift validate is the gate.
- **Chord-tone anchor:** strong beats on chord tones (3rd/7th preferred; 9th/13th as color); offbeats may
  be chromatic.
- **Approach grammar:** every melodic target approached by half-step or enclosed; runs use the bebop scale.
- **Anticipation rule:** "&" of 4 attacks resolving across the barline; downbeat-attack density ≤ ~50%.
- **Density gesture:** long values alternate with swing-8th bursts; monotone density rejected.
- **Form lock:** 32-bar AABA/ABAC or 12-bar blues; equal sections; turnaround on section ends;
  head–solo–head order.
- **Bridge contrast:** new register/contour vs A sections.
- **Comping separation:** V1 sparse under exposed head; V2 walks continuous; V3 ride continuous, swing
  ratio ~0.65/0.35.
- **Playability filter** (instrument ranges).
- **Humanize:** loose jazz profile — lead σ 8–15 ms, 10–20 ms layback; swing eighths encoded consistently
  across V0/V2 (else the head reads straight); ride tight σ 2–4 ms.

## 5. Table row added to `human_methods_db.md`

Appended after the HC-087 row (line 94 of `human_methods_db.md`):

```
| **HC-088** | human (→concrete) | Bebop Contrafact Head Composition — New Melody Over Borrowed Changes (Vehicle + Reharmonization: II–V Insertion, Tritone Sub, Form Compression/Splice; Head–Solo–Head Chorus Architecture) | Jazz — African-American bebop, USA (Minton's Playhouse, Monroe's, 52nd Street, NYC 1940s; pedagogy to present); device rooted in medieval *contrafactum* (new text over existing melody) | HARMONY, PITCH, RHYTHM, STRUCTURE, TEXTURE | ... | ✅ Documented |
```

Full row content is in the DB file (single aligned pipe row, matching the existing 9-column format).
`human_methods_db.md` was NOT touched by this job beyond the single appended row (the algorithmic
`methods_db.md` is owned by another job).

## 6. Verification

- `grep HC-088 human_methods_db.md` → **1 match** (the appended row; no pre-existing HC-088).
- `grep HC-088 human_method_HC-088_bebop-contrafact-head-composition.md` → **1 match** (header line).
- `grep HC-088 report_HC-088.md` → present (this file).
- Highest pre-existing ID was HC-087 (DB row + both file families agree). No duplicates.
- **Next free ID: HC-089.**

## 7. Quirks & pitfalls

- **The copyright engine is the method's fuel** — harmony uncopyrightable, melody copyrightable. Many bop
  heads were dashed off minutes before recording dates; expect short functional heads, not developments.
- **Authorship disputes are endemic** (*Donna Lee* Parker vs Davis; *Ornithology* Parker vs Harris;
  *Four*). Attribute as "credited to".
- **Compression breaks source geometry** (*Ko-Ko* 64→32) — track a source-bars → target-bars map; the
  UnitMatrix sections, not the source tune, are the invariant.
- **A contrafact must stand alone** — hummability and swing are the test, not harmonic cleverness.
- **Swing notation problem** — equal eighth-notes in tick-grid MIDI read straight; encode swing as
  duration ratios or via the humanizer's jazz profile, consistently with the ride pattern.
- **Vehicle concentration** — bop leans on a few skeletons (rhythm changes, blues, Cherokee,
  Honeysuckle Rose, How High the Moon); modern practice composes new vehicles (Lady Bird, Giant Steps)
  and contrafacts those — the method scales to any fixed skeleton.
- **Terminology collision** — "contrafact" also covers medieval *contrafactum* and classical
  recompositions (Gounod/Bach, Berio/Mahler): same device, different eras.

## 8. Sources consulted

- Wikipedia: *Contrafact*; *List of jazz contrafacts* (retrieved live 2026-11-09 — vehicle attributions
  verified: Ornithology→How High the Moon; Scrapple→Honeysuckle Rose + I Got Rhythm bridge;
  Hot House→What Is This Thing Called Love; Half Nelson→Lady Bird; Oleo→I Got Rhythm;
  In a Mellow Tone→Rose Room; Bright Mississippi→Sweet Georgia Brown; Rhythm-a-Ning→I Got Rhythm;
  In Walked Bud→Blue Skies; Moose the Mooche/Steeplechase/Cottontail→I Got Rhythm; Donna Lee→Indiana;
  Evidence→Just You, Just Me; Impressions→So What; Moody's Mood for Love→I'm in the Mood for Love).
- Jazz pedagogy: J. Levine, *The Jazz Theory Book*; D. Baker, *How to Play Bebop*; T. Owens,
  *Bebop: The Music and Its Players*; C. Woideck, *Charlie Parker: His Music and Life*; H. Martin,
  *Charlie Parker and Thematic Variation*; T. Gioia, *The History of Jazz*.
