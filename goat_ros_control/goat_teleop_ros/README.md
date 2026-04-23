# goat_teleop

## Purpose

`goat_teleop` is a ROS 2 Humble joystick teleop package for GOAT. It consumes
`sensor_msgs/msg/Joy` samples on `/joy` and publishes
`goat_vesc_ros/msg/VescControlCommand` on the canonical `cmd/vesc` topic for
manual vehicle control.

## Nodes

### `goat_joy`
- Purpose: Convert joystick axes and buttons into duty-cycle and servo commands.
- Executable: `goat_joy`
- Notes: Commands are only driven while the configured enable button is held. When disabled, the node publishes zero drive duty and a centered servo position. The published `goat_vesc_ros/msg/VescControlCommand` always uses `MODE_DUTY`, conditions throttle and steering input before scaling, treats `command_scale` as the throttle scale, and clamps steering around `servo_center` using `servo_amplitude` as the steering scale.

## Topics

### Subscribed Topics
- `/joy` (`sensor_msgs/msg/Joy`): Joystick state consumed by `goat_joy` for throttle, steering, and enable-button state.

### Published Topics
- `cmd/vesc` (`goat_vesc_ros/msg/VescControlCommand`): Canonical actuator command topic for `goat_vesc_ros`. `drive_value` reflects the configured throttle axis scaled by `command_scale`, and `servo_position` stays within `[0.0, 1.0]`.

## Parameters

- `throttle_axis` (`int`, default: `1`): Joystick axis index used for drive duty.
- `steering_axis` (`int`, default: `3`): Joystick axis index used for servo steering.
- `enable_button` (`int`, default: `4`): Button index that must be pressed before non-zero drive commands are published.
- `command_scale` (`double`, default: `0.10`): Maximum absolute duty command sent to `goat_vesc_ros` from the configured throttle axis.
- `invert_throttle` (`bool`, default: `false`): Invert the selected throttle axis before scaling.
- `invert_steering` (`bool`, default: `false`): Invert the selected steering axis before servo conversion.
- `servo_center` (`double`, default: `0.5`): Neutral servo position published when steering input is centered or disabled.
- `servo_amplitude` (`double`, default: `0.1`): Steering excursion added around `servo_center` before clamping to `[0.0, 1.0]`.
- `deadband` (`double`, default: `0.05`): Normalized throttle and steering input inside `[-deadband, deadband]` is treated as zero.
- `steer_tau_s` (`double`, default: `0.12`): Steering first-order low-pass filter time constant in seconds. Use `0.0` to disable steering filtering.
- `throttle_tau_s` (`double`, default: `0.18`): Throttle first-order low-pass filter time constant in seconds. Use `0.0` to disable throttle filtering.
- `max_steer_rate` (`double`, default: `3.0`): Maximum conditioned steering change in normalized joystick units per second. Use `0.0` to disable steering slew limiting.
- `max_throttle_rate` (`double`, default: `2.0`): Maximum conditioned throttle change in normalized joystick units per second. Use `0.0` to disable throttle slew limiting.
- `publish_epsilon` (`double`, default: `0.001`): Output-change threshold used to suppress repeated disabled neutral commands and snap tiny centered outputs to neutral.
- `control_rate_hz` (`double`, default: `50.0`): Timer rate used to update conditioned commands from the latest joystick sample.
- `command_topic` (`string`, default: `"cmd/vesc"`): Output topic for `goat_vesc_ros/msg/VescControlCommand`.

Deadband, filtering, and slew limiting run on normalized joystick values before
`command_scale` and `servo_amplitude` are applied. The defaults are intended for
manual demo driving, where small stick noise should disappear and quick stick
steps should soften without making the vehicle feel delayed.

## Launch Entry Points

- `bench_teleop.launch.py`: Starts `joy_node` plus `goat_joy` for local bench teleop. Accepts `config_file`, `joy_dev`, and `deadzone`.
- `remote_client.launch.py`: Starts the same client-side teleop stack for an operator machine that shares the robot's ROS graph. Accepts `config_file`, `joy_dev`, and `deadzone`.
- `goat_joy.launch.py`: Backward-compatible wrapper around `bench_teleop.launch.py`.

## Dependencies

- ROS packages: `goat_vesc_ros`, `joy`, `rclcpp`, `sensor_msgs`, `launch`, `launch_ros`
- Runtime assumptions: A joystick device is available to `joy_node`, typically `/dev/input/js0`
- Config files: `config/goat_joy.yaml` provides the default controller mapping, invert flags, throttle scale, steering scale, and conditioning configuration

## Example Usage

These examples assume `goat_teleop` is available in the current ROS
environment.

Start local bench teleop:

```bash
ros2 launch goat_teleop bench_teleop.launch.py
```

Start the same teleop stack on a remote operator client:

```bash
ros2 launch goat_teleop remote_client.launch.py
```

Override the joystick device or deadzone at launch time when needed:

```bash
ros2 launch goat_teleop bench_teleop.launch.py joy_dev:=/dev/input/js1 deadzone:=0.02
```

Use the package executable directly when you do not need the bundled launch
configuration:

```bash
ros2 run goat_teleop goat_joy
```

## Rules

- Topic names, parameter names, launch arguments, and examples in this README should match the installed package.
- This package does not define custom messages; it publishes the `goat_vesc_ros/msg/VescControlCommand` interface owned by `goat_vesc_ros`.
- Bench and remote client workflows intentionally share the same `cmd/vesc` command topic and differ only in where `joy_node` and `goat_joy` run.
