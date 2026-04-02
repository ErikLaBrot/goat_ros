#include "goat_teleop/goat_joy.hpp"

#include <algorithm>
#include <functional>
#include <memory>
#include <stdexcept>

namespace goat_teleop {

GoatJoy::GoatJoy(const rclcpp::NodeOptions &options)
    : Node("goat_joy", options) {
  throttle_axis_ = this->declare_parameter<int>("throttle_axis", 1);
  enable_button_ = this->declare_parameter<int>("enable_button", 4);
  command_scale_ = this->declare_parameter<double>("command_scale", 0.10);
  invert_throttle_ = this->declare_parameter<bool>("invert_throttle", false);
  servo_position_ = this->declare_parameter<double>("servo_position", 0.5);
  command_topic_ =
      this->declare_parameter<std::string>("command_topic", "cmd/vesc");

  if (command_scale_ < 0.0) {
    throw std::invalid_argument("command_scale must be non-negative");
  }
  if (servo_position_ < 0.0 || servo_position_ > 1.0) {
    throw std::invalid_argument("servo_position must be within [0.0, 1.0]");
  }
  if (command_topic_.empty()) {
    throw std::invalid_argument("command_topic must not be empty");
  }

  command_publisher_ =
      this->create_publisher<goat_vesc_ros::msg::VescControlCommand>(
          command_topic_, 10);
  joy_subscription_ = this->create_subscription<sensor_msgs::msg::Joy>(
      "/joy", rclcpp::SensorDataQoS(),
      std::bind(&GoatJoy::joyCallback, this, std::placeholders::_1));
}

void GoatJoy::joyCallback(const sensor_msgs::msg::Joy::SharedPtr msg) {
  double command = 0.0;

  if (isButtonPressed(*msg, enable_button_)) {
    const double throttle =
        getAxisValue(*msg, throttle_axis_, invert_throttle_);
    command =
        std::clamp(throttle * command_scale_, -command_scale_, command_scale_);
  }

  publishCommand(command);
}

double GoatJoy::getAxisValue(const sensor_msgs::msg::Joy &msg, int index,
                             bool invert) const {
  if (index < 0 || static_cast<std::size_t>(index) >= msg.axes.size()) {
    return 0.0;
  }

  double value = msg.axes[static_cast<std::size_t>(index)];
  return invert ? -value : value;
}

bool GoatJoy::isButtonPressed(const sensor_msgs::msg::Joy &msg,
                              int index) const {
  if (index < 0 || static_cast<std::size_t>(index) >= msg.buttons.size()) {
    return false;
  }

  return msg.buttons[static_cast<std::size_t>(index)] != 0;
}

void GoatJoy::publishCommand(double command) {
  goat_vesc_ros::msg::VescControlCommand message;
  message.stamp = this->get_clock()->now();
  message.drive_mode = goat_vesc_ros::msg::VescControlCommand::MODE_DUTY;
  message.drive_value = static_cast<float>(command);
  message.servo_position = static_cast<float>(servo_position_);
  command_publisher_->publish(message);
}

} // namespace goat_teleop

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<goat_teleop::GoatJoy>());
  rclcpp::shutdown();
  return 0;
}
