# modes/fire.py — Doom-style fire for a tiny LED matrix
#
# Based on the classic Doom fire algorithm:
# - We keep a 2D array of "heat" values (0..MAX_INTENSITY)
# - Bottom row is seeded with random heat
# - Each cell above looks at the cell below, subtracts a random decay,
#   and shifts a bit sideways, producing a rising fire effect.

import config
import grid

# Use urandom on MicroPython, random on desktop
try:
    import urandom as _random
except ImportError:
    import random as _random

# Fire tuning
_MAX_INTENSITY = 36  # more steps = smoother grad
_WIDTH  = config.COLS
_HEIGHT = config.ROWS

# Global state so it survives even if `state` dict is recreated
_fire_buffer = None
_palette = None


def _build_palette():
    """
    Build a simple fire palette from black -> dark red -> orange -> yellow -> white.
    Index 0 = black, index MAX_INTENSITY = white-hot.
    """
    palette = []
    for i in range(_MAX_INTENSITY + 1):
        # normalized "heat" 0..255 (integer)
        heat = i * 255 // _MAX_INTENSITY

        # Split into two zones: dark red -> orange, then orange -> yellow/white
        if heat < 128:
            # dark reds
            r = heat * 2            # ramp up quickly
            g = heat // 4
            b = 0
        else:
            # bright oranges / yellows / white
            r = 255
            g = min(255, (heat - 64) * 2)  # catches up to red
            b = (heat - 128) // 2 if heat > 160 else 0

        # clamp
        if r > 255: r = 255
        if g > 255: g = 255
        if b < 0:   b = 0

        palette.append((r, g, b))

    return palette


def _init():
    global _fire_buffer, _palette
    if _fire_buffer is None:
        _fire_buffer = [_MAX_INTENSITY] * (_WIDTH * _HEIGHT)
    if _palette is None:
        _palette = _build_palette()


def _idx(x, y):
    return y * _WIDTH + x


def _update_fire():
    """
    Update the fire buffer in-place.
    Bottom row is the "fuel line", everything above is derived from it.
    """
    # Seed bottom row with random heat
    for x in range(_WIDTH):
        # Flicker between ~3/4 and full intensity
        base = _MAX_INTENSITY * 3 // 4
        extra = _random.getrandbits(2)  # 0..3
        val = min(_MAX_INTENSITY, base + extra)
        _fire_buffer[_idx(x, _HEIGHT - 1)] = val

    # Propagate upwards
    # Start from y=0 (top) and look at y+1 (below)
    for y in range(_HEIGHT - 1):
        for x in range(_WIDTH):
            src = _idx(x, y + 1)
            below_int = _fire_buffer[src]

            if below_int == 0:
                _fire_buffer[_idx(x, y)] = 0
            else:
                decay = _random.getrandbits(2)  # 0..3
                new_int = below_int - decay
                if new_int < 0:
                    new_int = 0

                # Shift a bit sideways for that classic Doom wobble
                dst_x = x - decay + 1
                if dst_x < 0:
                    dst_x = 0
                elif dst_x >= _WIDTH:
                    dst_x = _WIDTH - 1

                _fire_buffer[_idx(dst_x, y)] = new_int


def step(np, state, t):
    """
    Main mode entrypoint. Ignores `t` and uses its own internal state.
    Call this every frame.

    This version damps intensity toward the top so the fire looks shorter
    and leaves black space above.
    """
    _init()
    _update_fire()

    for y in range(_HEIGHT):
        # scale factor: 1.0 at bottom row, ~0 at top row
        # tweak the exponent (2.0) for sharper/softer falloff
        row_factor = (y / (_HEIGHT - 1)) ** 2

        for x in range(_WIDTH):
            intensity = _fire_buffer[_idx(x, y)]
            # apply vertical damping so upper rows are darker/black
            damped = int(intensity * row_factor)
            if damped < 0:
                damped = 0
            if damped > _MAX_INTENSITY:
                damped = _MAX_INTENSITY

            color = _palette[damped]
            np[grid.xy_to_pixel(x, y)] = color

    np.write()

