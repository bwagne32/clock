#Subject to change depending on 12 hr/24 hr time

from machine import Pin
from lookup import DEBUG, tensPins, onesPins, segment, tensTable, onesTable, fillTimer, drainTimer
from time import sleep
lastHour = 0

tens = segment(seg2=tensPins[0],flush=tensPins[1])
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
    
    
    if(lastHour != hour):                                                                         # Filling condition
        if DEBUG: print("Outputting to solenoids")
        if hour > 9:
            tempOnes = onesTable[hour % 10]
            ones.out(tempOnes)
            tempTens = tensTable[int(hour / 10)]
            tens.out(tempTens)
            
            sleep(3)                                                          # Needs to be done simultaneously 
            ones.close()
            sleep(12)
            tens.close()
        else: 
            tempOnes = onesTable[hour % 10]
            ones.out(tempOnes)
            sleep(3.25)
        ones.close()
        tens.close()
        lastHour = hour

            
            
            
def leaking()->bool:
    return False

def dontLeak()->None:
    ...