# main.py — tiny glue: Wi-Fi + web + a placeholder animation loop
import time
import machine, neopixel
from modes import textmode, clock, tron

import webcontrol

# Runtime state (kept here to keep things minimal)
state = {
    "mode": "clock",
    "brightness": 0.4,
    "text": "words",
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
    # super simple demo that changes color with mode/brightness
    b = state["brightness"]
    if state["mode"] == "bars":
        # pulse green
        v = int(255 * b * (0.5 + 0.5*( (t*2) % 1 )))
        fill_color((0, v, 0))
    elif state["mode"] == "text":
        textmode.step(np, state, t)
    elif state["mode"] == "clock":
        clock.step(np, state, t)
    elif state["mode"] == "tron":
        tron.step(np, state, t)
    else:  # wave
        v = int(255 * b)
        fill_color((v, 0, v))

def main():
    wlan = webcontrol.connect_wifi()   # ok if None
    sock = None
    if wlan:
        sock = webcontrol.create_server()

    t0 = time.ticks_ms()
    while True:
        # 1) serve one HTTP request (if server exists)
        if sock:
            webcontrol.serve_once(sock, state)

        # 2) draw one frame
        t = (time.ticks_diff(time.ticks_ms(), t0) / 1000.0)
        demo_frame(t)

        # 3) small delay (~30 FPS)
        # print a . with no newline to show we're alive
        print(".", end="")
        time.sleep_ms(30)

if __name__ == "__main__":
    main()
