"""
EV3 program to search the maz using 'Left hand rule'
Author: WallDashE (first draft by Kevin)
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

# Connect motors
rightMotor = LargeMotor(OUTPUT_D)
leftMotor  = LargeMotor(OUTPUT_A)

# Haven't used this yet
lift	   = MediumMotor(OUTPUT_B)

# Connect sensors
ts = TouchSensor(INPUT_4);			assert ts.connected
#cs = ColorSensor(INPUT_3);			assert cs.connected
us	= UltrasonicSensor(INPUT_2);	assert us.connected
gs	= GyroSensor(INPUT_1);			assert gs.connected

gs.mode = 'GYRO-RATE'	# Changing the mode resets the gyro
gs.mode = 'GYRO-ANG'	# Set gyro mode to return compass angle

#cs.mode = "COL-COLOR" 

# We will need to check EV3 buttons state.
btn = Button()

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

def backup():
	"""
	Back away from an obstacle and turn in the direction opposite to the contact.
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
		# Stop both motors and reverse for 1.5 seconds
		# then turn the wheels in opposite directions for 0.25 seconds
		run_motors(-50, -50, 0.5)
	except Touch as t:
		turn(1)
	  
			
# Turns right in two steps, reverse, then turn
def turn(dir):
	# Sound backup alarm.

	# Turn backup lights on:

	try:
		# Stop both motors and reverse for 1 seconds
		# then turn the wheels in opposite directions for 0.5 seconds
		#run_motors(50, -50, 0.5)
		run_motors(dir*75, -dir*75, 0.5)
		run_motors(50, 50, 1)
	except Touch as t:
		sleep(3)
  
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
			turn(t.value)
		if us.value() > 200:
			turn(t.value)
			#run_motors(50, 50, 1)
			print 3
	except ButtonPress:
		stop()
		sys.exit()


# Stop the motors before exiting.
stop()
