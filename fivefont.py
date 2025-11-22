# fivefont.py — 3x5 font + renderer for 5-row LED matrices
import time

# 3x5 glyphs stored column-wise (width ≤3, height = 5).
# Each glyph is a tuple of columns; each column is a 5-bit int (LSB = row 0 / top).
# Example: column 0b10101 -> rows [1,0,1,0,1] from top to bottom.
FONT_3x5 = {
    " ": (),
    "!": (0b11110,),
    ".": (0b00010,),
    "-": (0b00100, 0b00100),
    "_": (0b00001,0b00001,0b00001),
    ":": (0b01010,),
    "/": (0b00001,0b00010,0b00100,0b01000,0b10000),
    "?": (0b10010,0b00001,0b00101,0b00010),

    "0": (0b11111,0b10001,0b11111),
    # "1": (0b00000,0b00000,0b11111),
    "1": (0b11111,),
    "2": (0b11001,0b10101,0b10011),
    "3": (0b10101,0b10101,0b11111),
    "4": (0b00111,0b00100,0b11111),
    "5": (0b10111,0b10101,0b11101),
    "6": (0b11111,0b10101,0b11101),
    "7": (0b10001,0b00101,0b00011),
    "8": (0b11111,0b10101,0b11111),
    "9": (0b10111,0b10101,0b11111),

    "A": (0b11110,0b00101,0b11110),
    "B": (0b11111,0b10101,0b01010),
    "C": (0b01110,0b10001,0b10001),
    "D": (0b11111,0b10001,0b01110),
    "E": (0b11111,0b10101,0b10001),
    "F": (0b11111,0b00101,0b00001),
    "G": (0b01110,0b10001,0b11101),
    "H": (0b11111,0b00100,0b11111),
    "I": (0b10001,0b11111,0b10001),
    # "I": (0b11111),
    "J": (0b10001,0b11110,0b00000),
    "K": (0b11111,0b00100,0b11011),
    "L": (0b11111,0b10000,0b10000),
    "M": (0b11111,0b00010,0b11111),
    "N": (0b11111,0b00001,0b11110),
    "O": (0b01110,0b10001,0b01110),
    "P": (0b11111,0b00101,0b00010),
    "Q": (0b01110,0b10001,0b11110),
    "R": (0b11111,0b00101,0b11010),
    "S": (0b10010,0b10101,0b01001),
    "T": (0b00001,0b11111,0b00001),
    "U": (0b11111,0b10000,0b11111),
    "V": (0b01111,0b10000,0b01111),
    "W": (0b11111,0b01000,0b11111),
    "X": (0b11011,0b00100,0b11011),
    "Y": (0b00011,0b11100,0b00011),
    "Z": (0b11001,0b10101,0b10011),
}

# Optional gamma/log LUT hook (identity by default)
LUT = list(range(256))
def map_rgb(r,g,b,lut=LUT): return (lut[r], lut[g], lut[b])

def pixel_index(x:int, y:int, width:int, height:int, serpentine=True) -> int:
    """Map (x,y) -> linear index for serpentine-wired rows; y=0 is top."""
    if not (0 <= x < width and 0 <= y < height):
        return -1
    if serpentine and (y % 2 == 1):
        x = width - 1 - x
    return y * width + x

def draw_char(np, width, height, x0, ch, color=(255,255,255), spacing=1, serpentine=True):
    """Draw a single 3x5 char with optional spacing column after it. Returns char width inc. spacing."""
    if height != 5:
        raise ValueError("This renderer expects height=5.")
    glyph = FONT_3x5.get(ch.upper(), FONT_3x5[" "])
    gw = len(glyph)
    r,g,b = map_rgb(*color)
    # Blit columns
    for dx in range(gw):
        colbits = glyph[dx]
        for y in range(5):        # y=0 top row bit0
            if (colbits >> y) & 1:
                idx = pixel_index(x0+dx, y, width, height, serpentine)
                if idx >= 0:
                    np[idx] = (r,g,b)
    # spacing column left blank
    return gw + spacing

def draw_text(np, width, height, text, x_start=None, color=(255,255,255), spacing=1, serpentine=True):
    """
    Draw text horizontally centered (if x_start=None) or starting at x_start.
    Returns total pixel width of the rendered text.
    """
    # measure text width first
    text_width = 0
    for ch in text:
        glyph = FONT_3x5.get(ch.upper(), ())
        text_width += len(glyph) + spacing
    if text_width > 0:
        text_width -= spacing  # remove trailing space

    # if no explicit start, center horizontally
    if x_start is None:
        x_start = (width - text_width) // 2

    # now draw
    x = x_start
    for ch in text:
        x += draw_char(np, width, height, x, ch, color=color, spacing=spacing, serpentine=serpentine)
    return text_width

def draw_text_window(np, width, height, text, window_x, color=(255,255,255), spacing=1, serpentine=True):
    """
    Render a scrolled 'window view' by offsetting text left with window_x (>=0).
    Example: call with window_x increasing to scroll left.
    """
    # Clear frame
    for i in range(width*height):
        np[i] = (0,0,0)
    # Compute total text width so we can stop early if desired
    tw = 0
    for ch in text:
        tw += len(FONT_3x5.get(ch.upper(), ())) + spacing
    # Draw with negative start so left edge is at -window_x
    x0 = -window_x
    x = x0
    for ch in text:
        x += draw_char(np, width, height, x, ch, color=color, spacing=spacing, serpentine=serpentine)
    return tw

def scroll_text(np, width, height, text,
                color=(255, 255, 255),
                spacing=1,
                speed_cols=1,
                delay_ms=40,
                serpentine=True,
                write_fn=None,
                sleep_fn=None):
    """
    Simple blocking marquee: scrolls text from off-screen right to off-screen left.
    - Starts with an empty window (text fully off to the right),
      scrolls in, then fully off to the left.
    - write_fn: function to flush (defaults to np.write if present, else no-op).
    - sleep_fn: function to sleep milliseconds (MicroPython: time.sleep_ms).
    """
    import time

    # total text width in columns
    tw = 0
    for ch in text:
        tw += len(FONT_3x5.get(ch.upper(), ())) + spacing

    window = width  # visible window width

    # We want the text to start completely off-screen to the right and
    # exit completely off-screen to the left.
    # So let the window "x" offset run from -window (all blank)
    # to +tw (text has fully exited on the left).
    start = -window
    end = tw

    # Resolve write/sleep
    if write_fn is None:
        write_fn = getattr(np, "write", lambda: None)
    if sleep_fn is None:
        # desktop vs micropython-friendly
        sleep_fn = lambda ms: time.sleep(ms / 1000.0)

    for window_x in range(start, end + 1, max(1, speed_cols)):
        draw_text_window(
            np,
            width,
            height,
            text,
            window_x=window_x,
            color=color,
            spacing=spacing,
            serpentine=serpentine,
        )
        write_fn()
        sleep_fn(delay_ms)


