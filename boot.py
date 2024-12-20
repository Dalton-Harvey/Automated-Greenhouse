"""Connect to the wifi network on boot
Provides global variable IP to be used by other scripts
Sometimes runs more than once when debugging with VSCode, it can generally be ignored"""

import network
from time import sleep
from machine import Pin
import ntptime


def get_ip():
    wlan = network.WLAN(network.STA_IF)
    if wlan.ifconfig():
        return wlan.ifconfig()[0]
    else:
        return ''


def boot():
    wifi_path = 'secrets/wifi_credentials'
    log_path = 'log/boot.log'
    
    log = []
    
    try:
        with open(wifi_path, 'r') as wifi_file:
            ssid, password, *_ = wifi_file.read().splitlines()
        
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(ssid, password)
        
        log.append(f'Connecting to SSID {ssid}...')
        
        led = Pin('LED', Pin.OUT)
        
        wait_time = 30
        interval = 0.5
        checks = int(wait_time / interval)
        for i in range(checks):
            sleep(interval)
            led.toggle()
            if wlan.isconnected():
                led.on()
                break
        else:
            # loop finished without breaking, unable to connect
            led.off()
            log.append('Failed to connect to WiFi')
            raise Exception(f'Timed out while attempting to connect to SSID {ssid} after {wait_time} seconds')
        
        IP = wlan.ifconfig()[0]
        
        log.append(f'Connected to SSID {ssid} with address: {IP}')
    
    except Exception as e:
        log.append(f'Exception: {e}')
    
    with open(log_path, 'w') as log_file:
        log_file.write('\n'.join(log) + '\n')

    ntptime.settime()
    


if __name__ == '__main__':
    boot()