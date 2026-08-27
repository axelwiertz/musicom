import numpy as np

def generate_euclidean_rhythm(pulses, steps):
    """Bjorklund's algorithm for Euclidean rhythms."""
    pattern = []
    counts = [pulses, steps - pulses]
    remainders = [pulses, steps - pulses]
    
    if pulses > steps: return []
    
    # Simple binary representation
    res = [1] * pulses + [0] * (steps - pulses)
    
    # For visualization, we keep it simple for DNA markers
    dna = ""
    for i in range(steps):
        if (i * pulses) % steps < pulses:
            dna += "█"
        else:
            dna += "░"
    return dna

def create_dna_marker(name, pulses, steps):
    dna = generate_euclidean_rhythm(pulses, steps)
    line = f"{name.ljust(15)} | {dna} | ({pulses},{steps})"
    return line

# Catalog of Rhythm DNA
catalog = [
    ("Balfolk Jig", 2, 6),
    ("Tresillo", 3, 8),
    ("Cinquillo", 5, 8),
    ("Son Clave", 5, 16),
    ("Bossa Nova", 5, 16),
    ("Techno Four", 4, 16),
    ("Arabic Maqsum", 3, 8)
]

print("=== RHYTHM DNA MARKER CATALOG ===")
for name, p, s in catalog:
    print(create_dna_marker(name, p, s))
