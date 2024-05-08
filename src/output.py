#Subject to change depending on 12 hr/24 hr time

from machine import Pin
from lookup import DEBUG, tensPins, onesPins, segment, tensTable, onesTable, fillTimer, drainTimer
from time import sleep
import uasyncio as asynio

tens = segment(seg2=tensPins[0],flush=tensPins[1], name="tens")
ones = segment(seg1=onesPins[0],seg2=onesPins[1],seg3=onesPins[2],seg4=onesPins[3],seg5=onesPins[4],seg6=onesPins[5],seg7=onesPins[6],flush=onesPins[7],name="ones")



'''
Flush states
0 -> flush only
1 -> flush & write
2 -> write only
3 -> close all
'''
async def writeHours(hour:int, flush:int) -> bool: # In testing while segment control is finalized
    
    match flush:
        case 0: # Flush only
            ones.flush()
            tens.flush()
            return True
        
        case 1: # Flush & Fill
            tempOnes = onesTable[hour % 10]
            ones.flushAndFill(tempOnes)
            if hour > 9:
                tempTens = tensTable[int(hour / 10)]
                tens.flushAndFill(tempTens)
            else: tens.flush()
            return True
        
        case 2: # Write only
            tempOnes = onesTable[hour % 10]
            ones.out(tempOnes)
            if hour > 9:
                tempTens = tensTable[int(hour / 10)]
                tens.out(tempTens)
            else: tens.flush()
            return True
        
        case 3: # Close all
            ones.close()
            tens.close()
    
    return False
        
    
    '''
    
    
    if(minute == 59) and (sec > 60 - drainTimer) and ((hour == 9) or (hour == 12)):      # Flush both hour digits
        if DEBUG: print("Flushing both segments")
        tens.flush()
        ones.flush()
    elif(minute == 59) and (sec > 60 - drainTimer):                                      # Flush ones digit
        if DEBUG: print("Flushing ones segment")
        ones.flush()
        tens.close()
    
    
    if(lastHour != hour):                                                                         # Filling condition
        if DEBUG: print("Outputting to solenoids")
        if hour > 9:
            tempOnes = onesTable[hour % 10]
            ones.out(tempOnes)
            tempTens = tensTable[int(hour / 10)]
            tens.out(tempTens)
            
            sleep(fillTimer[hour % 10] + 3)                                                          # Needs to be done simultaneously 
            ones.close()
            sleep(7)
            tens.close()
        else: 
            tempOnes = onesTable[hour % 10]
            ones.out(tempOnes)
            sleep(fillTimer[hour % 10] + 2)
            tens.close()
        ones.close()
        tens.close()
        lastHour = hour
        tens.close()
        tens.out([0,0,0,0,0,0,0,0])
            
            '''
            
def leaking()->bool:
    return False

def dontLeak()->None:
    ...