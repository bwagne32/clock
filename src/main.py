import network
import credentials
from time import sleep
import ntptime
import machine
import urequests as requests
import asyncio
import output

host = "http://worldtimeapi.org/api/timezone/America/New_York"

## i2c
sdaPIN=machine.Pin(0)
sclPIN=machine.Pin(1)
i2c=machine.I2C(0,sda=sdaPIN, scl=sclPIN, freq=400000)
devices = i2c.scan() # debugging
while(devices < 1):
    sleep(1)



def connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(credentials.SSID,credentials.PASSWORD)
    while wlan.isconnected() == False:
        sleep(1)
        

async def syncTime():
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
    
    
async def autoCalibrate():
    while(True):
        try:
            await syncTime()
        except:
            machine.RTC.now() #use whatever time the controller thinks it is
        
        asyncio.sleep(7*24*60*60) # sleeps task for a week



## Main ##################################################################################################################
def main():
    asyncio.create_task(autoCalibrate)
    asyncio.sleep(10) # giving RTC time to sync
    while(True):
        minute, hour = machine.RTC.datetime()[-4:-2]
        i2c.start()
        i2c.write(minute) # writes minutes to i2c bus
        i2c.stop()
        
        output.writeOutput(hour)
        
        sleep(10)


## Reboot if no internet
try:
    connect()
except KeyboardInterrupt:
    machine.reset()    


if __name__ == "__main__":
    main()