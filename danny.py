"""
EV3 program to search the maz using 'Left hand rule'
Author: WallDashE
Date: 9 May 2016
"""

# Import a few system libraries that will be needed
from time import sleep
import sys, os

# This tells Python to look for additional libraries in the parent directory of this program
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import the ev3dev specific library
from ev3dev.auto import *

"""
We define two custom exceptions for when the touch sensors are triggered and when
one of the EV3's button's is pressed. This requires using Python's object-oriented
programming contructs. A 'class' defines a type of object. When the class name is
used a function, it creates a new object that is an instance of the class
"""

# Not sure if this is still needed
class Touch(Exception):
    def __init__(self, which_side):
        self.value = which_side

class ButtonPress(Exception):
    def __init__(self, message):
        self.message = message

class Found(Exception):
    def __init__(self,value):
        self.value = value

# Connect motors
rightMotor = LargeMotor(OUTPUT_D)
leftMotor  = LargeMotor(OUTPUT_A)
lift       = MediumMotor(OUTPUT_B)

# Connect sensors
ts = TouchSensor(INPUT_4);          assert ts.connected
cs = ColorSensor(INPUT_3);         assert cs.connected
us  = UltrasonicSensor(INPUT_2);    assert us.connected
gs  = GyroSensor(INPUT_1);          assert gs.connected

# gs.mode = 'GYRO-RATE'   # Changing the mode resets the gyro
gs.mode = 'GYRO-ANG'    # Set gyro mode to return compass angle

cs.mode = "COL-COLOR"

# We will need to check EV3 buttons state.
btn = Button()

# Controls movement of claw in (destroy) and out (reset)
def destroy():
    while lift.position > -350:
        lift.run_to_abs_pos(duty_cycle_sp=100,position_sp=-350)

def reset():
    while lift.position < 700:
        lift.run_to_abs_pos(duty_cycle_sp=100,position_sp=700)

# Motor functions
def stop():
    # Stop both motors
    leftMotor.stop(stop_command='brake')
    rightMotor.stop(stop_command='brake')

def run_motors(left, right, duration):
    leftMotor.run_direct(duty_cycle_sp=left)
    rightMotor.run_direct(duty_cycle_sp=right)

    while duration > 0:
        sleep(0.1)
        duration -= 0.1

        if btn.any():
            raise ButtonPress("Stop robot")
        if ts.value():
            raise Touch(1)
        if us.value() > 200:
            raise Touch(-1)
        if cs.value() == 5:
            raise Found(1)
        if cs.value() != 5:
            raise Found(0)

def backup():
    """
    The call to 'run_motors' is embedded in a 'try-except' construct. So if a sensor
    is triggered during the operation of run_motors, an exception will be raised,
    causing run_motors to exit and the exception will be caught here. Note that 'backup'
    only catches 'Touch' exceptions. If a 'ButtonPress' exception is raised, that has
    to be caught elsewhere. In this case, that's in the top level code.
    """

    # Turn backup lights on:
    Leds.set_color(Leds.LEFT, Leds.RED)
    Leds.set_color(Leds.RIGHT, Leds.RED)

    try:
        run_motors(-50, -50, 0.5)
        rightMotor.stop(stop_command='brake')
        leftMotor.stop(stop_command='brake')
    except Touch as t:
        #turn(t.value) #turns right
        sleep(0.1)


# Turn function with input direction
def turn(dir):
    try:
        currentGs = gs.value()
        while gs.value() >= currentGs - 30:
            run_motors(dir*30, -dir*30, 0.5)
    except Touch as t:
        sleep(1)

# Move forward for a set amount of time
def moveForward():
    try:
        run_motors(70,70,3)
    except Touch as t:
        sleep(1)

# Main function
while True:
    try:
        # Turn lights green:
        Leds.set_color(Leds.LEFT, Leds.GREEN)
        Leds.set_color(Leds.RIGHT, Leds.GREEN)
        run_motors(70, 70, 10)
        print 1
    except Touch as t:
        if ts.value():
            print 2
            backup()
            turn(t.value)
            moveForward()
            
        if us.value() > 200:
            turn(t.value)
            print gs.value()
            #moveForward()
            #run_motors(50, 50, 1)
            
    except Found as t:
        if cs.value() == 5:
            stop()
            destroy()
        else:
            reset()
    except ButtonPress:
        stop()
        sys.exit()


# Stop the motors before exiting.
stop()
