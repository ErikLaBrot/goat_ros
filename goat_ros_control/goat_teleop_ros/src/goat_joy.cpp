#include "goat_teleop/goat_joy.hpp"

#include <algorithm>
#include <chrono>
#include <cmath>
#include <functional>
#include <memory>
#include <stdexcept>

namespace goat_teleop {

GoatJoy::GoatJoy(const rclcpp::NodeOptions &options)
    : Node("goat_joy", options) {
  throttle_axis_ = this->declare_parameter<int>("throttle_axis", 1);
  steering_axis_ = this->declare_parameter<int>("steering_axis", 3);
  enable_button_ = this->declare_parameter<int>("enable_button", 4);
  command_scale_ = this->declare_parameter<double>("command_scale", 0.10);
  invert_throttle_ = this->declare_parameter<bool>("invert_throttle", false);
  invert_steering_ = this->declare_parameter<bool>("invert_steering", false);
  servo_center_ = this->declare_parameter<double>("servo_center", 0.5);
  servo_amplitude_ = this->declare_parameter<double>("servo_amplitude", 0.1);
  deadband_ = this->declare_parameter<double>("deadband", 0.05);
  steer_tau_s_ = this->declare_parameter<double>("steer_tau_s", 0.12);
  throttle_tau_s_ = this->declare_parameter<double>("throttle_tau_s", 0.18);
  max_steer_rate_ = this->declare_parameter<double>("max_steer_rate", 3.0);
  max_throttle_rate_ =
      this->declare_parameter<double>("max_throttle_rate", 2.0);
  publish_epsilon_ = this->declare_parameter<double>("publish_epsilon", 0.001);
  control_rate_hz_ = this->declare_parameter<double>("control_rate_hz", 50.0);
  command_topic_ =
      this->declare_parameter<std::string>("command_topic", "cmd/vesc");

  if (command_scale_ < 0.0) {
    throw std::invalid_argument("command_scale must be non-negative");
  }
  if (servo_center_ < 0.0 || servo_center_ > 1.0) {
    throw std::invalid_argument("servo_center must be within [0.0, 1.0]");
  }
  if (servo_amplitude_ < 0.0) {
    throw std::invalid_argument("servo_amplitude must be non-negative");
  }
  if (!std::isfinite(deadband_) || deadband_ < 0.0 || deadband_ >= 1.0) {
    throw std::invalid_argument("deadband must be within [0.0, 1.0)");
  }
  if (!std::isfinite(steer_tau_s_) || steer_tau_s_ < 0.0) {
    throw std::invalid_argument("steer_tau_s must be non-negative");
  }
  if (!std::isfinite(throttle_tau_s_) || throttle_tau_s_ < 0.0) {
    throw std::invalid_argument("throttle_tau_s must be non-negative");
  }
  if (!std::isfinite(max_steer_rate_) || max_steer_rate_ < 0.0) {
    throw std::invalid_argument("max_steer_rate must be non-negative");
  }
  if (!std::isfinite(max_throttle_rate_) || max_throttle_rate_ < 0.0) {
    throw std::invalid_argument("max_throttle_rate must be non-negative");
  }
  if (!std::isfinite(publish_epsilon_) || publish_epsilon_ < 0.0) {
    throw std::invalid_argument("publish_epsilon must be non-negative");
  }
  if (!std::isfinite(control_rate_hz_) || control_rate_hz_ <= 0.0) {
    throw std::invalid_argument("control_rate_hz must be positive");
  }
  if (command_topic_.empty()) {
    throw std::invalid_argument("command_topic must not be empty");
  }
  last_published_servo_position_ = servo_center_;

  command_publisher_ =
      this->create_publisher<goat_vesc_ros::msg::VescControlCommand>(
          command_topic_, 10);
  joy_subscription_ = this->create_subscription<sensor_msgs::msg::Joy>(
      "/joy", rclcpp::SensorDataQoS(),
      std::bind(&GoatJoy::joyCallback, this, std::placeholders::_1));
  control_timer_ = this->create_wall_timer(
      std::chrono::duration<double>(1.0 / control_rate_hz_),
      std::bind(&GoatJoy::controlTimerCallback, this));
}

void GoatJoy::joyCallback(const sensor_msgs::msg::Joy::SharedPtr msg) {
  latest_throttle_input_ = getAxisValue(*msg, throttle_axis_, invert_throttle_);
  latest_steering_input_ = getAxisValue(*msg, steering_axis_, invert_steering_);
  enabled_ = isButtonPressed(*msg, enable_button_);
}

void GoatJoy::controlTimerCallback() {
  const auto now = std::chrono::steady_clock::now();
  double dt_s = 1.0 / control_rate_hz_;
  if (have_last_control_time_) {
    dt_s = std::chrono::duration<double>(now - last_control_time_).count();
  }
  last_control_time_ = now;
  have_last_control_time_ = true;

  if (!enabled_) {
    resetConditionedState();
    const bool should_publish_neutral =
        was_enabled_ || shouldPublish(0.0, servo_center_);
    was_enabled_ = false;
    if (should_publish_neutral) {
      publishCommand(0.0, servo_center_);
    }
    return;
  }

  was_enabled_ = true;
  const double throttle_target = applyDeadband(latest_throttle_input_);
  const double steering_target = applyDeadband(latest_steering_input_);
  conditioned_throttle_ =
      conditionAxis(throttle_target, conditioned_throttle_, throttle_tau_s_,
                    max_throttle_rate_, dt_s);
  conditioned_steering_ = conditionAxis(steering_target, conditioned_steering_,
                                        steer_tau_s_, max_steer_rate_, dt_s);

  if (throttle_target == 0.0 &&
      std::abs(conditioned_throttle_ * command_scale_) <= publish_epsilon_) {
    conditioned_throttle_ = 0.0;
  }
  if (steering_target == 0.0 &&
      std::abs(conditioned_steering_ * servo_amplitude_) <= publish_epsilon_) {
    conditioned_steering_ = 0.0;
  }

  double command = std::clamp(conditioned_throttle_ * command_scale_,
                              -command_scale_, command_scale_);
  double servo_position = std::clamp(
      servo_center_ + (conditioned_steering_ * servo_amplitude_), 0.0, 1.0);

  if (std::abs(command) <= publish_epsilon_) {
    command = 0.0;
  }
  if (std::abs(servo_position - servo_center_) <= publish_epsilon_) {
    servo_position = servo_center_;
  }

  publishCommand(command, servo_position);
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

double GoatJoy::applyDeadband(double value) const {
  return std::abs(value) <= deadband_ ? 0.0 : value;
}

double GoatJoy::conditionAxis(double target, double current, double tau_s,
                              double max_rate, double dt_s) const {
  double filtered = target;
  if (tau_s > 0.0) {
    const double alpha = dt_s / (tau_s + dt_s);
    filtered = current + (alpha * (target - current));
  }

  if (max_rate <= 0.0) {
    return filtered;
  }

  const double max_delta = max_rate * dt_s;
  return std::clamp(filtered, current - max_delta, current + max_delta);
}

void GoatJoy::resetConditionedState() {
  conditioned_throttle_ = 0.0;
  conditioned_steering_ = 0.0;
}

bool GoatJoy::shouldPublish(double command, double servo_position) const {
  if (!have_published_command_) {
    return true;
  }

  return std::abs(command - last_published_command_) > publish_epsilon_ ||
         std::abs(servo_position - last_published_servo_position_) >
             publish_epsilon_;
}

void GoatJoy::publishCommand(double command, double servo_position) {
  goat_vesc_ros::msg::VescControlCommand message;
  message.stamp = this->get_clock()->now();
  message.drive_mode = goat_vesc_ros::msg::VescControlCommand::MODE_DUTY;
  message.drive_value = static_cast<float>(command);
  message.servo_position = static_cast<float>(servo_position);
  command_publisher_->publish(message);
  last_published_command_ = command;
  last_published_servo_position_ = servo_position;
  have_published_command_ = true;
}

} // namespace goat_teleop

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<goat_teleop::GoatJoy>());
  rclcpp::shutdown();
  return 0;
}
