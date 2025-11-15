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


def serve_once(sock, state):
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

        if path.startswith("/set"):
            # apply params
            if "mode" in params:
                state["mode"] = params["mode"]
            if "brightness" in params:
                if params["brightness"] == "up":
                    state["brightness"] = min(1.0, state["brightness"] + 0.1)
                elif params["brightness"] == "down":
                    state["brightness"] = max(0.05, state["brightness"] - 0.1)
            if "text" in params and params["text"]:
                state["text"] = params["text"]

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
        html = """<!doctype html>
<html><head><meta charset="utf-8"><title>Helmet</title>
<style>
body {{font-family:sans-serif;background:#111;color:#eee;text-align:center}}
button {{font-size:1.1rem;margin:.25rem;padding:.4rem .8rem}}
input[type=text] {{width:80%%;font-size:1rem;padding:.3rem}}
</style></head>
<body>
<h1>Daft Punk Helmet</h1>
<p>Mode: <b>{mode}</b> — Brightness: {b:.2f}</p>
<form action="/set" method="get">
<p>
  <button name="mode" value="bars">Bars</button>
  <button name="mode" value="text">Text</button>
  <button name="mode" value="wave">Wave</button>
</p>
<p>
  <button name="brightness" value="up">Brightness +</button>
  <button name="brightness" value="down">Brightness -</button>
</p>
<p>
  <input name="text" value="{text}">
  <button type="submit">Set Text</button>
</p>
</form>
</body></html>""".format(mode=state["mode"], b=state["brightness"], text=state["text"])
    

        _resp(cl, html)
    finally:
        try: cl.close()
        except: pass
