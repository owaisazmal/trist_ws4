#!/usr/bin/env python3

import rospy
from std_msgs.msg import Int64
from geometry_msgs.msg import Twist, Pose, Point
from nav_msgs.msg import Odometry
from math import sin, cos

class OdometryCalculator:
    def __init__(self):
        rospy.init_node('odometry_calculator')
        self.encoder_sub_left = rospy.Subscriber('/left_encoder_ticks', Int64, self.left_encoder_callback)
        self.encoder_sub_right = rospy.Subscriber('/right_encoder_ticks', Int64, self.right_encoder_callback)
        self.odom_pub = rospy.Publisher('/odom', Odometry, queue_size=10)
        self.previous_left_ticks = 0
        self.previous_right_ticks = 0
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        self.last_time = rospy.Time.now()

    def left_encoder_callback(self, msg):
        left_ticks = msg.data
        left_delta_ticks = left_ticks - self.previous_left_ticks
        self.previous_left_ticks = left_ticks
        # Calculate left wheel displacement based on encoder ticks

    def right_encoder_callback(self, msg):
        right_ticks = msg.data
        right_delta_ticks = right_ticks - self.previous_right_ticks
        self.previous_right_ticks = right_ticks
        # Calculate right wheel displacement based on encoder ticks

    def calculate_odometry(self):
        # Calculate odometry here
        current_time = rospy.Time.now()
        dt = (current_time - self.last_time).to_sec()
        self.last_time = current_time

        # Calculate new x, y, theta based on wheel displacements

        # Populate Odometry message
        odom_msg = Odometry()
        odom_msg.header.stamp = current_time
        odom_msg.header.frame_id = "odom"
        odom_msg.child_frame_id = "base_link"
        odom_msg.pose.pose.position = Point(self.x, self.y, 0)
        # Set orientation quaternion based on self.theta
        odom_msg.pose.pose.orientation.x = 0.0
        odom_msg.pose.pose.orientation.y = 0.0
        odom_msg.pose.pose.orientation.z = 0.0
        odom_msg.pose.pose.orientation.w = 1.0
        odom_msg.twist.twist.linear.x = 0.0
        odom_msg.twist.twist.linear.y = 0.0
        odom_msg.twist.twist.angular.z = 0.0

        # Publish odometry message
        self.odom_pub.publish(odom_msg)

    def run(self):
        rate = rospy.Rate(30)  # 30 Hz
        while not rospy.is_shutdown():
            self.calculate_odometry()
            rate.sleep()

if __name__ == '__main__':
    try:
        odometry_calculator = OdometryCalculator()
        odometry_calculator.run()
    except rospy.ROSInterruptException:
        pass

