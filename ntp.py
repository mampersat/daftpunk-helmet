import network
import ntptime
import utime

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('ShArVa', 'end dirt people main zero')

print('Connecting to WiFi...')
while not wlan.isconnected():
    utime.sleep(1)

ntptime.settime()  # syncs from NTP (UTC)
print(utime.localtime())

