
from machine import Pin

DEBUG = True

### Output.py ###########################################################################

tensPins = [3,2]                    # segment 1 in segment control order
onesPins = [11,10,9,8,4,5,6,7]      # segment 2 in segment control order

class segment:
    def __init__(self,seg1="LED",seg2="LED",seg3="LED",seg4="LED",seg5="LED",seg6="LED",seg7="LED",flush="LED"):
        self.S1 = Pin(seg1,Pin.OUT)
        self.S2 = Pin(seg2,Pin.OUT)
        self.S3 = Pin(seg3,Pin.OUT)
        self.S4 = Pin(seg4,Pin.OUT)
        self.S5 = Pin(seg5,Pin.OUT)
        self.S6 = Pin(seg6,Pin.OUT)
        self.S7 = Pin(seg7,Pin.OUT)
        self.S8 = Pin(flush,Pin.OUT) # Flush
        if DEBUG: print([self.S1, self.S2,self.S3,self.S4,self.S5,self.S6,self.S7,self.S8])
        
    def out(self,array:list):       # For filling segments only
        self.S1.value(array[0])
        self.S2.value(array[1])
        self.S3.value(array[2])
        self.S4.value(array[3])
        self.S5.value(array[4])
        self.S6.value(array[5])
        self.S7.value(array[6])
        self.S8.off()               # Should not be flushing
        if DEBUG: print(f"Wrote: {array}")
        
    def flush(self):                # Flushes all segments
        self.S1.off()
        self.S2.off()
        self.S3.off()
        self.S4.off()
        self.S5.off()
        self.S6.off()
        self.S7.off()
        self.S8.on()
        if DEBUG: print("Wrote: [0,0,0,0,0,0,0,1]")
    
    def one(self):
        #self.S1.on()
        #self.S2.on()
        #self.S3.on()
        self.S4.on()
        self.S5.on()
        #self.S6.on()

        #self.S7.on()
        self.S8.off()
    
    def close(self):
        self.S1.off()
        self.S2.off()
        self.S3.off()
        self.S4.off()
        self.S5.off()
        self.S6.off()
        self.S7.off()
        self.S8.off()
        if DEBUG: print("Wrote: [0,0,0,0,0,0,0,0]")

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
             1:[ 0, 1, 0, 0, 0, 0, 0, 0]
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

def i2cMessage(minute: int,flush:list)->bytearray: # flush[0] flushes both segments. flush[1] flushes minutes
    array = [0,0]
    tens = int(minute / 10)
    ones = minute % 10
    
    tensTemp = tentacleTable
    
    
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
from machine import Pin

DEBUG = True

### Output.py ###########################################################################

tensPins = [3,2]                    # segment 1 in segment control order
onesPins = [11,10,9,8,4,5,6,7]      # segment 2 in segment control order

class segment:
    def __init__(self,seg1="LED",seg2="LED",seg3="LED",seg4="LED",seg5="LED",seg6="LED",seg7="LED",flush="LED"):
        self.S1 = Pin(seg1,Pin.OUT)
        self.S2 = Pin(seg2,Pin.OUT)
        self.S3 = Pin(seg3,Pin.OUT)
        self.S4 = Pin(seg4,Pin.OUT)
        self.S5 = Pin(seg5,Pin.OUT)
        self.S6 = Pin(seg6,Pin.OUT)
        self.S7 = Pin(seg7,Pin.OUT)
        self.S8 = Pin(flush,Pin.OUT) # Flush
        if DEBUG: print([self.S1, self.S2,self.S3,self.S4,self.S5,self.S6,self.S7,self.S8])
        
    def out(self,array:list):       # For filling segments only
        self.S1.value(array[0])
        self.S2.value(array[1])
        self.S3.value(array[2])
        self.S4.value(array[3])
        self.S5.value(array[4])
        self.S6.value(array[5])
        self.S7.value(array[6])
        self.S8.off()               # Should not be flushing
        if DEBUG: print(f"Wrote: {array}")
        
    def flush(self):                # Flushes all segments
        self.S1.off()
        self.S2.off()
        self.S3.off()
        self.S4.off()
        self.S5.off()
        self.S6.off()
        self.S7.off()
        self.S8.on()
        if DEBUG: print("Wrote: [0,0,0,0,0,0,0,1]")
    
    def one(self):
        #self.S1.on()
        #self.S2.on()
        #self.S3.on()
        self.S4.on()
        self.S5.on()
        #self.S6.on()

        #self.S7.on()
        self.S8.off()
    
    def close(self):
        self.S1.off()
        self.S2.off()
        self.S3.off()
        self.S4.off()
        self.S5.off()
        self.S6.off()
        self.S7.off()
        self.S8.off()
        if DEBUG: print("Wrote: [0,0,0,0,0,0,0,0]")

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
             1:[ 0, 1, 0, 0, 0, 0, 0, 0]
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
    #:[1,2,3,4,5, 6, 7]
    # 1 2 4 8 16 32 64
    0:[1,1,1,1,1,1,0],      # 63
    1:[0,1,1,0,0,0,0],      # 6
    2:[1,1,0,1,1,0,1],      # 91
    3:[1,1,1,1,0,0,1],      # 79
    4:[0,1,1,0,0,1,1],      # 102
    5:[1,0,1,1,0,1,1],      # 109
    6:[1,0,1,1,1,1,1],      # 125
    7:[1,1,1,0,0,0,0],      # 7
    8:[1,1,1,1,1,1,1],      # 127
    9:[1,1,1,0,0,1,1]       # 103
}                           # Flush 128

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

def i2cMessage(minute: int,flush:list)->bytearray: # flush[0] flushes both segments. flush[1] flushes minutes
    array = [0,0]
    tens = int(minute / 10)
    ones = minute % 10
    
    tensTemp = tentacleTable[tens]
    tensTemp = tensTemp[::-1]
    onesTemp = tentacleTable[ones]
    onesTemp = onesTemp[::-1]
    
    
    
    
    if(flush[0]): # flush all
        array = [128,128]
    elif(flush[1]): # flush ones
        array[1] = 128 
        for i in tensTemp: 
            array[0] = (array[0] << 1) | i
    else:
        for i in tensTemp: 
            array[0] = (array[0] << 1) | i
            
        for i in onesTemp: 
            array[1] = (array[1] << 1) | i
    
    return bytearray(array)


convertInput = {
    'one':1,
    'two':2,
    'three':3,
    'four':4,
    'five':5,
    'six':6,
    'seven':7,
    'eight':8,
    'nine':9,
    'zero':0,
    'flush':'flush',
    'close':'close'
}
            
