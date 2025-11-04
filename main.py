# main.py
import fivefont as ff

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
              speed_cols=1, delay_ms=10, serpentine=True)

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

# Map pixxel number to x,y
def pixel_to_xy(p):
    # pixels in each row
    counts = (20, 20, 20, 20, 20)
    a = 0
    for row, count in enumerate(counts):
        if p < a + count:
            return (row, p - a)
        a += count


if __name__ == "__main__":
    main_loop()
    