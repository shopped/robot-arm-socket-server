#!/usr/bin/env python
from gpiozero import LED

import asyncio
import socket
import websockets
from time import sleep

from adafruit_servokit import ServoKit
kit = ServoKit(channels=16)

white = LED(4) # Script Booted
yellow = LED(18) # TODO error indicator
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

ip = socket.gethostbyname(socket.gethostname() + ".local")

are_we_loggin_it = True
are_we_live = False

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
        sleep(ontime)
        led.off()
        sleep(offtime)
    if keepon:
        led.on()

def slovemove(final):
    if (isinstance(position[0], int) == False):
        map(lambda x: int(x), position)
    count = 0
    while (count < 6):
        count = 0
        for i in range(0, 6):
            if (position[i] < final[i]):
                position[i] += 1
                kit.servo[i].angle = position[i]
            else if (position[i] > final[i]):
                position[i] -= 1
                kit.servo[i].angle = position[i]
            else:
                count += 1
        sleep(0.1)

async def handlequit():
    syncblink(white, 5, 0.2, 0.2, True)
    slovemove(restdatahalf)
    slovemove(restdatafinal)
    syncblink(white, 3, 0.2, 0.2, True)
    resetleds()

position = [90, 90, 140, 90, 180, 90]
readydata = [90, 90, 90, 90, 90, 90]
restdatahalf = [90, 90, 90, 90, 180, 90]
restdatafinal = [90, 90, 140, 90, 180, 90]

async def loop(websocket, path):
    print("Connection established!")
    asyncio.ensure_future(blink(green, 3, 0.2, 0.2, True))
    white.on()
    try:
        async for rawdata in websocket:
            if (are_we_loggin_it):
                print("DATA: " + rawdata)
            if (are_we_live)
                data = rawdata.split(',')
                position = data[:6]
                for i in range(0, 6):
                    kit.servo[i].angle = int(data[i])
                handlemoving(data[6] == "True")
                handleerror(data[7] == "True")
                if (data[8] == "True"):
                    handlequit()
    except:
        print("Connection Closed or some other error!")
        green.off()

moving = False
def handlemoving(b):
    if (b != moving):
        moving = b
        if (b):
            red.on()
        else:
            red.off()

error = false
def handlerror(b):
    if (b != error):
        error = b
        if (b):
            yellow.on()
        else:
            yellow.off()

slovemove(restdatahalf)
slovemove(readydata)

start_server = websockets.serve(loop, ip, 8765)

white.on()

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
