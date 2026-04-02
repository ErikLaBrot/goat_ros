#ifndef GOAT_TELEOP__GOAT_JOY_HPP_
#define GOAT_TELEOP__GOAT_JOY_HPP_

#include <string>

#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/joy.hpp>
#include <std_msgs/msg/float32.hpp>

namespace goat_teleop
{

class GoatJoy : public rclcpp::Node
{
public:
  explicit GoatJoy(const rclcpp::NodeOptions & options = rclcpp::NodeOptions());

private:
  void joyCallback(const sensor_msgs::msg::Joy::SharedPtr msg);
  double getAxisValue(const sensor_msgs::msg::Joy & msg, int index, bool invert) const;
  bool isButtonPressed(const sensor_msgs::msg::Joy & msg, int index) const;
  void publishCommand(double command);

  int throttle_axis_;
  int enable_button_;
  double command_scale_;
  bool invert_throttle_;
  std::string command_topic_;

  rclcpp::Subscription<sensor_msgs::msg::Joy>::SharedPtr joy_subscription_;
  rclcpp::Publisher<std_msgs::msg::Float32>::SharedPtr command_publisher_;
};

}  // namespace goat_teleop

#endif  // GOAT_TELEOP__GOAT_JOY_HPP_
