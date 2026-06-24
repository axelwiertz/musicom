"""
Pitch Class Set Theory Analysis
Based on Straus, Forte, and the documents in in/Docs (Analyzing Atonal Music).
"""

from typing import List, Tuple
import itertools

class SetTheoryAnalyst:
    """Analytical engine for atonal pitch class sets."""

    @staticmethod
    def normal_form(pcs: List[int]) -> List[int]:
        """Arranges pitch classes into their most compact form."""
        if not pcs: return []
        unique_pcs = sorted(list(set([p % 12 for p in pcs])))
        n = len(unique_pcs)
        best_form = None
        min_span = 13
        
        # Test every rotation
        for i in range(n):
            rotation = unique_pcs[i:] + unique_pcs[:i]
            span = (rotation[-1] - rotation[0]) % 12
            if span < min_span:
                min_span = span
                best_form = rotation
            elif span == min_span:
                # Tie-breaker: check smaller intervals from the bottom
                for j in range(n - 2, 0, -1):
                    span_j_best = (best_form[j] - best_form[0]) % 12
                    span_j_curr = (rotation[j] - rotation[0]) % 12
                    if span_j_curr < span_j_best:
                        best_form = rotation
                        break
                    elif span_j_curr > span_j_best:
                        break
        return [(p - best_form[0]) % 12 for p in best_form] # Transposed to 0 for NF? 
        # Actually NF is typically untransposed, Prime Form is transposed.
        # Adjusted: return the actual rotation.
        return best_form

    @staticmethod
    def prime_form(pcs: List[int]) -> List[int]:
        """Calculates the canonical Prime Form (transposed to 0 and most left-packed)."""
        if not pcs: return []
        
        def to_zero(s):
            return sorted([(p - s[0]) % 12 for p in s])
        
        nf = SetTheoryAnalyst.normal_form(pcs)
        nf_zero = to_zero(nf)
        
        # Invert and get normal form of inversion
        inv = sorted([(12 - p) % 12 for p in nf])
        inf = SetTheoryAnalyst.normal_form(inv)
        inf_zero = to_zero(inf)
        
        # Choose the more "left-packed" one
        for i in range(len(nf_zero)):
            if nf_zero[i] < inf_zero[i]: return nf_zero
            if inf_zero[i] < nf_zero[i]: return inf_zero
        return nf_zero

    @staticmethod
    def interval_vector(pcs: List[int]) -> List[int]:
        """Calculates the Interval Class Vector (ICV).
        Represents counts of interval classes 1 through 6.
        """
        vector = [0] * 6
        unique_pcs = list(set([p % 12 for p in pcs]))
        for p1, p2 in itertools.combinations(unique_pcs, 2):
            interval = abs(p1 - p2) % 12
            if interval > 6: interval = 12 - interval
            if interval > 0:
                vector[interval - 1] += 1
        return vector
