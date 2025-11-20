# main.py
import fivefont as ff
import random
import time
import math

ROWS = 5
COLS = 21
# ROW_LENGTHS = (21, 21, 21, , 35)  # top to bottom, adjust to your actual counts

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
    def _ansi_rgb(r, g, b, gamma=0.1):
        # gamma < 1 brightens; gamma > 1 darkens
        def boost(x):
            return int(255 * ((x / 255.0) ** gamma))
        r, g, b = boost(r), boost(g), boost(b)
        return f"\x1b[38;2;{r};{g};{b}m"

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

N_PIX   = ROWS * COLS
np = MockNeoPixel(0, N_PIX, width=COLS, serpentine=True)

def main_loop():

    ff.draw_text(np, COLS, ROWS, "HELLO", color=(55, 55, 55), spacing=1, serpentine=True)
    np.write()

    side_burns()

    # Clock
    while True:
        t = time.localtime()  # keep as struct_time, not string

        hour = t[3]

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
        side_burns()
        ff.draw_text(np, COLS, ROWS, s, color = color, spacing=1, serpentine=True)
        np.write()
        time.sleep(0.1)


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
    