import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Point
from cv_bridge import CvBridge
import cv2
import numpy as np

class KalmanFilter:
    def __init__(self):
        self.kf = cv2.KalmanFilter(4, 2)
        self.kf.measurementMatrix = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], np.float32)
        self.kf.transitionMatrix = np.array([[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32) * 0.03
        self.kf.measurementNoiseCov = np.array([[1, 0], [0, 1]], np.float32) * 0.5
        self.first = True

    def update(self, x, y):
        if self.first:
            self.kf.statePost[0] = x
            self.kf.statePost[1] = y
            self.first = False
        self.kf.correct(np.array([[np.float32(x)], [np.float32(y)]]))
        prediction = self.kf.predict()
        return int(prediction[0]), int(prediction[1])

class TrackerNode(Node):
    def __init__(self):
        super().__init__('tracker_node')
        self.subscription = self.create_subscription(Image, '/camera/image_raw', self.image_callback, 10)
        self.publisher = self.create_publisher(Point, '/object/position', 10)
        self.bridge = CvBridge()
        self.kf = KalmanFilter()

    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_red = np.array([0, 70, 50])
        upper_red = np.array([10, 255, 255])
        mask = cv2.inRange(hsv, lower_red, upper_red)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            c = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(c)
            center_x, center_y = x + w//2, y + h//2
            kf_x, kf_y = self.kf.update(center_x, center_y)
            h_img, w_img, _ = frame.shape
            norm_x = (kf_x - w_img/2) / (w_img/2)
            norm_y = (kf_y - h_img/2) / (h_img/2)
            pos_msg = Point()
            pos_msg.x = norm_x
            pos_msg.y = norm_y
            pos_msg.z = 1.0
            self.publisher.publish(pos_msg)
        else:
            pos_msg = Point()
            pos_msg.x = 0.0
            pos_msg.y = 0.0
            pos_msg.z = 0.0
            self.publisher.publish(pos_msg)

def main():
    rclpy.init()
    node = TrackerNode()
    rclpy.spin(node)
    node.destroy_node()

if __name__ == '__main__':
    main()
