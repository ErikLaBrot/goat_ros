#include "goat_ros_laser/laser_node.hpp"

#include <chrono>
#include <cmath>
#include <stdexcept>

#include "rclcpp/qos.hpp"

namespace goat_ros_laser
{

namespace
{

constexpr auto kReconnectWarnThrottleMs = 5000;

}  // namespace

LaserNode::LaserNode(const rclcpp::NodeOptions & options)
: Node("goat_ros_laser", options)
{
  declare_parameters();
  params_ = load_parameters();
  validate_parameters(params_);
  scan_config_ = make_scan_config(params_);
  client_ = std::make_unique<ld19::Ld19Client>(make_driver_config(params_));

  create_interfaces();
  RCLCPP_INFO(
    get_logger(),
    "Starting goat_ros_laser for STL-19P with device_path='%s', baud=%d, topic='%s', frame_id='%s'",
    params_.device_path.c_str(), params_.baud, params_.scan_topic.c_str(),
    params_.frame_id.c_str());
  attempt_initial_connect();
}

LaserNode::~LaserNode()
{
  reconnect_timer_.reset();
  publish_timer_.reset();
  if (client_) {
    client_->disconnect();
  }
}

void LaserNode::declare_parameters()
{
  declare_parameter<std::string>("device_path", "/dev/ttyUSB0");
  declare_parameter<int>("baud", 230400);
  declare_parameter<bool>("auto_connect", true);
  declare_parameter<bool>("auto_reconnect", true);
  declare_parameter<int>("reconnect_period_ms", 1000);
  declare_parameter<int>("data_timeout_ms", 500);
  declare_parameter<bool>("check_device_path", true);
  declare_parameter<bool>("filter_ranges", true);
  declare_parameter<double>("range_min", 0.03);
  declare_parameter<double>("range_max", 12.0);
  declare_parameter<std::string>("scan_topic", "scan");
  declare_parameter<std::string>("frame_id", "laser");
  declare_parameter<double>("publish_rate_hz", 20.0);
  declare_parameter<double>("angle_min", -3.14159265358979323846);
  declare_parameter<double>("angle_max", 3.14159265358979323846);
  declare_parameter<double>("angle_increment", 0.017453292519943295);
}

LaserNode::Parameters LaserNode::load_parameters() const
{
  Parameters params;
  params.device_path = get_parameter("device_path").as_string();
  params.baud = static_cast<int>(get_parameter("baud").as_int());
  params.auto_connect = get_parameter("auto_connect").as_bool();
  params.auto_reconnect = get_parameter("auto_reconnect").as_bool();
  params.reconnect_period_ms =
    static_cast<int>(get_parameter("reconnect_period_ms").as_int());
  params.data_timeout_ms =
    static_cast<int>(get_parameter("data_timeout_ms").as_int());
  params.check_device_path = get_parameter("check_device_path").as_bool();
  params.filter_ranges = get_parameter("filter_ranges").as_bool();
  params.range_min = get_parameter("range_min").as_double();
  params.range_max = get_parameter("range_max").as_double();
  params.scan_topic = get_parameter("scan_topic").as_string();
  params.frame_id = get_parameter("frame_id").as_string();
  params.publish_rate_hz = get_parameter("publish_rate_hz").as_double();
  params.angle_min = get_parameter("angle_min").as_double();
  params.angle_max = get_parameter("angle_max").as_double();
  params.angle_increment = get_parameter("angle_increment").as_double();
  return params;
}

void LaserNode::validate_parameters(const Parameters & params) const
{
  if (params.device_path.empty()) {
    throw std::invalid_argument("device_path must not be empty");
  }
  if (params.baud <= 0) {
    throw std::invalid_argument("baud must be positive");
  }
  if (params.reconnect_period_ms <= 0) {
    throw std::invalid_argument("reconnect_period_ms must be positive");
  }
  if (params.data_timeout_ms <= 0) {
    throw std::invalid_argument("data_timeout_ms must be positive");
  }
  if (params.range_min < 0.0 || params.range_max <= params.range_min) {
    throw std::invalid_argument("range_min/range_max must be positive and increasing");
  }
  if (params.scan_topic.empty()) {
    throw std::invalid_argument("scan_topic must not be empty");
  }
  if (params.frame_id.empty()) {
    throw std::invalid_argument("frame_id must not be empty");
  }
  if (!std::isfinite(params.publish_rate_hz) || params.publish_rate_hz <= 0.0) {
    throw std::invalid_argument("publish_rate_hz must be positive");
  }
  if (!std::isfinite(params.angle_min) || !std::isfinite(params.angle_max) ||
    !std::isfinite(params.angle_increment) || params.angle_max <= params.angle_min ||
    params.angle_increment <= 0.0)
  {
    throw std::invalid_argument("angle parameters must be finite and increasing");
  }
}

ld19::Ld19Config LaserNode::make_driver_config(const Parameters & params) const
{
  ld19::Ld19Config config;
  config.device_path = params.device_path;
  config.baud = params.baud;
  config.auto_reconnect = params.auto_reconnect;
  config.reconnect_period = std::chrono::milliseconds(params.reconnect_period_ms);
  config.data_timeout = std::chrono::milliseconds(params.data_timeout_ms);
  config.check_device_path = params.check_device_path;
  config.filter_ranges = params.filter_ranges;
  config.range_min_m = params.range_min;
  config.range_max_m = params.range_max;
  config.wall_time_ns = []() {
    return static_cast<std::uint64_t>(
      std::chrono::duration_cast<std::chrono::nanoseconds>(
        std::chrono::system_clock::now().time_since_epoch())
        .count());
  };
  return config;
}

LaserScanConfig LaserNode::make_scan_config(const Parameters & params) const
{
  LaserScanConfig config;
  config.frame_id = params.frame_id;
  config.angle_min = params.angle_min;
  config.angle_max = params.angle_max;
  config.angle_increment = params.angle_increment;
  config.range_min = params.range_min;
  config.range_max = params.range_max;
  return config;
}

void LaserNode::create_interfaces()
{
  scan_publisher_ =
    create_publisher<sensor_msgs::msg::LaserScan>(params_.scan_topic, rclcpp::SensorDataQoS());

  const auto publish_period = std::chrono::duration<double>(1.0 / params_.publish_rate_hz);
  publish_timer_ = create_wall_timer(
    std::chrono::duration_cast<std::chrono::nanoseconds>(publish_period),
    [this]() { publish_timer_callback(); });

  if (params_.auto_reconnect) {
    reconnect_timer_ = create_wall_timer(
      std::chrono::milliseconds(params_.reconnect_period_ms),
      [this]() { reconnect_timer_callback(); });
  }
}

void LaserNode::attempt_initial_connect()
{
  if (!params_.auto_connect) {
    return;
  }

  if (!client_->connect()) {
    RCLCPP_WARN(get_logger(), "STL-19P initial connect failed: %s",
      client_->status().last_error.c_str());
  }
}

void LaserNode::reconnect_timer_callback()
{
  if (client_->is_connected()) {
    return;
  }

  if (!client_->connect()) {
    RCLCPP_WARN_THROTTLE(
      get_logger(), *get_clock(), kReconnectWarnThrottleMs,
      "STL-19P reconnect attempt failed: %s", client_->status().last_error.c_str());
  }
}

void LaserNode::publish_timer_callback()
{
  const auto scan = client_->latest_scan();
  if (!scan.has_value() || scan->stamp_ns == last_published_stamp_ns_) {
    return;
  }

  scan_publisher_->publish(
    to_laser_scan(*scan, scan_config_, stamp_from_ns(scan->stamp_ns)));
  last_published_stamp_ns_ = scan->stamp_ns;
}

builtin_interfaces::msg::Time LaserNode::stamp_from_ns(std::uint64_t stamp_ns) const
{
  builtin_interfaces::msg::Time stamp;
  stamp.sec = static_cast<std::int32_t>(stamp_ns / 1000000000ULL);
  stamp.nanosec = static_cast<std::uint32_t>(stamp_ns % 1000000000ULL);
  return stamp;
}

}  // namespace goat_ros_laser
