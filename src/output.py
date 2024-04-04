#Subject to change depending on 12 hr/24 hr time

from machine import pin

pin = {
    4,
    5,
    6,
    7,
    #8, GND
    9,
    10,
    11,
    12,
    #13, GND
    14,
    15,
    16,
    17,
    
    
}

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


def writeOutput(hour: int): # In testing while I figure out how picos work
    p0 = pin(0,pin.OUT) 
    p0.value(1)
    
    