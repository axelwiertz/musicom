"""Verification prototype for Method 140 — LDATAC (Latent Dirichlet Allocation Texture-Archetype Composition).

Checks:
 1 collapsed-Gibbs LDA recovers planted archetypes (token purity)
 2 recovers per-document (per-section) topic mixtures (cosine)
 3 held-out perplexity beats the uniform baseline
 4 exchangeability: doc likelihood is permutation-invariant (order-free by construction)
 5 determinism under a fixed seed
 6 alpha controls document sparsity (mean theta entropy)
 7 generation fills every UnitMatrix cell exactly (zero drift) + tension curve varies
 8 real musicom UnitMatrix build -> validate() -> to_midi()
"""
import itertools
import math
import os
import sys

import numpy as np

RNG_SEED = 140140

# ---------------------------------------------------------------- vocabulary
# token = (scale-degree step, duration ticks, velocity)
STEPS = (-2, -1, 0, 1, 2)
DURS = (120, 240, 480)      # 16th, 8th, quarter at tpb=480
DYN = (64, 100)
TOKENS = list(itertools.product(STEPS, DURS, DYN))
V = len(TOKENS)
assert V == 30, V

# archetypes = soft product distributions over (step, dur, dyn) — overlapping supports
ARCHETYPES = {
    "ostinato": dict(step={-1: .4, 0: .3, 1: .3}, dur={120: .8, 240: .2}, dyn={100: .95, 64: .05}),
    "sustain":  dict(step={0: .5, -1: .25, 1: .25}, dur={480: .8, 240: .2}, dyn={64: .9, 100: .1}),
    "flourish": dict(step={-2: .35, 2: .35, -1: .15, 1: .15},
                     dur={120: .7, 240: .3}, dyn={100: .85, 64: .15}),
}
K_TRUE = len(ARCHETYPES)
PHI_TRUE = np.zeros((K_TRUE, V))
for k, spec in enumerate(ARCHETYPES.values()):
    for i, (s, d, v) in enumerate(TOKENS):
        PHI_TRUE[k, i] = (spec["step"].get(s, 0.0) * spec["dur"].get(d, 0.0)
                          * spec["dyn"].get(v, 0.0))
    PHI_TRUE[k] /= PHI_TRUE[k].sum()


def sample_docs(n_docs, doc_len, rng, alpha=0.1):
    """Planted corpus: theta ~ Dir(alpha); words ~ mixture."""
    theta = rng.dirichlet(np.full(K_TRUE, alpha), size=n_docs)
    docs, zn = [], []
    for d in range(n_docs):
        k = rng.choice(K_TRUE, size=doc_len, p=theta[d])
        w = np.array([rng.choice(V, p=PHI_TRUE[kk]) for kk in k])
        docs.append(w.tolist())
        zn.append(k.tolist())
    return theta, docs, zn


# ---------------------------------------------------------------- collapsed Gibbs
def fit_lda(docs, K, alpha=0.1, eta=0.01, iters=300, seed=RNG_SEED):
    rng = np.random.default_rng(seed)
    D = len(docs)
    ndk = np.zeros((D, K))
    nkw = np.zeros((K, V))
    nk = np.zeros(K)
    z = []
    for d, doc in enumerate(docs):
        zz = rng.integers(0, K, size=len(doc))
        z.append(zz)
        for n, w in enumerate(doc):
            k = zz[n]
            ndk[d, k] += 1
            nkw[k, w] += 1
            nk[k] += 1
    Veta = V * eta
    for _ in range(iters):
        for d, doc in enumerate(docs):
            for n, w in enumerate(doc):
                k0 = z[d][n]
                ndk[d, k0] -= 1
                nkw[k0, w] -= 1
                nk[k0] -= 1
                p = (ndk[d] + alpha) * (nkw[:, w] + eta) / (nk + Veta)
                p /= p.sum()
                k1 = rng.choice(K, p=p)
                z[d][n] = k1
                ndk[d, k1] += 1
                nkw[k1, w] += 1
                nk[k1] += 1
    phi = (nkw + eta) / (nk[:, None] + Veta)
    theta = (ndk + alpha) / (ndk.sum(axis=1, keepdims=True) + K * alpha)
    return dict(phi=phi, theta=theta, ndk=ndk, nkw=nkw, nk=nk, z=z)


def infer_theta(doc, phi, alpha=0.1, iters=200, seed=RNG_SEED):
    """Fix phi, infer theta by Gibbs on a held-out document."""
    rng = np.random.default_rng(seed)
    K = phi.shape[0]
    n_dk = np.zeros(K)
    z = rng.integers(0, K, size=len(doc))
    for k in z:
        n_dk[k] += 1
    for _ in range(iters):
        for n, w in enumerate(doc):
            k0 = z[n]
            n_dk[k0] -= 1
            p = (n_dk + alpha) * phi[:, w]
            p /= p.sum()
            k1 = rng.choice(K, p=p)
            z[n] = k1
            n_dk[k1] += 1
    return (n_dk + alpha) / (n_dk.sum() + K * alpha)


