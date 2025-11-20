# modes/tron.py
import config
import grid

COLORS = {
    "off":    (0, 0, 0),
    "dimred": (20, 0, 0),
    "red":    (60, 0, 0),
    "orange": (200, 80, 0),
    "yellow": (200, 160, 0),
    "green":  (0, 160, 0),
    "amber":  (160, 80, 0),
}

# which rows act like persistent "buses"
BUS_ROWS = (1, 3)

# fixed logic nodes
NODES = (
    (2, 0),
    (4, 4),
    (7, 2),
    (10, 0),
    (13, 3),
    (16, 1),
)

def step(np, state, t):
    cols = config.COLS
    rows = config.ROWS

    # Slower global motion
    slow = int(t * 2)
    med  = int(t * 4)
    fast = int(t * 7)

    # Split the visor into 3 vertical zones
    zone_width = cols // 3

    # --- 1) Base background (mix of red + black) ---
    for x in range(cols):
        for y in range(rows):
            idx = grid.xy_to_pixel(x, y)

            # Every other row darker → more "PCB shadow"
            if (y % 2 == 0) and ((x + slow) % 4 == 0):
                np[idx] = COLORS["off"]
            else:
                np[idx] = COLORS["dimred"]

    # --- 2) Horizontal bus traces with slow data pulses ---
    for y in BUS_ROWS:
        for x in range(cols):
            idx = grid.xy_to_pixel(x, y)

            # base bus line
            np[idx] = COLORS["red"]

            # data pulses, slower & chunkier than before
            # different zones move at different speeds
            if x < zone_width:
                phase = slow
            elif x < zone_width * 2:
                phase = med
            else:
                phase = fast

            k = (x - phase) % 8
            if k == 0:
                np[idx] = COLORS["yellow"]
            elif k in (1, 2):
                np[idx] = COLORS["orange"]

            # occasional amber sparkle on buses
            if ((x * 9 + y * 3 + slow) % 31) == 0:
                np[idx] = COLORS["amber"]

    # --- 3) Vertical activity columns (different frequencies) ---
    for x in range(cols):
        # zone-based blinking speeds
        if x < zone_width:
            blink_phase = slow
            rate = 6
        elif x < zone_width * 2:
            blink_phase = med
            rate = 5
        else:
            blink_phase = fast
            rate = 4

        if (x + blink_phase) % rate == 0:
            y = (slow + x) % rows
            idx = grid.xy_to_pixel(x, y)

            # don't overwrite bright pulses
            r, g, b = np[idx]
            if r < 150 and g < 150 and b < 150:
                np[idx] = COLORS["orange"]

    # --- 4) Logic nodes with independent blink speeds ---
    for i, (nx, ny) in enumerate(NODES):
        if 0 <= nx < cols and 0 <= ny < rows:
            idx = grid.xy_to_pixel(nx, ny)

            # each node blinks at its own rate
            node_phase = int(t * (2 + i * 0.8))
            v = (node_phase + nx + ny * 5) % 10

            if v < 2:
                np[idx] = COLORS["green"]
            elif v < 4:
                np[idx] = COLORS["amber"]
            elif v == 7:
                np[idx] = COLORS["off"]  # real "dead" blink

    np.write()
