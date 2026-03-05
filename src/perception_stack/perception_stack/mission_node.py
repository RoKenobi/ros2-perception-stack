import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point
from geometry_msgs.msg import Twist

class MissionNode(Node):
    def __init__(self):
        super().__init__('mission_node')
        self.subscription = self.create_subscription(Point, '/object/position', self.pos_callback, 10)
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.publish_cmd)
        self.target_x = 0.0
        self.found = False

    def pos_callback(self, msg):
        self.target_x = msg.x
        self.found = (msg.z == 1.0)

    def publish_cmd(self):
        twist = Twist()
        if not self.found:
            twist.linear.x = 0.0
            twist.angular.z = 0.0
            self.get_logger().info("Object Lost -> STOP")
        else:
            if self.target_x < -0.2:
                twist.angular.z = 0.5
                self.get_logger().info("Object Left -> TURN LEFT")
            elif self.target_x > 0.2:
                twist.angular.z = -0.5
                self.get_logger().info("Object Right -> TURN RIGHT")
            else:
                twist.linear.x = 0.5
                self.get_logger().info("Object Center -> FORWARD")
        self.cmd_pub.publish(twist)

def main():
    rclpy.init()
    node = MissionNode()
    rclpy.spin(node)
    node.destroy_node()

if __name__ == '__main__':
    main()
