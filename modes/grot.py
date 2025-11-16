# modes/grot.py
import config
import grid
import math

def step(np, state, t):
    # grot = simple line graph
    # first pass = simple sine wave
    np.fill((0,0,0))
    for c in range(config.COLS):
        r = int(math.sin((c +t) / 3) * config.ROWS)
        
        np[grid.xy_to_pixel(c, r)] = (20,20,20)

    np.write()
