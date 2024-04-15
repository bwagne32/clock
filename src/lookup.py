
### Output.py ###########################################################################

setupPins = [           # Pin numbers used
    3,2,                # segment 1 in segment control order
    11,10,9,8,4,5,6,7   # segment 2 in segment control order
             ]          

controlPins = [] # holds pin objects

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
flushPins = [             # Pin outputs for flushing every hour
    0,1,
    0,0,0,0,0,0,0,1
    ] 

outputTable = {           # idk which solenoids to activate yet
    1:[0,1, # flushed
       0,1,1,0,0,0,0,0
       ],
    2:[0,1, # flushed
       1,1,0,1,1,0,1,0
       ],
    3:[0,1, # flushed
       1,1,1,1,0,0,1,0
       ], 
    4:[0,1, # flushed
       0,1,1,0,0,1,1,0
       ],
    5:[0,1, # flushed
       1,0,1,1,0,1,1,0
       ],
    6:[0,1, # flushed
       1,0,1,1,1,1,1,0
       ],
    7:[0,1, # flushed
       1,1,1,0,0,0,0,0
       ],
    8:[0,1, # flushed
       1,1,1,1,1,1,1,0
       ],
    9:[0,1, # flushed
       1,1,1,0,0,1,1,0
       ],
    10:[1,0,
        1,1,1,1,1,1,0,0
        ],
    11:[1,0,
        0,1,1,0,0,0,0,0        
        ],
    12:[1,0,
        1,1,0,1,1,0,1,0
        ],
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
    
slaveTable = { # This could have the efficiency improved, but it'll be easier to debug in this form
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
    
    if(flush[0]): # flush all
        array = [128,128]
    elif(flush[1]): # flush ones
        array[1] = 128 
        for i in slaveTable[tens]: 
            array[0] = (array[0] << 1) | i
    else:
        for i in slaveTable[tens]: 
            array[0] = (array[0] << 1) | i
            
        for i in slaveTable[ones]: 
            array[1] = (array[1] << 1) | i
    
    return bytearray(array)