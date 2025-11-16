# modes/textmode.py
import config
import grid

def step(np, state, t):
    # render text in state["text"], with brightness
    print("Text mode:", state.get("text", ""))
    np.fill((0,0,0))
    for c in range(config.COLS):
        np[grid.xy_to_pixel(c, 1)] = (0,0,150)
        np[grid.xy_to_pixel(c, 2)] = (0,0,150)
        np[grid.xy_to_pixel(c, 3)] = (0,0,150)

    np.write()
