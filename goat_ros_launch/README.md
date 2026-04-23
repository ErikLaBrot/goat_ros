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
- `slam.txt`: Core topics plus common scan, point cloud, stereo camera,
  Visual SLAM, and odometry topics.
- `debug.txt`: SLAM topics plus diagnostics, parameter events, and ROS logs.

## Parameters

- No package-owned ROS parameters.

Launch arguments provide the operator-facing configuration:

- `robot.launch.py`: `sensor_launch_file`, `sensor_launch_arguments`,
  `vesc_config_file`, `record`, `record_profile`, `bag_dir`, `bag_name`,
  `storage_id`, and `storage_preset`.
- `bench_robot_teleop.launch.py`: `sensor_launch_file`,
  `sensor_launch_arguments`, `teleop_config_file`, `vesc_config_file`,
  `joy_dev`, `deadzone`, `record`, `record_profile`, `bag_dir`, `bag_name`,
  `storage_id`, and `storage_preset`.
- `sensors.launch.py`: `config_file`, `sensor_launch_file`, and
  `sensor_launch_arguments`.
- `goat_d435_visual_slam.launch.py`: `serial_no`, `usb_port_id`,
  `enable_imu_fusion`, `imu_topic`, `visual_slam_config_file`,
  `camera_{x,y,z,roll,pitch,yaw}`, and `imu_{x,y,z,roll,pitch,yaw}`.
- `robot_d435_visual_slam.launch.py`: `sensor_launch_arguments`,
  `vesc_config_file`, `record`, `record_profile`, `bag_dir`, `bag_name`,
  `storage_id`, and `storage_preset`.
- `robot_d435_visual_slam_vio.launch.py`: Same as
  `robot_d435_visual_slam.launch.py`, but defaults `sensor_launch_arguments`
  to `enable_imu_fusion:=true` and `vesc_config_file` to the Isaac ROS
  VSLAM-oriented `goat_vesc_ros` parameter file.
- `teleop.launch.py`: `config_file`, `joy_dev`, and `deadzone`.
- `replay.launch.py`: `bag_path`, `rate`, and `publish_clock`.

Rosbag recording stores output under `bag_dir` with a timestamped `bag_name`.
Direct `ros2 launch` usage defaults to `~/.ros/goat/bags` so recordings do not
land in whichever directory launched the process. Top-level GOAT demo scripts
may pass a workspace-specific `bag_dir` when they run inside Docker.

## Launch Entry Points

- `robot.launch.py`: Canonical robot-side bringup entrypoint. It includes
  sensor integration, VESC interface bringup, and optional rosbag recording.
- `bench_robot_teleop.launch.py`: Explicit local bench-debug wrapper that
  composes `robot.launch.py` with local joystick teleop on the same machine.
- `sensors.launch.py`: Default sensor-stack integration wrapper. It reads
  `config/sensors.yaml` by default, which points at the D435 Visual SLAM stack,
  and still allows explicit launch file or argument overrides from the CLI. In
  the default GOAT deployment path this is the launch started by
  `./scripts/ops/run_vslam.sh`.
- `goat_d435_visual_slam.launch.py`: Bench bringup for the D435 stereo-only or
  visual-inertial Isaac ROS Visual SLAM stack. It owns the GOAT-facing stereo
  topic remaps, publishes static transforms for `camera_link` and
  `esc_imu_link`, and launches `isaac_ros_visual_slam`. The default profile is
  stereo-only: infrared stereo on, color off, depth off, and IMU fusion off.
- `robot_d435_visual_slam.launch.py`: Full GOAT bringup wrapper that uses the
  D435 Visual SLAM sensor stack with the normal `goat_vesc_ros` config.
- `robot_d435_visual_slam_vio.launch.py`: Full GOAT bringup wrapper that uses
  the D435 Visual SLAM sensor stack with `enable_imu_fusion:=true` and the
  VSLAM-oriented `goat_vesc_ros` config.
- `teleop.launch.py`: Thin local bench-teleop wrapper around
  `goat_teleop`'s `bench_teleop.launch.py`.
- `replay.launch.py`: Thin wrapper around `ros2 bag play`.

## Dependencies

