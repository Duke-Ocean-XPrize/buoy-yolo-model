from __future__ import division
import Adafruit_PCA9685
from dronekit import *
from pymavlink import mavutil
import signal
import time

# Initialise the PCA9685 using the default address (0x40).
global pwm
pwm = Adafruit_PCA9685.PCA9685()
pwm.set_pwm_freq(110)


global vehicle
global Tn
Tn = 1100

global r, p, y
r = 1500 #1530
p = 1500 #1530
y = 1500


################ Signal Parameters ###############
servo_max = int(2000*4096/9000)
servo_mid = int(1500*4096/9000)
servo_min = int(1000*4096/9000)
################ Will not Change, so no meed to be global ###############

def connect_drone():
    global vehicle
    connection_string = '/dev/ttyACM0'
    baud_rate = 115200
    print("Connecting to vehicle on: %s" % (connection_string))

    vehicle = connect(connection_string, baud=baud_rate)
    print(vehicle.location.global_relative_frame.alt)
    

def emergency_end_program(*args):
    global vehicle
    global Tn
    print('Emergency Landing')
    pwm.set_pwm(4, 0, servo_max) #Mode Land
    time.sleep(1)
    pwm.set_pwm(2, 0, servo_min)

    #while (Tn>1000):
        #Tn = Tn-10
        #pwm.set_pwm(2, 0, int(Tn *4096/9000))
        #time.sleep(0.5)
        #print(Tn)

    #time.sleep(1)
    #disarm()
    #time.sleep(1)
    vehicle.close()
    quit()

signal.signal(signal.SIGINT,emergency_end_program)




def disarm():
    pwm.set_pwm(3,0,servo_min)




def arm():
    print('Arming Drone')
    # Yaw to Mid.
    pwm.set_pwm(3,0,servo_mid)
    pwm.set_pwm(4,0,servo_min) # Change to Mode 1
    time.sleep(1)
    pwm.set_pwm(4,0,servo_mid) # Change to Mode 3 or 4
    time.sleep(1)
    # Yaw to Max
    pwm.set_pwm(3, 0, servo_max)
    # Set Throttal Min & Row Pitch Mid
    pwm.set_pwm(2, 0, servo_min) # Throttal to 0 
    pwm.set_pwm(0, 0, servo_mid)
    pwm.set_pwm(1, 0, servo_mid)
    time.sleep(3)
    #Yaw to Mid 
    pwm.set_pwm(3,0,servo_mid)


def land():
    print('Land Drone')
    pwm.set_pwm(4, 0, servo_max) #Mode to Land
    pwm.set_pwm(2, 0, servo_min) #Throttal to Min
    vehicle.close()
    quit()

def move_up():
    global vehicle
    global Tn
    global r, p, y
    print('Takeing off')

    Tn = 1100 
    # SET ROW PITCH YAW
    nr = int(r*4096/9000)
    np = int(p*4096/9000)
    ny = int(y*4096/9000)


    alt0 = vehicle.location.global_relative_frame.alt
    print('Alt0: ')
    print(alt0)
    timer = 0
    while (timer<50): 
        #Check Alt
        alt = vehicle.location.global_relative_frame.alt
        print(alt)
        if(alt < alt0-0.2):
            break
        #Haven't Taken Off Yet
        Tn = Tn + 10
        n = int(Tn *4096/9000)
        #Set Throttal Up
        pwm.set_pwm(2, 0, n)
        pwm.set_pwm(0, 0, nr)
        pwm.set_pwm(1, 0, np)
        pwm.set_pwm(3, 0, ny)

        timer = timer+ 1
        time.sleep(0.1)
    
    #Can't Take Off
    if(timer >=50):
        print('Can''t Take Off')
        land()
    #Go to 5 Meter above ground
    else:
        print('Go to 5Meter')
        while (alt>alt0-5):
            alt = vehicle.location.global_relative_frame.alt
            print(alt)
            time.sleep(0.1)
        #Change to Mode Loiter
        print('Alt_Hold Mode')
        #pwm.set_pwm(4, 0, servo_min)
        pwm.set_pwm(2, 0, int(1450 *4096/9000))
        pwm.set_pwm(4, 0 ,servo_min)
        while True:
            alt = vehicle.location.global_relative_frame.alt
            time.sleep(0.1)
        land()

def stop():
    print('Stop Motor Function')
    pwm.set_pwm(2, 0, servo_min)
    pwm.set_pwm(4, 0, servo_mid)
    pwm.set_pwm(2, 0, servo_min)


def move_left(n):
    global r
    if(r-n>=1000):
        r = r-n
        nr = int(r *4096/9000)
        pwm.set_pwm(0, 0, nr)

def move_right(n):
    global r
    if(r+n <=2000):
        r = r+n
        nr = int(r *4096/9000)
        pwm.set_pwm(0, 0, nr)

def forward(n):
    global p
    if(p-n>=1000):
        p = p-n
        np = int(p *4096/9000)
        pwm.set_pwm(1, 0, np)

def move_backward(n):
    global p
    if(p+n<=2000):
        p = p+n
        np = int(p *4096/9000)
        pwm.set_pwm(1, 0, np)

def hold():
    global r,p
    n = 1500
    p = 1500
    nr = int(r *4096/9000)
    np = int(p *4096/9000)
    pwm.set_pwm(0, 0, nr)
    pwm.set_pwm(1, 0, np)
