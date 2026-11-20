import numpy as np
import sts_prototype as S

x = S.make_target()
H = S.band_gains(S.N)
tgt = {"x": x, "H": H}
tgt.update(S.stats_of(x, H))
y, errs, E = S.synthesise(tgt, outer=1, inner=15)

for name, sig in (("x", x), ("y", y)):
    sp = np.abs(np.fft.rfft(sig)) ** 2
    fr = np.fft.rfftfreq(sig.size, 1 / S.FS)
    tot = sp.sum()
    print(name, "centroid", (sp * fr).sum() / tot, "rms", np.sqrt((sig**2).mean()))
    # octave band energy fractions
    for lo, hi in ((60, 250), (250, 1000), (1000, 4000), (4000, 8000), (8000, 11025)):
        m = (fr >= lo) & (fr < hi)
        print(f"   {lo:5d}-{hi:5d}: {sp[m].sum()/tot*100:6.2f}%")
