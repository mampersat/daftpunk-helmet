# modes/textmode.py
import fivefont as ff
import config

def step(np, state, t):
    # render text in state["text"], with brightness
    print("Text mode:", state.get("text", ""))
    np.fill((0,0,0))
    ff.draw_text(np, config.COLS, config.ROWS, state["text"], color=(55, 55, 55), spacing=1, serpentine=True)

    np.write()
