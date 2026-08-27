# Vector Base Amplitude Panning (VBAP) — Sound Production Method SP-053

> Canonical entry for the Musicom Sound Production Methods Framework. Object-based spatialization layer.
> Standalone companion to `methods_db.md` (detailed section + summary row id **SP-053**).

## One-liner
Place each mono voice as a phantom virtual source in an arbitrary discrete loudspeaker array (2 speakers = 2D pair panning, 3 speakers = 3D triplet panning) by decomposing the source direction into the enclosing speaker-*vector base*; the basis coefficients are constant-power panning gains, solved at $\mathcal{O}(1)$ per source on a Delaunay-triangulated array.

## Paradigm
Post-Processing / DSP — Spatialization (object-based). Amplitude-only: no per-source filters or delays. The object-based gap between binaural HRTF (SP-021), scene-based ambisonics (SP-034), and physical WFS (SP-043).

## Technical Mechanics (full math)

**Setup.** Loudspeaker $k$ at azimuth $\theta_k$, elevation $\phi_k$ → unit direction vector; virtual source $\mathbf{p}$:

$$\mathbf{l}_k = \big(\cos\theta_k \cos\phi_k,\ \sin\theta_k \cos\phi_k,\ \sin\phi_k\big)^\top,\qquad \mathbf{p} = \big(\cos\theta \cos\phi,\ \sin\theta \cos\phi,\ \sin\phi\big)^\top$$

**2D pair-wise panning.** Two adjacent speakers $\mathbf{l}_1,\mathbf{l}_2$ enclose $\mathbf{p}$:

$$\mathbf{p} = g_1\mathbf{l}_1 + g_2\mathbf{l}_2 \implies [\,g_1\ g_2\,] = \mathbf{p}^\top\big[\mathbf{l}_1\ \mathbf{l}_2\big]^{-1}$$

Azimuth-only form (sine law), $\theta_1 < \theta < \theta_2$:

$$g_1 = \frac{\sin(\theta_2 - \theta)}{\sin(\theta_2 - \theta_1)},\qquad g_2 = \frac{\sin(\theta - \theta_1)}{\sin(\theta_2 - \theta_1)}$$

**3D triplet panning.** Three speakers forming a non-degenerate triangle containing $\mathbf{p}$:

$$\mathbf{p} = g_1\mathbf{l}_1 + g_2\mathbf{l}_2 + g_3\mathbf{l}_3 = L_{123}\,\mathbf{g} \implies \mathbf{g} = \mathbf{p}^\top L_{123}^{-1},\qquad L_{123} = \big[\mathbf{l}_1\ \mathbf{l}_2\ \mathbf{l}_3\big],\ \ \mathbf{g}=[g_1,g_2,g_3]\ (\text{row})$$

Triangle valid iff $g_i \ge 0\ \forall i$.

**Constant-power normalization (Pulkki equalized VBAP):**

$$\mathbf{g}' = \frac{\mathbf{g}}{\lVert\mathbf{g}\rVert} \iff g_1^{\prime 2} + g_2^{\prime 2} + g_3^{\prime 2} = 1$$

Center of stereo pair → $g_1 = g_2 = 1/\sqrt2 \approx 0.707$. Equal-power form of the tangent law $\tan\theta / \tan\theta_0 = (g_1 - g_2)/(g_1 + g_2)$. Constant-amplitude ($\sum g_i = 1$) bumps center loudness — avoid.

**Mesh selection.** Delaunay-triangulate the speaker vectors once. Per source, find containing simplex via barycentric-coordinate test (all $\ge 0$); precompute $L_{123}^{-1}$ per triangle. Gains continuous across shared edges → click-free source morph; active-speaker-set change happens exactly on an edge.

**Hybrid panning (elevation).** With only a horizontal ring + high speakers: build a *virtual loudspeaker* $\mathbf{p}_v \parallel g_1'\mathbf{l}_1 + g_2'\mathbf{l}_2$ (two real speakers summed), then 2D-pan the elevated source between $\mathbf{p}_v$ and a real high speaker.

**Distance (optional).** $g_i^{(d)} = g_i \cdot d_{\text{ref}}/d$, per-speaker delay $\Delta t_i = d_i / c$. Headphone reproduction folds summed channels through per-speaker HRTFs (SP-021).

**Complexity:** precompute $\mathcal{O}(T)$ (invert $T$ triangle matrices); $\mathcal{O}(1)$ per source per sample. Memory $\mathcal{O}(K + T)$ for $K$ speakers, $T$ triangles.

## Python / NumPy implementation sketch

