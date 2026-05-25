#pragma once

#include <string>

#include "builtin_interfaces/msg/time.hpp"
#include "ld19/types.hpp"
#include "sensor_msgs/msg/laser_scan.hpp"

namespace goat_ros_laser
{

struct LaserScanConfig
{
  std::string frame_id{"laser"};
  double angle_min{-3.14159265358979323846};
  double angle_max{3.14159265358979323846};
  double angle_increment{0.017453292519943295};
  double range_min{0.03};
  double range_max{12.0};
};

sensor_msgs::msg::LaserScan to_laser_scan(
  const ld19::Scan & scan,
  const LaserScanConfig & config,
  const builtin_interfaces::msg::Time & stamp);

double ld19_clockwise_degrees_to_ros_radians(double angle_degrees);

}  // namespace goat_ros_laser
