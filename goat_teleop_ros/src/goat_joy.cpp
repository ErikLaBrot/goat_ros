#include "goat_teleop/goat_joy.hpp"

#include <functional>
#include <memory>

namespace goat_teleop
{

GoatJoy::GoatJoy(const rclcpp::NodeOptions & options)
: Node("goat_joy", options)
{
  throttle_axis_ = this->declare_parameter<int>("throttle_axis", 1);
  steering_axis_ = this->declare_parameter<int>("steering_axis", 0);
  enable_button_ = this->declare_parameter<int>("enable_button", 4);
  throttle_scale_ = this->declare_parameter<double>("throttle_scale", 1.0);
  steering_scale_ = this->declare_parameter<double>("steering_scale", 1.0);
  invert_throttle_ = this->declare_parameter<bool>("invert_throttle", false);
  invert_steering_ = this->declare_parameter<bool>("invert_steering", false);

  cmd_vel_publisher_ = this->create_publisher<geometry_msgs::msg::Twist>("/cmd_vel", 10);
  joy_subscription_ = this->create_subscription<sensor_msgs::msg::Joy>(
    "/joy",
    rclcpp::SensorDataQoS(),
    std::bind(&GoatJoy::joyCallback, this, std::placeholders::_1));
}

void GoatJoy::joyCallback(const sensor_msgs::msg::Joy::SharedPtr msg)
{
  double throttle = 0.0;
  double steering = 0.0;

  if (isButtonPressed(*msg, enable_button_)) {
    throttle = getAxisValue(*msg, throttle_axis_, invert_throttle_) * throttle_scale_;
    steering = getAxisValue(*msg, steering_axis_, invert_steering_) * steering_scale_;
  }

  publishCommand(throttle, steering);
}

double GoatJoy::getAxisValue(const sensor_msgs::msg::Joy & msg, int index, bool invert) const
{
  if (index < 0 || static_cast<std::size_t>(index) >= msg.axes.size()) {
    return 0.0;
  }

  double value = msg.axes[static_cast<std::size_t>(index)];
  return invert ? -value : value;
}

bool GoatJoy::isButtonPressed(const sensor_msgs::msg::Joy & msg, int index) const
{
  if (index < 0 || static_cast<std::size_t>(index) >= msg.buttons.size()) {
    return false;
  }

  return msg.buttons[static_cast<std::size_t>(index)] != 0;
}

void GoatJoy::publishCommand(double throttle, double steering)
{
  geometry_msgs::msg::Twist command;
  command.linear.x = throttle;
  command.angular.z = steering;
  cmd_vel_publisher_->publish(command);
}

}  // namespace goat_teleop

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<goat_teleop::GoatJoy>());
  rclcpp::shutdown();
  return 0;
}
