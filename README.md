# goat_ros

`goat_ros` is the unified ROS repository for the GOAT racer workspace. It
collects the platform-facing ROS 2 packages that are built together from the
`goat_racer` workspace.

## Repository Layout

- `goat_ros_control/`
  Control-facing ROS packages, including joystick teleop.
- `goat_ros_drivers/`
  Driver-facing ROS packages, including the VESC adapter node.

## Packages

- `goat_teleop`
  Joystick teleop node that turns `sensor_msgs/msg/Joy` input into
  `goat_vesc_ros/msg/VescControlCommand` output.
- `goat_vesc_ros`
  ROS adapter around `goat_vesc` for actuator commands and telemetry
  publishing.

## Workspace Usage

This repository is intended to be checked out under `goat_racer/ros_ws/src/`
and built through the shared `goat_racer/scripts/ros` workflow so it can
resolve the sibling `goat_vesc` dependency and write artifacts into the shared
workspace layout.
