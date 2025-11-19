# webcontrol.py — tiny, simple webserver for Pico W (MicroPython)
import network, socket, json, time, select

# ---- Wi-Fi setup at import (blocking here is ok) ---------------------------

TIMEOUT_MS = 10000

with open("wifi.json") as f:
    cfg = json.load(f)

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    print("Connecting to", cfg["ssid"], "...")
    wlan.connect(cfg["ssid"], cfg["password"])
    t0 = time.ticks_ms()
    while (not wlan.isconnected()
           and time.ticks_diff(time.ticks_ms(), t0) < TIMEOUT_MS):
        time.sleep_ms(100)

if wlan.isconnected():
    print("Wi-Fi STA connected:", wlan.ifconfig())
else:
    print("Wi-Fi connect failed.")

# ---- HTTP server: one global listening socket + poller --------------------

sock = socket.socket()
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
sock.bind(addr)
sock.listen(2)
sock.setblocking(False)   # non-blocking accept
print("HTTP server listening on", addr)

poller = select.poll()
poller.register(sock, select.POLLIN)


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
    try:
        cl.send(
            "HTTP/1.1 {}\r\nContent-Type: {}\r\nConnection: close\r\n\r\n"
            .format(status, ctype)
        )
        if body:
            cl.send(body)
    except OSError:
        pass


def _parse_color(s):
    if not s:
        return None
    s = s.strip()
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
    if s.lower().startswith('rgb(') and s.endswith(')'):
        s = s[s.find('(')+1:-1]
    parts = [p.strip() for p in s.split(',')]
    if len(parts) != 3:
        return None
    try:
        vals = [int(float(p)) for p in parts]
    except Exception:
        return None
    vals = [max(0, min(255, v)) for v in vals]
    return tuple(vals)


def serve_once(state, available_modes=None):
    """
    Handle at most one HTTP request (non-blocking).
    Call this every frame from your main loop.
    """
    # Check if there's a pending connection on the listening socket
    print('X', end='')
    res = poller.poll(0)   # 0 ms → do NOT block
    if not res:
        return
    print(f"{res=}")
    print('Y', end='')
    # We only care about events on the listening socket
    ready = False
    for fd, event in res:
        if fd == sock and (event & select.POLLIN):
            ready = True
            break
    if not ready:
        return

    try:
        cl, addr = sock.accept()
    except OSError:
        return

    try:
        # non-blocking client socket as well
        print("Client connected from", addr)
        cl.setblocking(True)
        try:
            req = cl.recv(1024)
        except OSError:
            # no data yet; drop this client, browser will retry
            return

        if not req:
            return

        first = req.split(b"\r\n", 1)[0].decode("utf-8", "ignore")
        path, params = _parse_path_qs(first)
        print("HTTP:", path, params, "before mode:", state["mode"])

        if path.startswith("/set"):
            _handle_set(cl, state, params)
            return

        _handle_root(cl, state, available_modes)

    finally:
        try:
            cl.close()
        except OSError:
            pass


def _handle_set(cl, state, params):
    print("Set params:", params)
    if "mode" in params:
        state["mode"] = params["mode"]
    if "text" in params and params["text"]:
        state["text"] = params["text"]
        # if text supplied without mode, default to text mode
        if "mode" not in params:
            state["mode"] = "text"
    if "color" in params and params["color"]:
        parsed = _parse_color(params["color"])
        if parsed:
            state["color"] = parsed

    # redirect back to root
    try:
        cl.send(
            "HTTP/1.1 303 See Other\r\n"
            "Location: /\r\n"
            "Cache-Control: no-store\r\n"
            "Connection: close\r\n\r\n"
        )
    except OSError:
        pass


def _handle_root(cl, state, available_modes):
    if available_modes is None:
        available_modes = []
    mode_buttons = " ".join(
        '<a class="btn" href="/set?mode={0}">{0}</a>'.format(m)
        for m in available_modes
    )

    words = [
        "HELLO", "HAPPY", "SAD", "BYE",
        "DAFT PUNK", "AL1VE", "ROBOT ROCK", "HUMAN",
        "ONE MORE TIME", "TECHNOLOGIC", "WORK 1T",
        "LOVE", "D1SCO", "FUNK", "PB4UGO",
    ]
    quick_links = " ".join(
        '<a class="btn" href="/set?mode=text&text={0}">{0}</a>'.format(w)
        for w in words
    )

    html = """<!doctype html>
<html><head><meta charset="utf-8"><title>Helmet</title>
<style>
body {{font-family:sans-serif;background:#111;color:#eee;text-align:center}}
button {{font-size:1.1rem;margin:.25rem;padding:.4rem .8rem}}
input[type=text] {{width:80%%;font-size:1rem;padding:.3rem}}
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
<a class="btn" href="/set?color=100,100,100">White-ish</a>
<a class="btn" href="/set?color=100,0,0">Red</a>
<a class="btn" href="/set?color=0,0,100">Blue</a>
<a class="btn" href="/set?color=0,100,0">Green</a>
</p>
<p>
    {quick_links}
</p>
<p>
    <a href="https://github.com/mampersat/daftpunk-helmet" target="_blank">GitHub repo</a>
</p>
</body></html>""".format(
        mode=state["mode"],
        b=state["brightness"],
        text=state["text"],
        quick_links=quick_links,
        mode_buttons=mode_buttons,
    )

    _resp(cl, html)
