from time import sleep
import time
import machine
import uasyncio as asyncio
import output
from lookup import i2cMessage, DEBUG, convertInput


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
'''
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
'''
## Main ##################################################################################################################
async def main() -> None:
    from output import ones, tens
    from lookup import onesTable, tensTable
    #await syncTime()
    #asyncio.create_task(autoCalibrate())
    acks = 0
    #uping.ping('10.128.10.30')
    while(True):
        
        command = input("What output: ")
        command = convertInput[command]
        
        if command == 'close':
            try: acks = i2c.writeto(tentacle,bytearray([0,0]))
            except: pass
            ones.close()
            tens.close()
            print("Closed")
        elif command == 'flush':
            try: acks = i2c.writeto(tentacle,bytearray([128,128]))
            except: pass
            ones.flush()
            tens.flush()
            print("Flushed")
        else:
            acks = i2c.writeto(tentacle,i2cMessage(command,[0,0]))
            ones.out(onesTable[command])
            if command in tensTable:
                tens.out(tensTable[command])
            else:
                tens.close()
            print(f"Wrote: {command}")
            
            
        print(f'Acks: {acks}')
            

        
            
        
        #output.writeOutput(hour,minute,sec)
        
        sleep(.5)


'''
## Reboot if no internet
try:
    if DEBUG: print("Connecting")
    connect()
except KeyboardInterrupt:
    pass # This 
    #machine.reset()    
'''

asyncio.run(main())