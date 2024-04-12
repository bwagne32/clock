#Subject to change depending on 12 hr/24 hr time

from machine import Pin
from main import DEBUG

lastHour = 0

flushPins = [] # Pin outputs for flushing every hour

setupPins = [] # Pin numbers used

controlPins = [] # holds pin objects

outputTable = { # idk which solenoids to activate yet
    1:[],
    2:[],
    3:[],
    4:[],
    5:[],
    6:[],
    7:[],
    8:[],
    9:[],
    10:[],
    11:[],
    12:[],
}

def setup():
    for i in range(0,len(setupPins)):
        controlPins[i] = Pin(0,Pin.OUT)

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
            
    
    
    