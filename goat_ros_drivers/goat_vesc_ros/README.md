# goat_vesc_ros

## Purpose

`goat_vesc_ros` is a ROS 2 Humble adapter around `goat_vesc`. It owns one
`goat_vesc::VescClient`, translates ROS messages into driver calls, republishes
driver telemetry into ROS, and keeps reconnect behavior plus ROS-facing
configuration inside one node.

## Nodes

### `goat_vesc_ros`
- Purpose: Expose ROS interfaces for actuator commands, IMU telemetry, and motor-state telemetry backed by `goat_vesc`.
- Executable: `vesc_node`
- Notes: The command path currently accepts only `goat_vesc_ros/msg/VescControlCommand` with `MODE_DUTY`. `drive_value` is clamped to `[-1.0, 1.0]`, `servo_position` is clamped to `[0.0, 1.0]`, telemetry publishing is event-driven from `goat_vesc` callbacks, and reconnect attempts run from the node timer when `auto_reconnect` is enabled.

## Topics

### Subscribed Topics
- `cmd/vesc` (`goat_vesc_ros/msg/VescControlCommand`): Canonical actuator command input. `stamp` is informational only, `drive_mode` must be `MODE_DUTY`, `drive_value` maps to `goat_vesc::VescClient::set_duty()`, and `servo_position` maps to `goat_vesc::VescClient::set_servo_pos()`.

### Published Topics
- `imu/data_raw` (`sensor_msgs/msg/Imu`): IMU samples forwarded from `goat_vesc` callbacks. The ROS message uses the host-clock timestamps provided by `goat_vesc`, carries angular velocity and linear acceleration, publishes an explicit IMU frame ID when configured, fills the angular-velocity and linear-acceleration covariance diagonals from ROS parameters, and leaves orientation unspecified.
- `motor_state` (`goat_vesc_ros/msg/VescMotorState`): Motor telemetry forwarded from `goat_vesc` callbacks, including `rpm`, `current_motor`, `current_in`, `duty_cycle`, `vin`, `temp_motor`, `temp_fet`, `tachometer`, `tachometer_abs`, and `fault_code`.

## Parameters

- `device_path` (`string`, default: `""`): Serial device path passed to `goat_vesc`. Set this to the stable VESC device path before field use.
- `baud` (`int`, default: `115200`): Serial baud rate for the VESC connection.
- `auto_connect` (`bool`, default: `true`): Attempt the initial VESC connection during startup.
- `auto_reconnect` (`bool`, default: `true`): Retry connection on the reconnect timer when disconnected.
- `reconnect_period_ms` (`int`, default: `1000`): Reconnect timer cadence in milliseconds.
- `imu_poll_interval_ms` (`int`, default: `10`): IMU poll cadence forwarded to `goat_vesc`. `0` disables IMU polling.
- `motor_poll_interval_ms` (`int`, default: `50`): Motor-state poll cadence forwarded to `goat_vesc`. `0` disables motor polling.
- `poll_response_timeout_ms` (`int`, default: `20`): Reply timeout forwarded to `goat_vesc`.
- `query_guard_window_ms` (`int`, default: `5`): Query guard window forwarded to `goat_vesc`.
- `command_watchdog_timeout_ms` (`int`, default: `0`): Drive-side watchdog timeout forwarded to `goat_vesc`. `0` disables it.
- `command_watchdog_action` (`string`, default: `"disabled"`): Drive-side watchdog action forwarded to `goat_vesc`: `disabled`, `coast`, or `brake_current`.
- `max_brake_current` (`double`, default: `0.0`): Maximum brake current allowed by the forwarded watchdog configuration.
- `command_watchdog_brake_current` (`double`, default: `0.0`): Requested watchdog brake current before clamping in `goat_vesc`.
- `publish_imu` (`bool`, default: `true`): Create and publish the IMU topic.
- `publish_motor_state` (`bool`, default: `true`): Create and publish the motor-state topic.
- `frame_id` (`string`, default: `"base_link"`): Default frame used for motor-state messages and as the IMU fallback frame.
- `imu_frame_id` (`string`, default: `""`): Optional IMU-specific frame ID. When empty, `frame_id` is used.
- `imu_angular_velocity_covariance_diagonal` (`double[3]`, default: `[0.0, 0.0, 0.0]`): Diagonal covariance for angular velocity in `(rad/s)^2`. Zero values mean the IMU is available but not yet characterized.
- `imu_linear_acceleration_covariance_diagonal` (`double[3]`, default: `[0.0, 0.0, 0.0]`): Diagonal covariance for linear acceleration in `(m/s^2)^2`. Zero values mean the IMU is available but not yet characterized.
- `command_topic` (`string`, default: `"cmd/vesc"`): ROS topic name for `VescControlCommand` input.

## Launch Entry Points

- `goat_vesc.launch.py`: Starts `vesc_node` and loads parameters from `config/goat_vesc.yaml`. Accepts a `config_file` launch argument when you need an alternate parameter file such as the Isaac ROS VSLAM preset.

## Dependencies

- ROS packages: `builtin_interfaces`, `rclcpp`, `sensor_msgs`, `std_msgs`, `launch`, `launch_ros`
- External libraries: installed `goat_vesc` package
- Runtime assumptions: A reachable VESC serial device and a parameter file that points `device_path` at the correct interface

## Example Usage

These examples assume `goat_vesc_ros` is available in the current ROS
environment.

Update `config/goat_vesc.yaml` so `device_path` points at the correct VESC
serial device, then launch the adapter node:

```bash
ros2 launch goat_vesc_ros goat_vesc.launch.py
```

Use an alternate parameter file when needed:

```bash
ros2 launch goat_vesc_ros goat_vesc.launch.py config_file:=/path/to/goat_vesc.yaml
```

Start the ESC IMU with the Isaac ROS Visual SLAM-oriented frame ID and bench
covariance placeholders:

```bash
ros2 launch goat_vesc_ros goat_vesc.launch.py \
  config_file:=$(ros2 pkg prefix goat_vesc_ros --share)/config/goat_vesc_isaac_vslam.yaml
```

## Rules

- Topic names, parameter names, launch files, and examples in this README should match the installed package.
- `goat_vesc_ros` owns the ROS message semantics described here; the `.msg` files intentionally remain minimal.
- `config/goat_vesc_isaac_vslam.yaml` is a bench bringup preset only; replace its IMU covariance placeholders with measured values before production use.