- ROS packages: `ament_index_python`, `goat_teleop`, `goat_vesc_ros`,
  `isaac_ros_visual_slam`, `launch`, `launch_ros`, `realsense2_camera`,
  `ros2bag`, `rosbag2_storage_mcap`, and `tf2_ros`
- Runtime assumptions: `goat_vesc_ros` is configured for the target VESC
  device, any sensor stack is exposed through its own launch file, and joystick
  hardware is available to `joy_node` when bench teleop is launched. The D435/
  Visual SLAM entrypoints also require the Isaac ROS runtime packages to be
  installed in the active ROS environment. In `goat_racer`, those heavy Isaac
  packages are expected to come from the GOAT Isaac image layer rather than a
  source checkout.
- Config files: `config/rosbag/profiles/*.txt` provide explicit topic
  allowlists for rosbag recording, and `config/isaac_ros/goat_d435_visual_slam.yaml`
  provides the default Visual SLAM parameters. `config/sensors.yaml` provides
  the default sensor bringup wrapper config used by `sensors.launch.py`.

## Example Usage

```bash
ros2 launch goat_ros_launch robot.launch.py
```

Start explicit local bench teleop plus robot bringup on one machine:

```bash
ros2 launch goat_ros_launch bench_robot_teleop.launch.py
```

Start canonical robot-side bringup with the core rosbag profile:

```bash
ros2 launch goat_ros_launch robot.launch.py record:=true
```

By default, that writes a bag directory like this:

```text
~/.ros/goat/bags/goat_20260415_172500
```

Record the sensor-heavy SLAM topic allowlist to MCAP:

```bash
ros2 launch goat_ros_launch robot.launch.py record:=true record_profile:=slam
```

Choose a different save location when needed:

```bash
ros2 launch goat_ros_launch robot.launch.py \
  record:=true \
  bag_dir:=/workspace/goat_racer/ros_ws/bags
```

Replay a recorded bag:

```bash
ros2 launch goat_ros_launch replay.launch.py \
  bag_path:=~/.ros/goat/bags/goat_20260415_172500
```

Start the bench D435 stereo-only Visual SLAM stack:

```bash
ros2 launch goat_ros_launch goat_d435_visual_slam.launch.py
```

Start the default sensor wrapper with its package-installed config:

```bash
ros2 launch goat_ros_launch sensors.launch.py
```

That default sensor wrapper path is the normal GOAT D435 demo. It resolves to
the stereo-only configuration unless you override launch arguments.

Turn on external ESC IMU fusion for the same sensor stack:

```bash
ros2 launch goat_ros_launch goat_d435_visual_slam.launch.py \
  enable_imu_fusion:=true \
  imu_roll:=0.0 imu_pitch:=0.0 imu_yaw:=0.0
```

Start full robot bringup with the D435 stereo Visual SLAM stack:

```bash
ros2 launch goat_ros_launch robot_d435_visual_slam.launch.py
```

Start full robot bringup with the ESC IMU fused into Visual SLAM:

```bash
ros2 launch goat_ros_launch robot_d435_visual_slam_vio.launch.py
```

Forward custom sensor launch arguments through the canonical robot wrapper when
you need measured transforms or a specific camera selection:

```bash
ros2 launch goat_ros_launch robot.launch.py \
  sensor_launch_file:=$(ros2 pkg prefix goat_ros_launch --share)/launch/goat_d435_visual_slam.launch.py \
  sensor_launch_arguments:="enable_imu_fusion:=true camera_x:=0.10 camera_z:=0.22 imu_yaw:=1.57" \
  vesc_config_file:=$(ros2 pkg prefix goat_vesc_ros --share)/config/goat_vesc_isaac_vslam.yaml
```

## Rules

- Keep this package launch/config only.
- Prefer including subsystem launch files over duplicating node logic.
- Do not add robot, teleop, VESC, perception, or recorder nodes here.
- Keep robot-side bringup and client-side teleop as separate workflows unless a
  launch file explicitly documents that it composes both for bench use.
- Rosbag recording uses explicit profile topic allowlists rather than `-a`.
- The D435 Visual SLAM launch defaults `base_link -> camera_link` and
  `base_link -> esc_imu_link` to zero transforms for bench bringup only; set
  the measured transforms before robot evaluation.
