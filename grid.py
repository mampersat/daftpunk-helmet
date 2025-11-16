import config

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