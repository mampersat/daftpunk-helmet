# modes/scroll.py
import fivefont as ff
import config

def step(np, state, t):
    # render text in state["text"], with brightness
    color = state["color"]
    np.fill((0,0,0))
    ff.scroll_text(np, config.COLS, config.ROWS, state["text"], color=color, spacing=1, serpentine=True)
    
    np.write()
