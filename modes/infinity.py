# modes/infinity.py
import config
import grid

def step(np, state, t):
    # infinity repeating pattern
    # there are multiple phases with steps in each one
    # it looks like each step is maybe 1/3 of a second or so, but let's go with 1 second to keep it simple

    np.fill((0,0,0))

    # Figure out phase (0-5)
    phases = 6
    seconds_per_phase = 1
    phase = (int(t) // seconds_per_phase) % phases
    phase_percent = (t % seconds_per_phase) / seconds_per_phase
    phase_time = phase_percent * seconds_per_phase
    print(f"{phase=}, {phase_percent=}")

    # phase = 4
    print("Infinity phase:", phase)

    if phase == 0: # broken red lines come in from top and bottom
        r = int(((config.ROWS // 2) +1) * phase_percent)
        for c in range(config.COLS):
            if c % 5 != 0:
                np[grid.xy_to_pixel(c, r)] = (150,0,0)
                np[grid.xy_to_pixel(c, config.ROWS - r -1)] = (150,0,0)
        np.write()
    
    if phase == 1: # solid red lins start in middle and fill out
        row = int(((config.ROWS // 2) +1) * phase_percent) +1
        print(" Phase time:", phase_time)
        for c in range(config.COLS):
            for r in range(row):
                np[grid.xy_to_pixel(c, (config.ROWS //2) - r)] = (150,0,0)
                np[grid.xy_to_pixel(c, (config.ROWS //2) + r)] = (150,0,0)
        np.write()

    if phase == 2: # solid red collapses from left/right to middle
        middle = config.COLS //2
        cols = middle - int((middle +2 )* phase_percent)
        print(" Phase time:", phase_time)
        for r in range(config.ROWS):
            for c in range(cols):
                np[grid.xy_to_pixel(middle + c, r)] = (150,0,0)
                np[grid.xy_to_pixel(middle - c, r)] = (150,0,0)
        np.write()

    if phase == 3: # solid blue lines middle to top/bottom
        row = int(((config.ROWS // 2) +1) * phase_percent)
        print(f"{row=}" )
        for c in range(config.COLS):
                np[grid.xy_to_pixel(c, row)] = (0,0,150)
                if row == config.ROWS // 2:
                    bottom = config.ROWS //2 +1
                else:
                    bottom = config.ROWS - row -1
                np[grid.xy_to_pixel(c, bottom)] = (0,0,150)
        np.write()

    if phase == 4: # solid blue lines middle to top/bottom
        row = int(((config.ROWS // 2) +1) * phase_percent)
        row = config.ROWS //2 - row
        print(f"{row=}" )
        for c in range(config.COLS):
                np[grid.xy_to_pixel(c, row)] = (0,0,150)
                if row == config.ROWS // 2:
                    bottom = config.ROWS //2 +1
                else:
                    bottom = config.ROWS - row -1
                np[grid.xy_to_pixel(c, bottom)] = (0,0,150)
        np.write()        

    if phase == 5: # blank
        np.write()