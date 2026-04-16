/**
 * @file goat_joy.hpp
 * @brief Public declaration for the GOAT joystick teleop node.
 */

#ifndef GOAT_TELEOP__GOAT_JOY_HPP_
#define GOAT_TELEOP__GOAT_JOY_HPP_

#include <chrono>
#include <string>

#include <goat_vesc_ros/msg/vesc_control_command.hpp>
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/joy.hpp>

namespace goat_teleop {

/**
 * @brief ROS node that converts joystick input into VESC control commands.
 *
 * The node consumes `sensor_msgs/msg/Joy` input, applies the configured axis
 * mapping and scaling, and publishes `goat_vesc_ros/msg/VescControlCommand`
 * messages for manual teleoperation.
 */
class GoatJoy : public rclcpp::Node {
public:
  /**
   * @brief Construct the joystick teleop node with ROS node options.
   *
   * @param options ROS node options used during node creation.
   */
  explicit GoatJoy(const rclcpp::NodeOptions &options = rclcpp::NodeOptions());

private:
  void joyCallback(const sensor_msgs::msg::Joy::SharedPtr msg);
  void controlTimerCallback();
  double getAxisValue(const sensor_msgs::msg::Joy &msg, int index,
                      bool invert) const;
  bool isButtonPressed(const sensor_msgs::msg::Joy &msg, int index) const;
  double applyDeadband(double value) const;
  double conditionAxis(double target, double current, double tau_s,
                       double max_rate, double dt_s) const;
  void resetConditionedState();
  bool shouldPublish(double command, double servo_position) const;
  void publishCommand(double command, double servo_position);

  int throttle_axis_;
  int steering_axis_;
  int enable_button_;
  double command_scale_;
  bool invert_throttle_;
  bool invert_steering_;
  double servo_center_;
  double servo_amplitude_;
  double deadband_;
  double steer_tau_s_;
  double throttle_tau_s_;
  double max_steer_rate_;
  double max_throttle_rate_;
  double publish_epsilon_;
  double control_rate_hz_;
  std::string command_topic_;

  bool enabled_{false};
  bool was_enabled_{false};
  double latest_throttle_input_{0.0};
  double latest_steering_input_{0.0};
  double conditioned_throttle_{0.0};
  double conditioned_steering_{0.0};
  bool have_last_control_time_{false};
  std::chrono::steady_clock::time_point last_control_time_;
  bool have_published_command_{false};
  double last_published_command_{0.0};
  double last_published_servo_position_{0.0};

  rclcpp::Subscription<sensor_msgs::msg::Joy>::SharedPtr joy_subscription_;
  rclcpp::TimerBase::SharedPtr control_timer_;
  rclcpp::Publisher<goat_vesc_ros::msg::VescControlCommand>::SharedPtr
      command_publisher_;
};

} // namespace goat_teleop

#endif // GOAT_TELEOP__GOAT_JOY_HPP_
