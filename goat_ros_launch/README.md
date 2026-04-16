# goat_ros_launch

## Purpose

`goat_ros_launch` is the high-level launch and recording surface for GOAT. It
keeps robot bringup, subsystem composition, rosbag recording profiles, and
replay helpers in one launch/config-only package.

## Nodes

This package does not define runtime nodes. It includes existing subsystem
launch files and starts `ros2 bag` processes when recording or replay is
requested.

## Topics

### Subscribed Topics

- No package-owned subscriptions.

### Published Topics

- No package-owned publishers.

Rosbag recording profiles install under `config/rosbag/profiles`:

- `core.txt`: Minimal joystick, command, vehicle telemetry, and TF topics.
- `slam.txt`: Core topics plus common scan, point cloud, camera, and odometry
  topics.
- `debug.txt`: SLAM topics plus diagnostics, parameter events, and ROS logs.

## Parameters

- No package-owned ROS parameters.

Launch arguments provide the operator-facing configuration:

- `robot.launch.py`: `sensor_launch_file`, `teleop_config_file`,
  `vesc_config_file`, `joy_dev`, `deadzone`, `record`, `record_profile`,
  `bag_dir`, `bag_name`, `storage_id`, and `storage_preset`.
- `sensors.launch.py`: `sensor_launch_file`.
- `teleop.launch.py`: `config_file`, `joy_dev`, and `deadzone`.
- `replay.launch.py`: `bag_path`, `rate`, and `publish_clock`.

## Launch Entry Points

- `robot.launch.py`: Canonical robot bringup entrypoint. It includes sensor
  integration, joystick teleop, VESC interface bringup, and optional rosbag
  recording.
- `sensors.launch.py`: Thin sensor-stack integration wrapper. It includes the
  launch file passed through `sensor_launch_file` when a sensor stack exists
  outside this package.
- `teleop.launch.py`: Thin joystick/control-side wrapper around
  `goat_teleop`'s `goat_joy.launch.py`.
- `replay.launch.py`: Thin wrapper around `ros2 bag play`.

## Dependencies

- ROS packages: `ament_index_python`, `goat_teleop`, `goat_vesc_ros`, `launch`,
  `launch_ros`, `ros2bag`, and `rosbag2_storage_mcap`
- Runtime assumptions: `goat_vesc_ros` is configured for the target VESC
  device, joystick hardware is available to `joy_node`, and any sensor stack is
  exposed through its own launch file.
- Config files: `config/rosbag/profiles/*.txt` provide explicit topic
  allowlists for rosbag recording.

## Example Usage

```bash
ros2 launch goat_ros_launch robot.launch.py
```

Start canonical bringup with the core rosbag profile:

```bash
ros2 launch goat_ros_launch robot.launch.py record:=true
```

Record the sensor-heavy SLAM topic allowlist to MCAP:

```bash
ros2 launch goat_ros_launch robot.launch.py record:=true record_profile:=slam
```

Replay a recorded bag:

```bash
ros2 launch goat_ros_launch replay.launch.py bag_path:=./goat_20260415_172500
```

## Rules

- Keep this package launch/config only.
- Prefer including subsystem launch files over duplicating node logic.
- Do not add robot, teleop, VESC, perception, or recorder nodes here.
- Rosbag recording uses explicit profile topic allowlists rather than `-a`.
