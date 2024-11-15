#!/usr/bin/env python3

import rospy
from sensor_msgs.msg import LaserScan

def main():
    rospy.init_node('lidar_publisher', anonymous=True)

    # Set the correct topic name to publish your LiDAR scan data
    lidar_topic = '/lidar_scan'

    # Create a publisher for the LiDAR scan data
    lidar_pub = rospy.Publisher(lidar_topic, LaserScan, queue_size=10)

    # Create a LaserScan message
    scan_msg = LaserScan()

    # Populate the LaserScan message with dummy data
    scan_msg.header.stamp = rospy.Time.now()
    scan_msg.header.frame_id = "laser_link"
    scan_msg.angle_min = -1.570796
    scan_msg.angle_max = 1.570796
    scan_msg.angle_increment = 3.141592 / 360.0  # 1 degree increment
    scan_msg.time_increment = 0.0
    scan_msg.scan_time = 0.1
    scan_msg.range_min = 0.1
    scan_msg.range_max = 30.0
    scan_msg.ranges = [1.0] * 180  # Dummy range values

    # Publish the LaserScan message repeatedly
    rate = rospy.Rate(10)  # 10 Hz
    while not rospy.is_shutdown():
        scan_msg.header.stamp = rospy.Time.now()
        lidar_pub.publish(scan_msg)
        rate.sleep()

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass

