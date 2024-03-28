import math
import time

from dronekit import connect, Command, VehicleMode, LocationGlobalRelative

# Set up option parsing to get connection string
import argparse
from dronekit import connect

parser = argparse.ArgumentParser(description='Demonstrates mission import/export from a file.')
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

# Specify the vehicle type as Rover by setting the vehicle_class parameter
vehicle = connect(connection_string, wait_ready=True)

# Competition dimensions and guidelines
distance = 30  # Distance in meters
speed = 0.17  # Speed in meters_per_second


# Calculates the target location
def calculate_target_location(current_ugv_location):
    d_lat = distance * math.cos(math.radians(current_ugv_location.lat))
    d_lon = distance * math.sin(math.radians(current_ugv_location.lon))
    target_location = LocationGlobalRelative(current_ugv_location.lat + d_lat, current_ugv_location.lon + d_lon,
                                             current_ugv_location.alt)
    return target_location


# Function to move the vehicle along a straight line
def perform_straight_line_movement():
    """
          This function moves the vehicle along a straight line.
          """
    # Calculate time to traverse the distance using the formula: time = distance/speed
    time_to_traverse = distance / speed

    print(f"Time to traverse: {time_to_traverse} sec(s)")

    # Set the vehicle to GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")

    # Arm the vehicle
    vehicle.armed = True

    # Wait for the vehicle to arm
    while not vehicle.armed:
        time.sleep(1)

    print("Vehicle armed!")

    target_location = calculate_target_location(vehicle.location.global_relative_frame)
    print(f"Calculated Target Location: {target_location.lat}, {target_location.lon}")

    # Move to the target location
    vehicle.simple_goto(target_location)

    # Wait for the vehicle to reach the target location
    start_time = time.time()
    while True:
        time_elapsed = time.time() - start_time
        if time_elapsed >= time_to_traverse:
            break

        # Updates the distance covered
        distance_covered = min(speed * time_elapsed, distance)

        print(f"Time elapsed: {time_elapsed} sec, Distance covered: {distance_covered:.2f} meters. ")
        time.sleep(1)

    print("UGV Reached destination!")


# Perform straight line movement given the speed and distance.
# Currently set at 30 meters for distance and 0.17m/s for speed.
perform_straight_line_movement()

# Disarm and close connection
vehicle.armed = False
vehicle.close()
