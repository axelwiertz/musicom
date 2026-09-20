# Research Report: HC-040 — Andalusi Nūbah Suite Architecture & Mīzān Metric Acceleration (Al-Āla Craft)

## Executive Summary
- **Method ID**: `HC-040`
- **Method Name**: Andalusi Nūbah Suite Architecture & Mīzān Metric Acceleration (Al-Āla Craft)
- **Tradition**: Arab-Andalusian Classical Music — Moroccan *al-Āla* school (Fes, Tetouan, Chefchaouen, Rabat); 9th century Córdoba (Ziryāb) through the Maghreb diaspora; codified in Muhammad al-Hā'ik's 1789 *Kunnāsh*.
- **Assigned Layer**: `concrete (target when implemented)`
- **Primary Musical Elements**: `STRUCTURE, RHYTHM, PITCH, TEXTURE, HARMONY`
- **Next Free HC ID**: `HC-041`

---

## 1. Craft Overview & Cultural Context

The **Andalusi Nūbah** is an expansive, multi-movement classical suite tradition cultivated over a millennium across Muslim Spain (al-Andalus) and the North African Maghreb. In Morocco, where it is known as **al-Āla** ("the instrumental/art music", distinguishing it from folk or vocal religious chant *samā'*), the repertory constitutes the pinnacle of courtly and devotional musical art.

Tradition attributes the system to the 9th-century Baghdad musician **Ziryāb**, who established an academy in the Umayyad capital of Córdoba with 24 distinct nūbāt, conceptually aligned with the 24 hours of the day and humoral temperaments. Following the Christian Reconquista and the 1492 expulsion of Muslims and Sephardic Jews from Granada, the tradition took refuge in Morocco. In late 18th-century Tetouan, scholar-musician **Muhammad ibn al-Husayn al-Hā'ik** compiled the surviving repertoire into the **Kunnāsh al-Hā'ik** (1789), stabilizing 11 grand nūbāt containing over 900 individual songs (*san'āt*).

Unlike Western classical suites structured around contrasting keys, a Moroccan Nūbah remains bound to a single modal universe (**tab'**). Dramatic progression is achieved not through harmonic modulations, but through a masterfully engineered **macro-structural acceleration arc** across five distinct metric movements called **mawāzīn** (singular **mīzān**):
1. **Basīt**: 6/4 compound slow meter
2. **Qā'im wa-Nisf**: 8/4 asymmetrical additive meter (3+2+3)
3. **Btāyhī**: 8/4 flowing moderate pulse
4. **Darj**: 4/4 walking rhythmic drive
5. **Quddām**: 3/4 or 6/8 rapid, dancing finale

Furthermore, each individual *mīzān* features a 3-stage internal micro-acceleration:
- **Muwassa'** ("spacious"): broad, contemplative, heavily ornamented singing.
- **Mahzūz** ("shaken"): steady, lively groove.
- **Insirāf** ("departure"): accelerated, driving sprint to the climax.

Movements and meters are chained by brief instrumental bridges called **qanātir** (singular *qantara*), enabling seamless shifts in rhythmic subdivision without stopping the ensemble.

---

## 2. Practitioner Craft Workflow (Step-by-Step)

1. **Modal Foundation (*Tab'*)**: The ensemble leader fixes the overarching mode (e.g. *Raml al-Māya*, *Rasd*, *Hijāz al-Kabīr*). All instruments tune their open strings to resonance points of the mode.
2. **Bughya (Improvisatory Prelude)**: The ensemble opens with an unmetered, contemplative prelude in heterophonic unison, stating the fundamental intervals, reciting notes, and emotional mood (*ethos*) of the *tab'*.
3. **Tushiya (Metered Overture)**: The percussion enters, launching an instrumental through-composed overture displaying ensemble virtuosic cohesion.
4. **Mīzān Progression (5-Suite Cycle)**: The master navigates through the canonical suite sequence (*Basīt* → *Qā'im wa-Nisf* → *Btāyhī* → *Darj* → *Quddām*).
5. **San'a Delivery (Vocal Strophes)**: Instrumentalists sing *muwashshah* and *zajal* poems in unison while playing. Tempo advances within each movement from *Muwassa'* to *Mahzūz* to *Insirāf*.
6. **Qantara Pivoting**: Instrumental bridge phrases pivot the percussion from one metric division to the next.
7. **Heterophonic Layering**: Texture is enriched by idiomatic layering: bowed *rabāb* (gutural core skeleton), plucked *'ūd* (ornamental arpeggios/runs), bowed *kamānja* (slides, shimmer), and *tār* frame drum (syncopated *dum-tek* timekeeping).

---

## 3. Real Practitioner References
- **Ziryāb (789–857 CE, Córdoba)**: Founding father of Andalusi music theory, lute pedagogy, and the cosmological 24-nūbah system.
- **Muhammad ibn al-Husayn al-Hā'ik (fl. 1789, Tetouan)**: Compiler of the monumental *Kunnāsh al-Hā'ik*, codifying the 11 surviving Moroccan nūbāt.
- **Haj Abdelkrim al-Raïs (1912–1996, Fes)**: *Rabāb* virtuoso and director of the *Orchestre Al-Brihi de Fès*, who directed the definitive 73-cassette national sound archive of *al-Āla*.
- **Moulay Ahmed Loukili (1907–1988, Rabat)**: Renowned leader of the Moroccan Radio Andalusian Orchestra, master of vocal *inshād* interpretation.
- **Mohamed Larbi Temsamani (1920–2001, Tetouan)**: Master of the Tetouani school and director of the Tetouan Conservatory, refined ensemble precision and orchestration.

---

## 4. Musical Elements & UnitMatrix Mapping

### Musical Elements
- **PITCH**: Modal unity within a single *tab'* (characteristic scales, resting *qarār*, reciting *nawā*).
- **RHYTHM**: Cyclical *mawāzīn* (*Basīt* 6/4, *Qā'im wa-Nisf* 8/4, *Btāyhī* 8/4, *Darj* 4/4, *Quddām* 3/4/6/8); tempo progression *Muwassa'* → *Mahzūz* → *Insirāf*.
- **HARMONY**: Modal monophony and heterophony; no functional chords; cadence always returns to the *qarār* tonic.
- **STRUCTURE**: Arch-suite form: *Bughya* (prelude) → *Tushiya* (overture) → *Mawāzīn 1–5* (strophic *san'āt* with internal tempo climbs) linked by *Qantara* bridges.
- **TEXTURE**: Heterophonic stratification (*Rabāb* skeleton + *'Ūd* plucked fill + *Kamānja* vocal doubling + *Tār* frame-drum groove).

### UnitMatrix Implementation
- **Voice 0 (Spine / Rabāb)**: Core modal melody; long held tones, invariant syllable alignment.
- **Voice 1 ('Ūd / Plucked Fill)**: Fast runs, tremolos, octave jumps ornamenting Voice 0.
- **Voice 2 (Kamānja / Vocal Chorus)**: Expressive lead delivery of poetic strophes (*san'āt*).
- **Voice 3 (Percussion / Tār & Darbūka)**: Channel 9 percussion; *dum* (center, kick/low tom) and *tek* (edge, tambourine/rimshot) rhythmic cycle.
- **Sections**:
  - S0: `Bughya` (arrhythmic rubato prelude)
  - S1: `Tushiya` (instrumental overture)
  - S2: `Basit_Muwassa` (slow 6/4 vocal stanzas)
  - S3: `Basit_Insiraf` (accelerated 6/4 stanzas)
  - S4: `Qantara_Bridge` (metric bridge)
  - S5: `Quddam_Muwassa` (moderate 6/8 swing)
  - S6: `Quddam_Insiraf` (fast 6/8 climactic finale)

### Zero-Drift & Production Rules
- Every cell padded strictly to `section_len` ticks.
- Monotonic tempo scaling across sections.
- Strict pitch-class containment within the selected *tab'*.

---

## 5. Table Row Appended to `human_methods_db.md`

```markdown
| HC-040 | human (→concrete) | Andalusi Nūbah Suite Architecture & Mīzān Metric Acceleration | Arab-Andalusian Classical — Moroccan al-Āla tradition (Fes/Tetouan/Rabat), 9th c. Ziryāb Córdoba roots → 1789 Kunnāsh al-Hā'ik canon | STRUCTURE, RHYTHM, PITCH, TEXTURE, HARMONY | Fix tab' mode & tuning → perform bughya unmetered prelude (heterophonic unison) → tushiya instrumental overture in fixed meter → cycle through five mawāzīn suites (Basīt 6/4 → Qā'im wa-Nisf 8/4 → Btāyhī 8/4 → Darj 4/4 → Quddām 3/4/6/8) → sing strophic san'āt poetry (muwashshah/zajal) in unison chorus with rabāb/oud/violin accompaniment → escalate tempo within each mīzān through three phases: Muwassa' (slow) → Mahzūz (shaken/medium) → Insirāf (fast driving finale) → connect movements via qantara metric bridges → ornament heterophonically (rabāb skeleton, 'ūd flourishes, kamānja slides, tār/darbūka dum-tek cycles) | Voice 0 = rabāb/spine (unadorned modal skeleton, invariant pitch/syllable anchor). Voice 1 = 'ūd (plucked heterophonic elaboration, octave touches, tremolo). Voice 2 = kamānja & vocal unison chorus (expressive lyric melody, fraseo bends). Voice 3 = tār/darbūka percussion (wazn cycle, dum-tek accent grammar, drives tempo escalation). Sections = Bughya (prelude) → Tushiya (overture) → Basīt Muwassa' → Basīt Insirāf → Qantara → Quddām Muwassa' → Quddām Insirāf. Rules: modal tab' invariance, heterophonic subordination to V0, mīzān metric mask, 3-phase tempo escalation, qantara metric pivot, zero-drift cell padding. | Ziryāb (Abbasid Córdoba court founder, 24 nūbāt), Muhammad al-Hā'ik (1789 Kunnāsh compiler), Haj Abdelkrim al-Raïs (Orchestre Al-Brihi de Fès, definitive national recordings), Moulay Ahmed Loukili (Rabat Radio Orchestra, inshād mastery), Mohamed Larbi Temsamani (Tetouan Conservatory) | ✅ Documented |
```

---

## 6. Verification & Status
- `human_method_HC-040_andalusi-nubah-suite-mizan.md` written and validated.
- `human_methods_db.md` table updated with row `HC-040`.
- Next free ID: **`HC-041`**.
