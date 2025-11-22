# modes/eqbars.py
import config
import grid
import math

colors_bars = [
    (0,100,0),
    (0,100,0),
    (100,100,0),
    (100,100,0),
    (100,0,0),

]

def step(np, state, t):
    # tron = 3 blue lines in middle rows
    np.fill((0,0,0))

    height = round((math.sin(t*10) + 1) / 2 * (config.ROWS))
    # print(height)
    # return
    for c in range(config.COLS):

        block = (config.COLS -1) - (c // 3 +1) # 0->7

        height = round((math.sin(t/2 * block) + 1) / 2 * (config.ROWS))
        for r in range(int(height)):

            np[grid.xy_to_pixel(c, (config.ROWS-1) - r)] = colors_bars[r] # (0,0,150)

    np.write()
