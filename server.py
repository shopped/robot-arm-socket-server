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

async def loop(websocket, path):
    print("Connection established!")
    asyncio.run(blink(green, 3, 0.3, 0.3, true))
    async for rawdata in websocket:
        data = rawdata.split(',')
        for i in range(0, 6):
            kit.servo[i].angle = int(data[i])
        handlemoving(data[6] == "True")

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

async def blink(led, times, ontime, offtime, keepon):
    for t in times:
        led.on()
        await asyncio.sleep(ontime)
        led.off()
        await asyncio.sleep(offtime)
    if keepon:
        led.on()
