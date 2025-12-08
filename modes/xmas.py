# modes/xmas.py – tiny Xmas scene for 21x5 visor
#
# - Green tree centered on bottom rows
# - Brown trunk
# - Twinkling colored lights
# - Falling snowflakes
#
# Assumes:
#   import config  (COLS, ROWS)
#   import grid    (xy_to_pixel)

import config
import grid

try:
    import urandom as _random
except ImportError:
    import random as _random

COLS = config.COLS
ROWS = config.ROWS

# Colors
BG       = (0, 0, 8)       # dark “night sky”
TREE     = (0, 120, 0)
TRUNK    = (80, 40, 0)
SNOW     = (200, 200, 255)
STAR     = (255, 255, 80)
LIGHT_COLORS = [
    (255, 40, 40),   # red
    (255, 160, 40),  # orange
    (255, 255, 80),  # yellow
    (80, 255, 80),   # green
    (80, 160, 255),  # blue
    (200, 80, 255),  # purple
]

# Module-level animation state
_frame = 0
_snowflakes = []   # list of (x, y)


# Precompute tree geometry for 21x5-ish layout
def _build_tree():
    """
    Return (tree_pixels, trunk_pixels, light_pixels, star_pixel) as lists of (x,y).
    Designed for 21x5, but uses COLS/ROWS so it adapts a bit.
    """
    cx = COLS // 2
    bottom = ROWS - 1

    tree_pixels = []
    trunk_pixels = []
    light_pixels = []

    # Simple 3-layer tree (bottom wide, top narrow)
    # from bottom-1 up to top-ish
    layers = [
        (bottom - 1, 4),  # y, half-width (so width = 2*w+1)
        (bottom - 2, 3),
        (bottom - 3, 2),
    ]
    for y, halfw in layers:
        if 0 <= y < ROWS:
            for dx in range(-halfw, halfw + 1):
                x = cx + dx
                if 0 <= x < COLS:
                    tree_pixels.append((x, y))

    # Trunk: 1 or 2 pixels wide centered
    trunk_y = bottom
    for dx in (-1, 0):
        x = cx + dx
        if 0 <= x < COLS and 0 <= trunk_y < ROWS:
            trunk_pixels.append((x, trunk_y))

    # Lights: choose a subset of tree pixels to host bulbs
    # (e.g. every Nth pixel)
    for i, (x, y) in enumerate(tree_pixels):
        if i % 3 == 0:  # tweak density by changing 3
            light_pixels.append((x, y))

    # Star at the top (one pixel above highest tree layer if possible)
    star_y = layers[-1][0] - 1
    star_pixel = None
    if 0 <= star_y < ROWS:
        star_pixel = (cx, star_y)

    return tree_pixels, trunk_pixels, light_pixels, star_pixel


_TREE_PIXELS, _TRUNK_PIXELS, _LIGHT_PIXELS, _STAR_PIXEL = _build_tree()


def _randint(a, b):
    # inclusive [a,b]
    return a + (_random.getrandbits(16) % (b - a + 1))


def _chance(p_num, p_den):
    """Return True with probability p_num/p_den."""
    return (_random.getrandbits(16) % p_den) < p_num


def _update_snow():
    """Update global _snowflakes list in-place."""
    global _snowflakes

    new_snow = []

    # Move existing flakes down
    for (x, y) in _snowflakes:
        # every frame they fall 1 row
        ny = y + 1
        if ny < ROWS:
            new_snow.append((x, ny))
        # else: dropped off bottom

    # Maybe spawn new flakes at top
    # Chance per frame to spawn a few flakes
    for _ in range(COLS // 4 + 1):
        if _chance(1, 4):  # 25% chance to spawn
            x = _randint(0, COLS - 1)
            new_snow.append((x, 0))

    _snowflakes = new_snow


def step(np, state, t):
    global _frame

    _frame += 1

    # 1) Update snow positions
    _update_snow()

    # 2) Clear background
    for x in range(COLS):
        for y in range(ROWS):
            np[grid.xy_to_pixel(x, y)] = BG

    # 3) Draw tree + trunk
    for (x, y) in _TREE_PIXELS:
        np[grid.xy_to_pixel(x, y)] = TREE

    for (x, y) in _TRUNK_PIXELS:
        np[grid.xy_to_pixel(x, y)] = TRUNK

    # 4) Star on top (twinkle a bit)
    if _STAR_PIXEL is not None:
        sx, sy = _STAR_PIXEL
        # Simple pulsing brightness based on frame
        fade = ((_frame // 4) % 4)  # 0..3
        base = 180 + fade * 20
        if base > 255:
            base = 255
        color = (base, base, 80)
        np[grid.xy_to_pixel(sx, sy)] = color

    # 5) Xmas lights – twinkle through LIGHT_COLORS
    for i, (x, y) in enumerate(_LIGHT_PIXELS):
        # Each light cycles through colors at its own pace
        phase = (_frame // 5 + i) % len(LIGHT_COLORS)
        col = LIGHT_COLORS[phase]
        np[grid.xy_to_pixel(x, y)] = col

    # 6) Snow drawn last so it sits "on top" of tree/lights
    for (x, y) in _snowflakes:
        np[grid.xy_to_pixel(x, y)] = SNOW

    np.write()
