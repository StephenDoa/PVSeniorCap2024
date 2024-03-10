# Challenge: UAV challenge 1
# Project: Raytheon Drone Competition
# Team: PantherBytes

from dronekit import connect, VehicleMode
import time

# Set up option parsing to get connection string
import argparse

parser = argparse.ArgumentParser(description='Control Copter and send commands in GUIDED mode')
parser.add_argument('--connect',
                    help="Vehicle connection target string. If not specified, SITL automatically started and used.")
args = parser.parse_args()

connection_string = args.connect
sitl = None

# Start SITL if no connection string specified
if not connection_string:
    import dronekit_sitl

    sitl = dronekit_sitl.start_default()
    connection_string = sitl.connection_string()

# Connect to the Vehicle
print('Connecting to vehicle on: %s' % connection_string)
vehicle = connect(connection_string, wait_ready=True)


# Arm and take off to an altitude of 2 meters
def arm_and_takeoff(aTargetAltitude):
    print("Basic pre-arm checks")

    # Don't let the user try to arm until autopilot is ready
    while not vehicle.is_armable:
        print(" Waiting for vehicle to initialise...")
        time.sleep(1)

    print("Arming motors")
    # Copter should arm in GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    while not vehicle.armed:
        print(" Waiting for arming...")
        time.sleep(1)

    print("Taking off!")
    vehicle.simple_takeoff(aTargetAltitude)  # Take off to target altitude

    # Wait until the vehicle reaches a safe height before exiting
    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)
        if vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:  # Trigger just below target alt.
            print("Reached target altitude")
            break
        time.sleep(1)


# Arm and take off to an altitude of 2 meters
arm_and_takeoff(2)

# Hover for 20 seconds
print("Hovering for 20 seconds...")
time.sleep(20)

# Land the drone
print("Setting LAND mode...")
vehicle.mode = VehicleMode("LAND")

# Checks for the system status. Once it gets to standby, it stops
while vehicle.system_status.state != 'STANDBY':
    print("Waiting for landing... System Status:", vehicle.system_status.state)
    time.sleep(1)
print("Drone has landed. Altitude:", vehicle.location.global_relative_frame.alt)

# Close the vehicle object before exiting the script
print("Close vehicle object")
vehicle.close()

# Shut down the simulator if it was started.
if sitl is not None:
    sitl.stop()

print("Completed")
