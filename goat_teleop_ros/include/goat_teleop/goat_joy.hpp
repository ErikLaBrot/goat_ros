#ifndef GOAT_TELEOP__GOAT_JOY_HPP_
#define GOAT_TELEOP__GOAT_JOY_HPP_

#include <geometry_msgs/msg/twist.hpp>
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/joy.hpp>

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
  void publishCommand(double throttle, double steering);

  int throttle_axis_;
  int steering_axis_;
  int enable_button_;
  double throttle_scale_;
  double steering_scale_;
  bool invert_throttle_;
  bool invert_steering_;

  rclcpp::Subscription<sensor_msgs::msg::Joy>::SharedPtr joy_subscription_;
  rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr cmd_vel_publisher_;
};

}  // namespace goat_teleop

#endif  // GOAT_TELEOP__GOAT_JOY_HPP_
