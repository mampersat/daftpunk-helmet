try:
    import machine, neopixel, time, random
    # Running on Pico (MicroPython)
    pin = machine.Pin(28)
    np = neopixel.NeoPixel(pin, 100)
    IS_PICO = True
except ImportError:
    # Running on desktop Python
    import random, time
    IS_PICO = False

    class MockNeoPixel(list):
        def __init__(self, pin, n):
            super().__init__([(0, 0, 0)] * n)
            self.n = n
        def write(self):
            # simulate sending data to LEDs
            print("Mock write:", self[:10], "...")
        def fill(self, color):
            for i in range(self.n):
                self[i] = color

    class MockPin:
        def __init__(self, n): self.n = n

    np = MockNeoPixel(MockPin(28), 100)

# Example usage
for i in range(np.n):
    np[i] = (random.randint(0, 50), 0, 0)
np.write()

print("Running on Pico" if IS_PICO else "Running on desktop")

while True:

    for i in range(100):
        if (random.randint(1,3) == 1):
            np[i] = (random.randint(0,20), random.randint(0,20), random.randint(0,20))
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

