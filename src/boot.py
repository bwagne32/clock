import network
import credentials
import time
import ntptime
import machine


def connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(credentials.SSID,credentials.PASSWORD)
    while wlan.isconnected() == False:
        sleep(1)
        
def sync():
    ntptime.settime()
    machine.RTC().datetime()
        
## Reboot if no internet
try:
    connect()
except KeyboardInterrupt:
    machine.reset()
    
    
