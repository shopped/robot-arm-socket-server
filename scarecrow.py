import sys
import time
import signal
import subprocess
import config.default as config
from adafruit_servokit import ServoKit

detect_motion = None
kit = ServoKit(channels=16)
config.set_pwm_ranges(kit)
for i in range(6):
    kit.servo[i].angle = config.resting[i]
current_position = config.resting.copy()

def signal_handler(sig, frame):
    for i in range(6):
        kit.servo[i].angle = None
    if detect_motion:
        detect_motion.terminate()
    sys.exit()

def slow_move(final):
    global current_position
    count = 0
    while (count < 6):
        count = 0
        for i in range(6):
            if (current_position[i] < final[i]):
                current_position[i] += 1
                kit.servo[i].angle = current_position[i]
            elif (current_position[i] > final[i]):
                current_position[i] -= 1
                kit.servo[i].angle = current_position[i]
            else:
                count += 1
        time.sleep(0.1)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

detect_motion = subprocess.Popen("/home/million/robot-arm-socket-server/exit-on-motion")
while True:
    while detect_motion.poll() != 0:
        time.sleep(1)
    time.sleep(2)
    for i in range(6):
        kit.servo[i].angle =  90
        current_position[i] = 90
    time.sleep(10)
    slow_move(config.resting)
    detect_motion = subprocess.Popen("/home/million/robot-arm-socket-server/build/detect_motion")
