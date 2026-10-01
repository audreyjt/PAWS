#!/usr/bin/env python3

# import rclpy
# from rclpy.node import Node

# class LiDARSensorNode(Node):
#     def __init__(self):
#         super().__init__("lidar_sensor")
#         self.get_logger().info("lidar sensor node has been started")
        

# def main(args=None):
#     rclpy.init(args=args)
#     node = LiDARSensorNode()
#     rclpy.spin(node)
#     rclpy.shutdown()

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


class LiDARSensorNode(Node):
    def __init__(self):
        super().__init__("lidar_sensor")
        self.subscription = self.create_subscription(
            LaserScan,
            "scan",
            self.scan_callback,
            10
        )
        self.get_logger().info("lidar sensor node has been started")

    def scan_callback(self, msg: LaserScan):
        # Filter out invalid readings (0.0 or inf/nan) before finding the closest point
        valid_ranges = [
            r for r in msg.ranges
            if r > msg.range_min and r < msg.range_max
        ]

        if not valid_ranges:
            self.get_logger().warn("No valid LiDAR readings in this scan")
            return

        min_distance = min(valid_ranges)
        min_index = msg.ranges.index(min_distance)
        angle = msg.angle_min + min_index * msg.angle_increment

        self.get_logger().info(
            f"Closest obstacle: {min_distance:.2f} m at {angle:.2f} rad"
        )

        # Simple obstacle warning threshold (adjust as needed)
        if min_distance < 0.3:
            self.get_logger().warn(
                f"Obstacle within 0.3m! Distance: {min_distance:.2f} m"
            )


def main(args=None):
    rclpy.init(args=args)
    node = LiDARSensorNode()
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