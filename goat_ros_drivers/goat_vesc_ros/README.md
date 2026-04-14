# goat_vesc_ros

`goat_vesc_ros` is a thin ROS 2 Humble adapter around `goat_vesc`. It owns one `goat_vesc::VescClient`, translates ROS messages into driver calls, republishes driver telemetry into ROS, and keeps reconnect behavior and ROS-facing configuration inside one plain node.

## Node

- Name: `goat_vesc_ros`
- Purpose: expose a small ROS interface for actuator commands, IMU telemetry, and motor-state telemetry
- Owns: ROS parameters, publishers/subscribers, reconnect policy, and message-to-driver conversion
- Does not own: teleop logic, vehicle-level control, autonomy, timer-driven telemetry publication, or ROS-managed steering timeout behavior

## Topics

| Topic | Type | Direction | Semantics |
| --- | --- | --- | --- |
| `cmd/vesc` | `goat_vesc_ros/msg/VescControlCommand` | subscribed | Canonical actuator command topic. In v1 only `MODE_DUTY` is accepted. `drive_value` is normalized duty and `servo_position` is normalized servo position. |
| `imu/data_raw` | `sensor_msgs/msg/Imu` | published | IMU samples forwarded directly from `goat_vesc` IMU callbacks. |
| `motor_state` | `goat_vesc_ros/msg/VescMotorState` | published | Motor-state samples forwarded directly from `goat_vesc` motor-state callbacks. |

## Messages

### `goat_vesc_ros/msg/VescControlCommand`

- `stamp`: ROS timestamp carried with the command for upstream bookkeeping; informational only in this refactor
- `MODE_DUTY=1`: only supported `drive_mode` in v1
- `drive_mode`: drive command schema selector
- `drive_value`: normalized drive command, clamped to `[-1.0, 1.0]` before calling `goat_vesc::VescClient::set_duty()`
- `servo_position`: normalized servo command, clamped to `[0.0, 1.0]` before calling `goat_vesc::VescClient::set_servo_pos()`

### `goat_vesc_ros/msg/VescMotorState`

- `header`
- `rpm`
- `current_motor`
- `current_in`
- `duty_cycle`
- `vin`
- `temp_motor`
- `temp_fet`
- `tachometer`
- `tachometer_abs`
- `fault_code`

## Parameters

| Parameter | Type | Default | Meaning |
| --- | --- | --- | --- |
| `device_path` | `string` | `""` | Serial path passed to `goat_vesc`. |
| `baud` | `int` | `115200` | Serial baud rate for the VESC connection. |
| `auto_connect` | `bool` | `true` | Attempt connection during startup. |
| `auto_reconnect` | `bool` | `true` | Retry connection on the reconnect timer when disconnected. |
| `reconnect_period_ms` | `int` | `1000` | Reconnect timer period in milliseconds. |
| `imu_poll_interval_ms` | `int` | `10` | IMU query cadence forwarded to `goat_vesc`. `0` disables polling. |
| `motor_poll_interval_ms` | `int` | `50` | Motor-state query cadence forwarded to `goat_vesc`. `0` disables polling. |
| `poll_response_timeout_ms` | `int` | `20` | Reply timeout forwarded to `goat_vesc`. |
| `query_guard_window_ms` | `int` | `5` | Query guard window forwarded to `goat_vesc`. |
| `command_watchdog_timeout_ms` | `int` | `0` | Drive-side watchdog timeout forwarded to `goat_vesc`. `0` disables it. |
| `command_watchdog_action` | `string` | `"disabled"` | Drive-side watchdog action forwarded to `goat_vesc`: `disabled`, `coast`, or `brake_current`. |
| `max_brake_current` | `double` | `0.0` | Maximum brake current used by the drive-side watchdog. |
| `command_watchdog_brake_current` | `double` | `0.0` | Requested watchdog brake current before clamping in `goat_vesc`. |
| `publish_imu` | `bool` | `true` | Create and publish the IMU topic. |
| `publish_motor_state` | `bool` | `true` | Create and publish the motor-state topic. |
| `frame_id` | `string` | `"base_link"` | Default frame used for motor-state and IMU messages. |
| `imu_frame_id` | `string` | `""` | Optional IMU-specific frame. When empty, `frame_id` is used. |
| `command_topic` | `string` | `"cmd/vesc"` | ROS topic name for `VescControlCommand` input. |

## Behavioral Notes

- Telemetry is event-driven. `goat_vesc_ros` publishes IMU and motor-state messages when `goat_vesc` invokes its callbacks; there is no ROS timer republishing cached telemetry.
- Reconnect behavior stays in the node. If startup connection fails or an active connection drops, the node retries on the reconnect timer when `auto_reconnect` is enabled.
- The watchdog parameters are passed through to `goat_vesc` and apply to drive-side stale-command behavior only. `goat_vesc_ros` does not implement ROS-owned steering timeout logic.
- Teleop or vehicle-level control mapping belongs in another package. This node expects already-decided actuator commands.

## Launch

`launch/goat_vesc.launch.py` starts `vesc_node` with `config/goat_vesc.yaml`.

## Example Startup

Update `config/goat_vesc.yaml` so `device_path` points at the correct VESC serial device, then start the node from the `goat_racer` repo root:

```bash
cd ../goat_racer
scripts/ros up
docker compose -f docker/compose.yaml exec ros-humble bash -lc \
  "source /opt/ros/humble/setup.bash && \
   source /workspace/goat_racer/ros_ws/install/setup.bash && \
   ros2 launch goat_vesc_ros goat_vesc.launch.py"
```
