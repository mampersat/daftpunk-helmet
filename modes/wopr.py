# modes/tron.py
import config
import grid

COLORS = {
    "off":    (0, 0, 0),
    "dimred": (25, 0, 0),
    "red":    (80, 0, 0),
    "orange": (255, 100, 0),
    "yellow": (255, 200, 0),
    "green":  (0, 200, 0),
    "amber":  (200, 120, 0),
}

# which rows act like "buses" on the board
BUS_ROWS = (1, 3)

# some fixed "logic node" coordinates (x, y)
NODES = (
    (2, 0),
    (5, 2),
    (8, 4),
    (12, 1),
    (15, 3),
)


def step(np, state, t):
    """
    WOPR / circuit-board style:
    - dim red background
    - horizontal buses on a couple rows
    - bright pulses flowing along buses
    - blinking logic nodes
    """
    cols = config.COLS
    rows = config.ROWS

    # phase values drive everything; tweak speeds here
    phase_fast  = int(t * 18)   # quick pulses
    phase_slow  = int(t * 5)    # node blinking
    phase_med   = int(t * 9)    # scan / shimmer

    # 1) base background: dim red everywhere
    for x in range(cols):
        for y in range(rows):
            np[grid.xy_to_pixel(x, y)] = COLORS["dimred"]

    # 2) horizontal buses with moving pulses
    for y in BUS_ROWS:
        for x in range(cols):
            idx = grid.xy_to_pixel(x, y)

            # base bus line slightly brighter than background
            np[idx] = COLORS["red"]

            # moving "data packets" along the bus
            # these are bright yellow / orange streaks
            # pattern repeats every 6 pixels, offset by time
            k = (x - phase_fast) % 6
            if k == 0:
                np[idx] = COLORS["yellow"]
            elif k == 1:
                np[idx] = COLORS["orange"]

            # extra shimmer: occasional amber pixel
            if ((x * 7 + y * 11 + phase_med) % 23) == 0:
                np[idx] = COLORS["amber"]

    # 3) subtle vertical scan, like activity in columns
    for x in range(cols):
        # every few columns, make one pixel in the column flicker brighter
        if ((x + phase_med) % 4) == 0:
            # choose a row that moves up/down slowly
            y = (phase_slow + x) % rows
            idx = grid.xy_to_pixel(x, y)
            # only boost if it's not already a bus highlight
            r, g, b = np[idx]
            if r < 200 and g < 200 and b < 200:
                np[idx] = COLORS["orange"]

    # 4) logic nodes that blink independently
    for (nx, ny) in NODES:
        if 0 <= nx < cols and 0 <= ny < rows:
            idx = grid.xy_to_pixel(nx, ny)
            # nodes blink with a slower pseudo-random pattern
            v = (nx * 13 + ny * 31 + phase_slow) % 16
            if v < 4:
                np[idx] = COLORS["green"]
            elif v < 8:
                np[idx] = COLORS["amber"]
            # else: leave whatever the bus/background set

    np.write()
