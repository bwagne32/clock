#Subject to change depending on 12 hr/24 hr time

from machine import Pin
from lookup import DEBUG, tensPins, onesPins, segment, tensTable, onesTable, fillTimer, drainTimer
from time import sleep
lastHour = 0

tens = segment(seg4=tensPins[0],flush=tensPins[1])
ones = segment(seg1=onesPins[0],seg2=onesPins[1],seg3=onesPins[2],seg4=onesPins[3],seg5=onesPins[4],seg6=onesPins[5],seg7=onesPins[6],flush=onesPins[7])


def writeOutput(hour: int, minute: int,sec:int) -> None: # In testing while segment control is finalized
    global lastHour
    
    if(minute == 59) and (sec > 60 - drainTimer[hour % 10]) and ((hour == 9) or (hour == 12)):      # Flush both hour digits
        if DEBUG: print("Flushing both segments")
        tens.flush()
        ones.flush()
    elif(minute == 59) and (sec > 60 - drainTimer[hour % 10]):                                      # Flush ones digit
        if DEBUG: print("Flushing ones segment")
        ones.flush()
    elif(lastHour != hour):                                                                         # Filling condition
        if DEBUG: print("Outputting to solenoids")
        ones.out(onesTable[hour % 10])
        tens.out(tensTable[int(hour / 10)])
        lastHour = hour
        
        if fillTimer[int(hour/10)] > fillTimer[hour % 10]: sleep(fillTimer[int(hour/10)])           # Choosing the longer timer for fill
        else: sleep(fillTimer[hour % 10])                                                           # Needs to be done simultaneously 
        
        ones.close()
        tens.close()

            
            
            
def leaking()->bool:
    return False

def dontLeak()->None:
    ...