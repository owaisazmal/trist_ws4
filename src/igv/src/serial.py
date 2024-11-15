#!/usr/bin/env python3
import rospy
from geometry_msgs.msg import Twist
from std_msgs.msg import UInt8MultiArray

class VelocityController():
    def __init__(self):
        self.max_linear_velocity = 1.0
        self.max_angular_velocity = 1.0
        self.wheel_distance = 0.771

        self.min_PWM = 20
        self.PWM_slope = 200

        rospy.Subscriber("/cmd_vel", Twist, self.velocityCallback)
        self.velPub = rospy.Publisher("/cmd_vel_PWM", UInt8MultiArray, queue_size=10)
    
    def velocityCallback(self, msg):
        self.velMsg = msg   
        x, z = self.velMsg.linear.x, self.velMsg.angular.z
        right_wheel_speed = x + (self.wheel_distance * z)/2
        left_wheel_speed = x - (self.wheel_distance * z)/2

        # print(right_wheel_speed, left_wheel_speed)

        self.getPWM(right_wheel_speed, left_wheel_speed)

    
    def getPWM(self, right_wheel_speed, left_wheel_speed):
        right_PWM = int(self.min_PWM + self.PWM_slope * abs(right_wheel_speed))
        left_PWM = int(self.min_PWM + self.PWM_slope * abs(left_wheel_speed))

        cmd_vel_msg = UInt8MultiArray()
        cmd_vel_msg.data = [right_PWM, left_PWM, int(right_wheel_speed > 0), int(left_wheel_speed > 0)]

        self.velPub.publish(cmd_vel_msg)
        


if __name__ == "__main__":
    rospy.init_node("joystick_controller")

    try:
        controller = VelocityController()
        rospy.spin()

    except rospy.ROSInterruptException:
        pass
