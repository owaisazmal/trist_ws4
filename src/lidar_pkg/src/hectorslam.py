#!/usr/bin/env python3

import rospy
from sensor_msgs.msg import LaserScan

def laser_callback(msg):
    ranges = msg.ranges
    intensities = msg.intensities

    # Print the range data
    for i, (range_val, intensity_val) in enumerate(zip(ranges, intensities)):
        print("Index: {}, Range: {}, Intensity: {}".format(i, range_val, intensity_val))

def main():
    rospy.init_node('hokuyo_listener', anonymous=True)

    # Set the topic name based on your Hokuyo scanner
    laser_topic = '/hokuyo_laser'
    
    # Subscribe to the laser scan topic
    rospy.Subscriber(laser_topic, LaserScan, laser_callback)

    # Spin to keep the script alive
    rospy.spin()

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass

