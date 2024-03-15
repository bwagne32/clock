## Ben Wagner
# 3/15/2024
## Written for Raspberry Pi
## Communicates with arduinos to display time on 7 segment displays

import smbus
import time
import math
import requests

# Define the I2C bus number (0 for older Pi models, 1 for newer ones)
I2C_BUS = 1

# Arduino interface addresses
arduinoAddress = [0x08, 0x09, 0x0A, 0x0B]

# Initialize the I2C bus
bus = smbus.SMBus(I2C_BUS)

def sendTimes(currentTime):
    msg = [arduinoAddress, currentTime]
    for i in range(len(arduinoAddress)):
        try:
            # Send the integer to the Arduino
            bus.write_byte(msg[0][i], msg[1][i])
            print(f"Integer sent to {msg[0][i]}: {msg[1][i]}") # debugging
        except IOError:
            print("Error communicating with Arduino") # debugging

def getTime(): # Returns current time in 12 hour H H M M array
    hour = time.gmtime().tm_hour - 12 - 4 # offset from 24 hour and GMT
    minute = time.gmtime().tm_min
    return [math.floor(hour / 10),
            hour % 10, 
            math.floor(minute / 10), 
            minute % 10]

def connectedToInternet():
    try:
        response = requests.get("http://www.google.com", timeout=5)
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.ConnectionError:
        #print("No internet connection available.")
        return False


if __name__ == "__main__":
    while not connectedToInternet():
        time.sleep(10)
    while True:
        # Example integer value to send
        sendTimes(getTime())
        time.sleep(10)  # seconds