# main.py — tiny glue: Wi-Fi + web + a placeholder animation loop
import time
import machine
import neopixel
import os

from modes import clock, grot, rain, text, tron
import webcontrol

# Runtime state (kept here to keep things minimal)
state = {
    "mode": "clock",
    "brightness": 0.4,
    "text": "words",
    "color": (150, 0, 0),
}

# Hardware (adjust to your pins/layout)
ROWS, COLS = 5, 21
PIN_LED = 28
NUM = ROWS * COLS
np = neopixel.NeoPixel(machine.Pin(PIN_LED), NUM)

def fill_color(rgb):
    for i in range(NUM):
        np[i] = rgb
    np.write()

def demo_frame(t):
    mode_name = state["mode"]  # e.g. "clock"
    print("Mode:", mode_name)
    try:
        mode_module = getattr(modes, mode_name)
        mode_func = getattr(mode_module, "step")
    except AttributeError:
        # fallback
        from modes import clock as mode_module
        mode_func = mode_module.step
    mode_func(np, state, t)

def main():
    # wlan = webcontrol.connect_wifi()   # ok if None
    # sock = None
    #if wlan:
    #    sock = webcontrol.create_server()

    # discover the modes in the modes directory
    files = os.listdir("modes")
    available_modes = [f[:-3] for f in files if f.endswith(".py") and f != "__init__.py"]

    modes_map = {}

    for name in available_modes:
        try:
            # Import as: modes.clock  -> returns the submodule object
            mod = __import__("modes." + name, None, None, (name,))
            modes_map[name] = mod
        except Exception as e:
            print("Error importing mode", name, e)
    print("Available modes:", available_modes)


    t0 = time.ticks_ms()
    while True:
        # 1) serve one HTTP request (if server exists)
        webcontrol.serve_once(state, available_modes=available_modes)

        # 2) draw one frame
        t = (time.ticks_diff(time.ticks_ms(), t0) / 1000.0)
        modes_map[state["mode"]].step(np, state, t)

        # 3) small delay (~30 FPS)
        # print a . with no newline to show we're alive
        print(".", end="")
        time.sleep_ms(10)
        
if __name__ == "__main__":
    main()
