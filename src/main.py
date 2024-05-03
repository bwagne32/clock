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
    
lastTens = -1
lastOnes = -1
lastMinute = -1
async def i2cOutput(minute, sec):
    global lastMinute
    global lastTens
    global lastOnes
    
    if DEBUG: print("Background i2c task")        
    from lookup import actualTable

    flush = [False, False]
    
    if minute % 10 == 9 and sec > 60-15: 
        flush = [True,True]                                                             # Flush tens and ones places
        try:
            acks = i2c.writeto(tentacle, bytearray([128,128]))
        except:
            pass
    elif sec > 60 - 15: 
        flush[1] = True                                                                 # Flush ones place
        try:
            acks = i2c.writeto(tentacle, bytearray([0,128]))
        except:
            pass
        
    
    elif lastMinute != minute:
        tempOnes = 0
        tempTens = 0
        if lastTens != int(minute / 10):
            tempTens = actualTable[int(minute / 10)]
            lastTens = int(minute / 10)
        if lastOnes != minute % 10:
            tempOnes = actualTable[minute % 10]
            lastOnes = minute % 10
            
        i2cConvert = bytearray([tempTens, tempOnes])

        try:
            acks = i2c.writeto(tentacle, i2cConvert)
        except:
            pass
        
        sleep(.75 * (fillTimer[int(minute/10)] + fillTimer[int(minute%10)]))

        try:
            acks = i2c.writeto(tentacle, bytearray([0,0]))
        except:
            pass
        
        '''
        if minute % 10 == 0:
            tempOnes = actualTable[minute % 10]
            tempTens = actualTable[int(minute / 10)]
            i2cConvert = bytearray([tempTens, tempOnes])
            
            try:
                acks = i2c.writeto(tentacle, i2cConvert)
            except:
                pass
            
            sleep((fillTimer[int(minute/10)] + fillTimer[int(minute%10)]) / 2)

            try:
                acks = i2c.writeto(tentacle, bytearray([0,0]))
            except:
                pass
        else:
            tempOnes = actualTable[minute % 10]
            tempTens = 0
            i2cConvert = bytearray([tempTens, tempOnes])
            
            try:
                acks = i2c.writeto(tentacle, i2cConvert)
            except:
                pass
            
            
            sleep((fillTimer[int(minute/10)] + fillTimer[int(minute%10)]) / 2)

            try:
                acks = i2c.writeto(tentacle, bytearray([0,0]))
            except:
                pass
    
        
        
        lastMinute = minute
    
    return
'''

    
    '''
    try:
        if not flush[0]:
            i2cConvert = bytearray([actualTable[command],actualTable[command]])
        elif:
            acks = i2c.writeto(tentacle, i2cConvert)

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
        '''




## Main ##################################################################################################################
async def main() -> None:
    await syncTime()
    asyncio.create_task(autoCalibrate())
    while(True):
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
        
        
        
        if DEBUG: print(f"{hour}:{minute}")        
        
        await i2cOutput(minute, sec)
            
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

#if DEBUG: uping.ping(host='10.128.10.30',count=3) # Test if NTP server is reachable
if DEBUG: sleep(1)
asyncio.run(main())