#!/usr/bin/env python3

import numpy as np
import rospy
import cv2
from cv_bridge import CvBridge
from sensor_msgs.msg import Image

def detect_white_lines(image_msg):
    # Convert ROS image message to OpenCV format
    cv_image = CvBridge().imgmsg_to_cv2(image_msg, desired_encoding='bgr8')

    # Convert image to grayscale
    gray_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

    # Apply adaptive thresholding to detect white regions on black background
    _, binary_image = cv2.threshold(gray_image, 220, 255, cv2.THRESH_BINARY)

    # Find contours in the binary image
    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter out small contours and approximate them to lines
    lines_image = np.zeros_like(cv_image)
    for contour in contours:
        if cv2.contourArea(contour) > 100:  # Filter out small contours
            # Fit a line to the contour
            vx, vy, x, y = cv2.fitLine(contour, cv2.DIST_L2, 0, 0.01, 0.01)
            slope = vy / vx if vx != 0 else np.inf

            # Calculate start and end points of the line
            x0 = int(x - 1000 * vx)
            y0 = int(y - 1000 * vy)
            x1 = int(x + 1000 * vx)
            y1 = int(y + 1000 * vy)

            # Draw the line on the output image
            cv2.line(lines_image, (x0, y0), (x1, y1), (0, 255, 0), 2)

    # Display the result
    cv2.imshow("White Lines Detection", lines_image)
    cv2.waitKey(1)

def image_callback(image_msg):
    # Detect white lines in the received image
    detect_white_lines(image_msg)

if __name__ == '__main__':
    rospy.init_node('white_lines_detection')

    # Initialize OpenCV window
    cv2.namedWindow("White Lines Detection", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("White Lines Detection", 800, 600)

    # Subscribe to camera image topic
    rospy.Subscriber('/mobile_robot/color/image_raw', Image, image_callback)

    # Initialize CV bridge
    CvBridge()

    # Start ROS node
    rospy.spin()

