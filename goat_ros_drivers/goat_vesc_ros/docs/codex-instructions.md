Implement a new ROS 2 C++ wrapper package for the existing `goat_vesc` library. Do not generate extra architecture or speculative features beyond what is requested.

## Goal

Create a straightforward ROS 2 package that:

* is structured cleanly as a thin wrapper around `goat_vesc`
* reads parameters on startup
* manages connection and setup of the VESC
* publishes IMU and motor state at dedicated ROS timer rates
* subscribes to a single command topic

Do not reimplement transport, protocol, packet parsing, scheduling, or watchdog internals already handled by `goat_vesc`.

## Constraints

* No Python nodes
* No `ros2_control`
* No lifecycle node unless it is already clearly justified by surrounding repo patterns
* No joystick/teleop logic
* No odometry
* No Ackermann mapping
* No autonomy logic
* No code generation beyond the wrapper package itself
* Keep the wrapper thin and boring

## Available context

Use the real local `goat_vesc` repository as the implementation source of truth.

Behavioral assumptions from architecture:

* `goat_vesc::VescClient` owns serial transport and keeps reads and writes on one background thread
* public methods may be called from multiple threads, but transport ownership remains centralized
* telemetry is cached internally and also available through subscriptions/callbacks
* reply-bearing queries are serialized separately from fire-and-forget commands
* watchdog exists in the library already and should not be reimplemented in ROS

Respect those assumptions. Do not fight the existing library design.

## Package name

Create a package named `goat_vesc_ros`.

## Package structure

Create a conventional ROS 2 C++ package layout with at least:

* `CMakeLists.txt`
* `package.xml`
* `include/goat_vesc_ros/vesc_node.hpp`
* `src/vesc_node.cpp`
* `src/main.cpp`
* `config/goat_vesc.yaml`
* `launch/goat_vesc.launch.py`

If a small helper like `converters.hpp/.cpp` is justified for message conversion, that is acceptable. Do not over-engineer.

## Node requirements

Create one plain `rclcpp::Node` class, e.g. `VescNode`.

### Responsibilities

The node must:

* declare and read ROS parameters
* construct and own one `goat_vesc::VescClient`
* connect to the VESC on startup
* manage reconnect attempts with a ROS timer if enabled by parameter
* subscribe to one command topic
* maintain latest received telemetry samples from the library
* publish IMU and motor state from dedicated ROS publish timers

Do not publish directly from the `goat_vesc` transport callback thread unless absolutely necessary. Prefer:

* transport callback updates cached latest samples
* ROS timers publish cached samples at configured rates

This keeps ROS publication on ROS-owned execution paths.

## Parameters

Add parameters for at least the following groups.

### Connection / transport

* `device_path`
* `baud`
* `auto_connect`
* `auto_reconnect`
* `reconnect_period_ms`

### Polling / library config

Expose relevant `goat_vesc` config values if they exist in the real library API, such as:

* `imu_poll_interval_ms`
* `motor_poll_interval_ms`
* any query or response timeout parameters that are part of the real config struct

Do not invent parameters that do not map cleanly to the real library.

### ROS publish behavior

* `publish_imu`
* `publish_motor_state`
* `imu_publish_rate_hz`
* `motor_state_publish_rate_hz`
* `frame_id`
* `imu_frame_id`

If both `frame_id` and `imu_frame_id` exist, document and implement a sensible precedence.

### Command handling

* `command_topic`
* `command_mode`

`command_mode` must be a constrained string or enum-like parameter indicating how incoming command values are interpreted. Keep it to modes that the real `goat_vesc` client clearly supports, such as:

* `current`
* `duty`
* `rpm`

Only implement modes that cleanly map to existing public API calls.

## Command subscription

Subscribe to a single command topic.

For the first implementation, keep the command message type simple and use a standard message type if possible. Favor something like:

* `std_msgs/msg/Float32` for a single scalar command

Interpret that scalar according to `command_mode`:

* `current` -> call the matching `goat_vesc` current command
* `duty` -> call the matching duty command
* `rpm` -> call the matching rpm command

Do not create a complex custom command message in this first pass.

If the real library exposes only differently named methods, adapt accordingly, but keep the ROS interface simple.

## Telemetry publishing

### IMU

Publish IMU as `sensor_msgs/msg/Imu`.

Map only fields that are clearly available and trustworthy from the real library data structures:

* angular velocity
* linear acceleration

Only publish orientation if the library actually provides a clearly defined orientation estimate with frame semantics that can be documented. Otherwise leave orientation unset/unknown in the standard ROS way.

If the library also provides magnetometer data, do not add a second publisher in this task unless it is extremely trivial and clean. The requested scope is only IMU and motor state.

### Motor state

Prefer a standard message if the data is very small and scalar, but if the real motor-state data is richer, create one small custom message only if necessary. Before doing that, check whether the surrounding repo already has a place for custom messages. If adding a custom message would substantially increase scope, publish a reduced standard message set for now and leave a clear TODO.

Bias toward minimalism.

### Publish timing

Use dedicated ROS timers:

* IMU publisher timer at `imu_publish_rate_hz`
* motor state publisher timer at `motor_state_publish_rate_hz`

The timers should publish the latest cached sample if one exists.

Do not block the timers on library queries.

## Connection and setup behavior

On startup:

1. read parameters
2. build any required `goat_vesc` config object from parameters
3. construct the client
4. register telemetry callbacks or subscriptions
5. attempt initial connection if enabled

If connection fails:

* log clearly
* mark internal connected state false
* allow reconnect timer to retry if enabled

When disconnected:

* command callbacks should not attempt unsafe behavior
* log at a reasonable throttled rate, not spam

Do not automatically replay old commands after reconnect.

## Internal state

Maintain simple internal cached state for:

* connection status
* latest IMU sample
* latest motor-state sample
* timestamps of last sample receipt

Protect shared cached state with straightforward mutex usage where needed. Keep concurrency simple and explicit.

## Logging and diagnostics

At minimum, log:

* startup parameters summary
* connection attempt success/failure
* reconnect attempts
* command rejections while disconnected
* first receipt of IMU and motor-state telemetry

Do not add full `/diagnostics` integration in this task unless it falls out naturally with very low complexity.

## Build system

Set up the package cleanly with:

* `ament_cmake`
* `rclcpp`
* `std_msgs`
* `sensor_msgs`
* any other minimal ROS deps actually used
* linkage against the existing `goat_vesc` library

Do not vendor `goat_vesc`.
Do not duplicate `goat_vesc` code into the ROS package.
Use the existing library through proper includes and linking.

If `goat_vesc` is not already exported in a way ROS can consume easily, make the smallest grounded integration choice needed, but do not redesign the upstream library build unless necessary.

## Launch and config

Create:

* a YAML config with reasonable defaults
* a launch file that starts the node and loads the YAML

Use a sane default `device_path`, preferably the stable `/dev/serial/by-id/...` path if that is already known in this project. If the exact full path is not available in the checked-in repo, leave a placeholder but make the parameter explicit.

## Documentation in code

Add concise comments only where useful.
Do not add bloated commentary.
Keep naming clear enough that the code mostly explains itself.

## Deliverable quality bar

The result should be:

* small
* understandable
* buildable
* obviously thin
* aligned with the real `goat_vesc` API
* easy to extend later

Do not add speculative abstractions for future multi-VESC, CAN buses, ros2_control, or autonomous vehicle control.

## Final output

After implementation, provide:

1. a short summary of files created
2. any assumptions made about the `goat_vesc` API
3. any mismatches or missing exports in the upstream library that need manual cleanup
4. any intentionally deferred items
