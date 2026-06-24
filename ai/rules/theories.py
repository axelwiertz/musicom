"""
Musicom AI Rules - Codification of Musical Theory
Consolidating Hindemith, Schoenberg, Fux, Jeppesen, and Adler.
"""

from typing import List, Tuple
import numpy as np

class HarmonyRules:
    """Rules derived from Hindemith and the Complete Idiot's Guide."""
    
    CHORD_LEADING = {
        'I':   ['ii', 'iii', 'iv', 'v', 'vi', 'vii_dim'],
        'ii':  ['v', 'vii_dim'],
        'iii': ['vi', 'ii', 'IV'],
        'IV':  ['v', 'vii_dim', 'I', 'ii'],
        'V':   ['I', 'vi'],
        'vi':  ['ii', 'IV', 'V', 'I'],
        'vii_dim': ['I', 'iii']
    }

    @staticmethod
    def get_hindemith_group(pitches: List[int]) -> str:
        """Classifies chords into Hindemith's tension groups (I, II, III)."""
        if not pitches: return "Empty"
        p = sorted([pt % 12 for pt in pitches])
        intervals = []
        for i in range(len(p)):
            for j in range(i + 1, len(p)):
                intervals.append((p[j] - p[i]) % 12)
        
        has_tritone = 6 in intervals
        has_sec_sev = any(i in [1, 2, 10, 11] for i in intervals)
        
        if not has_tritone and not has_sec_sev: return "Group I"
        if not has_tritone and has_sec_sev: return "Group II"
        return "Group III"

class CounterpointRules:
    """Species Counterpoint rules (Fux/Jeppesen)."""
    
    @staticmethod
    def check_parallels(voice1: List[int], voice2: List[int]) -> List[str]:
        """Detects parallel 5ths and octaves."""
        errors = []
        for i in range(1, len(voice1)):
            prev_int = abs(voice1[i-1] - voice2[i-1]) % 12
            curr_int = abs(voice1[i] - voice2[i]) % 12
            
            if prev_int == curr_int and prev_int in [0, 7]:
                if voice1[i] != voice1[i-1]: # Only if moving
                    interval_name = "Octave" if prev_int == 0 else "Fifth"
                    errors.append(f"Parallel {interval_name} at index {i}")
        return errors

class StructuralRules:
    """Motivic development (Schoenberg)."""
    
    @staticmethod
    def derive_variations(motif: List[int]) -> dict:
        """Returns Inverse, Retrograde, and Retro-Inverse variations."""
        axis = motif[0]
        inv = [(2 * axis - p) for p in motif]
        ret = motif[::-1]
        ret_inv = inv[::-1]
        return {
            "original": motif,
            "inversion": inv,
            "retrograde": ret,
            "retro_inversion": ret_inv
        }
