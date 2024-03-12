# Challenge: UAV challenge 1
# Project: Raytheon Drone Competition
# Team: PantherBytes

import argparse
import time
# Set up option parsing to get connection string
from math import radians, cos

from dronekit import connect, VehicleMode, LocationGlobalRelative

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

print()
print()
print("--------------------")
print("STARTING CHALLENGE UAV 1")
print("--------------------")
print()
print()
# Connect to the Vehicle
print('Connecting to vehicle on: %s' % connection_string)
vehicle = connect(connection_string, wait_ready=True)


# Arm and take off to an altitude of 2 meters
def arm_and_takeoff(a_target_altitude):
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
    vehicle.simple_takeoff(a_target_altitude)  # Take off to target altitude

    # Wait until the vehicle reaches a safe height before exiting
    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)
        if vehicle.location.global_relative_frame.alt >= a_target_altitude * 0.95:  # Trigger just below target alt.
            print("Reached target altitude")
            break
        time.sleep(1)


def perform_lawnmower_pattern(field_width, field_length, altitude):
    """
       This function executes a lawn mower pattern over a specified area.

       :param field_width: The width of the field in feet.
       :param field_length: The length of the field in feet.
       :param altitude: The altitude at which the drone will fly, in meters.
       """
    global waypoint
    home_location = vehicle.location.global_frame

    # Moves forward by 2 feet to take into account the starting position
    forward_position = LocationGlobalRelative(
        home_location.lat + (2 / 111111),
        home_location.lon,
        altitude
    )
    vehicle.simple_goto(forward_position)
    time.sleep(5)

    # Sets the initial position for the lawn mower pattern
    initial_position = LocationGlobalRelative(
        forward_position.lat,
        forward_position.lon,
        altitude
    )

    # Step size for the width iteration and can be adjusted based on the coverage we need.
    step_size = 5

    # First loop iterates over the width of the field.
    # Set the step_size to determine the spacing between two consecutive width-based waypoints.
    # Second loop iterates over the length of the field.
    for x in range(0, field_width, step_size):
        for y in range(0, field_length, 5):
            waypoint_lat = initial_position.lat + x / 111111
            waypoint_lon = initial_position.lon + y / (111111 * cos(radians(initial_position.lat)))

            if x % (2 * step_size) != 0:  # Reverse the direction every other row
                waypoint_lon = initial_position.lon + ((field_length - step_size) - y) / (
                        111111 * cos(radians(initial_position.lat)))

            waypoint = LocationGlobalRelative(waypoint_lat, waypoint_lon, altitude)
            vehicle.simple_goto(waypoint)
            time.sleep(2)

    # Moves forward by 2 feet to take into account the finishing line
    final_position = LocationGlobalRelative(
        waypoint.lat + (2 / 111111),
        waypoint.lon,
        altitude
    )
    vehicle.simple_goto(final_position)
    time.sleep(5)  # This is to make sure the drone gets to the final position


# Arm and take off to an altitude of 10 meters.
arm_and_takeoff(10)

# Perform the mowing pattern over a specified width and length.
perform_lawnmower_pattern(30, 50, 10)

# Land the drone
print("Setting LAND mode...")
vehicle.mode = VehicleMode("LAND")

# Close the vehicle object before exiting the script
print("Close vehicle object")
vehicle.close()

# Shut down the simulator
if sitl:
    sitl.stop()

print()
print()
print("--------------------")
print("Completed UAV CHALLENGE 1")
print("--------------------")
