#!/usr/bin/env python3
"""Debug MIDI pitch bend values."""
import numpy as np
import math

def freq_to_pitchbend_centered(freq, base_note):
    base_freq = 440.0 * 2**((base_note - 69) / 12)
    half_steps = 12 * math.log2(freq / base_freq)
    cents = half_steps * 100.0
    bend_value = int(round(cents / 200.0 * 8192))
    clipped = int(np.clip(bend_value, -8192, 8191))
    return clipped, cents, bend_value

# Simulate pattern
pattern = [
    (329.63, 0.0, 1.5, 440.0, 0.4),
    (440.0, 1.5, 0.5, None, 0.0),
    (392.0, 2.0, 0.5, None, 0.0),
    (329.63, 2.5, 0.5, None, 0.0),
    (493.88, 3.0, 1.5, 329.63, 0.3),
    (329.63, 4.5, 0.5, None, 0.0),
    (392.0, 5.0, 1.5, 493.88, 0.5),
    (440.0, 6.5, 0.5, None, 0.0),
    (369.99, 7.0, 0.5, 392.0, 0.2),
    (392.0, 7.5, 0.5, None, 0.0),
    (293.66, 8.0, 1.0, None, 0.0),
    (293.66, 9.0, 2.0, 440.0, 0.5),
    (440.0, 11.0, 1.0, None, 0.0),
    (440.0, 12.0, 0.75, 369.99, 0.3),
    (369.99, 12.75, 0.25, None, 0.0),
    (329.63, 13.0, 0.75, 293.66, 0.3),
    (293.66, 13.75, 0.25, None, 0.0),
    (261.63, 14.0, 0.5, None, 0.0),
    (329.63, 14.5, 3.5, None, 0.0),
]

for freq, start, dur, slide_freq, slide_off in pattern:
    nn = int(round(69 + 12 * math.log2(freq/440.0)))
    if slide_freq is not None:
        val, cents, raw = freq_to_pitchbend_centered(slide_freq, nn)
        print(f"freq={freq:.1f} nn={nn} slide_to={slide_freq:.1f}: cents={cents:.1f} raw={raw} clipped={val}")
        if val < -8192 or val > 8191:
            print(f"  >>> OUT OF RANGE <<<")