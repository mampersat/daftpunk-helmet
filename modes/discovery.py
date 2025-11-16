# modes/discovery.py
import config
import grid

def step(np, state, t):
    # discovery = 4 red lines
    np.fill((0,0,0))
    for c in range(config.COLS):
        np[grid.xy_to_pixel(c, 0)] = (150,0,0)
        np[grid.xy_to_pixel(c, 1)] = (150,0,0)
        np[grid.xy_to_pixel(c, 3)] = (150,0,0)
        np[grid.xy_to_pixel(c, 4)] = (150,0,0)

    np.write()
