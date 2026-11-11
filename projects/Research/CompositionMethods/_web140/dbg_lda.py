import numpy as np
import importlib.util
spec = importlib.util.spec_from_file_location("v", "/opt/data/projects/Research/CompositionMethods/_web140/verify_140_LDATAC.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

rng = np.random.default_rng(7)
theta_true, docs, z_true = m.sample_docs(n_docs=48, doc_len=28, rng=rng)
print("true archetype top tokens:")
for k in range(m.K_TRUE):
    top = np.argsort(-m.PHI_TRUE[k])[:6]
    print(k, [(m.TOKENS[i], round(m.PHI_TRUE[k, i], 4)) for i in top])

fit = m.fit_lda(docs, K=3, alpha=0.1, eta=0.01, iters=300)
for k in range(3):
    top = np.argsort(-fit["phi"][k])[:6]
    print("LEARNED", k, "nk=", round(fit["nk"][k], 1), [(m.TOKENS[i], round(fit["phi"][k, i], 4)) for i in top])

print("theta true[0:3]", np.round(theta_true[:3], 3))
print("theta fit [0:3]", np.round(fit["theta"][:3], 3))
print("doc0 tokens:", docs[0][:12])
print("z_true[0][:12]", z_true[0][:12])
print("z_fit [0][:12]", fit["z"][0][:12])
