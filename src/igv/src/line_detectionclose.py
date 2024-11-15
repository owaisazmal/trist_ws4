#!/usr/bin/env python3
import rospy
from sensor_msgs.msg import Image, CameraInfo, PointCloud2, PointField
from cv_bridge import CvBridge
import cv2
import numpy as np

class WhiteObjectFilter:
    def __init__(self):
        rospy.init_node('white_object_filter', anonymous=True)
        self.bridge = CvBridge()
        self.image_sub_color = rospy.Subscriber("/mobile_robot/color/image_raw", Image, self.image_callback_color)
        self.image_sub_depth = rospy.Subscriber("/mobile_robot/depth/image_raw", Image, self.image_callback_depth)
        self.camera_info_sub_depth = rospy.Subscriber("/mobile_robot/depth/camera_info", CameraInfo, self.camera_info_callback_depth)
        self.camera_info_sub_color = rospy.Subscriber("/mobile_robot/color/camera_info", CameraInfo, self.camera_info_callback_color)
        self.fx_depth = None
        self.fy_depth = None
        self.cx_depth = None
        self.cy_depth = None
        self.fx_color = None
        self.fy_color = None
        self.cx_color = None
        self.cy_color = None
        self.depth_image = None
        self.color_image = None
        self.pc_pub = rospy.Publisher("/mobile_robot/depth/points", PointCloud2, queue_size=10)
        self.offset_x = .2
        self.offset_y = 0
        self.offset_z = 0
        self.rotation_angle = 0.2

    def camera_info_callback_depth(self, msg):
        self.fx_depth = msg.K[0]
        self.fy_depth = msg.K[4]
        self.cx_depth = msg.K[2]
        self.cy_depth = msg.K[5]

    def camera_info_callback_color(self, msg):
        self.fx_color = msg.K[0]
        self.fy_color = msg.K[4]
        self.cx_color = msg.K[2]
        self.cy_color = msg.K[5]

    def image_callback_color(self, msg):
        try:
            self.color_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        except Exception as e:
            print(e)
            return
        self.process_images()

    def image_callback_depth(self, msg):
        try:
            self.depth_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding="passthrough")
        except Exception as e:
            print(e)
            return
        self.process_images()

    def process_images(self):
        if self.color_image is not None and self.depth_image is not None:
            contours, dilated_image = self.detect_white_objects(self.color_image)
            white_point_cloud = self.convert_to_point_cloud(contours, self.depth_image)
            white_point_cloud = self.offset_point_cloud(white_point_cloud)
            white_point_cloud = self.rotate_point_cloud(white_point_cloud)
            self.pc_pub.publish(white_point_cloud)
            self.show_contours_image(self.color_image, contours)
            self.show_dilated_image(dilated_image)

    def detect_white_objects(self, cv_image):
        gray_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        adaptive_thresh = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        hsv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
        lower_white = np.array([0, 0, 200], dtype=np.uint8)
        upper_white = np.array([180, 40, 255], dtype=np.uint8)
        mask = cv2.inRange(hsv_image, lower_white, upper_white)
        combined_mask = cv2.bitwise_and(adaptive_thresh, mask)
        kernel_size = 5
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        eroded_image = cv2.erode(combined_mask, kernel, iterations=1)
        dilated_image = cv2.dilate(eroded_image, kernel, iterations=2)
        contours, _ = cv2.findContours(dilated_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        filtered_contours = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if 1000 < area < 60000:
                rect = cv2.minAreaRect(contour)
                _, (width, height), angle = rect
                aspect_ratio = max(width, height) / min(width, height)
                hull = cv2.convexHull(contour)
                hull_area = cv2.contourArea(hull)
                solidity = float(area) / hull_area if hull_area > 0 else 0
                if 2 < aspect_ratio < 70 and 0.5 < solidity < 1.0:
                    filtered_contours.append(contour)
        return filtered_contours, dilated_image

    def convert_to_point_cloud(self, contours, depth_image):
        fields = [
            PointField('x', 0, PointField.FLOAT32, 1),
            PointField('y', 4, PointField.FLOAT32, 1),
            PointField('z', 8, PointField.FLOAT32, 1),
        ]
        points = []
        for contour in contours:
            for point in contour:
                x, y = point[0]
                if depth_image is not None:
                    if 0 <= x < depth_image.shape[1] and 0 <= y < depth_image.shape[0]:
                        Z = depth_image[int(y), int(x)] / 1000.0
                        if 0.5 < Z < 1.5:
                            X = (x - self.cx_depth) * Z / self.fx_depth
                            Y = (y - self.cy_depth) * Z / self.fy_depth
                            points.append([X, Y, Z])

        cloud_msg = PointCloud2(
            header=rospy.Header(frame_id="camera_depth_optical_frame"),
            height=1,
            width=len(points),
            fields=fields,
            is_bigendian=False,
            point_step=12,
            row_step=len(points) * 12,
            data=np.asarray(points).astype(np.float32).tobytes(),
            is_dense=False
        )
        return cloud_msg

    def offset_point_cloud(self, point_cloud):
        offset_points = []
        for data_byte in range(0, len(point_cloud.data), 12):
            x, y, z = np.frombuffer(point_cloud.data[data_byte:data_byte + 12], dtype=np.float32)
            x += self.offset_x
            y += self.offset_y
            z += self.offset_z
            offset_points.extend([x, y, z])
        point_cloud.data = np.array(offset_points, dtype=np.float32).tobytes()
        return point_cloud

    def rotate_point_cloud(self, point_cloud):
        rotation_matrix = np.array([[np.cos(self.rotation_angle), -np.sin(self.rotation_angle), 0],
                                     [np.sin(self.rotation_angle), np.cos(self.rotation_angle), 0],
                                     [0, 0, 1]])
        points = np.frombuffer(point_cloud.data, dtype=np.float32).reshape(-1, 3)
        rotated_points = np.dot(points, rotation_matrix.T)
        point_cloud.data = rotated_points.astype(np.float32).tobytes()
        return point_cloud

    def show_contours_image(self, cv_image, contours):
        image_with_contours = cv_image.copy()
        cv2.drawContours(image_with_contours, contours, -1, (0, 0, 255), 2)
        cv2.imshow('Contours', image_with_contours)
        cv2.waitKey(1)

    def show_dilated_image(self, dilated_image):
        cv2.imshow('Dilated Image', dilated_image)
        cv2.waitKey(1)

def main():
    white_object_filter = WhiteObjectFilter()
    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("Shutting down")
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()

