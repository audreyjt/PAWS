#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2


class CameraSensorNode(Node):
    def __init__(self):
        super().__init__("camera_sensor")

        self.declare_parameter("camera_index", 0)
        self.declare_parameter("publish_rate_hz", 15.0)

        camera_index = self.get_parameter("camera_index").value
        rate_hz = self.get_parameter("publish_rate_hz").value

        self.publisher_ = self.create_publisher(Image, "camera/image_raw", 10)
        self.bridge = CvBridge()

        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            self.get_logger().error(
                f"Failed to open camera at index {camera_index}. "
            )

        self.timer = self.create_timer(1.0 / rate_hz, self.timer_callback)
        self.get_logger().info("camera sensor node has been started")

    def timer_callback(self):
        ret, frame = self.cap.read()
        if not ret:
            self.get_logger().warn("Failed to read frame from camera")
            return

        msg = self.bridge.cv2_to_imgmsg(frame, encoding="bgr8")
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "camera_frame"
        self.publisher_.publish(msg)

    def destroy_node(self):
        if self.cap.isOpened():
            self.cap.release()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = CameraSensorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()