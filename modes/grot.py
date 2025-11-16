# modes/grot.py
import config
import grid
import math

def step(np, state, t):
    # grot = simple line graph
    # first pass = simple sine wave
    np.fill((0,0,0))
    for c in range(config.COLS):
        s = (math.sin((c + t)) + 1) / 2  # 0..1
        r = int(s * 5)
        np[grid.xy_to_pixel(c, r)] = (20,20,20)

    np.write()
