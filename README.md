# goat_ros

`goat_ros` collects the ROS 2 packages for the GOAT platform. It groups the
control-facing, driver-facing, and launch-facing packages that provide the ROS
interfaces for teleop, actuator commands, telemetry, and robot bringup.

## Repository Layout

- `goat_ros_control/`
  Control-facing ROS packages, including joystick teleop.
- `goat_ros_drivers/`
  Driver-facing ROS packages, including the VESC adapter node.
- `goat_ros_launch/`
  High-level robot bringup launch files and rosbag recording profiles.

## Packages

- `goat_teleop`
  Joystick teleop node that turns `sensor_msgs/msg/Joy` input into
  `goat_vesc_ros/msg/VescControlCommand` output.
- `goat_vesc_ros`
  ROS adapter around `goat_vesc` for actuator commands and telemetry
  publishing.
- `goat_ros_launch`
  Canonical launch entrypoints for robot bringup, subsystem composition,
  rosbag recording profiles, and bag replay.

## Usage

Build these packages as part of a ROS 2 workspace that also makes the
`goat_vesc` dependency available to `goat_vesc_ros`.
