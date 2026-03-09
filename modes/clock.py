# main.py
import fivefont as ff
import time
import config

PICO = True
try:
    import ntp
except ImportError:
    PICO = False

# Hours to add to UTC for display (Pico NTP is UTC). e.g. -5 for EST, -4 for EDT
TIMEZONE_OFFSET_HOURS = -5

def _weekday(year: int, month: int, day: int) -> int:
    """Weekday 0=Mon..6=Sun (Zeller's congruence, no datetime)."""
    if month < 3:
        month += 12
        year -= 1
    q, m, k, j = day, month, year % 100, year // 100
    h = (q + (13 * (m + 1)) // 5 + k + k // 4 + j // 4 - 2 * j) % 7
    return (h + 5) % 7  # Zeller 0=Sat,1=Sun,2=Mon,... -> 0=Mon,...,6=Sun

def _eastern_offset_utc(year: int, month: int, day: int, hour_utc: int) -> int:
    """Return offset hours (UTC + offset = Eastern). EST=-5, EDT=-4. DST: 1st Sun Mar 2am -> 1st Sun Nov 2am."""
    if month < 3 or month > 11:
        return -5
    if month > 3 and month < 11:
        return -4
    # March: DST starts 1st Sunday at 7:00 UTC
    w1 = _weekday(year, 3, 1)
    first_sun_march = 1 + (6 - w1) % 7
    if month == 3:
        if day < first_sun_march or (day == first_sun_march and hour_utc < 7):
            return -5
        return -4
    # November: DST ends 1st Sunday at 6:00 UTC
    w1 = _weekday(year, 11, 1)
    first_sun_nov = 1 + (6 - w1) % 7
    if month == 11:
        if day < first_sun_nov or (day == first_sun_nov and hour_utc < 6):
            return -4
        return -5
    return -4

def _utc_offset_hours(t) -> int:
    """Return hours to add to UTC for local display (DST-aware for US Eastern)."""
    if not PICO:
        return 0  # desktop uses system local time
    return _eastern_offset_utc(t[0], t[1], t[2], t[3])

def step(np, state, t):
    t = time.localtime()  # keep as struct_time, not string

    hour = t[3]

    # Pico NTP returns UTC; adjust for local display (DST-aware for US Eastern)
    if PICO:
        hour += _utc_offset_hours(t)

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
    side_burns(np)
    ff.draw_text(np, config.COLS, config.ROWS, s, color = color, spacing=1, serpentine=True)
    np.write()
    time.sleep(0.1)


def side_burns(np):
    # side burns
    for x in [0, 1, 2, config.COLS - 3, config.COLS - 2, config.COLS - 1]:
        np[xy_to_pixel(x, 0)] = (20, 0, 0)
        np[xy_to_pixel(x, 1)] = (10, 10, 0)
        np[xy_to_pixel(x, 2)] = (0, 20, 0)
        np[xy_to_pixel(x, 3)] = (0, 0, 20)
        np[xy_to_pixel(x, 4)] = (0, 0, 20)
        # np.write()

# Map x,y to pixel number
def xy_to_pixel(x, y):
    if y % 2 == 1:
        x = config.COLS - 1 - x
    return y * config.COLS + x