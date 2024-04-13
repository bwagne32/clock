
### Output.py ###########################################################################

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
    
slaveTable ={
    #:[1,2,3,4,5,6,7]
    0:[1,1,1,1,1,1,0],
    1:[0,1,1,0,0,0,0],
    2:[1,1,0,1,1,0,1],
    3:[1,1,1,1,0,0,1],
    4:[0,1,1,1,0,0,1],
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