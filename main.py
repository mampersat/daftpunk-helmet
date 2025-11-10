# main.py
import fivefont as ff
import starfield
import time
import math

ROWS = 5
COLS = 21
# ROW_LENGTHS = (21, 21, 21, , 35)  # top to bottom, adjust to your actual counts

# Portable setup: Pico on-device vs desktop mock
try:
    import machine, neopixel, time, random
    IS_PICO = True
    PIN_NUM = 28
    N_PIX   = ROWS * COLS           # e.g., 7 rows * 17 cols
    np = neopixel.NeoPixel(machine.Pin(PIN_NUM), N_PIX)

except ImportError:
    import time, random
    IS_PICO = False

    # ===== Mock with ASCII colored circles =====
    class MockNeoPixel(list):
        def __init__(self, pin, n, *, width=None, serpentine=True):
            super().__init__([(0, 0, 0)] * n)
            self.n = n
            self.width = width     # e.g., 17
            self.serpentine = serpentine
            self._fg = True        # use colored foreground glyphs
            self._dot = "●"        # full circle (fallback: "o")
            self._off = "·"        # dim dot for (0,0,0)

        # ANSI truecolor helpers
        @staticmethod
        def _ansi_rgb(r, g, b):
            return f"\x1b[38;2;{r};{g};{b}m"  # foreground
        @staticmethod
        def _reset():
            return "\x1b[0m"

        def fill(self, color):
            for i in range(self.n):
                self[i] = color

        def write(self):
            """Render pixels as colored ASCII circles in a grid."""

            # print("\033[2J\033[H", end="")
            print("\033c", end="")


            if self.width is None or self.width <= 0:
                # Linear render
                line = []
                for (r, g, b) in self:
                    if (r, g, b) == (0, 0, 0):
                        line.append(self._off)
                    else:
                        # 
                        line.append(self._ansi_rgb(r, g, b) + self._dot + self._reset())
                print("".join(line))
                return

            cols = self.width
            rows = (self.n + cols - 1) // cols
            out_lines = []
            for row in range(rows):
                seg = []
                for col in range(cols):
                    idx = row * cols + col
                    if idx >= self.n:
                        seg.append(" ")
                        continue
                    # Map serpentine if requested (visualize as you wired it)
                    wire_col = (cols - 1 - col) if (self.serpentine and (row % 2 == 1)) else col
                    wire_idx = row * cols + wire_col
                    r, g, b = self[wire_idx]
                    if (r, g, b) == (0, 0, 0):
                        seg.append(self._off)
                    else:
                        seg.append(self._ansi_rgb(r, g, b) + self._dot + self._reset())
                out_lines.append(" ".join(seg))
            print("\n".join(out_lines))

    class MockPin:
        def __init__(self, n): self.n = n

    # Configure your mock for a 7x17 visor (serpentine wiring default)
    PIN_NUM = 28
    N_PIX   = ROWS * COLS
    np = MockNeoPixel(MockPin(PIN_NUM), N_PIX, width=COLS, serpentine=True)

