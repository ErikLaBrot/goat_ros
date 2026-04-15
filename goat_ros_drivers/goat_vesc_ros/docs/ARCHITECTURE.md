# goat_vesc_ros Architecture Notes

This document describes the ROS-facing architecture of `goat_vesc_ros`. The
package is intentionally small: it wraps one `goat_vesc::VescClient`, owns the
ROS interfaces around that client, and leaves teleop and vehicle-level control
policy to other packages.

## Node Responsibilities

`goat_vesc_ros::VescNode` owns:

- ROS parameters and their validation
- ROS publishers, subscriptions, and launch-time configuration
- the single `goat_vesc::VescClient` instance used by the node
- connection state tracking and reconnect attempts
- conversion between driver types and ROS message types

The node does not own:

- joystick or higher-level teleop mapping
- autonomy or vehicle-level control logic
- a ROS-managed steering timeout policy
- timer-driven republishing of cached telemetry

## Startup And Interface Creation

Construction follows a fixed order:

1. declare ROS parameters
2. load and validate them into the local `Parameters` struct
3. build the `goat_vesc::VescConfig`
4. construct the `goat_vesc::VescClient`
5. create ROS publishers, subscriptions, and the reconnect timer
6. log the effective startup configuration
7. attempt the initial connection when `auto_connect` is enabled

This keeps parameter validation ahead of driver creation and ensures the node's
ROS interfaces exist before telemetry or reconnect activity begins.

## Command Path

The subscribed actuator input is `goat_vesc_ros/msg/VescControlCommand` on the
configured `command_topic`.

The command handler:

- rejects non-finite `drive_value` or `servo_position`
- rejects any `drive_mode` other than `MODE_DUTY`
- rejects commands while the node believes the client is disconnected
- clamps `drive_value` to `[-1.0, 1.0]`
- clamps `servo_position` to `[0.0, 1.0]`
- forwards the values to `goat_vesc::VescClient::set_duty()` and
  `goat_vesc::VescClient::set_servo_pos()`

The command timestamp is accepted for upstream bookkeeping only. It is not used
for timeout logic inside `goat_vesc_ros`.

## Telemetry Path

Telemetry publication is event-driven from `goat_vesc` callbacks rather than
from ROS timers.

- IMU samples are converted into `sensor_msgs/msg/Imu` and published on
  `imu/data_raw`
- motor-state samples are converted into
  `goat_vesc_ros/msg/VescMotorState` and published on `motor_state`

On the first sample of each type, the node logs that telemetry has started.
Incoming driver timestamps are converted into ROS time when present; otherwise
the node falls back to `now()`.

## Connection And Reconnect Model

`goat_vesc_ros` treats connection management as a node responsibility.

- `auto_connect` controls whether startup attempts an immediate connection
- `auto_reconnect` controls whether the reconnect timer retries after
  disconnects
- `reconnect_period_ms` controls the timer cadence

The node keeps an atomic `connected_` view so command rejection and warning
behavior can stay lightweight. A failed command path does not trigger a
reconnect directly; reconnects happen through the timer path.

## Parameter Boundary

Most transport-facing configuration is passed through directly to `goat_vesc`,
including:

- poll cadences
- reply timeout and query guard settings
- watchdog timeout and action
- brake-current limits

ROS-specific configuration stays in the adapter node, including:

- topic names
- whether ROS publishers are created
- frame ID selection and IMU frame fallback
- reconnect policy and logging

This keeps `goat_vesc_ros` focused on ROS integration while `goat_vesc`
continues to own transport and protocol behavior.
