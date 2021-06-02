#!/usr/bin/env python
from gpiozero import LED

import asyncio
import socket
import websockets
import time

from adafruit_servokit import ServoKit
kit = ServoKit(channels=16)

white = LED(4) # Script Booted
yellow = LED(27) # error indicator
green = LED(23) # Socket Connected
blue = LED(5) # Playback/Record indicator
red = LED(13) # Movement Active

def resetleds():
    white.off()
    yellow.off()
    green.off()
    blue.off()
    red.off()
resetleds()

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
ip = s.getsockname()[0]
s.close()

are_we_loggin_it = True
are_we_live = True

async def blink(led, times, ontime, offtime, keepon):
    for t in range(1, times):
        led.on()
        await asyncio.sleep(ontime)
        led.off()
        await asyncio.sleep(offtime)
    if keepon:
        led.on()

def syncblink(led, times, ontime, offtime, keepon):
    for t in range(1, times):
        led.on()
        time.sleep(ontime)
        led.off()
        time.sleep(offtime)
    if keepon:
        led.on()

def move(final):
    for i in range(0, 6):
        position[i] = final[i]
        kit.servo[i].angle = final[i]

def slowmove(final):
    if (isinstance(position[0], int) == False):
        map(lambda x: int(x), position)
    count = 0
    while (count < 6):
        count = 0
        for i in range(0, 6):
            if (position[i] < final[i]):
                position[i] += 1
                kit.servo[i].angle = position[i]
            elif (position[i] > final[i]):
                position[i] -= 1
                kit.servo[i].angle = position[i]
            else:
                count += 1
        time.sleep(0.1)

moving = False
def handlemoving(b):
    global moving
    if (b != moving):
        moving = b
        if (b):
            red.on()
        else:
            red.off()

error = False
def handleerror(b):
    global error
    if (b != error):
        error = b
        if (b):
            yellow.on()
        else:
            yellow.off()

def handlequit():
    syncblink(white, 5, 0.2, 0.2, True)
    slowmove(restdatahalf)
    slowmove(restdatafinal)
    syncblink(white, 3, 0.2, 0.2, True)
    resetleds()

position = [90, 90, 140, 90, 180, 90]
readydata = [90, 90, 90, 90, 90, 90]
restdatahalf = [90, 90, 90, 90, 180, 90]
restdatafinal = [90, 90, 140, 90, 180, 90]

lasttime = 0
blueon = False

async def idletimeout():
    while True:
        await asyncio.sleep(1)
        key = current_recording_key
        global blueon
        blueon = not blueon
        if (time.time() - lasttime > 6):
            handlequit()
            white.on()
            break
        elif (key == 1):
            if (blueon):
                blue.on()
            else:
                blue.off()
        elif (key == 3):
            if (blueon):
                asyncio.ensure_future(blink(blue, 1, 0.1, 0.1, True))

current_recording_key = 0
blue_blink_count = 20
async def handlerecording(key):
    if (key == 1):
        blue_blink_count = blue_blink_count - 1
        if (blue_blink_count == 0):
            blue_blink_count = 20
            asyncio.ensure_future(blink(blue, 1, 0.1, 0.1, False))
    if (current_recording_key != key):
        current_recording_key = key
        if (key == 0):
            blue.off()
        elif (key == 2):
            blue.on()

async def loop(websocket, path):
    global lasttime
    lasttime = time.time()
    print("Connection established!")
    asyncio.ensure_future(blink(green, 3, 0.2, 0.2, True))
    asyncio.ensure_future(idletimeout())
    white.on()
    try:
        async for rawdata in websocket:
            lasttime = time.time()
            if (are_we_loggin_it):
                print("DATA: " + rawdata)
            if (are_we_live):
                data = rawdata.split(',')
                position = data[:6]
                for i in range(0, 6):
                    kit.servo[i].angle = int(data[i])
                handlemoving(data[6] == "True")
                handleerror(data[7] == "True")
                handlerecording(int(data[8]))
                if (data[9] == "True"):
                    handlequit()
                    
    except Exception as e:
        print("Connection Closed or some other error!")
        print(type(e))
        print(e)
        green.off()

slowmove(restdatahalf)
move(readydata)

start_server = websockets.serve(loop, ip, 8765)

white.on()

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