def main_loop():
    print("Running on Pico" if IS_PICO else "Running on desktop (mock)")


    ff.draw_text(np, COLS, ROWS, "HELLO", color=(55, 55, 55), spacing=1, serpentine=True)
    np.write()

    side_burns()

    if IS_PICO:
        import ntp
        

    # Clock
    while True:
        t = time.localtime()  # keep as struct_time, not string

        hour = t[3]

        if IS_PICO:
            hour -= 5

        hour = hour % 12
        if hour == 0:
            hour = 12

        s = "%d:%02d" % (hour, t[4])  # hour (12-hour) and minute

        # Red at the top of every 0m/30m, blue at 15m/45m, green at 30m/60m
        if (t[4] % 30) < 10:
            color = (0, 100, 0)
        elif (t[4] % 30) < 20:
            color = (0, 0, 100)
        else:
            color = (100, 0, 0)

        np.fill((0, 0, 0))        
        side_burns()
        ff.draw_text(np, COLS, ROWS, s, color = color, spacing=1, serpentine=True, x_start=3)
        np.write()
        time.sleep(0.5)


    while True:
        t = time.time()
        
        for i in range(N_PIX):
            x, y = pixel_to_xy(i)
            # val = int((math.sin(t) + 1) / 2 * 255)
            val = (x + int(t)) % 5
            np[i] = (val, val, val)
            # print(val)

        np.write()
        time.sleep(0.1)
        print(val)


    while True:
        # Simple rainbow wipe
        for i in range(N_PIX):
            x, y = pixel_to_xy(i)
            r = (x * 5) % 256
            g = (y * 3) % 256
            b = (x * 7) % 256
            np[i] = (r, g, b)
            np.write()
            time.sleep(0.01)
            
    while True:
        # Starfield effect
        for t in range(0, 1000, 5):
            for p in range(N_PIX):
                x, y = pixel_to_xy(p)
                r, g, b = starfield.starfield_pixel(x * (200 // COLS), y * (200 // ROWS), t / 10.0)
                np[p] = (r, g, b)
            np.write()
            time.sleep(0.05)
            
    chorus = ("WORK", "1T", "HARD", "ER",
        "MAKE", "IT", "BETT", "ER",
        "DO", "IT", "FAST", "ER",
        "MAKE", "US", "STRONG", "ER",
        "MORE THAN", "EVER", "HOUR AFTER"
        "OUR", "WORK IS",
        "NEVER", "OVER",
        "OVER", "OV3E", "OVER", "0V3R")

    while True:

        for word in chorus:
            ff.draw_text(np, COLS, ROWS, word, color=(155,80,40), spacing=1, serpentine=True)
            np.write()
            time.sleep(1.952 / 4)
            np.fill((0,0,0))
            np.write()

        ff.scroll_text(np, COLS, ROWS, "HARDER   BETTER   FASTER   STRONGER    OUR WORK IS     NEVER     OVER     NEVER OVER NEVER OVER NEVER OVER", color=(0,0,100), spacing=1,
              speed_cols=1, delay_ms=3, serpentine=True)

        ff.scroll_text(np, COLS, ROWS, "                      DAFT PUNK", color=(100,0,0), spacing=1,
               speed_cols=1, delay_ms=50, serpentine=True)

        ff.scroll_text(np, COLS, ROWS, "                      DAFT PUNK", color=(0,100,0), spacing=1,
               speed_cols=1, delay_ms=50, serpentine=True)
               
        ff.scroll_text(np, COLS, ROWS, "                      DAFT PUNK", color=(0,0,100), spacing=1,
               speed_cols=1, delay_ms=50, serpentine=True)




    while True:

        for i in range(N_PIX):
            if (random.randint(1,3) == 1):
                np[i] = (random.randint(0,10), random.randint(0,10), random.randint(0,10))
            else:
                np[i] = (0, 0, 0)
                

        np.write()
        time.sleep(1)

def side_burns():
    # side burns
    for x in [0, 1, 2, COLS - 3, COLS - 2, COLS - 1]:
        np[xy_to_pixel(x, 0)] = (20, 0, 0)
        np[xy_to_pixel(x, 1)] = (10, 10, 0)
        np[xy_to_pixel(x, 2)] = (0, 20, 0)
        np[xy_to_pixel(x, 3)] = (0, 0, 20)
        np[xy_to_pixel(x, 4)] = (0, 0, 20)
        # np.write()

# Map pixel number to x,y
# The pixels are in a serpintine layout with COLS columns and ROWS rows
def pixel_to_xy(p):
    row = p // COLS
    col = p % COLS
    if row % 2 == 1:
        col = COLS - 1 - col
    return (col, row)

# Map x,y to pixel number
def xy_to_pixel(x, y):
    if y % 2 == 1:
        x = COLS - 1 - x
    return y * COLS + x


if __name__ == "__main__":
    main_loop()
    