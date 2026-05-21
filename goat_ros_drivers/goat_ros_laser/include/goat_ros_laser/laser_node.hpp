#pragma once

#include <memory>
#include <string>

#include "goat_ros_laser/laser_scan_conversion.hpp"
#include "ld19/ld19_client.hpp"
#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/laser_scan.hpp"

namespace goat_ros_laser
{

class LaserNode : public rclcpp::Node
{
public:
  explicit LaserNode(const rclcpp::NodeOptions & options = rclcpp::NodeOptions());
  ~LaserNode() override;

private:
  struct Parameters
  {
    std::string device_path{"/dev/ttyUSB0"};
    int baud{230400};
    bool auto_connect{true};
    bool auto_reconnect{true};
    int reconnect_period_ms{1000};
    int data_timeout_ms{500};
    bool check_device_path{true};
    bool filter_ranges{true};
    double range_min{0.03};
    double range_max{12.0};
    std::string scan_topic{"scan"};
    std::string frame_id{"laser"};
    double publish_rate_hz{20.0};
    double angle_min{-3.14159265358979323846};
    double angle_max{3.14159265358979323846};
    double angle_increment{0.017453292519943295};
  };

  void declare_parameters();
  Parameters load_parameters() const;
  void validate_parameters(const Parameters & params) const;
  ld19::Ld19Config make_driver_config(const Parameters & params) const;
  LaserScanConfig make_scan_config(const Parameters & params) const;
  void create_interfaces();
  void attempt_initial_connect();
  void reconnect_timer_callback();
  void publish_timer_callback();
  builtin_interfaces::msg::Time stamp_from_ns(std::uint64_t stamp_ns) const;

  Parameters params_;
  LaserScanConfig scan_config_;
  std::unique_ptr<ld19::Ld19Client> client_;
  rclcpp::Publisher<sensor_msgs::msg::LaserScan>::SharedPtr scan_publisher_;
  rclcpp::TimerBase::SharedPtr publish_timer_;
  rclcpp::TimerBase::SharedPtr reconnect_timer_;
  std::uint64_t last_published_stamp_ns_{0};
};

}  // namespace goat_ros_laser
