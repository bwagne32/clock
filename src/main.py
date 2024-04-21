import network
import credentials
from time import sleep
import time
import ntp
import machine
import uasyncio as asyncio
import output
from lookup import i2cMessage, DEBUG
import uping





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
    while not wlan.isconnected():
        sleep(1)
    status = wlan.ifconfig()
    print( 'ip = ' + status[0] )
    return wlan.isconnected()
        
async def syncTime() -> None:
    try:
        ntp.set_time(ntp.host1)
    except:
        ntp.set_time(ntp.host2)
    
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
        await asyncio.sleep(700) # sleeps task for a week



## Main ##################################################################################################################
async def main() -> None:
    await syncTime()
    asyncio.create_task(autoCalibrate())
    #uping.ping('10.128.10.30')
    while(True):
        hour, minute, sec = time.localtime()[3:6]
        hour -= 4 # NTP server was 4 hours off for some reason
        
        if hour > 12: hour -= 12 # PM
        elif hour == 0: hour = 12 # incase midnight is treated as 0
        
        
        
        if DEBUG: print(f"{hour}:{minute}")
        
        flush = [0,0]
        
        try:
            acks = i2c.writeto(slaveAddr,i2cMessage(minute,flush))
            if DEBUG: print(f"Sent: {minute}\nReceived: {acks}") 
        except: # so the controller doesn't crash
            if DEBUG: print("i2c failed")
            
        
        output.writeOutput(hour,minute,sec)
        
        sleep(1)


## Reboot if no internet
try:
    connect()
except KeyboardInterrupt:
    machine.reset()    


asyncio.run(main())