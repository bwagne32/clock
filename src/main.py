import network
import credentials
from time import sleep
import time
import ntp
import machine
import uasyncio as asyncio
import output
from output import leaking, dontLeak, fillTimer, drainTimer
from lookup import i2cMessage, DEBUG
import uping



daylightSavings = False


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



## i2c #################################################################
I2C_ENABLE = True
sdaPIN=machine.Pin(0)
sclPIN=machine.Pin(1)


tentacle = 0x30                                         # Pico GPIO expender
i2c=machine.I2C(0,sda=sdaPIN, scl=sclPIN, freq=100_000)
devices = i2c.scan() # debugging
if DEBUG: print(f"NUmber of i2c devices found: {devices}")
while(I2C_ENABLE and len(devices) < 1):
    if DEBUG: print("Still searching for devices")
    sleep(1)
    
    
async def i2cOutput(minute, sec):
    if DEBUG: print("Background i2c task")        

    flush = [False, False]
    
    if minute == 9 and sec > (60 - (drainTimer[int(minute/10)] + drainTimer[int(minute%10)]) / 2): 
        flush = [True,True]                                                             # Flush tens and ones places
    elif sec > 60 - drainTimer[minute%10]: 
        flush[1] = True                                                                 # Flush ones place
    
    try:
        acks = i2c.writeto(tentacle,i2cMessage(minute,flush))
        if DEBUG: print(f"Sent: {minute}\nReceived: {acks}") 
    except:                                                                             # so the controller doesn't crash
        if DEBUG: print("i2c failed")

    if not flush[1]:                                                                    # leave open for fill timer if not in flushing phase
        asyncio.sleep((fillTimer[int(minute/10)] + fillTimer[int(minute%10)]) / 2)
        try:
            acks = i2c.writeto(tentacle,bytearray([0,0]))                               # closing all solenoids
            if DEBUG: print(f"Sent close command. Acks: ") 
        except:                                                                         # so the controller doesn't crash
            if DEBUG: print("i2c failed")
        




## Main ##################################################################################################################
async def main() -> None:
    await syncTime()
    asyncio.create_task(autoCalibrate())
        
    while(True):
        hour, minute, sec = time.localtime()[3:6]
        
        if daylightSavings: 
            hour -= 5
        else:
            hour -= 4
        
        if hour > 12: hour -= 12 # PM
        elif hour == 0: hour = 12 # incase midnight is treated as 0
        
        
        
        if DEBUG: print(f"{hour}:{minute}")        
        
        asyncio.create_task(i2cOutput(minute, sec))
            
        output.writeOutput(hour,minute,sec)
        
        
        
        if leaking():   # Water proofing
            dontLeak()
            
        sleep(1)











## Reboot if no internet
try:
    if DEBUG: print("Connecting")
    connect()
except KeyboardInterrupt:
    pass # This was annoying me so now it's gone
    #machine.reset()    

if DEBUG: uping.ping('10.128.10.30') # Test if NTP server is reachable
asyncio.run(main())