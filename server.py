#!/usr/bin/env python
from gpiozero import LED

import asyncio
import socket
import websockets

ip = socket.gethostbyname(socket.gethostname() + ".local")

from adafruit_servokit import ServoKit
kit = ServoKit(channels=16)

white = LED(4) # Script Booted
yellow = LED(18) # TODO error indicator
green = LED(23) # Socket Connected
blue = LED(5) # Playback/Record indicator
red = LED(13) # Movement Active

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

async def loop(websocket, path):
    print("Connection established!")
    asyncio.ensure_future(blink(green, 3, 0.2, 0.2, True))
    try:
        async for rawdata in websocket:
            if (are_we_loggin_it):
                print("DATA: " + rawdata)
            if (are_we_live)
                data = rawdata.split(',')
                for i in range(0, 6):
                    kit.servo[i].angle = int(data[i])
                handlemoving(data[6] == "True")
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

start_server = websockets.serve(loop, ip, 8765)

white.on()

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
