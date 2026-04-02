#include "goat_vesc_ros/vesc_node.hpp"

#include "rclcpp/rclcpp.hpp"

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);
  auto node = std::make_shared<goat_vesc_ros::VescNode>();
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}
