from time    import sleep
import sys, os
from ev3dev.auto import *
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

"""
0 = no Color
1 = black
2 = blue
3 = green
4 = yellow
5 = red
6 = white
7 = brown
"""

#Connect motors
lift = MediumMotor(OUTPUT_B);   assert lift.connected
left = LargeMotor(OUTPUT_A);    assert left.connected
right = LargeMotor(OUTPUT_D);   assert right.connected

us = UltrasonicSensor(INPUT_2);        assert us.connected
ts = TouchSensor(INPUT_4);             assert ts.connected
cs = ColorSensor(INPUT_3);             assert cs.connected
gs = GyroSensor(INPUT_1);               assert gs.connected

# We will need to check EV3 buttons state.
btn = Button()
cs.mode = "COL-COLOR" 

# charges at opponent at 100% speed
def charge():
    right.run_direct(duty_cycle_sp=70)
    left.run_direct(duty_cycle_sp=70)
    
def chargeLen(len):
    right.run_direct(duty_cycle_sp=70, time_sp=len*1000)
    left.run_direct(duty_cycle_sp=70, time_sp=len*1000)
    
    
def reverse():
	right.run_direct(duty_cycle_sp=-70, time_sp=500)
	left.run_direct(duty_cycle_sp=-70, time_sp=500)

# close arm
def closeArm():
    while lift.position > -1000:
        lift.run_to_abs_pos(position_sp=-1000)

# open arm
def resetArm():
    while lift.position < 200:
        lift.run_to_abs_pos(position_sp= 200)

def turnLeft():
    currentGs = gs.value()
    while gs.value() >= currentGs - 85:
        right.run_direct(duty_cycle_sp=30)
        left.run_direct(duty_cycle_sp=-30)

def turnRight():
    currentGs = gs.value()
    while gs.value() <= currentGs + 85:
        right.run_direct(duty_cycle_sp=-30)
        left.run_direct(duty_cycle_sp=30)

def stop():
    right.run_direct(duty_cycle_sp=0)
    left.run_direct(duty_cycle_sp=0)

    
# main program 
charge()
while not btn.any():    
    while us.value() < 200:    
        print us.value()
        charge()
        
        direction = gs.value();     
        
        if direction > 5:
            right.duty_cycle_sp = 5
        elif direction < -5:
            left.duty_cycle_sp = 5
        else:
            left.duty_cycle_sp = 70
            right.duty_cycle_sp = 70
            
        if ts.value():
            reverse()
            turnRight()
            stop()
            
        if cs.value() == 5:
            closeArm()
        else:
            resetArm()
            
    while us.value() >= 200:
        print us.value()
        turnLeft()
        chargeLen(1)      
        
stop()
resetArm()