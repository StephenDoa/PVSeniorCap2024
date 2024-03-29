import math
import time

from dronekit import connect, VehicleMode, LocationGlobalRelative

# Set up option parsing to get connection string
import argparse

parser = argparse.ArgumentParser(description='Demonstrates mission import/export from a file.')
parser.add_argument('--connect',
                    help="Vehicle connection target string. If not specified, SITL automatically started and used.")
args = parser.parse_args()

connection_string = args.connect

# Start SITL if no connection string specified
if not connection_string:
    import dronekit_sitl

    sitl = dronekit_sitl.start_default()
    connection_string = sitl.connection_string()

print("")
print("")
print("--------------------")
print("STARTING CHALLENGE UGV 2")
print("--------------------")
print("")
print("")

# Connect to the Vehicle
print('Connecting to vehicle on: %s' % connection_string)

# Specify the vehicle type as Rover by setting the vehicle_class parameter
vehicle = connect(connection_string, wait_ready=True)

# Competition dimensions and guidelines
field_size_yards = 30  # Field size in yards
speed_in_yards_per_second = 1 / 12  # Speed in yards per second

# Calculate the finishing line location (slightly beyond the 30 yards line)
finishing_line_location_yards = field_size_yards + 1  # Adjust as needed


# Calculates the target location
def calculate_target_location(current_ugv_location, distance):
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
    # Calculate time to traverse the field size using the formula: time = field_size/speed
    time_to_traverse = field_size_yards / speed_in_yards_per_second

    print(f"Time to traverse the field: {int(time_to_traverse // 60)} min {int(time_to_traverse % 60)} sec(s)")

    # Set the vehicle to GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")

    # Arm the vehicle
    vehicle.armed = True

    # Wait for the vehicle to arm
    while not vehicle.armed:
        time.sleep(1)

    print("Vehicle armed!")

    # Calculate target location (slightly beyond the 30 yards line)
    target_location = calculate_target_location(vehicle.location.global_relative_frame, finishing_line_location_yards)
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
        distance_covered_yards = min(speed_in_yards_per_second * time_elapsed, field_size_yards)

        # Convert time elapsed to minutes and seconds
        minutes = int(time_elapsed // 60)
        seconds = int(time_elapsed % 60)

        print(f"Time elapsed: {minutes} min {seconds} sec, Distance covered: {distance_covered_yards:.2f} yards.")
        time.sleep(1)

    print("UGV Crossed the finishing line!")


# Perform straight line movement given the speed and field size.
# Currently set at 30 yards for field size and ~12 seconds per yard for speed.
perform_straight_line_movement()

# Disarm and close connection
vehicle.armed = False
vehicle.close()

print("")
print("")
print("--------------------")
print("Completed UGV CHALLENGE 2")
print("--------------------")
