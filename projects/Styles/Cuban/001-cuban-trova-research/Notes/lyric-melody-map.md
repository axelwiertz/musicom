# Lyric -> Melody Map

## Global rules
- **Stress** -> beat strength and velocity.
- **Question** -> phrase end rises.
- **Answer** -> phrase end falls to tonic.
- **Long vowel / open line** -> sustained note.
- **Story tension** -> wider interval, slightly longer phrase.
- **Story release** -> narrower interval, clear cadence.

## Section map

### Verse A1
1. `La tarde baja suave por el monte,`
   - contour: mid-low start, gentle rise on `baja`, settle on `monte`
   - rhythm: mostly even quarters with one held final syllable
   - stress targets: `TAR-de`, `BA-ja`, `SUA-ve`, `MON-te`
   - role: scene-setting, calm motion

2. `y tu recuerdo vuelve sin pedir.`
   - contour: small upward lift on `re-cuer-`, fall on `pedir`
   - rhythm: slightly compressed middle, longer last note
   - stress targets: `re-CUER-do`, `VUEL-ve`, `pe-DIR`
   - role: memory enters, mild tension

### Verse A2
3. `La yegua pisa lento el horizonte,`
   - contour: stepwise descent then rise toward `horizonte`
   - rhythm: more walking pulse, stable grid
   - stress targets: `YE-gua`, `PI-sa`, `LEN-to`, `ri-ZON-te`
   - role: image line, moving horizon

4. `y yo te canto para no morir.`
   - contour: rise on `canto`, strong fall on `morir`
   - rhythm: slight hold on `canto`, cadential landing on `morir`
   - stress targets: `yo`, `CAN-to`, `mo-RIR`
   - role: emotional confession, stronger close

### Chorus B1
5. `Ay, si me llamas, yo vuelvo a la senda,`
   - contour: open upward leap on `llamas`, then resolve but not fully closed
   - rhythm: more syncopation, stronger pickup
   - stress targets: `LLA-mas`, `VUEL-vo`, `SEN-da`
   - role: hook question / answer promise

6. `con esta voz de campo y de raíz.`
   - contour: smooth descent, held note on `raíz`
   - rhythm: longer vowel on final word
   - stress targets: `voz`, `CAM-po`, `ra-ÍZ`
   - role: identity statement, landed answer

7. `Ay, si te quedas, la pena se encienda,`
   - contour: repeat opening shape, but with more lift toward `encienda`
   - rhythm: same phrase grid as line 5 for recognizability
   - stress targets: `QUe-das`, `PE-na`, `en-CIEN-da`
   - role: emotional tension mirror

8. `pero en tu risa vuelve a ser feliz.`
   - contour: clear downward release, tonic landing on `feliz`
   - rhythm: slightly shorter than line 6 for closure
   - stress targets: `RI-sa`, `VUEL-ve`, `fe-LIZ`
   - role: release, emotional answer

### Bridge C
9. `Porque la noche sabe de caminos,`
   - contour: lower register, wider interval than verse
   - rhythm: slower, more space between phrases
   - stress targets: `NOC-he`, `SA-be`, `ca-MI-nos`
   - role: reflective turn

10. `y el río guarda nombres al pasar.`
    - contour: rising middle, then fall on `pasar`
    - rhythm: legato line, more sustained flow
    - stress targets: `RÍ-o`, `GUAR-da`, pa-SAR
    - role: memory in motion

11. `Si me preguntas dónde están mis signos,`
    - contour: strongest question lift in whole song
    - rhythm: expand phrase length, delay resolution
    - stress targets: `pre-GUN-tas`, `DÓN-de`, `SIG-nos`
    - role: real question, tension peak

12. `están en la tierra, en volver a amar.`
    - contour: stepwise descent to tonic resolution
    - rhythm: most settled cadence in bridge
    - stress targets: `TIE-rra`, `vol-VER`, a-MAR`
    - role: answer, return to home

## Practical melody plan
- Verse: stay around tonic and 3rd, few leaps.
- Chorus: jump to 5th or 6th on hook word `llamas` / `quedas`.
- Bridge: descend to lower register, then open upward on the question line.
- Final chorus: repeat chorus contour, maybe one higher final note on `feliz`.

## MIDI implementation hint
- Stressed syllables get note_on at beat 1 or beat 3.
- Weak syllables sit on passing notes or shorter durations.
- Final phrase syllable gets longest sustain.
- Use small upward pickup before each chorus line.
