#!/usr/bin/python

"""
EV3 program to drive one direction but try to go around obstacles when bumped.
Author: Claude Sammut
Date: 1 April 2016

This program gets around the limitation of 'avoid.tidy.py', which can't handle
a new contact during the backup.

We introduce Python's exception mechanism to interrupt the normal flow of control.
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

class Touch(Exception):
	def __init__(self, which_side):
		self.value = which_side

class ButtonPress(Exception):
	def __init__(self, message):
		self.message = message

#Connect motors
rightMotor = LargeMotor(OUTPUT_B)
leftMotor  = LargeMotor(OUTPUT_C)

# Connect touch sensors.
ts1 = TouchSensor(INPUT_1);	assert ts1.connected
ts4 = TouchSensor(INPUT_4);	assert ts4.connected
us  = UltrasonicSensor();	assert us.connected
gs  = GyroSensor();		assert gs.connected

gs.mode = 'GYRO-RATE'	# Changing the mode resets the gyro
gs.mode = 'GYRO-ANG'	# Set gyro mode to return compass angle

# We will need to check EV3 buttons state.
btn = Button()

def stop():
	# Stop both motors
	leftMotor.stop(stop_command='brake')  
	rightMotor.stop(stop_command='brake')

def run_motors(left, right, duration):
	"""
	Run both motors at the given speeds for a give duration.
	Instead of sleeping for the entire duration of the operation, we break the
	sleep up into 0.1 second intervals and loop. This allows the robot to wake
	up prediodically to check its sensors. If a sensor is triggered, the program
	raises an exception, causing the normal control flow to be interrupted. The
	calling code MUST have a 'try-except' construct to catch the exception.

	This still isn't ideal because we have to handle the sensors inside the motor
	control program, which isn't a very logical way to structure the program.
	"""
	leftMotor.run_direct(duty_cycle_sp=left)
	rightMotor.run_direct(duty_cycle_sp=right)

	while duration > 0:
 		sleep(0.1)
		duration -= 0.1

		if btn.any():
			raise ButtonPress("Stop robot")
		if ts1.value():
			raise Touch(-1)
		elif ts4.value():
			raise Touch(1)

def backup(dir):
	"""
	Back away from an obstacle and turn in the direction opposite to the contact.
	The call to 'run_motors' is embedded in a 'try-except' construct. So if a sensor
	is triggered during the operation of run_motors, an exception will be raised,
	causing run_motors to exit and the exception will be caught here. Note that 'backup'
	only catches 'Touch' exceptions. If a 'ButtonPress' exception is raised, that has
	to be caught elsewhere. In this case, that's in the top level code.
	"""

	# Sound backup alarm.
	Sound.tone([(1000, 500, 500)] * 3)

	# Turn backup lights on:
	Leds.set_color(Leds.LEFT, Leds.RED)
	Leds.set_color(Leds.RIGHT, Leds.RED)

	try:
		# Stop both motors and reverse for 1.5 seconds
		# then turn the wheels in opposite directions for 0.25 seconds
		run_motors(-50, -50, 1.5)
		run_motors(dir*75, -dir*75, 0.25)
	except Touch as t:
		backup(t.value)


# Run the robot

while True:
	"""
	If we bump an obstacle, back away, turn and go in other direction.
	'run_motors' is again called within a 'try-except' construct. This time,
	we handle both types of exceptions. When a button press is caught, the motors
	are turned off and the whole program exits.
	"""
	try:
		# Turn lights green:
		Leds.set_color(Leds.LEFT, Leds.GREEN)
		Leds.set_color(Leds.RIGHT, Leds.GREEN)
 		run_motors(dc, dc, 10)
	except Touch as t:
		backup(t.value)
	except ButtonPress:
		stop()
		sys.exit()


# Stop the motors before exiting.
stop()