```python
import numpy as np
from scipy.spatial import Delaunay

def speaker_vec(az, el):
    ce = np.cos(el)
    return np.array([np.cos(az) * ce, np.sin(az) * ce, np.sin(el)])

class VBAP:
    """Vector Base Amplitude Panning (SP-053)."""
    def __init__(self, speaker_az, speaker_el):
        self.ls = np.array([speaker_vec(a, e)
                            for a, e in zip(speaker_az, speaker_el)])      # (K,3)
        if self.ls.shape[0] < 3:
            self.tri, self.inv = None, None
        else:
            self.tri = Delaunay(self.ls)
            self.inv = [np.linalg.inv(self.ls[sim]) for sim in self.tri.simplices]

    def gains(self, az, el):
        p = speaker_vec(az, el)
        if self.tri is None:                                           # 2D ring fallback
            a = np.arctan2(self.ls[:, 1], self.ls[:, 0]) % (2 * np.pi)
            pa = np.arctan2(p[1], p[0]) % (2 * np.pi)
            idx = np.argsort(a)
            for a1, a2 in zip(idx, np.roll(idx, -1)):
                lo, hi = a[a1], a[a2]
                if hi < lo: hi += 2 * np.pi
                pa2 = pa if pa >= lo else pa + 2 * np.pi
                if lo <= pa2 <= hi:
                    w = np.array([np.sin(hi - pa2), np.sin(pa2 - lo)])
                    w /= np.linalg.norm(w)                             # constant power
                    return [a1, a2], w
            return None, np.zeros(2)
        for sim, inv in zip(self.tri.simplices, self.inv):
            g = p @ inv                                               # p^T L^{-1}
            if np.all(g > -1e-9):
                g = np.clip(g, 0.0, None)
                n = np.linalg.norm(g)
                return sim, (g / n if n > 1e-12 else g)
        return None, np.zeros(3)

    def render(self, sig, az, el):
        K = len(self.ls)
        out = np.zeros((K, len(sig)))
        for n in range(len(sig)):
            sim, g = self.gains(az[n], el[n])
            if sim is not None:
                np.add.at(out, sim, g * sig[n])
        return out                                                    # (K, N) per-speaker
```

**Tooling:** NumPy + SciPy Delaunay. Vectorize by precomputing per-triangle gains for a whole trajectory block and advanced-indexing; JIT (Numba) or move to C for many sources. musicom engine supplies the symbolic UnitMatrix + zero-drift MIDI upstream; VBAP is a downstream placement layer between mono renders and the spatial mix.

## Musical Elements Framework
- **PITCH** — amplitude-only, pitch untouched; register↔space map as "spatial EQ" (bass front-center, highs wide/rear).
- **RHYTHM** — continuous-time, grid-free; onset-locked jumps, tempo-synced LFO pan, bar-step automations.
- **HARMONY** — spatial harmony: chord voices spread to distinct azimuth (equiangular triad = max separation; narrow spread = mono phantom blend).
- **STRUCTURE** — spatial macro-form: verse = narrow front, chorus = full-width, bridge = elevated/rear, cadence = collapse to center.
- **TEXTURE** — spatial density: source count, angular spread, distance, motion speed, per-voice reverb send.

## UnitMatrix Integration (Voices & Sections)
- Rows = voices → independent sources with `az/el/d` trajectories.
- Columns = sections → spatial scenes (azimuth band, spread width, elevation, speed, distance).
- Cells $U_{v,s}$: `{PITCH}`=register→band, `{RHYTHM}`=pan keyframe timing, `{HARMONY}`=azimuth spread, `{TEXTURE}`=width/distance/reverb-send.
- Flow: UnitMatrix → validate → MIDI (musicom) → per-voice mono render (SP-029/016/010…) → VBAP pan per cell trajectory → sum channels → HRTF fold-down (SP-021) / decode (SP-034).

## Pitfalls
1. Degenerate triangles ($|\det L| \to 0$) → skip simplicies below threshold.
2. Edge-crossing clicks → equal-power crossfade across shared edge.
3. Normalization error ($\sum g_i=1$ vs $\sum g_i^2=1$) → center loudness bump; always normalize $\lVert\mathbf{g}\rVert$.
4. Off-sweet-spot instability → keep small listening area; HRTF for headphones.
5. No elevation without top speakers → hybrid virtual-loudspeaker panning.
6. Front–back confusion → add HRTF + distance reverb.
7. Per-sample Python loop slow → precompute inverses, cache triangle per source, vectorize blocks.

## References
- Pulkki, V. (1997). "Virtual Sound Source Positioning Using Vector Base Amplitude Panning." *J. Audio Eng. Soc.* 45(6), 456–466.
- Pulkki, V. (2000). "Generic Panning Tools for MAX/MSP." *Proc. ICMC*, Berlin.
- Pulkki, V. (2001). "Localization of Amplitude-Panned Virtual Sources II: Two- and Three-Dimensional Panning." *J. Audio Eng. Soc.* 49(9), 753–767.
- Pulkki, V., & Karjalainen, M. (2015). *Communication Acoustics.* Wiley.
- Zotter, F., & Frank, M. (2019). *Ambisonics.* Springer.