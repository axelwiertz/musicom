#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Random style + method selection for nightly composition cron."""
import os
import random

STYLES_DIR = "/opt/data/projects/Styles/"
EXCLUDE = {"_Comparison", "_Data_Patterns", "Research", "Poetry",
           "Production", "Percussion", "Other"}

styles = [d for d in os.listdir(STYLES_DIR)
          if os.path.isdir(os.path.join(STYLES_DIR, d)) and d not in EXCLUDE]
random.seed()
style = random.choice(styles)

# Method pool: stochastic / nature-led / rules-based spread.
# Avoid recently used (041 ant colony on Arabic 071, 055 SAMC).
methods = {
    "003": "Genetic Genome Selection",
    "022": "Markov-Constraint Wavefront Sequencing",
    "031": "Swarm Intelligence Flocking (Boids)",
    "036": "Abelian Sandpile Avalanche Rhythmics",
    "038": "Kuramoto Oscillator Phase Synchronization",
    "040": "Perlin Noise Composition",
    "048": "Reflected Brownian Motion Pitch Diffusion",
    "053": "Levy Flight Composition",
    "059": "Echo State Network Reservoir Composition",
    "061": "Gaussian Process Composition",
}
method_id = random.choice(sorted(methods.keys()))
print("STYLE=%s" % style)
print("METHOD=%s" % method_id)
print("METHOD_NAME=%s" % methods[method_id])
