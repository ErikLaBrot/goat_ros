#include "goat_ros_laser/laser_node.hpp"

#include "rclcpp/rclcpp.hpp"

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<goat_ros_laser::LaserNode>());
  rclcpp::shutdown();
  return 0;
}
