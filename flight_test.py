# Import DroneKit-Python
from dronekit import *

import `time`
import sys
import math
import signal
import zmq
from threading import Thread

################################
####### GLOBAL VARIABLES #######
################################
global vehicle              # object that holds the drone connection/info
vehicle = None

##################################
####### METHOD DEFINITIONS #######
##################################

# Arm the vehicle and takeoff to target altitude in meters
def arm_and_takeoff(aTargetAltitude):
    # Don't arm until autopilot is ready
    print "Basic pre-arm checks..."
    while not vehicle.is_armable:
        print "Waiting for vehicle to initialize..."
        time.sleep(1)

    # Arm the drone in GUIDED mode
    print "Arming the drone..."
    vehicle.mode = VehicleMode("GUIDED")
    while (not vehicle.mode=='GUIDED'):
        print "Waiting for guided mode"
        vehicle.mode = VehicleMode("GUIDED")
        time.sleep(2)


    vehicle.armed = True
    # Confirm that the mode is set and drone is armed
    while (not vehicle.armed):
        print "Waiting for arming..."
        vehicle.armed = True
        time.sleep(2)

    print "Ready to take off! (maybe not if safety switch is on...)"
    time.sleep(2)

    # Take off to target altitude
    print "Taking off"
    vehicle.simple_takeoff(aTargetAltitude)

    # Wait until the drone reaches at least 95% of the target
    # altitude before running other commands
    while True:
        relative_alt = vehicle.location.global_relative_frame.alt
        absolute_alt = vehicle.location.global_frame.alt
        print "Relative Altitude: %s" % relative_alt
        # print "Absolute Altitude: %s" % absolute_alt

        if relative_alt >= aTargetAltitude*0.95:
            print "Reached target altitude"
            break

        time.sleep(1)

# Display some basic state information
def show_info():
    # print " Type: %s" % vehicle.vehicle_type
    print " Armed: %s" % vehicle.armed
    print " Mode: %s" % vehicle.mode.name
    print " System status: %s" % vehicle.system_status.state
    print " GPS: %s" % vehicle.gps_0
    print " Location: %s,%s" % (vehicle.location.global_relative_frame.lat,
                                vehicle.location.global_relative_frame.lon)
    print " Relative Alt: %s" % vehicle.location.global_relative_frame.alt
    print " Absolute Alt: %s" % vehicle.location.global_frame.alt

# Prints the location of the drone in a format to use with Google Earth
def print_location():
    lon = vehicle.location.global_frame.lon
    lat = vehicle.location.global_frame.lat
    alt = vehicle.location.global_frame.alt
    groundspeed = vehicle.groundspeed
    airspeed = vehicle.airspeed
    print "%s,%s,%s" % (lon,lat,alt)
    print "Airspeed: %s" % airspeed
    print "Groundspeed: %s" % groundspeed
    time.sleep(1)

# A simple pause to wait for the user to continue
def pause_for_input():
    raw_input("** PRESS ENTER TO CONTINUE **")

# Signal handler for when a keyboard interrupt occurs or program end
def end_program(*args):
    # Disarm the drone and wait before closing
    # tell to disarm False
    # while vehicle.armed:
    #     vehicle.armed = False
        # time.sleep(2)
    while (not vehicle.mode == 'RTL'):
        vehicle.mode = VehicleMode("RTL")

    # Close the connection to the drone
    vehicle.close()

    # if background_thread is not None:
    #     while background_thread.isAlive():
    #         print "Attempting to close threads"
    #         background_thread.join(1)
    #         time.sleep(1)

    print "Threads closed...program ending"
    print "Completed"
    quit()

def connect_for_data(connection_port):
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.bind(connection_port)
    return socket;

def receive_data(socket):
    data_string = socket.recv(flags=zmq.NOBLOCK)
    #Format is [systemID, X, Y, Z]
    return data_string.split(",")

def purge_messages(socket, timeout_step):
    timeout = time.time() + timeout_step
    while time.time() < timeout:
        try:
            receive_data(socket)
        except zmq.Again as e:
            print("All messages purged.")
            break

#########################
####### MAIN CODE #######
#########################

# Set up interrupt handler for keyboard interrupt
signal.signal(signal.SIGINT, end_program)

# Start simulation and connect to the drone
# HOME LOCATION (Test Site): 35.970264,-79.091461
# SITL command: dronekit-sitl copter-3.3 --home=35.970264,-79.091461,170,353
# print "Start simulator (SITL)"
# sitl = dronekit_sitl.start_default()
# connection_string = sitl.connection_string()

# connection_string = 'tcp:127.0.0.1:5760'
connection_string = 'com4'
baud_rate = 115200
socket = connect_for_data("tcp://*:5556")
print "Connecting to vehicle on: %s" % connection_string
# vehicle = connect(connection_string, wait_ready=True)
vehicle = connect(connection_string, baud=baud_rate)

# Create message listener using decorator
@vehicle.on_message('*')
def listener(self, name, message):
    if name == 'COMMAND_ACK':
        if message.result != 0:
            print "COMMAND FAILED!"
        print 'message command: %s' % message.command
        print 'message results: %s' % message.result

show_info()

# vehicle.mode = VehicleMode('GUIDED')
# vehicle.armed = True
# vehicle.simple_takeoff(1)
# time.sleep(5)
# end_program()

# Takeoff to 2 meters
alt = 2
arm_and_takeoff(alt)

#######################################################################
##Code that moves in directions if marker found in certain direction.##
#######################################################################
timeout = time.time() + 50
while True:
    if time.time() < timeout:
        break
    try:
        data = receive_data(socket)
        #Mode keeps altitude but not pitch and roll.
        while vehicle.mode != VehicleMode(ACRO):
            vehicle.mode = VehicleMode("ACRO")
        #Rotate pitch and roll to move towards marker direction.
        if data[1] > 0:
            vehicle.rotate(-15, 0, 0)
            #Sleep to allow for a little bit of rotation.
            time.sleep(0.15)
            #Re-rotate back.
            vehicle.rotate(15, 0, 0)
        elif data[1] < 0:
            vehicle.rotate(15, 0, 0)
            #Sleep to allow for a little bit of rotation.
            time.sleep(0.15)
            #Re-rotate back.
            vehicle.rotate(-15, 0, 0)
        if data[2] > 0:
            vehicle.rotate(0, 15, 0)
            #Sleep to allow for a little bit of rotation.
            time.sleep(0.15)
            #Re-rotate back.
            vehicle.rotate(0, -15, 0)
        elif data[2] < 0:
            vehicle.rotate(0, -15, 0)
            #Sleep to allow for a little bit of rotation.
            time.sleep(0.15)
            #Re-rotate back.
            vehicle.rotate(0, 15, 0)
        #Just in case, use STABILIZE mode to stabilize automatically.
        while vehicle.mode != VehicleMode(STABILIZE):
            vehicle.mode = VehicleMode("STABILIZE")
            time.sleep(3)
        purge_messages(socket, 4)
    except zmq.Again as e:
        print "No message received yet"

print "Ready to land"
pause_for_input()

#land at current position
vehicle.mode = VehicleMode("LAND")
while True:
    alt = vehicle.location.global_relative_frame.alt
    print "Altitude: %s" % alt
    if alt <= 0.5:
        print "Landed"
        break
    time.sleep(0.5)

show_info()

# Script is completed
end_program()
