#!/usr/bin/env python3

import rospy
from geometry_msgs.msg import Twist  # Import Twist message type
from std_msgs.msg import Empty

# Declare led_pub as a global variable
led_pub = None

def cmd_vel_callback(msg):
    global led_pub  # Access the global variable
    # Your logic to determine LED state based on cmd_vel message
    # For demonstration, let's assume we want to flash LED when linear velocity is non-zero
    if msg.linear.x != 0.0:
        # Publish a message to the /led topic
        led_pub.publish(Empty())
        rospy.loginfo("Published message to /led topic (flashing LED)")

def light_control():
    rospy.init_node('light_controller')  # Initialize ROS node

    # Subscribe to the cmd_vel topic
    rospy.Subscriber('/cmd_vel', Twist, cmd_vel_callback)

    # Define the publisher for the LED topic as a global variable
    global led_pub
    led_pub = rospy.Publisher('/led', Empty, queue_size=10)

    rospy.spin()  # Keep the node running

if __name__ == '__main__':
    try:
        light_control()
    except rospy.ROSInterruptException:
        pass

