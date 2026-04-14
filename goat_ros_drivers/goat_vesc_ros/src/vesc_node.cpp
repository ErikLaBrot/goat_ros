// Copyright 2026 GOAT Maintainers

#include "goat_vesc_ros/vesc_node.hpp"

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <stdexcept>
#include <utility>

#include "builtin_interfaces/msg/time.hpp"
#include "rclcpp/qos.hpp"
#include "rclcpp/time.hpp"

namespace goat_vesc_ros
{

namespace
{

constexpr auto kDisconnectedWarnThrottle = 5000;
constexpr auto kReconnectWarnThrottle = 5000;

} // namespace

VescNode::VescNode(const rclcpp::NodeOptions & options)
: Node("goat_vesc_ros", options)
{
  declare_parameters();
  params_ = load_parameters();
  validate_parameters(params_);

  goat_vesc::VescConfig config;
  config.device_path = params_.device_path;
  config.baud = params_.baud;
  config.imu_poll_interval =
    std::chrono::milliseconds(params_.imu_poll_interval_ms);
  config.motor_poll_interval =
    std::chrono::milliseconds(params_.motor_poll_interval_ms);
  config.poll_response_timeout =
    std::chrono::milliseconds(params_.poll_response_timeout_ms);
  config.query_guard_window =
    std::chrono::milliseconds(params_.query_guard_window_ms);
  config.command_watchdog_timeout =
    std::chrono::milliseconds(params_.command_watchdog_timeout_ms);
  config.command_watchdog_action =
    parse_watchdog_action(params_.command_watchdog_action);
  config.max_brake_current = static_cast<float>(params_.max_brake_current);
  config.command_watchdog_brake_current =
    static_cast<float>(params_.command_watchdog_brake_current);

  client_ = std::make_unique<goat_vesc::VescClient>(std::move(config));

  create_interfaces();
  log_parameter_summary();
  attempt_initial_connect();
}

VescNode::~VescNode()
{
  reconnect_timer_.reset();
  command_subscription_.reset();
  if (client_) {
    client_->disconnect();
  }
  imu_subscription_.reset();
  motor_state_subscription_.reset();
}

void VescNode::declare_parameters()
{
  this->declare_parameter<std::string>("device_path", "");
  this->declare_parameter<int>("baud", 115200);
  this->declare_parameter<bool>("auto_connect", true);
  this->declare_parameter<bool>("auto_reconnect", true);
  this->declare_parameter<int>("reconnect_period_ms", 1000);
  this->declare_parameter<int>("imu_poll_interval_ms", 10);
  this->declare_parameter<int>("motor_poll_interval_ms", 50);
  this->declare_parameter<int>("poll_response_timeout_ms", 20);
  this->declare_parameter<int>("query_guard_window_ms", 5);
  this->declare_parameter<int>("command_watchdog_timeout_ms", 0);
  this->declare_parameter<std::string>("command_watchdog_action", "disabled");
  this->declare_parameter<double>("max_brake_current", 0.0);
  this->declare_parameter<double>("command_watchdog_brake_current", 0.0);
  this->declare_parameter<bool>("publish_imu", true);
  this->declare_parameter<bool>("publish_motor_state", true);
  this->declare_parameter<std::string>("frame_id", "base_link");
  this->declare_parameter<std::string>("imu_frame_id", "");
  this->declare_parameter<std::string>("command_topic", "cmd/vesc");
}

VescNode::Parameters VescNode::load_parameters()
{
  Parameters params;
  params.device_path = this->get_parameter("device_path").as_string();
  params.baud = this->get_parameter("baud").as_int();
  params.auto_connect = this->get_parameter("auto_connect").as_bool();
  params.auto_reconnect = this->get_parameter("auto_reconnect").as_bool();
  params.reconnect_period_ms =
    this->get_parameter("reconnect_period_ms").as_int();
  params.imu_poll_interval_ms =
    this->get_parameter("imu_poll_interval_ms").as_int();
  params.motor_poll_interval_ms =
    this->get_parameter("motor_poll_interval_ms").as_int();
  params.poll_response_timeout_ms =
    this->get_parameter("poll_response_timeout_ms").as_int();
  params.query_guard_window_ms =
    this->get_parameter("query_guard_window_ms").as_int();
  params.command_watchdog_timeout_ms =
    this->get_parameter("command_watchdog_timeout_ms").as_int();
  params.command_watchdog_action =
    this->get_parameter("command_watchdog_action").as_string();
  params.max_brake_current =
    this->get_parameter("max_brake_current").as_double();
  params.command_watchdog_brake_current =
    this->get_parameter("command_watchdog_brake_current").as_double();
  params.publish_imu = this->get_parameter("publish_imu").as_bool();
  params.publish_motor_state =
    this->get_parameter("publish_motor_state").as_bool();
  params.frame_id = this->get_parameter("frame_id").as_string();
  params.imu_frame_id = this->get_parameter("imu_frame_id").as_string();
  params.command_topic = this->get_parameter("command_topic").as_string();
  return params;
}

void VescNode::validate_parameters(const Parameters & params) const
{
  if (params.baud <= 0) {
    throw std::invalid_argument("baud must be positive");
  }
  if (params.reconnect_period_ms <= 0) {
    throw std::invalid_argument("reconnect_period_ms must be positive");
  }
  if (params.imu_poll_interval_ms < 0) {
    throw std::invalid_argument("imu_poll_interval_ms must be non-negative");
  }
  if (params.motor_poll_interval_ms < 0) {
    throw std::invalid_argument("motor_poll_interval_ms must be non-negative");
  }
  if (params.poll_response_timeout_ms < 0) {
    throw std::invalid_argument(
            "poll_response_timeout_ms must be non-negative");
  }
  if (params.query_guard_window_ms < 0) {
    throw std::invalid_argument("query_guard_window_ms must be non-negative");
  }
  if (params.command_watchdog_timeout_ms < 0) {
    throw std::invalid_argument(
            "command_watchdog_timeout_ms must be non-negative");
  }
  if (params.max_brake_current < 0.0) {
    throw std::invalid_argument("max_brake_current must be non-negative");
  }
  if (params.command_watchdog_brake_current < 0.0) {
    throw std::invalid_argument(
            "command_watchdog_brake_current must be non-negative");
  }
  if (params.frame_id.empty()) {
    throw std::invalid_argument("frame_id must not be empty");
  }
  if (params.command_topic.empty()) {
    throw std::invalid_argument("command_topic must not be empty");
  }

  (void)parse_watchdog_action(params.command_watchdog_action);
}

goat_vesc::ControlWatchdogAction
VescNode::parse_watchdog_action(const std::string & value)
{
  if (value == "disabled") {
    return goat_vesc::ControlWatchdogAction::Disabled;
  }
  if (value == "coast") {
    return goat_vesc::ControlWatchdogAction::Coast;
  }
  if (value == "brake_current") {
    return goat_vesc::ControlWatchdogAction::BrakeCurrent;
  }
  throw std::invalid_argument(
          "command_watchdog_action must be one of: disabled, coast, brake_current");
}

void VescNode::log_parameter_summary() const
{
  RCLCPP_INFO(
    this->get_logger(),
    "Starting goat_vesc_ros with device_path='%s', baud=%d, auto_connect=%s, "
    "auto_reconnect=%s, imu_poll_interval_ms=%d, motor_poll_interval_ms=%d, "
    "command_topic='%s'",
    params_.device_path.c_str(), params_.baud,
    params_.auto_connect ? "true" : "false",
    params_.auto_reconnect ? "true" : "false", params_.imu_poll_interval_ms,
    params_.motor_poll_interval_ms, params_.command_topic.c_str());
}

void VescNode::create_interfaces()
{
  if (params_.publish_imu) {
    imu_publisher_ = this->create_publisher<sensor_msgs::msg::Imu>(
      "imu/data_raw", rclcpp::SensorDataQoS());
  }

  if (params_.publish_motor_state) {
    motor_state_publisher_ =
      this->create_publisher<goat_vesc_ros::msg::VescMotorState>(
      "motor_state", rclcpp::SensorDataQoS());
  }

  command_subscription_ =
    this->create_subscription<goat_vesc_ros::msg::VescControlCommand>(
    params_.command_topic, rclcpp::QoS(10),
    [this](
      const goat_vesc_ros::msg::VescControlCommand::SharedPtr message) {
      handle_command(message);
    });

  imu_subscription_ =
    client_->subscribe_imu(
    [this](const goat_vesc::VescIMUData & sample) {
      handle_imu_sample(sample);
    });
  motor_state_subscription_ = client_->subscribe_motor_state(
    [this](const goat_vesc::VescMotorState & sample) {
      handle_motor_state_sample(sample);
    });

  reconnect_timer_ = this->create_wall_timer(
    std::chrono::milliseconds(params_.reconnect_period_ms),
    [this] {reconnect_timer_callback();});
}

void VescNode::attempt_initial_connect()
{
  if (!params_.auto_connect) {
    RCLCPP_INFO(
      this->get_logger(),
      "auto_connect is disabled; skipping initial connect.");
    return;
  }

  (void)attempt_connect("startup", false);
}

void VescNode::reconnect_timer_callback()
{
  if (sync_connected_state()) {
    return;
  }

  if (!params_.auto_reconnect) {
    return;
  }

  (void)attempt_connect("reconnect timer", true);
}

bool VescNode::sync_connected_state()
{
  const bool is_connected = client_ && client_->is_connected();
  const bool was_connected = connected_.exchange(is_connected);
  if (was_connected && !is_connected) {
    RCLCPP_WARN(this->get_logger(), "Lost connection to VESC.");
  }
  return is_connected;
}

bool VescNode::attempt_connect(const char * reason, bool throttled)
{
  if (!client_) {
    return false;
  }
  if (client_->is_connected()) {
    connected_.store(true);
    return true;
  }

  RCLCPP_INFO(this->get_logger(), "Attempting VESC connection (%s).", reason);
  const bool connected = client_->connect();
  connected_.store(connected);
  if (connected) {
    reset_post_connect_state();
    RCLCPP_INFO(this->get_logger(), "Connected to VESC.");
    return true;
  }

  if (throttled) {
    RCLCPP_WARN_THROTTLE(
      this->get_logger(), *this->get_clock(),
      kReconnectWarnThrottle,
      "VESC connection attempt failed (%s).", reason);
  } else {
    RCLCPP_WARN(
      this->get_logger(), "VESC connection attempt failed (%s).",
      reason);
  }
  return false;
}

void VescNode::reset_post_connect_state()
{
  saw_first_imu_.store(false);
  saw_first_motor_state_.store(false);
}

void VescNode::handle_command(
  const goat_vesc_ros::msg::VescControlCommand::SharedPtr message)
{
  if (!std::isfinite(message->drive_value) ||
    !std::isfinite(message->servo_position))
  {
    RCLCPP_WARN(this->get_logger(), "Rejected non-finite VESC command.");
    return;
  }

  if (message->drive_mode !=
    goat_vesc_ros::msg::VescControlCommand::MODE_DUTY)
  {
    RCLCPP_WARN(
      this->get_logger(), "Rejected unsupported drive mode %u.",
      static_cast<unsigned int>(message->drive_mode));
    return;
  }

  if (!sync_connected_state()) {
    RCLCPP_WARN_THROTTLE(
      this->get_logger(), *this->get_clock(),
      kDisconnectedWarnThrottle,
      "Rejected VESC command while disconnected.");
    return;
  }

  const float drive_value = std::clamp(message->drive_value, -1.0f, 1.0f);
  const float servo_position = std::clamp(message->servo_position, 0.0f, 1.0f);

  const bool drive_accepted = client_->set_duty(drive_value);
  if (!drive_accepted) {
    RCLCPP_WARN(
      this->get_logger(),
      "VESC drive command was not accepted by goat_vesc.");
  }

  const bool servo_accepted = client_->set_servo_pos(servo_position);
  if (!servo_accepted) {
    RCLCPP_WARN(
      this->get_logger(),
      "VESC servo command was not accepted by goat_vesc.");
  }
}

void VescNode::handle_imu_sample(const goat_vesc::VescIMUData & sample)
{
  connected_.store(true);
  if (!saw_first_imu_.exchange(true)) {
    RCLCPP_INFO(this->get_logger(), "Received first IMU telemetry sample.");
  }

  if (imu_publisher_) {
    imu_publisher_->publish(to_imu_message(sample));
  }
}

void VescNode::handle_motor_state_sample(
  const goat_vesc::VescMotorState & sample)
{
  connected_.store(true);
  if (!saw_first_motor_state_.exchange(true)) {
    RCLCPP_INFO(
      this->get_logger(),
      "Received first motor-state telemetry sample.");
  }

  if (motor_state_publisher_) {
    motor_state_publisher_->publish(to_motor_state_message(sample));
  }
}

sensor_msgs::msg::Imu
VescNode::to_imu_message(const goat_vesc::VescIMUData & sample) const
{
  sensor_msgs::msg::Imu message;
  message.header.stamp = stamp_from_ns(sample.stamp_ns);
  message.header.frame_id = resolved_imu_frame_id();
  message.angular_velocity.x = sample.gyro_x;
  message.angular_velocity.y = sample.gyro_y;
  message.angular_velocity.z = sample.gyro_z;
  message.linear_acceleration.x = sample.acc_x;
  message.linear_acceleration.y = sample.acc_y;
  message.linear_acceleration.z = sample.acc_z;
  message.orientation_covariance[0] = -1.0;
  return message;
}

goat_vesc_ros::msg::VescMotorState VescNode::to_motor_state_message(
  const goat_vesc::VescMotorState & sample) const
{
  goat_vesc_ros::msg::VescMotorState message;
  message.header.stamp = stamp_from_ns(sample.stamp_ns);
  message.header.frame_id = params_.frame_id;
  message.rpm = sample.rpm;
  message.current_motor = sample.current_motor;
  message.current_in = sample.current_in;
  message.duty_cycle = sample.duty_cycle;
  message.vin = sample.vin;
  message.temp_motor = sample.temp_motor;
  message.temp_fet = sample.temp_fet;
  message.tachometer = sample.tachometer;
  message.tachometer_abs = sample.tachometer_abs;
  message.fault_code = sample.fault_code;
  return message;
}

builtin_interfaces::msg::Time
VescNode::stamp_from_ns(std::uint64_t stamp_ns) const
{
  if (stamp_ns == 0U) {
    return this->now();
  }

  return rclcpp::Time(
    static_cast<rcl_time_point_value_t>(stamp_ns),
    RCL_SYSTEM_TIME);
}

const std::string & VescNode::resolved_imu_frame_id() const
{
  if (!params_.imu_frame_id.empty()) {
    return params_.imu_frame_id;
  }
  return params_.frame_id;
}

} // namespace goat_vesc_ros
