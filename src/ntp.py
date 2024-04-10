import network
import credentials
from time import sleep
import time
import ntp
import machine
import uasyncio as asyncio
import output

host = "http://worldtimeapi.org/api/timezone/America/New_York"

'''
## i2c
sdaPIN=machine.Pin(0)
sclPIN=machine.Pin(1)
i2c=machine.I2C(0,sda=sdaPIN, scl=sclPIN, freq=400000)
devices = i2c.scan() # debugging
while(devices < 1):
    sleep(1)
    '''



def connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(credentials.SSID,credentials.PASSWORD)
    while wlan.isconnected() == False:
        sleep(1)
        

async def syncTime() -> None:
    try:
        ntp.set_time(ntp.host1)
    except:
        ntp.set_time(ntp.host2)
    finally: # giving up
        return
    
async def autoCalibrate():
    while(True):
        try:
            await syncTime()
        except:
            pass #use whatever time the controller thinks it is
        
        print("done")
        print(time.localtime())
        asyncio.sleep(7*24*60*60) # sleeps task for a week



## Main ##################################################################################################################
async def main():
    asyncio.create_task(autoCalibrate())
    asyncio.sleep(10) # giving RTC time to sync
    while(True):
        #minute, hour = machine.RTC.datetime()[-4:-2]
        '''
        i2c.start()
        i2c.write(minute) # writes minutes to i2c bus
        i2c.stop()
        
        output.writeOutput(hour)
        '''
        hours, minutes = time.localtime()[3:5]
        hours = (hours - 4) % 12
        print(f"{hours}:{minutes}")
        sleep(1)


## Reboot if no internet
try:
    connect()
except KeyboardInterrupt:
    machine.reset()    


asyncio.run(main())