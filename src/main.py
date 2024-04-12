import network
import credentials
from time import sleep
import time
import ntp
import machine
import uasyncio as asyncio
import output

DEBUG = True


## i2c
I2C_ENABLE = False
sdaPIN=machine.Pin(0)
sclPIN=machine.Pin(1)
slaveAddr = 0x30
i2c=machine.I2C(0,sda=sdaPIN, scl=sclPIN, freq=100_000)
devices = i2c.scan() # debugging
while(I2C_ENABLE and len(devices) < 1):
    sleep(1)
    



def connect() -> bool:
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(credentials.SSID,credentials.PASSWORD)
    while wlan.isconnected() == False:
        sleep(1)
    return wlan.isconnected()
        
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
            if DEBUG: print("Synchronized successfully")
        except:
            if DEBUG: print("Failed to sync")
            pass #use whatever time the controller thinks it is
        if DEBUG:
            print("done")
            print(time.localtime())
        asyncio.sleep(7*24*60*60) # sleeps task for a week



## Main ##################################################################################################################
async def main() -> None:
    asyncio.create_task(autoCalibrate())
    asyncio.sleep(10) # giving RTC time to sync
    while(True):
        hour, minute = time.localtime()[3:5]
        hour = (hour - 4) % 12
        print(f"{hour}:{minute}")
        try:
            acks = i2c.writeto(slaveAddr,bytes(minute))
            if DEBUG: print(f"Sent: {minute}\nReceived: {acks}") # debugging
        except:
            if DEBUG: print("i2c failed") # debugging
            ...
            
        
        output.writeOutput(hour,minute)
        
        sleep(1)





## Reboot if no internet
try:
    connect()
except KeyboardInterrupt:
    machine.reset()    

output.setup()

asyncio.run(main())