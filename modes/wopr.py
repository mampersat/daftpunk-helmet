import random
import config
import grid

# ---------------------------------------------------------------------------
# Colour palette (R, G, B)
# ---------------------------------------------------------------------------
PALETTE = [
    (0,   160, 0),   # STATE_GREEN  — simulation nominal
    (0,   0,   0),   # STATE_BLACK  — simulation did not finish
    (200, 160, 0),   # STATE_YELLOW — significant casualties
    (60, 0,   0),   # STATE_RED    — nuclear exchange / mass casualties
]

STATE_GREEN  = 0
STATE_BLACK  = 1
STATE_YELLOW = 2
STATE_RED    = 3

# ---------------------------------------------------------------------------
# DEFCON level weights.
# Values are ratios — they don't need to sum to any particular number,
# just be in proportion to each other.
# e.g. black=10, red=1 means black is 10× more likely than red.
# ---------------------------------------------------------------------------
DEFCON_LEVELS = {
    5: dict(green=145, black=150, yellow= 14, red=  1),
    4: dict(green= 44, black= 40, yellow= 13, red=  1),
    3: dict(green= 39, black= 30, yellow= 23, red=  8),
    2: dict(green= 25, black= 40, yellow= 21, red= 14),
    1: dict(green=  5, black= 77, yellow= 10, red= 11),
}

def pick_state(defcon):
    w     = DEFCON_LEVELS.get(defcon, DEFCON_LEVELS[5])
    total = w['green'] + w['black'] + w['yellow'] + w['red']
    r     = random.random() * total
    if r < w['green']:
        return STATE_GREEN
    if r < w['green'] + w['black']:
        return STATE_BLACK
    if r < w['green'] + w['black'] + w['yellow']:
        return STATE_YELLOW
    return STATE_RED

def pick_duration():
    return 1.0 + random.random() * 9.0  # 1 – 10 seconds

# ---------------------------------------------------------------------------
# Step — called each frame.
# `state` is a dict that persists between calls (owned by the caller).
# `t`     is elapsed seconds (float).
# ---------------------------------------------------------------------------
def step(np, state, t):
    defcon = state.get('defcon', 5)
    n      = config.COLS * config.ROWS

    # First call — seed every agent with a staggered random timer
    if 'agent_states' not in state:
        state['agent_states']  = [pick_state(defcon) for _ in range(n)]
        state['next_change']   = [random.random() * 10.0 for _ in range(n)]
        state['last_defcon']   = defcon

    agent_states = state['agent_states']
    next_change  = state['next_change']

    # DEFCON changed — flush all timers so the new mix takes effect immediately
    if state['last_defcon'] != defcon:
        state['last_defcon'] = defcon
        for i in range(n):
            next_change[i] = 0.0

    # Tick agents whose timer has expired
    for i in range(n):
        if t >= next_change[i]:
            agent_states[i] = pick_state(defcon)
            next_change[i]  = t + pick_duration()

    # Render
    for y in range(config.ROWS):
        for x in range(config.COLS):
            np[grid.xy_to_pixel(x, y)] = PALETTE[agent_states[y * config.COLS + x]]

    np.write()
