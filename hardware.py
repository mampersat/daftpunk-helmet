# hardware.py
import machine, neopixel

PIN_LED = 28
ROWS = 5
COLS = 21
NUM_PIXELS = ROWS * COLS

def init_pixels():
    return neopixel.NeoPixel(machine.Pin(PIN_LED), NUM_PIXELS)

def init_button(pin=15):
    btn = machine.Pin(pin, machine.Pin.IN, machine.Pin.PULL_UP)
    return btn

def button_pressed(btn):
    return not btn.value()

