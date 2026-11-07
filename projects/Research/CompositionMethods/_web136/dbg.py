import numpy as np
from scipy.special import jn_zeros

def solve(sigma, k, xi, N=1400, m_values=(0,1,2)):
    h = 1.0 / N
    r = (np.arange(N) + 0.5) * h
    rho = 1.0 + (sigma**2 - 1.0) / 2.0 * (1.0 - np.tanh((r - k) / xi))
    res = {}
    for m in m_values:
        A = np.zeros((N, N))
        for i in range(N):
            rip, rim = r[i] + 0.5*h, r[i] - 0.5*h
            if i+1 < N: A[i, i+1] += -rip/(r[i]*h*h)
            if i > 0:   A[i, i-1] += -rim/(r[i]*h*h)
            A[i, i] += (rip+rim)/(r[i]*h*h) + m*m/(r[i]**2)
        B = np.diag(rho)
        lam = np.linalg.eigvals(np.linalg.solve(B, A))
        lam = np.sort(np.real(lam[lam > 1e-6]))
        res[m] = np.sqrt(lam[:5])
    return res

for sig,k,xi in [(1.0,0.492,0.091),(2.57,0.492,0.091),(3.125,0.4,0.091),(3.4,0.5,0.05)]:
    r = solve(sig,k,xi)
    print(f"sigma={sig} k={k} xi={xi}")
    for m,v in r.items():
        print("   m=%d:"%m, np.round(v,4), " ratios vs m0n1:", np.round(v/r[0][0],3))
