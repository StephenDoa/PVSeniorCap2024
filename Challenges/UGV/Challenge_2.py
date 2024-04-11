import datetime
import math
import time
import argparse
from dronekit import connect, VehicleMode, LocationGlobalRelative
import logging

# Set up option parsing to get connection string
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

# Set up logging configuration
logging.basicConfig(
    filename='ugv_basic.log',
    level=logging.INFO,
    format="RTXDC_2024 PVAMU_UGV_%(message)s",
    filemode="w"
)


# Log soak action
def log_soak(action, aruco_marker_id, gps_location):
    """
        Log soak action with specified parameters.

        Parameters:
            action (str): The action performed during the soak.
            aruco_marker_id (string): The ID of the ArUco marker associated with the soak.
            gps_location (str): The GPS location where the soak action is performed.

        Description:
            This function logs a soak action with details such as action type, ArUco marker ID,
            timestamp, and GPS location.

        Example:
             log_soak("Soaked", 123, "51.5074_0.1278")
            # Logs: "Soaked_123_[24hr datetime stamp]_51.5074_0.1278"

        Notes:
            - The timestamp is generated using UTC time in ISO 8601 format appended with 'Z'.
            - Ensure appropriate logging configuration, e.g., logging.basicConfig(level=logging.INFO).
            - Adheres to competition's specified method for logging soak actions.
        """
    # Get current timestamp in ISO 8601 format
    timestamp = datetime.datetime.utcnow().isoformat() + 'Z'
    # Construct the log message
    logging.info(f"{action}_{aruco_marker_id}_{timestamp}_{gps_location}")


# Connect to the Vehicle
logging.info(f"Connecting to vehicle on: {connection_string}")
vehicle = connect(connection_string, wait_ready=True)

# Competition dimensions and guidelines
field_size_yards = 30  # Field size in yards
field_size_meters = (field_size_yards + 0.1) * 0.9144  # Field size in meters (2 yards converted to meters)
speed_in_meters_per_second = 1 / 12 * 0.9144  # Speed in meters per second (1 yard per second converted to meters)

# Calculate the finishing line location (exactly at the 2 yards mark)
finishing_line_location_meters = field_size_meters * 0.9144  # Adjust as needed


# Calculates the target location
def calculate_target_location(current_ugv_location, distance):
    d_lat = distance * math.cos(math.radians(current_ugv_location.lat))
    d_lon = distance * math.sin(math.radians(current_ugv_location.lon))
    target_location = LocationGlobalRelative(current_ugv_location.lat + (d_lat / 111111), current_ugv_location.lon + (
            d_lon / (111111 * math.cos(math.radians(current_ugv_location.lat)))),
                                             current_ugv_location.alt)
    return target_location


# Function to move the vehicle along a straight line
def perform_straight_line_movement():
    """
    This function moves the vehicle along a straight line.
    """
    # Calculate time to traverse the field size using the formula: time = field_size/speed
    time_to_traverse = field_size_meters / speed_in_meters_per_second

    logging.info(f"Time to traverse the field: {int(time_to_traverse // 60)} min {int(time_to_traverse % 60)} sec(s)")

    # Set the vehicle to GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    logging.info("Vehicle Mode: GUIDED")

    # Arm the vehicle
    vehicle.armed = True

    # Wait for the vehicle to arm
    while not vehicle.armed:
        time.sleep(1)

    logging.info("Vehicle ARMED!")

    # Calculate target location (exactly at the 2 yards mark)
    target_location = calculate_target_location(vehicle.location.global_relative_frame, finishing_line_location_meters)
    logging.info(f"Calculated Target Location: ({target_location.lat}, {target_location.lon})")

    # Move to the target location
    vehicle.simple_goto(target_location)

    # Wait for the vehicle to reach the target location
    start_time = time.time()
    while True:
        time_elapsed = time.time() - start_time
        if time_elapsed >= time_to_traverse:
            break

        # Updates the distance covered
        distance_covered_meters = min(speed_in_meters_per_second * time_elapsed, field_size_meters)

        # Convert time elapsed to minutes and seconds
        minutes = int(time_elapsed // 60)
        seconds = int(time_elapsed % 60)

        logging.info(
            f"Time elapsed: {minutes} min {seconds} sec, Distance covered: {distance_covered_meters:.2f} meters.")
        time.sleep(1)
    logging.info("Crossed the finishing line!")


# Perform straight line movement given the speed and field size.
perform_straight_line_movement()

# Disarm and close connection
vehicle.armed = False
vehicle.close()

logging.info("Completed UGV CHALLENGE 2")
