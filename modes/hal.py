# modes/hal.py – HAL 9000 eye pulse
import math
import grid
import config

# HAL palette
BLACK = (0, 0, 0)
DARK_RED = (20, 0, 0)
MID_RED  = (80, 0, 0)
HAL_RED  = (255, 40, 20)
HAL_CORE = (255, 120, 80)


def step(np, state, t):
    """
    HAL 9000 Eye Pulse:
    - Smooth breathing red glow
    - Brighter center "lens"
    - Occasional tiny flicker glitches
    """

    cols = config.COLS
    rows = config.ROWS

    cx = (cols - 1) / 2
    cy = (rows - 1) / 2

    # --- Pulse: smooth sinusoidal breathing ---
    # slows down nicely: try adjusting 0.6 for speed
    pulse = (math.sin(t * 0.6) + 1) / 2

    # map pulse to brightness curve (non-linear, cinematic)
    base_intensity = int(30 + pulse * 100)
    core_intensity = int(80 + pulse * 150)

    # small random flicker every ~7 seconds
    flicker = False
    if int(t * 10) % 70 == 0:
        flicker = True

    for x in range(cols):
        for y in range(rows):
            dx = abs(x - cx)
            dy = abs(y - cy)

            # distance from center
            dist = math.sqrt(dx*dx + dy*dy)

            # lens falloff (soft radial gradient)
            falloff = max(0, 1.0 - dist / (cols / 2))

            if falloff <= 0:
                color = BLACK
            else:
                # base glow
                r = int(base_intensity * falloff)
                g = 0
                b = 0

                # brighter center core
                if dist < 1.5:
                    r = int(core_intensity)
                    g = int(core_intensity * 0.3)
                    b = int(core_intensity * 0.15)

                # subtle flicker glitch
                if flicker and dist < 2.5:
                    r = min(255, r + 60)

                color = (r, g, b)

            np[grid.xy_to_pixel(x, y)] = color

    np.write()
