# Exercise 01 — Balfolk vs Jazz vs Hybrid

Goal: hear genre as a semantic layer on top of Musicom `UnitMatrix` / `MusicMatrix`.

Reserved matrix meaning:

```text
Rows    = voices / pitch-space layers
Columns = measures / time-space segments
Cells   = MusicUnit-like bar material
```

Exercise row mapping:

```text
MusicMatrix row 1 = Foot Pulse / Drums     -> Rhythm DNA
MusicMatrix row 2 = Bass                  -> Bass DNA
MusicMatrix row 3 = Harmony / Chords      -> Harmony DNA
MusicMatrix row 4 = Lead / Fiddle or Sax  -> Melody DNA
```

Listen in this order:

1. Balfolk Dorian Jig
2. Jazz ii-V-I Swing
3. Hybrid Balfolk-Jazz
4. Compare file with all three

## A. Balfolk Dorian Jig

Files:

- `MIDI/exercise1a_balfolk_dorian_jig.mid`
- `Audio/exercise1a_balfolk_dorian_jig.ogg`

Parameters:

- Key/mode: D Dorian = D E F G A B C
- Meter: 6/8
- Tempo: dotted-quarter dance feel around 95 BPM
- Rhythm DNA: `█░░█░░`
- Harmony: Dm | C | Dm | G | Dm | C | G | Dm

Matrix:

```text
Bars:     1      2      3      4      5      6      7      8
Rhythm:   jig    jig    jig    jig    jig    jig    jig+   cadence
Bass:     D      C      D      G      D      C      G      D
Harmony:  Dm     C      Dm     G      Dm     C      G      Dm
Melody:   A      A'     A      B      A      A'     B'     Cad
Timbre:   fiddle fiddle fiddle acc+   fiddle fiddle full   resolve
Form:     Question      Answer        Repeat        Close
```

Listening tasks:

- Tap 1 and 4 in each 6/8 bar.
- Notice simple stepwise melody.
- Hear Dorian color: B natural inside D minor world.

## B. Jazz ii-V-I Swing

Files:

- `MIDI/exercise1b_jazz_ii_v_i_swing.mid`
- `Audio/exercise1b_jazz_ii_v_i_swing.ogg`

Parameters:

- Key: C major
- Meter: 4/4 swing
- Rhythm DNA: swing 8ths + 2-and-4 backbeat
- Harmony: Dm7 | G7 | Cmaj7 | Cmaj7 | Em7 | A7 | Dm7-G7 | Cmaj7

Matrix:

```text
Bars:     1      2      3       4       5      6      7        8
Rhythm:   swing  swing  swing   space   swing  swing  ii-V     cadence
Bass:     walk   walk   root-5  walk    walk   walk   turn     C
Harmony:  Dm7    G7     Cmaj7   Cmaj7   Em7    A7     Dm7-G7   Cmaj7
Melody:   guide  tense  resolve space   seq    tense  turn     home
Timbre:   sax    sax    sax     piano   sax    sax    full     soft
Form:     ii-V-I phrase         answer phrase           close
```

Listening tasks:

- Tap 2 and 4.
- Follow walking bass.
- Hear melody land on chord tones at strong points.

## C. Hybrid Balfolk-Jazz

Files:

- `MIDI/exercise1c_hybrid_balfolk_jazz.mid`
- `Audio/exercise1c_hybrid_balfolk_jazz.ogg`

Parameters:

- Base: Balfolk 6/8 jig body
- Borrowed layer: Jazz color harmony
- Mode: D Dorian
- Rhythm DNA: `█░░█░░`
- Harmony: Dm9 | Cmaj7 | Dm9 | G13 | Dm9 | Cmaj7 | G13 | Dm9

Matrix:

```text
Bars:     1      2       3      4      5      6       7      8
Rhythm:   jig    jig     jig    jig    jig    jig     jig+   cadence
Bass:     D      C       D      G      D      C       G      D
Harmony:  Dm9    Cmaj7   Dm9    G13    Dm9    Cmaj7   G13    Dm9
Melody:   folk   folk    folk   folk   folk   folk    lift   close
Timbre:   fiddle piano   fiddle piano  fiddle piano   full   resolve
Form:     Balfolk body + Jazz color
```

Listening tasks:

- Tap like Balfolk, not Jazz.
- Hear harmony as richer than plain Dm-C-G.
- Notice melody remains simple; harmony carries the hybrid color.

## Your practice task

After listening, answer these:

1. Which version makes your body move most?
2. Which version has strongest harmonic pull?
3. In the hybrid, does it still feel like Balfolk? Why?
4. Choose one transformation for next version:
   - darker: use Aeolian b6
   - brighter: use Lydian #4 color over G13
   - more dance: stronger accents on 1 and 4
   - more jazz: add chromatic approach notes
