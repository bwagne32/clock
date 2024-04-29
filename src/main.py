import network
import credentials
from time import sleep
import time
import ntp
import machine
import uasyncio as asyncio
import output
from output import leaking, dontLeak
from lookup import i2cMessage, DEBUG
import uping



daylightSavings = False

## i2c
I2C_ENABLE = False
sdaPIN=machine.Pin(0)
sclPIN=machine.Pin(1)


tentacle = 0x30                                         # Pico GPIO expender
i2c=machine.I2C(0,sda=sdaPIN, scl=sclPIN, freq=100_000)
devices = i2c.scan() # debugging
while(I2C_ENABLE and len(devices) < 1):
    sleep(1)

## Wifi #####################################################################
def connect() -> bool:
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(credentials.SSID,credentials.PASSWORD)
    while not wlan.isconnected():
        sleep(1)
    status = wlan.ifconfig()
    print( 'ip = ' + status[0] )
    return wlan.isconnected()

## Time sync #################################################################     
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
        timeChange(daylightSavings)
        await asyncio.sleep(700) # sleeps task for a while

def timeChange(dayLightSavings) -> bool: # True if daylight savings else false
    # EDT -> daylight savings starts last sunday in march (3)
    # EST -> standard starts last sunday in october (10)
    # (year, month, mday, hour, minute, second, weekday, yearday)
    if (time.localtime()[1] == 3) and (time.localtime()[2] < 7) and (time.localtime()[6] == 6):
        return True
    elif (time.localtime()[1] == 10) and (time.localtime()[2] < 7) and (time.localtime()[6] == 6):
        return False
    return dayLightSavings

## Main ##################################################################################################################
async def main() -> None:
    await syncTime()
    asyncio.create_task(autoCalibrate())
        
    #uping.ping('10.128.10.30')
    while(True):
        hour, minute, sec = time.localtime()[3:6]
        
        if daylightSavings: 
            hour -= 4
        else:
            hour -= 5
        
        
        if hour > 12: hour -= 12 # PM
        elif hour == 0: hour = 12 # incase midnight is treated as 0
        
        
        
        if DEBUG: print(f"{hour}:{minute}")        
        
        flush = [False, False]
        if minute == 9 and sec > 45: flush = [True,True]    # Flush tens and ones places
        elif sec > 45: flush[1] = True                      # Flush ones place
        
        
        try:
            acks = i2c.writeto(tentacle,i2cMessage(minute,flush))
            if DEBUG: print(f"Sent: {minute}\nReceived: {acks}") 
        except: # so the controller doesn't crash
            if DEBUG: print("i2c failed")
            
        
        output.writeOutput(hour,minute,sec)
        
        if leaking():
            dontLeak()
        
        sleep(1)


## Reboot if no internet
try:
    if DEBUG: print("Connecting")
    connect()
except KeyboardInterrupt:
    pass # This 
    #machine.reset()    


asyncio.run(main())