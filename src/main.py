import network
import credentials
from time import sleep
import time
import ntp
import machine
import uasyncio as asyncio
import output
from output import writeHours, leaking, dontLeak, fillTimer, drainTimer
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
        await timeChange(daylightSavings)
        await asyncio.sleep(60*60*24) # sleeps task for a while

async def timeChange(dayLightSavings) -> bool: # True if daylight savings else false
    # EDT -> daylight savings starts last sunday in march (3)
    # EST -> standard starts last sunday in october (10)
    # (year, month, mday, hour, minute, second, weekday, yearday)
    if (time.localtime()[1] == 3) and (time.localtime()[2] < 7) and (time.localtime()[6] == 6):
        return True
    elif (time.localtime()[1] == 10) and (time.localtime()[2] < 7) and (time.localtime()[6] == 6):
        return False
    return dayLightSavings



## i2c #################################################################
I2C_ENABLE = False
sdaPIN=machine.Pin(0)
sclPIN=machine.Pin(1)


tentacle = 0x30                                         # Pico GPIO expender
i2c=machine.I2C(0,sda=sdaPIN, scl=sclPIN, freq=100_000)
devices = i2c.scan() # debugging
if DEBUG: print(f"NUmber of i2c devices found: {devices}")
while(I2C_ENABLE and len(devices) < 1):
    if DEBUG: print("Still searching for devices")
    sleep(1)
    
'''
Flush states
0 -> flush only
1 -> flush & write
2 -> write only
3 -> close all
'''
async def i2cOutput(minute:int, flush:int):    # returns with success boolean
    from lookup import actualTable
    if flush == 0: # Flush only
        try:
            i2c.writeto(tentacle, bytearray([128,128]))
        except:
            pass
    elif flush == 1: # Flush & Fill
        tempTens = actualTable[int(minute / 10)]
        tempOnes = actualTable[minute % 10]
        
        i2cByte = bytearray([tempTens + 128, tempOnes + 128])

        try:
            i2c.writeto(tentacle, i2cByte)
        except:
            pass
    elif flush == 2: # Write only
        tempTens = actualTable[int(minute / 10)]
        tempOnes = actualTable[minute % 10]
        
        i2cByte = bytearray([tempTens, tempOnes])

        try:
            i2c.writeto(tentacle, i2cByte)
        except:
            pass
    elif flush == 3: # Close all
        try:
            i2c.writeto(tentacle, bytearray([0,0]))
        except:
            pass

    
    




