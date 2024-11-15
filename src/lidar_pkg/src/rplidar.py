#!/usr/bin/env python3

import rospy
from sensor_msgs.msg import LaserScan
from rplidar_ros.srv import *

class RPLidarReader:
    def __init__(self):
        rospy.init_node('rplidar_reader', anonymous=True)
        self.scan_publisher = rospy.Publisher('/scan', LaserScan, queue_size=10)
        self.rate = rospy.Rate(10)
        
    def run(self):
        rospy.wait_for_service('rplidar_node/start_motor')
        rospy.wait_for_service('rplidar_node/stop_motor')
        rospy.wait_for_service('rplidar_node/reset')
        start_motor = rospy.ServiceProxy('rplidar_node/start_motor', Empty)
        stop_motor = rospy.ServiceProxy('rplidar_node/stop_motor', Empty)
        reset = rospy.ServiceProxy('rplidar_node/reset', Empty)
        
        try:
            start_motor()
            rospy.sleep(2)
            
            while not rospy.is_shutdown():
                scan_data = self.get_scan_data()
                self.publish_scan(scan_data)
                self.rate.sleep()
                
        except rospy.ROSInterruptException:
            pass
        finally:
            stop_motor()
    
    def get_scan_data(self):
        rospy.wait_for_service('rplidar_node/get_scan')
        get_scan = rospy.ServiceProxy('rplidar_node/get_scan', GetRplidarScan)
        response = get_scan()
        return response.scan
    
    def publish_scan(self, scan_data):
        scan_msg = LaserScan()
        scan_msg.header.stamp = rospy.Time.now()
        scan_msg.header.frame_id = 'laser_frame'
        scan_msg.angle_min = scan_data.angle_min
        scan_msg.angle_max = scan_data.angle_max
        scan_msg.angle_increment = scan_data.angle_increment
        scan_msg.time_increment = scan_data.time_increment
        scan_msg.scan_time = scan_data.scan_time
        scan_msg.range_min = scan_data.range_min
        scan_msg.range_max = scan_data.range_max
        scan_msg.ranges = scan_data.ranges
        scan_msg.intensities = scan_data.intensities
        
        self.scan_publisher.publish(scan_msg)

if __name__ == '__main__':
    try:
        rplidar_reader = RPLidarReader()
        rplidar_reader.run()
    except rospy.ROSInterruptException:
        pass

