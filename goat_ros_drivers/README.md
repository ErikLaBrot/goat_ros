# goat_ros_drivers

`goat_ros_drivers` groups ROS 2 driver-facing packages for the GOAT platform.

## Packages

- `goat_vesc_ros`
  ROS adapter node for the `goat_vesc` VESC transport library.

## Usage

Build these packages as part of a ROS 2 workspace that also provides the
installed `goat_vesc` dependency used by `goat_vesc_ros`.
