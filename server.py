#!/usr/bin/env python
import asyncio
import socket
import websockets
import time
import board
import neopixel
import signal
import sys

import config.default as config

from adafruit_servokit import ServoKit
kit = ServoKit(channels=16)
config.set_pwm_ranges(kit)

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
YELLOW = (255,255,0)

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
    for index, address in enumerate(action_pixels):
        if (quarter2 == index) or (quarter * 2 + 1 == index):
            pixels[address] = BLUE
        else:
            pixels[address] = CLEAR

def set_looping(quarter):
    for index, address in enumerate(action_pixels):
        if (quarter * 2 == index) or (quarter * 2 + 1 == index):
            pixels[address] = BLUE
        else:
            pixels[address] = WHITE

set_clear()

hostname = socket.gethostname() + '.local'

are_we_loggin_it = True
are_we_live = True


def move(final):
    for i in range(0, 6):
        current_position[i] = final[i]
        kit.servo[i].angle = final[i]

def slowmove(final):
    global current_position
    if (isinstance(current_position[0], int) == False):
        current_position = list(map(lambda x: int(x), current_position))
    if (isinstance(final[0], int) == False):
        final = list(map(lambda x: int(x), final))
    count = 0
    while (count < 6):
        count = 0
        for i in range(0, 6):
            if (current_position[i] < final[i]):
                current_position[i] += 1
                kit.servo[i].angle = current_position[i]
            elif (current_position[i] > final[i]):
                current_position[i] -= 1
                kit.servo[i].angle = current_position[i]
            else:
                count += 1
        time.sleep(0.1)

def handle_quit():
    pixels.fill(MAGENTA)
    slowmove(halfway_resting_position)
    slowmove(config.resting)
    for i in range(6):
        kit.servo[i].angle = None
    set_clear()

current_position = config.resting.copy()
ready_position = [90, 90, 90, 90, 90, config.out_max[5] - config.out_min[5]]
halfway_resting_position = [(x[0] + (x[1] - x[0]) / 2) for x in zip(ready_position, config.resting)]
last_data = list("x" for x in range(4))

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
                current_position = data[:6]

                if (data[10] == "shutdown"):
                    handle_quit()
                else:
                    global last_data
                    new_data = data[6:10]
                    if new_data[0] != last_data[0]:
                        if new_data[0] == "free":
                            set_free()
                        elif new_data[0] == "left":
                            set_attached(False)
                        elif new_data[0] == "right":
                            set_attached(True)
                    elif new_data[1] != last_data[1]:
                        if new_data[1] == "idle":
                            set_inactive()
                        elif new_data[1] == "active":
                            set_active()
                        elif new_data[1] == "recording":
                            set_recording()
                    elif new_data[2] != last_data[2]:
                        if new_data[2] == "idle":
                            set_inactive()
                        elif new_data[2] == "playback":
                            set_playback(0)
                        elif new_data[2] == "looping":
                            set_looping(0)
                    elif new_data[3] != last_data[3]:
                        if (new_data[2] == "playback"):
                            set_playback(int(new_data[3]))
                        elif (new_data[2] == "looping"):
                            set_looping(int(new_data[3]))
                    if (new_data[1] != "idle" or new_data[2] != "idle"):
                        for i in range(0, 6):
                            kit.servo[i].angle = config.lerp(i, int(data[i]))
                    last_data = new_data
                    
    except Exception as e:
        print("Connection Closed or some other error!")
        print(type(e))
        print(e)
        set_clear()
        set_free()
        

pixels.fill(YELLOW)
slowmove(halfway_resting_position)
pixels.fill(CYAN)

def signal_handler(sig, frame):
    handle_quit()
    sys.exit()

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

start_server = websockets.serve(loop, hostname, 8765)

if (are_we_loggin_it):
    print("Server Ready")

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
