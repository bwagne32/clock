#Subject to change depending on 12 hr/24 hr time

from machine import Pin
from main import DEBUG
from lookup import flushPins, setupPins, controlPins, outputTable

lastHour = 0


def setup():
    for i in range(0,setupPins):
        controlPins.append(Pin(i,Pin.OUT))

def flush() -> None:
    for i in range(0,len(controlPins)):
            controlPins[i].value(flushPins[i])


def writeOutput(hour: int, minute: int) -> None: # In testing while segment control is finalized
    if DEBUG: print(f"Received: {hour}")
    if(minute == 59):
        flush()
    elif(lastHour != hour):
        for i in range(0,len(controlPins)):
            controlPins[i].value(outputTable[hour][i])
        lastHour = hour
            
    
    
    