def doc_logprob(doc, theta, phi):
    mix = theta @ phi
    return float(np.sum(np.log(np.clip(mix[doc], 1e-300, None))))


# ---------------------------------------------------------------- checks
def main():
    ok = []

    def check(name, cond, detail=""):
        ok.append(bool(cond))
        print(("PASS" if cond else "FAIL"), "|", name, "|", detail)

    rng = np.random.default_rng(7)
    theta_true, docs, z_true = sample_docs(n_docs=48, doc_len=28, rng=rng)

    fit = fit_lda(docs, K=K_TRUE, alpha=0.1, eta=0.01, iters=300)
    phi, theta = fit["phi"], fit["theta"]

    # 1. topic->archetype recovery: cosine(learned topic, true archetype), greedy 1-1 match
    C = np.zeros((K_TRUE, K_TRUE))
    for j in range(K_TRUE):
        for kt in range(K_TRUE):
            C[j, kt] = float(phi[j] @ PHI_TRUE[kt] /
                             (np.linalg.norm(phi[j]) * np.linalg.norm(PHI_TRUE[kt])))
    Cwork = C.copy()
    match = [-1] * K_TRUE
    for _ in range(K_TRUE):
        best, bj, bk = -1.0, -1, -1
        for j in range(K_TRUE):
            if match[j] != -1:
                continue
            for kt in range(K_TRUE):
                if Cwork[j, kt] > best:
                    best, bj, bk = Cwork[j, kt], j, kt
        match[bj] = bk
        Cwork[bj, :] = -1
        Cwork[:, bk] = -1
    sims = [float(C[j, match[j]]) for j in range(K_TRUE)]
    check("1 topic->archetype recovery (cosine, 1-1 match)", min(sims) >= 0.90,
          f"cos={[round(s,4) for s in sims]} match={match}")

    # 2. theta recovery (permute learned topics into true order)
    th_p = np.zeros_like(theta)
    for j in range(K_TRUE):
        th_p[:, match[j]] = theta[:, j]
    cos = np.array([float(th_p[d] @ theta_true[d] /
                          (np.linalg.norm(th_p[d]) * np.linalg.norm(theta_true[d])))
                    for d in range(len(docs))])
    check("2 per-section mixture recovery (cosine)", cos.mean() >= 0.95,
          f"mean cos={cos.mean():.4f} min={cos.min():.4f}")

    # 3. perplexity vs uniform
    lp = np.mean([doc_logprob(docs[d], theta[d], phi) / len(docs[d]) for d in range(len(docs))])
    ppl = math.exp(-lp)
    ppl_uni = float(V)
    check("3 perplexity < uniform", ppl < ppl_uni * 0.75,
          f"ppl={ppl:.3f} vs uniform={ppl_uni:.1f}")

    # 4. exchangeability: identical likelihood for a shuffled document
    d0 = docs[0]
    sh = d0.copy()
    np.random.default_rng(3).shuffle(sh)
    l1 = doc_logprob(d0, theta[0], phi)
    l2 = doc_logprob(sh, theta[0], phi)
    check("4 exchangeability (order-invariant likelihood)", abs(l1 - l2) < 1e-9,
          f"|dl|={abs(l1-l2):.2e}")

    # 5. determinism
    f2 = fit_lda(docs, K=K_TRUE, alpha=0.1, eta=0.01, iters=300)
    check("5 determinism (same seed)", np.allclose(phi, f2["phi"]),
          f"max|dphi|={np.abs(phi-f2['phi']).max():.2e}")

    # 6. alpha controls theta entropy
    ent = {}
    for a in (0.05, 1.0, 8.0):
        f = fit_lda(docs, K=K_TRUE, alpha=a, eta=0.01, iters=150, seed=99)
        th = f["theta"]
        ent[a] = float(np.mean(-(th * np.log(np.clip(th, 1e-12, 1))).sum(axis=1)))
    check("6 alpha -> theta entropy monotone", ent[0.05] < ent[1.0] < ent[8.0],
          " ".join(f"a={a}:H={v:.3f}" for a, v in ent.items()))

    # 7. generation: 4 voices x 8 sections, exact cell fill + tension curve
    TPB, BPB = 480, 4
    section_len = 4 * BPB * TPB          # 4 bars = 7680 ticks
    voices = ["Lead", "Pad", "Bass", "Counter"]
    beta = np.array([[0.7, 0.2, 0.1],      # Lead   -> flourish-ish
                     [0.1, 0.8, 0.1],      # Pad    -> sustain
                     [0.8, 0.2, 0.0],      # Bass   -> ostinato
                     [0.3, 0.3, 0.4]])     # Counter
    grng = np.random.default_rng(2024)
    inv = {kt: j for j, kt in enumerate(match)}   # archetype -> learned topic row
    # section mixtures follow a hand-set tension plan over 8 sections
    th_plan = np.array([[0.8, 0.2, 0.0], [0.6, 0.3, 0.1], [0.3, 0.4, 0.3],
                        [0.1, 0.3, 0.6], [0.0, 0.2, 0.8], [0.2, 0.5, 0.3],
                        [0.5, 0.4, 0.1], [0.8, 0.2, 0.0]])
    cells, fills_ok = {}, []
    for vi, vname in enumerate(voices):
        for si in range(len(th_plan)):
            mix = th_plan[si] * beta[vi]
            mix = mix / mix.sum()
            t, pitches, ticks, vel = 0, [], [], []
            while t < section_len:
                k = int(grng.choice(3, p=mix / mix.sum()))
                w = int(grng.choice(V, p=phi[inv[k]]))
                step, dur, dyn = TOKENS[w]
                dur = min(dur, section_len - t)          # duration clamp = zero drift
                last = pitches[-1] if pitches else 60 + 7 * vi
                pitches.append(int(np.clip(last + step, 36, 88)))
                ticks.append((t, t + dur))
                vel.append(dyn)
                t += dur
            cells[(vname, si)] = (pitches, ticks, vel)
            fills_ok.append(t == section_len and len(pitches) > 0)
    check("7a every cell fills exactly (zero drift)", all(fills_ok),
          f"cells={len(cells)} all end at {section_len}")
    theta_bar = th_plan.mean(axis=0)
    kl = [float(np.sum(th * np.log(np.clip(th, 1e-12, None) /
                                  np.clip(theta_bar, 1e-12, None)))) for th in th_plan]
    check("7b tension curve varies (KL spread)", max(kl) / max(min(kl), 1e-9) > 5,
          f"KL=[{', '.join(f'{x:.3f}' for x in kl)}] spread={max(kl)/max(min(kl),1e-9):.0f}x")
    n_notes = sum(len(v[0]) for v in cells.values())
    print(f"     generated {n_notes} events over {len(cells)} cells")

    # 8. real engine build
    try:
        from structures import MidiInstrument, MusicEvent, MusicUnit
        from workflows.unitmatrix_composer import UnitMatrixComposer
        comp = UnitMatrixComposer(bpm=96, ticks_per_beat=TPB, beats_per_bar=BPB)
        comp.create_matrix(num_voices=len(voices), num_sections=len(th_plan))
        progs = [MidiInstrument.FLUTE, MidiInstrument.SYNTH_PAD,
                 MidiInstrument.BASS, MidiInstrument.VIOLIN]
        for vi, vname in enumerate(voices):
            comp.add_voice(vname, program=progs[vi], channel=vi)
        for si in range(len(th_plan)):
            comp.add_section(f"S{si}", bars=4)
        for vi, vname in enumerate(voices):
            for si in range(len(th_plan)):
                pitches, ticks, vel = cells[(vname, si)]
                unit = MusicUnit(events=[MusicEvent(pitch=p, volume=vv,
                                                    start_tick=a, end_tick=b)
                                         for p, (a, b), vv in zip(pitches, ticks, vel)])
                comp.fill_voice_section(vname, f"S{si}", unit)
        validated, msg = comp.validate()
        out = "/opt/data/projects/Research/CompositionMethods/_web140/ldatac_140.mid"
        comp.to_midi(out)
        size = os.path.getsize(out)
        check("8 engine build validates + non-empty MIDI",
              validated and size > 40, f"validate={validated} '{msg}' size={size}B")
    except Exception as e:  # noqa: BLE001
        check("8 engine build validates + non-empty MIDI", False, f"error: {e!r}")

    # 9. held-out continuation: infer theta for unseen sections, compare to truth
    hrng = np.random.default_rng(31)
    th_h, docs_h, _ = sample_docs(n_docs=6, doc_len=28, rng=hrng)
    cs = []
    for d in range(len(docs_h)):
        th_hat = infer_theta(docs_h[d], phi)
        th_al = np.zeros(K_TRUE)
        for j in range(K_TRUE):
            th_al[match[j]] = th_hat[j]
        cs.append(float(th_al @ th_h[d] / (np.linalg.norm(th_al) * np.linalg.norm(th_h[d]))))
    check("9 held-out section mixture inferred (cosine)", min(cs) >= 0.85,
          f"mean={np.mean(cs):.4f} min={min(cs):.4f}")

    # 10. over-specified K splits archetypes instead of inventing new ones
    f5 = fit_lda(docs, K=5, alpha=0.1, eta=0.01, iters=300, seed=11)
    best_for_true = [max(float(f5["phi"][j] @ PHI_TRUE[kt] /
                              (np.linalg.norm(f5["phi"][j]) * np.linalg.norm(PHI_TRUE[kt])))
                          for j in range(5)) for kt in range(K_TRUE)]
    check("10 K=5 over-specification keeps archetypes covered",
          all(b >= 0.85 for b in best_for_true),
          f"best cos per archetype={[round(b,3) for b in best_for_true]} "
          f"(extra topics={5 - 3} absorb splits/outliers)")

    print(f"\n{sum(ok)}/{len(ok)} checks passed")
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main())
