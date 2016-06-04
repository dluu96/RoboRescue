"""
EV3 program to search the maz us1ing 'Left hand rule'
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
We define two cus1tom exceptions for when the touch sensors are triggered and when
one of the EV3's button's is pressed. This requires us1ing Python's object-oriented
programming contructs. A 'class' defines a type of object. When the class name is
us1ed a function, it creates a new object that is an instance of the class
"""

# Not sure if this is still needed
class Touch(Exception):
	def __init__(self, which_side):
		self.value = which_side

class ButtonPress(Exception):
	def __init__(self, message):
		self.message = message
		

# class Found(Exception):
	# def __init__(self, if_found):
		# self.val = if_found

# Connect motors
rightMotor = LargeMotor(OUTPUT_D)
leftMotor  = LargeMotor(OUTPUT_A)
lift	   = MediumMotor(OUTPUT_B)

# Connect sensors
us1	= UltrasonicSensor(INPUT_2);	assert us1.connected
us2 = UltrasonicSensor(INPUT_4);	assert us2.connected
cs = ColorSensor(INPUT_3);			assert cs.connected
gs	= GyroSensor(INPUT_1);			assert gs.connected

gs.mode = 'GYRO-RATE'	  # Changing the mode resets the gyro
gs.mode = 'GYRO-ANG'	# Set gyro mode to return compass angle

cs.mode = "COL-COLOR"

# We will need to check EV3 buttons state.
btn = Button()

# Controls movement of claw in (destroy) and out (reset)
def destroy():
	while lift.position > -800:
		lift.run_to_abs_pos(duty_cycle_sp=100,position_sp=-800)
def reset():	
	while lift.position <-200:
		lift.run_to_abs_pos(duty_cycle_sp=100,position_sp=-200)
		
# Motor functions
# def stop():
	# # Stop both motors
	# # Added condition for stop() hopefully bypasses loop problem
	# while lift.position > 700 or lift.position < -350: 
		# leftMotor.stop(stop_command='brake')
		# rightMotor.stop(stop_command='brake')
		
def stopComplete():


	#stop both motors without condition
	leftMotor.stop(stop_command='brake')
	rightMotor.stop(stop_command='brake')

	
def reallign(angle):
	if gs.value() > angle:
		print "left"
		while(gs.value() > angle):
			leftMotor.run_direct(duty_cycle_sp=5)
			rightMotor.run_direct(duty_cycle_sp=70)
	else:
		print"right"
		while(gs.value() < angle):			
			leftMotor.run_direct(duty_cycle_sp=70)
			rightMotor.run_direct(duty_cycle_sp=5)
  
	
def run_motors(left, right, duration):
	direction = gs.value();

	leftMotor.run_direct(duty_cycle_sp=left)
	rightMotor.run_direct(duty_cycle_sp=right)
	while duration > 0: 
		print "value is"
		print direction,gs.value()
		if direction > 5:
			# print('right')
			rightMotor.duty_cycle_sp = 5
		elif direction < -5:
			# print('left')
			leftMotor.duty_cycle_sp = 5
		else:
			leftMotor.duty_cycle_sp = left
			rightMotor.duty_cycle_sp = right
			
		
		
		sleep(0.1)
		duration -= 0.1

		if btn.any():
			raise ButtonPress("Stop robot")
		if us2.value() < 20:
			raise Touch(1)
		if us1.value() > 200:
			raise Touch(-1)
		if cs.value() == 5:
			print("I found red")
			raise Touch(0)
		else:
			raise Touch(2)
			
		

def backup():
	"""
	The call to 'run_motors' is embedded in a 'try-except' construct. So if a sensor
	is triggered during the operation of run_motors, an exception will be raised,
	caus1ing run_motors to exit and the exception will be caught here. Note that 'backup'
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
		print "start:"
		print currentGs
		
		if (dir == -1):
			while gs.value() >= currentGs - 80:
				# run_motors(-30, 30, 0.5)
				leftMotor.run_direct(duty_cycle_sp = -30)
				rightMotor.run_direct(duty_cycle_sp = 30)
		else:
			while gs.value() <= currentGs + 90:
				leftMotor.run_direct(duty_cycle_sp = 30)
				
				rightMotor.run_direct(duty_cycle_sp = -30)
				# run_motors(30, -30, 0.5)
				
		print "global:"
	except Touch as t:
		sleep(1)

# Move forward for a set amount of time
def moveForward():
	print("At this point")
	try:
		run_motors(50,50,7)
	except Touch as t:
		sleep(1)

# Main function
while True:
	try:
		# Turn lights green:
		Leds.set_color(Leds.LEFT, Leds.GREEN)
		Leds.set_color(Leds.RIGHT, Leds.GREEN)
		run_motors(50, 50, 10)
		
	except Touch as t:
		if t.value == 1:
			print 2
			backup()
			turn(t.value)
			moveForward()			
		elif t.value == -1:
			turn(t.value)
			#print("Do I get here")
			moveForward()
			#run_motors(50, 50, 1)
			
		if t.value == 0:
			stopComplete()
			destroy()
			print("found!!!!!@$QeRqe")
		else:
			reset()
		
		
	# except Found as f:
		# if(cs.value() == 5):
			# print ("found red")
			# stopComplete()
			# destroy()
		# else:
			# reset()
			# print("not found red")
		# """
		# if (f.value == 1):
			# print("In found")
			# stopComplete()
			# destroy()
		# elif (f.value == 0):
			# print("Didn't find")
			# reset()
		# else:
			# pass
			# """
	except ButtonPress:
		stopComplete()
		sys.exit()


# Stop the motors before exiting.
stopComplete()
