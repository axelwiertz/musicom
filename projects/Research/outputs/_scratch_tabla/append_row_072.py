import io

ROW = (
    "| HC-072 | human (→concrete) | Tabla Solo Composition — Gharana Theme-and-Variation Architecture "
    "(Peshkar → Kayda → Rela → Gat/Tukra with Tihai & Chakradar Cadence Math) | "
    "Hindustani (North Indian) classical tabla solo — six gharanas (Delhi, Ajrada, Farrukhabad, Lucknow, "
    "Benares/Purbi, Punjab), 18th c.–present; oral guru–shishya transmission with bol mnemonics as the notation | "
    "RHYTHM, STRUCTURE, TEXTURE, PITCH | "
    "Fix frame (tala + vibhag tali/khali map, laya, theka, gharana idiom) → compose the main bol / parent composition "
    "(2–4 main phrases, each half ending in a main-bol ending phrase: tuna/dhinna, tinna/dhinna, "
    "tuna kata/dhinna kata, tinna kina/dhinna gina) → split into tali + khali halves by changing ONLY the baya stroke "
    "on counterpart bols (dayan strokes identical) → check the vibhag stress pattern tali-tali-khali-tali and that the "
    "theme is 16 matras AT SOME LAYA (16 at 1x, 8 at 2x, 4 at 4x) → generate variations systematically, largest unit "
    "first (dohra = first quarter ×2 + main bol → first-phrase variations → second-phrase variations → gap variations → "
    "new main bol from a sub-phrase), using only repeat / rearrange / substitute / invert / add-gaps on the theme's bols → "
    "climb the layakari ladder monotonically: barabar (2:1, 4:1, 8:1) → aralay (3:1, 6:1, 12:1) → compose the cadence "
    "backward from sam: tihai (3p+2r = 16n dumdaar; 3p = 16n bedum; start phase free, e.g. 4-2-4-2-4 or 2-5-2-5-2), "
    "anagat (same shape landing one matra early), chakradar (3 × (mukhra + tihai), tintal 3×21+2 = 65 = 64+1) → "
    "assemble the solo arc: uthan → peshkar (blueprint not theme, non-theme bols allowed, incomplete tihai where the final "
    "dha is replaced by the theme's first bol) → kayda → rela (flowing unbroken chain, no cadential gaps) → gat/tukra/paran → "
    "final tihai on sam → recite the bols aloud (padhant) and only then play the chain from memory, doubling laya at "
    "section seams | "
    "V0 = Daya treble bol stream (spine: the phrase identity; strokes invariant between tali and khali halves). "
    "V1 = Baya open/closed strokes (form layer: open = tali, closed = khali — the stress/form is literally in this voice, "
    "not in velocity). V2 = Padhant recited bol (memory/surface layer, speech-like timbre, doubles V0 1:1). "
    "V3 = Theka reference grid (alignment oracle; muted in true solo). V4 = Sam/tali markers (colotomic, one event per vibhag). "
    "V5 = Nagma/lehera pitch bed (optional, Sa on sam). Sections = one composition unit each: S0 Uthan → S1 Peshkar theme → "
    "S2 Peshkar improvisation → S3 Kayda theme → S4 Dohra → S5–S8 phrase-1 variations → S9–S12 phrase-2 variations → "
    "S13 gap variations → S14 new main bol + its variations → S15 rela theme + variations → S16 gat/tukra/paran → "
    "S17 chakradar → S18 final tihai. Cells = one matra (480 ticks at 4/4); tintal avartana = 16 matras = 4 bars = 7680 ticks; "
    "cells subdivide by bol density (4:1 = 4 events, 12:1 = 12 events per matra). Rules: avartana lock "
    "(section length ≡ 0 mod avartana_ticks), vibhag stress gate (tintal vibhag 3 = zero open-baya events; vibhags 1, 2, 4 ≥ 1), "
    "tali-khali counterpart transform (dha→ta, dhin→tin, dhinna→tuna with V0 asserted identical), main-bol ending-phrase "
    "whitelist (closed form on the first half, its open counterpart on the second), kayda vocabulary closure + explicit "
    "peshkar exemption, systematic development order with no skipped rung, layakari ladder monotonic over {2,3,4,6,8,12} "
    "dividing the matra evenly, tihai/anagat/chakradar arithmetic gates, sam convergence (cadential final stroke ≡ 0 mod "
    "avartana), tempo doubling only at section seams, zero-drift validate per section | "
    "Pandit Ram Sahai (Benares founder, 1780–1826: six months' seclusion to redesign fingering — na with curved ring finger — "
    "then composed new forms uthan, Benarsi theka, fard, plus gats/tukras/parans), Ustad Ahmedjan Thirakwa (Farrukhabad peshkar; "
    "credited with the incomplete tihai; theme ↔ non-theme bols in 12:1), Pandit Chhotelal Misra (new main bol technique; "
    "Tal Prabandh 2006; 1978 BHU peshkar solo following the classical outline), Pandit Kishan Maharaj (tihai and chakradar "
    "calculation in live solo; Taal Vadya Kacheri with Palghat R. Raghu), Ustad Alla Rakha & Ustad Zakir Hussain (Punjab peshkar "
    "layakari, pakhawaj-derived relas, globalised solo format), Ustad Mian Shaukat Hussain Khan (self-composed tite-dhete qaydas, "
    "low-tuned wrist-worked bayan), Ustad Habibuddin Khan (Ajrada: gheghe tit kit composites, 3:1/6:1 divisions, extra third line, "
    "bayan work), Anokhelal Mishra, Samta Prasad, Anindo Chatterjee, Swapan Chaudhuri; scholars Rebecca Stewart (The Tabla in "
    "Perspective 1974, cyclic vs cadential), James Kippen (The Tabla of Lucknow 1988, pseudo-tihai), Gert-Matthias Wegner "
    "(Vintage Tabla Repertory 2004), Sadanand Naimpalli (2005/2009), Sudhir Kumar Saxena (2006), David R. Courtney (2002), "
    "Robert S. Gottlieb (1977/1993) | ✅ Documented |"
)

path = "/opt/data/projects/Research/CompositionMethods/human_methods_db.md"
with io.open(path, "r", encoding="utf-8") as f:
    txt = f.read()
if "HC-072" in txt:
    raise SystemExit("HC-072 already present — abort")
if not txt.endswith("\n"):
    txt += "\n"
txt += ROW + "\n"
with io.open(path, "w", encoding="utf-8") as f:
    f.write(txt)
print("appended; rows:", txt.count("\n| HC-") + txt.count("\n| **HC-"))
print("cols:", ROW.count("|"))
