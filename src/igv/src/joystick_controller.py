#!/usr/bin/env python3
import rospy
from geometry_msgs.msg import Twist
from std_msgs.msg import UInt8MultiArray

class VelocityController():
    def __init__(self):
        self.max_linear_velocity = 1.0
        self.max_angular_velocity = 1.0
        self.wheel_distance = 0.771

        self.min_PWM = 0  # Minimum PWM value
        self.PWM_slope = 150  # Increase PWM slope

        rospy.Subscriber("/cmd_vel", Twist, self.velocityCallback)
        self.velPub = rospy.Publisher("/cmd_vel_PWM", UInt8MultiArray, queue_size=10)
    
    def velocityCallback(self, msg):
        x, z = msg.linear.x, msg.angular.z
        right_wheel_speed = x + (self.wheel_distance * z)/2
        left_wheel_speed = x - (self.wheel_distance * z)/2

        self.getPWM(right_wheel_speed, left_wheel_speed)

    def getPWM(self, right_wheel_speed, left_wheel_speed):
        right_PWM = max(int(self.min_PWM + self.PWM_slope * abs(right_wheel_speed)), self.min_PWM)
        left_PWM = max(int(self.min_PWM + self.PWM_slope * abs(left_wheel_speed)), self.min_PWM)

        # Map angular.z to direction (positive/negative) for motor control
        right_direction = int(right_wheel_speed > 0)
        left_direction = int(left_wheel_speed > 0)

        cmd_vel_msg = UInt8MultiArray()
        cmd_vel_msg.data = [right_PWM, left_PWM, right_direction, left_direction]

        self.velPub.publish(cmd_vel_msg)

if __name__ == "__main__":
    rospy.init_node("joystick_controller")

    try:
        controller = VelocityController()
        rospy.spin()

    except rospy.ROSInterruptException:
        pass

