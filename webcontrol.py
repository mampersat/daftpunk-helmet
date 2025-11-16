# webcontrol.py — tiny, simple webserver for Pico W (MicroPython)
import network, socket, json, time

def connect_wifi(cfg_path="wifi.json", timeout_ms=10000):
    """Connect to Wi-Fi in STA mode using wifi.json. Returns wlan or None."""
    try:
        with open(cfg_path) as f:
            cfg = json.load(f)
    except:
        print("wifi.json missing; skipping Wi-Fi.")
        return None

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to", cfg["ssid"], "...")
        wlan.connect(cfg["ssid"], cfg["password"])
        t0 = time.ticks_ms()
        while (not wlan.isconnected()
               and time.ticks_diff(time.ticks_ms(), t0) < timeout_ms):
            time.sleep_ms(100)

    if wlan.isconnected():
        print("Wi-Fi STA connected:", wlan.ifconfig())
        return wlan
    print("Wi-Fi connect failed.")
    return None


def create_server(port=80):
    """Return a listening socket with a short accept timeout (simple & robust)."""
    addr = socket.getaddrinfo("0.0.0.0", port)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(2)
    s.settimeout(0.5)   # block up to 0.5s on accept() so main loop still runs
    print("HTTP server listening on", addr)
    return s


def _parse_path_qs(first_line):
    # "GET /set?mode=bars&text=HI HTTP/1.1"
    try:
        _, full, _ = first_line.split(" ", 2)
    except ValueError:
        return "/", {}
    if "?" in full:
        path, qs = full.split("?", 1)
    else:
        path, qs = full, ""
    params = {}
    if qs:
        for pair in qs.split("&"):
            if "=" in pair:
                k, v = pair.split("=", 1)
                v = v.replace("+", " ").replace("%20", " ")
                params[k] = v
    return path, params


def _resp(cl, body, status="200 OK", ctype="text/html; charset=utf-8"):
    print("Response:", status)
    cl.send("HTTP/1.1 {}\r\nContent-Type: {}\r\nConnection: close\r\n\r\n".format(status, ctype))
    if body:
        cl.send(body)


def _parse_color(s):
    """Parse a color string into an (r,g,b) tuple.

    Accepts:
      - hex: "#RRGGBB" or "RRGGBB"
      - rgb function: "rgb(r,g,b)"
      - comma-separated: "r,g,b"

    Returns (r,g,b) with ints 0-255, or None on parse failure.
    """
    if not s:
        return None
    s = s.strip()
    # hex form
    if s.startswith('#'):
        s2 = s[1:]
        if len(s2) == 6:
            try:
                r = int(s2[0:2], 16)
                g = int(s2[2:4], 16)
                b = int(s2[4:6], 16)
                return (r, g, b)
            except Exception:
                return None
    # rgb(...) form
    if s.lower().startswith('rgb(') and s.endswith(')'):
        s = s[s.find('(')+1:-1]

    # comma-separated numbers
    parts = [p.strip() for p in s.split(',')]
    if len(parts) != 3:
        return None
    try:
        vals = [int(float(p)) for p in parts]
    except Exception:
        return None
    # clamp to 0-255
    vals = [max(0, min(255, v)) for v in vals]
    return (vals[0], vals[1], vals[2])


def serve_once(sock, state, available_modes=None):
    """
    Handle at most one HTTP request. Keep it simple:
    - blocking accept up to 0.5s (socket timeout)
    - blocking recv once (small requests)
    """
    try:
        cl, addr = sock.accept()
    except OSError:
        return  # no client this tick

    try:
        print('Client connected from', addr)
        cl.settimeout(2)
        req = cl.recv(1024)
        if not req:
            return

        first = req.split(b"\r\n", 1)[0].decode("utf-8", "ignore")
        path, params = _parse_path_qs(first)
        print(f"{first=}")

        if path.startswith("/set"):
            
            print(f"HTTP:{path=}, {params=}", path, params, "before mode:", state["mode"])

            # apply params
            if "mode" in params:
                state["mode"] = params["mode"]
                print("Set mode to", state["mode"])

            if "text" in params and params["text"] and state["mode"] == "text":
                state["text"] = params["text"]
                state["mode"] = "text"
                print("Set text and mode")

            # color param: accept RRGGBB (no #), #RRGGBB, rgb(...) or r,g,b
            if "color" in params and params["color"]:
                parsed = _parse_color(params["color"])
                if parsed:
                    state["color"] = parsed
                    print("Set color to", state["color"])
                else:
                    print("Invalid color param:", params["color"])

            # proper redirect back to root
            cl.send(
                "HTTP/1.1 303 See Other\r\n"
                "Location: /\r\n"
                "Cache-Control: no-store\r\n"
                "Connection: close\r\n"
                "\r\n"
            )
            return

        # root page
        # build buttons for modes
        mode_buttons = " ".join(
            '<a class="btn" href="/set?mode={0}">{0}</a>'.format(m)
            for m in available_modes
        )

        words = [
            "HELLO",
            "HAPPY",
            "SAD",
            "BYE",
            "DAFT PUNK",
            "ALIVE",
            "ROBOT ROCK",
            "HUMAN",
            "ONE MORE TIME",
            "TECHNOLOGIC",
            "WORK IT",
            "LOVE",
            "DISCO",
            "FUNK",
        ]

        quick_links = " ".join(
            '<a class="btn" href="/set?mode=text&text={0}">{0}</a>'.format(w.upper())
            for w in words
        )
        

        html = """<!doctype html>
<html><head><meta charset="utf-8"><title>Helmet</title>
<style>
body {{font-family:sans-serif;background:#111;color:#eee;text-align:center}}
button {{font-size:1.1rem;margin:.25rem;padding:.4rem .8rem}}
input[type=text] {{width:80%%;font-size:1rem;padding:.3rem}}
/* styled anchor that looks like the buttons above */
.btn {{
    display:inline-block;
    text-decoration:none;
    color:inherit;
    background:#222;
    border:1px solid #444;
    padding:.4rem .8rem;
    margin:.25rem;
    font-size:1.1rem;
    border-radius:4px;
}}
.btn:hover {{ background:#333 }}
</style></head>
<body>
<h1>Daft Punk Helmet</h1>
<p>Mode: <b>{mode}</b> — Brightness: {b:.2f}</p>
<form action="/set" method="get">
<p>
    {mode_buttons}
    <div>
        <input name="text" value="{text}">
        <button name="mode" value="text">Text</button>
    </div>

 </p>
</form>
<p>
<a class="btn" href="/set?color=100,100,100">White</a>
<a class="btn" href="/set?color=100,0,0">Red</a>
<a class="btn" href="/set?color=0,0,100">Blue</a>
<a class="btn" href="/set?color=0,100,0">Green</a>
<p>
    {quick_links}
</p>
 
</body></html>""".format(mode=state["mode"], 
                         b=state["brightness"], 
                         text=state["text"], 
                         quick_links=quick_links, 
                         mode_buttons=mode_buttons  )
        

        _resp(cl, html)
    finally:
        try: cl.close()
        except: pass
