# Report HC-082 — Jingju (Beijing Opera) Aria Composition: Xipi/Erhuang Modes × Banshi Rhythmic Patterns × Luogujing Percussion × Jinghu Heterophonic Support

**Job:** daily-human-composition-research (nightly cron, 2026-11-02)
**Method ID:** HC-082
**Detail file:** `human_method_HC-082_jingju-xipi-erhuang-banshi-aria.md`
**Next free ID:** HC-083

---

## 1. Method name & tradition

**Jingju aria composition (京剧唱腔设计)** — the craft of building a sung aria (唱段 *chàngduàn*) for Chinese Peking opera from three interlocking human systems: (1) the two **melodic modes** 西皮 *xipi* / 二黄 *erhuang* (plus transposed 反调 *fǎn diào* forms), (2) the **rhythmic-metric patterns** 板式 *bǎnshì* (fixed tempo/meter templates chained into the aria's dramatic arc, governed by the 板眼 board-and-eye grid), and (3) the **percussion scores** 锣鼓经 *luógujīng* (oral mnemonic syllables that cue action, entrance, and aria), bound by the **heterophonic jinghu** fiddle accompaniment (托腔保调 — "support the aria, preserve the mode").

- **Tradition / Culture:** Chinese jingju, the national opera. Formation: Four Great Anhui Troupes (三庆/四喜/和春/春台) enter Beijing 1790 for the Qianlong Emperor's 80th birthday singing erhuang; 1828 Hubei Han-opera troupes add xipi → 皮黄 píhuáng fusion; Beijing dialect colouring; name 京剧 appears in the press 1876; fully formed by 1845; court maturation under Empress Dowager Cixi; golden age 1920s–30s (四大名旦); standardized post-1949; model works 样板戏 1960s–70s. **UNESCO ICH Representative List (2010).**
- **Layer:** `human (→concrete)` — target layer **concrete** when realized through the UnitMatrix (human-craft knowledge: how a singer + *qínshī* fiddler + *gǔshī* drummer team composes an aria by mouth and ear, with notation as memory aid only).

## 2. Why this method, why now

ID rotation: HC-081 Gnawa (North Africa), HC-080 Notre-Dame organum (medieval Western), HC-079 Musique Concrète (France), HC-078 Tin Pan Alley (US pop), HC-077 Kulintang (Philippines), HC-076 Pansori (Korea). **East Asian opera/theatre craft was missing from the DB** — guqin (HC-032) is solo instrumental China, gagaku (HC-041) & honkyoku (HC-029) are Japanese. Overlap check: HC-003 makam heterophony shares the shared-skeleton/no-functional-harmony texture principle but is Ottoman *instrumental* practice; HC-021/071 are Western harmonic voice-leading; HC-007 is Western pop prosody. Jingju is unique in the DB as one integrated human system of **mode × rhythmic-pattern grid × text-tone prosody × role-typed vocal register × heterophonic fiddle × mnemonic percussion score**. No duplicate: grep `jingju|xipi|erhuang|banshi|luogujing|锣鼓经|板式|皮黄` over the CompositionMethods dir → 0 hits. `methods_db.md` untouched (algorithmic DB, another job's).

## 3. The craft procedure in detail (how the human executes it)

### Stage 0 — apprenticeship (口传心授, oral/aural transmission)
1. Apprentices memorize whole highlight scenes by ear; *luógujīng* are learned as **spoken syllables** (仓 cang = big gong crash, 台 tai = small gong, 才/七 cai/qi = cymbals, 倾 qing = light gong, 匡 kuang = muffled gong, 空 kong = choked, 大/达 da = drum single, 八/崩 ba/beng = drum double, 嘟 du = roll, 隆咚 longdong = heavy-weak, 扎/衣 yi = clapper) before touching an instrument. Notation (工尺谱 historically, jianpu today) is a memory aid, not the composition.
2. The 鼓佬 *gǔlǎo* (drum master) conducts the whole ensemble from the 板鼓 *bǎngǔ* + 檀板 *tánbǎn* — drum-and-clapper player IS the conductor, cueing every pattern by gesture.

### Stage 1 — choose the mode by emotion
3. **Xipi** (la–mi open strings; "bright, lively, excited"; English scholarship: "joyous stories", derived from the high, loud Qinqiang of the northwest) — argument, excitement, haste, joy.
4. **Erhuang** (sol–re open strings; "low, soft, despondent folk tunes of south-central Hubei"; "lyrical stories") — reflection, grief, interiority, dignity.
5. Deeper sorrow → 反调 fan forms: 反二黄 *fǎn erhuang* (do–sol) and 反西皮 *fǎn xipi* (la–mi transposed down). Both modes share a standard 2/4-feel grid and six common bǎnshì; they differ in pitch inventory, cadence notes (落音), and ornament vocabulary.

### Stage 2 — design the 板式 chain (rhythmic architecture of the aria)
6. Chain bǎnshì patterns along the emotional arc; each = fixed meter + tempo + phrase structure:
   - 导板 *dǎobǎn* (free-rhythm lead-in, one line), 回龙 *huílóng* (link after 导板), 慢板/三眼 *mànbǎn·sānyǎn* (一板三眼 = 4/4, slow centre), 原板 *yuánbǎn* (一板一眼 = 2/4, medium "original", most common), 二六 *èrliù* (xipi, 2/4, syllabic argument), 流水 *liúshuǐ* (xipi, 有板无眼 = 1/4, flowing), 快板 *kuàibǎn* (xipi, very fast 1/4, climax), 摇板 *yáobǎn* (free voice over strict 1/4 orchestra), 散板 *sǎnbǎn* (无板无眼, free), 滚板 *gǔnbǎn* (erhuang, fast 1/4, extreme grief).
   Typical full chain: 导板 → 回龙 → 慢板 → 原板 → 快板/流水 → 散板 — an accelerating, densifying scena governed by the board-beat grid (板 = clapper downbeat, 眼 = weak beats).

### Stage 3 — set the text (依字行腔: melody born from the characters)
7. Lyrics are **couplets** (lián of two *jù*): two 7-char or two 10-char lines, each in three *dǒu* pauses (2-2-3 / 3-3-4); padding characters allowed.
8. Prosody: 13 rhyme categories (十三辙); Mandarin tones 1–2 = *píng* (level), 3–4 = *zè* (oblique); **every couplet's closing line ends on a level tone**; zè → lower/shorter, píng → higher/longer/ornamented.
9. Compose the vocal contour to *follow the speech tones* (依字行腔); same text may be re-set per school. Sing at the top of the range ("high pitch is a positive aesthetic value"; most arias span "an octave and a fifth"); ideal timbre a "controlled nasal tone"; vibrato slower and wider than Western; slogan 字正腔圆 ("characters accurate, melody round").
10. Ornament 润腔 by **role type** 行当: 生 shēng (lǎoshēng natural voice + 脑后音 back-of-head resonance; xiǎoshēng falsetto), 旦 dàn (qīngyī/huādàn/lǎodàn in 小嗓 falsetto), 净 jìng (painted face, chest power, wide vibrato), 丑 chòu (clown: mostly spoken 数板, improvisation license — orchestra follows even an unscripted folk song), 末 mò (minor male, fifth historical type).

### Stage 4 — co-compose the jinghu line (托腔保调)
11. The *qínshī*'s fiddle part is **heterophony**: follows the vocal contour but diverges — typically **more notes per measure, an octave lower**; techniques 托 (support) / 裹 (wrap in denser figuration) / 垫 (pad gaps) / 补 (mend ends).
12. Insert 过门 *guòmén* interludes between vocal phrases (and 垫头 fill-ins); the jinghu player keeps a personal "signature version" and **must adapt live to the singer's spontaneous ornaments** (Wichmann 1991).
13. Ensemble: jinghu (lead), yueqin (plucked lute fills), daluo/xiaoluo/naobo percussion — conducted by the drum-and-clapper player.

### Stage 5 — lay the percussion score (锣鼓经)
14. Set 锣鼓点 *luógǔdiǎn* patterns per dramatic beat (syllable→instrument table as in Stage 0). Standard patterns: 四击头 (four-stroke punctuation), 急急风 ("hurried wind", martial rush), 冲头, 长锤, 夺头 (the classic aria-introducing pattern), 乱锤, 阴锣, 水底鱼. **Up to 48 entrance patterns identify the entering character's rank and personality** (Guy 1990). Percussion cues 板式/tempo, punctuates 身段, imitates nature, accompanies 唱腔 and 念白.

### Stage 6 — assemble & fix the work
15. Interleave 曲牌 *qǔpái* instrumental tunes: 水龙吟 (VIP arrival), 急三枪 (feast), 小开门 (movement), 哭皇天 (mourning), 八岔, 柳摇金, 傍妆台, 夜深沉 (the sword-dance showpiece in *Farewell My Concubine*).
16. The "composer" is a **team** (singer + qínshī + gǔshī + playwright/director); model-work 唱腔设计 composers (e.g., the 智取威虎山 team, whose famous opening 二黄导板 "穿林海跨雪原气冲霄汉" is a landmark) formalized this into written craft. The result is fixed by school performance tradition, not a single autograph.

## 4. Practitioner examples

- **Tan Xinpei (谭鑫培, 1847–1917)** — "king of laosheng", canonical xipi/erhuang laosheng repertoire; accompanist 梅雨田 Mei Yutian (one of the "four great fiddlers").
- **Mei Lanfang (梅兰芳, 1894–1961)** — greatest qīngyī/dan; with qínshī 徐兰沅 Xu Lanyuan & 王少卿 Wang Shaoqing (who added the erhu to dan accompaniment 1923) reshaped dan arias; *贵妃醉酒 The Drunken Concubine* (a 四平调 aria — 吹腔-derived, outside strict xipi/erhuang) and *霸王别姬 Farewell My Concubine* (sword dance to the jinghu qǔpái 夜深沉).
- **Cheng Yanqiu (程砚秋)** — 程派, famous 哭腔 (crying-tone) and dark revised erhuang; same lyrics set differently per school (依字行腔).
- **Yu Shuyan (余叔岩)** — 脑后音 laosheng school ("空灵, 韵味绵长"); students include 孟小冬 Meng Xiaodong (female laosheng).
- **Yang Baosen (杨宝森) / Ma Lianliang (马连良)** — laosheng schools with house qínshī 杨宝忠 Yang Baozhong and composer-qínshī 李慕良 Li Muliang respectively.
- **Model works (样板戏)** — *智取威虎山 Taking Tiger Mountain by Strategy*: the opening 导板 "穿林海跨雪原气冲霄汉" is a textbook 二黄导板 inside a modern orchestra.
- **Contemporary** — 于魁智, 李胜素 (China National Peking Opera Company), 王珮瑜 (Yu-school laosheng).
- **Scholarship** — Elizabeth Wichmann (*Listening to Theatre*, 1991: text-setting, timbre, heterophony), Huang Jinpei (1989), Dolores Menstell Hsu (1964: drum-conductor), Nancy Guy (1990: qǔpái + 48 entrance patterns), Joshua Goldstein (*Drama Kings*, 2007).

## 5. UnitMatrix mapping

### Voices
- **V0 = Vocal lead (aria)** — role-typed register + ornament vocabulary; 依字行腔 contour; 板眼-aligned phrase ends.
- **V1 = Jinghu (托腔保调)** — heterophonic co-line: contour + densification (2–4× note density), octave lower, 过门 fills, lands 落音 with V0.
- **V2 = Yueqin** — plucked downbeat fills.
- **V3 = Bangu + Ban (drum master / conductor)** — 板眼 timekeeper, tempo authority per section.
- **V4 = Luogu percussion** — 锣鼓经 pattern dictionary (四击头/急急风/冲头/长锤/夺头/乱锤/阴锣/水底鱼), entrance patterns role-typed, 夺头 cues aria entries.
- **V5 = Metadata** — mode, bǎnshì, meter, role, 落音 cadence degrees, luógujīng syllables, qǔpái label, emotion/dramatic function.

### Sections
Columns = the **bǎnshì chain** (aria rhythmic architecture), subdivided into vocal-phrase / 过门 / percussion cells:
S0 导板 (free) → S1 回龙 → S2 慢板 (4/4 centre) → S3 原板 (2/4) → S4 流水/快板 (1/4 climax) → S5 散板 (free close); martial scenes swap interior columns for 急急风 action blocks; a 夺头 percussion column and qǔpái columns (e.g. 水龙吟) precede aria entries. All voices padded to full column length (zero-drift).

### Rules to encode
1. **Mode constraint:** xipi pitch set (la–mi A–E frame, bright mi/do), erhuang (sol–re D–A, dark sol/re), fan-erhuang (do–sol G–D); pentatonic core; 落音 cadence table per mode+bǎnshì; no functional harmony.
2. **Bǎnshì grid:** meter map (4/4, 2/4, 1/4, free); 板 strong / 眼 weak; tempo ladder across the chain.
3. **Couplet prosody:** 7/10-char lines, dǒu 2-2-3/3-3-4; píng → higher/longer/ornamented, zè → lower/shorter; level-tone couplet close; 13-辙 rhyme.
4. **落音 skeleton:** phrase ends on allowed cadence degrees, converging at column boundaries.
5. **Jinghu heterophony:** derived from V0 (contour + densification + 过门); personal "signature" per seed.
6. **Luógujīng:** syllable→instrument dictionary; entrance pattern by rank/personality tag; 夺头 before aria columns; low jitter.
7. **Role-typed ornament:** per-行当 vocabulary; chou spoken cells flagged improvisation.
8. **Zero-drift:** free-rhythm columns (导板/散板/摇板) quantized/rubato-padded to column length; `validate()` must pass.
9. **Emotion→mode mapping** (V5 steers the chain).

### Realization path
Framework row → `UnitMatrixComposer` (6 voices × ~7-section chain) → `fill_voice_section` per cell → `validate()` → `to_midi` → humanize (vocal rubato + wide vibrato; jinghu layback; percussion strict) → FluidSynth render (GM: violin≈jinghu, percussion≈gongs/cymbals; timbre out of scope) → `provenance.json` + grid visualization.

## 6. Table row added

```
| **HC-082** | human (→concrete) | Jingju (Beijing Opera) Aria Composition — Xipi/Erhuang Modes × Banshi Rhythmic-Pattern Chains × Luogujing Percussion Scores × Jinghu Heterophonic Support (托腔保调) | Chinese Jingju (京戲) — ... UNESCO ICH Representative List 2010 | STRUCTURE, RHYTHM, PITCH, TEXTURE (HARMONY emergent) | Learn by oral/aural imitation ... → fix the aria by school tradition | Voice 0 = vocal lead ... Voice 5 = metadata ... Sections = banshi chain columns ... Rules: ... | Tan Xinpei, Mei Lanfang, Cheng Yanqiu, Yu Shuyan, Yang Baosen, Ma Lianliang, model works, 于魁智/李胜素/王珮瑜; Wichmann 1991, Huang Jinpei 1989, Hsu 1964, Guy 1990 | ✅ Documented |
```
(full row appended to `human_methods_db.md` line 88; verified via grep `HC-082` → 1 hit in db + detail + report.)

## 7. Quirks & pitfalls

- **Oral/aural authority:** the aria is co-composed by singer + qínshī in rehearsal, fixed by school tradition — model the machinery, not a fixed score; 依字行腔 legitimately yields different melodies for the same text.
- **Absolute tuning flexible:** jinghu open strings conventionally la–mi (xipi) / sol–re (erhuang) / do–sol (fan erhuang); "key has value only as a technical tool" (singers pitch at range top, accompanists retune). English Wikipedia's A–D / C–G conflicts with the Chinese 6-3 / 5-2 convention — use relative degrees.
- **Free-rhythm bǎnshì vs zero-drift engine:** 导板/散板/摇板 are rubato — grid the orchestra, keep the voice flexible, pad everything or `validate()` fails.
- **四平调 and 南梆子 are neither xipi nor erhuang** (贵妃醉酒 uses 四平调) — don't force every famous aria into the two-mode frame.
- **Bǎnshì names ARE meters**, not chord progressions — encode as grid + cadence skeleton, never functional harmony.
- **Percussion leads:** 夺头/entrance patterns sit BEFORE the vocal columns they introduce.
- **Role register is compositional data:** wrong 行当 register breaks the idiom more than any single pitch.
- Do NOT touch `methods_db.md` (algorithmic DB, owned by another job) — only `human_methods_db.md` modified.

## 8. Verification

- `grep HC-082 human_methods_db.md` → 1 row (appended, ✅ Documented).
- `grep HC-082 human_method_HC-082_jingju-xipi-erhuang-banshi-aria.md` → header + body references.
- `grep HC-082 report_HC-082.md` → this record.
- **Next free ID: HC-083** (max existing = HC-082).
