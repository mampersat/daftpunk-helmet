# modes/kitt.py
import config
import grid

def step(np, state, t):
    # kitt = from knight rider
    # bouncing red dot with trail
    np.fill((0,0,0))
    print("KITT step at time", t)
    pos = t % (2 * (config.COLS -1))
    if pos >= config.COLS:
        pos = 2*(config.COLS -1) - pos  # reverse direction on return trip
    for offset in range(-2,3):
        c = int(pos) + offset
        if 0 <= c < config.COLS:
            intensity = max(0, 50 - abs(offset)*20)
            np[grid.xy_to_pixel(c, 2)] = (intensity,0,0)    

    np.write()
