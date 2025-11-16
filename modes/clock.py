# main.py
import fivefont as ff
import time
import ntp
import config

def step(np, state, t):
    t = time.localtime()  # keep as struct_time, not string

    hour = t[3]

    # timezone adjust - might brake 
    hour -= 5

    hour = hour % 12
    if hour == 0:
        hour = 12

    if t[5] % 2 == 0:
        s = "%d:%02d" % (hour, t[4])
    else:
        s = "%d.%02d" % (hour, t[4])

    # Red at the top of every 0m/30m, blue at 15m/45m, green at 30m/60m
    if (t[4] % 30) < 10:
        color = (0, 100, 0)
    elif (t[4] % 30) < 20:
        color = (0, 0, 100)
    else:
        color = (100, 0, 0)

    np.fill((0, 0, 0))        
    side_burns(np)
    ff.draw_text(np, config.COLS, config.ROWS, s, color = color, spacing=1, serpentine=True)
    np.write()
    time.sleep(0.1)


def side_burns(np):
    # side burns
    for x in [0, 1, 2, config.COLS - 3, config.COLS - 2, config.COLS - 1]:
        np[xy_to_pixel(x, 0)] = (20, 0, 0)
        np[xy_to_pixel(x, 1)] = (10, 10, 0)
        np[xy_to_pixel(x, 2)] = (0, 20, 0)
        np[xy_to_pixel(x, 3)] = (0, 0, 20)
        np[xy_to_pixel(x, 4)] = (0, 0, 20)
        # np.write()

# Map x,y to pixel number
def xy_to_pixel(x, y):
    if y % 2 == 1:
        x = config.COLS - 1 - x
    return y * config.COLS + x