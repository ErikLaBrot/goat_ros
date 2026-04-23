#include <memory>

#include "goat_teleop/goat_joy.hpp"
#include "rclcpp/rclcpp.hpp"

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<goat_teleop::GoatJoy>());
  rclcpp::shutdown();
  return 0;
}
