# modes/rain.py
import config
import grid

def step(np, state, t):
    # render raindrops
    # we've got like 21 columns and 5 rows
    # t (time) is in seconds
    # assign each colum a drop speed/existance based on time

    
    # render text in state["text"], with brightness

    np.fill((0,0,0))
    for col in range(config.COLS):
        speed = 1.0 + (col % 3) * 0.5  # different speeds
        pos = (t * speed) % (config.ROWS + 5)  # position of drop
        drop_row = int(pos)
        if 0 <= drop_row < config.ROWS:
            np[grid.xy_to_pixel(col, drop_row)] = (0,0,255)
        # tail effect
        for i in range(1,4):
            tail_row = drop_row - i
            if 0 <= tail_row < config.ROWS:
                brightness = max(0, 255 - i * 80)
                np[grid.xy_to_pixel(col, tail_row)] = (0,0,brightness)

    np.write()