## Main ##################################################################################################################
async def main() -> None:
    from output import tens,ones
    tens.flush()
    ones.flush()
    await i2cOutput(0,0)
    await syncTime()
    asyncio.create_task(autoCalibrate())
    await asyncio.sleep(drainTimer*.5)
    
    hour, minute, sec = time.localtime()[3:6]
    
    if daylightSavings:
        if (hour - 5 < 0):
            hour = 24 - (5 - hour)
        else:
            hour -= 5
    else:
        if (hour - 4 < 0):
            hour = 24 - (4 - hour)
        else:
            hour -= 4
    
        
        
    if hour > 12: hour -= 12 # PM
    elif hour == 0: hour = 12 # incase midnight is treated as 0
        
    
    stage = 0
    # Full flush
    await i2cOutput(minute,stage)
    await writeHours(hour,stage)
    await asyncio.sleep(drainTimer)
    stage += 1
    # Flush & Fill
    '''
    await i2cOutput(minute,stage)
    await writeHours(hour,stage)
    await asyncio.sleep(drainTimer * 1 / 2)
    '''
    stage += 1
    # Finish Fill
    await i2cOutput(minute,stage)
    await writeHours(hour,stage)
    await asyncio.sleep(4)                    # needs tested
    stage += 1
    # Close
    await i2cOutput(minute,stage)
    await asyncio.sleep(5) # hours take longer to fill
    await writeHours(hour,stage)
    await asyncio.sleep(10)                   # making sure to pause to not output more than once per iteration


    while(True):
        hour, minute, sec = time.localtime()[3:6]
        
        
        
        ## Hour processing
        if daylightSavings:
            if (hour - 5 < 0):
                hour = 24 - (5 - hour)
            else:
                hour -= 5
        else:
            if (hour - 4 < 0):
                hour = 24 - (4 - hour)
            else:
                hour -= 4
        
        if hour > 12: hour -= 12 # PM
        elif hour == 0: hour = 12 # incase midnight is treated as 0
        
        if DEBUG: print(f"{hour}:{minute}")        
        
        ## Outputting
        '''
        Flush states
        0 -> Flush only
        1 -> flush & write
        2 -> Write only
        3 -> close all
        '''
        ## Hour change + minute change
        if (minute == 59) and (sec > 60 - drainTimer):
            if hour == 12: hour = 1
            else: hour += 1
            if minute == 59: minute = 0
            else: minute = minute + 1
            
            stage = 0
            # Full flush
            await i2cOutput(minute,stage)
            await writeHours(hour,stage)
            await asyncio.sleep(drainTimer)
            stage += 1
            # Flush & Fill
            '''
            await i2cOutput(minute,stage)
            await writeHours(hour,stage)
            await asyncio.sleep(drainTimer * 2/4)
            '''
            stage += 1
            # Finish Fill
            await i2cOutput(minute,stage)
            await writeHours(hour,stage)
            await asyncio.sleep(4)                    # needs tested
            stage += 1
            # Close
            await i2cOutput(minute,stage)
            await asyncio.sleep(5) # hours take longer to fill
            await writeHours(hour,stage)
            await asyncio.sleep(10)                   # making sure to pause to not output more than once per iteration
        
        ## Hours refresh + minutes refresh
        elif ((minute+1) % 15 == 0) and (sec > 60 - drainTimer): 
            if minute == 59: minute = 0
            else: minute = minute + 1
            
            stage = 0
            # Full flush
            await i2cOutput(minute,stage)
            await writeHours(hour,stage)
            await asyncio.sleep(drainTimer)
            stage += 1
            # Flush & Fill
            '''
            await i2cOutput(minute,stage)
            await writeHours(hour,stage)
            await asyncio.sleep(drainTimer * 2/4)
            '''
            stage += 1
            # Finish Fill
            await i2cOutput(minute,stage)
            await writeHours(hour,stage)
            await asyncio.sleep(3)                    # needs tested
            stage += 1
            # Close
            await i2cOutput(minute,stage)
            await asyncio.sleep(5) # hours take longer to fill
            await writeHours(hour,stage)
            await asyncio.sleep(10)                   # making sure to pause to not output more than once per iteration
        
        ## Minutes refreh
        elif (sec > 60 - drainTimer):      
            if minute == 59: minute = 0
            else: minute = minute + 1
                
            stage = 0
            # Full flush
            await i2cOutput(minute,stage)
            await asyncio.sleep(drainTimer)
            stage += 1
            # Flush & Fill
            '''
            await i2cOutput(minute,stage)
            await asyncio.sleep(drainTimer * 2 / 4)
            '''
            stage += 1
            # Finish Fill
            await i2cOutput(minute,stage)
            await asyncio.sleep(3)                    # needs tested
            stage += 1
            # Close
            await i2cOutput(minute,stage)
            await asyncio.sleep(10)                   # making sure to pause to not output more than once per iteration
           
        
        
        
        
        if leaking():   # Water proofing
            dontLeak()
            
        await asyncio.sleep(.5)











## Reboot if no internet
try:
    if DEBUG: print("Connecting")
    connect()
except KeyboardInterrupt:
    pass # This was annoying me so now it's gone
    #machine.reset()    

if DEBUG: uping.ping(host='10.128.10.30',count=3) # Test if NTP server is reachable
if DEBUG: sleep(1)
asyncio.run(main())