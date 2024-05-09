
from machine import Pin

DEBUG = True

### Output.py ###########################################################################

tensPins = [3,2]                    # segment 1 in segment control order
onesPins = [11,10,9,8,4,5,6,7]      # segment 2 in segment control order

class segment:
    def __init__(self,seg1="LED",seg2="LED",seg3="LED",seg4="LED",seg5="LED",seg6="LED",seg7="LED",flush="LED", name="name"):
        self._name_ = name
        self.S1 = Pin(seg1,Pin.OUT)
        self.S2 = Pin(seg2,Pin.OUT)
        self.S3 = Pin(seg3,Pin.OUT)
        self.S4 = Pin(seg4,Pin.OUT)
        self.S5 = Pin(seg5,Pin.OUT)
        self.S6 = Pin(seg6,Pin.OUT)
        self.S7 = Pin(seg7,Pin.OUT)
        self.S8 = Pin(flush,Pin.OUT) # Flush
        if DEBUG: print([self._name_,self.S1, self.S2,self.S3,self.S4,self.S5,self.S6,self.S7,self.S8])
        
    def out(self,array:list):       # For filling segments only
        self.S1.value(array[0])
        self.S2.value(array[1])
        self.S3.value(array[2])
        self.S4.value(array[3])
        self.S5.value(array[4])
        self.S6.value(array[5])
        self.S7.value(array[6])
        self.S8.off()               # Should not be flushing
        if DEBUG: print(f"Wrote: {array} to {self._name_}")
    
    def flushAndFill(self,array:list):
        self.S1.value(array[0])
        self.S2.value(array[1])
        self.S3.value(array[2])
        self.S4.value(array[3])
        self.S5.value(array[4])
        self.S6.value(array[5])
        self.S7.value(array[6])
        self.S8.on()               
        if DEBUG: print(f"Wrote: {array} and flush to {self._name_}")
     
    def flush(self):                # Closes all fills and opens flush
        self.S1.off()
        self.S2.off()
        self.S3.off()
        self.S4.off()
        self.S5.off()
        self.S6.off()
        self.S7.off()
        self.S8.on()
        if DEBUG: print(f"Flushed {self._name_}")
    
    def close(self):                # Closes all segments
        self.S1.off()
        self.S2.off()
        self.S3.off()
        self.S4.off()
        self.S5.off()
        self.S6.off()
        self.S7.off()
        self.S8.off()
        if DEBUG: print(f"Closed {self._name_}")


'''
    --1--
   |     |    
   6     2   
   |     |     
    --7--
   |     |    
   5     3   
   |     |     
    --4--

// On the solenoid driver board...
// S1 pin 3 #
// S2 pin 5 #
// S3 pin 7 #
// S4 pin 9 #
// S5 pin 4 #
// S6 pin 6 #
// S7 pin 8 #
// S8 pin 10 Flush
'''

tensTable = {#  S1,S2,S3,S4,S5,S6,S7,S8
             0:[ 0, 0, 0, 0, 0, 0, 0, 1],
             1:[ 1, 1, 1, 1, 1, 1, 1, 0]
             }

onesTable = {           # idk which solenoids to activate yet
    1:[
       0,1,1,0,0,0,0,0
       ],
    2:[
       1,1,0,1,1,0,1,0
       ],
    3:[
       1,1,1,1,0,0,1,0
       ], 
    4:[
       0,1,1,0,0,1,1,0
       ],
    5:[
       1,0,1,1,0,1,1,0
       ],
    6:[
       1,0,1,1,1,1,1,0
       ],
    7:[
       1,1,1,0,0,0,0,0
       ],
    8:[
       1,1,1,1,1,1,1,0
       ],
    9:[
       1,1,1,0,0,1,1,0
       ],
    0:[
        1,1,1,1,1,1,0,0
        ]
}

### i2c #################################################################################
'''    struct
    {
        bool MinTen_Seg1 : 1; 1 // bit 0
        bool MinTen_Seg2 : 1; 2
        bool MinTen_Seg3 : 1; 4
        bool MinTen_Seg4 : 1; 8
        bool MinTen_Seg5 : 1; 16
        bool MinTen_Seg6 : 1; 32
        bool MinTen_Seg7 : 1; 64
        bool MinTen_Dump : 1; 128
        bool MinOne_Seg1 : 1;
        bool MinOne_Seg2 : 1;
        bool MinOne_Seg3 : 1;
        bool MinOne_Seg4 : 1;
        bool MinOne_Seg5 : 1;
        bool MinOne_Seg6 : 1;
        bool MinOne_Seg7 : 1;
        bool MinOne_Dump : 1; // bit 15
    };
    
    --1--
   |     |    
   6     2   
   |     |     
    --7--
   |     |    
   5     3   
   |     |     
    --4--

'''
    
tentacleTable = { # This could have the efficiency improved, but it'll be easier to debug in this form
    #:[1,2,3,4,5,6,7]
    0:[1,1,1,1,1,1,0],
    1:[0,1,1,0,0,0,0],
    2:[1,1,0,1,1,0,1],
    3:[1,1,1,1,0,0,1],
    4:[0,1,1,0,0,1,1],
    5:[1,0,1,1,0,1,1],
    6:[1,0,1,1,1,1,1],
    7:[1,1,1,0,0,0,0],
    8:[1,1,1,1,1,1,1],
    9:[1,1,1,0,0,1,1]
}


actualTable = {
    0:63,
    1:6,
    2:91,
    3:79,
    4:102,
    5:109,
    6:125,
    7:7,
    8:127,
    9:103
}

def i2cMessage(minute: int,flush:list)->bytearray: # flush[0] flushes both digits. flush[1] flushes ones digit
    array = [0,0]
    tens = int(minute / 10)
    ones = minute % 10
    
    if(flush[0]): # flush all
        array = [128,128]
    elif(flush[1]): # flush ones
        array[1] = 128 
        for i in tentacleTable[tens]: 
            array[0] = (array[0] << 1) | i
    else:
        for i in tentacleTable[tens]: 
            array[0] = (array[0] << 1) | i
            
        for i in tentacleTable[ones]: 
            array[1] = (array[1] << 1) | i
    
    return bytearray(array)



### fill/drain timer lookups #################################################################################

fillTimer = {
    0:3.5,
    1:3,
    2:3,
    3:3.25,
    4:2.75,
    5:3.75,
    6:3.75,
    7:2.75,
    8:3.5,
    9:3.5,
}

drainTimer = 30     # Mostly for minutes. Hours drain time is increased at use

'''
drainTimer = { # old drain timer style
    0:15,
    1:15,
    2:15,
    3:15,
    4:15,
    5:15,
    6:15,
    7:15,
    8:15,
    9:15,
}
'''