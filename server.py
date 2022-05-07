#!/usr/bin/env python
from gpiozero import LED

import asyncio
import socket
import websockets
import time
import board
import neopixel

from adafruit_servokit import ServoKit
kit = ServoKit(channels=16)

pixel_pin = board.D21
num_pixels = 16
ORDER = neopixel.GRB

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, pixel_order=ORDER)

control_pixels = [0, 1, 6, 7, 8, 9, 14, 15]
action_pixels = [2, 10, 3, 11, 4, 12, 5, 13]
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CLEAR = (0,0,0)
CYAN = (0,255,255)
MAGENTA = (255,0,255)
YELLOW (255,255,0)

def set_clear():
    pixels.fill(CLEAR)

def set_free():
    for i in control_pixels:
        pixels[i] = WHITE

def set_attached(right):
    for i in control_pixels:
        if right:
            pixels[i] = RED
        else:
            pixels[i] = GREEN

def set_active():
    for i in action_pixels:
        pixels[i] = WHITE

def set_inactive():
    for i in action_pixels:
        pixels[i] = CLEAR

def set_recording():
    for i in action_pixels:
        pixels[i] = BLUE

def set_playback(quarter): #(0/1/2/3)
    for index, address in action_pixels:
        if (quarter * 2 == index) or (quarter * 2 - 1 == index):
            pixels[address] = BLUE
        else:
            pixels[address] = CLEAR

def set_looping(quarter):
    for index, address in action_pixels:
        if (quarter * 2 == index) or (quarter * 2 - 1 == index):
            pixels[address] = BLUE
        else:
            pixels[address] = WHITE

set_clear()

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
ip = s.getsockname()[0]
s.close()

are_we_loggin_it = True
are_we_live = False


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
def handle_moving(b):
    global moving
    if (b != moving):
        moving = b
        if (b):
            set_active()
        else:
            set_inactive()

def handle_quit():
    pixels.fill(PURPLE)
    slowmove(restdatahalf)
    slowmove(restdatafinal)
    set_clear()

def handle_recording(key): #recording, playback, loop
    global last_quarter
    if (key == -1): # not doing anything
        return
    if (key == -2): # recording
        set_recording()
    elif (key == -3): # stop recording
        set_active()
    elif (key == -4): # stop playback
        set_inactive()
    elif (key == 4): # non looping recoding done playing
        set_inactive()
    elif (key >= 10): # looping
        set_looping(key - 10)
    else: # playing once
        set_playback(key)

position = [90, 90, 140, 90, 180, 90]
readydata = [90, 90, 90, 90, 90, 90]
restdatahalf = [90, 90, 90, 90, 180, 90]
restdatafinal = [90, 90, 140, 90, 180, 90]

async def loop(websocket, path):
    print("Connection established!")
    set_clear()
    set_free()
    try:
        async for rawdata in websocket:
            if (are_we_loggin_it):
                print("DATA: " + rawdata)

            if (are_we_live):
                data = rawdata.split(',')
                position = data[:6]
                for i in range(0, 6):
                    kit.servo[i].angle = int(data[i])
                handle_moving(data[6] == "True")
                # Taking out error handling, which is out of bounds
                handle_recording(int(data[8]))
                if (data[9] == "True"):
                    handle_quit()
                    
    except Exception as e:
        print("Connection Closed or some other error!")
        print(type(e))
        print(e)
        set_clear()
        set_free()
        

pixels.fill(CYAN)
slowmove(restdatahalf)
move(readydata)

start_server = websockets.serve(loop, ip, 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
