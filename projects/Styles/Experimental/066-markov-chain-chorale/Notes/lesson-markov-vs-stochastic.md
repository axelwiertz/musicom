# Lesson — Markov Chain vs Uniform Stochastic

Comparison with project 065 (Method 001, uniform stochastic):

| | 065 Uniform Monte Carlo | 066 First-Order Markov |
|---|---|---|
| Memory | none (i.i.d.) | Markov property (state → state) |
| Contour | random leaps | stepwise-neighbour walk |
| Chromatic leak | ~maximal | partial (escape states) |
| Raw melody character | chaotic, uncorrelated | coherent wandering line |
| Phase 2 effect | hard to tame | easy to tame (raw already mostly stepwise) |

**What to listen for in Phase 2:** the soprano line keeps a stepwise, singing
contour (a residue of the Markov walk) while the block-harmony texture is
entirely rules-controlled. 0 voice-leading violations after Phase 2c.

**Next variable to try:** a second-order (memory-2) Markov chain, or a
longer/looser transition matrix to raise chromatic variety.