#include "goat_ros_laser/laser_scan_conversion.hpp"

#include <cmath>
#include <limits>

#include <gtest/gtest.h>

namespace
{

TEST(LaserScanConversion, ConvertsClockwiseAnglesIntoRosBins)
{
  ld19::Scan scan;
  scan.stamp_ns = 123U;
  scan.speed_degrees_per_second = 3600.0;
  scan.points = {
    ld19::Point{0.0, 1.0, 1000, 10, true},
    ld19::Point{90.0, 2.0, 2000, 20, true},
    ld19::Point{270.0, 3.0, 3000, 30, true},
    ld19::Point{180.0, 0.01, 10, 40, true},
    ld19::Point{45.0, 5.0, 5000, 50, false},
  };

  goat_ros_laser::LaserScanConfig config;
  config.frame_id = "laser";
  config.angle_min = -3.14159265358979323846;
  config.angle_max = 3.14159265358979323846;
  config.angle_increment = 3.14159265358979323846 / 2.0;
  config.range_min = 0.03;
  config.range_max = 12.0;

  builtin_interfaces::msg::Time stamp;
  stamp.sec = 1;
  stamp.nanosec = 23;
  const auto message = goat_ros_laser::to_laser_scan(scan, config, stamp);

  ASSERT_EQ(message.ranges.size(), 5U);
  EXPECT_EQ(message.header.frame_id, "laser");
  EXPECT_EQ(message.header.stamp.sec, 1);
  EXPECT_EQ(message.header.stamp.nanosec, 23U);
  EXPECT_FLOAT_EQ(message.ranges[2], 1.0F);
  EXPECT_FLOAT_EQ(message.ranges[1], 2.0F);
  EXPECT_FLOAT_EQ(message.ranges[3], 3.0F);
  EXPECT_TRUE(std::isnan(message.ranges[0]));
}

TEST(LaserScanConversion, KeepsNearestPointInBin)
{
  ld19::Scan scan;
  scan.points = {
    ld19::Point{0.0, 3.0, 3000, 10, true},
    ld19::Point{0.1, 1.0, 1000, 20, true},
  };

  goat_ros_laser::LaserScanConfig config;
  config.angle_min = -0.1;
  config.angle_max = 0.1;
  config.angle_increment = 0.1;

  builtin_interfaces::msg::Time stamp;
  const auto message = goat_ros_laser::to_laser_scan(scan, config, stamp);

  ASSERT_EQ(message.ranges.size(), 3U);
  EXPECT_FLOAT_EQ(message.ranges[1], 1.0F);
  EXPECT_FLOAT_EQ(message.intensities[1], 20.0F);
}

}  // namespace
