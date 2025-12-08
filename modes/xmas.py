# modes/xmas.py – lightweight, robust falling snow for 21x5 visor
#
# Assumes:
#   import config  (COLS, ROWS)
#   import grid    (xy_to_pixel)
#
# Effect:
#   - Dark night background
#   - White/blue snowflakes drifting down
#   - Simple integer "twinkle"

import config
import grid

try:
    import urandom as _random
except ImportError:
    import random as _random

COLS = config.COLS
ROWS = config.ROWS

BG         = (0, 0, 8)          # night sky
SNOW_BASE  = (210, 210, 255)    # base snow color

# Global animation state
_frame = 0
_snowflakes = []   # list of (x, y, phase)

# --- Tuning knobs (you can change these) ---

FALL_EVERY = 5      # frames between downward moves (1 = fastest, 2 = nice fast, 3+ slower)
SPAWN_CHANCE_NUM = 1
SPAWN_CHANCE_DEN = 5  # spawn probability ≈ NUM/DEN
MAX_FLAKES = 10     # ABSOLUTE cap on flakes


def _randint(a, b):
    # inclusive [a,b]
    return a + (_random.getrandbits(16) % (b - a + 1))


def _chance(num, den):
    return (_random.getrandbits(16) % den) < num


def _spawn_snowflakes():
    global _snowflakes

    if len(_snowflakes) >= MAX_FLAKES:
        return

    # a few "slots" across the width
    slots = COLS // 3 + 1
    for _ in range(slots):
        if len(_snowflakes) >= MAX_FLAKES:
            break
        if _chance(SPAWN_CHANCE_NUM, SPAWN_CHANCE_DEN):
            x = _randint(0, COLS - 1)
            # (x, y, phase)
            _snowflakes.append((x, 0, _randint(0, 255)))


def _update_snowflakes():
    global _snowflakes, _frame

    move_now = (FALL_EVERY <= 1) or (_frame % FALL_EVERY == 0)

    new_list = []
    for (x, y, phase) in _snowflakes:
        if move_now:
            # tiny horizontal drift
            if _chance(1, 5):
                x += _randint(-1, 1)
                if x < 0:
                    x = 0
                elif x >= COLS:
                    x = COLS - 1
            y += 1

        if y < ROWS:
            # advance phase for twinkle (integer wrap)
            phase = (phase + 7) & 0xFF
            new_list.append((x, y, phase))

    # enforce hard cap
    if len(new_list) > MAX_FLAKES:
        new_list = new_list[-MAX_FLAKES:]

    _snowflakes = new_list

    # maybe spawn new flakes at top
    _spawn_snowflakes()


def _flake_color(phase):
    """
    Integer-only twinkle:
    - phase 0..255 -> local brightness 0..127 -> map to [60..100]%
    """
    v = phase & 0x7F   # 0..127
    if phase & 0x80:
        v = 127 - v    # triangle wave

    # brightness in 60..100% as integer 60..100
    #  v/127 ≈ 0..1 -> scale to 0..40 and add 60
    bright_pct = 60 + (40 * v) // 127  # 60..100

    r = (SNOW_BASE[0] * bright_pct) // 100
    g = (SNOW_BASE[1] * bright_pct) // 100
    b = (SNOW_BASE[2] * bright_pct) // 100

    # clamp, just in case
    if r > 255: r = 255
    if g > 255: g = 255
    if b > 255: b = 255

    return (r, g, b)


def step(np, state, t):
    global _frame
    _frame += 1

    _update_snowflakes()

    # background
    for x in range(COLS):
        for y in range(ROWS):
            np[grid.xy_to_pixel(x, y)] = BG

    # draw flakes
    for (x, y, phase) in _snowflakes:
        color = _flake_color(phase)
        np[grid.xy_to_pixel(x, y)] = color

    np.write()
