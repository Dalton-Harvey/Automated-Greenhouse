import network
import time
from machine import Pin

# Configure onboard LED
led = Pin("LED", Pin.OUT)

SSID = 'hardy1'
PASSWORD = 'hardyrje'

# Blink the LED to indicate startup
for _ in range(5):
    led.toggle()
    time.sleep(0.1)

def connect():
    try:
        # Connect to Wi-Fi
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(SSID, PASSWORD)

        # Wait for connection
        while not wlan.isconnected():
            led.toggle()
            time.sleep(0.5)
        
        return True
    except Exception as e:
        return False

# try twice, if either succeeds, light LED
led.value(connect() or connect())