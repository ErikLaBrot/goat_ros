#include "goat_ros_laser/laser_scan_conversion.hpp"

#include <algorithm>
#include <cmath>
#include <cstddef>
#include <limits>
#include <vector>

namespace goat_ros_laser
{

namespace
{

constexpr double kPi = 3.14159265358979323846;
constexpr double kTwoPi = 2.0 * kPi;

double normalize_ros_angle(double radians)
{
  while (radians >= kPi) {
    radians -= kTwoPi;
  }
  while (radians < -kPi) {
    radians += kTwoPi;
  }
  return radians;
}

std::size_t range_count(const LaserScanConfig & config)
{
  return static_cast<std::size_t>(
    std::floor((config.angle_max - config.angle_min) / config.angle_increment)) + 1U;
}

}  // namespace

double ld19_clockwise_degrees_to_ros_radians(double angle_degrees)
{
  return normalize_ros_angle(-angle_degrees * kPi / 180.0);
}

sensor_msgs::msg::LaserScan to_laser_scan(
  const ld19::Scan & scan,
  const LaserScanConfig & config,
  const builtin_interfaces::msg::Time & stamp)
{
  sensor_msgs::msg::LaserScan message;
  message.header.stamp = stamp;
  message.header.frame_id = config.frame_id;
  message.angle_min = static_cast<float>(config.angle_min);
  message.angle_max = static_cast<float>(config.angle_max);
  message.angle_increment = static_cast<float>(config.angle_increment);
  message.range_min = static_cast<float>(config.range_min);
  message.range_max = static_cast<float>(config.range_max);
  if (scan.speed_degrees_per_second > 0.0) {
    message.scan_time = static_cast<float>(360.0 / scan.speed_degrees_per_second);
  }

  const std::size_t bins = range_count(config);
  message.ranges.assign(bins, std::numeric_limits<float>::quiet_NaN());
  message.intensities.assign(bins, 0.0F);

  for (const auto & point : scan.points) {
    if (!point.valid || !std::isfinite(point.distance_m) ||
      point.distance_m < config.range_min || point.distance_m > config.range_max)
    {
      continue;
    }

    const double ros_angle = ld19_clockwise_degrees_to_ros_radians(point.angle_degrees);
    if (ros_angle < config.angle_min || ros_angle > config.angle_max) {
      continue;
    }

    const auto bin = static_cast<std::size_t>(
      std::floor((ros_angle - config.angle_min) / config.angle_increment + 0.5));
    if (bin >= bins) {
      continue;
    }

    const float range = static_cast<float>(point.distance_m);
    if (std::isnan(message.ranges[bin]) || range < message.ranges[bin]) {
      message.ranges[bin] = range;
      message.intensities[bin] = static_cast<float>(point.intensity);
    }
  }

  return message;
}

}  // namespace goat_ros_laser
