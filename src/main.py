import network
import credentials
from time import sleep
import ntptime
import machine
import urequests as requests

host = "http://worldtimeapi.org/api/timezone/America/New_York"

def connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(credentials.SSID,credentials.PASSWORD)
    while wlan.isconnected() == False:
        sleep(1)
        
 
def syncTime():
    try:
        current = requests.get(url=host).json()["datetime"]
        #current = current.json()["datetime"]
        year = current[0:4]
        month = current.split('-')[1]
        day = current.split('-')[2].split('T')[0]
        weekday = 0
        hour, minute = current.split('T')[1].split(':')[0:2]
        seconds, microseconds = current.split('T')[1].split(':')[-2].split('-')[0].split('.')
        timeArray = [year,month,day,weekday,hour,minute,seconds, microseconds]
        timeArray = [int(i) for i in timeArray]
        machine.RTC.datetime(timeArray)
    except:
        ntptime.settime()
    
    
def autoCalibrate():
    try:
        syncTime()
    except:
        machine.RTC.now() #use whatever time the controller thinks it is
    
        
## Reboot if no internet
try:
    connect()
except KeyboardInterrupt:
    machine.reset()

