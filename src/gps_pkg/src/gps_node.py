#!/usr/bin/env python3

import serial
from time import sleep  # Import the sleep function directly
from std_msgs.msg import String
from sensor_msgs.msg import NavSatFix
import rospy

def publish_gps_data(serial_port):
    try:
        # Open a serial connection to the Reach RTK Rover
        with serial.Serial(serial_port, baudrate=57600, timeout=1) as ser:
            # Create a publisher for the raw GPS data
            raw_gps_data_publisher = rospy.Publisher('/raw_gps_data', String, queue_size=10)
            # Create a publisher for the NavSatFix data
            navsatfix_publisher = rospy.Publisher('/gps_data', NavSatFix, queue_size=10)
            rospy.init_node('gps_node', anonymous=True)

            while not rospy.is_shutdown():
                # Read data from the serial port
                data = ser.readline().decode('utf-8')

                # Publish raw GPS data
                raw_gps_data_publisher.publish(data)

                # Parse LLH data and publish NavSatFix
                try:
                    parts = data.split()
                    if len(parts) >= 4:  # Check if there are at least 4 parts
                        date = parts[0]
                        time_val = parts[1]
                        latitude = float(parts[2])
                        longitude = float(parts[3])
                        altitude = float(parts[4])

                        gps_data = NavSatFix()
                        gps_data.latitude = latitude
                        gps_data.longitude = longitude
                        gps_data.altitude = altitude

                        navsatfix_publisher.publish(gps_data)

                        # Print LLH data
                        print(f"Date: {date}, Time: {time_val}, Latitude: {latitude}, Longitude: {longitude}, Altitude: {altitude}")

                    else:
                        rospy.logwarn(f"Invalid LLH data format: {data}")

                except Exception as e:
                    rospy.logerr(f"Error parsing LLH data: {e}")

                # Wait for a moment before the next request (adjust the sleep time as needed)
                sleep(1)

    except Exception as e:
        rospy.logerr(f"Error: {e}")

if __name__ == "__main__":
    # Use the correct serial port for your system (e.g., /dev/ttyACM0)
    serial_port = '/dev/ttyACM3'

    try:
        publish_gps_data(serial_port)
    except rospy.ROSInterruptException:
        pass
