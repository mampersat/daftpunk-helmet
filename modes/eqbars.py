"""
eqbars.py – Equalizer-style LED bar display for a 5x21 NeoPixel matrix.

Features:
- Fixed 5 rows × 21 columns (105 pixels total)
- Serpentine row wiring supported
- Color gradient from green → yellow → red
- Two driving modes:
    1. demo_bpm(): beat-driven “breathing” animation (no mic required)
    2. render_bars(): render arbitrary level values [0..1]
"""

import math
import time

ROWS = 5
COLS = 21
SERPENTINE = True


# ───────────────────────────── Mapping ───────────────────────────── #
def pixel_index(x, y):
    """Map (x, y) -> linear pixel index for serpentine rows (y=0 top)."""
    if SERPENTINE and (y % 2 == 1):
        x = COLS - 1 - x
    return y * COLS + x


# ───────────────────────────── Helpers ───────────────────────────── #
def clear(np):
    """Turn off all pixels."""
    for i in range(ROWS * COLS):
        np[i] = (0, 0, 0)


def level_color(t):
    """Map intensity 0..1 → green→yellow→red gradient."""
    t = max(0.0, min(1.0, t))
    if t < 0.5:
        # green → yellow
        u = t / 0.5
        r, g, b = int(255 * u), 255, 0
    else:
        # yellow → red
        u = (t - 0.5) / 0.5
        r, g, b = 255, int(255 * (1 - u)), 0
    return (r, g, b)


# ─────────────────────────── Main Render ─────────────────────────── #
def render_bars(np, levels):
    """
    Draw vertical bars from a list of normalized levels (0..1).
    len(levels) may be ≤ 21.
    """
    clear(np)
    for x, t in enumerate(levels[:COLS]):
        height = int(round(t * ROWS))
        color = level_color(t)
        for i in range(height):
            y = ROWS - 1 - i  # bottom-up
            np[pixel_index(x, y)] = color
    if hasattr(np, "write"):
        np.write()


# ─────────────────────────────  Demo  ────────────────────────────── #
def demo_bpm(np, bpm=123.0, phase=0.0):
    """
    Generate a beat-synced sine wave pattern across the display.
    Call repeatedly inside a loop to animate.
    """
    t = time.time()
    beat_hz = bpm / 60.0
    levels = []
    for x in range(COLS):
        ph = phase + (x / COLS) * math.pi * 0.75
        v = 0.5 + 0.5 * math.sin(2 * math.pi * beat_hz * t + ph)
        v = v ** 0.6  # ease curve for snappier peaks
        levels.append(v)
    render_bars(np, levels)
    return levels


