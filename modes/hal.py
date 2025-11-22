# modes/hal.py – HAL 9000 eye pulse (scaled for wide, short display)
import math
import grid
import config

# HAL-ish colors
BLACK = (0, 0, 0)
DIM_RED = (10, 0, 0)
MID_RED = (60, 0, 0)
HAL_RED = (255, 40, 20)
HAL_CORE = (255, 120, 80)


def step(np, state, t):
    """
    HAL 9000 Eye Pulse:
    - Designed for wide, short matrices (e.g. 21x5)
    - Small bright core in the center
    - One-pixel 'ring' around it
    - Slow breathing pulse
    """

    cols = config.COLS
    rows = config.ROWS

    cx = (cols - 1) / 2
    cy = (rows - 1) / 2

    # Slow pulse: tweak 0.5 for speed
    pulse = (math.sin(t * 0.5) + 1) / 2  # 0..1
    # Use a non-linear curve to make it linger dimmer/bright longer
    pulse_pow = pulse * pulse

    # Base intensities (keep fairly low so core pops)
    base_r = int(15 + 40 * pulse_pow)   # background glow
    ring_r = int(40 + 120 * pulse_pow)  # ring level
    core_r = int(80 + 175 * pulse_pow)  # bright core

    # Occasional tiny “thinking” flicker on the core only
    flicker = False
    if int(t * 8) % 37 == 0:
        flicker = True

    for x in range(cols):
        for y in range(rows):
            dx = abs(x - cx)
            dy = abs(y - cy)

            # For a 5-row display, don't bother with big circles:
            # define simple "bands" around the center.
            #
            # core region: very small, center-ish
            # ring region: slightly larger rectangle around it

            # measure “radius” with horizontal stretched (wide eye)
            # and vertical compressed
            nx = dx / max(1.0, (cols / 6))   # horizontal radius
            ny = dy / max(1.0, (rows / 2))   # vertical radius
            r = math.sqrt(nx * nx + ny * ny)

            if r < 0.5:
                # Core pixels: tiny center
                r_val = core_r
                g_val = int(core_r * 0.35)
                b_val = int(core_r * 0.2)

                if flicker:
                    r_val = min(255, r_val + 40)

                color = (r_val, g_val, b_val)

            elif r < 1.1:
                # Tight ring around core
                r_val = ring_r
                color = (r_val, 0, 0)

            elif r < 1.8:
                # Outer glow band (subtle)
                r_val = base_r
                color = (r_val, 0, 0)

            else:
                # Outside eye: mostly dark with a hint of dim red
                if (x + y) % 3 == 0:
                    color = DIM_RED
                else:
                    color = BLACK

            np[grid.xy_to_pixel(x, y)] = color

    np.write()
