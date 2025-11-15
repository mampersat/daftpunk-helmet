# modes/textmode.py
import fivefont  # or whatever your text renderer is called

def step(np, state, t):
    # render text in state["text"], with brightness
    print("Text mode:", state.get("text", ""))
    for i in range(len(np)):
        np[i] = (i % 255, (i * 2) % 255, (i * 3) % 255)  # clear
    np.write()
