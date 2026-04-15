# goat_teleop

## Purpose

`goat_teleop` is a ROS 2 Humble joystick teleop package for GOAT. It consumes
`sensor_msgs/msg/Joy` samples on `/joy` and publishes
`goat_vesc_ros/msg/VescControlCommand` on `cmd/vesc` for manual vehicle control.

## Nodes

### `goat_joy`
- Purpose: Convert joystick axes and buttons into duty-cycle and servo commands.
- Executable: `goat_joy`
- Notes: Commands are only driven while the configured enable button is held. When disabled, the node publishes zero drive duty and a centered servo position. The published `goat_vesc_ros/msg/VescControlCommand` always uses `MODE_DUTY`, scales drive output by `command_scale`, and clamps steering around `servo_center` using `servo_amplitude`.

## Topics

### Subscribed Topics
- `/joy` (`sensor_msgs/msg/Joy`): Joystick state consumed by `goat_joy` for throttle, steering, and enable-button state.

### Published Topics
- `cmd/vesc` (`goat_vesc_ros/msg/VescControlCommand`): Canonical actuator command topic for `goat_vesc_ros`. `drive_value` reflects the configured throttle axis scaled by `command_scale`, and `servo_position` stays within `[0.0, 1.0]`.

## Parameters

- `throttle_axis` (`int`, default: `1`): Joystick axis index used for drive duty.
- `steering_axis` (`int`, default: `3`): Joystick axis index used for servo steering.
- `enable_button` (`int`, default: `4`): Button index that must be pressed before non-zero drive commands are published.
- `command_scale` (`double`, default: `0.10`): Maximum absolute duty command sent to `goat_vesc_ros`.
- `invert_throttle` (`bool`, default: `false`): Invert the selected throttle axis before scaling.
- `invert_steering` (`bool`, default: `false`): Invert the selected steering axis before servo conversion.
- `servo_center` (`double`, default: `0.5`): Neutral servo position published when steering input is centered or disabled.
- `servo_amplitude` (`double`, default: `0.1`): Steering excursion added around `servo_center` before clamping to `[0.0, 1.0]`.
- `command_topic` (`string`, default: `"cmd/vesc"`): Output topic for `goat_vesc_ros/msg/VescControlCommand`.

## Launch Entry Points

- `goat_joy.launch.py`: Starts `joy_node` plus `goat_joy` for manual smoke tests. Accepts `config_file`, `joy_dev`, and `deadzone` launch arguments.
- `controller_demo.launch.py`: Starts `goat_vesc_ros`, `joy_node`, and `goat_joy` together for the default controller bringup path. Accepts `vesc_config_file`, `teleop_config_file`, `joy_dev`, and `deadzone` launch arguments.

## Dependencies

- ROS packages: `goat_vesc_ros`, `joy`, `rclcpp`, `sensor_msgs`, `launch`, `launch_ros`
- Runtime assumptions: A joystick device is available to `joy_node`, typically `/dev/input/js0`
- Config files: `config/goat_joy.yaml` provides the default teleop axis and scaling configuration

## Example Usage

For the default end-to-end controller demo, work from the `goat_racer` repo
root:

```bash
scripts/ros bootstrap
scripts/demo
```

Before running the combined demo, update the `goat_vesc_ros` parameter file so
`device_path` points at the correct VESC serial device.

Override the joystick device or deadzone at launch time when needed through the
workspace helper:

```bash
scripts/demo joy_dev:=/dev/input/js1 deadzone:=0.02
```

To launch teleop without the VESC adapter, start only the teleop package inside
the shared container:

```bash
docker compose -f docker/compose.yaml exec ros-humble bash -lc \
  "source /opt/ros/humble/setup.bash && \
   source /workspace/goat_racer/ros_ws/install/setup.bash && \
   ros2 launch goat_teleop goat_joy.launch.py"
```

## Rules

- Topic names, parameter names, launch arguments, and examples in this README should match the installed package.
- This package does not define custom messages; it publishes the `goat_vesc_ros/msg/VescControlCommand` interface owned by `goat_vesc_ros`.
